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
def ghosp_nota():
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
            print("Localizando menu principal...")
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
            driver.get(f"{caminho_ghosp}:4002/prontuarios")

            import pandas as pd
            user_dir = os.path.expanduser('~/AutoReg')
            os.makedirs(user_dir, exist_ok=True)
            csv_path = os.path.join(user_dir, 'lista_same.csv')

            # Carrega o CSV e garante a coluna 'dados'
            df = pd.read_csv(csv_path)
            if 'dados' not in df.columns:
                df['dados'] = ''

            for idx, row in df.iterrows():
                codigo = str(row[1])  # segunda coluna
                print(f"Buscando prontuário para código: {codigo}")

                # Aguarda campo de código de internação
                campo_codigo = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="intern_id"]'))
                )
                campo_codigo.clear()
                campo_codigo.send_keys(codigo)

                # Clica no botão de busca
                botao_busca = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="cabecalho"]/form/fieldset/div[10]/div/input'))
                )
                botao_busca.click()

                # Aguarda o campo de lembretes aparecer e extrai o conteúdo
                try:
                    lembretes_elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="paclembretes"]'))
                    )
                    lembretes_texto = lembretes_elem.get_attribute('innerText')
                    lembretes_texto = lembretes_texto.replace('\n', ' ').replace('\r', ' ')
                    print(f"Conteúdo de paclembretes para código {codigo} (sem quebras de linha):")
                    print(lembretes_texto)
                    df.at[idx, 'dados'] = lembretes_texto
                except Exception as e:
                    print(f"Não foi possível extrair lembretes para código {codigo}: {e}")
                    df.at[idx, 'dados'] = ''

                # Retorna à página de prontuários para o próximo código
                driver.get(f"{caminho_ghosp}:4002/prontuarios")

            # Salva o CSV atualizado
            df.to_csv(csv_path, index=False)
            print(f"CSV atualizado com coluna 'dados' salvo em {csv_path}")

        except Exception as e:
            print(f"Erro ao acessar o menu de prontuários ou buscar internação: {e}")

        print("EXTRAÇÃO DE DADOS CONCLUÍDA.")
    except Exception as e:
        print(f"Ocorreu um erro durante o login: {e}")
    finally:
        driver.quit()