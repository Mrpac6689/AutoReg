# AGENTS.md — AutoReg

Brazilian healthcare automation (SISREG + G-HOSP). Selenium WebDriver (Chrome), no build/lint/test suite.

## Commands

```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp config.ini.example config.ini   # edit with real creds
python autoreg.py --help            # all flags
python autoreg.py -interna          # admission cycle
python autoreg.py -alta             # discharge cycle
python autoreg.py -solicita         # AIH solicitation (interactive -spa step)
python autoreg.py -solicita-auto    # AIH solicitation, no human interaction (cron-safe)
python autoreg.py                   # no args: launches the Textual TUI
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
- **`-R` is obsolete** (hidden from `--help`): it used to report production to AUTOREG-API; for `-alta`/`-solicita` before the sequence, for `-interna` after.
- **Exam dedup (`-eas`)**: rows with non-empty `solicitacao` column are skipped unless `solicita='s'`. Column cleared after success.
- **Optional PDF path**: `-p2c`, `-especial-prepara` and `-especial-med-prepara` take an optional positional PDF path; all other flags are boolean.
- **Workflows differ slightly**: `--all` = `-interna` (2 steps) then `-alta` (4 steps). Workflow shortcuts are hardcoded in `main()` of `autoreg.py`, not composed from `FLAG_TO_FUNC`.
- **Environment**: standard Python `venv` + `requirements.txt` (pip) — no conda; the repo has a `venv/` directory locally.
- **Docker**: cron entry injects `docker-entry-script.sh` into container, runs with `DISPLAY=:1` for Xvnc. See `cron-autoreg-docker.sh`.
- **No test infrastructure** beyond the two ad-hoc scripts above.
