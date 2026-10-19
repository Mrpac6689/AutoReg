"""
Lista de RAs (Registros de Atendimento) de um paciente no G-HOSP e a regra de
RA duplicado na mesma data/24h, compartilhadas por:

- `-especial-extrai` (especial_extrai.py): extração da lista de RAs HUERB.
- `-ign` (internados_ghosp_nota.py): marca, na coluna COLUNA_RA_ANTERIOR, o RA
  anterior do mesmo paciente (mesmo dia ou até 24h antes) que já foi solicitado.
  Os lembretes (#paclembretes) são do PACIENTE, não do RA: a mesma lista aparece
  em qualquer RA dele. Por isso é a data de cada lembrete que diz a qual
  internação a solicitação pertence.
- `-std` (solicita_trata_dados.py) e `-spaa` (solicita_pre_aih_auto.py):
  removem as linhas marcadas, mantendo só a solicitação do RA mais antigo.
"""
import re
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

COLUNA_RA_ANTERIOR = 'ra_anterior_solicitado'
# 'sim' só quando -ign leu de fato os lembretes do prontuário. Sem essa
# confirmação o RA não pode ser solicitado: lembrete não lido é indistinguível
# de "paciente sem lembretes" e já causou solicitação duplicada (RA 642852,
# 01/10/2026: timeout do Chrome no -ign → dados vazio → -std não filtrou).
COLUNA_LEMBRETES_LIDOS = 'lembretes_lidos'
JANELA_RA_DUPLICADO = timedelta(hours=24)

# Lembrete de solicitação = um nº de solicitação SISREG (9 dígitos) + uma data.
# Formatos reais: "{data} - {nº} - {tipo}" (gravado por -snt) e anotações à mão
# como "SISREG CM 23/09 123456789" ou "SISREG: 123456789 em 23/09/2026".
NUMERO_SOLICITACAO_RE = re.compile(r'(?<!\d)\d{9}(?!\d)')
DATA_LEMBRETE_RE = re.compile(r'(?<!\d)(\d{2})/(\d{2})(?:/(\d{4}|\d{2}))?(?!\d)')
# Solicitação de leito de UTI não é solicitação de AIH de clínica (CM, CC...)
# e não conta como "já solicitado".
UTI_RE = re.compile(r'\bU\.?T\.?I\b', re.IGNORECASE)
# textContent de #paclembretes, com quebras de linha trocadas por espaço (como
# -ign grava em 'dados'), separa um lembrete do outro por blocos de espaços.
SEPARADOR_LEMBRETES_RE = re.compile(r'\s{3,}|[\r\n]+')


def extrair_ras_huerb(driver, timeout=10):
    """
    Extrai (ra, data_entrada) de cada RAitem da unidade HUERB na página de
    histórico do paciente atualmente carregada (mesma lógica de
    extrai_internados_ghosp_avancado.py).
    """
    ras = []
    try:
        container = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container-procedimentos"))
        )
    except TimeoutException:
        return ras

    for item in container.find_elements(By.CLASS_NAME, "RAitem"):
        try:
            if 'HUERB' not in item.text.upper():
                continue
            ra_numero = item.find_element(By.CLASS_NAME, "ra").get_attribute("value")
            span_data = item.find_element(By.CLASS_NAME, "ml5").text
            data_texto = span_data.replace('\n', ' ').strip()
            m = re.search(r'(\d{2}/\d{2}/\d{4})\s*(\d{2}):\s*(\d{2})', data_texto)
            if not m:
                continue
            data_obj = datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%d/%m/%Y %H:%M")
            ras.append({'ra': ra_numero, 'data_entrada': data_obj})
        except Exception:
            continue
    return ras


def _ra_int(ra):
    try:
        return int(str(ra).strip().split('.')[0])
    except ValueError:
        return None


def ras_anteriores_na_janela(ras, ra_atual):
    """
    Entre os RAs extraídos por extrair_ras_huerb(), retorna os mais antigos que
    o ra_atual com entrada no mesmo dia do calendário OU até 24h antes da
    entrada do ra_atual — ordenados do mais antigo para o mais novo.
    Em empate de data/hora, o RA de número menor é considerado o mais antigo.
    Retorna [] se o ra_atual não estiver na lista.
    """
    numero_atual = _ra_int(ra_atual)
    atual = next((r for r in ras if _ra_int(r['ra']) == numero_atual), None)
    if atual is None:
        return []

    entrada_atual = atual['data_entrada']
    anteriores = []
    for r in ras:
        numero = _ra_int(r['ra'])
        if numero is None or numero == numero_atual:
            continue
        entrada = r['data_entrada']
        mais_antigo = entrada < entrada_atual or (entrada == entrada_atual and numero < numero_atual)
        if not mais_antigo:
            continue
        if entrada.date() == entrada_atual.date() or entrada_atual - entrada <= JANELA_RA_DUPLICADO:
            anteriores.append(r)

    return sorted(anteriores, key=lambda r: (r['data_entrada'], _ra_int(r['ra'])))


