import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import multiprocessing
import glob
import re


def processar_lote(csv_path, lote_num, total_lotes):
    """
    Processa um lote específico de prontuários.
    Esta função será executada em um processo separado.
    """
    print(f"\n[LOTE {lote_num}/{total_lotes}] 🚀 Iniciando processamento...")
    
    # Ler o CSV do lote
    if not os.path.exists(csv_path):
        print(f"[LOTE {lote_num}] ❌ Arquivo não encontrado: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path, dtype=str)
    total = len(df)
    print(f"[LOTE {lote_num}] 📋 {total} prontuários neste lote")
    
    # Ler credenciais
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
    
    # Inicializar o driver
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Fazer login
        print(f"[LOTE {lote_num}] 🔐 Fazendo login no GHOSP...")
        url_login = f"{caminho_ghosp}:4002/users/sign_in"
        driver.get(url_login)
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(usuario_ghosp)
        
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        senha_field.send_keys(senha_ghosp)
        
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
        )
        login_button.click()
        
        print(f"[LOTE {lote_num}] ✅ Login realizado")
        time.sleep(2)
        
        # Loop pelos prontuários do lote
        for idx, row in df.iterrows():
            ra = str(row['ra']).strip()
            print(f"\n[LOTE {lote_num}] [{idx+1}/{total}] Processando RA: {ra}")
            
            nome2 = ''
            dn = ''
            
            try:
                # Acessar o prontuário
                driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
                time.sleep(1)
                
                # Verificar diálogo de justificativa
                try:
                    dialog = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@id="form_justificativa" and contains(@class, "ui-dialog-content")]'))
                    )
                    
                    dropdown = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_tabela_id"]'))
                    )
                    select = Select(dropdown)
                    select.select_by_visible_text("Enfermagem")
                    
                    justificativa = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_justificativa"]'))
                    )
                    justificativa.clear()
                    justificativa.send_keys("NIR")
                    
                    salvar_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="new_acesso_prontuario"]/div[3]/input'))
                    )
                    salvar_btn.click()
                    time.sleep(1)
                    
                    confirmar_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button/span'))
                    )
                    confirmar_btn.click()
                    time.sleep(1)
                    
                except TimeoutException:
                    pass
                
                # Clicar em informações
                try:
                    info_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
                    )
                    info_btn.click()
                    time.sleep(2)
                except TimeoutException:
                    print(f"[LOTE {lote_num}]   ⚠️  Aba de informações não encontrada")
                    continue
                
                # Extrair nome
                try:
                    nome2_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="span-4 direita dcampo"][contains(text(), "Nome:")]/following-sibling::div[@class="vcampo"][1]'))
                    )
                    nome2 = nome2_elem.text.strip()
                    print(f"[LOTE {lote_num}]   ✓ Nome: {nome2}")
                except Exception as e:
                    print(f"[LOTE {lote_num}]   ❌ Nome não encontrado")
                
                # Extrair data de nascimento
                try:
                    dn_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="span-4 direita dcampo"][contains(text(), "Data Nasc.")]/following-sibling::div[@class="vcampo"][1]'))
                    )
                    dn = dn_elem.text.strip().replace('\xa0', '').replace('&nbsp;', '')
                    print(f"[LOTE {lote_num}]   ✓ DN: {dn}")
                except Exception as e:
                    print(f"[LOTE {lote_num}]   ❌ DN não encontrada")
                
                # Atualizar DataFrame
                df.at[idx, 'nome2'] = nome2
                df.at[idx, 'dn'] = dn
                
            except Exception as e:
                print(f"[LOTE {lote_num}]   ❌ Erro: {e}")
                continue
        
        # Salvar o lote processado
        df.to_csv(csv_path, index=False)
        print(f"\n[LOTE {lote_num}] ✅ Lote salvo: {csv_path}")
        return True
        
    except Exception as e:
        print(f"[LOTE {lote_num}] ❌ Erro geral: {e}")
        return False
    
    finally:
        driver.quit()
        print(f"[LOTE {lote_num}] 🔒 Navegador fechado")


