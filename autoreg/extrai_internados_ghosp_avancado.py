import os
import time
import pandas as pd
from bs4 import BeautifulSoup
import traceback
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.chrome_options import get_chrome_options
from autoreg.justificativa_ghosp import tratar_justificativa_acesso
from autoreg.historico_solicitacoes import solicitacoes_por_numero
from autoreg.ras_paciente import cadeia_internacao, extrair_ras_huerb, ra_da_internacao
from autoreg.vinculos import vinculos_manuais, resolver, limpar, ler_data, na_janela, normalizar_nome
from datetime import datetime
import logging

def _verifica_erro_500(driver):
    """Verifica se a página atual é a página de erro 500 do G-HOSP (Rails)."""
    try:
        src = driver.page_source
        return 'rails-default-error-page' in src or 'ocorreu um problema inesperado (500)' in src.lower()
    except Exception:
        return False


def _refaz_login_ghosp(driver, caminho_ghosp, usuario_ghosp, senha_ghosp):
    """Refaz o login no G-HOSP a partir da tela de usuário e senha."""
    print("Erro 500 detectado. Refazendo login no G-HOSP...")
    logging.warning("Erro 500 detectado no G-HOSP. Refazendo login...")
    driver.get(caminho_ghosp + ':4002/users/sign_in')
    time.sleep(2)
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.clear()
    email_field.send_keys(usuario_ghosp)
    senha_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
    )
    senha_field.clear()
    senha_field.send_keys(senha_ghosp)
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
    )
    login_button.click()
    time.sleep(5)
    print("Re-login realizado com sucesso!")
    logging.info("Re-login no G-HOSP realizado com sucesso após erro 500.")


def _navega_prontuarios(driver, caminho_ghosp, usuario_ghosp, senha_ghosp):
    """Navega para /prontuarios, refazendo login se encontrar erro 500."""
    url = caminho_ghosp + ':4002/prontuarios'
    driver.get(url)
    time.sleep(2)
    if _verifica_erro_500(driver):
        _refaz_login_ghosp(driver, caminho_ghosp, usuario_ghosp, senha_ghosp)
        driver.get(url)
        time.sleep(2)


def _url_homonimo(html, nome, nascimento):
    """
    Em /listar_prontuarios, retorna o href do ÚNICO homônimo cuja linha traz o
    nome e a data de nascimento do SISREG; '' se nenhum ou mais de um.
    """
    if not nome or not ler_data(nascimento):
        return ''
    achados = set()
    for tr in BeautifulSoup(html, 'html.parser').select('table.tableFixedHead tbody tr'):
        texto = tr.get_text(' ', strip=True)
        link = tr.select_one("a[href^='/historicopacs/']")
        if link and nascimento in texto and normalizar_nome(nome) in normalizar_nome(texto):
            achados.add(link['href'])
    return achados.pop() if len(achados) == 1 else ''


def _abre(driver, url):
    driver.get(url)
    time.sleep(1.5)
    if tratar_justificativa_acesso(driver):
        driver.get(url)
        time.sleep(1.5)


def _ras_do_prontuario_do_ra(driver, caminho_ghosp, ra):
    """RAs HUERB do paciente dono do RA: a busca pode abrir um cadastro duplicado."""
    _abre(driver, f"{caminho_ghosp}:4002/pr/interns/{ra}")
    banner = driver.find_elements(By.ID, "paciente")
    m = re.search(r' - (\d{4,8})\b', banner[0].text) if banner else None
    if not m:
        return []
    _abre(driver, f"{caminho_ghosp}:4002/historicopacs/{m.group(1)}")
    return extrair_ras_huerb(driver)


def _saida_do_ra(driver, caminho_ghosp, ra):
    """datetime da "Alta médica" do RA, ou None se aberto. Lança se a página não abrir."""
    _abre(driver, f"{caminho_ghosp}:4002/pr/altas?intern_id={ra}")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-content.cor-sec03")))
    for rotulo in ('Alta médica:', 'Liberação quarto:'):
        for el in driver.find_elements(By.XPATH, f"//label[normalize-space()='{rotulo}']/following-sibling::div"):
            m = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', el.text)
            if m:
                return datetime.strptime(m.group(0), '%d/%m/%Y %H:%M')
    return None


