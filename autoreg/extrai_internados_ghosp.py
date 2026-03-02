# autoreg/extrai_internados_ghosp.py
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

setup_logging()

def linha_valida(linha):
    """Verifica se a linha possui dados válidos de internação."""
    # Verifica se a primeira coluna tem um número de 6 dígitos (Prontuário/ID)
    if re.match(r'^\d{6}$', str(linha[0])):
        # Verifica se a segunda ou a terceira coluna contém um nome válido
        if isinstance(linha[1], str) and linha[1].strip():
            return 'coluna_2'
        elif isinstance(linha[2], str) and linha[2].strip():
            return 'coluna_3'
    return False

def extrai_internados_ghosp():
    print("\n---===> EXTRAÇÃO DE INTERNADOS <===---")
    
    # Inicializa variáveis para garantir limpeza no finally
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
        driver.get(caminho_ghosp + ':4001/users/sign_in')
        
        # Definir tamanho da janela explicitamente (evita problemas com maximize no Docker/Kasm)
        print("Configurando tamanho da janela para 1920x1080...")
        driver.set_window_size(1920, 1080)
        time.sleep(2)

        # Realiza o login
        print("Tentando localizar o campo de e-mail...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(usuario_ghosp)
        
        print("Tentando localizar o campo de senha...")
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_password"))
        )
        senha_field.send_keys(senha_ghosp)
        
        print("Tentando localizar o botão de login...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar']"))
        )
        login_button.click()
        time.sleep(5)
        print("Login realizado com sucesso!")

        # Acessar a página de relatórios
        print("Acessando a página de relatórios...")
        driver.get(caminho_ghosp + ':4001/relatorios/rc001s')
        time.sleep(2)

        # Selecionar todas as opções no dropdown "Setor"
        print("Selecionando todos os setores...")
        setor_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "setor_id1"))
        ))
        for option in setor_select.options:
            # print(f"Selecionando o setor: {option.text}") # Comentado para reduzir spam no log
            setor_select.select_by_value(option.get_attribute('value'))
        print("Todos os setores selecionados!")

        # --- REMOVIDO: driver.maximize_window() ---
        # No lugar do zoom ou maximize, garantimos o tamanho da janela via set_window_size acima.
        time.sleep(1)

        # Selecionar o formato CSV
        print("Rolando até o dropdown de formato CSV...")
        formato_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tipo_arquivo"))
        )
        
        # Usa scroll via JS que é mais seguro que maximize_window
        driver.execute_script("arguments[0].scrollIntoView(true);", formato_dropdown)
        time.sleep(2)
        
        print("Selecionando o formato CSV...")
        formato_select = Select(formato_dropdown)
        formato_select.select_by_value("csv")
        print("Formato CSV selecionado!")

        # --- TIMESTAMP ANTES DO CLIQUE ---
        antes_download = time.time()

        # Clicar no botão "Imprimir"
        print("Tentando clicar no botão 'IMPRIMIR'...")
        imprimir_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "enviar_relatorio"))
        )
        imprimir_button.click()
        print("Relatório gerado! Aguardando download...")
        
        # --- REMOVIDO: driver.minimize_window() ---
        
        # Contador para timeout
        tentativas = 0
        max_tentativas = 60  # 5 minutos
        arquivo_recente = None

        # Aguardar até que um novo arquivo CSV seja baixado
        while tentativas < max_tentativas:
            novos_arquivos = []
            try:
                for arquivo in os.listdir(user_dir):
                    caminho_completo = os.path.join(user_dir, arquivo)
                    
                    # Filtra apenas CSVs (ignora .crdownload)
                    if (arquivo.lower().endswith('.csv') and 
                        os.path.isfile(caminho_completo)):
                        
                        # Verifica data de modificação e tamanho
                        if (os.path.getmtime(caminho_completo) > antes_download and
                            os.path.getsize(caminho_completo) > 0):
                            novos_arquivos.append(caminho_completo)
            except OSError:
                pass # Ignora erros momentâneos de leitura de disco

            if novos_arquivos:
                # Ordena pelo mais recente
                novos_arquivos.sort(key=os.path.getmtime, reverse=True)
                arquivo_recente = novos_arquivos[0]
                
                # Espera extra para garantir que o SO liberou o arquivo
                time.sleep(2)
                print(f"Arquivo CSV baixado encontrado: {os.path.basename(arquivo_recente)}")
                break
            
            print(f"Aguardando o download do arquivo CSV... (tentativa {tentativas+1}/{max_tentativas})")
            tentativas += 1
            time.sleep(5)

        if arquivo_recente:
            # Processa o arquivo encontrado
            try:
                print(f"Processando arquivo: {arquivo_recente}")
                # Carregar o arquivo CSV recém-baixado
                original_df = pd.read_csv(arquivo_recente, header=None, dtype=str)
                
                # Lista para armazenar os nomes extraídos
                nomes_extraidos = []
                
                # Percorre as linhas do DataFrame original
                for i, row in original_df.iterrows():
                    try:
                        coluna = linha_valida(row)
                        if coluna == 'coluna_2':
                            nome = row[1].strip()
                            nomes_extraidos.append(nome)
                        elif coluna == 'coluna_3':
                            nome = row[2].strip()
                            nomes_extraidos.append(nome)
                    except Exception:
                        continue # Pula linhas problemáticas

                # Converte a lista de nomes extraídos para um DataFrame
                nomes_df = pd.DataFrame(nomes_extraidos, columns=['Nome'])
                
                # Caminho para salvar o novo arquivo
                os.makedirs(user_dir, exist_ok=True)
                caminho_novo_arquivo = os.path.join(user_dir, 'internados_ghosp.csv')
                nomes_df.to_csv(caminho_novo_arquivo, index=False)
                print(f"✅ Sucesso! Nomes extraídos e salvos em {caminho_novo_arquivo}.")
                
            except Exception as e:
                print(f"Erro ao processar o arquivo CSV: {e}")
                print(traceback.format_exc())
        else:
            print("❌ Timeout: O arquivo não foi baixado após o tempo limite.")

    except Exception as e:
        print(f"❌ Ocorreu um erro crítico na extração: {e}")
        print(traceback.format_exc())
    
    finally:
        if driver:
            print("Fechando navegador...")
            driver.quit()

if __name__ == "__main__":
    extrai_internados_ghosp()
