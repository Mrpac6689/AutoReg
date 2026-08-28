import os
import re
import json
import time
import unicodedata
import pandas as pd
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.justificativa_ghosp import tratar_justificativa_acesso
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from autoreg.logging import setup_logging
import logging


CORRELACOES_PATH = os.path.expanduser('~/AutoReg/correlacoes_aih.json')

# Valores de retorno de _avaliar_registro
APROVADO   = 'aprovado'    # link capturado e gravado
MANUAL     = 'manual'      # sem condição satisfeita → linha fica para -spa
FALTA_AIH  = 'falta_aih'  # sem laudo em lugar nenhum → nota inserida + linha removida


# ── Normalização e lookup ─────────────────────────────────────────────────────

def _normalizar_clinica(texto):
    """Remove acentos e converte para maiúsculas para comparação de nomes de clínica."""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    sem_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acentos.upper().strip()


def _buscar_clinica_chave(clinica_valor, dicionario):
    """
    Retorna a chave real do dicionário que corresponde ao valor de clínica dado,
    normalizando ambos (sem acento, maiúsculo) para comparação.
    Retorna None se nenhuma chave corresponder.
    """
    clinica_norm = _normalizar_clinica(clinica_valor)
    for chave in dicionario:
        if _normalizar_clinica(chave) == clinica_norm:
            return chave
    return None


# ── Correlações e conversões ──────────────────────────────────────────────────

def _carregar_correlacoes():
    """
    Carrega e separa compatibilidades e conversões do arquivo JSON.
    Retorna (correlacoes, conversoes) onde:
      correlacoes = {"CLÍNICA X": {"prefixos": [...], "codigos": [...]}}
      conversoes  = {"CLÍNICA X": {"destino": "XXXXXXXXXX", "codigos": [...], "sempre": bool}}
    """
    if not os.path.exists(CORRELACOES_PATH):
        print(f"⚠️  Arquivo de correlações não encontrado: {CORRELACOES_PATH}")
        print("   Formato: {\"TIPO CLÍNICA\": {\"prefixos\": [...], \"codigos\": [...]}}")
        return {}, {}
    try:
        with open(CORRELACOES_PATH, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        conversoes = dados.get('conversoes', {})
        correlacoes = {
            k: v for k, v in dados.items()
            if not k.startswith('_') and k != 'conversoes'
        }
        n_conv = sum(len(v.get('codigos', [])) for v in conversoes.values())
        n_sempre = sum(1 for v in conversoes.values() if v.get('sempre', False))
        print(f"   ✅ Correlações: {len(correlacoes)} clínica(s), "
              f"{n_conv} conversão(ões) por código, {n_sempre} conversão(ões) universal(is)")
        return correlacoes, conversoes
    except Exception as e:
        print(f"❌ Erro ao carregar correlacoes_aih.json: {e}")
        return {}, {}


def _proc_compativel(proc_codigo, correlacoes, clinica_valor):
    """Retorna True se proc_codigo é compatível com clinica_valor nas correlações."""
    chave = _buscar_clinica_chave(clinica_valor, correlacoes)
    if chave is None:
        return False
    entrada = correlacoes[chave]
    if proc_codigo in entrada.get('codigos', []):
        return True
    return any(proc_codigo.startswith(p) for p in entrada.get('prefixos', []))


def _verificar_conversao(proc_codigo, clinica_valor, conversoes):
    """
    Retorna o código de destino se proc_codigo deve ser convertido nesta clínica,
    ou None se não há conversão definida.
    Se "sempre": true estiver no JSON, converte independentemente do código.
    """
    chave = _buscar_clinica_chave(clinica_valor, conversoes)
    if chave is None:
        return None
    entrada = conversoes[chave]
    if entrada.get('sempre', False):
        return entrada.get('destino')
    if proc_codigo in entrada.get('codigos', []):
        return entrada.get('destino')
    if any(proc_codigo.startswith(p) for p in entrada.get('prefixos', [])):
        return entrada.get('destino')
    return None


# ── Ações no formulário ───────────────────────────────────────────────────────

def _substituir_procedimento(driver, novo_codigo,
                             campo_id='campo_personalizado_laudo_aih_procedimento_solicitado'):
    """
    Substitui o campo de procedimento pelo novo_codigo via autocomplete.
    Tenta selecionar a primeira sugestão; se não aparecer, aceita com Tab.
    campo_id: ID do campo (diferente entre formeletronicos e printernlaudos).
    """
    try:
        proc_el = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, campo_id))
        )
        proc_el.clear()
        proc_el.send_keys(novo_codigo)
        time.sleep(2)

        try:
            primeira_opcao = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.ui-autocomplete .ui-menu-item:first-child a')
                )
            )
            primeira_opcao.click()
        except TimeoutException:
            proc_el.send_keys(Keys.TAB)

        time.sleep(1)
        print(f"   🔄 Campo procedimento atualizado para {novo_codigo}")
        return True
    except Exception as e:
        print(f"   ⚠️  Não foi possível substituir procedimento: {e}")
        return False


