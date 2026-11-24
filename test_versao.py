"""Confere se a versão e as flags estão sincronizadas na documentação: python test_versao.py"""
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))


def ler(nome):
    with open(os.path.join(AQUI, nome), encoding='utf-8') as f:
        return f.read()


versao = re.search(r'VERSAO = "([^"]+)"', ler('autoreg/versao.py'))[1]
erros = []
if f'Versão: {versao} ' not in ler('autoreg.py'):
    erros.append('autoreg.py (mostrar_informacoes)')
if set(re.findall(r'Version-([\d.]+)-orange|AutoReg v([\d.]+) Universe', ler('README.md'))) != {(versao, ''), ('', versao)}:
    erros.append('README.md (badges/rodapés)')
if re.search(r'^## \[(\d[^\]]*)\]', ler('CHANGELOG.md'), re.M)[1] != versao:
    erros.append('CHANGELOG.md (primeira versão numerada)')
for flag in re.findall(r"^    '(-[a-z0-9-]+)':", ler('autoreg.py'), re.M):
    if f'"{flag}"' not in ler('tui/catalogo.py'):
        erros.append(f'tui/catalogo.py sem {flag}')
if erros:
    raise SystemExit('Fora de sincronia: ' + '; '.join(erros))
print(f'OK {versao}')
