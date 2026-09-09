import os
import re
import time
import logging
import traceback
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.chrome_options import get_chrome_options
from autoreg.justificativa_ghosp import tratar_justificativa_acesso

JANELA_DIAS = 30
DATA_HORA_RE = re.compile(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}')


def _verifica_erro_500(driver):
    """Verifica se a página atual é a página de erro 500 do G-HOSP (Rails)."""
    try:
        src = driver.page_source
        return 'rails-default-error-page' in src or 'ocorreu um problema inesperado (500)' in src.lower()
    except Exception:
        return False


def _refaz_login_ghosp(driver, caminho_ghosp, usuario_ghosp, senha_ghosp):
    """Refaz o login no G-HOSP a partir da tela de usuário e senha."""
    print("Erro 500 detectado. Refazendo login no G-HOSP...")
    logging.warning("Erro 500 detectado no G-HOSP. Refazendo login...")
    driver.get(caminho_ghosp + ':4002/users/sign_in')
    time.sleep(2)
    email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
    email_field.clear()
    email_field.send_keys(usuario_ghosp)
    senha_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
    senha_field.clear()
    senha_field.send_keys(senha_ghosp)
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
    )
    login_button.click()
    time.sleep(5)
    print("Re-login realizado com sucesso!")
    logging.info("Re-login no G-HOSP realizado com sucesso após erro 500.")


def _navega_prontuarios(driver, caminho_ghosp, usuario_ghosp, senha_ghosp):
    """Navega para /prontuarios, refazendo login se encontrar erro 500."""
    url = caminho_ghosp + ':4002/prontuarios'
    driver.get(url)
    time.sleep(2)
    if _verifica_erro_500(driver):
        _refaz_login_ghosp(driver, caminho_ghosp, usuario_ghosp, senha_ghosp)
        driver.get(url)
        time.sleep(2)


def _navega_com_justificativa(driver, url):
    """driver.get(url), tratando a página de justificativa de acesso se surgir."""
    driver.get(url)
    time.sleep(1)
    if tratar_justificativa_acesso(driver):
        driver.get(url)
        time.sleep(1)


def _candidatos_historicopacs(driver, caminho_ghosp):
    """
    Após a busca em /prontuarios, retorna a lista de URLs completas de
    /historicopacs a considerar como candidatos ao paciente certo:
    - Se caiu em /listar_prontuarios: uma URL por linha da tabela de resultados.
    - Se caiu direto em /historicopacs/ID (nome único): lista com essa única URL.
    - Caso contrário (ex.: paciente ainda internado, sem histórico disponível
      diretamente): lista vazia.
    """
    url_atual = driver.current_url or ""
    if "listar_prontuarios" in url_atual:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.select("table.tableFixedHead tbody a[href^='/historicopacs/']")
        return [caminho_ghosp + ':4002' + a['href'] for a in links]
    if "historicopacs" in url_atual:
        return [url_atual]
    return []


def _extrai_ras_huerb(driver):
    """
    Extrai (ra, data_entrada) de cada RAitem da unidade HUERB na página de
    histórico do paciente atualmente carregada (mesma lógica de
    extrai_internados_ghosp_avancado.py).
    """
    ras = []
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container-procedimentos"))
        )
    except TimeoutException:
        return ras

    for item in container.find_elements(By.CLASS_NAME, "RAitem"):
        try:
            if 'HUERB' not in item.text.upper():
                continue
            ra_numero = item.find_element(By.CLASS_NAME, "ra").get_attribute("value")
            span_data = item.find_element(By.CLASS_NAME, "ml5").text
            data_texto = span_data.replace('\n', ' ').strip()
            m = re.search(r'(\d{2}/\d{2}/\d{4})\s*(\d{2}):\s*(\d{2})', data_texto)
            if not m:
                continue
            data_obj = datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%d/%m/%Y %H:%M")
            ras.append({'ra': ra_numero, 'data_entrada': data_obj})
        except Exception:
            continue
    return ras


