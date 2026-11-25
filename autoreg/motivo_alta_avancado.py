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
from autoreg.justificativa_ghosp import tratar_justificativa_acesso
from datetime import datetime
import logging

# Acima desta fração de erros, o problema é da rodada (sessão, layout), não do
# paciente: em 24/11/2026 os 86 RAs deram erro e o ciclo terminou com 0 altas, sem aviso.
FRACAO_FALHA_EM_MASSA = 0.5
MINIMO_FALHA_EM_MASSA = 5


def texto_resumo_valido(texto):
    """
    Texto do resumo de alta sem o rótulo do botão "INSERIR", que a seção exibe
    quando NÃO há resumo (RA 669835 foi lido como alta em 24/11/2026).
    """
    linhas = [l.strip() for l in str(texto or '').splitlines()]
    limpo = '\n'.join(l for l in linhas if l and l.upper() != 'INSERIR')
    return limpo if len(limpo) >= 5 else ''


def falha_em_massa(erros, verificados):
    return verificados >= MINIMO_FALHA_EM_MASSA and erros / verificados >= FRACAO_FALHA_EM_MASSA


def motivo_alta_avancado():
    print("\n---===> ACESSO AO GHOSP <===---")
    driver = None 
    
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg = ler_credenciais()
        
        # Caminho para salvar o novo arquivo baixado
        user_dir = os.path.expanduser('~/AutoReg')
        print(f"Diretório de download configurado: {user_dir}")
        
        # Inicializa o navegador
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        print("Iniciando o Chromedriver...")

        # Acesse a página de login do G-HOSP
        driver.get(caminho_ghosp + ':4002/users/sign_in')
        
        # Definir tamanho da janela explicitamente (evita problemas com maximize no Docker/Kasm)
        print("Configurando tamanho da janela para 1920x1080...")
        driver.set_window_size(1920, 1080)
        time.sleep(2)

        # Realiza o login
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
        time.sleep(5)
        print("Login realizado com sucesso!")

        # Loop para processar cada linha do CSV
        csv_path = os.path.join(user_dir, 'internados_sisreg.csv')
        if not os.path.exists(csv_path):
            print(f"Erro: Arquivo {csv_path} não encontrado.")
            return

        print(f"Lendo CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        # Garante que as novas colunas existam
        for col in ['situacao', 'motivo_alta', 'medico_alta', 'data_alta', 'tipo_saida']:
            if col not in df.columns:
                df[col] = ''

        verificados = erros = 0
        for index, row in df.iterrows():
            ra = str(row['RA']).strip()
            # Remove '.0' se o RA tiver sido interpretado como float
            if ra.endswith('.0'):
                ra = ra[:-2]
            
            if not ra or ra == 'nan':
                print(f"[{index}] RA não encontrado para {row.get('Nome', 'paciente')}, pulando...")
                continue

            print(f"\n🔍 [{index+1}/{len(df)}] Verificando RA: {ra} ({row.get('Nome', 'N/A')})")
            
            verificados += 1
            try:
                # Navega para a página de alta do internado
                url_alta = f"{caminho_ghosp}:4002/pr/altas?intern_id={ra}"
                driver.get(url_alta)
                time.sleep(1.5)

                # Paciente em alta: o GHOSP redireciona para a página de
                # justificativa de acesso. Preenche/envia e re-navega para a
                # página de alta, agora com o acesso liberado.
                if tratar_justificativa_acesso(driver):
                    driver.get(url_alta)
                    time.sleep(1.5)

                # Localiza a seção de "Resumo de alta"
                # A div de conteúdo tem a classe 'cor-sec03' e é precedida pelo título 'Resumo de alta'
                try:
                    resumo_content = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-content.cor-sec03"))
                    )
                    
                    # Verifica se há conteúdo na seção
                    # Pode-se verificar se há texto relevante ou se existem campos preenchidos
                    texto_resumo = texto_resumo_valido(resumo_content.text)
                    
                    if not texto_resumo:
                        print(f"   ℹ️ Sem resumo de alta. Segue internado.")
                        df.at[index, 'situacao'] = 'Segue internado'
                    else:
                        print(f"   ✅ Alta encontrada!")
                        df.at[index, 'situacao'] = 'Alta'
                        
                        # Captura Motivo de Cobrança:
                        try:
                            # A busca é pelo label com for="Motivo_Cobran_a" e pega o próximo div de valor
                            motivo_el = driver.find_element(By.XPATH, "//label[@for='Motivo_Cobran_a']/following-sibling::div")
                            df.at[index, 'motivo_alta'] = motivo_el.text.strip()
                        except:
                            pass
                            
                        # Atendimento de PS/retorno usa outro layout ("Tipo de saída").
                        # NÃO vira motivo_alta: é a saída do retorno, não da internação
                        # (24/11/2026: 4 "evasões" de retorno; internações MELHORADO).
                        # Serve só às travas do coringa no -eaa.
                        tipo_el = resumo_content.find_elements(By.XPATH, ".//div[contains(@class,'dcampo')][normalize-space()='Tipo de saída']/following-sibling::div[contains(@class,'vcampo')]")
                        if tipo_el:
                            df.at[index, 'tipo_saida'] = tipo_el[0].text.strip()

                        # Captura Médico:
                        try:
                            medico_el = driver.find_element(By.XPATH, "//label[@for='medico']/following-sibling::div")
                            df.at[index, 'medico_alta'] = medico_el.text.strip()
                        except:
                            pass
                            
                        # Captura Alta médica:
                        try:
                            # O label para a data de alta médica tem for="resumoalta"
                            data_el = driver.find_element(By.XPATH, "//label[@for='resumoalta']/following-sibling::div")
                            df.at[index, 'data_alta'] = data_el.text.strip()
                        except:
                            pass
                        
                        print(f"      📝 Motivo: {df.at[index, 'motivo_alta']}")
                        print(f"      🩺 Médico: {df.at[index, 'medico_alta']}")
                        print(f"      📅 Data: {df.at[index, 'data_alta']}")

                except Exception as e:
                    print(f"   ⚠️ Erro ao verificar seção de resumo: {str(e)}")
                    df.at[index, 'situacao'] = 'Erro ao verificar'
                    erros += 1
                
                # Salva a cada linha para evitar perdas em caso de erro no meio do processo
                df.to_csv(csv_path, index=False)

            except Exception as e:
                print(f"   ❌ Erro ao processar paciente {ra}: {str(e)}")
                df.at[index, 'situacao'] = 'Erro ao verificar'
                erros += 1

        df.to_csv(csv_path, index=False)
        logging.info(f"-maa: {verificados} RA(s) verificado(s), {erros} com erro")
        if falha_em_massa(erros, verificados):
            raise RuntimeError(f"falha em massa: {erros} de {verificados} RAs com erro ao verificar a alta")
        print("\n✅ Processamento concluído!")


    except Exception as e:
        print(f"Erro ao processar o CSV: {str(e)}")
        raise  # sem isto a etapa "concluía" e o -eaa rodava sobre nada, em silêncio
    finally:
        if driver:
            driver.quit()

