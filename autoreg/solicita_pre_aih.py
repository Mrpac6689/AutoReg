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

    csv_path = csv_solicita

    PAUSE_FLAG = os.path.join(user_dir, 'pause.flag')
    GRAVA_FLAG = os.path.join(user_dir, 'grava.flag')
    PULA_FLAG = os.path.join(user_dir, 'pula.flag')

    # Sinais órfãos de um clique anterior (ex.: "Gravar" clicado na TUI
    # durante o -spaa, 19/10/2026) seriam consumidos pelo primeiro registro
    # sem que ninguém o tivesse revisado
    for flag in (GRAVA_FLAG, PULA_FLAG):
        if os.path.exists(flag):
            os.remove(flag)
            logging.warning(f"-spa: {os.path.basename(flag)} órfão removido antes de iniciar")

    # Sem terminal (TUI, que roda com stdin=DEVNULL, ou cron) o input() de
    # _ler_comando_terminal() levanta EOFError e todo registro era pulado em
    # silêncio. Nesse caso a revisão só pode vir pelos flags de ~/AutoReg.
    import sys
    sem_terminal = not sys.stdin.isatty()
    if sem_terminal and not os.path.exists(PAUSE_FLAG):
        open(PAUSE_FLAG, 'w').close()
        print("   ⏸️  Sem terminal interativo: aguardando Gravar/Pular via pause.flag")

    try:
        df = pd.read_csv(csv_path)
        if 'ra' not in df.columns:
            print("❌ Arquivo CSV não contém a coluna 'ra'")
            driver.quit()
            return None

        if 'link' not in df.columns:
            df['link'] = ''
        # Coluna 'link' pode vir como float64 (NaN) do CSV quando todas as
        # linhas estão vazias — força dtype object para permitir gravar URLs.
        df['link'] = df['link'].astype(object)

        # Processa apenas os registros sem link (deixados pelo -spaa para
        # revisão manual), mas o CSV é sempre gravado inteiro: filtrar o df e
        # gravá-lo apagava todos os registros que o -spaa já tinha aprovado
        pendentes = [idx for idx in df.index if pd.isna(df.at[idx, 'link']) or str(df.at[idx, 'link']).strip() == '']
        if not pendentes:
            print("✅ Todos os registros já foram processados por -spaa. Nada a fazer.")
            driver.quit()
            return None
        print(f"   📋 {len(pendentes)} registro(s) pendentes de revisão manual")
        logging.info(f"-spa: {len(pendentes)} registro(s) pendentes de revisão manual")

    except FileNotFoundError:
        print("❌ Arquivo solicita_inf_aih.csv não encontrado em ~/AutoReg")
        driver.quit()
        return None

    def abrir_formeletronicos(ra):
        driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
        if tratar_justificativa_acesso(driver):
            driver.get(f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}")
            time.sleep(1)

    def gravar_link(idx, ra):
        url_atual = driver.current_url
        print(f"   📍 URL capturada: {url_atual}")
        df.at[idx, 'link'] = url_atual
        df.to_csv(csv_path, index=False)
        print(f"   ✅ Link salvo no CSV para o registro {ra}")
        logging.info(f"-spa RA {ra}: link gravado ({url_atual})")

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
                logging.warning(f"-spa RA {ra}: URL gravada fora dos padrões formeletronicos/printernlaudos — -sia não vai ler")

            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Não foi possível clicar no botão 'Gravar': {e}")

    def remover_registro(idx, ra):
        nonlocal df
        print(f"   🗑️  Removendo linha do registro {ra}")
        df = df.drop(index=idx)
        df.to_csv(csv_path, index=False)
        print(f"   ✅ Linha removida do CSV")
        logging.info(f"-spa RA {ra}: pulado pelo usuário, removido do CSV")

    total_registros = len(pendentes)
    for posicao, idx in enumerate(pendentes, start=1):
        try:
            ra = int(df.at[idx, 'ra'])
            print(f"\nProcessando registro {posicao}/{total_registros}: {ra}")

            if os.path.exists(PAUSE_FLAG):
                print(f"\n⏳ Pausado... aguardando sinal do frontend para o registro {posicao} (RA: {ra})...")
                time.sleep(1)
                abrir_formeletronicos(ra)

                while os.path.exists(PAUSE_FLAG):
                    time.sleep(1)

                    if os.path.exists(GRAVA_FLAG):
                        print("   ✅ Sinal 'grava' recebido!")
                        try:
                            os.remove(GRAVA_FLAG)
                        except Exception as e:
                            print(f"   ⚠️  Erro ao remover grava.flag: {e}")
                        gravar_link(idx, ra)
                        break

                    elif os.path.exists(PULA_FLAG):
                        print("   ✅ Sinal 'pula' recebido!")
                        try:
                            os.remove(PULA_FLAG)
                        except Exception as e:
                            print(f"   ⚠️  Erro ao remover pula.flag: {e}")
                        remover_registro(idx, ra)
                        break
                else:
                    # pause.flag removido (Retomar) sem Gravar/Pular: o registro
                    # fica sem link e segue para o -sia/-ssr como não revisado
                    print(f"   ⚠️  Retomado sem Gravar/Pular — registro {ra} fica sem link")
                    logging.warning(f"-spa RA {ra}: retomado sem Gravar/Pular — fica sem link")

            elif sem_terminal:
                print(f"   ⚠️  Sem terminal e sem pause.flag — registro {ra} fica sem link")
                logging.warning(f"-spa RA {ra}: sem terminal e sem pause.flag — fica sem link")

            else:
                time.sleep(1)
                abrir_formeletronicos(ra)

                print(f"⏳ Aguardando interação do usuário para o registro {ra}...")
                print("   O usuário deve clicar no link desejado, fazer as alterações necessárias.")
                print("   💡 Comandos disponíveis:")
                print("      Pressione 's' - Salvar URL atual e avançar")
                print("      Pressione 'p' - Pular (remover linha) e avançar")

                comando = _ler_comando_terminal("   👉 Pressione 's' ou 'p': ")
                if comando == 's':
                    gravar_link(idx, ra)
                elif comando == 'p':
                    remover_registro(idx, ra)
                else:
                    print(f"   ⚠️  Comando inválido '{comando}' - pulando registro sem alterar CSV")

        except KeyboardInterrupt:
            print("\n   ⚠️  Operação cancelada pelo usuário (Ctrl+C)")
            raise
        except Exception as e:
            print(f"❌ Erro ao processar o registro: {e}")
            logging.warning(f"-spa registro {posicao}/{total_registros}: {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}")

    if sem_terminal and os.path.exists(PAUSE_FLAG):
        os.remove(PAUSE_FLAG)
    driver.quit()
    return df
