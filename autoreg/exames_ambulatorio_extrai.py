import os
import time
import pandas as pd
import re
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.justificativa_ghosp import XPATH_LINK_PACIENTE_BANNER
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def comparar_hora(hora_csv, data_hora_tabela):
    """
    Compara a hora do CSV com a data/hora da tabela.
    Retorna True se as horas coincidirem.
    
    Args:
        hora_csv: Hora do CSV (formato pode variar: "18:46", "18:46:00", etc.)
        data_hora_tabela: Data/hora da tabela no formato "DD/MM/YYYY HH:MM" (ex: "11/01/2026 18:46")
    
    Returns:
        bool: True se as horas coincidirem, False caso contrário
    """
    if not hora_csv or not data_hora_tabela:
        return True  # Se não houver hora no CSV, não filtra por hora
    
    try:
        # Extrai a hora da data/hora da tabela (formato: "DD/MM/YYYY HH:MM")
        partes_tabela = data_hora_tabela.strip().split()
        if len(partes_tabela) >= 2:
            hora_tabela = partes_tabela[1]  # "HH:MM"
            # Normaliza a hora do CSV (remove segundos se houver)
            hora_csv_normalizada = hora_csv.strip()
            if ':' in hora_csv_normalizada:
                # Pega apenas HH:MM
                partes_hora_csv = hora_csv_normalizada.split(':')
                hora_csv_normalizada = f"{partes_hora_csv[0]}:{partes_hora_csv[1]}"
            
            # Compara apenas HH:MM
            return hora_csv_normalizada == hora_tabela
    except Exception as e:
        print(f"   ⚠️  Erro ao comparar horas: {e}")
        return True  # Em caso de erro, não filtra (retorna True para não excluir)
    
    return True  # Se não conseguir comparar, não filtra

