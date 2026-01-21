import os
import csv
import time
import random
import difflib
import pandas as pd
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from datetime import datetime

def exames_ambulatorio_solicita():
    print("Solicitação de exames ambulatoriais")
    
    navegador = None
    
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)
    
    # Lê credenciais do SISREG
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG-REG']['usuarioreg']
    senha_sisreg = config['SISREG-REG']['senhareg']
    
    def fazer_login():
        """Realiza o login no SISREG"""
        print("Acessando a página de login...")
        navegador.get("https://sisregiii.saude.gov.br")
        
        print("Localizando campo de usuário...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        print("Campo de usuário localizado.")

        print("Localizando campo de senha...")
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        print("Campo de senha localizado.")

        print("Preenchendo usuário...")
        usuario_field.clear()
        usuario_field.send_keys(usuario_sisreg)
        print("Usuário preenchido.")
        
        print("Preenchendo senha...")
        senha_field.clear()
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
    
    def verificar_erro_sistema():
        """Verifica se há erro de sistema na página atual"""
        try:
            # Procura por tabela com título "ERRO DE SISTEMA"
            erro_elementos = navegador.find_elements(By.XPATH, "//table//*[contains(text(), 'ERRO DE SISTEMA')]")
            if erro_elementos:
                print("   ⚠️  ERRO DE SISTEMA detectado na página!")
                return True
            
            # Também verifica no texto da página
            page_text = navegador.find_element(By.TAG_NAME, "body").text
            if "ERRO DE SISTEMA" in page_text.upper():
                print("   ⚠️  ERRO DE SISTEMA detectado na página!")
                return True
                
            return False
        except Exception as e:
            # Se houver erro ao verificar, assume que não há erro
            return False
    
    # Realiza o login inicial
    fazer_login()
    
    # Verifica erro após login
    if verificar_erro_sistema():
        print("   🔄 Refazendo login devido a erro de sistema...")
        fazer_login()


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
            
            # Remove linhas em branco (onde 'ra' está vazio, é NaN ou contém apenas espaços)
            linhas_antes = len(df)
            
            # Remove linhas onde 'ra' está vazio, é NaN ou contém apenas espaços (coluna principal obrigatória)
            df = df[df['ra'].notna()]  # Remove NaN
            df = df[df['ra'].astype(str).str.strip() != '']  # Remove strings vazias ou apenas espaços
            
            linhas_depois = len(df)
            linhas_removidas = linhas_antes - linhas_depois
            if linhas_removidas > 0:
                print(f"   🧹 {linhas_removidas} linha(s) em branco removida(s). {linhas_depois} linha(s) válida(s) restante(s).")
            else:
                print(f"   ✅ Nenhuma linha em branco encontrada. {linhas_depois} linha(s) válida(s).")
        else:
            print(f"   ❌ Arquivo não encontrado: {csv_exames}, crie o arquivo com o cabeçalho: 'ra' e insira a lista de prontuarios a pesquisar")
            return None

    except Exception as e:
        print(f"❌ Erro ao extrair informações dos exames a solicitar: {e}")
        return None

    # Garante que as colunas necessárias existem no DataFrame
    if 'procedimento' not in df.columns:
        df['procedimento'] = ''
    if 'contraste' not in df.columns:
        df['contraste'] = ''
    if 'dividir' not in df.columns:
        df['dividir'] = ''
    if 'chave' not in df.columns:
        df['chave'] = ''
    if 'solicitacao' not in df.columns:
        df['solicitacao'] = ''
    if 'erro' not in df.columns:
        df['erro'] = ''
    
    # Processa divisão de procedimentos múltiplos quando 'dividir' = 's'
    print("\n📋 Etapa 1.5: Verificando necessidade de divisão de procedimentos...")
    linhas_antes_divisao = len(df)
    linhas_para_expandir = []
    indices_para_remover = []
    
    for index, row in df.iterrows():
        dividir = str(row.get('dividir', '')).strip().upper() if pd.notna(row.get('dividir')) else ''
        procedimento = str(row.get('procedimento', '')).strip() if pd.notna(row.get('procedimento')) else ''
        
        # Verifica se precisa dividir e se há procedimentos múltiplos
        if dividir == 'S' and procedimento and '|' in procedimento:
            # Divide os procedimentos pelo delimitador '|'
            procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
            
            if len(procedimentos_lista) > 1:
                # Cria novas linhas para cada procedimento
                for proc in procedimentos_lista:
                    nova_linha = row.copy()
                    nova_linha['procedimento'] = proc
                    nova_linha['dividir'] = ''  # Remove o 's' para evitar erros
                    linhas_para_expandir.append(nova_linha)
                
                # Marca a linha original para remoção
                indices_para_remover.append(index)
    
    # Remove linhas originais que foram divididas
    if indices_para_remover:
        df = df.drop(indices_para_remover)
        print(f"   🗑️  {len(indices_para_remover)} linha(s) original(is) removida(s) para divisão.")
    
    # Adiciona as novas linhas expandidas
    if linhas_para_expandir:
        df_novas_linhas = pd.DataFrame(linhas_para_expandir)
        df = pd.concat([df, df_novas_linhas], ignore_index=True)
        df = df.reset_index(drop=True)  # Garante índices sequenciais
        linhas_depois_divisao = len(df)
        linhas_criadas = linhas_depois_divisao - linhas_antes_divisao + len(indices_para_remover)
        print(f"   ✅ {linhas_criadas} nova(s) linha(s) criada(s) a partir da divisão de procedimentos múltiplos.")
        print(f"   📊 Total de linhas após divisão: {linhas_depois_divisao} (antes: {linhas_antes_divisao})")
        
        # Salva o CSV após a divisão
        try:
            df.to_csv(csv_exames, index=False)
            print(f"   💾 CSV atualizado e salvo com as linhas divididas em: {csv_exames}")
        except Exception as e:
            print(f"   ⚠️  Erro ao salvar CSV após divisão: {e}")
    else:
        print(f"   ✅ Nenhuma divisão necessária. Todas as linhas estão prontas para processamento.")
    
    
    # Itera sobre os links do CSV
    for index, row in df.iterrows():
        try:
            # Verifica se a linha já foi processada (tem conteúdo em solicitacao e chave)
            chave = row.get('chave', '').strip() if pd.notna(row.get('chave')) else ''
            solicitacao = row.get('solicitacao', '').strip() if pd.notna(row.get('solicitacao')) else ''
            
            if chave and solicitacao:
                print(f"\n[{index + 1}/{len(df)}] ⏭️  Linha já processada (chave: {chave}, solicitação: {solicitacao}). Pulando...")
                continue
            
            cns_val = row.get('cns', '')
            procedimento = row.get('procedimento', '').strip() if pd.notna(row.get('procedimento')) else ''
            contraste = row.get('contraste', '').strip() if pd.notna(row.get('contraste')) else ''
            
            # Valida e converte CNS para número
            if pd.notna(cns_val) and str(cns_val).strip() != '':
                try:
                    cns_float = float(cns_val)
                    # Remove o .0 se for um número inteiro
                    cns = int(cns_float) if cns_float.is_integer() else cns_float
                except (ValueError, TypeError):
                    print(f"   ❌ Erro: valor inválido na coluna 'cns': '{cns_val}'. Pulando registro...")
                    continue
            else:
                print(f"   ❌ Erro: coluna 'cns' está vazia. Pulando registro...")
                continue
            print(f"\n[{index + 1}/{len(df)}] Processando Solicitação para o CNS: {cns}")
            if contraste and contraste.upper() == 'S':
                print(f"   ℹ️  Contraste obrigatório: apenas procedimentos 'COM CONTRASTE' serão selecionados")
            navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
            time.sleep(2)
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna à página de marcação após login
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
            
            # Aguarda a página carregar e localiza o campo CNS
            print("   Aguardando campo CNS carregar...")
            cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
            print(f"   Campo CNS localizado. Inserindo CNS: {cns}")
            
            # Limpa o campo e insere o CNS
            cns_field.clear()
            cns_field.send_keys(str(cns))
            print("   CNS inserido com sucesso.")
            
            # Localiza e clica no botão pesquisar
            print("   Localizando botão pesquisar...")
            pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
            print("   Botão pesquisar localizado. Clicando...")
            pesquisar_button.click()
            print("   Botão pesquisar clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a pesquisa ser processada
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna à página de marcação após login
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                # Reinsere o CNS e clica em pesquisar novamente
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
            
            # Localiza e clica no botão continuar
            print("   Localizando botão continuar...")
            continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
            print("   Botão continuar localizado. Clicando...")
            continuar_button.click()
            print("   Botão continuar clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna ao fluxo após login
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
                continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                continuar_button.click()
                time.sleep(2)
            
            # Seleciona o procedimento no dropdown "pa"
            print("   Localizando dropdown de procedimento (pa)...")
            pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
            pa_select = Select(pa_dropdown)
            print("   Selecionando 'XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS'...")
            
            # Tenta selecionar pelo value primeiro
            try:
                pa_select.select_by_value("0045000")
                print("   Procedimento selecionado com sucesso (por value).")
            except Exception as e:
                print(f"   ⚠️  Não foi possível selecionar por value, tentando por texto...")
                # Fallback: tenta selecionar pelo texto
                try:
                    pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                    print("   Procedimento selecionado com sucesso (por texto).")
                except Exception as e2:
                    print(f"   ❌ Erro ao selecionar procedimento: {e2}")
                    # Tenta buscar por texto parcial
                    try:
                        for option in pa_select.options:
                            if "TOMOGRAFIA COMPUTADORIZADA - INTERNADOS" in option.text:
                                pa_select.select_by_visible_text(option.text)
                                print(f"   Procedimento selecionado com sucesso (por texto parcial): {option.text}")
                                break
                        else:
                            raise Exception("Nenhuma opção de tomografia encontrada no dropdown")
                    except Exception as e3:
                        print(f"   ❌ Erro ao selecionar procedimento por texto parcial: {e3}")
                        raise
            
            # Preenche o campo CID10
            print("   Localizando campo CID10...")
            cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
            print("   Campo CID10 localizado. Inserindo 'R68'...")
            cid10_field.clear()
            cid10_field.send_keys("R68")
            print("   CID10 inserido com sucesso.")
            
            # Seleção aleatória no dropdown de profissional
            print("   Localizando dropdown de profissional (cpfprofsol)...")
            cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
            cpfprofsol_select = Select(cpfprofsol_dropdown)
            
            # Obtém todas as opções disponíveis (exceto a primeira que geralmente é vazia)
            opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
            if opcoes:
                opcao_aleatoria = random.choice(opcoes)
                valor_aleatorio = opcao_aleatoria.get_attribute("value")
                texto_aleatorio = opcao_aleatoria.text
                print(f"   Selecionando profissional aleatório: {texto_aleatorio} (value: {valor_aleatorio})...")
                cpfprofsol_select.select_by_value(valor_aleatorio)
                print("   Profissional selecionado com sucesso.")
            else:
                print("   ⚠️  Nenhuma opção disponível no dropdown de profissional.")
            
            # Seleciona a unidade de execução
            print("   Localizando dropdown de unidade de execução (upsexec)...")
            upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
            upsexec_select = Select(upsexec_dropdown)
            print("   Selecionando unidade com value '6861849'...")
            upsexec_select.select_by_value("6861849")
            print("   Unidade de execução selecionada com sucesso.")
            
            # Clica no botão OK
            print("   Localizando botão OK...")
            ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
            print("   Botão OK localizado. Clicando...")
            ok_button.click()
            print("   Botão OK clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna ao fluxo após login (precisa refazer todo o processo)
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
                continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                continuar_button.click()
                time.sleep(2)
                # Refaz seleções
                pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                pa_select = Select(pa_dropdown)
                try:
                    pa_select.select_by_value("0045000")
                except:
                    pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                cid10_field.clear()
                cid10_field.send_keys("R68")
                cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                cpfprofsol_select = Select(cpfprofsol_dropdown)
                opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                if opcoes:
                    opcao_aleatoria = random.choice(opcoes)
                    cpfprofsol_select.select_by_value(opcao_aleatoria.get_attribute("value"))
                upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                upsexec_select = Select(upsexec_dropdown)
                upsexec_select.select_by_value("6861849")
                ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                ok_button.click()
                time.sleep(2)

            # Função auxiliar para calcular similaridade melhorada
            def calcular_similaridade_melhorada(proc_csv, texto_opcao, contraste_solicitado=False):
                """
                Calcula similaridade melhorada priorizando palavras-chave críticas:
                - Partes anatômicas (OMBRO, JOELHO, TORAX, etc.)
                - Lateralidade (DIREITO, ESQUERDO)
                - Normaliza variações (DE/DO)
                - Contraste: quando não solicitado, prioriza SEM CONTRASTE ou sem menção
                
                Args:
                    proc_csv: Procedimento do CSV
                    texto_opcao: Texto da opção na tabela
                    contraste_solicitado: True se contraste foi solicitado ('S'), False caso contrário
                """
                # Normaliza textos
                proc_normalizado = proc_csv.upper().strip()
                opcao_normalizada = texto_opcao.upper().strip()
                
                # Palavras muito comuns que devem ser ignoradas no cálculo de peso
                palavras_ignoradas = {
                    'TOMOGRAFIA', 'COMPUTADORIZADA', 'DE', 'DO', 'DA', 'DAS', 'DOS',
                    'INTERNADOS', 'COM', 'SEM', 'CONTRASTE', 'OU', 'E', 'C/', 'S/',
                    'CLAVICULA', 'CLAVICULA)', '(', ')', '-', 'ARTICULACOES'
                }
                
                # Palavras-chave críticas de lateralidade (peso muito alto)
                lateralidades = {'DIREITO', 'DIREITA', 'ESQUERDO', 'ESQUERDA'}
                
                # Extrai palavras de cada texto, removendo palavras ignoradas
                def extrair_palavras_relevantes(texto):
                    # Remove parênteses e conteúdo dentro deles, normaliza espaços
                    texto_limpo = texto.replace('(', ' ').replace(')', ' ')
                    palavras = texto_limpo.split()
                    return {p for p in palavras if p not in palavras_ignoradas and len(p) > 2}
                
                palavras_proc = extrair_palavras_relevantes(proc_normalizado)
                palavras_opcao = extrair_palavras_relevantes(opcao_normalizada)
                
                # Identifica lateralidade no procedimento CSV
                lateralidade_proc = None
                for lat in lateralidades:
                    if lat in proc_normalizado:
                        lateralidade_proc = lat
                        break
                
                # Identifica lateralidade na opção
                lateralidade_opcao = None
                for lat in lateralidades:
                    if lat in opcao_normalizada:
                        lateralidade_opcao = lat
                        break
                
                # Identifica parte anatômica principal (palavras mais específicas)
                partes_anatomicas = {
                    'OMBRO', 'JOELHO', 'TORAX', 'CRANIO', 'COLUNA', 'CERVICAL', 'DORSAL',
                    'LOMBAR', 'LOMBO-SACRA', 'TORACICA', 'FACE', 'SEIOS', 'PESCOCO',
                    'ABDOMEN', 'PELVE', 'BACIA', 'RINS', 'BRACO', 'ANTEBRACO', 'COTOVELO',
                    'PUNHO', 'MAO', 'COXA', 'PERNA', 'PE', 'TORNOZELO', 'AORTA', 'ARTÉRIAS',
                    'CERVICAIS', 'ILÍACAS', 'CEREBRAL', 'URINARIO', 'SELA', 'TURCICA'
                }
                
                parte_proc = None
                for parte in partes_anatomicas:
                    if parte in proc_normalizado:
                        parte_proc = parte
                        break
                
                parte_opcao = None
                for parte in partes_anatomicas:
                    if parte in opcao_normalizada:
                        parte_opcao = parte
                        break
                
                # Similaridade base usando SequenceMatcher
                similaridade_base = difflib.SequenceMatcher(None, proc_normalizado, opcao_normalizada).ratio()
                
                # Bônus/Penalização baseado em palavras-chave críticas
                bonus = 0.0
                penalizacao = 0.0
                
                # 1. CORRESPONDÊNCIA DE PARTE ANATÔMICA (peso muito alto: +0.4)
                if parte_proc and parte_opcao:
                    if parte_proc == parte_opcao:
                        bonus += 0.4
                    else:
                        # Penaliza MUITO se partes anatômicas diferentes (prioridade absoluta)
                        penalizacao += 0.6
                
                # 2. CORRESPONDÊNCIA DE LATERALIDADE (peso muito alto: +0.3)
                if lateralidade_proc and lateralidade_opcao:
                    # Normaliza variações DIREITO/DIREITA e ESQUERDO/ESQUERDA
                    lat_proc_norm = 'DIREITO' if 'DIREIT' in lateralidade_proc else 'ESQUERDO'
                    lat_opcao_norm = 'DIREITO' if 'DIREIT' in lateralidade_opcao else 'ESQUERDO'
                    
                    if lat_proc_norm == lat_opcao_norm:
                        bonus += 0.3
                    else:
                        # Penaliza muito se lateralidade não corresponde
                        penalizacao += 0.4
                
                # 3. Se CSV tem lateralidade mas opção não tem (ou vice-versa), penaliza
                if lateralidade_proc and not lateralidade_opcao:
                    penalizacao += 0.2
                elif not lateralidade_proc and lateralidade_opcao:
                    # Menos penalização se CSV não especifica lateralidade
                    penalizacao += 0.1
                
                # 4. Bônus por palavras relevantes em comum (peso menor)
                palavras_comuns = palavras_proc.intersection(palavras_opcao)
                if palavras_comuns:
                    # Calcula proporção de palavras comuns
                    total_palavras_relevantes = len(palavras_proc.union(palavras_opcao))
                    if total_palavras_relevantes > 0:
                        proporcao_comuns = len(palavras_comuns) / total_palavras_relevantes
                        bonus += proporcao_comuns * 0.2
                
                # 5. Bônus se contém substring exata (para casos como "OMBRO DIREITO")
                if parte_proc and lateralidade_proc:
                    busca_exata = f"{parte_proc} {lateralidade_proc}"
                    if busca_exata in opcao_normalizada or busca_exata.replace(' ', '') in opcao_normalizada.replace(' ', ''):
                        bonus += 0.15
                
                # 6. LÓGICA DE CONTRASTE (só aplicada quando parte anatômica corresponde)
                # Normaliza o texto da opção para verificação de contraste
                texto_opcao_normalizado = ' '.join(opcao_normalizada.split())
                tem_com_contraste = "COM CONTRASTE" in texto_opcao_normalizado
                tem_sem_contraste = "SEM CONTRASTE" in texto_opcao_normalizado
                nao_mentiona_contraste = not tem_com_contraste and not tem_sem_contraste
                
                # Verifica se a parte anatômica corresponde (fator crítico)
                parte_anatomica_corresponde = parte_proc and parte_opcao and parte_proc == parte_opcao
                
                if contraste_solicitado:
                    # Se contraste foi solicitado, já foi filtrado antes (só chegam opções COM CONTRASTE)
                    # Mas damos um pequeno bônus para confirmar
                    if tem_com_contraste:
                        bonus += 0.1
                else:
                    # Se contraste NÃO foi solicitado, prioriza SEM CONTRASTE ou sem menção
                    # MAS só aplica bônus/penalização quando a parte anatômica corresponde
                    if parte_anatomica_corresponde:
                        # Só considera contraste quando parte anatômica está correta
                        if tem_sem_contraste:
                            # Bônus alto para opções explicitamente SEM CONTRASTE (quando parte anatômica correta)
                            bonus += 0.4
                        elif nao_mentiona_contraste:
                            # Bônus médio para opções que não mencionam contraste (quando parte anatômica correta)
                            bonus += 0.2
                        elif tem_com_contraste:
                            # Penaliza opções COM CONTRASTE quando não foi solicitado (quando parte anatômica correta)
                            penalizacao += 0.5
                    # Se parte anatômica NÃO corresponde, não aplica bônus de contraste
                    # Isso garante que parte anatômica errada nunca ganhe só por ter SEM CONTRASTE
                
                # Calcula similaridade final
                similaridade_final = similaridade_base + bonus - penalizacao
                
                # Aplica penalização multiplicativa adicional para COM CONTRASTE quando não solicitado
                # MAS só quando a parte anatômica corresponde (para não penalizar partes anatômicas erradas)
                if not contraste_solicitado and tem_com_contraste and parte_anatomica_corresponde:
                    # Reduz a similaridade final multiplicativamente para garantir que opções SEM CONTRASTE ganhem
                    # Mas só quando a parte anatômica está correta
                    similaridade_final = similaridade_final * 0.4
                
                # Garante que não ultrapasse 1.0 nem seja negativo
                similaridade_final = max(0.0, min(1.0, similaridade_final))
                
                return similaridade_final

            # Compara os procedimentos do CSV com as opções disponíveis na tabela
            if procedimento:
                # Separa os procedimentos pelo delimitador "|"
                procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
                print(f"   Encontrados {len(procedimentos_lista)} procedimento(s) para processar")
                
                # Aguarda a tabela carregar
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                
                # Encontra todos os checkboxes na tabela
                checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                
                checkboxes_marcados = []
                
                # Para cada procedimento do CSV
                for proc_idx, proc_csv in enumerate(procedimentos_lista, 1):
                    print(f"   [{proc_idx}/{len(procedimentos_lista)}] Buscando procedimento mais similar a: {proc_csv}")
                    
                    melhor_similaridade = 0
                    checkbox_selecionado = None
                    texto_selecionado = ""
                    
                    # Compara cada opção da tabela com o procedimento atual
                    for checkbox in checkboxes:
                        # Pula checkboxes já marcados
                        if checkbox in checkboxes_marcados:
                            continue
                            
                        # Obtém o texto da opção (texto do elemento pai td)
                        try:
                            td = checkbox.find_element(By.XPATH, "./..")
                            texto_opcao = td.text.strip()
                            
                            # Verifica se contraste foi solicitado
                            contraste_solicitado = contraste and contraste.upper() == 'S'
                            
                            # Se contraste for obrigatório ('s'), verifica se a opção contém "COM CONTRASTE"
                            # Esta verificação é OBRIGATÓRIA e deve ser feita ANTES de calcular similaridade
                            if contraste_solicitado:
                                # Normaliza o texto para comparação (remove espaços extras e converte para maiúsculas)
                                texto_opcao_normalizado = ' '.join(texto_opcao.upper().split())
                                if "COM CONTRASTE" not in texto_opcao_normalizado:
                                    # Pula esta opção se não contiver "COM CONTRASTE" - não considera para seleção
                                    continue
                            
                            # Usa a função de similaridade melhorada, passando informação sobre contraste
                            similaridade = calcular_similaridade_melhorada(proc_csv, texto_opcao, contraste_solicitado)
                            
                            if similaridade > melhor_similaridade:
                                melhor_similaridade = similaridade
                                checkbox_selecionado = checkbox
                                texto_selecionado = texto_opcao
                        except Exception as e:
                            continue
                    
                    # Marca o checkbox mais similar
                    if checkbox_selecionado and melhor_similaridade > 0.4:  # Threshold mínimo de 40%
                        # Verificação adicional: se contraste é obrigatório, confirma que a opção selecionada contém "COM CONTRASTE"
                        if contraste and contraste.upper() == 'S':
                            texto_selecionado_normalizado = ' '.join(texto_selecionado.upper().split())
                            if "COM CONTRASTE" not in texto_selecionado_normalizado:
                                print(f"      ❌ Erro: Opção selecionada não contém 'COM CONTRASTE' como exigido. Opção: {texto_selecionado}")
                                print(f"      ⚠️  Nenhum procedimento válido encontrado para '{proc_csv}' com contraste obrigatório")
                                continue
                        
                        print(f"      ✅ Procedimento encontrado: {texto_selecionado} (similaridade: {melhor_similaridade:.2%})")
                        if not checkbox_selecionado.is_selected():
                            checkbox_selecionado.click()
                        checkboxes_marcados.append(checkbox_selecionado)
                        print(f"      ✅ Checkbox marcado com sucesso.")
                    else:
                        if contraste and contraste.upper() == 'S':
                            print(f"      ⚠️  Nenhum procedimento similar encontrado para '{proc_csv}' com 'COM CONTRASTE' (melhor similaridade: {melhor_similaridade:.2%})")
                        else:
                            print(f"      ⚠️  Nenhum procedimento similar encontrado para '{proc_csv}' (melhor similaridade: {melhor_similaridade:.2%})")
                
                print(f"   ✅ Total de {len(checkboxes_marcados)} checkbox(es) marcado(s) de {len(procedimentos_lista)} procedimento(s)")
            else:
                print("   ⚠️  Procedimento não informado no CSV, pulando seleção.")
            
           
            # Clica no botão Confirmar
            print("   Localizando botão Confirmar...")
            confirmar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnConfirmar")))
            print("   Botão Confirmar localizado. Clicando...")
            confirmar_button.click()
            print("   Botão Confirmar clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna ao fluxo após login (precisa refazer todo o processo)
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
                continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                continuar_button.click()
                time.sleep(2)
                # Refaz seleções
                pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                pa_select = Select(pa_dropdown)
                try:
                    pa_select.select_by_value("0045000")
                except:
                    pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                cid10_field.clear()
                cid10_field.send_keys("R68")
                cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                cpfprofsol_select = Select(cpfprofsol_dropdown)
                opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                if opcoes:
                    opcao_aleatoria = random.choice(opcoes)
                    cpfprofsol_select.select_by_value(opcao_aleatoria.get_attribute("value"))
                upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                upsexec_select = Select(upsexec_dropdown)
                upsexec_select.select_by_value("6861849")
                ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                ok_button.click()
                time.sleep(2)
                # Refaz marcação de checkboxes se houver procedimentos
                if procedimento:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                    checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                    checkboxes_marcados = []
                    procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
                    for proc_csv in procedimentos_lista:
                        melhor_similaridade = 0
                        checkbox_selecionado = None
                        for checkbox in checkboxes:
                            if checkbox in checkboxes_marcados:
                                continue
                            try:
                                td = checkbox.find_element(By.XPATH, "./..")
                                texto_opcao = td.text.strip()
                                similaridade = difflib.SequenceMatcher(None, proc_csv.upper(), texto_opcao.upper()).ratio()
                                palavras_procedimento = set(proc_csv.upper().split())
                                palavras_opcao = set(texto_opcao.upper().split())
                                palavras_comuns = palavras_procedimento.intersection(palavras_opcao)
                                if palavras_comuns:
                                    bonus = len(palavras_comuns) / max(len(palavras_procedimento), len(palavras_opcao))
                                    similaridade += bonus * 0.3
                                if similaridade > melhor_similaridade:
                                    melhor_similaridade = similaridade
                                    checkbox_selecionado = checkbox
                            except:
                                continue
                        if checkbox_selecionado and melhor_similaridade > 0.3:
                            if not checkbox_selecionado.is_selected():
                                checkbox_selecionado.click()
                            checkboxes_marcados.append(checkbox_selecionado)
                    confirmar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnConfirmar")))
                    confirmar_button.click()
                    time.sleep(2)
        
            # Localiza e clica no link que expande a tabela de vagas
            print("   Localizando link para expandir tabela de vagas...")
            try:
                # Procura pelo elemento com onclick contendo controleVagas('divUnidade0')
                vagas_link = wait.until(EC.element_to_be_clickable((
                    By.XPATH, 
                    "//td[@onclick=\"controleVagas('divUnidade0');\"]"
                )))
                print("   Link encontrado. Clicando para expandir tabela...")
                vagas_link.click()
                print("   Link clicado com sucesso.")
                time.sleep(1)  # Aguarda a tabela expandir
                
                # Verifica erro de sistema após mudança de página
                if verificar_erro_sistema():
                    print("   🔄 Refazendo login devido a erro de sistema...")
                    fazer_login()
                    # Se houver erro após clicar em vagas, precisa refazer todo o processo
                    print("   ⚠️  Erro após seleção de vagas. Processo precisa ser reiniciado manualmente.")
                    continue
            except TimeoutException:
                print("   ⚠️  Link de expansão não encontrado, tentando localizar tabela diretamente...")
            
            # Aguarda a tabela de vagas aparecer
            print("   Aguardando tabela de vagas carregar...")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
            
            # Seleciona o primeiro radio button disponível
            print("   Localizando primeiro radio button disponível...")
            try:
                # Encontra o primeiro radio button com name="vagas" que está visível
                primeiro_radio = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    "//input[@type='radio' and @name='vagas']"
                )))
                
                # Verifica se está visível e clicável
                if primeiro_radio.is_displayed():
                    print("   Primeiro radio button encontrado. Selecionando...")
                    primeiro_radio.click()
                    print("   Radio button selecionado com sucesso.")
                else:
                    # Tenta usar JavaScript para clicar se não estiver visível
                    navegador.execute_script("arguments[0].click();", primeiro_radio)
                    print("   Radio button selecionado via JavaScript.")
            except TimeoutException:
                print("   ⚠️  Nenhum radio button disponível encontrado.")
            
            time.sleep(1)  # Aguarda a seleção ser processada
            
            
            #aqui
            # Clica no botão Próxima Etapa
            print("   Localizando botão Próxima Etapa...")
            proxima_etapa_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnProximaEtapa")))
            print("   Botão Próxima Etapa localizado. Clicando...")
            proxima_etapa_button.click()
            print("   Botão Próxima Etapa clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Se houver erro após próxima etapa, precisa refazer todo o processo
                print("   ⚠️  Erro após próxima etapa. Processo precisa ser reiniciado manualmente.")
                continue

            # Extrai a chave da solicitação
            print("   Extraindo chave da solicitação...")
            chave_valor = ''
            try:
                chave_element = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="fichaCompleta"]/table[1]/tbody/tr[2]/td/b'
                )))
                chave_valor = chave_element.text.strip()
                print(f"   ✅ Chave extraída: {chave_valor}")
                df.at[index, 'chave'] = chave_valor
            except TimeoutException:
                print("   ⚠️  Campo de chave não encontrado.")
                df.at[index, 'chave'] = ''
            except Exception as e:
                print(f"   ❌ Erro ao extrair chave: {e}")
                df.at[index, 'chave'] = ''
            
            # Extrai o número da solicitação
            print("   Extraindo número da solicitação...")
            solicitacao_valor = ''
            try:
                solicitacao_element = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    '/html/body/div[2]/form/div[1]/div/table[5]/tbody/tr[3]/td[1]/font/b'
                )))
                solicitacao_valor = solicitacao_element.text.strip()
                print(f"   ✅ Solicitação extraída: {solicitacao_valor}")
                df.at[index, 'solicitacao'] = solicitacao_valor
            except TimeoutException:
                print("   ⚠️  Campo de solicitação não encontrado.")
                df.at[index, 'solicitacao'] = ''
            except Exception as e:
                print(f"   ❌ Erro ao extrair solicitação: {e}")
                df.at[index, 'solicitacao'] = ''
            
            # Verifica se chave e solicitação foram extraídas; se não, captura o conteúdo da página
            if not chave_valor and not solicitacao_valor:
                print("   ⚠️  Chave e solicitação não encontradas. Capturando conteúdo da página...")
                try:
                    # Captura o texto visível da página
                    conteudo_pagina = navegador.find_element(By.TAG_NAME, "body").text.strip()
                    # Limita o tamanho para não sobrecarregar o CSV (primeiros 500 caracteres)
                    conteudo_erro = conteudo_pagina[:500] if len(conteudo_pagina) > 500 else conteudo_pagina
                    if len(conteudo_pagina) > 500:
                        conteudo_erro += "... (conteúdo truncado)"
                    df.at[index, 'erro'] = conteudo_erro
                    print(f"   ✅ Conteúdo da página capturado e salvo na coluna 'erro'")
                except Exception as e:
                    print(f"   ❌ Erro ao capturar conteúdo da página: {e}")
                    df.at[index, 'erro'] = f"Erro ao capturar conteúdo: {str(e)}"
            else:
                # Limpa a coluna erro se a solicitação foi bem-sucedida
                df.at[index, 'erro'] = ''
            
            # Salva o CSV após extrair os dados
            try:
                df.to_csv(csv_exames, index=False)
                print(f"   💾 CSV atualizado com chave, solicitação e erro (se houver)")
            except Exception as e:
                print(f"   ⚠️  Erro ao salvar CSV: {e}")

        
        except Exception as e:
            print(f"❌ Erro ao processar solicitação para o CNS: {e}")
            continue
    
    # Salva o CSV final após processar todos os registros
    print("\n💾 Salvando CSV final...")
    try:
        df.to_csv(csv_exames, index=False)
        print(f"✅ CSV salvo com sucesso em: {csv_exames}")
        print(f"📊 Total de registros processados: {len(df)}")
    except Exception as e:
        print(f"❌ Erro ao salvar CSV final: {e}")
    
    # Verifica se há registros pendentes e reprocessa
    max_tentativas = 3  # Limite de tentativas para evitar loop infinito
    tentativa = 0
    
    while tentativa < max_tentativas:
        # Recarrega o CSV para verificar registros pendentes
        try:
            df_atualizado = pd.read_csv(csv_exames)
            
            # Garante que as colunas necessárias existem no DataFrame atualizado
            if 'procedimento' not in df_atualizado.columns:
                df_atualizado['procedimento'] = ''
            if 'contraste' not in df_atualizado.columns:
                df_atualizado['contraste'] = ''
            if 'erro' not in df_atualizado.columns:
                df_atualizado['erro'] = ''
            
            # Identifica registros pendentes (sem chave ou sem solicitacao)
            registros_pendentes = df_atualizado[
                (df_atualizado['chave'].isna() | (df_atualizado['chave'].astype(str).str.strip() == '')) |
                (df_atualizado['solicitacao'].isna() | (df_atualizado['solicitacao'].astype(str).str.strip() == ''))
            ]
            
            if len(registros_pendentes) == 0:
                print("\n✅ Todos os registros foram processados com sucesso!")
                break
            
            tentativa += 1
            print(f"\n🔄 Tentativa {tentativa}/{max_tentativas}: Encontrados {len(registros_pendentes)} registro(s) pendente(s)")
            print("   Reprocessando registros pendentes...")
            
            # Processa apenas os registros pendentes
            for index, row in registros_pendentes.iterrows():
                try:
                    # Verifica novamente se ainda está pendente (pode ter sido processado em outra tentativa)
                    chave_val = row.get('chave', '')
                    chave = str(chave_val).strip() if pd.notna(chave_val) and chave_val != '' else ''
                    
                    solicitacao_val = row.get('solicitacao', '')
                    solicitacao = str(solicitacao_val).strip() if pd.notna(solicitacao_val) and solicitacao_val != '' else ''
                    
                    if chave and solicitacao:
                        print(f"   ⏭️  Registro {index + 1} já foi processado. Pulando...")
                        continue
                    
                    cns_val = row.get('cns', '')
                    procedimento_val = row.get('procedimento', '')
                    procedimento = str(procedimento_val).strip() if pd.notna(procedimento_val) and procedimento_val != '' else ''
                    contraste_val = row.get('contraste', '')
                    contraste = str(contraste_val).strip() if pd.notna(contraste_val) and contraste_val != '' else ''
                    
                    # Valida e converte CNS para número
                    if pd.notna(cns_val) and str(cns_val).strip() != '':
                        try:
                            cns_float = float(cns_val)
                            cns = int(cns_float) if cns_float.is_integer() else cns_float
                        except (ValueError, TypeError):
                            print(f"   ❌ Erro: valor inválido na coluna 'cns': '{cns_val}'. Pulando registro...")
                            continue
                    else:
                        print(f"   ❌ Erro: coluna 'cns' está vazia. Pulando registro...")
                        continue
                    print(f"\n[{index + 1}/{len(registros_pendentes)}] Reprocessando CNS: {cns}")
                    if contraste and contraste.upper() == 'S':
                        print(f"   ℹ️  Contraste obrigatório: apenas procedimentos 'COM CONTRASTE' serão selecionados")
                    
                    navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                    time.sleep(2)
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Retorna à página de marcação após login
                        navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                        time.sleep(2)
                    
                    # Aguarda a página carregar e localiza o campo CNS
                    print("   Aguardando campo CNS carregar...")
                    cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                    print(f"   Campo CNS localizado. Inserindo CNS: {cns}")
                    
                    # Limpa o campo e insere o CNS
                    cns_field.clear()
                    cns_field.send_keys(str(cns))
                    print("   CNS inserido com sucesso.")
                    
                    # Localiza e clica no botão pesquisar
                    print("   Localizando botão pesquisar...")
                    pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                    print("   Botão pesquisar localizado. Clicando...")
                    pesquisar_button.click()
                    print("   Botão pesquisar clicado com sucesso.")
                    
                    time.sleep(2)  # Aguarda a pesquisa ser processada
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Retorna à página de marcação após login
                        navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                        time.sleep(2)
                        # Reinsere o CNS e clica em pesquisar novamente
                        cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                        cns_field.clear()
                        cns_field.send_keys(str(cns))
                        pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                        pesquisar_button.click()
                        time.sleep(2)
                    
                    # Continua com o restante do processamento...
                    # (código similar ao loop principal, mas sem repetir tudo aqui)
                    # Por simplicidade, vou reutilizar a mesma lógica do loop principal
                    # mas apenas para os registros pendentes
                    
                    # Seleciona o procedimento no dropdown "pa"
                    print("   Localizando dropdown de procedimento (pa)...")
                    pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                    pa_select = Select(pa_dropdown)
                    print("   Selecionando 'XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS'...")
                    
                    try:
                        pa_select.select_by_value("0045000")
                        print("   Procedimento selecionado com sucesso (por value).")
                    except Exception as e:
                        print(f"   ⚠️  Não foi possível selecionar por value, tentando por texto...")
                        try:
                            pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                            print("   Procedimento selecionado com sucesso (por texto).")
                        except Exception as e2:
                            print(f"   ❌ Erro ao selecionar procedimento: {e2}")
                            continue
                    
                    # Preenche o campo CID10
                    print("   Localizando campo CID10...")
                    cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                    print("   Campo CID10 localizado. Inserindo 'R68'...")
                    cid10_field.clear()
                    cid10_field.send_keys("R68")
                    print("   CID10 inserido com sucesso.")
                    
                    # Seleção aleatória no dropdown de profissional
                    print("   Localizando dropdown de profissional (cpfprofsol)...")
                    cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                    cpfprofsol_select = Select(cpfprofsol_dropdown)
                    
                    opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                    if opcoes:
                        opcao_aleatoria = random.choice(opcoes)
                        valor_aleatorio = opcao_aleatoria.get_attribute("value")
                        texto_aleatorio = opcao_aleatoria.text
                        print(f"   Selecionando profissional aleatório: {texto_aleatorio} (value: {valor_aleatorio})...")
                        cpfprofsol_select.select_by_value(valor_aleatorio)
                        print("   Profissional selecionado com sucesso.")
                    else:
                        print("   ⚠️  Nenhuma opção disponível no dropdown de profissional.")
                    
                    # Seleciona a unidade de execução
                    print("   Localizando dropdown de unidade de execução (upsexec)...")
                    upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                    upsexec_select = Select(upsexec_dropdown)
                    print("   Selecionando unidade com value '6861849'...")
                    upsexec_select.select_by_value("6861849")
                    print("   Unidade de execução selecionada com sucesso.")
                    
                    # Clica no botão OK
                    print("   Localizando botão OK...")
                    ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                    print("   Botão OK localizado. Clicando...")
                    ok_button.click()
                    print("   Botão OK clicado com sucesso.")
                    
                    time.sleep(2)  # Aguarda a próxima tela carregar
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Retorna ao fluxo após login (precisa refazer todo o processo)
                        navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                        time.sleep(2)
                        cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                        cns_field.clear()
                        cns_field.send_keys(str(cns))
                        pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                        pesquisar_button.click()
                        time.sleep(2)
                        continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                        continuar_button.click()
                        time.sleep(2)
                        # Refaz seleções
                        pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                        pa_select = Select(pa_dropdown)
                        try:
                            pa_select.select_by_value("0045000")
                        except:
                            pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                        cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                        cid10_field.clear()
                        cid10_field.send_keys("R68")
                        cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                        cpfprofsol_select = Select(cpfprofsol_dropdown)
                        opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                        if opcoes:
                            opcao_aleatoria = random.choice(opcoes)
                            cpfprofsol_select.select_by_value(opcao_aleatoria.get_attribute("value"))
                        upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                        upsexec_select = Select(upsexec_dropdown)
                        upsexec_select.select_by_value("6861849")
                        ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                        ok_button.click()
                        time.sleep(2)
                    
                    # Compara os procedimentos do CSV com as opções disponíveis na tabela
                    if procedimento:
                        procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
                        print(f"   Encontrados {len(procedimentos_lista)} procedimento(s) para processar")
                        
                        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                        checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                        checkboxes_marcados = []
                        
                        for proc_idx, proc_csv in enumerate(procedimentos_lista, 1):
                            print(f"   [{proc_idx}/{len(procedimentos_lista)}] Buscando procedimento mais similar a: {proc_csv}")
                            
                            melhor_similaridade = 0
                            checkbox_selecionado = None
                            texto_selecionado = ""
                            
                            for checkbox in checkboxes:
                                if checkbox in checkboxes_marcados:
                                    continue
                                    
                                try:
                                    td = checkbox.find_element(By.XPATH, "./..")
                                    texto_opcao = td.text.strip()
                                    
                                    # Se contraste for obrigatório ('s'), verifica se a opção contém "COM CONTRASTE"
                                    if contraste and contraste.upper() == 'S':
                                        # Normaliza o texto para comparação (remove espaços extras e converte para maiúsculas)
                                        texto_opcao_normalizado = ' '.join(texto_opcao.upper().split())
                                        if "COM CONTRASTE" not in texto_opcao_normalizado:
                                            # Pula esta opção se não contiver "COM CONTRASTE" - não considera para seleção
                                            continue
                                    
                                    similaridade = difflib.SequenceMatcher(None, proc_csv.upper(), texto_opcao.upper()).ratio()
                                    
                                    palavras_procedimento = set(proc_csv.upper().split())
                                    palavras_opcao = set(texto_opcao.upper().split())
                                    palavras_comuns = palavras_procedimento.intersection(palavras_opcao)
                                    
                                    if palavras_comuns:
                                        bonus = len(palavras_comuns) / max(len(palavras_procedimento), len(palavras_opcao))
                                        similaridade += bonus * 0.3
                                    
                                    if similaridade > melhor_similaridade:
                                        melhor_similaridade = similaridade
                                        checkbox_selecionado = checkbox
                                        texto_selecionado = texto_opcao
                                except Exception as e:
                                    continue
                            
                            if checkbox_selecionado and melhor_similaridade > 0.3:
                                # Verificação adicional: se contraste é obrigatório, confirma que a opção selecionada contém "COM CONTRASTE"
                                if contraste and contraste.upper() == 'S':
                                    texto_selecionado_normalizado = ' '.join(texto_selecionado.upper().split())
                                    if "COM CONTRASTE" not in texto_selecionado_normalizado:
                                        print(f"      ❌ Erro: Opção selecionada não contém 'COM CONTRASTE' como exigido. Opção: {texto_selecionado}")
                                        print(f"      ⚠️  Nenhum procedimento válido encontrado para '{proc_csv}' com contraste obrigatório")
                                        continue
                                
                                print(f"      ✅ Procedimento encontrado: {texto_selecionado} (similaridade: {melhor_similaridade:.2%})")
                                if not checkbox_selecionado.is_selected():
                                    checkbox_selecionado.click()
                                checkboxes_marcados.append(checkbox_selecionado)
                                print(f"      ✅ Checkbox marcado com sucesso.")
                            else:
                                if contraste and contraste.upper() == 'S':
                                    print(f"      ⚠️  Nenhum procedimento similar encontrado para '{proc_csv}' com 'COM CONTRASTE' (melhor similaridade: {melhor_similaridade:.2%})")
                                else:
                                    print(f"      ⚠️  Nenhum procedimento similar encontrado para '{proc_csv}' (melhor similaridade: {melhor_similaridade:.2%})")
                        
                        print(f"   ✅ Total de {len(checkboxes_marcados)} checkbox(es) marcado(s) de {len(procedimentos_lista)} procedimento(s)")
                    else:
                        print("   ⚠️  Procedimento não informado no CSV, pulando seleção.")
                    
                    # Clica no botão Confirmar
                    print("   Localizando botão Confirmar...")
                    confirmar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnConfirmar")))
                    print("   Botão Confirmar localizado. Clicando...")
                    confirmar_button.click()
                    print("   Botão Confirmar clicado com sucesso.")
                    
                    time.sleep(2)  # Aguarda a próxima tela carregar
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Se houver erro após confirmar, precisa refazer todo o processo
                        print("   ⚠️  Erro após confirmar. Processo precisa ser reiniciado manualmente.")
                        continue
                    
                    # Localiza e clica no link que expande a tabela de vagas
                    print("   Localizando link para expandir tabela de vagas...")
                    try:
                        vagas_link = wait.until(EC.element_to_be_clickable((
                            By.XPATH, 
                            "//td[@onclick=\"controleVagas('divUnidade0');\"]"
                        )))
                        print("   Link encontrado. Clicando para expandir tabela...")
                        vagas_link.click()
                        print("   Link clicado com sucesso.")
                        time.sleep(1)
                        
                        # Verifica erro de sistema após mudança de página
                        if verificar_erro_sistema():
                            print("   🔄 Refazendo login devido a erro de sistema...")
                            fazer_login()
                            print("   ⚠️  Erro após seleção de vagas. Processo precisa ser reiniciado manualmente.")
                            continue
                    except TimeoutException:
                        print("   ⚠️  Link de expansão não encontrado, tentando localizar tabela diretamente...")
                    
                    # Aguarda a tabela de vagas aparecer
                    print("   Aguardando tabela de vagas carregar...")
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                    
                    # Seleciona o primeiro radio button disponível
                    print("   Localizando primeiro radio button disponível...")
                    try:
                        primeiro_radio = wait.until(EC.presence_of_element_located((
                            By.XPATH,
                            "//input[@type='radio' and @name='vagas']"
                        )))
                        
                        if primeiro_radio.is_displayed():
                            print("   Primeiro radio button encontrado. Selecionando...")
                            primeiro_radio.click()
                            print("   Radio button selecionado com sucesso.")
                        else:
                            navegador.execute_script("arguments[0].click();", primeiro_radio)
                            print("   Radio button selecionado via JavaScript.")
                    except TimeoutException:
                        print("   ⚠️  Nenhum radio button disponível encontrado.")
                    
                    time.sleep(1)
                    
                    # Clica no botão Próxima Etapa
                    print("   Localizando botão Próxima Etapa...")
                    proxima_etapa_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnProximaEtapa")))
                    print("   Botão Próxima Etapa localizado. Clicando...")
                    proxima_etapa_button.click()
                    print("   Botão Próxima Etapa clicado com sucesso.")
                    
                    time.sleep(2)
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Se houver erro após próxima etapa, precisa refazer todo o processo
                        print("   ⚠️  Erro após próxima etapa. Processo precisa ser reiniciado manualmente.")
                        continue
                    
                    # Extrai a chave da solicitação
                    print("   Extraindo chave da solicitação...")
                    chave_valor = ''
                    try:
                        chave_element = wait.until(EC.presence_of_element_located((
                            By.XPATH,
                            '//*[@id="fichaCompleta"]/table[1]/tbody/tr[2]/td/b'
                        )))
                        chave_valor = chave_element.text.strip()
                        print(f"   ✅ Chave extraída: {chave_valor}")
                        df_atualizado.at[index, 'chave'] = chave_valor
                    except TimeoutException:
                        print("   ⚠️  Campo de chave não encontrado.")
                        df_atualizado.at[index, 'chave'] = ''
                    except Exception as e:
                        print(f"   ❌ Erro ao extrair chave: {e}")
                        df_atualizado.at[index, 'chave'] = ''
                    
                    # Extrai o número da solicitação
                    print("   Extraindo número da solicitação...")
                    solicitacao_valor = ''
                    try:
                        solicitacao_element = wait.until(EC.presence_of_element_located((
                            By.XPATH,
                            '/html/body/div[2]/form/div[1]/div/table[5]/tbody/tr[3]/td[1]/font/b'
                        )))
                        solicitacao_valor = solicitacao_element.text.strip()
                        print(f"   ✅ Solicitação extraída: {solicitacao_valor}")
                        
                        # Remove o .0 da solicitação se for um número inteiro
                        try:
                            solicitacao_float = float(solicitacao_valor)
                            solicitacao_valor = str(int(solicitacao_float)) if solicitacao_float.is_integer() else str(solicitacao_float)
                        except (ValueError, TypeError):
                            pass
                        
                        df_atualizado.at[index, 'solicitacao'] = solicitacao_valor
                    except TimeoutException:
                        print("   ⚠️  Campo de solicitação não encontrado.")
                        df_atualizado.at[index, 'solicitacao'] = ''
                    except Exception as e:
                        print(f"   ❌ Erro ao extrair solicitação: {e}")
                        df_atualizado.at[index, 'solicitacao'] = ''
                    
                    # Verifica se chave e solicitação foram extraídas; se não, captura o conteúdo da página
                    if not chave_valor and not solicitacao_valor:
                        print("   ⚠️  Chave e solicitação não encontradas. Capturando conteúdo da página...")
                        try:
                            # Captura o texto visível da página
                            conteudo_pagina = navegador.find_element(By.TAG_NAME, "body").text.strip()
                            # Limita o tamanho para não sobrecarregar o CSV (primeiros 500 caracteres)
                            conteudo_erro = conteudo_pagina[:500] if len(conteudo_pagina) > 500 else conteudo_pagina
                            if len(conteudo_pagina) > 500:
                                conteudo_erro += "... (conteúdo truncado)"
                            df_atualizado.at[index, 'erro'] = conteudo_erro
                            print(f"   ✅ Conteúdo da página capturado e salvo na coluna 'erro'")
                        except Exception as e:
                            print(f"   ❌ Erro ao capturar conteúdo da página: {e}")
                            df_atualizado.at[index, 'erro'] = f"Erro ao capturar conteúdo: {str(e)}"
                    else:
                        # Limpa a coluna erro se a solicitação foi bem-sucedida
                        df_atualizado.at[index, 'erro'] = ''
                    
                    # Salva o CSV após extrair os dados
                    try:
                        df_atualizado.to_csv(csv_exames, index=False)
                        print(f"   💾 CSV atualizado com chave, solicitação e erro (se houver)")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao salvar CSV: {e}")
                    
                except Exception as e:
                    print(f"❌ Erro ao reprocessar registro {index + 1}: {e}")
                    continue
            
            # Atualiza o DataFrame principal com os dados atualizados
            df = df_atualizado
            
        except Exception as e:
            print(f"❌ Erro ao verificar registros pendentes: {e}")
            break
    
    if tentativa >= max_tentativas:
        print(f"\n⚠️  Limite de {max_tentativas} tentativas atingido. Alguns registros podem estar pendentes.")
    
    # Salva o CSV final após todas as tentativas
    print("\n💾 Salvando CSV final...")
    try:
        df.to_csv(csv_exames, index=False)
        print(f"✅ CSV salvo com sucesso em: {csv_exames}")
        print(f"📊 Total de registros processados: {len(df)}")
    except Exception as e:
        print(f"❌ Erro ao salvar CSV final: {e}")
    
    # Fecha o navegador
    if navegador:
        navegador.quit()
        print("✅ Navegador fechado")
    
    return