def remover_lembretes_uti(texto_lembretes):
    """Remove do texto de lembretes os lembretes que mencionam UTI."""
    if not texto_lembretes or str(texto_lembretes).strip().lower() == 'nan':
        return ''
    return '   '.join(
        lembrete for lembrete in SEPARADOR_LEMBRETES_RE.split(str(texto_lembretes))
        if not UTI_RE.search(lembrete)
    )


def tem_data_proxima(texto_dados, data_internacao, dias=15):
    """
    Critério de "já solicitado" do -std: True se o texto de lembretes contém
    alguma data (dd/mm/aaaa, dd/mm/aa ou dd/mm — esta com o ano da internação)
    a até ±`dias` da data de internação.
    """
    padrao_data_completa = r'\b(\d{2})/(\d{2})/(\d{4}|\d{2})\b'
    padrao_data_curta = r'\b(\d{2})/(\d{2})\b'

    texto_dados = str(texto_dados)
    datas_encontradas = []

    # Busca datas no formato dd/mm/aaaa ou dd/mm/aa
    for match in re.finditer(padrao_data_completa, texto_dados):
        dia, mes, ano = match.groups()
        # Se ano tem 2 dígitos, assume 20xx
        if len(ano) == 2:
            ano = '20' + ano
        try:
            datas_encontradas.append(datetime(int(ano), int(mes), int(dia)))
        except ValueError:
            continue

    # Busca datas no formato dd/mm (sem ano)
    # Remove as datas completas já encontradas para evitar duplicação
    texto_sem_completas = re.sub(padrao_data_completa, '', texto_dados)
    for match in re.finditer(padrao_data_curta, texto_sem_completas):
        dia, mes = match.groups()
        try:
            datas_encontradas.append(datetime(data_internacao.year, int(mes), int(dia)))
        except ValueError:
            continue

    limite_inferior = data_internacao - timedelta(days=dias)
    limite_superior = data_internacao + timedelta(days=dias)
    return any(limite_inferior <= data <= limite_superior for data in datas_encontradas)


def datas_solicitacoes_clinica(texto_lembretes, ano_referencia):
    """
    Datas dos lembretes de solicitação de clínica (não-UTI) do paciente: um
    lembrete conta se tiver nº de solicitação de 9 dígitos E uma data, e não
    mencionar UTI. Lembrete sem data é ignorado (a data é o que liga a
    solicitação a uma internação). dd/mm sem ano usa `ano_referencia`.
    """
    if not texto_lembretes or str(texto_lembretes).strip().lower() == 'nan':
        return []
    datas = []
    for lembrete in SEPARADOR_LEMBRETES_RE.split(str(texto_lembretes)):
        if not NUMERO_SOLICITACAO_RE.search(lembrete) or UTI_RE.search(lembrete):
            continue
        m = DATA_LEMBRETE_RE.search(NUMERO_SOLICITACAO_RE.sub(' ', lembrete))
        if not m:
            continue
        dia, mes, ano = m.groups()
        if ano is None:
            ano = ano_referencia
        elif len(ano) == 2:
            ano = '20' + ano
        try:
            datas.append(datetime(int(ano), int(mes), int(dia)).date())
        except ValueError:
            continue
    return datas


def tem_solicitacao_desde(texto_lembretes, data_entrada, dias=15):
    """
    True se os lembretes do paciente têm solicitação de clínica (não-UTI) com
    data entre o dia da entrada `data_entrada` e `dias` dias depois — a mesma
    janela de 15 dias que -std usa. Sem o limite superior, qualquer solicitação
    recente de um paciente de longa permanência (que quase sempre tem um RA de
    urgência aberto horas antes do RA de internação) bloquearia o RA para sempre.
    """
    inicio = data_entrada.date()
    fim = inicio + timedelta(days=dias)
    return any(
        inicio <= d <= fim
        for d in datas_solicitacoes_clinica(texto_lembretes, data_entrada.year)
    )


def filtrar_ra_anterior_solicitado(df):
    """
    Remove do DataFrame as linhas com COLUNA_RA_ANTERIOR preenchida (RA anterior
    na mesma data/24h já solicitado). Retorna (df_filtrado, quantidade_removida).
    CSV sem a coluna (gerado antes desta regra) passa intacto.
    """
    if COLUNA_RA_ANTERIOR not in df.columns:
        return df, 0
    valores = df[COLUNA_RA_ANTERIOR].astype(str).str.strip()
    mask = df[COLUNA_RA_ANTERIOR].notna() & (valores != '') & (valores.str.lower() != 'nan')
    return df[~mask].reset_index(drop=True), int(mask.sum())


def filtrar_lembretes_nao_lidos(df):
    """
    Remove do DataFrame as linhas cujos lembretes -ign não confirmou ter lido
    (COLUNA_LEMBRETES_LIDOS != 'sim'), inclusive quando a coluna nem existe
    (-ign não rodou ou caiu antes de salvar). Retorna (df_filtrado, quantidade_removida).
    """
    if COLUNA_LEMBRETES_LIDOS not in df.columns:
        return df.iloc[0:0].reset_index(drop=True), len(df)
    mask = df[COLUNA_LEMBRETES_LIDOS].astype(str).str.strip().str.lower() == 'sim'
    return df[mask].reset_index(drop=True), int((~mask).sum())
