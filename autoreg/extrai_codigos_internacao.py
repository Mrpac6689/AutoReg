# autoreg/extrai_codigos_internacao.py
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.chrome_options import get_chrome_options  # ajuste aqui
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.detecta_capchta import detecta_captcha
from autoreg.sessao_sisreg import login_sisreg
import logging

setup_logging()
def extrai_codigos_internacao():
    nomes_fichas = []
    navegador = None
    try:
        chrome_options = get_chrome_options()  # ajuste aqui
        navegador = webdriver.Chrome(options=chrome_options)

        print("Lendo credenciais do SISREG...")
        logging.info("Lendo credenciais do SISREG...")
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()

        print("Realizando login no SISREG...")
        logging.info("Realizando login no SISREG...")
        login_sisreg(navegador, usuario_sisreg, senha_sisreg)
        print("Login realizado com sucesso!")
        logging.info("Login realizado com sucesso!")

        # Navega diretamente para a página de Internação (elimina navegação por iframe)
        navegador.get("https://sisregiii.saude.gov.br/cgi-bin/config_internar")
        print("Login realizado e navegação para página de Internação...\n")
        logging.info("Login realizado e navegação para página de Internação...\n")
        time.sleep(2)

        # Localiza e extrai os dados dos pacientes
        while True:
            # Verifica se há CAPTCHA antes de processar
            resultado_captcha = detecta_captcha(navegador)
            if resultado_captcha != 'ok':
                print(f"CAPTCHA não resolvido ({resultado_captcha}). Abortando extração.")
                logging.error(f"Extração abortada por CAPTCHA não resolvido: {resultado_captcha}")
                break

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