def extrai_internados_ghosp_avancado():
    print("\n---===> CONSULTA PERMANENCIA DE INTERNADOS NO GHOSP <===---")
    
    driver = None 
    
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()
        
        # Caminho para salvar o novo arquivo baixado
        user_dir = os.path.expanduser('~/AutoReg')
        print(f"Diretório de download configurado: {user_dir}")
        
        # Inicializa o navegador
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        print("Iniciando o Chromedriver...")

        # Acesse a página de login do G-HOSP
        driver.get(caminho_ghosp + ':4002/users/sign_in')
        
        # Definir tamanho da janela explicitamente (evita problemas com maximize no Docker/Kasm)
        print("Configurando tamanho da janela para 1920x1080...")
        driver.set_window_size(1920, 1080)
        time.sleep(2)

        # Realiza o login
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
        time.sleep(5)
        print("Login realizado com sucesso!")

        # Loop para processar cada linha do CSV
        csv_path = os.path.join(user_dir, 'internados_sisreg.csv')
        if not os.path.exists(csv_path):
            print(f"Erro: Arquivo {csv_path} não encontrado.")
            return

        df = pd.read_csv(csv_path)
        if 'erro' not in df.columns:
            df['erro'] = ""
        if 'RA' not in df.columns:
            df['RA'] = ""

        def _buscar_e_liberar(campo_id, valor):
            """Busca em /prontuarios por campo_id=valor e garante acesso ao paciente.

            Após a busca, o paciente pode aparecer de três formas:
            1. Ainda internado -> div #paciente (fluxo normal, com guarda de homônimo).
            2. Em alta, 1º acesso -> página de justificativa; ao enviar, o GHOSP vai
               para /historicopacs/[prontuario] (lista de RAs).
            3. Em alta, acesso já liberado antes -> vai direto para /historicopacs
               (sem justificativa e sem #paciente).

            Os casos 2 e 3 exibem a mesma lista de RAs (container-procedimentos), de
            onde a extração do RA ocorre na página atual (não refazer a busca, pois
            um novo acesso re-dispararia a justificativa).

            Retorna (paciente_divs, tem_historico):
            - paciente_divs: divs #paciente (caso 1).
            - tem_historico: True se a página atual é o histórico do paciente em alta
              (container-procedimentos presente, sem #paciente) — casos 2 e 3."""
            _navega_prontuarios(driver, caminho_ghosp, usuario_ghosp, senha_ghosp)
            inp = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, campo_id))
            )
            inp.clear()
            inp.send_keys(valor)
            driver.find_element(
                By.XPATH, '//input[@type="submit" and @value="Procurar"]'
            ).click()
            time.sleep(3)

            if _verifica_erro_500(driver):
                _refaz_login_ghosp(driver, caminho_ghosp, usuario_ghosp, senha_ghosp)
                raise Exception(f"Erro 500 após busca por {campo_id} - abortando tentativa atual")

            # Caso 2: paciente em alta, 1º acesso -> justificativa. Ao enviar, vai
            # para /historicopacs. (Caso 3 já cai direto no histórico, sem justificativa.)
            if tratar_justificativa_acesso(driver):
                time.sleep(1)

            logging.info(f"Busca {campo_id} - URL após acesso: {driver.current_url}")

            # Sinal confiável do paciente em alta: a URL vira /historicopacs/[id].
            # (A página de histórico também possui um banner #paciente, então não dá
            # para distinguir pelo #paciente - por isso ancoramos na URL.)
            tem_historico = "historicopacs" in (driver.current_url or "")
            paciente_divs = driver.find_elements(By.ID, "paciente")
            return paciente_divs, tem_historico

        historico = solicitacoes_por_numero()
        manuais = vinculos_manuais()

        print(f"\nIniciando processamento de {len(df)} pacientes...")

        for index, row in df.iterrows():
            nome_csv = str(row['Nome']).strip().upper()
            # Garante que o CNS seja tratado como string e sem ".0" ao final
            cns_csv = str(row['cns']).strip() if pd.notna(row['cns']) else ""
            if cns_csv.endswith('.0'):
                cns_csv = cns_csv[:-2]
            
            print(f"\n[{index+1}/{len(df)}] Processando: {nome_csv}")

            # RA e documento (CPF ou CNS do G-HOSP) com que o -ssr fez a solicitação
            solicitacao = str(row.get('solicitacao_sisreg', '')).strip()
            if solicitacao.endswith('.0'):
                solicitacao = solicitacao[:-2]
            registro = historico.get(solicitacao, {})
            ra_historico = registro.get('ra', '')
            documento = registro.get('documento', '')

            # 0. RA informado por uma pessoa em vinculos_manuais.csv: prioridade total
            if solicitacao in manuais:
                df.at[index, 'RA'] = manuais[solicitacao]
                df.at[index, 'erro'] = ""
                print(f"RA {manuais[solicitacao]} informado em vinculos_manuais.csv")
                logging.info(f"-eiga solicitação {solicitacao}: RA {manuais[solicitacao]} de vinculos_manuais.csv")
                df.to_csv(csv_path, index=False)
                continue

            found = False
            # Reavaliação: limpa erro antigo para não manter "não encontrado" obsoleto
            # em pacientes que agora são localizados (ex.: via histórico de alta).
            df.at[index, 'erro'] = ""
            
            try:
                # 1. Tentar busca por CNS
                if cns_csv:
                    print(f"Buscando por CNS: {cns_csv}")
                    paciente_divs, tem_historico = _buscar_e_liberar("cns", cns_csv)
                    if tem_historico:
                        # Paciente em alta: já estamos em /historicopacs, RA extraído abaixo.
                        found = True
                        print("Paciente em alta - acesso liberado; extraindo RA do histórico.")
                    elif paciente_divs:
                        nome_ghosp = paciente_divs[0].find_element(By.XPATH, './/h2').text.strip().upper()
                        if nome_csv in nome_ghosp or nome_ghosp in nome_csv: # Comparação flexível para nomes
                            found = True
                            print(f"Sucesso: Paciente localizado por CNS ({nome_ghosp})")

                # 2. Tentar pelo documento do G-HOSP guardado no histórico: o CNS
                # do SISREG pode não estar cadastrado no G-HOSP (RA 657487).
                # Só aceita se o RA solicitado estiver na lista do paciente.
                if not found and documento and documento != cns_csv:
                    campo_doc = "cpf" if len(documento) == 11 else "cns"
                    print(f"Tentando busca por {campo_doc.upper()} do histórico")
                    try:
                        _buscar_e_liberar(campo_doc, documento)
                        if ra_historico in [str(r['ra']) for r in extrair_ras_huerb(driver, timeout=5)]:
                            found = True
                            print(f"Sucesso: paciente localizado por {campo_doc.upper()} (RA {ra_historico} confirmado)")
                        else:
                            logging.warning(f"-eiga solicitação {solicitacao}: busca por {campo_doc} não confirmou o RA {ra_historico}")
                    except Exception as e:
                        logging.warning(f"-eiga solicitação {solicitacao}: falha na busca por {campo_doc}: {e}")

                # 2b. Prontuário escrito na ficha do SISREG. É texto livre: só vale
                # com o nome na página e um RA HUERB na época da internação.
                prontuario = limpar(row.get('prontuario'))
                if not found and not ra_historico and prontuario.isdigit():
                    try:
                        url = f"{caminho_ghosp}:4002/historicopacs/{prontuario}"
                        driver.get(url)
                        time.sleep(2)
                        if tratar_justificativa_acesso(driver):
                            driver.get(url)
                            time.sleep(1)
                        internacao = ler_data(row.get('data_internacao'))
                        nome_ok = normalizar_nome(nome_csv) in normalizar_nome(
                            driver.find_element(By.TAG_NAME, 'body').text)
                        found = nome_ok and any(
                            na_janela(r['data_entrada'], internacao)
                            for r in extrair_ras_huerb(driver, timeout=5))
                        logging.info(f"-eiga solicitação {solicitacao}: prontuário {prontuario} "
                                     f"{'confirmado' if found else 'não confirmado'}")
                    except Exception as e:
                        found = False
                        logging.warning(f"-eiga solicitação {solicitacao}: falha no prontuário {prontuario}: {e}")

                # 3. Tentar busca por Nome se não encontrou por CNS
                # Com RA no histórico o nome é dispensável (e sujeito a homônimos).
                if not found and not ra_historico:
                    print(f"Tentando busca por Nome: {nome_csv}")
                    paciente_divs, tem_historico = _buscar_e_liberar("nome", nome_csv)
                    if tem_historico:
                        found = True
                        print("Paciente em alta - acesso liberado; extraindo RA do histórico.")
                    elif paciente_divs:
                        nome_ghosp = paciente_divs[0].find_element(By.XPATH, './/h2').text.strip().upper()
                        if nome_csv in nome_ghosp or nome_ghosp in nome_csv:
                            found = True
                            print(f"Sucesso: Paciente localizado por Nome ({nome_ghosp})")
                
                # 3b. Homônimos: desempata pelo nascimento e confere um RA HUERB na
                # época da internação
                if not found and not ra_historico and "listar_prontuarios" in (driver.current_url or ""):
                    href = _url_homonimo(driver.page_source, nome_csv, limpar(row.get('nascimento')))
                    if href:
                        try:
                            driver.get(caminho_ghosp + ':4002' + href)
                            time.sleep(2)
                            if tratar_justificativa_acesso(driver):
                                driver.get(caminho_ghosp + ':4002' + href)
                                time.sleep(1)
                            internacao = ler_data(row.get('data_internacao'))
                            found = any(na_janela(r['data_entrada'], internacao)
                                        for r in extrair_ras_huerb(driver, timeout=5))
                        except Exception as e:
                            logging.warning(f"-eiga solicitação {solicitacao}: falha ao abrir homônimo: {e}")
                    logging.info(f"-eiga solicitação {solicitacao}: homônimos, desempate por nascimento "
                                 f"{'confirmado' if found else 'sem decisão'}")

                if not found and not ra_historico:
                    msg_erro = "Paciente não encontrado no GHOSP ou Homônimos, revisar manualmente"
                    df.at[index, 'erro'] = msg_erro
                    print(f"Aviso: {msg_erro}")
                
            except Exception as e:
                print(f"Erro ao processar linha {index+1}: {str(e)}")
                df.at[index, 'erro'] = f"Erro técnico: {str(e)}"

            # 4. RA que gerou a solicitação e os que o continuam (troca de setor).
            # Nunca o mais recente: pode ser retorno/PS depois da alta (11 casos em
            # 24/11/2026) ou cadastro duplicado (sol. 699718318). Sem conseguir ler a
            # lista de RAs não há como saber se a internação continuou: fica pendente.
            try:
                ras = extrair_ras_huerb(driver, timeout=10) if found else []

                def saida_de(ra):
                    return _saida_do_ra(driver, caminho_ghosp, ra)

                inicial, origem, candidatos = ra_historico, 'solicitação', []
                if not inicial:
                    inicial, origem = ra_da_internacao(ras, ler_data(row.get('data_internacao')), saida_de), 'época'
                if not inicial:
                    # Memória do -ign (lembrete ou nome + data), só sem ambiguidade
                    inicial, origem, candidatos = resolver(
                        solicitacao, nome_csv, limpar(row.get('data_internacao')))
                if inicial and inicial not in [r['ra'] for r in ras]:
                    ras = _ras_do_prontuario_do_ra(driver, caminho_ghosp, inicial)
                cadeia = [r['ra'] for r in cadeia_internacao(ras, inicial, saida_de)] if inicial else []
                if cadeia:
                    df.at[index, 'RA'] = cadeia[-1]
                    df.at[index, 'erro'] = ""
                    print(f"RA da internação ({origem}): {' -> '.join(cadeia)}")
                    logging.info(f"-eiga solicitação {solicitacao}: RA {' -> '.join(cadeia)} ({origem})")
                elif inicial or ras:
                    df.at[index, 'RA'] = None  # não herdar RA de rodada anterior
                    df.at[index, 'erro'] = "RA da internação não identificado entre os RAs do paciente"
                    logging.warning(f"-eiga solicitação {solicitacao}: RA da internação não identificado "
                                    f"(inicial: {inicial or '-'}; RAs {', '.join(r['ra'] for r in ras[:8])}; "
                                    f"candidatos {', '.join(candidatos)})")
            except Exception as e:
                print(f"Erro ao identificar o RA da internação: {str(e)}")
                logging.warning(f"-eiga solicitação {solicitacao}: falha ao ler os RAs, fica pendente: {e}")
                df.at[index, 'RA'] = None
                df.at[index, 'erro'] = f"Erro técnico: {str(e)}"

            # Salva o progresso a cada linha
            df.to_csv(csv_path, index=False)

        # Atualiza arquivo final
        df.to_csv(csv_path, index=False)
        print(f"\nProcessamento concluído. CSV atualizado em: {csv_path}")
        # driver.quit() fica só no finally: fechar aqui também fazia o segundo
        # quit() bater num chromedriver morto (3x "Retrying ... Connection refused").

    except Exception as e:
        print(f"Erro ao extrair internados do GHOSP: {str(e)}")
        logging.error(f"Erro ao extrair internados do GHOSP: {str(e)}")
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

        