def _fechar_modal(driver):
    """Fecha o modal aberto (botão ✕ ou ESC como fallback)."""
    try:
        fechar = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.ui-dialog-titlebar-close'))
        )
        fechar.click()
        time.sleep(1)
    except Exception:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(1)


# ── Detecção de páginas ───────────────────────────────────────────────────────

def _formeletronicos_vazio(driver):
    """Retorna True se #lista-forms contém 'Nenhum registro'."""
    try:
        lista = driver.find_element(By.ID, 'lista-forms')
        return 'Nenhum registro' in lista.text
    except NoSuchElementException:
        return False


def _printernlaudos_vazio(driver, caminho_ghosp, ra):
    """
    Navega para printernlaudos e verifica se não há entradas de laudo.
    Deixa o driver na página de printernlaudos após a verificação.
    """
    url_printer = f"{caminho_ghosp}:4002/pr/printernlaudos?intern_id={ra}"
    driver.get(url_printer)
    time.sleep(1)
    try:
        linhas = driver.find_elements(
            By.XPATH, '//*[@id="lista_prlaudosmppes"]/tbody/tr'
        )
        return len(linhas) == 0
    except Exception:
        return True


def _inserir_nota_lembrete(driver, caminho_ghosp, ra, texto):
    """
    Navega para formeletronicos e insere um lembrete no prontuário.
    Retorna True se bem-sucedido, False em caso de falha.
    """
    try:
        url = f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}"
        driver.get(url)
        time.sleep(1)

        if tratar_justificativa_acesso(driver):
            driver.get(url)
            time.sleep(1)

        botao_lembrete = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="paciente"]/div[3]/div/h6/small/a')
            )
        )
        botao_lembrete.click()

        campo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="prlembrete_lembrete"]'))
        )
        campo.clear()
        campo.send_keys(texto)

        botao_salvar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="janela_modal"]/form/div[3]/input[1]')
            )
        )
        botao_salvar.click()
        time.sleep(1)
        print(f"   📝 Nota '{texto}' inserida para RA {ra}")
        return True
    except Exception as e:
        print(f"   ⚠️  Não foi possível inserir nota para RA {ra}: {e}")
        return False


# ── Extração e avaliação de laudos ────────────────────────────────────────────

def _extrair_laudos_aih(driver):
    """Retorna lista de URLs de edição dos Laudos AIH da página formeletronicos (mais recentes primeiro)."""
    laudos = []
    try:
        items = driver.find_elements(By.CSS_SELECTOR, 'li.formlist__list-item')
        for item in items:
            try:
                link_laudo = item.find_element(
                    By.CSS_SELECTOR, 'div.formlist__list-info p a[data-remote="true"]'
                )
                if link_laudo.text.strip() != 'Laudo AIH':
                    continue
                edit_el = item.find_element(By.CSS_SELECTOR, 'a[title="Editar"]')
                href = edit_el.get_attribute('href')
                if href:
                    laudos.append(href)
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"   ⚠️  Erro ao extrair Laudos AIH da lista: {e}")
    return laudos


