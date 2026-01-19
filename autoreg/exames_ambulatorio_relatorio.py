import os
import csv
import time
import json
import base64
import glob
import pandas as pd
import configparser
from PyPDF2 import PdfMerger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from datetime import datetime, timedelta

def exames_ambulatorio_relatorio():
    print("Relatório de exames ambulatoriais")

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
    usuario_sisreg = config['SISREG-REG']['usuarioreg']
    senha_sisreg = config['SISREG-REG']['senhareg']
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
    
    # Função auxiliar para verificar e resolver CAPTCHA
    def verificar_e_resolver_captcha():
        """Verifica se há CAPTCHA na página e tenta resolvê-lo"""
        try:
            # Verifica se há texto sobre CAPTCHA na página ou o elemento g-recaptcha
            try:
                # Verifica se existe o div com class g-recaptcha
                div_recaptcha = navegador.find_element(By.XPATH, "//div[@class='g-recaptcha']")
                print("   ⚠️  Página de CAPTCHA detectada. Tentando resolver...")
            except NoSuchElementException:
                # Verifica pelo texto da página
                page_text = navegador.find_element(By.TAG_NAME, "body").text
                if "CAPTCHA" not in page_text and "requisições" not in page_text.lower():
                    return False
                print("   ⚠️  Página de CAPTCHA detectada (por texto). Tentando resolver...")
            
            # Tenta encontrar o iframe do reCAPTCHA (o primeiro iframe dentro do div g-recaptcha)
            try:
                # Aguarda o iframe do reCAPTCHA aparecer (iframe com title="reCAPTCHA" dentro do div g-recaptcha)
                iframe_captcha = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@class='g-recaptcha']//iframe[@title='reCAPTCHA']"
                )))
                print("   ✅ Iframe do reCAPTCHA encontrado.")
                
                # Troca para o iframe do reCAPTCHA
                navegador.switch_to.frame(iframe_captcha)
                
                # Clica no checkbox do reCAPTCHA (dentro do iframe)
                print("   Clicando no checkbox do reCAPTCHA...")
                # O checkbox geralmente está em um span com id ou classe específica
                checkbox_captcha = wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//span[@class='recaptcha-checkbox-border'] | //span[@id='recaptcha-anchor'] | //div[@class='recaptcha-checkbox-border']"
                )))
                checkbox_captcha.click()
                print("   ✅ Checkbox do reCAPTCHA clicado.")
                
                # Volta para o frame principal
                navegador.switch_to.default_content()
                
                # Aguarda o CAPTCHA ser resolvido (pode demorar alguns segundos)
                print("   Aguardando resolução do CAPTCHA...")
                time.sleep(8)  # Aguarda mais tempo para o CAPTCHA ser processado
                
                # Verifica se o textarea g-recaptcha-response foi preenchido (indica que foi resolvido)
                try:
                    response_textarea = navegador.find_element(By.ID, "g-recaptcha-response")
                    if response_textarea.get_attribute("value"):
                        print("   ✅ CAPTCHA resolvido (resposta detectada).")
                    else:
                        print("   ⚠️  Aguardando resolução do CAPTCHA...")
                        time.sleep(5)  # Aguarda mais um pouco
                except:
                    pass
                
                # Clica no botão Confirmar (usando o name="btnConfirmar" do HTML fornecido)
                print("   Localizando botão Confirmar...")
                botao_confirmar = wait.until(EC.element_to_be_clickable((
                    By.NAME, "btnConfirmar"
                )))
                botao_confirmar.click()
                print("   ✅ Botão Confirmar clicado.")
                
                # Aguarda a página redirecionar após confirmar
                time.sleep(3)
                print("   ✅ CAPTCHA resolvido com sucesso!")
                return True
                
            except TimeoutException:
                print("   ⚠️  Iframe do reCAPTCHA não encontrado. Tentando método alternativo...")
                # Método alternativo: tenta encontrar o iframe por qualquer padrão
                try:
                    iframe_captcha = wait.until(EC.presence_of_element_located((
                        By.XPATH,
                        "//iframe[contains(@src, 'recaptcha')]"
                    )))
                    print("   ✅ Iframe do reCAPTCHA encontrado (método alternativo).")
                    navegador.switch_to.frame(iframe_captcha)
                    
                    checkbox_captcha = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                        "//span[contains(@class, 'recaptcha')] | //div[contains(@class, 'recaptcha')]"
                    )))
                    checkbox_captcha.click()
                    print("   ✅ Checkbox clicado (método alternativo).")
                    
                    navegador.switch_to.default_content()
                    time.sleep(8)
                    
                    botao_confirmar = wait.until(EC.element_to_be_clickable((
                        By.NAME, "btnConfirmar"
                    )))
                    botao_confirmar.click()
                    time.sleep(3)
                    print("   ✅ CAPTCHA resolvido com sucesso (método alternativo)!")
                    return True
                except Exception as e:
                    print(f"   ❌ Erro ao resolver CAPTCHA (método alternativo): {e}")
                    try:
                        navegador.switch_to.default_content()
                    except:
                        pass
                    return False
            except Exception as e:
                print(f"   ❌ Erro ao resolver CAPTCHA: {e}")
                # Garante que está no frame principal
                try:
                    navegador.switch_to.default_content()
                except:
                    pass
                return False
        except Exception as e:
            return False
    
    # Verifica CAPTCHA após login
    verificar_e_resolver_captcha()

    # Configuração dos diretórios e arquivos
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_exames = os.path.join(user_dir, 'exames_solicitar.csv')
    
    # verificar se o csv existe
    print("\n📋 Etapa 1: Extraindo informações dos exames a solicitar...")
    try:
        # Verifica se o arquivo existe para pegar o cabeçalho
        if os.path.exists(csv_exames):
            df = pd.read_csv(csv_exames)
            colunas = df.columns.tolist()
            print(f"   ✅ Arquivo encontrado com colunas: {', '.join(colunas)}")
            if 'ra' not in colunas:
                print(f"   ❌ Coluna 'ra' não encontrada no arquivo. Colunas disponíveis: {', '.join(colunas)}")
                return None
        else:
            print(f"   ❌ Arquivo não encontrado: {csv_exames}, crie o arquivo com o cabeçalho: 'ra' e insira a lista de prontuarios a pesquisar")
            return None

    except Exception as e:
        print(f"❌ Erro ao extrair informações dos exames a solicitar: {e}")
        return None

    # Garante que as colunas necessárias existem no DataFrame
    if 'procedimento' not in df.columns:
        df['procedimento'] = ''
    if 'chave' not in df.columns:
        df['chave'] = ''
    if 'solicitacao' not in df.columns:
        df['solicitacao'] = ''
    
    # Contador para numeração sequencial dos PDFs
    contador_pdf = 0

    # Itera sobre os links do CSV
    for index, row in df.iterrows():
        try:
            # Verifica se a linha tem chave e solicitação preenchidos (só processa se tiver ambos)
            chave_val = row.get('chave', '')
            chave = str(chave_val).strip() if pd.notna(chave_val) and chave_val != '' else ''
            
            solicitacao_val = row.get('solicitacao', '')
            solicitacao = str(solicitacao_val).strip() if pd.notna(solicitacao_val) and solicitacao_val != '' else ''
            
            if not (chave and solicitacao):
                print(f"\n[{index + 1}/{len(df)}] ⏭️  Linha sem chave ou solicitação preenchidos. Pulando...")
                continue
            
            cns = row['cns']
            procedimento_val = row.get('procedimento', '')
            procedimento = str(procedimento_val).strip() if pd.notna(procedimento_val) and procedimento_val != '' else ''
            cns_float = float(cns)
            # Remove o .0 se for um número inteiro
            cns = int(cns_float) if cns_float.is_integer() else cns_float
            
            # Remove o .0 da solicitação se for um número inteiro
            try:
                solicitacao_float = float(solicitacao)
                solicitacao = str(int(solicitacao_float)) if solicitacao_float.is_integer() else str(solicitacao_float)
            except (ValueError, TypeError):
                # Se não for um número, mantém como está
                pass
            
            print(f"\n[{index + 1}/{len(df)}] Processando Solicitação para o CNS: {cns}, Solicitação: {solicitacao}")

            navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/gerenciador_solicitacao?etapa=VISUALIZAR_FICHA&co_solicitacao={solicitacao}&co_seq_solicitacao={solicitacao}&ordenacao=2&pagina=0")

            time.sleep(1) # aguarda a pagina carregar
            
            # Verifica se há CAPTCHA na página antes de processar
            if verificar_e_resolver_captcha():
                print("   ⏳ Aguardando redirecionamento após resolver CAPTCHA...")
                time.sleep(2)
            
            # Incrementa o contador para o nome do arquivo
            contador_pdf += 1
            numero_pdf = str(contador_pdf).zfill(3)  # Formata como 001, 002, 003...
            nome_pdf = f"relatorio_exame_{numero_pdf}.pdf"
            caminho_pdf = os.path.join(user_dir, nome_pdf)
            
            print(f"   Gerando PDF usando Chrome DevTools Protocol...")
            
            try:
                # Aguarda um pouco para garantir que a página esteja totalmente carregada
                time.sleep(1)
                
                # Executa o comando de impressão do Chrome DevTools Protocol
                print_options = {
                    'landscape': False,
                    'displayHeaderFooter': False,
                    'printBackground': True,
                    'preferCSSPageSize': True
                }
                
                # Usa execute_cdp_cmd para salvar como PDF
                result = navegador.execute_cdp_cmd('Page.printToPDF', print_options)
                
                # Salva o PDF
                pdf_data = base64.b64decode(result['data'])
                with open(caminho_pdf, 'wb') as f:
                    f.write(pdf_data)
                
                # Pausa para garantir que o PDF foi salvo completamente
                time.sleep(2)
                
                print(f"   ✅ PDF salvo com sucesso: {caminho_pdf}")
                
            except Exception as e:
                print(f"   ❌ Erro ao gerar PDF: {e}")

        except Exception as e:
            print(f"❌ Erro ao processar Solicitação para o CNS: {e}")
            continue
    
    # Limpa PDFs finais antigos (mais de 30 dias)
    print("\n🧹 Limpando PDFs finais antigos (mais de 30 dias)...")
    try:
        data_limite = datetime.now() - timedelta(days=30)
        pdfs_antigos = glob.glob(os.path.join(user_dir, 'solicitacoes_exames_imprimir_*.pdf'))
        removidos = 0
        for pdf_path in pdfs_antigos:
            try:
                # Extrai a data do nome do arquivo (formato: solicitacoes_exames_imprimir_YYYYMMDD_HHMMSS.pdf)
                nome_arquivo = os.path.basename(pdf_path)
                if '_' in nome_arquivo:
                    partes = nome_arquivo.replace('solicitacoes_exames_imprimir_', '').replace('.pdf', '').split('_')
                    if len(partes) >= 2:
                        data_str = partes[0]  # YYYYMMDD
                        hora_str = partes[1]  # HHMMSS
                        try:
                            data_arquivo = datetime.strptime(f"{data_str}_{hora_str}", "%Y%m%d_%H%M%S")
                            if data_arquivo < data_limite:
                                os.remove(pdf_path)
                                removidos += 1
                                print(f"   🗑️  Removido PDF antigo: {nome_arquivo}")
                        except ValueError:
                            # Se não conseguir parsear a data, verifica pela data de modificação do arquivo
                            data_modificacao = datetime.fromtimestamp(os.path.getmtime(pdf_path))
                            if data_modificacao < data_limite:
                                os.remove(pdf_path)
                                removidos += 1
                                print(f"   🗑️  Removido PDF antigo (por data de modificação): {nome_arquivo}")
            except Exception as e:
                print(f"   ⚠️  Erro ao remover PDF antigo {os.path.basename(pdf_path)}: {e}")
        if removidos > 0:
            print(f"   ✅ {removidos} PDF(s) antigo(s) removido(s)")
        else:
            print(f"   ✅ Nenhum PDF antigo encontrado para remover")
    except Exception as e:
        print(f"   ⚠️  Erro ao limpar PDFs antigos: {e}")
    
    # Junta todos os PDFs individuais em um único arquivo
    print("\n📄 Juntando PDFs individuais em um único arquivo...")
    try:
        # Encontra todos os PDFs gerados na ordem correta
        pdfs_gerados = sorted(glob.glob(os.path.join(user_dir, 'relatorio_exame_*.pdf')))
        
        if pdfs_gerados:
            # Gera timestamp para o nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Define o caminho do PDF unificado com timestamp
            pdf_unificado = os.path.join(user_dir, f'solicitacoes_exames_imprimir_{timestamp}.pdf')
            
            # Se houver apenas um PDF, apenas renomeia
            if len(pdfs_gerados) == 1:
                print(f"   ✅ Encontrado 1 PDF. Renomeando para {os.path.basename(pdf_unificado)}...")
                try:
                    os.rename(pdfs_gerados[0], pdf_unificado)
                    print(f"   ✅ PDF renomeado com sucesso: {pdf_unificado}")
                    print(f"   ✅ Processo concluído! PDF unificado: {pdf_unificado}")
                except Exception as e:
                    print(f"   ❌ Erro ao renomear PDF: {e}")
            else:
                # Se houver mais de um PDF, faz o merge
                print(f"   ✅ Encontrados {len(pdfs_gerados)} PDF(s) para juntar")
                
                # Cria o merger e adiciona os PDFs em ordem
                merger = PdfMerger()
                for pdf_path in pdfs_gerados:
                    try:
                        merger.append(pdf_path)
                        print(f"   ✅ Adicionado: {os.path.basename(pdf_path)}")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao adicionar {os.path.basename(pdf_path)}: {e}")
                
                # Salva o PDF unificado
                merger.write(pdf_unificado)
                merger.close()
                print(f"   ✅ PDF unificado salvo: {pdf_unificado}")
                
                # Remove os PDFs individuais
                print("   🗑️  Removendo PDFs individuais...")
                for pdf_path in pdfs_gerados:
                    try:
                        os.remove(pdf_path)
                        print(f"   ✅ Removido: {os.path.basename(pdf_path)}")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao remover {os.path.basename(pdf_path)}: {e}")
                
                print(f"   ✅ Processo concluído! PDF unificado: {pdf_unificado}")
        else:
            print("   ⚠️  Nenhum PDF individual encontrado para juntar.")
    except Exception as e:
        print(f"   ❌ Erro ao juntar PDFs: {e}")
    
    # Verificação final: identifica registros com problemas para revisão manual
    print("\n📊 Verificando registros para revisão manual...")
    try:
        # Relê o CSV para ter os dados atualizados
        df_final = pd.read_csv(csv_exames)
        
        # Garante que as colunas existem
        if 'ra' not in df_final.columns:
            df_final['ra'] = ''
        if 'cns' not in df_final.columns:
            df_final['cns'] = ''
        if 'chave' not in df_final.columns:
            df_final['chave'] = ''
        if 'solicitacao' not in df_final.columns:
            df_final['solicitacao'] = ''
        
        # Identifica RAs sem CNS
        ras_sem_cns = []
        for index, row in df_final.iterrows():
            ra_val = row.get('ra', '')
            ra = str(ra_val).strip() if pd.notna(ra_val) and ra_val != '' else ''
            cns_val = row.get('cns', '')
            cns = str(cns_val).strip() if pd.notna(cns_val) and cns_val != '' else ''
            
            if ra and (not cns or cns == '' or cns == 'nan'):
                ras_sem_cns.append(ra)
        
        # Identifica RAs sem Solicitação/Chave
        ras_sem_solicitacao_chave = []
        for index, row in df_final.iterrows():
            ra_val = row.get('ra', '')
            ra = str(ra_val).strip() if pd.notna(ra_val) and ra_val != '' else ''
            chave_val = row.get('chave', '')
            chave = str(chave_val).strip() if pd.notna(chave_val) and chave_val != '' else ''
            solicitacao_val = row.get('solicitacao', '')
            solicitacao = str(solicitacao_val).strip() if pd.notna(solicitacao_val) and solicitacao_val != '' else ''
            
            if ra and (not chave or chave == '' or chave == 'nan' or not solicitacao or solicitacao == '' or solicitacao == 'nan'):
                ras_sem_solicitacao_chave.append(ra)
        
        # Remove duplicatas mantendo a ordem
        ras_sem_cns = list(dict.fromkeys(ras_sem_cns))
        ras_sem_solicitacao_chave = list(dict.fromkeys(ras_sem_solicitacao_chave))
        
        # Exibe os resultados
        if ras_sem_cns:
            print(f"\n   ⚠️  RAs sem CNS ({len(ras_sem_cns)} registro(s)):")
            print(f"      {', '.join(ras_sem_cns)}")
        else:
            print(f"\n   ✅ Todos os registros possuem CNS preenchido.")
        
        if ras_sem_solicitacao_chave:
            print(f"\n   ⚠️  RAs sem Solicitação/Chave ({len(ras_sem_solicitacao_chave)} registro(s)):")
            print(f"      {', '.join(ras_sem_solicitacao_chave)}")
        else:
            print(f"\n   ✅ Todos os registros possuem Solicitação e Chave preenchidos.")
        
        if not ras_sem_cns and not ras_sem_solicitacao_chave:
            print(f"\n   ✅ Nenhum registro pendente para revisão manual!")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar registros para revisão: {e}")
    
    # Fecha o navegador
    if navegador:
        navegador.quit()
        print("✅ Navegador fechado")
    
    return