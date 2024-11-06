import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser

# Função para ler as credenciais do arquivo config.ini
def ler_credenciais():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    usuario_ghosp = config['G-HOSP']['usuario']
    senha_ghosp = config['G-HOSP']['senha']
    
    return usuario_ghosp, senha_ghosp

# Função para ler a lista de pacientes de alta do CSV
def ler_pacientes_de_alta():
    df = pd.read_csv('pacientes_de_alta.csv')
    return df

# Função para salvar a lista com o motivo de alta
def salvar_pacientes_com_motivo(df):
    df.to_csv('pacientes_de_alta.csv', index=False)

# Inicializa o ChromeDriver
def iniciar_driver():
    chrome_driver_path = "chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver

# Função para realizar login no G-HOSP
def login_ghosp(driver, usuario, senha):
    driver.get('http://10.16.9.43:4002/users/sign_in')
    
    # Ajusta o zoom para 50%
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(2)
    
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
def obter_motivo_alta(driver, nome):
    driver.get('http://10.16.9.43:4002/prontuarios')

    # Localiza o campo de nome e insere o nome do paciente
    nome_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nome")))
    nome_field.send_keys(nome)
    
    # Clica no botão de procurar
    procurar_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Procurar']")))
    procurar_button.click()

    # Aguarda a página carregar
    time.sleep(10)
    
    try:
        # Localiza o elemento com o rótulo "Motivo da alta"
        motivo_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']"))
        )

        # Agora captura o conteúdo do próximo elemento <div> após o rótulo
        motivo_conteudo_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']/following::div[@class='pl5 pb5']"))
        )
        
        motivo_alta = motivo_conteudo_element.text
        print(f"Motivo de alta capturado: {motivo_alta}")
        
    except Exception as e:
        motivo_alta = "Motivo da alta não encontrado"
        print(f"Erro ao capturar motivo da alta para {nome}: {e}")
    
    return motivo_alta

# Função principal para processar a lista de pacientes e buscar o motivo de alta
def processar_lista():
    usuario, senha = ler_credenciais()
    driver = iniciar_driver()
    
    # Faz login no G-HOSP
    login_ghosp(driver, usuario, senha)
    
    # Lê a lista de pacientes de alta
    df_pacientes = ler_pacientes_de_alta()
    
    # Verifica cada paciente e adiciona o motivo de alta
    for i, row in df_pacientes.iterrows():
        nome = row['Nome']
        print(f"Buscando motivo de alta para: {nome}")
        
        motivo = obter_motivo_alta(driver, nome)
        df_pacientes.at[i, 'Motivo da Alta'] = motivo
        print(f"Motivo de alta para {nome}: {motivo}")
        
        time.sleep(2)  # Tempo de espera entre as requisições

    # Salva o CSV atualizado
    salvar_pacientes_com_motivo(df_pacientes)
    
    driver.quit()

# Execução do script
if __name__ == '__main__':
    processar_lista()
