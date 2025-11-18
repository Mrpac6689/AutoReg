import os
import time
import pandas as pd
import sys
import signal
import configparser
import threading
import select
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Variável global para controlar pausa
paused = False
pause_lock = threading.Lock()

def keyboard_listener():
    """Thread que escuta comandos do teclado sem bloquear a execução"""
    global paused
    print("💡 Pressione 'P' + ENTER para PAUSAR | 'C' + ENTER para CONTINUAR\n")
    
    while True:
        try:
            # Ler input de forma não-bloqueante
            comando = input().strip().upper()
            
            if comando == 'P':
                if not paused:
                    with pause_lock:
                        paused = True
                    print("\n⏸️  EXECUÇÃO PAUSADA")
                    print("💡 Digite 'C' + ENTER para retomar\n")
                else:
                    print("⚠️  Já está pausado\n")
                    
            elif comando == 'C':
                if paused:
                    with pause_lock:
                        paused = False
                    print("\n▶️  RETOMANDO EXECUÇÃO...\n")
                else:
                    print("⚠️  Não está pausado\n")
                    
        except EOFError:
            break
        except Exception:
            pass

def setup_pause_handler():
    """Inicia a thread de escuta do teclado"""
    listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
    listener_thread.start()

def producao_ambulatorial_dados():
    
    print("\n---===> EXTRAÇÃO DE DADOS DE PRODUÇÃO AMBULATORIAL - SISREG <===---")
    
    # Configurar handler de pausa
    setup_pause_handler()
    
    # Definir diretório e caminho do CSV
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'producao_ambulatorial.csv')
    
    # Ler credenciais
    config = configparser.ConfigParser()
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # Script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG-REG']['usuarioreg']
    senha_sisreg = config['SISREG-REG']['senhareg']
        
    # Inicializar o driver
    print("🌐 Iniciando navegador...")
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Fazer login no GHOSP
        url_login = "https://sisregiii.saude.gov.br"
        print(f"🔐 Acessando SISREG: {url_login}")
        driver.get(url_login)
                
        # Realizar login
        try:
            print("Localizando campo de usuário...")
            usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
            print("Campo de usuário localizado.")

            print("Localizando campo de senha...")
            senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
            print("Campo de senha localizado.")         

            print("Preenchendo usuário...")
            usuario_field.send_keys(usuario_sisreg)
            print("Usuário preenchido.")

            print("Preenchendo senha...")
            senha_field.send_keys(senha_sisreg)
            print("Senha preenchida.")

            print("Aguardando antes de clicar no botão de login...")
            time.sleep(1)

            print("Localizando botão de login...")
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
            print("Botão de login localizado.")

            print("Clicando no botão de login...")
            login_button.click()
            print("Botão de login clicado.")
            
        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            driver.quit()
            return
               
        # Aguardar página carregar
        time.sleep(2)

        # Ler o CSV com os códigos de solicitação
        print(f"\n📂 Lendo arquivo: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"❌ Arquivo não encontrado: {csv_path}")
            print("⚠️  Execute primeiro a função 'producao_ambulatorial' para gerar o arquivo.")
            driver.quit()
            return
        
        df = pd.read_csv(csv_path, dtype=str)
        
        if 'solicitacao' not in df.columns:
            print(f"❌ Coluna 'solicitacao' não encontrada no CSV")
            driver.quit()
            return
        
        total_solicitacoes = len(df)
        print(f"📊 Total de solicitações a processar: {total_solicitacoes}\n")
        
        # Loop pelos códigos de solicitação
        dados_extraidos = []
        
        for idx, row in df.iterrows():
            # Verificar se está pausado
            while paused:
                time.sleep(0.5)
            
            codigo = str(row['solicitacao']).strip()
            
            print(f"\n[{idx + 1}/{total_solicitacoes}] 🔍 Processando solicitação: {codigo}")
            
            try:
                # Acessar diretamente a página da solicitação
                url_solicitacao = f"https://sisregiii.saude.gov.br/cgi-bin/gerenciador_solicitacao?etapa=VISUALIZAR_FICHA&co_solicitacao={codigo}&co_seq_solicitacao={codigo}&ordenacao=2&pagina=0"
                driver.get(url_solicitacao)
                print(f"  ✓ Acessando página da solicitação")
                
                # Aguardar página carregar
                time.sleep(2)
                
                # Extrair dados da página
                try:
                    # Data
                    data_element = driver.find_element(By.XPATH, '//*[@id="fichaAmbulatorial"]/table/tbody[3]/tr[5]/td[4]')
                    data = data_element.text.strip()
                    
                    # Solicitante
                    solicitante_element = driver.find_element(By.XPATH, '//*[@id="fichaAmbulatorial"]/table/tbody[2]/tr[3]/td[3]')
                    solicitante = solicitante_element.text.strip()
                    
                    # Autorizador
                    autorizador_element = driver.find_element(By.XPATH, '//*[@id="fichaAmbulatorial"]/table/tbody[3]/tr[3]/td[3]')
                    autorizador = autorizador_element.text.strip()
                    
                    # Executante
                    executante_element = driver.find_element(By.XPATH, '//*[@id="fichaAmbulatorial"]/table/tbody[3]/tr[3]/td[1]')
                    executante = executante_element.text.strip()
                    
                    # Procedimento
                    procedimento_element = driver.find_element(By.XPATH, '//*[@id="fichaAmbulatorial"]/table/tbody[11]/tr[2]/td[1]')
                    procedimento = procedimento_element.text.strip()
                    
                    # Adicionar dados extraídos
                    dados_extraidos.append({
                        'solicitacao': codigo,
                        'data': data,
                        'solicitante': solicitante,
                        'autorizador': autorizador,
                        'executante': executante,
                        'procedimento': procedimento
                    })
                    
                    print(f"  ✓ Dados extraídos com sucesso")
                    print(f"    Data: {data}")
                    print(f"    Solicitante: {solicitante}")
                    print(f"    Autorizador: {autorizador}")
                    print(f"    Executante: {executante}")
                    print(f"    Procedimento: {procedimento[:50]}..." if len(procedimento) > 50 else f"    Procedimento: {procedimento}")
                    
                except NoSuchElementException as e:
                    print(f"  ⚠️  Erro ao extrair dados: elemento não encontrado - {e}")
                except Exception as e:
                    print(f"  ⚠️  Erro ao extrair dados: {e}")
                
            except Exception as e:
                print(f"  ❌ Erro ao processar solicitação {codigo}: {e}")
                continue
        
        print(f"\n✅ Processamento concluído!")
        print(f"📊 Total processado: {len(dados_extraidos)} registros")
        
        # Salvar dados em CSV
        if dados_extraidos:
            csv_saida = os.path.join(user_dir, 'producao_ambulatorial_dados.csv')
            df_saida = pd.DataFrame(dados_extraidos)
            df_saida.to_csv(csv_saida, index=False)
            print(f"\n✅ Dados salvos em: {csv_saida}")
            print(f"📊 Colunas: {list(df_saida.columns)}")
        else:
            print("\n⚠️  Nenhum dado foi extraído")

    finally:
        # Fechar navegador
        print("\n🔒 Fechando navegador...")
        driver.quit()
