import os
import re
import logging
import pandas as pd
from autoreg.logging import setup_logging

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


SITUACOES_VALIDAS = ('Feito', 'Cancelada', 'A fazer')
SITUACAO_RE = re.compile(r'\b(' + '|'.join(SITUACOES_VALIDAS) + r')\b')
COL_GAP = 2.5


def _limpa(texto):
    return re.sub(r'\s+', ' ', (texto or '').replace('\n', ' ')).strip()


def _limites_colunas(page):
    """
    Calcula os limites X das colunas a partir da linha de cabeçalho
    ('Solicitado | Tipo Avaliação | Paciente | Setor | Data | Solicitante |
    Situação | Atraso') da página. Retorna None se não achar o cabeçalho.
    """
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    solicitado = [w for w in words if w['text'] == 'Solicitado' and w['x0'] < 30]
    if not solicitado:
        return None
    header_top = solicitado[0]['top']
    header = {w['text']: w['x0'] for w in words
              if w['text'] in ('Paciente', 'Setor', 'Data', 'Solicitante', 'Situação')
              and abs(w['top'] - header_top) <= 3}
    if not all(k in header for k in ('Paciente', 'Setor', 'Data', 'Solicitante', 'Situação')):
        return None
    return {
        'paciente_ini': header['Paciente'] - 1,
        'paciente_fim': header['Setor'] - COL_GAP,
        'setor_ini': header['Setor'] - COL_GAP,
        'setor_fim': header['Data'] - COL_GAP,
        'data_ini': header['Data'] - COL_GAP,
        'data_fim': header['Solicitante'] - COL_GAP,
        'situacao_ini': header['Situação'] - 0.15,
    }


def _extrai_pagina(page, limites, pending):
    """
    Extrai os registros de uma página, agrupando linhas físicas em
    registros lógicos a partir da âncora 'Neurocirurgião' (coluna
    'Solicitado'). `pending` é o registro em aberto vindo da página
    anterior (quando um registro é quebrado entre páginas pelo Jasper) —
    se a página começa com conteúdo antes da primeira âncora, esse
    conteúdo é anexado a `pending` e o registro é fechado.
    Retorna (registros_fechados, novo_pending).
    """
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    if not words:
        return [], pending

    header_words = [w for w in words if w['text'] == 'Solicitado' and w['x0'] < 30]
    header_bottom = (header_words[0]['top'] + 10) if header_words else 0

    footer_tops = [w['top'] for w in words
                   if w['text'] == 'TOTAL' or w['text'].endswith('.jasper')]
    body_bottom = (min(footer_tops) - 4) if footer_tops else page.height

    anchors = sorted({w['top'] for w in words
                       if w['text'] == 'Neurocirurgião' and w['x0'] < 30})

    def extrai_coluna(top_ini, top_fim, x_ini, x_fim):
        crop = page.crop((max(x_ini, 0), top_ini, min(x_fim, page.width), top_fim))
        return _limpa(crop.extract_text() or '')

    registros = []

    band_pre_fim = (anchors[0] - 1) if anchors else body_bottom
    if pending is not None and band_pre_fim > header_bottom:
        pending['paciente'] += ' ' + extrai_coluna(header_bottom, band_pre_fim, limites['paciente_ini'], limites['paciente_fim'])
        pending['setor'] += ' ' + extrai_coluna(header_bottom, band_pre_fim, limites['setor_ini'], limites['setor_fim'])
        situ = extrai_coluna(header_bottom, band_pre_fim, limites['situacao_ini'], page.width)
        m = SITUACAO_RE.search(situ)
        if m and not pending['situacao']:
            pending['situacao'] = m.group(1)
        pending['paciente'] = _limpa(pending['paciente'])
        pending['setor'] = _limpa(pending['setor'])
        registros.append(pending)
        pending = None
    elif pending is not None:
        registros.append(pending)
        pending = None

    for i, top in enumerate(anchors):
        band_top = top - 1
        band_bottom = (anchors[i + 1] - 1) if i + 1 < len(anchors) else body_bottom
        paciente = extrai_coluna(band_top, band_bottom, limites['paciente_ini'], limites['paciente_fim'])
        setor = extrai_coluna(band_top, band_bottom, limites['setor_ini'], limites['setor_fim'])
        data = extrai_coluna(band_top, band_bottom, limites['data_ini'], limites['data_fim'])
        situ_texto = extrai_coluna(band_top, band_bottom, limites['situacao_ini'], page.width)
        m = SITUACAO_RE.search(situ_texto)
        registro = {
            'paciente': paciente,
            'setor': setor,
            'data': data,
            'situacao': m.group(1) if m else '',
        }
        is_last_on_page = (i == len(anchors) - 1)
        if is_last_on_page:
            pending = registro
        else:
            registros.append(registro)

    return registros, pending


