# -*- coding: utf-8 -*-
# autoreg/resolvedor_captcha.py
"""
Modulo para resolucao automatica de CAPTCHA usando servico 2Captcha.
Integra-se com o modulo detecta_capchta.py para resolver CAPTCHAs automaticamente.
"""

import os
import time
import logging
import base64
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

try:
    from twocaptcha import TwoCaptcha
    from twocaptcha.exceptions.solver import ValidationException, NetworkException, ApiException, TimeoutException as TwoCaptchaTimeoutException
    TWOCAPTCHA_DISPONIVEL = True
except ImportError:
    TWOCAPTCHA_DISPONIVEL = False
    logging.warning("Biblioteca 2captcha-python nao instalada. Resolucao automatica de CAPTCHA desabilitada.")


def resolver_captcha_automatico(driver, api_key, timeout=300):
    """
    Tenta resolver CAPTCHA automaticamente usando 2Captcha.

    Args:
        driver: Instancia do webdriver Selenium
        api_key: Chave de API do 2Captcha
        timeout: Tempo maximo em segundos para aguardar resolucao

    Returns:
        dict: {'sucesso': bool, 'mensagem': str, 'tempo': int}
    """

    if not TWOCAPTCHA_DISPONIVEL:
        return {
            'sucesso': False,
            'mensagem': 'Biblioteca 2captcha-python nao instalada',
            'tempo': 0
        }

    if not api_key or api_key.strip() == '':
        return {
            'sucesso': False,
            'mensagem': 'API key do 2Captcha nao configurada',
            'tempo': 0
        }

    tempo_inicio = time.time()

    try:
        logging.info("Iniciando resolucao automatica de CAPTCHA com 2Captcha...")
        print("\n[2Captcha] Iniciando resolucao automatica...")

        # Inicializa o solver 2Captcha
        solver = TwoCaptcha(api_key, defaultTimeout=timeout, pollingInterval=5)

        # Verifica saldo da conta
        try:
            saldo = solver.balance()
            logging.info(f"Saldo da conta 2Captcha: ${saldo}")
            print(f"[2Captcha] Saldo da conta: ${saldo}")

            if float(saldo) < 0.001:
                return {
                    'sucesso': False,
                    'mensagem': f'Saldo insuficiente na conta 2Captcha: ${saldo}',
                    'tempo': int(time.time() - tempo_inicio)
                }
        except Exception as e:
            logging.warning(f"Nao foi possivel verificar saldo: {e}")

        # Tenta identificar o tipo de CAPTCHA
        tipo_captcha = _identificar_tipo_captcha(driver)
        logging.info(f"Tipo de CAPTCHA identificado: {tipo_captcha}")
        print(f"[2Captcha] Tipo de CAPTCHA: {tipo_captcha}")

        # Resolve baseado no tipo
        if tipo_captcha == 'recaptcha_v2':
            resultado = _resolver_recaptcha_v2(driver, solver)
        elif tipo_captcha == 'recaptcha_v3':
            resultado = _resolver_recaptcha_v3(driver, solver)
        elif tipo_captcha == 'hcaptcha':
            resultado = _resolver_hcaptcha(driver, solver)
        elif tipo_captcha == 'image':
            resultado = _resolver_captcha_imagem(driver, solver)
        else:
            return {
                'sucesso': False,
                'mensagem': f'Tipo de CAPTCHA nao suportado: {tipo_captcha}',
                'tempo': int(time.time() - tempo_inicio)
            }

        tempo_total = int(time.time() - tempo_inicio)

        if resultado['sucesso']:
            logging.info(f"CAPTCHA resolvido automaticamente em {tempo_total}s")
            print(f"[2Captcha] CAPTCHA resolvido em {tempo_total}s!")
            return {
                'sucesso': True,
                'mensagem': 'CAPTCHA resolvido com sucesso',
                'tempo': tempo_total
            }
        else:
            logging.error(f"Falha ao resolver CAPTCHA: {resultado['mensagem']}")
            return {
                'sucesso': False,
                'mensagem': resultado['mensagem'],
                'tempo': tempo_total
            }

    except ValidationException as e:
        logging.error(f"Erro de validacao 2Captcha: {e}")
        return {
            'sucesso': False,
            'mensagem': f'Parametros invalidos: {e}',
            'tempo': int(time.time() - tempo_inicio)
        }
    except NetworkException as e:
        logging.error(f"Erro de rede 2Captcha: {e}")
        return {
            'sucesso': False,
            'mensagem': f'Erro de rede: {e}',
            'tempo': int(time.time() - tempo_inicio)
        }
    except ApiException as e:
        logging.error(f"Erro na API 2Captcha: {e}")
        return {
            'sucesso': False,
            'mensagem': f'Erro na API: {e}',
            'tempo': int(time.time() - tempo_inicio)
        }
    except TwoCaptchaTimeoutException as e:
        logging.error(f"Timeout 2Captcha: {e}")
        return {
            'sucesso': False,
            'mensagem': f'Timeout: CAPTCHA nao foi resolvido a tempo',
            'tempo': int(time.time() - tempo_inicio)
        }
    except Exception as e:
        logging.error(f"Erro inesperado ao resolver CAPTCHA: {e}")
        return {
            'sucesso': False,
            'mensagem': f'Erro inesperado: {e}',
            'tempo': int(time.time() - tempo_inicio)
        }


def _identificar_tipo_captcha(driver):
    """
    Identifica o tipo de CAPTCHA presente na pagina.

    Returns:
        str: Tipo do CAPTCHA ('recaptcha_v2', 'recaptcha_v3', 'hcaptcha', 'image', 'desconhecido')
    """
    try:
        page_source = driver.page_source

        # Verifica reCAPTCHA v2
        recaptcha_v2_frames = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha') or contains(@title, 'recaptcha')]")
        if recaptcha_v2_frames or 'g-recaptcha' in page_source:
            return 'recaptcha_v2'

        # Verifica reCAPTCHA v3 (mais dificil de detectar)
        if 'grecaptcha' in page_source and 'execute' in page_source:
            return 'recaptcha_v3'

        # Verifica hCaptcha
        hcaptcha_frames = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'hcaptcha')]")
        if hcaptcha_frames or 'h-captcha' in page_source:
            return 'hcaptcha'

        # Verifica CAPTCHA de imagem simples (procura por tag img com "captcha" no src ou id)
        captcha_images = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha') or contains(@id, 'captcha') or contains(@class, 'captcha')]")
        if captcha_images:
            return 'image'

        return 'desconhecido'

    except Exception as e:
        logging.error(f"Erro ao identificar tipo de CAPTCHA: {e}")
        return 'desconhecido'


def _resolver_recaptcha_v2(driver, solver):
    """Resolve reCAPTCHA v2"""
    try:
        # Busca o sitekey
        sitekey = _extrair_recaptcha_sitekey(driver)
        if not sitekey:
            return {'sucesso': False, 'mensagem': 'Nao foi possivel extrair sitekey do reCAPTCHA'}

        url_atual = driver.current_url
        logging.info(f"Resolvendo reCAPTCHA v2 - sitekey: {sitekey}, url: {url_atual}")
        print(f"[2Captcha] Enviando reCAPTCHA v2 para resolucao...")

        # Envia para 2Captcha
        resultado = solver.recaptcha(sitekey=sitekey, url=url_atual)
        token = resultado['code']

        logging.info(f"Token recebido: {token[:50]}...")
        print(f"[2Captcha] Token recebido, aplicando na pagina...")

        # Injeta o token e dispara o callback do reCAPTCHA v2
        driver.execute_script(f"""
            var token = '{token}';
            var field = document.getElementById('g-recaptcha-response');
            if (field) {{
                field.style.display = 'block';
                field.value = token;
                field.innerHTML = token;
            }}
            // Dispara o callback do grecaptcha para habilitar o botao de submit
            try {{
                var clients = window.___grecaptcha_cfg && window.___grecaptcha_cfg.clients;
                if (clients) {{
                    Object.keys(clients).forEach(function(key) {{
                        var c = clients[key];
                        Object.keys(c).forEach(function(k) {{
                            if (c[k] && typeof c[k].callback === 'function') {{
                                try {{ c[k].callback(token); }} catch(e) {{}}
                            }}
                            if (c[k] && typeof c[k] === 'object' && c[k] !== null) {{
                                Object.keys(c[k]).forEach(function(k2) {{
                                    if (c[k][k2] && typeof c[k][k2].callback === 'function') {{
                                        try {{ c[k][k2].callback(token); }} catch(e) {{}}
                                    }}
                                }});
                            }}
                        }});
                    }});
                }}
            }} catch(e) {{ console.log('recaptcha callback: ' + e); }}
        """)

        time.sleep(2)
        _submeter_formulario_captcha(driver)
        time.sleep(2)
        return {'sucesso': True, 'mensagem': 'reCAPTCHA v2 resolvido'}

    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao resolver reCAPTCHA v2: {e}'}


