"""
Módulo para extração e análise de internações duplicadas no sistema SISREG.
Funções principais:
- extrai_internacoes_duplicadas(): Orquestra o fluxo de extração e análise.
- sisreg_internados(): Extrai lista de internados (saída/permanência) e salva em CSV.
- sisreg_a_internar(): Extrai lista de pacientes a internar e salva em CSV.
- compara_duplicados(): Identifica nomes presentes em ambas as listas e preenche coluna DUPLICADOS.
- codigo_duplicados(): Extrai o código SISREG de cada duplicado e preenche coluna CODIGO.

Arquivo de saída: ~/AutoReg/internacoes_duplicadas.csv (colunas: ENTRADA, SAIDA, DUPLICADOS, CODIGO)
"""
import os
import time
import traceback
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging

setup_logging()


def extrai_internacoes_duplicadas():
    sisreg_internados()
    sisreg_a_internar()
    compara_duplicados()
    codigo_duplicados()


def sisreg_internados():
    print("\n---===> EXTRAÇÃO DE INTERNADOS (SAÍDA/PERMANÊNCIA) <===---")
    logging.info("---===> EXTRAÇÃO DE INTERNADOS (SAÍDA/PERMANÊNCIA) <===---")
    nomes = []
    navegador = None
    try:
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)

        print("Acessando SISREG...")
        navegador.get("https://sisregiii.saude.gov.br")

        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)

        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))).click()
        time.sleep(5)
        print("Login realizado com sucesso!")
        logging.info("Login SISREG realizado.")

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
        time.sleep(5)
        print("Página de Saída/Permanência acessada.")
        logging.info("Página de Saída/Permanência acessada.")

        WebDriverWait(navegador, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))

        WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
        ).click()
        time.sleep(5)

        while True:
            linhas = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas:
                nomes.append(linha.find_element(By.XPATH, './td[2]').text)

            try:
                next_page_button = WebDriverWait(navegador, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']"))
                )
                next_page_button.click()
                time.sleep(5)
            except Exception:
                print("Não há mais páginas.")
                break

        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

        if os.path.exists(csv_path):
            df_existente = pd.read_csv(csv_path)
            if 'ENTRADA' not in df_existente.columns:
                df_existente.insert(0, 'ENTRADA', '')
        else:
            df_existente = pd.DataFrame({'ENTRADA': []})

        df_saida = pd.DataFrame({'SAIDA': nomes})
        max_len = max(len(df_existente), len(df_saida))
        df_existente = df_existente.reindex(range(max_len)).reset_index(drop=True)
        df_saida = df_saida.reindex(range(max_len)).reset_index(drop=True)
        df_final = pd.concat([df_existente['ENTRADA'], df_saida['SAIDA']], axis=1)

        df_final.to_csv(csv_path, index=False)
        print(f"✅ {len(nomes)} internados salvos em '{csv_path}'.")
        logging.info(f"{len(nomes)} internados salvos em '{csv_path}'.")

    except TimeoutException:
        print("❌ Timeout ao localizar elementos na página.")
        logging.error("Timeout ao localizar elementos na página.")
    except NoSuchElementException as e:
        print(f"❌ Elemento não encontrado: {e}")
        logging.error(f"Elemento não encontrado: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
        print("Navegador fechado.")
        logging.info("Navegador fechado.")


def sisreg_a_internar():
    print("\n---===> EXTRAÇÃO DE PACIENTES A INTERNAR <===---")
    logging.info("---===> EXTRAÇÃO DE PACIENTES A INTERNAR <===---")
    nomes = []
    navegador = None
    try:
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)

        print("Acessando SISREG...")
        navegador.get("https://sisregiii.saude.gov.br")

        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        usuario_field.send_keys(usuario_sisreg)
        senha_field.send_keys(senha_sisreg)

        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))).click()
        time.sleep(5)
        print("Login realizado com sucesso!")
        logging.info("Login SISREG realizado.")

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        time.sleep(10)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Página de Internação acessada.")
        logging.info("Página de Internação acessada.")

        time.sleep(5)

        while True:
            linhas = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas:
                nomes.append(linha.find_element(By.XPATH, './td[2]').text)

            try:
                next_page_button = WebDriverWait(navegador, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']"))
                )
                next_page_button.click()
                time.sleep(5)
            except Exception:
                print("Não há mais páginas.")
                break

        user_dir = os.path.expanduser('~/AutoReg')
        os.makedirs(user_dir, exist_ok=True)
        csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

        if os.path.exists(csv_path):
            df_existente = pd.read_csv(csv_path)
            if 'ENTRADA' in df_existente.columns:
                df_existente = df_existente.drop(columns=['ENTRADA'])
        else:
            df_existente = pd.DataFrame()

        df_entrada = pd.DataFrame({'ENTRADA': nomes})
        max_len = max(len(df_existente), len(df_entrada))
        df_existente = df_existente.reindex(range(max_len)).reset_index(drop=True)
        df_entrada = df_entrada.reindex(range(max_len)).reset_index(drop=True)
        df_final = pd.concat([df_entrada, df_existente], axis=1)

        df_final.to_csv(csv_path, index=False)
        print(f"✅ {len(nomes)} pacientes a internar salvos em '{csv_path}'.")
        logging.info(f"{len(nomes)} pacientes a internar salvos em '{csv_path}'.")

    except TimeoutException:
        print("❌ Timeout ao localizar elementos na página.")
        logging.error("Timeout ao localizar elementos na página.")
    except NoSuchElementException as e:
        print(f"❌ Elemento não encontrado: {e}")
        logging.error(f"Elemento não encontrado: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
        print("Navegador fechado.")
        logging.info("Navegador fechado.")


def compara_duplicados():
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    if not os.path.exists(csv_path):
        print(f"❌ Arquivo '{csv_path}' não encontrado.")
        logging.error(f"Arquivo '{csv_path}' não encontrado.")
        return

    df = pd.read_csv(csv_path)

    if 'ENTRADA' not in df.columns or 'SAIDA' not in df.columns:
        print("❌ Colunas 'ENTRADA' e/ou 'SAIDA' não encontradas no arquivo.")
        logging.error("Colunas 'ENTRADA' e/ou 'SAIDA' não encontradas no arquivo.")
        return

    entradas = set(df['ENTRADA'].dropna().astype(str).str.strip())
    saidas = set(df['SAIDA'].dropna().astype(str).str.strip())
    duplicados = sorted(entradas & saidas)

    df['DUPLICADOS'] = ''
    for idx, nome in enumerate(duplicados):
        if idx < len(df):
            df.at[idx, 'DUPLICADOS'] = nome

    df.to_csv(csv_path, index=False)
    print(f"✅ {len(duplicados)} duplicado(s) identificado(s) em '{csv_path}'.")
    logging.info(f"{len(duplicados)} duplicado(s) identificado(s) em '{csv_path}'.")


def codigo_duplicados():
    print("\n---===> EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS <===---")
    logging.info("---===> EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS <===---")

    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        logging.error(f"Arquivo não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if 'DUPLICADOS' not in df.columns:
        print("❌ Coluna 'DUPLICADOS' não encontrada.")
        logging.error("Coluna 'DUPLICADOS' não encontrada.")
        return

    nomes_duplicados = df['DUPLICADOS'].dropna().astype(str).str.strip().tolist()
    nomes_duplicados = [n for n in nomes_duplicados if n]
    if not nomes_duplicados:
        print("Nenhum nome duplicado para buscar.")
        logging.info("Nenhum nome duplicado para buscar.")
        return

    print(f"📋 Buscando códigos para {len(nomes_duplicados)} duplicado(s).")

    codigos_por_nome = {}
    navegador = None

    try:
        _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)

        print("Acessando SISREG...")
        navegador.get("https://sisregiii.saude.gov.br")

        wait.until(EC.presence_of_element_located((By.NAME, "usuario"))).send_keys(usuario_sisreg)
        wait.until(EC.presence_of_element_located((By.NAME, "senha"))).send_keys(senha_sisreg)

        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))).click()
        time.sleep(5)
        print("Login realizado com sucesso!")
        logging.info("Login SISREG realizado.")

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))).click()
        time.sleep(5)

        try:
            navegador.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
        except Exception:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
            except Exception:
                pass

        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))).click()
        time.sleep(5)

        nomes_restantes = set(n.upper() for n in nomes_duplicados)
        while nomes_restantes:
            linhas = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas:
                try:
                    nome = linha.find_element(By.XPATH, "./td[2]").text.strip().upper()
                    if nome in nomes_restantes:
                        ficha_onclick = linha.get_attribute("onclick")
                        ficha = ficha_onclick.split("'")[1] if ficha_onclick else ""
                        codigos_por_nome[nome] = ficha
                        nomes_restantes.discard(nome)
                        print(f"   ✅ Código encontrado: {nome} -> {ficha}")
                except:
                    continue

            if not nomes_restantes:
                break

            try:
                prox = navegador.find_element(By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']")
                if prox.is_displayed():
                    prox.click()
                    time.sleep(5)
                else:
                    break
            except NoSuchElementException:
                print("Sem mais páginas para pesquisar.")
                break

        if nomes_restantes:
            print(f"⚠️ Não encontrados no SISREG: {nomes_restantes}")
            logging.warning(f"Nomes não encontrados no SISREG: {nomes_restantes}")

        print(f"Códigos extraídos: {len(codigos_por_nome)}")
        logging.info(f"Códigos extraídos para {len(codigos_por_nome)} duplicado(s).")

    except Exception as e:
        print(f"❌ Erro durante extração de códigos: {e}")
        logging.error(f"Erro durante extração de códigos: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
        print("Navegador fechado.")
        logging.info("Navegador fechado.")

    df['CODIGO'] = df['DUPLICADOS'].apply(
        lambda nome: codigos_por_nome.get(str(nome).strip().upper(), '') if pd.notna(nome) and str(nome).strip() else ''
    )
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Arquivo '{csv_path}' atualizado com coluna 'CODIGO'.")
    logging.info(f"Arquivo '{csv_path}' atualizado com coluna 'CODIGO'.")
