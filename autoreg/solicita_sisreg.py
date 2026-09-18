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
from autoreg.detecta_capchta import detecta_captcha
import logging
import random
from datetime import datetime

setup_logging()

# Status possíveis de uma tentativa de solicitação no SISREG
STATUS_SUCESSO = 'sucesso'
STATUS_PENDENTE = 'pendente'
STATUS_CNS_NAO_ENCONTRADO = 'cns_nao_encontrado'
STATUS_ERRO_DESCONHECIDO = 'erro_desconhecido'

# Procedimento substituto a tentar quando o SISREG rejeita a solicitação com
# "O paciente já possui uma solicitação pendente para o procedimento."
# As chaves espelham deliberadamente o mesmo agrupamento usado em
# tipo_para_opcao (incluindo "CIRURGIA GERAL" como sinônimo de clínica
# cirúrgica), para manter consistência com a lógica de especialidade já
# existente nesta mesma função.
SUBSTITUICAO_PROCEDIMENTO_PENDENTE = {
    'CLÍNICA MÉDICA': '0301060088',
    'CLINICA MEDICA': '0301060088',
    'CLÍNICA CIRÚRGICA': '0301060070',
    'CLINICA CIRURGICA': '0301060070',
    'CIRURGIA GERAL': '0301060070',
}


