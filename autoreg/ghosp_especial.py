import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.justificativa_ghosp import tratar_justificativa_acesso
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def ghosp_especial():
    print("\n---===> ACESSO AO GHOSP - EXTRAÇÃO PERSONALIZADA <===---")
    
    # Definir diretório e caminho do CSV
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'especial.csv')
    
    # Ler o CSV com os RAs
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return
    
    df = pd.read_csv(csv_path, dtype=str)
    
    # Verificar se as colunas necessárias existem
    if 'ra' not in df.columns:
        print("❌ Coluna 'ra' não encontrada no CSV")
        return
    
    # Adicionar colunas nome2 e dn se não existirem
    if 'nome2' not in df.columns:
        df['nome2'] = ''
    if 'dn' not in df.columns:
        df['dn'] = ''
    
    total = len(df)
    print(f"📋 Total de prontuários a processar: {total}")
    
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    # Inicializa o navegador (Chrome)
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    # Acesse a página de login do G-HOSP na porta 4002
    url_login = f"{caminho_ghosp}:4002/users/sign_in"
    driver.get(url_login)

    try:
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
        
        # Loop pelos prontuários
        for idx, row in df.iterrows():
            ra = str(row['ra']).strip()
            print(f"\n[{idx+1}/{total}] Processando prontuário: {ra}")
            
            nome2 = ''
            dn = ''
            
            try:
                # Acessar o prontuário
                driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
                time.sleep(1)
                
                # Paciente em alta: G-HOSP redireciona para a página de justificativa
                # de acesso. Preenche/envia e re-navega para o formulário eletrônico.
                if tratar_justificativa_acesso(driver):
                    driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
                    time.sleep(1)
                


                # Clica em informações
                try:
                    info_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
                    )
                    info_btn.click()
                    print("  ✓ Aba de informações clicada")
                    time.sleep(2)
                except TimeoutException:
                    print("  ❌ Aba de informações não encontrada")
                    continue

                # Extrair nome (busca a div vcampo logo após o dcampo "Nome:")
                try:
                    # Localiza o elemento que contém "Nome:" e pega o próximo elemento vcampo
                    nome2_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="span-4 direita dcampo"][contains(text(), "Nome:")]/following-sibling::div[@class="vcampo"][1]'))
                    )
                    nome2 = nome2_elem.text.strip()
                    print(f"  ✓ Nome extraído: {nome2}")
                except Exception as e:
                    print(f"  ❌ Nome não encontrado: {e}")

                # Extrair data de nascimento (busca a div vcampo logo após o dcampo "Data Nasc.:")
                try:
                    dn_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="span-4 direita dcampo"][contains(text(), "Data Nasc.")]/following-sibling::div[@class="vcampo"][1]'))
                    )
                    dn = dn_elem.text.strip().replace('\xa0', '').replace('&nbsp;', '')
                    print(f"  ✓ Data de nascimento extraída: {dn}")
                except Exception as e:
                    print(f"  ❌ Data de nascimento não encontrada: {e}")

                # Atualizar o DataFrame com os dados obtidos
                df.at[idx, 'nome2'] = nome2
                df.at[idx, 'dn'] = dn
                
            except Exception as e:
                print(f"  ❌ Erro ao processar prontuário {ra}: {e}")
                continue

        # Salvar o DataFrame atualizado no CSV
        df.to_csv(csv_path, index=False)
        print(f"\n✅ Extração finalizada! Resultados salvos em {csv_path}")
        print(f"📊 Total processado: {total} prontuários")
        
        # Tratamento do CSV
        print("\n🔧 Iniciando tratamento do CSV...")
        
        # Criar coluna revisao se não existir
        if 'revisao' not in df.columns:
            df['revisao'] = ''
        
        import re
        
        for idx, row in df.iterrows():
            # Limpar a coluna 'nome' - remover números e caracteres após nome e sobrenome
            if pd.notna(row['nome']) and row['nome']:
                nome_original = str(row['nome']).strip()
                
                # Remove números e caracteres especiais, mantendo apenas letras e espaços
                nome_limpo = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', nome_original)
                # Remove espaços múltiplos
                nome_limpo = re.sub(r'\s+', ' ', nome_limpo).strip()
                
                # Atualizar o nome limpo no DataFrame
                df.at[idx, 'nome'] = nome_limpo
                
                print(f"  [{idx+1}] Nome limpo: {nome_limpo}")
            
            # Comparar 'nome' com 'nome2'
            nome = str(df.at[idx, 'nome']).strip().upper() if pd.notna(df.at[idx, 'nome']) else ''
            nome2 = str(df.at[idx, 'nome2']).strip().upper() if pd.notna(df.at[idx, 'nome2']) else ''
            
            if nome and nome2:
                if nome == nome2:
                    df.at[idx, 'revisao'] = 'ok'
                    print(f"  [{idx+1}] ✅ Nomes coincidem: {nome}")
                else:
                    df.at[idx, 'revisao'] = 'revisar'
                    print(f"  [{idx+1}] ⚠️  Nomes diferentes:")
                    print(f"        Nome:  {nome}")
                    print(f"        Nome2: {nome2}")
            elif not nome2:
                df.at[idx, 'revisao'] = 'revisar'
                print(f"  [{idx+1}] ⚠️  Nome2 não encontrado")
        
        # Salvar o CSV tratado
        df.to_csv(csv_path, index=False)
        print(f"\n✅ Tratamento concluído! CSV atualizado: {csv_path}")
        
        # Estatísticas
        total_ok = len(df[df['revisao'] == 'ok'])
        total_revisar = len(df[df['revisao'] == 'revisar'])
        print(f"\n📊 Estatísticas:")
        print(f"   ✅ OK: {total_ok}")
        print(f"   ⚠️  Revisar: {total_revisar}")

    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        print(f"\n❌ Erro geral na execução: {e}")
    
    finally:
        # Fecha o navegador
        print("\n🔒 Fechando navegador...")
        driver.quit()