def _avaliar_laudos_printernlaudos(driver, correlacoes, conversoes):
    """
    Itera as linhas da tabela #lista_prlaudosmppes (driver já está na página printernlaudos).
    Para cada linha: abre o modal de edição, lê procedimento e clínica,
    verifica conversão/compatibilidade. Se compatível ou conversível, deixa o modal
    aberto e retorna APROVADO (o chamador usa _gravar_link com a URL de printernlaudos).
    Se nenhuma linha for compatível, retorna MANUAL.
    """
    try:
        linhas = driver.find_elements(
            By.XPATH, '//*[@id="lista_prlaudosmppes"]/tbody/tr'
        )
    except Exception as e:
        print(f"   ⚠️  Erro ao ler tabela de printernlaudos: {e}")
        return MANUAL

    print(f"   📋 printernlaudos: {len(linhas)} laudo(s) — verificando compatibilidade...")

    for idx, linha in enumerate(linhas, 1):
        try:
            botao_editar = linha.find_element(
                By.CSS_SELECTOR, 'a.btn-i-editar[title="Editar"]'
            )
            print(f"   🔍 Laudo printernlaudos {idx}/{len(linhas)}")
            # data-remote="true" — JS click garante disparo do evento AJAX
            driver.execute_script("arguments[0].click();", botao_editar)

            # Aguarda o campo de procedimento aparecer no modal
            proc_el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'susproc_descricao'))
            )
            time.sleep(1)

            proc_texto = proc_el.get_attribute('value') or ''
            match_proc = re.search(r'\((\d+)\)', proc_texto)
            proc_codigo = match_proc.group(1) if match_proc else ''

            clinica_el = driver.find_element(By.ID, 'clinicas_descricao')
            clinica_valor = clinica_el.get_attribute('value') or ''

            print(f"      Procedimento: {proc_codigo!r}  |  Clínica: {clinica_valor!r}")

            # Conversão automática de código
            codigo_destino = _verificar_conversao(proc_codigo, clinica_valor, conversoes)
            if codigo_destino:
                print(f"   🔄 Conversão: {proc_codigo} → {codigo_destino} ({clinica_valor})")
                if _substituir_procedimento(driver, codigo_destino, campo_id='susproc_descricao'):
                    return APROVADO  # modal fica aberto; _gravar_link clica Gravar
                print(f"   ⚠️  Conversão falhou — tentando próximo laudo")
                _fechar_modal(driver)
                continue

            # Compatibilidade direta
            if _proc_compativel(proc_codigo, correlacoes, clinica_valor):
                print(f"   ✅ Compatível! Modal aberto para gravação.")
                return APROVADO  # modal fica aberto; _gravar_link clica Gravar

            print(f"   ℹ️  Não compatível (proc={proc_codigo!r}, clínica={clinica_valor!r})")
            _fechar_modal(driver)

        except Exception as e:
            print(f"   ⚠️  Erro ao verificar laudo {idx}: {e}")
            _fechar_modal(driver)

    print(f"   ℹ️  Nenhum laudo em printernlaudos foi compatível")
    return MANUAL


# ── Avaliação principal por RA ────────────────────────────────────────────────

