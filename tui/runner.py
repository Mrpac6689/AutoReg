"""Execução de comandos do AutoReg como subprocesso, com streaming de saída
e parsing best-effort de progresso/ETA.

A TUI nunca importa os módulos de `autoreg/` diretamente nem chama
`FUNCOES[...]['func']()` em processo — cada comando roda como
`python autoreg.py <flags...>` em um subprocesso próprio (ver plano:
isola crashes, evita o comportamento de logging.basicConfig
"primeiro-import-vence", e permite matar o job sem derrubar a TUI).
"""

from __future__ import annotations

import asyncio
import os
import re
import signal
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOREG_PY = REPO_ROOT / "autoreg.py"
AUTOREG_DATA_DIR = Path.home() / "AutoReg"

MAX_OUTPUT_LINES = 4000

# "[2/4] 🚀 Executando: Verifica altas e extrai motivos" (passo do workflow,
# impresso por executar_funcao/main() sempre no início da linha)
_WORKFLOW_STEP_RE = re.compile(r"^\[(\d+)/(\d+)\]\s*(?:🚀\s*Executando:\s*(?P<desc>.+))?")

# "🔍 [7/23] Verificando RA: ..." (progresso de registro com total explícito)
_RECORD_RE = re.compile(r"\[(\d+)\s*/\s*(\d+)\]")

# "🚀 [12] Processando Solicitação: ..." (só o índice, sem total — usado por
# executa_alta_avancado.py; o total, quando existe, vem de _TOTAL_HINT_RE)
_RECORD_INDEX_ONLY_RE = re.compile(r"\[(\d+)\](?!\s*/)")

# "📋 Encontradas 23 altas para processar." — usado como pista de total antes
# do primeiro "[i/N]" aparecer.
_TOTAL_HINT_RE = re.compile(r"Encontrad[ao]s?\s+(\d+)")

PAUSE_FLAG = AUTOREG_DATA_DIR / "pause.flag"
GRAVA_FLAG = AUTOREG_DATA_DIR / "grava.flag"
PULA_FLAG = AUTOREG_DATA_DIR / "pula.flag"


@dataclass
class JobResult:
    label: str
    argv: list[str]
    sucesso: bool
    duracao_s: float
    motivo: str = ""


