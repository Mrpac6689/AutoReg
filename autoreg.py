# Automated System Operation - SISREG & G-HOSP
# Version 7.0.0-linux - Maio 2025
# Author: MrPaC6689
# Repo: https://github.com/Mrpac6689/AutoReg
# Contact: michelrpaes@gmail.com
# Developed with the support of ChatGPT in Python 3.119
# For more information, see README.md. Repository on GitHub.

# Copyright (C) 2024 - Michel Ribeiro Paes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


# --------------------------------------------------------------------------


# Operação Automatizada de Sistemas - SISREG & G-HOSP
# Versão 7.0.0-linux - Maio de 2025
# Autor: MrPaC6689
# Repo: https://github.com/Mrpac6689/AutoReg
# Contato: michelrpaes@gmail.com
# Desenvolvido com o apoio do ChatGPT em Python 3.119
# Informações em README.md. Repositório no GitHub.

# Este programa é um software livre: você pode redistribuí-lo e/ou
# modificá-lo sob os termos da Licença Pública Geral GNU, como publicada
# pela Free Software Foundation, na versão 3 da Licença, ou (a seu critério)
# qualquer versão posterior.

# Este programa é distribuído na esperança de que seja útil,
# mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
# COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM PROPÓSITO ESPECÍFICO. Consulte a
# Licença Pública Geral GNU para mais detalhes.

# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa. Caso contrário, consulte <https://www.gnu.org/licenses/>.
#
#
#  Alterações da v7.0.0-linux:
'''
- Removidos os imports de bibliotecas não utilizadas.
- Removido o argumento zoomed do ChromeOptions, pois não é compativel com Linux.
- Adicionado o argumento headless=new para rodar o Chrome em modo oculto.
- Removidos os reajustes da janela de internação.
- Removidos os reajustes da janela de alta.
- Ajuste de foco para frame f_principal antes de chamar configFicha em executar_ficha() para todas as rotinas que acessam fichas no SISREG.
- Substituidos pop-ups de criação de janela extra por prints no campo de logs.
- Removidas bibliotecas inócuas.
'''
# Alterações da v7.0.0-linux
'''
- Reajustado destino do Download na Função Internhosp
- Corrigidos destinos de arquivos temposrários para concentrar na pasta ~/AutoReg
- Testes e ajustes de empacotamento e distribuição .deb
'''


########################################################
# Importação de funções externas e bibliotecas Python  #
########################################################
import os
import imagens
import csv
import subprocess
import platform
import unicodedata
import time
import pandas as pd
import re
import configparser
import pyautogui
import ctypes
import tkinter as tk
import threading
import sys
import requests
import zipfile
import shutil
import random
import io
import pdb
from datetime import datetime, timedelta
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter.scrolledtext import ScrolledText
from tkinter import PhotoImage
from PIL import Image, ImageTk  # Biblioteca para manipular imagens
import base64
from io import BytesIO
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException, WebDriverException
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains  # Adicionando a importação correta
from selenium.webdriver.common.keys import Keys
import tkinter as tk
import csv
import threading
import random
import time
import sys
#print(sys.path)
########################################
#   DEFINIÇÕES DE FUNÇÕES GLOBAIS      #
########################################

# Popup CONCLUSÃO
def mostrar_popup_conclusao(mensagem):
    # Cria uma janela Toplevel temporária para servir como pai do messagebox
    janela_temporaria = tk.Toplevel()
    janela_temporaria.withdraw()  # Oculta a janela temporária
    
    # Define a janela temporária como "topmost" para garantir que o messagebox ficará à frente
    janela_temporaria.wm_attributes("-topmost", 1)
    
    # Exibe o messagebox modal
    messagebox.showinfo("Concluído", mensagem, parent=janela_temporaria)

    # Destroi a janela temporária após o messagebox ser fechado
    janela_temporaria.destroy()

def mostrar_popup_alerta(titulo, mensagem):
    # Cria uma janela Toplevel temporária para servir como pai do messagebox
    janela_temporaria = tk.Toplevel()
    janela_temporaria.withdraw()  # Oculta a janela temporária
    
    # Define a janela temporária como "topmost" para garantir que o messagebox ficará à frente
    janela_temporaria.wm_attributes("-topmost", 1)
    
    # Exibe o messagebox modal
    messagebox.showwarning(titulo, mensagem, parent=janela_temporaria)

    # Destroi a janela temporária após o messagebox ser fechado
    janela_temporaria.destroy()

'''
Bloco desativado no port para Linux

'''
    
'''
Bloco desativado no port para Linux

def bkp_mostrar_popup_conclusao(mensagem):
    # Cria uma janela Toplevel temporária para exibir o popup
    global janela_temporaria  # Torna a janela temporária acessível globalmente
    janela_temporaria = tk.Toplevel()
    janela_temporaria.title("Concluído")
    janela_temporaria.geometry("300x150")
    janela_temporaria.wm_attributes("-topmost", 1)  # Garante que fique no topo

    # Adiciona a mensagem ao popup
    label_mensagem = tk.Label(janela_temporaria, text=mensagem, wraplength=280, justify="center", font=("Helvetica", 12))
    label_mensagem.pack(pady=20)

    # Adiciona o botão "OK" para fechar o popup
    botao_ok = tk.Button(janela_temporaria, text="OK", command=lambda: fechar_popup())
    botao_ok.pack(pady=10)

def fechar_popup():
    global janela_temporaria
    if 'janela_temporaria' in globals() and isinstance(janela_temporaria, tk.Toplevel):
        janela_temporaria.destroy()  # Fecha a janela temporária
        del janela_temporaria  # Remove a referência global

# Popup ERROS
def mostrar_popup_erro(mensagem):
    # Cria uma janela Toplevel temporária para servir como pai do messagebox
    janela_temporaria = tk.Toplevel()
    janela_temporaria.withdraw()  # Oculta a janela temporária
    
    # Define a janela temporária como "topmost" para garantir que o messagebox ficará à frente
    janela_temporaria.wm_attributes("-topmost", 1)
    
    # Exibe o messagebox modal
    messagebox.showerror("Erro", mensagem, parent=janela_temporaria)

    # Destroi a janela temporária após o messagebox ser fechado
    janela_temporaria.destroy()

# Popup ALERTAS
def mostrar_popup_alerta(titulo, mensagem):
    # Cria uma janela Toplevel temporária para servir como pai do messagebox
    janela_temporaria = tk.Toplevel()
    janela_temporaria.withdraw()  # Oculta a janela temporária
    
    # Define a janela temporária como "topmost" para garantir que o messagebox ficará à frente
    janela_temporaria.wm_attributes("-topmost", 1)
    
    # Exibe o messagebox modal
    messagebox.showwarning(titulo, mensagem, parent=janela_temporaria)

    # Destroi a janela temporária após o messagebox ser fechado
    janela_temporaria.destroy()
'''

# Função para normalizar o nome (remover acentos, transformar em minúsculas)
def normalizar_nome(nome):
    # Remove acentos e transforma em minúsculas
    nfkd = unicodedata.normalize('NFKD', nome)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# Função para comparar os arquivos CSV e salvar os pacientes a dar alta
def comparar_dados():
    # Caminho para os arquivos
    arquivo_sisreg = 'internados_sisreg.csv'
    arquivo_ghosp = 'internados_ghosp.csv'

    # Verifica se os arquivos existem
    if not os.path.exists(arquivo_sisreg) or not os.path.exists(arquivo_ghosp):
        print(Fore.RED + "\nOs arquivos internados_sisreg.csv ou internados_ghosp.csv não foram encontrados!")
        return

    # Lê os arquivos CSV
    with open(arquivo_sisreg, 'r', encoding='utf-8') as sisreg_file:
        sisreg_nomes_lista = [normalizar_nome(linha[0].strip()) for linha in csv.reader(sisreg_file) if linha]

    # Ignora a primeira linha (cabeçalho)
    sisreg_nomes = set(sisreg_nomes_lista[1:])

    with open(arquivo_ghosp, 'r', encoding='utf-8') as ghosp_file:
        ghosp_nomes = {normalizar_nome(linha[0].strip()) for linha in csv.reader(ghosp_file) if linha}

    # Encontra os pacientes a dar alta (presentes no SISREG e ausentes no G-HOSP)
    pacientes_a_dar_alta = sisreg_nomes - ghosp_nomes

    if pacientes_a_dar_alta:
        print(Fore.GREEN + "\n---===> PACIENTES A DAR ALTA <===---")
        for nome in sorted(pacientes_a_dar_alta):
            print(Fore.LIGHTYELLOW_EX + nome)  # Alterado para amarelo neon
        
        # Salva a lista em um arquivo CSV
        with open('pacientes_de_alta.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nome'])  # Cabeçalho
            for nome in sorted(pacientes_a_dar_alta):
                writer.writerow([nome])
        
        print(Fore.CYAN + "\nA lista de pacientes a dar alta foi salva em 'pacientes_de_alta.csv'.")
        esperar_tecla_espaco()
    else:
        print(Fore.RED + "\nNenhum paciente a dar alta encontrado!")
        esperar_tecla_espaco()

# Função para ler as credenciais do arquivo config.ini
def ler_credenciais():
    import sys
    import os
    config = configparser.ConfigParser()
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # Script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG']['usuario']
    senha_sisreg = config['SISREG']['senha']
    return usuario_sisreg, senha_sisreg

########################################
#   DEFINIÇÕES DE FUNÇÕES MÓDULO ALTA  #
########################################

