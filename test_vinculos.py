"""Testes offline de autoreg/vinculos.py: python test_vinculos.py (usa HOME temporário)."""
import csv
import os
import tempfile
from datetime import datetime, timedelta

os.environ['HOME'] = tempfile.mkdtemp()
os.makedirs(os.path.join(os.environ['HOME'], 'AutoReg'))
from autoreg import vinculos as v  # noqa: E402
from autoreg.extrai_internados_sisreg import _dados_ficha  # noqa: E402

PASTA = os.path.join(os.environ['HOME'], 'AutoReg')


def visto(ra, nome, data, sols=''):
    return {'ra': ra, 'nome': nome, 'data_entrada': data, 'solicitacoes': sols}


def gravar_internados(linhas):
    v._gravar('internados_sisreg.csv', ['Nome', 'solicitacao_sisreg', 'cns', 'erro', 'RA', 'situacao', 'resultado_sisreg'], linhas)


def fila():
    return {l['solicitacao']: l for l in v._ler('altas_pendentes.csv')}


# resolver
N = 'Fulana Das Graças Exemplo Teste'
assert v.resolver('690000002', N.upper(), '25.10.2026', [visto('1', N, '24/10/2026', '690000002')])[:2] == ('1', 'lembrete')
assert v.resolver('9', 'FULANA DAS GRACAS EXEMPLO TESTE', '25.10.2026', [visto('1', N, '24/10/2026')])[:2] == ('1', 'nome+data')
assert v.resolver('9', N, '25.10.2026', [visto('1', N, '24/10/2026'), visto('2', N, '25/10/2026')]) == ('', '', ['1', '2'])
assert v.resolver('9', N, '25.10.2026', [visto('1', N, '01/08/2026')]) == ('', '', ['1'])  # outra internação
assert v.resolver('9', N, '', [visto('1', N, '24/10/2026')])[0] == ''                      # sem data não decide
assert v.resolver('9', 'JOSE DA SILVA', '21.10.2026', [visto('1', 'Jose Da Silva', '22/10/2026')])[0] == ''  # nome comum

# registrar_vistos acumula números e mantém RAs que saíram do censo
v.registrar_vistos([{'ra': 5.0, 'nome': 'A', 'data': '01/01/2026', 'lembretes': '22/10/2026 - 690000001 - CM'}])
v.registrar_vistos([{'ra': 5, 'nome': 'A', 'data': '01/01/2026', 'lembretes': '690000003'}, {'ra': 6, 'nome': 'B', 'data': '', 'lembretes': ''}])
assert {l['ra']: l['solicitacoes'] for l in v._ler('vinculos_ghosp.csv')} == {'5': '690000001;690000003', '6': ''}

# ficha
f = _dados_ficha("Nome da Mãe Naturalidade:\nANA DE TESTE CIDADE - AC\nData de Nascimento: Tipo Sanguíneo:\n01/02/1960 (66 anos) ---\nCondições que Justificam a Internação:\n22/10/2026 - 1234567\n")
assert f == {'nascimento': '01/02/1960', 'mae': 'ANA DE TESTE CIDADE - AC', 'prontuario': '1234567'}
assert _dados_ficha('qualquer coisa') == {'nascimento': '', 'mae': '', 'prontuario': ''}

# fila
t0 = datetime.now()
with open(os.path.join(PASTA, '_home_inovadora_x.csv'), 'w') as arq:
    arq.write(',,,G-HOSP\n100001,,Fulano\n')
