import os
import time
import pandas as pd
import sys
import configparser
import calendar
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def producao_ambulatorial_gmus():
    """
    Selecione o período desejado abaixo

    """
    
    mes = input("Digite o mês (MM): ")
    ano = input("Digite o ano (AAAA): ")
        
    """
    Extrai dados de produção ambulatorial GMUs do SISREG.
    """
    print("\n---===> EXTRAÇÃO DE PRODUÇÃO AMBULATORIAL GMUs - SISREG <===---")
    
    # Definir diretório e caminho do CSV
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'producao_ambulatorial_gmus.csv')
    _, _, caminho_ghosp, _, _ = ler_credenciais()
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
    usuario_ghosp = config['G-HOSP-REG']['usuario']
    senha_ghosp = config['G-HOSP-REG']['senha']
        
    # Inicializar o driver
    print("🌐 Iniciando navegador...")
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Fazer login no SISREG
        url_login = f"{caminho_ghosp}:4010/users/sign_in"
        print(f"🔐 Acessando GHOSP: {url_login}")
        driver.get(url_login)
                
        # Realizar login
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
                EC.presence_of_element_located((By.XPATH, '//*[@id="user_password"]'))
            )
            senha_field.send_keys(senha_ghosp)

            # Localiza e clica no botão de login (//*[@id="new_user"]/div/input)
            print("Localizando botão de login...")
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
            )
            login_button.click()

            print("Login realizado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            driver.quit()
            return
               
        # Aguardar página carregar
        time.sleep(2)
        
        print("\n✅ Login realizado com sucesso!")
        print("🔍 Iniciando extração de dados de produção ambulatorial GMUs...")
        
        # Dicionário para converter número do mês para abreviação em PT-BR
        meses_dict = {
            "01": "Jan",
            "02": "Fev",
            "03": "Mar",
            "04": "Abr",
            "05": "Mai",
            "06": "Jun",
            "07": "Jul",
            "08": "Ago",
            "09": "Set",
            "10": "Out",
            "11": "Nov",
            "12": "Dez"
        }

        # Converter o mês para abreviação
        mes_abrev = meses_dict.get(mes, mes)
        print(f"📅 Período selecionado: {mes_abrev}/{ano}")

        # Identificar dias úteis do mês (excluindo sábados e domingos)
        print(f"\n🗓️  Identificando dias úteis de {mes_abrev}/{ano}...")
        
        ano_int = int(ano)
        mes_int = int(mes)
        
        # Obter o número de dias no mês
        num_dias = calendar.monthrange(ano_int, mes_int)[1]
        
        # Lista para armazenar os dias úteis
        dias_uteis = []
        
        # Percorrer todos os dias do mês
        for dia in range(1, num_dias + 1):
            data = datetime(ano_int, mes_int, dia)
            dia_semana = data.weekday()  # 0=segunda, 1=terça, ..., 5=sábado, 6=domingo
            
            # Adicionar apenas se não for sábado (5) nem domingo (6)
            if dia_semana < 5:  # Segunda a sexta-feira
                dias_uteis.append(dia)
        
        print(f"✅ Total de dias úteis encontrados: {len(dias_uteis)}")
        print(f"📋 Dias úteis: {dias_uteis}")
        
        # Lista para armazenar todos os dados extraídos
        dados_gmus = []
        
        # Loop pelos dias úteis
        print(f"\n🔄 Iniciando extração dos agendamentos...")
        for idx, dia in enumerate(dias_uteis, 1):
            try:
                # Formatar data no formato DD/MM/YYYY (para exibição)
                data_formatada = f"{dia:02d}/{mes}/{ano}"
                print(f"\n📅 [{idx}/{len(dias_uteis)}] Processando dia {data_formatada}...")
                
                # Formatar data no formato YYYY-MM-DD (para URL)
                data_url = f"{ano}-{mes}-{dia:02d}"
                
                # Navegar diretamente para a URL da agenda com a data específica
                url_agenda = f"{caminho_ghosp}:4010/gdrecursos/9/agenda_limpa?data_inicial={data_url}"
                driver.get(url_agenda)
                print(f"🌐 Navegando para: {url_agenda}")
                time.sleep(3)  # Aguardar a página carregar
                
                # Localizar a tabela de horários
                try:
                    tabela_horarios = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "tablehorarios"))
                    )
                    
                    # Encontrar o tbody da tabela
                    tbody = tabela_horarios.find_element(By.TAG_NAME, "tbody")
                    
                    # Encontrar todas as linhas (tr)
                    linhas = tbody.find_elements(By.TAG_NAME, "tr")
                    
                    periodo_atual = ""
                    posicao_atual = 0
                    
                    print(f"🔍 Analisando {len(linhas)} linhas...")
                    
                    for linha in linhas:
                        try:
                            # Verificar se é uma linha de cabeçalho de período
                            td = linha.find_element(By.TAG_NAME, "td")
                            texto_td = td.text.strip()
                            
                            # Identificar se é um marcador de período
                            if texto_td in ["Manha", "Tarde", ""]:
                                if texto_td == "Manha":
                                    periodo_atual = "Manha"
                                    posicao_atual = 0
                                    print(f"  🌅 Período: Manhã")
                                elif texto_td == "Tarde":
                                    periodo_atual = "Tarde"
                                    posicao_atual = 0
                                    print(f"  🌆 Período: Tarde")
                                elif texto_td == "" and periodo_atual == "":
                                    periodo_atual = "Manha"  # Considera vazio inicial como manhã
                                continue
                            
                            # Tentar encontrar o link do paciente
                            try:
                                link_paciente = td.find_element(
                                    By.XPATH, 
                                    ".//a[@data-remote='true' and contains(@href, '/gdagendas/') and contains(@href, '/edit')]"
                                )
                                
                                # Extrair o texto completo do link
                                texto_completo = link_paciente.text.strip()
                                
                                # Verificar se não é uma linha vazia (com pontos)
                                if "." * 10 not in texto_completo:
                                    # Extrair posição e nome
                                    # Formato: "1 NOME DO PACIENTE(SUS)"
                                    partes = texto_completo.split(maxsplit=1)
                                    if len(partes) >= 2:
                                        posicao = partes[0]
                                        nome_paciente = partes[1].strip()
                                        
                                        # Remover "(SUS)" do final se existir
                                        if nome_paciente.endswith("(SUS)"):
                                            nome_paciente = nome_paciente[:-5].strip()
                                        
                                        # Extrair informações do tooltip (agendador)
                                        agendador = ""
                                        try:
                                            # Passar o mouse sobre a linha para exibir o tooltip
                                            actions = ActionChains(driver)
                                            actions.move_to_element(linha).perform()
                                            
                                            # Aguardar o tooltip aparecer
                                            time.sleep(1)
                                            
                                            # Tentar localizar o tooltip
                                            try:
                                                tooltip = WebDriverWait(driver, 5).until(
                                                    EC.presence_of_element_located((By.CLASS_NAME, "tooltipster-content"))
                                                )
                                                
                                                # Extrair o texto completo do tooltip
                                                tooltip_text = tooltip.text
                                                
                                                # Procurar por "Agendado por: " no texto
                                                if "Agendado por:" in tooltip_text:
                                                    # Extrair o nome do agendador
                                                    inicio = tooltip_text.find("Agendado por:") + len("Agendado por:")
                                                    fim = tooltip_text.find("em:", inicio)
                                                    
                                                    if fim > inicio:
                                                        agendador = tooltip_text[inicio:fim].strip()
                                                
                                            except TimeoutException:
                                                # Tooltip não apareceu
                                                pass
                                            
                                        except Exception as e:
                                            # Erro ao extrair tooltip, continuar sem o agendador
                                            pass
                                        
                                        # Adicionar aos dados
                                        dados_gmus.append({
                                            'data': data_formatada,
                                            'periodo': periodo_atual,
                                            'posicao': posicao,
                                            'nome': nome_paciente,
                                            'agendador': agendador
                                        })
                                        
                                        print(f"    ✓ Pos {posicao} ({periodo_atual}): {nome_paciente} | Agendador: {agendador if agendador else 'N/A'}")
                                
                            except NoSuchElementException:
                                # Não é uma linha com paciente, provavelmente é vazia
                                pass
                                
                        except Exception as e:
                            # Erro ao processar linha específica
                            pass
                    
                    print(f"✅ Dia {data_formatada} processado: {len([d for d in dados_gmus if d['data'] == data_formatada])} agendamentos encontrados")
                    
                    # Salvar dados incrementalmente no CSV após cada dia
                    if dados_gmus:
                        df_gmus = pd.DataFrame(dados_gmus)
                        df_gmus.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        print(f"💾 Dados salvos no CSV ({len(dados_gmus)} registros)")

                    
                except TimeoutException:
                    print(f"⚠️ Tabela de horários não encontrada para o dia {data_formatada}")
                    continue
                
            except Exception as e:
                print(f"❌ Erro ao processar dia {dia}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Relatório final
        if dados_gmus:
            print(f"\n✅ Extração concluída!")
            print(f"📊 Total de agendamentos extraídos: {len(dados_gmus)}")
            print(f"💾 Arquivo final salvo em: {csv_path}")
            
            # Mostrar preview dos dados
            df_final = pd.DataFrame(dados_gmus)
            print(f"\n📋 Preview dos dados (primeiras 10 linhas):")
            print(df_final.head(10).to_string(index=False))
        else:
            print("\n⚠️ Nenhum agendamento foi encontrado!")

        time.sleep(2)
        # TODO: Implementar lógica específica de extração para GMUs
        # Esta função deve ser customizada conforme necessidade específica
        
        print(f"\n💾 Dados salvos em: {csv_path}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a extração: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🔒 Fechando navegador...")
        driver.quit()
        print("✅ Processo finalizado!")
