import os
import time
import pandas as pd
import traceback
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.chrome_options import get_chrome_options
from autoreg.detecta_capchta import detecta_captcha
from datetime import datetime
import logging

def executa_alta_avancado():
    print("Executando alta avançada...")

    navegador = None
    try:
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)
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
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()
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
        
        # Navegação para a página de controle de saída
        print("Iniciando loop de processamento de altas...")
        csv_path = os.path.expanduser('~/AutoReg/internados_sisreg.csv')
        if not os.path.exists(csv_path):
            print(f"❌ Arquivo {csv_path} não encontrado.")
            return

        df = pd.read_csv(csv_path)
        
        # Garante a existência da coluna de resultado
        if 'resultado_sisreg' not in df.columns:
            df['resultado_sisreg'] = ''

        # Filtra apenas registros com situacao 'Alta'
        altas_pendentes = df[df['situacao'] == 'Alta']
        
        if altas_pendentes.empty:
            print("ℹ️ Nenhuma alta pendente encontrada no CSV.")
            return

        print(f"📋 Encontradas {len(altas_pendentes)} altas para processar.")

        # Mapeamento simplificado de motivos para facilitar a busca
        # O script tentará encontrar substring desses termos no 'motivo_alta' vindo do GHOSP
        mapa_motivos = {
            "CURADO": "37",
            "MELHORADO": "38",
            "PEDIDO": "40",
            "EVASAO": "42",
            "TRANSFERIDO": "53",
            "OBITO": "54",
            "ADMINISTRATIVO": "57"
        }

        for index, row in altas_pendentes.iterrows():
            # Verifica se há CAPTCHA antes de cada alta
            resultado_captcha = detecta_captcha(navegador)
            if resultado_captcha != 'ok':
                print(f"CAPTCHA não resolvido ({resultado_captcha}). Abortando altas.")
                logging.error(f"Altas abortadas por CAPTCHA não resolvido: {resultado_captcha}")
                break

            # Pula se a alta já foi efetivada
            if str(row.get('resultado_sisreg', '')).strip() == "Alta efetivada":
                print(f"⏩ [{index+1}] Pulando solicitação {row.get('solicitacao_sisreg')}: Já efetivada.")
                continue

            solicitacao = str(row['solicitacao_sisreg']).split('.')[0] # Remove .0 se houver
            motivo_ghosp = str(row['motivo_alta']).upper()
            
            print(f"\n🚀 [{index+1}] Processando Solicitação: {solicitacao} | Motivo GHOSP: {motivo_ghosp}")
            
            try:
                # 1. Navega para a página de Saída de Permanência
                navegador.get("https://sisregiii.saude.gov.br/cgi-bin/config_saida_permanencia")
                time.sleep(2)

                        
                # Clica no botão "PESQUISAR"
                print("Tentando localizar o botão PESQUISAR dentro do iframe...")
                logging.info("Tentando localizar o botão PESQUISAR dentro do iframe...")
                pesquisar_button = WebDriverWait(navegador, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
                )
                
                print("Botão PESQUISAR encontrado!")
                logging.info("Botão PESQUISAR encontrado!")
                pesquisar_button.click()
                print("Botão PESQUISAR clicado!")
                logging.info("Botão PESQUISAR clicado!")
                
                # 2. Executa a função JS configFicha(n) na tela de pesquisa
                print(f"   Carregando ficha: {solicitacao}...")
                navegador.execute_script(f"configFicha('{solicitacao}')")
                time.sleep(3)
                
                # 3. Seleciona o motivo baseado no texto do GHOSP
                valor_motivo = "57" # Default: ENCERRAMENTO ADMINISTRATIVO
                
                for chave, codigo in mapa_motivos.items():
                    if chave in motivo_ghosp:
                        valor_motivo = codigo
                        print(f"   Motivo mapeado: {chave} -> {codigo}")
                        break
                
                try:
                    # Seleciona no dropdown
                    select_motivo = Select(wait.until(EC.presence_of_element_located((By.NAME, "co_motivo"))))
                    select_motivo.select_by_value(valor_motivo)
                    print(f"   Opção selecionada no SISREG: {valor_motivo}")
                    time.sleep(1)
                    
                    # 4. Clica em "Efetua Saída"
                    botao_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                    botao_saida.click()
                    print("   Clicado em Efetua Saída.")
                    
                    # 5. Lida com pop-ups de confirmação
                    time.sleep(2)
                    try:
                        while True:
                            alert = navegador.switch_to.alert
                            print(f"   Confirmando alerta: {alert.text}")
                            alert.accept()
                            time.sleep(1)
                    except:
                        # Sai do loop quando não houver mais alertas
                        pass
                    
                    # 6. Atualiza o CSV
                    df.at[index, 'resultado_sisreg'] = 'Alta efetivada'
                    print("   ✅ Alta efetivada com sucesso!")
                    
                except Exception as e:
                    print(f"   ❌ Erro durante preenchimento da ficha: {str(e)}")
                    df.at[index, 'resultado_sisreg'] = f'Erro: {str(e)[:50]}'
                
                # Salva progresso no CSV
                df.to_csv(csv_path, index=False)
                
            except Exception as e:
                print(f"   ❌ Erro ao navegar/carregar paciente: {str(e)}")

        print("\n🏁 Processamento de altas finalizado.")

    except Exception as e:
        print(f"❌ Erro geral no loop de alta: {str(e)}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
