"""
Registro de produção para AUTOREG-API.
Envia relatório de execução (rotina e quantidade de registros) via POST.
Variáveis em config.ini: [AUTOREG-API] autoreg_api_relatorio_url, autoreg_api_key.
"""

import os
import sys
import csv
import configparser

try:
    import urllib.request
    import urllib.error
    import json
except ImportError:
    urllib = None
    json = None


def _caminho_config():
    """Retorna o caminho absoluto do config.ini."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', 'config.ini')


def _ler_config_api():
    """Lê URL e API key da seção [AUTOREG-API] do config.ini."""
    config_path = _caminho_config()
    if not os.path.isfile(config_path):
        return None, None
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'AUTOREG-API' not in config:
        return None, None
    url = config.get('AUTOREG-API', 'autoreg_api_relatorio_url', fallback=None)
    key = config.get('AUTOREG-API', 'autoreg_api_key', fallback=None)
    return (url.strip() if url else None), (key.strip() if key else None)


def contar_registros_csv(caminho_arquivo):
    """
    Conta o número de linhas de dados no CSV (excluindo cabeçalho).
    Retorna 0 se o arquivo não existir ou estiver vazio.
    """
    if not os.path.isfile(caminho_arquivo):
        return 0
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # pula cabeçalho
            return sum(1 for _ in reader)
    except (csv.Error, OSError):
        return 0


def enviar_relatorio_producao(rotina, registros):
    """
    Envia relatório de produção para a AUTOREG-API via POST.
    Payload: {"rotina": rotina, "registros": registros}.
    Retorna True se enviado com sucesso, False caso contrário.
    """
    if json is None or urllib is None:
        print("⚠️ Módulos urllib/json não disponíveis para envio do relatório.")
        return False

    url, api_key = _ler_config_api()
    if not url or not api_key:
        print("⚠️ autoreg_api_relatorio_url ou autoreg_api_key não configurados em config.ini [AUTOREG-API].")
        return False

    payload = json.dumps({"rotina": rotina, "registros": int(registros)}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if 200 <= resp.getcode() < 300:
                print(f"📤 Relatório de produção enviado: rotina={rotina}, registros={registros}")
                return True
            print(f"⚠️ API respondeu com status {resp.getcode()} para rotina={rotina}")
            return False
    except urllib.error.HTTPError as e:
        print(f"⚠️ Erro HTTP ao enviar relatório: {e.code} {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"⚠️ Erro de rede ao enviar relatório: {e.reason}")
        return False
    except Exception as e:
        print(f"⚠️ Erro ao enviar relatório de produção: {e}")
        return False


def registrar_producao(rotina, nome_arquivo_csv):
    """
    Conta os registros do CSV em ~/AutoReg/nome_arquivo_csv e envia
    o relatório de produção (rotina, registros) para a AUTOREG-API.
    Retorna True se o envio foi bem-sucedido, False caso contrário.
    """
    user_dir = os.path.join(os.path.expanduser('~'), 'AutoReg')
    caminho_csv = os.path.join(user_dir, nome_arquivo_csv)
    registros = contar_registros_csv(caminho_csv)
    return enviar_relatorio_producao(rotina, registros)


def contar_altas_efetivadas(caminho_arquivo):
    """
    Conta o número de linhas no CSV onde a coluna 'resultado_sisreg' é 'Alta efetivada'.
    """
    if not os.path.isfile(caminho_arquivo):
        return 0
    count = 0
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('resultado_sisreg') == 'Alta efetivada':
                    count += 1
    except Exception:
        pass
    return count


def registrar_producao_altas(rotina, nome_arquivo_csv):
    """
    Conta as 'Altas efetivadas' no CSV em ~/AutoReg/nome_arquivo_csv e envia
    o relatório de produção para a AUTOREG-API.
    """
    user_dir = os.path.join(os.path.expanduser('~'), 'AutoReg')
    caminho_csv = os.path.join(user_dir, nome_arquivo_csv)
    registros = contar_altas_efetivadas(caminho_csv)
    return enviar_relatorio_producao(rotina, registros)
