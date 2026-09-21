"""Tela inicial: banner, painel de status do sistema e os 5 botões
principais pedidos pelo usuário."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from .. import sysinfo
from ..banner import BANNER
from ..catalogo import PRINCIPAIS
from ..runner import JobRunner
from ..widgets.status_bar import StatusBar


class DashboardScreen(Screen):
    def __init__(self, runner: JobRunner) -> None:
        super().__init__()
        self.runner = runner

    def compose(self) -> ComposeResult:
        yield StatusBar(self.runner)
        with VerticalScroll():
            yield Static(BANNER, id="banner")
            yield Static("Automação SISREG & G-HOSP — v10.0.0 Universe", id="subtitulo")
            with Vertical(classes="painel"):
                yield Static("Estado do sistema", classes="painel-titulo")
                yield Static(sysinfo.resumo_config(), id="info-config")
                yield Static(sysinfo.resumo_autoreg_dir(), id="info-dir")
            with Vertical(classes="painel"):
                yield Static("Última execução (resumo_execucao.txt)", classes="painel-titulo")
                yield Static(sysinfo.resumo_ultima_execucao(), id="info-resumo")
            with Vertical(id="principais-grid"):
                for wf in PRINCIPAIS:
                    yield Button(
                        f"{wf.titulo}   ({wf.flag})",
                        id=f"wf-{wf.flag.lstrip('-')}",
                        classes="principal",
                        variant="primary",
                    )
            with Horizontal(id="nav-row"):
                yield Button("Comandos", id="nav-comandos")
                yield Button("Monitor", id="nav-monitor")
                yield Button("Logs", id="nav-logs")
                yield Button("Ajuda", id="nav-ajuda")
                yield Button("Sair", id="nav-sair", variant="error")
        yield Footer()

    def on_screen_resume(self) -> None:
        self.query_one("#info-config", Static).update(sysinfo.resumo_config())
        self.query_one("#info-dir", Static).update(sysinfo.resumo_autoreg_dir())
        self.query_one("#info-resumo", Static).update(sysinfo.resumo_ultima_execucao())

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        # @work: confirmar_e_sair() usa push_screen_wait(), que só pode ser
        # aguardado de dentro de um worker do Textual.
        bid = event.button.id or ""
        if bid.startswith("wf-"):
            self._disparar_workflow(f"-{bid[3:]}")
        elif bid == "nav-comandos":
            self.app.goto("comandos")
        elif bid == "nav-monitor":
            self.app.goto("monitor")
        elif bid == "nav-logs":
            self.app.goto("logs")
        elif bid == "nav-ajuda":
            self.app.goto("ajuda")
        elif bid == "nav-sair":
            await self.app.confirmar_e_sair()

    def _disparar_workflow(self, flag: str) -> None:
        wf = next((w for w in PRINCIPAIS if w.flag == flag), None)
        if wf is None:
            return
        if self.runner.is_busy():
            self.notify("Já existe um job em execução — aguarde ou pare o atual no Monitor.", severity="warning")
            return
        self.runner.start([wf.flag], f"{wf.titulo} ({wf.flag})")
        self.app.goto("monitor")