def _resolver_recaptcha_v3(driver, solver):
    """Resolve reCAPTCHA v3"""
    try:
        sitekey = _extrair_recaptcha_sitekey(driver)
        if not sitekey:
            return {'sucesso': False, 'mensagem': 'Nao foi possivel extrair sitekey do reCAPTCHA v3'}

        url_atual = driver.current_url
        logging.info(f"Resolvendo reCAPTCHA v3 - sitekey: {sitekey}")
        print(f"[2Captcha] Enviando reCAPTCHA v3 para resolucao...")

        resultado = solver.recaptcha(sitekey=sitekey, url=url_atual, version='v3')
        token = resultado['code']

        logging.info(f"Token v3 recebido: {token[:50]}...")
        print(f"[2Captcha] Token v3 recebido, aplicando...")

        # Injeta token no campo apropriado
        script = f"""
        if (typeof grecaptcha !== 'undefined') {{
            grecaptcha.execute('{sitekey}', {{action: 'submit'}}).then(function(token) {{
                document.getElementById('g-recaptcha-response').value = '{token}';
            }});
        }}
        """
        driver.execute_script(script)

        _submeter_formulario_captcha(driver)

        time.sleep(2)
        return {'sucesso': True, 'mensagem': 'reCAPTCHA v3 resolvido'}

    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao resolver reCAPTCHA v3: {e}'}


def _resolver_hcaptcha(driver, solver):
    """Resolve hCaptcha"""
    try:
        # Busca sitekey do hCaptcha
        sitekey = _extrair_hcaptcha_sitekey(driver)
        if not sitekey:
            return {'sucesso': False, 'mensagem': 'Nao foi possivel extrair sitekey do hCaptcha'}

        url_atual = driver.current_url
        logging.info(f"Resolvendo hCaptcha - sitekey: {sitekey}")
        print(f"[2Captcha] Enviando hCaptcha para resolucao...")

        # 2Captcha suporta hCaptcha atraves do metodo hcaptcha
        resultado = solver.hcaptcha(sitekey=sitekey, url=url_atual)
        token = resultado['code']

        logging.info(f"Token hCaptcha recebido: {token[:50]}...")
        print(f"[2Captcha] Token recebido, aplicando...")

        # Injeta token
        driver.execute_script(f"""
            var field = document.querySelector('[name=h-captcha-response]');
            if (field) {{
                field.style.display = 'block';
                field.value = '{token}';
                field.innerHTML = '{token}';
            }}
        """)

        _submeter_formulario_captcha(driver)

        time.sleep(2)
        return {'sucesso': True, 'mensagem': 'hCaptcha resolvido'}

    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao resolver hCaptcha: {e}'}


