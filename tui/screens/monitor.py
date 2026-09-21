"""Acompanhamento em tempo real: passo do workflow, progresso de registro,
ETA estimado, saída ao vivo, arquivos afetados e controles de
parar/pausar/retomar/gravar/pular."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Button, Footer, RichLog, Static

from ..catalogo import arquivos_para_flags
from ..runner import JobRunner
from ..widgets.file_watch import FileWatchPanel
from ..widgets.status_bar import StatusBar
from .modals import ConfirmModal


def _fmt_eta(segundos: float | None) -> str:
    if segundos is None:
        return "indisponível"
    if segundos < 60:
        return f"~{int(segundos)}s"
    if segundos < 3600:
        return f"~{int(segundos // 60)}min"
    return f"~{segundos / 3600:.1f}h"


class MonitorScreen(Screen):
    def __init__(self, runner: JobRunner) -> None:
        super().__init__()
        self.runner = runner
        self._linhas_mostradas = 0
        self._ultimo_label: str | None = None

    def compose(self) -> ComposeResult:
        yield StatusBar(self.runner)
        yield Static("", id="monitor-progress")
        yield RichLog(id="monitor-output", wrap=True, highlight=False, markup=False)
        yield FileWatchPanel(id="monitor-files")
        with Horizontal(id="monitor-controls"):
            yield Button("Parar", id="btn-parar", variant="error")
            yield Button("Pausar", id="btn-pausar", variant="warning")
            yield Button("Retomar", id="btn-retomar", variant="warning")
            yield Button("Gravar", id="btn-gravar", variant="primary")
            yield Button("Pular", id="btn-pular", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        self.runner.add_listener(self._on_update)
        # a árvore de widgets é recriada a cada remontagem (push/pop de
        # tela), então os contadores de "já mostrado" precisam reiniciar
        # para repovoar o RichLog/painel de arquivos recém-criados
        self._linhas_mostradas = 0
        self._ultimo_label = None
        self._sync_output()
        self._refresh()

    def on_unmount(self) -> None:
        self.runner.remove_listener(self._on_update)

    def on_screen_resume(self) -> None:
        self._sync_output()
        self._refresh()

    def _on_update(self, runner: JobRunner) -> None:
        if not self.is_mounted:
            return
        try:
            # o unmount da tela (ao trocar de tela) é assíncrono e pode
            # remover os widgets filhos entre a checagem acima e a consulta
            # abaixo — NoMatches aqui só significa "chegou tarde", ignora
            self._sync_output()
            self._refresh()
        except NoMatches:
            pass

    def _sync_output(self) -> None:
        log = self.query_one("#monitor-output", RichLog)
        linhas = list(self.runner.output_lines)
        if len(linhas) < self._linhas_mostradas:
            # o buffer foi limpo (começou um job novo, fora de uma sequência)
            log.clear()
            self._linhas_mostradas = 0
        for linha in linhas[self._linhas_mostradas:]:
            log.write(linha)
        self._linhas_mostradas = len(linhas)

        label_atual = self.runner.label
        if label_atual and label_atual != self._ultimo_label:
            self._ultimo_label = label_atual
            self.query_one(FileWatchPanel).set_arquivos(arquivos_para_flags(list(self.runner.argv)))

    def _refresh(self) -> None:
        runner = self.runner
        partes: list[str] = []
        if runner.state == "idle" and runner.last_result is None:
            partes.append("Nenhum comando em execução ainda. Rode algo no Dashboard ou em Comandos.")
        else:
            label = runner.label or (runner.last_result.label if runner.last_result else "?")
            partes.append(f"[b]{label}[/b]")
            if runner.workflow_step:
                i, n, desc = runner.workflow_step
                sufixo = f": {desc}" if desc else ""
                partes.append(f"Passo {i}/{n}{sufixo}")
            if runner.record_progress:
                i, n = runner.record_progress
                eta = f" — ETA estimado {_fmt_eta(runner.eta_seconds())}" if n else ""
                partes.append(f"Registro {i}/{n}{eta}")
            partes.append(f"Tempo decorrido: {int(runner.elapsed())}s")
            if runner.state == "idle" and runner.last_result:
                if runner.last_result.sucesso:
                    partes.append("[green]✅ Concluído com sucesso[/green]")
                else:
                    motivo = f" — {runner.last_result.motivo}" if runner.last_result.motivo else ""
                    partes.append(f"[red]❌ Terminou com erro{motivo}[/red]")
            elif runner.state == "stopping":
                partes.append("[yellow]Parando…[/yellow]")
        self.query_one("#monitor-progress", Static).update("\n".join(partes))

        pausavel = runner.is_pausavel()
        self.query_one("#btn-parar", Button).disabled = not runner.is_busy()
        for bid in ("btn-pausar", "btn-retomar", "btn-gravar", "btn-pular"):
            self.query_one(f"#{bid}", Button).display = pausavel
        if pausavel:
            self.query_one("#btn-pausar", Button).disabled = runner.pausado()
            self.query_one("#btn-retomar", Button).disabled = not runner.pausado()

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        # @work: push_screen_wait() abaixo só pode ser aguardado de dentro
        # de um worker do Textual.
        bid = event.button.id
        if bid == "btn-parar":
            aviso = ""
            if self.runner.is_riscoso_interromper():
                aviso = (
                    "\n\n[yellow]Atenção:[/yellow] esta etapa (solicitação de AIH) não garante "
                    "fechar o Chrome ao ser interrompida à força — pode deixar um processo órfão."
                )
            ok = await self.app.push_screen_wait(
                ConfirmModal(f"Parar a execução atual?{aviso}", confirmar="Parar", cancelar="Cancelar")
            )
            if ok:
                await self.runner.stop()
        elif bid == "btn-pausar":
            self.runner.pausar()
        elif bid == "btn-retomar":
            self.runner.retomar()
        elif bid == "btn-gravar":
            self.runner.gravar()
        elif bid == "btn-pular":
            self.runner.pular()
