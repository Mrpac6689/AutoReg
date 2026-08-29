# autoreg/extrai_codigos_internacao.py
import os
import pandas as pd
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from autoreg.logging import setup_logging
from autoreg.detecta_capchta import detecta_captcha
from autoreg.sessao_sisreg import login_sisreg, ControleSessao, SessaoSisregAbortada
from autoreg.internacao_sisreg import internar_ficha_sisreg
import logging

setup_logging()
def interna_pacientes():
    navegador = None
    user_dir = os.path.expanduser('~/AutoReg')
    csv_path = os.path.join(user_dir, 'codigos_internacao.csv')

    print("INICIANDO PROCESSO DE INTERNAÇÃO\n")
    df = pd.read_csv(csv_path)
    if 'resultado' not in df.columns:
        df['resultado'] = ''
    df.to_csv(csv_path, index=False)

    # Configura o navegador Chrome com opções personalizadas
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)

    _, _, _, usuario_sisreg, senha_sisreg = ler_credenciais()

    print("Realizando login no SISREG...")
    logging.info("Realizando login no SISREG...")
    login_sisreg(navegador, usuario_sisreg, senha_sisreg)
    print("Login realizado com sucesso!")
    logging.info("Login realizado com sucesso!")

    # Controle global de re-logins desta rotina (aborta ao passar do teto)
    controle = ControleSessao()

    try:
        for idx, linha in df.iterrows():
            # Verifica se há CAPTCHA antes de cada internação
            resultado_captcha = detecta_captcha(navegador)
            if resultado_captcha != 'ok':
                print(f"CAPTCHA não resolvido ({resultado_captcha}). Abortando internações.")
                logging.error(f"Internações abortadas por CAPTCHA não resolvido: {resultado_captcha}")
                break

            ficha = linha['Número da Ficha']  # Captura o número da ficha
            print(f"\n🚀 Internando ficha: {ficha}")
            try:
                resultado = internar_ficha_sisreg(navegador, ficha, usuario_sisreg, senha_sisreg, controle)
                df.at[idx, 'resultado'] = resultado
                print(f"   {resultado}")
                logging.info(f"Ficha {ficha}: {resultado}")
            except Exception as e:
                print(f"Erro ao processar a ficha {ficha}: {e}\n")
                logging.error(f"Erro ao processar a ficha {ficha}: {e}")
                df.at[idx, 'resultado'] = f'Erro: {e}'

            df.to_csv(csv_path, index=False)
    except SessaoSisregAbortada as e:
        print(f"⛔ Rotina de internação abortada: {e}")
        logging.error(f"Rotina de internação abortada por conflito de sessao: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}\n")
        logging.error(f"Erro inesperado: {e}")
    finally:
        if navegador:
            navegador.quit()
        print("Processo de internação concluído.\n")
        logging.info("Processo de internação concluído.")
        print("Todos os códigos de internação foram processados. Verifique o arquivo 'codigos_internacao.csv' no diretório ~/AutoReg.\n")
        logging.info("Todos os códigos de internação foram processados. Verifique o arquivo 'codigos_internacao.csv' no diretório ~/AutoReg.")
