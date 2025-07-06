import logging
import os

def setup_logging():
    """Configura o logging para registrar em arquivo e terminal."""
    log_path = os.path.expanduser('~/AutoReg/autoreg.log')
    logging.basicConfig(
        level=logging.INFO,  # ou logging.DEBUG para mais detalhes
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )