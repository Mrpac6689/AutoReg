import os
import sys
import csv
import logging
from autoreg.logging import setup_logging

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    convert_from_path = None


def pdf2csv(pdf_file):
    """
    Converte um arquivo PDF em CSV usando OCR.
    O arquivo CSV será salvo em ~/AutoReg/lista_same.csv com colunas: num, nome, cod, data.
    Recebe o caminho do PDF como argumento.
    """
    setup_logging()
    logger = logging.getLogger("pdf2csv")

    if pytesseract is None or convert_from_path is None:
        logger.error("Dependências não instaladas: pytesseract, pdf2image. Instale com pip.")
        print("❌ Dependências não instaladas: pytesseract, pdf2image. Instale com pip.")
        return

    if not pdf_file:
        print("❌ Informe o caminho do PDF: python autoreg.py -p2c arquivo.pdf")
        return

    if not os.path.isfile(pdf_file):
        print(f"❌ Arquivo PDF não encontrado: {pdf_file}")
        return

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'lista_same.csv')

    print(f"🔎 Processando PDF: {pdf_file}")
    try:
        images = convert_from_path(pdf_file)
    except Exception as e:
        logger.error(f"Erro ao converter PDF em imagens: {e}")
        print(f"❌ Erro ao converter PDF: {e}")
        return

    import re
    dados = []
    for i, img in enumerate(images):
        texto = pytesseract.image_to_string(img, lang='por')
        for linha in texto.splitlines():
            partes = linha.strip().split()
            if len(partes) >= 3:
                # nome: apenas letras e espaços
                nome_raw = ' '.join(partes[:-2])
                nome = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', nome_raw).strip()
                # cod: apenas números
                cod_raw = partes[-2]
                cod = re.sub(r'\D', '', cod_raw)
                # data: apenas data (formato dd/mm/aaaa ou similar)
                data_raw = partes[-1]
                match_data = re.search(r'(\d{2}/\d{2}/\d{4})', data_raw)
                data = match_data.group(1) if match_data else ''
                if nome and cod and data:
                    dados.append([nome, cod, data])

    if not dados:
        print("❌ Nenhum dado extraído do PDF.")
        return

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['nome', 'cod', 'data'])
        writer.writerows(dados)

    print(f"✅ CSV gerado: {csv_path} ({len(dados)} registros)")
    