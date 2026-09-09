import os
import re
import logging
import pandas as pd
from datetime import datetime
from autoreg.logging import setup_logging

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

RA_RE = re.compile(r'^\d{6}$')
DT_RE = re.compile(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})')
COL_GAP = 2.5
NOME_X_MIN = 78
ACIMA_TOP_MIN = 9
ACIMA_TOP_MAX = 2


def _limpa(texto):
    return re.sub(r'\s+', ' ', (texto or '').replace('\n', ' ')).strip()


def _limites_pagina(page):
    """Localiza no cabeçalho da página ('Nº Int. TpNome Dias Internamento/Alta
    Convênio Médico Mot. CID') os limites X usados para achar a coluna de RA
    e o fim da coluna Nome. Retorna None se a página não tiver esse cabeçalho.
    """
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    tpnome_cands = [w for w in words if w['text'] == 'TpNome']
    if not tpnome_cands:
        return None
    tpnome = tpnome_cands[0]
    header_top = tpnome['top']
    # 'Dias' também aparece no rodapé de resumo ('Dias: 908 Altas: ...'); só
    # aceita o token que está na mesma linha física do cabeçalho de colunas.
    dias_cands = [w for w in words if w['text'] == 'Dias' and abs(w['top'] - header_top) <= 3]
    if not dias_cands:
        return None
    return {
        'ra_x_max': tpnome['x0'],
        'nome_x_max': dias_cands[0]['x0'] - COL_GAP,
    }


def _normaliza_data_hora(data_str, hora_str):
    """Converte 'dd/mm/aa' + 'hh:mm' para 'dd/mm/AAAA HH:MM' (assume 20xx)."""
    try:
        dt = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%y %H:%M")
        return dt.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return f"{data_str} {hora_str}"


def _extrai_pagina(page, limites, logger):
    """Extrai (ra, nome, data_hora_internamento, data_hora_alta) de cada
    registro da página. Âncora de registro = token que casa ^\\d{6}$ com
    x0 < limites['ra_x_max']. As 2 datas de 'Internamento/Alta' são sempre
    encontradas na própria linha da âncora. O nome do paciente normalmente
    está na própria linha da âncora; quando é longo demais, vaza inteiro
    para a linha imediatamente acima.
    """
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    if not words:
        return []

    legenda_tops = [w['top'] for w in words if w['text'] == 'Legenda']
    total_tops = [w['top'] for w in words if w['text'] == 'Total']
    marcadores = legenda_tops + total_tops
    body_bottom = (min(marcadores) - 2) if marcadores else page.height

    anchors = sorted({
        w['top'] for w in words
        if RA_RE.match(w['text']) and w['x0'] < limites['ra_x_max'] and w['top'] < body_bottom
    })

    registros = []
    for top in anchors:
        linha = sorted([w for w in words if abs(w['top'] - top) <= 2], key=lambda w: w['x0'])
        ra = next(w['text'] for w in linha if RA_RE.match(w['text']) and w['x0'] < limites['ra_x_max'])
        texto_linha = ' '.join(w['text'] for w in linha)
        datas = DT_RE.findall(texto_linha)
        if len(datas) != 2:
            logger.warning(f"RA {ra}: esperava 2 datas na linha, encontrei {len(datas)}. Registro ignorado.")
            continue
        (data_int, hora_int), (data_alta, hora_alta) = datas

        nome_tokens = [w['text'] for w in linha if NOME_X_MIN <= w['x0'] <= limites['nome_x_max']]
        nome = _limpa(' '.join(nome_tokens))
        if not nome:
            acima = sorted(
                [w for w in words
                 if (top - ACIMA_TOP_MIN) <= w['top'] < (top - ACIMA_TOP_MAX)
                 and NOME_X_MIN <= w['x0'] <= limites['nome_x_max']],
                key=lambda w: w['x0'],
            )
            nome = _limpa(' '.join(w['text'] for w in acima))

        registros.append({
            'ra': ra,
            'nome': nome,
            'data_hora_internamento': _normaliza_data_hora(data_int, hora_int),
            'data_hora_alta': _normaliza_data_hora(data_alta, hora_alta),
        })
    return registros


def especial_med_prepara(pdf_path=None):
    """Extrai RA, NOME, DATA/HORA DE INTERNAMENTO e DATA/HORA DE ALTA do
    relatório G-HOSP em PDF 'Altas por período' (rc008), a partir das
    colunas 'Nº Int.' e 'Internamento/Alta', e grava
    ~/AutoReg/especial-med-resultado.csv para uso pelo -especial-med-extrai.
    """
    setup_logging()
    logger = logging.getLogger("especial_med_prepara")

    if pdfplumber is None:
        print("❌ Dependência não instalada: pdfplumber. Instale com: pip install pdfplumber")
        return

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)

    if pdf_path is None:
        pdf_path = os.path.join(user_dir, 'dado_bruto_especial_med.pdf')

    if not os.path.isfile(pdf_path):
        print(f"❌ Arquivo PDF não encontrado: {pdf_path}")
        return

    csv_path = os.path.join(user_dir, 'especial-med-resultado.csv')

    print(f"🔎 Processando PDF: {pdf_path}")

    registros = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pagina_num, page in enumerate(pdf.pages, start=1):
                limites = _limites_pagina(page)
                if limites is None:
                    logger.warning(f"Página {pagina_num}: cabeçalho de colunas não encontrado, pulando.")
                    continue
                registros.extend(_extrai_pagina(page, limites, logger))
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {e}")
        print(f"❌ Erro ao processar PDF: {e}")
        return

    if not registros:
        print("❌ Nenhum registro extraído do PDF.")
        logger.warning("Nenhum registro encontrado no PDF")
        return

    print(f"📊 Registros extraídos: {len(registros)}")
    logger.info(f"Registros extraídos: {len(registros)}")

    df = pd.DataFrame([{
        'ra': r['ra'],
        'nome': r['nome'],
        'data_hora_internamento': r['data_hora_internamento'],
        'data_hora_alta': r['data_hora_alta'],
        'medicoalta': '',
        'erro': '',
    } for r in registros])

    df.to_csv(csv_path, index=False)
    print(f"✅ CSV gerado: {csv_path} ({len(df)} registros)")
    logger.info(f"CSV gerado com sucesso: {len(df)} registros")