def _avaliar_registro(driver, ra, correlacoes, conversoes, url_lista, caminho_ghosp):
    """
    Avalia se o RA pode ser processado automaticamente.

    Retorna:
      APROVADO   — Laudo compatível (ou convertido) encontrado; driver na página/modal de edição.
      FALTA_AIH  — Sem laudo em formulários nem em printernlaudos; nota inserida.
      MANUAL     — Nenhuma condição satisfeita; linha fica para -spa.
    """

    # ── Sem nenhum registro em formeletronicos ────────────────────────────────
    if _formeletronicos_vazio(driver):
        print(f"   ℹ️  RA {ra}: formeletronicos sem registros — verificando printernlaudos...")
        if _printernlaudos_vazio(driver, caminho_ghosp, ra):
            print(f"   ℹ️  RA {ra}: printernlaudos também vazio → inserindo nota FALTA AIH")
            _inserir_nota_lembrete(driver, caminho_ghosp, ra, 'FALTA AIH')
            return FALTA_AIH
        # printernlaudos tem registros — avalia laudos no modal
        return _avaliar_laudos_printernlaudos(driver, correlacoes, conversoes)

    # ── Condicional 1: Atendimento com o mesmo número do RA ──────────────────
    try:
        h5_elements = driver.find_elements(
            By.XPATH, '//div[contains(@class,"formlist__content")]//h5'
        )
        atendimento_ok = any(f"Atendimento: {ra}" in h5.text for h5 in h5_elements)
        if not atendimento_ok:
            print(f"   ℹ️  RA {ra}: nenhum Atendimento com este número")
            return MANUAL
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar Atendimento: {e}")
        return MANUAL

    # ── Condicional 2: Laudo AIH presente e compatível (ou conversível) ───────
    laudos_urls = _extrair_laudos_aih(driver)
    if not laudos_urls:
        print(f"   ℹ️  RA {ra}: nenhum Laudo AIH encontrado")
        return MANUAL
    print(f"   📋 RA {ra}: {len(laudos_urls)} Laudo(s) AIH — verificando compatibilidade...")

    for idx, edit_url in enumerate(laudos_urls, 1):
        try:
            print(f"   🔍 Laudo AIH {idx}/{len(laudos_urls)}: {edit_url}")
            driver.get(edit_url)
            time.sleep(1)

            proc_el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, 'campo_personalizado_laudo_aih_procedimento_solicitado')
                )
            )
            proc_texto = proc_el.get_attribute('value') or ''
            match_proc = re.search(r'\((\d+)\)', proc_texto)
            proc_codigo = match_proc.group(1) if match_proc else ''

            clinica_el = driver.find_element(By.ID, 'campo_personalizado_laudo_aih_clinica')
            clinica_valor = clinica_el.get_attribute('value') or ''

            print(f"      Procedimento: {proc_codigo!r}  |  Clínica: {clinica_valor!r}")

            # Conversão automática de código
            codigo_destino = _verificar_conversao(proc_codigo, clinica_valor, conversoes)
            if codigo_destino:
                print(f"   🔄 Conversão: {proc_codigo} → {codigo_destino} ({clinica_valor})")
                if _substituir_procedimento(driver, codigo_destino):
                    return APROVADO
                print(f"   ⚠️  Conversão falhou — tentando próximo laudo")
                continue

            # Compatibilidade direta
            if _proc_compativel(proc_codigo, correlacoes, clinica_valor):
                print(f"   ✅ Compatível! URL de edição capturada.")
                return APROVADO

            print(f"   ℹ️  Não compatível (proc={proc_codigo!r}, clínica={clinica_valor!r})")

        except Exception as e:
            print(f"   ⚠️  Erro ao verificar Laudo AIH {idx}: {e}")

    print(f"   ℹ️  RA {ra}: nenhum Laudo AIH compatível com as correlações")
    driver.get(url_lista)
    time.sleep(1)
    return MANUAL


# ── Gravação ──────────────────────────────────────────────────────────────────

def _gravar_link(driver, df, i, ra, csv_path):
    """
    Captura a URL atual, salva no CSV e clica no botão Gravar.
    Para printernlaudos, o botão Gravar está dentro do modal de edição aberto.
    """
    url_atual = driver.current_url
    print(f"   📍 URL capturada: {url_atual}")

    df.at[i, 'link'] = url_atual
    df.to_csv(csv_path, index=False)
    print(f"   ✅ Link salvo no CSV para o registro {ra}")

    try:
        if '/formeletronicos' in url_atual:
            botao_gravar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//form[starts-with(@id, "edit_formeletronico_")]/div[2]/input')
                )
            )
            botao_gravar.click()
            print("   ✅ Botão 'Gravar' (formeletronicos) clicado")
        elif '/printernlaudos' in url_atual:
            botao_gravar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//form[starts-with(@id, "edit_hhlaudosaih_")]/div/div/input')
                )
            )
            botao_gravar.click()
            print("   ✅ Botão 'Gravar' (printernlaudos/modal) clicado")
        else:
            print("   ⚠️  URL não corresponde aos padrões esperados — Gravar não clicado")
        time.sleep(1)
    except Exception as e:
        print(f"   ⚠️  Não foi possível clicar no botão 'Gravar': {e}")


# ── Função principal ──────────────────────────────────────────────────────────

