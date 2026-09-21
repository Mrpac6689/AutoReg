"""Catálogo de todos os demais comandos, por categoria, com filtro de texto
e toggle para mostrar flags obsoletas."""

from __future__ import annotations

import os
import subprocess

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static, Switch

from ..catalogo import CATEGORIAS, CONFIRMAR_ANTES, Comando
from ..runner import REPO_ROOT, JobRunner
from ..widgets.status_bar import StatusBar
from .modals import ConfirmModal, IntPromptModal, PathPromptModal


def _flag_id(flag: str) -> str:
    return flag.lstrip("-").replace("-", "_")


class ComandosScreen(Screen):
    def __init__(self, runner: JobRunner) -> None:
        super().__init__()
        self.runner = runner
        self._comando_por_id: dict[str, Comando] = {}

    def compose(self) -> ComposeResult:
        yield StatusBar(self.runner)
        with Horizontal(id="log-filtros"):
            yield Input(placeholder="Filtrar por flag ou descrição…", id="filtro")
            yield Switch(id="toggle-obsoletos")
            yield Label("mostrar obsoletos", id="lbl-obsoletos")
        with VerticalScroll(id="lista-comandos"):
            with Horizontal(classes="cmd-row"):
                yield Button("Rodar", id="run-ciclo-completo")
                yield Static(
                    "Ciclo Completo — roda -interna e -alta em N repetições "
                    "(equivalente a --all, sem travar em prompt de terminal)",
                    classes="cmd-desc",
                )
            with Horizontal(classes="cmd-row"):
                yield Button("Abrir", id="run-config")
                yield Static("Editar config.ini no seu editor ($EDITOR, ou nano)", classes="cmd-desc")
            for categoria in CATEGORIAS:
                yield Static(categoria.nome, classes="categoria-titulo")
                for cmd in categoria.comandos:
                    self._comando_por_id[f"run-{_flag_id(cmd.flag)}"] = cmd
                    with Horizontal(classes="cmd-row", id=f"row-{_flag_id(cmd.flag)}"):
                        yield Button("Rodar", id=f"run-{_flag_id(cmd.flag)}")
                        desc = f"{cmd.flag}  —  {cmd.desc}" + ("  [obsoleto]" if cmd.obsoleto else "")
                        yield Static(
                            desc,
                            classes="cmd-desc obsoleto" if cmd.obsoleto else "cmd-desc",
                        )
        yield Footer()

    def on_mount(self) -> None:
        self._aplicar_filtro()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filtro":
            self._aplicar_filtro()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "toggle-obsoletos":
            self._aplicar_filtro()

    def _aplicar_filtro(self) -> None:
        texto = self.query_one("#filtro", Input).value.strip().lower()
        mostrar_obsoletos = self.query_one("#toggle-obsoletos", Switch).value
        for run_id, cmd in self._comando_por_id.items():
            row_id = f"row-{_flag_id(cmd.flag)}"
            try:
                row = self.query_one(f"#{row_id}", Horizontal)
            except Exception:
                continue
            bate_texto = not texto or texto in cmd.flag.lower() or texto in cmd.desc.lower()
            row.display = bate_texto and (not cmd.obsoleto or mostrar_obsoletos)

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        # @work: push_screen_wait() (usado abaixo para confirmação, caminho
        # de PDF e Ciclo Completo) só pode ser aguardado de dentro de um
        # worker do Textual — um handler on_* comum não conta como um.
        bid = event.button.id or ""
        if bid == "run-ciclo-completo":
            await self._ciclo_completo()
            return
        if bid == "run-config":
            self._editar_config()
            return

        cmd = self._comando_por_id.get(bid)
        if cmd is None:
            return
        if self.runner.is_busy():
            self.notify("Já existe um job em execução — aguarde ou pare o atual no Monitor.", severity="warning")
            return

        if cmd.flag in CONFIRMAR_ANTES:
            ok = await self.app.push_screen_wait(
                ConfirmModal(f"Confirma executar {cmd.flag}?\n{cmd.desc}", confirmar="Rodar", cancelar="Cancelar")
            )
            if not ok:
                return

        extra_arg = None
        if cmd.aceita_pdf:
            caminho = await self.app.push_screen_wait(
                PathPromptModal(f"Caminho do PDF para {cmd.flag} (opcional):")
            )
            if caminho is None:
                return
            extra_arg = caminho or None

        argv = [cmd.flag] + ([extra_arg] if extra_arg else [])
        self.runner.start(argv, f"{cmd.flag} — {cmd.desc}")
        self.app.goto("monitor")

    async def _ciclo_completo(self) -> None:
        if self.runner.is_busy():
            self.notify("Já existe um job em execução — aguarde ou pare o atual no Monitor.", severity="warning")
            return
        n = await self.app.push_screen_wait(
            IntPromptModal("Quantas vezes deseja executar o ciclo completo (Interna + Alta)?", padrao=1)
        )
        if not n:
            return
        jobs: list[tuple[list[str], str]] = []
        for ciclo in range(1, n + 1):
            jobs.append((["-interna"], f"Ciclo {ciclo}/{n} — Interna (-interna)"))
            jobs.append((["-alta"], f"Ciclo {ciclo}/{n} — Alta (-alta)"))
        self.runner.start_sequence(jobs)
        self.app.goto("monitor")

    def _editar_config(self) -> None:
        config_path = REPO_ROOT / "config.ini"
        if not config_path.exists():
            self.notify("config.ini não encontrado.", severity="error")
            return
        editor = os.environ.get("EDITOR", "nano")
        with self.app.suspend():
            subprocess.run([editor, str(config_path)])
        self.notify("config.ini fechado.")
