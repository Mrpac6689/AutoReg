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

def ghosp_cns():
    print("\n---===> ACESSO AO GHOSP NOTA <===---")
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    # Inicializa o navegador (Chrome)
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    # Acesse a página de login do G-HOSP na porta 4002
    url_login = f"{caminho_ghosp}:4002/users/sign_in"
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

    print("Login realizado com sucesso!")
    # Localiza o menu dropdown e passa o mouse para abrir
    from selenium.webdriver.common.action_chains import ActionChains


    time.sleep(2)

    # Clica no link 'Prontuários'
    print("Clicando no link Prontuários...")

    driver.get(f"{caminho_ghosp}:4002/prontuarios")

    import pandas as pd
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'lista_same.csv')
    df = pd.read_csv(csv_path)
    if 'CNS' not in df.columns:
        df['CNS'] = ''

    for idx, row in df.iterrows():
        codigo = str(row[1])  # segunda coluna
        print(f"[{idx+1}/{len(df)}] Buscando CNS para código: {codigo}")
        try:
            campo_codigo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="intern_id"]'))
            )
            campo_codigo.clear()
            campo_codigo.send_keys(codigo)

            botao_busca = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cabecalho"]/form/fieldset/div[10]/div/input'))
            )
            botao_busca.click()

            link_cns = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/p/a'))
            )
            href_cns = link_cns.get_attribute('href')
            if not href_cns.startswith('http'):
                href_cns = f"{caminho_ghosp}:4002{link_cns.get_attribute('href')}"
            print(f"Abrindo link de prescrição: {href_cns}")
            driver.get(href_cns)

            link_h4 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
            )
            link_h4.click()
            print("Clique no link h4/a realizado com sucesso!")

            cns_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/small/fieldset[1]/div[2]'))
            )
            cns_valor = ''.join(filter(str.isdigit, cns_elem.text))
            print(f"CNS extraído: {cns_valor}")
            df.at[idx, 'CNS'] = cns_valor
        except Exception as e:
            print(f"Não foi possível clicar ou extrair CNS para código {codigo}: {e}")
            df.at[idx, 'CNS'] = ''

        # Volta para página de internação para o próximo código
        driver.get(f"{caminho_ghosp}:4002/prontuarios")

    # Salva o novo arquivo com CNS
    csv_cns_path = os.path.join(user_dir, 'lista_same_cns.csv')
    df.to_csv(csv_cns_path, index=False)
    print(f"Arquivo lista_same_cns.csv salvo em {csv_cns_path}")