### Definições Herdadas extrator.py
def extrator():
    print("\n---===> EXTRAÇÃO DE INTERNADOS <===---")
    # Exemplo de uso no script extrator.py
    usuario, senha = ler_credenciais()

    '''
    Bloco desativado no port para Linux

    # Caminho para o ChromeDriver
    chrome_driver_path = "chromedriver.exe"

    # Cria um serviço para o ChromeDriver
    service = Service(executable_path=chrome_driver_path)
    '''
    # Modo silencioso
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--incognito')   
    #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
        

    # Inicializa o navegador (Chrome neste caso) usando o serviço
    driver = webdriver.Chrome(options=chrome_options)

    # Minimizando a janela após iniciar o Chrome
    driver.minimize_window()

    # Acesse a página principal do SISREG
    driver.get('https://sisregiii.saude.gov.br/')

    try:
        print("Tentando localizar o campo de usuário...")
        usuario_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "usuario"))
        )
        print("Campo de usuário encontrado!")
    
        print("Tentando localizar o campo de senha...")
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "senha"))
        )
        print("Campo de senha encontrado!")

        # Preencha os campos de login
        print("Preenchendo o campo de usuário...")
        usuario_field.send_keys(usuario)
        
        print("Preenchendo o campo de senha...")
        senha_field.send_keys(senha)

        # Pressiona o botão de login
        print("Tentando localizar o botão de login...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
        )
        
        print("Botão de login encontrado. Tentando fazer login...")
        login_button.click()

        time.sleep(5)
        print("Login realizado com sucesso!")

        # Agora, clica no link "Saída/Permanência"
        print("Tentando localizar o link 'Saída/Permanência'...")
        saida_permanencia_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
        )
        
        print("Link 'Saída/Permanência' encontrado. Clicando no link...")
        saida_permanencia_link.click()

        time.sleep(5)
        print("Página de Saída/Permanência acessada com sucesso!")

        # Mudança de foco para o iframe correto
        print("Tentando mudar o foco para o iframe...")
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
        print("Foco alterado para o iframe.")

        # Clica no botão "PESQUISAR"
        print("Tentando localizar o botão PESQUISAR dentro do iframe...")
        pesquisar_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        )
        
        print("Botão PESQUISAR encontrado!")
        pesquisar_button.click()
        print("Botão PESQUISAR clicado!")

        time.sleep(5)

        # Extração de dados
        nomes = []
        while True:
            # Localiza as linhas da tabela com os dados
            linhas = driver.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")

            for linha in linhas:
                # Extrai o nome do segundo <td> dentro de cada linha
                nome = linha.find_element(By.XPATH, './td[2]').text
                nomes.append(nome)

            # Tenta localizar o botão "Próxima página"
            try:
                print("Tentando localizar a seta para a próxima página...")
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']"))
                )
                print("Seta de próxima página encontrada. Clicando na seta...")
                next_page_button.click()
                time.sleep(5)  # Aguarda carregar a próxima página
            except:
                # Se não encontrar o botão "Próxima página", encerra o loop
                print("Não há mais páginas.")
                break

        # Cria um DataFrame com os nomes extraídos
        df = pd.DataFrame(nomes, columns=["Nome"])

        # Salva os dados em uma planilha CSV
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'internados_sisreg.csv')
        df.to_csv(csv_path, index=False)
        print(f"Dados salvos em '{csv_path}'.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()

def ler_credenciais_ghosp():
    import sys
    import os
    config = configparser.ConfigParser()
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # Script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.ini')
    config.read(config_path)
    usuario_ghosp = config['G-HOSP']['usuario']
    senha_ghosp = config['G-HOSP']['senha']
    caminho_ghosp = config['G-HOSP']['caminho']
    return usuario_ghosp, senha_ghosp, caminho_ghosp

# Função para encontrar o arquivo mais recente na pasta de Downloads
''' Backup 

def encontrar_arquivo_recente(diretorio):
    arquivos = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, f))]
    arquivos.sort(key=os.path.getmtime, reverse=True)  # Ordena por data de modificação (mais recente primeiro)
    if arquivos:
        return arquivos[0]  # Retorna o arquivo mais recente
    return None

    '''
''' Destavidado, nova abordagem por Claude 3.7 Sonnet
def encontrar_arquivo_recente(diretorio):
    try:
        print(f"Verificando arquivos em: {diretorio}")
        
        # Verifica se o diretório existe
        if not os.path.exists(diretorio):
            print(f"O diretório {diretorio} não existe!")
            return None
            
        # Verifica se temos permissão para acessar o diretório
        if not os.access(diretorio, os.R_OK):
            print(f"Sem permissão para ler o diretório {diretorio}!")
            return None
            
        # Lista todos os arquivos no diretório
        arquivos = []
        for f in os.listdir(diretorio):
            caminho_completo = os.path.join(diretorio, f)
            if os.path.isfile(caminho_completo):
                arquivos.append(caminho_completo)
        
        if not arquivos:
            print(f"Nenhum arquivo encontrado em {diretorio}")
            return None
            
        print(f"Total de arquivos encontrados: {len(arquivos)}")
        
        # Mostra alguns arquivos como exemplo
        for arquivo in arquivos[:3]:
            print(f"Exemplo de arquivo: {os.path.basename(arquivo)}")
        
        # Ordena por data de modificação (mais recente primeiro)
        arquivos.sort(key=os.path.getmtime, reverse=True)
        
        # Lista os 5 arquivos mais recentes para debug
        print("Arquivos mais recentes:")
        for i, arquivo in enumerate(arquivos[:5]):
            mod_time = datetime.fromtimestamp(os.path.getmtime(arquivo))
            print(f"{i+1}. {os.path.basename(arquivo)} - {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Procura pelo primeiro arquivo CSV na lista ordenada
        for arquivo in arquivos:
            nome_arquivo = os.path.basename(arquivo).lower()
            if nome_arquivo.endswith('.csv'):
                tamanho = os.path.getsize(arquivo)
                print(f"Arquivo CSV encontrado: {nome_arquivo} ({tamanho} bytes)")
                if tamanho > 0:
                    return arquivo
                else:
                    print(f"Arquivo vazio ignorado: {nome_arquivo}")
        
        print("Nenhum arquivo CSV válido encontrado no diretório.")
        return None
        
    except Exception as e:
        print(f"Erro ao buscar arquivos em {diretorio}: {str(e)}")
        return None
'''

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
    
    '''
    # Determina o diretório onde o executável ou o script está sendo executado
    if getattr(sys, 'frozen', False):
        # Se o programa estiver rodando como executável
        base_dir = os.path.dirname(sys.executable)
    else:
        # Se estiver rodando como um script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    '''
    # Caminho para salvar o novo arquivo na pasta ~/AutoReg/
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    caminho_novo_arquivo = os.path.join(user_dir, 'internados_ghosp.csv')
    nomes_df.to_csv(caminho_novo_arquivo, index=False)
    
    print(f"Nomes extraídos e salvos em {caminho_novo_arquivo}.")

#Função para extrair internados no G-HOSP
def internhosp():
    print("\n---===> EXTRAÇÃO DE INTERNADOS <===---")
    usuario, senha, caminho = ler_credenciais_ghosp()

    '''
    Bloco desativado no port para Linux
    # Caminho para o ChromeDriver
    chrome_driver_path = "chromedriver.exe"

    # Inicializa o navegador (Chrome neste caso) usando o serviço
    service = Service(executable_path=chrome_driver_path)

   
            '''
    # Obtém o caminho da pasta de Downloads do usuário
    #pasta_downloads = str(Path.home() / "Downloads")

    # Caminho para salvar o novo arquivo baixado
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    print(f"Diretório de download configurado: {user_dir}")

    #download_path = os.path.join(user_dir, 'ghosp_download.csv')
    #print(f"Pasta de Downloads: {download_path}")
    
    # Captura timestamp antes do download para identificar arquivos novos
    antes_download = time.time()

    # Inicializa o navegador (Chrome neste caso) usando o serviço
    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": user_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    })    
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")
    
    # Minimizando a janela após iniciar o Chrome
    driver.minimize_window()

    # Acesse a página de login do G-HOSP
    driver.get(caminho + ':4001/users/sign_in')

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
        driver.get(caminho + ':4001/relatorios/rc001s')

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

        # Maximiza a janela para garantir que todos os elementos estejam visíveis
        driver.maximize_window()
        
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

        driver.minimize_window()

        # Aguardar até que o arquivo CSV seja baixado
        '''
        while True:
            arquivo_recente = encontrar_arquivo_recente(pasta_downloads)
            if arquivo_recente and arquivo_recente.endswith('.csv'):
                print(f"Arquivo CSV encontrado: {arquivo_recente}")
                break
            else:
                print("Aguardando o download do arquivo CSV...")
                time.sleep(5)  # Aguarda 5 segundos antes de verificar novamente
        '''
        # Contador para timeout
        tentativas = 0
        max_tentativas = 60  # 5 minutos (5 segundos * 60)
        arquivo_recente = None

        # Aguardar até que um novo arquivo CSV seja baixado
        while tentativas < max_tentativas:
            # Procura por arquivos CSV no diretório que foram criados após o início do download
            novos_arquivos = []
            for arquivo in os.listdir(user_dir):
                caminho_completo = os.path.join(user_dir, arquivo)
                if (arquivo.lower().endswith('.csv') and 
                    os.path.isfile(caminho_completo) and 
                    os.path.getmtime(caminho_completo) > antes_download and
                    os.path.getsize(caminho_completo) > 0):
                    novos_arquivos.append(caminho_completo)
            
            if novos_arquivos:
                # Ordena pelo mais recente
                novos_arquivos.sort(key=os.path.getmtime, reverse=True)
                arquivo_recente = novos_arquivos[0]
                print(f"Arquivo CSV baixado encontrado: {os.path.basename(arquivo_recente)}")
                break
            
            print(f"Aguardando o download do arquivo CSV... (tentativa {tentativas+1}/{max_tentativas})")
            tentativas += 1
            time.sleep(5)

        if arquivo_recente:
            # Processa o arquivo encontrado
            try:
                # Carregar o arquivo CSV recém-baixado
                original_df = pd.read_csv(arquivo_recente, header=None, dtype=str)
                # Chamar a função para extrair os nomes do CSV recém-baixado
                extrair_nomes(original_df)
            except Exception as e:
                print(f"Erro ao processar o arquivo CSV: {e}")
        else:
            print("Timeout: Não foi possível encontrar o arquivo CSV baixado no tempo esperado.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()

''' Bloco desativado no port para Linux
def trazer_terminal():
    # Obtenha o identificador da janela do terminal
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    hwnd = kernel32.GetConsoleWindow()
    
    if hwnd != 0:
        user32.ShowWindow(hwnd, 5)  # 5 = SW_SHOW (Mostra a janela)
        user32.SetForegroundWindow(hwnd)  # Traz a janela para frente
'''

### Definições Herdadas do motivo_alta.py
def motivo_alta():
    # Função para ler a lista de pacientes de alta do CSV
    def ler_pacientes_de_alta():
        user_dir = os.path.expanduser('~/AutoReg')
        csv_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
        df = pd.read_csv(csv_path)
        print("Lista de pacientes de alta lida com sucesso.")
        return df

    # Função para salvar a lista com o motivo de alta
    def salvar_pacientes_com_motivo(df):
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
        df.to_csv(csv_path, index=False)
        print(f"Lista de pacientes com motivo de alta salva com sucesso em '{csv_path}'.")

    # Inicializa o ChromeDriver
    def iniciar_driver():
        '''
        Bloco desativado no port para Linux

        chrome_driver_path = "chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        '''
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
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
            
        except Exception as e:
            motivo_alta = "Motivo da alta não encontrado"
            print(f"Erro ao capturar motivo da alta para {nome}: {e}")
        
        return motivo_alta

    # Função principal para processar a lista de pacientes e buscar o motivo de alta
    def processar_lista():
        usuario, senha, caminho = ler_credenciais_ghosp()
        driver = iniciar_driver()
        
        # Faz login no G-HOSP
        login_ghosp(driver, usuario, senha, caminho)
        
        # Lê a lista de pacientes de alta
        df_pacientes = ler_pacientes_de_alta()
        
        # Verifica cada paciente e adiciona o motivo de alta
        for i, row in df_pacientes.iterrows():
            nome = row['Nome']
            print(f"Buscando motivo de alta para: {nome}")
            
            motivo = obter_motivo_alta(driver, nome, caminho)
            df_pacientes.at[i, 'Motivo da Alta'] = motivo
            print(f"Motivo de alta para {nome}: {motivo}")
            
            time.sleep(2)  # Tempo de espera entre as requisições

        # Salva o CSV atualizado
        salvar_pacientes_com_motivo(df_pacientes)
        print("Motivos de alta encontrados, CSV atualizado.")
        
        driver.quit()

    # Execução do script
    if __name__ == '__main__':
        processar_lista()

''' Bloco desativado no port para Linux
#Definições para extração do código SISREG dos internados
def bkp_extrai_codigos():
    nomes_fichas = []

    #Inicia o webdriver
    print("Iniciando o navegador Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)  # Define um tempo de espera de 20 segundos para aguardar os elementos
    
    # Acessa a URL do sistema SISREG
    print("Acessando o sistema SISREG...")
    navegador.get("https://sisregiii.saude.gov.br")

    # Localiza e preenche o campo de usuário
    print("Tentando localizar o campo de usuário...")
    usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
    print("Campo de usuário encontrado!")

    print("Tentando localizar o campo de senha...")
    senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
    print("Campo de senha encontrado!")

    # Preenche os campos de login com as credenciais do config.ini
    usuario, senha = ler_credenciais()
    print("Preenchendo o campo de usuário...")
    usuario_field.send_keys(usuario)
    
    print("Preenchendo o campo de senha...")
    senha_field.send_keys(senha)

    # Pressiona o botão de login
    print("Tentando localizar o botão de login...")
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
    )
    
    print("Botão de login encontrado. Tentando fazer login...")
    login_button.click()

    time.sleep(5)  # Aguarda o carregamento da página após login
    print("Login realizado com sucesso!")


    # Clica no link "Saída/Permanência"
    print("Tentando localizar o link 'Saída/Permanência'...")
    saida_permanencia_link = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
    )
    
    print("Link 'Saída/Permanência' encontrado. Clicando no link...")
    saida_permanencia_link.click()

    time.sleep(5)  # Aguarda o carregamento da nova página
    print("Tentando mudar o foco para o iframe...")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
    print("Foco alterado para o iframe com sucesso!")

    # Localiza e clica no botão PESQUISAR dentro do iframe
    try:
        print("Tentando localizar o botão PESQUISAR dentro do iframe...")
        botao_pesquisar_saida = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        )
        print("Botão PESQUISAR localizado. Clicando no botão...")
        botao_pesquisar_saida.click()
        print("Botão PESQUISAR clicado com sucesso!")
        time.sleep(2)
    except TimeoutException as e:
        print(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
        navegador.quit()
        exit()

    #Já logado, faz a extração do numero das fichas por paciente internado direto do codigo fonte html
    try:
        while True:
            # Obtém todas as linhas da tabela de pacientes na página atual
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel') and (contains(@class, 'impar_tr') or contains(@class, 'par_tr'))]")
            for linha in linhas_pacientes:
                # Extrai o nome do paciente e o número da ficha
                nome_paciente = linha.find_element(By.XPATH, "./td[2]").text
                ficha_onclick = linha.get_attribute("onclick")
                ficha = ficha_onclick.split("'")[1]
                nomes_fichas.append((nome_paciente, ficha))
                print(f"Nome: {nome_paciente}, Ficha: {ficha}")
            
            # Verifica se há uma próxima página
            try:
                print("Verificando se há uma próxima página...")
                botao_proxima_pagina = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if botao_proxima_pagina.is_displayed():
                    print("Botão para próxima página encontrado. Clicando...")
                    botao_proxima_pagina.click()
                    time.sleep(2)
                else:
                    break
            except NoSuchElementException:
                print("Não há próxima página disponível.")
                break
    except TimeoutException:
        print("Erro ao tentar localizar as linhas de pacientes na página atual.")
        pass

    # Salva os dados em um arquivo CSV
    with open('codigos_sisreg.csv', mode='w', newline='', encoding='utf-8') as file:
        escritor_csv = csv.writer(file)
        escritor_csv.writerow(["Nome do Paciente", "Número da Ficha"])
        escritor_csv.writerows(nomes_fichas)
        
    print("Dados salvos no arquivo 'codigos_sisreg.csv'.")
    print("A extração dos códigos SISREG foi concluída com sucesso!")
    #mostrar_popup_conclusao("A extração dos códigos SISREG foi concluída com sucesso!")
    navegador.quit()
'''

def extrai_codigos():
    nomes_fichas = []

    # Inicia o webdriver
    print("Iniciando o navegador Chrome...")
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--incognito')   
    #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
    #chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)  # Define um tempo de espera de 20 segundos para aguardar os elementos
    
    try:
        # Acessa a URL do sistema SISREG
        print("Acessando o sistema SISREG...")
        navegador.get("https://sisregiii.saude.gov.br")

        # Localiza e preenche o campo de usuário
        print("Tentando localizar o campo de usuário...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        print("Campo de usuário encontrado!")

        print("Tentando localizar o campo de senha...")
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        print("Campo de senha encontrado!")

        # Preenche os campos de login com as credenciais do config.ini
        usuario, senha = ler_credenciais()
        usuario_field.send_keys(usuario)
        senha_field.send_keys(senha)

        # Pressiona o botão de login
        print("Tentando localizar o botão de login...")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
        )
        login_button.click()

        time.sleep(5)  # Aguarda o carregamento da página após login
        print("Login realizado com sucesso!")

        # Clica no link "Saída/Permanência"
        saida_permanencia_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
        )
        saida_permanencia_link.click()

        time.sleep(5)  # Aguarda o carregamento da nova página
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))

        # Localiza e clica no botão PESQUISAR dentro do iframe
        botao_pesquisar_saida = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        )
        botao_pesquisar_saida.click()
        time.sleep(5)

        # Extrai dados das tabelas
        while True:
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas_pacientes:
                nome_paciente = linha.find_element(By.XPATH, "./td[2]").text
                ficha_onclick = linha.get_attribute("onclick")
                ficha = ficha_onclick.split("'")[1]
                nomes_fichas.append((nome_paciente, ficha))
                
            
            # Verifica próxima página
            try:
                botao_proxima_pagina = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if botao_proxima_pagina.is_displayed():
                    botao_proxima_pagina.click()
                    time.sleep(5)
                else:
                    break
            except NoSuchElementException:
                break

        # Salva os dados em um arquivo CSV na pasta ~/AutoReg/
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'codigos_sisreg.csv')
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerow(["Nome do Paciente", "Número da Ficha"])
            escritor_csv.writerows(nomes_fichas)

        print(f"Dados salvos no arquivo '{csv_path}'.")

    except Exception as e:
        print(f"Erro durante a execução de extrai_codigos: {e}")

    finally:
        navegador.quit()
        print("Navegador encerrado.")
    
    print("Exibindo popup de conclusão...")
    print("A extração dos códigos SISREG foi concluída com sucesso!")
    #mostrar_popup_conclusao("A extração dos códigos SISREG foi concluída com sucesso!")

#Atualiza arquivo CVS para organizar nomes e incluir numeros de internação SISREG    
def atualiza_csv():
    import os
    import pandas as pd

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)

    pacientes_de_alta_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
    codigos_sisreg_path = os.path.join(user_dir, 'codigos_sisreg.csv')

    # Verifique se os arquivos existem
    if not os.path.exists(pacientes_de_alta_path):
        print(f"Arquivo não encontrado: {pacientes_de_alta_path}")
        return
    if not os.path.exists(codigos_sisreg_path):
        print(f"Arquivo não encontrado: {codigos_sisreg_path}")
        return

    pacientes_de_alta_df = pd.read_csv(pacientes_de_alta_path, encoding='utf-8')
    codigos_sisreg_df = pd.read_csv(codigos_sisreg_path, encoding='utf-8', dtype={'Número da Ficha': str})

    #print("Colunas pacientes_de_alta_df:", pacientes_de_alta_df.columns)
    #print("Colunas codigos_sisreg_df:", codigos_sisreg_df.columns)
    #print("Primeiras linhas pacientes_de_alta_df:\n", pacientes_de_alta_df.head())
    #print("Primeiras linhas codigos_sisreg_df:\n", codigos_sisreg_df.head())

    # Atualizar os nomes dos pacientes para caixa alta
    if 'Nome' in pacientes_de_alta_df.columns:
        pacientes_de_alta_df['Nome'] = pacientes_de_alta_df['Nome'].str.upper()
    else:
        print("Coluna 'Nome' não encontrada em pacientes_de_alta.csv")
        return

    # Mesclar os dois DataFrames
    if 'Nome do Paciente' not in codigos_sisreg_df.columns:
        print("Coluna 'Nome do Paciente' não encontrada em codigos_sisreg.csv")
        return

    pacientes_atualizados_df = pacientes_de_alta_df.merge(
        codigos_sisreg_df, left_on='Nome', right_on='Nome do Paciente', how='left'
    )

    if 'Número da Ficha' in pacientes_atualizados_df.columns:
        pacientes_atualizados_df['Número da Ficha'] = pacientes_atualizados_df['Número da Ficha'].astype(str)

    atualizados_path = os.path.join(user_dir, 'pacientes_de_alta_atualizados.csv')
    pacientes_atualizados_df.to_csv(atualizados_path, index=False, encoding='utf-8')

    print(f"\nArquivo '{atualizados_path}' atualizado com sucesso!")

