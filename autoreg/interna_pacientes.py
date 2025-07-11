# autoreg/extrai_codigos_internacao.py
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.chrome_options import get_chrome_options  # ajuste aqui
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
import logging
import datetime
from datetime import datetime, timedelta
import random   
from selenium.webdriver.support.ui import Select

setup_logging()
def interna_pacientes():
    nomes_fichas = []
    navegador = None
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'codigos_internacao.csv')
    with open(csv_path, mode='r', encoding='utf-8') as file:
        print("INICIANDO PROCESSO DE INTERNAÇÃO\n")
        # Configura o diretório do usuário e o caminho do arquivo CSV
        leitor_csv = csv.reader(file)
        next(leitor_csv)  # Pula o cabeçalho
        # Configura o navegador Chrome com opções personalizadas
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 10)
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
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
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
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Login realizado e navegação para página de Internação...\n")
        logging.info("Login realizado e navegação para página de Internação...\n")

        try:
            for linha in leitor_csv:
                ficha = linha[1]  # Captura o número da ficha da segunda coluna
                try:
                    print(f"Acessando a página de Internação para a ficha {ficha}...\n")

                    # ABRE A FICHA A SER INTERNADA
                    navegador.switch_to.default_content()
                    wait = WebDriverWait(navegador, 10)
                    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
                    navegador.execute_script(f"configFicha('{ficha}')")
                    print(f"Executando a função configFicha para a ficha: {ficha}\n")
                    time.sleep(1)  # Reduzi o tempo de espera para acelerar o fluxo                    
                    print(f"Ficha {ficha} processada com sucesso.\n")
                    # Captura a data de solicitação e formata corretamente
                    try:
                        all_trs = navegador.find_elements(By.XPATH, "//tr")
                        tr_solicitacao = None
                        for tr in all_trs:
                            if "Data de Solicitação:" in tr.text:
                                tr_solicitacao = tr
                                break

                        if tr_solicitacao:
                            tr_data = tr_solicitacao.find_element(By.XPATH, "following-sibling::tr[1]")
                            data_element = tr_data.find_element(By.XPATH, "td[3]")
                            data_text = data_element.text.split(" - ")[0].strip()
                            data_original = datetime.strptime(data_text, "%d.%m.%Y")
                            data_internacao = data_original - timedelta(days=2)
                            data_internacao_str = data_internacao.strftime("%d/%m/%Y")

                            print(f"Data de solicitação encontrada: {data_text}\n")
                            print(f"Data formatada para inserção: {data_internacao_str}\n")
                        else:
                            print("Erro: A TR com 'Data de Solicitação:' não foi encontrada!\n")

                    except (TimeoutException, NoSuchElementException, ValueError) as e:
                        print(f"Erro na extração da data: {e}\n")

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

                    # Lidar com o primeiro popup de confirmação
                    try:
                        WebDriverWait(navegador, 10).until(EC.alert_is_present())  
                        alert = navegador.switch_to.alert
                        texto_popup = alert.text
                        print(f"Popup detectado: {texto_popup}\n")
                        alert.accept()
                        print("✔️ Botão 'OK' pressionado com sucesso.\n")
                        time.sleep(2)
                    except TimeoutException:
                        print("⚠️ Nenhum popup encontrado. Prosseguindo com a operação.\n")
                    except Exception as e:
                        print(f"❌ Erro ao interagir com o popup: {e}\n")

                    # Aguarda um possível segundo popup
                    try:
                        WebDriverWait(navegador, 10).until(EC.alert_is_present())
                        segundo_alert = navegador.switch_to.alert
                        texto_segundo_popup = segundo_alert.text
                        segundo_alert.accept()
                        print(f"Segundo alerta confirmado: {texto_segundo_popup}\n")
                    except TimeoutException:
                        print("Nenhum segundo alerta apareceu. Prosseguindo com a operação.\n")
                    except Exception as e:
                        print(f"Erro ao lidar com o segundo alerta: {e}\n")

                    # Verifica se há erro de sistema na tela
                    try:
                        erro_sistema = navegador.find_element(By.XPATH, "//div[contains(text(), 'Erro de Sistema')]")
                        print("⚠️ Erro de Sistema detectado. Processo interrompido.\n")
                    except NoSuchElementException:
                        print("✔️ Nenhum erro de sistema detectado. Internação realizada com sucesso.\n")
                        #wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']")))
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
            print("Todos os códigos de internação foram processados. Verifique o arquivo 'codigos_internacao.csv' no diretório ~/AutoReg.\n")
            logging.info("Todos os códigos de internação foram processados. Verifique o arquivo 'codigos_internacao.csv' no diretório ~/AutoReg.")          


