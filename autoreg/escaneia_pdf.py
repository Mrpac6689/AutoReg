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


def pdf2csv(pdf_file=None):
    """
    Extrai dados do PDF 'dado_bruto.pdf' e gera 'especial.csv'.
    Extrai as colunas 'Nro. Antend.' e 'Nome' da tabela,
    salvando-as como 'ra' e 'nome' no CSV de saída.
    """
    setup_logging()
    logger = logging.getLogger("pdf2csv")

    if pytesseract is None or convert_from_path is None:
        logger.error("Dependências não instaladas: pytesseract, pdf2image. Instale com pip.")
        print("❌ Dependências não instaladas: pytesseract, pdf2image. Instale com pip.")
        return

    # Verificar se o Tesseract está instalado no sistema
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        print("\n❌ Tesseract OCR não está instalado no sistema!")
        print("\n📦 Para instalar no Linux/Ubuntu:")
        print("   sudo apt-get update")
        print("   sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print("\n📦 Para instalar no Fedora/RHEL:")
        print("   sudo dnf install tesseract tesseract-langpack-por")
        print("\n📦 Para instalar no Arch:")
        print("   sudo pacman -S tesseract tesseract-data-por")
        print("\n📦 Para instalar no macOS:")
        print("   brew install tesseract tesseract-lang")
        print("\n⚠️  Após instalar, reinicie o terminal.\n")
        logger.error(f"Tesseract não encontrado: {e}")
        return

    # Definir caminhos fixos
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    
    if pdf_file is None:
        pdf_file = os.path.join(user_dir, 'dado_bruto.pdf')
    
    if not os.path.isfile(pdf_file):
        print(f"❌ Arquivo PDF não encontrado: {pdf_file}")
        return

    csv_path = os.path.join(user_dir, 'especial.csv')

    print(f"🔎 Processando PDF: {pdf_file}")
    
    # Primeiro, contar quantas páginas o PDF tem
    try:
        from pdf2image import pdfinfo_from_path
        info = pdfinfo_from_path(pdf_file)
        total_pages = info['Pages']
        print(f"📊 Total de páginas: {total_pages}")
    except Exception as e:
        logger.warning(f"Não foi possível contar páginas, processando todas de uma vez: {e}")
        total_pages = None
    
    import re
    dados = []
    
    # Processar em lotes de 10 páginas
    PAGINAS_POR_LOTE = 10
    
    if total_pages:
        num_lotes = (total_pages + PAGINAS_POR_LOTE - 1) // PAGINAS_POR_LOTE
        print(f"📦 Dividindo em {num_lotes} lotes de até {PAGINAS_POR_LOTE} páginas")
        
        for lote in range(num_lotes):
            first_page = lote * PAGINAS_POR_LOTE + 1
            last_page = min((lote + 1) * PAGINAS_POR_LOTE, total_pages)
            
            print(f"\n🔄 Processando lote {lote + 1}/{num_lotes} (páginas {first_page}-{last_page})...")
            
            try:
                images = convert_from_path(
                    pdf_file, 
                    dpi=300,
                    first_page=first_page,
                    last_page=last_page
                )
            except Exception as e:
                logger.error(f"Erro ao converter lote {lote + 1}: {e}")
                print(f"❌ Erro ao processar lote {lote + 1}: {e}")
                continue
            
            for i, img in enumerate(images):
                pagina_atual = first_page + i
                print(f"📄 Processando página {pagina_atual}/{total_pages}...")
                
                # Configurar OCR para melhor qualidade
                custom_config = r'--oem 3 --psm 6'
                texto = pytesseract.image_to_string(img, lang='por', config=custom_config)
                
                linhas = texto.splitlines()
                
                for linha in linhas:
                    linha = linha.strip()
                    if not linha:
                        continue
                    
                    # Padrão: RA (5-6 dígitos) + Nome (letras e espaços) + Data de Entrada (dd/mm/yy)
                    # Exemplo: 320016 Icaro Luan Nascimento Da Silva 01/10/24 00:50
                    match = re.match(r'^(\d{5,6})\s+([A-Za-zÀ-ÿ\s]+?)\s+(\d{2}/\d{2}/\d{2,4})', linha)
                    
                    if match:
                        ra = match.group(1).strip()
                        nome = match.group(2).strip()
                        entrada = match.group(3).strip()
                        
                        # Limpar o nome - remover espaços múltiplos
                        nome = re.sub(r'\s+', ' ', nome)
                        
                        if ra and nome and len(nome) > 3 and entrada:  # Validação básica
                            dados.append([ra, nome, entrada])
                            logger.info(f"Extraído: RA={ra}, Nome={nome}, Entrada={entrada}")
            
            # Liberar memória do lote
            del images
            print(f"✅ Lote {lote + 1} processado. Total acumulado: {len(dados)} registros")
    
    else:
        # Fallback: processar tudo de uma vez se não conseguir contar páginas
        try:
            images = convert_from_path(pdf_file, dpi=300)
        except Exception as e:
            logger.error(f"Erro ao converter PDF em imagens: {e}")
            print(f"❌ Erro ao converter PDF: {e}")
            return
        
        for i, img in enumerate(images):
            print(f"📄 Processando página {i+1}...")
            custom_config = r'--oem 3 --psm 6'
            texto = pytesseract.image_to_string(img, lang='por', config=custom_config)
            
            linhas = texto.splitlines()
            
            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                
                # Padrão: RA (5-6 dígitos) + Nome (letras e espaços) + Data de Entrada (dd/mm/yy)
                match = re.match(r'^(\d{5,6})\s+([A-Za-zÀ-ÿ\s]+?)\s+(\d{2}/\d{2}/\d{2,4})', linha)
                
                if match:
                    ra = match.group(1).strip()
                    nome = match.group(2).strip()
                    entrada = match.group(3).strip()
                    
                    # Limpar o nome - remover espaços múltiplos
                    nome = re.sub(r'\s+', ' ', nome)
                    
                    if ra and nome and len(nome) > 3 and entrada:
                        dados.append([ra, nome, entrada])
                        logger.info(f"Extraído: RA={ra}, Nome={nome}, Entrada={entrada}")

    if not dados:
        print("❌ Nenhum dado extraído do PDF.")
        logger.warning("Nenhum registro encontrado no PDF")
        return

    # Remover duplicatas mantendo a primeira ocorrência
    dados_unicos = []
    ras_vistos = set()
    for ra, nome, entrada in dados:
        if ra not in ras_vistos:
            dados_unicos.append([ra, nome, entrada])
            ras_vistos.add(ra)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ra', 'nome', 'entrada'])
        writer.writerows(dados_unicos)

    print(f"✅ CSV gerado: {csv_path} ({len(dados_unicos)} registros)")
    logger.info(f"CSV gerado com sucesso: {len(dados_unicos)} registros")
    