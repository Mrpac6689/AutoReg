# autoreg/exames_ambulatoriais_consulta.py

import os
import csv
import time
import random
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
from autoreg.detecta_capchta import detecta_captcha
from datetime import datetime, timedelta

def buscar_valor_por_rotulo(navegador, wait, rotulo_texto, timeout=10):
    """
    Busca um valor na tabela procurando pelo rótulo e retornando o conteúdo da linha seguinte.
    
    Args:
        navegador: Instância do WebDriver
        wait: Instância do WebDriverWait
        rotulo_texto: Texto do rótulo a buscar (ex: "Chave de Confirmação:", "Código da Solicitação:")
        timeout: Timeout em segundos
    
    Returns:
        str: Valor encontrado ou None se não encontrado
    """
    try:
        # Cria um novo WebDriverWait com o timeout especificado
        wait_custom = WebDriverWait(navegador, timeout)
        
        # Tenta diferentes estratégias de busca
        rotulo_elemento = None
        
        # Estratégia 1: Busca direta pelo texto completo
        try:
            rotulo_xpath = f'//*[@id="fichaAmbulatorial"]//table//td[contains(., "{rotulo_texto}")]'
            rotulo_elemento = wait_custom.until(
                EC.presence_of_element_located((By.XPATH, rotulo_xpath))
            )
        except:
            # Estratégia 2: Busca sem o ":" no final
            try:
                rotulo_texto_sem_dois_pontos = rotulo_texto.replace(':', '').strip()
                rotulo_xpath = f'//*[@id="fichaAmbulatorial"]//table//td[contains(., "{rotulo_texto_sem_dois_pontos}")]'
                rotulo_elemento = wait_custom.until(
                    EC.presence_of_element_located((By.XPATH, rotulo_xpath))
                )
            except:
                # Estratégia 3: Busca por texto parcial (primeira palavra)
                try:
                    primeira_palavra = rotulo_texto.split()[0] if rotulo_texto.split() else rotulo_texto
                    rotulo_xpath = f'//*[@id="fichaAmbulatorial"]//table//td[contains(., "{primeira_palavra}")]'
                    rotulo_elemento = wait_custom.until(
                        EC.presence_of_element_located((By.XPATH, rotulo_xpath))
                    )
                except:
                    pass
        
        if not rotulo_elemento:
            return None
        
        # Encontra o elemento tr pai do rótulo
        tr_rotulo = rotulo_elemento.find_element(By.XPATH, './ancestor::tr')
        
        # Encontra o tbody que contém o rótulo
        tbody_rotulo = tr_rotulo.find_element(By.XPATH, './ancestor::tbody')
        
        # Tenta encontrar o próximo tr no mesmo tbody
        tr_valor = None
        try:
            tr_valor = tr_rotulo.find_element(By.XPATH, './following-sibling::tr[1]')
            # Verifica se está no mesmo tbody
            try:
                tbody_valor = tr_valor.find_element(By.XPATH, './ancestor::tbody')
                if tbody_valor != tbody_rotulo:
                    tr_valor = None  # Não está no mesmo tbody, precisa buscar de outra forma
            except:
                pass  # Se não conseguir verificar, assume que está no mesmo tbody
        except:
            tr_valor = None
        
        # Se não encontrou no mesmo tbody, tenta buscar no próximo tr do mesmo tbody usando índice
        if not tr_valor:
            try:
                # Pega todos os tr do tbody e encontra o índice do tr_rotulo
                todos_trs = tbody_rotulo.find_elements(By.XPATH, './tr')
                indice_rotulo = None
                for idx, tr in enumerate(todos_trs):
                    if tr == tr_rotulo:
                        indice_rotulo = idx
                        break
                
                if indice_rotulo is not None and indice_rotulo + 1 < len(todos_trs):
                    tr_valor = todos_trs[indice_rotulo + 1]
            except:
                pass
        
        # Se ainda não encontrou, tenta buscar no próximo tbody
        if not tr_valor:
            try:
                tbody_seguinte = tbody_rotulo.find_element(By.XPATH, './following-sibling::tbody[1]')
                tr_valor = tbody_seguinte.find_element(By.XPATH, './tr[1]')
            except:
                pass
        
        if not tr_valor:
            return None
        
        # Extrai o texto do tr de valor
        # Tenta pegar o texto da primeira célula (td) ou do elemento <b> dentro dela
        try:
            # Primeiro tenta pegar o elemento <b> dentro da primeira td
            td_valor = tr_valor.find_element(By.XPATH, './td[1]')
            try:
                b_elemento = td_valor.find_element(By.XPATH, './b')
                valor = b_elemento.text.strip()
            except:
                # Se não tiver <b>, pega o texto da td diretamente
                valor = td_valor.text.strip()
        except:
            # Se não conseguir pegar td[1], pega o texto completo do tr
            valor = tr_valor.text.strip()
        
        return valor if valor else None
    except Exception as e:
        print(f"      ⚠️  Erro ao buscar '{rotulo_texto}': {e}")
        return None

