"""
Módulo para tratamento de internações duplicadas no sistema SISREG III.
"""
import os
import time
import pandas as pd
import csv
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autoreg.ler_credenciais import ler_credenciais
from autoreg.chrome_options import get_chrome_options
from autoreg.logging import setup_logging

setup_logging()

def trata_duplicados():
    # Verifica o arquivo antes de qualquer coisa
    user_dir = os.path.expanduser('~/AutoReg')
    duplicadas_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')
    
    if not os.path.exists(duplicadas_path):
        print(f"⚠️ Arquivo {duplicadas_path} não encontrado. Pulando tratamento de duplicados.")
        logging.warning(f"Arquivo {duplicadas_path} não encontrado. Pulando tratamento.")
        return

    try:
        df = pd.read_csv(duplicadas_path)
        if df.empty or len(df) == 0:
            print("✅ Arquivo de duplicados está vazio. Nenhuma ação necessária.")
            logging.info("Arquivo de duplicados vazio.")
            return
    except Exception as e:
        print(f"Erro ao ler arquivo de duplicados: {e}")
        return

    # Se chegou aqui, tem dados para processar
    alta_duplicados(duplicadas_path)
    cod_inter_duplicado(duplicadas_path)
    interna_duplicados(duplicadas_path)

def alta_duplicados(duplicadas_path):
    print("\n--- INICIANDO ALTA DE DUPLICADOS ---")
    
    try:
        pacientes_duplicados_df = pd.read_csv(duplicadas_path, encoding='utf-8')
        if 'CODIGO' not in pacientes_duplicados_df.columns:
            print("Arquivo não possui coluna 'CODIGO'.")
            return
        
        # Filtra apenas quem tem código válido
        pacientes_validos = pacientes_duplicados_df[pacientes_duplicados_df['CODIGO'].notna() & (pacientes_duplicados_df['CODIGO'] != '')]
        
        if pacientes_validos.empty:
            print("Nenhum código válido para dar alta.")
            return

    except Exception as e:
        print(f"Erro na leitura inicial: {e}")
        return

    def iniciar_navegador():
        print("Iniciando o navegador Chrome...")
        logging.info("Iniciando o navegador Chrome para execução de alta de pacientes")
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
        # REMOVIDO: navegador.maximize_window()
        return navegador, wait

    def realizar_login(navegador, wait):
        print("Acessando o sistema SISREG...")
        navegador.get("https://sisregiii.saude.gov.br")
        
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)
        
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
        except TimeoutException:
            print("Erro ao carregar tabela de pacientes.")
            navegador.quit()
            return False
        return True

    navegador, wait = iniciar_navegador()
    if not realizar_login(navegador, wait):
        return

    motivo_alta = "5.1 ENCERRAMENTO ADMINISTRATIVO"

    try:
        for _, paciente in pacientes_validos.iterrows():
            ficha = paciente.get('CODIGO', None)
            ficha_str = str(ficha).split('.')[0]
            
            print(f"Processando alta para a ficha: {ficha_str}")
            logging.info(f"Processando alta para a ficha: {ficha_str}")
            
            try:
                navegador.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
                
                script_exists = navegador.execute_script("return typeof configFicha === 'function';")
                if not script_exists:
                    print("Função configFicha indisponível.")
                    continue

                navegador.execute_script(f"configFicha('{ficha_str}')")
                
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                except TimeoutException:
                    print("Botão 'Efetua Saída' não apareceu (ficha inexistente ou já com alta).")
                    continue

                try:
                    motivo_select = wait.until(EC.presence_of_element_located((By.NAME, "co_motivo")))
                    select = webdriver.support.ui.Select(motivo_select)
                    
                    found = False
                    for opcao in select.options:
                        if motivo_alta.upper() in opcao.text.upper():
                            select.select_by_visible_text(opcao.text)
                            found = True
                            break
                    
                    if not found:
                        print("Motivo de alta não encontrado.")
                        continue

                    botao_efetua_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                    botao_efetua_saida.click()
                    
                    WebDriverWait(navegador, 10).until(EC.alert_is_present())
                    navegador.switch_to.alert.accept()
                    WebDriverWait(navegador, 10).until(EC.alert_is_present())
                    navegador.switch_to.alert.accept()
                    print(f"Alta realizada para {ficha_str}")
                    
                except Exception as e:
                    print(f"Erro na interação de alta: {e}")

                time.sleep(2)
            except Exception as e:
                print(f"Erro ao processar ficha {ficha_str}: {e}")
                # Reinicia navegador se necessário
                try:
                    navegador.quit()
                except:
                    pass
                navegador, wait = iniciar_navegador()
                if not realizar_login(navegador, wait):
                    return

    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        if navegador:
            navegador.quit()

