"""
Vínculo solicitação SISREG → RA G-HOSP e fila de altas pendentes.

Regra do módulo: nenhuma internação aberta no SISREG pode ficar esquecida. Cada
uma tem um RA vinculado ou aparece em altas_pendentes.csv e no resumo do
WhatsApp. NUNCA se dá alta só porque o paciente não foi achado no G-HOSP.

Arquivos em ~/AutoReg (preservados por -clc):
- vinculos_ghosp.csv   (-ign): RAs vistos internados, com nome, data de entrada
                       e nºs de solicitação citados nos lembretes do paciente.
- vinculos_manuais.csv (humano): solicitacao,ra,observacao — tem prioridade total.
- altas_pendentes.csv  (-rap): fila; linhas resolvidas são mantidas, para que
                       'desde' não zere se uma extração vier incompleta.
"""
import csv
import glob
import logging
import os
import re
import unicodedata
from datetime import datetime, timedelta

from autoreg.ras_paciente import NUMERO_SOLICITACAO_RE

COLUNAS_GHOSP = ['ra', 'nome', 'data_entrada', 'solicitacoes', 'visto_em']
COLUNAS_MANUAIS = ['solicitacao', 'ra', 'observacao']
COLUNAS_PENDENTES = ['solicitacao', 'nome', 'cns', 'data_internacao', 'motivo', 'ra',
                     'candidatos', 'desde', 'ultima_vez', 'resolvida_em']
FORMATO = '%Y-%m-%d %H:%M:%S'
AVISO_HORAS = 24
DESTAQUE_HORAS = 72
MAXIMO_NO_RESUMO = 30
# -ip grava a internação como data da solicitação - 2 dias, então a entrada no
# G-HOSP pode cair um pouco depois da data do SISREG.
JANELA_ANTES = timedelta(days=15)
JANELA_DEPOIS = timedelta(days=3)
CENSO_VALIDADE = timedelta(hours=36)


def _caminho(nome):
    pasta = os.path.expanduser('~/AutoReg')
    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, nome)


def limpar(valor):
    texto = str(valor if valor is not None else '').strip()
    if texto.lower() in ('', 'nan', 'none'):
        return ''
    return texto[:-2] if texto.endswith('.0') else texto


def normalizar_nome(nome):
    sem_acento = unicodedata.normalize('NFKD', str(nome)).encode('ascii', 'ignore').decode()
    return ' '.join(re.sub(r'[^A-Z ]', ' ', sem_acento.upper()).split())


def ler_data(texto):
    m = re.search(r'(\d{2})[./](\d{2})[./](\d{4})', str(texto))
    try:
        return datetime(int(m[3]), int(m[2]), int(m[1])) if m else None
    except ValueError:
        return None


def na_janela(entrada, internacao):
    return bool(entrada and internacao and
                internacao - JANELA_ANTES <= entrada <= internacao + JANELA_DEPOIS)


