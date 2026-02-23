import os
import time
import pandas as pd
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
import logging

setup_logging()

def atualiza_restos():
    # 1. Atualiza o arquivo CSV localmente primeiro
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'restos.csv')
    
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if df.shape[0] > 0:
                # Define o motivo padrão para os restos
                df.iloc[:, 1] = 'ENCERRAMENTO ADMINISTRATIVO' 
                df.to_csv(csv_path, index=False)
                print(f"Coluna atualizada e dados salvos em '{csv_path}'.")
            else:
                print("Arquivo restos.csv está vazio.")
                return # Se está vazio, não precisa abrir navegador
        else:
            print(f"Arquivo {csv_path} não encontrado.")
            return
    except Exception as e:
        print(f"Erro ao manipular CSV inicial: {e}")
        return

    # Funções internas de navegação
    def iniciar_navegador():
        print("Iniciando o navegador Chrome...")
        logging.info("Iniciando o navegador Chrome para execução de alta de restos")
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        
        # --- REMOVIDO: navegador.maximize_window() ---
        
        return navegador, wait

    def realizar_login(navegador, wait):
        print("Acessando o sistema SISREG...")
        logging.info("Acessando o sistema SISREG III para login")
        navegador.get("https://sisregiii.saude.gov.br")
        
        print("Tentando localizar o campo de usuário...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)
        
        print("Tentando localizar o botão de login...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
        print("Login realizado e navegação para página de Saída/Permanência concluída!")
        
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        
        try:
            botao_pesquisar_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']")))
            botao_pesquisar_saida.click()
            wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")))
            print("Tabela de pacientes carregada!")
        except TimeoutException as e:
            print(f"Erro ao carregar tabela: {e}")
            navegador.quit()
            return False
        return True

    # Início do Fluxo Principal da Função
    navegador, wait = iniciar_navegador()
    if not realizar_login(navegador, wait):
        return

    atualizados_path = os.path.join(user_dir, 'restos.csv')
    
    try:
        pacientes_atualizados_df = pd.read_csv(atualizados_path, encoding='utf-8')
        
        for _, paciente in pacientes_atualizados_df.iterrows():
            try:
                nome_paciente = paciente.get('Nome', None)
                motivo_alta = paciente.get('Motivo da Alta', None) # Já deve ser 'ENCERRAMENTO ADMINISTRATIVO'
                ficha = paciente.get('Número da Ficha', None)

                if nome_paciente is None or motivo_alta is None or ficha is None:
                    print("Dados insuficientes, pulando...")
                    continue

                ficha = str(ficha).split('.')[0]
                print(f"Processando alta (Restos) para: {nome_paciente}")
                logging.info(f"Processando alta (Restos) para: {nome_paciente}")
                
                dar_alta(navegador, wait, motivo_alta, ficha)
                time.sleep(2)
                
            except Exception as e:
                print(f"Erro no loop de pacientes: {e}")
                logging.error(f"Erro no loop de pacientes: {e}")
                # Reinicia se necessário
                try:
                    navegador.quit()
                except:
                    pass
                navegador, wait = iniciar_navegador()
                if not realizar_login(navegador, wait):
                    return

    except Exception as e:
        print(f"Erro geral na execução de restos: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
            print("Navegador fechado.")

def dar_alta(navegador, wait, motivo_alta, ficha):
    # Lógica de dar alta
    navegador.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    
    script_exists = navegador.execute_script("return typeof configFicha === 'function';")
    if not script_exists:
        print("Função configFicha indisponível.")
        return

    navegador.execute_script(f"configFicha('{ficha}')")

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
    except TimeoutException:
        print(f"Timeout ficha {ficha}. Talvez já tenha alta.")
        return

    try:
        motivo_select = wait.until(EC.presence_of_element_located((By.NAME, "co_motivo")))
        select = webdriver.support.ui.Select(motivo_select)
        
        # Mapeamento simplificado para Restos (focando em Encerramento Administrativo)
        motivo_mapping = {
            'ENCERRAMENTO ADMINISTRATIVO': '5.1 ENCERRAMENTO ADMINISTRATIVO'
        }
        
        motivo_final = motivo_mapping.get(motivo_alta, motivo_alta) # Tenta mapear, se não, usa o original
        
        encontrou = False
        for opcao in select.options:
            if motivo_final.upper() in opcao.text.upper():
                select.select_by_visible_text(opcao.text)
                encontrou = True
                break
        
        if not encontrou:
            print(f"Motivo '{motivo_final}' não encontrado no select.")
            return

        botao_efetua_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
        botao_efetua_saida.click()
        
        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        print(f"Alta realizada para ficha {ficha}.")
        
    except Exception as e:
        print(f"Erro ao efetivar alta: {e}")
