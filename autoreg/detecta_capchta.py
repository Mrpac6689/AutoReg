# -*- coding: utf-8 -*-
# autoreg/detecta_capchta.py
"""
Sistema centralizado de deteccao e tratamento de CAPTCHA do SISREG III.
Usado por todos os modulos que interagem com sisregiii.saude.gov.br
"""

import os
import time
import logging
import configparser
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def detecta_captcha(driver, timeout=300):
    """
    Detecta a presenca de CAPTCHA na pagina do SISREG e aguarda resolucao manual.

    Args:
        driver: Instancia do webdriver Selenium
        timeout: Tempo maximo em segundos para aguardar resolucao (padrao: 5 minutos)

    Returns:
        bool: True se nao havia CAPTCHA ou se foi resolvido, False se timeout
    """

    # Texto exato que identifica o CAPTCHA
    CAPTCHA_TEXT = "Devido a grande quantidade de requisições (> 500) realizadas na ultima hora pelo seu operador, será realizado um teste automatizado para diferenciação entre computadores e humanos (CAPTCHA):"

    try:
        # Busca rapida pelo texto de CAPTCHA na pagina
        captcha_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), 'CAPTCHA')]")

        # Se nao encontrou, retorna imediatamente
        if not captcha_elements:
            return True

        # Verifica se e realmente o texto completo do CAPTCHA do SISREG
        captcha_detectado = False
        for element in captcha_elements:
            if "grande quantidade de requisições" in element.text:
                captcha_detectado = True
                break

        if not captcha_detectado:
            return True

        # CAPTCHA detectado - pausar processamento
        logging.warning("CAPTCHA DETECTADO no SISREG!")
        print("\n" + "="*80)
        print("CAPTCHA DETECTADO!")
        print("="*80)

        # Captura URL atual
        url_atual = driver.current_url
        print(f"\nURL da pagina com CAPTCHA: {url_atual}")
        logging.info(f"URL da pagina com CAPTCHA: {url_atual}")

        # Detecta o ambiente (local vs Docker/KASM)
        display_env = os.environ.get('DISPLAY', '')
        eh_kasm = display_env == ':1' or 'KASM' in os.environ.get('HOME', '')

        if eh_kasm:
            # Ambiente Docker/KASM - fornece link do visualizador
            print("\nAmbiente Docker/KASM detectado")

            # Tenta ler URL do KASM do config.ini
            kasm_url = _ler_kasm_url()

            if kasm_url:
                print(f"\nAcesse o visualizador KASM para resolver o CAPTCHA:")
                print(f"   {kasm_url}")
            else:
                print("\nAcesse o visualizador KASM (geralmente https://SEU_SERVIDOR:6901)")
                print("   Configure a URL em config.ini na secao [KASM]")

            logging.info(f"CAPTCHA detectado em ambiente KASM. URL: {kasm_url}")
        else:
            # Ambiente local - navegador deve estar visivel
            print("\nAmbiente local detectado")
            print("O navegador deve estar visivel na sua tela")
            print("Resolva o CAPTCHA manualmente no navegador")
            logging.info("CAPTCHA detectado em ambiente local")

        print(f"\nAguardando resolucao do CAPTCHA...")
        print(f"   Tempo maximo: {timeout} segundos ({timeout//60} minutos)")
        print("="*80 + "\n")

        # Loop de espera com verificacao periodica
        tempo_inicio = time.time()
        contador = 0

        while True:
            # Verifica timeout
            tempo_decorrido = time.time() - tempo_inicio
            if tempo_decorrido > timeout:
                logging.error(f"Timeout: CAPTCHA nao foi resolvido em {timeout} segundos")
                print(f"\nTIMEOUT! CAPTCHA nao resolvido em {timeout//60} minutos.")
                print("   Abortando processamento...\n")
                return False

            # Aguarda antes de verificar novamente
            time.sleep(5)
            contador += 1

            # Mensagem de progresso a cada 30 segundos
            if contador % 6 == 0:
                minutos_restantes = (timeout - tempo_decorrido) // 60
                print(f"Ainda aguardando... ({int(tempo_decorrido//60)}min decorridos, ~{int(minutos_restantes)}min restantes)")

            # Verifica se o CAPTCHA ainda esta presente
            try:
                captcha_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), 'CAPTCHA')]")

                # Se nao encontrou mais o texto, CAPTCHA foi resolvido
                captcha_presente = False
                for element in captcha_elements:
                    if "grande quantidade de requisições" in element.text:
                        captcha_presente = True
                        break

                if not captcha_presente:
                    tempo_total = int(time.time() - tempo_inicio)
                    print(f"\nCAPTCHA RESOLVIDO! (tempo: {tempo_total}s)")
                    print("Retomando processamento...\n")
                    logging.info(f"CAPTCHA resolvido apos {tempo_total} segundos")
                    return True

            except Exception as e:
                # Qualquer erro na verificacao assume que foi resolvido
                logging.warning(f"Erro ao verificar CAPTCHA (assumindo resolvido): {e}")
                return True

    except Exception as e:
        # Em caso de erro na deteccao, loga mas continua processamento
        logging.error(f"Erro na funcao detecta_captcha: {e}")
        print(f"Erro na deteccao de CAPTCHA: {e}")
        print("   Continuando processamento...\n")
        return True


def _ler_kasm_url():
    """
    Le a URL do visualizador KASM do arquivo config.ini

    Returns:
        str: URL do KASM ou None se nao configurado
    """
    try:
        config = configparser.ConfigParser()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, '..', 'config.ini')

        if not os.path.exists(config_path):
            return None

        config.read(config_path)

        if 'KASM' in config and 'viewer_url' in config['KASM']:
            url = config['KASM']['viewer_url'].strip()
            return url if url else None

        return None

    except Exception as e:
        logging.warning(f"Erro ao ler URL do KASM do config.ini: {e}")
        return None
