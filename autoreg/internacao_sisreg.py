"""
Lógica compartilhada de internação de uma ficha no SISREG III.

Usada tanto por -ip (interna_pacientes.py) quanto pela etapa final de -td
(trata_duplicados.py), para não duplicar — e deixar divergir — a mesma
automação em dois lugares.
"""
import time
import random
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from autoreg.sessao_sisreg import garantir_sessao_sisreg

URL_CONFIG_INTERNAR = "https://sisregiii.saude.gov.br/cgi-bin/config_internar"


def internar_ficha_sisreg(navegador, ficha, usuario_sisreg, senha_sisreg, controle):
    """
    Interna uma ficha no SISREG III. Assume que já houve login prévio
    (chame sessao_sisreg.login_sisreg() antes do loop de fichas).

    Navega para a página de internação ANTES de checar sessão expirada —
    nessa ordem, para não confundir a mensagem de negócio "Erro de Sistema"
    (deixada na tela por uma ficha anterior que não pôde ser internada) com
    a mensagem de sessão finalizada pelo servidor: ambas contêm o texto
    "erro de sistema", que é justamente a assinatura usada por
    sessao_sisreg.sessao_expirada() para detectar expiração.

    CAPTCHA não é tratado aqui — fica com o chamador, por ficha, como hoje.
    Propaga exceções Selenium não tratadas para o chamador decidir como
    registrar o resultado.

    Retorna 'Internado com sucesso' ou 'Erro: Erro de Sistema detectado no SISREG'.
    """
    wait = WebDriverWait(navegador, 10)

    navegador.get(URL_CONFIG_INTERNAR)
    time.sleep(1)
    while garantir_sessao_sisreg(navegador, URL_CONFIG_INTERNAR, usuario_sisreg, senha_sisreg, controle):
        pass

    navegador.execute_script(f"configFicha('{ficha}')")
    time.sleep(3)

    # Extrai "Data de Solicitação" e interna 2 dias antes; se não achar,
    # usa a data de hoje como fallback — sempre inicializado antes do try,
    # evitando o NameError que ocorria quando a TR não era encontrada.
    data_internacao_str = datetime.now().strftime("%d/%m/%Y")
    try:
        all_trs = navegador.find_elements(By.XPATH, "//tr")
        tr_solicitacao = None
        for tr in all_trs:
            if "Data de Solicitação:" in tr.text:
                tr_solicitacao = tr
                break

        if tr_solicitacao:
            tr_data = tr_solicitacao.find_element(By.XPATH, "following-sibling::tr[1]")
            data_element = tr_data.find_element(By.XPATH, "td[3]")
            data_text = data_element.text.split(" - ")[0].strip()
            data_original = datetime.strptime(data_text, "%d.%m.%Y")
            data_internacao = data_original - timedelta(days=2)
            data_internacao_str = data_internacao.strftime("%d/%m/%Y")
        else:
            print("   ⚠️  'Data de Solicitação' não encontrada — usando data de hoje.")
    except (TimeoutException, NoSuchElementException, ValueError) as e:
        print(f"   ⚠️  Erro na extração da data ({e}) — usando data de hoje.")

    data_field = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@type='text' and contains(@id, 'dp')]")
    ))
    data_field.clear()
    time.sleep(0.3)
    data_field.send_keys(data_internacao_str)

    select_profissional = Select(wait.until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id='main_page']/form/table[2]/tbody/tr[2]/td[2]/select")
    )))
    opcoes = select_profissional.options[1:-1]
    if opcoes:
        select_profissional.select_by_visible_text(random.choice(opcoes).text)

    botao_internar = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id='main_page']/form/center[2]/input[2]")
    ))
    botao_internar.click()

    # Até dois popups de confirmação, cada um tratado separadamente —
    # mais rastreável que um único "while True / except: pass" genérico.
    try:
        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        alert = navegador.switch_to.alert
        print(f"   Popup detectado: {alert.text}")
        alert.accept()
        time.sleep(2)
    except TimeoutException:
        pass

    try:
        WebDriverWait(navegador, 10).until(EC.alert_is_present())
        segundo_alert = navegador.switch_to.alert
        print(f"   Segundo popup detectado: {segundo_alert.text}")
        segundo_alert.accept()
    except TimeoutException:
        pass

    try:
        navegador.find_element(By.XPATH, "//div[contains(text(), 'Erro de Sistema')]")
        return 'Erro: Erro de Sistema detectado no SISREG'
    except NoSuchElementException:
        time.sleep(3)
        return 'Internado com sucesso'
