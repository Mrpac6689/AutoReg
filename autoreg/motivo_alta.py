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

def motivo_alta():
    print("\n---===> ACESSO AO GHOSP <===---")
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

    # Localiza e clica no botão de login (value="Entrar" ou class="botao")
    print("Localizando botão de login...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.botao[value="Entrar"]'))
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
    csv_path = os.path.join(user_dir, 'pacientes_de_alta.csv')


    df = pd.read_csv(csv_path)
    if 'Motivo da Alta' not in df.columns:
        df['Motivo da Alta'] = ''

    for idx, row in df.iterrows():
        nome = str(row[0]).strip()
        print(f"[{idx+1}/{len(df)}] Buscando motivo de alta para: {nome}")
        # Localiza campo de nome e insere o valor
        campo_nome = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="nome"]'))
        )
        campo_nome.clear()
        campo_nome.send_keys(nome)

        # Clica no botão de busca
        botao_busca = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="cabecalho"]/form/fieldset/div[10]/div/input'))
        )
        botao_busca.click()
        #aqui
        motivoalta = None
        try:
            motivo_elem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[starts-with(@id,"ra-vw-")]/div/div[3]/div[1]/div[2]'))
            )
            motivoalta = motivo_elem.text
            print(f"Motivo de alta extraído: {motivoalta}")
        except Exception:
            print("Elemento de motivo de alta não encontrado.")
            # Nova verificação na tabela
            try:
                nome_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cabecalho"]/table/tbody/tr[1]/td[2]'))
                )
                nome_tabela = nome_elem.text.strip().lower()
                if nome_tabela == nome.strip().lower():
                    href_elem = driver.find_element(By.XPATH, '//*[@id="cabecalho"]/table/tbody/tr[1]/td[1]/a')
                    href = href_elem.get_attribute('href')
                    if not href.startswith('http'):
                        href = f"{caminho_ghosp}:4002{href_elem.get_attribute('href')}"
                    print(f"Acessando prontuário pelo link: {href}")
                    driver.get(href)
                    # Tenta novamente extrair motivo de alta
                    try:
                        motivo_elem2 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[starts-with(@id,"ra-vw-")]/div/div[3]/div[1]/div[2]'))
                        )
                        motivoalta = motivo_elem2.text
                        print(f"Motivo de alta extraído na nova página: {motivoalta}")
                    except Exception:
                        print("Motivo de alta não encontrado na nova página.")
                else:
                    print("Nome na tabela não corresponde ao paciente buscado.")
            except Exception:
                print("Tabela de pacientes não encontrada ou erro ao comparar nomes.")

        df.at[idx, 'Motivo da Alta'] = motivoalta if motivoalta else ''
        # Retorna à página de prontuários para o próximo paciente
        driver.get(f"{caminho_ghosp}:4002/prontuarios")

    # Salva o resultado no próprio arquivo
    df.to_csv(csv_path, index=False)
    print(f"Arquivo atualizado com motivos de alta salvo em {csv_path}")
    