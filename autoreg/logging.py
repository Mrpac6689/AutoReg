import logging
import os
import time


class _FusoHorarioFilter(logging.Filter):
    """
    Acrescenta o fuso (%z) de cada registro. O ciclo do cron roda com
    TZ=America/Rio_Branco (docker-entry-script.sh), mas execuções disparadas
    de outros lugares (ex.: TUI dentro do container KASM) herdam UTC — sem o
    fuso na linha, as duas aparecem misturadas no mesmo arquivo com horários
    5h diferentes e sem como saber qual é qual.
    """
    def filter(self, record):
        record.fuso = time.strftime('%z', time.localtime(record.created))
        return True


def setup_logging():
    """Configura o logging para registrar em arquivo e terminal."""
    log_path = os.path.expanduser('~/AutoReg/autoreg.log')
    handlers = [
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
    # [pid N] separa processos que gravam ao mesmo tempo neste arquivo
    # (cron e execuções manuais compartilham ~/AutoReg)
    for handler in handlers:
        handler.addFilter(_FusoHorarioFilter())
    logging.basicConfig(
        level=logging.INFO,  # ou logging.DEBUG para mais detalhes
        format='%(asctime)s %(fuso)s [pid %(process)d] - %(levelname)s - %(message)s',
        handlers=handlers
    )
