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
def internados_ghosp_nota():
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
                try:
                    driver.get(f"{caminho_ghosp}:4002/pr/interns/{codigo}")
                    
                    # Aguarda a página carregar
                    time.sleep(1)

                    # Obtém o setor do span
                    setor_span = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/p[1]/span[2]'))
                    )
                    setor = setor_span.get_attribute('title')
                    print(f"Setor encontrado: {setor}")

                    # Adiciona ou atualiza o setor no DataFrame
                    if 'setor' not in df.columns:
                        df['setor'] = ''
                    df.at[idx, 'setor'] = setor

                    # Obtém a nota do paciente na mesma página
                    try:
                        lembretes_elem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="paclembretes"]'))
                        )
                        lembretes_texto = lembretes_elem.get_attribute('innerText')
                        lembretes_texto = lembretes_texto.replace('\n', ' ').replace('\r', ' ')
                        print(f"Conteúdo de lembretes extraído")
                        df.at[idx, 'dados'] = lembretes_texto
                    except Exception as e:
                        print(f"Não foi possível extrair lembretes: {e}")
                        df.at[idx, 'dados'] = ''

                except Exception as e:
                    print(f"Erro ao acessar prontuário {codigo}: {e}")
                    if 'setor' not in df.columns:
                        df['setor'] = ''
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

        print("EXTRAÇÃO DE DADOS CONCLUÍDA.")
    except Exception as e:
        print(f"Ocorreu um erro durante o login: {e}")
    finally:
        driver.quit()