#Função para dar alta individual
def dar_alta(navegador, wait, motivo_alta, ficha):
    '''
    print(f"Executando a função configFicha para a ficha: {ficha}")
    navegador.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    navegador.execute_script(f"configFicha('{ficha}')")
    print("Função de Saída/Permanência executada com sucesso!")
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
    '''
    print(f"Executando a função configFicha para a ficha: {ficha}")
    navegador.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    
    # Verifica se a função configFicha está disponível
    script_exists = navegador.execute_script("return typeof configFicha === 'function';")
    if not script_exists:
        print("Função configFicha não está disponível no contexto atual!")
        print(navegador.page_source)  # Debug: imprime o HTML do frame
        return

    navegador.execute_script(f"configFicha('{ficha}')")
    
    # Aguarda o botão "Efetua Saída" aparecer, indicando que a ficha foi carregada
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
    except TimeoutException:
        print("Timeout esperando o botão 'Efetua Saída'. Verifique se a ficha existe ou se já foi dada alta.")
        print(navegador.page_source)  # Debug: imprime o HTML do frame
        return

    print("Aguarda o carregamento da página após a execução do script configFicha.")

    try:
        print(f"Selecionando o motivo de alta: {motivo_alta}")
        motivo_select = wait.until(EC.presence_of_element_located((By.NAME, "co_motivo")))
        select = webdriver.support.ui.Select(motivo_select)
        motivo_mapping = {
            'PERMANENCIA POR OUTROS MOTIVOS': '1.2 ALTA MELHORADO',
            'ALTA MELHORADO': '1.2 ALTA MELHORADO',
            'ALTA A PEDIDO': '1.4 ALTA A PEDIDO',
            'ALTA POR OUTROS MOTIVOS': '1.8 ALTA POR OUTROS MOTIVOS',
            'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO': '3.1 TRANSFERIDO PARA OUTRO ESTABELECIMENTO',
            'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE': '4.1 OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
            'ALTA POR EVASAO': '1.6 ALTA POR EVASAO',
            'ENCERRAMENTO ADMINISTRATIVO': '5.1 ENCERRAMENTO ADMINISTRATIVO'
        }
        motivo_alta = motivo_mapping.get(motivo_alta, None)
        if motivo_alta is None:
            print("Motivo de alta não reconhecido, nenhuma ação será tomada.")
            return

        for opcao in select.options:
            if motivo_alta.upper() in opcao.text.upper():
                select.select_by_visible_text(opcao.text)
                print(f"Motivo de alta '{motivo_alta}' selecionado com sucesso!")
                break
    except TimeoutException:
        print("Erro ao tentar localizar o campo de motivo de alta.")
        return

    try:
        print("Tentando localizar o botão 'Efetua Saída'...")
        botao_efetua_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
        botao_efetua_saida.click()
        print("Botão 'Efetua Saída' clicado com sucesso!")

        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        print("Primeiro pop-up confirmado!")

        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        print("Segundo pop-up confirmado!")
    except TimeoutException:
        print("Erro ao tentar localizar o botão 'Efetua Saída' ou ao confirmar os pop-ups.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

#Loop para rodar o webdriver e executar as altas
def executa_saidas():
    def iniciar_navegador():
        print("Iniciando o navegador Chrome...")
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
        #chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20) #mudado de 20 para 10
        navegador.maximize_window()
        return navegador, wait

    def realizar_login(navegador, wait):
        print("Acessando o sistema SISREG...")
        navegador.get("https://sisregiii.saude.gov.br")

        print("Tentando localizar o campo de usuário...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        usuario, senha = ler_credenciais()
        usuario_field.send_keys(usuario)
        senha_field.send_keys(senha)

        print("Tentando localizar o botão de login...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
        print("Login realizado e navegação para página de Saída/Permanência concluída!")

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Foco alterado para o iframe com sucesso!")

        try:
            botao_pesquisar_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']")))
            botao_pesquisar_saida.click()
            print("Botão PESQUISAR clicado com sucesso!")
            # Aguarde a tabela/lista de pacientes aparecer
            wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")))
            print("Tabela de pacientes carregada!")
        except TimeoutException as e:
            print(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
            navegador.quit()
            return False
        return True

    # Iniciar navegador e realizar login inicial
    navegador, wait = iniciar_navegador()
    if not realizar_login(navegador, wait):
        return

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    atualizados_path = os.path.join(user_dir, 'pacientes_de_alta_atualizados.csv')
    restos_path = os.path.join(user_dir, 'restos.csv')

    try:
        pacientes_atualizados_df = pd.read_csv(atualizados_path, encoding='utf-8')
        for _, paciente in pacientes_atualizados_df.iterrows():
            try:
                nome_paciente = paciente.get('Nome', None)
                motivo_alta = paciente.get('Motivo da Alta', None)
                ficha = paciente.get('Número da Ficha', None)

                if nome_paciente is None or motivo_alta is None or ficha is None:
                    print("Dados insuficientes para o paciente, pulando para o próximo...")
                    continue

                # Converter o número da ficha para string, garantindo que não haverá .0 no final
                ficha = str(ficha).split('.')[0]

                print(f"Processando alta para o paciente: {nome_paciente}")
                dar_alta(navegador, wait, motivo_alta, ficha)
                time.sleep(2)

            except Exception as e:
                # Tratamento de erros específicos e reinicialização do navegador
                if isinstance(e, NoSuchElementException):
                    log_area.insert(tk.END, f"Erro: Elemento não encontrado - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                elif isinstance(e, TimeoutException):
                    log_area.insert(tk.END, f"Erro: Ocorreu um TimeoutException - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                else:
                    log_area.insert(tk.END, f"Erro inesperado: {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                
                log_area.see(tk.END)
                navegador.quit()

                # Reiniciar o navegador e refazer o login
                navegador, wait = iniciar_navegador()
                if not realizar_login(navegador, wait):
                    return

    except Exception as e:
        print(f"Erro geral na execução: {e}")

    # Criar arquivo 'restos.csv' com pacientes que não possuem motivos de alta desejados
    pacientes_df = pd.read_csv(atualizados_path, encoding='utf-8')
    motivos_desejados = [
        'PERMANENCIA POR OUTROS MOTIVOS',
        'ALTA MELHORADO',
        'ALTA A PEDIDO',
        'ALTA POR OUTROS MOTIVOS',
        'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO',
        'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
        'ENCERRAMENTO ADMINISTRATIVO',
        'ALTA POR EVASAO'
    ]
    restos_df = pacientes_df[~pacientes_df['Motivo da Alta'].isin(motivos_desejados)]
    restos_df.to_csv(restos_path, index=False)
    print(f"Arquivo '{restos_path}' criado com os pacientes sem motivo de alta desejado.")

    navegador.quit()
    print("\n Processo de saída concluído para todos os pacientes. \n Pacientes para análise manual gravados.")
# Função para normalizar o nome (remover acentos, transformar em minúsculas)
def normalizar_nome(nome):
    nfkd = unicodedata.normalize('NFKD', nome)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# Função para comparar os arquivos CSV e salvar os pacientes a dar alta
def comparar_dados():
    print("Comparando dados...")
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    arquivo_sisreg = os.path.join(user_dir, 'internados_sisreg.csv')
    arquivo_ghosp = os.path.join(user_dir, 'internados_ghosp.csv')
    arquivo_saida = os.path.join(user_dir, 'pacientes_de_alta.csv')

    if not os.path.exists(arquivo_sisreg) or not os.path.exists(arquivo_ghosp):
        print("Os arquivos internados_sisreg.csv ou internados_ghosp.csv não foram encontrados!")
        return

    with open(arquivo_sisreg, 'r', encoding='utf-8') as sisreg_file:
        sisreg_nomes_lista = [normalizar_nome(linha[0].strip()) for linha in csv.reader(sisreg_file) if linha]

    sisreg_nomes = set(sisreg_nomes_lista[1:])

    with open(arquivo_ghosp, 'r', encoding='utf-8') as ghosp_file:
        ghosp_nomes = {normalizar_nome(linha[0].strip()) for linha in csv.reader(ghosp_file) if linha}

    pacientes_a_dar_alta = sisreg_nomes - ghosp_nomes

    if pacientes_a_dar_alta:
        print("\n---===> PACIENTES A DAR ALTA <===---")
        for nome in sorted(pacientes_a_dar_alta):
            print(nome)

        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nome'])
            for nome in sorted(pacientes_a_dar_alta):
                writer.writerow([nome])

        print(f"\nA lista de pacientes a dar alta foi salva em '{arquivo_saida}'. \n")
    else:
        print("\nNenhum paciente a dar alta encontrado!")

# Função para executar o extrator e atualizar o status na interface
def executar_sisreg():
    def run_task():
        try:
            extrator()
            log_area.insert(tk.END, "Extração dos internados SISREG realizada com sucesso!")
            #mostrar_popup_conclusao("Extração dos internados SISREG realizada com sucesso!")
        except Exception as e:
            log_area.insert(tk.END, "Erro", f"Ocorreu um erro: {e}")
            #mostrar_popup_erro("Erro", f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()  # Executar a função em um thread separado

# Função para executar a extração do G-HOSP
def executar_ghosp():
    def run_task():
        try:
            internhosp()
            log_area.insert(tk.END, "Extração dos internados G-HOSP realizada com sucesso!")          
            #mostrar_popup_conclusao("Extração dos internados G-HOSP realizada com sucesso!")          
        except Exception as e:
            log_area.insert(tk.END, "Ocorreu um erro: {e}")
            #mostrar_popup_erro(f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()

# Função para comparar os dados
def comparar():
    def run_task():
        try:
            comparar_dados()
            log_area.insert(tk.END, "Comparação de dados realizada com sucesso!")
            #mostrar_popup_conclusao("Comparação de dados realizada com sucesso!")
        except Exception as e:
            log_area.insert(tk.END, "Ocorreu um erro: {e}")
            #mostrar_popup_erro(f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()

# Função para trazer a janela principal para a frente
def trazer_janela_para_frente():
    janela.lift()  # Traz a janela principal para a frente
    janela.attributes('-topmost', True)  # Coloca a janela no topo de todas
    janela.attributes('-topmost', False)  # Remove a condição de "sempre no topo" após ser trazida à frente

# Função para capturar o motivo de alta
def capturar_motivo_alta():
    print("Capturando motivo de alta...")
    def run_task():
        try:
           # Função para trazer a janela principal para a frente
            motivo_alta()
            log_area.insert(tk.END, "Motivos de alta capturados com sucesso!")
            #mostrar_popup_conclusao("Motivos de alta capturados com sucesso!")
        except Exception as e:
            log_area.insert(tk.END, "Ocorreu um erro: {e}")
            #mostrar_popup_erro(f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()
    janela.after(3000, trazer_janela_para_frente)

##############################################
#   DEFINIÇÕES DE FUNÇÕES DE ALTA POR CNS    #
##############################################

##### Captura CNS de pacientes em restos.csv
def captura_cns_restos_alta():
    # Função para realizar o login no SISREG
    def iniciar_navegador_cns():
        log_area.insert(tk.END, "Iniciando o navegador Chrome com melhorias de desempenho...\n")
        log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
        
        #Define opções do Driver
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Abre o navegador maximizado
        chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
        chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
        chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
        chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas  
       # chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
        
        #Roda o chromedriver com o label 'navegador'
        navegador = webdriver.Chrome(options=chrome_options)
        
        #Ajusta a visibilidade da janela do programa
        #janela.iconify()    # Minimizar a janela
        #janela.update()     # Atualizar o estado da janela
        #janela.deiconify()  # Restaurar para garantir visibilidade

        return navegador
    
    def realizar_login_cns_alta(navegador, wait, usuario, senha):
        log_area.insert(tk.END, "Acessando a página do SISREG...\n")
        log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
        navegador.get("https://sisregiii.saude.gov.br")
        try:
            # Realiza o login
            usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
            senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
            usuario_field.send_keys(usuario)
            senha_field.send_keys(senha)
            
            # Clica no botão de login
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
            login_button.click()
            
            # Clica no link "saída/permanência"
            saida_permanencia = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='barraMenu']/ul/li[2]/a")))
            saida_permanencia.click()
            
            # Troca o iframe
            navegador.switch_to.frame("f_principal")
                  
            # Aguarda a presença do botão "Pesquisar" e tenta o clique usando JavaScript
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center/table/tbody/tr[10]/td/input[@name='pesquisar']")))
            navegador.execute_script("document.querySelector('#main_page > form > center > table > tbody > tr:nth-child(10) > td > input[name=pesquisar]').click()")
            
            log_area.insert(tk.END, "Login realizado com sucesso e botão 'Pesquisar' clicado.\n")
            log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
            return True
        except TimeoutException:
            log_area.insert(tk.END, "Erro: Falha ao realizar login ou encontrar o botão 'Pesquisar'.\n")
            log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
            navegador.quit()
            return False

    # Função para executar o JavaScript da ficha do paciente
    def executar_ficha_js(navegador, ficha):
        try:
            time.sleep(2)
            navegador.execute_script(f"configFicha('{ficha}')\n")
            log_area.insert(tk.END, f"Executando a função configFicha para a ficha: {ficha}\n")
            log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
            time.sleep(1)  # Espera de 1 segundo para garantir a execução
            navegador.switch_to.default_content()  # Retorna ao frame principal após a execução
        except TimeoutException:
            log_area.insert(tk.END, "Erro: Frame 'f_main' não disponível no tempo esperado.\n")
            log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo

    # Inicializa o navegador e faz login
    navegador = iniciar_navegador_cns()
    wait = WebDriverWait(navegador, 10)
    usuario, senha = ler_credenciais()
    
    if not realizar_login_cns_alta(navegador, wait, usuario, senha):
        return
    
    # Lista para armazenar as linhas atualizadas com o CNS
    linhas_atualizadas = []

    # Abre o arquivo CSV e percorre cada linha
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    restos_path = os.path.join(user_dir, 'restos.csv')

    with open(restos_path, mode='r', encoding='utf-8') as file:
        leitor_csv = csv.reader(file)
        cabecalho = next(leitor_csv)  # Pega o cabeçalho
        cabecalho.append("CNS")  # Adiciona uma nova coluna "CNS"
        linhas_atualizadas.append(cabecalho)  # Adiciona o cabeçalho atualizado à lista

        for linha in leitor_csv:
            ficha = linha[3]  # Captura o número da ficha da quarta coluna
            try:                                                 
                ficha = str(ficha).split('.')[0] # Converter o número da ficha para string, garantindo que não haverá .0 no final
                executar_ficha_js(navegador, ficha) # Abre a ficha do paciente
                
                # Ajusta o foco para o frame correto
                navegador.switch_to.frame("f_principal")
                
                try:
                    # Espera o elemento CNS estar presente
                    WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table[1]/tbody/tr[17]/td")))
                    
                    # Localiza e captura o CNS
                    cns_paciente = navegador.find_element(By.XPATH, "//*[@id='main_page']/form/table[1]/tbody/tr[17]/td")
                    cns_texto = cns_paciente.text
                    
                    # Verifica se o CNS termina com ".0" e remove se necessário
                    if cns_texto.endswith('.0'):
                        cns_texto = cns_texto[:-2]
                    
                    log_area.insert(tk.END, f"CNS encontrado: {cns_texto}\n")
                    log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
                    
                    # Adiciona o CNS na linha atual
                    linha.append(cns_texto)
                    
                except TimeoutException:
                    log_area.insert(tk.END, "Erro: Não foi possível localizar o CNS do paciente no tempo esperado.\n")
                    log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
                    linha.append("Erro ao localizar CNS")  # Marca erro na coluna CNS
                    log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
                
                # Adiciona a linha com o CNS ao conjunto de linhas atualizadas
                linhas_atualizadas.append(linha)

            except Exception as e:
                log_area.insert(tk.END, f"Erro ao processar ficha {ficha}: {e}\n")
                log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
                linha.append("Erro ao abrir ficha")  # Marca erro se não conseguir abrir a ficha
                linhas_atualizadas.append(linha)
    
    # Salva o CSV atualizado com a nova coluna CNS
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    restos_atualizado_path = os.path.join(user_dir, 'restos_atualizado.csv')
    with open(restos_atualizado_path, mode='w', newline='', encoding='utf-8') as file:
        escritor_csv = csv.writer(file)
        escritor_csv.writerows(linhas_atualizadas)
    
    log_area.insert(tk.END, "Arquivo CSV atualizado com CNS salvo como 'restos_atualizado.csv'.\n")
    log_area.see(tk.END)  # Faz o widget rolar automaticamente até o final do conteúdo
    #mostrar_popup_conclusao("Arquivo CSV atualizado com CNS salvo como 'restos_atualizado.csv'.")

####Capturar motivo alta por CNS
def motivo_alta_cns():
    # Caminho para a pasta do usuário
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    restos_csv_path = os.path.join(user_dir, 'restos_atualizado.csv')

    # Corrige o arquivo CSV antes de iniciar a rotina
    try:
        df_corrigir = pd.read_csv(restos_csv_path)
        # Verifica se a coluna 'CNS' existe; se não, tenta acessar pela posição (índice 4)
        if 'CNS' in df_corrigir.columns:
            df_corrigir['CNS'] = df_corrigir['CNS'].astype(str).apply(lambda x: x[:-2] if x.endswith('.0') else x)
        else:
            nome_coluna = df_corrigir.columns[4]
            df_corrigir[nome_coluna] = df_corrigir[nome_coluna].astype(str).apply(lambda x: x[:-2] if x.endswith('.0') else x)
        df_corrigir.to_csv(restos_csv_path, index=False)
        log_area.insert(tk.END, "Arquivo CSV corrigido: removido '.0' dos CNS, se necessário.\n")
        log_area.see(tk.END)
    except Exception as e:
        log_area.insert(tk.END, f"Erro ao corrigir o CSV: {e}\n")
        log_area.see(tk.END)
    
    # Função para inicializar o ChromeDriver
    def iniciar_driver():
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        log_area.insert(tk.END, "Iniciando driver...\n")
        log_area.see(tk.END)
        return driver

    # Função para realizar login no G-HOSP
    def login_ghosp(driver, usuario, senha, caminho):
        driver.get(caminho + ':4002/users/sign_in')
        driver.execute_script("document.body.style.zoom='50%'")
        time.sleep(2)
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(usuario)
        senha_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        senha_field.send_keys(senha)
        log_area.insert(tk.END, "Logando no G-Hosp driver...\n")
        log_area.see(tk.END)
        driver.execute_script("""
            document.getElementById('user_email').value = arguments[0];
            document.getElementById('user_password').value = arguments[1];
            document.getElementById('new_user').submit();
        """, usuario, senha)

    # Função para buscar o motivo de alta pelo CNS no G-HOSP
    def obter_motivo_alta(driver, cns, caminho):
        driver.get(caminho + ':4002/prontuarios')
        cns_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "cns")))
        cns_field.send_keys(cns)
        procurar_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Procurar']")))
        procurar_button.click()
        time.sleep(10)
        try:
            motivo_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']"))
            )
            motivo_conteudo_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']/following::div[@class='pl5 pb5']"))
            )
            motivo_alta = motivo_conteudo_element.text
            log_area.insert(tk.END, f"Motivo de alta capturado: {motivo_alta}\n")
            log_area.see(tk.END)
        except Exception as e:
            motivo_alta = "Motivo da alta não encontrado"
            log_area.insert(tk.END, f"Erro ao capturar motivo da alta para CNS {cns}: {e}\n")
            log_area.see(tk.END)
        return motivo_alta

    # Código principal da função motivo_alta_cns
    usuario, senha, caminho = ler_credenciais_ghosp()
    driver = iniciar_driver()
    login_ghosp(driver, usuario, senha, caminho)

    # Lê a lista de pacientes de alta, garantindo que a coluna CNS seja lida como string
    df_pacientes = pd.read_csv(restos_csv_path, dtype={'CNS': str})
    df_pacientes['CNS'] = df_pacientes['CNS'].apply(lambda x: re.sub(r'\.0$', '', x) if isinstance(x, str) else x)

    # Verifica cada paciente a partir da segunda linha e adiciona o motivo de alta
    for i, row in df_pacientes.iloc[1:].iterrows():
        cns = row[4]  # CNS está na quinta coluna (índice 4)
        log_area.insert(tk.END, f"Buscando motivo de alta para CNS: {cns}\n")
        log_area.see(tk.END)
        motivo = obter_motivo_alta(driver, cns, caminho)
        df_pacientes.at[i, df_pacientes.columns[1]] = motivo
        log_area.insert(tk.END, f"Motivo de alta para CNS {cns}: {motivo}\n")
        log_area.see(tk.END)
        time.sleep(2)

    # Salva o CSV atualizado com o motivo de alta
    df_pacientes.to_csv(restos_csv_path, index=False)
    log_area.insert(tk.END, f"Motivos de alta encontrados, CSV atualizado em '{restos_csv_path}'.\n")
    log_area.see(tk.END)
    driver.quit()

#### Executa altas capturadas por CNS
def executa_saidas_cns():
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    restos_atualizado_path = os.path.join(user_dir, 'restos_atualizado.csv')
    saida_manual_path = os.path.join(user_dir, 'saida_manual.csv')

    log_area.insert(tk.END, "Iniciando o navegador Chrome...\n")
    log_area.see(tk.END)
    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)

    log_area.insert(tk.END, "Acessando o sistema SISREG...\n")
    log_area.see(tk.END)
    navegador.get("https://sisregiii.saude.gov.br")

    log_area.insert(tk.END, "Tentando localizar o campo de usuário...\n")
    log_area.see(tk.END)
    usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
    senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
    usuario, senha = ler_credenciais()
    usuario_field.send_keys(usuario)
    senha_field.send_keys(senha)

    log_area.insert(tk.END, "Tentando localizar o botão de login...\n")
    log_area.see(tk.END)
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
    login_button.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
    log_area.insert(tk.END, "Login realizado e navegação para página de Saída/Permanência concluída!\n")
    log_area.see(tk.END)

    # Aguarda e altera o foco para o iframe
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        log_area.insert(tk.END, "Foco alterado para o iframe com sucesso!\n")
        log_area.see(tk.END)
    except TimeoutException as e:
        log_area.insert(tk.END, f"Erro ao tentar acessar o iframe 'f_main': {e}\n")
        log_area.see(tk.END)
        navegador.quit()
        return

    # Aguarda o botão 'PESQUISAR' estar presente e clicável
    try:
        botao_pesquisar_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']")))
        botao_pesquisar_saida.click()
        log_area.insert(tk.END, "Botão PESQUISAR clicado com sucesso!\n")
        log_area.see(tk.END)
        time.sleep(5)
    except TimeoutException as e:
        log_area.insert(tk.END, f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}\n")
        log_area.see(tk.END)
        navegador.quit()
        return

    pacientes_atualizados_df = pd.read_csv(restos_atualizado_path, encoding='utf-8')

    for _, paciente in pacientes_atualizados_df.iterrows():
        nome_paciente = paciente.get('Nome', None)
        motivo_alta = paciente.get('Motivo da Alta', None)
        ficha = paciente.get('Número da Ficha', None)

        if nome_paciente is None or motivo_alta is None or ficha is None:
            log_area.insert(tk.END, "Dados insuficientes para o paciente, pulando para o próximo...\n")
            log_area.see(tk.END)
            continue

        ficha = str(ficha).split('.')[0]

        log_area.insert(tk.END, f"Processando alta para o paciente: {nome_paciente}\n")
        log_area.see(tk.END)
        dar_alta(navegador, wait, motivo_alta, ficha)
        time.sleep(2)

    pacientes_df = pd.read_csv(restos_atualizado_path, encoding='utf-8')
    motivos_desejados = [
        'PERMANENCIA POR OUTROS MOTIVOS',
        'ALTA MELHORADO',
        'ALTA A PEDIDO',
        'ALTA POR OUTROS MOTIVOS',
        'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO',
        'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
        'ENCERRAMENTO ADMINISTRATIVO',
        'ALTA POR EVASAO'
    ]
    restos_df = pacientes_df[~pacientes_df['Motivo da Alta'].isin(motivos_desejados)]
    restos_df.to_csv(saida_manual_path, index=False)
    log_area.insert(tk.END, f"Arquivo '{saida_manual_path}' criado com os pacientes sem motivo de alta desejado.\n")
    log_area.see(tk.END)

    navegador.quit()
    print("Processo de saída concluído para todos os pacientes. \n Pacientes para análise manual gravados.\n")

