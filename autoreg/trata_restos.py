import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, NoSuchFrameException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
import logging
setup_logging()

def atualiza_restos():
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'restos.csv')
    df = pd.read_csv(csv_path)
    if df.shape[0] > 0:
        df.iloc[:, 1] = 'ENCERRAMENTO ADMINISTRATIVO'
        df.to_csv(csv_path, index=False)
        print(f"Coluna atualizada e dados salvos em '{csv_path}'.")
    else:
        print("Arquivo está vazio.")

    def iniciar_navegador():
        print("Iniciando o navegador Chrome...")
        logging.info("Iniciando o navegador Chrome para execução de alta de pacientes")
        # Configurações do Chrome
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20) #mudado de 20 para 10
        navegador.maximize_window()
        return navegador, wait

    def realizar_login(navegador, wait):
        print("Acessando o sistema SISREG...")
        logging.info("Acessando o sistema SISREG III para login")
        navegador.get("https://sisregiii.saude.gov.br")

        print("Tentando localizar o campo de usuário...")
        logging.info("Tentando localizar o campo de usuário no SISREG")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)

        print("Tentando localizar o botão de login...")
        logging.info("Tentando localizar o botão de login no SISREG")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
        print("Login realizado e navegação para página de Saída/Permanência concluída!")
        logging.info("Login realizado com sucesso e navegação para página de Saída/Permanência concluída")

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Foco alterado para o iframe com sucesso!")
        logging.info("Foco alterado para o iframe principal do SISREG")
        
        try:
            botao_pesquisar_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']")))
            botao_pesquisar_saida.click()
            print("Botão PESQUISAR clicado com sucesso!")
            logging.info("Botão PESQUISAR clicado com sucesso na página de Saída/Permanência")
            # Aguarde a tabela/lista de pacientes aparecer
            wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")))
            print("Tabela de pacientes carregada!")
            logging.info("Tabela de pacientes carregada com sucesso na página de Saída/Permanência")
        except TimeoutException as e:
            print(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
            logging.error(f"Erro ao tentar localizar o botão PESQUISAR na página de Saída/Permanência: {e}")
            # Se o botão PESQUISAR não for encontrado, encerra o navegador
            navegador.quit()
            return False
        return True

    # Iniciar navegador e realizar login inicial
    navegador, wait = iniciar_navegador()
    if not realizar_login(navegador, wait):
        return

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    atualizados_path = os.path.join(user_dir, 'restos.csv')
    restos_path = os.path.join(user_dir, 'restos-atualizado.csv')

    try:
        pacientes_atualizados_df = pd.read_csv(atualizados_path, encoding='utf-8')
        for _, paciente in pacientes_atualizados_df.iterrows():
            try:
                nome_paciente = paciente.get('Nome', None)
                motivo_alta = paciente.get('Motivo da Alta', None)
                ficha = paciente.get('Número da Ficha', None)

                if nome_paciente is None or motivo_alta is None or ficha is None:
                    print("Dados insuficientes para o paciente, pulando para o próximo...")
                    logging.warning(f"Dados insuficientes para o paciente: {paciente}")
                    continue

                # Converter o número da ficha para string, garantindo que não haverá .0 no final
                ficha = str(ficha).split('.')[0]

                print(f"Processando alta para o paciente: {nome_paciente}")
                logging.info(f"Processando alta para o paciente: {nome_paciente}")
                dar_alta(navegador, wait, motivo_alta, ficha)
                time.sleep(2)

            except Exception as e:
                # Tratamento de erros específicos e reinicialização do navegador
                if isinstance(e, NoSuchElementException):
                    print("Erro: Elemento não encontrado - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    logging.error(f"Erro: Elemento não encontrado - {e}")
                elif isinstance(e, TimeoutException):
                    print("Erro: Ocorreu um TimeoutException - {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    logging.error(f"Erro: TimeoutException - {e}")
                else:
                    print("Erro inesperado: {str(e)}\nAGUARDE A REINICIALIZAÇÃO DO CHROMEDRIVER...\n")
                    logging.error(f"Erro inesperado: {e}")
                
                navegador.quit()

                # Reiniciar o navegador e refazer o login
                navegador, wait = iniciar_navegador()
                if not realizar_login(navegador, wait):
                    return

    except Exception as e:
        print(f"Erro geral na execução: {e}")
        logging.error(f"Erro geral na execução: {e}")

    # Criar arquivo 'restos.csv' com pacientes que não possuem motivos de alta desejados
    pacientes_df = pd.read_csv(atualizados_path, encoding='utf-8')
    motivos_desejados = [
        'PERMANENCIA POR OUTROS MOTIVOS',
        'ALTA MELHORADO',
        'ALTA A PEDIDO',
        'ALTA POR OUTROS MOTIVOS',
        'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO',
        'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
        'ENCERRAMENTO ADMINISTRATIVO',
        'ALTA POR EVASAO'
    ]
    restos_df = pacientes_df[~pacientes_df['Motivo da Alta'].isin(motivos_desejados)]
    restos_df.to_csv(restos_path, index=False)
    print(f"Arquivo '{restos_path}' criado com os pacientes sem motivo de alta desejado.")
    logging.info(f"Arquivo '{restos_path}' criado com os pacientes sem motivo de alta desejado.")   

    navegador.quit()
    print("\n Processo de saída concluído para todos os pacientes. \n Pacientes para análise manual gravados.")
    logging.info("Processo de saída concluído para todos os pacientes. Pacientes para análise manual gravados.")    
    # Contar e registrar a quantidade de altas executadas
    quantidade_altas = len(pacientes_atualizados_df)
    print(f"Quantidade de altas executadas: {quantidade_altas}")
    logging.info(f"Quantidade de altas executadas: {quantidade_altas}")

def dar_alta(navegador, wait, motivo_alta, ficha):
    
    print(f"Executando a função configFicha para a ficha: {ficha}")
    logging.info(f"Executando a função configFicha para a ficha: {ficha}")

    navegador.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    
    # Verifica se a função configFicha está disponível
    script_exists = navegador.execute_script("return typeof configFicha === 'function';")
    if not script_exists:
        print("Função configFicha não está disponível no contexto atual!")
        logging.error("Função configFicha não está disponível no contexto atual!")
        print(navegador.page_source)  # Debug: imprime o HTML do frame
        logging.debug("HTML do frame atual: " + navegador.page_source)
        return

    navegador.execute_script(f"configFicha('{ficha}')")
    
    # Aguarda o botão "Efetua Saída" aparecer, indicando que a ficha foi carregada
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
    except TimeoutException:
        print("Timeout esperando o botão 'Efetua Saída'. Verifique se a ficha existe ou se já foi dada alta.")
        logging.error("Timeout esperando o botão 'Efetua Saída'. Verifique se a ficha existe ou se já foi dada alta.")
        print(navegador.page_source)  # Debug: imprime o HTML do frame
        logging.debug("HTML do frame atual: " + navegador.page_source)
        return

    print("Aguarda o carregamento da página após a execução do script configFicha.")
    logging.info("Aguardando o carregamento da página após a execução do script configFicha.")

    try:
        print(f"Selecionando o motivo de alta: {motivo_alta}")
        logging.info(f"Selecionando o motivo de alta: {motivo_alta}")
        motivo_select = wait.until(EC.presence_of_element_located((By.NAME, "co_motivo")))
        select = webdriver.support.ui.Select(motivo_select)
        motivo_mapping = {
            'PERMANENCIA POR OUTROS MOTIVOS': '1.2 ALTA MELHORADO',
            'ALTA MELHORADO': '1.2 ALTA MELHORADO',
            'ALTA A PEDIDO': '1.4 ALTA A PEDIDO',
            'ALTA POR OUTROS MOTIVOS': '1.8 ALTA POR OUTROS MOTIVOS',
            'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO': '3.1 TRANSFERIDO PARA OUTRO ESTABELECIMENTO',
            'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE': '4.1 OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE',
            'ALTA POR EVASAO': '1.6 ALTA POR EVASAO',
            'ENCERRAMENTO ADMINISTRATIVO': '5.1 ENCERRAMENTO ADMINISTRATIVO'
        }
        motivo_alta = motivo_mapping.get(motivo_alta, None)
        if motivo_alta is None:
            print("Motivo de alta não reconhecido, nenhuma ação será tomada.")
            logging.warning(f"Motivo de alta '{motivo_alta}' não reconhecido, nenhuma ação será tomada.")       
            return

        for opcao in select.options:
            if motivo_alta.upper() in opcao.text.upper():
                select.select_by_visible_text(opcao.text)
                print(f"Motivo de alta '{motivo_alta}' selecionado com sucesso!")
                logging.info(f"Motivo de alta '{motivo_alta}' selecionado com sucesso!")
                break
    except TimeoutException:
        print("Erro ao tentar localizar o campo de motivo de alta.")
        logging.error("Erro ao tentar localizar o campo de motivo de alta.")
        return

    try:
        print("Tentando localizar o botão 'Efetua Saída'...")
        logging.info("Tentando localizar o botão 'Efetua Saída' no SISREG")
        botao_efetua_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
        botao_efetua_saida.click()
        print("Botão 'Efetua Saída' clicado com sucesso!")
        logging.info("Botão 'Efetua Saída' clicado com sucesso no SISREG")

        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        print("Primeiro pop-up confirmado!")
        logging.info("Primeiro pop-up confirmado com sucesso após clicar em 'Efetua Saída'")

        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        print("Segundo pop-up confirmado!")
        logging.info("Segundo pop-up confirmado com sucesso após clicar em 'Efetua Saída'")
    except TimeoutException:
        print("Erro ao tentar localizar o botão 'Efetua Saída' ou ao confirmar os pop-ups.")
        logging.error("Erro ao tentar localizar o botão 'Efetua Saída' ou ao confirmar os pop-ups.")
        print(navegador.page_source)  # Debug: imprime o HTML do frame
        logging.debug("HTML do frame atual: " + navegador.page_source)
    except ElementClickInterceptedException as e:
        print(f"Erro ao clicar no botão 'Efetua Saída': {e}")
        logging.error(f"Erro ao clicar no botão 'Efetua Saída': {e}")
        print(navegador.page_source)
        logging.debug("HTML do frame atual: " + navegador.page_source)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
        print(navegador.page_source)  # Debug: imprime o HTML do frame
        logging.debug("HTML do frame atual: " + navegador.page_source)              
    
