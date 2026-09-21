"""Painel de arquivos CSV afetados pelo comando em execução — polling
simples de tamanho/mtime/contagem de linhas em `~/AutoReg/`."""

from __future__ import annotations

import time
from pathlib import Path

from textual.widgets import Static

AUTOREG_DATA_DIR = Path.home() / "AutoReg"


def _formata_ha(segundos: float) -> str:
    if segundos < 60:
        return f"há {int(segundos)}s"
    if segundos < 3600:
        return f"há {int(segundos // 60)}min"
    return f"há {int(segundos // 3600)}h"


def _conta_linhas(caminho: Path) -> int | None:
    try:
        with caminho.open("rb") as fh:
            return sum(1 for _ in fh) - 1  # desconta cabeçalho
    except OSError:
        return None


class FileWatchPanel(Static):
    """Mostra estado de um conjunto fixo de arquivos de `~/AutoReg`."""

    def __init__(self, nomes: tuple[str, ...] = (), **kwargs) -> None:
        super().__init__(**kwargs)
        self._nomes = nomes

    def set_arquivos(self, nomes: tuple[str, ...]) -> None:
        self._nomes = nomes
        self._refresh()

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(2.0, self._refresh)

    def _refresh(self) -> None:
        if not self._nomes:
            self.update("[i]Nenhum arquivo mapeado para este comando.[/i]")
            return
        linhas = ["[b]Arquivos afetados (~/AutoReg):[/b]"]
        agora = time.time()
        for nome in self._nomes:
            caminho = AUTOREG_DATA_DIR / nome
            if not caminho.exists():
                linhas.append(f"  • {nome} — [dim]ainda não criado[/dim]")
                continue
            stat = caminho.stat()
            tam_kb = stat.st_size / 1024
            n_linhas = _conta_linhas(caminho)
            sufixo = f", {n_linhas} linha(s)" if n_linhas is not None and n_linhas >= 0 else ""
            linhas.append(
                f"  • {nome} — {tam_kb:.1f} KB{sufixo}, modificado {_formata_ha(agora - stat.st_mtime)}"
            )
        self.update("\n".join(linhas))