def _canoniza_setores(registros):
    """
    Corrige um caractere solto vazando de uma coluna vizinha para o início
    do texto de Setor (artefato de posicionamento de coluna no PDF — ver
    autoreg/especial_prepara.py). Usa votação por maioria: valores de Setor
    que aparecem >=2 vezes são tratados como corretos; um valor que só
    difere de um desses pela ausência do primeiro caractere é corrigido.
    """
    from collections import Counter
    contagem = Counter(r['setor'] for r in registros)
    canonicos = {v for v, c in contagem.items() if c >= 2}
    for r in registros:
        valor = r['setor']
        if valor not in canonicos and len(valor) > 1 and valor[1:] in canonicos:
            r['setor'] = valor[1:]
    return registros


def especial_prepara(pdf_path=None):
    """
    Extrai NOME, SETOR e DATA DA AVALIAÇÃO do relatório G-HOSP em PDF
    'Avaliações Profissionais' (ex.: pr018.jasper, filtrado por
    especialidade), mantendo só linhas com Situação = 'Feito', e grava
    ~/AutoReg/saida_especial.csv para uso pelo -especial-extrai.
    """
    setup_logging()
    logger = logging.getLogger("especial_prepara")

    if pdfplumber is None:
        logger.error("Dependência não instalada: pdfplumber. Instale com pip.")
        print("❌ Dependência não instalada: pdfplumber. Instale com: pip install pdfplumber")
        return

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)

    if pdf_path is None:
        pdf_path = os.path.join(user_dir, 'dado_bruto_especial.pdf')

    if not os.path.isfile(pdf_path):
        print(f"❌ Arquivo PDF não encontrado: {pdf_path}")
        return

    csv_path = os.path.join(user_dir, 'saida_especial.csv')

    print(f"🔎 Processando PDF: {pdf_path}")

    registros = []
    pending = None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            limites = None
            for pagina_num, page in enumerate(pdf.pages, start=1):
                if limites is None:
                    limites = _limites_colunas(page)
                if limites is None:
                    logger.warning(f"Página {pagina_num}: cabeçalho de colunas não encontrado, pulando.")
                    continue
                novos, pending = _extrai_pagina(page, limites, pending)
                registros.extend(novos)
            if pending is not None:
                registros.append(pending)
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {e}")
        print(f"❌ Erro ao processar PDF: {e}")
        return

    if not registros:
        print("❌ Nenhum registro extraído do PDF.")
        logger.warning("Nenhum registro encontrado no PDF")
        return

    registros = _canoniza_setores(registros)

    total_extraidos = len(registros)
    feitos = [r for r in registros if r['situacao'] == 'Feito']
    print(f"📊 Registros extraídos: {total_extraidos} — mantendo {len(feitos)} com Situação = 'Feito'")
    logger.info(f"Registros extraídos: {total_extraidos}, mantidos (Feito): {len(feitos)}")

    df = pd.DataFrame([{
        'nome': r['paciente'],
        'setor': r['setor'],
        'data_avaliacao': r['data'],
        'ra': '',
        'neurocirurgiao': '',
        'data_hora_avaliacao': '',
        'erro': '',
    } for r in feitos])

    df.to_csv(csv_path, index=False)
    print(f"✅ CSV gerado: {csv_path} ({len(df)} registros)")
    logger.info(f"CSV gerado com sucesso: {len(df)} registros")
