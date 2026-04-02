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

# Importa o resolvedor automatico de CAPTCHA
try:
    from .resolvedor_captcha import resolver_captcha_automatico
    RESOLVEDOR_DISPONIVEL = True
except ImportError:
    RESOLVEDOR_DISPONIVEL = False
    logging.warning("Modulo resolvedor_captcha nao disponivel")

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

    logging.debug("=== INICIANDO DETECCAO DE CAPTCHA ===")
    logging.debug(f"URL atual: {driver.current_url}")

    try:
        # Garante verificacao no contexto correto.
        # Se o driver estiver dentro de um frame invalido (frame destruido por navegacao
        # top-level para a pagina de CAPTCHA), page_source lanca excecao.
        # Nesse caso, muda para default_content antes de verificar.
        try:
            page_source = driver.page_source.lower()
        except Exception as e_ctx:
            logging.warning(f"page_source falhou no contexto atual ({e_ctx}) - tentando default_content")
            try:
                driver.switch_to.default_content()
                page_source = driver.page_source.lower()
            except Exception as e2:
                logging.error(f"Impossivel obter page_source mesmo em default_content: {e2}")
                return 'ok'

        logging.debug(f"Verificando CAPTCHA na URL: {driver.current_url}")

        captcha_detectado = False
        metodo_deteccao = ""

        # Padroes de texto que identificam CAPTCHA do SISREG
        # Prefixos curtos cobrem variantes de encoding dos caracteres acentuados
        padroes_sisreg = [
            "grande quantidade de requ",       # cobre "requisições", "requisicoes" e variantes de encoding
            "teste automatizado para difer",   # cobre "diferenciação", "diferenciacao" e variantes
            "computadores e humanos",          # sempre presente na mensagem de CAPTCHA do SISREG
            "500) realizadas na ultima hora",  # trecho ASCII da mensagem do SISREG
            "pelo seu operador, ser",          # outro trecho ASCII unico da mensagem
        ]

        # Metodo 1: Busca por texto especifico do SISREG no page_source
        for padrao in padroes_sisreg:
            if padrao in page_source:
                captcha_detectado = True
                metodo_deteccao = f"texto SISREG: '{padrao}'"
                logging.info(f"CAPTCHA detectado via {metodo_deteccao}")
                break

        # Metodo 2: Detecta widget reCAPTCHA/hCaptcha via data-sitekey no HTML
        # (cobre o caso em que o JS ainda nao criou o iframe mas o widget ja esta no DOM)
        if not captcha_detectado:
            if 'data-sitekey' in page_source and ('g-recaptcha' in page_source or 'h-captcha' in page_source):
                captcha_detectado = True
                metodo_deteccao = "widget reCAPTCHA/hCaptcha (data-sitekey)"
                logging.info(f"CAPTCHA detectado via {metodo_deteccao}")

        # Metodo 3: Busca por iframes de CAPTCHA ja criados pelo JS (reCAPTCHA, hCaptcha)
        if not captcha_detectado:
            try:
                captcha_iframes = driver.find_elements(By.XPATH,
                    "//iframe[contains(@src, 'captcha') or contains(@src, 'recaptcha') or contains(@src, 'hcaptcha')]")
                if captcha_iframes:
                    captcha_detectado = True
                    metodo_deteccao = "iframe reCAPTCHA/hCaptcha"
                    logging.info(f"CAPTCHA detectado via {metodo_deteccao}")
            except Exception as e:
                logging.debug(f"Erro ao buscar iframes de CAPTCHA: {e}")

        if not captcha_detectado:
            logging.debug("=== NENHUM CAPTCHA DETECTADO - retornando 'ok' ===")
            return 'ok'

        # CAPTCHA detectado - pausar processamento
        logging.warning(f"CAPTCHA DETECTADO no SISREG! (Metodo: {metodo_deteccao})")
        print("\n" + "="*80)
        print(f"CAPTCHA DETECTADO! (Metodo: {metodo_deteccao})")
        print("="*80)

        # Captura URL atual
        url_atual = driver.current_url
        print(f"\nURL da pagina com CAPTCHA: {url_atual}")
        logging.info(f"URL da pagina com CAPTCHA: {url_atual}")

        # Verifica se resolucao automatica esta habilitada
        config_2captcha = _ler_config_2captcha()
        if config_2captcha['enabled'] and RESOLVEDOR_DISPONIVEL:
            print("\n[RESOLUCAO AUTOMATICA] 2Captcha habilitado")
            logging.info("Tentando resolucao automatica com 2Captcha...")

            resultado = resolver_captcha_automatico(
                driver=driver,
                api_key=config_2captcha['api_key'],
                timeout=timeout
            )

            if resultado['sucesso']:
                print(f"\n[SUCESSO] CAPTCHA resolvido automaticamente em {resultado['tempo']}s!")
                logging.info(f"CAPTCHA resolvido automaticamente: {resultado['mensagem']}")

                # Verifica se a sessao continua valida
                if _verifica_sessao_invalida(driver):
                    print("Sessao expirou apos resolver CAPTCHA. Sera necessario fazer login novamente.")
                    logging.warning("Sessao expirou apos resolver CAPTCHA - relogin necessario")
                    return 'relogin'

                print("Retomando processamento...\n")
                return 'ok'
            else:
                print(f"\n[FALHA] Nao foi possivel resolver automaticamente: {resultado['mensagem']}")
                logging.warning(f"Falha na resolucao automatica: {resultado['mensagem']}")
                print("Alternando para modo manual...")
                # Continua para resolucao manual abaixo
        elif config_2captcha['enabled'] and not RESOLVEDOR_DISPONIVEL:
            print("\n[AVISO] 2Captcha habilitado mas biblioteca nao instalada")
            print("        Execute: pip install 2captcha-python")
            logging.warning("2Captcha habilitado mas biblioteca nao disponivel")
        else:
            print("\n[MODO MANUAL] Resolucao automatica desabilitada no config.ini")
            logging.info("Resolucao automatica desabilitada - aguardando resolucao manual")

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

            # Verifica se o CAPTCHA ainda esta presente
            try:
                try:
                    page_source_check = driver.page_source.lower()
                except Exception:
                    driver.switch_to.default_content()
                    page_source_check = driver.page_source.lower()
                captcha_presente = False

                # Padroes de texto que identificam CAPTCHA do SISREG (mesma lista da deteccao inicial)
                padroes_verificacao = [
                    "grande quantidade de requ",
                    "teste automatizado para difer",
                    "computadores e humanos",
                    "500) realizadas na ultima hora",
                    "pelo seu operador, ser",
                ]

                # Verifica texto do SISREG
                for padrao in padroes_verificacao:
                    if padrao in page_source_check:
                        captcha_presente = True
                        break

                # Verifica widget reCAPTCHA via data-sitekey
                if not captcha_presente:
                    if 'data-sitekey' in page_source_check and ('g-recaptcha' in page_source_check or 'h-captcha' in page_source_check):
                        captcha_presente = True

                # Verifica iframes de reCAPTCHA/hCaptcha ja criados pelo JS
                if not captcha_presente:
                    try:
                        captcha_iframes = driver.find_elements(By.XPATH,
                            "//iframe[contains(@src, 'captcha') or contains(@src, 'recaptcha') or contains(@src, 'hcaptcha')]")
                        if captcha_iframes:
                            captcha_presente = True
                    except:
                        pass

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


def _ler_config_2captcha():
    """
    Le as configuracoes do 2Captcha do arquivo config.ini

    Returns:
        dict: {'enabled': bool, 'api_key': str}
    """
    try:
        config = configparser.ConfigParser()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, '..', 'config.ini')

        # Valores padrao
        resultado = {
            'enabled': False,
            'api_key': ''
        }

        if not os.path.exists(config_path):
            logging.warning("Arquivo config.ini nao encontrado")
            return resultado

        config.read(config_path)

        if '2CAPTCHA' not in config:
            logging.info("Secao [2CAPTCHA] nao encontrada no config.ini")
            return resultado

        # Le o enabled
        if 'enabled' in config['2CAPTCHA']:
            enabled_str = config['2CAPTCHA']['enabled'].strip().lower()
            resultado['enabled'] = enabled_str in ('true', '1', 'yes', 'sim')

        # Le a API key
        if 'api_key' in config['2CAPTCHA']:
            resultado['api_key'] = config['2CAPTCHA']['api_key'].strip()

        return resultado

    except Exception as e:
        logging.error(f"Erro ao ler configuracoes do 2Captcha: {e}")
        return {'enabled': False, 'api_key': ''}
