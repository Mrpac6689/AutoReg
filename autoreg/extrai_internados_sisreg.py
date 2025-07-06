# autoreg/extrai_internados_sisreg.py
import os
import csv
import time
import tkinter as tk
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
import logging

setup_logging()

def extrai_internados_sisreg():
    print("\n---===> EXTRAÇÃO DE INTERNADOS <===---")
    logging.info("---===> EXTRAÇÃO DE INTERNADOS <===---")
    nomes_fichas = []
    navegador = None
    try:
        chrome_options = get_chrome_options()
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
        
        time.sleep(5)
        print("Login realizado com sucesso!")
        logging.info("Login realizado com sucesso!")

        # Agora, clica no link "Saída/Permanência"
        print("Tentando localizar o link 'Saída/Permanência'...")
        logging.info("Tentando localizar o link 'Saída/Permanência'...")
        saida_permanencia_link = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
        )
        
        print("Link 'Saída/Permanência' encontrado. Clicando no link...")
        logging.info("Link 'Saída/Permanência' encontrado. Clicando no link...")
        saida_permanencia_link.click()

        time.sleep(5)
        print("Página de Saída/Permanência acessada com sucesso!")
        logging.info("Página de Saída/Permanência acessada com sucesso!")

        # Mudança de foco para o iframe correto
        print("Tentando mudar o foco para o iframe...")
        logging.info("Tentando mudar o foco para o iframe...")
        WebDriverWait(navegador, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
        print("Foco alterado para o iframe.")
        logging.info("Foco alterado para o iframe.")

        # Clica no botão "PESQUISAR"
        print("Tentando localizar o botão PESQUISAR dentro do iframe...")
        logging.info("Tentando localizar o botão PESQUISAR dentro do iframe...")
        pesquisar_button = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        )
        
        print("Botão PESQUISAR encontrado!")
        logging.info("Botão PESQUISAR encontrado!")
        pesquisar_button.click()
        print("Botão PESQUISAR clicado!")
        logging.info("Botão PESQUISAR clicado!")

        time.sleep(5)

        # Extração de dados
        nomes = []
        while True:
            # Localiza as linhas da tabela com os dados
            linhas = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")

            for linha in linhas:
                # Extrai o nome do segundo <td> dentro de cada linha
                nome = linha.find_element(By.XPATH, './td[2]').text
                nomes.append(nome)

            # Tenta localizar o botão "Próxima página"
            try:
                print("Tentando localizar a seta para a próxima página...")
                logging.info("Tentando localizar a seta para a próxima página...")
                next_page_button = WebDriverWait(navegador, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']"))
                )
                print("Seta de próxima página encontrada. Clicando na seta...")
                logging.info("Seta de próxima página encontrada. Clicando na seta...")
                next_page_button.click()
                time.sleep(5)  # Aguarda carregar a próxima página
            except Exception:
                print("Não há mais páginas.")
                logging.info("Não há mais páginas.")
                break

        # Cria um DataFrame com os nomes extraídos
        df = pd.DataFrame(nomes, columns=["Nome"])

        # Salva os dados em uma planilha CSV
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'internados_sisreg.csv')
        df.to_csv(csv_path, index=False)
        print(f"Dados salvos em '{csv_path}'.")
        logging.info(f"Dados salvos em '{csv_path}'.")
        
    except TimeoutException:
        print("Erro ao tentar localizar os elementos na página. Verifique a conexão com a internet ou o estado do site.")
        logging.error("Erro ao tentar localizar os elementos na página. Verifique a conexão com a internet ou o estado do site.")
    except NoSuchElementException as e:         
        print(f"Erro ao localizar um elemento na página: {e}")
        logging.error(f"Erro ao localizar um elemento na página: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
    finally:
        if navegador:
            navegador.quit()
        print("Navegador fechado.")
        logging.info("Navegador fechado.")
