# -*- coding: utf-8 -*-
# autoreg/justificativa_ghosp.py
"""
Tratamento centralizado da pagina de "Justificativa de Acesso ao Atendimento
de Internacao" do G-HOSP.

Ate versoes anteriores, ao acessar o prontuario de um paciente em alta o G-HOSP
exibia um MODAL sobreposto (div#form_justificativa.ui-dialog-content) e era
possivel ler o HTML por tras sem preencher. Apos a atualizacao (v26.07.x), o
G-HOSP passou a redirecionar para uma PAGINA CHEIA em
    [endereco]:4002/acessos_prontuarios/new?paciente_id=[id]
que precisa ser preenchida e enviada antes de liberar o prontuario.

Os IDs dos campos sao os mesmos do modal antigo:
- select   #acesso_prontuario_tabela_id   (motivo do acesso)
- textarea #acesso_prontuario_justificativa
- submit   input[name=commit] value="Salvar e Acessar Internacao"

Padrao de uso (acesso direto a um prontuario):
    driver.get(url)
    if tratar_justificativa_acesso(driver):
        driver.get(url)   # acesso liberado - re-navega para a URL pretendida
    # ... segue processando a pagina do prontuario
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Valores padrao usados pelo NIR ao justificar o acesso.
MOTIVO_PADRAO = "Enfermagem"
TEXTO_PADRAO = "Acesso NIR Internação"


def em_pagina_justificativa(driver):
    """Retorna True se a pagina atual e a de justificativa de acesso.

    Ancora primeiro na URL (acessos_prontuarios), conforme sugerido, e usa a
    presenca do campo de justificativa como fallback robusto.
    """
    try:
        if "acessos_prontuarios" in (driver.current_url or ""):
            return True
    except Exception:
        pass
    try:
        return bool(driver.find_elements(By.ID, "acesso_prontuario_justificativa"))
    except Exception:
        return False


def tratar_justificativa_acesso(driver, motivo=MOTIVO_PADRAO, texto=TEXTO_PADRAO, timeout=8):
    """Se a pagina de justificativa surgiu, seleciona o motivo, preenche o texto
    e envia o formulario.

    Args:
        driver: webdriver Selenium.
        motivo: texto visivel da opcao no dropdown de motivo (padrao 'Enfermagem').
        texto: justificativa a preencher (padrao 'Acesso NIR Internação').
        timeout: espera maxima pelos elementos do formulario.

    Returns:
        bool: True se tratou a justificativa (o chamador deve re-navegar para a
              URL pretendida), False se a pagina nao era a de justificativa.
    """
    if not em_pagina_justificativa(driver):
        return False

    print("  📝 Página de justificativa de acesso detectada. Preenchendo...")
    logging.info("Justificativa de acesso GHOSP detectada - preenchendo automaticamente.")
    wait = WebDriverWait(driver, timeout)

    dropdown = wait.until(EC.presence_of_element_located((By.ID, "acesso_prontuario_tabela_id")))
    Select(dropdown).select_by_visible_text(motivo)

    campo = driver.find_element(By.ID, "acesso_prontuario_justificativa")
    campo.clear()
    campo.send_keys(texto)

    submit = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @name='commit']"))
    )
    submit.click()
    time.sleep(2)

    logging.info(f"Justificativa de acesso enviada (motivo='{motivo}').")
    print("  ✓ Justificativa enviada. Acesso liberado.")
    return True
