import os
import csv
import time
import json
import base64
import glob
import pandas as pd
import configparser
try:
    from PyPDF2 import PdfMerger
except ImportError:
    try:
        from pypdf import PdfMerger
    except ImportError:
        PdfMerger = None
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from datetime import datetime

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
                time.sleep(0.5)
                
                print(f"   ✅ PDF salvo com sucesso: {caminho_pdf}")
                
            except Exception as e:
                print(f"   ❌ Erro ao gerar PDF: {e}")

        except Exception as e:
            print(f"❌ Erro ao processar Solicitação para o CNS: {e}")
            continue
    
    # Junta todos os PDFs individuais em um único arquivo
    print("\n📄 Juntando PDFs individuais em um único arquivo...")
    try:
        if PdfMerger is None:
            print("   ⚠️  Biblioteca PyPDF2 ou pypdf não encontrada. Instale com: pip install PyPDF2 ou pip install pypdf")
            print("   📋 PDFs individuais não foram juntados, mas foram mantidos na pasta.")
        else:
            # Encontra todos os PDFs gerados na ordem correta
            pdfs_gerados = sorted(glob.glob(os.path.join(user_dir, 'relatorio_exame_*.pdf')))
            
            if pdfs_gerados:
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
                pdf_unificado = os.path.join(user_dir, 'solicitacoes_exames_imprimir.pdf')
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
    
    # Fecha o navegador
    if navegador:
        navegador.quit()
        print("✅ Navegador fechado")
    
    return