############################################
#   DEFINIÇÕES DE FUNÇÕES MENU SUPERIOR    #
############################################

# Função para abrir e editar o arquivo config.ini
def abrir_configuracoes():
    def salvar_configuracoes():
        import sys
        import os
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config.ini')
            with open(config_path, 'w') as configfile:
                configfile.write(text_area.get("1.0", tk.END))
            mostrar_popup_conclusao("Configurações salvas com sucesso!")
        except Exception as e:
            mostrar_popup_erro("Erro", f"Erro ao salvar o arquivo: {e}")

    # Cria uma nova janela para editar o arquivo config.ini
    janela_config = tk.Toplevel()
    janela_config.title("Editar Configurações - config.ini")
    janela_config.geometry("500x400")

    # Área de texto para exibir e editar o conteúdo do config.ini
    text_area = scrolledtext.ScrolledText(janela_config, wrap=tk.WORD, width=60, height=20)
    text_area.pack(pady=10, padx=10)

    # Tenta ler o config.ini e exibir no text_area
    import sys
    import os
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config.ini')
        with open(config_path, 'r') as configfile:
            text_area.insert(tk.END, configfile.read())
    except FileNotFoundError:
        mostrar_popup_erro("Erro", "Arquivo config.ini não encontrado!")

    # Botão para salvar as alterações (sempre aparece)
    btn_salvar = tk.Button(janela_config, text="Salvar", command=salvar_configuracoes)
    btn_salvar.pack(pady=10)

# URL do JSON com as versões e links de download do ChromeDriver
CHROMEDRIVER_VERSIONS_URL = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"

# Função para obter a versão do Google Chrome
def obter_versao_chrome():
    try:
        print("Verificando a versão do Google Chrome instalada...")
        process = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True
        )
        version_line = process.stdout.strip().split()[-1]
        print(f"Versão do Google Chrome encontrada: {version_line}")
        return version_line
    except Exception as e:
        mostrar_popup_erro("Erro", f"Erro ao obter a versão do Google Chrome: {e}")
        print(f"Erro ao obter a versão do Google Chrome: {e}")
        return None

# Função para obter a versão do ChromeDriver
def obter_versao_chromedriver():
    try:
        print("Verificando a versão atual do ChromeDriver...")
        process = subprocess.run(
            ['chromedriver', '--version'],
            capture_output=True,
            text=True
        )
        version_line = process.stdout.strip().split()[1]
        print(f"Versão do ChromeDriver encontrada: {version_line}")
        return version_line
    except Exception as e:
        mostrar_popup_erro(f"Erro ao obter a versão do ChromeDriver: {e}")
        print(f"Erro ao obter a versão do ChromeDriver: {e}")
        return None

# Função para consultar o JSON e obter o link de download da versão correta do ChromeDriver
def buscar_versao_chromedriver(versao_chrome):
    try:
        print(f"Buscando a versão compatível do ChromeDriver para o Google Chrome {versao_chrome}...")
        response = requests.get(CHROMEDRIVER_VERSIONS_URL)
        if response.status_code != 200:
            mostrar_popup_erro(f"Erro ao acessar o JSON de versões: Status {response.status_code}")
            print(f"Erro ao acessar o JSON de versões: Status {response.status_code}")
            return None
        
        major_version = versao_chrome.split('.')[0]
        json_data = response.json()
        for version_data in json_data["versions"]:
            if version_data["version"].startswith(major_version):
                for download in version_data["downloads"]["chromedriver"]:
                    if "win32" in download["url"]:
                        print(f"Versão do ChromeDriver encontrada: {version_data['version']}")
                        return download["url"]
        
        mostrar_popup_erro(f"Não foi encontrada uma versão correspondente do ChromeDriver para a versão {versao_chrome}")
        print(f"Não foi encontrada uma versão correspondente do ChromeDriver para o Google Chrome {versao_chrome}")
        return None
    except Exception as e:
        mostrar_popup_erro(f"Erro ao processar o JSON do ChromeDriver: {e}")
        print(f"Erro ao processar o JSON do ChromeDriver: {e}")
        return None

