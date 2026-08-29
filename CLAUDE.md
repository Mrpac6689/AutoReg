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
python3 -m venv venv
source venv/bin/activate  # Linux/macOS (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
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
- `relatorio_execucao.py` — builds per-module (interna/alta/solicitação) execution summaries from final CSV state, accumulates them in `~/AutoReg/resumo_execucao.txt`, and sends the consolidated summary via WhatsApp (Evolution API, `config.ini` `[EVOLUTION-API]`). Called from `autoreg.py`'s `-interna`/`-alta`/`-solicita-auto` blocks and from `docker-entry-script.sh` (`python3 -m autoreg.relatorio_execucao`) at the end of the cron cycle
- `sessao_sisreg.py` — centralized SISREG III login (`login_sisreg`) and session-expiry recovery (`sessao_expirada`, `garantir_sessao_sisreg`, `ControleSessao`/`SessaoSisregAbortada`). Used by `executa_alta_avancado.py`, `interna_pacientes.py`, `trata_duplicados.py`, `extrai_internacoes_duplicadas.py`, `extrai_codigos_internacao.py`
- `internacao_sisreg.py` — `internar_ficha_sisreg()`, the single implementation of "internar uma ficha no SISREG" (navigate, `configFicha`, date extraction, professional selection, popups, "Erro de Sistema" check). Shared by `-ip` (`interna_pacientes.py`) and the final step of `-td` (`trata_duplicados.py`) so the two don't drift into divergent, differently-broken copies

**Legacy backup files** — `autoreg/*bkp.py` (e.g. `executa_altabkp.py`, `trata_restosbkp.py`, `trata_duplicadosbkp.py`) are old versions kept for reference. They are not imported or active — prefer the non-`bkp` versions.

**Filename typo** — `autoreg/detecta_capchta.py` (note "capchta", not "captcha") is the canonical file. All imports use this spelling; do not rename it.

## Key Workflows and Their Flags

| Shortcut | Flags in sequence | Description |
|----------|------------------|-------------|
| `-interna` | `-eci` → `-ip` | Full admission cycle |
| `-alta` | `-eis` → `-eiga` → `-maa` → `-eaa` | Full discharge cycle |
| `-solicita` | `-spa` → `-sia` → `-ssr` → `-snt` | AIH solicitation |
| `-solicita-auto` | `-spaa` → `-spb` → `-sia` → `-ssr` → `-snt` | AIH solicitation with no human interaction (cron-safe): `-spb` replaces `-spa`, dropping any record `-spaa` couldn't auto-approve |
| `-aihs` | `-iga` → `-ign` → `-std` | AIH pre-processing (GHOSP notes → SISREG data) |
| `--all` | `-interna` then `-alta` | Complete workflow (prompts for repetition count) |
| *(no shortcut)* | `-eac` → `-eae` → `-eas` → `-ear` | Ambulatorial exam solicitation cycle (consult → extract → solicit → report) |
| *(no shortcut)* | `-pra` / `-pad` / `-pag` | Ambulatorial production extraction (SISREG); run individually as needed |
| *(no shortcut)* | `-td` alone | Duplicate-admission handling: `-td` now runs the former `-eid` extraction internally as its first step, then treats duplicates |

Individual flags follow the pattern: short flag (e.g. `-ip`) = `--interna-pacientes`. Run `python autoreg.py` with no args to see all functions with descriptions.

## Obsolete Flags

