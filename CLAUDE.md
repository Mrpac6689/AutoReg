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
- `ler_credenciais.py` — reads `config.ini` sections:
  - `[SISREG]` / `[SISREG-REG]` — primary and regulatory SISREG accounts
  - `[G-HOSP]` / `[G-HOSP-REG]` — primary and regulatory G-HOSP accounts
  - `[EVOLUTION-API]` — WhatsApp notification integration
  - `[AUTOREG-API]` — production tracking API (used by `-R` flag via `producao_relatorio.py`)
  - `[2CAPTCHA]` / `[KASM]` — CAPTCHA solving and remote desktop viewer
- `chrome_options.py` — shared Chrome/Selenium config
- `logging.py` — logs to `~/AutoReg/autoreg.log` and stdout
- `detecta_capchta.py` — centralizes CAPTCHA detection for all SISREG modules, supports automatic resolution via 2Captcha
- `resolvedor_captcha.py` — handles automatic CAPTCHA solving using 2Captcha API (reCAPTCHA v2/v3, hCaptcha, image captchas)

**Legacy backup files** — `autoreg/*bkp.py` (e.g. `executa_altabkp.py`, `trata_restosbkp.py`, `trata_duplicadosbkp.py`) are old versions kept for reference. They are not imported or active — prefer the non-`bkp` versions.

## Key Workflows and Their Flags

| Shortcut | Flags in sequence | Description |
|----------|------------------|-------------|
| `-interna` | `-eci` → `-ip` | Full admission cycle |
| `-alta` | `-eis` → `-eiga` → `-maa` → `-eaa` | Full discharge cycle |
| `-solicita` | `-spa` → `-sia` → `-ssr` → `-snt` | AIH solicitation |
| `-aihs` | `-iga` → `-ign` → `-std` | AIH pre-processing (GHOSP notes → SISREG data) |
| `--all` | `-interna` then `-alta` | Complete workflow (prompts for repetition count) |

Append `-R` to any shortcut to register production results in AUTOREG-API after completion (e.g. `python autoreg.py -solicita -R`).

Individual flags follow the pattern: short flag (e.g. `-ip`) = `--interna-pacientes`. Run `python autoreg.py` with no args to see all functions with descriptions.

## Deployment

Runs locally or inside a **Docker/KASM container** (KasmVNC remote desktop). The `cron-autoreg-docker.sh` script is the cron-facing entry: it copies `docker-entry-script.sh` into the running container and executes it with `DISPLAY=:1` for the Xvnc virtual display.

## CAPTCHA Handling

AutoReg includes automatic CAPTCHA detection and resolution:

- **Detection**: All SISREG modules call `detecta_captcha(driver)` which monitors for CAPTCHA challenges
- **Automatic Resolution**: When `[2CAPTCHA] enabled = true` in config.ini, uses 2Captcha API to solve automatically
- **Manual Fallback**: If automatic fails or disabled, pauses and waits for manual resolution (local or KASM viewer)
- **Supported Types**: reCAPTCHA v2/v3, hCaptcha, simple image CAPTCHAs
- **Documentation**: See `CAPTCHA_2CAPTCHA.md` and `INSTALACAO_2CAPTCHA.md`
- **Testing**: Run `python test_2captcha_integration.py` to verify setup

## Important Files

| File | Purpose |
|------|---------|
| `config.ini` | Runtime credentials — **gitignored**, never commit |
| `config.ini.example` | Template for `config.ini` (includes `[2CAPTCHA]` section) |
| `autoreg/__init__.py` | Exports all public functions (source of truth for available API) |
| `~/AutoReg/*.csv` | Runtime data files (inter-module exchange, not in repo) |
| `~/AutoReg/autoreg.log` | Runtime log file |
| `CAPTCHA_2CAPTCHA.md` | Complete 2Captcha integration documentation |
| `INSTALACAO_2CAPTCHA.md` | Step-by-step installation guide for 2Captcha |
| `test_2captcha_integration.py` | Test script to validate 2Captcha setup |