def buscar_procedimentos_solicitados(navegador, wait, timeout=10):
    """
    Busca todos os procedimentos solicitados na tabela.
    
    Args:
        navegador: Instância do WebDriver
        wait: Instância do WebDriverWait
        timeout: Timeout em segundos
    
    Returns:
        list: Lista de procedimentos encontrados
    """
    try:
        # Cria um novo WebDriverWait com o timeout especificado
        wait_custom = WebDriverWait(navegador, timeout)
        
        # Busca pelo rótulo "Procedimentos Solicitados:"
        rotulo_xpath = '//*[@id="fichaAmbulatorial"]//table//td[contains(., "Procedimentos Solicitados")]'
        rotulo_elemento = wait_custom.until(
            EC.presence_of_element_located((By.XPATH, rotulo_xpath))
        )
        
        # Encontra o elemento tr pai do rótulo
        tr_rotulo = rotulo_elemento.find_element(By.XPATH, './ancestor::tr')
        
        # Encontra o tbody que contém o rótulo
        tbody_rotulo = tr_rotulo.find_element(By.XPATH, './ancestor::tbody')
        
        # Busca todas as linhas tr dentro do mesmo tbody após o rótulo
        procedimentos = []
        
        # Pega a primeira linha após o rótulo (onde está o primeiro procedimento)
        contador = 1
        while contador <= 20:  # Limite de segurança
            try:
                tr_procedimento = tr_rotulo.find_element(By.XPATH, f'./following-sibling::tr[{contador}]')
                
                # Verifica se ainda está no mesmo tbody
                try:
                    tbody_procedimento = tr_procedimento.find_element(By.XPATH, './ancestor::tbody')
                    if tbody_procedimento != tbody_rotulo:
                        # Saiu do tbody, para de procurar
                        break
                except:
                    # Se não conseguir verificar o tbody, continua
                    pass
                
                # Verifica se é um cabeçalho de seção (tem classe td_titulo_tabela)
                try:
                    classe_tr = tr_procedimento.get_attribute('class') or ''
                    if 'td_titulo_tabela' in classe_tr:
                        # Encontrou um novo cabeçalho, para de procurar
                        break
                except:
                    pass
                
                # Pega o texto da primeira coluna (onde está o procedimento)
                try:
                    td_procedimento = tr_procedimento.find_element(By.XPATH, './td[1]')
                    procedimento_texto = td_procedimento.text.strip()
                    
                    # Verifica se não é um rótulo (rótulos geralmente têm ":" no final)
                    if procedimento_texto and not procedimento_texto.endswith(':'):
                        # Verifica se não é vazio e não está duplicado
                        if procedimento_texto and procedimento_texto not in procedimentos:
                            procedimentos.append(procedimento_texto)
                except:
                    # Se não conseguir pegar td[1], tenta pegar o texto completo do tr
                    try:
                        texto_tr = tr_procedimento.text.strip()
                        # Verifica se não é um rótulo e não está vazio
                        if texto_tr and not texto_tr.endswith(':') and texto_tr not in procedimentos:
                            # Verifica se não é apenas um número (código)
                            if not texto_tr.isdigit():
                                procedimentos.append(texto_tr)
                    except:
                        pass
                
                contador += 1
                    
            except NoSuchElementException:
                # Não há mais linhas
                break
            except Exception as e:
                # Outro erro, continua tentando
                contador += 1
                if contador > 20:
                    break
        
        return procedimentos
    except Exception as e:
        print(f"      ⚠️  Erro ao buscar procedimentos solicitados: {e}")
        return []

