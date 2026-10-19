"""Tela de ajuda: mesmo conteúdo de `mostrar_informacoes()` (autoreg.py),
reformatado para a TUI, mais a tabela de atalhos de teclado/mouse."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Static

from ..runner import JobRunner
from ..widgets.status_bar import StatusBar

CONTEUDO = """\
[b]AutoReg[/b] — Automação de Sistemas de Saúde (SISREG & G-HOSP)
Versão: 10.0.0 - Universe
Autor: Michel Ribeiro Paes (MrPaC6689)
Contato: michelrpaes@gmail.com
Repositório: https://github.com/Mrpac6689/AutoReg

[b]DESCRIÇÃO[/b]
Coordenador de workflow para automatização de processos de internação e alta
em sistemas hospitalares SISREG e G-HOSP. Esta TUI é uma interface por cima
do autoreg.py — cada comando roda como um subprocesso próprio, exatamente
como se você tivesse digitado a flag no terminal.

[b]OS 6 BOTÕES PRINCIPAIS (Dashboard)[/b]
  Interna                    -interna         -eci → -ip
  Alta                       -alta            -eis → -eiga → -maa → -eaa
  Trata Duplicados           -td              extração + tratamento de duplicados
  Busca AIHs não solicitadas -aihs            -iga → -ign → -std
  Solicita AIHs (manual)     -solicita        -spaa → -spa → -sia → -ssr → -snt
  Solicita AIHs (automática) -solicita-auto   -spaa → -spb → -sia → -ssr → -snt

[b]TELAS[/b]
  Dashboard   Início: banner, estado do sistema, os 6 botões principais.
  Comandos    Catálogo completo das demais flags, por categoria, com filtro
              de texto e opção de mostrar flags obsoletas.
  Monitor     Acompanha o comando em execução: passo do workflow, progresso
              de registro, ETA estimado, saída ao vivo, arquivos afetados em
              ~/AutoReg, e controles de Parar/Pausar/Retomar/Gravar/Pular.
  Logs        autoreg.log (com filtro por texto/nível), saída bruta do
              último job, e o resumo_execucao.txt da última execução.

[b]SOBRE "SOLICITA AIHs (revisão manual)" (-spa)[/b]
Esse passo pede revisão humana dos registros que o -spaa não aprovou. Ao
chegar no -spa a execução já entra pausada: abra o laudo correto no Chrome
e use Gravar para capturar o link atual e confirmar, ou Pular para
descartar o registro. Retomar libera os registros restantes sem link (o
-ssr não os solicita). Gravar/Pular só ficam ativos enquanto pausado.
Protocolo: arquivos pause.flag/grava.flag/pula.flag em ~/AutoReg/.
"Solicita AIHs (automática)" (-solicita-auto) não tem revisão: o que o
-spaa não aprovar é descartado.

[b]EXEMPLOS EQUIVALENTES NO TERMINAL[/b]
  python autoreg.py -eci               Extrai códigos de internação
  python autoreg.py -eci -ip           Executa duas funções em sequência
  python autoreg.py --all              Executa workflow completo (a TUI faz
                                        isso via "Ciclo Completo", sem o
                                        prompt de repetições do terminal)
  python autoreg.py --config           Edita configuração
  python autoreg.py --help             Mostra a ajuda no terminal

[dim]Algumas flags legadas (-ea, -ar, -tat, -p2c, -especial,
-especial-parallel, -eid, -duplicados, -R) ficam ocultas por padrão na tela
de Comandos — continuam funcionais, ative "mostrar obsoletos" para vê-las.
Ver CHANGELOG.md.[/dim]
"""

ATALHOS = """\
[b]ATALHOS DE TECLADO[/b]
  d           Ir para o Dashboard
  c           Ir para Comandos
  m           Ir para o Monitor
  l           Ir para Logs
  ?           Ir para esta Ajuda
  Esc         Voltar ao Dashboard
  q           Sair (confirma se houver job em execução)
  Tab / Setas Navegar entre botões e campos
  Enter/Espaço Ativar o botão/campo focado

[b]MOUSE[/b]
  Clique direto em qualquer botão, aba ou campo — a TUI funciona
  inteiramente por mouse também, sem precisar do teclado.
"""


class AjudaScreen(Screen):
    def __init__(self, runner: JobRunner) -> None:
        super().__init__()
        self.runner = runner

    def compose(self) -> ComposeResult:
        yield StatusBar(self.runner)
        with VerticalScroll(id="ajuda-body"):
            yield Static(CONTEUDO)
            yield Static(ATALHOS)
        yield Footer()
