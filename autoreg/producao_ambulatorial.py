import os
import time
import pandas as pd
import sys
import configparser
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def producao_ambulatorial():
    """
    Extrai dados de produção ambulatorial do SISREG.
    """
    print("\n---===> EXTRAÇÃO DE PRODUÇÃO AMBULATORIAL - SISREG <===---")
    
    # Definir diretório e caminho do CSV
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'producao_ambulatorial.csv')
    
    # Ler credenciais
    config = configparser.ConfigParser()
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # Script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG-REG']['usuarioreg']
    senha_sisreg = config['SISREG-REG']['senhareg']
        
    # Inicializar o driver
    print("🌐 Iniciando navegador...")
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Fazer login no GHOSP
        url_login = "https://sisregiii.saude.gov.br"
        print(f"🔐 Acessando SISREG: {url_login}")
        driver.get(url_login)
                
        # Realizar login
        try:
            print("Localizando campo de usuário...")
            usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
            print("Campo de usuário localizado.")

            print("Localizando campo de senha...")
            senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
            print("Campo de senha localizado.")         

            print("Preenchendo usuário...")
            usuario_field.send_keys(usuario_sisreg)
            print("Usuário preenchido.")

            print("Preenchendo senha...")
            senha_field.send_keys(senha_sisreg)
            print("Senha preenchida.")

            print("Aguardando antes de clicar no botão de login...")
            time.sleep(1)

            print("Localizando botão de login...")
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
            print("Botão de login localizado.")

            print("Clicando no botão de login...")
            login_button.click()
            print("Botão de login clicado.")
            
        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            driver.quit()
            return
        
        
        # Aguardar até que o usuário execute as ações necessárias
        print("\n" + "="*80)
        print("⏳ AGUARDANDO AÇÕES DO USUÁRIO NO NAVEGADOR")
        print("="*80)
        print("👤 Execute as ações necessárias no SISREG:")
        print("   1. Configure os filtros desejados")
        print("   2. Clique no botão de exportação/geração do relatório")
        print("   3. Aguarde a tabela de resultados carregar")
        print("\n📍 Quando terminar, PRESSIONE ENTER neste terminal para continuar")
        print("="*80 + "\n")
        
        # Aguardar o usuário pressionar ENTER
        input("Pressione ENTER para continuar...")
        
        print("\n✅ Continuando com a extração dos dados...\n")
        
        # Aguardar um pouco para garantir que a página está estável
        time.sleep(2)
        

        # Extração dos códigos de solicitação
        print("\n🔍 Iniciando extração dos códigos de solicitação...")
        
        # Mudar para o iframe onde está a tabela
        try:
            print("🔄 Mudando para iframe 'f_main'...")
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
            print("  ✓ Iframe localizado e ativado")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️  Erro ao mudar para iframe: {e}")
            print("  Tentando continuar sem mudar de iframe...")
        
        # Verificar se existe checkpoint (última página processada)
        checkpoint_path = os.path.join(user_dir, 'producao_ambulatorial_checkpoint.txt')
        pagina_inicial = 1
        
        if os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, 'r') as f:
                    pagina_inicial = int(f.read().strip()) + 1
                print(f"\n📍 Checkpoint encontrado! Retomando da página {pagina_inicial}")
                
                # Navegar até a página do checkpoint
                if pagina_inicial > 1:
                    print(f"⏩ Avançando para página {pagina_inicial}...")
                    try:
                        campo_pagina = driver.find_element(By.NAME, "txtPagina")
                        campo_pagina.clear()
                        campo_pagina.send_keys(str(pagina_inicial))
                        
                        # Obter total de páginas do elemento
                        elemento_paginacao = driver.find_element(By.XPATH, "//td[contains(text(), 'Exibindo Página')]")
                        texto_paginacao = elemento_paginacao.text
                        # Extrair o número total de páginas do texto "de XXX"
                        import re
                        match = re.search(r'de (\d+)', texto_paginacao)
                        total_paginas = int(match.group(1)) if match else 999
                        
                        # Simular Enter
                        campo_pagina.send_keys('\n')
                        time.sleep(3)
                    except Exception as e:
                        print(f"  ⚠️  Erro ao navegar para checkpoint: {e}")
                        pagina_inicial = 1
            except Exception as e:
                print(f"  ⚠️  Erro ao ler checkpoint: {e}")
                pagina_inicial = 1
        
        # Carregar dados existentes se o CSV já existe
        dados = []
        if os.path.exists(csv_path):
            try:
                df_existente = pd.read_csv(csv_path, dtype=str)
                dados = df_existente.to_dict('records')
                print(f"📂 CSV existente carregado: {len(dados)} registros\n")
            except Exception as e:
                print(f"⚠️  Erro ao carregar CSV existente: {e}\n")
        
        pagina_atual = pagina_inicial
        contador_desde_ultimo_save = 0
        
        while True:
            print(f"\n📄 Processando página {pagina_atual}...")
            
            try:
                # Aguardar a tabela carregar
                time.sleep(2)
                
                # Localizar TODAS as tabelas com a classe table_listagem
                try:
                    tabelas = driver.find_elements(By.CLASS_NAME, "table_listagem")
                    print(f"  ℹ️  Total de tabelas encontradas: {len(tabelas)}")
                    
                    # A segunda tabela (índice 1) contém os dados
                    if len(tabelas) < 2:
                        print(f"  ⚠️  Tabela de dados não encontrada na página {pagina_atual}")
                        break
                    
                    tabela = tabelas[1]  # Pegar a segunda tabela
                    print(f"  ✓ Tabela de dados selecionada (segunda tabela)")
                except Exception as e:
                    print(f"  ⚠️  Erro ao localizar tabelas na página {pagina_atual}: {e}")
                    break
                
                # Encontrar todas as linhas da tabela (exceto cabeçalho)
                linhas = tabela.find_elements(By.TAG_NAME, "tr")
                print(f"  ℹ️  Total de linhas na tabela de dados: {len(linhas)}")
                
                # Contador de códigos extraídos nesta página
                codigos_pagina = 0
                
                # Percorrer as linhas (pular as 2 primeiras que são cabeçalhos)
                for idx, linha in enumerate(linhas[2:], start=3):
                    try:
                        # Pegar todas as células da linha
                        celulas = linha.find_elements(By.TAG_NAME, "td")
                        
                        if not celulas:
                            continue
                        
                        # Debug: mostrar conteúdo da primeira célula nas primeiras linhas
                        if pagina_atual == 1 and idx <= 5:
                            print(f"    Debug linha {idx}: {len(celulas)} células, primeira: '{celulas[0].text.strip()}'")
                        
                        # Se há células, a primeira contém o código de solicitação
                        if len(celulas) > 0:
                            codigo = celulas[0].text.strip()
                            
                            # Validar se é um número (código válido)
                            if codigo and codigo.isdigit():
                                dados.append({'solicitacao': codigo})
                                codigos_pagina += 1
                    
                    except Exception as e:
                        # Erro ao processar linha específica, continuar
                        if pagina_atual == 1 and idx <= 5:
                            print(f"    ⚠️  Erro ao processar linha {idx}: {e}")
                        continue
                
                print(f"  ✓ Extraídos {codigos_pagina} códigos nesta página")
                print(f"  📊 Total acumulado: {len(dados)} códigos")
                
                contador_desde_ultimo_save += 1
                
                # Salvar a cada 10 páginas
                if contador_desde_ultimo_save >= 10:
                    print(f"\n💾 Salvando progresso (página {pagina_atual})...")
                    try:
                        df_temp = pd.DataFrame(dados)
                        df_temp.to_csv(csv_path, index=False)
                        
                        # Atualizar checkpoint
                        with open(checkpoint_path, 'w') as f:
                            f.write(str(pagina_atual))
                        
                        print(f"  ✓ {len(dados)} registros salvos em {csv_path}")
                        print(f"  ✓ Checkpoint atualizado: página {pagina_atual}")
                        contador_desde_ultimo_save = 0
                    except Exception as e:
                        print(f"  ⚠️  Erro ao salvar progresso: {e}")
                
                # Detectar página atual e total de páginas
                try:
                    elemento_paginacao = driver.find_element(By.XPATH, "//td[contains(text(), 'Exibindo Página')]")
                    texto_paginacao = elemento_paginacao.text
                    # Extrair números do formato "Exibindo Página X de Y"
                    import re
                    match = re.search(r'value="(\d+)".*de (\d+)', driver.page_source)
                    if match:
                        pagina_detectada = int(match.group(1))
                        total_paginas = int(match.group(2))
                        print(f"  ℹ️  Página {pagina_detectada} de {total_paginas}")
                except:
                    pass
                
                # Tentar encontrar o botão de próxima página
                try:
                    # Localizar o link com a seta para a direita
                    botao_proxima = driver.find_element(By.XPATH, 
                        "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                    
                    # Verificar se o botão está habilitado (clicável)
                    if botao_proxima.is_displayed():
                        print(f"  ➡️  Avançando para próxima página...")
                        
                        # Clicar no link pai da imagem
                        link_proxima = botao_proxima.find_element(By.XPATH, "..")
                        link_proxima.click()
                        
                        pagina_atual += 1
                        
                        # Aguardar a nova página carregar
                        time.sleep(2)
                    else:
                        print(f"  ✓ Última página alcançada")
                        break
                        
                except NoSuchElementException:
                    print(f"  ✓ Botão 'Próxima' não encontrado - última página alcançada")
                    break
                    
            except Exception as e:
                print(f"  ⚠️  Erro ao processar página {pagina_atual}: {e}")
                break
        
        print(f"\n✅ Extração concluída!")
        print(f"📊 Total de páginas processadas: {pagina_atual}")
        print(f"📊 Total de códigos extraídos: {len(dados)}")
        


        # Salvar dados finais em CSV
        if dados:
            df = pd.DataFrame(dados)
            df.to_csv(csv_path, index=False)
            print(f"\n✅ Dados salvos em: {csv_path}")
            print(f"📊 Total de registros: {len(dados)}")
            
            # Remover checkpoint ao concluir com sucesso
            if os.path.exists(checkpoint_path):
                os.remove(checkpoint_path)
                print(f"✅ Checkpoint removido - extração completa")
        else:
            print("\n⚠️  Nenhum dado extraído")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Extração interrompida pelo usuário na página {pagina_atual}")
        print(f"💾 Salvando progresso...")
        
        if dados:
            df = pd.DataFrame(dados)
            df.to_csv(csv_path, index=False)
            with open(checkpoint_path, 'w') as f:
                f.write(str(pagina_atual))
            print(f"✅ {len(dados)} registros salvos")
            print(f"📍 Checkpoint salvo na página {pagina_atual}")
            print(f"▶️  Execute novamente para continuar de onde parou")
        
    except Exception as e:
        print(f"\n❌ Erro na execução na página {pagina_atual}: {e}")
        print(f"💾 Salvando progresso...")
        
        if dados:
            df = pd.DataFrame(dados)
            df.to_csv(csv_path, index=False)
            with open(checkpoint_path, 'w') as f:
                f.write(str(pagina_atual))
            print(f"✅ {len(dados)} registros salvos")
            print(f"📍 Checkpoint salvo na página {pagina_atual}")
            print(f"▶️  Execute novamente para continuar de onde parou")

    finally:
        # Fechar navegador
        print("\n🔒 Fechando navegador...")
        driver.quit()

