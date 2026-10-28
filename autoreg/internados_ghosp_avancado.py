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
import logging
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


# Relatório rc001 com 0 internados nunca é real (o hospital tem ~200+):
# indica relatório vazio/quebrado, e seguir com ele não solicitaria ninguém.
MIN_INTERNADOS = 1


def _salvar_diagnostico(driver, user_dir):
    """Salva URL, screenshot e HTML da página em que o -iga falhou.

    Nas falhas de 13/10 e 28/10/2026 todas as etapas do G-HOSP falharam por
    horas com durações fixas (login?), e o print() do cron já tinha sido
    sobrescrito; sem a página não dava para saber onde travou.
    """
    if driver is None:
        return
    base = os.path.join(user_dir, 'diagnostico', f"iga_{time.strftime('%Y%m%d_%H%M%S')}")
    try:
        os.makedirs(os.path.dirname(base), exist_ok=True)
        logging.error(f"-iga: página na falha: {driver.current_url!r} (título {driver.title!r})")
        driver.save_screenshot(base + '.png')
        with open(base + '.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logging.error(f"-iga: screenshot e HTML salvos em {base}.png/.html")
    except Exception as e:
        logging.error(f"-iga: não foi possível salvar diagnóstico: {e}")


def internados_ghosp_avancado():
    """Baixa o rc001 (internados por setor) e grava ~/AutoReg/internados_ghosp_avancado.csv.

    Falha fechada: o CSV anterior é apagado antes de começar e qualquer falha
    lança exceção. Até 28/10/2026 os erros eram só print()ados e a etapa
    "concluía" sem regravar o CSV. Como -std sobrescreve esse mesmo arquivo com
    os registros que filtrou, -ign/-std/-spaa reprocessavam a lista da rodada
    anterior e nenhum paciente internado depois dela era solicitado (13/10 e
    28/10, sempre com a etapa levando ~134s).
    """
    print("\n---===> EXTRAÇÃO DE INTERNADOS <===---")
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    caminho_novo_arquivo = os.path.join(user_dir, 'internados_ghosp_avancado.csv')
    print(f"Diretório de download configurado: {user_dir}")

    if os.path.exists(caminho_novo_arquivo):
        os.remove(caminho_novo_arquivo)
        logging.info("-iga: internados_ghosp_avancado.csv anterior removido")
    # Relatórios brutos antigos: com eles o Chrome salva o novo como "... (1).csv"
    for arquivo in os.listdir(user_dir):
        if arquivo.startswith('_home_inovadora') and arquivo.lower().endswith('.csv'):
            os.remove(os.path.join(user_dir, arquivo))

    driver = None
    try:
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        print("Iniciando o Chromedriver...")
        logging.info("-iga: Chrome iniciado, abrindo login do G-HOSP")

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
        # Ao logar, o G-HOSP sai de /users/sign_in
        WebDriverWait(driver, 20).until(lambda d: "/users/sign_in" not in d.current_url)
        print("Login realizado com sucesso!")
        logging.info("-iga: login confirmado, abrindo relatório rc001")

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
        logging.info("-iga: relatório solicitado, aguardando download do CSV")
        
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
                    
                    # Filtra apenas CSVs cujo nome começa com "_home_inovadora"
                    # (padrão do relatório G-HOSP), ignorando .crdownload e outros CSVs
                    if (arquivo.lower().endswith('.csv') and
                        arquivo.startswith('_home_inovadora') and
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

        if not arquivo_recente:
            raise RuntimeError(f"download do rc001 não chegou em {max_tentativas * 5}s")
        logging.info(f"-iga: CSV baixado ({os.path.basename(arquivo_recente)}), processando")

        # Carregar o arquivo CSV recém-baixado
        original_df = pd.read_csv(arquivo_recente, header=None, dtype=str)

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

        if len(dados_extraidos) < MIN_INTERNADOS:
            raise RuntimeError(f"rc001 sem internados ({len(dados_extraidos)} registro(s) extraído(s))")

        # Converte a lista de dados extraídos para um DataFrame
        dados_df = pd.DataFrame(dados_extraidos)
        dados_df.to_csv(caminho_novo_arquivo, index=False)
        
        print(f"Nomes extraídos e salvos em {caminho_novo_arquivo}.")
        logging.info(f"-iga: {len(dados_df)} internado(s) gravado(s) em internados_ghosp_avancado.csv")

    except Exception as e:
        # Propaga: executar_funcao() marca a etapa como falha e o -aihs para
        # antes de -ign/-std rodarem sem lista de internados.
        print(f"Ocorreu um erro: {e}")
        logging.exception(f"-iga: falha na extração de internados: {e}")
        _salvar_diagnostico(driver, user_dir)
        raise
    finally:
        if driver is not None:
            driver.quit()
