"""Estado do ciclo automático (cron) para a TUI: se está rodando, em que
etapa, ETA, e quando é a próxima rodada.

O cron roda no host (cron-autoreg-docker.sh) e o ciclo dentro do container
(docker-entry-script.sh), enquanto a TUI pode estar em qualquer um dos dois.
O único estado comum é ~/AutoReg, então:
- docker-entry-script.sh grava ciclo_cron.json a cada etapa e o apaga ao sair;
  autoreg.py acrescenta a subetapa (executar_funcao) quando roda no ciclo;
- cron-autoreg-docker.sh grava cron_agenda.txt (linhas do crontab), lido
  quando `crontab -l` não está disponível (TUI dentro do container).
"""

from __future__ import annotations

import json
import re
import statistics
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from .runner import AUTOREG_DATA_DIR

STATUS_PATH = AUTOREG_DATA_DIR / "ciclo_cron.json"
AGENDA_PATH = AUTOREG_DATA_DIR / "cron_agenda.txt"
LOG_PATH = AUTOREG_DATA_DIR / "autoreg.log"

# O crontab do host está nesse fuso; o container roda em UTC.
FUSO = ZoneInfo("America/Rio_Branco")

# Sequência do ciclo: etapas do docker-entry-script.sh e, em cada uma, as
# funções que o atalho correspondente roda em autoreg.py main(). Manter em
# sincronia manualmente com os dois.
CICLO: list[tuple[str, list[str]]] = [
    ("interna", ["extrai_codigos_internacao", "interna_pacientes"]),
    ("aihs", ["internados_ghosp_avancado", "internados_ghosp_nota", "solicita_trata_dados"]),
    ("solicita-auto", ["solicita_pre_aih_auto", "solicita_pre_aih_bridge", "solicita_inf_aih",
                       "solicita_sisreg", "solicita_nota"]),
    ("alta", ["extrai_internados_sisreg", "extrai_internados_ghosp_avancado",
              "motivo_alta_avancado", "executa_alta_avancado"]),
]
SUBETAPAS_POR_FLAG = {f"-{etapa}": subs for etapa, subs in CICLO}

# Sem a TUI saber quanto um job vai levar, avisa se faltar menos que isso.
MARGEM_PADRAO_S = 30 * 60

_LOG_TAIL_BYTES = 8 * 1024 * 1024
_AMOSTRAS = 20
_DURACAO_RE = re.compile(r"<<< Etapa (\w+) concluída \((\d+)s\)")


# -- durações típicas -----------------------------------------------------

_cache_duracoes: dict[str, float] = {}
_cache_lido_em = 0.0


def duracoes_tipicas() -> dict[str, float]:
    """Mediana das últimas execuções de cada função, a partir do final do
    autoreg.log. Recalculada no máximo a cada 10 minutos."""
    global _cache_duracoes, _cache_lido_em
    if time.time() - _cache_lido_em < 600:
        return _cache_duracoes
    _cache_lido_em = time.time()
    amostras: dict[str, list[int]] = {}
    try:
        with open(LOG_PATH, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - _LOG_TAIL_BYTES))
            texto = f.read().decode("utf-8", errors="replace")
    except OSError:
        return _cache_duracoes
    for m in _DURACAO_RE.finditer(texto):
        amostras.setdefault(m.group(1), []).append(int(m.group(2)))
    _cache_duracoes = {
        nome: statistics.median(vals[-_AMOSTRAS:]) for nome, vals in amostras.items()
    }
    return _cache_duracoes


def duracao_estimada(flag: str) -> Optional[float]:
    """Duração típica de um atalho do ciclo (-interna, -aihs, ...), ou None."""
    subs = SUBETAPAS_POR_FLAG.get(flag)
    if not subs:
        return None
    dur = duracoes_tipicas()
    if not all(s in dur for s in subs):
        return None
    return sum(dur[s] for s in subs)


# -- ciclo em andamento ---------------------------------------------------

@dataclass
class CicloAtivo:
    inicio: float
    etapa: str
    etapa_n: int
    etapa_total: int
    etapa_inicio: float
    subetapa: Optional[str]
    subetapa_inicio: Optional[float]

    def restante_s(self) -> Optional[float]:
        """Estimativa do tempo até o fim do ciclo, ou None sem histórico."""
        dur = duracoes_tipicas()
        nomes = [e for e, _ in CICLO]
        if self.etapa not in nomes:
            return None
        restante = 0.0
        agora = time.time()
        for etapa, subs in CICLO[nomes.index(self.etapa):]:
            for sub in subs:
                if sub not in dur:
                    return None
                restante += dur[sub]
            if etapa == self.etapa:
                # desconta o que já passou nesta etapa: subetapas concluídas
                # inteiras e o tempo decorrido na atual
                if self.subetapa in subs:
                    i = subs.index(self.subetapa)
                    restante -= sum(dur[s] for s in subs[:i])
                    restante -= min(dur[self.subetapa], agora - (self.subetapa_inicio or agora))
                else:
                    restante -= min(sum(dur[s] for s in subs), agora - self.etapa_inicio)
        return max(restante, 0.0)