# Função para baixar o ChromeDriver
def baixar_chromedriver(chromedriver_url):
    try:
        print(f"Baixando o ChromeDriver de {chromedriver_url}...")
        response = requests.get(chromedriver_url, stream=True)
        
        if response.status_code != 200:
            mostrar_popup_erro(f"Não foi possível baixar o ChromeDriver: Status {response.status_code}")
            print(f"Não foi possível baixar o ChromeDriver: Status {response.status_code}")
            return
        
        # Salva o arquivo ZIP do ChromeDriver
        with open("chromedriver_win32.zip", "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                print(".", end="", flush=True)  # Imprime pontos para acompanhar o progresso
        print("\nDownload concluído. Extraindo o arquivo ZIP...")
        
        # Extrai o conteúdo do ZIP
        with zipfile.ZipFile("chromedriver_win32.zip", 'r') as zip_ref:
            zip_ref.extractall(".")  # Extrai para a pasta atual

        # Descobre o diretório onde o script está rodando
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        
        # Caminho para o ChromeDriver extraído
        chromedriver_extraido = os.path.join(pasta_atual, "chromedriver-win32", "chromedriver.exe")
        destino_chromedriver = os.path.join(pasta_atual, "chromedriver.exe")

        if os.path.exists(chromedriver_extraido):
            print(f"Movendo o ChromeDriver para {destino_chromedriver}...")
            shutil.move(chromedriver_extraido, destino_chromedriver)
            print("Atualização do ChromeDriver concluída!")
        else:
            print(f"Erro: o arquivo {chromedriver_extraido} não foi encontrado.")

        # Remove o arquivo ZIP após a extração
        os.remove("chromedriver_win32.zip")
        
        mostrar_popup_conclusao("ChromeDriver atualizado com sucesso!")
    except Exception as e:
        mostrar_popup_erro(f"Erro ao atualizar o ChromeDriver: {e}")
        print(f"Erro ao atualizar o ChromeDriver: {e}")

# Função para verificar a versão do Chrome e ChromeDriver e atualizar, se necessário
def verificar_atualizar_chromedriver():
    versao_chrome = obter_versao_chrome()
    versao_chromedriver = obter_versao_chromedriver()
    
    if versao_chrome and versao_chromedriver:
        if versao_chrome.split('.')[0] == versao_chromedriver.split('.')[0]:
            print("Versão do ChromeDriver e Google Chrome são compatíveis.")
            mostrar_popup_conclusao(f"Versão do Chrome ({versao_chrome}) e ChromeDriver ({versao_chromedriver}) são compatíveis.")
        else:
            resposta = messagebox.askyesno("Atualização Necessária", f"A versão do ChromeDriver ({versao_chromedriver}) não é compatível com o Chrome ({versao_chrome}). Deseja atualizar?")
            if resposta:
                chromedriver_url = buscar_versao_chromedriver(versao_chrome)
                if chromedriver_url:
                    baixar_chromedriver(chromedriver_url)

#Função com informações da versão
def mostrar_versao():
    versao = "AUTOMATOR - AUTOREG\nOperação automatizada de Sistemas - SISREG & G-HOSP\nVersão 7.0.0-linux - Maio de 2025\nAutor: Michel R. Paes\nGithub: MrPaC6689\nDesenvolvido com o apoio do ChatGPT 4o\nContato: michelrpaes@gmail.com"
    mostrar_popup_alerta("AutoReg 7.0.0-linux", versao)

# Função para exibir o conteúdo do arquivo README.md
def exibir_leia_me():
    try:
        import sys
        # Descobre o diretório base do script/executável
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        readme_path = os.path.join(base_dir, 'README.md')

        # Verifica se o arquivo README.md existe
        if not os.path.exists(readme_path):
            mostrar_popup_erro("O arquivo README.md não foi encontrado.")
            return
        
        # Lê o conteúdo do arquivo README.md
        with open(readme_path, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        
        # Cria uma nova janela para exibir o conteúdo
        janela_leia_me = tk.Toplevel()
        janela_leia_me.title("Leia-me")
        janela_leia_me.geometry("1000x800")
        
        # Cria uma área de texto com scroll para exibir o conteúdo
        text_area = scrolledtext.ScrolledText(janela_leia_me, wrap=tk.WORD, width=120, height=45)
        text_area.pack(pady=10, padx=10)
        text_area.insert(tk.END, conteudo)
        text_area.config(state=tk.DISABLED)  # Desabilita a edição do texto

        # Adiciona um botão "Fechar" para fechar a janela do Leia-me
        btn_fechar = tk.Button(janela_leia_me, text="Fechar", command=janela_leia_me.destroy)
        btn_fechar.pack(pady=10)
    except Exception as e:
        mostrar_popup_erro(f"Ocorreu um erro ao tentar abrir o arquivo README.md: {e}")

# Função para abrir o arquivo CSV com o programa de planilhas padrão
def abrir_csv(caminho_arquivo):
    # Se o caminho não for absoluto, busque em ~/AutoReg/
    if not os.path.isabs(caminho_arquivo):
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        caminho_arquivo = os.path.join(user_dir, caminho_arquivo)

    try:
        if os.path.exists(caminho_arquivo):
            if os.name == 'nt':  # Windows
                print("Abrindo o arquivo CSV como planilha, aguarde...")
                os.startfile(caminho_arquivo)
            elif os.name == 'posix':  # macOS ou Linux
                print("Abrindo o arquivo CSV como planilha, aguarde...")
                subprocess.call(('xdg-open', caminho_arquivo))
        else:
            print(f"O arquivo {caminho_arquivo} não foi encontrado.")           
    except Exception as e:
        print(f"Não foi possível abrir o arquivo: {e}")

# Função para sair do programa
def sair_programa():
    janela.destroy()
    
##############################################
#   DEFINIÇÕES DE FUNÇÕES MÓDULO INTERNAÇÃO  #
##############################################

# Função de captura dos numeros de ficha de internação
def extrai_codigos_internacao(log_area):
    nomes_fichas = []
    try:
        chrome_options = Options()
        chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
        chrome_options.add_argument("--start-maximized")  
        chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
        chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
        chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
        chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas 
        #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        log_area.insert(tk.END, "Acessando a página de Internação...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        usuario, senha = ler_credenciais()
        usuario_field.send_keys(usuario)
        senha_field.send_keys(senha)
        time.sleep(10)
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        log_area.insert(tk.END, "Login realizado e navegação para página de Internação...\n")

        # Localiza e extrai os dados dos pacientes
        while True:
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas_pacientes:
                nome_paciente = linha.find_element(By.XPATH, "./td[2]").text
                ficha_onclick = linha.get_attribute("onclick")
                ficha = ficha_onclick.split("'")[1]
                nomes_fichas.append((nome_paciente, ficha))
                log_area.insert(tk.END, f"Nome: {nome_paciente}, Ficha: {ficha}\n")
                log_area.see(tk.END)
            
            # Verifica se há próxima página
            try:
                botao_proxima_pagina = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if botao_proxima_pagina.is_displayed():
                    botao_proxima_pagina.click()
                    time.sleep(2)
                else:
                    break
            except NoSuchElementException:
                log_area.insert(tk.END, "Não há próxima página disponível.\n")
                break
    
    except TimeoutException:
        log_area.insert(tk.END, "Erro ao tentar localizar as linhas de pacientes na página atual.\n")
    except Exception as e:
        log_area.insert(tk.END, f"Erro inesperado: {e}\n")
    finally:
        # Salva os dados em um arquivo CSV na pasta ~/AutoReg/
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'codigos_internacao.csv')
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerow(["Nome do Paciente", "Número da Ficha"])
            escritor_csv.writerows(nomes_fichas)
        log_area.insert(tk.END, f"Dados salvos no arquivo '{csv_path}'.\n")
        navegador.quit()
        log_area.insert(tk.END, f"Processo de captura de pacientes a internar concluído. \n Dados salvos no arquivo '{csv_path}'.")
        log_area.see(tk.END)

# Função para atualizar a planilha na interface com o conteúdo do CSV
def atualizar_planilha():
    try:
        user_dir = os.path.expanduser('~/AutoReg')
        csv_path = os.path.join(user_dir, 'codigos_internacao.csv')
        with open(csv_path, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.reader(file)
            next(leitor_csv)  # Pula o cabeçalho
            for linha in leitor_csv:
                treeview.insert('', 'end', values=linha)
        log_area.insert(tk.END, "Planilha atualizada com os dados do CSV.\n")
    except FileNotFoundError:
        log_area.insert(tk.END, f"Erro: O arquivo '{csv_path}' não foi encontrado.\n")

# Função para inicializar o navegador
def iniciar_navegador():
    log_area.insert(tk.END, "Iniciando o navegador Chrome com melhorias de desempenho...\n")
    
    #Define opções do Driver
    chrome_options = Options()
    #chrome_options.add_argument("--start-maximized")  # Abre o navegador maximizado
    chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
    chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
    chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
    chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas  
    #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
    #Roda o chromedriver com o label 'navegador'
    navegador = webdriver.Chrome(options=chrome_options)
    
    #Ajusta a visibilidade da janela do programa
    #janela_internacao.iconify()    # Minimizar a janela
    #janela_internacao.update()     # Atualizar o estado da janela
    #janela_internacao.deiconify()  # Restaurar para garantir visibilidade
    
    return navegador

# Função para realizar o login no SISREG
def realizar_login(navegador, wait, usuario, senha):
    log_area.insert(tk.END, "Acessando a página do SISREG...\n")
    navegador.get("https://sisregiii.saude.gov.br")
    usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
    senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
    usuario_field.send_keys(usuario)
    senha_field.send_keys(senha)
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
    login_button.click()
    try:
        log_area.insert(tk.END, "Verificando se o login foi realizado com sucesso...\n")
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='internar']")))
        log_area.insert(tk.END, "Login realizado com sucesso.\n")
        return True
    except TimeoutException:
        log_area.insert(tk.END, "Erro: Falha ao realizar login, elemento esperado não encontrado.\n")
        navegador.quit()
        return False
    time.sleep(2)

# Função para acessar a página de internação
def acessar_pagina_internacao(navegador, wait):
    try:
        log_area.insert(tk.END, "Tentando localizar o link 'Internação'...\n")
        internacao_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='barraMenu']/ul/li[1]/a")))
        internacao_link.click()
        log_area.insert(tk.END, "Link 'Internação' encontrado e clicado com sucesso.\n")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        log_area.insert(tk.END, "Foco alterado para o iframe com sucesso!\n")
        return True
    except TimeoutException:
        log_area.insert(tk.END, "Erro: O elemento não foi encontrado no tempo limite.\n")
        return False

# Função para executar o JavaScript da ficha do paciente
def executar_ficha(navegador, ficha):
    '''
    Port para Linux. configFicha não estava sendo encontrado.
    Corrigi a função para garantir que o foco seja alterado corretamente para o iframe antes de executar o JavaScript.
    Também adicionei um tempo de espera reduzido para acelerar o fluxo.
    '''
    navegador.switch_to.default_content()
    wait = WebDriverWait(navegador, 10)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    navegador.execute_script(f"configFicha('{ficha}')")
    log_area.insert(tk.END, f"Executando a função configFicha para a ficha: {ficha}\n")
    time.sleep(1)  # Reduzi o tempo de espera para acelerar o fluxo

# Função para capturar uma parte específica do screenshot
def capturar_screenshot_parcial(navegador, frame_print_area):
    navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    log_area.insert(tk.END, "Rolando a página até o final para capturar a imagem da ficha.\n")
    screenshot_png = navegador.get_screenshot_as_png()
    image = Image.open(io.BytesIO(screenshot_png))
    width, height = image.size
    # Crop ajustado para remover as bordas laterais brancas
    cropped_image = image.crop((int(width * 0.2), int(height * 0.2), int(width * 0.8), height))
    cropped_image = cropped_image.resize((1200, 600), Image.LANCZOS)  # Ajusta para caber no frame expandido
    log_area.insert(tk.END, "Print da ficha de internação capturado com sucesso.\n")

    # Exibir o print na interface gráfica em uma área limitada
    img = ImageTk.PhotoImage(cropped_image)
    for widget in frame_print_area.winfo_children():  # Remove qualquer imagem anterior
        widget.destroy()
    lbl_img = tk.Label(frame_print_area, image=img)
    lbl_img.image = img  # Necessário para manter a referência da imagem
    lbl_img.pack(pady=10)
    return navegador  # Retorna o navegador para manter a sessão aberta

# Função para iniciar o processo de internação
def iniciar_internacao(ficha, frame_print_area, log_area):
    global navegador
    try:
        navegador = iniciar_navegador()
        wait = WebDriverWait(navegador, 10)  # Reduzi o tempo de espera padrão para 10 segundos
        usuario, senha = ler_credenciais()  # Função para ler credenciais
        if not realizar_login(navegador, wait, usuario, senha):
            log_area.insert(tk.END, "Falha ao realizar login no SISREG.\n")
            return
        if not acessar_pagina_internacao(navegador, wait):
            log_area.insert(tk.END, "Erro ao acessar a página de internação.\n")
            return
        executar_ficha(navegador, ficha)
        navegador = capturar_screenshot_parcial(navegador, frame_print_area)
        log_area.insert(tk.END, f"Ficha {ficha} processada com sucesso.\n")
    except TimeoutException as e:
        log_area.insert(tk.END, f"Erro: Ocorreu um TimeoutException - {str(e)}\n")
    except NoSuchElementException as e:
        log_area.insert(tk.END, f"Erro: Elemento não encontrado - {str(e)}\n")
    except Exception as e:
        log_area.insert(tk.END, f"Erro inesperado: {str(e)}\n")
    finally:
        log_area.see(tk.END)  # Scroll para o final do log
    