def capturar_informacoes_ficha(navegador, wait, df, index, csv_exames):
    """
    Captura informações da ficha ambulatorial após clicar em uma linha da tabela.
    
    Args:
        navegador: Instância do WebDriver
        wait: Instância do WebDriverWait
        df: DataFrame do pandas com os dados do CSV
        index: Índice da linha atual no DataFrame
        csv_exames: Caminho do arquivo CSV
    
    Returns:
        bool: True se capturou com sucesso, False caso contrário
    """
    try:
        # Aguarda a página carregar e verifica se o elemento principal existe
        print("   ⏳ Aguardando página da ficha ambulatorial carregar...")
        try:
            # Aguarda o elemento principal da ficha aparecer
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="fichaAmbulatorial"]'))
            )
            print("   ✅ Ficha ambulatorial carregada")
            time.sleep(2)  # Aguarda mais um pouco para garantir que tudo carregou
        except Exception as e:
            print(f"   ⚠️  Ficha ambulatorial pode não ter carregado completamente: {e}")
            time.sleep(3)  # Aguarda um pouco mais
        
        # Captura informações da ficha ambulatorial
        print("   📋 Capturando informações da ficha ambulatorial...")
        
        # Captura o número da chave
        print("   🔍 Buscando 'Chave de Confirmação:'...")
        chave_valor = buscar_valor_por_rotulo(navegador, wait, "Chave de Confirmação:")
        if chave_valor:
            df.at[index, 'chave'] = chave_valor
            print(f"   ✅ Chave capturada: {chave_valor}")
        else:
            print("   ⚠️  Chave não encontrada")
        
        # Captura o número da solicitação
        print("   🔍 Buscando 'Código da Solicitação:'...")
        solicitacao_valor = buscar_valor_por_rotulo(navegador, wait, "Código da Solicitação:")
        if solicitacao_valor:
            # Remove tags HTML e espaços extras
            solicitacao_valor = solicitacao_valor.strip()
            df.at[index, 'solicitacao'] = solicitacao_valor
            print(f"   ✅ Solicitação capturada: {solicitacao_valor}")
        else:
            print("   ⚠️  Solicitação não encontrada")
        
        # Captura os exames existentes (procedimentos solicitados)
        print("   🔍 Buscando 'Procedimentos Solicitados:'...")
        procedimentos = buscar_procedimentos_solicitados(navegador, wait)
        if procedimentos:
            # Junta os procedimentos com "|"
            exames_formatados = ' | '.join(procedimentos)
            df.at[index, 'existentes'] = exames_formatados
            print(f"   ✅ Exames existentes capturados: {len(procedimentos)} exame(s)")
            if exames_formatados:
                print(f"      {exames_formatados[:100]}..." if len(exames_formatados) > 100 else f"      {exames_formatados}")
        else:
            print("   ⚠️  Nenhum procedimento encontrado")
        
        # Adiciona observação (não sobrescreve se já houver conteúdo)
        obs_nova = "Solicitação pré-existente"
        obs_atual = df.at[index, 'obs']
        
        if pd.isna(obs_atual) or str(obs_atual).strip() == '':
            df.at[index, 'obs'] = obs_nova
        else:
            df.at[index, 'obs'] = f"{obs_atual} | {obs_nova}"
        
        print("   ✅ Observação adicionada")
        
        # Salva o CSV atualizado
        try:
            df.to_csv(csv_exames, index=False)
            print("   💾 CSV atualizado com informações capturadas")
        except Exception as e:
            print(f"   ⚠️  Erro ao salvar CSV atualizado: {e}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro ao capturar informações da ficha: {e}")
        return False