base = [
    {'Nome': 'SEM RA', 'solicitacao_sisreg': '1'},
    {'Nome': 'COM ERRO', 'solicitacao_sisreg': '2', 'erro': 'Paciente não encontrado'},
    {'Nome': 'INTERNADO', 'solicitacao_sisreg': '3', 'RA': '100001.0', 'situacao': 'Segue internado'},
    {'Nome': 'FORA DO CENSO', 'solicitacao_sisreg': '4', 'RA': '100002.0', 'situacao': 'Segue internado'},
    {'Nome': 'ALTA OK', 'solicitacao_sisreg': '5', 'RA': '1', 'situacao': 'Alta', 'resultado_sisreg': 'Alta efetivada'},
    {'Nome': 'ALTA FALHOU', 'solicitacao_sisreg': '6', 'RA': '1', 'situacao': 'Alta', 'resultado_sisreg': 'Erro: x'},
    {'Nome': 'NAO VERIFICADO', 'solicitacao_sisreg': '7', 'RA': '100001.0', 'situacao': 'Erro ao verificar'},
]
gravar_internados(base)
v.atualiza_altas_pendentes(t0)
assert set(fila()) == {'1', '2', '4', '6', '7'}
assert v.resumo_pendentes(t0) == ''
t1 = t0 + timedelta(hours=30)
v.atualiza_altas_pendentes(t1)
assert '🟡' in v.resumo_pendentes(t1) and '🔴' not in v.resumo_pendentes(t1)
# some por um ciclo curto e volta: mantém a idade; resolvida de vez: sai do resumo
gravar_internados(base[2:3])
v.atualiza_altas_pendentes(t1 + timedelta(hours=1))
assert v.resumo_pendentes(t1 + timedelta(hours=1)) == ''
gravar_internados(base)
t2 = t0 + timedelta(hours=40)
v.atualiza_altas_pendentes(t2)
assert fila()['1']['desde'] == t0.strftime(v.FORMATO)
t3 = t0 + timedelta(hours=80)
v.atualiza_altas_pendentes(t3)
assert '🔴' in v.resumo_pendentes(t3)
gravar_internados([])
try:
    v.atualiza_altas_pendentes(t3)
    raise SystemExit('lista vazia deveria falhar')
except RuntimeError:
    assert not fila()['1']['resolvida_em']

# vínculo manual: só linhas numéricas valem
with open(os.path.join(PASTA, 'vinculos_manuais.csv'), 'a') as arq:
    arq.write('690000001,600001,x\nabc,1,\n5,,\n')
assert v.vinculos_manuais() == {'690000001': '600001'}

# motivos e resumo de alta
from autoreg.motivos_alta import codigo_motivo  # noqa: E402
from autoreg.motivo_alta_avancado import texto_resumo_valido, falha_em_massa  # noqa: E402
for texto, codigo in (
    ('ALTA MELHORADO', '38'), ('Alta por Evasão', '42'), ('TRANSFERENCIA PARA OUTRO ESTABELECIMENTO', '53'),
    ('ALTA COM PREVISAO DE RETORNO PARA ACOMPANHAMENTO DO PACIENTE', '41'),
    ('OBITO COM DECLARACAO DE OBITO FORNECIDA PELO MEDICO ASSISTENTE', '54'),
    ('OBITO COM DECLARACAO DE OBITO FORNECIDA PELO INSTITUTO MEDICO LEGAL - IML', '55'),
    ('OBITO COM DECLARACAO DE OBITO FORNECIDA PELO INSTITUTO MEDICO LEGAL', '55'),
    ('OBITO COM DECLARACAO DE OBITO FORNECIDA PELO', ''), ('PERMANENCIA POR OUTROS MOTIVOS', ''),
    ('', ''), ('nan', ''), (None, ''), ('QUALQUER', ''),
):
    assert codigo_motivo(texto) == codigo, (texto, codigo_motivo(texto))
from autoreg.motivos_alta import bloqueio_coringa  # noqa: E402
with open(os.path.join(PASTA, '_home_inovadora_x.csv'), 'w') as arq:
    arq.write(',,,G-HOSP\nN Intern,,Nome\n100001,,Fulano De Tál,,\n')
censo = v.censo_ghosp_nomes()
assert censo == {'100001': 'FULANO DE TAL'} and v.censo_ghosp() == {'100001'}
assert bloqueio_coringa('100002.0', 'BELTRANO', ('', float('nan')), censo) == ''
assert bloqueio_coringa('100002.0', 'BELTRANO', ('QUALQUER', 'ALTA POR EVASAO'), censo) == ''
assert bloqueio_coringa('100001.0', 'BELTRANO', ('',), censo)  # RA internado
assert bloqueio_coringa('100002', 'FULANO DE TAL', ('',), censo)  # internado em outro RA
assert bloqueio_coringa('100002', 'BELTRANO', ('', 'PERMANÊNCIA POR OUTROS MOTIVOS'), censo)
assert bloqueio_coringa('100002', 'BELTRANO', ('ÓBITO SEM DECLARACAO',), censo)
assert bloqueio_coringa('100002', 'BELTRANO', ('',), None)
assert texto_resumo_valido('INSERIR') == '' and texto_resumo_valido(' Inserir \n') == '' and texto_resumo_valido('') == ''
assert texto_resumo_valido('INSERIR\nPaciente em alta') == 'Paciente em alta'
assert falha_em_massa(86, 86) and not falha_em_massa(1, 86) and not falha_em_massa(2, 3) and not falha_em_massa(0, 0)
print('OK')
