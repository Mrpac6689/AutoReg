"""Leituras read-only de estado do sistema para o painel do Dashboard.
Nunca expõe valores de config.ini — só quais seções existem."""

from __future__ import annotations

import configparser

from .runner import REPO_ROOT, AUTOREG_DATA_DIR

CONFIG_PATH = REPO_ROOT / "config.ini"
RESUMO_PATH = AUTOREG_DATA_DIR / "resumo_execucao.txt"
LOG_PATH = AUTOREG_DATA_DIR / "autoreg.log"

SECOES_ESPERADAS = ("SISREG", "G-HOSP", "SISREG-REG", "G-HOSP-REG", "EVOLUTION-API", "AUTOREG-API", "2CAPTCHA")


def resumo_config() -> str:
    if not CONFIG_PATH.exists():
        return "[red]config.ini não encontrado[/red] — copie config.ini.example e preencha"
    cfg = configparser.ConfigParser()
    try:
        cfg.read(CONFIG_PATH)
    except configparser.Error as exc:
        return f"[red]config.ini inválido: {exc}[/red]"
    presentes = [s for s in SECOES_ESPERADAS if s in cfg]
    ausentes = [s for s in SECOES_ESPERADAS if s not in cfg]
    linha = f"config.ini: [green]{', '.join(presentes) or 'nenhuma seção reconhecida'}[/green]"
    if ausentes:
        linha += f"  [dim](ausentes: {', '.join(ausentes)})[/dim]"
    return linha


def resumo_autoreg_dir() -> str:
    if not AUTOREG_DATA_DIR.exists():
        return "~/AutoReg: [yellow]ainda não existe[/yellow] (será criado na primeira execução)"
    n_csv = len(list(AUTOREG_DATA_DIR.glob("*.csv")))
    tem_log = "sim" if LOG_PATH.exists() else "não"
    return f"~/AutoReg: {n_csv} CSV(s), log presente: {tem_log}"


def resumo_ultima_execucao(max_linhas: int = 12) -> str:
    if not RESUMO_PATH.exists():
        return "[dim]Nenhum resumo_execucao.txt encontrado ainda.[/dim]"
    try:
        texto = RESUMO_PATH.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return f"[red]Erro ao ler resumo_execucao.txt: {exc}[/red]"
    if not texto:
        return "[dim]resumo_execucao.txt está vazio.[/dim]"
    linhas = texto.splitlines()
    if len(linhas) > max_linhas:
        linhas = linhas[-max_linhas:]
        linhas.insert(0, "[dim]… (mostrando só o final)[/dim]")
    return "\n".join(linhas)
