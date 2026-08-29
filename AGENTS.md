# AGENTS.md — AutoReg

Brazilian healthcare automation (SISREG + G-HOSP). Selenium WebDriver (Chrome), no build/lint/test suite.

## Commands

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp config.ini.example config.ini   # edit with real creds
python autoreg.py --help            # all flags
python autoreg.py -interna          # admission cycle
python autoreg.py -alta             # discharge cycle
python autoreg.py -solicita -R      # AIH solicitation + production report
python autoreg.py --all             # full admission + discharge (prompts for count)
# Tests (ad-hoc, no test runner):
python test_2captcha_integration.py
python test_detecta_captcha.py
```

## Architecture

- **Entrypoint**: `autoreg.py` – argparse CLI. Maps short flags (`-ip`) to module functions via `FUNCOES` dict, preserving order from `sys.argv`.
- **Module pattern**: every module in `autoreg/` reads `config.ini` → opens Chrome → scrapes/fills → writes CSV to `~/AutoReg/` → closes browser in `finally`.
- **Data flow**: CSVs in `~/AutoReg/` are the inter-module store; each step's output is the next step's input.
- **Config sections**: `[SISREG]` / `[SISREG-REG]` (some modules read from `[SISREG-REG]` directly, not via `ler_credenciais`), `[G-HOSP]` / `[G-HOSP-REG]`, `[AUTOREG-API]`, `[2CAPTCHA]`, `[EVOLUTION-API]`, `[KASM]`.
- **Backup files** (`*bkp.py`): dead code, not imported anywhere.

## Critical gotchas

- **Filename typo**: `autoreg/detecta_capchta.py` (note "capchta"). All imports use this spelling; do not rename.
- **G-HOSP 500 recovery**: `extrai_internados_ghosp_avancado.py` silently re-logs in and retries if it detects a Rails 500 error page mid-session.
- **`-R` is pre-registration**: for `-alta`, `-interna`, `-solicita`, production is reported to AUTOREG-API *before* the sequence runs.
- **Exam dedup (`-eas`)**: rows with non-empty `solicitacao` column are skipped unless `solicita='s'`. Column cleared after success.
- **`-p2c`** is the only flag taking an optional positional arg (PDF path); all others are boolean.
- **Workflows differ slightly**: `--all` = `-interna` (2 steps) then `-alta` (4 steps). These are hardcoded in `autoreg.py:473-489`, not composed from `FLAG_TO_FUNC`.
- **Environment**: standard Python `venv` + `requirements.txt` (pip) — no conda; the repo has a `venv/` directory locally.
- **Docker**: cron entry injects `docker-entry-script.sh` into container, runs with `DISPLAY=:1` for Xvnc. See `cron-autoreg-docker.sh`.
- **`tst/` directory is empty** – no test infrastructure exists beyond two ad-hoc scripts.
