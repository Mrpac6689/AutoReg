#!/usr/bin/env python3
"""Entry point da TUI do AutoReg.

Uso:
    python tui_app.py

Wrapper de interface por cima de `autoreg.py` — não substitui o CLI, cada
ação da TUI dispara `python autoreg.py <flags>` como subprocesso.
"""

from tui.app import run

if __name__ == "__main__":
    run()
