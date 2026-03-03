"""
Módulo para tratamento de internações duplicadas no sistema SISREG III.
"""
import os
import time
import traceback
import pandas as pd
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from autoreg.ler_credenciais import ler_credenciais
from autoreg.chrome_options import get_chrome_options
from autoreg.logging import setup_logging

setup_logging()

def trata_duplicados():
    user_dir = os.path.expanduser('~/AutoReg')
    duplicadas_path = os.path.join(user_dir, 'internacoes_duplicadas.csv')

    if not os.path.exists(duplicadas_path):
        print(f"⚠️ Arquivo {duplicadas_path} não encontrado. Pulando tratamento de duplicados.")
        logging.warning(f"Arquivo {duplicadas_path} não encontrado. Pulando tratamento.")
        return

    try:
        df = pd.read_csv(duplicadas_path)
        if df.empty:
            print("✅ Arquivo de duplicados está vazio. Nenhuma ação necessária.")
            logging.info("Arquivo de duplicados vazio.")
            return
    except Exception as e:
        print(f"Erro ao ler arquivo de duplicados: {e}")
        return

    alta_duplicados(duplicadas_path)
    cod_inter_duplicado(duplicadas_path)
    interna_duplicados(duplicadas_path)


def alta_duplicados(duplicadas_path):
    print("\n---===> ALTA DE DUPLICADOS <===---")
    logging.info("---===> ALTA DE DUPLICADOS <===---")

    try:
        df = pd.read_csv(duplicadas_path, encoding='utf-8')
        if 'CODIGO' not in df.columns:
            print("Arquivo não possui coluna 'CODIGO'.")
            return

        pacientes_validos = df[df['CODIGO'].notna() & (df['CODIGO'].astype(str).str.strip() != '')]
        if pacientes_validos.empty:
            print("Nenhum código válido para dar alta.")
            return

        print(f"📋 {len(pacientes_validos)} ficha(s) para alta.")
    except Exception as e:
        print(f"Erro na leitura inicial: {e}")
        return

    if 'resultado_alta' not in df.columns:
        df['resultado_alta'] = ''

    navegador = None
    try:
        chrome_options = get_chrome_options()
        navegador = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(navegador, 20)

        print("Acessando SISREG...")
        logging.info("Acessando SISREG para alta de duplicados...")
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

        for index, paciente in df.iterrows():
            if not (pd.notna(paciente.get('CODIGO')) and str(paciente.get('CODIGO')).strip()):
                continue

            ficha = str(paciente['CODIGO']).split('.')[0]
            print(f"\n🚀 [{index+1}] Processando alta para ficha: {ficha}")
            logging.info(f"Processando alta para ficha: {ficha}")

            try:
                navegador.get("https://sisregiii.saude.gov.br/cgi-bin/config_saida_permanencia")
                time.sleep(2)

                pesquisar_button = WebDriverWait(navegador, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
                )
                pesquisar_button.click()

                navegador.execute_script(f"configFicha('{ficha}')")
                time.sleep(3)

                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                except TimeoutException:
                    print(f"   ⚠️ Botão 'Efetua Saída' não encontrado (ficha inexistente ou já com alta).")
                    df.at[index, 'resultado_alta'] = 'Ficha não encontrada ou já com alta'
                    df.to_csv(duplicadas_path, index=False)
                    continue

                select_motivo = Select(wait.until(EC.presence_of_element_located((By.NAME, "co_motivo"))))
                select_motivo.select_by_value("57")
                print("   Motivo selecionado: ENCERRAMENTO ADMINISTRATIVO (57)")
                time.sleep(1)

                botao_saida = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='bt_acao' and @value='Efetua Saída']")))
                botao_saida.click()

                time.sleep(2)
                try:
                    while True:
                        alert = navegador.switch_to.alert
                        print(f"   Confirmando alerta: {alert.text}")
                        alert.accept()
                        time.sleep(1)
                except:
                    pass

                df.at[index, 'resultado_alta'] = 'Alta efetivada'
                print(f"   ✅ Alta efetivada para {ficha}.")
                logging.info(f"Alta efetivada para ficha {ficha}.")

            except Exception as e:
                print(f"   ❌ Erro ao processar ficha {ficha}: {e}")
                logging.error(f"Erro ao processar ficha {ficha}: {e}")
                df.at[index, 'resultado_alta'] = f'Erro: {str(e)[:50]}'

            df.to_csv(duplicadas_path, index=False)

    except Exception as e:
        print(f"❌ Erro geral na alta de duplicados: {e}")
        logging.error(f"Erro geral na alta de duplicados: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
        print("Alta de duplicados concluída.")


def cod_inter_duplicado(duplicadas_path):
    print("\n---===> EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS <===---")
    logging.info("---===> EXTRAÇÃO DE CÓDIGOS SISREG - DUPLICADOS <===---")

    try:
        df = pd.read_csv(duplicadas_path)
        if 'DUPLICADOS' not in df.columns:
            print("Coluna 'DUPLICADOS' não encontrada.")
            return

        nomes_duplicados = df['DUPLICADOS'].dropna().astype(str).str.strip().tolist()
        if not nomes_duplicados:
            print("Nenhum nome duplicado para buscar.")
            return

        print(f"📋 Buscando códigos para {len(nomes_duplicados)} paciente(s).")
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return

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

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))
        print("Página de Internação acessada.")

        nomes_restantes = set(n.upper() for n in nomes_duplicados)

        while nomes_restantes:
            linhas = navegador.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")
            for linha in linhas:
                try:
                    nome = linha.find_element(By.XPATH, "./td[2]").text.strip().upper()
                    if nome in nomes_restantes:
                        ficha_onclick = linha.get_attribute("onclick")
                        if ficha_onclick:
                            ficha = ficha_onclick.split("'")[1]
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
                    time.sleep(3)
                else:
                    break
            except NoSuchElementException:
                print("Sem mais páginas para pesquisar.")
                break

        if nomes_restantes:
            print(f"⚠️ Não encontrados no SISREG: {nomes_restantes}")
            logging.warning(f"Nomes não encontrados no SISREG: {nomes_restantes}")

        print(f"Códigos extraídos: {len(codigos_por_nome)}")

    except Exception as e:
        print(f"❌ Erro na extração de códigos: {e}")
        logging.error(f"Erro na extração de códigos: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()

    # Atualiza o CSV com os códigos encontrados
    df['CODINTERNA'] = df['DUPLICADOS'].apply(
        lambda x: codigos_por_nome.get(str(x).strip().upper(), '') if pd.notna(x) else ''
    )

    cols = list(df.columns)
    if 'CODINTERNA' in cols:
        cols.remove('CODINTERNA')
    cols.insert(4, 'CODINTERNA')
    df = df[cols]

    df.to_csv(duplicadas_path, index=False)
    print("CSV atualizado com coluna CODINTERNA.")
    logging.info("CSV atualizado com CODINTERNA.")


def interna_duplicados(duplicadas_path):
    print("\n---===> INTERNAÇÃO DE DUPLICADOS <===---")
    logging.info("---===> INTERNAÇÃO DE DUPLICADOS <===---")

    try:
        df = pd.read_csv(duplicadas_path)
        if 'CODINTERNA' not in df.columns:
            print("Coluna CODINTERNA não encontrada.")
            return

        df_validos = df[df['CODINTERNA'].notna() & (df['CODINTERNA'].astype(str).str.strip() != '')]
        if df_validos.empty:
            print("Nenhum código para internar.")
            return

        print(f"📋 {len(df_validos)} ficha(s) para internar.")
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return

    if 'resultado_internacao' not in df.columns:
        df['resultado_internacao'] = ''

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

        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/cgi-bin/config_internar' and text()='internar']"))).click()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'f_main')))

        for index, row in df.iterrows():
            ficha = str(row.get('CODINTERNA', '')).strip()
            if not ficha or ficha == 'nan':
                continue

            print(f"\n🚀 [{index+1}] Internando ficha: {ficha}")
            logging.info(f"Internando ficha: {ficha}")

            try:
                navegador.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))

                navegador.execute_script(f"configFicha('{ficha}')")
                time.sleep(2)

                data_hoje = datetime.now().strftime("%d/%m/%Y")
                data_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")))
                data_field.clear()
                data_field.send_keys(data_hoje)

                select_prof = Select(wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/table[2]/tbody/tr[2]/td[2]/select"))))
                opts = select_prof.options[1:-1]
                if opts:
                    select_prof.select_by_visible_text(random.choice(opts).text)

                wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]"))).click()

                time.sleep(2)
                try:
                    while True:
                        alert = navegador.switch_to.alert
                        print(f"   Confirmando alerta: {alert.text}")
                        alert.accept()
                        time.sleep(1)
                except:
                    pass

                df.at[index, 'resultado_internacao'] = 'Internado'
                print(f"   ✅ Internação processada para {ficha}.")
                logging.info(f"Internação processada para ficha {ficha}.")
                time.sleep(5)

            except Exception as e:
                print(f"   ❌ Erro na ficha {ficha}: {e}")
                logging.error(f"Erro ao internar ficha {ficha}: {e}")
                df.at[index, 'resultado_internacao'] = f'Erro: {str(e)[:50]}'

            df.to_csv(duplicadas_path, index=False)

    except Exception as e:
        print(f"❌ Erro geral na internação de duplicados: {e}")
        logging.error(f"Erro geral na internação de duplicados: {e}")
        traceback.print_exc()
    finally:
        if navegador:
            navegador.quit()
        print("Internação de duplicados concluída.")