def exames_ambulatorio_extrai():
    print("\n---===> EXTRAÇÃO DE EXAMES A SOLICITAR <===---")

    
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
    
    driver = None

    # Inicializa o navegador e faz login
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)

        print("Iniciando o Chromedriver...")
        url_login = f"{caminho_ghosp}:4002/users/sign_in"
        driver.get(url_login)

        # Login
        print("Localizando campo de e-mail...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(usuario_ghosp)

        print("Localizando campo de senha...")
        senha_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        senha_field.send_keys(senha_ghosp)

        print("Localizando botão de login...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
        )
        login_button.click()
        print("Login realizado com sucesso!")

        # Garante que as colunas necessárias existem no DataFrame
        if 'procedimento' not in df.columns:
            df['procedimento'] = ''
        if 'hora' not in df.columns:
            print("   ⚠️  Coluna 'hora' não encontrada no CSV. A filtragem por hora não será aplicada.")
        if 'contraste' not in df.columns:
            df['contraste'] = ''
        if 'cns' not in df.columns:
            df['cns'] = ''
        
        # Reordena as colunas para garantir a ordem: ra, hora, contraste, cns, procedimento, ...
        colunas_ordenadas = ['ra']
        if 'hora' in df.columns:
            colunas_ordenadas.append('hora')
        if 'contraste' in df.columns:
            colunas_ordenadas.append('contraste')
        if 'cns' in df.columns:
            colunas_ordenadas.append('cns')
        if 'procedimento' in df.columns:
            colunas_ordenadas.append('procedimento')
        # Adiciona outras colunas que possam existir
        outras_colunas = [col for col in df.columns if col not in colunas_ordenadas]
        colunas_ordenadas.extend(outras_colunas)
        df = df[colunas_ordenadas]
        
        # Itera sobre os links do CSV
        for index, row in df.iterrows():
            try:
                ra = row['ra']
                ra_float = float(ra)
                # Remove o .0 se for um número inteiro
                ra = int(ra_float) if ra_float.is_integer() else ra_float
                
                # Lê a hora do CSV (se existir)
                hora_csv = None
                if 'hora' in df.columns:
                    hora_val = row.get('hora', '')
                    if pd.notna(hora_val) and hora_val != '':
                        hora_csv = str(hora_val).strip()
                        print(f"\n[{index + 1}/{len(df)}] Processando Registro de Atendimento {ra} - Hora: {hora_csv}")
                    else:
                        print(f"\n[{index + 1}/{len(df)}] Processando Registro de Atendimento {ra} - Hora não informada")
                else:
                    print(f"\n[{index + 1}/{len(df)}] Processando Registro de Atendimento {ra}")
                
                # Verifica se já existe CNS no CSV
                cns_valor = ''
                cns_existente = row.get('cns', '')
                if pd.notna(cns_existente) and str(cns_existente).strip() != '':
                    # Remove caracteres não numéricos do CNS existente
                    cns_valor = re.sub(r'\D', '', str(cns_existente))
                    print(f"   ✅ CNS já informado no CSV: {cns_valor}")
                else:
                    print(f"   ℹ️  CNS não informado no CSV. Será extraído do modal.")
                time.sleep(1)
                driver.get(f"{caminho_ghosp}:4002/nm/solcabs/new?intern_id={ra}&local=prsolexames")
                
                # Aguarda a tabela carregar
                print("   Aguardando tabela de exames carregar...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "lista_cancelamento"))
                )
                

                


                # Localiza todas as linhas com "TOMOGRAFIA" ou "ANGIO" na coluna Procedimento do atendimento específico
                print(f"   Buscando procedimentos de tomografia ou angio para o atendimento {ra}...")
                procedimentos_lista = []
                try:
                    # Encontra todas as linhas da tabela
                    todas_linhas = driver.find_elements(By.XPATH, '//table[@class="lista_cancelamento"]//tbody//tr')
                    
                    # Encontra o índice da linha do atendimento
                    atendimento_index = -1
                    for idx, linha in enumerate(todas_linhas):
                        try:
                            texto = linha.text
                            if f"Atendimento: {ra} De:" in texto:
                                atendimento_index = idx
                                break
                        except:
                            continue
                    
                    if atendimento_index >= 0:
                        print(f"   ✅ Seção do atendimento {ra} encontrada")
                        # Procura por tomografias nas linhas seguintes até a próxima linha de atendimento
                        for idx in range(atendimento_index + 1, len(todas_linhas)):
                            try:
                                linha = todas_linhas[idx]
                                # Verifica se é uma nova linha de atendimento (fim da seção atual)
                                texto_linha = linha.text
                                if "Atendimento:" in texto_linha and f"Atendimento: {ra} De:" not in texto_linha:
                                    print(f"   ✅ Fim da seção do atendimento {ra}")
                                    break
                                
                                # Verifica se a linha contém TOMOGRAFIA ou ANGIO na coluna Procedimento (4ª coluna)
                                try:
                                    # Primeiro verifica a data/hora (3ª coluna) se houver hora no CSV
                                    hora_coincide = True
                                    if hora_csv:
                                        try:
                                            data_hora_cell = linha.find_element(By.XPATH, './td[3]')
                                            data_hora_tabela = data_hora_cell.text.strip()
                                            hora_coincide = comparar_hora(hora_csv, data_hora_tabela)
                                        except:
                                            hora_coincide = True  # Se não conseguir ler a hora, não filtra
                                    
                                    # Se a hora coincidir (ou não houver hora no CSV), verifica o procedimento
                                    if hora_coincide:
                                        procedimento_cell = linha.find_element(By.XPATH, './td[4]')
                                        texto_procedimento = procedimento_cell.text.strip()
                                        
                                        if texto_procedimento and ("TOMOGRAFIA" in texto_procedimento.upper() or "ANGIO" in texto_procedimento.upper()):
                                            # Remove espaços extras e quebras de linha, mantendo apenas um espaço
                                            texto_limpo = ' '.join(texto_procedimento.split())
                                            if texto_limpo and texto_limpo not in procedimentos_lista:
                                                procedimentos_lista.append(texto_limpo)
                                                print(f"   ✅ Procedimento encontrado: {texto_limpo}")
                                except:
                                    continue
                            except:
                                continue
                    else:
                        print(f"   ⚠️  Atendimento {ra} não encontrado na tabela")
                    
                    # Junta todos os procedimentos com separador "|"
                    if procedimentos_lista:
                        procedimento_texto = ' | '.join(procedimentos_lista)
                        print(f"   ✅ Total de {len(procedimentos_lista)} procedimento(s) de tomografia/angio encontrado(s)")
                        df.at[index, 'procedimento'] = procedimento_texto
                    else:
                        print(f"   ⚠️  Nenhuma linha com 'TOMOGRAFIA' ou 'ANGIO' encontrada para o RA {ra}")
                        # Tenta clicar no botão "Tomografia" para carregar mais exames
                        try:
                            print(f"   🔄 Tentando clicar no botão 'Tomografia' para carregar mais exames...")
                            botao_tomografia = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, '//a[@class="botao btn-2nd mais_exames" and contains(text(), "Tomografia")]'))
                            )
                            botao_tomografia.click()
                            print(f"   ✅ Botão 'Tomografia' clicado. Aguardando 2 segundos...")
                            time.sleep(2)
                            
                            # Aguarda o div_mais_exames aparecer e carregar o conteúdo
                            print(f"   🔄 Aguardando conteúdo carregar no div_mais_exames...")
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.ID, "div_mais_exames"))
                                )
                            except:
                                pass  # Continua mesmo se não encontrar o div
                            
                            # Busca novamente pelos procedimentos após clicar no botão
                            print(f"   🔄 Buscando novamente procedimentos de tomografia...")
                            procedimentos_lista = []
                            
                            # Busca dentro do div_mais_exames (a estrutura é diferente: tbody está fora da table)
                            # Tenta buscar por tbody dentro do div_mais_exames ou diretamente por tr que contenham o RA
                            try:
                                # Primeiro tenta buscar dentro do div_mais_exames
                                div_mais_exames = driver.find_element(By.ID, "div_mais_exames")
                                # Busca todas as linhas tr dentro do div_mais_exames
                                todas_linhas = div_mais_exames.find_elements(By.XPATH, './/tbody//tr | .//tr[contains(@id, "solicitacao")]')
                            except:
                                # Fallback: busca em toda a página por linhas que possam conter os procedimentos
                                todas_linhas = driver.find_elements(By.XPATH, '//div[@id="div_mais_exames"]//tbody//tr | //div[@id="div_mais_exames"]//tr[contains(@id, "solicitacao")]')
                            
                            # Encontra o índice da linha do atendimento novamente
                            atendimento_index = -1
                            for idx, linha in enumerate(todas_linhas):
                                try:
                                    texto = linha.text
                                    if f"Atendimento: {ra}" in texto and "De:" in texto:
                                        atendimento_index = idx
                                        break
                                except:
                                    continue
                            
                            if atendimento_index >= 0:
                                print(f"   ✅ Seção do atendimento {ra} encontrada no div_mais_exames")
                                # Procura por tomografias nas linhas seguintes
                                for idx in range(atendimento_index + 1, len(todas_linhas)):
                                    try:
                                        linha = todas_linhas[idx]
                                        # Verifica se é uma nova linha de atendimento (fim da seção atual)
                                        texto_linha = linha.text
                                        if "Atendimento:" in texto_linha and f"Atendimento: {ra}" not in texto_linha:
                                            print(f"   ✅ Fim da seção do atendimento {ra}")
                                            break
                                        
                                        # Verifica se a linha contém TOMOGRAFIA ou ANGIO na coluna Procedimento (4ª coluna)
                                        try:
                                            # Primeiro verifica a data/hora (3ª coluna) se houver hora no CSV
                                            hora_coincide = True
                                            if hora_csv:
                                                try:
                                                    data_hora_cell = linha.find_element(By.XPATH, './td[3]')
                                                    data_hora_tabela = data_hora_cell.text.strip()
                                                    hora_coincide = comparar_hora(hora_csv, data_hora_tabela)
                                                except:
                                                    hora_coincide = True  # Se não conseguir ler a hora, não filtra
                                            
                                            # Se a hora coincidir (ou não houver hora no CSV), verifica o procedimento
                                            if hora_coincide:
                                                procedimento_cell = linha.find_element(By.XPATH, './td[4]')
                                                texto_procedimento = procedimento_cell.text.strip()
                                                
                                                if texto_procedimento and ("TOMOGRAFIA" in texto_procedimento.upper() or "ANGIO" in texto_procedimento.upper()):
                                                    # Remove espaços extras e quebras de linha, mantendo apenas um espaço
                                                    texto_limpo = ' '.join(texto_procedimento.split())
                                                    if texto_limpo and texto_limpo not in procedimentos_lista:
                                                        procedimentos_lista.append(texto_limpo)
                                                        print(f"   ✅ Procedimento encontrado: {texto_limpo}")
                                        except:
                                            continue
                                    except:
                                        continue
                            else:
                                # Se não encontrou pela linha de atendimento, tenta buscar diretamente por linhas com id="solicitacao"
                                print(f"   🔄 Tentando buscar diretamente por linhas de solicitação...")
                                try:
                                    linhas_solicitacao = driver.find_elements(By.XPATH, f'//div[@id="div_mais_exames"]//tr[contains(@id, "solicitacao")]')
                                    for linha in linhas_solicitacao:
                                        try:
                                            # Primeiro verifica a data/hora (3ª coluna) se houver hora no CSV
                                            hora_coincide = True
                                            if hora_csv:
                                                try:
                                                    data_hora_cell = linha.find_element(By.XPATH, './td[3]')
                                                    data_hora_tabela = data_hora_cell.text.strip()
                                                    hora_coincide = comparar_hora(hora_csv, data_hora_tabela)
                                                except:
                                                    hora_coincide = True  # Se não conseguir ler a hora, não filtra
                                            
                                            # Se a hora coincidir (ou não houver hora no CSV), verifica o procedimento
                                            if hora_coincide:
                                                # Verifica se a linha contém TOMOGRAFIA na coluna Procedimento (4ª coluna)
                                                procedimento_cell = linha.find_element(By.XPATH, './td[4]')
                                                texto_procedimento = procedimento_cell.text.strip()
                                                
                                                if texto_procedimento and "TOMOGRAFIA" in texto_procedimento.upper():
                                                    # Remove espaços extras e quebras de linha, mantendo apenas um espaço
                                                    texto_limpo = ' '.join(texto_procedimento.split())
                                                    if texto_limpo and texto_limpo not in procedimentos_lista:
                                                        procedimentos_lista.append(texto_limpo)
                                                        print(f"   ✅ Procedimento encontrado: {texto_limpo}")
                                        except:
                                            continue
                                except:
                                    pass
                            
                            # Verifica se encontrou procedimentos após clicar no botão
                            if procedimentos_lista:
                                procedimento_texto = ' | '.join(procedimentos_lista)
                                print(f"   ✅ Total de {len(procedimentos_lista)} procedimento(s) de tomografia/angio encontrado(s) após clicar no botão")
                                df.at[index, 'procedimento'] = procedimento_texto
                            else:
                                print(f"   ⚠️  Nenhuma linha com 'TOMOGRAFIA' ou 'ANGIO' encontrada mesmo após clicar no botão")
                                df.at[index, 'procedimento'] = ''
                                
                        except (TimeoutException, NoSuchElementException):
                            print(f"   ⚠️  Botão 'Tomografia' não encontrado ou não clicável")
                            df.at[index, 'procedimento'] = ''
                        except Exception as e:
                            print(f"   ⚠️  Erro ao tentar clicar no botão 'Tomografia': {e}")
                            df.at[index, 'procedimento'] = ''
                        
                except Exception as e:
                    print(f"   ❌ Erro ao localizar procedimentos: {e}")
                    df.at[index, 'procedimento'] = ''
                
                # Extrai CNS do modal apenas se não foi informado no CSV
                if not cns_valor:
                    print("   Abrindo modal de dados do paciente para extrair CNS...")
                    try:
                        # Clica no link para abrir o modal
                        paciente_link = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, XPATH_LINK_PACIENTE_BANNER))
                        )
                        paciente_link.click()
                        time.sleep(1)  # Aguarda o modal abrir
                        
                        # Aguarda o modal aparecer
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "ui-dialog-content"))
                        )
                        
                        # Tenta encontrar o campo CNS
                        print("   Buscando campo CNS...")
                        try:
                            # Encontra o div com texto "CNS:" e pega o próximo div com class "vcampo"
                            cns_cell = driver.find_element(
                                By.XPATH,
                                '//div[@class="span-4 direita dcampo" and contains(text(), "CNS:")]/following-sibling::div[@class="vcampo"]'
                            )
                            cns_texto = cns_cell.text.strip()
                            
                            if cns_texto and cns_texto != '':
                                # Extrai apenas os números
                                cns_valor = re.sub(r'\D', '', cns_texto)
                                print(f"   ✅ CNS encontrado: {cns_valor}")
                            else:
                                # Se CNS estiver vazio, busca CPF
                                print("   CNS vazio, buscando CPF...")
                                cpf_cell = driver.find_element(
                                    By.XPATH,
                                    '//div[@class="span-4 direita dcampo" and contains(text(), "CPF:")]/following-sibling::div[@class="vcampo"]'
                                )
                                cpf_texto = cpf_cell.text.strip()
                                
                                if cpf_texto and cpf_texto != '':
                                    # Extrai apenas os números
                                    cns_valor = re.sub(r'\D', '', cpf_texto)
                                    print(f"   ✅ CPF encontrado e usado como CNS: {cns_valor}")
                                else:
                                    print("   ⚠️  CNS e CPF vazios")
                        except NoSuchElementException:
                            print("   ⚠️  Campos CNS/CPF não encontrados no modal")
                        
                        # Fecha o modal (pode ser um botão X ou clicando fora)
                        try:
                            # Tenta encontrar e clicar no botão de fechar do modal
                            close_button = driver.find_element(By.CLASS_NAME, "ui-dialog-titlebar-close")
                            close_button.click()
                            time.sleep(0.5)
                        except:
                            # Se não encontrar o botão, tenta pressionar ESC
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                            time.sleep(0.5)
                        
                    except TimeoutException:
                        print("   ⚠️  Modal não encontrado ou não abriu")
                    except Exception as e:
                        print(f"   ❌ Erro ao extrair CNS/CPF: {e}")
                else:
                    print(f"   ⏭️  Pulando extração de CNS do modal (já informado no CSV)")
                
                # Atualiza o DataFrame com o CNS
                df.at[index, 'cns'] = cns_valor

                # Salva o CSV após cada processamento
                try:
                    df.to_csv(csv_exames, index=False)
                    print(f"   💾 CSV atualizado")
                except Exception as e:
                    print(f"   ⚠️  Erro ao salvar CSV: {e}")
              
            except Exception as e:
                print(f"❌ Erro ao processar Registro de Atendimento {index + 1}: {e}")
                continue
        
        # Salva o CSV final após processar todos os registros
        print("\n💾 Salvando CSV final...")
        try:
            df.to_csv(csv_exames, index=False)
            print(f"✅ CSV salvo com sucesso em: {csv_exames}")
            print(f"📊 Total de registros processados: {len(df)}")
        except Exception as e:
            print(f"❌ Erro ao salvar CSV final: {e}")

    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        if driver:
            driver.quit()
        return
    
    # Fecha o navegador
    if driver:
        driver.quit()
        print("✅ Navegador fechado")