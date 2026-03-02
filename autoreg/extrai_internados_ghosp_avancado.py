import os
import time
import pandas as pd
import traceback
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.chrome_options import get_chrome_options
from datetime import datetime
import logging

def extrai_internados_ghosp_avancado():
    print("\n---===> CONSULTA PERMANENCIA DE INTERNADOS NO GHOSP <===---")
    
    driver = None 
    
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()
        
        # Caminho para salvar o novo arquivo baixado
        user_dir = os.path.expanduser('~/AutoReg')
        print(f"Diretório de download configurado: {user_dir}")
        
        # Inicializa o navegador
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        print("Iniciando o Chromedriver...")

        # Acesse a página de login do G-HOSP
        driver.get(caminho_ghosp + ':4002/users/sign_in')
        
        # Definir tamanho da janela explicitamente (evita problemas com maximize no Docker/Kasm)
        print("Configurando tamanho da janela para 1920x1080...")
        driver.set_window_size(1920, 1080)
        time.sleep(2)

        # Realiza o login
        print("Localizando campo de e-mail...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(usuario_ghosp)

        # Localiza e preenche o campo de senha (//*[@id="password"])
        print("Localizando campo de senha...")
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        senha_field.send_keys(senha_ghosp)

        # Localiza e clica no botão de login (//*[@id="new_user"]/div/input)
        print("Localizando botão de login...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
        )
        login_button.click()
        time.sleep(5)
        print("Login realizado com sucesso!")

        # Loop para processar cada linha do CSV
        csv_path = os.path.join(user_dir, 'internados_sisreg.csv')
        if not os.path.exists(csv_path):
            print(f"Erro: Arquivo {csv_path} não encontrado.")
            return

        df = pd.read_csv(csv_path)
        if 'erro' not in df.columns:
            df['erro'] = ""
        if 'RA' not in df.columns:
            df['RA'] = ""

        print(f"\nIniciando processamento de {len(df)} pacientes...")

        for index, row in df.iterrows():
            nome_csv = str(row['Nome']).strip().upper()
            # Garante que o CNS seja tratado como string e sem ".0" ao final
            cns_csv = str(row['cns']).strip() if pd.notna(row['cns']) else ""
            if cns_csv.endswith('.0'):
                cns_csv = cns_csv[:-2]
            
            print(f"\n[{index+1}/{len(df)}] Processando: {nome_csv}")
            
            found = False
            
            try:
                # 1. Tentar busca por CNS
                if cns_csv:
                    print(f"Buscando por CNS: {cns_csv}")
                    driver.get(caminho_ghosp + ':4002/prontuarios')
                    
                    cns_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "cns"))
                    )
                    cns_input.clear()
                    cns_input.send_keys(cns_csv)
                    
                    # Clica no botão Procurar
                    botao_procurar = driver.find_element(By.XPATH, '//input[@type="submit" and @value="Procurar"]')
                    botao_procurar.click()
                    time.sleep(3)
                    
                    # Verifica se abriu a div "paciente"
                    paciente_divs = driver.find_elements(By.ID, "paciente")
                    if paciente_divs:
                        nome_ghosp = paciente_divs[0].find_element(By.XPATH, './/h2').text.strip().upper()
                        if nome_csv in nome_ghosp or nome_ghosp in nome_csv: # Comparação flexível para nomes
                            found = True
                            print(f"Sucesso: Paciente localizado por CNS ({nome_ghosp})")
                
                # 2. Tentar busca por Nome se não encontrou por CNS
                if not found:
                    print(f"Tentando busca por Nome: {nome_csv}")
                    driver.get(caminho_ghosp + ':4002/prontuarios')
                    
                    nome_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "nome"))
                    )
                    nome_input.clear()
                    nome_input.send_keys(nome_csv)
                    
                    botao_procurar = driver.find_element(By.XPATH, '//input[@type="submit" and @value="Procurar"]')
                    botao_procurar.click()
                    time.sleep(3)
                    
                    paciente_divs = driver.find_elements(By.ID, "paciente")
                    if paciente_divs:
                        nome_ghosp = paciente_divs[0].find_element(By.XPATH, './/h2').text.strip().upper()
                        if nome_csv in nome_ghosp or nome_ghosp in nome_csv:
                            found = True
                            print(f"Sucesso: Paciente localizado por Nome ({nome_ghosp})")
                
                # 3. Se encontrou o paciente, extrair o RA mais recente
                if found:
                    try:
                        print("Extraindo RA mais recente...")
                        # Aguarda a div principal de procedimentos
                        container = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "container-procedimentos"))
                        )
                        
                        # Localiza todos os itens de RA
                        ra_items = container.find_elements(By.CLASS_NAME, "RAitem")
                        
                        ras_encontradas = []
                        
                        for item in ra_items:
                            try:
                                # Extrai o número do RA do valor do checkbox
                                ra_checkbox = item.find_element(By.CLASS_NAME, "ra")
                                ra_numero = ra_checkbox.get_attribute("value")
                                
                                # Extrai a data e hora do span ml5
                                span_data = item.find_element(By.CLASS_NAME, "ml5").text
                                # Limpa espaços e quebras de linha para extrair data dd/mm/yyyy hh:mm
                                data_texto = span_data.replace('\n', ' ').strip()
                                # Normaliza espaços duplos e tenta extrair os números
                                # Exemplo: "24/02/2026 16:  10" -> "24/02/2026 16:10"
                                data_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*(\d{2}):\s*(\d{2})', data_texto)
                                
                                if data_match:
                                    data_str = f"{data_match.group(1)} {data_match.group(2)}:{data_match.group(3)}"
                                    data_obj = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                                    
                                    ras_encontradas.append({
                                        'ra': ra_numero,
                                        'data': data_obj
                                    })
                            except Exception:
                                continue
                        
                        if ras_encontradas:
                            # Ordena pela data mais recente (decrescente)
                            ras_encontradas.sort(key=lambda x: x['data'], reverse=True)
                            ra_recente = ras_encontradas[0]['ra']
                            df.at[index, 'RA'] = ra_recente
                            print(f"RA mais recente identificado: {ra_recente} ({ras_encontradas[0]['data']})")
                        else:
                            print("Aviso: Nenhuma RA válida encontrada na lista.")
                            
                    except Exception as e:
                        print(f"Aviso: Falha ao extrair dados de RA: {str(e)}")
                
                if not found:
                    msg_erro = "Paciente não encontrado no GHOSP ou Homônimos, revisar manualmente"
                    df.at[index, 'erro'] = msg_erro
                    print(f"Aviso: {msg_erro}")
                
            except Exception as e:
                print(f"Erro ao processar linha {index+1}: {str(e)}")
                df.at[index, 'erro'] = f"Erro técnico: {str(e)}"

            # Salva o progresso a cada linha
            df.to_csv(csv_path, index=False)

        # Atualiza arquivo final
        df.to_csv(csv_path, index=False)
        print(f"\nProcessamento concluído. CSV atualizado em: {csv_path}")
        
        driver.quit()
    
    except Exception as e:
        print(f"Erro ao extrair internados do GHOSP: {str(e)}")
        logging.error(f"Erro ao extrair internados do GHOSP: {str(e)}")
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

        