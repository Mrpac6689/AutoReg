import os
import time
from datetime import datetime
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.justificativa_ghosp import tratar_justificativa_acesso
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.logging import setup_logging
from autoreg.ras_paciente import (
    COLUNA_LEMBRETES_LIDOS, COLUNA_RA_ANTERIOR, datas_solicitacoes_clinica, extrair_ras_huerb, ras_anteriores_na_janela,
    tem_solicitacao_desde,
)
import logging


def _url_historico_paciente(driver, caminho_ghosp):
    """
    Na página /pr/interns/{RA} já carregada, monta a URL /historicopacs/{prontuario}
    (lista de RAs do paciente) a partir do link do prontuário no banner do
    paciente — mesmo XPath que -sia usa para ler o nº do prontuário.
    """
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
    )
    href = link.get_attribute('href') or ''
    if '/historicopacs/' in href:
        return href
    prontuario = ''.join(filter(str.isdigit, link.text))
    if not prontuario:
        raise ValueError("nº do prontuário não encontrado no banner do paciente")
    return f"{caminho_ghosp}:4002/historicopacs/{prontuario}"


def _ra_anterior_solicitado(driver, caminho_ghosp, codigo, lembretes_texto):
    """
    Procura RAs HUERB anteriores do mesmo paciente (mesmo dia ou até 24h antes)
    e confere nos lembretes do paciente — iguais em todos os RAs dele — se há
    solicitação de clínica (não-UTI) datada a partir da entrada desse RA anterior.
    Deve ser chamada com /pr/interns/{codigo} carregada; navega para o
    histórico do paciente (/historicopacs/{prontuario}) só se os lembretes
    tiverem alguma solicitação de clínica com data.
    Retorna o número do RA anterior já solicitado, ou ''. Fail-open: qualquer
    falha de leitura retorna '' e o RA atual segue para solicitação como antes.
    """
    datas_clinica = datas_solicitacoes_clinica(lembretes_texto, datetime.now().year)
    if not datas_clinica:
        logging.info(f"-ign RA {codigo}: sem solicitação de clínica datada nos lembretes — histórico de RAs não consultado")
        return ''
    logging.info(
        f"-ign RA {codigo}: solicitação(ões) de clínica datada(s) nos lembretes: "
        f"{', '.join(d.strftime('%d/%m/%Y') for d in datas_clinica)} — consultando histórico de RAs"
    )
    try:
        url_historico = _url_historico_paciente(driver, caminho_ghosp)
        driver.get(url_historico)
        time.sleep(1)
        if tratar_justificativa_acesso(driver):
            driver.get(url_historico)
            time.sleep(1)
        ras = extrair_ras_huerb(driver)
        if not ras:
            logging.warning(f"Prontuário {codigo}: lista de RAs não encontrada em {url_historico}")
            return ''
        anteriores = ras_anteriores_na_janela(ras, codigo)
        logging.info(
            f"-ign RA {codigo}: {url_historico} → RAs HUERB: "
            f"{', '.join(f'''{r['ra']} ({r['data_entrada']:%d/%m/%Y %H:%M})''' for r in ras)}; "
            f"anteriores na janela mesmo dia/24h: {', '.join(str(r['ra']) for r in anteriores) or 'nenhum'}"
        )
        for anterior in anteriores:
            if tem_solicitacao_desde(lembretes_texto, anterior['data_entrada']):
                return str(anterior['ra'])
            logging.info(
                f"-ign RA {codigo}: RA anterior {anterior['ra']} sem solicitação de clínica datada entre "
                f"{anterior['data_entrada']:%d/%m/%Y} e +15 dias — não descarta"
            )
        return ''
    except Exception as e:
        logging.warning(f"Prontuário {codigo}: falha ao verificar RA anterior na mesma data/24h: {e}")
        return ''