def _encontra_ra_compativel(ras, data_avaliacao):
    """
    Entre os RAs HUERB extraídos, retorna o mais próximo (por baixo) da
    data_avaliacao dentro da janela [data_entrada, data_entrada+30 dias],
    ou None se nenhum RA satisfizer a janela.
    """
    candidatos = []
    for r in ras:
        diff_dias = (data_avaliacao.date() - r['data_entrada'].date()).days
        if 0 <= diff_dias <= JANELA_DIAS:
            candidatos.append((diff_dias, r['ra']))
    if not candidatos:
        return None
    candidatos.sort(key=lambda x: x[0])
    return candidatos[0][1]


def _extrai_avaliacoes_neurocirurgiao(driver, especialidade='NEUROCIRURGIÃO'):
    """
    Na página /pr/presavalprofs/solicitacoes já carregada, tenta expandir
    'Mostrar todas solicitações' e retorna a lista de avaliações realizadas
    da especialidade pedida: [{'profissional': ..., 'data_hora': datetime}, ...],
    ordenada por data/hora crescente.
    """
    try:
        driver.find_element(By.LINK_TEXT, "Mostrar todas solicitações").click()
        time.sleep(2)
    except NoSuchElementException:
        pass

    soup = BeautifulSoup(driver.page_source, "html.parser")
    avaliacoes = []
    for bloco in soup.select("div.col2"):
        col_l = bloco.select_one(".col2-L .tooltip-presavalprof .clear")
        col_r = bloco.select_one(".col2-R")
        if not col_l or not col_r:
            continue
        primeira_linha = col_l.get_text("\n").strip().splitlines()[0].strip()
        if primeira_linha.upper() != especialidade.upper():
            continue
        span_nome = col_r.select_one("span[title]")
        profissional = span_nome['title'].strip() if span_nome and span_nome.has_attr('title') else ''
        datas = DATA_HORA_RE.findall(col_r.get_text("\n"))
        if not datas:
            continue
        try:
            data_hora = datetime.strptime(datas[-1], "%d/%m/%Y %H:%M")
        except ValueError:
            continue
        avaliacoes.append({'profissional': profissional, 'data_hora': data_hora})

    avaliacoes.sort(key=lambda a: a['data_hora'])
    return avaliacoes


