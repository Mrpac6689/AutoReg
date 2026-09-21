"""Modais reutilizáveis: confirmação, prompt numérico, prompt de caminho."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class ConfirmModal(ModalScreen[bool]):
    """Pede confirmação; retorna True/False."""

    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(self, mensagem: str, confirmar: str = "Confirmar", cancelar: str = "Cancelar") -> None:
        super().__init__()
        self._mensagem = mensagem
        self._confirmar = confirmar
        self._cancelar = cancelar

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label(self._mensagem, id="modal-msg")
            with Horizontal(id="modal-botoes"):
                yield Button(self._confirmar, id="ok", variant="warning")
                yield Button(self._cancelar, id="cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "ok")

    def action_cancelar(self) -> None:
        self.dismiss(False)


class IntPromptModal(ModalScreen[int | None]):
    """Pede um número inteiro >= 1; retorna None se cancelado/inválido."""

    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(self, mensagem: str, padrao: int = 1) -> None:
        super().__init__()
        self._mensagem = mensagem
        self._padrao = padrao

    def action_cancelar(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label(self._mensagem, id="modal-msg")
            yield Input(value=str(self._padrao), id="valor")
            with Horizontal(id="modal-botoes"):
                yield Button("OK", id="ok", variant="primary")
                yield Button("Cancelar", id="cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._confirmar()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self._confirmar()
        else:
            self.dismiss(None)

    def _confirmar(self) -> None:
        valor = self.query_one("#valor", Input).value.strip()
        try:
            n = int(valor)
            if n < 1:
                raise ValueError
        except ValueError:
            self.query_one("#modal-msg", Label).update(
                f"{self._mensagem}\n[red]Digite um número inteiro >= 1.[/red]"
            )
            return
        self.dismiss(n)


class PathPromptModal(ModalScreen[str | None]):
    """Pede um caminho de arquivo opcional. Retorna "" (usa o padrão do
    autoreg.py), o caminho digitado, ou None se cancelado."""

    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def __init__(self, mensagem: str) -> None:
        super().__init__()
        self._mensagem = mensagem

    def action_cancelar(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-box"):
            yield Label(self._mensagem, id="modal-msg")
            yield Input(placeholder="deixe em branco para usar o caminho padrão", id="valor")
            with Horizontal(id="modal-botoes"):
                yield Button("OK", id="ok", variant="primary")
                yield Button("Cancelar", id="cancel")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(self.query_one("#valor", Input).value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.dismiss(self.query_one("#valor", Input).value.strip())
        else:
            self.dismiss(None)
