"""App principal da TUI do AutoReg — junta as telas e o JobRunner
compartilhado, e define a navegação global (teclado + clique)."""

from __future__ import annotations

from textual import work
from textual.app import App

from .runner import JobRunner
from .screens.ajuda import AjudaScreen
from .screens.comandos import ComandosScreen
from .screens.dashboard import DashboardScreen
from .screens.logs import LogsScreen
from .screens.modals import ConfirmModal
from .screens.monitor import MonitorScreen


class AutoRegApp(App):
    CSS_PATH = "theme.tcss"
    TITLE = "AutoReg"

    BINDINGS = [
        ("q", "quit_app", "Sair"),
        ("d", "goto_dashboard", "Início"),
        ("c", "goto_comandos", "Comandos"),
        ("m", "goto_monitor", "Monitor"),
        ("l", "goto_logs", "Logs"),
        ("question_mark", "goto_ajuda", "Ajuda"),
        ("escape", "goto_dashboard", "Voltar"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.runner = JobRunner()

    def on_mount(self) -> None:
        self.install_screen(DashboardScreen(self.runner), name="dashboard")
        self.install_screen(ComandosScreen(self.runner), name="comandos")
        self.install_screen(MonitorScreen(self.runner), name="monitor")
        self.install_screen(LogsScreen(self.runner), name="logs")
        self.install_screen(AjudaScreen(self.runner), name="ajuda")
        self.push_screen("dashboard")

    def goto(self, name: str) -> None:
        """Colapsa a pilha de telas de volta ao dashboard e, se necessário,
        empilha a tela de destino — mantém a navegação em no máximo 2
        níveis (dashboard + tela atual). O Textual já mantém uma tela-base
        implícita sob a nossa "dashboard", por isso o alvo do "colapso" é
        profundidade 2 (base + dashboard), não 1."""
        while len(self.screen_stack) > 2:
            self.pop_screen()
        if name != "dashboard":
            self.push_screen(name)

    def action_goto_dashboard(self) -> None:
        self.goto("dashboard")

    def action_goto_comandos(self) -> None:
        self.goto("comandos")

    def action_goto_monitor(self) -> None:
        self.goto("monitor")

    def action_goto_logs(self) -> None:
        self.goto("logs")

    def action_goto_ajuda(self) -> None:
        self.goto("ajuda")

    async def confirmar_e_sair(self) -> None:
        """Lógica de saída compartilhada entre o binding 'q' e o botão Sair
        do Dashboard. Não é decorada com @work — quem chama precisa estar
        rodando dentro de um worker (push_screen_wait exige isso)."""
        if self.runner.is_busy():
            confirmar = await self.push_screen_wait(
                ConfirmModal(
                    "Um job está em execução. Sair mesmo assim?\n"
                    "O processo em segundo plano será finalizado.",
                    confirmar="Sair",
                    cancelar="Cancelar",
                )
            )
            if not confirmar:
                return
            await self.runner.stop()
        self.exit()

    @work
    async def action_quit_app(self) -> None:
        # @work: push_screen_wait() dentro de confirmar_e_sair() só pode
        # ser aguardado de dentro de um worker do Textual.
        await self.confirmar_e_sair()


def run() -> None:
    AutoRegApp().run()
