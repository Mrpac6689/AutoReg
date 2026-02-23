
"""
Módulo para tratamento de internações duplicadas no sistema SISREG III.
Este módulo automatiza o processo de:
1. Dar alta administrativa em internações duplicadas.
2. Extrair códigos SISREG de pacientes duplicados.
3. Realizar nova internação para os casos duplicados.
Funções principais:
- trata_duplicados(): Executa o fluxo completo de tratamento de duplicados.
- alta_duplicados(): Automatiza o processo de alta administrativa para fichas duplicadas, utilizando Selenium para interação com o SISREG.
- cod_inter_duplicado(): Extrai os códigos SISREG das internações duplicadas e atualiza o arquivo CSV correspondente.
- interna_duplicados(): Realiza a internação automática dos pacientes duplicados, preenchendo os campos necessários e lidando com pop-ups de confirmação.
Requisitos:
- O arquivo 'internacoes_duplicadas.csv' deve estar presente no diretório '~/AutoReg' com as colunas apropriadas.
- As funções dependem de credenciais de acesso ao SISREG e de configurações específicas do navegador Chrome.
- Utiliza Selenium WebDriver para automação de navegador.
Logs e mensagens de status são gerados durante todo o processo para facilitar o acompanhamento e depuração.
Exceções e erros são tratados para garantir a continuidade do processo, mesmo em caso de falhas pontuais.
Autor: [Seu Nome ou Equipe]
Data: [Data de criação ou modificação]
"""

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autoreg.ler_credenciais import ler_credenciais
from autoreg.chrome_options import get_chrome_options
from autoreg.logging import setup_logging
from autoreg.executa_alta import dar_alta   
import logging
import csv
from datetime import datetime
from selenium.webdriver.support.ui import Select
import random
setup_logging()

def trata_duplicados():
    alta_duplicados()
    cod_inter_duplicado()
    interna_duplicados()

