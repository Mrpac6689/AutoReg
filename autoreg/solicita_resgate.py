import os
import json
import logging
import unicodedata
import pandas as pd

from autoreg.logging import setup_logging
from autoreg.solicita_sisreg import solicita_sisreg
from autoreg.solicita_nota import solicita_nota

setup_logging()

CORRELACOES_PATH = os.path.expanduser('~/AutoReg/correlacoes_aih.json')
ERRO_ALVO = 'Procedimento nao habilitado!'


def _normalizar(texto):
    """Remove acentos e converte para maiúsculas, para comparação tolerante."""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    sem_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acentos.upper().strip()


def _carregar_codigos_residuais():
    """
    Lê os códigos curinga (campo 'destino') de cada clínica a partir do bloco
    'conversoes' de correlacoes_aih.json — a mesma fonte já usada por -spaa —
    em vez de duplicar os códigos aqui. Retorna {CLÍNICA_NORMALIZADA: codigo}.
    """
    if not os.path.exists(CORRELACOES_PATH):
        print(f"⚠️  Arquivo de correlações não encontrado: {CORRELACOES_PATH}")
        return {}
    try:
        with open(CORRELACOES_PATH, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        conversoes = dados.get('conversoes', {})
        return {
            _normalizar(clinica): entrada['destino']
            for clinica, entrada in conversoes.items()
            if entrada.get('destino')
        }
    except Exception as e:
        print(f"❌ Erro ao carregar correlacoes_aih.json: {e}")
        return {}


def solicita_resgate():
    """
    Resgata registros de solicita_inf_aih.csv que falharam no SISREG com o
    erro "Procedimento não habilitado!": troca o procedimento pelo código
    curinga da clínica do registro (lido de correlacoes_aih.json ->
    conversoes.<CLÍNICA>.destino) e retoma a pipeline a partir de -ssr
    (solicita_sisreg -> solicita_nota) para os registros resgatados.
    """
    print("\n---===> RESGATE DE SOLICITAÇÕES (-sresg) <===---")
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'solicita_inf_aih.csv')

    if not os.path.exists(csv_path):
        print(f"❌ Arquivo não encontrado: {csv_path}")
        logging.error(f"solicita_resgate: arquivo não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    colunas_necessarias = ('erro', 'tipo', 'procedimento')
    faltantes = [c for c in colunas_necessarias if c not in df.columns]
    if faltantes:
        print(f"❌ CSV não contém as colunas necessárias: {', '.join(faltantes)}")
        logging.error(f"solicita_resgate: colunas faltantes no CSV: {', '.join(faltantes)}")
        return

    codigos_residuais = _carregar_codigos_residuais()
    if not codigos_residuais:
        print("❌ Nenhum código residual disponível em correlacoes_aih.json (bloco 'conversoes')")
        logging.error("solicita_resgate: nenhum código residual disponível")
        return

    # Colunas de texto que este módulo grava via df.at[] — podem vir como
    # float64 (NaN) do CSV quando vazias, travando com "Invalid value ...
    # for dtype 'float64'" (mesmo problema já corrigido em -sia/-ssr/-snt).
    for col in ('erro', 'revisar', 'procedimento'):
        if col in df.columns:
            df[col] = df[col].astype(object)

    alvo_normalizado = _normalizar(ERRO_ALVO)
    mask_alvo = df['erro'].apply(lambda x: alvo_normalizado in _normalizar(x))
    indices_alvo = df[mask_alvo].index

    if len(indices_alvo) == 0:
        print(f"✅ Nenhum registro com erro '{ERRO_ALVO}' encontrado — nada a resgatar.")
        logging.info("solicita_resgate: nenhum registro para resgatar")
        return

    print(f"🔎 {len(indices_alvo)} registro(s) com '{ERRO_ALVO}' encontrado(s)")

    resgatados = 0
    for idx in indices_alvo:
        clinica = df.at[idx, 'tipo']
        codigo_residual = codigos_residuais.get(_normalizar(clinica))
        if not codigo_residual:
            print(f"   ⚠️  Registro {idx}: clínica {clinica!r} sem código residual configurado — mantido para revisão manual")
            logging.warning(f"solicita_resgate: registro {idx} — clínica {clinica!r} sem código residual configurado")
            continue

        # Zero-preenche para exibição: o CSV pode ter perdido o zero à
        # esquerda do código SIGTAP (10 dígitos) numa releitura anterior do
        # pandas, que infere a coluna como número quando todos os valores
        # parecem dígitos — mesmo caso já tratado em solicita_sisreg.py.
        procedimento_original = str(df.at[idx, 'procedimento'])
        if procedimento_original.endswith('.0'):
            procedimento_original = procedimento_original[:-2]
        procedimento_original = procedimento_original.replace('.', '').zfill(10)
        df.at[idx, 'procedimento'] = codigo_residual
        df.at[idx, 'erro'] = ''
        if 'revisar' in df.columns:
            df.at[idx, 'revisar'] = ''
        print(f"   🔄 Registro {idx}: procedimento {procedimento_original} → {codigo_residual} ({clinica})")
        logging.info(f"solicita_resgate: registro {idx} — procedimento {procedimento_original} → {codigo_residual} ({clinica})")
        resgatados += 1

    df.to_csv(csv_path, index=False)

    if resgatados == 0:
        print("⚠️  Nenhum registro pôde ser resgatado automaticamente (clínica sem código residual configurado).")
        logging.warning("solicita_resgate: nenhum registro resgatado")
        return

    print(f"✅ {resgatados} registro(s) atualizado(s) com o código residual — retomando pipeline a partir de -ssr...")
    logging.info(f"solicita_resgate: {resgatados} registro(s) atualizados — retomando -ssr")

    solicita_sisreg()
    solicita_nota()

    print("\n---===> RESGATE CONCLUÍDO <===---")
