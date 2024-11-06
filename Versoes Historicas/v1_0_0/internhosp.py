import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import configparser
from pathlib import Path
import pandas as pd
import re

# Função para ler as credenciais do arquivo config.ini
def ler_credenciais():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    usuario_ghosp = config['G-HOSP']['usuario']
    senha_ghosp = config['G-HOSP']['senha']
    
    return usuario_ghosp, senha_ghosp

# Exemplo de uso no script internhosp.py
usuario, senha = ler_credenciais()

# Caminho para o ChromeDriver
chrome_driver_path = "chromedriver.exe"
# Obtém o caminho da pasta de Downloads do usuário
pasta_downloads = str(Path.home() / "Downloads")

print(f"Pasta de Downloads: {pasta_downloads}")

# Função para encontrar o arquivo mais recente na pasta de Downloads
def encontrar_arquivo_recente(diretorio):
    arquivos = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, f))]
    arquivos.sort(key=os.path.getmtime, reverse=True)  # Ordena por data de modificação (mais recente primeiro)
    if arquivos:
        return arquivos[0]  # Retorna o arquivo mais recente
    return None

# Função para verificar se a linha contém um nome válido
def linha_valida(linha):
    # Verifica se a primeira coluna tem um número de 6 dígitos
    if re.match(r'^\d{6}$', str(linha[0])):
        # Verifica se a segunda ou a terceira coluna contém um nome válido
        if isinstance(linha[1], str) and linha[1].strip():
            return 'coluna_2'
        elif isinstance(linha[2], str) and linha[2].strip():
            return 'coluna_3'
    return False

# Função principal para extrair os nomes
def extrair_nomes(original_df):
    # Lista para armazenar os nomes extraídos
    nomes_extraidos = []
    
    # Percorre as linhas do DataFrame original
    for i, row in original_df.iterrows():
        coluna = linha_valida(row)
        if coluna == 'coluna_2':
            nome = row[1].strip()  # Extrai da segunda coluna
            nomes_extraidos.append(nome)
        elif coluna == 'coluna_3':
            nome = row[2].strip()  # Extrai da terceira coluna
            nomes_extraidos.append(nome)
        else:
            print(f"Linha ignorada: {row}")
    
    # Converte a lista de nomes extraídos para um DataFrame
    nomes_df = pd.DataFrame(nomes_extraidos, columns=['Nome'])
    
    # Caminho para salvar o novo arquivo sobrescrevendo o anterior na pasta atual
    caminho_novo_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'internados_ghosp.csv')
    nomes_df.to_csv(caminho_novo_arquivo, index=False)
    
    print(f"Nomes extraídos e salvos em {caminho_novo_arquivo}.")

# Inicializa o navegador (Chrome neste caso) usando o serviço
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Maximiza a janela para garantir que todos os elementos estejam visíveis
driver.maximize_window()

# Acesse a página de login do G-HOSP
driver.get('http://10.16.9.43:4001/users/sign_in')

try:
    # Ajustar o zoom para 50% antes do login
    print("Ajustando o zoom para 50%...")
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(2)  # Aguarda um pouco após ajustar o zoom

    # Realiza o login
    print("Tentando localizar o campo de e-mail...")
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.send_keys(usuario)

    print("Tentando localizar o campo de senha...")
    senha_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "user_password"))
    )
    senha_field.send_keys(senha)

    print("Tentando localizar o botão de login...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar']"))
    )
    login_button.click()

    time.sleep(5)
    print("Login realizado com sucesso!")

    # Acessar a página de relatórios
    print("Acessando a página de relatórios...")
    driver.get('http://10.16.9.43:4001/relatorios/rc001s')

    # Ajustar o zoom para 60% após acessar a página de relatórios
    print("Ajustando o zoom para 60% na página de relatórios...")
    driver.execute_script("document.body.style.zoom='60%'")
    time.sleep(2)  # Aguarda um pouco após ajustar o zoom

    # Selecionar todas as opções no dropdown "Setor"
    print("Selecionando todos os setores...")
    setor_select = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "setor_id1"))
    ))
    for option in setor_select.options:
        print(f"Selecionando o setor: {option.text}")  # Para garantir que todos os setores estão sendo selecionados
        setor_select.select_by_value(option.get_attribute('value'))

    print("Todos os setores selecionados!")

    # Selecionar o formato CSV
    print("Rolando até o dropdown de formato CSV...")
    formato_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "tipo_arquivo"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", formato_dropdown)
    time.sleep(2)

    print("Selecionando o formato CSV...")
    formato_select = Select(formato_dropdown)
    formato_select.select_by_value("csv")

    print("Formato CSV selecionado!")

    # Clicar no botão "Imprimir"
    print("Tentando clicar no botão 'IMPRIMIR'...")
    imprimir_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "enviar_relatorio"))
    )
    imprimir_button.click()

    print("Relatório sendo gerado!")

    # Aguardar até que o arquivo CSV seja baixado
    while True:
        arquivo_recente = encontrar_arquivo_recente(pasta_downloads)
        if arquivo_recente and arquivo_recente.endswith('.csv'):
            print(f"Arquivo CSV encontrado: {arquivo_recente}")
            break
        else:
            print("Aguardando o download do arquivo CSV...")
            time.sleep(5)  # Aguarda 5 segundos antes de verificar novamente

    try:
        # Carregar o arquivo CSV recém-baixado, garantindo que todas as colunas sejam lidas como texto
        original_df = pd.read_csv(arquivo_recente, header=None, dtype=str)

        # Chamar a função para extrair os nomes do CSV recém-baixado
        extrair_nomes(original_df)

    except Exception as e:
        print(f"Erro ao processar o arquivo CSV: {e}")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    driver.quit()
