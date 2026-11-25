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
            tipo = re.search(r'RA:\s*(\d+)\s*-', item.text.replace('\xa0', ' '))
            ras.append({'ra': ra_numero, 'data_entrada': data_obj, 'tipo': tipo.group(1) if tipo else ''})
        except Exception:
            continue
    return ras


# "RA: 1 - 600001" no histórico = internação (sempre com leito); 2 = PS/ambulatório.
# Medido em 24/11/2026: 119 de 119 RAs tipo 1 com leito, 161 de 161 tipo 2 sem.
TIPO_INTERNACAO = '1'
# Novo RA de internação até 24 h após a saída do anterior = mesma internação
# (troca de setor). Em 168 pares reais: 2 com 1,6 h e o seguinte só com 48,2 h.
INTERVALO_MESMA_INTERNACAO = timedelta(hours=24)


def cadeia_internacao(ras, ra_inicial, saida_de):
    """
    RAs da mesma internação, a partir do RA que gerou a solicitação, em ordem.
    O último é o que vale para a alta. `saida_de(ra)` → datetime da saída, ou
    None se ainda aberto; só é chamada quando há RA de internação posterior.
    RA inicial de PS segue para a internação que começar até 24 h depois dele.
    Exceção de saida_de é propagada: sem a saída não dá para decidir.
    """
    numero = _ra_int(ra_inicial)
    atual = next((r for r in ras if _ra_int(r['ra']) == numero), None)
    if atual is None:
        return []
    cadeia = [atual]
    for proximo in sorted((r for r in ras if r.get('tipo') == TIPO_INTERNACAO),
                          key=lambda r: (r['data_entrada'], _ra_int(r['ra']) or 0)):
        atual = cadeia[-1]
        if proximo is atual or proximo['data_entrada'] < atual['data_entrada']:
            continue
        saida = saida_de(atual['ra']) if atual.get('tipo') == TIPO_INTERNACAO else atual['data_entrada']
        # Internação ainda aberta: o paciente não saiu; o novo RA a continua
        if saida is None or proximo['data_entrada'] - saida <= INTERVALO_MESMA_INTERNACAO:
            cadeia.append(proximo)
        else:
            break
    return cadeia


def ra_da_internacao(ras, internacao, saida_de):
    """
    Sem RA solicitado conhecido: o RA de internação da época do SISREG (15 dias
    antes a 3 depois). Com mais de uma internação, só o único a até 3 dias da
    data; '' se não houver ou houver dúvida.
    """
    if not internacao:
        return ''
    na_epoca = [r for r in ras if r.get('tipo') == TIPO_INTERNACAO and
                internacao - timedelta(days=15) <= r['data_entrada'] <= internacao + timedelta(days=4)]
    seguintes = {c['ra'] for r in na_epoca for c in cadeia_internacao(ras, r['ra'], saida_de)[1:]}
    inicios = [r for r in na_epoca if r['ra'] not in seguintes]
    if len(inicios) > 1:
        inicios = [r for r in inicios
                   if abs((r['data_entrada'].date() - internacao.date()).days) <= 3]
    return inicios[0]['ra'] if len(inicios) == 1 else ''


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
