

# autoreg/extrai_internados_sisreg.py
"""
Módulo para extração e análise de internações duplicadas no sistema SISREG.
Funções principais:
- extrai_internacoes_duplicadas(): Orquestra o fluxo de extração e análise de internações duplicadas.
- sisreg_internados(): Realiza login no SISREG, extrai a lista de pacientes internados e salva em CSV.
- sisreg_a_internar(): Realiza login no SISREG, extrai a lista de pacientes a internar e salva em CSV.
- compara_duplicados(): Compara as listas de internados e a internar, identifica nomes duplicados e atualiza o CSV.
- codigo_duplicados(): Para cada nome duplicado, extrai o código SISREG correspondente e atualiza o CSV.
Dependências:
- selenium: Para automação de navegador e extração de dados do SISREG.
- pandas: Para manipulação e atualização dos dados em CSV.
- logging: Para registro de logs das operações.
- autoreg.chrome_options, autoreg.ler_credenciais, autoreg.logging: Utilitários internos para configuração do navegador, leitura de credenciais e logging.
Observações:
- O arquivo de saída principal é '~/AutoReg/internacoes_duplicadas.csv', contendo as colunas ENTRADA, SAIDA, DUPLICADOS e CODIGO.
- É necessário que as credenciais do SISREG estejam configuradas corretamente para o funcionamento do script.
- O fluxo completo envolve extração dos dados, comparação de duplicados e obtenção dos códigos SISREG dos pacientes duplicados.
"""
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


def extrai_internacoes_duplicadas():
    sisreg_internados()
    sisreg_a_internar()
    compara_duplicados()
    codigo_duplicados()


def sisreg_internados():
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
        # Cria um DataFrame com a coluna "SAIDA" preenchida com os nomes
        # Verifica se já existe o arquivo e se possui a coluna "ENTRADA"
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

        if os.path.exists(csv_path):
            df_existente = pd.read_csv(csv_path)
            if 'ENTRADA' not in df_existente.columns:
                df_existente.insert(0, 'ENTRADA', '')
        else:
            # Cria DataFrame vazio com coluna "ENTRADA"
            df_existente = pd.DataFrame({'ENTRADA': []})

        # Cria DataFrame com os novos dados na coluna "SAIDA"
        df_saida = pd.DataFrame({'SAIDA': nomes})

        # Garante que o DataFrame existente tenha o mesmo número de linhas
        max_len = max(len(df_existente), len(df_saida))
        df_existente = df_existente.reindex(range(max_len)).reset_index(drop=True)
        df_saida = df_saida.reindex(range(max_len)).reset_index(drop=True)

        # Concatena as colunas "ENTRADA" e "SAIDA"
        df_final = pd.concat([df_existente['ENTRADA'], df_saida['SAIDA']], axis=1)

        # Salva os dados em uma planilha CSV
        df_final.to_csv(csv_path, index=False)
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

def sisreg_a_internar():
    print("\n---===> EXTRAÇÃO DE PACIENTES A INTERNAR <===---")
    logging.info("---===> EXTRAÇÃO DE PACIENTES A INTERNAR <===---")
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
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Internação...\n")
        logging.info("Login realizado e navegação para página de Internação...\n")


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
        # Cria um DataFrame com a coluna "ENTRADA" preenchida com os nomes
        # Caminho do arquivo CSV
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

        # Lê o arquivo existente ou cria um novo DataFrame se não existir
        if os.path.exists(csv_path):
            df_existente = pd.read_csv(csv_path)
            # Remove a coluna ENTRADA se já existir para evitar duplicidade
            if 'ENTRADA' in df_existente.columns:
                df_existente = df_existente.drop(columns=['ENTRADA'])
        else:
            df_existente = pd.DataFrame()

        # Cria DataFrame com os novos dados na coluna "ENTRADA"
        df_entrada = pd.DataFrame({'ENTRADA': nomes})

        # Garante que o DataFrame existente tenha o mesmo número de linhas
        max_len = max(len(df_existente), len(df_entrada))
        df_existente = df_existente.reindex(range(max_len)).reset_index(drop=True)
        df_entrada = df_entrada.reindex(range(max_len)).reset_index(drop=True)

        # Concatena a nova coluna "ENTRADA" com as colunas existentes
        df_final = pd.concat([df_entrada, df_existente], axis=1)

        # Salva os dados em uma planilha CSV
        df_final.to_csv(csv_path, index=False)
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