def alta_duplicados():
    def iniciar_navegador():
        print("Iniciando o navegador Chrome...")
        logging.info("Iniciando o navegador Chrome para execução de alta de pacientes")
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        navegador.maximize_window()
        return navegador, wait

    def realizar_login(navegador, wait):
        print("Acessando o sistema SISREG...")
        logging.info("Acessando o sistema SISREG III para login")
        navegador.get("https://sisregiii.saude.gov.br")

        print("Tentando localizar o campo de usuário...")
        logging.info("Tentando localizar o campo de usuário no SISREG")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)

        print("Tentando localizar o botão de login...")
        logging.info("Tentando localizar o botão de login no SISREG")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
        print("Login realizado e navegação para página de Saída/Permanência concluída!")
        logging.info("Login realizado com sucesso e navegação para página de Saída/Permanência concluída")

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Foco alterado para o iframe com sucesso!")
        logging.info("Foco alterado para o iframe principal do SISREG")
        
        try:
            botao_pesquisar_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']")))
            botao_pesquisar_saida.click()
            print("Botão PESQUISAR clicado com sucesso!")
            logging.info("Botão PESQUISAR clicado com sucesso na página de Saída/Permanência")
            wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")))
            print("Tabela de pacientes carregada!")
            logging.info("Tabela de pacientes carregada com sucesso na página de Saída/Permanência")
        except TimeoutException as e:
            print(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
            logging.error(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
            navegador.quit()
            return False
        return True

    # Iniciar navegador e realizar login inicial
    navegador, wait = iniciar_navegador()
    if not realizar_login(navegador, wait):
        return

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    duplicadas_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    motivo_alta = "5.1 ENCERRAMENTO ADMINISTRATIVO"

    try:
        pacientes_duplicados_df = pd.read_csv(duplicadas_path, encoding='utf-8')
        if 'CODIGO' not in pacientes_duplicados_df.columns:
            print("Arquivo não possui coluna 'CODIGO'.")
            logging.error("Arquivo não possui coluna 'CODIGO'.")
            navegador.quit()
            return

        for _, paciente in pacientes_duplicados_df.iterrows():
            ficha = paciente.get('CODIGO', None)
            if pd.isna(ficha) or str(ficha).strip() == '':
                continue

            ficha_str = str(ficha).split('.')[0]
            print(f"Processando alta para a ficha: {ficha_str}")
            logging.info(f"Processando alta para a ficha: {ficha_str}")

            try:
                print(f"Executando a função configFicha para a ficha: {ficha_str}")
                logging.info(f"Executando a função configFicha para a ficha: {ficha_str}")

                navegador.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
                
                # Verifica se a função configFicha está disponível
                script_exists = navegador.execute_script("return typeof configFicha === 'function';")
                if not script_exists:
                    print("Função configFicha não está disponível no contexto atual!")
                    logging.error("Função configFicha não está disponível no contexto atual!")
                    print(navegador.page_source)  # Debug: imprime o HTML do frame
                    logging.debug("HTML do frame atual: " + navegador.page_source)
                    continue

                navegador.execute_script(f"configFicha('{ficha_str}')")
                
                # Aguarda o botão "Efetua Saída" aparecer, indicando que a ficha foi carregada
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                except TimeoutException:
                    print("Timeout esperando o botão 'Efetua Saída'. Verifique se a ficha existe ou se já foi dada alta.")
                    logging.error("Timeout esperando o botão 'Efetua Saída'. Verifique se a ficha existe ou se já foi dada alta.")
                    print(navegador.page_source)  # Debug: imprime o HTML do frame
                    logging.debug("HTML do frame atual: " + navegador.page_source)
                    continue

                print("Aguarda o carregamento da página após a execução do script configFicha.")
                logging.info("Aguardando o carregamento da página após a execução do script configFicha.")

                try:
                    print(f"Selecionando o motivo de alta: {motivo_alta}")
                    logging.info(f"Selecionando o motivo de alta: {motivo_alta}")
                    motivo_select = wait.until(EC.presence_of_element_located((By.NAME, "co_motivo")))
                    select = webdriver.support.ui.Select(motivo_select)
                    # Não há mapeamento, sempre será '5.1 ENCERRAMENTO ADMINISTRATIVO'
                    for opcao in select.options:
                        if motivo_alta.upper() in opcao.text.upper():
                            select.select_by_visible_text(opcao.text)
                            print(f"Motivo de alta '{motivo_alta}' selecionado com sucesso!")
                            logging.info(f"Motivo de alta '{motivo_alta}' selecionado com sucesso!")
                            break
                    else:
                        print("Motivo de alta não encontrado nas opções.")
                        logging.warning(f"Motivo de alta '{motivo_alta}' não encontrado nas opções.")
                        continue
                except TimeoutException:
                    print("Erro ao tentar localizar o campo de motivo de alta.")
                    logging.error("Erro ao tentar localizar o campo de motivo de alta.")
                    continue

                try:
                    print("Tentando localizar o botão 'Efetua Saída'...")
                    logging.info("Tentando localizar o botão 'Efetua Saída' no SISREG")
                    botao_efetua_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                    botao_efetua_saida.click()
                    print("Botão 'Efetua Saída' clicado com sucesso!")
                    logging.info("Botão 'Efetua Saída' clicado com sucesso no SISREG")

                    WebDriverWait(navegador, 10).until(EC.alert_is_present())
                    navegador.switch_to.alert.accept()
                    print("Primeiro pop-up confirmado!")
                    logging.info("Primeiro pop-up confirmado com sucesso após clicar em 'Efetua Saída'")

                    WebDriverWait(navegador, 10).until(EC.alert_is_present())
                    navegador.switch_to.alert.accept()
                    print("Segundo pop-up confirmado!")
                    logging.info("Segundo pop-up confirmado com sucesso após clicar em 'Efetua Saída'")
                except TimeoutException:
                    print("Erro ao tentar localizar o botão 'Efetua Saída' ou ao confirmar os pop-ups.")
                    logging.error("Erro ao tentar localizar o botão 'Efetua Saída' ou ao confirmar os pop-ups.")
                    print(navegador.page_source)  # Debug: imprime o HTML do frame
                    logging.debug("HTML do frame atual: " + navegador.page_source)
                except ElementClickInterceptedException as e:
                    print(f"Erro ao clicar no botão 'Efetua Saída': {e}")
                    logging.error(f"Erro ao clicar no botão 'Efetua Saída': {e}")
                    print(navegador.page_source)
                    logging.debug("HTML do frame atual: " + navegador.page_source)
                except Exception as e:
                    print(f"Erro inesperado: {e}")
                    logging.error(f"Erro inesperado: {e}")
                    print(navegador.page_source)  # Debug: imprime o HTML do frame
                    logging.debug("HTML do frame atual: " + navegador.page_source)

                time.sleep(2)
            except Exception as e:
                print(f"Erro ao processar alta para a ficha {ficha_str}: {e}")
                logging.error(f"Erro ao processar alta para a ficha {ficha_str}: {e}")
                navegador.quit()
                navegador, wait = iniciar_navegador()
                if not realizar_login(navegador, wait):
                    return

    except Exception as e:
        print(f"Erro geral na execução: {e}")
        logging.error(f"Erro geral na execução: {e}")

    navegador.quit()
    print("\nProcesso de saída concluído para todos os pacientes.")
    logging.info("Processo de saída concluído para todos os pacientes.")

def cod_inter_duplicado():
    print("EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS")
    logging.info("Iniciando extração de códigos SISREG - DUPLICADOS")

    # Caminho do arquivo de duplicados
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    # Lê o arquivo de duplicados
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

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Internação...\n")
        logging.info("Login realizado e navegação para página de Internação...\n")

        # Extrai códigos dos nomes duplicados
        nomes_restantes = set([n.upper() for n in nomes_duplicados])
        while nomes_restantes:
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas_pacientes:
                try:
                    nome_paciente = linha.find_element(By.XPATH, "./td[2]").text.strip().upper()
                    if nome_paciente in nomes_restantes:
                        ficha_onclick = linha.get_attribute("onclick")
                        ficha = ficha_onclick.split("'")[1] if ficha_onclick else ""
                        codigos_por_nome[nome_paciente] = ficha
                        nomes_restantes.discard(nome_paciente)
                except Exception:
                    continue
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
        print(f"Erro durante a execução de cod_inter_duplicado: {e}")
        logging.error(f"Erro durante a execução de cod_inter_duplicado: {e}")
    finally:
        navegador.quit()
        print("Navegador encerrado.")
        logging.info("Navegador encerrado após extração de códigos SISREG - DUPLICADOS")

    # Atualiza o arquivo CSV com a coluna CODINTERNA (quinta coluna)
    # Mantém o conteúdo anterior, apenas adiciona/atualiza a coluna CODINTERNA
    df['CODINTERNA'] = df['DUPLICADOS'].apply(
        lambda nome: codigos_por_nome.get(str(nome).strip().upper(), "") if pd.notna(nome) and str(nome).strip() else ""
    )
    # Garante que a coluna CODINTERNA seja a quinta coluna
    cols = list(df.columns)
    if 'CODINTERNA' in cols:
        cols.remove('CODINTERNA')
    # Insere na posição 4 (quinta coluna, índice 4)
    cols.insert(4, 'CODINTERNA')
    df = df[cols]

    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Arquivo '{csv_path}' atualizado com a coluna 'CODINTERNA'.")
    logging.info(f"Arquivo '{csv_path}' atualizado com a coluna 'CODINTERNA'.")

def interna_duplicados():

    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        logging.error(f"Arquivo não encontrado: {csv_path}")
        return

    # Lê os códigos da quinta coluna (CODINTERNA)
    codigos = []
    with open(csv_path, mode='r', encoding='utf-8') as file:
        leitor_csv = csv.reader(file)
        header = next(leitor_csv)
        try:
            idx_cod = header.index('CODINTERNA')
        except ValueError:
            print("Coluna 'CODINTERNA' não encontrada no arquivo.")
            logging.error("Coluna 'CODINTERNA' não encontrada no arquivo.")
            return
        for linha in leitor_csv:
            codigo = linha[idx_cod].strip()
            if codigo:
                codigos.append(codigo)

    if not codigos:
        print("Nenhum código encontrado na coluna 'CODINTERNA'.")
        logging.info("Nenhum código encontrado na coluna 'CODINTERNA'.")
        return

    navegador = None
    try:
        print("INICIANDO PROCESSO DE INTERNAÇÃO DE DUPLICADOS\n")
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 10)
        navegador.get("https://sisregiii.saude.gov.br")

        # Login
        print("Realizando login no SISREG...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Internação...\n")

        for ficha in codigos:
            try:
                print(f"Acessando a página de Internação para a ficha {ficha}...\n")
                navegador.switch_to.default_content()
                wait = WebDriverWait(navegador, 10)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
                navegador.execute_script(f"configFicha('{ficha}')")
                print(f"Executando a função configFicha para a ficha: {ficha}\n")
                time.sleep(1)

                # Data de internação: dia corrente
                data_internacao_str = datetime.now().strftime("%d/%m/%Y")
                print(f"Data de internação utilizada: {data_internacao_str}\n")

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
                print(f"O profissional selecionado foi: {opcao_aleatoria.text}\n")

                # Clica no botão "Internar"
                botao_internar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]")))
                botao_internar.click()

                # Lidar com popups de confirmação
                try:
                    WebDriverWait(navegador, 10).until(EC.alert_is_present())
                    alert = navegador.switch_to.alert
                    print(f"Popup detectado: {alert.text}\n")
                    alert.accept()
                    print("✔️ Botão 'OK' pressionado com sucesso.\n")
                    time.sleep(2)
                except TimeoutException:
                    print("⚠️ Nenhum popup encontrado. Prosseguindo com a operação.\n")
                except Exception as e:
                    print(f"❌ Erro ao interagir com o popup: {e}\n")

                try:
                    WebDriverWait(navegador, 10).until(EC.alert_is_present())
                    segundo_alert = navegador.switch_to.alert
                    print(f"Segundo alerta confirmado: {segundo_alert.text}\n")
                    segundo_alert.accept()
                except TimeoutException:
                    print("Nenhum segundo alerta apareceu. Prosseguindo com a operação.\n")
                except Exception as e:
                    print(f"Erro ao lidar com o segundo alerta: {e}\n")

                # Verifica se há erro de sistema na tela
                try:
                    navegador.find_element(By.XPATH, "//div[contains(text(), 'Erro de Sistema')]")
                    print("⚠️ Erro de Sistema detectado. Processo interrompido.\n")
                except NoSuchElementException:
                    print("✔️ Nenhum erro de sistema detectado. Internação realizada com sucesso.\n")
                    time.sleep(10)
            except Exception as e:
                print(f"Erro ao processar a ficha {ficha}: {e}\n")
                logging.error(f"Erro ao processar a ficha {ficha}: {e}")
                continue

    except TimeoutException:
        print("⚠️ Tempo limite excedido ao tentar acessar a página de internação. Verifique a conexão com a internet e tente novamente.\n")
        logging.error("Tempo limite excedido ao tentar acessar a página de internação.")
    except Exception as e:
        print(f"Erro inesperado: {e}\n")
        logging.error(f"Erro inesperado: {e}")
    finally:
        if navegador:
            navegador.quit()
        print("Processo de internação concluído.\n")
        logging.info("Processo de internação concluído.")
        print("Todos os códigos de internação duplicados foram processados. Verifique o arquivo 'internacoes_duplicadas.csv' no diretório ~/AutoReg.\n")
        logging.info("Todos os códigos de internação duplicados foram processados. Verifique o arquivo 'internacoes_duplicadas.csv' no diretório ~/AutoReg.")
