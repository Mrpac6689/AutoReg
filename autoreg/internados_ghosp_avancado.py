# autoreg/extrai_internados_ghosp.py
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.chrome_options import get_chrome_options
import re

setup_logging()

def linha_valida(linha):
    # Verifica se a primeira coluna tem um número de 6 dígitos
    if re.match(r'^\d{6}$', str(linha[0])):
        # Verifica se a segunda ou a terceira coluna contém um nome válido
        if isinstance(linha[1], str) and linha[1].strip():
            return 'coluna_2'
        elif isinstance(linha[2], str) and linha[2].strip():
            return 'coluna_3'
    return False


def internados_ghosp_avancado():
    print("\n---===> EXTRAÇÃO DE INTERNADOS <===---")
    usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()

    # Caminho para salvar o novo arquivo baixado
    user_dir = os.path.expanduser('~/AutoReg')
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
    print(f"Diretório de download configurado: {user_dir}")

    #download_path = os.path.join(user_dir, 'ghosp_download.csv')
    #print(f"Pasta de Downloads: {download_path}")
    
    # Captura timestamp antes do download para identificar arquivos novos
    antes_download = time.time()

    # Inicializa o navegador (Chrome neste caso) usando o serviço
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")
    
    # Minimizando a janela após iniciar o Chrome
    #driver.minimize_window()

    # Acesse a página de login do G-HOSP
    driver.get(caminho_ghosp + ':4001/users/sign_in')

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

        # Acessar a página de relatórios
        print("Acessando a página de relatórios...")
        driver.get(caminho_ghosp + ':4001/relatorios/rc001s')
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

        # Contador para timeout
        tentativas = 0
        max_tentativas = 60  # 5 minutos (5 segundos * 60)
        arquivo_recente = None

        # Aguardar até que um novo arquivo CSV seja baixado
        while tentativas < max_tentativas:
            # Procura por arquivos CSV no diretório que foram criados após o início do download
            novos_arquivos = []
            for arquivo in os.listdir(user_dir):
                caminho_completo = os.path.join(user_dir, arquivo)
                if (arquivo.lower().endswith('.csv') and 
                    os.path.isfile(caminho_completo) and 
                    os.path.getmtime(caminho_completo) > antes_download and
                    os.path.getsize(caminho_completo) > 0):
                    novos_arquivos.append(caminho_completo)
            
            if novos_arquivos:
                # Ordena pelo mais recente
                novos_arquivos.sort(key=os.path.getmtime, reverse=True)
                arquivo_recente = novos_arquivos[0]
                print(f"Arquivo CSV baixado encontrado: {os.path.basename(arquivo_recente)}")
                break
            
            print(f"Aguardando o download do arquivo CSV... (tentativa {tentativas+1}/{max_tentativas})")
            tentativas += 1
            time.sleep(5)

        if arquivo_recente:
            # Processa o arquivo encontrado
            try:
                # Carregar o arquivo CSV recém-baixado
                original_df = pd.read_csv(arquivo_recente, header=None, dtype=str)
                # Chamar a função para extrair os nomes do CSV recém-baixado
                
                

                    # Lista para armazenar os dados extraídos
                dados_extraidos = []
                
                # Percorre as linhas do DataFrame original
                for i, row in original_df.iterrows():
                    # Verifica se a primeira coluna contém um número de internação (6 dígitos)
                    if re.match(r'^\d{6}$', str(row[0])):
                        internacao = str(row[0]).strip()
                        nome = row[1].strip() if pd.notna(row[1]) and row[1].strip() else row[2].strip()
                        # Procura a data de internação (formato dd/mm/yyyy)
                        data = None
                        for col in row:
                            if pd.notna(col) and isinstance(col, str):
                                data_match = re.search(r'\d{2}/\d{2}/\d{4}', col)
                                if data_match:
                                    data = data_match.group(0)
                                    break
                        
                        if internacao and nome and data:
                            dados_extraidos.append({
                                'internacao': internacao,
                                'nome': nome,
                                'data': data
                            })
                        else:
                            print(f"Linha com dados incompletos ignorada: {row}")
                
                # Converte a lista de dados extraídos para um DataFrame
                dados_df = pd.DataFrame(dados_extraidos)
                
                # Caminho para salvar o novo arquivo na pasta ~/AutoReg/
                user_dir = os.path.expanduser('~/AutoReg')
                os.makedirs(user_dir, exist_ok=True)
                caminho_novo_arquivo = os.path.join(user_dir, 'internados_ghosp_avancado.csv')
                dados_df.to_csv(caminho_novo_arquivo, index=False)
                
                print(f"Nomes extraídos e salvos em {caminho_novo_arquivo}.")


                
            except Exception as e:
                print(f"Erro ao processar o arquivo CSV: {e}")
        else:
                # Defina ou importe a função extrair_nomes conforme necessário
                print(original_df.head())

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()