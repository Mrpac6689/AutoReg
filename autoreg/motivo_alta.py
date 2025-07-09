from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC        
import pandas as pd
import os
import time 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from autoreg.logging import setup_logging
import logging

setup_logging()

def motivo_alta():
    # Função para ler a lista de pacientes de alta do CSV
    def ler_pacientes_de_alta():
        user_dir = os.path.expanduser('~/AutoReg')
        csv_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
        df = pd.read_csv(csv_path)
        print("Lista de pacientes de alta lida com sucesso.")
        logging.info("Lista de pacientes de alta lida com sucesso.")
        return df

    # Função para salvar a lista com o motivo de alta
    def salvar_pacientes_com_motivo(df):
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
        df.to_csv(csv_path, index=False)
        print(f"Lista de pacientes com motivo de alta salva com sucesso em '{csv_path}'.")
        logging.info(f"Lista de pacientes com motivo de alta salva em '{csv_path}'.")

    # Inicializa o ChromeDriver
    def iniciar_driver():

        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    # Função para realizar login no G-HOSP
    def login_ghosp(driver, usuario, senha, caminho):
        
        driver.get(caminho + ':4002/users/sign_in')

        # Ajusta o zoom para 50%
        driver.execute_script("document.body.style.zoom='50%'")
        time.sleep(2)
        #trazer_terminal()
        
        # Localiza os campos visíveis de login
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(usuario)
        
        senha_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        senha_field.send_keys(senha)
        
        # Atualiza os campos ocultos com os valores corretos e simula o clique no botão de login
        driver.execute_script("""
            document.getElementById('user_email').value = arguments[0];
            document.getElementById('user_password').value = arguments[1];
            document.getElementById('new_user').submit();
        """, usuario, senha)

    # Função para pesquisar um nome e obter o motivo de alta via HTML
    def obter_motivo_alta(driver, nome, caminho):
        driver.get(caminho + ':4002/prontuarios')
        driver.maximize_window()     
        time.sleep(5) 

        # Localiza o campo de nome e insere o nome do paciente
        nome_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "nome")))
        nome_field.send_keys(nome)
        
        # Clica no botão de procurar
        procurar_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Procurar']")))
        procurar_button.click()

        # Aguarda a página carregar
        time.sleep(5)
        
        try:
            # Localiza o elemento com o rótulo "Motivo da alta"
            motivo_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']"))
            )

            # Agora captura o conteúdo do próximo elemento <div> após o rótulo
            motivo_conteudo_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']/following::div[@class='pl5 pb5']"))
            )
            
            motivo_alta = motivo_conteudo_element.text
            print(f"Motivo de alta capturado: {motivo_alta}")
            logging.info(f"Motivo de alta capturado para {nome}: {motivo_alta}")
            
        except Exception as e:
            motivo_alta = "Motivo da alta não encontrado"
            print(f"Erro ao capturar motivo da alta para {nome}: {e}")
            logging.error(f"Erro ao capturar motivo da alta para {nome}: {e}")
        
        return motivo_alta

    # Função principal para processar a lista de pacientes e buscar o motivo de alta
    def processar_lista():
        usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
        usuario = usuario_ghosp
        senha = senha_ghosp
        caminho = caminho_ghosp

        df_pacientes = ler_pacientes_de_alta()

        i = 0
        while i < len(df_pacientes):
            nome = df_pacientes.at[i, 'Nome']
            try:
                print(f"Buscando motivo de alta para: {nome}")
                logging.info(f"Buscando motivo de alta para: {nome}")

                driver = iniciar_driver()
                login_ghosp(driver, usuario, senha, caminho)

                motivo = obter_motivo_alta(driver, nome, caminho)
                df_pacientes.at[i, 'Motivo da Alta'] = motivo
                print(f"Motivo de alta para {nome}: {motivo}")
                logging.info(f"Motivo de alta para {nome}: {motivo}")

                salvar_pacientes_com_motivo(df_pacientes)
                driver.quit()
                time.sleep(2)
                i += 1  # Avança para o próximo paciente

            except Exception as e:
                print(f"Erro ao processar {nome}: {e}")
                logging.error(f"Erro ao processar {nome}: {e}")
                try:
                    driver.quit()
                except Exception:
                    pass
                print("Reiniciando driver e tentando novamente a partir do paciente problemático...")
                logging.info("Reiniciando driver e tentando novamente a partir do paciente problemático...")
                time.sleep(3)
                # Não incrementa i, para tentar novamente o mesmo paciente

        print("Motivos de alta encontrados, CSV atualizado.")
        logging.info("Motivos de alta encontrados, CSV atualizado.")
        

    # Execução do script
    
    processar_lista()
