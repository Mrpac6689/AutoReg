"""
Histórico local das solicitações de internação feitas pelo AutoReg no SISREG
(~/AutoReg/historico_solicitacoes.csv), independente dos lembretes do G-HOSP.

- `-ssr` (solicita_sisreg.py) registra cada solicitação criada com sucesso.
- `-spaa` (solicita_pre_aih_auto.py) não reenvia um RA solicitado nos últimos
  DIAS_BLOQUEIO_RESOLICITACAO dias, mesmo que os lembretes não tenham sido
  lidos/gravados — o SISREG só barra uma nova solicitação para o mesmo
  procedimento enquanto a anterior está pendente; depois que ela é internada
  (-interna), uma nova passa (caso RA 642852, 01/10/2026).
- `-clc` (limpa_cache.py) preserva o arquivo.
"""
import os
import csv
import logging
from datetime import datetime, timedelta

ARQUIVO_HISTORICO = 'historico_solicitacoes.csv'
DIAS_BLOQUEIO_RESOLICITACAO = 15
COLUNAS = ['data_hora', 'ra', 'solsisreg', 'procedimento', 'cns']


def _caminho():
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, ARQUIVO_HISTORICO)


def _normalizar_ra(ra):
    texto = str(ra).strip()
    if texto.lower() in ('', 'nan', 'none'):
        return ''
    return texto[:-2] if texto.endswith('.0') else texto


def registrar_solicitacao(ra, solsisreg, procedimento='', cns=''):
    """Acrescenta uma solicitação ao histórico. Nunca lança exceção."""
    try:
        caminho = _caminho()
        novo = not os.path.exists(caminho)
        with open(caminho, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if novo:
                writer.writerow(COLUNAS)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                _normalizar_ra(ra), str(solsisreg).strip(), str(procedimento).strip(), str(cns).strip(),
            ])
        logging.info(f"Histórico de solicitações: RA {_normalizar_ra(ra)} → solicitação {solsisreg} registrada")
    except Exception as e:
        logging.error(f"Histórico de solicitações: falha ao registrar RA {ra} / solicitação {solsisreg}: {e}")


def solicitacoes_recentes(dias=DIAS_BLOQUEIO_RESOLICITACAO):
    """
    Retorna {ra: (data_hora, solsisreg)} com a solicitação mais recente de cada
    RA feita nos últimos `dias` dias. Arquivo ausente/ilegível → {}.
    """
    caminho = _caminho()
    if not os.path.exists(caminho):
        return {}
    limite = datetime.now() - timedelta(days=dias)
    recentes = {}
    try:
        with open(caminho, newline='', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                ra = _normalizar_ra(linha.get('ra', ''))
                try:
                    quando = datetime.strptime(linha.get('data_hora', ''), '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
                if ra and quando >= limite and (ra not in recentes or quando > recentes[ra][0]):
                    recentes[ra] = (quando, linha.get('solsisreg', ''))
    except Exception as e:
        logging.error(f"Histórico de solicitações: falha ao ler {caminho}: {e}")
    return recentes