class JobRunner:
    """Estado + orquestração de execução de um comando por vez."""

    def __init__(self) -> None:
        self.state: str = "idle"  # idle | running | stopping
        self.label: Optional[str] = None
        self.argv: list[str] = []
        self.workflow_step: Optional[tuple[int, int, str]] = None  # (i, n, desc)
        self.record_progress: Optional[tuple[int, int]] = None  # (i, total)
        self._progress_history: deque[tuple[float, int]] = deque(maxlen=50)
        self.output_lines: deque[str] = deque(maxlen=MAX_OUTPUT_LINES)
        self.start_time: Optional[float] = None
        self.step_start_time: Optional[float] = None
        self.error_lines: list[str] = []
        self.last_result: Optional[JobResult] = None
        self.history: list[JobResult] = []

        self._proc: Optional[asyncio.subprocess.Process] = None
        self._task: Optional[asyncio.Task] = None
        self._listeners: list[Callable[["JobRunner"], None]] = []
        self._cancel_requested = False

    # -- observadores ------------------------------------------------------

    def add_listener(self, cb: Callable[["JobRunner"], None]) -> None:
        self._listeners.append(cb)

    def remove_listener(self, cb: Callable[["JobRunner"], None]) -> None:
        if cb in self._listeners:
            self._listeners.remove(cb)

    def _notify(self) -> None:
        for cb in list(self._listeners):
            try:
                cb(self)
            except Exception:
                pass

    # -- estado derivado -----------------------------------------------

    def is_busy(self) -> bool:
        return self.state in ("running", "stopping")

    def is_riscoso_interromper(self) -> bool:
        from .catalogo import RISCO_CHROME_ORFAO

        return any(f in RISCO_CHROME_ORFAO for f in self.argv)

    def is_pausavel(self) -> bool:
        return self.is_riscoso_interromper() and self.state == "running"

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.monotonic() - self.start_time

    def eta_seconds(self) -> Optional[float]:
        if not self.record_progress:
            return None
        atual, total = self.record_progress
        if total <= 0 or atual >= total or len(self._progress_history) < 2:
            return None
        (t0, i0) = self._progress_history[0]
        (t1, i1) = self._progress_history[-1]
        if i1 <= i0 or t1 <= t0:
            return None
        taxa = (i1 - i0) / (t1 - t0)  # registros por segundo
        if taxa <= 0:
            return None
        return (total - atual) / taxa

    def resumo_curto(self) -> str:
        if self.state == "idle":
            if self.last_result:
                icone = "✅" if self.last_result.sucesso else "❌"
                return f"Ocioso — última execução: {icone} {self.last_result.label}"
            return "Ocioso"
        partes = [f"▶ {self.label}"]
        if self.workflow_step:
            i, n, _desc = self.workflow_step
            partes.append(f"passo {i}/{n}")
        if self.record_progress:
            i, n = self.record_progress
            partes.append(f"registro {i}/{n}")
        partes.append(f"{int(self.elapsed())}s")
        if self.state == "stopping":
            partes.append("(parando…)")
        return " · ".join(partes)

    # -- controle de flags (pausa/retoma/pula) ------------------------

    def pausado(self) -> bool:
        return PAUSE_FLAG.exists()

    def pausar(self) -> None:
        AUTOREG_DATA_DIR.mkdir(exist_ok=True)
        PAUSE_FLAG.touch()
        self._notify()

    def retomar(self) -> None:
        PAUSE_FLAG.unlink(missing_ok=True)
        self._notify()

    def gravar(self) -> None:
        AUTOREG_DATA_DIR.mkdir(exist_ok=True)
        GRAVA_FLAG.touch()
        self._notify()

    def pular(self) -> None:
        AUTOREG_DATA_DIR.mkdir(exist_ok=True)
        PULA_FLAG.touch()
        self._notify()

    # -- execução ---------------------------------------------------------

    def start(self, argv: list[str], label: str) -> None:
        """Dispara um único comando (`python autoreg.py <argv>`)."""
        if self.is_busy():
            return
        self._task = asyncio.create_task(self._run_single(argv, label))

    def start_sequence(self, jobs: list[tuple[list[str], str]]) -> None:
        """Dispara vários comandos em sequência (ex.: Ciclo Completo),
        parando no primeiro que falhar — mesma semântica de
        `executar_todas()`, sem o input() bloqueante."""
        if self.is_busy():
            return
        self._task = asyncio.create_task(self._run_sequence(jobs))

    async def _run_sequence(self, jobs: list[tuple[list[str], str]]) -> None:
        for argv, label in jobs:
            ok = await self._run_single(argv, label, is_sequence_member=True)
            if not ok or self._cancel_requested:
                break
        self._cancel_requested = False

    async def _run_single(
        self, argv: list[str], label: str, *, is_sequence_member: bool = False
    ) -> bool:
        self.state = "running"
        self.label = label
        self.argv = argv
        self.workflow_step = None
        self.record_progress = None
        self._progress_history.clear()
        self.error_lines = []
        if not is_sequence_member:
            self.output_lines.clear()
        self.start_time = time.monotonic()
        self.step_start_time = self.start_time
        self._notify()

        AUTOREG_DATA_DIR.mkdir(exist_ok=True)
        for flag in (PAUSE_FLAG, GRAVA_FLAG, PULA_FLAG):
            flag.unlink(missing_ok=True)

        try:
            kwargs = dict(
                cwd=str(REPO_ROOT),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                stdin=asyncio.subprocess.DEVNULL,
            )
            if os.name == "posix":
                kwargs["start_new_session"] = True
            # "-u": sem isso, o print() do processo filho fica bufferizado em
            # bloco (stdout não é um tty) e a saída só chegaria de uma vez,
            # no final — nada de streaming ao vivo nem parsing de progresso.
            self._proc = await asyncio.create_subprocess_exec(
                sys.executable, "-u", str(AUTOREG_PY), *argv, **kwargs
            )
        except Exception as exc:  # ex.: autoreg.py sumiu, python inválido
            self._append_line(f"❌ Falha ao iniciar processo: {exc}")
            sucesso = False
        else:
            assert self._proc.stdout is not None
            while True:
                raw = await self._proc.stdout.readline()
                if not raw:
                    break
                linha = raw.decode("utf-8", errors="replace").rstrip("\n")
                if linha:
                    self._processa_linha(linha)
            returncode = await self._proc.wait()
            sucesso = returncode == 0 and not self.error_lines
        self._proc = None

        duracao = time.monotonic() - self.start_time
        motivo = ""
        if self.state == "stopping":
            sucesso = False
            motivo = "interrompido pelo usuário"
        elif not sucesso and self.error_lines:
            motivo = self.error_lines[-1]

        resultado = JobResult(label=label, argv=argv, sucesso=sucesso, duracao_s=duracao, motivo=motivo)
        self.last_result = resultado
        self.history.append(resultado)
        self.state = "idle"
        self.label = None
        self._notify()
        return sucesso

    def _append_line(self, linha: str) -> None:
        self.output_lines.append(linha)
        if "❌" in linha:
            self.error_lines.append(linha)

    def _processa_linha(self, linha: str) -> None:
        self._append_line(linha)

        if linha.startswith("["):
            m = _WORKFLOW_STEP_RE.match(linha)
            if m:
                i, n = int(m.group(1)), int(m.group(2))
                desc = m.group("desc") or (self.workflow_step[2] if self.workflow_step else "")
                self.workflow_step = (i, n, desc)
                self.record_progress = None
                self._progress_history.clear()
                self.step_start_time = time.monotonic()
        else:
            m = _RECORD_RE.search(linha)
            if m:
                i, n = int(m.group(1)), int(m.group(2))
                self.record_progress = (i, n)
                self._progress_history.append((time.monotonic(), i))
            elif self.record_progress is not None:
                m2 = _RECORD_INDEX_ONLY_RE.search(linha)
                if m2:
                    i = int(m2.group(1))
                    _, n = self.record_progress
                    self.record_progress = (i, n)
                    self._progress_history.append((time.monotonic(), i))
            else:
                hint = _TOTAL_HINT_RE.search(linha)
                if hint:
                    self.record_progress = (0, int(hint.group(1)))

        self._notify()

    async def stop(self) -> None:
        if not self._proc or self.state != "running":
            return
        self.state = "stopping"
        self._cancel_requested = True
        self._notify()
        proc = self._proc
        try:
            if os.name == "posix":
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
            else:
                proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=8)
            except asyncio.TimeoutError:
                if os.name == "posix":
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    proc.kill()
        except ProcessLookupError:
            pass
