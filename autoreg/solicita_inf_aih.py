import os
import time
import pandas as pd
import re
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.logging import setup_logging
import logging

def solicita_inf_aih():
    print("\n---===> ACESSO AO GHOSP SOLICITA <===---")
    
    # Configuração dos diretórios e arquivos
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'solicita_inf_aih.csv')
    
    driver = None
    df = None

    # Lê o arquivo CSV
    try:
        df = pd.read_csv(csv_path)
        if 'link' not in df.columns:
            print("❌ Arquivo CSV não contém a coluna 'link'")
            return None
    except FileNotFoundError:
        print("❌ Arquivo solicita_inf_aih.csv não encontrado em ~/AutoReg")
        return None
    
    # Inicializa o navegador e faz login
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)

        print("Iniciando o Chromedriver...")
        url_login = f"{caminho_ghosp}:4002/users/sign_in"
        driver.get(url_login)

        # Login
        print("Localizando campo de e-mail...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(usuario_ghosp)

        print("Localizando campo de senha...")
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        senha_field.send_keys(senha_ghosp)

        print("Localizando botão de login...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
        )
        login_button.click()
        print("Login realizado com sucesso!")
        
        # Itera sobre os links do CSV
        for index, row in df.iterrows():
            try:
                link = row['link']
                print(f"\nProcessando link {index + 1}/{len(df)}: {link}")
                driver.get(link)

                # Obtém o número do prontuário
                print("Extraindo número do prontuário...")
                prontuario_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
                )
                prontuario_text = prontuario_element.text
                prontuario = ''.join(filter(str.isdigit, prontuario_text))
                # Remove ".0" no final se existir
                if prontuario.endswith('.0'):
                    prontuario = prontuario[:-2]
                # Remove qualquer ponto restante
                prontuario = prontuario.replace('.', '')
                print(f"Prontuário extraído: {prontuario}")

                # Obtém as informações dos sinais e sintomas
                print("Extraindo informações clínicas...")
                informacoes_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="campo_personalizado_laudo_aih_principais_sinais_e_sintomas_clinicos"]'))
                )
                informacoes = informacoes_element.text
                # Trata o texto removendo quebras de linha e caracteres problemáticos
                informacoes = ' '.join(informacoes.split())  # Remove quebras de linha e múltiplos espaços
                informacoes = informacoes.replace(';', ',').replace('"', "'").replace('\n', ' ').replace('\r', ' ')
                print(f"Informações clínicas extraídas: {informacoes}")

                # Extrai o tipo de clínica
                print("Extraindo tipo de clínica...")
                tipo_clinica_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="campo_personalizado_laudo_aih_clinica"]'))
                )
                tipo_clinica = tipo_clinica_element.get_attribute('value')
                # Trata o texto removendo quebras de linha e caracteres problemáticos
                tipo_clinica = ' '.join(tipo_clinica.split()).replace(';', ',').replace('"', "'").replace('\n', ' ').replace('\r', ' ')
                print(f"Tipo de clínica extraído: {tipo_clinica}")
                
                # Obtém o procedimento solicitado
                print("Extraindo procedimento...")
                procedimento_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "campo_personalizado_laudo_aih_procedimento_solicitado"))
                )
                procedimento_text = procedimento_element.get_attribute('value')
                procedimento_match = re.search(r'\((\d+)\)', procedimento_text)
                procedimento = procedimento_match.group(1) if procedimento_match else ''
                print(f"Procedimento extraído: {procedimento}")

                # Obtém o nome do médico e data
                print("Extraindo nome do médico e data...")
                botao = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[starts-with(@id, "edit_formeletronico_")]/div[2]/input'))
                )
                botao.click()

                info_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="lista-forms"]/ul/li[1]/div/span'))
                )
                info_text = info_element.text

                data_match = re.search(r'Preenchido em: (\d{2}/\d{2}/\d{4})', info_text)
                medico_match = re.search(r'por (.*?)\s*\(CRM', info_text)
                
                data = data_match.group(1) if data_match else ""
                medico = medico_match.group(1).strip() if medico_match else ""
                # Trata o nome do médico removendo caracteres problemáticos
                medico = ' '.join(medico.split()).replace(';', ',').replace('"', "'").replace('\n', ' ').replace('\r', ' ')
                
                print(f"Médico extraído: {medico}")
                print(f"Data extraída: {data}")

                # Clica no elemento do paciente para extrair CNS
                print("Clicando no elemento do paciente...")
                paciente_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
                )
                paciente_element.click()

                print("Extraindo CNS do paciente...")
                cns_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/small/fieldset[1]/div[2]'))
                )
                cns_text = cns_element.text
                cns = ''.join(filter(str.isdigit, cns_text))
                # Remove ".0" no final se existir
                if cns.endswith('.0'):
                    cns = cns[:-2]
                # Remove qualquer ponto restante
                cns = cns.replace('.', '')
                
                # Se CNS estiver vazio, tenta obter o CPF
                if not cns or cns.strip() == '':
                    print("CNS vazio, tentando extrair CPF...")
                    try:
                        cpf_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/small/fieldset[1]/div[4]'))
                        )
                        cpf_text = cpf_element.text
                        cns = ''.join(filter(str.isdigit, cpf_text))
                        # Remove ".0" no final se existir
                        if cns.endswith('.0'):
                            cns = cns[:-2]
                        # Remove qualquer ponto restante
                        cns = cns.replace('.', '')
                        if cns:
                            print(f"CPF extraído e usado como CNS: {cns}")
                        else:
                            print("CPF também está vazio")
                    except Exception as e:
                        print(f"Não foi possível extrair CPF: {e}")
                else:
                    print(f"CNS extraído: {cns}")

                # Clica no botão de fechar/voltar
                print("Fechando modal...")
                fechar_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[1]/a'))
                )
                fechar_element.click()

                # Atualiza o DataFrame com as informações extraídas
                df.at[index, 'prontuario'] = prontuario
                df.at[index, 'informacoes'] = informacoes
                df.at[index, 'tipo'] = tipo_clinica
                df.at[index, 'procedimento'] = procedimento
                df.at[index, 'cns'] = cns
                df.at[index, 'medico'] = medico
                df.at[index, 'data'] = data
                
                # Salva o progresso após cada iteração
                df.to_csv(csv_path, index=False)
                print(f"✔️ Informações salvas para o link {index + 1}")

            except Exception as e:
                print(f"❌ Erro ao processar link {index + 1}: {str(e)}")
                # Em caso de erro, salva o que já foi processado
                if df is not None:
                    df.to_csv(csv_path, index=False)
                continue

    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        return None
    finally:
        if driver is not None:
            print("\nFechando o navegador...")
            driver.quit()

    print("\n✔️ Processamento concluído!")
    return df