"""
Motivo de alta do G-HOSP → código do SISREG (select co_motivo, lido em
24/11/2026). codigo_motivo devolve '' para o que não reconhece; aí o -eaa usa o
coringa ALTA MELHORADO (decisão do usuário, 24/11/2026), com as travas de
bloqueio_coringa.
"""
import re
import unicodedata

MOTIVOS_SISREG = {
    'ALTA CURADO': '37',
    'ALTA MELHORADO': '38',
    'ALTA A PEDIDO': '40',
    'ALTA COM PREVISAO DE RETORNO PARA ACOMPANHAMENTO DO PACIENTE': '41',
    'ALTA POR EVASAO': '42',
    'ALTA POR OUTROS MOTIVOS': '44',
    'ALTA DE PACIENTE AGUDO EM PSIQUIATRIA': '75',
    'TRANSFERIDO PARA OUTRO ESTABELECIMENTO': '53',
    'TRANSFERENCIA PARA OUTRO ESTABELECIMENTO': '53',  # texto do G-HOSP
    'TRANSFERENCIA PARA INTERNACAO DOMICILIAR': '59',
    'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE': '54',
    'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO INSTITUTO MEDICO LEGAL IML': '55',
    'OBITO COM DECLARACAO DE OBITO FORNECIDA PELO SERVICO DE VERIFICACAO DE OBITO SVO': '56',
    'ENCERRAMENTO ADMINISTRATIVO': '38',  # regra anterior do -eaa, mantida
}


def codigo_motivo(texto):
    """Código do SISREG, ou '' se vazio, permanência ou não reconhecido."""
    sem_acento = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode()
    chave = ' '.join(re.sub(r'[^A-Z ]', ' ', sem_acento.upper()).split())
    if chave in MOTIVOS_SISREG:
        return MOTIVOS_SISREG[chave]
    # Sufixo opcional da sigla ("... LEGAL" sem "IML")
    iniciados = {c for m, c in MOTIVOS_SISREG.items() if chave.startswith('OBITO COM') and len(chave) > 45 and m.startswith(chave)}
    return iniciados.pop() if len(iniciados) == 1 else ''


CORINGA = '38'  # ALTA MELHORADO


def bloqueio_coringa(ra, nome, textos, censo):
    """
    Por que o coringa NÃO pode ser usado, ou '' se pode. `censo` é o retorno de
    vinculos.censo_ghosp_nomes: {ra: nome normalizado}, ou None.

    O RA mais recente pode ser um atendimento de PS encerrado enquanto o
    paciente segue internado em outro RA; por isso confere também o nome.
    """
    from autoreg.vinculos import limpar, normalizar_nome
    for texto in textos:
        chave = normalizar_nome(limpar(texto))
        if 'OBITO' in chave or 'PERMANENCIA' in chave:
            return f'motivo exige conferência ({limpar(texto)})'
    if censo is None:
        return 'sem lista recente de internados do G-HOSP'
    if limpar(ra) in censo or normalizar_nome(nome) in censo.values():
        return 'consta na lista de internados do G-HOSP'
    return ''