def ciclo_ativo() -> Optional[CicloAtivo]:
    try:
        dados = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        return CicloAtivo(
            inicio=float(dados["inicio"]),
            etapa=str(dados["etapa"]),
            etapa_n=int(dados["etapa_n"]),
            etapa_total=int(dados["etapa_total"]),
            etapa_inicio=float(dados["etapa_inicio"]),
            subetapa=dados.get("subetapa"),
            subetapa_inicio=dados.get("subetapa_inicio"),
        )
    except (OSError, ValueError, KeyError, TypeError):
        return None


# -- agenda do cron -------------------------------------------------------

def _expandir(campo: str, minimo: int, maximo: int) -> set[int]:
    """Expande um campo de cron simples (N, a,b, a-b, */k, a-b/k, *)."""
    valores: set[int] = set()
    for parte in campo.split(","):
        passo = 1
        if "/" in parte:
            parte, p = parte.split("/", 1)
            passo = int(p)
        if parte == "*":
            ini, fim = minimo, maximo
        elif "-" in parte:
            a, b = parte.split("-", 1)
            ini, fim = int(a), int(b)
        else:
            ini = fim = int(parte)
        valores.update(range(ini, fim + 1, passo))
    return valores


def _linhas_agenda() -> list[str]:
    try:
        saida = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5).stdout
        linhas = [l for l in saida.splitlines() if "cron-autoreg-docker.sh" in l]
        if linhas:
            return linhas
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        return AGENDA_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


_cache_horarios: Optional[list[tuple[int, int]]] = None
_cache_horarios_em = 0.0


def horarios_cron() -> list[tuple[int, int]]:
    """(hora, minuto) de cada rodada diária do ciclo. Ignora os campos de
    dia (todas as entradas atuais são diárias). Lista vazia se desconhecida."""
    global _cache_horarios, _cache_horarios_em
    if _cache_horarios is not None and time.time() - _cache_horarios_em < 600:
        return _cache_horarios
    horarios: set[tuple[int, int]] = set()
    for linha in _linhas_agenda():
        campos = linha.split()
        if len(campos) < 5 or linha.lstrip().startswith("#"):
            continue
        try:
            for h in _expandir(campos[1], 0, 23):
                for m in _expandir(campos[0], 0, 59):
                    horarios.add((h, m))
        except ValueError:
            continue
    _cache_horarios = sorted(horarios)
    _cache_horarios_em = time.time()
    return _cache_horarios


def proxima_rodada() -> Optional[datetime]:
    horarios = horarios_cron()
    if not horarios:
        return None
    agora = datetime.now(FUSO)
    for dias in (0, 1):
        dia = (agora + timedelta(days=dias)).date()
        for h, m in horarios:
            quando = datetime(dia.year, dia.month, dia.day, h, m, tzinfo=FUSO)
            if quando > agora:
                return quando
    return None


# -- textos para a TUI ----------------------------------------------------

def fmt_duracao(segundos: float) -> str:
    minutos = int(round(segundos / 60))
    if minutos < 60:
        return f"{minutos} min"
    return f"{minutos // 60}h{minutos % 60:02d}"


def resumo_curto() -> str:
    """Uma linha para a barra de status."""
    ciclo = ciclo_ativo()
    if ciclo:
        partes = [f"⏱ Cron rodando: {ciclo.etapa} ({ciclo.etapa_n}/{ciclo.etapa_total})"]
        if ciclo.subetapa:
            partes[0] += f" › {ciclo.subetapa}"
        partes.append(f"há {fmt_duracao(time.time() - ciclo.inicio)}")
        restante = ciclo.restante_s()
        if restante is not None:
            fim = datetime.fromtimestamp(time.time() + restante, FUSO)
            partes.append(f"término previsto ~{fim:%H:%M} (≈{fmt_duracao(restante)})")
        return " · ".join(partes)
    proxima = proxima_rodada()
    if proxima is None:
        return "Cron: ocioso · agenda desconhecida"
    falta = (proxima - datetime.now(FUSO)).total_seconds()
    return f"Cron: ocioso · próxima rodada {proxima:%H:%M} (em {fmt_duracao(falta)})"


def aviso_conflito(flag: Optional[str]) -> Optional[str]:
    """Mensagem de confirmação se iniciar `flag` agora pode colidir com o
    ciclo automático; None se não há conflito."""
    ciclo = ciclo_ativo()
    if ciclo:
        restante = ciclo.restante_s()
        prev = f" (término previsto em ≈{fmt_duracao(restante)})" if restante is not None else ""
        return (
            f"O ciclo automático está rodando agora: {ciclo.etapa}"
            f"{' › ' + ciclo.subetapa if ciclo.subetapa else ''}{prev}.\n"
            "Rodar em paralelo usa as mesmas credenciais e os mesmos CSVs de ~/AutoReg.\n"
            "Iniciar mesmo assim?"
        )
    proxima = proxima_rodada()
    if proxima is None:
        return None
    falta = (proxima - datetime.now(FUSO)).total_seconds()
    estimada = duracao_estimada(flag) if flag else None
    if estimada is not None:
        if estimada < falta:
            return None
        detalhe = f"{flag} costuma levar ≈{fmt_duracao(estimada)}, então os dois rodariam ao mesmo tempo."
    else:
        if falta >= MARGEM_PADRAO_S:
            return None
        detalhe = "Um job iniciado agora pode ainda estar rodando quando ele começar."
    return (
        f"O próximo ciclo automático começa às {proxima:%H:%M} (em {fmt_duracao(falta)}).\n"
        f"{detalhe}\nIniciar mesmo assim?"
    )