def compara_duplicados():
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    if not os.path.exists(csv_path):
        print(f"Arquivo '{csv_path}' não encontrado.")
        logging.error(f"Arquivo '{csv_path}' não encontrado.")
        return

    df = pd.read_csv(csv_path)

    # Garante que as colunas existam
    if 'ENTRADA' not in df.columns or 'SAIDA' not in df.columns:
        print("Colunas 'ENTRADA' e/ou 'SAIDA' não encontradas no arquivo.")
        logging.error("Colunas 'ENTRADA' e/ou 'SAIDA' não encontradas no arquivo.")
        return

    # Remove valores nulos e espaços extras
    entradas = set(df['ENTRADA'].dropna().astype(str).str.strip())
    saidas = set(df['SAIDA'].dropna().astype(str).str.strip())

    duplicados = sorted(entradas & saidas)

    # Preenche a coluna DUPLICADOS a partir da primeira linha com os nomes duplicados
    df['DUPLICADOS'] = ''
    for idx, nome in enumerate(duplicados):
        if idx < len(df):
            df.at[idx, 'DUPLICADOS'] = nome

    df.to_csv(csv_path, index=False)
    print(f"Coluna 'DUPLICADOS' atualizada em '{csv_path}'.")
    logging.info(f"Coluna 'DUPLICADOS' atualizada em '{csv_path}'.")

def codigo_duplicados():
    print("EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS")
    logging.info("Iniciando extração de códigos SISREG - DUPLICADOS")

    # Caminho do arquivo de duplicados
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    # Lê os nomes duplicados
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        logging.error(f"Arquivo não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if 'DUPLICADOS' not in df.columns:
        print("Coluna 'DUPLICADOS' não encontrada em internacoes_duplicadas.csv")
        logging.error("Coluna 'DUPLICADOS' não encontrada em internacoes_duplicadas.csv")
        return

    nomes_duplicados = df['DUPLICADOS'].dropna().astype(str).str.strip().tolist()
    if not nomes_duplicados:
        print("Nenhum nome duplicado encontrado para buscar códigos.")
        logging.info("Nenhum nome duplicado encontrado para buscar códigos.")
        return

    # Inicia o webdriver
    print("Iniciando o navegador Chrome...")
    logging.info("Iniciando o navegador Chrome para extração de códigos SISREG - DUPLICADOS")
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)

    codigos_por_nome = {}

    try:
        # Acessa o sistema SISREG
        print("Acessando o sistema SISREG...")
        logging.info("Acessando o sistema SISREG III")
        navegador.get("https://sisregiii.saude.gov.br")

        # Login
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
        )
        login_button.click()
        time.sleep(5)
        logging.info("Login realizado com sucesso no SISREG")

        # Clica no link "Saída/Permanência"
        saida_permanencia_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
        )
        saida_permanencia_link.click()
        time.sleep(5)
        # Troca para o iframe correto
        try:
            navegador.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
        except Exception:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
            except Exception:
                pass

        # Clica no botão PESQUISAR
        botao_pesquisar_saida = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        )
        botao_pesquisar_saida.click()
        time.sleep(5)

        # Extrai códigos dos nomes duplicados
        nomes_restantes = set([n.upper() for n in nomes_duplicados])
        while nomes_restantes:
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas_pacientes:
                nome_paciente = linha.find_element(By.XPATH, "./td[2]").text.strip().upper()
                if nome_paciente in nomes_restantes:
                    ficha_onclick = linha.get_attribute("onclick")
                    ficha = ficha_onclick.split("'")[1] if ficha_onclick else ""
                    codigos_por_nome[nome_paciente] = ficha
                    nomes_restantes.discard(nome_paciente)
            # Se todos encontrados, pare
            if not nomes_restantes:
                break
            # Próxima página
            try:
                botao_proxima_pagina = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if botao_proxima_pagina.is_displayed():
                    botao_proxima_pagina.click()
                    time.sleep(5)
                else:
                    break
            except NoSuchElementException:
                break

        print(f"Códigos extraídos para {len(codigos_por_nome)} pacientes duplicados.")
        logging.info(f"Códigos extraídos para {len(codigos_por_nome)} pacientes duplicados.")

    except Exception as e:
        print(f"Erro durante a execução de codigo_duplicados: {e}")
        logging.error(f"Erro durante a execução de codigo_duplicados: {e}")
    finally:
        navegador.quit()
        print("Navegador encerrado.")
        logging.info("Navegador encerrado após extração de códigos SISREG - DUPLICADOS")

    # Atualiza o arquivo CSV com a coluna CODIGO
    df['CODIGO'] = df['DUPLICADOS'].apply(
        lambda nome: codigos_por_nome.get(str(nome).strip().upper(), "") if pd.notna(nome) and str(nome).strip() else ""
    )
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Arquivo '{csv_path}' atualizado com a coluna 'CODIGO'.")
    logging.info(f"Arquivo '{csv_path}' atualizado com a coluna 'CODIGO'.")

