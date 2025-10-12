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

def solicita_sisreg():
    print("\n---===> SOLICITA SISREG <===---")
        
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
    csv_path = os.path.join(user_dir, 'solicita_inf_aih.csv')
    
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        logging.error(f"Arquivo não encontrado: {csv_path}")
        return
        
    # Lê o CSV e pega o primeiro CNS
    df = pd.read_csv(csv_path)
    if df.empty:
        print("Arquivo CSV está vazio!")
        logging.error("Arquivo CSV está vazio")
        return
        
    try:
        for index, row in df.iterrows():
            try:
                print(f"\nProcessando registro {index + 1}/{len(df)}")
                print(f"CNS a ser processado: {row['cns']}")

                # Navega até o menu de Internação
                print("Acessando menu de Internação...")
                logging.info("Tentando acessar menu de Internação")
                
                # Primeiro, movemos o mouse sobre o menu "solicitar" para exibir o submenu
                menu_solicitar = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'solicitar')]"))
                )
                ActionChains(navegador).move_to_element(menu_solicitar).perform()
                time.sleep(2)  # Aguarda o submenu aparecer
                
                # Clica no link de Internação
                print("Clicando no link de Internação...")
                internacao_link = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/cadweb50?url=/cgi-bin/marcar_ih']"))
                )
                internacao_link.click()
                print("Link de Internação clicado com sucesso!")
                
                # Aguarda carregamento da página e mudança para o frame principal
                time.sleep(3)
                navegador.switch_to.frame("f_principal")
                
                # Localiza o campo de CNS e preenche
                print("Preenchendo CNS...")
                campo_cns = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='main_div']/form/center[1]/table/tbody/tr[2]/td[2]/input"))
                )
                # Trata o CNS removendo ".0" e pontos se existirem
                cns = str(row['cns'])
                if cns.endswith('.0'):
                    cns = cns[:-2]
                cns = cns.replace('.', '')
                campo_cns.clear()
                campo_cns.send_keys(cns)
                
                # Clica no botão de pesquisa
                print("Pesquisando CNS...")
                botao_pesquisar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='main_div']/form/center[2]/input[1]"))
                )
                botao_pesquisar.click()
                print("Pesquisa realizada com sucesso!")
                
                time.sleep(3)  # Aguarda resultado da pesquisa
                
                # Clica no botão na nova tela
                print("Clicando no botão de confirmação...")
                botao_confirmar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='main_div']/form/center[3]/input[3]"))
                )
                botao_confirmar.click()
                print("Botão de confirmação clicado com sucesso!")
                logging.info("Botão de confirmação clicado com sucesso")
                
                time.sleep(3)  # Aguarda processamento após o clique

                # Lê o procedimento do CSV, remove pontos e ".0", depois garante 10 dígitos
                procedimento = str(row['procedimento'])
                # Remove ".0" no final se existir
                if procedimento.endswith('.0'):
                    procedimento = procedimento[:-2]
                # Remove qualquer ponto restante
                procedimento = procedimento.replace('.', '')
                # Garante que tenha 10 dígitos com zero à esquerda
                procedimento = procedimento.zfill(10)
                print(f"Procedimento a ser inserido: {procedimento}")

                # Localiza o campo de procedimento e preenche
                print("Preenchendo código do procedimento...")
                campo_procedimento = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[2]/td[2]/input[1]"))
                )
                campo_procedimento.clear()
                campo_procedimento.send_keys(str(procedimento))
                
                # Clica no botão ao lado do campo de procedimento
                print("Pesquisando procedimento...")
                botao_pesquisar_proc = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[2]/td[2]/input[2]"))
                )
                botao_pesquisar_proc.click()
                print("Pesquisa do procedimento realizada com sucesso!")
                logging.info("Pesquisa do procedimento realizada com sucesso")
                
                time.sleep(2)  # Aguarda processamento da pesquisa do procedimento

                # Localiza o dropdown do CID
                print("Localizando menu dropdown do CID...")
                dropdown_cid = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[4]/td[2]/select"))
                )
                select_cid = Select(dropdown_cid)
                
                # Pega todas as opções exceto a primeira (rótulo)
                options = select_cid.options[1:]  # Ignora a primeira opção
                
                if not options:
                    print("Erro: Nenhuma opção de CID disponível além do rótulo!")
                    logging.error("Nenhuma opção de CID disponível além do rótulo")
                    return
                    
                # Seleciona uma opção aleatória entre as disponíveis
                random_option = random.choice(options)
                select_cid.select_by_visible_text(random_option.text)
                print(f"CID selecionado aleatoriamente: {random_option.text}")
                logging.info(f"CID selecionado aleatoriamente: {random_option.text}")
                
                time.sleep(2)  # Aguarda processamento da seleção
                
                # Mapeamento do tipo de clínica para a opção do dropdown
                tipo_para_opcao = {
                    'CLÍNICA MÉDICA': 'ESPEC - CLINICO - CLINICA GERAL',
                    'CLÍNICA CIRÚRGICA': 'ESPEC - CIRURGICO - CIRURGIA GERAL',
                    'CLÍNICA PEDIÁTRICA': 'PEDIATRICO - PEDIATRIA CLINICA'
                }
                
                # Obtém o tipo do CSV
                tipo_clinica = row['tipo'].upper()  # Converte para maiúsculas para garantir
                print(f"Tipo de clínica do paciente: {tipo_clinica}")
                
                # Localiza o segundo dropdown
                print("Localizando segundo menu dropdown...")
                segundo_dropdown = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[5]/td[2]/select"))
                )
                select_especialidade = Select(segundo_dropdown)
                
                # Seleciona a opção baseada no tipo
                if tipo_clinica in tipo_para_opcao:
                    opcao_desejada = tipo_para_opcao[tipo_clinica]
                    print(f"Selecionando especialidade: {opcao_desejada}")
                    select_especialidade.select_by_visible_text(opcao_desejada)
                    print(f"Especialidade selecionada: {opcao_desejada}")
                    logging.info(f"Especialidade selecionada: {opcao_desejada}")
                else:
                    print(f"Tipo de clínica não mapeado: {tipo_clinica}")
                    logging.warning(f"Tipo de clínica não mapeado: {tipo_clinica}")
                    return
                    
                time.sleep(2)  # Aguarda processamento da seleção
                
                # Localiza o dropdown de profissionais
                print("Localizando dropdown de profissionais...")
                profissional_dropdown = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[6]/td[2]/select"))
                )
                select_profissional = Select(profissional_dropdown)
                
                # Pega a última opção (PROFISSIONAL NAO LISTADO)
                opcoes = select_profissional.options
                ultima_opcao = opcoes[-1]
                print(f"Selecionando opção: {ultima_opcao.text}")
                select_profissional.select_by_visible_text(ultima_opcao.text)
                
                # Aguarda o campo de nome do médico aparecer e preenche
                print("Preenchendo nome do médico...")
                nome_medico = row['medico']
                campo_medico = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='idSolicitante']/td[2]/input"))
                )
                campo_medico.clear()
                campo_medico.send_keys(str(nome_medico))
                print(f"Nome do médico preenchido: {nome_medico}")
                logging.info(f"Nome do médico preenchido: {nome_medico}")
                
                time.sleep(2)  # Aguarda processamento
                
                # Seleciona o nível de urgência
                print("Selecionando nível de urgência...")
                urgencia_dropdown = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[8]/td[2]/select"))
                )
                select_urgencia = Select(urgencia_dropdown)
                select_urgencia.select_by_visible_text("2 - Urgencia")
                print("Nível de urgência selecionado: 2 - Urgencia")
                logging.info("Nível de urgência selecionado: 2 - Urgencia")
                
                time.sleep(1)  # Pequena pausa entre seleções
                
                # Seleciona a prioridade
                print("Selecionando prioridade...")
                prioridade_dropdown = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[10]/td[2]/select"))
                )
                select_prioridade = Select(prioridade_dropdown)
                select_prioridade.select_by_visible_text("Amarelo - Prioridade 1")
                print("Prioridade selecionada: Amarelo - Prioridade 1")
                logging.info("Prioridade selecionada: Amarelo - Prioridade 1")
                
                time.sleep(1)  # Pequena pausa antes de clicar no botão
                
                # Clica no botão de confirmar
                print("Clicando no botão de confirmar...")
                botao_confirmar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/center/form/center/input"))
                )
                botao_confirmar.click()
                print("Solicitação confirmada!")
                logging.info("Solicitação confirmada com sucesso")
                
                time.sleep(3)  # Aguarda carregamento da nova tela
                
                # Seleciona o hospital
                print("Selecionando hospital...")
                hospital_dropdown = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr[5]/td[2]/select"))
                )
                select_hospital = Select(hospital_dropdown)
                select_hospital.select_by_visible_text("HOSPITAL GERAL DE CLINICAS DE RIO BRANCO")
                print("Hospital selecionado: HOSPITAL GERAL DE CLINICAS DE RIO BRANCO")
                logging.info("Hospital selecionado com sucesso")
                
                time.sleep(1)  # Pequena pausa entre ações
                
                # Preenche a data de hoje
                print("Preenchendo data...")
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                campo_data = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='dt_desejada']"))
                )
                campo_data.clear()
                campo_data.send_keys(data_hoje)
                print(f"Data preenchida: {data_hoje}")
                logging.info(f"Data preenchida: {data_hoje}")
                
                time.sleep(2)  # Aguarda processamento
                
                # Preenche o primeiro textarea com as informações clínicas
                print("Preenchendo informações clínicas...")
                informacoes = row['informacoes']
                texto_info = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr[42]/td/textarea"))
                )
                texto_info.clear()
                texto_info.send_keys(str(informacoes))
                print("Informações clínicas preenchidas")
                
                time.sleep(1)  # Pequena pausa entre campos
                
                # Preenche o segundo textarea com "ACIMA DESCRITO"
                print("Preenchendo campo de justificativa...")
                texto_justificativa = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr[44]/td/textarea"))
                )
                texto_justificativa.clear()
                texto_justificativa.send_keys("ACIMA DESCRITO")
                print("Justificativa preenchida")
                
                time.sleep(1)  # Pequena pausa entre campos
                
                # Preenche o terceiro textarea com data e prontuário
                print("Preenchendo informações complementares...")
                # Trata o prontuário removendo ".0" e pontos se existirem
                prontuario = str(row['prontuario'])
                if prontuario.endswith('.0'):
                    prontuario = prontuario[:-2]
                prontuario = prontuario.replace('.', '')
                data_prontuario = f"{row['data']} - {prontuario}"
                texto_complementar = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr[46]/td/textarea"))
                )
                texto_complementar.clear()
                texto_complementar.send_keys(data_prontuario)
                print(f"Informações complementares preenchidas: {data_prontuario}")
                
                time.sleep(2)  # Aguarda processamento dos campos
                
                # Clica no botão final de confirmação
                print("Confirmando solicitação...")
                botao_final = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/center/form/center/p/input[2]"))
                )
                botao_final.click()
                print("Solicitação finalizada com sucesso!")
                logging.info("Solicitação finalizada com sucesso")
                
                time.sleep(3)  # Aguarda processamento final e carregamento da página de confirmação
                
                # Captura o número da solicitação
                print("Capturando número da solicitação...")
                numero_solicitacao = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/center/p[1]/b"))
                ).text
                print(f"Número da solicitação capturado: {numero_solicitacao}")
                logging.info(f"Número da solicitação capturado: {numero_solicitacao}")
                
                # Atualiza o CSV com o número da solicitação
                df.at[index, 'solsisreg'] = numero_solicitacao
                df.to_csv(csv_path, index=False)
                print(f"CSV atualizado com o número da solicitação: {numero_solicitacao}")
                logging.info(f"CSV atualizado com o número da solicitação: {numero_solicitacao}")
                
                navegador.switch_to.default_content()
                print(f"Registro {index + 1} processado com sucesso!")
                time.sleep(3)  # Dar tempo para o sistema processar antes do próximo registro
            except Exception as e:
                print(f"Erro ao processar registro {index + 1}: {str(e)}")
                logging.error(f"Erro ao processar registro {index + 1}: {str(e)}")
                navegador.switch_to.default_content()
                continue
    except Exception as e:
        print(f"Erro geral durante o processamento: {str(e)}")
        logging.error(f"Erro geral durante o processamento: {str(e)}")
    finally:
        if navegador:
            navegador.quit()
            print("Navegador encerrado.")
            logging.info("Navegador encerrado após solicitação no SISREG")