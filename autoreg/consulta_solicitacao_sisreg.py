import os
import csv
import time
import pandas as pd
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from autoreg.logging import setup_logging
import logging
import random
from datetime import datetime

setup_logging()

def consulta_solicitacao_sisreg():
    print("\n---===> CONSULTA SOLICITAÇÃO SISREG <===---")
        
    navegador = None
    
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)
    print("Acessando a página de Internação...\n")

    navegador.get("https://sisregiii.saude.gov.br")
    
    # Realiza o login
    print("Localizando campo de usuário...")
    usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
    print("Campo de usuário localizado.")

    print("Localizando campo de senha...")
    senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
    print("Campo de senha localizado.")

    print("Lendo credenciais do SISREG...")
    
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG']['usuariosol']
    senha_sisreg = config['SISREG']['senhasol']
    print("Credenciais lidas.")
    

    print("Preenchendo usuário...")
    usuario_field.send_keys(usuario_sisreg)
    print("Usuário preenchido.")
    
    print("Preenchendo senha...")
    senha_field.send_keys(senha_sisreg)
    print("Senha preenchida.")
    
    print("Aguardando antes de clicar no botão de login...")
    time.sleep(5)

    print("Localizando botão de login...")
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
    print("Botão de login localizado.")

    print("Clicando no botão de login...")
    login_button.click()
    print("Botão de login clicado.")
    
    time.sleep(5)
    print("Login realizado com sucesso!")
    logging.info("Login realizado com sucesso no SISREG")


    # Lê o arquivo CSV com as informações
    print("Lendo arquivo de solicitações...")
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'consulta_solicitacao_sisreg.csv')
    
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        logging.error(f"Arquivo não encontrado: {csv_path}")
        return
        
    # TESTA SE O CSV TEM DADOS
    df = pd.read_csv(csv_path)
    if df.empty:
        print("Arquivo CSV está vazio!")
        logging.error("Arquivo CSV está vazio")
        return
        
    try:
        for index, row in df.iterrows():
            try:
                print(f"\nProcessando registro {index + 1}/{len(df)}")
                print(f"Solicitação a ser processada: {row['solicitacao']}")

                # Navega até o menu de Consulta
                print("Acessando menu de Consulta...")
                logging.info("Tentando acessar menu de Consulta")
                
                # Extrai o número da solicitação
                solicitacao = str(row['solicitacao']).strip()
                print(f"Número da solicitação extraído: {solicitacao}")
                logging.info(f"Processando solicitação número: {solicitacao}")
                
                # Navega pelo menu
                print("Localizando menu principal...")
                menu_principal = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="barraMenu"]/ul/li[3]/a')))
                
                # Usa Actions para fazer hover no menu principal
                print("Movendo mouse para menu principal...")
                actions = ActionChains(navegador)
                actions.move_to_element(menu_principal).perform()
                time.sleep(1)  # Espera o submenu aparecer
                
                # Clica no submenu
                print("Clicando no submenu...")
                submenu = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="barraMenu"]/ul/li[3]/ul/li[1]/a')))
                submenu.click()
                print("Submenu clicado com sucesso!")
                time.sleep(1)  # Espera a página carregar
                
                # Muda para o frame principal
                print("Mudando para o frame principal...")
                navegador.switch_to.frame("f_principal")
                print("Mudança de frame realizada!")

                # Localiza o campo de solicitação
                print("Localizando campo de solicitação...")
                campo_solicitacao = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main_page"]/form/center/table/tbody/tr[2]/td[2]/input')))
                print("Campo de solicitação localizado!")

                # Insere o número da solicitação
                print(f"Inserindo número da solicitação: {solicitacao}")
                campo_solicitacao.clear()  # Limpa o campo primeiro
                campo_solicitacao.send_keys(solicitacao)
                print("Número da solicitação inserido!")
                time.sleep(2)  # Pequena pausa após inserir

                # Localiza e clica no botão de consulta
                print("Localizando botão de consulta...")
                botao_consulta = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main_page"]/form/center/table/tbody/tr[12]/td/input[1]')))
                print("Botão de consulta localizado!")
                
                print("Clicando no botão de consulta...")
                botao_consulta.click()
                print("Consulta iniciada!")
                time.sleep(1)  # Espera a consulta carregar

                # Verifica o status diretamente na tabela de resultados
                print("Verificando status de autorização...")
                try:
                    # Tenta localizar o elemento de status na tabela
                    elemento_status = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main_page"]/form/center[2]/table/tbody/tr[3]/td[7]')))
                    status = elemento_status.text.strip()
                    
                    print(f"Status encontrado: {status}")
                    
                    # Verifica o status
                    if status == "APROVADA":
                        print("Solicitação AUTORIZADA!")
                        df.at[index, 'autorizacao'] = 'OK'
                    elif status == "PENDENTE":
                        print("Solicitação PENDENTE!")
                        df.at[index, 'autorizacao'] = 'Autorizar'
                    else:
                        print(f"Status desconhecido: {status}")
                        df.at[index, 'autorizacao'] = 'Verificar'
                except Exception as e:
                    print(f"Erro ao verificar status: {str(e)}")
                    df.at[index, 'autorizacao'] = 'Erro'
                    logging.error(f"Erro ao verificar status da solicitação {solicitacao}: {str(e)}")
                
                # Volta para o frame principal para a próxima iteração
                navegador.switch_to.default_content()
                
                # Salva o DataFrame atualizado a cada iteração
                print("Salvando resultados no CSV...")
                df.to_csv(csv_path, index=False)
                print("Resultados salvos!")
                
                time.sleep(1)  # Pequena pausa antes da próxima solicitação
                
            except Exception as e:
                print(f"Erro ao processar registro {index + 1}: {str(e)}")
                logging.error(f"Erro ao processar registro {index + 1}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Erro geral durante o processamento: {str(e)}")
        logging.error(f"Erro geral durante o processamento: {str(e)}")
        
    finally:
        if navegador:
            print("\nFechando o navegador...")
            navegador.quit()
            print("Navegador fechado.")

    