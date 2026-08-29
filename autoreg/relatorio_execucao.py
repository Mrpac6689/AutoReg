"""
Resumo de execução do ciclo de cron (interna / alta / solicitação) + envio
do resumo consolidado via WhatsApp (Evolution API).

Substitui o antigo envio do log cru (tail -n 10) por um resumo real,
derivado do estado final dos CSVs de cada rotina: o que foi feito, o que
não foi feito e detalhes de erro.
"""

import os
import sys
import json
import configparser
from datetime import datetime

import pandas as pd

try:
    import urllib.request
    import urllib.error
except ImportError:
    urllib = None

from .producao_relatorio import contar_registros_csv


def _user_dir():
    return os.path.expanduser('~/AutoReg')


def _caminho_config():
    """Retorna o caminho absoluto do config.ini."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', 'config.ini')


def _truncar(texto, limite=150):
    texto = str(texto).strip()
    if len(texto) > limite:
        return texto[:limite].rstrip() + '…'
    return texto


def contar_linhas_csv(nome_arquivo):
    """Conta linhas de dados (sem cabeçalho) de um CSV dentro de ~/AutoReg."""
    return contar_registros_csv(os.path.join(_user_dir(), nome_arquivo))


# ── Resumo por módulo ──────────────────────────────────────────────────────

def resumo_interna():
    """Monta o bloco de resumo da rotina de internação a partir de
    codigos_internacao.csv (coluna 'resultado', gravada por interna_pacientes)."""
    caminho = os.path.join(_user_dir(), 'codigos_internacao.csv')
    if not os.path.exists(caminho):
        return "🏥 *INTERNAÇÃO*\n⚠️ Arquivo codigos_internacao.csv não encontrado — etapa pode não ter rodado."

    try:
        df = pd.read_csv(caminho)
    except Exception as e:
        return f"🏥 *INTERNAÇÃO*\n⚠️ Erro ao ler codigos_internacao.csv: {e}"

    total = len(df)
    if total == 0:
        return "🏥 *INTERNAÇÃO*\nℹ️ Nenhum paciente a internar neste ciclo."

    if 'resultado' not in df.columns:
        return (f"🏥 *INTERNAÇÃO*\n"
                f"ℹ️ {total} ficha(s) processada(s) (detalhamento indisponível — coluna 'resultado' ausente)")

    resultado = df['resultado'].astype(str)
    sucesso = df[resultado == 'Internado com sucesso']
    erros = df[resultado.str.startswith('Erro', na=False)]
    sem_processar = total - len(sucesso) - len(erros)

    linhas = ["🏥 *INTERNAÇÃO*", f"✅ {len(sucesso)}/{total} internado(s) com sucesso"]
    if len(erros) > 0:
        linhas.append(f"❌ {len(erros)} erro(s):")
        for _, row in erros.iterrows():
            ficha = row.get('Número da Ficha', '?')
            nome = row.get('Nome do Paciente', '')
            motivo = _truncar(row.get('resultado', ''))
            linhas.append(f"   • Ficha {ficha} ({nome}): {motivo}")
    if sem_processar > 0:
        linhas.append(f"⏸️ {sem_processar} não processada(s) (execução interrompida antes de chegar nesse registro)")

    return "\n".join(linhas)


def resumo_alta():
    """Monta o bloco de resumo da rotina de alta a partir de
    internados_sisreg.csv (coluna 'resultado_sisreg', gravada por executa_alta_avancado)."""
    caminho = os.path.join(_user_dir(), 'internados_sisreg.csv')
    if not os.path.exists(caminho):
        return "🚪 *ALTA*\n⚠️ Arquivo internados_sisreg.csv não encontrado — etapa pode não ter rodado."

    try:
        df = pd.read_csv(caminho)
    except Exception as e:
        return f"🚪 *ALTA*\n⚠️ Erro ao ler internados_sisreg.csv: {e}"

    if 'situacao' not in df.columns:
        return "🚪 *ALTA*\nℹ️ Coluna 'situacao' ausente — detalhamento indisponível."

    pendentes = df[df['situacao'] == 'Alta']
    total = len(pendentes)
    if total == 0:
        return "🚪 *ALTA*\nℹ️ Nenhuma alta pendente neste ciclo."

    if 'resultado_sisreg' not in pendentes.columns:
        return (f"🚪 *ALTA*\n"
                f"ℹ️ {total} alta(s) pendente(s) (detalhamento indisponível — coluna 'resultado_sisreg' ausente)")

    resultado = pendentes['resultado_sisreg'].astype(str)
    efetivadas = pendentes[resultado == 'Alta efetivada']
    erros = pendentes[resultado.str.startswith('Erro', na=False)]
    nao_processadas = total - len(efetivadas) - len(erros)

    linhas = ["🚪 *ALTA*", f"✅ {len(efetivadas)}/{total} alta(s) efetivada(s)"]
    if len(erros) > 0:
        linhas.append(f"❌ {len(erros)} erro(s):")
        for _, row in erros.iterrows():
            solicitacao = row.get('solicitacao_sisreg', '?')
            motivo = _truncar(row.get('resultado_sisreg', ''))
            linhas.append(f"   • Solicitação {solicitacao}: {motivo}")
    if nao_processadas > 0:
        linhas.append(f"⏸️ {nao_processadas} não processada(s) (execução interrompida antes de chegar nesse registro)")

    return "\n".join(linhas)


def resumo_solicitacao(snapshots):
    """
    Monta o bloco de resumo da rotina de solicitação de AIH.

    snapshots: dict com contagens de linhas tiradas em pontos-chave da
    sequência -spaa -spb -sia -ssr -snt:
      'inicial'     — linhas de internados_ghosp_avancado.csv, antes de rodar
      'apos_spaa'   — linhas de solicita_inf_aih.csv logo após -spaa
      'apos_bridge' — linhas de solicita_inf_aih.csv logo após -spb
    O estado final (após -snt) é lido diretamente de solicita_inf_aih.csv.
    """
    inicial = snapshots.get('inicial', 0)
    apos_spaa = snapshots.get('apos_spaa', inicial)
    apos_bridge = snapshots.get('apos_bridge', apos_spaa)

    caminho = os.path.join(_user_dir(), 'solicita_inf_aih.csv')
    try:
        df_final = pd.read_csv(caminho) if os.path.exists(caminho) else pd.DataFrame()
    except Exception:
        df_final = pd.DataFrame()

    restantes = len(df_final)
    falta_aih = max(inicial - apos_spaa, 0)
    manual_pendente = max(apos_spaa - apos_bridge, 0)
    sucesso = max(apos_bridge - restantes, 0)

    linhas = ["📨 *SOLICITAÇÃO DE AIH*", f"📋 {inicial} internação(ões) avaliada(s)"]
    linhas.append(f"✅ {sucesso} solicitação(ões) concluída(s) com sucesso")
    if falta_aih > 0:
        linhas.append(f"📝 {falta_aih} sem laudo disponível (nota 'FALTA AIH' registrada no G-HOSP)")
    if manual_pendente > 0:
        linhas.append(f"⏭️ {manual_pendente} pendente(s) de revisão manual (sem laudo compatível — rodar -spa)")

    if restantes > 0:
        linhas.append(f"❌ {restantes} ainda pendente(s) ao final do ciclo:")
        for _, row in df_final.iterrows():
            ra = row.get('ra', '?')
            erro_val = row.get('erro') if 'erro' in df_final.columns else None
            revisar_val = row.get('revisar') if 'revisar' in df_final.columns else None
            if pd.notna(erro_val) and str(erro_val).strip():
                motivo = str(erro_val)
            elif str(revisar_val).strip().lower() == 'sim':
                motivo = 'dados incompletos (revisão necessária)'
            else:
                motivo = 'motivo não identificado'
            linhas.append(f"   • RA {ra}: {_truncar(motivo)}")

    return "\n".join(linhas)


# ── Persistência e envio ────────────────────────────────────────────────────

def registrar_resumo(bloco_texto):
    """Adiciona um bloco de resumo ao arquivo acumulado do ciclo atual."""
    caminho = os.path.join(_user_dir(), 'resumo_execucao.txt')
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'a', encoding='utf-8') as f:
        f.write(bloco_texto.strip() + "\n\n")
    print(f"📝 Resumo registrado em {caminho}")


def _ler_config_evolution():
    """Lê URL, chave e número da seção [EVOLUTION-API] do config.ini."""
    config_path = _caminho_config()
    if not os.path.isfile(config_path):
        return None, None, None
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'EVOLUTION-API' not in config:
        return None, None, None
    url = config.get('EVOLUTION-API', 'evolution_api_url', fallback=None)
    key = config.get('EVOLUTION-API', 'evolution_api_key', fallback=None)
    numero = config.get('EVOLUTION-API', 'evolution_api_number', fallback=None)
    return (
        url.strip() if url else None,
        key.strip() if key else None,
        numero.strip() if numero else None,
    )


def enviar_resumo_whatsapp(limpar_depois=True):
    """
    Lê o resumo acumulado do ciclo (~/AutoReg/resumo_execucao.txt) e envia
    via WhatsApp (Evolution API), usando credenciais de config.ini [EVOLUTION-API].
    Retorna True se enviado com sucesso.
    """
    if urllib is None:
        print("⚠️ Módulo urllib não disponível para envio do resumo.")
        return False

    caminho = os.path.join(_user_dir(), 'resumo_execucao.txt')
    if not os.path.exists(caminho):
        print(f"⚠️ Nenhum resumo encontrado em {caminho} — nada a enviar.")
        return False

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()

    if not conteudo:
        print("⚠️ Resumo vazio — nada a enviar.")
        return False

    url, api_key, numero = _ler_config_evolution()
    if not url or not api_key or not numero:
        print("⚠️ [EVOLUTION-API] incompleto em config.ini "
              "(evolution_api_url / evolution_api_key / evolution_api_number). Envio abortado.")
        return False

    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
    mensagem = f"📊 *Resumo AutoReg — {data_hora}*\n\n{conteudo}"

    payload = json.dumps({"number": numero, "text": mensagem}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "apikey": api_key},
        method='POST',
    )

    sucesso = False
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            sucesso = 200 <= resp.getcode() < 300
            if sucesso:
                print("📤 Resumo enviado com sucesso via WhatsApp.")
            else:
                print(f"⚠️ API respondeu com status {resp.getcode()} ao enviar resumo.")
    except urllib.error.HTTPError as e:
        print(f"⚠️ Erro HTTP ao enviar resumo via WhatsApp: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        print(f"⚠️ Erro de rede ao enviar resumo via WhatsApp: {e.reason}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar resumo via WhatsApp: {e}")

    if sucesso and limpar_depois:
        try:
            os.remove(caminho)
        except OSError:
            pass

    return sucesso


if __name__ == '__main__':
    enviar_resumo_whatsapp()
