#                   AUTOREG 4
#    Operação automatizada de Sistemas - SISREG & G-HOSP
#          Versão 4.2.1 - Novembro de 2024
#                 Autor: MrPaC6689
#            Contato michelrpaes@gmail.com
#         Desenvolvido com o apoio do ChatGPT em Python 3.2
#         Informações em README.md. Repositório em Github  
# 
#  V.4.2.1 - Alterações:
#  - Ajustada função executar_multiplas_internacoes() - movidos excepts para o bloco de looping, evitando a quebra do processo em caso de erro ao internar.
#  - Pop-ups concentrados em três funções def - Conclusão, Erro e Alerta - Agora chamam uma janela toplevel temporária paraâncora, evitando arrastar a janela de seleção de modulos de volta ao topo, ou deixando o pop-up escondido atrás da janela ativa.
#  - Convertidos .ico em base64

########################################################
# Importação de funções externas e bibliotecas Python  #
########################################################
import os
import csv
import subprocess
import platform
import unicodedata
import time
import pandas as pd
import re
import configparser
import pygetwindow as gw
import ctypes
import tkinter as tk
import threading
import sys
import requests
import zipfile
import shutil
import random
import io
import PyInstaller
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter.scrolledtext import ScrolledText
from tkinter import PhotoImage
from PIL import Image, ImageTk  # Biblioteca para manipular imagens
import base64
from io import BytesIO
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path

########################################
#   DEFINIÇÕES DE FUNÇÕES GLOBAIS      #
########################################

# String base64 gerada - icone janelas
icone_base64 = """
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
"""

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
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    usuario_sisreg = config['SISREG']['usuario']
    senha_sisreg = config['SISREG']['senha']
    
    return usuario_sisreg, senha_sisreg

########################################
#   DEFINIÇÕES DE FUNÇÕES MÓDULO ALTA  #
########################################

### Definições Herdadas extrator.py

def extrator():
    # Exemplo de uso no script extrator.py
    usuario, senha = ler_credenciais()

    # Caminho para o ChromeDriver
    chrome_driver_path = "chromedriver.exe"

    # Cria um serviço para o ChromeDriver
    service = Service(executable_path=chrome_driver_path)

    # Modo silencioso
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--incognito')

    # Inicializa o navegador (Chrome neste caso) usando o serviço
    driver = webdriver.Chrome(service=service, options=chrome_options)

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
        df.to_csv('internados_sisreg.csv', index=False)
        print("Dados salvos em 'internados_sisreg.csv'.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()

### Definições Interhosp.py
def ler_credenciais_ghosp():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    usuario_ghosp = config['G-HOSP']['usuario']
    senha_ghosp = config['G-HOSP']['senha']
    caminho_ghosp = config['G-HOSP']['caminho']
    
    return usuario_ghosp, senha_ghosp, caminho_ghosp

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
    
    # Determina o diretório onde o executável ou o script está sendo executado
    if getattr(sys, 'frozen', False):
        # Se o programa estiver rodando como executável
        base_dir = os.path.dirname(sys.executable)
    else:
        # Se estiver rodando como um script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho para salvar o novo arquivo sobrescrevendo o anterior na pasta atual
    caminho_novo_arquivo = os.path.join(base_dir, 'internados_ghosp.csv')
    nomes_df.to_csv(caminho_novo_arquivo, index=False)
    
    print(f"Nomes extraídos e salvos em {caminho_novo_arquivo}.")

#Função para extrair internados no G-HOSP
def internhosp():
    usuario, senha, caminho = ler_credenciais_ghosp()

    # Caminho para o ChromeDriver
    chrome_driver_path = "chromedriver.exe"
    # Obtém o caminho da pasta de Downloads do usuário
    pasta_downloads = str(Path.home() / "Downloads")

    print(f"Pasta de Downloads: {pasta_downloads}")

    # Inicializa o navegador (Chrome neste caso) usando o serviço
    service = Service(executable_path=chrome_driver_path)
    
    # Inicializa o navegador (Chrome neste caso) usando o serviço
    driver = webdriver.Chrome(service=service)

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

#def trazer_terminal():
#    # Obtenha o identificador da janela do terminal
#    user32 = ctypes.windll.user32
#    kernel32 = ctypes.windll.kernel32
#    hwnd = kernel32.GetConsoleWindow()
#    
#    if hwnd != 0:
#        user32.ShowWindow(hwnd, 5)  # 5 = SW_SHOW (Mostra a janela)
#        user32.SetForegroundWindow(hwnd)  # Traz a janela para frente

### Funções do motivo_alta.py
def motivo_alta():
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

#Definições para extração do código SISREG dos internados
def extrai_codigos():
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
    navegador.quit()
    mostrar_popup_conclusao("A extração dos códigos SISREG foi concluída com sucesso!")

#Atualiza arquivo CVS para organizar nomes e incluir numeros de internação SISREG    
def atualiza_csv():
    import pandas as pd

    # Carregar os arquivos CSV como DataFrames
    pacientes_de_alta_df = pd.read_csv('pacientes_de_alta.csv', encoding='utf-8')
    codigos_sisreg_df = pd.read_csv('codigos_sisreg.csv', encoding='utf-8')

    # Atualizar os nomes dos pacientes para caixa alta
    pacientes_de_alta_df['Nome'] = pacientes_de_alta_df['Nome'].str.upper()

    # Mesclar os dois DataFrames com base no nome do paciente para adicionar o número da ficha
    pacientes_atualizados_df = pacientes_de_alta_df.merge(codigos_sisreg_df, left_on='Nome', right_on='Nome do Paciente', how='left')

    # Salvar o DataFrame atualizado em um novo arquivo CSV
    pacientes_atualizados_df.to_csv('pacientes_de_alta_atualizados.csv', index=False, encoding='utf-8')

    print("Arquivo 'pacientes_de_alta.csv' atualizado com sucesso!")
    mostrar_popup_conclusao("Arquivo 'pacientes_de_alta.csv' atualizado com sucesso!")

#Função para dar alta individual
def dar_alta(navegador, wait, motivo_alta, ficha):
    print(f"Executando a função configFicha para a ficha: {ficha}")
    navegador.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    navegador.execute_script(f"configFicha('{ficha}')")
    print("Função de Saída/Permanência executada com sucesso!")
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))

    try:
        print(f"Selecionando o motivo de alta: {motivo_alta}")
        motivo_select = wait.until(EC.presence_of_element_located((By.NAME, "co_motivo")))
        select = webdriver.support.ui.Select(motivo_select)
        motivo_mapping = {
            'PERMANENCIA POR OUTROS MOTIVOS': '1.2 ALTA MELHORADO',
            'ALTA MELHORADO': '1.2 ALTA MELHORADO',
            'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO': '3.1 TRANSFERIDO PARA OUTRO ESTABELECIMENTO',
            'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE': '4.1 OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
            'ALTA POR EVASAO': '1.6 ALTA POR EVASAO'
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
    print("Iniciando o navegador Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--window-position=3000,3000")  # Posiciona a janela do navegador fora do campo visual
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)

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
    except TimeoutException as e:
        print(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
        navegador.quit()
        return

    pacientes_atualizados_df = pd.read_csv('pacientes_de_alta_atualizados.csv', encoding='utf-8')

    for _, paciente in pacientes_atualizados_df.iterrows():
        nome_paciente = paciente.get('Nome', None)
        motivo_alta = paciente.get('Motivo da Alta', None)
        ficha = paciente.get('Número da Ficha', None)

        if nome_paciente is None or motivo_alta is None or ficha is None:
            print("Dados insuficientes para o paciente, pulando para o próximo...")
            continue

        print(f"Processando alta para o paciente: {nome_paciente}")
        dar_alta(navegador, wait, motivo_alta, ficha)
        time.sleep(2)

    pacientes_df = pd.read_csv('pacientes_de_alta_atualizados.csv', encoding='utf-8')
    motivos_desejados = [
        'PERMANENCIA POR OUTROS MOTIVOS',
        'ALTA MELHORADO',
        'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO',
        'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
        'ALTA POR EVASAO'
    ]
    restos_df = pacientes_df[~pacientes_df['Motivo da Alta'].isin(motivos_desejados)]
    restos_df.to_csv('restos.csv', index=False)
    print("Arquivo 'restos.csv' criado com os pacientes sem motivo de alta desejado.")

    navegador.quit()
    mostrar_popup_conclusao("Processo de saída concluído para todos os pacientes. \n Pacientes para análise manual gravados.")

# Função para normalizar o nome (remover acentos, transformar em minúsculas)
def normalizar_nome(nome):
    nfkd = unicodedata.normalize('NFKD', nome)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# Função para comparar os arquivos CSV e salvar os pacientes a dar alta
def comparar_dados():
    print("Comparando dados...")
    arquivo_sisreg = 'internados_sisreg.csv'
    arquivo_ghosp = 'internados_ghosp.csv'

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

        with open('pacientes_de_alta.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nome'])
            for nome in sorted(pacientes_a_dar_alta):
                writer.writerow([nome])

        print("\nA lista de pacientes a dar alta foi salva em 'pacientes_de_alta.csv'.")
    else:
        print("\nNenhum paciente a dar alta encontrado!")

# Função para executar o extrator e atualizar o status na interface
def executar_sisreg():
    def run_task():
        try:
            extrator()
            mostrar_popup_conclusao("Extração dos internados SISREG realizada com sucesso!")
        except Exception as e:
            mostrar_popup_erro("Erro", f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()  # Executar a função em um thread separado

# Função para executar a extração do G-HOSP
def executar_ghosp():
    def run_task():
        try:
            internhosp()
            mostrar_popup_conclusao("Extração dos internados G-HOSP realizada com sucesso!")          
        except Exception as e:
            mostrar_popup_erro(f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()

# Função para comparar os dados
def comparar():
    def run_task():
        try:
            comparar_dados()
            mostrar_popup_conclusao("Comparação de dados realizada com sucesso!")
        except Exception as e:
            mostrar_popup_erro(f"Ocorreu um erro: {e}")
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
            mostrar_popup_conclusao("Motivos de alta capturados com sucesso!")
        except Exception as e:
            mostrar_popup_erro(f"Ocorreu um erro: {e}")
    threading.Thread(target=run_task).start()
    janela.after(3000, trazer_janela_para_frente)

############################################
#   DEFINIÇÕES DE FUNÇÕES MENU SUPERIOR    #
############################################

# Função para abrir e editar o arquivo config.ini
def abrir_configuracoes():
    def salvar_configuracoes():
        try:
            with open('config.ini', 'w') as configfile:
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

    try:
        with open('config.ini', 'r') as configfile:
            text_area.insert(tk.END, configfile.read())
    except FileNotFoundError:
        mostrar_popup_erro("Erro", "Arquivo config.ini não encontrado!")

    # Botão para salvar as alterações
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
    versao = "AUTOMATOR - AUTOREG\nOperação automatizada de Sistemas - SISREG & G-HOSP\nVersão 4.2 - Novembro de 2024\nAutor: Michel R. Paes\nGithub: MrPaC6689\nDesenvolvido com o apoio do ChatGPT 4o\nContato: michelrpaes@gmail.com"
    mostrar_popup_alerta("AutoReg 4.2.1", versao)

# Função para exibir o conteúdo do arquivo README.md
def exibir_leia_me():
    try:
        # Verifica se o arquivo README.md existe
        if not os.path.exists('README.md'):
            mostrar_popup_erro("O arquivo README.md não foi encontrado.")
            return
        
        # Lê o conteúdo do arquivo README.md
        with open('README.md', 'r', encoding='utf-8') as file:
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
    try:
        if os.path.exists(caminho_arquivo):
            if os.name == 'nt':  # Windows
                print("Abrindo o arquivo CSV como planilha, aguarde...")
                os.startfile(caminho_arquivo)              
            elif os.name == 'posix':  # macOS ou Linux
                print("Abrindo o arquivo CSV como planilha, aguarde...")
                subprocess.call(('xdg-open' if 'linux' in os.sys.platform else 'open', caminho_arquivo))
        else:
            print("O arquivo {caminho_arquivo} não foi encontrado.")
            mostrar_popup_erro(f"O arquivo {caminho_arquivo} não foi encontrado.")            
    except Exception as e:
        print("Não foi possível abrir o arquivo: {e}")
        mostrar_popup_erro(f"Não foi possível abrir o arquivo: {e}")

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
        chrome_options.add_argument("--start-maximized")  # Abre o navegador maximizado
        chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
        chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
        chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
        chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas 
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
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
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
        # Salva os dados em um arquivo CSV
        with open('codigos_internacao.csv', mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerow(["Nome do Paciente", "Número da Ficha"])
            escritor_csv.writerows(nomes_fichas)
        log_area.insert(tk.END, "Dados salvos no arquivo 'codigos_internacao.csv'.\n")
        navegador.quit()
        mostrar_popup_conclusao("Processo de captura de pacientes a internar concluído. \n Dados salvos no arquivo 'codigos_internacao.csv'.")
        log_area.see(tk.END)

# Função para atualizar a planilha na interface com o conteúdo do CSV
def atualizar_planilha():
    try:
        with open('codigos_internacao.csv', mode='r', encoding='utf-8') as file:
            leitor_csv = csv.reader(file)
            next(leitor_csv)  # Pula o cabeçalho
            for linha in leitor_csv:
                treeview.insert('', 'end', values=linha)
        log_area.insert(tk.END, "Planilha atualizada com os dados do CSV.\n")
    except FileNotFoundError:
        log_area.insert(tk.END, "Erro: O arquivo 'codigos_internacao.csv' não foi encontrado.\n")

# Função para inicializar o navegador
def iniciar_navegador():
    log_area.insert(tk.END, "Iniciando o navegador Chrome com melhorias de desempenho...\n")
    
    #Define opções do Driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Abre o navegador maximizado
    chrome_options.add_argument("--disable-extensions")  # Desabilita extensões para aumentar a velocidade
    chrome_options.add_argument("--disable-gpu")  # Desabilita GPU para melhorar o desempenho em ambientes sem aceleração gráfica
    chrome_options.add_argument("--no-sandbox")  # Pode acelerar o navegador em alguns casos
    chrome_options.add_argument("--disable-dev-shm-usage")  # Resolve problemas de espaço insuficiente em alguns sistemas  
    
    #Roda o chromedriver com o label 'navegador'
    navegador = webdriver.Chrome(options=chrome_options)
    
    #Ajusta a visibilidade da janela do programa
    janela_internacao.iconify()    # Minimizar a janela
    janela_internacao.update()     # Atualizar o estado da janela
    janela_internacao.deiconify()  # Restaurar para garantir visibilidade

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

        with open('codigos_internacao.csv', mode='r', encoding='utf-8') as file:
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
        # Seleciona um item aleatório, ignorando o primeiro e o último
        opcoes = select_profissional.options[1:-1]
        opcao_aleatoria = random.choice(opcoes)
        select_profissional.select_by_visible_text(opcao_aleatoria.text)
        log_area.insert(tk.END, f"O profissional selecionado foi: {opcao_aleatoria.text}\n")

        data_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")))
        data_field.clear()
        time.sleep(0.3)
        data_field.send_keys(data_internacao)
        navegador.execute_script("Internar();")

        try:
            alert = navegador.switch_to.alert
            texto_popup = alert.text
            alert.accept()
            log_area.insert(tk.END, f"Primeiro alerta confirmado: {texto_popup}\n")
        except NoAlertPresentException:
            log_area.insert(tk.END, "Nenhum alerta encontrado no primeiro pop-up.\n")

        try:
            segundo_alert = navegador.switch_to.alert
            texto_segundo_popup = segundo_alert.text
            segundo_alert.accept()
            log_area.insert(tk.END, f"Segundo alerta confirmado: {texto_segundo_popup}\n")
        except NoAlertPresentException:
            log_area.insert(tk.END, "Nenhum segundo alerta encontrado.\n")

        log_area.insert(tk.END, f"Ficha {ficha} processada. Mensagem do sistema: {texto_segundo_popup}\n")
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        log_area.insert(tk.END, f"Erro durante a internação: {e}\n")
        mostrar_popup_erro(f"Ocorreu um erro durante a internação: {e}")
    finally:
        log_area.see(tk.END)
        entry_data.delete(0, tk.END)
        entry_data.focus_set()

######################################
## CODIFICAÇÃO DA INTERFACE GRAFICA ##
######################################

### INTERFACE MÓDULO ALTA

# Função para redirecionar a saída do terminal para a Text Box
class RedirectOutputToGUI:
    def __init__(self, text_widget):
        self.text_widget = text_widget

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

# Interface modulo alta
def criar_interface():
    # Cria a janela principal
    global janela  # Declara a variável 'janela' como global para ser acessada em outras funções
    janela = tk.Tk()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela.iconphoto(True, icone)
    janela.title("AutoReg - v.4.2.1 ")
    janela.state('zoomed')  # Inicia a janela maximizada
    janela.configure(bg="#ffffff")  # Define uma cor de fundo branca

    # Adiciona texto explicativo ou outro conteúdo abaixo do título principal
    header_frame = tk.Frame(janela, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 4.2.1", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Sistema automatizado para captura de pacientes a dar alta - SISREG G-HOSP.\nPor Michel R. Paes - Outubro 2024\nEscolha uma das opções à esquerda", 
             font=("Helvetica", 14), fg="#ffffff", bg="#4B79A1", justify="center").pack()

    # Criação do menu
    menubar = tk.Menu(janela)
    janela.config(menu=menubar)

    # Adiciona um submenu "Configurações"
    config_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Configurações", menu=config_menu)
    config_menu.add_command(label="Editar config.ini", command=lambda: abrir_configuracoes())
    config_menu.add_command(label="Verificar e Atualizar ChromeDriver", command=lambda: verificar_atualizar_chromedriver())

    # Adiciona um submenu "Informações" com "Versão" e "Leia-me"
    info_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Informações", menu=info_menu)
    info_menu.add_command(label="Versão", command=lambda: mostrar_versao())
    info_menu.add_command(label="Leia-me", command=lambda: exibir_leia_me())

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
    style.configure("TButton", font=("Helvetica", 12), padding=10)

    # Frame para manter os botões lado a lado e padronizar tamanho
    button_width = 40  # Define uma largura fixa para todos os botões

    # Frame para SISREG
    frame_sisreg = tk.LabelFrame(frame_esquerdo, text="SISREG", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_sisreg.pack(pady=10, fill="x")

    btn_sisreg = ttk.Button(frame_sisreg, text="Extrair internados SISREG", command=lambda: threading.Thread(target=executar_sisreg).start(), width=button_width)
    btn_sisreg.pack(side=tk.LEFT, padx=6)

    btn_exibir_sisreg = ttk.Button(frame_sisreg, text="Exibir Resultado SISREG", command=lambda: abrir_csv('internados_sisreg.csv'), width=button_width)
    btn_exibir_sisreg.pack(side=tk.LEFT, padx=6)

    # Frame para G-HOSP
    frame_ghosp = tk.LabelFrame(frame_esquerdo, text="G-HOSP", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_ghosp.pack(pady=10, fill="x")

    btn_ghosp = ttk.Button(frame_ghosp, text="Extrair internados G-HOSP", command=lambda: threading.Thread(target=executar_ghosp).start(), width=button_width)
    btn_ghosp.pack(side=tk.LEFT, padx=6)

    btn_exibir_ghosp = ttk.Button(frame_ghosp, text="Exibir Resultado G-HOSP", command=lambda: abrir_csv('internados_ghosp.csv'), width=button_width)
    btn_exibir_ghosp.pack(side=tk.LEFT, padx=6)

    # Frame para Comparação
    frame_comparar = tk.LabelFrame(frame_esquerdo, text="Comparar e Tratar Dados", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_comparar.pack(pady=10, fill="x")

    btn_comparar = ttk.Button(frame_comparar, text="Comparar e tratar dados", command=lambda: threading.Thread(target=comparar).start(), width=button_width)
    btn_comparar.pack(side=tk.LEFT, padx=6)

    btn_exibir_comparar = ttk.Button(frame_comparar, text="Exibir Resultado da Comparação", command=lambda: abrir_csv('pacientes_de_alta.csv'), width=button_width)
    btn_exibir_comparar.pack(side=tk.LEFT, padx=6)

    # Frame para Capturar Motivo de Alta
    frame_motivo_alta = tk.LabelFrame(frame_esquerdo, text="Capturar Motivo de Alta", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_motivo_alta.pack(pady=10, fill="x")

    btn_motivo_alta = ttk.Button(frame_motivo_alta, text="Capturar Motivo de Alta", command=lambda: threading.Thread(target=capturar_motivo_alta).start(), width=button_width)
    btn_motivo_alta.pack(side=tk.LEFT, padx=6)

    btn_exibir_motivo_alta = ttk.Button(frame_motivo_alta, text="Exibir Motivos de Alta", command=lambda: abrir_csv('pacientes_de_alta.csv'), width=button_width)
    btn_exibir_motivo_alta.pack(side=tk.LEFT, padx=6)

    # Frame para Extrair Códigos Sisreg Internados
    frame_extrai_codigos = tk.LabelFrame(frame_esquerdo, text="Extrair Códigos SISREG", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_extrai_codigos.pack(pady=10, fill="x")

    btn_extrai_codigos = ttk.Button(frame_extrai_codigos, text="Extrair Código SISREG dos Internados", command=lambda: threading.Thread(target=extrai_codigos).start(), width=button_width)
    btn_extrai_codigos.pack(side=tk.LEFT, padx=6)

    btn_exibir_extrai_codigos = ttk.Button(frame_extrai_codigos, text="Exibir Código SISREG dos Internados", command=lambda: abrir_csv('codigos_sisreg.csv'), width=button_width)
    btn_exibir_extrai_codigos.pack(side=tk.LEFT, padx=6)

    # Frame para Atualizar CSV
    frame_atualiza_csv = tk.LabelFrame(frame_esquerdo, text="Atualizar Planilha para Alta", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_atualiza_csv.pack(pady=10, fill="x")

    btn_atualiza_csv = ttk.Button(frame_atualiza_csv, text="Organizar Planilha para Alta", command=lambda: threading.Thread(target=atualiza_csv).start(), width=button_width)
    btn_atualiza_csv.pack(side=tk.LEFT, padx=6)

    btn_exibir_atualiza_csv = ttk.Button(frame_atualiza_csv, text="Exibir Planilha para Alta", command=lambda: abrir_csv('pacientes_de_alta_atualizados.csv'), width=button_width)
    btn_exibir_atualiza_csv.pack(side=tk.LEFT, padx=6)

    # Frame para Executar Altas no SISREG
    frame_executar_altas = tk.LabelFrame(frame_esquerdo, text="Executar Altas no SISREG", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_executar_altas.pack(pady=10, fill="x")

    btn_executar_altas = ttk.Button(frame_executar_altas, text="Executar Altas", command=lambda: threading.Thread(target=executa_saidas).start(), width=button_width)
    btn_executar_altas.pack(side=tk.LEFT, padx=6)

    btn_relacao_pacientes = ttk.Button(frame_executar_altas, text="Relação de pacientes para análise manual", command=lambda: abrir_csv('restos.csv'), width=button_width)
    btn_relacao_pacientes.pack(side=tk.LEFT, padx=6)

    # Botão de Sair
    btn_sair = ttk.Button(frame_esquerdo, text="Sair", command=sair_programa, width=2*button_width + 10)  # Largura ajustada para ficar mais largo
    btn_sair.pack(pady=20)

    # Widget de texto com scroll para mostrar o status
    text_area = ScrolledText(frame_direito, wrap=tk.WORD, height=30, width=80, font=("Helvetica", 12))
    text_area.pack(pady=10, fill="both", expand=True)

    # Redireciona a saída do terminal para a Text Box
    sys.stdout = RedirectOutputToGUI(text_area)

    # Inicia o loop da interface gráfica
    janela.mainloop()

### FIM DA INTERFACE MÓDULO ALTA

### INTERFACE MÓDULO INTERNAÇÃO
def interface_internacao():
    global janela_internacao, frame_print_area, entry_data, navegador, btn_confirmar_internacao, log_area
    janela_internacao = tk.Tk()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela_internacao.iconphoto(True, icone)
    janela_internacao.state('zoomed')
    janela_internacao.title("AutoReg - v.4.2.1 - Módulo de internação ")
    janela_internacao.configure(bg="#ffffff")
    
    # Frame para organizar a interface
    header_frame = tk.Frame(janela_internacao, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 4.2.1", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Sistema automatizado para captura de pacientes a dar alta - SISREG G-HOSP.\nPor Michel R. Paes - Outubro 2024\nMÓDULO INTERNAÇÃO", 
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

#Codifica imagens em Base64 para a Janela de Seleção de Módulo
img_alta_data = """
/9j/4AAQSkZJRgABAQEAYABgAAD/4QCCRXhpZgAATU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABgAAAAAQAAAGAAAAABAAKgAgAEAAAAAQAACAKgAwAEAAAAAQAAAwwAAAAAAAD/4Q3uaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pg0KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI+DQoJPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4NCgkJPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6QXR0cmliPSJodHRwOi8vbnMuYXR0cmlidXRpb24uY29tL2Fkcy8xLjAvIj4NCgkJCTxBdHRyaWI6QWRzPg0KCQkJCTxyZGY6U2VxPg0KCQkJCQk8cmRmOmxpIHJkZjpwYXJzZVR5cGU9IlJlc291cmNlIj4NCgkJCQkJCTxBdHRyaWI6Q3JlYXRlZD4yMDIxLTA1LTA1PC9BdHRyaWI6Q3JlYXRlZD4NCgkJCQkJCTxBdHRyaWI6RXh0SWQ+YmRjODk0ZDYtNzNlNC00MGYwLWFkODAtOTRmYWIyODE3OTg1PC9BdHRyaWI6RXh0SWQ+DQoJCQkJCQk8QXR0cmliOkZiSWQ+NTI1MjY1OTE0MTc5NTgwPC9BdHRyaWI6RmJJZD4NCgkJCQkJCTxBdHRyaWI6VG91Y2hUeXBlPjI8L0F0dHJpYjpUb3VjaFR5cGU+DQoJCQkJCTwvcmRmOmxpPg0KCQkJCTwvcmRmOlNlcT4NCgkJCTwvQXR0cmliOkFkcz4NCgkJPC9yZGY6RGVzY3JpcHRpb24+DQoJCTxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyI+DQoJCQk8ZGM6dGl0bGU+DQoJCQkJPHJkZjpBbHQ+DQoJCQkJCTxyZGY6bGkgeG1sOmxhbmc9IngtZGVmYXVsdCI+YWx0YSBob3NwaXRhbGFyPC9yZGY6bGk+DQoJCQkJPC9yZGY6QWx0Pg0KCQkJPC9kYzp0aXRsZT4NCgkJPC9yZGY6RGVzY3JpcHRpb24+DQoJCTxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOnBkZj0iaHR0cDovL25zLmFkb2JlLmNvbS9wZGYvMS4zLyI+DQoJCQk8cGRmOkF1dGhvcj5iZWxhYnVsY2FvPC9wZGY6QXV0aG9yPg0KCQk8L3JkZjpEZXNjcmlwdGlvbj4NCgkJPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIj4NCgkJCTx4bXA6Q3JlYXRvclRvb2w+Q2FudmE8L3htcDpDcmVhdG9yVG9vbD4NCgkJPC9yZGY6RGVzY3JpcHRpb24+DQoJPC9yZGY6UkRGPg0KPC94OnhtcG1ldGE+DQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg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
"""
img_internacao_data = """
/9j/4AAQSkZJRgABAQEAYABgAAD/4QAiRXhpZgAATU0AKgAAAAgAAQESAAMAAAABAAEAAAAAAAD/7AARRHVja3kAAQAEAAAAPAAA/+EDLGh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8APD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4NCjx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDcuMS1jMDAwIDc5LmRhYmFjYmIsIDIwMjEvMDQvMTQtMDA6Mzk6NDQgICAgICAgICI+DQoJPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4NCgkJPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6MEZGOTAyQTQ0RUVGMTFFREE0QkY5Q0ZBQzM5MjEyMTEiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6MEZGOTAyQTM0RUVGMTFFREE0QkY5Q0ZBQzM5MjEyMTEiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDIwMjIgV2luZG93cyI+DQoJCQk8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0iRkUwQTY0NTY5Mzg0REI3ODFEM0E2QkI3ODAxQjExMEEiIHN0UmVmOmRvY3VtZW50SUQ9IkZFMEE2NDU2OTM4NERCNzgxRDNBNkJCNzgwMUIxMTBBIi8+DQoJCTwvcmRmOkRlc2NyaXB0aW9uPg0KCTwvcmRmOlJERj4NCjwveDp4bXBtZXRhPg0KPD94cGFja2V0IGVuZD0ndyc/Pv/bAEMAAgEBAgEBAgICAgICAgIDBQMDAwMDBgQEAwUHBgcHBwYHBwgJCwkICAoIBwcKDQoKCwwMDAwHCQ4PDQwOCwwMDP/bAEMBAgICAwMDBgMDBgwIBwgMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDP/AABEIA88DzwMBIgACEQEDEQH/xAAfAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/AP3jvI/Njr4n/wCCpnwjj8b/AAb1v9zvlSFnX/vmvt64j/d145+1B4PXxH4D1C32b98Lf+g17/D+JdDG05ro0efmdFVcPKD6o/mh1yzbwZ40dvuK7/8As1e5fB/xT/qfnrmP2uPhn/wi/wAQNYt1T/U3LbaxPg34k8qRImf7lf1pRnz0ubukz8J1pVnB92fW+h6w1hcWd7C/zQur1+nH7G/xIXxR4TsJd/30Wvym8J6h9q0tPmr7M/4Jx/FT7LG+ls/zQv8ALX5xxxlvtsI5JfDr+B9zwzjOTEezezVj9HI5PNj3VJHVDwvqH2/T0b/YrQ+b2r+ftm0fpcdh6dakTpUadabTKJJ6r06S4qGgCSnR1GnSpfm9qzqALRTfMo8yswHUU3zKdQBJF2ooi7UUAN2UbKdRQBXuE8yuL8eeH1urd67a5qhrFmstvVR3A+OfjR4OawuHlVPuV5tX1H8aPB63Vu/yV806xpzaXqDq38FbAQJ0qX5vaoKmjk82gBfm9qSOnUUAFSVHUlABF2qSiigAooooAdHU1Q+ZUm+gB1FFFABF2qSo6koAKKbvo30AOooooAf83tR83tR83tR83tQAfN7UtJ83tS0AOTrUidKhqTzfegAooooAKkqOiLtQBJTo6bRQA/5vaj5vak8yl+b2oAPm9qlqL5van76AHUUUUASUU3fTqACiiigAooooAKd5lNooAf8AN7UfN7UnmUvze1AB83tR83tR83tR83tQA9OtOpqdadQAUUUUAFFFFAElFFFAEcveiLtRL3qSgAooooAKKd5lNoAKKKKACiiigAooooAKKKKACiiigCOLtUlFFABRRRQAUUUUAFFFFABRRRQBH5XtRUlRy96ACiiigAqL5vapabsoAZ83tT060z5vaj5vagB79aZ83tR83tSSUANooooA+9bj+tcl8TNL+3+H7lf76NXZP0rJ1yz+12b1OHqck+YmUU00z8Kv+CmHwrbQfi3qTKny3n72vizQ5JPC/i3bs+V3+7X6wf8ABVz4bqdUhvVh+/8AIzV+X3xI8PtpeobtnzJX9X8M4z6xltKfkkfhOfYd0sfKPzPePhXrv2uzRWevdf2X/HjeA/i5Ztv2RXnyN/vV8nfBvxR+7T569m0vVJIri2uon+aF1dW+lb5nhY1qUod0XgsVKnUjNdGftn8G/FC6zocLf30rt/m9q+Wf2I/iwvijwfYN53mfIu6vp+O4+1W9fy7m2Flh8VKlJbH7ZhMRGtSjOPYmkpnmLTKK806Rz9KjfrU1Ry96AC3kqf5vaoKn+b2rOoAfN7UfN7VE/SnVmA/5vakjpfm9qPm9qAFqSo6mTpQAJ0pZI/3dSfN7VHcf0oAhuP61DJH51Pl+/UidaadgOI8eeH/t9m/yfwV8xfFz4dzRag8sSV9j6pp63Udeb+PPh+t/G3yVrGVwPjm4t5LWTbKmyi3/AKV6v8QPhX9/aleV6hp8ml3Dq33qoB1FNjp1ACfN7VLUXze1S0AOTpTqjpydKAHUU/5vamUAFTJ1qGn/ADe1AEtFNTrTqACiiigAoi7UUUASUUUUAN306iigB0dL83tTKf8AN7UALUlRfN7U9OtADqKKKACiLtRRF2oAkooooAanSpfm9qPm9qPm9qAD5vanp1pnze1S0AFFFFABF2ol70UUAOTpTqanSnUAFFFFABRRRQAU/wCb2plP+b2oAPm9qPm9qPm9qPm9qAHp1p1RfN7U9OtADqKKKACiiigAoi7UU5OlADqji7VJRQAUUUUAFFFFABRRRQAUUU/5vagBlFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRUdAB5vvRRRQAUUUUAFR1JUXze1AB83tR83tR83tR83tQAfN7UklL83tSSUANoopr9KAPvx+lU7y34q4/Sq8lc/NZ3Kjtc+If+CnHw7/tT4d3Nwqfvbb5/wAq/JH4weEPNkeVUr91/wBszweviP4d6lDs374Wr8avib4f/eXkez/UuyflX9EeGuO9rgXQb2aPyTjTCuGLjWWzX5Hz98P7xtG1jymf5d9fQPhi8W/09P3lfPfiS3bRtU3fxo9er/CfxB9qtEr9CxFN7nymHqKSPu3/AIJz/EySwvH0uWb/AFL/ACq/vX6QeD9UW/0tGr8av2c/Gn/CG/FCwl37Ipn2NX6xfAvxZ/bPh+Fv9ivwfxCy32eK9suqP1jhHGc+H9nLoz0uiiivzU+sJKjl71JTX6UARRf6up6jp9v/AErOoAmypIo6k2U6OOswIfLp8cdP8r2p8cdADPK9qdsp1P8Am9qAGVHcSU5+lRv1oAjkT+KpN9RySVDQBNJ+9qhqGnLdfLVtOlLL/rK0pgee+LPB6y7/AJK8Q+KnwzUb2VK+pry3W6riPHHg9bqN/k/grQD4zvLNrC4dW+8lN+b2r0f4ufD9rW4aWJPuV5v80W+gB1SVF83tUtABRRRQBJRUcXapKACn/N7Uyn/N7UAPTrTqjqSgAooooAKKKKAJKKanSnUAFFFFABT/AJvamU/5vagA+b2p6daZ83tS0ASUUUUAFEXaiigCSimp0p1ADvMpfm9qiTpUvze1AB83tS0nze1Hze1AC1JUdSUAFFFFADk6U6o6koAKKKKAH/N7Unl0R0vze1AB83tS0nze1LQA7ZTacnWh+tADPm9qWk+b2o+b2oAloqOnb6AHUU3fTqACLtUlRxdqkoAKKKji7UASUUUUAFFFR0AFSVHUlABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRUcvegCSio/N96PN96AHb6bRRQAUUUUAFFFN30AG+mfN7UtJ83tQAfN7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AET9KdT/m9qZQB99P0pr/6qnP0ptc4HAfHDR11Pwvcrt++jV+Nvx98LtoPxM1uzZNn75n/AD+av2z8aWa3WjzL/sV+Sn7fnhf/AIRz40PKqbFuf6V+teF+NaxEqPdHwvG2HUsMpnw98V/DbWtw7bKp/CfXGtbzyq9L+Jnh5b/T3Za8Z0/zNB1z/Zr930ktT8pp1JQmkj6N0vVJIpIbiKT5odr/AJV+mv7DfxQXxJ4PsG3/AMC1+U3g/VP7Q09Pn/gr7G/4Jz/ExtL1N9Llm/1L/KtfBccZZ7fAOVvhdz7rhnGezxahfRn6iWcnmwbv79TVj+C9UW/0dK2K/nSUeWTXmfqqaeqJKa/SjfTqQyOpraoZe9Pt5KiabAuRx/3qk+b2qJOlS/N7Vm1YA+b2o+b2o+b2plIAoqPzfeoZLxTTs2BI/Wo5JKrSXlM8zzafKwJqKI46kqQI6c/Sm0SSebTs2AVDeaf9qjqROtXE61onYDx/4meB1urd/kr5r+IHhNtBvHZU+WvtvxJo63du/wAleIfFj4frLHNtSrA+b/lqROtS65pbaNqDoyfLUFADn60bKdRQAURdqKKAJKanSm+b70+OSgCdOtOqL5van76AHUU3fTqACiiigAi7VJUdSUAFFFFABT/m9qZTvMoAdRTY6dQBJRTd9OoAKKKKACLtUlR1JQA1OlS/N7Uyn/N7UAHze1Hze1Hze1Hze1AC1JTU606gAooooAKkqOpKACiiigAooooAKf8AN7UyigB/ze1Hze1Hze1Hze1AC1JUXze1PTrQAP1pnze1S03ZQAz5vaj5vaj5vaj5vagCWio6dvoAdTt9NooAkoqOLtUlADX6U2pKjoAKkpqdKdQAUUUUAFN306o6AHb6dUdSUAFFFFABRTd9OoAKjqSo/K9qACXvRRRQAUUUUAFFFFABRRTX60AGyjZRvptABSfN7U9+tGygBnze1Hze1Hze1Hze1AB83tR83tR83tR83tQAfN7UklL83tSSUAffD9KdT/m9qgrnAp65H5tm61+Zv/BVTwe1hqFtqip9yb5mr9OLyLzY6+Lf+CnHw7bxH8L9SlVPmhTev4V9lwTi/YZnTv1djwuIcMquBmuyufmhqiLqml7f4tleG+PNDaw1B69s8P3fm2+1vvfxVxnxU8P+bvlVK/p6m/sn4biYu3OUPhXrDS26L/cr3j9nfxv/AMIR8ULC6V9kUz7G/GvmDwncSaNrH9xa9g0fUGi8m4X70PzrXDmFFVabpy2Z6WCrShKM4vY/a39n/wAWLr3h+2bfvV0r1Gvj/wDYP+Kn/CU+D7Bt/wA2xd34V9dWc/m2yNX8t51g3h8VOD7s/csvrqvQjNdianJ0psXapK8k6yOXvRF2ol70UAXI5KdvqvHTqxluBJ5vvTJLiq0l55VZt5rHlR1XswL9xeVlXmqeVVC81BpT8tU/Lku5PmojoVymrHeNK9aVnWbpdm39yt63t/3dNzsySf5vaoJJGp8ki1X+b2rNagS0UUeV7VrGNgCOOrkcdVreOrNZy3AhuP7tcf408P8A2u3f5K7aqeqW/wBqjq1O4HyL8ZPA7WsjsqV5d/qpNtfWPxU8HrdW7/JXzP400NtG1R/7rvVgYtSVF83tS0ASUUUUAFEXaiigCSn/ADe1Mp0dADqcnWm05OtADqKKKACnJ0ptFAElFNfpTaAJKKKKAH/N7UtJ83tR83tQA9OtOqOpKACiiigAi7VJUdOTpQA6nR02igB/ze1Hze1JHS/N7UALUlRfN7UtAElFR0nze1AEtSVCnWpqACo5e9SUUAFFFFABRRRQAU3fTqdHQAvze1LTY6X5vagCWmv1pnze1S0ARfN7UfN7U9+tCdaAGfN7UfN7VLTdlADadvptJ83tQA6OSp6hTrTqADzfeiiigBydKdUdFADn6U6o6cnSgB1R1JTU6UAGynUUUAFRy96kqOXvQAU5OlNooAJe9FFFABRRRQAUUUUAFFFFABTX606mv1oAZ83tT060bKbQBJUdO30z5vagA+b2o+b2o+b2o+b2oAPm9qPm9qPm9qPm9qAD5vakkpfm9qPm9qAPvz5vaoKn+b2qLZXOBFP/AKs14h+1x4TXxH4Dv4tm/fCyV7lcR/u64z4oaGuqaHMuz+Cu7L6vsq8Z9jKvT56bifhFrFnJ4X+IGpaa/wAn2aZk20eKNPXVNL/2tlehft2eA2+HP7QFzLs2W9/8/wDwKuD0+4W/s6/rDLcU8RhqeIj1R+EYzDunWnSl9lnjmsWbWGoV3ngvUPt+np/rP92sT4iaO0M7tVb4dap9luNtehUWlzkw909D7n/4Jz/Ez+y9cm0tn/1L/u6/TjwXqi3+npX4q/APxo3gj4mWF5v2RO/lN+Nfrj+z34wXWdDtm3796L81fhPiFlns8R7aKspL9T9W4RxilR9k90erxdqkqOnJ0r8vPsQ2U2pKjoAPM8uobjUFijqHULjyo657UNY/ebVep5QL+oavWXJcSSyVVj8y/krY0vS6UnoWlYhs9PaX71bFvpa1Ys7Pyo6uxxrUczFIZb2ampv9TTqiuJKkkhuJKZH+9pkklWbeOtJRsgHbKk8ul+b2o+b2qeZgOjjp9EXapKTdwI5e9Mkjp8veo6E7Acz400hbq3b5K+afjZ4Ta1kdlSvrHVLfzbevGfjJoH2q3m+StINsD5a8tt9Oq1rlm1hqjrVPzKsCaimp1p0XagAop2ym0AO31J5lQxdqkoAkopsdOoAdvp1RfN7VLQBHUlNTrTqADzfeiOSiigCSio6koAKf83tTKdHQAvze1LSfN7UfN7UAS0VHTk60AOo833oooAdvp1RxdqkoAd5lHmU2igB/ze1Hze1Rb6l+b2oAPm9qPm9qPm9qPm9qAHp1p1NTrTqAJKbvptFAElFRxdqkoAKKKKACneZTaKAHeZS/N7UynR0AL83tT99M+b2paACpKbvp1ABRRRQA1+tM+b2qWmv1oAbUlNTrTqACiiigAoi7UVJQAUUUUAFFFFABRUcvejzfegCSm7KE6U6gCOiiigAooqSgCOiiigAooooAKKKKACiiigApr9aE606gCL5vaj5valpPm9qAD5vaj5vanp1ptACfN7UfN7UfN7UfN7UAJ5dL83tR83tSR0AfdsfiC1l/jjqaO8jl/jr42s/jpqWjfemrp/C/7Tk03yNN81aywcgPqXzFl/jrN1y3W6snWvNPCfxwXVNm6SvQtL1yPVLf/frL2UqbuB+Yn/BYD4ZyWsdnq0UP/HtN+8b618Z+DtU82NFav1f/AOClnwvXxl8H9VXZ8yQs61+P/he8awvJLdv4H2V/Rvh7jlicrUHvH9T8j4uw6o47n6SRvePNL+1WW6vN9PkbS9Ur2C8jW/0uvK/FFm1hqD19vZSVj5GUnGXMel6HqDfY4bhX+aH56/S/9gP4qf8ACR+D7PdNvljTa3+9X5WfD/VGlt9rPX15/wAE8/iZ/YPjCbS5X+WR96rXxHG2WrE4GTW8f6Z9dwzjnSxUU+uh+sFncfabNHq1XO/D/WF1TR4WV9/yV0G+v5yqxcanKz9bTuOpJP8AV0tFAzG1SPl65u4s2luNuyuwvI6zvsa791AFXS9L8qtuzt1jjqG3t/Lq/F2rGT0G3cfH/q6k+b2qJOlG+lZsQskjVWkkokkptaxAKt2/9KrRx/u6sJ0qZO6AdTo6j2VPbx1mBKnSpfm9qSKOl+b2oAgqOpKJe9VECGSPzY9tcB8TNHWWzmr0Guf8YWf2qzf5a05kB8YfFjS2sNY3Vy1e0fGzwm0sjsqV4zcRtaybWqgJE606OSoY5PNqROtAEm+m0UUAFOTpTaKAHJ0qX5vaok6VL83tQAfN7UfN7UfN7UtACfN7UtFJ83tQBLRRRQAVJUdFAElFFFAD/m9qPm9qTzKX5vagA+b2o+b2o+b2o+b2oAenWjfTPm9qPm9qAJaIu1FFAElFFFABTo6bTvMoAX5vaj5vaj5valoAcnWnVHUlABRRRQAUS96KKACpKjooAkooooAanSpfm9qZT/m9qAD5vaj5vaj5vaj5vagA+b2o+b2o+b2o+b2oAfvp1N2U2gCSio6dvoAdRRRQAUUUUAOTpTqj833qSgAooooAKa/SnUUAR0U7ZTaACLtRL3qSigAopr9KbF2oAkpr9KdUfm+9ABRRRQAUUUUAFFFFABRRRQAUUVHQBJUdO30b6ADfTqi+b2p++gAfrTPm9qfvpnze1AB83tTKa/SnUAR65b/6O9cT/wAJB/ZeseUz16Lrln/o714t8TJJNL1BJf8AvqvYjZ7gfQPwz8QfaY0+ffXuXw/8UNFsXfXyF8B/HK3Xkrvr6f8AA8nmxo1ZV4IC5+0hbrrPgO8ib7ro1fh18UNLXwl8XNYtV+7Hcttr9vPjhJ5Xgub/AHGr8Sf2lJP+L2a3u/57V+r+FtSX7yn0tf8AE/O+Oqa5IT6p/ob3h+8+02f/AACuZ+IGj87lqX4f6xn5a6HxJpf2qzr9a0jKzPzifvQPOvBeofYNQ217T8G/GjeDfiBpt/8AcXeqSN/smvDby3aw1D/gddzoF79rtEauXGUI1IyhLqrHXgazjKL6pn7Yfsx+OF17w3bMr796LXs9fBH/AATr+Mn9u+F7a1Z/3tt+6b8K+6tHvPtVnur+Y+JMDLC4yUWft2V4pV6Cmi7RRRXgnpEdxGtU5I6uT1DLHQAW1TUyOOn1n7MCSqsklOpPm9qqMbAMpIv9ZSbKl+b2qgJY418up/m9qgjkqSspRsrgOi+/Vm3jqtbVcjqAHU2SiSo99ADaZJJSPJ5UlV5LigCbzKp6hb+ZHU3+tqf5vamnYDyT4meE1v7d/kr5s+JHhP8Asa8dtmyvszxRo63Vu9eFfGDwes0DtsrfmugPn1OlTUuoW7afePF9z56ZHQBNRUdSUAFFFFAElOjqNOlOoAdJTqjooAkpPm9qSOl+b2oAfvo30z5vaj5vagCWimp1p1ABUlR05OlADqdHTadHQAvze1Hze1Hze1Hze1AB83tR83tR83tR83tQBLRTU606gAqSo6cnSgB1FFFAD/m9qWk+b2o+b2oAWnJ1pnze1Hze1AEtFNTrTqACiiigCSo6KKAJKKji7U7fQA6nR02igB0lL83tTKKAH/N7UfN7UynR0ASP1pnze1LTn60AM+b2p6daZ83tR83tQBLRTU606gApqdaH60z5vagCWiLtTU606gCSio4u1SUAFFFFABRRRQAVHL3ol70UAFSVHRQBJTdlNooAJe9FFFABRRRQAUUUUAFFFNfrQA6o6T5vaj5vagA+b2o+b2o+b2o+b2oAPm9qPm9qPm9qPm9qAD5vaj5vakkptADX6U6iigDa1X/j3evGfjBpfm2822vY72T93XAfEDT1urN69aLa2A8Z+EfjRtB8WfZ5fk2PX3V8F9cj1TS4WV6/O7xxZyeHfEH2qL93sevq79j/AOKC6zp8KtJ83y7qVZ3QHuvx8vPK8F3P+41fiT+0zeLL8bNb/wCu1ft58VNL/tnwm+3+NP51+Mn7eHgdvBHxsubhvkW/f73+1X6P4bYpUsROm92j4njTCuph4yj0ZwfhPUPst5tr1TT5Vv8AS9teG6Pqn7yNq9a8D6w11Z1+zVV9o/Laa15OhyXjjS2iuHqTwPqjb/K/8drpvHml+bb7q4PS7j+y9Uo+JCi2pH1v+wv8UG8G/EhLNn2RXn9+v1i+FfiBdU0eFt/36/DTwP4ok0HXLDUrd9nkur1+tf7HfxQj8UeE7CVX370WvxzxHyl+7iYrf/gH6bwfjrwdB9D6RopI5PNjRqWvx+Ksfe2I5e9NfrTpe9NfrTEG+m1DvpftH0oAk+b2o+b2qP7R9Kk+b2oAPm9qPm9qPm9qPm9qAFpydaZ83tT061M9gLdvHVr5vaqtv/Wpd9YgOqO4uKJJKp3FxQAXElNTrUP+sqxbxrQA+OPyak+b2o+b2o+b2oAq3lussdedfETw2t1bPXp3l1g+JNL+1W71tHYD45+KHhdrC8dl/v1xtfQfxg8F+bHM2yvBNQ09tLvHiaqAhjqROtM+b2p6daAHVJUcXapKACiiigAop/ze1Hze1AB83tR83tSR0vze1AB83tS0nze1LQBJRTd9OoAKcnSm05OlADqKKKAHR0vze1Mp/wA3tQAfN7UfN7UfN7UfN7UALTt9M+b2o+b2oAlp2+o0606LtQBJRRRQA/5vak/1NNooAd5lL83tTKf83tQA9OtGym1JQAUUUUAFFFFABRRRQA7fTqjpydKAHUUUUAFO8ym0UAP+b2o+b2o+b2o+b2oAPm9qPm9qPm9qPm9qAHp1p1R1JQA1+tM+b2qWmv1oAZ83tUtRfN7U/fQA6pKhTrTqAJKKj833ooAPN96dvptFAElR0eb70UAFFFFAB5XtR5XtRRQAUUUUAFFFFABRRRQAU3ZTqKAIvm9qPm9qPm9qPm9qAD5vaj5vaj5vaj5vagA+b2o+b2o+b2o+b2oAPm9qZT/m9qPm9qAGUUUUAdNrHh9oo64bxZp7eW/yV9D654P82L7lcN4g+GbS/wAFenSkhJ3PkX4qeG/tVs7bKrfs5/ET/hDfEiW7PsXf92vfvGnwTmv7Z9sNfPHxM+D+peCdUe8iWRPnrWzewuY+3tM+KFrrPgv78f3K/M3/AIKgeTqmoQyr95H/AIK9C8P/ALQmoaXvs2eRGT71ee/HzwvdfEa3e4b5/wCOvc4fxCw2LU+7PMzbC+2oOED4/wBP1xorj5v4PvV6d8N9fryjxx4fuPCXiR7eVNi10ngfWGikT95X9DYKsq1FPyPxLGU5Uazi+57lqH+n6f8A8ArzHxJZ/Zbzd/t13/h/UPt9mlYPjzR/N+Za3p2T1MancZ4T1Tzbfbv+avu3/gmv8aGtf+JNcTf6l9kf+7X56eG7z7LefN93+7XtP7PfxEk+HPxAsL9X2RO6pJ+NeJxHlsMXhJ07bI9nJce8PiVN7N6n7keD9YXVNPRq1U/1teOfs3/EmPxR4btmV9+9Fr2OP97X8w4yi6NZwkftdOSnFTjs0EveobmrD9Kr3keI65zQybzUFtf46zpPFixf8tKoeOLxrWJ68t1jxw0W9d9JysB69/wmkf8Az0jq5Z+LI5f46+dbz4kSRSffq54b+KjS3CbnqVJFSPpO31BZY/vVPXnngvxgupxp89dtZ3nmxpVJ3JLtOjqHz6I7imBpW8lTVTt5KfcXHk1E02Ay8uKoSXH7yn3lx5tMt46E7ATW8dW06U2LtRWQElOjqHzfenxyfu6AJaiuIGljqWigDzX4geG1uo3r5v8Aih4Pa2vHbZX2B4g0tbqOvGfip4QWVH+SugD5m/2ak+b2rU8WaG2l3j/79ZFAEydakTpUUclPoAdvp1R05OlAEvze1MoooAKdHTad5lAC/N7UfN7UtFACfN7VLUdFAElFEclFAElFRxdqkoAKf83tTKanSgCX5vaj5vaj5vaj5vagA+b2o+b2o+b2o+b2oAenWnU1OtOoAdvp1R05OlADqKKKACn/ADe1Mp3mUAL83tS0nze1Hze1AD99OqL5valoAkpu+jfTPm9qAH76dUXze1PTrQA6iiigCSio6koAKKKKACn/ADe1Mp/ze1AB83tS0nze1LQA7ZTqbvo30AOopu+nUAFRfN7VLUXze1AD0606ovm9qenWgB1FFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUARfN7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tSeZQAvze1Hze1J5lHmUARv0p1FFAH1/eeH/ADf4Kzbjwmssn3K7P7H/AJzTPsQq41GieU4yT4dw3UfzJXE/FD9n+11nS5v3MfzpXuUdmppmoaet1b7dlXGvJPQTVj8i/wBoz4FSfD7xg9xFDsi31N4a0O313w3t/i2V9e/tofB9dZ8P3FwsP71E3rXxV4D8SNo2uPY3HybH2fPXsU5KSUkRe+h8x/tefCuSxvHulh/1deIaHqDWtwi195/tGeD4fFvhuZkTe2yvhjxBocmg6w9u38D1+3cH5k6tCMZPVH5XxZgeSo5xW56p8L9c82NN1dh4gt/tWn14/wDDvXPst4i/7dezaPIt/p/+/X21Rpao+Rp3lHlZ5XqkbWGoV1vhzVPNgT+8n8VVvHmh+VK7f981j+F7xrW420SkpIKfNDVn6O/8E4/2hGutPTS7q5/0i2fZ/wABr9EfCesLqmno38Vfhp8A/iTN8OfiJYXivsid9ky/7Jr9d/2b/iRH4j8P20u/fvSvwnj7JHQr/WILR/8AAP1jhPNFVoKjN+8j2r/WVHcRr5b0+P8A1dMkjr8xjc+wPPfiZb/6O9fPHizUGivJl319M/ESz82zmr5a+JDtYaw9TUXUDntQ1Cn6XeeVeJ+8qn80tX9Ls28yszQ9i+F+qNL5deyaHcfu68R+Gf7rZXsXh+T/AEZK0WwG959R/bKi+0fSqd5eVoZmxHqnlR0Saostc8l40taWnx+bSTuNqxpW/wC9kq/b2+ahs7f93V+OP93WUtxEb9KbL3p8klVpJKkB1SJ/qqi+b2qxb/0oAlopsdTRdqAK1xGvl7a4zxx4f+127/u67mSP93WbrFn5tvtrVTuB8r/FDwP5sb7U+avJby3a1uHjZPuV9XfEDwt9q3189/Ejwu1heOypVgclHTqbHH5VOoAcnWnVHTk60ATUVHUlABRRT/m9qAFopPm9qPm9qAFopPm9qWgCSiiigApydKbRF2oAkpqdKN9OoAf83tR83tSR0vze1AB83tSR02nR0AOqSovm9qloAKcnSm0UASUUUUAFNTpTqanSgCX5vaj5vaj5vak8ygBfm9qPm9qPm9qPm9qAD5vaj5vaj5vaj5vagA+b2paT5vaj5vagCWiiigAqSiigAooooAanSpfm9qZTo6AF+b2o+b2pPMptAD/m9qenWmfN7UfN7UAPTrTqi+b2p6daAHU1+tOpr9aAGfN7U9OtM+b2o+b2oAlooooAKKKKACiiigAooooAKKKKACimv1ptAElFFFABRRTd9ADqKbvp1AEXze1Hze1Hze1Hze1AB83tR83tR83tSSUAElNoooAKKKKACiio6APvLZTfK9qtbKhqINsBuymyf3akoqwOC+MPhOPXtDmXy9+9Gr8sv2rPAdx8KviQ91EmyKZ6/XrWNP8A7Qs3Vvu18bft4fANfFHhu5kih/0hPu16eBntE56mjsfG0fiiPXvD/wA38afMtfLX7Qng/wCwa491EnyzPXrtnqlx4S1S50248xPJ3Iu+uV+LEces2brX6HwnjHQxCT2Pn8+wyq0G+p4hocjWtwlex/DfUGuo0X79eb+D/hvrHi3WPsthbSTeW/zN5fy1+in/AASz/YksdU8QTal4gto7xrN18uGWPcv/AHzX6VnPEGFwOHdao9ei7n57gsnr4mtyxWnc8K8N/sl+OPjdboug+GNSvFf/AJbeXti/76bFZvxM/wCCcfxQ+EGlvqmpaDJ9lh+eb7PIsrRr/tba/dnw74RsfDWnpDbW8UaR/dVUqPxX4SsfFGjTWt1bwyJMjfLs+/8ALX5PPxUxfttKa5P67n2EuCaLjzc7bP55bN1ij+b5Gr9Av+Ccfxka/wDD8NhcTb5rb5K+Nv8AgpR8I7r9lr9ojUrOK22aXfzNd2bfw7S33f8Avqtv9i740NoOqQ3UT/f27lrvz7iqhmOE5LatBkuVzoVlUjsftb4b1RdUs021qxR14J+z/wDGy38T6XC0U336910u8W6t91flVZJPQ+4iYfjiz82zf/cr5Y+MmjtFrG7/AG6+utct/Nt3r58+NHh7zbh22VnPYo8es9PaWuh0PS/3n3Kfp+l10Oh6XWcTQ6HwXZ+Vs+SvS9Hk8qP79cZ4fs/KjjrrdP2xRp/eqgNaSTn79UriT+Gn+ZRHH+8quYSVh9nbtW9p9usUVU9Pt62LeOobaFIsxx/u6dvpsXaiXvUt3JGSSVWkkp88jVBSAnt5Ks28lU4Ks2/9aALMdTRdqanWnRdqACqd5HVyq1x/SqjuBzHijR1urevGfiZ4PWWN/k3179eW/mR1xPjDw/8Aard/krYD5C13S20vUHXZsWqVemfFDwe3ztXmskflSbaAG0Unze1LQBJTt9Ni7UUASU7zKjTpTqAH/N7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AD0606mp1ofrQA6iiigAp2+m0RdqAJo6PMptP8Am9qAGUUUUAO8ynVHT/m9qAFqSmp1p1AElR+b70UUAHm+9SVHRF2oAkooooAd5lL83tTKdHQAvze1LSfN7UtABSfN7UtJ83tQBLRTU606gAo833oooAkpu+m0UAO306iigAooooAKf83tTKKAH/N7UtJ83tSR0ATUU1OtOoAjpPm9qe/WmfN7UAP306o6cnWgB1FFFABRRRQAUUUUAFFFFADX60b6bSfN7UAS03fTaT5vagBaT5vaj5vaj5vagA+b2p++mfN7UfN7UAHze1Hze1Hze1Hze1AB83tSSUvze1JJQA2iiigAooqOXvQAUUUUAffFR07zKbUQTQBRRRVgRyR1xPxY8Fx69o8ysm/fXbeb71DqFutzbv8A7dOMnGSaA/Hb9uj4HyeB/GE1/bpsV68o+F/wjvvi1qkMSp/o/wDE1fo7+3R8I7fxRocyslcH+yP8G7XRo418mP5K+nw+Yyprng9TjlTUnaZN+zv+xXpvhfT4W+xx7tle5fCfS4fg38QLZY02W95+6k/3v4a7bS7KPS7NFX5KwfHGnrLZ+b/Ej71rzsZj62I/iu4UaEIL92fRtvcefErf3qc/SuA+DHxKtfEnhqGKaaP7Rb/JJ/vCu2bUoYItzSRqvua+ecJJ2OrmR8Sf8Fo/2SIfjV8B5vEFnbRSat4eRpY/70kf8a1+PvwH8WTeEvFCW8vmIqPs21/QZ8b9bsfiLZv4StbmKabUE2zqnzMkbV5vpn/BKT4Q6f4Ye1i8K2P2iZNrXT/NO7f3t1dccQ4wUJI4Y05e0fs9j5P/AGR/i4tpqltF53yvX6C/DfxJ/amnp8/30r82f2iPgPdfsb/HCHTbV5P7IvP9IsZH/uhvmWvsD9lP4or4j0O2bfv+6jVrL3o3idNKSndo+jdQj823rx/4saX+7evYLe4W6t0auA+JGn+bbzVibnidlp37yuk0ezqtb2f+kfc+5W3pdn5VZmhq6PH5Udb1vJWXZx+VHWjb/wBKALkf72rlnb/cqnZx1sWcf3KaVwLlnHVtOlV7f/W1YTpUyViG7kkdOqOkkk8moEQ3H9aip1xJ+8ptOzQFiCrMX+rqtBVikBatqmT/AFVQx06gCSXvUdFFAFe4jasHV9P+1x10NxHVC4jWtKYHjnxE8JrLG9eA+NPDf9l3jts+5X174s0Nbq2rxD4oeD/O3bUrQDxKk+b2qXWNPk0y8dW/4DVaOSgCWpKh8ynUASU5OlNooAkooooAdHS/N7UnmUvze1AB83tT060z5van76ADfTqjqTyvagAooooAIu1T/N7VBUlAD/m9qZRRQAU/5vamU7zKAF+b2paT5vaj5vagCWimp1p1ABRRRQBJRUcXapKACiiigB/ze1Hze1J5lNoAf83tR83tSeZS/N7UALTt9M+b2o+b2oAfvp1RfN7VLQAU5OlNo833oAkoqPzfepKACiiigAooooAKdHTaKAH/ADe1S1DHTqAHP1pnze1L/rKKAE+b2p6daZ83tS0ASUUUUAFN302igAqSovm9qWgCSovm9qfvpnze1AB83tR83tR83tR83tQAfN7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tR83tQAfN7UfN7UfN7UfN7UAHze1Mp3mU2gAooooAKKj833ooAKKKKAPvPzFpnm+9FFABRR5nl0eb70AFMuJP3dPqG8k8q3pN2A8B/askX+w5q8Z+BfjBbW8eL7letftUXn/Erm2/devlTw34kbw5rDy16NOp7mpjy63Ps//hKIYtL81nj+5XlHxY+PFro0bxM/zP8AdWvH/iR+1BJoHhuZ1m+ZEr5j0P8AaAuviL4wf7U+9Um2KtaKnF6tnPWqcuh9XeF/Hmvaprj3Gl3NxbK/3dldhqFv408ZbFvNe1J1/u+Yy/8AoNTfs5+H7W/0e2l/ievZpPDcNhIkuz7lc+Id7oqjTVrnDfs1+D5vhf8AE+G6vPMmivP3TSSyM3zV9jR7ZE3V8k/FT4mWfhfS3bfHC0Pzq3mV1/7L/wC3X4R+MmnvYf2rbJqmn/upo3fb0rz5RlJ2RtzxhuY3/BUL4Ir8SPgVNq1rHu1LQf8ASof90feWvCf+CeniT7fo6Lv+bfX19+0H4w0/Xvh/f2EU0dytzCyNs+b5TXwh8J7xv2ffiBeW6/8AHhM+9f8ApnXVQTUeVnPF2m+XZn6NaXcRxaejtXH/ABA8SWsMbqzx189+LP26NL8N6Xt+0/N/CqferxPxp+25ea9cP9nT5f71VLDSirs6lVTZ9P8A9uWsuoPteuh0uSOUV8W+F/2mLj7ZuuK9s+G/x8t9U8td/wA1Yui0rmiqpux73b/crSs48SVzfhfxRb6zGm199dVp9t+73fw1k1Y0L9nb/u60oP8AViq0FWY5F8unEmRZtqmqnHJVmOSpqEku+m3ElMkkqGSSlGNwFp0UdQxdqmjjanJWQ27kyf62rFV6sVmImTpU1Qp0qagAooooAbc1Tkj82Sr1RSR/vKqMrAZt5b+alcN4w8J/aon+SvQpI1qnqGnrdx1rF3A+Y/iB8M/Mkdtleb6x4PuLCR/41r608SeD1ut9ed+JPAa+Y/y0wPnfy/K+9Tq9M8SfDNZd21K4fVPCVxpcn+p+WgDLqSo6T5vagCWLtUlR0RdqAJKdHTaKAH/N7UfN7UkdL83tQAtO30z5valoAkoqOpKACnJ0ptFAElNfpTqKAI/N96koooAdHS/N7UkdOoAcnWnUUUAFFN306gAi7VJUdSUAFFR0RdqAJKKKKACnR02nR0AL83tR83tR83tR83tQAfN7VLUXze1S0AFFFFABRF2oooAkooooAKf83tTKKACnR02neZQAvze1Hze1Hze1Hze1AD0606mp1p1AEXze1Hze1S1HQAU5OtM+b2o+b2oAloqL5vanp1oAZ83tR83tR83tR83tQAfN7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tR83tQAfN7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1ACR0SU2igAooooAKjl70S96KACnbKbRQAUUUUAfeWym1a2VHJH+7qIy7gVaWOOpdlGyrAbVbUJP8AR6s1X1D/AI9qAPmX9qyRv7Lmr421jXFiuJl3/Nvr7Y/ak0/zdDuf9yvz68cXDReIJl3+X8/3a7oxvG5mYnxIjbXrR4t/yvXmml+G5PC+rpcRfd3/ADV67b+G47+P5pPv0y48F2ctu6t/31TSsDimtT6N/ZH+KC/ZLaKWb+D7tfWNvqkOs6X8r1+Yng/xJJ4M1RFt7nY38K19mfs7/Ei+8R6fCsvyS/3amotjONloeRf8FF/DfiL/AIQu8bRppEbY33K/Pf8AYg+JGqfCr4wag2r3lzNLNN/rHkr9jvix4Tj8W+H5rW6T76V+W37Sv7P83wv+KE11bw7LeabetZapqwVIqSsz7zs/21NLi8JpapDJNcOmxWrldY0O48eW738qbPk3rXz98A5I/EV5bLK+/ZX2f4T0OP8A4RN1VPvw10y9mldEwpyTvM+APjRLfWHjRl8yTyoXrS8PyebZotd5+0h4Dki1S5lSH/gVcf4L0/8A0dNyUpVLsxqaPQ3tH8PyXXzLXYeFtP1DRrhGX7qUeE7eP5Fr0LQ9Djljrb2M3G5xvHQjLlkztvhP8YGsfJilfy2SvpD4f+PIdYtk+fdXxV4s0eTRv9Ii+7XVfA/42XFhqiWsr/7tcNTD2Wp6NLFJrc+4beTzY/lqaOSuQ8B+KP7U09GrrI5K5djvLMclWfMqtHH+8qejchqwkklMokkqGS4o2BK5aqbfWfHcfvKmjvKmTugasXI/7tWKqR3H7yrMdZiJo5KsVVTrVxOtADaKKKACm+XTqKAK8kdQyx1aqOSOto7AZWoW9c3rGhxyj7ldheW9YmqQVQHDah4bX+5XN+IPh5HdR/cr0KSTypPmqz/Zcd1HQB8weNPhfJayO0SVxNxG1rJ5TfeSvrHxR4LW6t/uffrxb4k/Db7LI0qp9ygDzhOtOouLdrWTa33qKADzfenb6bRF2oAm8yjzKbRQA7zKdUdOjoAdTt9M+b2paAJKKbvp1ABUlR0UASUUUUAOjqTfUcdL83tQA/fTaT5vaj5vagA+b2p++mfN7U9OtADqkqOigA833oi7UURdqAJKKKKACiiigB/ze1Hze1Hze1Hze1AB83tS0nze1Hze1AC05OtM+b2p6daAHURdqKIu1AElFFFABRRRQAUUUUAOjpfm9qSOl+b2oAWnb6Z83tR83tQA/fTaT5vaj5vagA+b2o+b2o+b2plAD/m9qPm9qZTd9AEvze1Hze1Rb6N9AEvze1Hze1Hze1Hze1AB83tR83tR83tSSUAL83tR83tUW+nUAO8yjzKbRQA/5vamUUUAFFFFABRRRQBHL3ooooAKKbvptACySUu+mfN7UfN7UAfoDRJGtO2U2ucCOmyVNUdAEdUdS+41aHl1m6xcLa271s02xSdlc8E/akuFtfDlz/uV+Y/xI8YRxeMJl/22r78/bQ8efZfD9zEv3tlfm94s0uaXWJrxvnab7texCLUVc5OZ30O+8H+IIbqNFZPMrtbfQ49Ut0ZYa8T8L+IP7BuEll+fZXqPhP44Wpj2t5aVpGCauT7SXUZ4o+F6y3CXUf3kfdX0P+y/eQ/2fCyzR7k/1kdeSn4kabrMe1vLT/aqHSvFjeF9YS802bb/AHlSuap7xs3ZH29Jrlr4j0/ym8rzUSvnj9qT4Lw+PLN4vJ33CfdatX4Z+PNS8ebJbeGTan3mr2DS/C/9s7GuE+b+LfXJZLVDhJs/P34f/B/XPh74vh3W2yJHr7V+D9u2vaPHC33krT8ceB7GLe2yOpfgfGul+INzfJE77KqNSUo2kWXfGH7Jdv4o097hoY33pXx38VPg3N8L/Hl5prJsVPnj/wB01+sXh+zjutLRdlfM3/BQD4FrdaHbeJrWH97YP5Vxs/55v91v++q56NRqo0znrRaifBkesNpd5tb+Cu8+HfxIh8z7PK/364D4gWbaVefL/Gny1z3w/wDBfiLxbqkzabYX14qfxRR7tlfqHCeW0MTRca8lFW6n4L4qcS5hlNanPL6bm32V9rH1pZ+H18Uaf9z5XrgNY8DzeA/FiSy/8esz/wCs/wCeddt+zvcato2mPpevWdzZ3UPzxtcR/wCsWr/xsktbrQ3VfvJ89edjsltifZR1Xlqe1kfGHtcAsXU92VtU9Nfmj2P4B65JLp6RN8/yf+O17Nb27RRp/t/dr5R/Y/8AHn9qB9Nlf/SLb54/+mkf3f8Ax2vrrS9tzpX+1/DXxeZYGWFrunJWP1TI81pY3DRxFLZj6JJFipn2j61TuLiuFqx7adyaS4+/VaS4qGS88qqFxeUhlm41TypKZb67+8+/WBqGoc1Uj1BoriswO/0/UPNrYjk/d1yXh+886unt5P3daUyZF+3/AK1Zi+/VO3kq1Uy3JJKKjp/ze1SAtFR07zKACSl+b2paT5vagCCSOqGqW6y1o7KbcR/u625gOG1u38r5qh0PVP8ASNtb2t6f+7rkpd1rcVQ0rnZyWa38dcT488FrdW8nyV2Hhu8863Wr+oaPHdW/3KBHx/8AEnwO1hcOypXDf6r733q+qPiR4Djuo3+T79eA+OPA8mjXjsqfLQBzFFH/AC1ooAIu1O302igCSio6koAdHS/N7UnmUeZQA6iiigCSim76dQAVJUdFAElP+b2plFADvMpfm9qZT/m9qAD5vaj5vaj5vaj5vagB6daN9M+b2o+b2oAlopu+m0AWKbvptFADt9OqvUnm+9AElOkptFABT/m9qZT/AJvagB6dabSfN7UfN7UAS0VHRQBYoqOjzfegCSio6KAJKKj833o833oAkp3mVD5vvUlADpKX5vamU3fQBJ5lHmU2igAooooAKKKKACiiigB/ze1Hze1MooAKKKKACo5e9SVHL3oAKIu1FEXagCSiiigBu+jfTaKAHb6dUdFABTX606igCL5vaj5valp2ygBnze1Hze1LSfN7UAfoHvptFFc4BRRUdADZfuVxnxE1j7Lpc1dhc/8AHvJXnXxQk82zdf8AbrsoR5pJmdSVtD4q/a41CS6/0ff/AK568Ev/AAJ9qjdmSvof9pDw22qeIIV/6bLT9L+Cc13p/wDqa7KlRc1mznjF6s+P/FngdbWN9qVyVn4buP7UTa8u2vp/4wfCObS9/wC5+5Xleh+F2/tD5k+aqp1LxuZ3beplafo80Vv9/wCeiOSaw1SHdNIi713f7tdhrGn/AGC3rzTxhJcX9x5Vv5m7/YqeVvRGsp2R+n37L/h7TbXwvYXCpG/nQrXZ/FSS30aT/RfvP96vj/8AYr8ceLtB8Pw2F4kk1un+rb+KOvp+y0e88UbGuPkVK5/ZyUryLpu62Oet9PuNeuNtdJpfhf8AsyCun0fw1HYR7VrSk0xZY6rmNDqvhX4oW/09Flf5k/dN/vV0fjfw5a+KfD15Y3Seda3kLRSr/smvGtL1yTwl4g3f8u918jf9M/8Aar2Dw34oj1nT/mf96n3q4KkHGXMipLmVj8xPih+z3qkvx0fwa0MiS/adkMn/AD0hP3W/75r9AfgJ+zDoPwg8IWdrDaxPMiLubZ/FXCftIeH7XRvHmj+KlT/TNHfZJs/5bwn/AOJr13wX8bPD+veH4biLUrbbs/56V01MZWcOSDaXU8eOBoKr7SulzdLmj4g+GGj69ZtFNZ24/wBox18RftcfBfUPC+oPb6XDvimfyv8Arnn7tfZPiD9oDw3o0bf8TK2kf+7vrxnWPiJpPxV8SPa7433fd/CvY4fzbEYGuq09YrufPcXcL4PN8FLDQtGUuqsmfLvwT8J698OdYtr+8h2NDN95Pu+WfvV9q+C/Giy2afP9/wDrWDrnw/s/7EdWSP7n3q800fx5/YNx9l87/Uvs/Ktc/wA0jmNb2rVmZcB8L/2BhfqalKSf8z1PoGTVPN+7/H92q1xqFcf4b8YNqkSVqveNLXzktz9DSL73bVTuLimSSVQvbzyo/mrOW4ytqFzVO3vP9IqnqmoVW0u8824jqQPSPC8nnba7C0/1dcR4X6pXaWcn7utKZMi/b/0q7VFOlWvN96mW5I/7R9KI5POpnm+9Hm+9SBP83tR83tUcclSfN7UAJHTqbHTqAHbKj8unUU07AUdYs/NjrhvEGn+VJXoskf7uuT8UafzWincqJn+E7jyrhFrtrf7lcHoe6K8rvNP/AHttVibuZviDQ47q3dtteS/ET4frLG/7mvcpI/NjrB8QeH1uo6BHxt438FyaXeOypXMeW0Um1q+mfiB4DW6jf5K8O8aeC5NLuHZU/wB6gDl6KPm8yigApydKbRF2oAkoop/ze1ACR06m+ZTqACnJ1ptO30AOopu+nUAFSVHTk6UAOp0dNooAf83tR83tTKKAH/N7UfN7UkdL83tQAfN7U9OtM+b2o+b2oAe/Wm0nze1P2UACdadTU606gCSio4u1SUAFOjptNTpQBL83tR83tR83tR83tQAfN7UtJ83tR83tQBLRTU606gAooooAKKKKACiLtRRF2oAc/Sm1JUdAElFRxdqkoAKKKKACn/N7UyigAooooAKKbvp1ABRRRQAVHL3qSo5e9ABRRRQA5OlNl70UUAFFFFABRRRQAUUU1+tADqKi+b2o+b2oAe/WmfN7UfN7UnmUAfoF5XtR5vvUlV6yjG4ElR07fTaUgIbz/j3evO/iJH+7f/vuvSLj/VVwfxAt/wCL+5XVhpO5E1pc+dfiZ4Hk1TV4ZVhkdVfe1e6/C/4dx3Wjws8P8HzV0en/AA7tb+0hm2/eRXrsNA0OPSotqfdrDEVLy0FTPBfj5+zvb69o9zLbw/vdlfEln8M2sPFl5bsmzyZmSv1f1PT4722ZWXdvr45+NnwrXwv8aHdU8u31D96v93cKuhWtCxz1afv3R8zeOPhu0Uf3Plqf4B/s5r4t8QebLDvVHr6b8SfBuPVNCRtmytj9m/4dx6NqDxSp86v96tI4jS5tKCOh+HfwLt/DmlJth2MiV1sejra/Ls2V3/8AZccVnt2VyWuR/ZbiinPmKKflrFHUMknk0SSNUNxHWqVwMfxPpf2+3+VKzdL8cXXhLY2/5ofkb/potdJIiyx7a5jxZbwxRybnqJpONmBwH7SHxgj1nw+7Rfd2V8Z/8LgutL8QXNm15JDFM++PZJtWvpb4oeG4dYjmiV/v18nfFD4T3lhqDsqS7f4WrmjW9nIcsLGotUbeqeJLy6k837Tc/P8AxeY1dn8D/iZdeHPGFm0s0j/P826vCtL1y+8L26RX6SfZ/wDnpXQ6X4wWK7hlifem+vRpz5o3OD2MYuzSP0aj+JEeqaP9/wC+lfOXjTxItr4ouGX+/WJ4f+Mjf2P9/wDgrg9c8cSX+uP/ALb1mqaRfM73PrT4R+IGutPhr06OTza8N/Z/kkutPhr2y2rkqWvoejHYsb6y9YuP3f36uSSVz3iC88qOspblGJrGqfvKf4buPOua5vWNTaW421seC7j95UgeteE/ux12+ndK4jwn92Ouz0+WtKZMjUTpVjfVWLtUlVykjvMp1J83tR83tWIEsXanb6ijkqVOlAEvze1PTrTPm9qPm9qAFoopydaAHeV7Vzfin/V10z9K5nxFVRKiYmn2/wDpldnpcf7iub0e3/0iuntP9XWxJO/WoLiOp99QXH9KAOe8QaPHdR1458SPCa+W9e66hJ/o9eXfEjb5T0AfM3ijS/sOoVm103j/AP4+JK5d+tADqIu1FFAElFNTpTfN96AJKd5lRp0p1ADvMp1R06OgBfm9qWk+b2o+b2oAfvo30z5vaj5vagCWLtR5vvRRQAeb707fTaIu1AElO8ym0UAP+b2o+b2o+b2o+b2oAfsp1R07fQA6imp1p1ABF2qSo6PN96AJKKj833qSgB/ze1Hze1Mpu+gCX5vaj5vakjpfm9qAH76NlM+b2p6daAHUUUUAFFFFABTt9NooAJe9FFFADt9OqOnJ0oAdRRRQAUVH5vvUlABUcvepKjoAKPN96KKACjzfeiigB2+nUUUAR+V7UVJUdABRRRQAUUUUAFFFNfrQAb6bSfN7UfN7UAHze1Hze1Hze1JJQAvze1Mpu+nUAfoPJHTJe9TeXTJI65wIKKKKACuc8aaf51u/96uh8yqeuWf2q3etIJqQmrlb4Z6h9v0ONW/1tt+6aupTpXnHgPUP7B8Yvat928+7/vV6TU4j3Z6iiFea/tDfD+PxH4eTUlT/AErTX81f92vSqrX1iuoWckLfdddprOMrMJq60PG/D8lvqnhtN39yuKsvHNv4S8aeU3yLVjX9Zk+F/jC50mf5YXffDv8A7prwT9pvxY2jXCalb/8ALH522f3a6o6mPOnG6Pufw34oh1nTt0T799ZXiSPzfmr5a/Zf/ash1mzS3lm+aP5P9ZX0IPHEOp28bK/y1EYpS0NYtyVhz9Kr3FxVa81yP+/VD+2Fuvu11iLmoag0UD7fnrwT9oD4wXXhiNl2SfP8lfQlvbr/AGW7NXyv+2hrmm6Np7ytNHu3/dSuWpJydiudLc4nQ/jZHqlxtuPk3/erekstP8UR7ZfLf+61fM3jzxhff2ekum2FzNs+9sjrofgf8TNY1STyrq2khZ/79Z8jW5pTqNM9C8cfBO3ljdVSN4n/AIf4ZFrxPxJ8E77w5qDy6XJ8v/PF/u19UW9veX+n/Km9f7r1x/iDTGurhk2bGqfbSpu51xw8auvU8Q07VNWsLfyrizkT/aSun+Hfhu48UeIIfkk27/m312cfwzm1ST7ny1678G/g5HpextlbfWHNHHUwcoS5mz0L4N+D/wCy9LT5Nlehv1qloenrYWyKtTXEi0SLK15O0UdcZ4o1D929dDrF55Ub1574w1j93WctwMS91D/S67PwH+9kSvNI9Q824r0j4d/vdlSB7H4Tjby0rsLCuS8J/wDHujV1tlWlMmRpRdqdvqKOSl31oSOpydKj306OSplsBNHUidar76njkrKzQEqdKl+b2qCnb6QE1FJ83tSeZTSuAXEnlxvWDd7bq43VpahcVX2VpBNAR6XZ/vK1ZJGqtbx+VT5JKsA+0fWmXF5+7qPZTbiP93QBieINU8mOvJfiJ4g/duv8Veo+ILOSX7teaeK/A811I/8At1W6sgPEPGFx9quHrnPm9q9H8W/DO48zd+8ridY8NzaXI+5KnVPUDO+b2p6dabTk60ASJ0p1R0eb70AOTpTqbvo30AOoqPzfenxyUASfN7UfN7UyigB/ze1Hze1J5lHmUASJ1p1QxyU6gCSiLtRRQBJT/m9qg833qSgB/wA3tR83tTKd5lAC/N7UfN7UfN7UfN7UAHze1LSfN7UfN7UAS0UUUAFEXaiigCSiiigAp/ze1Mp0dAC/N7U9OtM+b2paAJKKbvp1ABTU60b6bQBJRRRQAUUUUAFFN306gAooooAIu1SVHR5vvQBJRRUfm+9ABL3ooooAKkqOigCSo4u1FN30AOopu+jfQA6im76bQAUnze1Hze1Hze1AB83tR83tR83tR83tQAfN7UfN7UfN7UnmUAElNoooAKKjooA/RCoX6VNTn61zgVajqZ+lNoAr0kn72PbU0kdN+b2rT2gHC+NNLa1k+0Rf61K7fwh4jXxHokNx/H92Rf7jVmeINPW/s65Lwn4j/wCEI8SPb3D/AOi3nyf9c2rapHnp+ZOzPWKKjgkWUbl+7UlefG5R4Z+2f8K7jxn4G/tTS/8AkKaV88e3/lov8S18H+JPHDeKNLmt7pP3v+qkV/71fqrq9ouoafIrfxJX55ftofA//hA/iI+rWEOy1v3/AHy/7VbKV1Y5+Vqdz5g8N/2p8OfFD3Fq8n2d337Ur6c+Ffx0mutPTdNXB+F/C9vrMfmt86vW3efDttGj821/36nmknqdHKktD0jxT8dP7Ls0Zn+Wt74J/ET/AIS28Rvv/wB6vlD4qeKJIdPe3lSRG/vV3v7K/wAULfR7e2WWb/eauqnUXLqTI+t/iBrDaLoc219nyfLX5v8A7THjS68UfExLdrmR4oZt/wDs19XftEftSaTovht/Nuf+WP8Az0r8qfi5+1BdeKPHl5LpNtI6o7IrVz4htLQ78vjCcmp9D7AsPEFrFoaLN5f3P92mfDvVI9f8aQxWab1V/mZK8Q/Zr/Z48eftI3kMuqX9zZ6a/wB2GL5d9ffnwH/YctfhpZwyqkjsn3mesYU6ktWx1ZU07RR6B8O/CcN1pabk2fJVXxJ8J7W6uNypXoun6GujWe1fvJWbrEddbipROfVHAaP8OLewk3V22h2cdhGirHVP/lpVyzk8o0o2irIJSclZm9Hcfu6rahcVW+2/5zVDVNUWgkzfEmqeXG9eY+MNYrqvFmsffryvxZrHm3D1MtwJtLvPNvE216/8NfuR14d4bvPNuE/369y+Gci/uakD2fwt/wAe9dZZ/wCqrl/DH/HvXQ2n+rrSmTI046X5vaok6U6tCR/ze1LUO+l+0fSgCzHJT45KrR3FSJ1qZRuBbjkp9U4u1TR1PswLCdKH6UJ0pZI/OqY7gU5I/wB5SJ0q0/8Aqqi+b2rYB6dad/y1qL5vanp1oAlkjqGW38z71T1JQBnSaP5v+7VC88Lxy/erotlRyUa9AOD1z4fxyx/crzPxx8J1l37Ur3+42+X9ysTXNHjuo/uUAfG3izwHdaNcMyp8tc5JG0VfVXiz4fx3W/5K8c+IHwz+yl2VPuUAecb6E6064t2tpNrVF83tQBLRUXze1Hze1AEtFFFAB5vvUlR1JQAUUUUANTpU1Qp0qX5vagCWio6dvoAdTk6U2nJ0oAdTo6j306gB/wA3tR83tR83tR83tQAfN7UfN7UfN7UfN7UAPTrTqi+b2p6daAHUU3fTqACLtUlRxdqkoAKKKKAH/N7UfN7UkdL83tQA9OtNpPm9qPm9qAD5vanp1pnze1Hze1AEtFRfN7UfN7UAS01+tM+b2o+b2oAWnJ1pnze1PTrQA6iiigAooooAKKKKACiiigAooooAa/WmfN7VLTX60AM+b2o+b2o+b2o+b2oAPm9qPm9qPm9qPm9qAD5vaj5vaj5vaj5vagA+b2o+b2o+b2pJKACSm0UUAR+b70UUUAFFSVHQB+iFOfrTaT5vaucA+b2qJ+lS/N7UygCOmSR0+igCnJb/ALuuG+IHhvzbd2X7yfPXob9azNU09b+3et6NRqQmm1dHPfC/4iLc2f8AZd0+y8tvkj3/APLRa6z/AISy3ik8pn2NXkfjjwvJpd59qt/klh+ZWSuS8afEDULrS32ybLqFK2+qqb5kYc0oo+k49Yhljf568H/a48Nw+I/DdysqfwfLXkvhv9rW88Oax9g1J5Nv96t74ofGi317wu8m/wAzen3a5vYuE7MftFKOh8eSfEz/AIVf4ge1upv3SP8AKz16p4L+Lmm+KLNPKmjdn+8tfGH7WnxUt5dUvNrbGR2ry74WfH/UPDd2ircybf8ArpW8qMWrijJn6R+LPB+l+I4/3sP/AAKvKPGfhv8A4QiN5bD5P7tcl8P/ANqC4v7NFZ/Mqz4w+KE2vR7VSsPZvobSPEPjBe614yvHilmkdG/hqn8M/wBm+OLT0umh+bf81ehf2W1/eb2Su50+BdL0D7lbSp3d5CTaPrr9h/wHY2Hhew2pGvyLX1LqGnw2ul/KlfK/7C+oNdaPbfPX1jrkf/EnqpJR2KTbPMdY1BYrh1rE1S4WWOs3xp4k/svXHirEuPFiy1BqaslwvmUR3lYP9uebT/7Q/d7qyA2LjVPKj+/WJrGseVG/zVT1DV65vXNY+/SbaAp+KNc+/wDPXnWuah5txWr4k1jzt/z1yVxcebPUt3A6TwnJ/pif79e9/C3+Cvn7wfJ/piV9CfC7/VpSA9r8Mf8AHvXRWdc34Xk/0euks60pkyLydKdTU6VJ5daElaQtRGWqz9mqaOzoApxdqsxx/u6f9j/zmrP2f60AQxx+bVy3t6fb29WY46xcmmAyONaZJ+6NTSbarXFxRHcCGT97UPmVJvqDzFrYB8dTRdqrR3C1ZgoAfH+9qzVeN1ip39oLFHQASSVXlkaWkk1COj+0I5f46AIZN1AjX+KpvMWX7tN+b2oApahocd1HXB+OPBccsb/JXosklYPiTbLHQB8sfFDwX9lkdlSvP/8AY/ir6H+IGjrdb/krxDxZpf2DUP8AZegDI+b2o+b2o+b2o+b2oAfvp1NTrTqACnb6bRF2oAkooooAKf8AN7UyigB/ze1Hze1Hze1Hze1AD0606o6koAKKKIu1AElFFFADvMo8ym0UAP8Am9qPm9qPm9qPm9qAD5vapai+b2p6daAHUeb70UUAHm+9SVHRQBJTvMqHzfepKAH/ADe1Hze1Rb6l+b2oAPm9qPm9qPm9qPm9qAD5vaj5vaj5vaj5vagA+b2o+b2o+b2o+b2oAPm9qPm9qPm9qPm9qAH76N9M+b2o+b2oAWnb6Z83tR83tQBLUdO302gB2+jfTPm9qPm9qAH76N9M+b2o+b2oAfvpnze1Hze1JJQAvze1Hze1Rb6N9AEvze1Hze1JHS/N7UAHze1J5lNooAd5lNoooAKjl71JUcvegA8r2oi7U5+lNi7UAO302iXvRQB+h/ze1Hze1J5lL83tXOAfN7UfN7UfN7UfN7UARP0ptSVHQAS96a/Wneb71HQBi+JPD639vXjPxE8FtayMyp8tfQT9a5rxp4Xjv7f7ldFGs47kzgpLU+M/iR8K4dZ/0iJPmryXxLZ6x4XjeL95Na/886+tPGnhebRrh/k+VvvVwfijwPb69bu0Sf8AAa7KsXURifmt+1h+zvcfEGzudS0mbybpfvQ18SeINc1r4aa59nv7aSFkfZur9jfip8F5PMeW1TY38VfNfxY/Z703xvvtdW02Lzf73l/+zVy3nDSRXs1f3T5X+E/7RH3Nz76978H/ABYXXtnz15j4g/YDk0u5ebSbny1/u1veA/gXr3heRPtE0e1P4qnmUtUNJpHv3he4jv40atXxpri2Glpbr96uM0O8k0a327/Matvwn4buviD4strdUkm3v81dA2m9D7Y/4J96XJ/wj9szfx19ga5b/wDEn/4BXjP7J/w7Xwl4btotmzYi17lqsfm6e/8AuVzytz6lpWPjn9ozUJNG8Qbl/jrzqz8YNLJ8z16X+2RpbCPzdv3HrwfS7xqVTcuJ6jpeueb96tW31D93XDaPqFbEeqfu/v1BRq6pqn7uuP8AEGsVZ1jVP9uuP1zUGlqZAUNY1DzZKzY5PNkouJPNkos7fElSB1vguNvtCV798L5PL2V4P4Ljb7Qle3/DuTytlVED2/wvJ5scddTp3WuK8J3H7tK7PS5PNrSJMjSjq1VW2q1VEksca1NHb1DHtiqaOSplsBN5S/5NPjjqH7TT/torPlYE9QT3CxVWuNQWsrUNRb/npWkbgXNQ1j95tSoftnm1mx+ZLJWlZ2bVpKCiroAkvG8qqFxcSSyVtyWf7uq39l/vKIyS3E1cp2cjVpW1FvpflVY2UpWvoMrySN5dVpJGrS+z/Sj7ItITVzK+aiO3rV/s1aT+zqASaKMUf92nxxtV/wCxf5xR5dAzKuI2rH1C3aWut+zVTvNPWWgDyXxho/7t68Z+JGj/AH6+lvFmh+bbvXi3xI0Pyt/yUAeFSR+VJtpfm9qs63bfZdQdap0AP+b2o+b2o+b2o+b2oAWpKi+b2qWgAooooAIu1SVHF2qSgB0dL83tSeZS/N7UAHze1PTrTPm9qfvoAdRTd9OoAcnSnVHR5vvQBJRUfm+9SUAFP+b2plFAD/m9qWk+b2o+b2oAe/WhOtM+b2p++gB1FN306gAqSo6KAJKKKKACiiigB0dHmU2igB3mUeZTaKAHeZS/N7UyigB/ze1Hze1Hze1J5lAC/N7UfN7UnmUeZQAvze1Hze1J5lL83tQAfN7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tR83tQAklEdL83tR83tQAfN7VE/Spfm9qifpQA6iio6ACiiigAooooAcnSh+lN833okkrGKaAKKKbvrYD9Efm9qPm9qPm9qPm9q5wD5vaj5vaj5vaj5vagA+b2qPy1qT5vaon6UAQ0VJL3qOgAqK4jWpaKAON8ceC49Zt3ZU314t4s8B3WjXDyxJ8v92vpa4j80fc31ia54Xt9Uj+ZK7oVWlYlw0sfK+q6fb6pHtuIdktedePPhHb38f+pjmWvqXxp8FlmjdovvV5F4w8J32gyfMm9a05ozVmTyPoz5U8SfBeSwuHa3eSP/AGdlcrqfw71C13/JG6/3q+n7yNb+T5l+amR/DePVJPuVjKhBOxaVj5d8N/BvVvEeoIsUP8fzNX1d+zH+yvH4SlS4uE3yfxb67/4X/CS1sJIfkr2/wt4fh0uNPkodR2sCVjS8F6Gujaei7Ni1vXn/AB5VTgqzH/q5Kx5Xe4z5s/a48P8A2vQ5mr5Us7fypK+0v2lNPW60Ob/cavjySPyrh6qWsblRNLT5PKqzJeeVWabjyqp3mqfu6zKLOs6hXN6hcebT9Q1Ss17tamQD9n7yrlnb4kqhb3FaWnyfvKkDsfB9v5UqV6z4LuPKrybwv0SvSvC9x5UaVUQPYPCeqfu0rudH1ivGdH1zyq6rQ/Fn+3Vp2E1c9as7xTVn7YtcHp/iv/brVt/FC/36sXKdV9tFP+2f5xXMf2+ahuPFixR/fphynVSaosVULzxIsVcfceLPN+WmW95Jcyf7NXGPck6r+1Guvu1cs7NpfvVmaPH5u2ulsrfyqmSSegD7PT1ijrQjj8uq++pPtNTr1Amk/e0zyl/yaZ5lL83tQA6ST+7T6i+b2p6daAHUeb70UUpOyAKPN96kpJI6UZXAROlOqOiqAc/SopI6fRQBj6xZ+bG9eRfEzR/3b17ZeQebG9ee/ETT/wDR2oA+TvHln5WoVz9d38XNPWK4rhKAH/N7UfN7Uyn/ADe1AB83tT060z5vaj5vagCWiovm9qWgCSjzfeo6dvoAmpu+m07fQAb6l+b2qLfTqAJKdvqPzKX5vagB++nVF83tUtABRRRQBJRUdSUAFOjptFAD/m9qPm9qZT/m9qAHp1p1RfN7U9OtADqKKKACjzfeiigCSio6Iu1AElFN306gAooooAKKKKAHR02iigAooooAf83tR83tSSU2gB0lR76dRQA3fRvp1FADd9SR02igB/ze1Hze1MooAf8AN7VE/SpJKbQAVHL3ool70AFFFFABTX60b6bQBJRUXze1Hze1AD360z5vak8yjzKAP0V+b2o+b2o+b2qPzFrnAk+b2o+b2qP7R9KPtH0oAk+b2o+b2qLfRvoAbTdlOooAjopz9abQA7ZUElv5NS07ZTbbApfZ1lj2tXPeKPAdrrNu6tH9+unkj/eUytacmB4nrHwHs/M+WGmWfwkhtZPuV7BeWa/3KoXFkv8Adq+Zgclonh9bD+Cuks46JLf95U9unl0gLSdKk/1SVGnSjfQB5f8AHi383R5v9yvi3WNsWoTf77V9sfGyT/iWTV8Q+LLhYtYuV/26ForGhTuLz/brH1TUP3f36hvNUWsq81BZY/v1n0AZqGqf9NKhj1Dzax9UvF8yobe8aobbA6e3vK29DkaXY1cfp8nmSJXYeGqQHZ+H5P3iV3Ph+8aLZXDaXti+7XT6XrCxR1UQO8s7z939+rlvrjRS1x9v4gWH5asx66v9+qA7/T/Ejf361bPxQ39+vNLfXFFPk8WLFH9+tAPTrjxr5X/LSs2PxZJdSfLXn1vrkl/J/s11Phe3aWRK2jFJ3RMjs9Hkkuq7LQ9PrC8N6X5UfzV2Gnx+VH8tUSaunxrFV+3krNt5Kv21Yz3AsxyedU6dagt/6VOnWpAmp/ze1Mpu+gCX5van76jjpfm9qAH76N9M+b2o+b2pNXAl833o833qOnb6FGwDqKbvo30wHUU3fQ/WgBLj+tcl44s/Ns3+SusrF8UQebb0dbAfK/xo0/8AeP8AJ92vKa93+NGl/u5q8GuP+PhqKiS2AdRUcXapKAHeZR5lNooAf83tR83tUW+jfQBJ5lL83tTKdHQBJvp1RfN7VLQAU5OlNooAkooooAf83tS1HT/m9qAH76dUXze1LQBJUlR05OlADqKjl70RdqAJKKKKAHeZS/N7UynR0ASb6N9M+b2paAJKKanWnUAFFFFABRRRQBJRUdSUAFFFR+b70ASUVH5vvR5vvQBJRUfm+9SUAFFR+b70eb70ASUVH5vvUlABTd9D9KbQAeb70eb70UUAHm+9Hm+9FFAB5vvRTU606gAqOpKjoAdvptJ83tS1E20AU2SnVC/SnECTzKbRRVAFFFR+b70AfopR5vvUdO31zgO833o833qHzKPMoAfHcU/e1RfN7UfN7UAS72qOik+b2oAenWneb71D5lSb6rlYDaKdvptSA2WOoasU2WOrjKwFeSPzKpXEdXX61VnrRO4FCS3/AHlM8v8Au1cljqGXvTAkqCSSn1WuJKAPNPjZcf8AErua+FfHl55WuXn+/X2x8dLz/iV3NfBPxA1Nf7YvPn/jahaq4GPqmqfvKxLjWKp6pqn+3WJe6pWe6NDYuNUWn2dx5tcxJqH7ytLT7yswOw0uT97XW+H9Q8quA0/UKvyeKI7CP79AHqP/AAlEdrb1QuPiQtrJ9+vH/EHxN+y/x1x+ofEySWT5XoA+kLf4sL/z2rb0vx4t1/HXy1ofjCa6uPv16d4L1Ca62VUQPdY/Fnm/x1Yj1lrqRK4rR92xPnrt/C+ntdSJuSuunsB1ng/T2upE+SvWvB+j+VGlcl4L0Jfkr0jR4PKjT5Kshu5t6XH+7St6zjrH07/Ctu3/AHVZ1BF+2q5F9+s2O8X+/U0eqR1nzIaTZq2/9KnTrWTHrkcX8dH/AAkq/wDPSoc7Ak2bCf62p/m9qwP+Enj/AOelTR+JIZafMh8rNn5valrLj1mP+Fqsx6gstHMJpotfN7UtR/alqbzPK/4HRzCHU3ZTou1FNysBHSfN7VLJHTdlCdwGfN7UfN7UfN7UnmUwI36VR1iP/R3q/J+9qnqsf7t6APEPjBZ+bbPXzfr8Hk6o1fUvxYsl+zvXzH48t/J1h6H8AGVTt9R76dQAUUUUASUVHTt9ADqf83tTKKAH/N7VLUXze1P30AG+nVF83tT99ADqIu1N306gCSneZUPm+9O30ASeZS/N7UyneZQBJvo30z5vaj5vagB++nVF83tT99ADou1O31DUlAElFR+b70eb70ASU7zKbRQA/wCb2o+b2plFAD/m9qPm9qTzKX5vagA+b2p++mfN7UfN7UAS0VHRQBJRUdH+soAkooooAKKKKACiiigAooooAKKKbvoAN9G+mfN7UfN7UALSfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tR83tQAfN7UfN7UfN7UfN7UAHze1RP0qX5vaon6UAOpr9KdRQBH5XtRTt9NoA/QX7R9afHJVPe1G9q5wL2+l8xarRyNU0clAE/ze1Hze1RJ0qX5vagB6daZ83tSeZ5VNoAKKKK2jsA6OnVHRUSjZXAkopsclOqAK89VriOrMveq0n+rq4ysBWkqGXvU1xJUMvetQGSSVTvJP3b1cuP61lapcf6O1Juw0rnif7ReqfZdHuWb+5X5++ONY/4mlz/vtX2x+1p4g+y+H7n5/wCBq/PrxZrnm3kzf7dJy9wpKxQ1DWP3lZr39Zt5qH7yqcuoViM2ItQq/p+orXJf2h+8ovPEi2se2gDtrjxYthH8r1z2t/ED939+uJ1jxo39+ubuNckv7igDqtY8WTXVx9+n6fJJd1iaHZtL96u/8GeE5Lq4Tany0AbfgPQ5Lq4Tale3+B/D7WFun96sT4f+B1sLdK9F0ez8rbXTTp21YGx4f0vzdlekeENL8rZXGaHb/vEr0jwvHHaxozVpKpFOw1qd/wCG7Pyo03V1Wn3EcUdcHZ+JFtY6m/4TD93/AKysZ4iKWpdPC1Knwo9F/wCEgji/jpknjBYq80uPFn7v79VpPEkkv3a8ivmtKPu3PWo5HOWsj0u48cf9NKqf8Jx/t15zJqE0tPt5G/v15dTOJPSOx7EMlpx3O/8A+E5/2qP+E4aWuMgkar9vJXHLNqzZ1Qy2jE6ePxpJVm38YSeXXPW8lXLeNan+1K/cHl1FdDet/GElX7Pxg2fv1zEdutP8urhmlZO5jPK6Mt0dzZ+NP9utiz8WLXlfmN/kVcs9Umiruw+cXXvHDUyWL+E9gs/EEMv8dX7e8WWvIrfxhJa/erY0z4gfvE+evVpY6lPS549bKatN3SPTflo2Vyel+NI5f462INcjlH369CMtDz5U5RdpaGlUMlN/tmOqsmsR1XMjPQtVV1D7klQ/2rDUNxqiyfx0KV3YDzr4nx/6O9fMfxEjb+0H/wB+vp/4jyLLbvXzT8ULdftH/A6uWkbCaucjTt9Q0Uhk2+hOtM+b2o+b2oAloqL5vaj5vagCXzfenJ0qN+tCdaAJqf8AN7VBUlAD/m9qPm9qSOl+b2oAWnb6Z83tR83tQBLRTU606gBydKdUcXapKAHR0vze1Mp/ze1AB83tR83tR83tR83tQAtO30z5vaj5vagCWiLtRRQBJRUdSUAFFFFABT/m9qZT/m9qAD5vaj5vaj5vaj5vagA+b2o+b2o+b2o+b2oAPm9qenWmfN7U9OtADqKbvpnze1AEtFRfN7UfN7UAS01+tNpPm9qAH76dUXze1P30AOpr9aN9G+gBnze1Hze1Hze1Hze1AB83tR83tR83tSeZQAR0SUSUvze1AEW+jfTqKAG76N9Opu+gA306m76bQBJUfm+9FFABRUdJ83tQB98eY3+RRHJ+8pkklM+0fWucC5HJVm3krNt7irlvItAFyOSnb6it5KlTpQA2jzfepKr0AWKKKbvquZgOp/ze1J5oo80UczAX5vak8ymSSUfaPpUgMl71WuP6VNJI1Q3H9KAKFxJTd9Jcf1qGSRq6AGXklYniO48qzf8A3K1biRq5jxpefZdPepkVE+S/21PEnleH7lK+EvEGqN89fTn7enjhbXzot+yvjnXPEH7v79TUvYoNQ1T94/WqEmocVlX+sNLJu31D9s82OswNK813yo/v1zeseKG/v0/WJG8uuM1i8b7RtoAuXGuSXUm2tjw/G0sn9+uV0/78ddl4O/4+I933aAPQ/AfheTVJI9qfLXvfw/8Ah8trbpuSvNPhXqENrsr3nwnrcP2euinGO7A2tP0tbCP5Uq59tjirH1TxTH/frKg8QNf3nyv8tVUrJK6NKdOU3ZHpfh/VV+Suz0/XGMf36808NPXW6XulrwcdmkYO8T6TA5Src09zrY9ckp8eoSS1lWdm2a1bONa+br46dXVM9+jhowj7qL9v/t1ct46rRx/vKswVySk2zUsxx0+3jojjarMdvSGnYfBV+3/pVa3jarkUdAi5bVct7iqEf7qpo5KBNXL/AJ9Hn1VTpUvze1AuVEsXanxyURx/u6WgaVhLiSqFx5kX3fvVcl71DLHVc8lsPS1mMs9YurCSt7T/ABvJ5fzPsrA2U2S3rsw2Y1KXU48Rl9Godh/wn7f89KrXHxAb+/XK+W1Q3Fn5leh/bE7bfgef/YtM6eP4iN5m3fXQ6X4k+3x15X9j8qSuq8LyN5dehl+ZOpLlkrHl5hlfJHngaXjTddWb185fFTdFePX0tqlu0tnt/v14J8ZNDb7Q9e8pN7ngSVnY8u833qSo6KBElO8ym01OlAEvze1Hze1Hze1Hze1AB83tR83tR83tR83tQA9OtOqOpKAJKd5lQxdqkoAf83tR83tSR0vze1AD99OqL5vapaACpKjpydKAHU6Om0UAO8yjzKbRQA/5vaj5vakjpfm9qAH76bSfN7UtAElHm+9FFAElFRxdqkoAKKKKAHeZS/N7UynR0AL83tR83tR83tR83tQAfN7UfN7UfN7UklAC/N7UfN7UfN7UkdAC/N7UfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tR83tQAfN7UnmVHvp1ADvMo8ym0UAFFFFABRTU6U2XvQBJUfm+9FFABTd9D9aZ83tQA/fRvpnze1JJQBJvofrTabJWSbYB5lHmU2itQPu7fUX2j61Q+2/5zR9t/zmuc0NKOSrMdxWJLqFQyaxQB1VveKasx361yEfiDyo6SPxJ/t0GZ2El55tM8+uettc83+OrlvqlAG3HcU/7R9azY9QXy6f8AaaAL/wBo+tH2j61T+0fWiO4oAueY1Mkkqt9o+tEklAE0klQySLUMklQ3ElADLiRYhVb7R9aZeSYkqvvrbmQ0rjri4rz34wa4thpkzV215cfu3rxb9ozXPsuh3Pz/AMDVnIs/Nb9vj4mNL4sS1/22r5pk8WNLHXYftmeJJNU+KFx8/wAqV5Lp8jS1I7NnVW+oNXQ+G7f7fsriY7yvSfhPH9qkRaBDtQ8HtLH9z79edeMPC8lhcSM38dfWmn/D9b/T92yvMfi58OPK3fJVcrA8E0+3aWRK6e0vPsEdH/CP/YLj7lZXiDUPssdJqwHbeH/igulyffr0Xw38fFuotqvXydrHiBvtGxXrvPhHp9xqlwn916v2jtcqjF1HZH1RofjyTXvuvXpHgvS5Pk3V518I/A7eWjMle9+C/DbRbPlr53HZk17qPsMuy+MI3NXw/pf3K7PR9P8AKqvo+j+VF9yuj0vS/wB3XzcpOTue5sFvb5q5b2+auW+n/vKvx6XUhzFO3t6uW2n1ct9PXy6mjg8oUEkMdvVmO3pdlWLe3oAZHb1Zt41p8cf7ypo46CeZDPs1SbKljjWmUFXT2JKdHUNFAFzzfen+Z5tVvMqROtADpe9FFO2UAN8imSW9XI46LiOgDNkjpnle1TS/fo8ugHqrFa4t8VZ8N6h5Vxtplx/SqdvJ9lvEaurB1XTqpnHiaSnTaO/81Zbf/frzH4waOstu7V3+n3n+jpXMfEiP7Vpb195RkpWZ8Di4csrHzTqsflag/wDv1X31b8QHy9Udf9uqPze1bGJLUlQ76dQBJT/m9qZRQA/5vaj5vamU/wCb2oAPm9qlqL5valoAki7U7fUe+nUASUVH5vvUlADo6k31H5lHmUATUVHTt9AEj9KbF2pu+nUAO306o6dvoAdRRRQA/wCb2o+b2plO8ygCROtOpkclLvoAdRTd9G+gB1EXam76dQBJRUfm+9Hm+9AElFFFABRRRQAUUUUAFFFN30AOooooAf8AN7UyiigAooooAKKjo833oAkqOiigAoooqeYApr9adUdUAnze1Hze1Hze1Hze1ACSU2n/ADe1RP0oAdRRRQAU3fTaKAPsmS8/eVB/aNZE+qNDVaTWG8uuc0N7+0f85qheaxWV/atVry8/eUAaVxrFQx6u3mfLWVJcfvKms5KAN7T9caKuk0vUPN/jrj45Fq5b+IFtY/v0AdnHqnlVP/aa1wv/AAlCxfx0f8Jb/t0S0KjTlN2irnf/ANqLT/7R/wA5rho/EjS/Nvoj8QSf364pZhQi7NnpQyTEyV2jvI9QpftlcXH4kk/v1Zt/EmK2p4qjPaRz1crxMFdxOnkvKZJcVjx63HL/ALFEmocVvqcPLJfErE1xeVD9o+tU5LyiO4oKH6hcf6PXzf8AtYeIfsmh3Kf7DV7x4g1T7Lbv/uV8l/tZ+IWutPmhX52oE3bc/Lj9oiRrr4g3krP8u+uP0+Pyo91eq/GzwfcS6hNN9mk3b99eT3m61+VkkT/tnR9xtyy5btMfJeeVXqPwD1VZdURW/v14tqmqeVurrfgn4wWw1RNz0ambPv8A8D6fHdaOn+5XJfGDwnH5btWP4D+LkcWnIu+sr4qfGCOXT3/fVopaWEeJfESSHS5H214v448ULFI6766T4qfEiOW4m+evMdP0+68eaxtVJHV3rOpKK1ZpTpSm7Iv+C9IuPFmsJt+7X2B+z38I2it4WaGuc/Zr/Zrkl8mVoa+1Phf8H49Ls4f3NeHmGYaNQPqsty9QV5Ih+H/w/wDsscPyV6l4f8N+TH9ytHQ/Cf2XZ8ldPp+jrFXzlSo27s96Nkihpeh1sW+leVWlZ6esUdWfsa1KdwKFvZ1ft7epPsdWLePyqYEP2aj7NVzzFlNWY7RZfu0nITdjNjt6s/ZquR2flUfZqXMLmIfK9qKm+zUfZvKqSSGnbKk8pqmjjqohzWIfs1H2arkUdTeRRyh7QoR2/wC8qby/KFXBb+VTJe9SVzFeinXNRp0ppXGncn8zyqZJJTajnpDIZfv0eZTJf9ZS0ARz1QvJPLq/cSLWVfyfu3rSOuvYzqbHSaHqH/EvSqHiiT7VaOv+xWb4X1T93tq/qEf2qOvtcvqOVJM+NzWilPmR88eOLdrXXJv9+sPfXafFzS2tdY8zb8r1xtemeKP+b2qWoY6X5vagCWjzfemp1p1AElFR0RdqAJ/m9qPm9qZRQA/5valpsdL83tQA9OtOpqdadQAeb71JUdFADt9S/N7UyigCSnb6Z83tR83tQBLRUXze1LQBJ5vvR5vvRRQBJRUdSUAFOjptFAD/AJvaj5vamUUASU5OtV06VL83tQBLRUdO30AOo833pu+nUAHm+9FFFABR5vvRRQAeb70UUUAHm+9Hm+9FFAB5vvR5vvRRQAUUUUAFFFEveoU7gFFN307zfenKVgCimv1ptZN3YBSfN7UfN7UnmVuAvze1Rb6dRQA3fTqKKACo5e9O302XvQAUUUUAfRtxqH+3VO41Cs24uKzbvWGi+XfWMTaJtx6h+8+/VzzPNjrlbPVPNk+/XSaPIsse2iW5VkU7zUPKkqG38SKJNtauoaOsse5a5XVNPa1ld1eiI/dbsjb1DxYtrb7t9Y//AAsHzfu1wfjDxRNFIkSv9+tDwvo80tvub+OscRWhSjzSPTwOVOtLU6//AISSS6KVt6HJJdj5q5XT7NvtO2u58N6f5UdfK5hmk6nuwVj7bB5TRw6v1Nuzt1q/Hb1DbJsFaada8bVuzNKvu6oq/wBnf5xTLiz8n7tadR1rGTi7o59zHkkki/26I9YaKrl5GtU5Il8vdXdRzKvSe5yV8DRq9B/9sN/FT/7cXy6x5Y6rSeZ/fr0KeeSS9+J5tTh2nPZj/El59vjda868UfCe18Rybriu5l/e/epkdv8AanrjxmcVJK0dD38vyPD0tZanj+qfsj6Hr33raN/+2a1yHjD/AIJx+G/Edu6/YLbd/wBc6+nrdLfS4/8ASHjhX+89U9U+Iej6V/y287f/AApH/wDqry44ytbWTPSlRpyfLGCfyPzT+Pn/AASQ8u3muNFkuLZvvKv8NfGfxI+Cfib4Baw66pbSeUj/AOuSP5a/eDUPiZp91H81ncuv+3trx/48fs9+GfjnodzbtDHC03/PWP8A+Jr0sHnjpu03dHm47hmFaHPTi4n5C6P8cJtLt9vnbKxPGnx0mv7fasm+vS/2uP8Agnv42+A2uTXUWj315oMzt5d5b/vYo/8AeZfu/wDAqwfg3+xnqXjK8hlvIZNr/wANfSRxtF0+fmPinlGIhV9lKOp5R4b8J6p8S9UTbDI8T19gfsz/ALH7ReTcXFt83369y/Z7/YjtdBt4f9G/8h19S+A/gva6Dbp+5+5Xh47NHNcsNj6TB5RCkk5bnB/Cf4FQ6DZp+52V61ofg+O1j+5XSaX4fW1/grVt9LX+5Xj8zPRMGz0dYv4Kv29osX8NbCWFEln5VNq4FCO3qzHb0+OOrlvb5oSsBT+z/WmSR+VWxJb/ALuqwt/NqOVvQzuluY/mNFJWnp8lJJpa0+O3WKizi7G3uuNyahP9bTU605P9bXRGKMSzHEstMkt6d/q6kjkquVGfMyGODyhU3kU7fTqOVBdvcdFHU3le1Qx06jlQhsv3Khl71NL9yof96uU0TuQyUR0+SOmR0DHyR1Dcf0qz/B/uVWuP6UBr0Kc/+sNMqa4jptBo3ZFW5rK1iTyo3rVva5vxJceTHtrWMG0zO7tYreG9Y+y6hs/56V3NhH9qjrxyPVPsuobv7leu+A9UW/s0/vbK+vyq/s7M+bzqn7t0cZ8YPB63Vm7bK8Qkt/ssjq33kr6u8WaP9vs3WvnX4meF5NG1R5VT5Xr1o7XPlzmad5lQ+b70RyVQE/ze1P31HHS/N7UAS0U1OtOoAkoqOpKACnR02igCSnb6Z83tR83tQA/fTqi+b2qWgAi7VJUdSUAFP+b2plFAD/m9qPm9qPm9qPm9qAHp1p1NTrQ/WgB1FFFAElFR1JQAUUUUANTpUvze1Mp0dAC/N7UfN7UfN7UfN7UAHze1P30z5vaj5vagBaKT5vaj5vagB++jfTPm9qPm9qAH76N9M+b2o+b2oAlqOnb6bQA7fRvpnze1LQBJRTd9G+gB1NfrTaKwTsAUU2SjzKG2wHUU3zKPMpAHmU2io/N966AHb6b5vvRRQAeb70eb70UUAFFFNfrQA6m76N9M+b2oA9cuNYx/HWDrmsNFVC81jypK57xJ4gbY/wA9JKx3U6eups2fjBYn+aSuk0f4mQ2pT5/mrwDXPFklrJ9+uP1T4sXFhI+16Z2RwvM7I+wLj4sW+z5pq5vXPipHfyPFF/HXyLefHS+luEiV5Nz17Z8B/Dd14o2XF1XNiMVCjDnmelhcl5pJz2PSPDfg9te1D7RKn+7XoWn+H1tYEiVPuU/wvocdhGiLHXVaXp6/3O1fFYzGVK0rs+ooUVRSiYln4X8qTdsre0/T/KrYg09ZI/u0SWeB8teadEsTzKzIKkgqG4jaKOi3nx838P8AFTjuZy1jdF6opJGrG1TxxY2Em1ptzf3YvmrC1D4mLFvWKONG/hZ/nq7pbmcaM2r2OwkuP3dZt5qsNqf3rxr/AL8m2uD1Tx5eX/8Ay2+X/Yqn9sk8x9zx1PtUmbrAzauztrzxJZ/wzf8AfEbVlah44tYvu+Y71ytxeeVG7K/zVj3nmSyf7T/d/wB6odRtWR00sCo7tHYah44by9sUMe5Pur5m6sHUPiRdR/6qbZs+9s+Wsq4t7iwkhWX7z/Ozfd8xaxNct7q1kRVSN1m+f/gNZuUup6VHC0o/Eatz4gmvx9olm3+X8+3+KRqp6/rkdhp8O55JriZ1SRv/AIms6486Kz+X92yfxJ97mqWsRyf2O7Sx/NDtdf8AvquWs7o9XDxpxmkjodPvPt+zc/y7Pmrb0vT1uvl3+X/dZK4/Q5Gv5EXZ8tdt4fs/OuNuzYqferK6exriJJLUv2+nzRR/unrmLf4V+G49QeVdKttNuvvs1pH5Syf7TKPlrv47OPy02puX+7VOz09rq3mZvvP/AA/d+WnzVIvRnmWhVWo/w/4bs4rf/R0jret9LWuYt/M0u8+V/lrqtL8QL5afaE+VvuyJXXRxMZaSPCxmDlT95O6LH2Ol+z/WtKPy5Y/lo+zr612HnlDyKZcf1q/5FU7iNqOZrYCtHIvmVcjkqnHbt5lT76ALPze1Ojj86oN9Tx3C0GTdiaS3qt5Qq5HIstVriOrUGxcy6jPs1Pjt6hjkanxSf7dXysnVvQsx2/nUfZ/pT7eSrMca1sIp/Z/pTK0vs1Vri3xQAyOSnU2OPyqkfrQA2myx1InWnS96mV7aDKckdEvepKjl71k6bY4tdSOmyU6m+XS9myuZEMkf7yqr9Kuz/wCsNULymqbFJprQp3lx5cdcN4s1j949b3ijWFtbd68r8UeKFluH+eunCU3KZOltSbzPtVxXqPwr1BrWNFryXw3cfb7hK9a8J2/2WNNtfX4OklueTjmnBqR6d9j+1W9cT8QPh3HrNm+5K7PwveLLHtatu40eO6jrpifI1E0z458YfDu48OSOyr+7rm/+WtfWPjj4dx6nbv8AJXgnxA+F82g3DzRJ8v8AFWqdzM42nR1D/qpNtHm+9MCf5vaj5vamU/5vagB6dadTd9G+gCTfRvqPfTqAJKdHUe+nUAP+b2p6daZ83tS0ASUVHUlAElFR+b71JQAU/wCb2plO8ygBfm9qPm9qTzKPMoAk30b6j8yl+b2oAlopu+jfQBJvp1R0eb70ASUVH5vvUlAD/m9qPm9qZRQA/wCb2o+b2pPMo8ygBfm9qPm9qTzKPMoAX5vak8yjzKbQA7zKPMptFADvMo8ym0UAO8ym03fTqACn/N7UyigB/wA3tR83tTKKx5WA/wCb2o+b2plP+b2pWaAifpRvofpTa1jsAeV7UUeb70VQBRRRQAVHTn60z5vagBac/WmfN7UfN7UAHze1Hze1Hze1Hze1AFvVNU82uS8Qawv8X3af4g8QeXv3Psrz3xZ4okl3rb+ZM391Pm/9BpOSW7R7FGlKVkkw8Wa5DFv+evMfEniCHf8Afq/rnhvxl4juPs+l+G/El40z7P3Wmzbdx+7ubbtWtv4f/sH/ABQ8ZapHcazon9j2CP8AMt3fwrLJj/YVmP8A47XNWxlGkrzZ72BwMm72Jv2e/hnJ481xLpk/db/lr7e+H/gOPQdLhiVNn96sT4N/AOH4aaPDFLNbeaifNs3V6RZyR2saba+PzDG/WKt76H0NOLh7q1Lmn2axfwVvafb1ytx4g8p/lT5v4qoan4rupY3VnkRU3Ov7z/2WvNlKPUcozkz0KTWLXT/vTRp/wOsfUPiJY2u7yk85q4DUJJotjK+xvvtvrN/tCa1vNy+Zt/8AZqzdRJ2NY4FNXZ2d/wDEi8v43aJI7Na56412bVN7S3kj/wCzVC81Rrq33Kn7rZ937tZseuQxW+3fH/vfdqHWsrnTTwqS03HaheTW0jr/AA/7f/LSoo9Yhlj+/vb+Jah+0SapI/z71/2JKzbjd9o/uVg6jbuehTjG3vF/zIfN376uR3DXPy1lW9g1qn343/u1f0+SSW4TzfL/AN5Pmqo6O4V5RWwy8t1lk+VJPn/v/wB2rMccf2xP49ib9tPjvFlj2/xf7VM1CRZbj5Uj+dPvVtotjhUm9yneag323bLHv/5a/wC1t+as28uG8zds+aSH7r/+PVpXlx9kuLlvJ+bZ5X8P92q0kUcscMTJ/wAsW8vf/vVL2OqPKrXOPu9QmtZE2p992/3f9mn6hrt1Fp9tBLDG8V4/+1+7ZP8A4rdW3rHhuPzNqTfP8r7fMqteRqbfyoUjm8lP9rdXn1oytdHrYapDQh0S9ksNQ3f6lX+Ta8bf+O13/hy4m8xGb51ufkX/AHhXGaXqkMtum6GT59u793/8TXZ2dnHdRwtF/ozbN/ybttTRm1G9isVaT5WdtplvZy2e5po4W/66VQkjU2+7+H/lm3/PRafof7rT5muEj83Z97y60vEFmpjRtnkr8vy/xV3e7OGh4tOThU5WcrqFv+73I9XPDd55tu6t8/8AB5dLeRwxW6fJ/vVqaf4f8vTIWVPmb56440nzaM6sRWg4aofZ3E1gN1v/AKp/vR/wVq2eqLLH8v8AwKqdvGsUfzfJ/B+VPu7PypElgf5q7qUnF2bPDrU01eJf8zzKjpun3Ed1Jtb921X/ALEK6tLaHBK6ZTkt6h+z/Stj7Evl1DJZ+VQLmMryKPmirS+zrR9i/wA4q4K5nLYoQSNU0knnVZ+wVWuLfFbxjYlK5W8vzafHb0+Onf6yplUs7Gi0Vie3jar9tVO3jq55laGRNUNzR9pqN+lAEUn+sqby1plTRR0AQ0S96fJHTJe9AEXze1QS96mljqGXvQBHRRTZKAIbiSsrWNQWKN91X7muG+IHiD7Bbv8APTcGxcxx/wATPFnlb/3ny14tqnjRbnVPv1N8YPiB5XnfPXlGj+IGv9U3V9DgcCrc7OPFYyFJOJ9J/C+882RGr2Pw/dr8lfN/w78SeVbJXrvhPxYvlL89e7GKSsj5utinPQ9m0fUPKj+Wut0PXFl+V3ryjR/Eiy/x10ml65/t1gefKV2ei3FnHdR/364/xh4Hj1S2fdDW34f8Sf3q2/Ljv7f5aqMrENXPlT4k/B9rWR5bdNleb3Fu1rI6S/ejr7G8YeF1u7d/k314D8WPAa2u+4VdjVrF3IPMYu1SVG/+toi7UwHb6l+b2plP+b2oAPm9qenWmfN7UfN7UASxdqkqOiLtQBJTo6j30b6AJqdvqCOSn+ZQBNRUXze1PTrQA7zfepKh306gCSio4u1O30AOp0dNpu+gCX5valqOn/N7UAPTrTqi+b2o+b2oAlopu+nUAHm+9EXaiigCSio4u1O30AOopu+jfQA6im76N9TKVgHUU3fTacXcCSmv0ptFMCSo6KKACjzfeiioc7MA833o833oope0APN96dvptFTKVwCXvRRRWkdgCio6T5vaqAe/WjfTPm9qPm9qAFpPm9qPm9qPm9qAD5vaj5vamUUAOkptFFAHpVv8A/DOjSI1xayaxK7/AHruT5f++UwK6HT9HhsLd1sLO2ttn8NvAsX/AKDWxJIv2dGiTzm+b5n/APiahuNUmj+b93tr8zxGbTm3eR+xYXAQhH4UQ29vdeXul+Tf8+16s28kkvy/3/7kf8NFxIsv8ez/AGqmt7f7LIiqm9X+7/vV5rxLkrNnZKPKr2IdQk/eTKv/AAGq1vJ5uxV+9/FvqbUP3uyT/wBD/wDQap3CQ2upov2j/gXy0e2RtTpx5bIfcXjf61fvw1WkvFl2Mz7N+5FqGS8WKd5WSNIt/lMqVW1DUI7WJ1X5G2faNyfern9sr2Y/Yq9mM1ST7LZv++++ny1mxySS2aKzx+an/AqoahrEf+qX/add/wDve9Mt5Ibq4huIn8n5NjL975qqFS+xfJyouRztpeoPvePyHqh4guI7ovtf5v8AY21fkEP2d9yRur/391c3ceTp9x/o8Ns8SfwxV0GcaifvPcZZ3l1a/cmjdY/4fL/+JqaPVPNk2t5fz/8ATSs2PWG/3W/hX5VqnqGqNJIjfu6SVjSN3sdVHrDeX5X39lWbfVFll3N8lcxZ3n2n5m+Rv71X7S4W0uPmfetXzGNSi2zpJJMyP8/zfL9yqHmSRSIu+VP9qmJcRyyfK/zf7FEkbSx/N95Pu1pzIwjSaItYuJLq8vFl8zdN8i/722sO4uJItPhbfLuR1+V/7prU1XUGit/N/wBZs+RqxdUkW685dmz+Nf8A0Ks6lRWO6nFFC88SXEV46Sv9z7slVrPxReaPvb/XKm7/AHqZceTdW/39jVla55lhH5TPv8z512V5tSqm9T2sLGLfKzsPB/jSE26K38e2u40vxJHdRon3GT7v/TRa8F0eSS1k/wCWu3+Guw8L+JG+0IzfdT7tZxrWd0dOIwCa5kfQmjyW8tv/AK7Yz10mqTw39vt279ifK39+vIvDHiT7VGit93+Ku5t9YX7PuX7v8Nd1GtFq6PlsTh5xqXZck0uOXT4VZPmf+lXtHkaOWGJvuo9Ysmuf6R/cVPkWtjR7hftCbvup8/51009zkqX5bMm8uS5kdV+7sZvkqaRFEe1njqa3kXzHb95/s0+82+Yi7Pm/i2f8s6uMVa7OOVT3uVFbUNMWX51ff/tVDZ+IGsJPKuvM2/8APT+L/gVX02xRtt8x1/hV6p3lmt1H/wCzVpzNbGUlFu0jVt9QWWLcvzq/3akkdZa5SO8k0a43RfPb/wAUdbdvqkd3HuX561p3luZVKLjqy55XtVyzt6oRz+bJV/T7jyq1p7nPLYsvZrVC80/93Wx9pokjWWOugm7WxytxZtHRbxtWlqFvUMdvU8qvcOZhH+6p2+l+z/SiSPyqoQz/AFtTeXTLf+lWZe9AEPl06imyUAMk/e0mypfm9qifpQBDVeSP93VimyUAV9lR3EdWqgvfu1SiIwfFGqR2Fm/z/PXz98aPiIthbzfPXrvxAjkurd9r18u/HDw5eapJNEqSP/uV6WDwspyTRz16yjG54n8RPiJ/ampuu/f/AHqZ4W1BYtjeZRJ8E777Q7eTcbnqzb/CvUrX/ljLX01uRcqPjMRWnUm5TO58N+KFi/jrvPDnxA8offrxyz8J6ta/8sZPkrY0+z1SL/ljJRzMwPorw/8AERf79d54f8eRy7Pnr5d0e81SI/6mSu28N+INQiCboZKkD6i0PxQv8L13Ph/xR/t180+F/FF5j7klemeF/Ek0sfzUAexXlxHf2e6vK/iZo8d1bv8AJXZ6FqjTJtrH8YWbS27/ACfwVXMxNXPl3xRp/wBg1R/7r/drMrt/iZ4cm+2blST5K4+LT7j+KGStiBnm+9SU77Bcf88ZKP7Puf8AnjJQAeZR5lP+wTf3JKPsU390UAJTt9N+xTf885Pzo+xTf885PzoAdvpI5KT7FN/zzk/Oj7FN/wA85PzoAkp2+m/ZZP7v/kOj7PJ/zwkoAm8yjzKj8iT1p3lyf3KAH/N7U/fUce7+5R5cn+TQBJvp1Q4b+5T493mfcoAf5vvRRhv7lGG/uUAHm+9SVHhv7lSbG/uUAO8yjzKbTvLoAX5valpvlNT44/OoAfRRRQAUUUUAFFN30b6ADfTqjqSk43AJJKbvofrTPm9qErALRSfN7UtMB2+nVHTt9ADqKIu1FYy3AKPN96KjrTkQDt9O833qL5valqJRsBJ5vvTd9NopczAT5vaj5vaj5vakkrYA8yjzKbRQA7zKbRUcvegCSm76bRUy2AKKKKUG2B7r5bWGoOrP/o7VW0aT95Nbt5j/AD71Wt648ONqkbNcJsWH/lslVo9H8qPevmOyfxfNtkr8dlh3zbH7xDFU3Fph5bS28Lfca2+8taUl4sUkLL8nnfIv93dtp+n6Z5th9qWH7/ysv8W2rkujxy2G1m+58it/6DXTCm4x0OGtUjJpHN6pG0Uj2+zYu/Z/wE1z2oR280fmyp8ybkkbzPm4/irb8WWDfYJvtHyND+6/i+7/AHlrzqTXGik/12+VN0TL/wA9GH+9Xm4qtySsexhablHmTuX4PEDWsj2rP8025G2R7lkb+9VCTxZ+7Td5jq+5N33elclqniSS137HkfZN97+L7tY9x4gaK4839599dy/N92uenXvY7JYa92dheeLFl8nd5m10/j/75qh/aDWtxt3/ALp33xsklcrZ+IG8pPk3qjsm56sya5Hc2+392i796sldHtFc45YezsdRceLPKt9rP8qP9191ZNxrH7zdb+XtdKxINUjuo/v/AC7/AJv71Mkk+4uzYtdMWnqjH2JsSag3l1D5kcvy7I3qhJeLFbr/ALH8NQ2+sr5m77laOSLhTtsdDb3ElrH8z/L/AHav295+7+/vrm49YaWPatH9ueVJs/ipcyL9jzO50MeoTRSffqzceII/M+b7tcx/anmx/wDstH2jzfmby6zcpJXM400zeuNUW6t3X+/VOTUI5f3X9z71c9qmoeVGjL/BVaPXF/v1HtGdlPCq10atzP5W/wCffFVC80/+1I9//A1aiTWF8v8A2aof8JJHF/wCsKmp1UefYs2+6VNqpv8A9+tjw/o/zo3mbGT+HzK5uPxIt1JuX9z/ALlbGj6x+8Rm+f8A2q4aklc9NTkkd54bt5opPm+eKu50+8klkT/nlXm+j+IFrp9L8SebGitXRRqpPQ8bGU5Sd2dxb+Tdfd+8n8Naej3DWsm3f838Vcro/wC9iRl/76res7hTIjN/3zXqQmpLQ8OtBpWOzsriOWPdv2In3V+lMvdxk3K+z+7/AOzVT0+SOX5m+7/Cqfdq5Z7fMf8Aj2feruhrGx5lT4izHApj27ti7N6/xVTuI1it3XZ82+rke7y/7/mVTkufNkTam/f8n/Aap2krGUb82pWuLbzN9ULfzNLk3W/yf3l/hrS+0RxSJvT5fmSqd5b+VJ5i/wDfNFn0NrKWhq6PqEeqRtt+8n3lrVj/AHVcZeW7WsiSwP5MqfxVveH/ABB/an+j3HyXqfeX/np/tLW1Gqm7S3OGvh3GPNE6G3uKmqtb/wBKs12vR2OTToU7yqccf7yr9x/Sq0sdIAjokoj/AHVEklADakqvL3p8X+soAn31Vkkqf5vaqtx/WgA+0fWjzPNpvze1JHQAvze1LSfN7VLSbsBDJTJLf7VVmO382StjT9H82P7ldNKk27nHXrcq0OP1DwX9qj+5XN6h8B47/wCZoY3r2y30Nf7lXI9Lj/uV7lH3VZHiVsRJ6M+e5P2d7X7v2aOqdz+zvby/8sY6+kJNHjqH+w4f7lbqozllUX2j5pk/Zut/+faj/hnmH/njFX0t/wAI1DUn/CPw/wDPOn7RmcpQufN1v+ztDEf9TVy3+A8cX/LGvoX/AIRqGnf8I/DW3tmYyVPojwez+Dy2v8FdJo/w/wDK/g2V6v8A8I9DT49Dh/uU3VaMZRj0OM0vw35X8FTX/hf7VHXY/wBnR/8APOnf2esv8FCbZJ4/4k+F8d//AAVh/wDCk4/+eNe8y6RHL/BS/wBhR0yeU8Fj+C8f9ynf8KWj/wCeNe8f2FHR/YUdAcp4HJ8F4/8AnjR/wpaP/njXvX9gw07+xIf7tAcp4H/wpaP/AJ40f8KTj/54175/YUf9yo/+EfjoDlPB/wDhSkP92m/8KUj/ALle9f8ACPx0f2BDQJqx4IfgnD/ElMk+Ccf9yvfv7Aho/sCGgErngP8Awo+H/njR/wAKUj/uV79/YENP/sCP+7QI+fv+FKL/AHKZ/wAKPj/u19A/8I/HR/wjkdAHz9/wo6H/AJ50f8KTX+5X0D/wjUNH/CNQ0AfPv/Cko/8Ann+lLH8E4/8Anjsr6B/4RaP+5TJPD8cUf3KTm3uB4D/wpNf7lM/4Ugv9z9a9g1i8t7D/AJ5pWPJ4wtf78dXGTQHm/wDwpBf7n603/hSa/wB2vRP+E0tv+elN/wCEztf78f51XtGB5/8A8KUX+5R/wpRf7ld5/wAJra/34qZJ44tf78dZ6gcHJ8E1/uUz/hSi/wByu5k8b2v9+of+E3tf79VGpLqBxP8AwpBf+edM/wCFKL/crs5PiBa/36rSfEC3i/5bUnOVwOT/AOFJr/dqP/hSkf8Acjrqv+FiW/8Az0/Wq0nxEt/79Lmb3A57/hSkf9yOof8AhTEf/TOuhk+JEP3vOqtcfEi3/v1UZNAY8nwbX/pnUMnwfX/pnWlcfEy3/v1Tk+Jlv/fpSd3cCnJ8I44j9+oZPhXD/fqa4+JkP/Paqdx8VIf79VzsB3/Cr4P79Rf8Kzjj/jqtcfFSH/ntVO4+Kkf/AD2pRqS6gaUnw/ji/jqGTwHD/wA9qxLz4sR/89qoXHxYj/v01IDoZPBcMX/LamSeE4f+e1clcfFiP+9VC4+Lin+OOn7RgdtJ4et4o9vnVDJo9uP464C4+LC/36oXHxc/uSUaAekSafbxf8tKrSW9v/z2rzS4+Kkn/PSqdx8SJJf46NAPUZJbeL+OoZNQt/4X315dJ8QG/v1D/wAJ639+jQD1L+0IfSq/9qx15v8A8Jx/t0f8Jo39+jQD0j+1Y6P7Vjrzv/hMaJPGH7v79HtGB6F/bCUf2xDXl2ofED7LJ81Gj/Ehb+fb/E/3aAPUf7Yhpn9qR+1cxZ299dR7oo99THQ9Ulk+5/5EoA+4f919m75f+udD6e3mbvuKz/Kv8Mn+7VmQLFvVU+5toiiWSP5flX+7X5xLXc/VovqmQmNYo/l8xP45I9nzVD/0z2/N/ufK/wD9lV541lKqv3l+7u+aq948nl7m+9/CypWUrpGkJdDN1izW63q33v4l/wDia8r+L/hObT4Ib63SObZ/rmT5fMx93d/tV6vdxzS/eeT/ANB/2qgIj1CCWCdY5t33lb/Jrz8RRVSLVj1cHip0Wpbo+OvGEjRag7ReZ5UyK7L9fvbahs5JtL+ZXj3TJ8y/7JrvP2lPgndeHLd9W0m2j+y/M81un/LNf4mVa8H/AOE4jtbz7PK0e75t2ySvBlL2c+WR9zSisTQVSi7+R6L5ElhJ5v8ArFf/AIF81Ztzu0u8T+CJ93+15eaytP8AGC3/AO687+7830pmoap5umJdK+/yU2bfpXbGUWro4XhWn75qyag1rJ/tb/m/75qa31FrrT0+b5krkpPFiyx/7VFv4kWH+P8A2mreM30MvqrtY7P+0PNt91UP7UWKT5vkrB/4SX/ppHWbqHiz/brNybHTwrW53L6pH96L5/71Zt5qjZdtny1zEfjRYo90tVtQ8aRy2+3zqftGaRw9nc62PxIvl7t9Pk8Wf6O/z151J4kWb7tVn8UeV996Tm2jRYRI7mTxQ11v/eVTk1xvM+/XJf8ACSLFH/rv+A0f8J5axfKz7Kn3jojTSVrHcx64vl/M9VpNYXLsvz/7NcBefEi1+6j1lXnxMhi+ZZtlZNTexpTppyPUbPXPNk+WtjTvEH+3/wABrxbT/iJH/wA9vlrY0/4kRyyfK/8Aq6xnRk9Tp5Lns2n+JFik/wBdXT6P4wjiuPv7/wC7Xhul+KP3n362LPxJ/eesI8yY6mEi42Ppnwv4s+1R/K9dhp+qLJGjN96vmrwX44+y7Pnr0TQ/iL5v8dd1LEWZ87jsvcZOx7fp+sfZY/kf7/8ADWrZ3n7zzd+9a8o0fxp5safPXVaX4wjl2fPXr0q63Pm8RhJxdrHf/aFljTb/AB/xUG4aPeqpsrnbfxB5siKv3f4mrZj/ANWn/fFdcKiexw+za3Jo9t1I7f53H/8AZqnJGvybvkX/ANlo+a1fb/wOn+Wsrorfd/1si/8APTFbEO6KdxJ5v2lW+T5N/wDwKq2qW/k6pttfklR12t9Vq5eSLF8zJ99//Hf4v/QqoeXNLrjsv8G6Va56t07o6qMotXZ1vgvxQviOzfd8l1D8si10NeP6PeSeHNU+3xfOqPsb/pov938a9as9Qjv7dLiJ/wB06K6/7prswdf2kbPc8zH4dUp80dmPkjqtPVp+tQXH9K7DiK0lL83tTriSmSVXLpcSIZ6anWnT1F83tUjJfM/u0P8A6qiLtRVcoitJJ+8ojkpH6VXkvFiP+1Ug3ZXLkci0/wAzzazbaSS6k/uV0mj6HW9Oi5M5a2IjGN0P0jTGl2NXVaXp9M0fQ/K2VvW9v5cderRo8sbng4rEuRWjg8oUeXVzy6ZJH/drs06HD7Vlby6j2VapuygmUrjPm9qPm9qfso2U0rkjPm9qWljjp/le1a8pDdwi7UUeV7VJVESI/L82n+U3+TT/AC6j2VUdiR1FFFUAUUUUAFFFFABRRRQAUUUUEN3CineXS/N7UD5hlFSUUEkdJ5Tf5NS0UAR0nlN/k1LRQBDsrO8UXn2WzfbWvWF40t2ls3pSdlcD5g/aI+Mlx4XjmWLzN38NeCSftJ6tJI6/+1K9R/ao8NyfbPN/hSvmzVLf7LeMv8VCdypRsdzJ+0Zq39//AMiUz/hojWM/K8n/AH8rz6imSd9J+0JrHl/fqGT4+a1/frh6j8r2oA7n/he+tf8APaof+F661/z2FcZ5XtUlAHWSfGjWv+e1QyfGTWv+fquV8r2ooA6T/hbmtS/8vFMk+KmsfxXlc5so2UAbsnxQ1j/n8kpknxF1aX/l8krHpuygDXk8cat/z+SUz/hM9S/5+ZKy9lGygC9/wlmoS/8ALzJTP+EkvsfNcyVSpslAFmTxBef8/MlH9uXn/PxJVSigCx/al1/z3kpv9oTf89pKhooAd58n96Sj7Q396l+b2pJKADzWqGpKKAI6Kn+b2qCgBnmNUMkjVZl71Ds82gAjuGqb7Z/nFVvKb/Jp8f7qOgC5Hefu6mjuPNjrPpvmUAU/Fkcnl7lj/wCBVj+B9Ua11TzZf4P79dJJJ+7rH1TQ1ljeWKmnYD2/wH44t5bdN3l139gVvv8Aj3TfXxbb+KNSsNUSJZpYYk+9sr3r4TfE1hZrHLcydP8AnpVJ3A/Qy4vIZTt/du1PjvIYv+ee5/vbKpvIsn/oK1DcXK+ZtX7z/wANfn0pJ7H6t7HSxq5/dvIrb6jkjj/76pul3H7v5X2L/Er0+STzUf5Nn91v79S0mtTPWLsVvLWST5U+b+Jqqz6f87M33vu7q1vta+XtWH5v/ZqZJceZ95I6xlSdtDSNaaZzV74fa9t3iuFjZXTZ/wABr5J/a/8A2R7rS5H8TeGbPzooUZriGL723+Lav8VfaUlwv3V/4FVXUdNhuLZ45vm31w4jAxqRu1qe1lucVcJVVSH3H5MeE/iY0UjxS/IyfJ88bbq6q88eL/Z77X2b02Nsr1n9uT/gnnqWpzv4m+HcP+np89xpqSKv2v8A2k3fdavhnX/iJqngjW30vXLa5028T5JLe4gaKWNh/stivCdGcHyyR+mYeth8fFVcO1d7o9p/4WAtrcTLL93+GqGofFSGL7r/AMFeD6p8VFuvuzf7tcrrHxYaLf8AP/B8tddOm2i5YWCex9LXHxojij/1kb/79ZVx8bIf+em+vlrVPixN5fyvWJe/FC4H+qk2LXVHCykrs5JezhufVGofGz95t875azY/jI0snzTV8wR/ES4uvvPI++n/APCcXH8U2xf7ryU/qbOWWIV7H03J8bI4v+WlNuPjYvl/K9fN9n4lvLr5o7a5mX+8iMy/1pknjST7R9n37Lp/ux1qsGTLGU4rQ+jZPjgvl/66s28+MDSx7t/y1T+Ef7CfxM+L+npf2v8AZNhazfda9v8Ab/46is1e5fDv/gj/AKxdTpL4o8bWMMX8S6VBJL/wHdIq/wDoNRGjBM5amYRhpI8NvPiZ5tujLJ8u/wC8lQ2/jSbWb9LWzS5vLhvnWGKNpZZP+Armvvz4T/8ABNP4V/D75rzTb7xPdfwzard7l/74j2J/30te3+G/hX4f8EWflaHpWm6VF/06QLF/KtFQucP9sWeiPgn4D/sj+LPihqEMvia21LwroezfI0sflXU6lflVFZf++mar/wASP+Cf/ij4N2eq694V1iTxDo1nD9rks7iNvt/H39uxSkn8bfLX3VqHh+HzP7jVm/aG0a4+aT5aVWioKzNqOOnN2gfmtofxkb7PDK00br/45XW6H8ZIb/8AjjRk+9X0t8cP2D/AfxuuJtUs/tPhXXptzyXGmRr5V233t0sDfI3/AAFlavmP4n/8E9/id8Kd9xpNnH4t0lPn+0aZt+0R/wC9A7b/APv3urz5UYSVo7nrU8wcWlM7nw38VI5dmx9613+h/EeGW3Tc/wA1fHOh/EBrC4e3uHktriF9kkLxsrRsP4WVq9C8L/Ej7n76uOphZQ2O6UqVVXR9aaF8RP4fO+5Xc+F/Hnm/Lv8Alr5L0P4kR+Wm6b5q7zwx8RPO2Mr/AO7SjKcep5+KwUZKyR9e+EvFiynaz/7tdnb+IFit0X+Kvlfwv8RG8xPnr0/w38QPtWzc/wAterh8UlufK4vLWpaI9is9V+1XG7f81XJNsnzfw1wGj+KP4lf/AHa6S38Qfb7fZv8AL/2q9KnX5tzxamGkmbd5cLL9jVv91m+rVQjuPKkuWb5FSFv1rNk8QNLJDv8AnRH+Vf8AZFQ3moebo6Ns+a5dn3f7I+WlUqpO5dHB2Vhkn+qmX+Hfv211vwj8R/arObTW+/b/ADx/7u75q4yP/j3f599TeD9Q/svxJZyq+/59kn+6flqMNUUKqkVjaftKTgz2H5vao7j+lP8AmiqG4kr6CyPmEyG4kqPfUVxJTPM8qh7FRHyfvaZ5dHmU6piA7fSS3CxGq1xcfwrT7fT5L+tY021yxM51FBXZTuLiS6+Vam0/w/JdSbmrodL8Jt95q6fS/C6xfNsrqp4Pqzza+OVrI57R/CflRp8ldbpeh+V95K0rfT1i/gqdOtelTpKKPDq4lzehBHbrFUtOfrTa1Oe7e4U2SjzKbQAU3ZTqd5daRiJuxHso2VJ5dHl1XKiW7i/N7Unl06iqI5mN8uj5aX5vaj5vaq5UJtsPm9qPm9qPm9qPm9qoQnl0eXS/N7UfN7UAJ5dHl0vze1Hze1ACeXR5dL83tR83tQAnl0eXTqKCG7jfLo8unUUCCiiigAoqTyvamv1oAbRRUclz5dAElFUbjVPKqneeLIbX+OgDaqvqlutzb7a564+IEMX3njqGT4iW8v8AHQNK54/+0j4LW/0qZlT5q+MPHul/YLzdX3P8UPEkOqWcy74/nr5F+Lmhr5kzKlY3s7G8kuVM8ukptOk/u/3KbWxzhRRRQAUUUUAFN2U6igCOiinbKAG0UUUAFFFFADdlNoooAb5dNqSo6ACiiigBu+jfTaKAHb6WOT95TKKAJpJKhpu+nUAN302imyUAOpvmUeZTaAHR0S/fptFACSR/u6ZU/wA3tUT9KAMjVNDjuvm2fN/erlNZ1PUvDM+LV5EX/Yr0CSP93VO/0yG+h2sm+mnYD9OLfVIbW3dV+bYnzU6S8+0x7opI1/vN/s1ROnt9oVdu7f8AeWrkWj/v/wDpnv31+bRk+p+3SjTWpYs9bkj+VX+7/FVq31S4kk+/8yv97+5R/ZHlSf7v3qcEjjTbt+b+KqfN3OOfs5fChYtX82N9rf7q/dqWK4X733Kox7YpPlTf/tU6O8Yxsv3V/vNUxm29SXTTWhaS4aUPItMkkWX733v7tJFdt5/y/N/eaq8n8Eq/Iz/Iv+7VPXYnlu7MmuLeO6j2r/wKvPfjJ+zX4N+N2lpa+KNB0nXoof8AVte2iytHn+43BX/vqu8njaKTdv8AvVDJu81F+5WcoRlo0axqSpu8HY+GPjB/wRT+Hviy3uZPDmpa34VvH/1eyf7Zax/9spPn/wDH6+b/ABh/wQz+IVrebdN8YeF9Si/vSxzWrbf91Vf/ANCr9bryzmlj+5H8/wB6s2fS4/7nzVz+xaV0ezRz7Fxj70rn41ax/wAES/jNDK/lv4SuV/h2ak37z/vqKsH/AIc3/HK1uN/9g6TN/d8rWrfdJ/30wr9qp/C7eX8s2z/tnTJ9Pj+6r/vf++qqnGcXcdTOqzjZs+Cf2T/+CR/gvwR4LhuviDolz4k8TP8APNbyySLYWny/LGuxh5m3+83/AHyle2ah+zl4R8B6W6+FfhX4XtrpE/drb6Laq/8A32yivo2OzW1j2t/309Q21vHLcf31orQdTdnFHMKjfvO5+Tv7ZHwL/aA+IN5crZ/DrxJ/Zafw2/kt1/uqkm6vHP2a/wBgv4gS/FSG68VeC/EmlW8L/wDL3YSKlfuXc263cm3Zv/8AHafJocNtv/cx1UZzjTdONtSpY6U6inM+b/hX4PXw5pdtaqu1YUVNr16jZ2flR7q9C/4RO1v490sMfyf9M9v/AI9TP+FaWt0P3Sf+RKxo0eRNIK2O9pLmOA8v+Knx3HlfNvrtrv4VwxR/fuUrN/4V/HFLs/ebv4a25WTGtFq5yV5qCy/71c3rFvJdb/krvLj4bzS3HyPUNx8P7z7uyN6mWqsehhcTCC0Zwel27Wsm7+GunstYjij2r96mXng+8td/7msHxhqEfgjR7m8uvMRYUrh5XF6HZOtGp8TPOv2sPgX8P/jJp/2zxNZ+TrMKbI9UstsV1t/hVmOVkVf7slfnd4o0e6+F/iiawa5j1K1R/wB3eRfKsi/7a/w/99V6v+1Z+2RJ4j1i5s9NvN8SfI0iSblrj/2Y/C83xL8UebdJ51q/3lf5lkX/AGt1bSpOMHOodODqTU+SGxm6F4sj+T5tzfwrXoXhvxw1rGiq+z/ZrsPix/wTf1iLT01n4dzfad775tHuJFVvu7t0Dt97/davE449Q8OapNpuqWFzpupWD+VdW93G0UsDf7StiuP2acdD28PjVJ8iep9CeE/iQ3yfvq9R8H/ETzdm56+UfDeuNHJ8vzLXeaH408rY2/ZsrmlT10Kq0Iyep9aeH/iBJ5afPvWu28P/ABAjlt9u+NN9fKnhf4hyeX9+u20Pxw0sifPVxrSpnl1MtU3Zn0V/bkd1HuZ/uVc0/VG1DyYm+6ibNv8As15L4f8AFjSx/frs/C+qrLe7q6liXJWOGpgfZ6HWyah5Uf8AcamafcNa3CN/cqtcXkflbvvtVDULxoo9y/7lKnU95W7nnyoptx8j6KtrjzbOGX++iv8A+O1TuLisHwfrn2W3TSZf+Pi2hV4f+mi1fvLxRX1kZpRTZ8PUouE3FdyaSSoZLiqEmoeVVaTUGmk2rQncT0VzY+2LFH81RebJdSfL92o9L0Oa/l+auw0Pwmv9yumjh3N3aOTEYqMVZMzdD8NtL87V1uj+F8/wVf0vQ1ijT5K2I41ij+5XsUcLGK1PAxGKbbsVrPS1tavxxrUdL5nlV0HA5NqzH/6qo6WSSmeZTUWyQ8yjzKbTvLq1FoTdg8ujy6dRWhF0FFO2UbKNSZDadsp1FGpIUUUVoAU3ZTqKAG7KNlOooAbso2U6igzG7KE606igAl70UUUAFFFO2UANop2yjZQA2jyvapKKAI6Je9OfpTaAIbmqF3/q60riOs24/pQVEwdYuGijrg/FGuXFrG9d5rsf7uuE8YW/mo9BR5h4o+IF1F91656T4qXnm/fq/wCNLP8AeVw1x9+pltY2UY3ujpLjxpcar96uY8caX9qs3arNvJVy8jW/091rORrGN4tHzxrFn/Z+oTLVSum+KOjtYapurma1Uk1dHFKLi7BT/m9qdb7fMqtqF5H5f+1TJHb6dWTJrv8At0R6wtAGtR/rKzJNZjp9vqkf96gC/HHRJG1Mj1iHzKvx6xDsoAp/Z2/550nkSf3a0INYtzT5PEEP/TOgDN+zt/zzo8pv8mrMniCHy/8AlnVO48SQ/wB+gBkn7r71JVHUPEC/36rf8JIvl/foA0pLimSXEcVYkniBvMqtcao3mUAdD9tFM/tFf+elc9/aTVF9uagDpvtkdH9oD+7XM/bmqP7fJQB1X2xaZJeqK5v+1Gpn9qN/fFAHSfb1qaOPzf8Aerkv7SarMfiBovvPQB0/lL/k0zK+ZXL/APCTt602TxI1AHZxW8f9+jyIf71cfH4wkqL/AISy4/u0AdrcR2/9+i3jt5fvP8tcNJ4ouJaP+EsuIqAO21jybWP5fkrNs7hZZK5u88WXF+fm8uptD1hvM+agDpPL8r71R1JbyLdx/wB+iSOgD9F4/EkMh+ZdjPWxaX/nPuWbb/drm5JGi2/PG+/+F6uW9x5sfy+Xu372b+KvyelJrVs/dq1ODXunR/2hJFHNu8yorjUPJ+9WVJeeZGkrf99eZTNQ1jzZPv8Ay10e1bOONG2ppfbI4onZf++alt9vkfN5jfxbmrn5NQml2bofldKZH4kWKNFZJEbf8tVGoaexZ0NxqkcQb/Z/4DWV/wAJHHE/3JP7m5k+WqF5HNLb/N5b/P8A7tU/s7WsiMySfvv+BVo5PobxoU1E62z1OOV/N/v/ACKtW7eSHzEbZG7VyFxrEMMv3I9396po9f8A3ibfMkZ/uq9HM+pyVsM2tDp49Uhurd12ff8A4qhwunx/3/46x7i883Z+5+ZP4qpvqE1rJtlm3rv+7RzaERw6vobf2hvusn/Aqzbi8jik3Mnzf3krO/4SCSW4m+T+9UtxqnlR7t8aMnyMtSVKi47mlJcQ6hb/ACpVO3kj+zu3+p2fxUyPVFl09Pk+b+H+7zVPWJZLq38vfKlUo3VxQptyuTRySX8iSRea6/7G3bW9cXkP2NPn+7XN+H9trborzRo2z7vl7afq/mSyIsbyps/iqnCyubOmpT5Tp9P/AOPd2i8uprORbSRGaTZ/s1laHqn2WNIvub/7lW/LaW8+b+OiMV0OOUWrpmlqF4wfzVfev92oo/8ASo381I0l/vf886NUj8nT08r/AL5qtZ6hJ5n2fZ97734VfKjKMZNXQXEaxecq/e/vVQuNLb7F5rf8CWrn2n/QHZv432LTNc1D/j2t1/j+dv8AdFRKKSNafNexlXGhyTWabn2b/u/521W1jwusVvul8t/Of5Ver8dx9vk2q/l/wKv+1/tVS1DUJLvX3iVPkt0/8ernlZadztp87aVzw746fsH/AA5+NNvctrnhXTftE3/L5ZR/ZbyNv7yumP8Ax7dXkvgv9huT9nmRG0a5k1XTXf7sse26gX/a2/K1fZnlrf71/h/iV6NY8N+bb7Yk+b/YrGtRU42fQ9KjjnRkoo80+G+2KzRam+Mn7I/gf9pbw/t16w8nVIYfKs9Wtf3V5af7rfxL/syfLWr4k8Ltpcn2qz+T/nsv/PSqGn/ED/R0+fb/ALNTh7Q+MmdOpWl7Si7M/Lv4meENe/Z5+LmqeFdettl1ps2yOb/lldw/wTJ/0zdV3Vc0vXPNj3fc/urX3/8AtWfs56b+1f8ADB4/JtofFWmws2j6h91o5PveS7f8832/8B+9X5mx3mqeEvEE2k6tbSWd/YTNb3FvLHtaCRG2sv8A47Wdakm+aJ9Hl+Lco8lTdHq+j640UabfkrufC/imSLZuryXw/rCy/wAHzV22h6r9l2Vx1Enoz1tOp7f4P8QNhNz16F4b8SNFJu8yvBPC+uSDZ89eneD9UWWPdWNNNM4MZFWbPW7PWGl2fPWhZ/8AE58QWcGzf50y7vwrjdD1jEf367b4d3kM3iD7Yz7IrZK7KFNymkzwsRHkg526HZ+LNc/sHWLO6i+Rk+Rq1ZPEE1/s8j+OvNPHnij+1NYRl/1KfIv4V7H8B9Hj8W+H/ufNbPs/4Ca+ow/7ypyM+TzSi6GHjXl/Vytp/hu6v5PmrsPD/gNvk3JXZ6X4PjtflrbttPjtfu171DAwgz4nEZpJqxiaX4Tjta27O0WL+Cpflo313RhFbHjyrSkx1SVDvo31bdzG7b1JPMpfm9qZRT5RN2Cn/N7UfN7UkdaRjYlu4eXTqKKoluzCnJ1p1FVykBRRRTSsAUUUUwCiiLtUlAEdFSUUCbsR0VJRQLmG7KH6U6igkjp2ynUUAN2UbKdRQAUUUUAFFFFABRRRQAU1+lOpr9KAIrj+tU7iOrr9aguP6UDTsc9qkf7t64bxZb/u3rv9UjzG9cf4ot1G+gs8X8caf9+vNtUt1ikevYfHGn/fryrxBZ+VI9TLa5tBX1M23/rWrpb/ALzbWPbx1pWdZy2Nqe9jjPjJ4f8ANs3avJq+ifGul/2po7tXz9rln9g1CaL+49VTldGFeHvXKcn7qP5a5jWNUaK4rq65fxhZ+TI9aHMZv2tv7lH2hoqZZyebb0SR0AL9uao/tjeZRUdAEn9oSf36f/ak39+SoKKAJ/7Umi/jqH+1JpT9+SmSUeXQA/7bN/eFM+0N/eoSP+9T/KX/ACaAGSSNLRHG1SbKTy2oAZ5TVJsp1FVygHkUzy/KqVOlD9KaVgK/2ajy/wC7U1PjjpcoFb7NRJb1c+zrR9mpNWAofZ/pTJLer8lvR9n+lCVwKEdvRJZ1f+z/AEpklutPlAz/ALHTfs1X/IX0pksdHKBTkj8qmSRrVmSOoZfv1IFWpk6U2igDY0fWPsvys9dJFeLdJXn9aWk6w1q/zSb6rcD9ObeSO63qv+tSoY7e4/hf5v7rfLRL/q/3U0iN/wCjKZJHJ9oTdN/wKvyWUVax+5KpLoXJLdfse2VLlf8AcqvcSR5TbDvVP4njpNQ8yLf5Tx/8DqtHtlj+b5933v3lGpUZOxNJeSXVvt/d7k+7UMlvJLHGzJH8n8KSVDcW/wC4fb5kP+15lQ/2o0UaL52//arSncmNTsWZI28x22SOv/fVM+2N/wBNNyf8s3k2tVNNYW6s32v+9/u/dqteah5Un+u3Mn3a2iHNrdj5NYjijeL95tf5Gb5fvVZt9vyMs2/YmxWrH+2LdbN3+/uq59vb7Om15Pv/AHX+7VFSre7c6GzvJLW3279/96q1zcYDtv8A++6zZNQjtY3/ANW7f8CqGTVJPs6f+Ot/z0oc4paHLHmbsbf2hfLeVfkbZ/z0rNjkWW4RWSTa/wB7fVC31BpY/wB68f8Asr81MjuMSfMmxf71VHla0NIxa3NW31D7LJ8vmIv8K/ep9xqDXUfzfJ/dZKyjqH7vbv3rU1vIsv8Ay0+aqLTaLmlapcWt5tl8uarln4ga61R4mf5f4VrH1CTzY08r72/5mqzp/wC7/wBiq5n1LlFXudJZ+ZLcJ/Av95KuXEjWsibf4PnrBt9Qkik27P8Aton/ALNVm4uPK2bpvl2fNU3a2OSVOTlZnVR6hDfxpJv2ec/zLRZ7f7UuVb5NifLXN2eqW8UaKz7Gd12yVZj877Z8z/M779yf3f4a05lazOf2TWg+z1BbryVZN+zduqHUJG/tyaX7i26LEtVtHj/eQr/Ejsm7/gVZVnqFx/plw377fM23/dqZaxR3RptM0dQ1iHRdMuLzy5N0P+rjT/lpXP6V4gWK3h82b/SH+dmf/lpVPxprn2rULazZPuQtcSbP+Wn8O2qFvrFnFsZn2L9xl/55/wC1XLU3PYw+Hj7O0k7+R3MGqR3V5bLv/wBc/wAy/Ra0ri8uIo5trRwxIm/d97fXE6Pp9v4j2XFvNv3v+7WtvVIrjQdP8pvuv95fvf8AfNEXJRbOadGKnydexfkjW60r9796ZPNrxnx5Zto2v7l/1T7vm/2g1eqaprC/aEX94ivCyL/3zXjP7RnxJX4afCfUvEdxbR3MWlJ9omV9yrHHu+dty/7Nc04qdVQXVm1GXsIyqzvy2b0Oh8L+JGtdlfPH/BST9nNviXocPjzwzpvna9o6MurQ28f72+tV3bZNq/eki2/98/7lXPh3+2R4R8b7P9Jk0pv4mfbPF/30nzf+O1674L8YQ69/x53lteL/AHreRW/7628r/wACrbEYHFYVy9pTfLfdGmFzTA4lqpRqLmtt1PzQ8HeKPNfbv8z+7Xoul6x5saV6F+2n+wXfaNPqHj/4eWElzZv/AKRqmh28f72D+/NAo+8v8TR/w/w7q+b/AAf48+3hF31yVKevMj6jBYynW9x2v5H0D4b1PyvL2vvr0vwn4g8r5a8H8H+IPK2bK9O8D6wvmfvW+euZOx1YjDq2x7T4T1D7cfmj+VP/ACJXc+C7xftnzf6rYzt/d+7XAeD9ssaba27PxBDdahtt4Y4f4JGTd+8bd/tf7tdeFk3UTZ89iabfunT6pb/u92z79e5fsZ6o1rqlzZ/wXNs0q/g1eLWf+n6Xub71eqfsf6i3/CeeUybNiN/3z96vfy2T+tJnznEEVUy6a7I+nPLWk302SSm76+xPxdyb3HUU3fRvoJHUURdqK1iribsSU6KOm0/5vanykdBaKKT5varSuTzMWpKi+b2pafKiSSiiiqAKKKKACiiigA833qSo4u1SUAFFFFBDdwooooEFFFFA0rhRRRQWFFFFABRRRQZhRRRQAUUUUAFNfpTqKAIJI/3dQ3H9Ksy96rXH9KAMrUI/3b1yviCDzY67C8jXy65vXLf93QaHlHjC3/dvXl3ii3/eP8lezeK9P+/Xl3jCz/ePUy2Ki3fQ4b/VSVZt46ZeW/lSU+3/AK1DVzqgk9zVjj+1ae6tXhvxY0P+y9Y81E+V69y0ufypP9muG+Onh/zdPeVf9+og2pE1l7lzxqszxRZ/atPd1+8tadJcR+am3+F66DhPN9LuPKvHiar8lUPElu2japu2fx1fjk823Rv79ADabsp1Sxyfu6aVwINlNkjp/mLS0gI/K9qdsqTzKJKAI9lGyl8zyqWgCOnJ0o2U6rSsA3ZQnSpfm9qSKOmAvze1Hze1P2UbKAII46lopslADqKKk8r2pNXAjoqTyvam/LTAbRRRQAnze1RyR0+Sm0AQSR1D9n+lWZe9N2UmrgUvs/1pksdWqjl71LVgIfLo8unVE8jbKQH6cfbZovlZ9i/wt96iORbqNP4mT+/up9xZ8o0UO/8AvK9U5LOSXY0U3zJ96P8Air8qlFn7encs3tvayx/Kkm7/ANFtVOO8hiuEjmT5n+7JTzG118u+RG/uv8tY+sW8nlurJvX+H/eqNty401PRlyS8+wSbX8t99U7y48r5lf5X/hSseTWIfL8tvkf78bP97/dqGTUFuov/AGWqjJSV0H1drcZcavJ5nlfxJ91qvya55sbtLDvrnpLz7BcJu8x4qfcah5X3X+V6pVLPQqpSskbkmoRyxo2+Pan3at2/76PdF5fz/wANcfc7v4quWWseVHt8zYv+3Vp3JqRfLZG9JeSW0j7k3/8AbSn28izfwVif2o38X3qms9Qz8zUydTSk8uKP+/TBJ5Un+z/t1WkvPNj3VFcap5v3qakio3LccjRXDt/B/sVNZ6gvmbqzU1Bf4auW+26+9/31VJ3LasXP7Q/eI38VTR6p/F/49VCWLyvvfdf7tVbjb/A9NaO5L1VjqI9UXD7f9ndU1xefu9y/8CrmLe4/0lFb560rf97b7d/3Pu1pzIlx5TYj2y+S38W9a1be8k+3u339ifdrBjuG8tGb71SR6g32jd/EtHMjKWuiNG3vMyPt+Rt7Pt+tYmn6p5Wl7f3e3e27f/vVvW8kctw7N8/yb65i409vs80TJ/Hv/OsZya1R1YSUW2mVrye1v/FEm75/3McSt/49VDxRo9vFo3lRQx/vpli3JVazjmtZH/jZ3+99KfJ4k+1apDE3l/udzt/vV5rqSlHlZ9HTote9D5nW+G9LhsZLZon2RL8n/Aq6bUz9r1ixtZH3xJD9okZX/u1wlnqDXX72Jd/8DLWrZ6gt/qDsqbF8lUrsp4hxjynlYrDylLnvsZXji4WWR1V9m/7q15X8ZPCf/C1fhH4k8Ly/P/belXOnq3/PNpIWRW/76avVPFlnHFJ/f/vNXJaJbrJqE3/fa1wVG1UTR2R5fqzhLt+h+Dmj/wBoeF9UddJ165026hdka3u/l8th/vV6L4X/AGvPHHwvuIWupo5mh+dZIpNv/jytXVf8FHPgnffCX9rDxbarpUdzo2qzf2rYzeX8vlz/ADSKrL/dlaVa8Bk8N+bb7YnuYWf/AJZy/vVr7unipSgnfofnMsrgpvTqz7D+G/8AwXM8TeB7iFdStv7SiTbuW7k83zP+Bff/APHq80/aY/bM+FPxG8SQ+K/C9hfeD9cvJt+raS8fm2d3Ifma4gdceW395dvzfe/3/mnXPh/dSR7tm9U/5aRVyWqfDe8lG3y5H31NaFKp8cT1MB7XC1FOnJ6H3V8J/i5a+I7e2aK5jeJ/u17l8P8AXFluE2v/AHa/Jrw/Z+KPh9eefo15fWbf3U+Zf++fu17f8J/27PH3gOWFb/R7bWIk/i+aJv6rXzeIyi2tN3P0LC59CpH98uU/Yn4X3v2rT0/u1ft0ksPLl8n5bl2l/wBZub733a+M/wBnv/gqJoeqRw2+reHvEGm3Hyp5kUCzxR/98t/7LX0h4b/bE8I+I43tbd99vc/dZ/3VxA395VfFeK/aUp2aMcRi4Sn7mt/M918L6hHLZ7m+Rf8Abr139jeOTWfiBfXir/otnZ7N3+0Wrw34UWmofGPWIdL8M6VfXkvyvNeXEkcVrBGfvSMy5r7e+Gfw3034VeG49N01Nn8c0z/enk2/eavq8jo1K1RVXtE+F4pzSlTw8sMrOc9LdkdR83tTKh8z/ao319klc/KyTfUkX36rfaPrS760jFomRapY5Khjkp/mVZJNHJTt9R76TzF/yKDMnp/ze1Qeb70eb71UbgT/ADe1Hze1RxyU/wAyqAX5vanp1qPzKX5vagCWim76N9ADqKKKAHJ0p1FFBmFFFFABRRRQAUUUUGgU7y6bTvMoMxtFP+b2plABRRRQaBRRRQQ1YKKKKBBRRRQBHL3pkkdS7KbJ+9oAzbyOsTVLf93XQ3EdZWqR0Fp3PPfFGn+bG9eXeMNP/wBZXtXiCz+/8leZ+MNPzu/3KUldWLjueOapZ+VJVJOldF4ks/KkeufqNTSJes/vpVrxpo/9veG3/wBz5qpW8lb+j7bqzkias6m9zoi7o+Wdcs/sGqTW/wDEj1Trs/jZ4f8A7G8SO2z771xlbqSaujzpJp2ZyvxM0f7Vp/2hfvJ/6DXPeHNQ82zdf4kr0XUbNb+zeNk3768ut/8AiQ+JHt2+Rd9MRuv0p1Nz+8p1ABSRx0/5aj31bVwJPLo8ujzKPtNQAfZqfHHTPtNR76AJ/KX/ACaZJR9p8qj7Z5taAPjj/d1A/SlkuKZ59GgDk6Ub6b5vvR5vvQBJTo6hjkp2+gCaik+b2plAElFQ76b5vvQBYpslQ+b70eb70ASVHR5vvTd9AA/Wm02SSo99AA/Smy96JLim76AI5KbTd9D9KmQH6qXGmNLE/myb2Wq1xp6xfx+T/d21vfY1lk/0j/vlf+Wi0vlxxblih3/7Pl1+XyinsfskZNHKahp/7zds/wCBeWzNWDrFu0u9WjkRf4WSvSI7NpY/+Waf7P3aytY8H29+nzJH/wAAj+Ss6lF2OilWSdpHiHi3S7jy3ZZvOb7/APtf71cxYfECG6jeKV/JvIfvK/tXoXjzTG0bfKzx7Uf+OP5a+e/jBO0Uj3lu9t9ohffuSSvKqScHofQYOLqx6Hq8muQ3+ntu+9/eSsq41xovLVn3xSfdrwHQP2lI7S7+y3D+TKn8O+uz0v4qafrOxluN/wD20rWNTqa1cvnF2aueo/2wvlp89Pt9U8r7/wA9cHZ+NLXzPlm+WrMniyHy/lm3/wCzXXTqLc5KmGsrHfx6ovlp89atvJ+7/wB+vPdH8SLLv+et6019pY6t1VaxxuhJHQ+Y3ltuqpJeeV/trVL+2P3fzfPUL6qsvzVn7RFRos1be88qT/ZrVt9YXO1a5W3v1lk+X71TJIvmff8AmqJVtbI09ndWOkuNYb/gVM+0NL81YMmqN5dTR6pJLGn92t4y11M/ZNbHQ294vmbv40rSs7z/AG64+PUPKkq5b655se6tXUSVznlTlex2H2xfL27/ALlQ3moN5jqqfwVzdvrH7zdvq/HrHmyKzfdrD2ieqLjRlHVouW+uXH2OZd+xo0o/4SDzZIV3/wAGysfVLj/SNy/IsnyNVa4k+yxwsv3v4qPaNM6I0VJ3sb2qR2/7nb+5Z/krm/7LmsNQuWZ9+91eodQ1i4+83/LHbRHrH7zc33qzqKE3dnfRrTpaXL9nrjWF5tZ/mrV0/WG8z5nrno7eO6k3M9WbO4WLe1cdS8XZHdzRnHU3tQ1iOXYv9yqejwR/aHZfvfxVzeoahJFcff8A96rnhfVPst5Ju/jT71TQ1epzYqny09GZvx0s/DejfD/Ute8TeGI/Emm6btS6X5WlghLbfMXd/d3/AHa8x8D/AAD/AGZ/jxZzRWaabZ3l+ke63uPMs7iPH8Ks2U3V9J6f4X03xv4Xv9L1ZPtOm6rbSW9xG/8Ay0jddrf+OtX5m/Ej4X33wb+JGseH7p5HuNKuZLdpH/5br/BJ/wACj2V9RgcQoQ5Zanw2OwftKrlBuLPq7xB/wRn+F+vWm3TbzW9NX948bfubhZM7tvzcf7H3a4nWP+CEen3Vwn9l+KraTejfLcQbW3fLXlfwz/aQ8efCC8T+wfEN9bWf8NrLI0tr/wB8P8tfQnwn/wCCsjWF5DF400WP9y67rzT933v9pG/9lr1KNajU30PHm8dRfuyujyvxR/wQL8SafHc/YLnTb9t+xfKrzvX/APgj34y8GyP5ulRvbwvsaRK/UD4P/toeDfiFbwy6Tr1i8vy7Y5ZPKaPH+z/wKvZLPxnY3+lvFcJHM03/AC0f5utb/U6c42TM45/jqT95I/F3w3+w3J4Rjf7VD9muE+75se2q2sfCPVvC/wC98n5Uf70W2v2h1z4J+FfGWn/Z1hj+RG/5Z/7NeJ/Fj/gm/Y+I45msHktpX/it5Nv/AI5XFUyiSldao6qfFCk/3iSZ8L/s/wD/AAUE8afs3XFtp1h4n36Wj/NpepxrLayfyeP/AIC1fZvwn/4K2eGfFAhXxJpcthu/1l1p8n2q3j/4CcP/AOhV8c/tIf8ABMfxlo148trZ/wBq28Pz/wB2XbXyl44+EfjD4P6x/or32mypu3Ry7tu7/e+61epg4ypR5XseNmOIp4l89kn3W5/QB8P/AI4eE/irbo3h/wAQ6bqW/wD5ZpPsuP8AgSNhv/Ha6p91fzx+E/2mPGXg28hjv9Kubn5/3c1vu3f99LX1l+zv/wAFhJtBk+wN48+33EL/AGdbXU/9IigYNtZVdvmb5v7rV6lFOb0PnK3uWP1qjkWjeteCfsp/tqW/7QUt1YapZ2+iX8MKy29wk+23v13bW2LJ8+5a9ye48r71buLTsY8ytdFyO4qbzF/yKzY7ipo7ilqUXPMX/Ip+9az/ALZU8dxVcpmXI7j93U3mL/kVQ81qmjkaqAtRyY+7TvN96qp0qX5vagCzTd9Ni7VJQA/5vanp1qOOnUASUU1OtOoE3YcnSnU1OlOoICin/N7UfN7UAMooooAKKd5dEe2KgrmG0U7zKZ5i0Ei0UklwtHmLQAtFOjokoK5htFFFAm7hRRRQIKKdHTqAI6jf/W1N5TVG/SgCm/SqN5H+7rWfrWfeRtQBzGuW/wC7rz3xhZ+bG9enaxb/ALt64bxRZ/u3oNU7HifivT/v1x8kf7x69I8aWH+srgNUTyrh6mRcZDIK0tLuGikrNjkqaOTypKzlG6N4Ssznv2iPC63+j/al+8leFRx19UeJLD+3vCc0Wz+CvmDWNPbS9UuI2TY2+inLQwxMbPmK1eb/ABn0drW4hv4vuv8Ae/CvRfMaqHifS4fEeh3Nq33nRnX/AHq2Oc5LR7z+1NLhuF/jSpjb+bWP8M7yO1uLzTZfvQvvWunkjXzKtICn9mpn2f6Vf8oUySNaYFP7OsUnzUzyvar8lp+7+aqckaxfdpNXAgpvmVNL3qr8tQBJ9po+0fvKhooAfJcU/wC01D5vvRQBN5oo8yoaPN96adgJvNFEci1DHJRJcVYFn7R9aZJP5VQ+b70/zF8tKTdgDzPNpN9Nof8A1VLmAf8AaPpTJZP7tRfN7Uz/AFdHMBY+0NRJJVb7R9KJLhvLpt2An30n2j61W8+jz6E7gT/N7VE/Sl+0+b96oZJfLqW7gP8AK9qjpv2mj7T5tCdgP13/AHfmfN+++T5m/uUzyvKj3bv91U+9VazvFlk+aPyf7zf7NW0g+0yP+58n/a/ievzCL5tj9kcbEUmoLL8sXzt/eepbBI5JN7f99VUkt2Ee2L72/wCZn+9Va3uPssnzJJ8n3qpR5XcVl1Okk0Ox1m0/ewxzf9dY9y15v8TP2P8Awr8RbObzYZLZn+9JabYq9C0vXI5Y/wC4tXnv2ki/u1p7GlUjaSMoVK1Gd6crH50/Hv8A4I33WoXk154f8balZ3H34VuIFl8v/ZZlYV8n/FD9mP49fs56hMsVnbeIbNPvSW87K3/ftq/b6Ty7m3dWeN/71cl4s+Gdrr1n5TQx+VXJ9R5daZ9DheJa8dK6uvSx+Buqft9+JPhfqDWviPRNSsLhP+esbLWl4f8A+CpGm3+zz3khb+Kv1N+Pn/BP/wAN/EuOZbjR7G53/wDTDetfB/7Rn/BFTRftE0uk2EtnLJ91ovlSP/gK1dKFK96sWj1aeZ0ay0aMrwX/AMFJNFutn+k/7a1674T/AG9NHv7dWW5jf/tpX57+PP8AgnB4y+GGobrd7m5t43+60e35a7z4X/DPwXH5Nvr2sXOj6ps2NJqdpIq/7quuV+WtZYfDtXUgqc20YXPv/T/2tNL1mNNs0e5/+mldDo/x0sb/AOb7TH8/3a+XfDf7Eeh+MtP83Q/H+y6dN8LWUkdxbx/7ybt1cB8UPAfxM/ZpuPNv3j1LTd+yO6t922T/AL6+7XF9Xi9ISNo0+WN5xsff9n8TLWWRfnrV0/xpb+Zu31+d3gv9tBotkV/+5l/vPXrXhP8Aao0+/jRftOz/ALaVjKhVggjTo1F7p9jReKFlo/4SjzY/v189+G/jRb38fyzeZ/20rp4/ih5Me1an2sluifqsX8J67H4kXzPmeiPxZ5XyrXkUnxMx9771XLf4iLLJ9/5aPaoPqJ6vb+JGl/jq/b+IG/v/AC15RH8SLfy/v1aj8dwyyffrNya2CWDZ6n/wkqy/x0+PWFlt/wB797+GvOrfxYssfy/P/tVq6Xri3Xzb6t1U1Yy+rNI7mS8WWz/vr/drE1iNfs+63b5qrWeufw1DeapH93fsqHUj0Kp07S1H2/ieS1+VvvVpQeKIYvvSVxOoa5D5js3z7/kX71VrO4kupNuzf/v0OpdWZ2ujFvU7m5la6uE2/PvetK4s2iiRV+86Vj+F7OS12SytvrqrOP7X+9/ztp07W0PLxFVL3TtvA8jfZ7aL+/Xg/wC358L7W68UaV4o2bGvE/s+6kT/AJaMnzRM3/Ad617lod59lkT/AGPvNWD+0Z4bX4jfCPxDYbN9wls13a/9do/3q/8AfW3bXfSny6Hg1KcufmR8Vah8I5NU0/dav5zfw15X8QPCeoeHLjbcW0iPv/557a9b8D/EhfLTbNHt/u16tofiTTdes/s+pWdtcxui7lljVlr0aM3fQ8/F8y0sfD3/AAmF14XvEuLW5ktpf4v4fMr2z4H/APBRzxR4CuUtbi/ke3h2/LL8y17H4w/Yf+H/AMWrN5dN+06DdO/zNbybl3f7j188fGj/AIJZ/EDwlvvPD81j4ks/m+W3k+z3H3fl+R/vf99V61GTPnsRyzd2fcPwe/4Kmafr0ifb4fJZ/wCKKT1+X7tfT/w3/bA0fxHvS11W1m+T+KT5q/n+1vT/AB18G9c+z3+m6lpssP8AyzuIGXzMN/tV1XgP9uTVPC95tvIZEaH70kUm1v8Avlq9GNSSR49WhCW5/RRpfxM0fxRZp9qhj+f+/tZa574gfsteA/irp7tLpti+/wCfa0at1r8oPgH/AMFOJPLRYtejeb5U+z3Em1t3+6//AMVX2B8Ov+ChFnLp8cupJ9g2I3mMkny/73zVtCpzaTOSWFcNYHmP/BRT9kPSf2Qfg1r3irwR4e/tjxHsVIYYo/tUWm28jKkt86f7O51X/wCwr4J0f9i+++Df7F6fG6WG2ufFGt37W+i2ssce20hdWVbza2GkZpVl2Kv3fs+6v0U/b0/4KWN+zJ4Atl0O3ttW+KHxLsFvYVuH3f2LazL5VguxW+827zPLZvvSfNXzf4s+Pnwj/a0vPE/hnxJ8QvEng/wz8NEtvDXheS38uWwv2srfZPfS2zR/NI87S/vFkVmWvaw2H91NHiYrEa8r2Plf4V/twfFD4c+F7a81zSo9e8P200dp9qeD/loV3JHv2n7235a6r4L/APBbD42fB/x5c3kWq2OpaDcv/wAgG9g82wgUfd8r5hLH/tfP838Vd/8A8FO/jZ4N8Jfsz/CP4S+BrOSz0Pw/oMHjDWd237Vd6hdQ7lkl25/eeU/mf9vFfFVnpEeqaHY3izWMy38O+NbedZWj/wBl9qja1VLclO5+x/7Cf/Bdfwj8brO8sPireeH/AANq6TL9hvIvMi027U7tyuzblhkT/aba1favwv8Ajh4P+N2l3V/4N8T+H/FVnYTfZ7qTSr+O6W3k+9tfYx2/L92v5j7yzupYEiiuv3VtudVTb+7z8zfdr0L9nP8Aa48dfsl63Nrng3xPfaPq022KaFLRZbW7hDbtrq+Vb/vms/Z8zuX7TlP6WPtH7ypo7j939+vyd/ZD/wCDgDVLrxpcW/xmh0T/AIR+8/1N94c02RZdNk/208w+ZD/u/vf9+vvz4L/twfCv9oLxY+h+C/Hnh/xDq0MP2hrOLzFlkjHzMy71XdtX7235lqeVrctJtntkd5/DvqzHcf7dc9HeMasx3jeXQX7Nm/8AaP8AppR9o/6aVkx3jVN5rUB7NmrHcf7dTR3H/A6xxceV975Kmt7jzf46CXBpGr59P+0fSqFT/N7UElj7R9Kf9pqunWnUEyJvtNH2modi1HQSTf2jR/aNU9lNoAvf2jTvtlZ/n0z7R9aAL/8AaP8AnNMkvGqhJeKarahqjRWbstAGlJqDQ/71M+2NLXGafqF5dah8z/LXU6b9xaALscjVcgkamRx1Z+WKPdQAye48qOs2TVGlk+Wi8uGurjb/AA0+3s6AHx3ElTfaGqOpKAH+Y3+RR5jf5FMooAm+0NR9saoadsoAk+2/5zR9pptOl+5QAyS4qtcXFWfLWq1xGtAGPqXeuS8QR/u3rs9QjWuV8QSQxRvuf79Badzyvxhp/wB6vNNft/Kkr2DxZH5sb7f++q8r8YW/36TVy4nKpqCxVZ/tRK57VN0UlVvtEn/PSlyo3PSPD+qLdfuq8J+PGhro3ih5VT5Zq9G8H6o0Wobd9V/2hPD/APbPhtLpU+aH+Kso6SsjWrDnh5nhPmU2o/N96krc86Ss7HlvxEt5PCXjyz1KJP8AR7z/AFn/ALNXUf2o3l7vv7/nq34/8Jr4y8Pva+ZslT542qto/g+a10eGKWbe0KbN1NNoQz+1PrRHrH7yrP8Awibf3qkj8L8/fp8zAgvNcWW3+VKzZJPOre/4RNf736Uz/hFo/wDnpRzMDDqKX/WV0kfhuH7u+n/8InDUgcq/+qpkcbV1v/CJ28NH/CN28X8FAHK+Z5Xy1D5TV2H/AAj8P/POj+wrf/nnQBzHltFTPK9q63+z4f4kjpP7Phi/goA4/wAtv+edSfZ2/wCeddh9nj/551HsX+5VczA4/wAuT+5TrOOT+JK6/wCzr/zzo+zr/wA86TdwOS+zzSyP8lSfY5v7ldP83tS0gOT/ALKuP7lPj0O6l/grq9lJJH5XyUAct/wj9x/zzpI/D9x8ldPL9+o36U27gc//AMI/NFUP/CNzeZXSUUJ2A5//AIRGSkk8Jt/froabvpAYH/CJt/z0pP8AhDv+mlb1O+WgD9NJJI5ZPlTf8ny74/lo8yb+9TPsbCPdL8n92PzPmqG9kUybYvM3f7f3a/LnJLc/Z3FN3Hx6gssnlbJPk+9JVPULiOLYqw7l/upJVnf+72qkr/7P8NVpfLiG393bbvutUe0SdkdNOmrj7LVIfM+Z5E2fwpWjb6ov2j/UyOz/AHV/uLWPHJD5+1WkmlT52bZUkt5N9o+5s/vMknzVXtEiqlFN3R2GlXDXX3X2L/tVc8hf+e3+81cxZ6hDFGn+lRp/v1ft/EDRRoq/dT+H7zV0U6ykjya1GXNoXLzR4ZY/lrlfEHgOHVJP9TGn+196uhk8Rxyx7ZHjTf8Aw79tMvNUh+z/AOu2L/31WvMhU1OG6PFvHH7Nem+KPM822jdn/vxrXi3xE/4J56D4jjf/AIlsfz/xeRX2fHqlvfx7Vf5v71QSSW/l7fvtUvDwta510s0r0ndM/LP4if8ABK+18ya6s7byZU+dWT5W/wDHa808afszfEzwlo82mxeJ9budJT7tndv9qi/75kzX7B6r4ftZfmljrifEnwjs9ZkdZLbZ/s+X/rKydOa0R6lHPJSVpxPwo+Jn7P8A4iikdrrSrF/+mlvuiavNJ/DeveEndlm1K2/2ZfmSv3C+JH7K+n3Ujr9jj2/wt5deCfFD9h+1uvO/0b+Df88dEMVUg7VNT0KVTDzV4qx+a3hP44eLNB/6fFT7zJJtavRfD/7Yl9YRot5YX0K/3vvV678SP2F2sN8rW3kr/eT5WryjV/gvr3hL91F5d5b/AMMd3Asv/j1ae0o1PiNuWtHWMrnYaH+2Zot1Gi3Fz5Lfw+bG0X/oVdno/wC0Jp+s/duY3/7aV836gVinddU8Jb1T5Gksp2i/8cdT/wChUy38aeBdLkTzbPxJZsn3tkC/u/8AvlqPqdJq6IljKtP4z6x0/wCKEd1s8qT5f/Hq6TQ/iB5sm37/AP481fJGj/GXwDa/6rW/ECf7T2jbv/HWrY/4aU8F2se3/hJPEm6P+JLBf/iqmeWyl8KMI5xTT1PszQ/FCy/ek2N/EtdVpfiCGXZ89fnLpfxwm8R/Ez7R4Z8Q+IJtN2L9ohvf+Wcn95V3H5Wr6o+HfjS48uFrh/O/vSeZXnYnByoux62GxFOtHmifRtvqqyyfK+z/AGqmuLxpo/mffsrz3Q/GFvdW+3fsatvT9Y82T5n+WuTlOmVNLU2/9bJW9o/7rZ8n/stYmn3Ecv3XrY0uRZZNsv8ABWTd2RKTasdhp+3yt33/AO7/AHY63tDjaKNH/wC+a5vR3j8z/Zrp7e4by9qpXXRt0PHxGm5t286xR7mqG3vJIpNqzb2T59v3fl21D5i3dukf9/52plnZt9omb7nyfL+7raSb0OOUlY/ND4+SN8Ef2kPFXhVfMS1s7xrix3/8+8372Jf+Aq+2rPhf4wato0iPZ3m+J/4fM/8Aiq+tP2kP+CW837ZvjC/8W6Drcem6zZ20FpJavb7lnx5rK27/AIFtr5U+Kn/BO/4vfAuR2utNkurdPuyJG0q17VLA1p01UjseDWzLDxqeyqPU9R+Hf7YFrpdwkWuWclt/02i+Wvo34b/tKaH4ot1js9bsZt//ACxu/wB1/wChfLX5lSeLPGHgi4+z3GmyfJ95UjVl/wC+WWrWmfHzQ7+9Rb/Tf7NuEf5pLTdbt/3z93/x2hVK1D4tiZYTDYhXi0frhfweHfiNo/2DXNKsby3uU/1Mscdwsn868T+Ln/BJP4T/ABkt7qXTYbnw3eXPzrJp8m6Ld/uPn/x1q+YPhf8AtM6p4XkSXwz4zl/69dQ+XzP+BcrXuXgf9vi+0yRF8QaD/vXVk+3/AMeTK/8AjtdVLNI297Q8/EZHNK8GfP3xk/4IZ/E7wRvuPCVzpviqzTc/lxT/AGW6kX/ckb5v+AtXi3h+8+I37NNxqv8AwluleJNN0vw3Zz6hfWOoRyQRTxp8qwrvX/ltI0Ua7f8AnpX64/Df9tDwr4ys0+x69Gjfwx3se3/x5crXYXHgfwj+1J4ofQfGWg6J4q8M6bYf2nJY3sa3VrPdSSeVBIyfdbZGlx/wKvYwuIjXdlJO583i8PWoQ55Rasfgh8SP22PFX7VXxQ+IXxy1zR7aG30fy5bext52+z2l1Iv2awhRmb5lhVfM2/8ATvXlfgvx5NdeA/7G02aNJV2/aLjzN37vbulZf++f4v8Adr92vjB/wSf+BP7QXhfXvhnofh6LwH4Z0e/g1qRvD8n2dp9Wmjb5n8zesipBs2q3yr5ny7K/PH/gpZ/wTX+Gv/BLr9nNF03xJqXiTxv441KS3sY7u0ht/sliFillk2KxbcvyR/e+7cPX0CrtO6Pl+V31PlG4+ME3iPXLm6uppHluX/eM/wA/yj5V/wC+Vre8N+JNPjs/KiSOFX+8qRqvX/d/ir5+j1SS1uK6e3+Ik0ul20VxDbJLbbkWZPlaRS38VXe+pPLY9s8D2cml6R9glfTbmJJmlt7hIPKuo8/e3P8AxVDo9xb67caqtxc21ndWc2yOze0k3Tx/89N/3P8AgNcH4b8f291ob3S3n72F/KaF/wC7/eVq6vR/Hnm2/m7ZHVPkZvm/d0tAL0lu0Uk1nb3Mib/nkhTdt2/w7v4a0vh/40174QeKE1zQ9Y1vRdWsPmsbzTJ2t5YJP7yurBqzdD1j7BrF/eWuoXMP9qwrFeQ/K0U+Pu7t1Wf7cW68UW0UsN8+mzQs+63jVv3n91938NNK4nc+uv2f/wDguB8YPCXxQ0q48Yalc+LfD8KbNSsfsFvFcTwqvzSJKkat53+033q+7fhX/wAFnPhH8WvFmiaNZ6xq2m6lrzrDCuoWDKsczttWOWVcpuZv4vu1+LEmnw3WoW9rF5r3V+7JDHbx7mfC/N92q39hyaXqkNx+8dU+fakm3zKzlRUlodVPFSjo9T+ka4+JF1pfzSwy/wC9UN58dJLCP5vkr8Dfhf8At4fGL4S6xoLab458UPa6Pcr9n0+41KS4sJFLKzRvE7FGVtv935a/Qv4f/wDBcj4N+LdLsLfxf4M8W6DrM032e8/s/wCz6lZwL/z0VmkSVv8Ad2f991ySw9eDvF3OyniMM3qrH174g/ag/ebVf/yJT9L/AGuIbC3T7Q/zf3krofDn7P8A4T+KHhfT9e0O5sdb0bUoVuLW8spFuIp4z/ErL8rfe/vVpW/7Jfh//njG7VySp4jm3O36xglG3KZWj/tcW+syfL5ldJo/7QH2+T5kkq/of7N+h6N/qoY/+/ddJZfCfTbX7iR1vCnXb96VjnrVsJJe7Eyo/jpa2se6V9lUNQ/ag0m1+89dVJ8J9Lut+5I6oXH7PWg3X3raJ/8AtnXYoyPPlKlc56T9rDQ/+e0dQyftYaH5f/HzHWxefsx+Hbr71nH/AN+6x9Q/Y/8ADt1H/qY6zdSql7ppbC31T+RQvP2vNDi/5eY//Hax9Y/bQ0ew3t51Tap+wnoN192H/wAfrE1D/gnnot1/HJ/wCSsf9ob0sbQ+p76mDrn/AAUU0ewk/wBdvrBvP+Clmn/dXza27z/gmX4flk+Zrn/v5TI/+CZ/heL5m8z/AL+VnL63eysdkXl1tbnMXP8AwUghl/guazdQ/wCCjEZt3+WSvRbf/gnX4PtfvJG//A6v2/7A/wAP7X/W21t8lZcmKespmkq2Ba0pniyf8FIFi+6kj10nhP8A4KOLLJ80Mu3/AGK9Ut/2J/hjFHsaz03/AL9rVO8/Yf8Ahzdf8e6W6N/sfLWToYhS/iL7zSOIwrXLKkzY8B/t6aHr2xbh9jf7ddZqn7XnhuJN32m2/wC/i14vqn7F+g2En+h6lJCtYOsfsd2Mse5tbk/8drSFbFQdpu/3GVTD4OprC8X6H0Jpf7WnhW6k2/bLbd/10Wuk0v8AaA8P3WzbeR/P/u18N+KP2U7PS5HaLW5N0f8AD5a1wHiDR77wG/7rVpH2f9NGWpq5lKKu4mtPIYVXeMrfJn6fWfxM0e/+7cx7Wq5H4002X7t5HX5ZaP8AGjWtL+VdSufk/vyV1Gl/tEa5a/8AMSk/4HXPHPoL7J2PhGT2mfpdHrdnL92aOrMd5HL9146/NxP2oPE1rsaK/jf/AGas2f7fHi7QZdskPnL/ALD1tSzqjUdtjjxHCuJg/ds0fo7F2qSvhrwP/wAFNGl+XUrO5hb+99+vTvD/APwUM8L3Ucf2i8jhf/b+WvRjjKL15keXUyjFQ+KLPpeivD7D9uTwff8A/MSsf+/ldDp/7VnhXVfu39t/38WtVWpvaSOaWBxC+w/uPT6q3EdcrZ/HDw/f7Nt5HWlH8QNJv/u3kf8A38qo1IN2TRlPD1Yq8ov7izqEbeW9eXePNH1C/wBQ/cPXpcmuWt1G+2aN657y1und99WlfYyaadmedahpc1rZ7Za868YW7fPXtPiSBfLevMfGlmvzfLQ00VTfU8T8T/6ys2OSuq8WaevmPXJeX5UlI6eZPYms9Q+y3iNXeXkcfiTw28T/AHXSvPX212HgvUFurNF+/srGqup1UU3oz571zT20rWLm3b+B6reYtdv8ePD39l+KEul+Rbr/ANCrhY9ufv1pD4bnm1Y8s2FFFFUZhRRTd9ADqjoooAcnWrH23yvu1VooAk8+mSfvaip3mUAElNpJJKWgBu+m0UUAFFD7qa/WgBtFO2U2gAopPm9qWgApfmlpKXzPKoASm+Y3l7aPMo8ygA8umSR0/wAymSSUAMk/u1HU/mNJSfLQBHsqOT97J/fqw/SopI6bdwP1EuI/Kj2q+1v71Vrez/efN5m3+Hf/APY1ZuLiQSbWXy1/8dqGS4jEm5X2N/31X5o4xex+wU5SKeoR/vNqwy7f++arSaf5sm3yZPuf9+6s3F5/pP3N++j7Zm3T/lns/hrN0rmyxTSsVo7ZYo9qvvb+JqP7LjtY/mff/tPUNxeN5m1fkqa21SSWPb/F/eohS1sEq8raMpyafCf+PeH/AIFULmSLf++3p/drYkjklj3fu99UJI18z79V9XREcZraQyOSO6j+ZKvx3EcVm+xPlRN9Ztxb2/l/3GSn2+oNFsVYfMV/kZnrWMElZBUqRkrouWeqxxRv+5/4F81WYrxZLjasMn8PzJ81QyRrDs+zvs+T5l+9TDqDRR/8e2/b96RPlarMm01axZk1lpXeJoY3/u/w0R+TF8uySFdlVvtkYj3N8jf7VMt9UaXc0sMaRJ91aTdiuS6uiz/wja38kzTJG67P3dcZ4k+H639w7fvHi3/d8uu8t7iHy/NVN6/xb6Zp9xHc3iRMm1Xf7qbm2UuWMtGiY1KlOR4J40+C8eoSOvk/uv4q8N+JH7L9vLeeaqRurp/zzr7b13w3DdSTJvj+Tdu/hauS8QeAo7r5f4Xh+7Wbo2R6WGzKSSbZ+bPjz9mdfMdVs43+f5mrxzx5+zn9knuV8nez/wDoNfp940+Edr9nmbyY9vzP/rK8f8QfAdr+zeXyZNz/AHV/2aXvxPapY6M7KR+X3in9n9pbeZlh2Nvba1eaa58M7zTLxIpU2b/ut/DX6ceKP2d1iuJovscm1Pn3eX615d8QP2a4buKFfs2xt9dFHGVIO5piMvw1eNmj4e8MeE9a8G+IIby3T7nySL5nyyL/AHa+k/hv8TPt9vDFv8ln/hq/Zfs1/wDFYQ6TdTRwrf8AyWsj/d3fwq1P+On7L+pfAzw3Z+ILe5jms/O+z3CpJ/qGP3G/76+WpxmMpVpWfxHHhaVTBz9ne8T07wv4o/dpuevQvC/jCO6/jr5s+GfjRrq3TdJXq+hax/o6NE+yvGrU+Vs+moyU0e2aX4gWX+P/AHa3tP1z7VJ/cryvw3qjf89K7DR9QYbPn2LXA7p2NZ00tT1rwncL5ibq7bT7yPy/9r+GvH/DXiBf3fz13mh+IF8tF31tRqang46m9TrY5FP3v/Zq2Lfb5dc3p+oebFurbs5Glt/9lK7ou55M4tLU9F/Zj1Ff+E41KwZ9i3Ngsv8A3xIq/wDs9ezaho9vf27rL5cyv8jK8e6vkiz8Sap4c8cf8St40lmtpNzP8ny7lrb1T4keMPL3LeW3/fyvr8tx0aeHUJHxmZ5TOviHUj1/4B6F8XP2I/hv8X7Z11LRLGG4f/ltb7VbdXx/8fP+CG9rrMc114X1KxvP7tvcfK3/AH1XrWsfFzxtF928tv8Adrnrj4+eOrWR915HU186w6VqkS8Nw3ik7wmfnp8ZP+Ca/wAQvg3ePL/ZupQrH/EiNLF/47Xldv4k8ZfDS82yw3zxI/8AB83/AI7X6j6h+0Z42uvlZ/OX/rnXN6x4T0/4tXH/ABU3g/Tb/wA75Gmhj+y3H/fafe/4FXiSzPLqkuV3TPajlua0Y3i1Jdlf/I+BvC/7SFnfyf6fbeXL9zd/qpa+hP2W/wBqDXvh9p+vaz4f8SbLfzo4bizvZNqbY496sroxb/lq9dh8SP8AglvoPjyN5fDtzJCz/dtdTjVW/wBlfN+5/wB9V4P48/YH8ZfC/S9KulvLnRLNJmt761uJGitbvy7j5fnXKrJ5bJ/wGuunhedc2EmpejOermSi+TGU2l6aH0/8D/24PFHgnxBrfmTW2t/b9SaW+2Tr/wAfCRrA/wAsm3d80Xy+W1fmn/wXE/agvPjb+1JptvcW32O30fR43W3SDyljmnZpX+X739xfmr1fwf8AALxBdah/bOjeLY5orzUpPtFi8/2W4jkEn72PbJlJG/2t618Vf8FFNY1zXv2xPGFx4jSOPUofs0UixfdjUW8Wzb8x/h+981ezlMcVGu1Wbta+583ncsDUwylQSUr22PNP7Uj+Rt+9nqzHeNs3bPlauVjuGi+b/wAeqzb6hJax7f4a+iTufGuDudbZ6h5Q2qmxXrY0PxhdaX9pWK5k8q5TZIv/AD0ribPXPKj2sn36uafqiy/K00aUzOSs7HqPhP4gQ2uoPFfQyPbunyyJJtaNv71dJ4b8WNrN4lqrxwyzfd3ybVrxa31hqs2+sL5iNv8AmR/lquYfKe5f2pDdXkP2pP8ASLN28tvMZGjb7vysuKv6xrk11b2y2flv5MyvNH5nlefH/d3V41b+M7i1uIZbd/3qPXR3HxIW6uHupfLtt+3zFij2r/dqo1LEnpfiTWLOw0dLiVPL+6jR+Z8u4tt+9TLjR44rdNr+cuxXZref5f8Ad3VzF54ns5Y0WKb7ZazIrtv/APQa0pLz7Vob2q+ZZ29zDsjZI/l2/wCzWntAOz0/4ueLPhpI8Xh/Xtb0q3eaO9aHT9Skt187b/rFVGHzbf73zV+i/wCzP/wcEQ6ZpeleH/idZ3KXltbRWkniLT91xFOyLt86eJvnVv73l7v92vzHivLqWzSW8mtprp/vNFB5SyY/i2/+zV6v+xH+xX4m/br+NH/CJeF0jhuIbaS7ury4jb7PYKn3Wl25Zst/yz/irCrTjPc0o1XTd0fuF4f/AGxIfEfh+21TS7z7fpt4iyw3Cbk8yM/dbayhl/4FUWqftyLo33vMr82Nc1D9oz9gr4iaVofxL8N3OsaDcpI8d8kiyrcRxrvbZcr8u7bs/dyfN/s12f7Pf7VGg/GTxzf6D4o0f/hFdZ099klncSeVLH9392m75vl/u1wSwleKvTk2e/hsfhJWVWCXp/wx9sXn/BRyG1/5YyPVP/h5o0sm2KwuXrg7P4Z+FYo/NihjmV/4qv2fg/w/Ef3VnH/37rypY+rB8snqezTy/DVPehFteR3Mf/BSSb+LTbhKv2f/AAUYWXZusLlP+2deeyeG9L/584/+/dTW+h2PybbP/wAh1H9qVv5jb+xcN/Ieo237e7XX+qsLl/8AtnWlb/taapqkf7rTbn/gfyV5pZ2axRfLbVDqmoX0Wz7PDGlH9pVesgjktDpTO/8AEH7RHiSKzeVYY0X/AG5P/ia8x8SftUeLrq48qKa2T/vque8WSeItek+z7/Ji/vVPoHwv82PdcTSO1ceIzaS0Wp3UMnpL3pxiW4/jp4suov3uq7P9yOsq48ceKPEeoOq+JLlF/wBjbXQ3Hwfhuo9q1Nof7N8lhZzXjPGkWz5f3lef9cxE37P9T0HgcNT952T9Dj7i81iK4fzfFV87fxfvKuW/ijUIrfauvX3m/wB7zKytG+G6/wBuXPmzSP8APXoWh/CfS7q3/epJ/veXWf1iSfvXNJYKGidjy7xBrHiiw/f/APCQ6k6/9dFqzo/ijWtes3X+3r59lekXnwXtftiLB++if+F6m8SfstzaDZw39nD8r/6yOtPrVWcfcTFKhQpzjGbXvbHzl4oPiiXXHX+1bl1/66MtY/jDwf4gFp9o864uf9nzN1fTMfwM/t6z/wBquP8AiB8J9c8G27y2f+kqn/LOs4YqU2nLY1jQjGPubnyjcfEhtLvHtbhPJuE/hqaPxxfS/NElZfxEs77VPiBI1/ZyQt9xq7vwR4Eh1SNNr/8AAa6sVUpUoprUxwsa9Wbg7/cZVh4g1a6krbj0/VL+P7m+vSPDfwPWWRK9I8N/AtfL2768mpmVNv3Nz0o4OUP4h8zXnhvVoo32wyVi6pp+uRxv/o0lfbtv8AI/L/evHVm4+Aek2sH71I3rooZlNauKMK+Hpy93mZ8AR6xrFhcfNbSV1XhvxxdeYnm21yn/AH1X1XrHwj0eKT91Zx7v+udUI/gnY30nzW0VFTMoPRx+40pZfKOqn+H/AATyvw344/dJ++uYf+2jV3nh/wAaal8n2fVblP8AtpXQ6h8G7Gws3ZYY/krKs/C9vaxttTZsrm+sSa91s7Fhacl7yT+Rvaf8WPEFh8q6lI6/7dX4P2mNe8OSfvf3yp9795Xj/jDxJNoN46rHUOn3FxrMe66fyVf/AL6rqhmGKh7lNnNiMly9vnqQXyWp9V/Dv9oS1+IUXlM/73+LfV/xZbrdR7lf5a+VdL+Jln4C+W1+eVK9T+F/7Rln4ys/s90+yWvrMszRTXJVep+eZ5w/Ok3Ww8Pd7E/jCzbzHrz/AFCPyrivTvFHl3UTtE8brXmniCPyrh69vmPmYqy97Qr/ADe1angfUPsuqeV/C9YmV/v1Cl59gvIZf7j1MpK2p005tPVG98bNH/tnw/M2z97bfvVrw/8A1lfRGsXEd/p8Lffif73+6a8E8QaW2g+ILyzb7sL/APjtZ0ZfZJzCla1RFaijzF8yo66ZKzseaFFFJ83tSAWlk2035vaj5vagBaKjooAKa/Sm0eV7UASVHRUdAElMkkby6I/9ZTJJKAJN9H/LOm0vmL5fzLvoAI5GpKb5lL83tQBL8v8ADTX61B/tU/pIjUAL83tR83tUpkjlo2LQBWjkWjzFqaS3/ipkf7qT5qAG1HL3qz5kefmqG42yyfLQAymSfwbaSl8zypKbdwGSSeVJtaj7TT/PX+7RJcLQnYD9Mo9Q+1SP89Ml3RSOu/er/P8A6uubj1hoo/N/hf73+9T/AO1JJY03vI9flUa5+1PDyTsbf2jzf4Nn+/TJI2lkTb5e7+9WP/aEnyfxr/E1XI5M7Nv3q6Kda61OWtRadya8jh+z7WSR2/iqh9oWL+ORP9+priRv97/arK1Dda/Mvz7/AO5W3M+pmtXY0o9Yk8v++r0zULxZfmXzKx47iT/ppV+Ifu/v/wDfdEZJ7A6dnqTS3El1Gn+3/wACqzb3Elrb7V/75rN8xopF21NJI0tUG6L9n5d/LIyvIjVZt9Ybe9vv/wC+/lrEFw0Un+zSx6hJFcf66TZ/dqedFQinual5qn2XYrJv/vK8f/s1PF5Hf2+3/j2Z/wCF46oR6o0Vwred/H/HTzeLLcP+72L9zd/DQrSNldPQv2UbWOza/wDrPn+T7taGl+JIbWTytnkz79ir/wA9M/3WrGjkk0vyZd8jr9xf4l/8eqzHqEMUe7ZG/nfP/dqrJbFSSn8RNrEcl9dzbk/dfM67/l60/wAQRrYWaK3+t8lfvx/Lt/2Wqtcax5sbtE8iK/yMrx7l2ijWPM/4R/8AezfKifdeT+H+7QtrmU4PRHPeINDhv9QeJUjfZD8y/wDPPPzVj6p4Lt4rN7iKH91Cnzeanp/tLXVXEnleF3liT5n+8r/8s8/KtYPjTy7XQ/s6zfNM6o0aUWT3OnDqTkkjz3/hG4bq3dlh3vN8/lp/dWuM8c+A9P168s7BYfJa5dUbZH80de8f2XHpcVsvk+d5KL5flfM3/jtcZrmj/b/FM11cQyQrp8LOv+9/tfxUWSV0ehh6153R8yfGT4J29rvliTfcQ/Ou/wD5ZsPm+WviP/gpH+3hH4o8cXPgjwRDJYeH9FeNNSuLiP8A0jUrhF+df9mFJPu/3vvV+kfxEkW6juVZ9/8Adr8Xv2uNL+y/tb+PLfZsWHWJ/lSlhI05zfN0NsTKo1F3PSPhV4wjv7O3urf57e5+df71e3+F9cX7Om1/+A18bfCvxo3g24/epv02T/WKn3o2/vLX0n4L8SR3Vmktu8bq6fL/AHdtcmOoNHuZfWU42Pb9D8T+V/HXYaN4kaX51+9Xjmj+IP3SfwV2GgeIOfv15Ozse1KKtY9d0fWGi/jrufDeuL5aLv8AMavGNL8QNLJ9/fXaeD9QaW4T56zhuebiKLaZ7f4a1j93tZ67PS9QX7G/+x96vJfC+ofvPmrttH1Rfs+376/f/wCA130bs8DFUXbQ634f/C7/AIWhrmq3V1f/AGCKw8uKPZJ/rN+5m/8AZK7GP4B6X92XXpP+/lfLnxYj8YWviSZtN1W5s9PRFTy4pNvmMF+Zq89vPiJ4ssLjbLrd87f9dK7ZZtQwy5JwuzmpZFiMTLnp1LLtofdUf7P/AIXi+9qu/wD7aVZt/gV4Hi+ZryN2/i/eV8GQfFTxFL8v2++f/gbVsaH4g8Raz965vv8Av41clTiLC21o/ma/6q4xaqu15o+4bf4T/D+w+bzrZ/8AtpV+38MfD21/jsf+/i18f+G/C+tX8n72a5f/ALaNXbaP8L9QMe5nkrpweZ4arrGkjzsRkdaC/eYiT+Z9GySeA7X+Ox/7+VQ1TxZ4J+xzWu+xmt7lPKmhf5op1P8ADIv8S14nH8K7yX+OSrMfwnvP7kletTxEY+9Cmo+iseZUy2Ely1K0pLz1Owjj+G+g6Pf2Gm6JoiafqUzXF1ZpaK1vPIfvM0TLs/8AHa+J/wBrj/gjv8If2lvGmpeINDub7wfq1+i7beyg82w8xI9itsb513bfm2t/wGvq6P4V3kX8f/kOrMfw7vLX703y/wC3XXTzCqnpba2pzVMnwsk1rqfjDqn/AAQf+LQ0u8litvDb3FtMyQxxasrNdqP4kZlT/wAer5g8afsd+NPBHiDWNL1Lw9q0OpaD/wAfkP2CT/R/m27m+X7v91q/pF/4Q+6/57VoR6feWtu6s8j702ba7qOZVtbpM8XFZHhrpQk0/M/lok8J3lrI+2GSZv4dlZslvJFI/wDBs+9/er+kP4kf8E4vhH8ZPHk3ibxH8PdN1LVrlNlxIk9xbxT/AO00Ucipu/2ttfM37QH/AAbz+G/G/iyzv/AOsSeFdNm+S80/UI5L/wAtt3/LB2Zf++ZP++q66GbU5y5ZJ+qPLxGR1aSvFpn4sx3Elr80XyVNb6zJFcbmr7+/as/4IF/FL4I29tf+HLP/AIWFpt5N5LLoVpJ9qtP7rPA/zbf9pd1fMfxw/YD+KH7PFms/jDwX4k8P2ruqLdXtgy2+4/Mq+b9z/wAer0qdaE/hZ4dahKC95Hlf9uR+Z8vyLVyTWFi/j3q6Vm6h4TvLX70Oxahs9Puv7QhWDzEuN6+Xs/vbq0MErHVW+uf8S9/4FdP3f/xVbej+OLqKzSJrmSaJHby1f3rj9c0fWNB+XVLa5sJXfesdxG0TSM33vlaq1vrDeXt/i3002iWrHqml/FBrnS0tWSSGVH3/AOs+WTNe6yftKax+y38L/BNh4VvLnTdc1tJ/FerXFpfyWtxIsitbWEP7tt+2KJZbj/t8r5a+FejzfEH4iaJoMM2yXW7+DT1k/wCebTSKm7/x6v2e8ef8Er/2Y/iN4PttG03W/EngPxBo9mySXl7IupLqWyP5pJ4m+eH5U3fu/KVaiVbldmb0qMp7I6H9nb9se4+IP7P/AMGfil+0t4mj1uK58SR6V4dtbuNYmtIfMgknvrnYoabCWyL+83f8flfQd9+yj+zL/wAFPbjWtU/4SBNL+KmsalPeteW120F/ZyBVWKFYnYRzeWipu2/xb/mr468SfsB/Fj4yeD/B9xr194S0pvBNhPD8OfAtu8a6tftHCzxSXL7vJhZ/kmZpm/5ZwLXxV4p/Zv8AiV+y34j+1a9pvjbwTcW03+s12xm+y7v4dt5H8rfe+9VxqJhPDSvY/SL4h/sm/tKf8E6Z5pms/wDhbXw9sPm/tDT0ZrqCH/bibLr/AOPL/tV337O/7XngX4+26RWt5HYal/y0t7j5WRvu7WWvlX9kv/gvn8YP2ZPs1v4t8zx54XTbF5d1Itw0cf8AeS5T7v8AutX1LB8Y/wBjT/gqBafap5ofg/8AErUP3tvqMTrZSvMf+mir5M3vu+aufFYGjiY3kk/NbnZg8wxODl+7b5ex9BW/w7muo0mVI3if51kT5lkX/eFaun/C+aWTcybK8B1P4WftBfsFWFtq2m/8Xp+Hjvva40f97dQQ/wB5ot27b/tRs3+9XuX7Mf7cHgP9oyz26beR2esp8kmm3fyyxt/d+bb83+9XiSyfkfNe6Poo8Sxqx5bWZvS/DuSKP/crHj8Bt/aHy17HJ53lvtsN9Q2fhvUJZPN+zRQq/wDfpxy+Nu4/7Wb0/M4C3+Edvfx77j/vlK0rf4X6Xax/6muwk0OS1TdcX9tCv8Vc9cajpPmP5niS3h2f7a0pYOMY8zRH16pOSg5fcVv+Fd2NrH5rJ8tY+ueE7rxRH9liSSGz/wBiSuk0/UNBtfveJI5l/wCui1sf8Jh4bit9raxbJ/tVn9XppWbSNFiKsWtG35q/4I5Xwv8ABvSbCNN1tG7f3nrV1Dwfpdr+5a2j/wB5Kpyahpcuqeba+JLHb/deRa2I/GlnYJuZ7G5/vMklY8tK/Lyo6HKt8bd/K1rHPT+H7W1k3Wtt+9/hZ6hvND1zxHH5X2mNIv4Vo8SfFy3GsbV8tLf/AK6LWxoHxQ8Py7Fa5/e/3fMrhjisPObhGdj0qmFxUIKq6d2YNv8ADzUtGj3Lc764/wCJnxUsfhzp7tq32V1T733WrvPih8UI9L0Ob7BZyXMsiN5eyviT4geB9e+LXiiabVJpIV3/AC27/wB2uXGYrD0knCWh6eV4HEV7ykmj1Hwf8aPg/wCPNUe4urO2juE+T54K3pLb4S6pJ5trNa2cv+x8teV+F/2R9Nl2bodjfxV3Oj/sp2Z2RMkf+9XPLOKM6fJTp8yNZZPOnU9q6zidho/hfwzL/wAeutx/7O/a1dDpfgf7jWuq2zrXN6X+yGp2LF93+FkrY0v9kvUtL+a1v76H/cdqxioVP+XD+VzSVRwWmIXztc7Oz8B6hLbptmjerMnwz1C5j+ZK5LS/hn4o0G42vqt1t/hrVs7PxZpdxtW/km/367KHsV8VOSPOre3bvCpB/MuH4J30v3YY6huPgnqkUf7qGPd/erYsPGnia1/1vz7a1dP+JmsS/etvlrujh8vnvzL1RxTx2ZQ0jyteRw158D9alt9rJG9cTrnwH17S7h2W23q9e36j8VL6KL57auY8UePNa1Ty1iT7Nv8A4njpzwODjtKQUc4zJK7ijwfxB8D5rW4+1apDsiRPlWvnL9oPXLyw1Tbpv2lIof4a+z/iJo/ia/g2S3Ns8Tp/HXj/AIg/ZruvFEjtceXu/wBiOuZ04U5Jx1OyGKr1VepdM+M9Q+IOqeXt/iqhb/EjWLC4SSKaSFl/iSvqvxJ+x/a+Xt/5ap9793XDeJP2W/su/bDG6/8AXOvSdSnC0Jqxxx9tWi7Sdjj/AAX+2xrXheNItST7TF/erY1j9vDSZbfc1tsb+KsrXP2d1luNsttIi/8AXOuD+Jn7OccWn/6H5m7+JXjr1qeMtBSR49bL1Kbi9zsLj/goJ4btfvJs/wC+qx9U/wCCjnhuIbdkj/8AfVfPGufA+P8AtBIpftKJ/E3l1Q1f9n/T4p9sV5JVLG3VznnlnLokfod+y/8AtEab+0P8O7q6sH+awma0mX/x5f8A0Kn/ABg0/wDeWepKn30+zzN/tD7teAf8E7/D6/CXx5eaf9p8611622bf4fOT5l/8dr6m8UaH/bPhrUrXZvlRPtcf+8laUKzlLmj1ObHYWSw7py3PJ6Kijk/d0/zRXpt3PmZKzsElPjj/ANumfLLRJ/s0hB81M8zy5KZ/y020eZ5lADt9NoooAKPmopr9aAHS96bso30kklACVHTvMptADvMo8v8AdbqbTvMaX+P5KAF+b2qLfTqjj2+ZQBJ/rKKT/dplADt9N+WiigB8clQ+Z5X36V+tNoAb5rUeZ5X+7TJI/N+aloAd5lHzURffqaORaAK9Ry96svJHF/B/wGofM82m1YD7tk1hvs/yp8r1zd548h0G8Tdc/wCjybkbf/yzrp44Glj2/c3/AMNcN8UPh/8A2ppb/Js/3K/F6jbj7p/Q1KMFO09jqrD4kWcuxfOj2/wt5lbEnjS3i2fPG/8Adavgn4oeMNe+EF5MsV5vWHc8avJ8tZvgP/gpbpP9oJYa5ef2bInyKzyfLV0a1a+x2VuH1OPPTZ+iP/CQw+XuV6p3muQ/89o6+evB/wC1JpviPT4Zbe8tZonT5WSTdXS/8LQs7qPcrx13UcU2rM8OeVzhueo2esN5kn77f/s1sW+qfu/m/wC+q8r0fxgv/Pat6z8WRyxp89dUat9jlqYS2x20d4oo/tDypNyvIi/3q5iPXI5f4/lp/wDaEf3Ypq05k9znlRSOwjk/e/fqb7Ot1H83/Aa57S9U/d7d9aUd55VU5JK5Er2sy59n+/RZyTfMtVvtn7z/ANmqzHcL5aVN10LjJpWLlxbyfY0+f5qht7eOWRIpX87fTP7QWX+On+ZHLcI39z7tBMZTLnmfZbfybf738Wz+792qEklxrOyJfMRUTbJvk+V/96po9QjlkTcnzbG+b7tZtx4gmtbi5Zfu/wALVfMjajFvRE2uf6xIlTyWZ/mX+His248nVfEttDL95NzyN/tU+TVPM1C2/gZE3rVD7R/xNJrpn2bE2/8AAq5pTtK6PUo0pM6S80tYonltZpEX+95nzVx+sXkkXh65kuPL82/mbayfejjStKPxZ5UbrL/c+X/eNYniTUI7qOGJfL/c/wCWqXjLO1zow+FlF+8eP/ESOH95Krxor/PIz/3RX4mfFTxZ/wALK+MnjDxB/wAs9Y1ie7h3/wDPEyNs/wDIeyv2J/bM8QR/D74H+Ldc3/8AHnpU/l/w/vCuxP8AyJJX4tyQN9o/3Hb7lduAd05IrGU480UX9D2mPymT5d9d98N9dvPBtxti/fWbv80f/wATXG6PGssfzV2fhuTMibn+5SrVL6M9DC07JM9s8N+IF1SNGX+P/gNd5omoeVs3V4z4X1T7L/8AFV3nh/XVlk+/vb/brxq1NWPbjUdj1fS9UWL5Pv123hvxAuU+evFdL8Sfw7/lrfs/GK2kn+u+5XM4NDlFS91n0bofiSPy9rP8v8Vex/s5/D+++NPiCa1tZvJtbNPNuLj+FP7i/wDfVfMH7O/gPxJ+0N48ttE0OHdv+eSZ/wDVQR/xSP8A7Nfqh8D/AIN6T8B/A8Oh6X5k3/LW6un/ANbdzH70jf8AstfQ5LlM68ueppFHwXFedUsDSdKlrUf4HiGsf8E/7jUPva9cv/e/d1zGof8ABNCYSfLf7/8Afr7Mjkp3+sr3KvCeBqr3r/I+Jw/G+a0HZSR8UW//AATv1TS5Plmjda6TR/2M9Y0vZt8t9lfW6f62prb91XBLgHLXLqdb8RM0as3E+b/D/wCz3q2j/wDLtG9dJH4CvLBE3Wfzf8Br2ySdYvvfe/hWi3s/tUnmtXq4XhfD4dWg/vPGxHGWKqS96KPI7fwfdRfesKvR6HJEP+PCSvWo41okt4/M+5Xessj0ZzVOIqkl8J5L/Z7fxabJ/wB+6hk0uH7zabJ/37r179zWZrGsWNq/2dnj3Uf2XF2bloZ/2872jHU8lvLO3/h02Td/1zqGTT7fy/8AkFSO3/XOvWrfVdLtY/8AXW27/gNPk8R6bFH/AK6OreFio8kWjP8AtaTlzODZ4/JZ4+7o9z/37o8y+i/1Wj3Neo3nxA0ex+ZnjrKuPjJo8O9lhk2x/wAXl1nHAQtbmOhZpUm9KbOAkt9aufli0fZVPxR8KJviX4XvND8R+HtJ1jRr5NtxY6hBHdW86/3WR1K122oftCaXa/8ALGSsHVP2sNJsY/8Ajzkm/wBym6dFOzmyfbYme1JHifxU/wCCT3wj+Mngd9H1b4b+EtKiS2+yW95o+mw2F1YL/C0Txxhfl/2lavmPxR/wbD/DPWfA81vpPjDxbZ64m54b69jtbi3kb+BXiSNGVf8AaV6+87j9rjS7/YrW0kKv97dXVaP8YF1S3RlsJUST7rV1U50afuqT+Z5tfD4qfvzgkj8IvFn/AAbX/tBf2fcyxW3hfUriwf7PawxeIY1aeMfdZPMUKq/7LMtfGHjT9i/4heDfFGsaNeeEvEFtqnh6ZotQh/s2ZvsjBtu5tse3b/db7rV/VlcfED95t+wSPWV4k+LjaDbu32PYz/wvJ/rK2daCV2zljh6knZI/mV/4Jt/CvVLr9uDwa0Wgya9deHrmTW20lP8Aj4u/ssfm+XGrfxfxV+pvx0/bc0v4l/DvWPDN14P8beEtcmhj3R63pslv9khM0STyK7qPmWNn27a+zPHHh/wT8Vbh7jXPh74XvLz5kW++yLFfx5+9tuY1WZf+AtXAeIP2T7PWdHvtN0O88SfZbmFkh0/W9WuNW03cV2/OkzNNtaPfH8svy+ZXlYynCb5kz3cv9rQXK4qx4n4o+KHgvXviBqTWfi2P+0rOZfL1a7kZop2Ee14Ub7nzK6bv/QXrv/C/xs8eaXp+3QfGei+IbCZNklndzx3UUi/3fl2qv/fNZWj/APBL/Ute8Lw2GpeFfhfZ2thNIljYxWmpXXkK/wA7yfbPNim3PJ/Dtb5Y0rm9V/4JPeKNGvPN0vwfYvap/wAtNH8d3S/+OajaSr/4/XNTp1YaxZ1VKuGm7VImV8SPgX8J/HmoPdeKvgnJ4Y1S5+ebVvA8n9m/Mf8Alp8n+js3+9FXgPjT/gl/4Z1nWJrj4afFHSXab/WaT4rsG0m8kb/bnjU29x/wKJa+k7f9hv4heFxtih+NGgt/eso9P1m3/wDIN5Azf98Vj+LPhf8AFLwbH/p+pR6rb/8AUx+D9Ss2/wC+mtHi/wDItawxWKpy2uR9VwVVcsZWPFvBfxL/AGuv+CZ0/wBqtYdXfwjM/mqyeXq2gyf70lt5kMf/AAJYK9Utv+Ck/wCzr+2ReW118bvBupfCv4gqmz/hPPCX7pZ2H8Tsm7zF/wBmTzazfDfjDxNYao6eH0slvF/1i+FPFEPmyY/vWyyk/wDjlQ/EGz0v4gyQ2fxE+Gkd5dTOsUNxqHh6TSdUkkLfKv2y28hpNzf89GatY50tFWg15nLPh2TV6Eon0h4L/at1z9m/xg/gvxH8VLbxx4VvrC01Lwr4otdJmaK7s5FZttzKm5Y5EVN3y/Lt+b5NlezXnijXvEenw3S+J5LyzmTdDJZbWWRT91lZa/Nb9nvVNQ/Zg+IH/CW+ErnxT4Vlh+028en/ANkrrmk2FmW2JCyTMH2tEqbvn83dvb+OvpX4H/8ABQTwvp/iS4ia30Xwbq2pP80OjyTXXhzUpv7z2EircWEzf3rRZf8AaV6jGWxMrQm/uf8AkbZfKeDi3UpJns+qaHq11vaK28QX8v8AtyNXMXHwj8UX9xuXwlcuv+3PX1v+z/4o8N/GT4d22vaT88UztDcKkiy+XMjbXVWX7y7vu138fh+1i/grDEZC6qUOfRHRh+KvYuUuRXPjDw38K9YsI0+0aJfWzf7G1lrrdH+G8csf+mJJCv8AF5sdfV0ej2/9ynyeH7OX5Wto3/346mjkMaa3uZVuKJ1HtY+YP+FJ6Hfx7ovsMjJVO4+C8dr/AKqGRP8Aaikr6fvPhnoN3uaXTbbcn8SR1yGqeH/CctxNa2s0ltdI+z/WNRPJbtWSLp8SJK8mz5x1j4H3Gsx7ovtzyx/xeZXN3Hwf17RrjdF5vyV9n6f8K47C3T7PeSOn+3U3/CFt/Ekc3/bOvJxvCqqzfJoe/l/GkqVP35c3qfHOjz+JrW4Rbr7qfe3x1T8WaXfa/cb1tvJlT7rV9aSfDuHVNUdmsI3t4fk/4FUOofDvT4o/m0qT5P7sdc+I4ZqU8MsPGe7vJ2erN8HxpTqYl15Q0StFbaHzH4Q1zVtBkRLyzjuVr03wv8UPD+E+2W0kP/j1dprHhPSYo9zabfJ/2wrjNc0PS5fuw3KL/twNXl0crxGGleEk/VP/ACPRqZlhcavejb5o9I8P/EjwvdRosVxbK391/lrqdP8AEOlyxptubd/9yRa+ZNQ8B2t1/qkj/wB77tYmqeA9StZP9FvLlP8ArlPXrRzfE0l+8pJr0PIqZLha79yq0fWOqR6fqn3Xj3VQuNDjikTb5b18c6hZ/Ey1keLSbnUv96X7tbHgfWPi9pdwv9qXMc0H8LPXVRzmFeaioGNbh+phqbnGqnY+orPR4bnVJmZP3SU/XNPt7G33KnzV454P8Q/Ea1lfzdNieN3+Vq7nT38Vazbol1YRw/8AA673iqNT3Ix22PHjgcRRfNKektWX/wCz7f8A1t08aVz3jDXLW6j+z27x10MnwvvNZt/9MupP+AViap8A1/5/9lcmKp1uW0I3PSwlXCqfNXm/Q5vxBo1r480eGKK8+zX9t93/AKaVlW9vfeEj5VxbSSbE/wBYnzLXUXHwXWKT/RXkml/vJXWWfg+6h8P21neP5zO/zN/zzWuTLsuniK3NVXK1u1szszLNqWFofupc8X0e6OA8LeA28W27zyw+Sv39z1pXHwj0mw+ZreN2r1STT47C3SKL7qfItc14kj+y2czf3EZ6+1jgableXQ/P5ZpiGrRk0uyPDtb8H6ff+IJlW2j8q2TZ/q64nxZ4H02Xf/ocf/fuvW49Hki0t5WT/SJtztXC+LLP79dmIhSb5bHHha1Ve9d/r8zwTxx8J9Duo5mls4/kTfu8uuA0f9mfw7r1n9omtvvvXsfxU8yLS3XZ80zrFVDT7f7Bp8Mf9xK55YelybandTxeI9p8b0PPdL+Adn4N1SwvNLeSGWzmWVfwavZrONftm776t/6CawfL82tjw/cebZw/3oX2N+FctTDwguaJ6NPEVaj5Zv0PH/Gmh/8ACL+LL+1/hWbfH/un5qy69E/aE8P+VLZ6kvz7/wB1J/6Eteb7/wB5XZGXMrnhYim4TaY7fTqj8zyvlp8f+VqjET5abT/MWj/VSUAMoo8r2pu+gB3+qjqL5van76Z83tQAnmtTaKKAG5/eU2SRqkpJP9Z/uUAEknm/eplFFAAn+tof/W0U3fQA6myfxU6mv1oAb/6F/FSy/wCrpnmUSfuqAHA/I9R0/wCb2plADd9L5jf5FSfN7UygBr9KbRTX60AOqNPv07fSXMbRfeoA/R238N28tvt3/vf4f7tZusfC9te0/bvkSL/Yk+aSuw0ORZbj5U+VE2NWkL2Gb5v4Yf4q/JYUoyjdn7jUr1Iy90+SPjZ/wT7t/ihp80VxqtzbL/yzVP8Aln/wKvkL4wf8EDF8Uax9qsPGGrKqJ8y+Wv3v71frQ/8Aq93/AANqh/s+O6jT5Pv1mqDg/wB22j1aGdV4Kzeh+Ikn/BJj40/Ayf7R4S8ZXDLH8/lS/NGV/wB2t3Q/Gnx0+EFukXiDwlJqUUP3rq1k/wDZWr9mrjw3ay/K0P8AsVkax8JtP1mP95Zx7fuV0RjVqb7+hpU4gitKkdD8oND/AOCgsnhy426zo+t6b/eaW0avV/h3+3Z4V8W7FXVbZG/uvJtb/wAexX2l4w/Y38K+I45vtWlW0yzf9M9zV4n8RP8Agkv4J8bxzMmlRw3H8LJV+xqdER/amAq/HoUPD/xw0/VLf91eRuv/AF0Wun0v4mQy/wAdfOviz/gkv4i8B77jwr4k1awb+GNJ2Zf++WrgNU8H/HL4GSbrqzj161T+Ly9rf+O1PLOHxI2jQwldfuJr0eh91aX48WWT5nrpNP8AFC3Uf36+A/D/AO3hJ4X2ReJdB1vTZU+83keav/jteu/Dv9tTwj4o2La63Yo7f8s5ZPKb/vlq1jUTRwYjLKq1UT63t9YWWP5pKfb6h5v+5XjmjfFyz1ONWW5jdX+7+8robfx4t1/y2pOrY5JYOS3R6L9vp9vrjfOrVxVv40WX+P7lS/8ACUR/8Cpe2HHDtLY7C41T7LHt376wr3xAxk2t953rmtY8atFEn775a57VPiB5tx8r7m/hqXWurHXhcDJu7OtvfGjRapN8/wAvypVaPxp5sflNJ9999ee3PjT92zM/zO9Q/wDCUW/2dFWbY1c1SVlufQUcLpsehaprEkke5X/3lrK1zxjHa27q3mbn+7XGap44k8varfL/AHqx7jxJNqmyG3SS5vLx1t7eNPmaRnbaq1xKTb0O+OHjGHPPRHkX/BUjxxN/wy9eWFrDJMupX9pZTSfNtjUbp/mb7vzeVX5jfY18z/Z/u1/QV8QP2P8ASfG/7I+vfD7Voba61TXrZriSb73kXwXdAyN/sN/7P/fr8EfH/hu48EeKL+wuIZLa6s5mt5oX+Vo5Ebayt/wJa+2hl88Lhoc/VXf+R8Jhc4o43E1I0touy8/Mp6XH+92rXVaPGud1clp9z8+77ldhodwssdeZVi27H0uHrRS1Ox8NxtL5ddfp/wC6j3f3K4/w/ul+63zV6R4P8F3F/Ii/cV/nZvM/1dcjwspLQ2ljIRV2ybT7dpZa+gf2U/2M/E37RmuIum2ckOkwv/pWpXCMtvAv8Xzbfmb/AGVr0L9gv9hu1+Mmppq2pW3neHLOZfMuHj2xTsP+Waf3m/8AHVr9JtD0Oz8L6XbWGm2dtYWFmnlW9vbxrEkaj+FVWvcy7IXP3q+3Y+Lz7jR0k6GE+JbvsYP7Pf7Pfh/9nPwWmk6Db/6Q+37ZeP8A627k/wBr/Z9Fr0K2qhHu/v1ZjjbzK+up04wioxWh+X1q9StN1KrvJ7svx7aPMWoY46JJFijdm+4laHLKOty5HJRcagtrH/tf3a4DXPHmqXX/ACDbaSGNH2bnj3tJXVeB7fUJdPS41L/j4f8AhSnF2ZjO9jb0+3aX97L97+7V2q9Sb1rRu5lpayHybvLbb97+GuP8aXOtWlm+3+P/AJ5ferrZLhbWN2/uVx+q+MNUlvPKtbaNE/hjl/5aVE4uSsXRruDvucl/aGtXUjxL9u3J96n2+hzXVwjXFtcvL/eeOvUdDs5IrPdcfJK/3tlXPLWudYVKPLc3lj5OTlyr5Hld54bk8tNtnI//AGzqtceF9Q8v91Zyf7teu+WtJn93RHCxj1J+vT6JHz5rnhfWrXfKtnJ8v9+uD8YeJPEWx7O1to5mdPmWKvqXxh4L/wCEt2K15c20X8UcX8dVtD+Fei+HI90Vr86feZ/maueth6jdo7Ho0MypwhzSep8YSfDvx1f/ADf2bfOtbHgT4CeJvEcjzXVncx/wLvr6i1jxpceZtsLeJIv4d8f+srp/C9vdRaPC115aSv8AOypRTy2MXdsqfEFWSSUUeA6H+x2scaS3Cb7j/b+7XpHgv4Jr4Xs0WW53tXouxaNi1tRwNOm+ZbnHiM2xFWPI3ZGJb+C7W2+987VQ8QeA9JupE82zjmun/wBWr1c8Ya5JFH9lt/tKSyf8tEj3VQ8D6XqUtw9xf3Mj+S/7tX/u13e7fVHm+1qLVMv6N8O9HsLf5bC23fxNWlb6HZ2n3baNP+2dXKPN96iUU3ew41KiXxMh+yQxfdhi/wC/dH2dc79lOoq+bS1iXJkXlrTzI38LyJvokptxH5sbqr7G/hb/AGqiSu7gtO5x3xAs/B+qSPb+JNH0TVW/iW702O6/8edTWPof7Nfw9l0/da+FbGwiuf8AlnaeZZrIp/h2wsq7a6r/AIV5by3O66vL65/vL5m35v71dDHHHFGqr8ipSlCMlqkUqkls395yXxA8J6Dfxw3F54e0nWLxE2R/aLSNmjUfwqzrurhtI/Z78B/Eu4uf7U+G/g10t32Sb9Nhb/2WvYLjT4bqT97DG9Gl6fDYR7beGOFX+dtny/NS9nFu8kHtJpWUmQ+E/C+m+DdDttN0mwttNsLZNkNvbxrFFH/F8qrWxHUKf62rkcjVZBZjjp9VvMb/ACKPPb1oAfqFn9qs3i86SFn/AIkrmP8AhVn/ABOIbiW886KF9+1466WneZQBNHu/4D/CtcZ44j1DVLh/s/26HyfkjaL/AJaV1vmUeZTVkBifDuzvLXQ0a8eR5Znb7/y10NR0UtQGyRrTJbOGX70Mf/fupPm9qTzKXLF9EUqk1tJlO58Lafd/62zt3/7Z1myfDPQ5ZN32C2X/AHI63vMo80VnKjBu7SNI4iqtpv7zmNQ+H+h6LZvcXCeTEn3mrHs9A8O+I9chW3uY5ooU+VUk/irrfEmhyeItP+zrcfZm3/6zy1b/ANCqt4X8Dw+HLx7jf50rps3eXtqaeFoQd1BfcVLGYiSs5v7x8fgezi+7/wCzVMPCdvH/AMtJK1tlNpxw9OPRDljKz3kzO/4ReH+L56P7HtYfl8mOr8lNqvZQ7Gft6nRmTrGnyS6ZNFZ+XDJInytXmkfwv1iw1yzl+2XMy+d++/efLtr12eqc9WlbYz5m9zHvI1ijrx/46ad4i1m4SLSY7lIUT70Uir5n/fVezXkeI6wdUj/vfdp63uCPDfA2h61YWVy2rSSbt/7tZZN3y/8AAazfFlv9+vVPEka/PXnvim3pyd3ccZWPkX4ySeLr/XLmWwS+ht0m2QxpH/rF/vVq/DuO+/4RO2bUvM+2P88m/wC9XsPijT+a4LUI/KuHpHVR+PmGRR1T0/xI2l+MLOwaGT7PqSSJ5n/PORF3r/30u+rG+myf6LcJKv8AA+6s60eaNjojLlkpG98QPD//AAlHgO5t/wCJE3r/ALw+b/2Wvn6OP+Fv4f4a+mdL23W+L+GZPl/Gvn74gaHJ4c8W3lv9xXferfWpoytoTmEL6oyP+WlO/wCWVQ5XzPuU6tjzQopvmr/cptAEsf8Aq9rf99UeZ5tRUnmfvEoAf5nm02o6koATzP3b0tRy96KAHP0pr/6qiigAw39yj/lrRTJJPOoAfTJP3cny/wDj9JTZJKAHZ/26KbHJR5lAD5JFpnmebTqbJQAR02im76AJDI0QqGXvRJJRHIvl0AFNfrTaKbVgCm+ZTqbIMybqpO4H6U6d4gW1t0t1f/e3UR6x9qkVY/kiR64yTXGl2Qq+zf8AxUy41ST7R5Vu+/8A2vu1+Oczsfvzw8U7s7m38SKbh1Xy3lf5P+udatveLLInz72SuAt55rWNP30br/d+tbel6pJ5kar8i/xVtSqSa1OfEYdJXR1skkcXztJvZP4asnUPNjT5P+A1z1vJH5f99v71WY7yP7R9zf8A7Vd12tjzbJ7m/wD62R/kp0dmsv3f4KzbPUI4f+B0+TWPK+7N/wCRK6FPS7OOpSk3oXL3R4/+WqR7a57Vfhvpus/622jdf7rx1vW8l1dRozeXMrf3JKms9v2x1ZJN38Kv81aRlpcx1izw34ifsX+GfFsbrcabbfP/ANM6+b/ix/wST0PWY5riwtvJlf8AuR7a/QiSS3lj2q8e7/Y3f+zVWk8nzNrf7m2tJU6MtGdWHzbF0n7rb/E/I7xR/wAE+vHnwq3y+HNY1a22fdVJ2Zf++WrnpPGHxm+FUiLdPHqq/wASywfN/wB9LX7B3nhOz1Te1xD/ALCr5dcN40/Z/wBJv9nm2cb7/n2uit1rnrZapK6Z62H4p15K0UfmnoH7fl9oNx9n8TaDqVg38U1v/pEX9K9X8B/tWaD8QbPdYarbTN/zz+60f+8rV7H8WP2B9L8USfubaNG++zeX/q6+PP2hP+CdeseB7y51TQbmSzurP51ZP/sa8mrhqlN6rQ+hwuNwOJVouzPddU+IC3UfyzR1g3njT94/z186/Cr4uata3D6brKSQ3lm+yZX/AL1eqR6ouqR7t/36wPTp8tN2OkvPHHmx7aoR+LGkf79cxeah9g+VX+b+Fa6T4d+D4/Eey/1R/Js/+WMP8U/+0391a3oYWVeXJEnFZpTw0PaS+46HwnpesePLx4tGtpLlk+SSR5P3Uf8AvM3y19FfAf4P6X8JJE1S8mj1jXnTYtw/+qtFP3liX/2avN9D8YWfhzT0tbPy7W3h+7HF9ytW3+Kkf/Pz/wCRK+vyvJ6OHftZ6yPzbPuIsXjoulBcsGfQMnjBbqT5nr8sv+Czf7Ic3hzxw/xQ0az36Nrzr/bCxf8ALheHavmN/sy/+hf79fatv8W4/M/4+aNc8YaL430O50nVobK/0u/ha3uLW42tFJGfvKy17uIhGrT5H3v8z5TL51MLWVSHa1u5+GlmZIZNrJXZ+E/MlkjXZ8v+xX1X+0J/wS7uNL1S51T4d3Meq6W7s/8AZdxOq3UH8W1Gb5ZP/Qq574P/ALEfjaXxBDa3Xh65sPM/5eLvasUf+0zbjXzNTCT5uVI/RaebYaUOe5x/hfQ/7PSFvJ33H8Mf8dfaX7Ff/BO/xB8Wr+21zxvDc6D4XT97HavH5V1qS/e+Vf4Y/wDpo1ewfs7/ALN/gP4GW9tdRWFtquvIitJqF3Hubd/sK33a91g+Kiy/Nvr1sJlyh8R8tmOezqpwoo9U8N2+n+DdDs9L0u2trCwsEWKG3ij2rGorVj1eP+/Xj9v8VIZZP9dH/wB/FrVt/iBHLGnz16iqJHydTDyfvSPV7fVI/wC9VyPVFryu38eR/wDPar9v8QI/79P2yJ9ieox6guPv1NHcLXmkfjyP/ntV+38cL/fq4yi9WZOk07HosdxHj/lnuqaO483+OuGt/HEP8T1T8UfHDTfBFn9ovPtLq/3Vt4Gl/wDQa0ja+pzVKMtkenRn/bp8e2vnLxJ+3x4fsLN10uG+ub9Pux3FpIq/99LWD/w2p4yv7fzbXRNNRf8AbjZv/ZqzliaSdrhDLa8lfRep9XJto+zx/wDPOKvlTT/20PFX/Lxptsjf7Fo23/0KtO3/AGyNe/isLZ/+2Df/ABVT9apdyZZfWi7H05T/AJvavmWD9sTXpf8AmG2//A42X/2anyftka9FcfZ/sGmpL9/y3j+bb/38q44iN7CWX1n0PpC4vI7WN2lkjRU+dmeTalUNH8aaTr1w8VnqVjcyp/DFIrN/47Xy748/aQ174jeH7nSby2js7W5/5aeXtb/0KvLrO8bwRqH2iz1WOzuP+Bbv6VhPFJPRHRTy28LzlqfoLHJTH218baf+1R46sLNfJ1uxuVT7vmx7q1dL/bY8cWsm66s/D94v93y5Iv8A0Fq1+sQMpYCrf3WreZ9afZ4/+ecVFfPHhP8Abwjvvl1bw9cwypt3fZJ1l6/xV6XZ/tMeC5tLS6l1uOz3/wDLO4jZW/75q/aR6nNLD1IvVHeUV57J+1h8P4pPm8T2P/fuT/4mqsn7Xnw7iPzeKrH/AL4k/wDjdHNHow+rzW0X9x6T9ob0pK8yk/bE+G//AENVj/34m/8AjdVpP21PhnDJt/4SeN2/2LS4b/2nRzQ6sX1arf4H9x6xvpteR3H7cnw5i+7qtzN/spYTf+zLWbeft+eB4vM8qHW7n/t0Vf8A0OQUOtTSvc0WDr/yP7j2m8uFsLd5W+6nzt95/wD0GvPdZ8QeJtZ8QTLapdW2m71SHbt3SKf4mrgNU/4KGeH5dLuZbPRNb3Qp8skvkqu4/wAP3jXMSf8ABSSHS7NFtfCWpXmz/lpLfr+8b+JvlU/3qqVWnFXkyIYPEVHaEGfUWmW7WFmkUs0k0q/eZ6l318b6x/wVA16L/jz8ARv/AHfNv2/+Niue1T/gqB448v8A0fwr4XsP9q7nmb/0GRax+uUVpc645TimtYn3d83tTP8AWV+eF5/wUw8fapv3a34SsF/u2WmtcN/49urNk/bc+Jnij/j18Q+Lbn/ry021iX/gO6MtWTx9JK6Nv7Grt6tL5n6P5/eVJHIsX3q/NC4+Onxa1TZK3irxtptu7/KzXdnu/wC+Nu9f++KhvP2nPihoNwlvYeJPi9qUqfeaKwt2WP8A4FJbBWrKWZ010kV/YlX+ZH6dxyLLVnz19a/NPw/+3h8dPDkm7+zfFuqr/DHquhWcv/j0KxtXeaH/AMFR/iFaxbtb+EtzIqfJJJaWlxb/APfP+sqlmdFq5jPJcTf3dT7zjkor5I8J/wDBXjwHLcR2/iDR/EHh64/i3RrKv/j21/8AxyvY/Bf7bHwt+IMaf2b420lJX+7HcSfZ2/8AH1renjKE1pI5amBxMN4M9W30b6ztH8QWPiK3RrC8trxf71vIsq/+O1c89fWuiLTV0czi07Ml30b6i+0fWj7R9aYh/m+9Zt5440ew1B7WXUrGG6T70byLuj/3qs6j50unzfZ3jS4dG8tn+7G23+LpXl3/AAqO68R6P9osNS028WZJEaaWNt08nmfeVyu9VX5/71VGm1HmZHOublPV9P1CHVLdJbeaOaJ/usn3al31R0fT10bS4bVfuwoqbn+9Jj+9tqbzKkssb6N9V/MojkWgCxvqTzKreYv+RXl3iTxB4qlvJrr7Tc2ETzMi2qRrKsf935l+b5v92gD1r5v4adWL4LjvofD9t/aXmfb3TfIryK3lt/vD71bHmUAL83tTKKKAI5P3tVpI6s1Xud38NAGXedKyNQtlrbuI2rL1COgDkdcs1rgPEdmvz16RrEf7t64nxJb/ALugDyjxJZ/vK898SWflSV6p4ot/v1514sjag6KMnY5uO386nyW/7umRyN5lTR/vY/moNnJvc3vC15+7hZvvQvs/L7tcT+0p4bb/AEbVIk/3q6TQ7j/THi/57J/48K0vHGj/APCUeCpovvts+WsOZqpynV/Eo2Pm+OSn+ZTPs7Wtw0TfeT5Gpa3PHCmv0p1NfpQAb6d/rKjojkoAPK9qfHI0Ubr/AH6ZRL3oAKKbvo30AOkkpu+k8zzaSgBZJP3dJUdP+b2oAWm+ZR5lNPV6ACiiigB3mU2o5JP3lT/N7UAQS96KKdsoAbL3qOnP1ptABTY/3tTbFqH5v4abdwDzKPMokptCdgPv7+z5vM+ZNip93ZTPsbR2+5fLT/tpWr9o/wBHfzaoXFva39xtb5VT+GvyadOJ+8U60nqzNj0PzdQ+0TTec392tu3jvP8AllNGn+/VC3t7WLcsU29qs3Fv+7/12xv9ilGm0zapV5tCazvJLC8drq537Pu7KvyeIJJbf/R/7/zfjXK3CR2qM7TSvL/F/FRpeqXEv3U+Wtk7BKnGT0Ots9QmiuPmm/74+7V+3kbzN108aLXBxapfRXm1fk2f3v8AlpW3Hc3V/bx+a8aVvTqSOerhVodVp/iiG6uHX93tT7rfdqzHrHlXCeU+9t/3q5WORfL/AHX3k+RWSn2d+ulxvcM8nm7/AJd9X7RnK8LFu9jubOSOVJvMh2N9/cklMt5LeWPdv2RJ/D/+1XH2/iCS63r/AA/fVv8Aaqa88QL9nS3X5Gf73+9WsZLocksM5PQ7C81iO1t/9dJt/wA/3afHrkN3cblePcnyeW/y1yXymRFby3X+KptPvG3yMz/7v8VdEK1tzCphVax2F5bx3VmjXEOxn2/N96uP+KHgez1SzuYpYY/nRtrPWrpeqSXUcM7P/o8Pz/NH/rG/hWuV+Iniz7Vb7W8x2mfZ+dZ4ipB025Cw2GkqqsfnF+258H7f4afFjTdStUjSLVbZt3+8jL/8VXF6NrH2W3+Z9n92vW/+CjHiD+1PHGg2Fun2n7HDI/8Asx5ZfvN/wGvAY/O/i+f+7XBTwcqlpH1v17kp8s9ZHSR6pHLcbpPnVH+Vf+elaUnjyb+/XGeXNL/z0q5Fp1xJ/DXtUacaMbQPGxU5Vpc0jVuPHl8N+2b/AMiViah441aWT5bmT/v5V+Pw3NdUR+A5PM+ZZK6o1tDilTWxx+seMNc/hv7lP+2jVjx/EzXorjb9vvv+/jV6pb/DhZfvQyPWrZ/DO3lj+a2j2/7VdMKjuctSnB6xOY8D/EzxBFsb7fc/8Dr2Pwf8VL6XYss3zbK4yPwZoel/62/022/663ca/wDs1XNL8SeC9L/13i3w3D/e36lD/wDFV0RqdzjlR1sewaf8QJJju8ysf4qePPFV/pb6b4ZtvOurn5ZJnkjXyI/73+sDf+O1xknxs8A2P2a3i8Z+G0+0pv8AtD3atFAo/i+983+7XVeE/jJ8JdBs9q+PPD80r/PJM93uaRv++a39rFK8mcPLd2UWM+E/gO60b/StZeS4l/hhl2s8bf7XzMtewWfjyaL5fuKn3a4a0+PHwpl/5nbSX/3PMb/2Wr9v8dPhX/D4tsX/ANyCZv8A2nXM60Er3R0Sw9RqzizvLf4iXEX8dXI/iRN/frg4/jz8Mf4fEm//AHLCb/43Vm3+Nnw5u7jbFqt9M38Kpps3/wATU/WKd7Jon6m0tYM7bUPixeaNZo1vbyXkrvsVU+Ty/wDaauJ0u48Ta94s+0aleX32e5dnkVNyrAo+6q7mO6qz/GTwPf6o/wBovNW+z2z/ALuNLCRvMx/E1bFv8dfAvmf67W3/AO4bJW0cRTSs5I5XhatrqLseo+G/Gf8AY1mlvb/IqJWlqniCHxHpb2epJJNazfej+Zf/AEGvK7P4+eA4v+XzVk/37Bv/AIqr8X7RngHCf8TDUk/7dG/+KrspVYNanBUwtSD5kjevPg/4Vv43aK1uobh/ut9rm2/8CXdXKyfBfxBa3H+h+JLGGL/nn9nkX/x7dW3b/tCeAd//ACFrnZ/ee3/+yqzH8fPh/L/zGPm/241/+KrSVOk+hzc1VbnPf8Kr8TWHzf2lbXLf9fDf/E1Zs/B/iq1j3eTI/wDuX/8A8Viuqs/jZ4Huv9VrG/8A7Zq3/s1X7f4keFZf9Vqsn/fv/wCJpKlSBVKiOA1iPxRDH5Uum6lt/upJ9o/9BaseSTWPtHzeHtbuWT7sj2Dbq9js/HnhuX/mK/8AkCT/AOJq1/wl/h3/AKCn/kCT/wCN0owpN/Eg9tV7M8V1C88Qaxb7W0fxB8/3lew3/wDoS1Db+H9euv8AmCas7f3ntGWvdbfxH4bl/wCYxH/wOCRf/Zasx+IPDP8A0MNin+/uX/2WtfZ0e6D20+zPF9P8B+JJfu6Jcwr/AHX2r/6E1dBpfwv8RXNwq3CR29v99lSePd/47Xp0eseGZf8AmZNN/wCBybasx6h4Z/6GTSf+/wCtNUaXdHPKtUvqmcHJ8L9Qis3W3e1Rtn7tfPrEuPgnrF0/m3E0c0r/AMXnrXrUdx4Zl/5mTSf+Azq1P+2eF4j/AMjDpv8A38qZUaVt0HtKq1SZ5F/wofUJY/8Aj2jdv+vtaytQ+AeueZ8umxv/ALX2uOvdbfUfCcUe7/hIbH/x6rMeueEYvmbXrH/v2zf+y1i8PTezNqeOrp6R+8+abz4B61/HpV8/+5+9/wDQVNZtx8L77R3/AOQbqyN/Cv2SZf8Ax5Yq+qLj4geBdLuIYrjxPpsMtz/qV+bdJ/wHbVaT48fDG1k2/wDCW2LsnybYo5mb/wAdjNZ/VoN6TaOqGZYnm0pfgfM1v4Y+y/NLpUkzf3Zr+Zf/AEKOn/NYSJ9n0HRIf7zPPIzf+PKK+h9Q/a4+Fujf63W751T73lWE3/syisG8/wCCgPwbsPvXmtzf7Kaav/s0lZvAxXwyNv7Tq3t7Nni2qeLNW+eK1TSYbeP7uzdWJqGoa1f/AHnjm3/3J1X/ANCzXvH/AA8D+DMnzf2V4ouf9r+xbf8A+O1Dcf8ABRz4R2o/deD/ABRMv/YJtV/9ClrGvhVOXM6hph8bKK5Y0ZHzxJ8O9Y1mT/kH2Tr/ANNdWkX/ANAxWx4b+BdjFKjalpvhLd/ef7RdeX/33JXtkf8AwUw8B+X/AKL8MfEk3/XWOxi/9qGr+n/8FFNNv/8Ajw+GPkt/D9r1KFf/AB2OJq5fqsP+fh2RrV5u6oN+baOe8H+A/B+lxxrb6VYzXCfdW0tI1/8AHVzXQyfDvxlqEjtpOg2MNu/+rjm0m8laP/ebcv8A6DRrH/BQjxJF/wAeGg+G9Ki/25JJf/iF/wDHa808ef8ABQ/4kXVw8Vrr1tZ7/wDn00232x/99q1ZyxGHox1n90Un9+ppRy3F13dUl/29K532ofAj4lSeTN/wjem3Gx/3i28Eitt/i2rJ/wDFVz/ifwp400y4f7VpfiixZPkVv7CZV2/7LJFs/wDHq4DR/wBvD4qWqbV8bXz/AO/aWrN/6KrSt/2/PixF93xbJ/4LbX/41Xh1sRh6msKk0exh8vxtNW9lTa821+SZZvNQ8ZWEm2LWPJVP4b3TY1b/AL62j/0Gn/8AC0fG2lxpbreaLf8A8fk3sEaru/2WTZWbcft0fFy/3+b4wuUV/wCH7Ja//GqwdY/aX8ca/wDJeaxY36/3bvRrGX/0KKvPlVlTd4YifzimehHCcy/e0IJ/3ZSv+KOz/wCFyXktu9v4o8DR3MX960k81f8AviRdtc7rng/4J+N98txZyeHrp/vSJHJa+Wx/3PkrjX+JeuWt359rcx2DfxLaQeVbyf8AbL/VL/wFVqb/AIXQ1/8ALrOj6TeN/wA9oo2t5f8Ax2qjmmJg/fs0aSyLDSXMrr5o25P2b7fS7hLrwN8UY7aVPnVbi7X/ANDSRWret/iB+0l8KrdZodYvvEFiv3Wt9SW68xf92Zf/AEGuJs9Q8H6z/rdNvrb/AK5SVfs9D0G1+bS/E+t6Pcf3U3Kv/jjVtHOHFXSaOOpkelr8y8+h2Gh/8FXPH3hy8+z69ZxpLD/rFu9NZW/77TbXrXgT/gq5DrwT7V4e0i4/vNa6l5Df98uhr5v1jwsviiPbf+M5LmL/AJ6SyM3/AI6+ax7P4T6XFeeSt/pOq/3fKnj+0f3fuPj/ANCrann1aOkJSZyy4bwnLerFep9va5/wUE8O6z4UuVbTfEGlNN5UUlw0cdwqRu22Rl8uQt5nl7/4a6fwv+3p8HZbO2s4vGFjpqQosMcd7BNarGo/h+ePb/49XxNb+HNDsI4dLa8jtorZ2dvn8rzJD8rfN92ulj/Z70nxHZ/urnfv+fc+2X/x7mvVxXFFahKOFlFOy95929Uv+3dj53B8H4bFp42LcVP4V2jHRP8A7ed33SaTPtX/AIbA+FMsfy/EjwTt/wBvWoV/9Can2/7WHwzuvli+IvgV2/7Dtr/8cr4M1z9hu11X/mKeSr/xfK1cT4s/4J96p5DtpusabM331V42X/x5c1tS4mpS3jYqpwbJfBLQ/T7S/jp4L1mTba+M/Bty392LWrVn/wDHZK3rPxJY38afZ7+xud//ADynVv8A0GvxA8Y/BvxV8NLzbf6bYzbP+eU6v5n8mqhpfxM0/QbhLe/sNS0mX+Fl/er/AOPY/wDQa9FZxGUU6cbnmvh1xlyVJ8p+6mqazDoOiXV5cf6q2haZvwWqfw/0+40vw+kt9/yEr92urr/YZ/8Aln/uovy1+R3gf4oR2vhua/i8Q6klvcv9it2+3zRLu+++1dw+6uz/AL+V6L4Y/aT8daCiTWvj7xQ6p/C980q8f77MtXiM+pUKCUoSTm2/knZffY48LwrVxeKqTpVFy0/dXnJ6yfpsvVPsfqV5nH+z/ep2+vzv8N/8FC/iJo2z7RrFlqq/887uxjVv++o1Q1618O/+Cll1fyQxa94Yj2v8jTWV3t/8cf5f/Hq5qXE2Cas24+v/AAx6VTgvMoR5orm9P+HPrfzG/wAimfNXE/Dv9oTwz8Rbj7Pa3ktnfum9bO9j+z3H/Aezf8Bau9+b2r26NenVjzU2mvI+ZrYerRly1YtPzIKhljqaoZK1MShcR1m6hHWrc1m3lAHPaxHXGeJLf91Xc6p/q5K4/wAQR8UAeaeKLf79edeJLPzd9eo+KY/v1574lSg2p6HAXFv5M+2nxdqm1i3/AHny1Wt/60Gy1Vx8cjWtwkv9yun0uRZY3i/hf7tcw/8Aqq1dDvP3af3v4qxqxe500PhseJ/FjQ5NB8YTf3Zn3rWD5i16v+0J4f8AtVnDfqnzJ96vIo/71aU5LlsefWp8s2S76dUdFUZBRF2oqOgCTzfK+ai4uGl+9Td9NoAb81OoooAbJS/N7U6SOmeUKAI99Op/ze1Hze1AEWf3dOoooAjop8kdMoAKP+WVFFABsWiSOm76N9ACSR/3qXZTab5lADqXzPKpkklL83tQAfN7Uyn/ADe1MeP5N1VID74uLiT5/K/j/v0+SNvs/wAz/M/9yobyTzf+Afdo8vzY/l+Ra/JmuY/eOeysh9nZw2H8e9v4qmj+z+W8v3d/8VU7iRvL+Wbb/tPRb3i3Vx5cr/L/ALFUkkrInVsf5flW7sskk2//AKZ0RSeVsXb838VMjvY4pNqv/u1DqFxN9sRvvrWiVhptj5NYWwk2yw79/wB2objUPtVvuTzEV/urRqEnmyb1h3/3qoXlxJFbp5X8FOWh0w5dmatnLJa26Mr/AO9vpkcjXQ/evHt31Tj8yXT3VvvUWdpHYR/M+/fTSuDpps6G31C3ht/KX71Pj1CP+3N39xP/AB6seS4t7D5lfez/AMT1myahJL93+D56uVRJXOeGHcjpP+Eo/wBI2bN+z7zVf/4SRotPfyod7f8AouuV0O8aKzeWVPv/AD1vaXIv2dF/1nnfw1Mq1jSWHUUdDeeKGi0eGJn+4myvPfGnixf4fvfdrrdUj82N9tePfGTxBZ+DfC+pazePHDb2aSXDSPJtXaF21y1q7aUe5tgaNNtt9D87/wBsT44X2vftIa9FZzXP2fTXWyXZI23ci/P/AOPV51H8QPEBj+Wa5j/7aV3kng/wf4o1u51KfWJZry8ma4mb5V/eOzM33V/2q1Y/A3g/y1X7fG/+092q/wDoS16P1mFOPLqcbwlWpK6PMbfx5r3mfNcyP/20Za1bPxxqk33prn/e8/bXoVv4L8J/dW8tv/AtdtX7Pwf4Z/v6b/wO7Vv/AGWspZpBdzeGUVWr3/D/AIJ5dJ8RLgybWm1J/wDcnoj8YXV1919W/wC/7f8AxVex6f4T0X/l3fTU/vbJ/wD4la0o/Cdr5m2L+zX/AO28jf8AstYyzmMehvDh+rL7SPAby8mu/vJrb/8AbSSsHVPD9vdb2l03Upv++m/nX1XH4Lh/i/slP+2jVm+JPh3bxWczf6D/AORP/ZVrhnnsVp+p00eG5yev5f8ABPiLxvJpNhcfZ7fRLmaV/wDpn/8AFYpPCfwXj1S3S/uPDdzc+d/x72/l7mk/2m+b5Vr368+Adnf6o95cQ21zKn+phWwvJV/4Ftj+7T4/2Y9U1TUHvGtr65uJvnkZLC8X/wBCjqv7apQpe15nJ9k9jL/VqvWqOglyxWrb0v6a/f8AI8ot/gRdS3n2i88Jasn/AE0SwmZdv/AVNbGh/CPQ/M+az2N/ErwTbv8A0GvafDf7PfjCwkRbOHxQi/fZUnuIl/8AH1210kH7P/jq6uN3/CL3N03/AD0/tK3Vv/HlFedPMKtXW7v8v8z1KOSxo2U+XQ8r8N/Dvw/Ds2w7P+3ST/4kV3+h/DvRxsbZcOv/AFzkX/2Wu58P/s3+NLX5pfCsn/gyt2b/AL53V2Gh/AvxdF97w3fIv/XeH95/3y1YU8RXlNQg7v1Oqth8JSg51ZJW/rc4DR/A+myyJFHbXzyzfJGqxyf/AFq0tQ0PRdGt3s7e8uYZX/11wnmf98q392vb9H+HevaNb/Z4vDdy+/8A1k3y/vP9nb/drYi0PVLCP974bkT/ALbqtehLHfV/cspS6u+ny0PDeDeLnzydodE9/XyXbq+yPmCTR7G1+WLWJP8AZ3z0/wCxtF93Uo5v7yyvJ/6ErCve/FGhtdRv5ugxoz/35Fb/ANlrzTxJ4PtfM+awsUatsHnPPLlsPFZQuTmbZytn4khikT7RYW0y/wDTK+uIm/8AHpGr0L4Z/wDCM+MdZhsLqwvrZpk/1n2uSVY/97pXnWqaHb2sm2JI0lm+RfvV6L8P/AkelW+17mTzf+Wmz5eq/KtfUrFRjT51dfI+WnlcqlVxjbQ9IuPhv4B0GP8A0ya2SX/nn58krf8AoVVpJPANrG62uiSX/wA/3vL2r/49V/wp4D0mKNIfJ/1n+skf73+7XZ6X4L0vy9zJGmz5FWsv7aitNTN8Puzk7Hm8eseH4vls/AttM38P2jbt/wDQafHqmoeW/wBn8N6JZ/3dlp89ezaf4PsbX5VSP5ErYk8JwxwblSP53+Zq2jmjfQ5ZZRBK7PB7PUPEksny2emp/wBui0SR+KrqPdvjjb+6lpH/APE17r/wi8MVx83/AH1UsfhKEXG3+J6n+0pdEbRyqCd3c8Fk0fxVdR7lvpE+fYypGq+XUMnhfxd5nyalff7X7yvoGPwP9lO7Z99/4afb+E/Nk+59xN/5f71T/aE+iK/s2l/TPnj/AIQ/xVLJ82sakjf3XkZahuPBfijzHX+1b75PvRvJJ+7/APHq+h7jwPJf6f8A6nfJ82393TJPhnqmqW7t/Zt867NjNFAzeXlq0jj6rV1H8CZZfhEuacl9582SeD/EkTv/AKZJMv8AeeeT/wCKqteaXqEUm26sLl/9pJPNX/x1t1fUun/sx+ItUuE3W1tYIyf6yXczR/8AfFdVo/7Jei2saNq3maq3/LRZZPKik/4Auf8Ax5q9SjUxE3rBI8vEV8vpO0JNs+M9L8D6p4okSLRra5ubh/k22+793/vM3yrXpHhf9ifXL+3+0azrFzbfx/ZbKdt3+6zt/wCyq1fWlv4f0vQY4Yrezjhih+SNYo9qx/7qr8q1DeaxHF93zH/2Ujro99LU8eWL5paI+S/Fn7M/ij57e1+zWFq/yqtvGzPt/wBp3bc3/fX/AAGuMuP2Q9c+dWTVpv7vlbV/9mNfZlxqjeZ/x7f+Q6rXd5NKflh2f9s9tZxnU25jX6yuW7gn9/8AmfJFn+ynr0Uf/IE1J0/6eL9dv/oVMn/Zn8QRfd8PWKf7XmLur6ouPtV1J/rvlp8enwy/evI938S+ZRJKStc1jjqsdkj5Cvf2d/FG/wD5Bsaf9tFp+n/sz6xv/fpInl/3I/8A7Gvr24jsbD5pZti/3n+SobfWNFv5PKiv45m/2JN3/oNY/U4veTNlnFZbJHzZp/wTh0aNPNs5Xb+9L8zf98tWzB4TtbWPyvJ2Kn9zbXu+of2Laxu0vl/8DkX/AOKrj9U8WeF5dQ+yqv73+95Hy/8AfVcdbCqCve53UM0nUdpxPKNY0ex8vaqf8B8use48B2csn71I/wDgdewSfD/Sdek3W95bbf8Abnj/APrVWk+G6xRzf8TKxWJP+mG7/wBmrwsRg683eNj3MPmWGjHVnkX/AAr6x/hf/gPl7ak/4VvzuV5P+/derW/wbvr+PzbPUrZ1dP4IG/8AiqyvEn7P/iC6kdV1WNP+2bf/ABVcn1HEx1aOxZphW7c6PNLzwGtsjtLc2ybP+BN/3ytZUejyfwwyOv8Aef5Vrv7z9n/xRFG629/9z+GKNV/nmsS8+GfiTS4/KuP7Sm/2kjVm/wDQTWdSlVWrizqhWw0nrNfeYj2cdr/rfk/2UjqneQW8v3vLT/fk3NV+48ByRH/SJtWhZ/vb9v8A7NHTI/B9v5nm/wBpakkifdZ4428v/wAdFczko/GzoUYyXu2Me40dvL+VJHX+8+1VqtHo9xdR/f2f7X3V/wDHq6e28JySyP8A8Tjzm/vXECt5f/jwqG8+H95LJu/tuP8A4HaL/wDFU1WjeyZEqa6o8Z/aA8SX3w+0izS3m2XF+7J9o8z/AFahfm21zfwf1yz0v7ZqX2yR7+2TfZ28XzSyXD7l8xv+uX+997ZXqHxY/Z3m+I1vDFcalI7W03mx7LT1Xbt/1lchB+yvceHLj/Rb+5T/AH4Nv/oLGvpMvzDDUaSaa5u9j5bNcrxGKqOnr7Nq39evXuizoXh/UpPmWw1Z1/24/wD4pq63w/oevWGx7XStWh/65bV/9mqn4f8ACeqaDJta8ttn/XSRf/ZTXovg+41CXZEt5pv/AAOST/41Xk4qbqSbhq27nu4eioU1Ha2i8kZQ13xZYR7WTUtv93z2qG4+JniCL5ZZr6FX/wCun/sq16jb/DPXNejTbN4fkX/r7Zf/AEKOtKz/AGW9cv8A5mfRf/Avd/7LWUaNXfluRKvQS9+aXqfN/ijR7zxl81xqV8jP/wBdP/Zlrm4/2b7q/uEZdS3t/Dvgbdur7DT9kPWpf4NNm/vf6f8A/Y1f0/8AZT8SaXOktvYaTuhffGz3e5o2/wC+a78PLGU5pxg0vQ4cRPAVKbXOnLp0/M+U7/4H6hpeqW1ra3Mf2PTbb7OsKfLFJIW3Sybf9pv/AEWlaHhfwXDF4v02z1KaTR7e8m+ztfPH+6jkP3Nzfwq397bX05efsp+JvM+Wz0SP/ae/b/43WD4o/Y28VXUds0tt4fvIra5guGt0u2WW4VJFbbuaP/ZrTFSxmLxDqzptRbVkui2S+5L56mOW/wBnYDBRowrJzS1b6u927evn1Kdv+yfrF/rkMVvpsdsqf6yR59yz4X7393czf3a9O8F/sfyWEkP2y/toW/ij+83+7tWvWvD+j32qW/2jxBNbaJBs/wCPHTZGdpP726dlVl/7ZqtVvHnxo8N/C/Q3t9Nto3ZP+XeHavT+9/8AZV0VslwNNe0rt7Xdzjp59meKmqGF1bdtP1fT7iz8P/gZb+HNH+ztN9vlR1lt2lj2+Q3+yv3q9q8H3k0un+VLNHNLD/En93/gTV8d3Hx88QfEK4eKzmksbVvuxxfL5n+zuWu5/Z8+KFx8OvElyurXNzeabefIzPuaVG3blb/2U1tlOeYWFaNKjG0O/T7jDPOFcbKhKtWmnNdOv3/8A+n6hX+Oiz1C31WzS4t5o5reZN6yJJuWRaJK+7Svqtj8yneMuWW5TuazbytKS4rNuLihrsTzehj6hH+7euY12P8Ad10+o/41g6zS1Gtex514ot6868UWbDfXq/iS3/dvXnXii3+/U8xr1tqeXaxbyfPWRHL5UldN4gjXzHrmLyT95RzHQouxZ8z93VnQ7jyrh1/v1mxyNRHcLFcI1Eoto2pySR0PjDT117wvNF9/5K+dbyzbS9Qmib7yPX0hZyebb7f79eJ/GDQ/7G8QPKv8dY05W0FjI6cxzdFMt5KSug84kl71HUlR0AFFNkpfm9qAHeYv+RRH/rKZ5lNoAsSSebVbzG/yKWmv0oAk/wCWdNoooAdHUef3dSSVDF2oAkooooAj+aKjzPMpz9KbQAVF83tS0nze1ACea1NoooAjkk/eUeb70U3ZQA6XvTPMby6Jf9XUVAH3feaovl1Wt9YbzK8u8N/tAeHfFt49ra6xbPdJ/rI/MXdXTx+ILW6j3RTRur/xJJX5XzN7n9C/VYLRnYf2pHdfL/FTI9sUn+1XOW+qL8jLN/wKr0eoLn/XfNVqJlUpuPwm3bxxy/e+Rv4af5k0sbq0n/Aqy7fWF8z5nq9/akfmfLVxOScmmElvNF92bfTI428v79PkvF/hojt1/v0pJsIVLbkMfmSRyLK9FxeLFsWi48uL7slULi4XzPmT5f71I6KdVNak1xeeb/8AE1m3l55Ufy/x/JS3Fx+9/wBypftEMlnt/jrGV7aHXHQs2eoeVsVvu1sf8JBDHIjb9n92uVuNsUafPWbeagtrvuJX2RJ8/wA/3dtYuEup1KMJnpF54gWWzfa/y/xNXl3jTWNJ8W6o9hqU2m/YIU/eW93JHtfP95X/AIa+df2jf+ClnhnwbHeaH4S1Wx1XXk/dfak3S2tg3+0y/wCsb/dr4b1j4Z2fxB8WXOvapr0eqalqU3m3FxLd7mkz/wBs60wrjSqqtV2R5tejOpB0aL1Z+sVn8O/gvdD/AE+2+F3+1v8AsK/+g4q/H8J/2c5f+Pj/AIVcn+5q0MX/AKDKK/NDwP8As72N/B/o80kMv8OyeP8A9mWu20f9nu4ik2Lc6t/upPC//oNelU4jwt9YJHDT4VxTjb20vvP0P0/4L/s2y/8ALz4A/wDClZf/AEGetSz+Af7OMse1X8E/+FD/APb6/PSz+AepRfMtz4gj/wBz5v5LVz/hT+rRfL9v1v8A4HAzf+y1l/rHg+kYlf6rYxf8vp/efodb/st/s73XzLD4Sf8A3PErf/H6uf8ADG/7PtzHuaHw/u/2PEsi/wDoM9fnRH8I9S8z5ry+f/fgk/8AiaP+FT30X3rjf/2wal/rJgnvTj/XyJ/1Vxv/AD/mvmfo1J+xH8Bbr7vlw/8AXLxZcL/7XrB8UfsN/AX7H+98Q3Om/wC1/wAJmy/+hyGvz9uPh/cWv3YbZ/8Af3J/7LXmnxd8NyeX/wAeem7f4tj/ADf+gVnLiDAy3oQOqnw1jlosVM/QvU/2M/2d9Lk3L8YL6w/3/G9j/wCzqzVi6h8E/wBnXS/l/wCGh5YW/u/8JRpdx/7SNfmTHZ+Vv/4kkc2z72yNv/ZY6v2/iOSw+VfDGpP/ALNvAzf+yiuKpnOCk/dwsH8j06XDuPS1x9Rf18j9EZPh/wDAG1/1X7S19u/2J7O4/wDQIKrfY/gzpf8Ax6/tJ6k+z/qBNdf+gRivgq08YTS7N3hXxQv91UsN3/s1bWn67eSybl8MeJH/AN+w2/8AoTVyyzbCN/7rBfedccpxiVvr9T8D7bj8cfDfS/8Aj1/aHvpv9zwRdN/6DItP/wCF0eE7SX5fjffTf3d/gG8/+SRXyXofiDUrrZ/xRniR/wDcgj/+OV1Wn6Xrl1H+68GeINz/AMT+Wv8A7UpLMaMdY0Yp903+jB5VJq0q7a84RfpvA+kJP2gPD8tvtX4tXzr/ALfgi6/+S6zbz40eF7r73xX1JP8Ac8ETf+zXdeJ2/h/WvL2S+GL5P9/b/wCytVPUNPuov9bYbP8AZroo1sNUf8OP3vQ48Rh61NXVV/OK1PVNX8aeCdUf/SPjB4kRf+mXgRv/AJLrBk0/4U39x/pHxj8ZO3/Ykbf/AG7rynULNhI/7mRNlR6P4em1m82xJ/vM/wAqx19Jg6dGGqhFM+XxksROfJGpJt/I9s0zwX8FJbhGl+K3jaRkf73/AAiH/wB1V6d8P/CXwdlP/JXfFHmfcWSXwvIv/oMjV4h4L+Ca3Ue6VPOZPn3NXq/hv4HrLGnyRw/3aqpm2EjpKJnDI8ZdzlVaZt/EQaL4Iv7NfDnja28VRXKM8jf2bNatb42/e3sd1ZVv8YLy1f8A13nMn9yNv/ZlFdho/wAA4xGn/wC1W9p/7Pcctz/qfl/651y/XcLN/B9x1clenHknO7XyOJs/j5fRSbms/wDgXzfvK2LP9pS8tf8Alw37/kb/AHa7y3/Z/j8vZ5O//aeOr9n+zX9qkRvJ2f7Pl1pGphpStGm/x/zM3iKq+KcfuX+RwFv+0xNFGnm2MnyfxVvaX+0Yt/sa4tr6FUfd8ka121n+zPHFIm6GPd/d8utKT9nPzfl8nZ/2zpyhStdQkT9aT0dRfcjBt/2kdDlk3S2187fxLLuX/gPy11Wh/tGaDFHut9Ksfk/ilkk7/wC9Wbcfs3rEn3I0/wBp6x9Y/Z/kij22/wC7h+/u/wCelaxxc4r3aenoc88Ph6ju6lj1HT/2iFupEWz0/SXb+FU3Vfk+MmsX1vuW3tof9ry68Kk+DdxYR74ppElT7uz5arWcmvfDmT7Rb69c/J87R3G2WKT/AGdtaU85s7VdDjxHDyavQkper1PfpPHmrX8f+u2f7XlrUP8AbrS/625k3V514H/aQ0PxHqCWeqeXoN+/yL5vzWs/+6/8P/Aq7/WJNPsLfdcXMcKfws8i/wCWr1qeIjOPNF3Pm8Rg5UZcs0FxqFvL9+/uX/2ahvPs91HtXzP97y6898WftCeDfC9w6trFtNcf3UkridY/bY0Owk/0X99/vyLU/WknZ3OiOWzavD8T2zy5ov8AVW3/AAJ6zTod19odl+RpP+BV4Jeft0XUsn+i6Vbv/wBt6oXH7ZniK6/1VhYr/wCPUpVaL3udEcrxW65T6HvNHvLqN/NvJET/AGKyv+ELhilba8m5/vN5jL/6DXgl5+0x4qv/AL1zbW3+5U0fxk1zS9D+2X9/51xefJax/wCz/wA9v/iaVHE0XJ8yaS3YVspxUIpXTk9kezXvg/T7qT/SJt+z+/Ju/wDQqzdQs9D0v5Vk2f7leA6h8cNSij+ZJX3/AMXmVjyfHy4j+9DvavFx2dRUv3UND3sFwzPlSqzu+p7xeX+m+W+xbl2rm9YjaWT90l0+/wDh89lX/wAdrzGz/aAm/itvl/2K0rP45wy/73916+cxmcV92j6Chw7TjojoZND1QSbrfUr6zVP4fM3L/wCPVNJceKLCP5b+N/8AadFbzKp2/wASIb/7r7GrSj1xbqP5fn/vbK8uObVY7s9B5TTe8UU/+E08ZWsfyzW25P4fur/47UP/AAujxZYXP+kWFzJs+8ySebWrnzJNy/u6feafNdf6RbpsZPvL/wA9K645xO2kjH+xaF7yivuIfCf7TF1a3m6KGNpX+8qSfN/3y1dhZ/taSS/LeWexf4f3dcHqngi18UbJZbb95/e/irHuPCepaMm6zmjuYtnyw3HzL/31XRRzyafxHLiOHcNPRI918P8Axw0nxHJ+9e2mi/593jXdHW3Zx/D/AMUSbZ0ktm/iVJK+b/7c0mWO3XVrC502Wb/VzRfNF/30K6TT/D8d/saw1KO5X/rp81dkc+VrVIJ/I8ypw+nK9OpKPzPb4/hX4D1S9+zxfbk/6aP/AKr/AL63VNefsz6XLHvsNSsnX/pru/8Aiq8Z/wCEbvorf/R7+5tpf+eifLRZ3njLRo9sOofaV/2qqOOwNT+JTt6CWX4+l8FZfM9at/2b2v8Aetreabc7P4op/wD9dEn7KepfxW0c3/bSvMdP+LnjTw5J+6s45m/i2fL5lX739oTXr+SGW60q5SVP+mjf+y1pGGWNXdyW83S5VZo7m4/ZrvIo/wDkGx7f9yOs64/Z/k0v/mFR7v8Arh/8TVLTv2q9WtY/3sNyi/7ElWdP/bAuItU3XE2pf7ryblrb2OXNXhUa9TH22arSVNMZH8E77eyrpUe7/rn/APFU+3+A+tf8soZIf9lJ9v8A6Diuq0/9rTzo/N3ybv8Abjq/pf7UEcVw9xcX+xX/AOWcsCqsddVLB4OVuWt+Jy1MwzCP/Lk5rT/AfjLS49sSXzqn8P2uT/2Stm38J+Poo90qSW3/AF1jZv8A0Ni//jtdnp/7TFnLB5izWO3/AGKs2/7RlrHcea1zYpa/w/u9tegsHR6V39558syxUneWGX3anE3EfjTQY0l+zateM/8Az1jWJZG/2VVd3/jtaUmueNIrNIl0v/SH/uQbvL/3t1d/b/tAab5aMz222T/pptqzb/GBZbj919h+z/cb95W6wytaFdnLLHNPmq4WP3HlGqaB40v7zyrx75Ipvk3JH8u0r833awbP9m/UL+RvtX2r7Qjt9/8A5aKPlr6K/wCFgQ3Ue1U3/wC5ItMj1y4ubj7kflP/AHPvVzVuH6NaznUlI6qXFmJoJqjSjD0PGdL+E994I/d/YPOX+FvL2+ZRrkl9Yf6zQb52T+5H83/fS17eLib5FVP97zfu0SRyfPtSPd/1zqoZDh46Um18jCXFNapL2lWCZ4D4f+PGrfDm43WaalbLJ/rLe4g3RSf8BH8VXPEn7eniKwj/AND0fRLltnzLK80TfpXs2oaHHf2+66s7a5l/6ax7v/HqxNc+Geg3Vu/m6Vpr/wCz5f8A9lW6wONoq1Kr9+wSzjK60uavhtfLc+ePEH/BTzxpo0b+b4G0l1T+Jbu4b/0GM1wuqf8ABW/xd9o/5Fjw/D/s/vm/9CYV9F6p8B/Bd1/rdNsYW/2J9tcf4k/ZL+Huqb/Nufs3+z9oVv8A2Wl7TMIfFJM1lTySbtTpSj8mzxmP/gqZ421CNPK0HSX3/wByCT/47XPfEj/goh488W+HJrG3S20Gab7t5ZR7biP/AL7Zlrv/ABZ+w34Hl3tZ6xIiv/00j/8ArV514g/Yf0W1uHa316+f/c8unHMKy3MqmX4T/l3G3qrP7meM658ePH2qf8fXj/xk6/8AX+y/+g4ry74gfFjxVYO7N4h8UXn/AF11KSvpDUP2W7fRpP3U11c/9df/ALGuM8YfBeaKTZ5O9a1pYlt6nJWw8Yqyt9x8u6x+0J4g8t/+JlqXyf8APW7kpnhf9tDxN8Prz7RG/wBsuE/5+7u4df8AvjzNteu+LP2f7e6jfzbGP/erz3xB+yna3Um5ba5h/wC2ldntIuzRxxu3yySL9v8A8FQPGB2btH0R/wDcjk/+OVsaf/wUs8SX8m1tL0RP9+OT/wCOV57H+ynHF917n/d+9W3of7N8lrJ9yR9n8Py1nLEVL7mnsqSVrH2r+y/8cJvjJ4HS8uobaG6T5Gji3bf/AB6tv4u6OuqaW8q/fSvHP2R9Hm+H2qTWbJIlvN8/+zXveuR/2hbuv8L12Upyb1OLEU1NWWx4PHuik21N5lWfEmnto+qTLs/3apxyV3p3PA5WtGS0U3zKPMpgOpPm9qTzKPtNAB5dHl0eZS/N7UAMooooAKbvptFAElN303zPLp/mLQAymv1pJJFo8xf8igBd9M+b2pJJFojoAPMo8uiSmSSUALUcvejzfemSSUALvo31HJItEdABJJTaluI1qKgD5l0+SSwk3RTSI3+x96tu3+LGvaDGn2XW9Stl/upOy1f1zwm1hv3Q/N/D+7auM8SaHql1/wAe+m3L/wDbNq+Ji1LRo/bFT9nqpGlqn7bHjTwb/qvEN8/93fIr/wDoVcx4g/4K4fFTw5H/AKHc21y3/TW0/wDiWFZuofBPxNr0j7dNk/4HHVOT9j/xJdWb3FxZyJEn3m8v5Y66KVCkn8LMamIqON+dr52Nvwv/AMF4Pihpcn/Ey8K6Jfr/ANMpJLf/ABr0jwn/AMHAjfJFq3ga+h/vNaXat/6EoryDR/8Agm/4s8W/vYtHuba1f7snl7ZZ/wDd/u11Gj/8Eo/E0saKujyItavC4Zr4X+vyOdYjEP7aPojwv/wXU+Huqf8AH5Z63prP8jebB5v/AKDmvQvDf/BXj4W+I9mzxPbQt/dljkX/ANCr5U0//gjv4u1T7ulSVt6X/wAEN/GGp/8ALhs/76rmqYGn9m6OqnjUn77ifZPh/wDbs8D6981v4q8Pvv8A+n+P/wCKrbuP2uPCPl/N4k0T/wAD4V/9mr5F0f8A4N//ABZfyJ/yx3/ers/D/wDwbv6xLJ/pF/srn/s2XRP5mjzLCp2ckeqeMP8Agof8L/CX/H14w0R2/uw3ay/+gZryLxx/wWk8E+HJHXQ7DVvE9x9xVigaKL/vplr07wn/AMG7djFIjXl//wCQ69j+Hf8AwQr8E+F5EaVPOZP+mdVDKZJ3tcmrxBgqcdJHxDb/APBVj4nfEY7dG8GWOmq/+rklguLyX/2Vap+II/jB+0ZsXxQmrX+kzPs+x2//ABLreT/gDK3mf8C3V+q3hP8A4J9+Cfhzst7DTY7y/wBn7uP+GP8A2n/u16p4L/Zn0XwvcfbJbaO5vPu+Z5e1YF/uov8ADXoPh91EuaTj6dTx63GUI+7Rjfvc/JrwP/wTzvLW3Tb4S025X5d0N7Jb27bf9l4//iK9Os/+CfGk3Vui/wDCJ6b5v92XXdvl/wC7ujb/ANBr9Srfwnb2v8Ee2pv+Ebs/+eMb/wC/Gtcs+FYyfx6djnjxlWWkYn5Tah/wTf1T/mE22k6PL/Cya1/8TbLVzw3+wh8StG+aXxRob/7Pns3/AKFmv1Ki8L6b/FZ2z/78a0//AIRPSf4tKsX/AN+Ba56vBtKas5HdR8QsTBpWPzfs/wBl/wCI2lx/8f8A4bm/z/srVm3+DHxIsY23J4XmX/Ykk/8Aiq/RS48B+H7+PbLomkv/AL8C1m6r8F/BMtu8t14e0lIk+8yQbfL/AO+a8OtwDKUrUpr+vkelT8So71qb+Vv8z4Js/hX428v/AEjStJdX+95V3Iv81Nb2l/B/UPklvNK3v9zy0v12/wC980dfXdn+zH4N1S8+1f2DHYW6bvLjSSRZZM/xN83y1BefsV/D+6/5cNSh/wBzUrj/AOOUUuBcRhk5x5Zz6X2Xn/iM63iDh8TJRlzQh5bvy9D5pt/gpo4t/wDSNB1aZv4tmpQr/wC065Txn8FvDsV3+78B+c+z5ZLrXf8A2VEFfV9x+wv4Ll+7c+JIf9zVpP8A2auV1j/gnf4VupN0WveLYWf/AKf9/wD6EtcdTg7Moq1OMb+Vv8jvhxxlkn71Sp8k3+p8hah+zW19ebrfR/Ddgr/eVPm/9DVqLT9mNvM3eTYu3/XT/wCJjr6rk/4Jx6P/AMu/i3xIn+/Irf4VQ1j/AIJ32NhbvcN421JIk+95sf8A9lXBPgnM739km/8AEl+R6tPjrKor+O0vOGp4DZ/s1r9n+W2sXb+L95/9jU1v8A1sLdG+x+H1/wCvi7VfL/8AHa9s0f8A4J33F/ZvL/wklxC025P3sDeb5Z/7afLVO8/4JgLL/wAxu3m/345v/jlbYng/FUKSjGhzTe/vJ2+9mNDjrB1puU8Sow84b/hoeRHR5NB2f6T4Nh+T/nuzVg65441Cwk22+seF0X/plAzf+hNXtL/8Et7iX7uq6J/34m/+Kpn/AA671i1/49fEOmwt/sfaF/8AZq4P9Wc1ekaTX3f5nc+Ksmjq66l9/wDkfN+oSa1rNw/+nx3P91bfTWb/ANBq5p/7O/izxl81vpWtzf3We0aL/wBCxX0bb/8ABOPxtFJ+68cxw7P7kl1/8crodH/YL+IFhHtX4kXSL/20/wDZmr0sHw3mNKd503+H+Z5+M4qy2UbQqL5pngngv/gmX4g8R3nm65NHpNv/AHfP82WT/vn5Vr0LWP8AgmXb22l2cWk3kcLQv+8b/np/dr1rT/2N/iJahP8Ai6N8i/3fsit/6FXQ6f8Asr+OovvfE7Un/wC3SOvssPlNVxtKMvvX+Z8Vis/hGfPSqxv6P/I8B0P9lTxF4ckSBrb7RFC8iMsW79438LVc0Pw/faNeX8V5YSJLZv8AvFSNvu/7NfS2h/s7+JLXZ9o8ealc/wC/aR1t2/wLus/6R4hvnZ02bvIjrmqcI8zum0zWHG7S/e2l6L/gHhWieILPS7NGltpN03yKvl7mrej+Jui2H+tT5Yfvfu/4q9jt/gPa+XtbUr5/+2a0f8M96PL/AK2a5m/7aLXbR4erwWjXzOGpxRhanxxZ5XH8bPD9hHuby/N/65/6umSftMeG7CP5f/sq9Xj/AGc/DI+9bSP/AL8lXLP9n/wrbf8AMKjf/erqp5TjL6yj+JySz7L7W9lJnht5+1xoNh923uXb/rm1Y97+2ZZ/8u9hfP8A7kDV9M2/wj8N2n3dEsf+/a0XHg/S5bj7HZ6bYo3/AC0k8hf3a11RyetJ8vPbzOapxFg4++qF+2v/AAT5a1z9qy4/suNl0e+mluf9XGkDbtv95v7tc3eftKeJtQ+W18PXyL/16SM1fbdn4X0+1t0iis7ZFRNn+rXdUx0y1i+7DGn/AGzrpq5ZeKp82iOXDcQKF5ukrs+DLnx5421mT5dB8SPv/hitNtUJPAfxI16TdZ+DNS81/wCK4kr9BfLhi/gjSoZJFrkfDtK15O52/wCt+I+xFI/OvVP2N/jF48j2vptjZxP97zZ1rsPC/wCw/wDFiXwumg+INV0nVdDk+T7PcSNugX/Yda+3pLyOL7zxpWVqnjzR9Lj3XWpWUOz+/Otd1PLKEI2vZHmVs8xVaXM0r+h8N3H/AAR71LVNQmaTxPHDat/q18tmaNf96r9n/wAEc4YvveIY3Z/vM8bN/wCzV9UeIP2pPAPhz/j68T6ajf3UkVq5XUP2+Phza7/s+qyX7f8ATKBqr2eH2c2aU8dj5fBFf+A/5nj+j/8ABIPQYv8Aj68T323+7bwLF/Ouw8P/APBLf4e6X/x8XniC8/37/b/6DRrn/BSjw7ayOtno+pXjfwt8qr/6FXH6h/wU01rVNRS10bwxbJv+9JcT/wCrX+98uaz5sI5+zTuzWUs2cXJrlS66Jfmeov8AsKfC/wAORrb2/h6O5vLn5I/tE8kvl/7XzNXY2/7J/wAO/ka48K6Tc3CIqNJLBubivkHxZ/wUD+JV/wCKLltBsdNZf9UrPGzdK5/UP2xPj1dRvLLN9mi/i8q0WlUx2BhH2VON/lf8CKWWZnVl7WrVUf5VzvQ+5pP2W/h75f8AyJ+if9+FqhefshfDW6+aXwZoj/8AbpXwrb/tifFy6jffqXiCZl/ht7Bax/EH7ZHxytLf/RdK8UTL/wA9Hj/+Jrk+u4SSuqN/WNjreW4+MtcR905fofedx+xP8LZP+ZV02Hf/AM8ty/8AoLViax/wTv8AhjrP+qsL6wb+9b3bf+zZr83/ABJ+2Z8cNU+9f+ILNU+8vkbf/ZayLP8Aa8+LkX+t8Q+JN3/XT/7GuGvi8DJ8roI9PD5bm3/LnEtfe/xZ95eMP+CV8Mu+Xw54tvrVv4Y7uBWX/wAdxXnuofsD/FjwRcbrBNN1iJP4op9rSf8AAWr518P/ALYHxeuvlXxDre3+88i//E11Wn/tgfFi1+94nvv/AB3/AOJrwsVHJ6krezlE+kw0s9pr+NGa81r+R2GuWfjT4Zyf8VB4R1aziT/lskDNF/30uVp+h/HDRfuyzbG+/wDPUPhP9r/4ma9cJZy+IZJmm+TbLArLJ/47WD8WLeHxv4gf+1L+2e6h/wBZJbx+V81eLWwGFjTeIoOXKnbXuexh80re2jhsUo8zV9O3meteH/Gnh/WfLlivLbd/y0XzK2I/DdnfyP5T74n+7/0zr5st/hfYy/Na3lyjfw7JK6rw3p/iLw5Gn2PVbl1T+/8ANXkShC+jPSi4tXR67qHw7t5bdImhj8n76t/zzasrWPgXDqcaXESyW10n8UXytJ/tbqreB/iZ4mlvIbW6to5ovvySPH/DWrJ+0BDFrG26025S1R9m5P7tephcDH6q8RU01svNnk1sdP64sPRV9LvyRwfxI1TVPgtoaXV5rHnRfwwyx7pZM/wrXPeB/wBqyPXrf/SLOSGX/Y+apvGl5p/xa8YTX+peYkTzbLe3l+7HGPlrf8J/s/2cUm7TZrJ1f/lm9Y+0oxhyNXkerGnK6nJqxqaX8bNPvynm+Ztf/phXSaH400u6k/dTW0f/AF13Rf8AoVTaP8D44o083TZE/wBqL5lrrdD+D+i+X83mI3/TWOtsPRlJ+6mcWJr0YvVszbLS49e/g0mZX/6bx7quf8KTa/j/AHVhG6/7E6tWrefBDS5Y90Tx/wDAKp2/wTb7R/ot/cwt/sTtXp4fCOorOm3pe/keLWxzpvmVRLWyumU4P2d76L7thJD/ANtKv/8ADL95dfKyR7X+8vmVsaf8M/FGl/8AHvrd9t/671sf2X42sPmXW5H2f341at6VHB/8vIz+RjVr45v93OJzFn+yndRfLb/Iv916f/wyNqV1J/pFzIip/q137lroZPiZ400H701tcr/twVZ8J/Hjxh4j8QJpdrodjeSv/rJPMZVgX/arsoYfLK0+Rc1zkrYrOqVPnvCyOYk/ZD1yW4hm8622227y43/vferN1T4Z+INB2T3nmbU/uV9J+C9Q1aXfFrn2b7R/yzaL7u2rnizR47rR5v3O9tn3a7KnDtHkcqDa8meZh+LcSqihiFGV+x8r2d41rHtlv7mFU/hSTa0lb2j6x4iuY9tneSQ27v8AwfK3/fVM1zw+v/CR/wCkQ+T89eheB9Hkv7PbYW29V+dpPL+Wvksvli6ld0VJ9ku59pj6uFpUFWcY/wCRiaHH4mlufs8WqyJLs3s3/wC1XQ2fhjxtqkaLFrcn/AK7b4b/AA3WWN9SvHkaWZ/lj/2a7+zs47CPbEmyv0n+yZe6nNqyR+X1OJFFSlGEXJvT3VovwPHLP9n/AMTX/wC9vNeuf93zKzfFHwL1TS7ZJZZvO3usS/v23SMa94k3Vz2sH+1PGFnbt/qrNPtDf738NdlHI8LN+9ex5+I4qxsY/u3FO/8AKjxmT9nfXrX5mSN1/wBiRf8A4moZPg1qEUnzWG//AH5G/wDZa+hJLf8A26rXEdc/9j4e943vfqdMuJ8ZOC9pbbofNN54AWXXIbW6sI0XY0s33vu/8CqnJ8N/B93cOq/YXl/6+K9y0O3XWfEGq37p8rP9nX/dFYPiT4F+F9ZkdrjR7Lc/zsyJtaunGZfCLjClFXXU4svzmVVSniJy12t0PH7j4X6DpcDy26Rs38K+Zurwr4wR3ltJMtrZyIv97y6+kPFH7Kfhu6k3Wr6lZv8A9Mrtq4zXP2a4bX/V63qzr/tyK1eZLC4hvSK+R61PHYRL3ptnxV4g0fXL+R/4K4/xB4T16KRPtF5Im/8AhT5q+2NQ+CcelybmvPtK/wB2WNa4Dxp4D0+68aWdqsO1YYWlkX/0GujB5fXnP947IjH51hoL92r3dj5j0/wXq32hPNvLl67/AMN+D2+T/WP/ALT16vceA9Pik+WHZRb+E7eKP5Xk20Qy+otWzLEZlFxXIraHN6Ppa2FwjbNldzb3H2qPdWb/AMIvD/flp9neL/aD26v80Kb2rs9jbY56OIV0mcf8VND/AHn2ha4ffXsvizR/7U09l/iry648D6lLqDrFZysv+xW1OSODF0Gp3Rm+Z/dp8claUfw/1r/oG3P/AH7q5B8J/EV193R75/8AtnWnMjiMKo6623+A/i66j3LolzU//DP/AIu/6Atx/wCO0cyA4vzfeiu5/wCGa/GUvzLo9zU0f7K/jjzP+QPJ/wB/KOZAcBR5vvXpH/DJfjiX/mFf+RKfH+yB46l/5hX/AJEo5kB5pTX616lH+xf48l/5cY/+/lTx/sV+Ov4rO2/7+U07geReZS/N7V6//wAMR+NpY/8Aj2tv+/lTW/7C/jS5/gtk/wC+qG7AeL0V7pH+wH4yk/jsf/HqfJ/wT/8AFkX3prb/AMepcyA8Ior32P8A4J7+KJfvXlt/37qzb/8ABOvxF/0Erb/v3RzID57MjRCoY5K+kI/+Cc+vS/e1K2/78VNH/wAE39Y+82qxf9+6OZAfM79aj8yvqKL/AIJv6lL97WP/ACAtWbf/AIJp3X8WsSf+A9HMgPlX5vaos/vK+tf+HZzf9Bi5/wC/a1Zi/wCCZcP8WsXP/ftaOZAfIvmim19hf8Oy7P8Ai1W+/wC/a1NB/wAEy9NH3tSvv/HaOZAejW//AATz8L+Z81nG6/7cda+l/sB+EYv+Ybbf9+6+hLiSOwgeVv4P7leLfFzxR4o8UaxDZ6W/9laajqn7qTbdXbf7u37q1yxwtNK1j3nmmIlvIrXH7HfhHQY0b+x47mV/kjjij+aRqs6X+xv4b+2JdalYWM0qP+5t/L/dQf8AxTV3/wAP/hnJoMaXGpX99f3n/TWdtsf/AI9trrfK9q2jCEVaKOOpiK0nacmzgLP4D6Ha/csLb/v3WrZ/CfSbX7tnbf8AfuuqjjqSjlQe2m9G2Ydv8P8AT4o/lto4/wDtnVyPwnZx/dhjrQpqdKXs0R7SXcrpo9vF/BGlTR6XD97ZHU/ze1cp8SPipY/D7Rnk/wCPm6d/KjhT5vMb/ap8o46s6H+z44v4I6oSSSapI9vYfIv/AC0un+7/AMB/2q4nwH4g8XeN5N0tzHbWu/8AebI/87q9Is7NrW3Rd/nbP4q0hyx2QqtNpWu7EOl6HDpdu6xJ8z/6yR/vSN/tVN5FO2VL83tU9bjp2tZFK4t6hkt2rQpJP3sdBoZvltR9n+tTXEixfNK8aKn3mevKPix8eLrRtYh03Q4Y3uI/nmmeP5Y6TVzGMW3Y9L1S8j0a382X/gKp8zSNVbT9Pmv5Eur/AO8vzx2/8MH/ANlWD8P4/EWqRw3mszWyL99Y0jWuwrRSSVkiZQkn7xJRUcXanb6zSsMN9VJ/9YauSSLFG7f3K8r+MHxcurCNLXw4kdzdb9803yssC0xL3tDv9Q1CPS7d5ZfnWP8Ahqhp+l3Gs3CXl/8AJs/1Nv8A88/9pv8AarkvhVH4i8UWcOpapqX+i/eVU+XzK78apaxfeuY0/wC2i1rGWmtvvM5UZTa5dSaOPyaf5dcx44+Mnh34c2f2jUtSjRf4dnzf+g15drH/AAUc+H9hefZ4n1K8l/vJaNtrkrY6jSdpySO6jgMVU/hxbPdY7en+XXicf7dmi39uk1nYXLq/9+TbVP8A4bUa6k229hbQ/wC/IzVj9fodzRZfiP5T3rYv9yrVtXy74o/a81612fZ5LZGf7qpAzVjyfH3xV4jjk3arfQ7/APnlHXLLNqSel36HRTyarPfT5n2B8sX8dH2yOL+OOvhXUNY8WXUjtceMPEif7sn+r/8AHaoXGs6l5ez/AITDxJM38X79qccyX8pv/Yckr834f8E+/wCPUIf4po/+/lH9qw/89o/+/i1+fsceuS/d1vVpv9+7bd/6FU0dvr3mbf7S1L/wLatlmLf2fx/4BhLKElrUX3f8E/QKPUI5fuzR/wDfxam8yvg/T9L8YRW+611jUoWT7reezV7H4D0fxdL4bs2l1u+mldN7M8ldNPEOSvy/icVTARj9tH0b5kf8Tx1DJrFra/euY0X/AK6LXzx8QND16xt7Zf7cvl3v82yTbXDXHheaWTbdX+pTf78jVXtm5cqRH1L3OfmVj6l8SfEzR9GjRWv7ZGf7reYtc9eftEeC/C1vtbW7Z2+/Js+bzGr54uPhXHqluirDcuifd+9VO4/Z3muvu21z/wCPVjiswnBctNHZhcnpVVzYhr+vM9p8Qft2eEdGH+j/AGm8/wByOvOvEn/BSi3td6WGiSv/ALUslcx/wylcXW/dZ3P/AAOi3/Yzuprjctn/AN9V49XH4tu0Y/ge9RynLUvflp6mJ4o/4KUeKLmN1tbe2s/7uyNpWrgPEn7cnxE1k/urzW/n/wCfe02/+y17ro/7H91a72a2jrb0/wDZr1Cwk/dWcdckq2YzWja/A7owyql8DifGHiT40/FLxR92Hxbc7/78jL/6DXNyeE/ih4ok/wCQJqTs/wDz1kav0Os/gfrUUm5kjTZWrofw31K6O5fLTY9VQwOKrXU7r1MqmcYSgv3cY/Lc/PTwf+yf8RNZuFa/sPsa/wANd/H+xn4olj2tcyQo/wDcr7k/4VnqUsnzXkaf7kdMk+Ed1J97VZE/3K1/siq9IXE+IqTV20vkfDkn7A+qXUb/AGjWNWT/AHZNv/sta/gf9hux0uzuIpZtWf7YmySZ5/mr7DvPhWv9oW1v/aVy6v8Ae/eVvWfwo0+1/jk/77row+Tzpxc38TPMxfEFOrNQb91fifNnw7/Zb8P/AA+t0Wzs7nd/elk3V6RofhvS7D5ZbCN9n+7XrX/CD6bax7pU2LVPUND035Le38t2m+StsHlLou0fvepxY7PKdaF5RRx+l6fot1I629hbIyfe/d1sR6fb6f8ANFpts6v/AA+XXeaP4P0+wjRFto/l/irS/wCEetf+eMdd31VttJr7v+CefTx0bJ/qeS3H9l3X/Hx4Ytpv72y33f8AstQweF/CN1H+98JR/wDA7T/7GvZo9Lhii+5HU1vpcf8AcjrKWXu/2fmv+Cbf2nFdH/4E1+R5Fb/D/wCH/lbZfD1jbL/t2i//ABNUNQ/Zn+GPiP5m03TUb/vmvbLyztZY9rQxv/2zrB8QeF9JhsppWto938OysllbfuuEX8iv7Zfxqc1/29f9DxCT9kP4f2HiCH+zba2tpdnzSJJWJrn/AAT78H30jyxXmx3/AOmle8aP8I9Nls/OuIf3r/PUsnwf02WT78n/AH8ajGZXCVOOHVJckdd9316GmBzurCpLESrSU5aX5Vt03vt8j5huP+Cd+n2G9rXXpIf9/bWbqn7GepaDHut/Els+z+F6+qLj4KWcv3Zrn/vusHxR8D7OO3jVZpHlmfYq+ZXiy4ZhUnyqlv2en5H0MOLJwhzutd+as/wf6HypqHge68E2clu032y6m+RmT+7VOz8HzX8f/Hhv/wB+vrq3/Zr03y0a4Tzpf4mqzH+z/pdr/qraPdXHmmQ4itONKirU4KyXkduVcSYWlCVWs/3k3dvzPkL/AIUfdap92wjSrmn/ALLeqS3Ee2aS2/65V9Y/8Kja1/491jpmqeC9YtY/9HSN/wDZrz48Myi+aafyO+XFNOStSkvmeFeH/wBnfxFpfksut321P4a7zR/DetaX8tw/2lf9uOr+qf8ACaWEv7rSvOX/AGJ//iqwbjXPG3mfNpVyn+5tatPYwoe6ozH9ZrYiN3UhYs+LPtlhZvK1na7a8E+JH7TGvfDnXH+x6PHdWqfeavXbzT/EWvSPFcQ33+0vl/6uqdx+zHZ+KI2+3w3zq/3lrsr060MN+5i1Ke/p2ucmFrUJYrmryi4U9ter0ueS+G/+ChC3/wDx9aJ83/XRq9F8F/tUWfi23dm025s/9+un8L/sdeD9H+7o+9v9uPdXc6P8A9F0+P8AdaVGn/bOvPjlePt7rfz1PRqZxlqfw/19x5j/AMLI/wCEj1iG3/eQ2r/6xq7bwf8AFPT/AAb/AKHYab5Kv/rJP4pP96uh1D4V2thbvLFZ/dqHw38I7q/tt3kxorvvXfXoYfLcwpx9pC3N6HkYzNMtrS9jVb5bXep0+l/ESx163RpU8lv4a6GPbfx7l+df4axND+D62Eieb/45XYafocdhGqqlfVYNYmcf3ysfHZhLCU5WwrMG8+Gem67JuurON/8AtnVnXLOHQNDSws0jT7T+5VU/u1t3uoQ2Me64eOFf9uuej1i11nxWmybfFCny/wC9XpYPC0adTnikjx8djsRVpcjk99DodPslsNPhiX7qJU3ltTPMo80VXM5asz5bJegSSeVG7N91PnrE8JR/apLy/b71w/y/7oqbxRqi2umOqzR+a/yVNoca2ulwqr+Z8lbRl+7uupjKP7xLsWZ6yvEl5/ZejzS/xbPl/wB6tWSRa5jxxJ5v2aD+/N834VNGKdRX2uPESfLoQ+F7NrDw/Crfef52/Gk1HrWs/wC6t0X+58lZt7RUleTfmOnFKKS7HN6zXH+II/N3122qR5jeuV12P79ZmqdjzfxRb/fryKONb/xhqt1/Cn7pa9m8YfurOZv7ib68o0PS2tdPdm+9M7PW1NpQk/KxlUTlOK87mJqkf7z5apx/3a0tXj/eVkVhF6I9DW5afpXLeD91/rGq3X8LzbF/3RW3qtx9lsJm/uI1Ynw7t/K0d5W/5bOz1rCMfYyfXQx9pavHst/6+Z09vJ5snzV6X8O/CdrdR+a8O+vN/Ddg1/qqrs+V3r6i+E/gSOPw+m7+NPu1yRi0dmKqXOGl/smwuNrJs2V0Oj65ocUafJHWV8SPA8l1qj/Z0+Wse38B3lrH/wAtErRK55/KekWXjDQ7WOnyeMNFl/h/8h15pH4Xut//AC0ok0O6i/56U+ULLueo2/jjRYv4P/IdWf8AhYmi/wAKV5FJo95/f+WoRp9xF/HRyiZ7NH8SNF/uU/8A4WhpPmfLDXi32e4ipn2e4lo5QR7Z/wALd0v/AJ40yT4uaX/zxrxaS3uopKPIuvLo5R2Xc9pj+LGm/wDPGmR/FzT/APnjXiZjuovlp/8ApntTauJnt8fxgs4v+WMdMuPixay/dhrw2S4vIqPtd7S5RHuUfxUt/L/1MdP/AOFsR/8APGOvCv7QvIvu0+PWLqjlA9y/4WxH/wA8Y6JPiwso+7HXif8AbFx60yTXJqOUD2z/AIWosR+5FRJ8VPN/5514h/btxR/btxRyge3/APC0G/6Z0v8AwtCT0jrw/wD4SC4ok8STUcoHt/8Aws+T+9HRJ8TJP+e1eIR+JJqm/wCEom/v0coH2l5f96mfZIfM3bI9397y6n2UbKk7BI41pKkooAbso2U6igBuynUU3fQA6qH/AAiemy/fs7Z2k+f546u76jkkoKjJrYZZ2cNhHtiSOFf7qVLUPzU6gnqOkkqTfVWXvRQaUy18tRybah3tRQDm07FPXNLt9Zs3t7iPfE/8NYv/AAr/AEcyJus432f3/auguI6p/NQZ3a2Hx7Y/lVPlpd9R+U1OoCUiSimp1p1BPMMuLdbq3eOVN6v8jLXJeNNDj0HSnl03R/tlx9zy0k2r/wACrsJe9QySf+P/AHqpx6Ci7Pa58i/tIePPi5L4fS10PQbHQbeH7rfb1X5a+bLO4+IV/wCIN3ijW5La3T+GK7k/ef8Ajor9NfEngux8Wxot5D5yp/D/AA1yuqfs3+E9ekRrrR7Z9n9+Ovn8Zk9etK8Zn1eV59QoR9nOmreSv+h8l+D9YsZbP7P5P9pN/el3S/8AoVWbjy7+8eKLRI7ZvubvIr6/0T4F+GdBj22um2yf9s60P+FX6L/z4R/9+6xjkdS3vtN+eoVOIKSk+RNL1Pk7w/pckse37NY/9+K0rfw3dS3G1ZraH/aSBa+qLf4f6PF92zjT/tnVmPwPpfmf8e0f/fuu6OV2d7o4f7a7Jnyv/wAK7uLq2fdeSPLs+VvLX93U3gPwnZ+HLx7e8ub68uHf5m/hr3jx58JLrxJqkLWFz9gtU+8qf8tKueF/gvZ6N81w/nS/3mrnp4OpzvTQ6qmZUnC7lr2PItY0e11CP7PFbSf7Nc8nwL1S6uN0SbIv4f3dfUtl4TsbX7tvH/vVfj0+GL7qV2yy9z96TOGnnPIrJHzbo/wDuPk8/wC0v/2z211+j/Afzdm222f7T17THbrF/BUldFLCRicNfMpTexwWl/BdYrfbcPsT+6ldPofg+10az+zr86/w761qjkj82PbXX7OK2OP28mee/FzxJb6DcQ28Vn9puP8A0XR8O9Hm164+1XVtHDF/1zrqrzwHa6pcebcJvb+996tjS9Pj0uzSKJPkSmlYzu7WuMj0e1i+7DH/AN+6n+xx/wB2NP8Acp/ze1Rb6XLHsV7STVmx3lr/AM86jfbj5aJJKhkquljOW9x1U9c1iHQdPe4lfYqf36teZVPV9Mh1m38q4TetJq4nqeUa58TNW164f7Bcx/Z3+SNUjr0XwPp82l6HD9o/1r/O1Fn4L0/S5EaK2jRvv1qVTk2rXYtOxJ5vvXA/EDVdQv7x4ovtMNun8SV3Hl03+z1m+8lIDhfhHo99LcPdXjybfuR769Cj3eXT7PT1ij2qny1Zjt/3lJ3YkrHl3xY1y+urj7Hb21z9n/iZKrfCPwHdXWuJdN9pS3T7qvXrv9jQy/ehjqazs47UfKmyqTaGPt41ijqSimv0pdbjbuL9s8qm/a2pPL82jY1BZg+MPGC+GLfc3zy/wrXPaP8AFCTXtQhtZbP7/wDwKtvxZ8M18UXHmtNJTPB/wvh8Oah5u/eyfxPRH3VoZnVp9yOnf6mjy6JKPUrmZT1DxJa6XJtuJo4WqtbyWus6olws2/y/urXm/jS3vtZ8VzJLZyPb/wALV2Hwr8JyaNbvLL/H/C9VGTi7ozlFSWp19O+Wm02Ss+UodTfNFNoqtQCo7zy4rd2ZI/kqHWNUj0bTpLiX+CuDuPjJN9oZWs/3TvsVqTVxptHYeG9Hj/fXjQx7rl/+ef8ADWr9khi/5Yx1W0O8a/0+GXZ5e9KtU60+doVGLgrXYn2eH/njHRHGv9ylrM8QeLLPw5sW4m2M9Tyor2knuM8UXHmyJZxfem/1n+7WrbbbW3WL+5XPaP4k03XtQ3W7+ZLW95XtW3MuVRRjyvmc3sP+0fSjz29aZRWTVzVu5xPxXs9Q164ht4od9r/y0rH+H/ge6sPFCSyw+Tbqn+7Xp1FPpYRJWf4lvJrDQ7lrdN8uz5Vq5RL+9+9QB4he6fqF150rfbvtD/d/hWvV/A9vJa+G7ZbjzPN2fNurS/s+H/njHU3le1KwdbnN/EzXJtG8Pv8AZ0/0h/kWvH49Q1SXUId1zczS7/mVo69+1Czjuo9sqb6zZPD9n9o3fZo91Um0BDp5b+z4d39yqd7WrJGtZuoR0gMLUI65rxBH5Vu7V1uo/wCNc3rlv5se1vu0AfK/xU+KGrS+ILmK1eOG3h3Ju+9VP4b+ILzxHbzNdfvNnyLsr2DxP8I9JvpHaWH5n+9XMf8ACIWvhe2eO1TZR0sVE4/WLP79c3cW/lyV2GsW/wB+ub1SOg2jI8K8afGjWotcubOws/Ot1+Rmeun+B/ji68W6fMtxD5LW38NdDefDLT7q4dvJjRn+9U3gf4b2vg3znt/uzfeajUnlV7nSeH9c/sG8SVv4K9g8L/tOW9hpn2dn2V4neW9c3rFvJFJ8tJq4Sbe59JxftAabdXjszx/7W+rP/DQmg+X/AMfNtur4w8Ya5dWGj3LL97ZXzx4k+KmsQ3kyrcybUf8A56NXp4LA+2u07WPLx2LVFq/U/VOP4+eH5f8Al5tkpknxv8Py/wDLzbV+QuqfGzxFF925k/7+N/8AFVg6h+0R4qi8z/SZP+/jf/FV2f2K1vI83+1vJn7DXnxs0H+G5tqzZPjBo8v/AC2tq/GrVP2qPFVr/wAvkn/fxqzZP2yfFlh/y8y/9/2qZZTbqaRzVvoftPb/ABY0Uf8ALaP/AL+VNH8UNH8z/j5tv+/lfiHcft0eLrWT5bmT/v41U7z/AIKMeLNL/wBbc3P/AH8as3lqTH/ab7H7kSfEzSZf+Xm2/wC/lTR/EzR/u/abb/v5X4Syf8FWPEFp96a53f8AXej/AIe4a5F/y2uf+/8A/wDY1nLAxte5vHGN9D93f+E80n732mN/+2lEfjTS/wDn5j/77r8JY/8AgsJrEX8d9/38Wrsf/BZTVvL+/fP/ALPmLWf1NdzT6xPoj904/Gmky/L50f8A38Wn/wDCQaTLJ/rv/Qa/CiP/AILOap/0/J/3zVmP/gtZqUX/AD/O3/AamWDXc0VabR+6n/CQaPKdvnR/+O1D/amk+Z/ro/8Ax2vwx/4fYah/z0vv+/a//FVZT/gtpqH8X27/AL9r/wDFUfVY9yfrEz9y47vS5f8AltHT/tOl/wB8V+Hsf/BcS6tf+f5/+2f/ANlVmP8A4LkXEv3nuY/+2bf/ABVH1eH8xXtqvRH7bb9L/wCetMk/sv8A57R1+J3/AA/Im/57XP8A37b/AOKqxb/8F0JP47mT/v23/wAVU/V49ylUm1ex+1nl6b/z0j/OiS002X+OOvxb/wCH6Df8/Uv/AH7arNv/AMF11k/5eZf+/bUfU13M/bz3P2ej0/TYj96OmPaabL/y2jr8bf8Ah+gvyf6Z/wChVMn/AAXUhif5rz/0Kj6mu5pGtN7I/pY+zVD5XtWh9hao/sDV5+p6V0U/K9qPK9qtfY5P8mj7HJ/k0ahdFWipvsclEmnyUajUkQ1HU39nzetN/s6ajUfMiL5vaon6VPJp81M+xzUahzIhkuKZ9o+tTSWd1/cqH7Jdf3anmRQeY1P3rTf7PvP+eNVZLfUP4Ujo5kXF2Lnm+9EklZcmn61L91I0qD/hE9ev5P8AXRov92s3Jp6FuSRpfNLHVaSr9vod9YW/zfvmqH7PJ/FDW2pzOSZWjkaj7TU0lu2//U1DJHJF/wAsaadtwWo/zPNpKbmb/njTPNm/59pajmQ+V9CWoX6UslxIf+XaSoZLmQf8sZK05kHKx+9qKb5kn/PGSk+0t/zxko5kJqxa+b2pPMqGO4b/AJ4y0ef/ALEn51PtEPlZa306q/2z/pnJTo7xf+mlUpphysmp3y1X+3r/ANNad/aMdHMg5WW/m9qWqv8Aa9v/AH6b/blv/fo50HKzQoi7VQ/t+1/vUf2/a/3qOZE+zl2NHfRvrO/4SS1/v0z/AISWz/56UcyD2bNXzPKpm9qoR+JLOX/ltT/7cs/+e360cyJ5WXKKrf2va/8APamf25Z/89v1pe0j3DlZcokjqn/wkljF/wAtqJPFmn/89qrmj3BQk9iZ4/7tH2dqpyeNNP8A+e1Q3HxA0+KT79T7SPcfs59mX5Lel+x1jSfEfT4h9+q0nxY0+L/lpHSdaCV2yvYz7HQ/Z/pU0cfm/drlY/jBp/mbd8dX7P4uaT/fjqfbw7kfV6v8rOkt7NjVn7P9K56P4saXL/HHUkfxR02U/fjq/aR7h7GfZnQfZqNnlViR/ETT/M/10dWY/HGnyj/XR0e0j3J9nLszSkoijqmniSzlPyzVNHqlvN/HT9pF7ByyW6ZZ+z/Wj7P9aZHqEf8Afo+2LVEy3sTUVD9sWm/bKSdySxTdlQ/alpPtH0pgPkt4/wC5R8sXy1DJcU3fQBNRUHmeVT/PoAc/Sm+V7UefR59AGb4o8P8A/CRW/lfcWsR/hfHLJDu+dYfnWut8+jz6aTYBb2f2WNF/hSpKg+0fWl30gHSSN92uA8SeD9Q17WHluPnt/wCFa73fTftlAHG/DvwG2g381xKkab/u121M8xf8il30AO8r2o8r2pu+jfQA7yvapKq/aaPMoAsP0oTpUHze1LQBJRUPmUeZQA+T/WVA/SnVHQBVfpVGer8klZt5JQBlaj/jWDqn+qre1COsTUI/v0Acf4gj4rhvEFuvlvXoWsW/mx1xPiC3/wBigqJ514gj5rktY+/Xc+JbRq4rWI/Keg0g0mZtWI5PNqjvq3byUFBcR1g6wjf8BrpPL/d1m6hZ+b8tHS5Mjyv4of6L4fuGr5m1y3b7Y7f7dfUXxos/K0N1r511TS/NkdtlfWZFQfsnc+M4gxEVVSPPdcjjirjNc/fb9tdz4os5Irjay/LWDcaYs1fSQwqUT5SWYXlY801jT5Jf4K5XVNLk8yvYNU8P/wCxXN6n4T/2K46lHU644uNtWeSahYSZrlvEGjtdR/cr2PVPCbS/wVg3ngf/AGKiWHfY0jmFJHgOt+B2k+bZXPXvhOTzK+h9Q8D+b95Kx7z4brL91K5KmWqWrN6OdOLseCv4TkqCTw3JXud58PMfwVn3Hw//AHvypXPLK0b/AOsDj8R4zJ4bb+5RH4favYJPhu3l/cqnJ8O2i/5Y1n/ZKbOlcQxtqeV/8I/70f2B/tV6j/wg7f3Kf/wrhpY/uUf2S1q0NcQQfY8r/wCEf96P7E/zmvVP+FXt5f3Kf/wrBvM+5U/2YuqNIZ5FnkVxpflVDbaP5sleo+JPhfcZ/dJVPQ/hXdfaPmSSsZZfK+x2U86pKPvM4OTR/wB3Vb+z/wB5XscnwoaW3+59+sqT4N3H2j7klEssk3exEM9pL4rHAf2P/FVOXR/nr2G2+GDQxx+Ynl1h+K/AUllLu2fLRPL5RRNHOIzmf27VHUlR186fVBRRTX60AM+b2o+b2o+b2o+b2oAPm9qSSiSm0AFFFFADX6U2pKji7VPKg1JKj3tRL3oo5UGoeb70b2opr9aOVBre4n2hvSlfrTPm9qSSqAX5vakkptFJq4ahRRRS5UOMmlYTzFo8taWijlQpNtWE8taZ9nj/AOedSUUcqDUj+zx/886Ps8f/ADzqSijlQ4yaViP7PH/zzo+zw/3akoo5UPmZH9nh/u03+z4f7lOl71JRyoOZlf8Asq3/ALlN/sy3/wCeNWqKOVBzMq/2Ta/886f/AGHZ/wDPGp6KOVBzMq/8I/Y/88ah/wCETsf+eMdaUdMjko5Y9Q5mUJPBdj/cqP8A4Qex/u1rfaaPMo5Y9gVSS6mX/wAIFZ/3KhuPhvp8v8Fbfze1Hze1SqUUCqSXU53/AIVXp8tQ3Hwb03/pp/38rqPm9qWp9jAHVkjkJPgfp8v8cn/fymf8KH0+U/8ALT/v5XaJ1p3m+9HsImkcXUSsmcBJ+z/Y/wB+Smf8M72P8LyV6F59Hn0vq8A+uVe55p/wz5bxSf66Sof+Gd28z/XV6j59Hn0vq0OgfXa3c8uk/Z7kP3Zqh/4UPcRfdua9X8+jz6X1Sm9yvr1XyPJ/+FBXn/PzTf8AhRepRfdvJK9a8+jz6X1OHmV9fqdkeSx/CPWrX7t/U3/Cv/EEUf8Ax+V6p59Hm+9CwsVs2L69N7pHltv4U8RRf8to3q7b2fiC1k+Za9F833o3rVLDpKxH1pvdHDfa9Y/59qZ9v1j/AJ967nzF/wCedM81f7lV7N33I9rD+X8TjI9Y1SKP5raSrMfiC8H3raSuq8oUfu6rlfcPaw/l/E5X/hILrzPmtpKI/Eknmf8AHtJXVeXH/k0fYo/7lHK+5DqJu9jno/EHmn/U1NHrEY/gkrY+x2//ADzo+x2//POjlfcOZdjI/tmP+5JUEniCOL+CStv+zof+edH9lW/9yjlfcFKJiReIIZP+elH9ux/9Na2JNHt/4kpf7Ht6pRfcOZdjJj1SOX7r0/7fH/frR/sGGlk0OGqJsu5lf2nH/wA9KfHeR/36uf8ACPQ0f2BHQVyLuVvtsf8Afp8dxH/fp/8AYC+9O/sFaA5F3G+Yv96jzP7tO/sFak/sagzGRyLS0n9kLUsen0AR07zKebPyqX7K39+gCGipvscn+TUFxZyUAI/Smy96j/s+Sj+z5KAGyRrVO4t6uSafJR/Z7f3qAMe8s1lrH1DS662TS2qtJofm0Aeb6xpFcl4g0Nv7lezXHhfzP4KzdQ8D/av4KAPnXxB4fk+f5K4zV/C7Sjdsr6f1T4X+b/BWDqHwXWX+CgrmPle88NyCT7lEehyD+Cvo+8+A6yn/AFNRf8KDWKT/AFNBpzaHgMehyS/wUy88PzS/wfNX0PH8D1/ihqzH8E4/4oaPIiT0sfD3x40Ob7Ht2fwV4Ve+E5v7lfov8WP2cP7e/wBVbSfPXAf8MfN/z5yV93k9ajTopTkfmXEkcTUxV6cHa1j4J1j4ZyXUb/ua5XUPhfdRfdSv0a/4Y/X+Kzk/8dqtcfsfw/xWcn/jte3Tx2GWjkj5Gvg8bL3owZ+a154DvLX/AJY/+Q6zbjwPJ91oZK/Sy4/Yvs5fvWcn/ftaoXH7C+myyf6mT/v3XdTxWCas5I8mph83g/dg2fmnefDdpf4KpyfCtpY/lSv0j1T9hOx3/Kkn/fisq8/YTtf7kn/fuqlUwDfxo5albN4b0b/13PziuPhRJL/yxqhefBub/njX6NSfsFwy/wC9/wBc6Z/wwesX/POr9nguk0YrMs0W9CR+bNx8F5DH9yoZPg35X8FfpBcfsHr/AHI6rXH7Bfm/wR7v+A0/q+FlvNE/2xmTf8F/M/N+T4X+X/BvrN1T4cNIdsMO9/8ArnX6W/8ADBi/8+tJH+wpDayf8edOOFwsdU0zOeb5lNckqdvkfmRb/BS8upE/0WRP+AV0Fn8F5LWPa0P/AJDr9FIv2M1j+7Z/+Q6Zcfsfr/z7f+Q6ylh6c3o0dOHzOpSV5J3Pz0j+D7eZ/qf/ACHR/wAKWb/njLX6Ef8ADIS/8+tN/wCGR1/54/rR9Rpdzo/1gm1dp/cfntcfBdvM/wCPakj+DDRf8u0n/fuv0J/4ZDX+KGnx/sjx/wDPGj6nSWmgo5/Jq6TPz5/4Uu0X3YZKX/hTcnmf6mv0L/4ZIj/59T/3xTo/2Q44pP8AU1P1Gn5FRzyd7WZ+fH/Cl5PM+aH/AMh1ieL/ANny61O3Cw23zYH/ACzr9LI/2R4/+eNTR/sfx5+aH/vuOp+qU7W0N6OeSjLmSZ+zFFFFfjp/R4U1+tD9aZ83tQAfN7UfN7UfN7UklAB5lNp/ze1MoAKKKjl70AHm+9Hm+9FFABTd9OqL5vagBaT5vaj5vaj5vagA+b2o+b2qLfTqACiiigAooooAKKj833o833oAkoqPzfejzfegAl70eb70UUASUVH5vvR5vvQAeb71JUdSUAR+b71JTdlOoAKKKKAH/N7Uym76dQA3ZUkdNp/ze1Am7C0nze1MooFzD/m9qTzKPMptAm7jvMo8ym0UCHeZS/N7UyigB3mU6o6f83tQAtN8ym0/5vagBaKb5lHmUAHmUeZTaKAHeZR5lNooAKf83tTKKAH/ADe1MoooAf8AN7UnmU2igAp/ze1MooAd5lHmU2igTVwooooGOi+/Tqjp3mUCSsHmUeZTaKBjvMp1R0/5vagBab5lL83tTKACiiigB/ze1J5lNooAd5lHmU2igB/ze1Hze1MooAd5lNpr9Kb5vvQBJTZY1lp1FACeWtM+zr/zzqSigCP+z45ahk0eOrVFAFL+wof+edL/AGFb/wByrlFBXMU/7Ct/7lH9hw1coo6WJM+Xw/by/eWmf8InZ/8APOr/AJvvR5vvRrbcXLF9DNk8JWMv8NQyeC7P+5WpRTUmurI9lDsjCk8CWMv/ACzpkngOx/uVvSVDVOpN7th7GHZGDJ8O7H+5H/37qF/hfp8v/LOP/v3XSU1+tP20+7J+r0uxyknwnsfL/wBTHUMnwjsf+eMddbJTav6zV/mZMsLSas4o4u4+D9j/AM8Y6h/4Uxp//PtHXdUU/rtVbyZn/ZtCT1ijz+T4J2P/AD7R/wDfuq0nwLsf+eMf/fuvRfN96KqOY1U9JM56mU4ZuzgjzT/hQ+n/APPvUNx+z/Y/88a9Rorq/tOv/MzOWRYKW8V9x5LJ+zxZyj/U1WuP2b7P+5XsdFCzbEraRzz4cwL+yjxOT9m+1/uVDJ+znDEfuV7lRJH5taLO8Sla5l/qvgf5DwqT9nNf+edM/wCGd/K/gr3io9i/3K0/tzE9GR/qjgbWsjwX/hn6T1pr/AKbZ8qV779nX/nnRHbx/wByrWfYjqZf6o4H7Njs6KKK8A+xGv1pnze1LSfN7UAHze1JJS/N7UklADaKKKACo6Je9FABRRRQA1+tM+b2p79aZ83tQAfN7Uyn/N7Unl0ANooooAKKKKACo6KKACiiigAooooAKKKKACiiigAoo8r2ooAIu1O31Hvo30ASb6dUO+jfQBNUfn1Dlv79L83tQBY+0fSj7R9KgooAko833oooAKKKKACnJ0ptHm+9BDViSim76bQIkp/ze1Rb6b5vvQBJRUdO30AOopu+my96AJKKbvptAElN302igCSio6dvoAdRRTd9ADqbvofpTaAJKbvo302gCSo6dvptAD45P71JvptFAElFN30b6AHUU3fRvoAdRRTd9ADqKbvp1ABRTd9G+gB1FRxdqdvoAdRTd9G+gB1FN30b6AHUUU3fQA6im76N9ADqKKbvoAdRRTd9ADac/Sm0UAFFFFADX602iigBslNqSm+XQA2mv0p1FAEdNfrTvK9qKAI6Kdso2UARyUeXT5I6ZJJ5VAB5dNpJJ2H3ah8xqAJd9No2NTtlADaPK9qm8ujy6AIfK9qPK9qm8ujy6AIfK9qPK9qm8ujy6AIdjUeV7VN5dHl0AdVUdSVHQaCfN7UfN7UfN7UfN7UAHze1JJS/N7VE/SgB1FFFAEcveiiXvRQAU1+tOpr9aAGfN7UfN7UfN7UfN7UAHze1Hze1Hze1J5lADaKKKACmv0p1R0CTuFFFFAwooqOgCSim76Z83tQBLTX60z5vaj5vagB++mfN7UfN7UfN7UAHze1Hze1Hze1Hze1AB83tR83tR83tR83tQAfN7UfN7UfN7U9OtADPm9qfsp1FBPMN2U6iigoKKKKACiiigSdwooooBuwUUUUEtWCiiigQUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABUlR0UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFNfrQAJ1p1FFABRRRQAUUUUAFFFFABRRRQA1+tNqSXvTdlADaKKKAE+b2pPLp1FACfN7UynSUeXQBHso2U6igCC4/rVb/AFtWbj+tMtqAGRxtU32f60+ORakoAjoqSigCOjyvapKKAI/K9qPK9qPK9qPK9qAI6WOP+9T/ACvajyvagCOipPK9qKAOgpPm9qWk+b2oLTuHze1Hze1JJUe+gYb6dRRQAVH5vvRL3ooAKKKKAG76Z83tR83tR83tQAfN7UfN7UfN7UklAm7Eb9KdRRQMKKKKCG7hUfm+9OfpTaBxCiiigbdiOinP1pnze1Aw+b2o+b2o+b2o+b2oAPm9qPm9qPm9qPm9qAD5vaj5vaj5vaj5vagA+b2o+b2o+b2paAE+b2p+yjZTqBN2G7KdRRQS3cKKKKBBRRRQNOwUUUUA3cKKKKATsFFFFAgooooG3cKKKKBBRRRQAUUUUAFFFFABRRUlAEdFO2UbKADZTakpuygBtFO2UbKAG0U7ZRsoANlGynUUAR0U5+lNoAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigApuynUUAFFFFABRRRQAUUUUAFFFFABRTX606gApu+nRdqKAI6KKk8r2oAjooooAKKKKAG+XS/N7UtFADZI/NqHyvarFFAFeOOpKdJTaACiiigAooooAKKKKACiiigApuynUUAblN8yjzKbQA6Sm0U3fQA6o5e9O302gadgoopu+gch1R0UUEhRRSfN7UAJ5lNoooAKKKKACm76N9NoAKKKKACiiigAooooAKi+b2paT5vagqIfN7UfN7UfN7UfN7UFC0U7ZTqDMjqSo6dvoAdRTd9OoAKKKbvoAdRRRQAUUUUAFFFFABRRTd9ADqKKKACiiigAooooAKKKKACiiigAooooAKKKKACnJ0ptFADt9G+m0UAO30b6bRQAU5OlNooAKkqOigAooooAKKKKACiiigAooooAKKKKACiiigAoopu+gB1FN30b6AHUVHUlABRRRQAUUUUAFFFFABRRTd9ADqKbvo30AOol703fRvoAbRRRQAUUUUAFFFFABRRRQAUUUUAFFFFADZKbUlNkoAbRRRQA/5vaj5vakjokoAbRRRQAUU6OiSgBtFFFAH/9k=
"""

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
    icone_data = base64.b64decode(icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)
    janela_principal.iconphoto(True, icone)
    janela_principal.title("AutoReg - v.4.2.1 ") 
    janela_principal.configure(bg="#ffffff")

    janela_principal.protocol("WM_DELETE_WINDOW", lambda: fechar_modulo())
    
    # Header da janela principal
    header_frame = tk.Frame(janela_principal, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 4.2.1", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Novembro 2024", 
             font=("Helvetica", 14), fg="#ffffff", bg="#4B79A1", justify="center").pack()

    # Criação do menu superior
    menubar = tk.Menu(janela_principal)
    janela_principal.config(menu=menubar)

    # Adiciona um submenu "Configurações"
    config_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Configurações", menu=config_menu)
    config_menu.add_command(label="Editar config.ini", command=lambda: abrir_configuracoes())
    config_menu.add_command(label="Verificar e Atualizar ChromeDriver", command=lambda: verificar_atualizar_chromedriver())

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
    frame_selecao = tk.Frame(janela_principal, bg="#ffffff", pady=50)
    frame_selecao.pack(fill="both", expand=True)

    tk.Label(frame_selecao, text="Selecione o Módulo", font=("Helvetica", 24, "bold"), fg="#4B79A1", bg="#ffffff").pack(pady=30)

    # Frame para os botões de seleção e imagens
    botoes_frame = tk.Frame(frame_selecao, bg="#ffffff")
    botoes_frame.pack(pady=20)

    # Decodificar as imagens de base64
    img_alta_buffer = BytesIO(base64.b64decode(img_alta_data))
    img_alta = Image.open(img_alta_buffer)
    img_alta = img_alta.resize((300, 300), Image.LANCZOS)
    img_alta = ImageTk.PhotoImage(img_alta)

    img_internacao_buffer = BytesIO(base64.b64decode(img_internacao_data))
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

    img_internacao_label = tk.Label(botoes_frame, image=img_internacao, bg="#ffffff")
    img_internacao_label.image = img_internacao  # Manter uma referência para a imagem
    img_internacao_label.grid(row=0, column=1, padx=20, pady=10)

    btn_internacao = tk.Button(botoes_frame, text="Módulo Internação", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#87CEEB", command=lambda: mostrar_modulo(frame_selecao, 'internacao'), relief="flat", bd=0, highlightthickness=0)
    btn_internacao.configure(width=15, height=2)
    btn_internacao.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
    btn_internacao.config(borderwidth=2, relief="raised")
    btn_internacao.config(highlightbackground="#87CEEB", activebackground="#87CEFA", activeforeground="#ffffff")

    botoes_frame.columnconfigure(0, weight=1)
    botoes_frame.columnconfigure(1, weight=1)

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

#def criar_interface_modulo_alta_old():
    # Criar um novo frame para o módulo de Alta dentro da janela_principal
#    frame_alta = tk.Frame(janela_principal, bg="#ffffff")
#    frame_alta.pack(fill="both", expand=True)
    # Adicionar widgets específicos ao frame_alta
#    tk.Label(frame_alta, text="Interface do Módulo Alta", font=("Helvetica", 24, "bold"), fg="#4B79A1", bg="#ffffff").pack(pady=30)
    # Outros componentes para o módulo alta
#    return frame_alta

#def criar_interface_modulo_internacao_old():
    # Criar um novo frame para o módulo de Internação dentro da janela_principal
 #   frame_internacao = tk.Frame(janela_principal, bg="#ffffff")
  #  frame_internacao.pack(fill="both", expand=True)
    # Adicionar widgets específicos ao frame_internacao
   # tk.Label(frame_internacao, text="Interface do Módulo Internação", font=("Helvetica", 24, "bold"), fg="#4B79A1", bg="#ffffff").pack(pady=30)
    # Outros componentes para o módulo internação
  #  return frame_internacao

# Função para fechar o módulo e reexibir a janela principal
def fechar_modulo():
    mostrar_popup_conclusao('\nAté Breve!')
    janela_principal.destroy()
         
# Interface do Módulo Alta
def criar_interface_modulo_alta():
    global janela, menubar  # Declara a variável 'janela' como global para ser acessada em outras funções
    janela = tk.Toplevel()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(icone_base64)    
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela.iconphoto(True, icone)
    janela.title("AutoReg - v.4.2.1 ")
    janela.state('zoomed')  # Inicia a janela maximizada
    janela.configure(bg="#ffffff")  # Define uma cor de fundo branca
    janela.config(menu=menubar)

    #Evita que a jenal principal seja chamada junto com popups
    #janela.wm_attributes("-topmost", 1)
    # Depois de estar no topo, desabilita o "topmost" para permitir que os popups sejam visíveis
    #janela.after(100, lambda: janela.wm_attributes("-topmost", 0))

    # Quando a janela for fechada, reexibe a janela principal
    #janela.protocol("WM_DELETE_WINDOW", lambda: fechar_modulo(janela, janela_principal))

    # Adiciona texto explicativo ou outro conteúdo abaixo do título principal
    header_frame = tk.Frame(janela, bg="#4B79A1", pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="AutoReg 4.2.1", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Novembro 2024\nMÓDULO ALTA", 
             font=("Helvetica", 14), fg="#ffffff", bg="#4B79A1", justify="center").pack()

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
    style.configure("TButton", font=("Helvetica", 12), padding=10)

    # Frame para manter os botões lado a lado e padronizar tamanho
    button_width = 40  # Define uma largura fixa para todos os botões

    # Frame para SISREG
    frame_sisreg = tk.LabelFrame(frame_esquerdo, text="SISREG", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_sisreg.pack(pady=10, fill="x")

    btn_sisreg = ttk.Button(frame_sisreg, text="Extrair internados SISREG", command=lambda: threading.Thread(target=executar_sisreg).start(), width=button_width)
    btn_sisreg.pack(side=tk.LEFT, padx=6)

    btn_exibir_sisreg = ttk.Button(frame_sisreg, text="Exibir Resultado SISREG", command=lambda: abrir_csv('internados_sisreg.csv'), width=button_width)
    btn_exibir_sisreg.pack(side=tk.LEFT, padx=6)

    # Frame para G-HOSP
    frame_ghosp = tk.LabelFrame(frame_esquerdo, text="G-HOSP", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_ghosp.pack(pady=10, fill="x")

    btn_ghosp = ttk.Button(frame_ghosp, text="Extrair internados G-HOSP", command=lambda: threading.Thread(target=executar_ghosp).start(), width=button_width)
    btn_ghosp.pack(side=tk.LEFT, padx=6)

    btn_exibir_ghosp = ttk.Button(frame_ghosp, text="Exibir Resultado G-HOSP", command=lambda: abrir_csv('internados_ghosp.csv'), width=button_width)
    btn_exibir_ghosp.pack(side=tk.LEFT, padx=6)

    # Frame para Comparação
    frame_comparar = tk.LabelFrame(frame_esquerdo, text="Comparar e Tratar Dados", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_comparar.pack(pady=10, fill="x")

    btn_comparar = ttk.Button(frame_comparar, text="Comparar e tratar dados", command=lambda: threading.Thread(target=comparar).start(), width=button_width)
    btn_comparar.pack(side=tk.LEFT, padx=6)

    btn_exibir_comparar = ttk.Button(frame_comparar, text="Exibir Resultado da Comparação", command=lambda: abrir_csv('pacientes_de_alta.csv'), width=button_width)
    btn_exibir_comparar.pack(side=tk.LEFT, padx=6)

    # Frame para Capturar Motivo de Alta
    frame_motivo_alta = tk.LabelFrame(frame_esquerdo, text="Capturar Motivo de Alta", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_motivo_alta.pack(pady=10, fill="x")

    btn_motivo_alta = ttk.Button(frame_motivo_alta, text="Capturar Motivo de Alta", command=lambda: threading.Thread(target=capturar_motivo_alta).start(), width=button_width)
    btn_motivo_alta.pack(side=tk.LEFT, padx=6)

    btn_exibir_motivo_alta = ttk.Button(frame_motivo_alta, text="Exibir Motivos de Alta", command=lambda: abrir_csv('pacientes_de_alta.csv'), width=button_width)
    btn_exibir_motivo_alta.pack(side=tk.LEFT, padx=6)

    # Frame para Extrair Códigos Sisreg Internados
    frame_extrai_codigos = tk.LabelFrame(frame_esquerdo, text="Extrair Códigos SISREG", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_extrai_codigos.pack(pady=10, fill="x")

    btn_extrai_codigos = ttk.Button(frame_extrai_codigos, text="Extrair Código SISREG dos Internados", command=lambda: threading.Thread(target=extrai_codigos).start(), width=button_width)
    btn_extrai_codigos.pack(side=tk.LEFT, padx=6)

    btn_exibir_extrai_codigos = ttk.Button(frame_extrai_codigos, text="Exibir Código SISREG dos Internados", command=lambda: abrir_csv('codigos_sisreg.csv'), width=button_width)
    btn_exibir_extrai_codigos.pack(side=tk.LEFT, padx=6)

    # Frame para Atualizar CSV
    frame_atualiza_csv = tk.LabelFrame(frame_esquerdo, text="Atualizar Planilha para Alta", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_atualiza_csv.pack(pady=10, fill="x")

    btn_atualiza_csv = ttk.Button(frame_atualiza_csv, text="Organizar Planilha para Alta", command=lambda: threading.Thread(target=atualiza_csv).start(), width=button_width)
    btn_atualiza_csv.pack(side=tk.LEFT, padx=6)

    btn_exibir_atualiza_csv = ttk.Button(frame_atualiza_csv, text="Exibir Planilha para Alta", command=lambda: abrir_csv('pacientes_de_alta_atualizados.csv'), width=button_width)
    btn_exibir_atualiza_csv.pack(side=tk.LEFT, padx=6)

    # Frame para Executar Altas no SISREG
    frame_executar_altas = tk.LabelFrame(frame_esquerdo, text="Executar Altas no SISREG", padx=10, pady=10, font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#4B79A1")
    frame_executar_altas.pack(pady=10, fill="x")

    btn_executar_altas = ttk.Button(frame_executar_altas, text="Executar Altas", command=lambda: threading.Thread(target=executa_saidas).start(), width=button_width)
    btn_executar_altas.pack(side=tk.LEFT, padx=6)

    btn_relacao_pacientes = ttk.Button(frame_executar_altas, text="Relação de pacientes para análise manual", command=lambda: abrir_csv('restos.csv'), width=button_width)
    btn_relacao_pacientes.pack(side=tk.LEFT, padx=6)

    # Botão de Sair
    btn_sair = ttk.Button(frame_esquerdo, text="Sair", command=sair_programa, width=2*button_width + 10)  # Largura ajustada para ficar mais largo
    btn_sair.pack(pady=20)

    # Widget de texto com scroll para mostrar o status
    text_area = ScrolledText(frame_direito, wrap=tk.WORD, height=30, width=80, font=("Helvetica", 12))
    text_area.pack(pady=10, fill="both", expand=True)

    # Redireciona a saída do terminal para a Text Box
    sys.stdout = RedirectOutputToGUI(text_area)

    # Inicia o loop da interface gráfica
    janela.mainloop()

# Interface do Módulo Internação
def criar_interface_modulo_internacao():
    global janela_internacao, frame_print_area, entry_data, navegador, btn_confirmar_internacao, log_area, menubar
    janela_internacao = tk.Toplevel()
    # Decodifique a imagem em base64
    icone_data = base64.b64decode(icone_base64)
    # Crie uma PhotoImage para o ícone a partir dos dados decodificados
    icone = PhotoImage(data=icone_data)    
    janela_internacao.iconphoto(True, icone)
    janela_internacao.title("AutoReg - v.4.2.1 - Módulo de Internação")
    janela_internacao.state('zoomed')
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
    tk.Label(header_frame, text="AutoReg 4.2.1", font=("Helvetica", 20, "bold"), fg="#ffffff", bg="#4B79A1").pack()
    tk.Label(header_frame, text="Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Novembro 2024\nMÓDULO INTERNAÇÃO", 
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

### FIM DA INTERFACE SELEÇÃO DE MÓDULO

#Controla o fechamento da Splash Screen se utilizada na compilação
if getattr(sys, 'frozen', False):
    import pyi_splash

if getattr(sys, 'frozen', False):
    pyi_splash.update_text("AutoReg 4.2.1")
    pyi_splash.update_text("Operação automatizada de Sistemas - SISREG & G-HOSP.\nPor Michel R. Paes - Novembro 2024")
    pyi_splash.close()
    pyi_splash.close()


# Inicia a aplicação
criar_janela_principal()


