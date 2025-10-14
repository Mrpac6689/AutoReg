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
            '''print("Localizando menu principal...")
            menu_principal = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="menu-drop"]/ul[1]/li[1]/a'))
            )
            ActionChains(driver).move_to_element(menu_principal).perform()
            time.sleep(1)

            # Torna o submenu visível via JS
            driver.execute_script(
                "document.querySelector('#menu-drop > ul > li:first-child > ul').style.display = 'block';"
            )
            time.sleep(1)

            # Clica no link 'Prontuários'
            print("Clicando no link Prontuários...")
            #link_prontuarios = driver.find_element(By.CSS_SELECTOR, "#menu-drop > ul > li:first-child > ul > li.nobr > a[href='/prontuarios']")
            #link_prontuarios.click()
            #print("Acesso ao prontuário realizado!")
            driver.get(f"{caminho_ghosp}:4002/prontuarios")'''

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
            for idx, row in df_valido.iterrows():
                codigo = str(row['prontuario'])  # usando coluna 'prontuario'
                # Remove ".0" no final se existir
                if codigo.endswith('.0'):
                    codigo = codigo[:-2]
                # Remove qualquer ponto restante
                codigo = codigo.replace('.', '')
                print(f"Acessando prontuário: {codigo}")

                # Acessa diretamente a URL do prontuário
                driver.get(f"{caminho_ghosp}:4002/historicopacs/{codigo}")
                
                # Aguarda a página carregar
                time.sleep(1)

                # Verifica se o diálogo de justificativa de acesso aparece
                try:
                    dialog = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@id="form_justificativa"]'))
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

                except Exception as e:
                    print(f"Erro ao adicionar lembrete para código {codigo}: {e}")

            # Após processar todos os registros, mantém apenas as linhas com 'revisar' = 'sim'
            print("\n🧹 Limpando registros processados com sucesso...")
            df_revisar = df[df['revisar'].str.lower() == 'sim']
            
            if len(df_revisar) > 0:
                df_revisar.to_csv(csv_path, index=False)
                print(f"✅ CSV atualizado. {len(df_revisar)} linha(s) marcada(s) para revisão mantida(s).")
            else:
                # Se não há linhas para revisar, cria um CSV vazio com apenas os cabeçalhos
                df_vazio = pd.DataFrame(columns=df.columns)
                df_vazio.to_csv(csv_path, index=False)
                print("✅ Todos os registros foram processados com sucesso! CSV limpo.")
            
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
                        codigo = str(row['prontuario'])  # usando coluna 'prontuario'
                        # Remove ".0" no final se existir
                        if codigo.endswith('.0'):
                            codigo = codigo[:-2]
                        # Remove qualquer ponto restante
                        codigo = codigo.replace('.', '')
                        print(f"Acessando prontuário para lembrete CNS: {codigo}")

                        try:
                            # Acessa diretamente a URL do prontuário
                            driver.get(f"{caminho_ghosp}:4002/historicopacs/{codigo}")
                            
                            # Aguarda a página carregar
                            time.sleep(1)

                            # Verifica se o diálogo de justificativa de acesso aparece
                            try:
                                dialog = WebDriverWait(driver, 1).until(
                                    EC.presence_of_element_located((By.XPATH, '//div[@id="form_justificativa"]'))
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
                            print(f"Erro ao adicionar lembrete CNS para código {codigo}: {e}")
                    
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