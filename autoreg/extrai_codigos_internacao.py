# autoreg/extrai_codigos_internacao.py
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.chrome_options import get_chrome_options  # ajuste aqui
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
import logging

setup_logging()
def extrai_codigos_internacao():
    nomes_fichas = []
    navegador = None
    try:
        chrome_options = get_chrome_options()  # ajuste aqui
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Internação...\n")
        logging.info("Acessando a página de Internação...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        print("Localizando campo de usuário...")
        logging.info("Localizando campo de usuário...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        print("Campo de usuário localizado.")
        logging.info("Campo de usuário localizado.")

        print("Localizando campo de senha...")
        logging.info("Localizando campo de senha...")
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        print("Campo de senha localizado.")
        logging.info("Campo de senha localizado.")

        print("Lendo credenciais do SISREG...")
        logging.info("Lendo credenciais do SISREG...")
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()
        print("Credenciais lidas.")
        logging.info("Credenciais lidas.")

        print("Preenchendo usuário...")
        logging.info("Preenchendo usuário...")
        usuario_field.send_keys(usuario_sisreg)
        print("Usuário preenchido.")
        logging.info("Usuário preenchido.")

        print("Preenchendo senha...")
        logging.info("Preenchendo senha...")
        senha_field.send_keys(senha_sisreg)
        print("Senha preenchida.")
        logging.info("Senha preenchida.")

        print("Aguardando antes de clicar no botão de login...")
        logging.info("Aguardando antes de clicar no botão de login...")
        time.sleep(10)

        print("Localizando botão de login...")
        logging.info("Localizando botão de login...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        print("Botão de login localizado.")
        logging.info("Botão de login localizado.")

        print("Clicando no botão de login...")
        logging.info("Clicando no botão de login...")
        login_button.click()
        print("Botão de login clicado.")
        logging.info("Botão de login clicado.")
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Internação...\n")
        logging.info("Login realizado e navegação para página de Internação...\n")

        # Localiza e extrai os dados dos pacientes
        while True:
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas_pacientes:
                nome_paciente = linha.find_element(By.XPATH, "./td[2]").text
                ficha_onclick = linha.get_attribute("onclick")
                ficha = ficha_onclick.split("'")[1]
                nomes_fichas.append((nome_paciente, ficha))
                print(f"Nome: {nome_paciente}, Ficha: {ficha}\n")
                logging.info(f"Nome: {nome_paciente}, Ficha: {ficha}\n")
            print(f"Total de pacientes encontrados nesta página: {len(linhas_pacientes)}\n")
            logging.info(f"Total de pacientes encontrados nesta página: {len(linhas_pacientes)}\n")
            
            # Verifica se há próxima página
            try:
                botao_proxima_pagina = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if botao_proxima_pagina.is_displayed():
                    botao_proxima_pagina.click()
                    time.sleep(2)
                else:
                    break
            except NoSuchElementException:
                print("Não há próxima página disponível.\n")
                logging.info("Não há próxima página disponível.\n")
                break
    
    except TimeoutException:
        print("Erro ao tentar localizar as linhas de pacientes na página atual.\n")
        logging.error("Erro ao tentar localizar as linhas de pacientes na página atual.\n")
    except Exception as e:
        print(f"Erro inesperado: {e}\n")
        logging.error(f"Erro inesperado: {e}\n")
    finally:
        # Salva os dados em um arquivo CSV na pasta ~/AutoReg/
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'codigos_internacao.csv')
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerow(["Nome do Paciente", "Número da Ficha"])
            escritor_csv.writerows(nomes_fichas)
        print(f"Dados salvos no arquivo '{csv_path}'.\n")
        logging.info(f"Dados salvos no arquivo '{csv_path}'.\n")
        if navegador is not None:
            navegador.quit()
        print(f"Processo de captura de pacientes a internar concluído. \nDados salvos no arquivo '{csv_path}'.")
        logging.info(f"Processo de captura de pacientes a internar concluído. \nDados salvos no arquivo '{csv_path}'.")
