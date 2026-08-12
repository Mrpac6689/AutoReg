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
from autoreg.sessao_sisreg import (
    login_sisreg,
    garantir_sessao_sisreg,
    ControleSessao,
    SessaoSisregAbortada,
)
from datetime import datetime
import logging

def executa_alta_avancado():
    print("Executando alta avançada...")

    navegador = None
    try:
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)

        # Le as credenciais SISREG desta rotina (conta principal [SISREG])
        # ANTES do loop, para que o re-login use a credencial correta.
        print("Lendo credenciais do SISREG...")
        logging.info("Lendo credenciais do SISREG...")
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()

        print("Realizando login no SISREG...")
        logging.info("Realizando login no SISREG...")
        login_sisreg(navegador, usuario_sisreg, senha_sisreg)
        print("Login realizado com sucesso!")
        logging.info("Login realizado com sucesso!")

        # Controle global de re-logins desta rotina (aborta ao passar do teto)
        controle = ControleSessao()

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
            "ADMINISTRATIVO": "38"
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
                url_saida = "https://sisregiii.saude.gov.br/cgi-bin/config_saida_permanencia"
                navegador.get(url_saida)
                time.sleep(2)

                # Se a sessão foi finalizada pelo servidor, refaz o login e
                # re-navega para esta mesma página antes de processar o item.
                while garantir_sessao_sisreg(navegador, url_saida, usuario_sisreg, senha_sisreg, controle):
                    pass

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
                valor_motivo = "38" # Default: ALTA MELHORADO
                
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

    except SessaoSisregAbortada as e:
        print(f"⛔ Rotina de alta abortada: {e}")
        logging.error(f"Rotina de alta abortada por conflito de sessao: {e}")
    except Exception as e:
        print(f"❌ Erro geral no loop de alta: {str(e)}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