def _ler(nome):
    """Linhas do CSV; [] se não existe. Erro de leitura é propagado: regravar
    a partir de uma leitura falha apagaria o que já foi acumulado."""
    caminho = _caminho(nome)
    if not os.path.exists(caminho):
        return []
    with open(caminho, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def _gravar(nome, colunas, linhas):
    caminho = _caminho(nome)
    with open(caminho + '.tmp', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, colunas, extrasaction='ignore', restval='')
        w.writeheader()
        w.writerows(linhas)
    os.replace(caminho + '.tmp', caminho)


def registrar_vistos(vistos, agora=None):
    """-ign: acrescenta/atualiza [{ra, nome, data, lembretes}]. Nunca lança."""
    try:
        agora = (agora or datetime.now()).strftime(FORMATO)
        base = {limpar(l['ra']): l for l in _ler('vinculos_ghosp.csv')}
        for v in vistos:
            ra = limpar(v.get('ra'))
            if not ra:
                continue
            antigos = set(filter(None, base.get(ra, {}).get('solicitacoes', '').split(';')))
            novos = set(NUMERO_SOLICITACAO_RE.findall(str(v.get('lembretes', ''))))
            base[ra] = {'ra': ra, 'nome': limpar(v.get('nome')), 'data_entrada': limpar(v.get('data')),
                        'solicitacoes': ';'.join(sorted(antigos | novos)), 'visto_em': agora}
        _gravar('vinculos_ghosp.csv', COLUNAS_GHOSP, base.values())
    except Exception as e:
        logging.error(f"Vínculos: falha ao registrar RAs vistos: {e}")


def vinculos_manuais():
    try:
        return {limpar(l.get('solicitacao')): limpar(l.get('ra')) for l in _ler('vinculos_manuais.csv')
                if limpar(l.get('solicitacao')).isdigit() and limpar(l.get('ra')).isdigit()}
    except Exception as e:
        logging.error(f"Vínculos: vinculos_manuais.csv ilegível: {e}")
        return {}


def resolver(solicitacao, nome, data_internacao, vistos=None):
    """
    Retorna (ra, origem, candidatos) a partir dos RAs vistos pelo -ign. Só
    aceita automaticamente com UM candidato e data compatível; senão ra=''.
    """
    try:
        vistos = _ler('vinculos_ghosp.csv') if vistos is None else vistos
    except Exception as e:
        logging.error(f"Vínculos: vinculos_ghosp.csv ilegível: {e}")
        return '', '', []
    internacao = ler_data(data_internacao)
    alvo = normalizar_nome(nome)
    por_numero = [v for v in vistos if limpar(solicitacao) in v.get('solicitacoes', '').split(';')]
    por_nome = [v for v in vistos if alvo and normalizar_nome(v['nome']) == alvo]
    candidatos = sorted({v['ra'] for v in por_numero + por_nome})
    for origem, grupo in (('lembrete', por_numero), ('nome+data', por_nome)):
        compativeis = [v for v in grupo if na_janela(ler_data(v['data_entrada']), internacao)]
        # Nome com menos de 3 termos é homônimo fácil ("JOSE DA SILVA")
        comum = origem == 'nome+data' and len([t for t in alvo.split() if len(t) > 2]) < 3
        if len(compativeis) == 1 and not comum:
            return compativeis[0]['ra'], origem, candidatos
        if compativeis:
            break  # ambíguo na fonte mais forte: não decide pela mais fraca
    return '', '', candidatos


def censo_ghosp_nomes(agora=None):
    """{ra: nome normalizado} do último relatório bruto do -iga, ou None se ausente/velho."""
    arquivos = glob.glob(_caminho('_home_inovadora*.csv'))
    if not arquivos:
        return None
    recente = max(arquivos, key=os.path.getmtime)
    if (agora or datetime.now()) - datetime.fromtimestamp(os.path.getmtime(recente)) > CENSO_VALIDADE:
        return None
    with open(recente, encoding='utf-8', errors='replace') as f:
        # N Intern,,Nome,... — o nome fica na 3ª coluna
        censo = {l[0].strip(): normalizar_nome(l[2]) if len(l) > 2 else ''
                 for l in csv.reader(f) if l and re.fullmatch(r'\d{5,7}', l[0].strip())}
    return censo or None


def censo_ghosp(agora=None):
    """RAs do último relatório bruto do -iga, ou None se ausente/velho."""
    censo = censo_ghosp_nomes(agora)
    return set(censo) if censo else None


def motivo_pendencia(linha, censo):
    """Motivo pelo qual a internação precisa de alguém, ou '' se está resolvida."""
    ra, situacao = limpar(linha.get('RA')), limpar(linha.get('situacao'))
    if not ra:
        return limpar(linha.get('erro')) or 'Prontuário aberto, mas sem RA HUERB'
    if situacao == 'Alta':
        resultado = limpar(linha.get('resultado_sisreg'))
        return '' if resultado == 'Alta efetivada' else f"Alta não efetivada no SISREG {resultado}".strip()
    if situacao == 'Segue internado':
        # Sem resumo de alta: normal só enquanto consta no censo do G-HOSP
        if censo is None or ra in censo:
            return ''
        return 'Sem resumo de alta e fora da lista de internados do G-HOSP'
    return f"Alta não verificada no G-HOSP ({situacao or 'etapa -maa não chegou ao paciente'})"


def atualiza_altas_pendentes(agora=None):
    """-rap: recalcula altas_pendentes.csv a partir de internados_sisreg.csv."""
    agora = agora or datetime.now()
    carimbo = agora.strftime(FORMATO)
    if not os.path.exists(_caminho('vinculos_manuais.csv')):
        _gravar('vinculos_manuais.csv', COLUNAS_MANUAIS, [])
    internados = _ler('internados_sisreg.csv')
    if not internados:
        raise RuntimeError('internados_sisreg.csv ausente ou vazio — fila de pendências mantida como estava')
    censo = censo_ghosp(agora)
    if censo is None:
        logging.warning('-rap: sem lista recente de internados do G-HOSP; "Segue internado" não conferido')
    vistos = _ler('vinculos_ghosp.csv')
    fila = {l['solicitacao']: l for l in _ler('altas_pendentes.csv')}
    abertas = set()
    for linha in internados:
        sol = limpar(linha.get('solicitacao_sisreg'))
        motivo = motivo_pendencia(linha, censo)
        if not sol or not motivo:
            continue
        abertas.add(sol)
        # Reaberta em menos de 24 h (ex.: extração incompleta): mantém a idade
        antiga = fila.get(sol, {})
        desde = antiga.get('desde') or carimbo
        resolvida = antiga.get('resolvida_em')
        if resolvida and agora - datetime.strptime(resolvida, FORMATO) > timedelta(hours=AVISO_HORAS):
            desde = carimbo
        _, _, candidatos = resolver(sol, linha.get('Nome', ''), linha.get('data_internacao', ''), vistos)
        fila[sol] = {
            'solicitacao': sol, 'nome': limpar(linha.get('Nome')), 'cns': limpar(linha.get('cns')),
            'data_internacao': limpar(linha.get('data_internacao')), 'motivo': motivo,
            'ra': limpar(linha.get('RA')), 'candidatos': ';'.join(candidatos),
            'desde': desde, 'ultima_vez': carimbo, 'resolvida_em': '',
        }
    for sol, l in fila.items():
        if sol not in abertas and not l.get('resolvida_em'):
            l['resolvida_em'] = carimbo
    _gravar('altas_pendentes.csv', COLUNAS_PENDENTES, fila.values())
    logging.info(f"-rap: {len(abertas)} alta(s) pendente(s) de vínculo/verificação")
    print(f"📌 {len(abertas)} alta(s) pendente(s) em altas_pendentes.csv")


def resumo_pendentes(agora=None):
    """Bloco do WhatsApp; '' se nada tem 24 h ou mais."""
    agora = agora or datetime.now()
    try:
        abertas = [l for l in _ler('altas_pendentes.csv') if not l.get('resolvida_em')]
        itens = sorted(
            [((agora - datetime.strptime(l['desde'], FORMATO)).total_seconds() / 3600, l) for l in abertas],
            key=lambda x: -x[0])
    except Exception as e:
        return f"📌 *SEM VÍNCULO*\n⚠️ Erro ao ler altas_pendentes.csv: {e}"
    itens = [(h, l) for h, l in itens if h >= AVISO_HORAS]
    if not itens:
        return ''
    texto = [f"📌 *SEM VÍNCULO / ALTA A CONFERIR* ({len(itens)})"]
    for horas, l in itens[:MAXIMO_NO_RESUMO]:
        marca = '🔴' if horas >= DESTAQUE_HORAS else '🟡'
        extra = f" | candidatos: {l['candidatos']}" if l.get('candidatos') else ''
        ra = f" | RA {l['ra']}" if l.get('ra') else ''
        texto.append(f"{marca} {l['nome']} — sol. {l['solicitacao']}{ra}, {int(horas // 24)}d: {l['motivo'][:90]}{extra}")
    if len(itens) > MAXIMO_NO_RESUMO:
        texto.append(f"… e mais {len(itens) - MAXIMO_NO_RESUMO} em altas_pendentes.csv")
    texto.append("Informe o RA em vinculos_manuais.csv ou dê a saída no SISREG.")
    return '\n'.join(texto)