def solicita_pre_aih_auto():

    print("\n---===> SOLICITAÇÃO PRÉ-AIH AUTOMÁTICA <===---")

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_solicita = os.path.join(user_dir, 'solicita_inf_aih.csv')
    csv_internados = os.path.join(user_dir, 'internados_ghosp_avancado.csv')

    # ── Carrega correlações e conversões ─────────────────────────────────────
    print("\n📋 Carregando correlações de procedimento × clínica...")
    correlacoes, conversoes = _carregar_correlacoes()
    if not correlacoes:
        print("   ⚠️  Nenhuma correlação carregada — todos os registros irão para -spa")

    # ── Etapa 1: Limpa solicita_inf_aih.csv mantendo apenas o cabeçalho ──────
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
        print("   ✅ Arquivo limpo (mantido apenas cabeçalho)")
    except Exception as e:
        print(f"   ❌ Erro ao limpar solicita_inf_aih.csv: {e}")
        return None

    # ── Etapa 2: Extrai RAs de internados_ghosp_avancado.csv ─────────────────
    print("\n📋 Etapa 2: Extraindo dados de internados_ghosp_avancado.csv...")
    try:
        if not os.path.exists(csv_internados):
            print("   ❌ Arquivo internados_ghosp_avancado.csv não encontrado em ~/AutoReg")
            return None

        df_internados = pd.read_csv(csv_internados)

        if 'internacao' not in df_internados.columns:
            print(f"   ❌ Coluna 'internacao' não encontrada")
            print(f"   📄 Colunas disponíveis: {', '.join(df_internados.columns.tolist())}")
            return None

        solicitacoes = df_internados['internacao'].dropna()
        total_solicitacoes = len(solicitacoes)
        print(f"   ✅ Encontradas {total_solicitacoes} internações")
    except Exception as e:
        print(f"   ❌ Erro ao ler internados_ghosp_avancado.csv: {e}")
        return None

    # ── Etapa 3: Transfere RAs para solicita_inf_aih.csv ─────────────────────
    print("\n📋 Etapa 3: Transferindo dados para solicita_inf_aih.csv...")
    try:
        if 'ra' not in df_solicita_limpo.columns:
            df_solicita_limpo['ra'] = ''
        df_solicita_limpo['ra'] = solicitacoes.values

        if 'link' not in df_solicita_limpo.columns:
            df_solicita_limpo['link'] = ''

        df_solicita_limpo.to_csv(csv_solicita, index=False)
        print(f"   ✅ {total_solicitacoes} registros transferidos com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao transferir dados: {e}")
        return None

    print("\n✅ Preparação de arquivos concluída!\n")

    # ── Selenium ──────────────────────────────────────────────────────────────
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    contagem_aprovados  = 0
    contagem_pulados    = 0
    contagem_falta_aih  = 0

    try:
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

        df = pd.read_csv(csv_solicita)
        if 'ra' not in df.columns:
            print("❌ Arquivo CSV não contém a coluna 'ra'")
            return None
        if 'link' not in df.columns:
            df['link'] = ''

        i = 0
        while i < len(df):
            total_registros = len(df)
            try:
                ra = int(df.at[i, 'ra'])
                print(f"\nProcessando registro {i + 1}/{total_registros}: RA {ra}")

                url_lista = f"{caminho_ghosp}:4002/pr/formeletronicos?intern_id={ra}"
                time.sleep(1)
                driver.get(url_lista)

                if tratar_justificativa_acesso(driver):
                    driver.get(url_lista)
                    time.sleep(1)

                resultado = _avaliar_registro(
                    driver, ra, correlacoes, conversoes, url_lista, caminho_ghosp
                )

                if resultado == APROVADO:
                    _gravar_link(driver, df, i, ra, csv_solicita)
                    contagem_aprovados += 1
                    i += 1

                elif resultado == FALTA_AIH:
                    print(f"   🗑️  RA {ra} removido do CSV (FALTA AIH registrada)")
                    df = df.drop(index=i).reset_index(drop=True)
                    df.to_csv(csv_solicita, index=False)
                    contagem_falta_aih += 1
                    # Não incrementa i: próxima linha agora ocupa este índice

                else:  # MANUAL
                    print(f"   ⏭️  RA {ra} encaminhado para revisão manual (-spa)")
                    contagem_pulados += 1
                    i += 1

            except Exception as e:
                print(f"❌ Erro ao processar RA {ra}: {e}")
                contagem_pulados += 1
                i += 1

            time.sleep(1)

    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        return None
    finally:
        print("\nFechando o navegador...")
        driver.quit()

    print(f"\n✅ Processamento automático concluído!")
    print(f"   Aprovados automaticamente : {contagem_aprovados}")
    print(f"   FALTA AIH (nota inserida) : {contagem_falta_aih}")
    print(f"   Encaminhados para -spa    : {contagem_pulados}")

    return df