def exames_ambulatoriais_consulta():
    print("Consulta previa existência de solicitação no SISREG para o mesmo paciente e exame, lançada recentemente.")

    navegador = None
    
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)
    print("Acessando a página de Consulta de Exames Ambulatoriais...\n")

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

    # Verifica se a coluna 'cns' existe
    if 'cns' not in df.columns:
        print(f"   ❌ Coluna 'cns' não encontrada no arquivo. Colunas disponíveis: {', '.join(df.columns.tolist())}")
        print(f"   ℹ️  Adicione a coluna 'cns' ao CSV para continuar.")
        navegador.quit()
        return None
    
    # Garante que as colunas necessárias existem no DataFrame
    if 'procedimento' not in df.columns:
        df['procedimento'] = ''
    if 'chave' not in df.columns:
        df['chave'] = ''
    if 'solicitacao' not in df.columns:
        df['solicitacao'] = ''
    if 'existentes' not in df.columns:
        df['existentes'] = ''
    if 'obs' not in df.columns:
        df['obs'] = ''
    
    # Acessa diretamente a página de marcação após o login
    print("\n📋 Etapa 2: Acessando página de marcação...")
    try:
        navegador.get("https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
        print("   ✅ Página de marcação acessada com sucesso")
        time.sleep(2)
    except Exception as e:
        print(f"   ❌ Erro ao acessar página de marcação: {e}")
        navegador.quit()
        return None

    # Itera sobre as linhas do CSV
    print(f"\n📋 Etapa 3: Processando {len(df)} registro(s) do CSV...")
    for index, row in df.iterrows():
        try:
            # Verifica se há CAPTCHA antes de processar
            if not detecta_captcha(navegador):
                print("CAPTCHA não resolvido. Abortando processamento.")
                break
            # Obtém o CNS do CSV
            cns_csv = row.get('cns', '')
            
            # Verifica se o CNS está preenchido
            if pd.isna(cns_csv) or str(cns_csv).strip() == '':
                print(f"\n[{index + 1}/{len(df)}] ⚠️  CNS vazio na linha {index + 1}, pulando...")
                continue
            
            cns_csv = str(cns_csv).strip()
            print(f"\n[{index + 1}/{len(df)}] Processando CNS: {cns_csv}")
            
            # Volta para a página de marcação (caso tenha navegado para outra página)
            try:
                navegador.get("https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️  Erro ao recarregar página de marcação: {e}")
            
            # Preenche o campo nu_cns
            print("   Preenchendo campo CNS...")
            try:
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(cns_csv)
                print(f"   ✅ Campo CNS preenchido com: {cns_csv}")
            except TimeoutException:
                print(f"   ❌ Campo 'nu_cns' não encontrado na página")
                continue
            except Exception as e:
                print(f"   ❌ Erro ao preencher campo CNS: {e}")
                continue
            
            # Clica no botão btn_pesquisar
            print("   Clicando em 'btn_pesquisar'...")
            try:
                btn_pesquisar = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                btn_pesquisar.click()
                print("   ✅ Botão 'btn_pesquisar' clicado")
                time.sleep(3)  # Aguarda a página carregar
            except TimeoutException:
                print(f"   ❌ Botão 'btn_pesquisar' não encontrado")
                continue
            except Exception as e:
                print(f"   ❌ Erro ao clicar em 'btn_pesquisar': {e}")
                continue
            
            # Verifica o CNS retornado na página
            print("   Verificando CNS retornado na página...")
            try:
                cns_elemento = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="main_div"]/form/center[1]/table/tbody/tr[3]/td/font/b'))
                )
                cns_retornado = cns_elemento.text.strip()
                print(f"   ✅ CNS retornado: {cns_retornado}")
                
                # Compara os CNSs
                if cns_retornado == cns_csv:
                    print("   ✅ CNS correto, prosseguindo")
                else:
                    # CNS diferente encontrado, atualiza o CSV
                    print(f"   ℹ️  CNS diferente encontrado: {cns_retornado}")
                    df.at[index, 'cns'] = cns_retornado
                    
                    # Garante que a coluna 'obs' existe
                    if 'obs' not in df.columns:
                        df['obs'] = ''
                    
                    # Adiciona observação sobre atualização do CNS
                    obs_atual = df.at[index, 'obs']
                    if pd.isna(obs_atual) or str(obs_atual).strip() == '':
                        df.at[index, 'obs'] = "CNS atualizado conforme base DATASUS"
                    else:
                        df.at[index, 'obs'] = f"{obs_atual} | CNS atualizado conforme base DATASUS"
                    
                    # Salva o CSV atualizado
                    try:
                        df.to_csv(csv_exames, index=False)
                        print("   ✅ CNS atualizado conforme base DATASUS")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao salvar CSV atualizado: {e}")
                
            except TimeoutException:
                print("   ⚠️  Elemento com CNS não encontrado na página (pode não haver resultado)")
                # Se não encontrou o elemento, pode ser que não tenha retornado resultado
                # Continua o loop mesmo assim
            except Exception as e:
                print(f"   ⚠️  Erro ao verificar CNS retornado: {e}")
            
            # Nova etapa: Consulta no gerenciador de solicitação
            print("\n   📋 Etapa 4: Consultando solicitações recentes no gerenciador...")
            try:
                # Acessa diretamente a página do gerenciador de solicitação
                navegador.get("https://sisregiii.saude.gov.br/cgi-bin/gerenciador_solicitacao")
                print("   ✅ Página do gerenciador de solicitação acessada")
                time.sleep(2)
                
                # Preenche o campo cns_paciente
                print("   Preenchendo campo CNS do paciente...")
                cns_paciente_field = wait.until(EC.presence_of_element_located((By.NAME, "cns_paciente")))
                cns_paciente_field.clear()
                cns_paciente_field.send_keys(cns_csv)
                print(f"   ✅ Campo CNS do paciente preenchido com: {cns_csv}")
                
                # Clica no botão pesquisar
                print("   Clicando em 'pesquisar'...")
                btn_pesquisar_gerenciador = wait.until(EC.element_to_be_clickable((By.NAME, "pesquisar")))
                btn_pesquisar_gerenciador.click()
                print("   ✅ Botão 'pesquisar' clicado")
                time.sleep(3)  # Aguarda a tabela carregar
                
                # Verifica se há registros na tabela
                print("   Verificando registros na tabela...")
                try:
                    # Procura pela tabela de resultados
                    # Primeiro tenta encontrar o cabeçalho da tabela para identificar a coluna "Data da Solicitação"
                    indice_coluna_data = None
                    try:
                        # Procura pelo cabeçalho da tabela (thead ou primeira linha)
                        cabecalhos = navegador.find_elements(By.XPATH, "//table//thead//th | //table//tr[1]//th | //table//tr[1]//td")
                        for idx, cabecalho in enumerate(cabecalhos):
                            texto_cabecalho = cabecalho.text.strip().upper()
                            if "DATA" in texto_cabecalho and "SOLICITAÇÃO" in texto_cabecalho:
                                indice_coluna_data = idx
                                print(f"   ✅ Coluna 'Data da Solicitação' encontrada no índice {idx}")
                                break
                    except Exception as e:
                        print(f"   ⚠️  Não foi possível identificar a coluna pelo cabeçalho: {e}")
                    
                    # Procura por todas as linhas da tabela (tbody/tr)
                    linhas_tabela = navegador.find_elements(By.XPATH, "//table//tbody//tr")
                    
                    if not linhas_tabela:
                        print("   ℹ️  Nenhuma linha encontrada na tabela")
                    else:
                        print(f"   ✅ Encontradas {len(linhas_tabela)} linha(s) na tabela")
                        
                        # Calcula a data limite (7 dias atrás)
                        data_atual = datetime.now()
                        data_limite = data_atual - timedelta(days=7)
                        print(f"   📅 Verificando registros desde {data_limite.strftime('%d/%m/%Y')}")
                        
                        # Itera sobre as linhas da tabela
                        registro_encontrado = False
                        for idx, linha in enumerate(linhas_tabela):
                            try:
                                # Obtém todas as células da linha
                                celulas = linha.find_elements(By.TAG_NAME, "td")
                                
                                if len(celulas) == 0:
                                    continue
                                
                                # Se encontrou o índice da coluna de data, usa diretamente
                                if indice_coluna_data is not None and indice_coluna_data < len(celulas):
                                    texto_data = celulas[indice_coluna_data].text.strip()
                                else:
                                    # Se não encontrou o índice, procura em todas as células
                                    texto_data = None
                                    for celula in celulas:
                                        texto_celula = celula.text.strip()
                                        # Verifica se parece uma data
                                        if '/' in texto_celula and len(texto_celula) >= 8:
                                            texto_data = texto_celula
                                            break
                                
                                if texto_data:
                                    # Tenta fazer parse da data (formato brasileiro DD/MM/YYYY)
                                    try:
                                        # Remove espaços e pega apenas a parte da data (antes de espaço se houver hora)
                                        texto_data_limpo = texto_data.split()[0] if ' ' in texto_data else texto_data
                                        
                                        # Tenta diferentes formatos de data
                                        data_solicitacao = None
                                        for formato in ['%d/%m/%Y', '%d/%m/%Y %H:%M', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y']:
                                            try:
                                                data_solicitacao = datetime.strptime(texto_data_limpo, formato)
                                                break
                                            except:
                                                continue
                                        
                                        if data_solicitacao:
                                            # Verifica se a data está dentro dos últimos 7 dias
                                            if data_solicitacao >= data_limite:
                                                print(f"   ✅ Registro encontrado com data recente ({texto_data}): {data_solicitacao.strftime('%d/%m/%Y')}")
                                                # Clica na linha
                                                try:
                                                    linha.click()
                                                    print("   ✅ Linha clicada")
                                                    registro_encontrado = True
                                                    
                                                    # Captura informações da ficha ambulatorial
                                                    if capturar_informacoes_ficha(navegador, wait, df, index, csv_exames):
                                                        break
                                                except Exception as e:
                                                    print(f"   ⚠️  Erro ao clicar na linha: {e}")
                                                    # Tenta clicar em um elemento específico da linha
                                                    try:
                                                        link_linha = linha.find_element(By.TAG_NAME, "a")
                                                        link_linha.click()
                                                        print("   ✅ Link da linha clicado")
                                                        registro_encontrado = True
                                                        
                                                        # Captura informações da ficha ambulatorial
                                                        if capturar_informacoes_ficha(navegador, wait, df, index, csv_exames):
                                                            break
                                                    except Exception as e:
                                                        print(f"   ⚠️  Erro ao clicar no link da linha: {e}")
                                                        pass
                                    except Exception as e:
                                        # Se não conseguir fazer parse da data, continua procurando
                                        continue
                                
                            except Exception as e:
                                print(f"   ⚠️  Erro ao processar linha {idx + 1} da tabela: {e}")
                                continue
                        
                        if not registro_encontrado:
                            print("   ℹ️  Nenhum registro encontrado nos últimos 7 dias")
                            
                except Exception as e:
                    print(f"   ⚠️  Erro ao verificar tabela de resultados: {e}")
                    
            except TimeoutException as e:
                print(f"   ⚠️  Timeout ao acessar gerenciador de solicitação: {e}")
            except Exception as e:
                print(f"   ⚠️  Erro ao consultar gerenciador de solicitação: {e}")
            
        except Exception as e:
            print(f"\n[{index + 1}/{len(df)}] ❌ Erro ao processar linha {index + 1}: {e}")
            continue
    
    # Salva o CSV final após processar todos os registros
    print("\n💾 Salvando CSV final...")
    try:
        df.to_csv(csv_exames, index=False)
        print(f"✅ CSV salvo com sucesso em: {csv_exames}")
        print(f"📊 Total de registros processados: {len(df)}")
    except Exception as e:
        print(f"❌ Erro ao salvar CSV final: {e}")
    
    # Compara procedimentos GHOSP com existentes SISREG
    print("\n📋 Etapa 5: Comparando procedimentos GHOSP com existentes SISREG...")
    try:
        # Importa o módulo compartilhado com as funções auxiliares
        from autoreg import exames_utils
        
        # Compara cada linha do CSV
        linhas_comparadas = 0
        for index, row in df.iterrows():
            procedimento_ghosp = row.get('procedimento', '').strip() if pd.notna(row.get('procedimento')) else ''
            existentes_sisreg = row.get('existentes', '').strip() if pd.notna(row.get('existentes')) else ''
            
            # Se não há procedimento GHOSP ou não há existentes SISREG, pula
            if not procedimento_ghosp or not existentes_sisreg:
                continue
            
            # Garante que a coluna 'obs' existe
            if 'obs' not in df.columns:
                df['obs'] = ''
            
            # Separa os procedimentos existentes (podem estar separados por "|")
            procedimentos_existentes = [p.strip() for p in existentes_sisreg.split('|') if p.strip()]
            
            # Compara cada procedimento existente com o procedimento GHOSP
            exames_iguais = False
            exames_diferentes = False
            
            for proc_existente in procedimentos_existentes:
                # Usa as funções auxiliares para comparar
                tipo_exame_ghosp = exames_utils.identificar_tipo_exame(procedimento_ghosp)
                parte_corpo_ghosp = exames_utils.identificar_parte_corpo(procedimento_ghosp)
                lateralidade_ghosp = exames_utils.identificar_lateralidade(procedimento_ghosp)
                
                tipo_exame_sisreg = exames_utils.identificar_tipo_exame(proc_existente)
                parte_corpo_sisreg = exames_utils.identificar_parte_corpo(proc_existente)
                lateralidade_sisreg = exames_utils.identificar_lateralidade(proc_existente)
                
                # Verifica se são o mesmo exame usando as funções de correspondência
                mesmo_tipo = tipo_exame_ghosp == tipo_exame_sisreg
                mesma_parte = parte_corpo_ghosp == parte_corpo_sisreg
                mesma_lateralidade = lateralidade_ghosp == lateralidade_sisreg or (not lateralidade_ghosp and not lateralidade_sisreg)
                
                # Se tipo, parte e lateralidade são iguais, considera o mesmo exame
                if mesmo_tipo and mesma_parte and mesma_lateralidade:
                    exames_iguais = True
                    break
                else:
                    exames_diferentes = True
            
            # Adiciona observação conforme o resultado (sem sobrescrever)
            obs_atual = df.at[index, 'obs']
            if pd.isna(obs_atual) or str(obs_atual).strip() == '':
                obs_atual = ''
            
            if exames_iguais:
                obs_nova = "Exame já solicitado"
                if obs_atual:
                    df.at[index, 'obs'] = f"{obs_atual} | {obs_nova}"
                else:
                    df.at[index, 'obs'] = obs_nova
                linhas_comparadas += 1
            elif exames_diferentes:
                obs_nova = "Solicitação preexistente para exame diferente, solicitar?"
                if obs_atual:
                    df.at[index, 'obs'] = f"{obs_atual} | {obs_nova}"
                else:
                    df.at[index, 'obs'] = obs_nova
                linhas_comparadas += 1
        
        if linhas_comparadas > 0:
            print(f"   ✅ {linhas_comparadas} registro(s) comparado(s) e observações adicionadas")
            # Salva o CSV atualizado com as observações
            try:
                df.to_csv(csv_exames, index=False)
                print(f"   💾 CSV atualizado com observações de comparação")
            except Exception as e:
                print(f"   ⚠️  Erro ao salvar CSV com observações: {e}")
        else:
            print(f"   ℹ️  Nenhum registro com procedimento e existentes para comparar")
            
    except ImportError as e:
        print(f"   ⚠️  Erro ao importar módulo exames_utils: {e}")
        print(f"   ℹ️  Certifique-se de que o módulo autoreg/exames_utils.py existe")
    except Exception as e:
        print(f"   ⚠️  Erro ao comparar procedimentos: {e}")
    
    # Fecha o navegador
    if navegador:
        navegador.quit()
        print("✅ Navegador fechado")

def criar_modulo_compartilhado():
    """Cria o módulo compartilhado exames_utils.py com as funções auxiliares"""
    # Esta função será implementada se necessário
    pass
    