These flags still work if invoked directly (their `.py` files and `FUNCOES`/`FLAG_TO_FUNC` entries are untouched — kept for historical reference), but are hidden from `--help` and from the no-args menu (`argparse.SUPPRESS`, removed from `mostrar_informacoes()`'s `flags` list). See `CHANGELOG.md` for the version each was deprecated in.

| Flag | Reason |
|------|--------|
| `-ea` (`executa_alta`) | Superseded by `-eaa` (`executa_alta_avancado`), which is what `-alta` actually runs today |
| `-ar` (`atualiza_restos`) | No longer used by any current workflow |
| `-tat` (`trata_altas`) | Superseded by `-maa` (`motivo_alta_avancado`) |
| `-p2c` (`pdf2csv`) | No longer part of any current data intake path |
| `-especial` / `-especial-parallel` (`ghosp_especial*`) | No longer used |
| `-R` (`--registro-producao`, AUTOREG-API reporting) | Deprecated production-tracking mechanism; `producao_relatorio.py` kept for reference |
| `-eid` (`extrai_internacoes_duplicadas`) | Absorbed into `-td` — runs automatically as `-td`'s first step now |
| `-duplicados` | Was `-eid` → `-td`; now equivalent to just running `-td` alone |

## Deployment

Runs locally or inside a **Docker/KASM container** (KasmVNC remote desktop). The `cron-autoreg-docker.sh` script is the cron-facing entry: it copies `docker-entry-script.sh` into the running container and executes it with `DISPLAY=:1` for the Xvnc virtual display. Inside the container, `docker-entry-script.sh` runs the cycle `-interna` → `-aihs` → `-solicita-auto` → `-alta`, aborting and sending a WhatsApp summary if any step fails.

## CAPTCHA Handling

AutoReg includes automatic CAPTCHA detection and resolution:

- **Detection**: All SISREG modules call `detecta_captcha(driver)` which monitors for CAPTCHA challenges
- **Automatic Resolution**: When `[2CAPTCHA] enabled = true` in config.ini, uses 2Captcha API to solve automatically
- **Manual Fallback**: If automatic fails or disabled, pauses and waits for manual resolution (local or KASM viewer)
- **Supported Types**: reCAPTCHA v2/v3, hCaptcha, simple image CAPTCHAs
- **Documentation**: See `CAPTCHA_2CAPTCHA.md` and `INSTALACAO_2CAPTCHA.md`
- **Testing**: Run `python test_2captcha_integration.py` to verify setup

## Non-obvious Behaviors

- **G-HOSP 500 auto-recovery** (`extrai_internados_ghosp_avancado.py`): if a Rails error-500 page is detected mid-session, the module silently performs a full re-login and retries the navigation. This is transparent to the caller.
- **`-p2c` optional argument**: `-p2c` / `--pdf2csv` is the only flag that accepts an optional positional argument (path to a PDF file). All other flags are boolean.
- **`-R` timing**: for `-alta`, production is registered *before* the sequence runs; for `-interna` and `-solicita` it is also registered before the sequence. This is a pre-registration pattern, not a post-registration one.
- **Exam deduplication (`-eas`)**: records with a non-empty `solicitacao` column are skipped unless `solicita='s'` is set. The `solicita` column is cleared after successful processing.
- **Bash exit codes through `tee`** (`docker-entry-script.sh`): after `cmd | tee file`, `$?` reflects `tee`'s exit code, not `cmd`'s — use `${PIPESTATUS[0]}` to check whether the piped command actually failed.
- **Testing a single `autoreg/` module in isolation**: `from autoreg.X import Y` triggers `autoreg/__init__.py`, which eagerly imports every module in the package (Selenium, requests, bs4, 2captcha...) — even to test a pure-pandas module like `solicita_pre_aih_bridge.py`. Without the full `venv` dependencies installed, load the file directly via `importlib.util.spec_from_file_location(...)` or copy the needed files into a throwaway package instead.
- **`sessao_sisreg.sessao_expirada()` false positive**: it detects expired sessions by looking for the substring "erro de sistema" anywhere in `driver.page_source` — but that's also the exact business-error message SISREG shows for a single ficha that can't be internada/dada alta (not a session problem). `internacao_sisreg.internar_ficha_sisreg()` avoids the collision by always doing `driver.get()` to a fresh page *before* calling `garantir_sessao_sisreg()`, so a leftover error div from a previous ficha is never on screen when the check runs. Keep that ordering in any new loop that checks session state.

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
