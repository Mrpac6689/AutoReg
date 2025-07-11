"""
Realiza a extração dos códigos SISREG (Alta) de pacientes a partir do sistema SISREG III, utilizando automação com Selenium.
O processo inclui:
- Inicialização do navegador Chrome com opções customizadas.
- Acesso ao sistema SISREG III e autenticação automática utilizando credenciais armazenadas.
- Navegação até a seção "Saída/Permanência" e pesquisa de registros.
- Extração dos nomes dos pacientes e números das fichas de todas as páginas disponíveis.
- Salvamento dos dados extraídos em um arquivo CSV na pasta ~/AutoReg/.
- Registro de logs detalhados de cada etapa do processo.
Exceções e erros durante a execução são tratados e registrados em log. O navegador é encerrado ao final do processo, independentemente do sucesso ou falha.
Retorno:
    None
"""

import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC        
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging   
from autoreg.chrome_options import get_chrome_options
import logging
import pandas as pd


setup_logging()

def extrai_codigos_sisreg_alta():
    nomes_fichas = []
    print("EXTRAÇÃO DE CÓDIGOS SISREG - ALTA")
    logging.info("Iniciando extração de códigos SISREG - Alta")

    # Inicia o webdriver
    print("Iniciando o navegador Chrome...")
    logging.info("Iniciando o navegador Chrome para extração de códigos SISREG - Alta")
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)  # Define um tempo de espera de 20 segundos para aguardar os elementos
    
    try:
        # Acessa a URL do sistema SISREG
        print("Acessando o sistema SISREG...")
        logging.info("Acessando o sistema SISREG III")
        navegador.get("https://sisregiii.saude.gov.br")

        # Localiza e preenche o campo de usuário
        print("Tentando localizar o campo de usuário...")
        logging.info("Tentando localizar o campo de usuário no SISREG")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        print("Campo de usuário encontrado!")
        logging.info("Campo de usuário localizado com sucesso")

        print("Tentando localizar o campo de senha...")
        logging.info("Tentando localizar o campo de senha no SISREG")
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        print("Campo de senha encontrado!")
        logging.info("Campo de senha localizado com sucesso")

        # Preenche os campos de login com as credenciais do config.ini
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)

        # Pressiona o botão de login
        print("Tentando localizar o botão de login...")
        logging.info("Tentando localizar o botão de login no SISREG")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
        )
        login_button.click()

        time.sleep(5)  # Aguarda o carregamento da página após login
        print("Login realizado com sucesso!")
        logging.info("Login realizado com sucesso no SISREG")

        # Clica no link "Saída/Permanência"
        saida_permanencia_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
        )
        saida_permanencia_link.click()

        time.sleep(5)  # Aguarda o carregamento da nova página
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))

        # Localiza e clica no botão PESQUISAR dentro do iframe
        botao_pesquisar_saida = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        )
        botao_pesquisar_saida.click()
        time.sleep(5)

        # Extrai dados das tabelas
        while True:
            linhas_pacientes = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas_pacientes:
                nome_paciente = linha.find_element(By.XPATH, "./td[2]").text
                ficha_onclick = linha.get_attribute("onclick")
                ficha = ficha_onclick.split("'")[1]
                nomes_fichas.append((nome_paciente, ficha))
                
            
            # Verifica próxima página
            try:
                botao_proxima_pagina = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if botao_proxima_pagina.is_displayed():
                    botao_proxima_pagina.click()
                    time.sleep(5)
                else:
                    break
            except NoSuchElementException:
                break

        # Salva os dados em um arquivo CSV na pasta ~/AutoReg/
        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'codigos_sisreg.csv')
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerow(["Nome do Paciente", "Número da Ficha"])
            escritor_csv.writerows(nomes_fichas)
        print(f"Dados extraídos com sucesso! {len(nomes_fichas)} registros encontrados.")
        logging.info(f"Dados extraídos com sucesso! {len(nomes_fichas)}) registros encontrados.")
        print(f"Dados salvos no arquivo '{csv_path}'.")
        logging.info(f"Dados salvos no arquivo '{csv_path}'.")

    except Exception as e:
        print(f"Erro durante a execução de extrai_codigos: {e}")
        logging.error(f"Erro durante a execução de extrai_codigos_sisreg_alta: {e}")


    finally:
        navegador.quit()
        print("Navegador encerrado.")
        logging.info("Navegador encerrado após extração de códigos SISREG - Alta")

    print("A extração dos códigos SISREG foi concluída com sucesso!")
    logging.info("A extração dos códigos SISREG foi concluída com sucesso!")

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)

    pacientes_de_alta_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
    codigos_sisreg_path = os.path.join(user_dir, 'codigos_sisreg.csv')

    # Verifique se os arquivos existem
    if not os.path.exists(pacientes_de_alta_path):
        print(f"Arquivo não encontrado: {pacientes_de_alta_path}")
        logging.error(f"Arquivo não encontrado: {pacientes_de_alta_path}")  
        return
    if not os.path.exists(codigos_sisreg_path):
        print(f"Arquivo não encontrado: {codigos_sisreg_path}")
        logging.error(f"Arquivo não encontrado: {codigos_sisreg_path}")
        return

    pacientes_de_alta_df = pd.read_csv(pacientes_de_alta_path, encoding='utf-8')
    codigos_sisreg_df = pd.read_csv(codigos_sisreg_path, encoding='utf-8', dtype={'Número da Ficha': str})

    # Atualizar os nomes dos pacientes para caixa alta
    if 'Nome' in pacientes_de_alta_df.columns:
        pacientes_de_alta_df['Nome'] = pacientes_de_alta_df['Nome'].str.upper()
    else:
        print("Coluna 'Nome' não encontrada em pacientes_de_alta.csv")
        logging.error("Coluna 'Nome' não encontrada em pacientes_de_alta.csv")
        return

    # Mesclar os dois DataFrames
    if 'Nome do Paciente' not in codigos_sisreg_df.columns:
        print("Coluna 'Nome do Paciente' não encontrada em codigos_sisreg.csv")
        logging.error("Coluna 'Nome do Paciente' não encontrada em codigos_sisreg.csv")
        return

    pacientes_atualizados_df = pacientes_de_alta_df.merge(
        codigos_sisreg_df, left_on='Nome', right_on='Nome do Paciente', how='left'
    )

    if 'Número da Ficha' in pacientes_atualizados_df.columns:
        pacientes_atualizados_df['Número da Ficha'] = pacientes_atualizados_df['Número da Ficha'].astype(str)

    atualizados_path = os.path.join(user_dir, 'pacientes_de_alta_atualizados.csv')
    pacientes_atualizados_df.to_csv(atualizados_path, index=False, encoding='utf-8')

    print(f"\nArquivo '{atualizados_path}' atualizado com sucesso!")
    logging.info(f"Arquivo '{atualizados_path}' atualizado com sucesso!")

