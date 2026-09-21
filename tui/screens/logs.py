"""Visualizador de logs: autoreg.log (tail + filtro), saída bruta do último
job rodado pela TUI, e resumo_execucao.txt."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Input, RichLog, Select, Static, TabbedContent, TabPane

from .. import sysinfo
from ..runner import JobRunner
from ..widgets.status_bar import StatusBar

NIVEIS = ["TODOS", "INFO", "WARNING", "ERROR"]


def _tail_lines(path: Path, n: int = 500) -> list[str]:
    if not path.exists():
        return []
    try:
        with path.open("rb") as fh:
            fh.seek(0, 2)
            tamanho = fh.tell()
            bloco = 4096
            dados = b""
            pos = tamanho
            while pos > 0 and dados.count(b"\n") <= n:
                ler = min(bloco, pos)
                pos -= ler
                fh.seek(pos)
                dados = fh.read(ler) + dados
        texto = dados.decode("utf-8", errors="replace")
        return texto.splitlines()[-n:]
    except OSError:
        return []


class LogsScreen(Screen):
    def __init__(self, runner: JobRunner) -> None:
        super().__init__()
        self.runner = runner
        self._log_mtime: float | None = None
        self._linhas_saida_job = 0

    def compose(self) -> ComposeResult:
        yield StatusBar(self.runner)
        with TabbedContent():
            with TabPane("autoreg.log", id="tab-arquivo"):
                with Horizontal(id="log-filtros"):
                    yield Input(placeholder="Filtrar texto…", id="log-filtro-texto")
                    yield Select(
                        [(n, n) for n in NIVEIS], value="TODOS", id="log-filtro-nivel", allow_blank=False
                    )
                yield RichLog(id="log-arquivo", wrap=True, highlight=False, markup=False)
            with TabPane("Saída do último job", id="tab-saida"):
                yield RichLog(id="log-saida", wrap=True, highlight=False, markup=False)
            with TabPane("Resumo da última execução", id="tab-resumo"):
                with VerticalScroll():
                    yield Static("", id="log-resumo")
        yield Footer()

    def on_mount(self) -> None:
        self.runner.add_listener(self._on_runner_update)
        # a árvore de widgets é recriada a cada remontagem (push/pop de
        # tela), então o contador de "já mostrado" precisa reiniciar para
        # repovoar o RichLog recém-criado
        self._linhas_saida_job = 0
        self._recarrega_arquivo(force=True)
        self._recarrega_saida()
        self._recarrega_resumo()
        self.set_interval(2.0, self._poll)

    def on_unmount(self) -> None:
        self.runner.remove_listener(self._on_runner_update)

    def on_screen_resume(self) -> None:
        self._poll()
        self._recarrega_saida()

    def _on_runner_update(self, runner: JobRunner) -> None:
        if not self.is_mounted:
            return
        try:
            # o unmount da tela é assíncrono e pode remover os widgets
            # filhos entre a checagem acima e a consulta abaixo — NoMatches
            # aqui só significa "chegou tarde", ignora
            self._recarrega_saida()
        except NoMatches:
            pass

    def _poll(self) -> None:
        if not self.is_mounted:
            return
        try:
            self._recarrega_arquivo()
            self._recarrega_resumo()
        except NoMatches:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "log-filtro-texto":
            self._recarrega_arquivo(force=True)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "log-filtro-nivel":
            self._recarrega_arquivo(force=True)

    def _recarrega_arquivo(self, force: bool = False) -> None:
        path = sysinfo.LOG_PATH
        try:
            mtime = path.stat().st_mtime if path.exists() else None
        except OSError:
            mtime = None
        if not force and mtime == self._log_mtime:
            return
        self._log_mtime = mtime
        texto_filtro = self.query_one("#log-filtro-texto", Input).value.strip().lower()
        nivel = self.query_one("#log-filtro-nivel", Select).value
        log = self.query_one("#log-arquivo", RichLog)
        log.clear()
        for linha in _tail_lines(path, 500):
            if nivel != "TODOS" and f" - {nivel} - " not in linha:
                continue
            if texto_filtro and texto_filtro not in linha.lower():
                continue
            log.write(linha)

    def _recarrega_saida(self) -> None:
        log = self.query_one("#log-saida", RichLog)
        linhas = list(self.runner.output_lines)
        if len(linhas) < self._linhas_saida_job:
            log.clear()
            self._linhas_saida_job = 0
        for linha in linhas[self._linhas_saida_job:]:
            log.write(linha)
        self._linhas_saida_job = len(linhas)

    def _recarrega_resumo(self) -> None:
        self.query_one("#log-resumo", Static).update(sysinfo.resumo_ultima_execucao(max_linhas=300))
