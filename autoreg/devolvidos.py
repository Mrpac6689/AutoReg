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

import csv
import time
import configparser
import sys
import os
from datetime import datetime   
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from dateutil.relativedelta import relativedelta
import pandas as pd 
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
import logging
setup_logging()

def devolvidos():
    
    def ler_credenciais_solicitante():
        config = configparser.ConfigParser()
        if getattr(sys, 'frozen', False):
            # Executável PyInstaller
            base_dir = os.path.dirname(sys.executable)
        else:
            # Script Python
            base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, '..', 'config.ini')
        config.read(config_path)
        usuariosol = config.get('SISREG', 'usuariosol')
        senhasol = config.get('SISREG', 'senhasol')
        return usuariosol, senhasol

    #Logar no sisreg e chegar à pagina de solicitações devolvida


    #Captura fichas devolvidas conforme periodo definido
    def captura_devolvidas(data_inicio, data_fim):
        print(f"Capturando devolvidas de {data_inicio} até {data_fim}")
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Internação...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        usuariosol_sisreg, senhasol_sisreg = ler_credenciais_solicitante()
        usuario_field.send_keys(usuariosol_sisreg)
        senha_field.send_keys(senhasol_sisreg)
        
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
        navegador.quit()  # Fecha o navegador

    ##### Captura CNS de pacientes em FICHAS_DEVOLVIDAS_SISREG.CSV
    def captura_cns_devolvidas():
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Solicitações Devolvidas...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        usuariosol_sisreg, senhasol_sisreg = ler_credenciais_solicitante()
        usuario_field.send_keys(usuariosol_sisreg)
        senha_field.send_keys(senhasol_sisreg)
        
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
        navegador.quit()  # Fecha o navegador

    ####Capturar motivo alta por CNS
    def motivo_alta_cns_devolvidas():
        # Função para ler a lista de pacientes do CSV criado anteriormente
        def ler_pacientes_devolvidas():
            df = pd.read_csv('fichas_devolvidas_atualizado.csv')
            print("Lista de pacientes devolvidas lida com sucesso.")
            logging.info("Lista de pacientes devolvidas lida com sucesso.")
            return df

        # Função para salvar a lista com o motivo de alta
        def salvar_pacientes_com_motivo(df):
            df.to_csv('fichas_devolvidas_motivo_alta.csv', index=False)
            print("Lista de pacientes com motivo de alta salva com sucesso em 'fichas_devolvidas_motivo_alta.csv'.")
            logging.info("Lista de pacientes com motivo de alta salva em 'fichas_devolvidas_motivo_alta.csv'.")

        # Inicializa o ChromeDriver
        def iniciar_driver():
            chrome_options = get_chrome_options()
            driver = webdriver.Chrome(options=chrome_options)
            print("Iniciando driver...\n")
            return driver

        # Função para realizar login no G-HOSP
        def login_ghosp(driver, usuario, senha, caminho):
            # Remove espaços em branco e garante formatação correta da URL
            caminho = caminho.strip()
            if not caminho.startswith(('http://', 'https://')):
                url = f'http://{caminho}:4002/users/sign_in'
            else:
                url = f'{caminho}:4002/users/sign_in'
            
            print(f"Tentando acessar G-HOSP em: {url}")
            
            # Tenta verificar se o servidor está acessível
            try:
                print("Verificando conectividade com o servidor G-HOSP...")
                driver.get(url)
                print("✅ Conectividade estabelecida com sucesso!")
            except Exception as e:
                print(f"❌ Erro de conectividade: {e}")
                print("⚠️  Verificações sugeridas:")
                print("   1. O servidor G-HOSP está rodando?")
                print("   2. O endereço no config.ini está correto?") 
                print("   3. Você tem acesso à rede onde o G-HOSP está hospedado?")
                raise e

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
        def obter_motivo_alta(driver, nome, caminho):
            # Remove espaços em branco e garante formatação correta da URL
            caminho = caminho.strip()
            if not caminho.startswith(('http://', 'https://')):
                url = f'http://{caminho}:4002/prontuarios'
            else:
                url = f'{caminho}:4002/prontuarios'
            
            driver.get(url)
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

            df_pacientes = ler_pacientes_devolvidas()
            
            # Adiciona coluna 'Motivo da Alta' se não existir
            if 'Motivo da Alta' not in df_pacientes.columns:
                df_pacientes['Motivo da Alta'] = ''

            i = 0
            while i < len(df_pacientes):
                nome = df_pacientes.at[i, 'Nome']  # Nome está na coluna 'Nome'
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

        # Execução da função
        print("Coluna 'motivo' adicionada com sucesso.")
        processar_lista()

    #Reenviar solicitação
    def reenvia_solicitacoes():
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        print("Acessando a página de Internação...\n")
        navegador.get("https://sisregiii.saude.gov.br")
        
        # Realiza o login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        usuariosol_sisreg, senhasol_sisreg = ler_credenciais_solicitante()
        usuario_field.send_keys(usuariosol_sisreg)
        senha_field.send_keys(senhasol_sisreg)
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()
        
        # Executa o JavaScript para clicar no item "Solicitações Devolvidas" dentro do menu suspenso
        script = "document.querySelector('#barraMenu > ul > li:nth-child(3) > ul > li:nth-child(2) > a').click();"
        navegador.execute_script(script)
        
        # Aguardando a mudança de frame após o clique
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Solicitações Devolvidas...\n")
        
        # Verifica se o arquivo com motivos de alta existe
        if os.path.exists('fichas_devolvidas_motivo_alta.csv'):
            print("📁 Arquivo com motivos de alta encontrado. Usando dados completos...")
            df_fichas = pd.read_csv('fichas_devolvidas_motivo_alta.csv')
            usar_motivo = True
        elif os.path.exists('fichas_devolvidas_atualizado.csv'):
            print("📁 Arquivo com motivos não encontrado. Usando arquivo base sem motivos...")
            df_fichas = pd.read_csv('fichas_devolvidas_atualizado.csv')
            usar_motivo = False
        else:
            print("❌ Nenhum arquivo CSV encontrado para reenvio de solicitações!")
            navegador.quit()
            return
        
        # Itera sobre as linhas do CSV (ignora o cabeçalho automaticamente)
        for i, row in df_fichas.iterrows():
            # Acessa as colunas pelo nome
            nome = row['Nome']
            ficha = str(row['Numero da Ficha'])
            
            if usar_motivo and 'Motivo da Alta' in df_fichas.columns:
                motivo = row['Motivo da Alta']
                # Verifica se o motivo de alta é válido antes de proceder
                if pd.isna(motivo) or motivo == "" or motivo == "Motivo da alta não encontrado":
                    print(f"Motivo de alta inválido para ficha {ficha} (paciente: {nome}). Pulando...\n")
                    continue  # Pula para a próxima ficha
                print(f"Processando ficha: {ficha} (paciente: {nome}) com motivo: {motivo}\n")
                motivo_texto = f"{motivo}. FAVOR CANCELAR/NEGAR A SOLICITAÇÃO"
            else:
                print(f"Processando ficha: {ficha} (paciente: {nome}) sem motivo específico...\n")
                motivo_texto = "PACIENTE JÁ TEVE ALTA. FAVOR CANCELAR/NEGAR A SOLICITAÇÃO"

            # Executa o JavaScript para abrir a ficha do paciente
            navegador.execute_script(f"mostrarFicha('{ficha}')")
            print(f"Executando a função mostrarFicha para a ficha: {ficha}\n")
            time.sleep(5)  # Tempo para garantir que a ficha foi carregada
            
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
    hoje = datetime.today()
    # Determina o primeiro mês do semestre anterior (6 meses atrás, início do mês)
    primeiro_mes = (hoje.replace(day=1) - relativedelta(months=6))
    meses = []
    for i in range(6):
        inicio = (primeiro_mes + relativedelta(months=i)).replace(day=1)
        # Último dia do mês: pega o primeiro dia do mês seguinte e subtrai um dia
        fim = (inicio + relativedelta(months=1)) - relativedelta(days=1)
        meses.append((inicio, fim))

    for data_inicio, data_fim in meses:
        data_inicio_str = data_inicio.strftime("%d/%m/%Y")
        data_fim_str = data_fim.strftime("%d/%m/%Y")
        print(f"Processando período: {data_inicio_str} a {data_fim_str}")
        
        print("🔄 Iniciando captura_devolvidas...")
        captura_devolvidas(data_inicio_str, data_fim_str)
        print("✅ captura_devolvidas concluída com sucesso!")
        
        print("🔄 Iniciando captura_cns_devolvidas...")
        captura_cns_devolvidas()
        print("✅ captura_cns_devolvidas concluída com sucesso!")
        
        print("🔄 Iniciando motivo_alta_cns_devolvidas...")
        motivo_alta_cns_devolvidas()
        print("✅ motivo_alta_cns_devolvidas concluída com sucesso!")
        
        print("🔄 Iniciando reenvia_solicitacoes...")
        reenvia_solicitacoes()
        print("✅ reenvia_solicitacoes concluída com sucesso!")
        
        print(f"✅ Período {data_inicio_str} a {data_fim_str} processado completamente!")

if __name__ == "__main__":
    devolvidos()