def cod_inter_duplicado(csv_path):
    print("\n--- EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS ---")
    
    df = pd.read_csv(csv_path)
    if 'DUPLICADOS' not in df.columns:
        print("Coluna 'DUPLICADOS' não encontrada.")
        return

    nomes_duplicados = df['DUPLICADOS'].dropna().astype(str).str.strip().tolist()
    if not nomes_duplicados:
        print("Nenhum nome duplicado para buscar.")
        return

    print("Iniciando navegador...")
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)
    codigos_por_nome = {}

    try:
        navegador.get("https://sisregiii.saude.gov.br")
        
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))).click()
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        
        print("Página de Internação acessada.")

        nomes_restantes = set([n.upper() for n in nomes_duplicados])
        
        # Paginação
        while nomes_restantes:
            linhas = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas:
                try:
                    nome = linha.find_element(By.XPATH, "./td[2]").text.strip().upper()
                    if nome in nomes_restantes:
                        ficha_onclick = linha.get_attribute("onclick")
                        if ficha_onclick:
                            ficha = ficha_onclick.split("'")[1]
                            codigos_por_nome[nome] = ficha
                            nomes_restantes.discard(nome)
                except:
                    continue
            
            if not nomes_restantes:
                break
                
            try:
                prox = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if prox.is_displayed():
                    prox.click()
                    time.sleep(3)
                else:
                    break
            except NoSuchElementException:
                break
        
        print(f"Códigos extraídos: {len(codigos_por_nome)}")

    except Exception as e:
        print(f"Erro na extração: {e}")
    finally:
        navegador.quit()

    # Atualiza CSV
    df['CODINTERNA'] = df['DUPLICADOS'].apply(
        lambda x: codigos_por_nome.get(str(x).strip().upper(), "") if pd.notna(x) else ""
    )
    
    # Reordena colunas
    cols = list(df.columns)
    if 'CODINTERNA' in cols:
        cols.remove('CODINTERNA')
    cols.insert(4, 'CODINTERNA')
    df = df[cols]
    
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print("Arquivo atualizado com CODINTERNA.")

def interna_duplicados(csv_path):
    print("\n--- INTERNAÇÃO DE DUPLICADOS ---")
    
    codigos = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            leitor = csv.reader(file)
            header = next(leitor)
            try:
                idx = header.index('CODINTERNA')
                for linha in leitor:
                    if len(linha) > idx and linha[idx].strip():
                        codigos.append(linha[idx].strip())
            except ValueError:
                print("Coluna CODINTERNA não encontrada.")
                return
    except Exception as e:
        print(f"Erro ao ler CSV para internar: {e}")
        return

    if not codigos:
        print("Nenhum código para internar.")
        return

    print("Iniciando navegador...")
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 10)

    try:
        navegador.get("https://sisregiii.saude.gov.br")
        # Login (simplificado)
        wait.until(EC.presence_of_element_located((By.NAME, "usuario"))).send_keys(ler_credenciais()[3])
        wait.until(EC.presence_of_element_located((By.NAME, "senha"))).send_keys(ler_credenciais()[4])
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))).click()
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))

        for ficha in codigos:
            try:
                print(f"Internando ficha {ficha}...")
                navegador.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
                
                navegador.execute_script(f"configFicha('{ficha}')")
                time.sleep(1)
                
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                data_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")))
                data_field.clear()
                data_field.send_keys(data_hoje)
                
                select_prof = Select(wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table[2]/tbody/tr[2]/td[2]/select"))))
                opts = select_prof.options[1:-1]
                if opts:
                    esc = random.choice(opts)
                    select_prof.select_by_visible_text(esc.text)
                
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]"))).click()
                
                try:
                    WebDriverWait(navegador, 5).until(EC.alert_is_present()).accept() # Confirma
                    time.sleep(1)
                    WebDriverWait(navegador, 5).until(EC.alert_is_present()).accept() # Confirma 2
                except:
                    pass
                
                print(f"Internação processada para {ficha}")
                time.sleep(5)
                
            except Exception as e:
                print(f"Erro na ficha {ficha}: {e}")
                continue

    except Exception as e:
        print(f"Erro geral internar: {e}")
    finally:
        navegador.quit()
        print("Fim do processo.")
