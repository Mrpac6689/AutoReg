import os
import time
import pandas as pd
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.justificativa_ghosp import tratar_justificativa_acesso
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.logging import setup_logging
import logging


def _ler_comando_terminal(prompt):
    """Lê um comando do terminal.

    Em um terminal interativo (TTY), detecta a tecla 's' ou 'p' imediatamente,
    sem exigir ENTER (modo não-canônico). Demais teclas são ignoradas.
    Em ambientes sem TTY (cron/pipe) ou sem termios, faz fallback para
    input() (exige ENTER).
    """
    import sys
    if not sys.stdin.isatty():
        return input(prompt).strip().lower()
    try:
        import termios, tty
    except ImportError:
        return input(prompt).strip().lower()

    sys.stdout.write(prompt)
    sys.stdout.flush()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == '\x03':              # Ctrl+C
                raise KeyboardInterrupt
            cmd = ch.lower()
            if cmd in ('s', 'p'):
                sys.stdout.write(cmd)     # eco da tecla detectada
                sys.stdout.flush()
                return cmd
            # qualquer outra tecla é ignorada; continua aguardando 's' ou 'p'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write('\n')
        sys.stdout.flush()


def solicita_pre_aih():

    print("\n---===> AJUSTA SOLICITAÇÕES E EXTRAI LINK DE AIH DO GHOSP <===---")

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_solicita = os.path.join(user_dir, 'solicita_inf_aih.csv')
    csv_internados = os.path.join(user_dir, 'internados_ghosp_avancado.csv')

    # Verifica se -spaa já preparou o CSV (possui links preenchidos).
    # Nesse caso, pula as Etapas 1-3 e processa apenas os registros sem link.
    print("\n📋 Verificando se -spaa já processou registros...")
    try:
        if os.path.exists(csv_solicita):
            df_check = pd.read_csv(csv_solicita)
            ja_preparado = 'link' in df_check.columns and df_check['link'].notna().any()
        else:
            ja_preparado = False
    except Exception:
        ja_preparado = False

    if ja_preparado:
        print("   ✅ CSV já preparado por -spaa — pulando Etapas 1-3")
    else:
        # Etapa 1: Limpar solicita_inf_aih.csv mantendo apenas o cabeçalho
        print("\n📋 Etapa 1: Preparando arquivo solicita_inf_aih.csv...")
        try:
            if os.path.exists(csv_solicita):
                df_solicita = pd.read_csv(csv_solicita)
                colunas = df_solicita.columns.tolist()
                print(f"   ✅ Arquivo encontrado com colunas: {', '.join(colunas)}")
            else:
                colunas = ['ra', 'link']
                print(f"   ⚠️  Arquivo não encontrado, criando com colunas padrão: {', '.join(colunas)}")

            df_solicita_limpo = pd.DataFrame(columns=colunas)
            df_solicita_limpo.to_csv(csv_solicita, index=False)
            print(f"   ✅ Arquivo limpo (mantido apenas cabeçalho)")

        except Exception as e:
            print(f"   ❌ Erro ao limpar solicita_inf_aih.csv: {e}")
            return None

        # Etapa 2: Extrair dados de internados_ghosp_avancado.csv
        print("\n📋 Etapa 2: Extraindo dados de internados_ghosp_avancado.csv...")
        try:
            if not os.path.exists(csv_internados):
                print(f"   ❌ Arquivo internados_ghosp_avancado.csv não encontrado em ~/AutoReg")
                return None

            df_internados = pd.read_csv(csv_internados)

            if 'internacao' not in df_internados.columns:
                print(f"   ❌ Coluna 'internacao' não encontrada no arquivo internados_ghosp_avancado.csv")
                print(f"   📄 Colunas disponíveis: {', '.join(df_internados.columns.tolist())}")
                return None

            solicitacoes = df_internados['internacao'].dropna()
            total_solicitacoes = len(solicitacoes)
            print(f"   ✅ Encontradas {total_solicitacoes} internações")

        except Exception as e:
            print(f"   ❌ Erro ao ler internados_ghosp_avancado.csv: {e}")
            return None

        # Etapa 3: Transferir dados para solicita_inf_aih.csv
        print("\n📋 Etapa 3: Transferindo dados para solicita_inf_aih.csv...")
        try:
            if 'ra' not in df_solicita_limpo.columns:
                df_solicita_limpo['ra'] = ''

            df_solicita_limpo['ra'] = solicitacoes.values

            if 'link' not in df_solicita_limpo.columns:
                df_solicita_limpo['link'] = ''

            df_solicita_limpo.to_csv(csv_solicita, index=False)
            print(f"   ✅ {total_solicitacoes} registros transferidos com sucesso")
            print(f"   📄 Arquivo salvo: {csv_solicita}")

        except Exception as e:
            print(f"   ❌ Erro ao transferir dados: {e}")
            return None

        print("\n✅ Preparação de arquivos concluída com sucesso!\n")

    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    url_login = f"{caminho_ghosp}:4002/users/sign_in"
    driver.get(url_login)

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
    from selenium.webdriver.common.action_chains import ActionChains

    csv_path = csv_solicita

    PAUSE_FLAG = os.path.join(user_dir, 'pause.flag')
    GRAVA_FLAG = os.path.join(user_dir, 'grava.flag')
    PULA_FLAG = os.path.join(user_dir, 'pula.flag')

    df = None

    try:
        df = pd.read_csv(csv_path)
        if 'ra' not in df.columns:
            print("❌ Arquivo CSV não contém a coluna 'ra'")
            driver.quit()
            return None

        if 'link' not in df.columns:
            df['link'] = ''

        # Filtra apenas registros sem link (deixados pelo -spaa para revisão manual)
        df = df[df['link'].isna() | (df['link'] == '')].reset_index(drop=True)
        if df.empty:
            print("✅ Todos os registros já foram processados por -spaa. Nada a fazer.")
            driver.quit()
            return None
        print(f"   📋 {len(df)} registro(s) pendentes de revisão manual")

    except FileNotFoundError:
        print("❌ Arquivo solicita_inf_aih.csv não encontrado em ~/AutoReg")
        driver.quit()
        return None

    i = 0
    while i < len(df):
        try:
            total_registros = len(df)
            ra = int(df.at[i, 'ra'])

            if os.path.exists(PAUSE_FLAG):
                print(f"\n⏳ Pausado... aguardando sinal do frontend para o registro {i + 1} (RA: {ra})...")
                print(f"Processando registro {i + 1}/{total_registros}: {ra}")
                time.sleep(1)
                driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")

                if tratar_justificativa_acesso(driver):
                    driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
                    time.sleep(1)

                while os.path.exists(PAUSE_FLAG):
                    time.sleep(1)

                    if os.path.exists(GRAVA_FLAG):
                        print("   ✅ Sinal 'grava' recebido!")
                        try:
                            os.remove(GRAVA_FLAG)
                        except Exception as e:
                            print(f"   ⚠️  Erro ao remover grava.flag: {e}")

                        url_atual = driver.current_url
                        print(f"   📍 URL capturada: {url_atual}")

                        df.at[i, 'link'] = url_atual
                        df.to_csv(csv_path, index=False)
                        print(f"   ✅ Link salvo no CSV para o registro {ra}")

                        try:
                            if '/formeletronicos' in url_atual:
                                botao_gravar = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//form[starts-with(@id, "edit_formeletronico_")]/div[2]/input'))
                                )
                                botao_gravar.click()
                                print(f"   ✅ Botão 'Gravar' (formeletronicos) clicado automaticamente")
                            elif '/printernlaudos' in url_atual:
                                botao_gravar = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//form[starts-with(@id, "edit_hhlaudosaih_")]/div/div/input'))
                                )
                                botao_gravar.click()
                                print(f"   ✅ Botão 'Gravar' (printernlaudos) clicado automaticamente")
                            else:
                                print(f"   ⚠️  URL não corresponde aos padrões esperados - botão não foi clicado")

                            time.sleep(1)
                        except Exception as e:
                            print(f"   ⚠️  Não foi possível clicar no botão 'Gravar': {e}")

                        i += 1
                        break

                    elif os.path.exists(PULA_FLAG):
                        print("   ✅ Sinal 'pula' recebido!")
                        try:
                            os.remove(PULA_FLAG)
                        except Exception as e:
                            print(f"   ⚠️  Erro ao remover pula.flag: {e}")

                        print(f"   🗑️  Removendo linha do registro {ra}")
                        df = df.drop(index=i).reset_index(drop=True)
                        df.to_csv(csv_path, index=False)
                        print(f"   ✅ Linha removida do CSV")
                        break

                if os.path.exists(PAUSE_FLAG):
                    continue

            else:
                print(f"\nProcessando registro {i + 1}/{total_registros}: {ra}")
                time.sleep(1)
                driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")

                if tratar_justificativa_acesso(driver):
                    driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
                    time.sleep(1)

                print(f"⏳ Aguardando interação do usuário para o registro {ra}...")
                print("   O usuário deve clicar no link desejado, fazer as alterações necessárias.")
                print("   💡 Comandos disponíveis:")
                print("      Pressione 's' - Salvar URL atual e avançar")
                print("      Pressione 'p' - Pular (remover linha) e avançar")

                try:
                    comando = _ler_comando_terminal("   👉 Pressione 's' ou 'p': ")

                    if comando == 's':
                        url_atual = driver.current_url
                        print(f"   📍 URL capturada: {url_atual}")

                        df.at[i, 'link'] = url_atual
                        df.to_csv(csv_path, index=False)
                        print(f"   ✅ Link salvo no CSV para o registro {ra}")

                        try:
                            if '/formeletronicos' in url_atual:
                                botao_gravar = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//form[starts-with(@id, "edit_formeletronico_")]/div[2]/input'))
                                )
                                botao_gravar.click()
                                print(f"   ✅ Botão 'Gravar' (formeletronicos) clicado automaticamente")
                            elif '/printernlaudos' in url_atual:
                                botao_gravar = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//form[starts-with(@id, "edit_hhlaudosaih_")]/div/div/input'))
                                )
                                botao_gravar.click()
                                print(f"   ✅ Botão 'Gravar' (printernlaudos) clicado automaticamente")
                            else:
                                print(f"   ⚠️  URL não corresponde aos padrões esperados - botão não foi clicado")

                            time.sleep(1)
                        except Exception as e:
                            print(f"   ⚠️  Não foi possível clicar no botão 'Gravar': {e}")

                        i += 1

                    elif comando == 'p':
                        print(f"   🗑️  Removendo linha do registro {ra}")
                        df = df.drop(index=i).reset_index(drop=True)
                        df.to_csv(csv_path, index=False)
                        print(f"   ✅ Linha removida do CSV")

                    else:
                        print(f"   ⚠️  Comando inválido '{comando}' - pulando registro sem alterar CSV")
                        i += 1

                except KeyboardInterrupt:
                    print("\n   ⚠️  Operação cancelada pelo usuário (Ctrl+C)")
                    raise
                except Exception as e:
                    print(f"   ⚠️ Erro ao processar comando: {e}")
                    i += 1


        except Exception as e:
            print(f"❌ Erro ao processar o registro: {e}")
            i += 1
