import os
import time
import pandas as pd
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.logging import setup_logging
import logging

def solicita_pre_aih():
    
    print("\n---===> AJUSTA SOLICITAÇÕES E EXTRAI LINK DE AIH DO GHOSP <===---")
    
    # Configuração dos diretórios e arquivos
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_solicita = os.path.join(user_dir, 'solicita_inf_aih.csv')
    csv_internados = os.path.join(user_dir, 'internados_ghosp_avancado.csv')
    
    # Passo 1: Limpar solicita_inf_aih.csv mantendo apenas o cabeçalho
    print("\n📋 Etapa 1: Preparando arquivo solicita_inf_aih.csv...")
    try:
        # Verifica se o arquivo existe para pegar o cabeçalho
        if os.path.exists(csv_solicita):
            df_solicita = pd.read_csv(csv_solicita)
            colunas = df_solicita.columns.tolist()
            print(f"   ✅ Arquivo encontrado com colunas: {', '.join(colunas)}")
        else:
            # Se não existe, cria com colunas padrão
            colunas = ['ra', 'link']
            print(f"   ⚠️  Arquivo não encontrado, criando com colunas padrão: {', '.join(colunas)}")
        
        # Cria DataFrame vazio com apenas o cabeçalho
        df_solicita_limpo = pd.DataFrame(columns=colunas)
        df_solicita_limpo.to_csv(csv_solicita, index=False)
        print(f"   ✅ Arquivo limpo (mantido apenas cabeçalho)")
        
    except Exception as e:
        print(f"   ❌ Erro ao limpar solicita_inf_aih.csv: {e}")
        return None
    
    # Passo 2: Extrair dados de internados_ghosp_avancado.csv
    print("\n📋 Etapa 2: Extraindo dados de internados_ghosp_avancado.csv...")
    try:
        if not os.path.exists(csv_internados):
            print(f"   ❌ Arquivo internados_ghosp_avancado.csv não encontrado em ~/AutoReg")
            return None
        
        df_internados = pd.read_csv(csv_internados)
        
        if 'internacao' not in df_internados.columns:
            print(f"   ❌ Coluna 'internacao' não encontrada no arquivo internados_ghosp_avancado.csv")
            print(f"   📄 Colunas disponíveis: {', '.join(df_internados.columns.tolist())}")
            return None
        
        # Extrai apenas os dados da coluna 'internacao' (removendo valores vazios/NaN)
        solicitacoes = df_internados['internacao'].dropna()
        total_solicitacoes = len(solicitacoes)
        print(f"   ✅ Encontradas {total_solicitacoes} internações")
        
    except Exception as e:
        print(f"   ❌ Erro ao ler internados_ghosp_avancado.csv: {e}")
        return None
    
    # Passo 3: Transferir dados para solicita_inf_aih.csv
    print("\n📋 Etapa 3: Transferindo dados para solicita_inf_aih.csv...")
    try:
        # Garante que a coluna 'ra' existe
        if 'ra' not in df_solicita_limpo.columns:
            df_solicita_limpo['ra'] = ''
        
        # Cria DataFrame com os dados da coluna 'internacao' na coluna 'ra'
        df_solicita_limpo['ra'] = solicitacoes.values
        
        # Garante que a coluna 'link' existe
        if 'link' not in df_solicita_limpo.columns:
            df_solicita_limpo['link'] = ''
        
        # Salva o arquivo atualizado
        df_solicita_limpo.to_csv(csv_solicita, index=False)
        print(f"   ✅ {total_solicitacoes} registros transferidos com sucesso")
        print(f"   📄 Arquivo salvo: {csv_solicita}")
        
    except Exception as e:
        print(f"   ❌ Erro ao transferir dados: {e}")
        return None
    
    print("\n✅ Preparação de arquivos concluída com sucesso!\n")
        
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    # Inicializa o navegador (Chrome)
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    # Acesse a página de login do G-HOSP na porta 4002
    url_login = f"{caminho_ghosp}:4002/users/sign_in"
    driver.get(url_login)

    # Localiza e preenche o campo de e-mail
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

    print("Login realizado com sucesso!")
    # Localiza o menu dropdown e passa o mouse para abrir
    from selenium.webdriver.common.action_chains import ActionChains

    # Configuração dos diretórios e arquivos
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'solicita_inf_aih.csv')
    
    # Relê o arquivo CSV atualizado para processamento
    df = None

    try:
        df = pd.read_csv(csv_path)
        if 'ra' not in df.columns:
            print("❌ Arquivo CSV não contém a coluna 'ra'")
            driver.quit()
            return None
        
        # Adiciona coluna 'link' se não existir
        if 'link' not in df.columns:
            df['link'] = ''
            
    except FileNotFoundError:
        print("❌ Arquivo solicita_inf_aih.csv não encontrado em ~/AutoReg")
        driver.quit()
        return None

    # Itera sobre os registos de atendimento do CSV usando índices
    total_registros = len(df)
    for i in range(total_registros):
        try:
            # Converte ra para inteiro para remover o .0
            ra = int(df.at[i, 'ra'])
            print(f"\nProcessando registro {i + 1}/{total_registros}: {ra}")
            driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
            
            #desenvolvimento
            print(f"⏳ Aguardando interação do usuário para o registro {ra}...")
            print("   O usuário deve clicar no link desejado, fazer as alterações necessárias.")
            print("   💡 Comandos disponíveis:")
            print("      Digite 's' e pressione Enter - Salvar URL atual e avançar")
            print("      Digite 'p' e pressione Enter - Pular (remover linha) e avançar")
            
            try:
                # Aguarda input do usuário
                comando = input("   👉 Digite o comando (s/p): ").strip().lower()
                
                if comando == 's':
                    # Salvar URL atual
                    url_atual = driver.current_url
                    print(f"   📍 URL capturada: {url_atual}")
                    
                    df.at[i, 'link'] = url_atual
                    df.to_csv(csv_path, index=False)
                    print(f"   ✅ Link salvo no CSV para o registro {ra}")

                    # Clica no botão Gravar (com ID dinâmico)
                    try:
                        # Busca o botão usando XPath que aceita qualquer número no ID
                        botao_gravar = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//form[starts-with(@id, "edit_formeletronico_")]/div[2]/input'))
                        )
                        botao_gravar.click()
                        print(f"   ✅ Botão 'Gravar' clicado automaticamente")
                        time.sleep(1)  # Aguarda um momento para processar
                    except Exception as e:
                        print(f"   ⚠️  Não foi possível clicar no botão 'Gravar': {e}")
                
                elif comando == 'p':
                    # Pular (remover linha)
                    print(f"   🗑️  Removendo linha do registro {ra}")
                    df = df.drop(index=i).reset_index(drop=True)
                    df.to_csv(csv_path, index=False)
                    print(f"   ✅ Linha removida do CSV")
                
                else:
                    print(f"   ⚠️  Comando inválido '{comando}' - pulando registro sem alterar CSV")
                
            except KeyboardInterrupt:
                print("\n   ⚠️  Operação cancelada pelo usuário (Ctrl+C)")
                raise
            except Exception as e:
                print(f"   ⚠️ Erro ao processar comando: {e}")

        
        except Exception as e:
            print(f"❌ Erro ao processar o registro: {e}")
            continue