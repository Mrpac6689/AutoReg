"""Barra de status persistente — mostra o job em andamento (ou o resultado
da última execução) em qualquer tela da TUI."""

from __future__ import annotations

from textual.widgets import Static

from ..runner import JobRunner


class StatusBar(Static):
    """Docada no topo de cada tela; escuta o JobRunner compartilhado."""

    def __init__(self, runner: JobRunner, **kwargs) -> None:
        super().__init__(**kwargs)
        self._runner = runner

    def on_mount(self) -> None:
        self._runner.add_listener(self._on_update)
        self._refresh()
        self.set_interval(1.0, self._refresh)

    def on_unmount(self) -> None:
        self._runner.remove_listener(self._on_update)

    def _on_update(self, runner: JobRunner) -> None:
        self._refresh()

    def _refresh(self) -> None:
        if not self.is_mounted:
            # a tela pode ter sido desmontada entre o evento do runner e a
            # remoção do listener (unmount é assíncrono) — ignora com segurança
            return
        try:
            runner = self._runner
            self.update(runner.resumo_curto())
            self.remove_class("rodando", "ocioso-sucesso", "ocioso-erro")
            if runner.is_busy():
                self.add_class("rodando")
            elif runner.last_result is not None:
                self.add_class("ocioso-sucesso" if runner.last_result.sucesso else "ocioso-erro")
        except Exception:
            pass
