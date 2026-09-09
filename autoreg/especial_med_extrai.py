import os
import time
import logging
import traceback

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.chrome_options import get_chrome_options
from autoreg.justificativa_ghosp import tratar_justificativa_acesso


def especial_med_extrai():
    """Para cada linha de ~/AutoReg/especial-med-resultado.csv (gerada por
    -especial-med-prepara), navega diretamente para
    [caminho_ghosp]:4002/pr/altas?intern_id=[ra] (RA já conhecido — não é
    necessário buscar por nome), trata a página de Justificativa de Acesso
    se aparecer, localiza a seção de resumo de alta
    (div.section-content.cor-sec03) e extrai o nome do médico que deu alta
    (label[for='medico'] + div irmã), gravando o texto completo (nome + CRM)
    na coluna 'medicoalta'. Erros por linha são gravados na coluna 'erro'
    sem interromper o processamento das demais.
    """
    setup_logging()
    print("\n---===> EXTRAÇÃO DE MÉDICO DE ALTA (ESPECIAL MED) <===---")

    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'especial-med-resultado.csv')
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo {csv_path} não encontrado. Rode -especial-med-prepara primeiro.")
        return

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    for col in ('ra', 'nome', 'data_hora_internamento', 'data_hora_alta', 'medicoalta', 'erro'):
        if col not in df.columns:
            df[col] = ''

    driver = None
    try:
        usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        driver.get(caminho_ghosp + ':4002/users/sign_in')
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

        total = len(df)
        print(f"\nIniciando processamento de {total} registros...")

        for index, row in df.iterrows():
            ra = str(row['ra']).strip()
            nome = str(row['nome']).strip()
            print(f"\n[{index + 1}/{total}] Processando RA {ra} ({nome})")

            df.at[index, 'erro'] = ""

            if not ra or ra == 'nan':
                df.at[index, 'erro'] = "RA vazio/ausente na linha"
                df.to_csv(csv_path, index=False)
                continue

            try:
                url_alta = f"{caminho_ghosp}:4002/pr/altas?intern_id={ra}"
                driver.get(url_alta)
                time.sleep(1.5)

                if tratar_justificativa_acesso(driver):
                    driver.get(url_alta)
                    time.sleep(1.5)

                try:
                    resumo_content = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-content.cor-sec03"))
                    )
                    texto_resumo = resumo_content.text.strip()
                except Exception:
                    df.at[index, 'erro'] = "Seção de resumo de alta não encontrada (RA pode seguir internado)"
                    df.to_csv(csv_path, index=False)
                    continue

                if not texto_resumo or len(texto_resumo) < 5:
                    df.at[index, 'erro'] = "Resumo de alta vazio (RA pode seguir internado)"
                    df.to_csv(csv_path, index=False)
                    continue

                try:
                    medico_el = driver.find_element(
                        By.XPATH, "//label[@for='medico']/following-sibling::div"
                    )
                    medico_texto = medico_el.text.strip()
                    if medico_texto:
                        df.at[index, 'medicoalta'] = medico_texto
                        print(f"  ✓ Médico de alta: {medico_texto}")
                    else:
                        df.at[index, 'erro'] = "Campo médico encontrado, mas vazio"
                except Exception:
                    df.at[index, 'erro'] = "Campo médico não localizado (label[for='medico'])"

            except Exception as e:
                print(f"  ❌ Erro ao processar RA {ra}: {str(e)}")
                df.at[index, 'erro'] = f"Erro técnico: {str(e)}"

            df.to_csv(csv_path, index=False)

        df.to_csv(csv_path, index=False)
        print(f"\nProcessamento concluído. CSV atualizado em: {csv_path}")

    except Exception as e:
        print(f"Erro ao extrair médico de alta (especial med): {str(e)}")
        logging.error(f"Erro ao extrair médico de alta (especial med): {str(e)}")
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
