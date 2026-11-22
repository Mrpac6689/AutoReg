# -*- coding: utf-8 -*-
# autoreg/sessao_sisreg.py
"""
Gerenciamento centralizado de sessao do SISREG III.

Trata o caso em que o servidor finaliza a sessao no meio de um loop
(mensagem "Erro de Sistema / Este operador efetuou logon em outra estacao de
trabalho / Sua sessao foi finalizada pelo servidor. Efetue o logon novamente").

Pecas:
- login_sisreg          : executa o login (reutilizavel por qualquer conta).
- sessao_expirada       : detecta a pagina de sessao finalizada.
- ControleSessao        : conta re-logins da rotina e aborta ao passar do teto.
- SessaoSisregAbortada  : excecao lancada ao exceder o teto global.
- garantir_sessao_sisreg: se a sessao expirou, refaz login e retoma a URL anterior.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_LOGIN_SISREG = "https://sisregiii.saude.gov.br"

# Trechos (minusculos) que identificam a pagina de sessao finalizada pelo servidor.
# Cobrem variantes com e sem acentuacao para resistir a diferencas de encoding.
_ASSINATURAS_SESSAO_EXPIRADA = [
    "efetuou logon em outra",
    "sua sessão foi finalizada pelo servidor",
    "sua sessao foi finalizada pelo servidor",
    "efetue o logon novamente",
    "erro de sistema",
]


URL_PERFIL_SISREG = "https://sisregiii.saude.gov.br/cgi-bin/config_perfil"
URL_INDEX_SISREG = "https://sisregiii.saude.gov.br/cgi-bin/index"


class SessaoSisregAbortada(Exception):
    """Lancada quando o numero de re-logins excede o teto global da rotina."""


class AcessoSisregNegado(Exception):
    """Login nao deu acesso de fato: senha expirada ou login recusado.

    Senha expirada e silenciosa no SISREG: o login cai no index normalmente e
    SO as outras paginas redirecionam para config_perfil ("Senha expirada,
    informe uma nova senha"). Sem esta checagem a rotina so falhava depois,
    num TimeoutException vazio a cada registro (caso de 21-22/11/2026, operador
    SOL-MICHEL: dois dias sem nenhuma AIH solicitada).
    """

    def __init__(self, rotulo, operador, motivo):
        self.rotulo = rotulo
        self.operador = operador
        self.motivo = motivo
        super().__init__(f"SISREG: {motivo} — operador {operador} ({rotulo})")


def _texto_pagina(driver):
    try:
        return driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return ""


def _registrar_alerta_acesso(erro):
    """Poe o alerta no resumo do ciclo (WhatsApp), uma vez por operador/motivo."""
    try:
        from autoreg import relatorio_execucao
        bloco = (
            f"🔐 *SISREG — {erro.motivo.upper()}*\n"
            f"Operador {erro.operador} ({erro.rotulo}): as etapas que usam este login "
            f"não rodaram neste ciclo. Acertar a senha no SISREG e, se mudar, "
            f"atualizar o config.ini."
        )
        import os
        caminho = os.path.join(relatorio_execucao._user_dir(), 'resumo_execucao.txt')
        if os.path.exists(caminho):
            with open(caminho, encoding='utf-8') as f:
                if bloco.splitlines()[1] in f.read():
                    return
        relatorio_execucao.registrar_resumo(bloco)
    except Exception as e:
        logging.warning(f"Nao foi possivel registrar o alerta de acesso no resumo: {e}")


def verificar_acesso_sisreg(driver, rotulo, usuario=""):
    """Confere, logo depois do login, se o operador tem acesso de fato.

    1. Ainda na tela de login (campo 'usuario' presente) -> login recusado.
    2. config_perfil com "senha expirada" -> senha expirada.
    Se estiver tudo certo, volta ao index (o estado normal pos-login).
    Levanta AcessoSisregNegado e registra o alerta no resumo do ciclo.
    """
    # A tela de login tambem tem o rotulo "Operador:" — o que distingue e o
    # campo 'usuario'. Pagina lenta: da ate ~10 s para ele sumir.
    for _ in range(10):
        if not driver.find_elements(By.NAME, "usuario"):
            break
        time.sleep(1)
    texto_index = _texto_pagina(driver)
    na_tela_login = bool(driver.find_elements(By.NAME, "usuario"))
    operador = usuario or "?"
    if not na_tela_login and "Operador:" in texto_index:
        operador = texto_index.split("Operador:", 1)[1].split()[0]

    erro = None
    if na_tela_login:
        motivo = "login recusado"
        if "incorreto" in texto_index.lower():
            motivo = "login recusado (login ou senha incorretos)"
        erro = AcessoSisregNegado(rotulo, operador, motivo)
    else:
        driver.get(URL_PERFIL_SISREG)
        time.sleep(2)
        if "senha expirada" in _texto_pagina(driver).lower():
            erro = AcessoSisregNegado(rotulo, operador, "senha expirada")

    if erro:
        logging.critical(str(erro))
        print(f"\n🔐 {erro}\n")
        _registrar_alerta_acesso(erro)
        raise erro

    driver.get(URL_INDEX_SISREG)
    time.sleep(1)
    logging.info(f"Acesso SISREG conferido: operador {operador} ({rotulo}), senha válida")


def pagina_senha_expirada(driver):
    """True se o navegador foi redirecionado para a troca de senha (meio da rotina)."""
    try:
        if "config_perfil" not in driver.current_url:
            return False
    except Exception:
        return False
    return "senha expirada" in _texto_pagina(driver).lower()


class ControleSessao:
    """Conta re-logins de uma rotina inteira e aborta ao passar do teto global."""

    def __init__(self, teto=5):
        self.teto = teto
        self.relogins = 0

    def registrar_relogin(self):
        self.relogins += 1
        logging.warning(f"Re-login SISREG #{self.relogins} (teto global={self.teto})")
        if self.relogins > self.teto:
            raise SessaoSisregAbortada(
                f"Numero de re-logins ({self.relogins}) excedeu o teto ({self.teto}). "
                "Provavel conflito persistente de sessao - abortando rotina."
            )


def sessao_expirada(driver):
    """Retorna True se a pagina atual e a de sessao finalizada pelo servidor."""
    try:
        page = driver.page_source.lower()
    except Exception as e:
        logging.warning(f"Nao foi possivel ler page_source ao checar sessao: {e}")
        return False
    return any(assinatura in page for assinatura in _ASSINATURAS_SESSAO_EXPIRADA)


def login_sisreg(driver, usuario, senha, timeout=20, espera_pre_click=10, espera_pos_login=5,
                 rotulo="exec"):
    """Executa o login no SISREG III com as credenciais informadas.

    Navega para a pagina de login antes de preencher, entao serve tanto para o
    login inicial quanto para o re-login apos sessao expirada. Ao final confere
    o acesso (verificar_acesso_sisreg): senha expirada ou login recusado
    levantam AcessoSisregNegado. rotulo = conta do config.ini (exec / sol).
    """
    wait = WebDriverWait(driver, timeout)
    driver.get(URL_LOGIN_SISREG)

    usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
    senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
    usuario_field.clear()
    usuario_field.send_keys(usuario)
    senha_field.clear()
    senha_field.send_keys(senha)

    # Espera antes do clique reproduz o comportamento original dos modulos
    # (o SISREG rejeita logins disparados cedo demais apos o carregamento).
    time.sleep(espera_pre_click)

    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
    )
    login_button.click()
    time.sleep(espera_pos_login)
    logging.info("Login SISREG realizado.")
    verificar_acesso_sisreg(driver, rotulo, usuario)


def garantir_sessao_sisreg(driver, url_retomar, usuario, senha, controle):
    """Se a sessao expirou, refaz o login e re-navega para url_retomar.

    Args:
        driver: webdriver Selenium.
        url_retomar: URL para onde voltar apos o re-login ("pagina anterior ao erro").
        usuario, senha: credenciais da rotina em execucao.
        controle: instancia de ControleSessao (contagem global de re-logins).

    Returns:
        bool: True se precisou re-logar (o chamador deve repetir a operacao/item),
              False se a sessao ja estava valida.

    Raises:
        SessaoSisregAbortada: se o teto global de re-logins foi excedido.
    """
    if not sessao_expirada(driver):
        return False

    logging.warning("Sessao SISREG expirada detectada - refazendo login.")
    print("\n⚠️  Sessao SISREG finalizada pelo servidor. Refazendo login...")
    controle.registrar_relogin()
    login_sisreg(driver, usuario, senha)

    if url_retomar:
        driver.get(url_retomar)
        time.sleep(2)

    print("✅ Login refeito. Retomando da pagina anterior ao erro.\n")
    return True
