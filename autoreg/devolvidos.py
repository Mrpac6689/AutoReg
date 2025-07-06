# Automated System Operation - SISREG & G-HOSP
# Version 5.0.1 - November 2024
# Author: MrPaC6689
# Repo: https://github.com/Mrpac6689/AutoReg
# Contact: michelrpaes@gmail.com
# Developed with the support of ChatGPT in Python 3.13
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
# Versão 5.0.1 - Novembro de 2024
# Autor: MrPaC6689
# Repo: https://github.com/Mrpac6689/AutoReg
# Contato: michelrpaes@gmail.com
# Desenvolvido com o apoio do ChatGPT em Python 3.13
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
#
#  Script avulso para lidar com as solicitações devolvidas no SISREG
#
#

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
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter.scrolledtext import ScrolledText
from tkinter import PhotoImage
from PIL import Image, ImageTk  # Biblioteca para manipular imagens
import base64
import argparse
from datetime import datetime
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

def devolvidos():
    # Função para ler as credenciais do arquivo config.ini
    def ler_credenciais():
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        usuario_sisreg = config['SISREG']['usuario']
        senha_sisreg = config['SISREG']['senha']
        usuariosol_sisreg = config['SISREG']['usuariosol']
        senhasol_sisreg = config['SISREG']['senhasol']
        
        return usuario_sisreg, senha_sisreg, usuariosol_sisreg, senhasol_sisreg

    #Logar no sisreg e chegar à pagina de solicitações devolvida
    import csv
    import time
    from selenium.common.exceptions import NoSuchElementException

    #Captura fichas devolvidas conforme periodo definido
    def captura_devolvidas(data_inicio, data_fim):
        print(f"Capturando devolvidas de {data_inicio} até {data_fim}")
        chrome_options = Options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Internação...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        usuario_sisreg, senha_sisreg, usuariosol, senhasol = ler_credenciais()
        usuario_field.send_keys(usuariosol)
        senha_field.send_keys(senhasol)
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()
        
        # Executa o JavaScript para clicar no item "Solicitações Devolvidas" dentro do menu suspenso
        script = "document.querySelector('#barraMenu > ul > li:nth-child(3) > ul > li:nth-child(2) > a').click();"
        navegador.execute_script(script)
        
        # Aguardando a mudança de frame após o clique
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Solicitações Devolvidas...\n")
        
        # Preenche os campos de data com as variáveis data_inicio e data_fim
        data_inicio_field = wait.until(EC.presence_of_element_located((By.NAME, "dataInicial")))
        data_fim_field = wait.until(EC.presence_of_element_located((By.NAME, "dataFinal")))
        
        data_inicio_field.clear()
        data_inicio_field.send_keys(data_inicio)
        
        data_fim_field.clear()
        data_fim_field.send_keys(data_fim)
        
        # Clica no botão de submissão
        submit_button_script = "document.querySelector('#main_page > form > center > table > tbody > tr:nth-child(5) > td > input:nth-child(1)').click();"
        navegador.execute_script(submit_button_script)
        
        print("Datas preenchidas e solicitação enviada.\n")
        time.sleep(2)  # Aguarda carregar a tabela
        
        # Abre o arquivo CSV para salvar os resultados
        with open('fichas_devolvidas_sisreg.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nome', 'Numero da Ficha'])  # Cabeçalho do CSV
            
            # Função para extrair dados da tabela e salvar no CSV
            while True:
                # Pega todas as linhas da tabela
                linhas = navegador.find_elements(By.CSS_SELECTOR, "tr.linha_selecionavel")
                
                # Captura nome e número da ficha de cada linha
                for linha in linhas:
                    nome = linha.find_elements(By.TAG_NAME, "td")[1].text  # Nome está na segunda coluna
                    onclick_attr = linha.get_attribute("onclick")
                    ficha_numero = onclick_attr.split("'")[1] if onclick_attr else None
                    if nome and ficha_numero:
                        writer.writerow([nome, ficha_numero])
                
                # Tenta localizar a seta de próxima página, se não existir, encerra o loop
                try:
                    next_page_button = navegador.find_element(By.XPATH, "//a[@onclick='exibirPagina(1,2); return false;']")
                    next_page_button.click()
                    time.sleep(2)  # Espera a próxima página carregar
                except NoSuchElementException:
                    print("Última página alcançada, encerrando captura.")
                    break

        print("Captura finalizada e dados salvos em fichas_devolvidas_sisreg.csv.")

    ##### Captura CNS de pacientes em FICHAS_DEVOLVIDAS_SISREG.CSV
    def captura_cns_devolvidas():
        chrome_options = Options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Solicitações Devolvidas...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        usuario_sisreg, senha_sisreg, usuariosol, senhasol = ler_credenciais()
        usuario_field.send_keys(usuariosol)
        senha_field.send_keys(senhasol)
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()

        # Lista para armazenar as linhas atualizadas com o CNS
        linhas_atualizadas = []

        # Abre o arquivo CSV e percorre cada linha
        with open('fichas_devolvidas_sisreg.csv', mode='r', encoding='utf-8') as file:
            leitor_csv = csv.reader(file)
            cabecalho = next(leitor_csv)  # Pega o cabeçalho
            cabecalho.append("CNS")  # Adiciona uma nova coluna "CNS"
            linhas_atualizadas.append(cabecalho)

            for linha in leitor_csv:
                # Antes de cada iteração, navega de volta à página "Solicitações Devolvidas"
                try:
                    navegador.switch_to.default_content()  # Garante que estamos no contexto principal
                    script = "document.querySelector('#barraMenu > ul > li:nth-child(3) > ul > li:nth-child(2) > a').click();"
                    navegador.execute_script(script)
                    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
                    print("Retornando à página de Solicitações Devolvidas.\n")
                except Exception as e:
                    print(f"Erro ao retornar à página de Solicitações Devolvidas: {e}\n")
                    continue  # Pula para a próxima ficha se houver falha ao retornar

                # Processa a ficha
                ficha = linha[1]  # Captura o número da ficha da quarta coluna
                try:                                                 
                    ficha = str(ficha).split('.')[0]  # Converter o número da ficha para string, garantindo que não haverá .0 no final
                    
                    # Tenta abrir a ficha do paciente usando JavaScript
                    try:
                        navegador.execute_script(f"mostrarFicha('{ficha}')")
                        print(f"Executando a função mostrarFicha para a ficha: {ficha}\n")
                        time.sleep(3)  # Espera para garantir que a ficha foi carregada
                    except JavascriptException:
                        print(f"Erro ao executar JavaScript para a ficha {ficha}. Tentando novamente.\n")
                        linha.append("Erro ao abrir ficha")
                        linhas_atualizadas.append(linha)
                        continue  # Pula para a próxima ficha em caso de erro
                    
                    # Certifique-se de estar no frame correto antes de capturar o CNS
                    navegador.switch_to.default_content()  # Sai do frame para voltar ao padrão
                    navegador.switch_to.frame("f_principal")  # Acessa o frame onde o CNS está localizado

                    try:
                        # Espera o elemento CNS estar presente
                        cns_paciente = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table/tbody/tr[8]/td")))
                        cns_texto = cns_paciente.text
                        print(f"CNS encontrado: {cns_texto}\n")
                        
                        # Adiciona o CNS na linha atual
                        linha.append(cns_texto)
                        
                    except TimeoutException:
                        print("Erro: Não foi possível localizar o CNS do paciente no tempo esperado.\n")
                        linha.append("Erro ao localizar CNS")  # Marca erro na coluna CNS
                    
                    # Adiciona a linha com o CNS ao conjunto de linhas atualizadas
                    linhas_atualizadas.append(linha)

                except Exception as e:
                    print(f"Erro ao processar ficha {ficha}: {e}\n")
                    linha.append("Erro ao abrir ficha")  # Marca erro se não conseguir abrir a ficha
                    linhas_atualizadas.append(linha)
        
        # Salva o CSV atualizado com a nova coluna CNS
        with open('fichas_devolvidas_atualizado.csv', mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerows(linhas_atualizadas)
        
        print("Arquivo CSV atualizado com CNS salvo como 'fichas_devolvidas_atualizado.csv'.\n")

    ### Definições Interhosp.py
    def ler_credenciais_ghosp():
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        usuario_ghosp = config['G-HOSP']['usuario']
        senha_ghosp = config['G-HOSP']['senha']
        caminho_ghosp = config['G-HOSP']['caminho']
        
        return usuario_ghosp, senha_ghosp, caminho_ghosp


    ####Capturar motivo alta por CNS
    def motivo_alta_cns_devolvidas():
        # Carrega o arquivo CSV existente
        df = pd.read_csv('fichas_devolvidas_atualizado.csv')

        # Adiciona uma nova coluna 'motivo' com valores vazios ou um valor padrão
        df['motivo'] = ''  # ou use um valor padrão, como 'Sem motivo'

        # Salva o arquivo com a nova coluna adicionada
        df.to_csv('fichas_devolvidas_atualizado.csv', index=False)

        print("Coluna 'motivo' adicionada com sucesso.")
        
        # Função para inicializar o ChromeDriver
        def iniciar_driver():
            chrome_driver_path = "chromedriver.exe"
            service = Service(executable_path=chrome_driver_path)
            driver = webdriver.Chrome(service=service)
            driver.maximize_window()
            print("Iniciando driver...\n")
            return driver

        # Função para realizar login no G-HOSP
        def login_ghosp(driver, usuario, senha, caminho):
            driver.get(caminho + ':4002/users/sign_in')
            driver.execute_script("document.body.style.zoom='50%'")
            time.sleep(2)
            
            # Localiza os campos de login
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(usuario)
            senha_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
            senha_field.send_keys(senha)
            print("Logando no G-Hosp driver...\n")
            
            # Executa o login via script
            driver.execute_script("""
                document.getElementById('user_email').value = arguments[0];
                document.getElementById('user_password').value = arguments[1];
                document.getElementById('new_user').submit();
            """, usuario, senha)

        # Função para buscar o motivo de alta pelo CNS no G-HOSP
        def obter_motivo_alta(driver, cns, caminho):
            driver.get(caminho + ':4002/prontuarios')

            # Insere o CNS no campo de busca
            cns_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "cns")))
            cns_field.send_keys(cns)
            
            # Clica no botão de procurar
            procurar_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Procurar']")))
            procurar_button.click()

            # Aguarda a página carregar
            time.sleep(2)
            
            try:
                # Tenta localizar o rótulo "Motivo da alta" e o conteúdo
                motivo_conteudo_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//small[text()='Motivo da alta: ']/following::div[@class='pl5 pb5']"))
                )
                motivo_alta = motivo_conteudo_element.text
                print(f"Motivo de alta capturado: {motivo_alta}\n")
                
            except (TimeoutException, NoSuchElementException):
                motivo_alta = "Motivo da alta não encontrado"
                print(f"Erro ao capturar motivo da alta para CNS {cns}: Motivo não encontrado\n")
            
            return motivo_alta

        # Código principal da função motivo_alta_cns_devolvidas
        usuario, senha, caminho = ler_credenciais_ghosp()  # Lê as credenciais de fora da função
        driver = iniciar_driver()

        # Faz login no G-HOSP
        login_ghosp(driver, usuario, senha, caminho)

        # Lê a lista de pacientes de alta, pulando a primeira linha (cabeçalho)
        df_pacientes = pd.read_csv('fichas_devolvidas_atualizado.csv')

        # Verifica cada paciente a partir da segunda linha e adiciona o motivo de alta
        for i, row in df_pacientes.iloc[1:].iterrows():  # .iloc[1:] para ignorar o cabeçalho
            cns = row[2]  # CNS está na terceira coluna (índice 2)
            print(f"Buscando motivo de alta para CNS: {cns}\n")
            
            motivo = obter_motivo_alta(driver, cns, caminho)
            df_pacientes.at[i, df_pacientes.columns[3]] = motivo  # Atualiza a quarta coluna com o motivo
            print(f"Motivo de alta para CNS {cns}: {motivo}\n")
            
            time.sleep(2)  # Tempo de espera entre as requisições

        # Salva o CSV atualizado com o motivo de alta
        df_pacientes.to_csv('fichas_devolvidas_motivo_alta.csv', index=False)
        print("Motivos de alta encontrados, CSV atualizado.\n")

        driver.quit()

    #Reenviar solicitação
    def reenvia_solicitacoes():
        chrome_options = Options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Internação...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        usuario_sisreg, senha_sisreg, usuariosol, senhasol = ler_credenciais()
        usuario_field.send_keys(usuariosol)
        senha_field.send_keys(senhasol)
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()
        
        # Executa o JavaScript para clicar no item "Solicitações Devolvidas" dentro do menu suspenso
        script = "document.querySelector('#barraMenu > ul > li:nth-child(3) > ul > li:nth-child(2) > a').click();"
        navegador.execute_script(script)
        
        # Aguardando a mudança de frame após o clique
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Solicitações Devolvidas...\n")
        
            # Lê o arquivo CSV para obter as fichas e motivos de alta
        df_fichas = pd.read_csv('fichas_devolvidas_motivo_alta.csv')
        
        # Itera sobre as linhas do CSV a partir da segunda linha (ignora o cabeçalho)
        for i, row in df_fichas.iloc[1:].iterrows():
            motivo = row[3]  # Motivo de alta está na quarta coluna
            ficha = str(row[1])  # Número da ficha está na segunda coluna
            
            # Verifica se o motivo de alta é válido antes de proceder
            if not motivo or motivo ==  "" or motivo == "Motivo da alta não encontrado":
                print(f"Motivo de alta inválido para ficha {ficha}. Pulando...\n")
                continue  # Pula para a próxima ficha
            
            print(f"Processando ficha: {ficha} com motivo: {motivo}\n")

            # Executa o JavaScript para abrir a ficha do paciente
            navegador.execute_script(f"mostrarFicha('{ficha}')")
            print(f"Executando a função mostrarFicha para a ficha: {ficha}\n")
            time.sleep(5)  # Tempo para garantir que a ficha foi carregada
            
            # Formata o motivo no formato desejado
            motivo_texto = f"{motivo}. FAVOR CANCELAR/NEGAR A SOLICITAÇÃO"
            
            # Preenche os três campos <textarea> com o motivo formatado
            try:
                ds_sintoma_field = wait.until(EC.presence_of_element_located((By.NAME, "ds_sintoma")))
                ds_prova_field = wait.until(EC.presence_of_element_located((By.NAME, "ds_prova")))
                ds_justificativa_field = wait.until(EC.presence_of_element_located((By.NAME, "ds_justificativa")))
                
                ds_sintoma_field.clear()
                ds_sintoma_field.send_keys(motivo_texto)
                
                ds_prova_field.clear()
                ds_prova_field.send_keys(motivo_texto)
                
                ds_justificativa_field.clear()
                ds_justificativa_field.send_keys(motivo_texto)
                
                print("Campos preenchidos com o motivo.\n")
                
            except TimeoutException:
                print("Erro ao localizar os campos de texto na ficha.\n")
            
            # Clica no botão de reenviar solicitação
            reenviar_button_script = "document.querySelector('#main_page > form > center:nth-child(7) > table > tbody > tr:nth-child(8) > td > input[type=button]:nth-child(1)').click();"
            navegador.execute_script(reenviar_button_script)
            print("Botão de reenviar clicado.\n")
            
            # Confirma os dois pop-ups que surgem
            try:
                # Primeiro pop-up de confirmação com opções Cancelar e OK
                alert = WebDriverWait(navegador, 10).until(EC.alert_is_present())
                alert.accept()  # Clica em OK no primeiro pop-up
                print("Primeiro pop-up confirmado com OK.\n")
                
                time.sleep(1)  # Pequena pausa para garantir que o próximo pop-up carregue
                
                # Segundo pop-up que só tem OK
                alert = WebDriverWait(navegador, 10).until(EC.alert_is_present())
                alert.accept()  # Clica em OK no segundo pop-up
                print("Segundo pop-up confirmado com OK.\n")
                
            except Exception as e:
                print(f"Erro ao confirmar os pop-ups: {e}\n")
            
        # Fecha o navegador
        navegador.quit()
        print("Processo de reenviar solicitação concluído.\n")

    # Utilização - Comentar funções conforme necessário

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Captura devolvidas dentro do intervalo de datas.")
        parser.add_argument("--data_inicio", required=True, help="Data inicial no formato DD/MM/AAAA")
        parser.add_argument("--data_fim", required=True, help="Data final no formato DD/MM/AAAA")
        
        args = parser.parse_args()
        
        # Validação e conversão de datas
        try:
            data_inicio = datetime.strptime(args.data_inicio, "%d/%m/%Y").date()
            data_fim = datetime.strptime(args.data_fim, "%d/%m/%Y").date()
            
            if data_inicio > data_fim:
                raise ValueError("A data inicial não pode ser maior que a data final.")
            
            # Convertendo as datas para string antes de usá-las no Selenium
            data_inicio_str = data_inicio.strftime("%d/%m/%Y")
            data_fim_str = data_fim.strftime("%d/%m/%Y")

            captura_devolvidas(data_inicio_str, data_fim_str)
            captura_cns_devolvidas()
            motivo_alta_cns_devolvidas()
            reenvia_solicitacoes()

        except ValueError as e:
            print(f"Erro: {e}")