def _executar_tentativa_solicitacao(navegador, wait, row, cns, procedimento):
    """
    Executa uma tentativa completa de solicitação de internação no SISREG:
    navega até a página de marcação, busca/confirma o CNS, preenche
    procedimento/CID/especialidade/profissional/médico/urgência/prioridade,
    confirma, preenche hospital/data/textos, confirma novamente e lê o
    resultado final (número da solicitação ou mensagem de erro conhecida).

    Não grava nada no CSV/DataFrame — apenas retorna o desfecho para o
    chamador decidir o que persistir, permitindo chamar esta função duas
    vezes (tentativa original + retry com procedimento substituto) sem
    duplicar a lógica de gravação. Não trata exceções genéricas: qualquer
    erro inesperado do Selenium propaga para o try/except do loop principal
    de solicita_sisreg().

    Retorna uma tupla (status, detalhe):
      (STATUS_SUCESSO, numero_solicitacao)
      (STATUS_PENDENTE, None)
      (STATUS_CNS_NAO_ENCONTRADO, None)
      (STATUS_ERRO_DESCONHECIDO, None)
    """
    # Navega até o menu de Internação
    print("Acessando menu de Internação...")
    logging.info("Tentando acessar menu de Internação")
    navegador.get("https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar_ih")

    # Localiza o campo de CNS e preenche
    print("Preenchendo CNS...")
    campo_cns = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='main_div']/form/center[1]/table/tbody/tr[2]/td[2]/input"))
    )
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
    try:
        botao_confirmar = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='main_div']/form/center[3]/input[3]"))
        )
        botao_confirmar.click()
        print("Botão de confirmação clicado com sucesso!")
        logging.info("Botão de confirmação clicado com sucesso")
    except TimeoutException:
        # Se o botão não for encontrado, significa que o CNS não foi encontrado na base
        return (STATUS_CNS_NAO_ENCONTRADO, None)

    time.sleep(3)  # Aguarda processamento após o clique

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
        return (STATUS_ERRO_DESCONHECIDO, None)

    # Seleciona uma opção aleatória entre as disponíveis
    random_option = random.choice(options)
    select_cid.select_by_visible_text(random_option.text)
    print(f"CID selecionado aleatoriamente: {random_option.text}")
    logging.info(f"CID selecionado aleatoriamente: {random_option.text}")

    time.sleep(2)  # Aguarda processamento da seleção

    # Mapeamento do tipo de clínica para a opção do dropdown
    tipo_para_opcao = {
        'CLÍNICA MÉDICA': 'ESPEC - CLINICO - CLINICA GERAL',
        'CLINICA MEDICA': 'ESPEC - CLINICO - CLINICA GERAL',
        'CLINICA PSIQUIATRICA': 'ESPEC - CLINICO - SAUDE MENTAL',
        'CLÍNICA PSIQUIÁTRICA': 'ESPEC - CLINICO - SAUDE MENTAL',
        'CLÍNICA CIRÚRGICA': 'ESPEC - CIRURGICO - CIRURGIA GERAL',
        'CLINICA CIRURGICA': 'ESPEC - CIRURGICO - CIRURGIA GERAL',
        'CIRURGIA GERAL': 'ESPEC - CIRURGICO - CIRURGIA GERAL',
        'CLINICA PEDIATRICA': 'PEDIATRICO - PEDIATRIA CLINICA',
        'CLÍNICA PEDIÁTRICA': 'PEDIATRICO - PEDIATRIA CLINICA'
    }

    # Obtém o tipo do CSV
    tipo_clinica = row['tipo'].upper()  # Converte para maiúsculas para garantir
    print(f"Tipo de clínica do paciente: {tipo_clinica}")
    logging.info(f"Tipo de clínica do paciente: {tipo_clinica}")

    # Localiza o segundo dropdown
    print("Localizando segundo menu dropdown...")
    segundo_dropdown = wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/center/form/table/tbody/tr/td/table/tbody/tr[5]/td[2]/select"))
    )
    select_especialidade = Select(segundo_dropdown)

    # Tipos que podem representar cirurgia ortopédica
    tipos_cirurgico_ortopedico = {
        'CLÍNICA CIRÚRGICA', 'CLINICA CIRURGICA', 'CIRURGIA GERAL',
        'ORTOPEDIA', 'TRAUMATORTOPEDIA', 'CLÍNICA ORTOPÉDICA', 'CLINICA ORTOPEDICA',
        'ORTOPEDIA E TRAUMATOLOGIA', 'TRAUMATOLOGIA'
    }

    # Seleciona a opção baseada no tipo
    # Prioridade 1: procedimento específico de Saúde Mental (independe do tipo)
    if procedimento == '0303170131':
        opcao_desejada = 'ESPEC - CLINICO - SAUDE MENTAL'
        print(f"Procedimento de Saúde Mental detectado ({procedimento}). Clínica: {opcao_desejada}")
        logging.info(f"Procedimento de Saúde Mental detectado ({procedimento}). Clínica: {opcao_desejada}")
    # Prioridade 2: se tipo é cirúrgico/ortopédico E procedimento inicia em 0408, usa ortopedia
    elif tipo_clinica in tipos_cirurgico_ortopedico and procedimento.startswith('0408'):
        opcao_desejada = 'ESPEC - CIRURGICO - ORTOPEDIATRAUMATOLOGIA'
        print(f"Procedimento ortopédico detectado ({procedimento}). Clínica: {opcao_desejada}")
        logging.info(f"Procedimento ortopédico detectado ({procedimento}). Clínica: {opcao_desejada}")
    elif tipo_clinica in tipo_para_opcao:
        opcao_desejada = tipo_para_opcao[tipo_clinica]
    else:
        opcao_desejada = 'ESPEC - CLINICO - CLINICA GERAL'
        print(f"Tipo de clínica não mapeado: '{tipo_clinica}'. Usando padrão: {opcao_desejada}")
        logging.warning(f"Tipo de clínica não mapeado: '{tipo_clinica}'. Usando padrão: {opcao_desejada}")
    print(f"Selecionando especialidade: {opcao_desejada}")
    select_especialidade.select_by_visible_text(opcao_desejada)
    print(f"Especialidade selecionada: {opcao_desejada}")
    logging.info(f"Especialidade selecionada: {opcao_desejada}")

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

    # Preenche o primeiro textarea com as informações clínicas (ds_sintoma)
    print("Preenchendo informações clínicas...")
    informacoes = row['informacoes']
    texto_info = wait.until(
        EC.presence_of_element_located((By.NAME, "ds_sintoma"))
    )
    texto_info.clear()
    texto_info.send_keys(str(informacoes))
    print("Informações clínicas preenchidas")

    time.sleep(1)  # Pequena pausa entre campos

    # Preenche o segundo textarea com "ACIMA DESCRITO" (ds_prova)
    print("Preenchendo campo de justificativa...")
    texto_justificativa = wait.until(
        EC.presence_of_element_located((By.NAME, "ds_prova"))
    )
    texto_justificativa.clear()
    texto_justificativa.send_keys("ACIMA DESCRITO")
    print("Justificativa preenchida")

    time.sleep(1)  # Pequena pausa entre campos

    # Preenche o terceiro textarea com data e prontuário (ds_justificativa)
    print("Preenchendo informações complementares...")
    # Trata o prontuário removendo ".0" e pontos se existirem
    prontuario = str(row['prontuario'])
    if prontuario.endswith('.0'):
        prontuario = prontuario[:-2]
    prontuario = prontuario.replace('.', '')
    data_prontuario = f"{row['data']} - {prontuario}"
    texto_complementar = wait.until(
        EC.presence_of_element_located((By.NAME, "ds_justificativa"))
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

    # Tenta capturar o número da solicitação
    print("Capturando número da solicitação...")
    try:
        numero_solicitacao = wait.until(
            EC.presence_of_element_located((By.XPATH, "/html/body/center/p[1]/b"))
        ).text
        print(f"Número da solicitação capturado: {numero_solicitacao}")
        logging.info(f"Número da solicitação capturado: {numero_solicitacao}")
        return (STATUS_SUCESSO, numero_solicitacao)

    except TimeoutException:
        # Se não encontrou o número, verifica se há mensagem de solicitação pendente
        print("Número da solicitação não encontrado, verificando mensagem de erro...")
        try:
            mensagem_pendente = navegador.find_element(
                By.XPATH,
                "//td[contains(text(), 'O paciente já possui uma solicitação pendente para o procedimento.')]"
            )
            if mensagem_pendente:
                print("⚠️  O paciente já possui uma solicitação pendente para o procedimento.")
                logging.warning("O paciente já possui uma solicitação pendente para o procedimento.")
                return (STATUS_PENDENTE, None)
        except NoSuchElementException:
            print("❌ Número da solicitação não encontrado e nenhuma mensagem de erro conhecida detectada")
            logging.error("Número da solicitação não encontrado")

        return (STATUS_ERRO_DESCONHECIDO, None)


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

    # Remove ".0" do final dos campos numéricos lidos como float pelo pandas
    for col in ['ra', 'cns', 'procedimento']:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(
                lambda x: x[:-2] if x.endswith('.0') else x
            )

    # Colunas de texto que este módulo grava via df.at[] — podem vir como
    # float64 (NaN) do CSV quando todas as linhas estão vazias (ex.: recém-
    # recriado por -spaa), travando a gravação com "Invalid value ... for
    # dtype 'float64'". Força dtype object quando já existirem.
    for col in ('erro', 'revisar', 'solsisreg', 'obs_substituicao'):
        if col in df.columns:
            df[col] = df[col].astype(object)

    df.to_csv(csv_path, index=False)
    print("CSV normalizado (removido '.0' de ra, cns e procedimento)")

    try:
        for index, row in df.iterrows():
            try:
                # Verifica se há CAPTCHA antes de cada solicitação
                resultado_captcha = detecta_captcha(navegador)
                if resultado_captcha != 'ok':
                    print(f"CAPTCHA não resolvido ({resultado_captcha}). Abortando solicitações.")
                    logging.error(f"Solicitações abortadas por CAPTCHA não resolvido: {resultado_captcha}")
                    break

                # Se a linha possuir dados na coluna solsisreg, ela deve ser ignorada no loop
                if 'solsisreg' in df.columns and pd.notna(row['solsisreg']) and str(row['solsisreg']).strip() != '':
                    print(f"Registro {index + 1}/{len(df)} já possui solicitação ({row['solsisreg']}). Pulando...")
                    continue

                print(f"\nProcessando registro {index + 1}/{len(df)}")

                # Normaliza e valida o CNS antes de qualquer interação com o navegador:
                # remove tudo que não for dígito (não só ".0"/pontos) e confere 11 ou 15
                # dígitos, evitando o alert() do SISREG quando o valor já chega malformado
                # do G-HOSP e dando um diagnóstico imediato e específico.
                cns_original = str(row['cns'])
                cns = ''.join(ch for ch in cns_original if ch.isdigit())
                # CPF usado como CNS (quando o G-HOSP não tem CNS cadastrado,
                # ver solicita_inf_aih.py) pode ter perdido o zero à esquerda
                # numa releitura do CSV pelo pandas, que infere a coluna como
                # número quando todos os valores parecem dígitos — 11 dígitos
                # vira 10. Um CNS de verdade tem 15 dígitos e nunca começa
                # com 0, então só o caso de 10 dígitos é inequivocamente um
                # CPF truncado, seguro para reconstruir.
                if len(cns) == 10:
                    cns = cns.zfill(11)
                if len(cns) not in (11, 15):
                    erro_msg = (
                        f"CNS malformado após normalização: '{cns_original}' → '{cns}' "
                        f"({len(cns)} dígitos, esperado 11 ou 15)"
                    )
                    print(f"⚠️  {erro_msg}")
                    logging.warning(f"Registro {index + 1}: {erro_msg}")

                    if 'erro' not in df.columns:
                        df['erro'] = ''
                    if 'revisar' not in df.columns:
                        df['revisar'] = ''

                    df.at[index, 'erro'] = erro_msg
                    df.at[index, 'revisar'] = 'sim'
                    df.to_csv(csv_path, index=False)
                    print(f"Erro registrado no CSV: {erro_msg}")
                    logging.info(f"Erro registrado no CSV para registro {index + 1}: {erro_msg}")
                    continue

                print(f"CNS a ser processado: {cns}")

                # Lê o procedimento do CSV, remove pontos e ".0", depois garante 10 dígitos
                procedimento_original = str(row['procedimento'])
                if procedimento_original.endswith('.0'):
                    procedimento_original = procedimento_original[:-2]
                procedimento_original = procedimento_original.replace('.', '')
                procedimento_original = procedimento_original.zfill(10)
                print(f"Procedimento a ser inserido: {procedimento_original}")
                logging.info(f"Registro {index + 1}: procedimento a ser inserido: {procedimento_original}")

                # Primeira tentativa, com o procedimento vindo do CSV
                status, detalhe = _executar_tentativa_solicitacao(navegador, wait, row, cns, procedimento_original)

                procedimento_usado = procedimento_original
                procedimento_substituido = False
                tipo_clinica_retry = None

                # Se o SISREG acusar solicitação pendente para o procedimento, tenta uma
                # única vez com o procedimento substituto correspondente à clínica do
                # paciente (Cirúrgica -> 0301060070, Médica -> 0301060088). Para outras
                # clínicas (Psiquiátrica, Pediátrica, tipo desconhecido) não há substituto
                # mapeado e o comportamento permanece o de apenas registrar o erro.
                if status == STATUS_PENDENTE:
                    tipo_clinica_retry = str(row['tipo']).upper()
                    procedimento_substituto = SUBSTITUICAO_PROCEDIMENTO_PENDENTE.get(tipo_clinica_retry)

                    if procedimento_substituto and procedimento_substituto != procedimento_original:
                        print(f"⚠️  Solicitação pendente para o procedimento {procedimento_original}. "
                              f"Tentando novamente com o procedimento substituto {procedimento_substituto} "
                              f"(clínica: {tipo_clinica_retry})...")
                        logging.warning(
                            f"Registro {index + 1}: solicitação pendente para procedimento "
                            f"{procedimento_original}; tentando substituto {procedimento_substituto}"
                        )
                        navegador.switch_to.default_content()

                        status, detalhe = _executar_tentativa_solicitacao(
                            navegador, wait, row, cns, procedimento_substituto
                        )
                        procedimento_usado = procedimento_substituto
                        procedimento_substituido = True

                # Ponto único de gravação no CSV para este registro, cobrindo tanto a
                # primeira tentativa quanto a segunda (retry com procedimento substituto)
                if status == STATUS_SUCESSO:
                    numero_solicitacao = detalhe
                    df.at[index, 'solsisreg'] = numero_solicitacao
                    if 'erro' in df.columns:
                        df.at[index, 'erro'] = ''
                    if procedimento_substituido:
                        df.at[index, 'procedimento'] = procedimento_usado
                        if 'obs_substituicao' not in df.columns:
                            df['obs_substituicao'] = ''
                        df.at[index, 'obs_substituicao'] = (
                            f"Procedimento original {procedimento_original} trocado para "
                            f"{procedimento_usado} por pendência prévia; solicitação enviada "
                            f"com sucesso na 2ª tentativa."
                        )
                    df.to_csv(csv_path, index=False)
                    print(f"CSV atualizado com o número da solicitação: {numero_solicitacao}")
                    logging.info(f"CSV atualizado com o número da solicitação: {numero_solicitacao}")

                elif status == STATUS_PENDENTE:
                    erro_msg = "O paciente já possui uma solicitação pendente para o procedimento."
                    if procedimento_substituido:
                        erro_msg += (
                            f" Também tentado com procedimento substituto {procedimento_usado} "
                            f"(clínica {tipo_clinica_retry}), sem sucesso."
                        )
                    print(f"⚠️  {erro_msg}")
                    logging.warning(f"Registro {index + 1}: {erro_msg}")

                    if 'erro' not in df.columns:
                        df['erro'] = ''

                    df.at[index, 'erro'] = erro_msg
                    df.to_csv(csv_path, index=False)
                    print(f"Erro registrado no CSV: {erro_msg}")
                    logging.info(f"Erro registrado no CSV para registro {index + 1}: {erro_msg}")

                elif status == STATUS_CNS_NAO_ENCONTRADO:
                    erro_msg = "CNS incorreto ou não encontrado na base do DATASUS"
                    print(f"⚠️  {erro_msg}")
                    logging.warning(f"Registro {index + 1}: {erro_msg}")

                    if 'erro' not in df.columns:
                        df['erro'] = ''

                    df.at[index, 'erro'] = erro_msg
                    df.to_csv(csv_path, index=False)
                    print(f"Erro registrado no CSV: {erro_msg}")
                    logging.info(f"Erro registrado no CSV para registro {index + 1}: {erro_msg}")

                    navegador.switch_to.default_content()
                    continue  # Pula para o próximo registro

                elif status == STATUS_ERRO_DESCONHECIDO:
                    print("❌ Número da solicitação não encontrado e nenhuma mensagem de erro conhecida detectada")
                    logging.error(f"Registro {index + 1}: Número da solicitação não encontrado")

                navegador.switch_to.default_content()
                print(f"Registro {index + 1} processado com sucesso!")
                time.sleep(3)  # Dar tempo para o sistema processar antes do próximo registro
            except Exception as e:
                print(f"Erro ao processar registro {index + 1}: {str(e)}")
                logging.error(f"Erro ao processar registro {index + 1}: {str(e)}")

                # Tenta capturar o texto do alert se houver
                erro_texto = str(e)
                if "Alert Text" in erro_texto:
                    try:
                        # Extrai o texto do alert da mensagem de erro
                        inicio = erro_texto.find("Alert Text : ") + len("Alert Text : ")
                        fim = erro_texto.find("}", inicio)
                        if fim == -1:
                            fim = erro_texto.find("\n", inicio)
                        alert_text = erro_texto[inicio:fim].strip()

                        # Cria a coluna 'erro' se não existir
                        if 'erro' not in df.columns:
                            df['erro'] = ''

                        # Cria a coluna 'revisar' se não existir
                        if 'revisar' not in df.columns:
                            df['revisar'] = ''

                        # Atualiza o CSV com o erro e marca para revisão
                        df.at[index, 'erro'] = alert_text
                        df.at[index, 'revisar'] = 'sim'
                        df.to_csv(csv_path, index=False)
                        print(f"Erro registrado no CSV: {alert_text}")
                        logging.info(f"Erro registrado no CSV para registro {index + 1}: {alert_text}")
                    except Exception as ex:
                        print(f"Erro ao tentar extrair texto do alert: {str(ex)}")
                        logging.error(f"Erro ao tentar extrair texto do alert: {str(ex)}")

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
