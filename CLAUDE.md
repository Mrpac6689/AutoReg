# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AutoReg** is a Brazilian healthcare automation system that automates workflows between two government platforms:
- **SISREG III** (`sisregiii.saude.gov.br`) - National hospital regulation system
- **G-HOSP** (local server, e.g. `http://10.16.9.43:4002`) - Hospital management system

All automation is Selenium WebDriver-based (Chrome), navigating and filling forms programmatically.

## Running the Application

```bash
# Setup (one-time)
conda env create -f environment.yml
conda activate autoreg_env
cp config.ini.example config.ini
# Edit config.ini with real credentials

# Run
python autoreg.py --help           # Show all flags and descriptions
python autoreg.py -interna         # Run full admission workflow
python autoreg.py -alta            # Run full discharge workflow
python autoreg.py -solicita -R     # Run AIH solicitation + record production
python autoreg.py --all            # Full admission + discharge cycle
```

No build step, no test suite, no linter configuration exists in this project.

## Architecture

**Entry point:** `autoreg.py` — CLI coordinator using `argparse`. Maps short flags (e.g. `-ip`) to module functions via a `FUNCOES` dict. Workflow shortcuts (`-interna`, `-alta`, `-solicita`) chain multiple steps sequentially via `executar_funcao()`.

**Module pattern** — every module in `autoreg/` follows the same structure:
1. `ler_credenciais()` reads `config.ini`
2. `get_chrome_options()` configures Selenium Chrome (downloads to `~/AutoReg/`)
3. `webdriver.Chrome()` opens a browser, logs into SISREG or G-HOSP, scrapes/fills data
4. Results are written to `~/AutoReg/*.csv`
5. Browser closed in a `finally` block

**Data flow:** CSV files in `~/AutoReg/` are the inter-module data store — each step's output CSV is the next step's input.

**Shared infrastructure (`autoreg/`):**
- `ler_credenciais.py` — reads `config.ini` sections: `[SISREG]`, `[G-HOSP]`, `[SISREG-REG]`, `[G-HOSP-REG]`, `[EVOLUTION-API]`, `[AUTOREG-API]`
- `chrome_options.py` — shared Chrome/Selenium config
- `logging.py` — logs to `~/AutoReg/autoreg.log` and stdout

## Key Workflows and Their Flags

| Workflow | Flags in sequence |
|----------|------------------|
| Admission | `-eci` → `-ip` |
| Discharge | `-eis` `-eiga` `-maa` `-eaa` |
| AIH Solicitation | `-spa` `-sia` `-ssr` `-snt` |
| AIH Pre-processing | `-iga` `-ign` `-std` |

Individual flags follow the pattern: short flag (e.g. `-ip`) = `--interna-pacientes`. Run `python autoreg.py` with no args to see all functions with descriptions.

## Deployment

Runs locally or inside a **Docker/KASM container** (KasmVNC remote desktop). The `cron-autoreg-docker.sh` script is the cron-facing entry: it copies `docker-entry-script.sh` into the running container and executes it with `DISPLAY=:1` for the Xvnc virtual display.

## Important Files

| File | Purpose |
|------|---------|
| `config.ini` | Runtime credentials — **gitignored**, never commit |
| `config.ini.example` | Template for `config.ini` |
| `autoreg/__init__.py` | Exports all public functions (source of truth for available API) |
| `~/AutoReg/*.csv` | Runtime data files (inter-module exchange, not in repo) |
| `~/AutoReg/autoreg.log` | Runtime log file |