def ghosp_especial_parallel():
    """
    Versão paralela da extração do GHOSP.
    Divide o CSV em lotes e processa em paralelo.
    """
    print("\n---===> ACESSO AO GHOSP - EXTRAÇÃO PARALELA <===---")
    
    # Definir diretório e caminho do CSV
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'especial.csv')
    
    # Ler o CSV principal
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return
    
    df = pd.read_csv(csv_path, dtype=str)
    
    # Verificar colunas necessárias
    if 'ra' not in df.columns:
        print("❌ Coluna 'ra' não encontrada no CSV")
        return
    
    # Adicionar colunas se não existirem
    if 'nome2' not in df.columns:
        df['nome2'] = ''
    if 'dn' not in df.columns:
        df['dn'] = ''
    
    total = len(df)
    print(f"📋 Total de prontuários: {total}")
    
    # Definir tamanho do lote
    TAMANHO_LOTE = 500
    num_lotes = (total + TAMANHO_LOTE - 1) // TAMANHO_LOTE
    
    print(f"📦 Dividindo em {num_lotes} lotes de até {TAMANHO_LOTE} registros")
    
    # Criar lotes
    lotes_paths = []
    for i in range(num_lotes):
        inicio = i * TAMANHO_LOTE
        fim = min((i + 1) * TAMANHO_LOTE, total)
        
        df_lote = df.iloc[inicio:fim].copy()
        lote_path = os.path.join(user_dir, f'especial{i+1:02d}.csv')
        df_lote.to_csv(lote_path, index=False)
        lotes_paths.append(lote_path)
        
        print(f"  ✓ Lote {i+1}/{num_lotes} criado: {os.path.basename(lote_path)} ({len(df_lote)} registros)")
    
    print(f"\n🚀 Iniciando processamento paralelo com {num_lotes} processos...")
    
    # Perguntar ao usuário quantos processos simultâneos deseja
    print(f"\n⚙️  Quantos processos simultâneos deseja executar?")
    print(f"   Recomendado: {min(4, num_lotes)} (ou menos se o sistema ficar lento)")
    try:
        max_workers = int(input(f"   Digite o número (1-{num_lotes}): "))
        max_workers = max(1, min(max_workers, num_lotes))
    except:
        max_workers = min(4, num_lotes)
        print(f"   Usando padrão: {max_workers}")
    
    # Processar lotes em paralelo
    with multiprocessing.Pool(processes=max_workers) as pool:
        # Criar argumentos para cada processo
        args = [(lotes_paths[i], i+1, num_lotes) for i in range(num_lotes)]
        
        # Executar em paralelo
        resultados = pool.starmap(processar_lote, args)
    
    # Verificar resultados
    sucessos = sum(resultados)
    print(f"\n📊 Processamento concluído:")
    print(f"   ✅ Lotes bem-sucedidos: {sucessos}/{num_lotes}")
    print(f"   ❌ Lotes com erro: {num_lotes - sucessos}")
    
    # Reunir todos os lotes processados
    print(f"\n🔗 Reunindo lotes em um único CSV...")
    
    dfs_lotes = []
    for lote_path in lotes_paths:
        if os.path.exists(lote_path):
            df_lote = pd.read_csv(lote_path, dtype=str)
            dfs_lotes.append(df_lote)
    
    # Concatenar todos os lotes
    df_final = pd.concat(dfs_lotes, ignore_index=True)
    
    # Tratamento do CSV
    print("\n🔧 Iniciando tratamento do CSV...")
    
    # Criar coluna revisao se não existir
    if 'revisao' not in df_final.columns:
        df_final['revisao'] = ''
    
    for idx, row in df_final.iterrows():
        # Limpar a coluna 'nome'
        if pd.notna(row['nome']) and row['nome']:
            nome_original = str(row['nome']).strip()
            nome_limpo = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', nome_original)
            nome_limpo = re.sub(r'\s+', ' ', nome_limpo).strip()
            df_final.at[idx, 'nome'] = nome_limpo
        
        # Comparar nomes
        nome = str(df_final.at[idx, 'nome']).strip().upper() if pd.notna(df_final.at[idx, 'nome']) else ''
        nome2 = str(df_final.at[idx, 'nome2']).strip().upper() if pd.notna(df_final.at[idx, 'nome2']) else ''
        
        if nome and nome2:
            if nome == nome2:
                df_final.at[idx, 'revisao'] = 'ok'
            else:
                df_final.at[idx, 'revisao'] = 'revisar'
        elif not nome2:
            df_final.at[idx, 'revisao'] = 'revisar'
    
    # Salvar CSV final
    df_final.to_csv(csv_path, index=False)
    print(f"✅ CSV final salvo: {csv_path}")
    
    # Limpar arquivos temporários
    print("\n🧹 Limpando arquivos temporários...")
    for lote_path in lotes_paths:
        if os.path.exists(lote_path):
            os.remove(lote_path)
            print(f"  ✓ Removido: {os.path.basename(lote_path)}")
    
    # Estatísticas finais
    total_ok = len(df_final[df_final['revisao'] == 'ok'])
    total_revisar = len(df_final[df_final['revisao'] == 'revisar'])
    
    print(f"\n📊 Estatísticas Finais:")
    print(f"   📋 Total processado: {len(df_final)}")
    print(f"   ✅ OK: {total_ok}")
    print(f"   ⚠️  Revisar: {total_revisar}")
    print(f"\n🎉 Processamento paralelo concluído!")


# Manter a função original para compatibilidade
def ghosp_especial():
    """
    Wrapper que chama a versão paralela.
    Mantém compatibilidade com o código existente.
    """
    ghosp_especial_parallel()