def _resolver_captcha_imagem(driver, solver):
    """Resolve CAPTCHA de imagem simples"""
    try:
        # Busca a imagem do CAPTCHA
        captcha_img = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha') or contains(@id, 'captcha') or contains(@class, 'captcha')]")

        # Captura screenshot da imagem ou pega o src
        img_src = captcha_img.get_attribute('src')

        logging.info(f"Resolvendo CAPTCHA de imagem: {img_src[:100]}...")
        print(f"[2Captcha] Enviando imagem CAPTCHA para resolucao...")

        # Se for base64, usa diretamente, senao faz screenshot
        if img_src.startswith('data:image'):
            # Ja e base64
            resultado = solver.normal(img_src)
        else:
            # Salva screenshot temporario
            temp_path = '/tmp/captcha_temp.png'
            captcha_img.screenshot(temp_path)
            resultado = solver.normal(temp_path)

            # Remove arquivo temporario
            if os.path.exists(temp_path):
                os.remove(temp_path)

        codigo = resultado['code']
        logging.info(f"Codigo CAPTCHA recebido: {codigo}")
        print(f"[2Captcha] Codigo recebido: {codigo}")

        # Tenta encontrar o campo de input do CAPTCHA
        input_captcha = None
        possiveis_inputs = driver.find_elements(By.XPATH, "//input[contains(@name, 'captcha') or contains(@id, 'captcha') or contains(@class, 'captcha')]")

        if possiveis_inputs:
            input_captcha = possiveis_inputs[0]
            input_captcha.clear()
            input_captcha.send_keys(codigo)
            logging.info("Codigo inserido no campo de input")
        else:
            logging.warning("Nao foi possivel encontrar campo de input do CAPTCHA")
            return {'sucesso': False, 'mensagem': 'Campo de input do CAPTCHA nao encontrado'}

        _submeter_formulario_captcha(driver)

        time.sleep(2)
        return {'sucesso': True, 'mensagem': 'CAPTCHA de imagem resolvido'}

    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao resolver CAPTCHA de imagem: {e}'}


def _extrair_recaptcha_sitekey(driver):
    """Extrai o sitekey do reCAPTCHA da pagina"""
    try:
        # Tenta varios metodos para encontrar o sitekey

        # Metodo 1: Atributo data-sitekey
        elements = driver.find_elements(By.XPATH, "//*[@data-sitekey]")
        if elements:
            return elements[0].get_attribute('data-sitekey')

        # Metodo 2: Busca no page_source
        page_source = driver.page_source
        import re
        match = re.search(r'data-sitekey=["\']([^"\']+)["\']', page_source)
        if match:
            return match.group(1)

        # Metodo 3: Busca por sitekey no iframe
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            src = iframe.get_attribute('src')
            if 'recaptcha' in src:
                match = re.search(r'k=([^&]+)', src)
                if match:
                    return match.group(1)

        return None

    except Exception as e:
        logging.error(f"Erro ao extrair sitekey: {e}")
        return None


def _extrair_hcaptcha_sitekey(driver):
    """Extrai o sitekey do hCaptcha da pagina"""
    try:
        # Busca elemento com data-sitekey do hCaptcha
        elements = driver.find_elements(By.XPATH, "//*[@data-sitekey]")
        for elem in elements:
            if 'h-captcha' in elem.get_attribute('class'):
                return elem.get_attribute('data-sitekey')

        # Busca no page_source
        page_source = driver.page_source
        import re
        match = re.search(r'data-sitekey=["\']([^"\']+)["\']', page_source)
        if match:
            return match.group(1)

        return None

    except Exception as e:
        logging.error(f"Erro ao extrair sitekey hCaptcha: {e}")
        return None


def _submeter_formulario_captcha(driver):
    """Tenta submeter o formulario apos resolver o CAPTCHA"""
    try:
        # Tenta chamar validarHumano() do SISREG via JavaScript (especifico do SISREG)
        try:
            driver.execute_script("if (typeof validarHumano === 'function') { validarHumano(); }")
            logging.info("validarHumano() chamado via JavaScript (SISREG)")
            return True
        except Exception:
            pass

        # Tenta encontrar e clicar no botao de submit (ordem: mais especifico primeiro)
        possiveis_botoes = [
            "//input[@name='btnConfirmar']",             # botao Confirmar do SISREG
            "//input[@value='Confirmar']",               # fallback por valor
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'Enviar')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Continuar')]",
            "//button[contains(text(), 'Continue')]",
            "//input[contains(@value, 'onfirm')]",       # variantes de "Confirm"
        ]

        for xpath in possiveis_botoes:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                logging.info(f"Botao de submit clicado: {xpath}")
                return True
            except NoSuchElementException:
                continue

        # Se nao encontrou botao, tenta submeter o form diretamente
        try:
            form = driver.find_element(By.TAG_NAME, 'form')
            driver.execute_script("arguments[0].submit();", form)
            logging.info("Formulario submetido via JavaScript")
            return True
        except Exception:
            pass

        logging.warning("Nao foi possivel submeter o formulario automaticamente")
        return False

    except Exception as e:
        logging.error(f"Erro ao submeter formulario: {e}")
        return False
