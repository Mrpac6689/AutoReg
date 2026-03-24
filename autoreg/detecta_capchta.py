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
        str: 'ok' se nao havia CAPTCHA ou foi resolvido,
             'timeout' se excedeu o tempo limite,
             'relogin' se precisa fazer login novamente apos resolver CAPTCHA
    """

    # Texto exato que identifica o CAPTCHA
    CAPTCHA_TEXT = "Devido a grande quantidade de requisições (> 500) realizadas na ultima hora pelo seu operador, será realizado um teste automatizado para diferenciação entre computadores e humanos (CAPTCHA):"

    try:
        # Busca mais abrangente pelo CAPTCHA - verifica todo o body da pagina
        page_source = driver.page_source

        # Verifica multiplas formas de detectar o CAPTCHA
        captcha_detectado = False

        # Metodo 1: Busca por elementos com texto "CAPTCHA"
        captcha_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'CAPTCHA')]")
        for element in captcha_elements:
            if "grande quantidade de requisições" in element.text or "requisições" in element.text.lower():
                captcha_detectado = True
                logging.info(f"CAPTCHA detectado via elemento XPATH: {element.text[:100]}")
                break

        # Metodo 2: Busca no page_source completo (para casos onde o texto esta fragmentado)
        if not captcha_detectado:
            if "CAPTCHA" in page_source and ("grande quantidade" in page_source or "requisições" in page_source or "requisicoes" in page_source):
                captcha_detectado = True
                logging.info("CAPTCHA detectado via page_source")

        # Metodo 3: Busca por iframe de CAPTCHA comum (reCAPTCHA, hCaptcha, etc)
        if not captcha_detectado:
            captcha_iframes = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'captcha') or contains(@title, 'captcha')]")
            if captcha_iframes:
                captcha_detectado = True
                logging.info("CAPTCHA detectado via iframe")

        if not captcha_detectado:
            return 'ok'

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
                return 'timeout'

            # Aguarda antes de verificar novamente
            time.sleep(5)
            contador += 1

            # Mensagem de progresso a cada 30 segundos
            if contador % 6 == 0:
                minutos_restantes = (timeout - tempo_decorrido) // 60
                print(f"Ainda aguardando... ({int(tempo_decorrido//60)}min decorridos, ~{int(minutos_restantes)}min restantes)")

            # Verifica se o CAPTCHA ainda esta presente (usando mesma logica de deteccao)
            try:
                page_source_check = driver.page_source
                captcha_presente = False

                # Metodo 1: Verifica elementos
                captcha_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'CAPTCHA')]")
                for element in captcha_elements:
                    if "grande quantidade de requisições" in element.text or "requisições" in element.text.lower():
                        captcha_presente = True
                        break

                # Metodo 2: Verifica page_source
                if not captcha_presente:
                    if "CAPTCHA" in page_source_check and ("grande quantidade" in page_source_check or "requisições" in page_source_check or "requisicoes" in page_source_check):
                        captcha_presente = True

                # Metodo 3: Verifica iframes de CAPTCHA
                if not captcha_presente:
                    captcha_iframes = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'captcha') or contains(@title, 'captcha')]")
                    if captcha_iframes:
                        captcha_presente = True

                if not captcha_presente:
                    tempo_total = int(time.time() - tempo_inicio)
                    print(f"\nCAPTCHA RESOLVIDO! (tempo: {tempo_total}s)")
                    logging.info(f"CAPTCHA resolvido apos {tempo_total} segundos")

                    # Verifica se a sessao expirou apos resolver o CAPTCHA
                    if _verifica_sessao_invalida(driver):
                        print("Sessao expirou apos resolver CAPTCHA. Sera necessario fazer login novamente.")
                        logging.warning("Sessao expirou apos resolver CAPTCHA - relogin necessario")
                        return 'relogin'

                    print("Retomando processamento...\n")
                    return 'ok'

            except Exception as e:
                # Qualquer erro na verificacao assume que foi resolvido
                logging.warning(f"Erro ao verificar CAPTCHA (assumindo resolvido): {e}")

                # Ainda verifica se precisa relogin
                if _verifica_sessao_invalida(driver):
                    return 'relogin'
                return 'ok'

    except Exception as e:
        # Em caso de erro na deteccao, loga mas continua processamento
        logging.error(f"Erro na funcao detecta_captcha: {e}")
        print(f"Erro na deteccao de CAPTCHA: {e}")
        print("   Continuando processamento...\n")
        return 'ok'


def _verifica_sessao_invalida(driver):
    """
    Verifica se a sessao do SISREG expirou apos resolver o CAPTCHA.

    Args:
        driver: Instancia do webdriver Selenium

    Returns:
        bool: True se a sessao esta invalida, False caso contrario
    """
    try:
        page_source = driver.page_source

        # Texto exato que indica sessao invalida
        mensagens_sessao_invalida = [
            "A sessão deste operador esta invalida",
            "A sessão deste operador está invalida",
            "Sua sessão foi finalizada pelo servidor",
            "Efetue o logon novamente",
            "Erro de Sistema"
        ]

        for mensagem in mensagens_sessao_invalida:
            if mensagem in page_source:
                logging.info(f"Sessao invalida detectada: '{mensagem}'")
                return True

        return False

    except Exception as e:
        logging.warning(f"Erro ao verificar sessao invalida: {e}")
        return False


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