def internados_ghosp_nota():
    setup_logging()
    print("\n---===> ACESSO AO GHOSP NOTA <===---")
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    # Inicializa o navegador (Chrome)
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    # Acesse a página de login do G-HOSP na porta 4002
    url_login = f"{caminho_ghosp}:4002/users/sign_in"
    driver.get(url_login)

    try:
        # Localiza e preenche o campo de e-mail
        print("Localizando campo de e-mail...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(usuario_ghosp)

        # Localiza e preenche o campo de senha (//*[@id="password"])
        print("Localizando campo de senha...")
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        senha_field.send_keys(senha_ghosp)

        # Localiza e clica no botão de login (//*[@id="new_user"]/div/input)
        print("Localizando botão de login...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
        )
        login_button.click()

        print("Login realizado com sucesso!")
        # Localiza o menu dropdown e passa o mouse para abrir
        from selenium.webdriver.common.action_chains import ActionChains

        try:
            #print("Localizando menu principal...")
            #menu_principal = WebDriverWait(driver, 10).until(
            #    EC.presence_of_element_located((By.XPATH, '//*[@id="menu-drop"]/ul[1]/li[1]/a'))
            #)
            #ActionChains(driver).move_to_element(menu_principal).perform()
            #time.sleep(1)

            # Torna o submenu visível via JS
            #driver.execute_script(
            #    "document.querySelector('#menu-drop > ul > li:first-child > ul').style.display = 'block';"
            #)
            #time.sleep(1)

            # Clica no link 'Prontuários'
            #print("Clicando no link Prontuários...")

            #driver.get(f"{caminho_ghosp}:4002/prontuarios")

            import pandas as pd
            user_dir = os.path.expanduser('~/AutoReg')
            os.makedirs(user_dir, exist_ok=True)
            csv_path = os.path.join(user_dir, 'internados_ghosp_avancado.csv')

            try:
                # Carrega o CSV e garante a coluna 'dados'
                df = pd.read_csv(csv_path)
                if 'dados' not in df.columns:
                    df['dados'] = ''  # Adiciona a coluna 'dados' se não existir
                # Recalculada a cada execução; dtype object para aceitar o número do RA
                # mesmo quando a coluna vem toda vazia (float64/NaN) do CSV.
                df[COLUNA_RA_ANTERIOR] = ''
                df[COLUNA_RA_ANTERIOR] = df[COLUNA_RA_ANTERIOR].astype(object)
                # Só vira 'sim' quando os lembretes são lidos de fato (ver ras_paciente)
                df[COLUNA_LEMBRETES_LIDOS] = ''
                df[COLUNA_LEMBRETES_LIDOS] = df[COLUNA_LEMBRETES_LIDOS].astype(object)
                print(f"Arquivo {csv_path} carregado com sucesso.")
                print(f"Total de prontuários a processar: {len(df)}")
            except FileNotFoundError:
                print(f"Erro: Arquivo {csv_path} não encontrado.")
                print("Execute primeiro a função -iga para gerar a lista de internados.")
                return
            except Exception as e:
                print(f"Erro ao ler o arquivo CSV: {e}")
                return

            total_prontuarios = len(df)
            for idx, row in df.iterrows():
                codigo = str(row['internacao'])  # usa a coluna 'internacao'
                print(f"[{idx+1}/{total_prontuarios}] Acessando prontuário para código: {codigo}")

                # Acessa diretamente a URL do histórico do paciente
                if 'setor' not in df.columns:
                    df['setor'] = ''
                try:
                    driver.get(f"{caminho_ghosp}:4002/pr/interns/{codigo}")

                    # Aguarda a página carregar
                    time.sleep(1)

                    # Paciente em alta: G-HOSP redireciona para a justificativa de
                    # acesso. Preenche/envia e re-navega para o prontuário do internado.
                    if tratar_justificativa_acesso(driver):
                        driver.get(f"{caminho_ghosp}:4002/pr/interns/{codigo}")
                        time.sleep(1)

                    # Obtém a nota do paciente (independente do setor abaixo, para que
                    # uma falha na leitura do setor nunca apague uma nota já lida).
                    # Usa textContent (não innerText): innerText só retorna texto
                    # visível/renderizado e pode vir vazio, sem lançar exceção, se o
                    # painel "DADOS IMPORTANTES" ainda não estiver com a classe "show"
                    # aplicada no instante da leitura.
                    try:
                        lembretes_elem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="paclembretes"]'))
                        )
                        lembretes_texto = lembretes_elem.get_attribute('textContent')
                        lembretes_texto = lembretes_texto.replace('\n', ' ').replace('\r', ' ').strip()
                        print(f"Conteúdo de lembretes extraído")
                        df.at[idx, 'dados'] = lembretes_texto
                        df.at[idx, COLUNA_LEMBRETES_LIDOS] = 'sim'
                        logging.info(f"-ign RA {codigo}: lembretes lidos ({len(lembretes_texto)} caracteres): {lembretes_texto!r}")
                    except Exception as e:
                        print(f"Não foi possível extrair lembretes: {e} — RA {codigo} fica fora da solicitação neste ciclo")
                        logging.warning(f"Prontuário {codigo}: falha ao extrair lembretes (#paclembretes) — RA fica fora da solicitação neste ciclo: {e}")
                        df.at[idx, 'dados'] = ''

                    # Obtém o setor do span (XPath posicional, mais suscetível a
                    # variações de layout entre pacientes/setores)
                    try:
                        setor_span = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/p[1]/span[2]'))
                        )
                        setor = setor_span.get_attribute('title')
                        print(f"Setor encontrado: {setor}")
                        logging.info(f"-ign RA {codigo}: setor {setor!r}")
                        df.at[idx, 'setor'] = setor
                    except Exception as e:
                        print(f"Não foi possível extrair o setor: {e}")
                        logging.warning(f"Prontuário {codigo}: falha ao extrair setor: {e}")
                        df.at[idx, 'setor'] = ''

                    # Por último, pois pode navegar para o histórico do paciente.
                    ra_anterior = _ra_anterior_solicitado(driver, caminho_ghosp, codigo, df.at[idx, 'dados'])
                    if ra_anterior:
                        print(f"RA anterior {ra_anterior} (mesma data/24h) já solicitado — RA {codigo} será descartado")
                        logging.info(f"-ign RA {codigo}: RA anterior {ra_anterior} na mesma data/24h já solicitado — RA {codigo} será descartado")
                    df.at[idx, COLUNA_RA_ANTERIOR] = ra_anterior

                except Exception as e:
                    print(f"Erro ao acessar prontuário {codigo}: {e} — RA fica fora da solicitação neste ciclo")
                    logging.error(f"Erro ao acessar prontuário {codigo} — RA fica fora da solicitação neste ciclo: {e}")
                    df.at[idx, COLUNA_LEMBRETES_LIDOS] = ''
                    df.at[idx, 'setor'] = ''
                    df.at[idx, 'dados'] = ''

            # Ordena o DataFrame pelo setor antes de salvar
            print("\nOrdenando dados por setor...")
            try:
                # Garante que a coluna 'setor' existe
                if 'setor' not in df.columns:
                    df['setor'] = ''
                
                # Ordena o DataFrame pelo setor
                df_ordenado = df.sort_values(by='setor', ascending=True)
                
                # Salva o CSV atualizado e ordenado
                df_ordenado.to_csv(csv_path, index=False)
                print(f"CSV atualizado e ordenado por setor salvo em {csv_path}")
                
                # Mostra um resumo dos setores e quantidade de pacientes
                resumo_setores = df_ordenado['setor'].value_counts()
                print("\nResumo de pacientes por setor:")
                for setor, count in resumo_setores.items():
                    print(f"{setor}: {count} paciente(s)")
                
            except Exception as e:
                print(f"Erro ao ordenar dados: {e}")
                # Em caso de erro na ordenação, salva o DataFrame original
                df.to_csv(csv_path, index=False)
                print(f"CSV salvo sem ordenação em {csv_path}")

        except Exception as e:
            print(f"Erro ao acessar o menu de prontuários ou buscar internação: {e}")
            logging.exception(
                f"-ign: execução interrompida — internados_ghosp_avancado.csv não foi salvo; "
                f"-std/-spaa vão descartar todos os RAs deste ciclo (lembretes não lidos): {e}"
            )

        print("EXTRAÇÃO DE DADOS CONCLUÍDA.")
    except Exception as e:
        print(f"Ocorreu um erro durante o login: {e}")
        logging.exception(f"-ign: falha no login/execução — nenhum lembrete lido neste ciclo: {e}")
    finally:
        driver.quit()