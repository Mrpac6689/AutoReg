"""Testes offline do resultado da internação: python test_internacao.py (usa HOME temporário)."""
import os
import tempfile

os.environ['HOME'] = tempfile.mkdtemp()
PASTA = os.path.join(os.environ['HOME'], 'AutoReg')
os.makedirs(PASTA)
from autoreg import producao_relatorio as p, relatorio_execucao as rel  # noqa: E402
from autoreg.internacao_sisreg import INTERNADO, internar_ficha_sisreg, resultado_internacao as r  # noqa: E402
from selenium.common.exceptions import TimeoutException  # noqa: E402
import sys  # noqa: E402

CONFIRMA = 'Confirma Operação?'
assert r([CONFIRMA, 'Paciente Internado.']) == INTERNADO
assert r([CONFIRMA, 'Sem leito disponivel.']) == 'Sem leito disponivel'
assert r([CONFIRMA, 'Mensagem\n nova.']) == 'Mensagem nova'
assert r([CONFIRMA]) == r([]) == r([CONFIRMA, '']) == 'Erro: Sem resposta do SISREG'
assert r(['Informe o profissional.']) == 'Erro: Informe o profissional'
assert r([CONFIRMA], True) == 'Erro: Erro de Sistema detectado no SISREG'
assert r([CONFIRMA, 'Paciente Internado.'], True) == INTERNADO

# internar_ficha_sisreg com navegador simulado: aceita os dois popups e devolve o 2º
m = sys.modules['autoreg.internacao_sisreg']
m.time.sleep = lambda s: None
m.garantir_sessao_sisreg = lambda *a: False


class Opcao:
    text = 'X'


class Seletor:
    options = [Opcao()] * 3
    def __init__(self, el): pass
    def select_by_visible_text(self, t): pass


class Nav:
    def __init__(self, textos, erro=False):
        self.fila, self.aceitos, self.erro = list(textos), [], erro
        self.switch_to = self
    @property
    def alert(self): return self
    @property
    def text(self): return self.fila[0]
    def accept(self): self.aceitos.append(self.fila.pop(0))
    def find_elements(self, by, xp): return [1] if self.erro and 'Erro de Sistema' in xp else []
    def __getattr__(self, n): return lambda *a, **k: self


class Espera:
    def __init__(self, nav, t): self.nav = nav
    def until(self, cond):
        if cond == 'alerta' and not self.nav.fila:
            raise TimeoutException()
        return self.nav


m.WebDriverWait, m.Select = Espera, Seletor
m.EC = type('EC', (), {'alert_is_present': staticmethod(lambda: 'alerta'),
                       'presence_of_element_located': staticmethod(lambda x: 'el')})
for textos, erro, esperado in (([CONFIRMA, 'Paciente Internado.'], False, INTERNADO),
                               ([CONFIRMA, 'Sem leito disponivel.'], False, 'Sem leito disponivel'),
                               ([CONFIRMA], False, 'Erro: Sem resposta do SISREG'),
                               ([CONFIRMA], True, 'Erro: Erro de Sistema detectado no SISREG')):
    nav = Nav(textos, erro)
    assert internar_ficha_sisreg(nav, '600000001', 'u', 's', None) == esperado
    assert nav.aceitos == textos and not nav.fila

with open(os.path.join(PASTA, 'codigos_internacao.csv'), 'w') as f:
    f.write('Nome do Paciente,Número da Ficha,resultado\nA,1,Paciente Internado\nB,2,Sem leito disponivel\n'
            'C,3,Sem leito disponivel\nD,4,Paciente ja se encontra internado com outra autorizacao\n'
            'E,5,Erro: Sem resposta do SISREG\nF,6,\n')
resumo = rel.resumo_interna().split('\n')
assert resumo == ['🏥 *INTERNAÇÃO*', '✅ 1/6 internado(s)', '⚠️ 2 Sem leito disponivel',
                  '⚠️ 1 Paciente ja se encontra internado com outra autorizacao', '❌ 1 erro(s):',
                  '   • Ficha 5 (E): Erro: Sem resposta do SISREG',
                  '⏸️ 1 não processada(s) (execução interrompida antes de chegar nesse registro)'], resumo
enviados = []
p.enviar_relatorio_producao = lambda rotina, n: enviados.append(n)
p.registrar_producao_internacoes('Internar Pacientes', 'codigos_internacao.csv')
assert enviados == [1]
print('OK')