def especial_extrai():
    """
    Para cada linha de ~/AutoReg/saida_especial.csv (gerada por
    -especial-prepara), localiza o paciente no G-HOSP, identifica o RA
    (internação) cuja data de entrada está a até 30 dias antes da
    data_avaliacao, navega até as avaliações daquele RA e extrai o(s)
    neurocirurgião(ões) que realizaram a avaliação e a(s) respectiva(s)
    data/hora. Quando há mais de uma avaliação de NEUROCIRURGIÃO no mesmo
    RA, a primeira é gravada na própria linha e as demais viram linhas
    novas no CSV (não reprocessadas nesta mesma execução). Erros por linha
    são gravados na coluna 'erro' sem interromper o processamento.
    """
    setup_logging()
    print("\n---===> EXTRAÇÃO DE AVALIAÇÕES DE NEUROCIRURGIA (ESPECIAL) <===---")

    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'saida_especial.csv')
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo {csv_path} não encontrado. Rode -especial-prepara primeiro.")
        return

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    for col in ('ra', 'neurocirurgiao', 'data_hora_avaliacao', 'erro'):
        if col not in df.columns:
            df[col] = ''

    driver = None
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(caminho_ghosp + ':4002/users/sign_in')
        driver.set_window_size(1920, 1080)
        time.sleep(2)
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(usuario_ghosp)
        senha_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        senha_field.send_keys(senha_ghosp)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
        )
        login_button.click()
        time.sleep(5)
        print("Login no G-HOSP realizado com sucesso!")

        indices_originais = list(df.index)
        print(f"\nIniciando processamento de {len(indices_originais)} avaliações...")

        for pos, index in enumerate(indices_originais, start=1):
            nome = str(df.at[index, 'nome']).strip()
            setor = str(df.at[index, 'setor']).strip()
            data_avaliacao_str = str(df.at[index, 'data_avaliacao']).strip()
            print(f"\n[{pos}/{len(indices_originais)}] Processando: {nome} ({data_avaliacao_str})")

            df.at[index, 'erro'] = ""

            try:
                data_avaliacao = datetime.strptime(data_avaliacao_str, "%d/%m/%Y")

                _navega_prontuarios(driver, caminho_ghosp, usuario_ghosp, senha_ghosp)
                inp = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nome")))
                inp.clear()
                inp.send_keys(nome)
                driver.find_element(By.XPATH, '//input[@type="submit" and @value="Procurar"]').click()
                time.sleep(3)

                if _verifica_erro_500(driver):
                    _refaz_login_ghosp(driver, caminho_ghosp, usuario_ghosp, senha_ghosp)
                    raise Exception("Erro 500 após busca por nome - abortando tentativa atual")

                if tratar_justificativa_acesso(driver):
                    time.sleep(1)

                candidatos = _candidatos_historicopacs(driver, caminho_ghosp)
                if not candidatos:
                    df.at[index, 'erro'] = "Paciente não encontrado no GHOSP (sem histórico de prontuário acessível)"
                    df.to_csv(csv_path, index=False)
                    continue

                ra_encontrado = None
                for url_candidato in candidatos:
                    if driver.current_url != url_candidato:
                        _navega_com_justificativa(driver, url_candidato)
                    else:
                        if tratar_justificativa_acesso(driver):
                            driver.get(url_candidato)
                            time.sleep(1)

                    ras = _extrai_ras_huerb(driver)
                    ra_encontrado = _encontra_ra_compativel(ras, data_avaliacao)
                    if ra_encontrado:
                        break

                if not ra_encontrado:
                    df.at[index, 'erro'] = (
                        "Nenhum RA compatível encontrado (internação HUERB na janela de 30 dias)"
                    )
                    df.to_csv(csv_path, index=False)
                    continue

                url_avaliacoes = f"{caminho_ghosp}:4002/pr/presavalprofs/solicitacoes?intern_id={ra_encontrado}"
                _navega_com_justificativa(driver, url_avaliacoes)

                avaliacoes = _extrai_avaliacoes_neurocirurgiao(driver)
                if not avaliacoes:
                    df.at[index, 'ra'] = ra_encontrado
                    df.at[index, 'erro'] = f"Nenhuma avaliação de NEUROCIRURGIÃO encontrada para o RA {ra_encontrado}"
                    df.to_csv(csv_path, index=False)
                    continue

                primeira = avaliacoes[0]
                df.at[index, 'ra'] = ra_encontrado
                df.at[index, 'neurocirurgiao'] = primeira['profissional']
                df.at[index, 'data_hora_avaliacao'] = primeira['data_hora'].strftime("%d/%m/%Y %H:%M")
                df.at[index, 'erro'] = ""
                print(f"  ✓ RA {ra_encontrado}: {primeira['profissional']} em {df.at[index, 'data_hora_avaliacao']}")

                for extra in avaliacoes[1:]:
                    nova_linha = {
                        'nome': nome,
                        'setor': setor,
                        'data_avaliacao': data_avaliacao_str,
                        'ra': ra_encontrado,
                        'neurocirurgiao': extra['profissional'],
                        'data_hora_avaliacao': extra['data_hora'].strftime("%d/%m/%Y %H:%M"),
                        'erro': '',
                    }
                    df.loc[len(df)] = nova_linha
                    print(f"  ✓ Avaliação adicional gravada em nova linha: {extra['profissional']} em {nova_linha['data_hora_avaliacao']}")

            except Exception as e:
                print(f"Erro ao processar linha {pos}: {str(e)}")
                df.at[index, 'erro'] = f"Erro técnico: {str(e)}"

            df.to_csv(csv_path, index=False)

        df.to_csv(csv_path, index=False)
        print(f"\nProcessamento concluído. CSV atualizado em: {csv_path}")

    except Exception as e:
        print(f"Erro ao extrair avaliações especiais do GHOSP: {str(e)}")
        logging.error(f"Erro ao extrair avaliações especiais do GHOSP: {str(e)}")
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
