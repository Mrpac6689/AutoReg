import os
import time
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.logging import setup_logging
import logging
def solicita_nota():
    print("\n---===> SOLICITA INSERE CODIGO SISREG NA NOTA <===---")
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    # Inicializa o navegador (Chrome)
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    # Acesse a página de login do G-HOSP na porta 4002
    url_login = f"{caminho_ghosp}:4002/users/sign_in"

    try:
        # Efetua login com verificação. O problema observado ocorre no momento do
        # login (que às vezes não se conclui). Se o login não for confirmado por
        # qualquer motivo, fecha o navegador, reabre e tenta novamente.
        max_tentativas_login = 3
        logado = False
        for tentativa_login in range(1, max_tentativas_login + 1):
            try:
                print(f"Tentativa de login {tentativa_login}/{max_tentativas_login}...")
                driver.get(url_login)

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

                # Verifica se o login foi bem-sucedido: ao logar, o G-HOSP sai da
                # página /users/sign_in. Se continuar nela, o login falhou.
                WebDriverWait(driver, 10).until(
                    lambda d: "/users/sign_in" not in d.current_url
                )
                logado = True
                print("Login realizado com sucesso!")
                break
            except Exception as e:
                print(f"⚠️  Falha no login (tentativa {tentativa_login}/{max_tentativas_login}): {e}")
                # Fecha o navegador e reabre para uma nova tentativa de login
                if tentativa_login < max_tentativas_login:
                    print("Reiniciando o navegador para nova tentativa de login...")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = webdriver.Chrome(options=chrome_options)

        if not logado:
            print("❌ Não foi possível efetuar login no G-HOSP após várias tentativas. Abortando.")
            return

        # Localiza o menu dropdown e passa o mouse para abrir
        from selenium.webdriver.common.action_chains import ActionChains

        try:

            import pandas as pd
            user_dir = os.path.expanduser('~/AutoReg')
            os.makedirs(user_dir, exist_ok=True)
            csv_path = os.path.join(user_dir, 'solicita_inf_aih.csv')

            # Carrega o CSV e garante as colunas necessárias
            df = pd.read_csv(csv_path)
            colunas_necessarias = ['prontuario', 'data', 'solsisreg', 'tipo']
            colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
            
            if colunas_faltantes:
                print(f"❌ Arquivo CSV não contém as colunas: {', '.join(colunas_faltantes)}")
                return

            # Verifica linhas com dados faltantes
            if 'revisar' not in df.columns:
                df['revisar'] = ''  # Cria a coluna 'revisar' se não existir
            
            linhas_invalidas = df[df[colunas_necessarias].isna().any(axis=1)].index
            if not linhas_invalidas.empty:
                print(f"⚠️ {len(linhas_invalidas)} linha(s) com dados faltantes serão ignoradas")
                df.loc[linhas_invalidas, 'revisar'] = 'sim'
                df.to_csv(csv_path, index=False)  # Salva as alterações no CSV

            # Filtra apenas linhas válidas para processamento
            df_valido = df[~df[colunas_necessarias].isna().any(axis=1)]
            print(f"📄 Processando {len(df_valido)} registros válidos...")

            # Rastreia os índices cuja nota foi efetivamente gravada no GHOSP.
            # Somente esses serão removidos do CSV na limpeza final.
            indices_sucesso = []

            for idx, row in df_valido.iterrows():
                ra = str(row['ra'])  # usando coluna 'ra'
                # Remove ".0" no final se existir
                if ra.endswith('.0'):
                    ra = ra[:-2]
                # Remove qualquer ponto restante
                ra = ra.replace('.', '')
                print(f"Acessando formulário eletrônico (RA: {ra})...")

                # Acessa diretamente a URL do formulário eletrônico usando intern_id
                driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")

                # Aguarda a página carregar
                time.sleep(1)

                # Verifica se o diálogo de justificativa de acesso aparece (com conteúdo)
                try:
                    dialog = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@id="form_justificativa" and contains(@class, "ui-dialog-content")]'))
                    )
                    print("Diálogo de justificativa encontrado!")

                    # Seleciona 'Enfermagem' no dropdown
                    dropdown = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_tabela_id"]'))
                    )
                    from selenium.webdriver.support.ui import Select
                    select = Select(dropdown)
                    select.select_by_visible_text("Enfermagem")
                    print("Opção 'Enfermagem' selecionada.")

                    # Preenche justificativa com 'NIR'
                    justificativa = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_justificativa"]'))
                    )
                    justificativa.clear()
                    justificativa.send_keys("NIR")
                    print("Justificativa preenchida com 'NIR'.")

                    # Clica em salvar
                    salvar_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="new_acesso_prontuario"]/div[3]/input'))
                    )
                    salvar_btn.click()
                    print("Botão 'Salvar' clicado.")

                    # Aguarda 1 segundo
                    time.sleep(1)

                    # Clica no botão de confirmação
                    confirmar_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button/span'))
                    )
                    confirmar_btn.click()
                    print("Botão de confirmação clicado.")
                except Exception as e:
                    print(f"Diálogo de justificativa não encontrado.")


                # Aguarda um momento para garantir que a página carregou após o diálogo
                time.sleep(1)

                # Clica no botão para adicionar novo lembrete
                try:
                    print("Clicando no botão de novo lembrete...")
                    botao_novo_lembrete = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[3]/div/h6/small/a'))
                    )
                    botao_novo_lembrete.click()

                    # Aguarda o campo de lembrete aparecer
                    campo_lembrete = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="prlembrete_lembrete"]'))
                    )

                    # Trata o número da solicitação para remover o '.0' caso exista
                    solsisreg = str(row['solsisreg']).rstrip('.0')

                    # Verifica se solsisreg tem 9 dígitos, se não tiver adiciona 0 ao final
                    if len(solsisreg) != 9:
                        solsisreg = solsisreg + '0'
                        print(f"⚠️  Número da solicitação ajustado para 9 dígitos: {solsisreg}")

                    # Monta o texto do lembrete com as informações das colunas
                    texto_lembrete = f"{row['data']} - {solsisreg} - {row['tipo']}"
                    print(f"Inserindo lembrete: {texto_lembrete}")
                    campo_lembrete.clear()  # Limpa o campo antes de inserir
                    campo_lembrete.send_keys(texto_lembrete)

                    # Clica no botão para salvar o lembrete
                    botao_salvar = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="janela_modal"]/form/div[3]/input[1]'))
                    )
                    botao_salvar.click()
                    print("Lembrete salvo com sucesso!")

                    # Aguarda um momento para garantir que o lembrete foi salvo
                    time.sleep(1)

                    # Nota gravada com sucesso: marca para remoção do CSV na limpeza final
                    indices_sucesso.append(idx)

                except Exception as e:
                    print(f"Erro ao adicionar lembrete para RA {ra}: {e}")
                    # Mantém o registro no CSV (preserva o solsisreg) e marca o erro,
                    # sem mexer em 'revisar' para não impedir a regravação posterior via -snt.
                    if 'erro' not in df.columns:
                        df['erro'] = ''
                    df.at[idx, 'erro'] = 'Falha ao gravar nota no GHOSP'

            # Após processar todos os registros, remove APENAS as linhas cuja nota foi
            # gravada com sucesso no GHOSP. As demais permanecem: linhas com dados
            # inválidos (revisar='sim') e linhas cuja gravação da nota falhou — estas
            # preservam o solsisreg e podem ser regravadas rodando o -snt isolado.
            print("\n🧹 Limpando apenas registros com nota gravada com sucesso...")
            df_restante = df.drop(index=indices_sucesso)
            df_restante.to_csv(csv_path, index=False)
            print(f"✅ {len(indices_sucesso)} registro(s) gravado(s) e removido(s). "
                  f"{len(df_restante)} mantido(s) (falhas de nota / revisão).")
            
            # Verificação adicional: processa linhas com CNS vazio
            print("\n🔍 Verificando linhas com CNS vazio...")
            
            # Relê o CSV atualizado
            df_revisar = pd.read_csv(csv_path)
            
            # Verifica se a coluna 'cns' existe
            if 'cns' not in df_revisar.columns:
                print("⚠️  Coluna 'cns' não encontrada no CSV. Pulando verificação de CNS.")
            elif len(df_revisar) == 0:
                print("ℹ️  Nenhum registro para verificar CNS.")
            else:
                # Filtra linhas onde CNS está vazio (NaN, None, string vazia ou só espaços)
                mask_cns_vazio = df_revisar['cns'].isna() | (df_revisar['cns'].astype(str).str.strip() == '') | (df_revisar['cns'].astype(str) == 'nan')
                df_cns_vazio = df_revisar[mask_cns_vazio]
                
                if len(df_cns_vazio) > 0:
                    print(f"📝 Encontradas {len(df_cns_vazio)} linha(s) com CNS vazio. Inserindo lembretes...")
                    
                    indices_processados = []
                    
                    for idx, row in df_cns_vazio.iterrows():
                        ra = str(row['ra'])  # usando coluna 'ra'
                        # Remove ".0" no final se existir
                        if ra.endswith('.0'):
                            ra = ra[:-2]
                        # Remove qualquer ponto restante
                        ra = ra.replace('.', '')
                        print(f"Acessando formulário eletrônico para lembrete CNS (RA: {ra})...")

                        try:
                            # Acessa diretamente a URL do formulário eletrônico usando intern_id
                            driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
                            
                            # Aguarda a página carregar
                            time.sleep(1)

                            # Verifica se o diálogo de justificativa de acesso aparece (com conteúdo)
                            try:
                                dialog = WebDriverWait(driver, 1).until(
                                    EC.presence_of_element_located((By.XPATH, '//div[@id="form_justificativa" and contains(@class, "ui-dialog-content")]'))
                                )
                                print("Diálogo de justificativa encontrado!")

                                # Seleciona 'Enfermagem' no dropdown
                                dropdown = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_tabela_id"]'))
                                )
                                from selenium.webdriver.support.ui import Select
                                select = Select(dropdown)
                                select.select_by_visible_text("Enfermagem")
                                print("Opção 'Enfermagem' selecionada.")

                                # Preenche justificativa com 'NIR'
                                justificativa = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_justificativa"]'))
                                )
                                justificativa.clear()
                                justificativa.send_keys("NIR")
                                print("Justificativa preenchida com 'NIR'.")

                                # Clica em salvar
                                salvar_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="new_acesso_prontuario"]/div[3]/input'))
                                )
                                salvar_btn.click()
                                print("Botão 'Salvar' clicado.")

                                # Aguarda 1 segundo
                                time.sleep(1)

                                # Clica no botão de confirmação
                                confirmar_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button/span'))
                                )
                                confirmar_btn.click()
                                print("Botão de confirmação clicado.")
                            except Exception as e:
                                print(f"Diálogo de justificativa não encontrado ou erro no preenchimento: {e}")

                            # Aguarda um momento para garantir que a página carregou após o diálogo
                            time.sleep(1)

                            # Clica no botão para adicionar novo lembrete
                            print("Clicando no botão de novo lembrete...")
                            botao_novo_lembrete = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[3]/div/h6/small/a'))
                            )
                            botao_novo_lembrete.click()

                            # Aguarda o campo de lembrete aparecer
                            campo_lembrete = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="prlembrete_lembrete"]'))
                            )

                            # Texto do lembrete para CNS faltante
                            texto_lembrete_cns = "FALTA CNS/CPF, FAVOR PROVIDENCIAR PARA SOLICITAÇÃO DE AIH"
                            print(f"Inserindo lembrete CNS: {texto_lembrete_cns}")
                            campo_lembrete.clear()  # Limpa o campo antes de inserir
                            campo_lembrete.send_keys(texto_lembrete_cns)

                            # Clica no botão para salvar o lembrete
                            botao_salvar = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="janela_modal"]/form/div[3]/input[1]'))
                            )
                            botao_salvar.click()
                            print("Lembrete CNS salvo com sucesso!")
                            
                            # Aguarda um momento para garantir que o lembrete foi salvo
                            time.sleep(1)
                            
                            # Marca o índice para remoção
                            indices_processados.append(idx)

                        except Exception as e:
                            print(f"Erro ao adicionar lembrete CNS para RA {ra}: {e}")
                    
                    # Remove as linhas processadas do CSV
                    if indices_processados:
                        print(f"\n🗑️  Removendo {len(indices_processados)} linha(s) com lembretes CNS inseridos...")
                        df_revisar = df_revisar.drop(index=indices_processados)
                        df_revisar.to_csv(csv_path, index=False)
                        print(f"✅ CSV atualizado. {len(df_revisar)} linha(s) restante(s).")
                else:
                    print("✅ Nenhuma linha com CNS vazio encontrada.")

        except Exception as e:
            print(f"Erro ao acessar o menu de prontuários ou buscar internação: {e}")

        print("EXTRAÇÃO DE DADOS CONCLUÍDA.")
    except Exception as e:
        print(f"Ocorreu um erro durante o login: {e}")
    finally:
        driver.quit()