# Função para iniciar o processo de internação com multiplas fichas
def iniciar_internacao_multiplas_fichas(frame_print_area, log_area, entry_data, btn_confirmar_internacao):
    global navegador
    try:
        navegador = iniciar_navegador()
        wait = WebDriverWait(navegador, 10)
        usuario, senha = ler_credenciais()
        if not realizar_login(navegador, wait, usuario, senha):
            log_area.insert(tk.END, "Falha ao realizar login no SISREG.\n")
            return
        if not acessar_pagina_internacao(navegador, wait):
            log_area.insert(tk.END, "Erro ao acessar a página de internação.\n")
            return

        user_dir = os.path.expanduser('~/AutoReg')
        csv_path = os.path.join(user_dir, 'codigos_internacao.csv')
        with open(csv_path, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.reader(file)
            next(leitor_csv)  # Pula o cabeçalho
            for linha in leitor_csv:
                ficha = linha[1]  # Captura o número da ficha da segunda coluna
                try:
                    executar_ficha(navegador, ficha)
                    navegador = capturar_screenshot_parcial(navegador, frame_print_area)
                    log_area.insert(tk.END, f"Ficha {ficha} processada com sucesso.\n")
                    log_area.see(tk.END)

                    # Espera pela entrada da data e confirmação manual antes de seguir para a próxima ficha
                    log_area.insert(tk.END, "Aguardando a confirmação da internação.\n")
                    # Aguarda até que a data seja preenchida e a confirmação seja feita
                    confirmar_evento = threading.Event()

                    def on_confirmar():
                        confirmar_evento.set()

                    entry_data.bind("<Return>", lambda event: on_confirmar())
                    btn_confirmar_internacao.configure(command=on_confirmar)

                    # Espera até que o evento de confirmação seja acionado
                    confirmar_evento.wait()
                    confirmar_internacao(entry_data, ficha, log_area, navegador)

                    # Remove o binding para evitar conflito na próxima iteração
                    entry_data.unbind("<Return>")
                
                except Exception as e:
                    if isinstance(e, NoSuchElementException):
                        log_area.insert(tk.END, f"Erro: Elemento não encontrado - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    elif isinstance(e, TimeoutException):
                        log_area.insert(tk.END, f"Erro: Ocorreu um TimeoutException - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    elif isinstance(e, NoAlertPresentException):
                        log_area.insert(tk.END, f"Erro: Nenhum alerta presente - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    else:
                        log_area.insert(tk.END, f"Erro inesperado: {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    log_area.see(tk.END)
                    navegador.quit()
                    navegador = iniciar_navegador()
                    wait = WebDriverWait(navegador, 10)
                    if not realizar_login(navegador, wait, usuario, senha):
                        log_area.insert(tk.END, "Falha ao realizar login no SISREG ao tentar reiniciar.\n")
                        return
                    if not acessar_pagina_internacao(navegador, wait):
                        log_area.insert(tk.END, "Erro ao acessar a página de internação ao tentar reiniciar.\n")
                        return

    finally:
        log_area.see(tk.END)

# Função para confirmar a internação
def confirmar_internacao(entry_data, ficha, log_area, navegador):
    data_internacao = entry_data.get().strip()
    if not data_internacao or len(data_internacao) < 10:
        mostrar_popup_alerta("Entrada de Dados", "Por favor, insira a data de internação.")
        return

    try:
        wait = WebDriverWait(navegador, 15)
        select_profissional = Select(wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table[2]/tbody/tr[2]/td[2]/select"))))
        opcoes = select_profissional.options[1:-1]
        opcao_aleatoria = random.choice(opcoes)
        select_profissional.select_by_visible_text(opcao_aleatoria.text)
        log_area.insert(tk.END, f"O profissional selecionado foi: {opcao_aleatoria.text}\n")

        data_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")))
        data_field.clear()
        time.sleep(0.3)
        data_field.send_keys(data_internacao)

        # Adiciona ação explícita para clicar no botão "Internar"
        botao_internar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]")))
        botao_internar.click()

        texto_segundo_popup = ""  # Inicializa a variável antes do uso

        # Primeiro alerta
        try:
            alert = navegador.switch_to.alert
            texto_popup = alert.text
            alert.accept()
            log_area.insert(tk.END, f"Primeiro alerta confirmado: {texto_popup}\n")
        except NoAlertPresentException:
            log_area.insert(tk.END, "Nenhum alerta encontrado no primeiro pop-up.\n")

        # Segundo alerta com espera dinâmica
        try:
            WebDriverWait(navegador, 60).until(EC.alert_is_present())  # Aguarda até que o alerta esteja presente
            segundo_alert = navegador.switch_to.alert
            texto_segundo_popup = segundo_alert.text
            segundo_alert.accept()
            log_area.insert(tk.END, f"Segundo alerta confirmado: {texto_segundo_popup}\n")
        except TimeoutException:
            log_area.insert(tk.END, "Nenhum segundo alerta apareceu. Prosseguindo com a operação.\n")

        # Confirma se o segundo alerta foi tratado
        if not texto_segundo_popup:
            log_area.insert(tk.END, "Aviso: A mensagem do segundo popup está vazia ou o popup não apareceu. Verifique o comportamento do sistema, se necessário.\n")

        log_area.insert(tk.END, f"Ficha {ficha} processada. Mensagem do sistema: {texto_segundo_popup}\n")
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        log_area.insert(tk.END, f"Erro durante a internação: {e}\n")
        mostrar_popup_erro(f"Ocorreu um erro durante a internação: {e}")
    finally:
        log_area.see(tk.END)
        entry_data.delete(0, tk.END)
        entry_data.focus_set()

        # Solução adicional para verificar alertas residuais
        try:
            residual_alert = navegador.switch_to.alert
            residual_alert_text = residual_alert.text
            residual_alert.accept()
            log_area.insert(tk.END, f"Alerta residual tratado: {residual_alert_text}\n")
        except NoAlertPresentException:
            log_area.insert(tk.END, "Nenhum alerta residual encontrado.\n")
'''
Bloco inativado no port para Linux.
def bkp_iniciar_internacao_auto(log_area):
    with open('codigos_internacao.csv', mode='r', encoding='utf-8') as file:
        leitor_csv = csv.reader(file)
        next(leitor_csv)  # Pula o cabeçalho
        for linha in leitor_csv:
            ficha = linha[1]  # Captura o número da ficha da segunda coluna
            try:
                chrome_options = Options()
                #chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
                #chrome_options.add_argument("--start-maximized")  
                #chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
                #chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
                #chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
                #chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas 
                navegador = webdriver.Chrome(options=chrome_options)
                wait = WebDriverWait(navegador, 20)
                log_area.insert(tk.END, "Acessando a página de Internação...\n")
                navegador.get("https://sisregiii.saude.gov.br")
                
                # Realiza o login
                usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
                senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
                usuario, senha = ler_credenciais()
                usuario_field.send_keys(usuario)
                senha_field.send_keys(senha)
                time.sleep(5)
                login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
                login_button.click()
                
                wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
                time.sleep(5)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
                log_area.insert(tk.END, "Login realizado e navegação para página de Internação...\n")

                #ABRE A FICHA A SER INTERNADA
                executar_ficha(navegador, ficha)
                log_area.insert(tk.END, f"Ficha {ficha} processada com sucesso.\n")
                log_area.see(tk.END)

                try:
                    # Encontrar todas as TRs que contêm alguma descrição
                    all_trs = navegador.find_elements(By.XPATH, "//tr")

                    tr_solicitacao = None
                    for tr in all_trs:
                        try:
                            if "Data de Solicitação:" in tr.text:
                                tr_solicitacao = tr
                                break
                        except:
                            continue

                    if tr_solicitacao:
                        # Identificar a TR seguinte (onde está a data)
                        tr_data = tr_solicitacao.find_element(By.XPATH, "following-sibling::tr[1]")

                        # Obter a TD correta (terceira coluna)
                        data_element = tr_data.find_element(By.XPATH, "td[3]")

                        # Extração e processamento da data
                        data_text = data_element.text.split(" - ")[0].strip()  # Pega só a data
                        data_original = datetime.strptime(data_text, "%d.%m.%Y")
                        data_internacao = data_original - timedelta(days=2)
                        data_internacao_str = data_internacao.strftime("%d/%m/%Y")

                        log_area.insert(tk.END, f"Data de solicitação encontrada: {data_text}\n")
                        log_area.insert(tk.END, f"Data formatada para inserção: {data_internacao_str}\n")

                    else:
                        log_area.insert(tk.END, "Erro: A TR com 'Data de Solicitação:' não foi encontrada!\n")

                except TimeoutException:
                    log_area.insert(tk.END, "Erro: Timeout ao buscar a TR com 'Data de Solicitação:'!\n")
                except NoSuchElementException:
                    log_area.insert(tk.END, "Erro: Não foi possível localizar a TR com a data!\n")
                except ValueError as e:
                    log_area.insert(tk.END, f"Erro na conversão da data: {e}\n")


                # Preenche a data de internação
                data_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")))
                data_field.clear()
                time.sleep(0.3)
                data_field.send_keys(data_internacao_str)

                # Seleciona aleatoriamente um profissional da lista
                select_profissional = Select(wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table[2]/tbody/tr[2]/td[2]/select"))))
                opcoes = select_profissional.options[1:-1]
                opcao_aleatoria = random.choice(opcoes)
                select_profissional.select_by_visible_text(opcao_aleatoria.text)
                log_area.insert(tk.END, f"O profissional selecionado foi: {opcao_aleatoria.text}\n")                                                

                # Adiciona ação explícita para clicar no botão "Internar"
                botao_internar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]")))
                botao_internar.click()

                texto_segundo_popup = ""  # Inicializa a variável antes do uso

                # Lidar com o primeiro popup de confirmação
                try:
                    
                    WebDriverWait(navegador, 10).until(EC.alert_is_present())  
                    alert = navegador.switch_to.alert
                    texto_popup = alert.text
                    log_area.insert(tk.END, f"Popup detectado: {texto_popup}\n")

                    # Confirma a operação clicando em "OK"
                    alert.accept()
                    log_area.insert(tk.END, "✔️ Botão 'OK' pressionado com sucesso.\n")

                    # Pequena pausa para que o sistema processe a ação
                    time.sleep(2)
                except TimeoutException:
                    log_area.insert(tk.END, "⚠️ Nenhum popup encontrado. Prosseguindo com a operação.\n")
                except Exception as e:
                    log_area.insert(tk.END, f"❌ Erro ao interagir com o popup: {e}\n")


                # Aguarda a possível aparição do segundo popup
                try:
                    WebDriverWait(navegador, 5).until(EC.alert_is_present())  # Tempo reduzido, pois pode não aparecer
                    segundo_alert = navegador.switch_to.alert
                    texto_segundo_popup = segundo_alert.text
                    segundo_alert.accept()
                    log_area.insert(tk.END, f"Segundo alerta confirmado: {texto_segundo_popup}\n")
                except TimeoutException:
                    log_area.insert(tk.END, "Nenhum segundo alerta apareceu. Prosseguindo com a operação.\n")
                except Exception as e:
                    log_area.insert(tk.END, f"Erro ao lidar com o segundo alerta: {e}\n")

                # Verifica se há erro na tela após o primeiro popup
                try:
                    erro_sistema = navegador.find_element(By.XPATH, "//div[contains(text(), 'Erro de Sistema')]")
                    log_area.insert(tk.END, "Erro de Sistema detectado na interface. Processo interrompido.\n")
                except NoSuchElementException:
                    log_area.insert(tk.END, "Nenhum erro de sistema detectado. Continuando operação.\n")

            finally:
                
                log_area.see(tk.END)
'''

def iniciar_internacao_auto(log_area):
    log_area.insert(tk.END, "INICIANDO PROCESSO DE INTERNAÇÃO\n")
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'codigos_internacao.csv')
    with open(csv_path, mode='r', encoding='utf-8') as file:
        leitor_csv = csv.reader(file)
        next(leitor_csv)  # Pula o cabeçalho
        
        # Inicializa o navegador uma única vez antes do loop
        chrome_options = Options()
        chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
        chrome_options.add_argument("--start-maximized")  
        chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
        chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
        chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
        chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas 
        #chrome_options.add_argument("--headless=new")  # <-- Esta linha faz o Chrome rodar oculto
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)

        navegador.get("https://sisregiii.saude.gov.br")

        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        usuario, senha = ler_credenciais()
        usuario_field.send_keys(usuario)
        senha_field.send_keys(senha)
        time.sleep(5)
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(5)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        log_area.insert(tk.END, "Login realizado e navegação para página de Internação...\n")

        try:
            for linha in leitor_csv:
                ficha = linha[1]  # Captura o número da ficha da segunda coluna
                try:
                    log_area.insert(tk.END, f"Acessando a página de Internação para a ficha {ficha}...\n")

                    # ABRE A FICHA A SER INTERNADA
                    executar_ficha(navegador, ficha)
                    #wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='cod_solicitacao_ficha']"))) #Adiconado para esperar a página carregar
                    log_area.insert(tk.END, f"Ficha {ficha} processada com sucesso.\n")
                    log_area.see(tk.END)

                    # Captura a data de solicitação e formata corretamente
                    try:
                        all_trs = navegador.find_elements(By.XPATH, "//tr")
                        tr_solicitacao = None
                        for tr in all_trs:
                            if "Data de Solicitação:" in tr.text:
                                tr_solicitacao = tr
                                break

                        if tr_solicitacao:
                            tr_data = tr_solicitacao.find_element(By.XPATH, "following-sibling::tr[1]")
                            data_element = tr_data.find_element(By.XPATH, "td[3]")
                            data_text = data_element.text.split(" - ")[0].strip()
                            data_original = datetime.strptime(data_text, "%d.%m.%Y")
                            data_internacao = data_original - timedelta(days=2)
                            data_internacao_str = data_internacao.strftime("%d/%m/%Y")

                            log_area.insert(tk.END, f"Data de solicitação encontrada: {data_text}\n")
                            log_area.insert(tk.END, f"Data formatada para inserção: {data_internacao_str}\n")
                        else:
                            log_area.insert(tk.END, "Erro: A TR com 'Data de Solicitação:' não foi encontrada!\n")

                    except (TimeoutException, NoSuchElementException, ValueError) as e:
                        log_area.insert(tk.END, f"Erro na extração da data: {e}\n")

                    # Preenche a data de internação
                    data_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")))
                    data_field.clear()
                    time.sleep(0.3)
                    data_field.send_keys(data_internacao_str)

                    # Seleciona aleatoriamente um profissional
                    select_profissional = Select(wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table[2]/tbody/tr[2]/td[2]/select"))))
                    opcoes = select_profissional.options[1:-1]
                    opcao_aleatoria = random.choice(opcoes)
                    select_profissional.select_by_visible_text(opcao_aleatoria.text)
                    log_area.insert(tk.END, f"O profissional selecionado foi: {opcao_aleatoria.text}\n")

                    # Clica no botão "Internar"
                    botao_internar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]")))
                    botao_internar.click()

                    # Lidar com o primeiro popup de confirmação
                    try:
                        WebDriverWait(navegador, 10).until(EC.alert_is_present())  
                        alert = navegador.switch_to.alert
                        texto_popup = alert.text
                        log_area.insert(tk.END, f"Popup detectado: {texto_popup}\n")
                        alert.accept()
                        log_area.insert(tk.END, "✔️ Botão 'OK' pressionado com sucesso.\n")
                        time.sleep(2)
                    except TimeoutException:
                        log_area.insert(tk.END, "⚠️ Nenhum popup encontrado. Prosseguindo com a operação.\n")
                    except Exception as e:
                        log_area.insert(tk.END, f"❌ Erro ao interagir com o popup: {e}\n")

                    # Aguarda um possível segundo popup
                    try:
                        WebDriverWait(navegador, 60).until(EC.alert_is_present())
                        segundo_alert = navegador.switch_to.alert
                        texto_segundo_popup = segundo_alert.text
                        segundo_alert.accept()
                        log_area.insert(tk.END, f"Segundo alerta confirmado: {texto_segundo_popup}\n")
                    except TimeoutException:
                        log_area.insert(tk.END, "Nenhum segundo alerta apareceu. Prosseguindo com a operação.\n")
                    except Exception as e:
                        log_area.insert(tk.END, f"Erro ao lidar com o segundo alerta: {e}\n")

                    # Verifica se há erro de sistema na tela
                    try:
                        erro_sistema = navegador.find_element(By.XPATH, "//div[contains(text(), 'Erro de Sistema')]")
                        log_area.insert(tk.END, "⚠️ Erro de Sistema detectado. Processo interrompido.\n")
                    except NoSuchElementException:
                        log_area.insert(tk.END, "✔️ Nenhum erro de sistema detectado. Internação realizada com sucesso.\n")
                        #wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']")))
                        time.sleep(10)

                except Exception as e:
                    log_area.insert(tk.END, f"❌ Erro durante a internação da ficha {ficha}: {e}\n")

                finally:
                    log_area.see(tk.END)

        finally:
            navegador.quit()
            log_area.insert(tk.END, "✔️ Internação automática finalizada com sucesso.\n")
            log_area.see(tk.END)


######################################
## CODIFICAÇÃO DA INTERFACE GRAFICA ##
######################################

### INTERFACE MÓDULO ALTA

# Função para redirecionar a saída do terminal para a Text Box
class RedirectOutputToGUI:
    def __init__(self, text_widget):
        self.text_widget = self.text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)  # Auto scroll para o final da Text Box

    def flush(self):
        pass

# Classe para redirecionar a saída do terminal para a interface gráfica
class RedirectOutputToGUI:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()  # Atualiza a interface para exibir o texto imediatamente

    def flush(self):
        pass

### FIM DA INTERFACE MÓDULO ALTA

### INTERFACE MÓDULO INTERNAÇÃO
def interface_internacao():
    global janela_internacao, frame_print_area, entry_data, navegador, btn_confirmar_internacao, log_area
    janela_internacao = tk.Tk()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(imagens.icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela_internacao.iconphoto(True, icone)
    #janela_internacao.state('zoomed')
    janela_internacao.title("AutoReg - v.7.0.0-linux - Módulo de internação ")
    janela_internacao.configure(bg="#ffffff")
    
    # Frame para organizar a interface
    header_frame = tk.Frame(janela_internacao, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 7.0.0-linux", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Sistema automatizado para captura de pacientes a dar alta - SISREG G-HOSP.\nPor Michel R. Paes - Outubro 2025\nMÓDULO INTERNAÇÃO", 
             font=("Helvetica", 14), fg="#ffffff", bg="#4B79A1", justify="center").pack()

    frame_principal = tk.Frame(janela_internacao, bg="#ffffff")
    frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

    # Criando os frames esquerdo e direito para a estrutura da janela
    frame_direito = tk.Frame(frame_principal, bg="#ffffff")
    frame_direito.pack(side=tk.LEFT, fill="both", expand=True)

    frame_esquerdo = tk.Frame(frame_principal, bg="#ffffff")
    frame_esquerdo.pack(side=tk.RIGHT, fill="both", expand=True)

    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)
    button_width = 40

    # Frame dos botões de internação
    frame_sisreg = tk.LabelFrame(frame_esquerdo, text="Internação", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_sisreg.pack(pady=10, fill="x")

    # Botão para extrair códigos de internação
    btn_extrair_codigos = ttk.Button(frame_sisreg, text="Extrair Códigos de Internação", command=lambda: threading.Thread(target=lambda: extrai_codigos_internacao(log_area)).start(), width=button_width)
    btn_extrair_codigos.pack(pady=5)

    # Botão para iniciar a internação com múltiplas fichas
    btn_internar_multiplas = ttk.Button(frame_sisreg, text="Iniciar Internação Múltiplas Fichas", command=lambda: threading.Thread(target=lambda: iniciar_internacao_multiplas_fichas(frame_print_area, log_area, entry_data, btn_confirmar_internacao)).start(), width=button_width)
    btn_internar_multiplas.pack(pady=5)

    # Frame para entrada de dados de internação
    frame_data = tk.LabelFrame(frame_esquerdo, text="Dados de Internação", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_data.pack(fill="x", expand=False, padx=10, pady=5)

    # Campo de entrada para data de internação
    lbl_data = tk.Label(frame_data, text="Data de Internação (dd/mm/aaaa):", font=("Helvetica", 12), bg="#ffffff")
    lbl_data.pack(pady=5)
    entry_data = tk.Entry(frame_data, font=("Helvetica", 12))
    entry_data.pack(pady=5)

    # Função para formatar a data enquanto digita
    def formatar_data(event):
        conteudo = entry_data.get().replace("/", "")  # Remove barras para processar
        novo_conteudo = ""
        if len(conteudo) > 2:
            novo_conteudo = conteudo[:2] + "/"
            if len(conteudo) > 4:
                novo_conteudo += conteudo[2:4] + "/"
                novo_conteudo += conteudo[4:8]  # Ano
            else:
                novo_conteudo += conteudo[2:4]
        else:
            novo_conteudo = conteudo

        entry_data.delete(0, tk.END)
        entry_data.insert(0, novo_conteudo)

    # Associa o evento de tecla ao campo de entrada
    entry_data.bind("<KeyRelease>", formatar_data)

    # Botão para confirmar a internação
    def confirmar_internacao_com_foco():
        threading.Thread(target=lambda: confirmar_internacao(entry_data, '566960502', log_area, navegador)).start()
        
    btn_confirmar_internacao = ttk.Button(frame_data, text="Confirmar Internação", command=confirmar_internacao_com_foco, width=button_width)
    btn_confirmar_internacao.pack(pady=10)

    # Ativa o botão de confirmação ao pressionar Enter
    entry_data.bind("<Return>", lambda event: confirmar_internacao_com_foco())

    # Área de print contida e com dimensões fixas que ocupam toda a altura disponível
    frame_print_area = tk.LabelFrame(frame_direito, text="Print da Ficha de Internação", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_print_area.pack(fill="both", expand=True, padx=10, pady=5)  # Expande verticalmente para ocupar mais espaço
    frame_print_area.configure(width=1200, height=600)  # Ajustando o tamanho do frame para a altura total
    frame_print_area.pack_propagate(False)  # Evita que o frame mude de tamanho conforme o conteúdo

    # Quadro ativo de log de execução
    frame_log = tk.LabelFrame(frame_esquerdo, text="Log de Execução", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_log.pack(fill="both", expand=True, padx=10, pady=5)
    log_area = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD, font=("Helvetica", 10), width=70, height=20)
    log_area.pack(fill="both", expand=True)

    janela_internacao.mainloop()

### FIM DA INTERFACE MÓDULO INTERNAÇÃO
  
### INTERFACE SELEÇÃO DE MÓDULO

# Função para redirecionar a saída do terminal para a Text Box
class RedirectOutputToGUI:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)  # Auto scroll para o final da Text Box

    def flush(self):
        pass

# Função para criar a janela principal e selecionar o módulo
def criar_janela_principal():
    global janela_principal, menubar 
    janela_principal = tk.Tk() 
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(imagens.icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)
    janela_principal.iconphoto(True, icone)
    janela_principal.title("AutoReg - v.7.0.0-linux ") 
    janela_principal.configure(bg="#ffffff")

    janela_principal.protocol("WM_DELETE_WINDOW", lambda: fechar_modulo())
    
    # Header da janela principal
    header_frame = tk.Frame(janela_principal, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    icone_resized = icone.subsample(3, 3)
    
    tk.Label(header_frame, text="AutoReg 7.0.0-linux", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack(side="top")
    tk.Label(header_frame, text="Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Maio 2025", 
             font=("Helvetica", 14), fg="#ffffff", bg="#4B79A1", justify="center").pack()

    # Criação do menu superior
    menubar = tk.Menu(janela_principal)
    janela_principal.config(menu=menubar)

    # Adiciona um submenu "Configurações"
    config_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Configurações", menu=config_menu)
    config_menu.add_command(label="Editar config.ini", command=lambda: abrir_configuracoes())
    # Verifica o sistema operacional
    if platform.system().lower() == "windows":
        config_menu.add_command(label="Verificar e Atualizar ChromeDriver", command=lambda: verificar_atualizar_chromedriver())
    else:
        config_menu.add_command(label="Verificar e Atualizar ChromeDriver", command=lambda: None, state=tk.DISABLED)
    
    #config_menu.add_command(label="Verificar e Atualizar ChromeDriver", command=lambda: verificar_atualizar_chromedriver())

    # Adiciona um submenu "Informações" com "Versão" e "Leia-me"
    info_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Informações", menu=info_menu)
    info_menu.add_command(label="Versão", command=lambda: mostrar_versao())
    info_menu.add_command(label="Leia-me", command=lambda: exibir_leia_me())

    #Menu para alternar entre modulos

    modulo_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Selecionar Módulo", menu=modulo_menu)
    modulo_menu.add_command(label="Rotina de ALTA", command=lambda: mostrar_modulo(frame_selecao, 'alta'))
    modulo_menu.add_command(label="Rotina de INTERNAÇÃO", command=lambda: mostrar_modulo(frame_selecao, 'internacao'))
    
    #Comando para sair    
    menubar.add_command(label="Sair", command=lambda: fechar_modulo())

    # Frame para a seleção do módulo
    frame_selecao = tk.Frame(janela_principal, bg="#ffffff", pady=40)
    frame_selecao.pack(fill="both", expand=True)

    tk.Label(frame_selecao, text="Selecione o Módulo", font=("Helvetica", 24, "bold"), fg="#4B79A1", bg="#ffffff").pack(pady=20)

    # Frame para os botões de seleção e imagens
    botoes_frame = tk.Frame(frame_selecao, bg="#ffffff")
    botoes_frame.pack(pady=20)

    # Decodificar as imagens de base64
    img_alta_buffer = BytesIO(base64.b64decode(imagens.img_alta_data))
    img_alta = Image.open(img_alta_buffer)
    img_alta = img_alta.resize((300, 300), Image.LANCZOS)
    img_alta = ImageTk.PhotoImage(img_alta)

    img_internacao_buffer = BytesIO(base64.b64decode(imagens.img_internacao_data))
    img_internacao = Image.open(img_internacao_buffer)
    img_internacao = img_internacao.resize((300, 300), Image.LANCZOS)
    img_internacao = ImageTk.PhotoImage(img_internacao)

    # Adicionando imagens e botões
    img_alta_label = tk.Label(botoes_frame, image=img_alta, bg="#ffffff")
    img_alta_label.image = img_alta  # Manter uma referência para a imagem
    img_alta_label.grid(row=0, column=0, padx=20, pady=10)

    btn_alta = tk.Button(botoes_frame, text="Módulo Alta", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#87CEEB", command=lambda: mostrar_modulo(frame_selecao, 'alta'), relief="flat", bd=0, highlightthickness=0)
    btn_alta.configure(width=15, height=2)
    btn_alta.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    btn_alta.config(borderwidth=2, relief="raised")
    btn_alta.config(highlightbackground="#87CEEB", activebackground="#87CEFA", activeforeground="#ffffff")

    alta_labelimg_internacao_label = tk.Label(botoes_frame, image=img_internacao, bg="#ffffff")
    alta_labelimg_internacao_label.image = img_internacao  # Manter uma referência para a imagem
    alta_labelimg_internacao_label.grid(row=0, column=1, padx=20, pady=10)

    btn_internacao = tk.Button(botoes_frame, text="Módulo Internação", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#87CEEB", command=lambda: mostrar_modulo(frame_selecao, 'internacao'), relief="flat", bd=0, highlightthickness=0)
    btn_internacao.configure(width=15, height=2)
    btn_internacao.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
    btn_internacao.config(borderwidth=2, relief="raised")
    btn_internacao.config(highlightbackground="#87CEEB", activebackground="#87CEFA", activeforeground="#ffffff")

    botoes_frame.columnconfigure(0, weight=1)
    botoes_frame.columnconfigure(1, weight=1)

    # Rodapé "Powered by"
    footer_frame = tk.Frame(janela_principal, bg="#ffffff", pady=10)
    footer_frame.pack(fill="x", side="bottom")

    tk.Label(footer_frame, text="Powered by:", font=("Helvetica", 12), fg="#4B79A1", bg="#ffffff").pack(side="left", padx=10)

    # Logomarcas no rodapé
    iconebase_data = base64.b64decode(imagens.icone_base64)
    logo_python_data = base64.b64decode(imagens.logo_python)
    logo_chatgpt_data = base64.b64decode(imagens.logo_chatgpt)
    logo_linux_data = base64.b64decode(imagens.logo_linux)

    iconebase_img = ImageTk.PhotoImage(Image.open(BytesIO(iconebase_data)))
    logo_python_img = ImageTk.PhotoImage(Image.open(BytesIO(logo_python_data)))
    logo_chatgpt_img = ImageTk.PhotoImage(Image.open(BytesIO(logo_chatgpt_data)).resize((70, 70), Image.LANCZOS))
    logo_linux_img = ImageTk.PhotoImage(Image.open(BytesIO(logo_linux_data)).resize((140, 70), Image.LANCZOS))

    tk.Label(footer_frame, image=logo_python_img, bg="#ffffff").pack(side="left", padx=5)
    tk.Label(footer_frame, image=logo_chatgpt_img, bg="#ffffff").pack(side="left", padx=5)
    tk.Label(footer_frame, image=logo_linux_img, bg="#ffffff").pack(side="left", padx=5)

    # Manter referências para as imagens do rodapé
    footer_frame.image_logo_python = logo_python_img
    footer_frame.image_logo_chatgpt = logo_chatgpt_img
    footer_frame.image_logo_chatgpt = logo_linux_img

    janela_principal.mainloop()

# Função para exibir o módulo selecionado
def mostrar_modulo(frame_atual, modulo):
    # Fechar todas as janelas secundárias (Toplevel), mantendo a janela principal intacta
    for widget in janela_principal.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()
    
    # Cria a nova interface de acordo com o módulo selecionado
    if modulo == 'alta':
        frame_atual = criar_interface_modulo_alta()  # Cria a interface do módulo 'alta'

    elif modulo == 'internacao':
        frame_atual = criar_interface_modulo_internacao()  # Cria a interface do módulo 'internacao'

    # Retornar a nova referência do frame atual
    return frame_atual

# Função para fechar o módulo e reexibir a janela principal
def fechar_modulo():
    mostrar_popup_conclusao('\nAté Breve!')
    janela_principal.destroy()

# Funções para normalizar o processo autônomo
def iniciar_extracao():
    thread = threading.Thread(target=extrai_codigos, daemon=True)
    thread.start()

def iniciar_atualiza_csv():
    thread = threading.Thread(target=atualiza_csv, daemon=True)
    thread.start()

def iniciar_executa_saidas():
    thread = threading.Thread(target=executa_saidas, daemon=True)
    thread.start()

def iniciar_captura_cns_restos_alta():
    thread = threading.Thread(target=captura_cns_restos_alta, daemon=True)
    thread.start()

def iniciar_motivo_alta_cns():
    thread = threading.Thread(target=motivo_alta_cns, daemon=True)
    thread.start()

def iniciar_executa_saidas_cns():
    thread = threading.Thread(target=executa_saidas_cns, daemon=True)
    thread.start()

def rodar_automatico():
    print("""
        ======================================================================
        
            Iniciando rotina de extração de pacientes internados - SISREG
        
        ======================================================================
        """)
    executar_sisreg()
    confirmar_popup()
    print("""
        ======================================================================
        
             Iniciando rotina de extração de pacientes internados - GHOSP
        
        ======================================================================
        """)
    executar_ghosp()
    confirmar_popup()
    print("""
        ======================================================================
        
                       COMPARANDO DADOS E DETERMINANDO ALTAS
        
        ======================================================================
        """)
    comparar()
    confirmar_popup()
    print("""
        ======================================================================
        
                      CAPTURANDO MOTIVOS DE ALTAS POR PACIENTE
        
        ======================================================================
        """)    
    capturar_motivo_alta()
    confirmar_popup()
    print("""
        ======================================================================
        
                      CAPTURANDO CODIGOS INDIVIDUAIS SISREG
        
        ======================================================================
        """)
    iniciar_extracao()
    confirmar_popup()
    print("""
        ======================================================================
        
                    PREPARANDO PLANILHA PARA PROCESSAR ALTAS
        
        ======================================================================
        """)
    iniciar_atualiza_csv()
    confirmar_popup()
    print("""
        ======================================================================
        
                          EXECUTANDO ALTAS NO SISREG
        
        ======================================================================
        """)
    iniciar_executa_saidas()
    confirmar_popup()
    print("""
        ======================================================================
        
              CAPTURANDO CNS DE PACIENTES CUJO MOTIVO NÃO FOI DETERMINADO
        
        ======================================================================
        """)
    iniciar_captura_cns_restos_alta()
    confirmar_popup()
    print("""
        ======================================================================
        
                      CAPTURANDO MOTIVOS DE ALTA - REVISANDO
        
        ======================================================================
        """)    
    iniciar_motivo_alta_cns()
    confirmar_popup()
    print("""
        ======================================================================
        
                       REEXECUTANDO ALTAS PENDENTES - SISREG
        
        ======================================================================
        """)    
    iniciar_executa_saidas_cns()
    confirmar_popup()
    print("""
        \n
        ======================================================================
        
                             Rotina de Alta Encerrada.
        
        ======================================================================
        """)

def bkp_confirmar_popup():
    # Aguarda a criação e fechamento da janela temporária
    try:
        while True:
            if 'janela_temporaria' in globals() and isinstance(janela_temporaria, tk.Toplevel):
                if not janela_temporaria.winfo_exists():
                    print("Popup fechado. Continuando o fluxo...")
                    del janela_temporaria  # Remove a referência global
                    return
                else:
                    print("Aguardando fechamento do popup...")
                    janela_temporaria.update()  # Processa eventos da janela temporária
            else:
                print("Janela temporária não detectada. Saindo do loop...")
                return
            time.sleep(0.1)  # Pausa para evitar consumo excessivo de CPU
    except Exception as e:
        print(f"Erro ao confirmar popup: {e}")

def confirmar_popup():
    # Aguarda a criação da janela temporária específica e destrói-a após 5 segundos
    try:
        while True:
            # Verifica todas as janelas Toplevel
            for window in tk._default_root.winfo_children():
                if isinstance(window, tk.Toplevel) and window.wm_attributes("-topmost"):
                    print("""
        ======================================================================
                                Etapa finalizada.
""")
                    time.sleep(1)
                    window.destroy()  # Fecha a janela temporária detectada
                    print("""
                        Prosseguindo com rotina de Alta
        ======================================================================

""")
                    return
            time.sleep(0.1)  # Pausa antes de verificar novamente
    except Exception as e:
        print(f"Erro ao confirmar popup: {e}")

# Interface do Módulo Alta
def criar_interface_modulo_alta():
    global janela, menubar, log_area  # Declara a variável 'janela' como global para ser acessada em outras funções
    janela = tk.Toplevel()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(imagens.icone_base64)    
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela.iconphoto(True, icone)
    janela.title("AutoReg - v.7.0.0-linux ")
    #janela.state('zoomed')  # Inicia a janela maximizada
    janela.configure(bg="#ffffff")  # Define uma cor de fundo branca
    janela.config(menu=menubar)

    # Adiciona texto explicativo ou outro conteúdo abaixo do título principal
    header_frame = tk.Frame(janela, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 7.0.0-linux", font=("Helvetica", 18, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Maio 2025\nMÓDULO ALTA", 
             font=("Helvetica", 12), fg="#ffffff", bg="#4B79A1", justify="center").pack()

    # Frame principal para organizar a interface em duas colunas
    frame_principal = tk.Frame(janela, bg="#ffffff")
    frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

    # Frame esquerdo para botões
    frame_esquerdo = tk.Frame(frame_principal, bg="#ffffff")
    frame_esquerdo.pack(side=tk.LEFT, fill="y")

    # Frame direito para a área de texto
    frame_direito = tk.Frame(frame_principal, bg="#ffffff")
    frame_direito.pack(side=tk.RIGHT, fill="both", expand=True)

    # Estilo dos botões
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 10), padding=3)  # Reduz a altura dos botões

    button_width = 40  # Define uma largura fixa para todos os botões

    # Frame para SISREG
    frame_sisreg = tk.LabelFrame(frame_esquerdo, text="SISREG", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_sisreg.pack(pady=10, fill="x")

    btn_sisreg = ttk.Button(frame_sisreg, text="Extrair internados SISREG", command=lambda: threading.Thread(target=executar_sisreg).start(), width=button_width)
    btn_sisreg.pack(side=tk.LEFT, padx=6)

    btn_exibir_sisreg = ttk.Button(frame_sisreg, text="Exibir Resultado SISREG", command=lambda: abrir_csv('internados_sisreg.csv'), width=button_width)
    btn_exibir_sisreg.pack(side=tk.LEFT, padx=6)

    # Frame para G-HOSP
    frame_ghosp = tk.LabelFrame(frame_esquerdo, text="G-HOSP", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_ghosp.pack(pady=10, fill="x")

    btn_ghosp = ttk.Button(frame_ghosp, text="Extrair internados G-HOSP", command=lambda: threading.Thread(target=executar_ghosp).start(), width=button_width)
    btn_ghosp.pack(side=tk.LEFT, padx=6)

    btn_exibir_ghosp = ttk.Button(frame_ghosp, text="Exibir Resultado G-HOSP", command=lambda: abrir_csv('internados_ghosp.csv'), width=button_width)
    btn_exibir_ghosp.pack(side=tk.LEFT, padx=6)

    # Frame para Comparação
    frame_comparar = tk.LabelFrame(frame_esquerdo, text="Comparar e Tratar Dados", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_comparar.pack(pady=10, fill="x")

    btn_comparar = ttk.Button(frame_comparar, text="Comparar e tratar dados", command=lambda: threading.Thread(target=comparar).start(), width=button_width)
    btn_comparar.pack(side=tk.LEFT, padx=6)

    btn_exibir_comparar = ttk.Button(frame_comparar, text="Exibir Resultado da Comparação", command=lambda: abrir_csv('pacientes_de_alta.csv'), width=button_width)
    btn_exibir_comparar.pack(side=tk.LEFT, padx=6)

    # Frame para Capturar Motivo de Alta
    frame_motivo_alta = tk.LabelFrame(frame_esquerdo, text="Capturar Motivo de Alta", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_motivo_alta.pack(pady=10, fill="x")

    btn_motivo_alta = ttk.Button(frame_motivo_alta, text="Capturar Motivo de Alta", command=lambda: threading.Thread(target=capturar_motivo_alta).start(), width=button_width)
    btn_motivo_alta.pack(side=tk.LEFT, padx=6)

    btn_exibir_motivo_alta = ttk.Button(frame_motivo_alta, text="Exibir Motivos de Alta", command=lambda: abrir_csv('pacientes_de_alta.csv'), width=button_width)
    btn_exibir_motivo_alta.pack(side=tk.LEFT, padx=6)

    # Frame para Extrair Códigos Sisreg Internados
    frame_extrai_codigos = tk.LabelFrame(frame_esquerdo, text="Extrair Códigos SISREG", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_extrai_codigos.pack(pady=10, fill="x")

    btn_extrai_codigos = ttk.Button(frame_extrai_codigos, text="Extrair Código SISREG dos Internados", command=lambda: threading.Thread(target=extrai_codigos).start(), width=button_width)
    btn_extrai_codigos.pack(side=tk.LEFT, padx=6)

    btn_exibir_extrai_codigos = ttk.Button(frame_extrai_codigos, text="Exibir Código SISREG dos Internados", command=lambda: abrir_csv('codigos_sisreg.csv'), width=button_width)
    btn_exibir_extrai_codigos.pack(side=tk.LEFT, padx=6)

    # Frame para Atualizar CSV
    frame_atualiza_csv = tk.LabelFrame(frame_esquerdo, text="Atualizar Planilha para Alta", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_atualiza_csv.pack(pady=10, fill="x")

    btn_atualiza_csv = ttk.Button(frame_atualiza_csv, text="Organizar Planilha para Alta", command=lambda: threading.Thread(target=atualiza_csv).start(), width=button_width)
    btn_atualiza_csv.pack(side=tk.LEFT, padx=6)

    btn_exibir_atualiza_csv = ttk.Button(frame_atualiza_csv, text="Exibir Planilha para Alta", command=lambda: abrir_csv('pacientes_de_alta_atualizados.csv'), width=button_width)
    btn_exibir_atualiza_csv.pack(side=tk.LEFT, padx=6)

    # Frame para Executar Altas no SISREG
    frame_executar_altas = tk.LabelFrame(frame_esquerdo, text="Executar Altas no SISREG", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_executar_altas.pack(pady=10, fill="x")

    btn_executar_altas = ttk.Button(frame_executar_altas, text="Executar Altas", command=lambda: threading.Thread(target=executa_saidas).start(), width=button_width)
    btn_executar_altas.pack(side=tk.LEFT, padx=6)

    btn_relacao_pacientes = ttk.Button(frame_executar_altas, text="Relação de pacientes para análise manual", command=lambda: abrir_csv('restos.csv'), width=button_width)
    btn_relacao_pacientes.pack(side=tk.LEFT, padx=6)

    # Frame para Altas Não Executadas a partir do CNS
    frame_altas_pendentes = tk.LabelFrame(frame_esquerdo, text="Tratamento das Altas Não Executadas a partir do CNS", padx=10, pady=10, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_altas_pendentes.pack(pady=10, fill="x")

    # Sub-frames para empilhar os botões em pares
    row1 = tk.Frame(frame_altas_pendentes, bg="#ffffff")
    row1.pack(fill="x", pady=4)
    
    btn_captura_cns_pendentes = ttk.Button(row1, text="Capturar CNS pendentes", command=lambda: threading.Thread(target=captura_cns_restos_alta).start(), width=button_width)
    btn_captura_cns_pendentes.pack(side=tk.LEFT, padx=6)

    btn_exibir_cns_pendentes = ttk.Button(row1, text="Exibir relação de CNS para alta", command=lambda: abrir_csv('restos_atualizado.csv'), width=button_width)
    btn_exibir_cns_pendentes.pack(side=tk.LEFT, padx=6)

    row2 = tk.Frame(frame_altas_pendentes, bg="#ffffff")
    row2.pack(fill="x", pady=4)

    btn_captura_motivo_alta_pendentes = ttk.Button(row2, text="Capturar Motivo de Alta pendentes", command=lambda: threading.Thread(target=motivo_alta_cns).start(), width=button_width)
    btn_captura_motivo_alta_pendentes.pack(side=tk.LEFT, padx=6)

    btn_exibir_motivo_alta_pendentes = ttk.Button(row2, text="Exibir Motivos de Alta", command=lambda: abrir_csv('restos_atualizado.csv'), width=button_width)
    btn_exibir_motivo_alta_pendentes.pack(side=tk.LEFT, padx=6)

    row3 = tk.Frame(frame_altas_pendentes, bg="#ffffff")
    row3.pack(fill="x", pady=4)

    btn_executa_altas_pendentes = ttk.Button(row3, text="Executar Altas pendentes", command=lambda: threading.Thread(target=executa_saidas_cns).start(), width=button_width)
    btn_executa_altas_pendentes.pack(side=tk.LEFT, padx=6)

    btn_exibir_altas_pendentes = ttk.Button(row3, text="Exibir Planilha para alta manual", command=lambda: abrir_csv('saida_manual.csv'), width=button_width)
    btn_exibir_altas_pendentes.pack(side=tk.LEFT, padx=6)

    # Criação do botão "Rodar Automático"
    btn_rodar_automatico = ttk.Button(frame_esquerdo, text="Rodar Automático", command=lambda: threading.Thread(target=rodar_automatico).start(), width=2*button_width + 10)
    btn_rodar_automatico.pack(pady=5)

    # Widget de texto com scroll para mostrar o status
    log_area = ScrolledText(frame_direito, wrap=tk.WORD, height=30, width=80, font=("Helvetica", 12))
    log_area.pack(pady=10, fill="both", expand=True)

    # Redireciona a saída do terminal para a Text Box
    sys.stdout = RedirectOutputToGUI(log_area)

    # Inicia o loop da interface gráfica
    janela.mainloop()

# Interface do Módulo Internação
def criar_interface_modulo_internacao():
    global janela_internacao, frame_print_area, entry_data, navegador, btn_confirmar_internacao, log_area, menubar
    janela_internacao = tk.Toplevel()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(imagens.icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela_internacao.iconphoto(True, icone)
    janela_internacao.title("AutoReg - v.7.0.0-linux - Módulo de Internação")
    #janela_internacao.state('zoomed')
    janela_internacao.configure(bg="#ffffff")
    janela_internacao.config(menu=menubar)

    #Evita que a jenal principal seja chamada junto com popups
    #janela_internacao.wm_attributes("-topmost", 1)
    
    # Depois de estar no topo, desabilita o "topmost" para permitir que os popups sejam visíveis
    #janela_internacao.after(100, lambda: janela_internacao.wm_attributes("-topmost", 0))

    # Quando a janela for fechada, reexibe a janela principal
    #janela_internacao.protocol("WM_DELETE_WINDOW", lambda: fechar_modulo(janela_internacao, janela_principal))

    # Frame para organizar a interface
    header_frame = tk.Frame(janela_internacao, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 7.0.0-linux", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Maio 2025\nMÓDULO INTERNAÇÃO", 
             font=("Helvetica", 14), fg="#ffffff", bg="#4B79A1", justify="center").pack()

    frame_principal = tk.Frame(janela_internacao, bg="#ffffff")
    frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

    # Criando os frames esquerdo e direito para a estrutura da janela
    frame_direito = tk.Frame(frame_principal, bg="#ffffff")
    frame_direito.pack(side=tk.LEFT, fill="both", expand=True)

    frame_esquerdo = tk.Frame(frame_principal, bg="#ffffff")
    frame_esquerdo.pack(side=tk.RIGHT, fill="both", expand=True)

    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)
    button_width = 40

    # Frame dos botões de internação
    frame_sisreg = tk.LabelFrame(frame_esquerdo, text="Internação", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_sisreg.pack(pady=10, fill="x")

    # Botão para extrair códigos de internação
    btn_extrair_codigos = ttk.Button(frame_sisreg, text="Extrair Códigos de Internação", command=lambda: threading.Thread(target=lambda: extrai_codigos_internacao(log_area)).start(), width=button_width)
    btn_extrair_codigos.pack(pady=5)

    # Botão para iniciar a internação com múltiplas fichas
    btn_internar_multiplas = ttk.Button(frame_sisreg, text="Iniciar Internação Múltiplas Fichas", command=lambda: threading.Thread(target=lambda: iniciar_internacao_multiplas_fichas(frame_print_area, log_area, entry_data, btn_confirmar_internacao)).start(), width=button_width)
    btn_internar_multiplas.pack(pady=5)

    # Botão para iniciar a internação com múltiplas fichas
    btn_internar_auto = ttk.Button(frame_sisreg, text="Rodar Internação Automática", command=lambda: threading.Thread(target=lambda: iniciar_internacao_auto(log_area)).start(), width=button_width)
    btn_internar_auto.pack(pady=5)

    # Frame para entrada de dados de internação
    frame_data = tk.LabelFrame(frame_esquerdo, text="Dados de Internação", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_data.pack(fill="x", expand=False, padx=10, pady=5)

    # Campo de entrada para data de internação
    lbl_data = tk.Label(frame_data, text="Data de Internação (dd/mm/aaaa):", font=("Helvetica", 12), bg="#ffffff")
    lbl_data.pack(pady=5)
    entry_data = tk.Entry(frame_data, font=("Helvetica", 12))
    entry_data.pack(pady=5)

    # Função para formatar a data enquanto digita
    def formatar_data(event):
        conteudo = entry_data.get().replace("/", "")  # Remove barras para processar
        novo_conteudo = ""
        if len(conteudo) > 2:
            novo_conteudo = conteudo[:2] + "/"
            if len(conteudo) > 4:
                novo_conteudo += conteudo[2:4] + "/"
                novo_conteudo += conteudo[4:8]  # Ano
            else:
                novo_conteudo += conteudo[2:4]
        else:
            novo_conteudo = conteudo

        entry_data.delete(0, tk.END)
        entry_data.insert(0, novo_conteudo)

    # Associa o evento de tecla ao campo de entrada
    entry_data.bind("<KeyRelease>", formatar_data)

    # Botão para confirmar a internação
    def confirmar_internacao_com_foco():
        threading.Thread(target=lambda: confirmar_internacao(entry_data, '566960502', log_area, navegador)).start()
        
    btn_confirmar_internacao = ttk.Button(frame_data, text="Confirmar Internação", command=confirmar_internacao_com_foco, width=button_width)
    btn_confirmar_internacao.pack(pady=10)

    # Ativa o botão de confirmação ao pressionar Enter
    entry_data.bind("<Return>", lambda event: confirmar_internacao_com_foco())

    # Área de print contida e com dimensões fixas que ocupam toda a altura disponível
    frame_print_area = tk.LabelFrame(frame_direito, text="Print da Ficha de Internação", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_print_area.pack(fill="both", expand=True, padx=10, pady=5)  # Expande verticalmente para ocupar mais espaço
    frame_print_area.configure(width=1200, height=600)  # Ajustando o tamanho do frame para a altura total
    frame_print_area.pack_propagate(False)  # Evita que o frame mude de tamanho conforme o conteúdo

    # Quadro ativo de log de execução
    frame_log = tk.LabelFrame(frame_esquerdo, text="Log de Execução", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_log.pack(fill="both", expand=True, padx=10, pady=5)
    log_area = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD, font=("Helvetica", 10), width=70, height=20)
    log_area.pack(fill="both", expand=True)

    janela_internacao.mainloop()

### FIM DA INTERFACE SELEÇÃO DE MÓDULO
'''
#Controla o fechamento da Splash Screen se utilizada na compilação
if getattr(sys, 'frozen', False):
    import pyi_splash

if getattr(sys, 'frozen', False):
    pyi_splash.update_text("AutoReg 7.0.0-linux")
    pyi_splash.update_text("Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Maio 2025")
    pyi_splash.close()
    pyi_splash.close()
'''
# Inicia a aplicação
criar_janela_principal()


