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
python autoreg.py                  # No args: launches the TUI (see below)
python autoreg.py -h                # Show all flags and descriptions (was the no-args behavior)
python autoreg.py -interna         # Run full admission workflow
python autoreg.py -alta            # Run full discharge workflow
python autoreg.py -solicita-auto   # Run AIH solicitation with no human interaction
python autoreg.py --all            # Full admission + discharge cycle
./run_autoreg.sh -interna          # Same as above, activating venv/ first (used outside an activated shell)

# Ad-hoc check scripts (plain python, no test runner)
python test_detecta_captcha.py         # CAPTCHA detection patterns, offline
python test_2captcha_integration.py    # 2Captcha setup, needs [2CAPTCHA] in config.ini

# TUI can also be launched directly (equivalent to `python autoreg.py` with no args)
python tui_app.py
```

## TUI (`tui_app.py`, `tui/`)

Running `python autoreg.py` with **no arguments** launches the TUI
(`tui/app.py`'s `run()`, imported lazily inside `main()` — falls back to
`mostrar_informacoes()` with a warning if `textual` isn't installed, e.g. in
a minimal cron/Docker image). `python tui_app.py` does the same thing
directly. Any explicit flag (including `-h`/`--help`, which now shows the
`mostrar_informacoes()` menu directly — `add_help=False` disables argparse's
own auto-generated help) still goes through the normal CLI path untouched.

`tui_app.py`/`tui/` is a Textual-based terminal UI that wraps `autoreg.py` —
an alternative to typing flags one at a time. It is strictly additive:
nothing in `autoreg.py`'s CLI dispatch or in `autoreg/` was changed, and
every action in the TUI runs as its own subprocess
(`sys.executable -u autoreg.py <flags>`), exactly as if typed in a terminal.
This isolates Selenium crashes from the TUI process, avoids
`autoreg/logging.py`'s first-import-wins `logging.basicConfig()` quirk, and
lets the TUI kill a job without killing itself. `-u` is required because the
child's `print()` output would otherwise be fully block-buffered (stdout
isn't a tty) and never stream live.

- `tui/catalogo.py` — the single source of truth for what the TUI can run:
  the 5 primary Dashboard buttons (`PRINCIPAIS`) and every other flag,
  grouped by category (`CATEGORIAS`), each with the CSV(s) it's known to
  touch in `~/AutoReg/`, whether it's interactive, whether it takes an
  optional PDF path, and whether it's obsolete (hidden by default in the
  Comandos screen, same philosophy as `argparse.SUPPRESS` in `autoreg.py`).
  Keep this in sync manually if `autoreg.py`'s `FLAG_TO_FUNC`/`FUNCOES`
  change.
- `tui/runner.py` — `JobRunner`: spawns/streams/kills the subprocess, and
  does best-effort regex parsing of the child's stdout (`[i/N]` step/record
  counters, `Encontrad[ao]s N` totals) to drive a naive ETA. There is no
  real progress/ETA concept in `autoreg.py` itself — treat this as a rough
  estimate, not a guarantee.
- **`-all` and `-cfg` are never invoked as raw subprocess flags** from the
  TUI, because both block on an interactive `input()` inside `autoreg.py`
  (`executar_todas()`'s repetition-count prompt, `editar_config()`'s editor
  picker) and the TUI runs child processes with `stdin=DEVNULL`. Instead,
  "Ciclo Completo" in the Comandos screen asks the repetition count via a
  Textual modal and then runs `-interna`/`-alta` as separate subprocesses
  N times; "Editar config" opens `config.ini` directly in `$EDITOR` via
  `app.suspend()`.
- **Pause/Retomar/Gravar/Pular controls** (Monitor screen, shown only while
  running `-solicita` or `-spa`) drive the pause/resume protocol that
  `autoreg/solicita_pre_aih.py` already implements via flag files in
  `~/AutoReg/`: `pause.flag`, `grava.flag`, `pula.flag`. This is the same
  mechanism a separate external frontend (`Autoreg-web`, referenced in
  `docker-entry-script.sh`) already uses — the TUI doesn't touch Selenium.
  That module has no `try/finally` around its main loop, so force-killing
  it can leave an orphaned Chrome/chromedriver process; the TUI warns about
  this specifically when stopping a job flagged as risky
  (`catalogo.RISCO_CHROME_ORFAO`).
- Screens (`tui/screens/`) are installed once via `App.install_screen()`
  and navigated with `AutoRegApp.goto(name)`, which collapses the stack
  back to the Dashboard before pushing the target — but Textual **unmounts
  and recreates each screen's widget tree on every pop/push** (the screen
  object persists, `compose()` runs again). Any handler that awaits
  `push_screen_wait()` (confirmations, prompts) must be wrapped in
  `@textual.work`, since plain `on_*`/action handlers aren't run inside a
  Textual worker and `push_screen_wait()` raises `NoActiveWorker` otherwise.
  Any code that reacts to `JobRunner` listener callbacks from a screen/
  widget must guard with `self.is_mounted` and/or catch
  `textual.css.query.NoMatches`, since a background job can emit an update
  in the (asynchronous) gap between a screen's unmount and its listener
  actually being removed.

No build step, no test suite (only the two ad-hoc scripts above), no linter configuration exists in this project.

`AGENTS.md` is a shorter parallel guide for other agents. It has drifted out of date, so trust this file over it when they disagree.

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
| `-solicita` | `-spaa` → `-spa` → `-sia` → `-ssr` → `-snt` | AIH solicitation (`-spa` is interactive: human reviews what `-spaa` couldn't auto-approve) |
| `-solicita-auto` | `-spaa` → `-spb` → `-sia` → `-ssr` → `-snt` | AIH solicitation with no human interaction (cron-safe): `-spb` replaces `-spa`, dropping any record `-spaa` couldn't auto-approve |
| `-aihs` | `-iga` → `-ign` → `-std` | AIH pre-processing (GHOSP notes → SISREG data) |
| `--all` | `-interna` then `-alta` | Complete workflow (prompts for repetition count) |
| *(no shortcut)* | `-eac` → `-eae` → `-eas` → `-ear` | Ambulatorial exam solicitation cycle (consult → extract → solicit → report) |
| *(no shortcut)* | `-pra` / `-pad` / `-pag` | Ambulatorial production extraction (SISREG); run individually as needed |
| *(no shortcut)* | `-td` alone | Duplicate-admission handling: `-td` now runs the former `-eid` extraction internally as its first step, then treats duplicates |
| *(no shortcut)* | `-especial-prepara` → `-especial-extrai` | Targeted one-off pipeline: extract NOME/SETOR/DATA from a G-HOSP "Avaliações Profissionais" PDF report (e.g. `pr018.jasper`), then look up in G-HOSP which professional performed each evaluation and when; run individually, not part of any cron cycle |
| *(no shortcut)* | `-especial-med-prepara` → `-especial-med-extrai` | Targeted one-off pipeline: extract RA + internamento/alta datetimes from a G-HOSP "Altas por período" PDF report (`rc008`), then look up in G-HOSP which physician signed the discharge for each RA; independent of the `-especial-prepara`/`-especial-extrai` pair above, run individually, not part of any cron cycle |

Workflow shortcuts are hardcoded sequences in `main()` (not composed from `FLAG_TO_FUNC`), each stops at the first failing step, and each `return`s, so a shortcut can't be combined with other flags on the same command line. Individual flags, on the other hand, run in the **exact order they appear in `sys.argv`** (`autoreg.py -eid -td` runs `-eid` first).

`-sresg` (`solicita_resgate.py`) is a standalone flag outside every shortcut. It shares `correlacoes_aih.json` with `-spaa`. `-clc` wipes `~/AutoReg/` except `solicita_inf_aih.csv`, `internados_ghosp_avancado.csv` and `historico_solicitacoes.csv`.

**Adding a new flag** touches several places in `autoreg.py`, and nothing enforces that they stay in sync: the import, the `FUNCOES` dict (func + `desc`), `FLAG_TO_FUNC` (both short and long forms), the `flags` list in `mostrar_informacoes()`, `parser.add_argument(...)`, and the optional-positional-arg special case in the argv loop if the flag takes a path. Outside that file, also update `autoreg/__init__.py` exports and `tui/catalogo.py`.

Individual flags follow the pattern: short flag (e.g. `-ip`) = `--interna-pacientes`. Run `python autoreg.py -h` (or `--help`) to see all functions with descriptions — running `python autoreg.py` with **no** args launches the TUI (`tui_app.py`) instead (see the TUI section above).

### `-especial-prepara` / `-especial-extrai`

Unrelated to the obsolete `-especial`/`-especial-parallel` flags below (those do identity verification from an already-known RA; these two extract and cross-reference evaluation authorship from a PDF report).

- `-especial-prepara [PDF]` (`autoreg/especial_prepara.py`) — reads a G-HOSP "Avaliações Profissionais" PDF (a native/vector PDF, not scanned — parsed via `pdfplumber` column-position extraction, not OCR), keeps only rows with `Situação = Feito`, and writes `~/AutoReg/saida_especial.csv` (columns: `nome`, `setor`, `data_avaliacao`, plus empty `ra`/`neurocirurgiao`/`data_hora_avaliacao`/`erro` for the next step). Optional positional PDF path argument, same `nargs='?'` pattern as `-p2c`; defaults to `~/AutoReg/dado_bruto_especial.pdf`.
- `-especial-extrai` (`autoreg/especial_extrai.py`) — for each row, searches the patient by name in G-HOSP `/prontuarios` (handling the `/listar_prontuarios` homonym list, direct `/historicopacs/ID` redirects, and the "Justificativa de Acesso" page — which can appear either right after the name search or when opening a specific `/historicopacs` candidate), picks the HUERB admission (RA) whose entry date is within `[data_entrada, data_entrada + 30 dias]` of `data_avaliacao` (day-granularity comparison — comparing full datetimes would wrongly reject same-day admissions later in the clock than midnight), then reads `/pr/presavalprofs/solicitacoes?intern_id=RA` (expanding "Mostrar todas solicitações" first) to find the NEUROCIRURGIÃO evaluation(s). If a RA has more than one such evaluation, the first is written to the current row and each additional one becomes a **new appended row** (not reprocessed in the same run — the loop iterates over the row indices captured before appending starts).

### `-especial-med-prepara` / `-especial-med-extrai`

A second, independent one-off pipeline — shares no code or CSV with `-especial-prepara`/`-especial-extrai` above, only the two-stage "prepare from PDF, then extract via Selenium" shape.

- `-especial-med-prepara [PDF]` (`autoreg/especial_med_prepara.py`) — reads a G-HOSP "Altas por período" PDF (report `rc008`), parsed via `pdfplumber` word-position extraction (not OCR). Each record is anchored by its RA (`Nº Int.`, always a 6-digit token in the leftmost column) rather than by any text marker, since this report's "Internamento/Alta" column reliably contains exactly two `dd/mm/aa hh:mm` tokens on the RA's own line — extracted by regex rather than fixed column bounds, which proved more robust than position-based cropping for this report. Patient name is normally on the RA's own line, but for long names it spills entirely onto the line just above the anchor (confirmed empirically against a real report: 2 of 82 records) — handled with a fallback lookup in a narrow band above the anchor. Writes `~/AutoReg/especial-med-resultado.csv` (columns: `ra`, `nome`, `data_hora_internamento`, `data_hora_alta`, plus empty `medicoalta`/`erro` for the next step). Optional positional PDF path argument, same `nargs='?'` pattern as `-especial-prepara`; defaults to `~/AutoReg/dado_bruto_especial_med.pdf`.
- `-especial-med-extrai` (`autoreg/especial_med_extrai.py`) — for each row, navigates directly to `/pr/altas?intern_id=RA` (RA already known from the PDF — no name search needed, unlike `-especial-extrai`), handles the "Justificativa de Acesso" page via the shared `autoreg/justificativa_ghosp.py` helper, waits for `div.section-content.cor-sec03` (discharge summary section), and reads the physician's name from `label[for='medico'] + div` (same XPath already used in production by `autoreg/motivo_alta_avancado.py` — kept including the CRM suffix, e.g. `"Nome Completo (CRM-AC-1234)"`, for consistency with that existing convention). Writes the result into `medicoalta`; a RA with no discharge summary yet (still admitted) is recorded as an `erro` on that row without stopping the loop.

## Obsolete Flags

These flags still work if invoked directly (their `.py` files and `FUNCOES`/`FLAG_TO_FUNC` entries are untouched — kept for historical reference), but are hidden from `-h`/`--help` (`argparse.SUPPRESS`, removed from `mostrar_informacoes()`'s `flags` list — note `add_help=False`: argparse's own `-h`/`--help` is disabled and `main()` calls `mostrar_informacoes()` directly when `-h`/`--help` is passed, since no-args now launches the TUI instead of this menu). See `CHANGELOG.md` for the version each was deprecated in.

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
- **Optional PDF argument**: `-p2c`, `-especial-prepara` and `-especial-med-prepara` accept an optional positional PDF path (`nargs='?'`). The argv-order loop in `main()` has a hardcoded tuple of these function names so it can consume the next token. All other flags are boolean.
- **`-R` timing (obsolete flag)**: for `-alta`/`-solicita`/`-solicita-auto`, production is registered *before* the sequence runs, but for `-interna` it is registered *after*.
- **Exam deduplication (`-eas`)**: records with a non-empty `solicitacao` column are skipped unless `solicita='s'` is set. The `solicita` column is cleared after successful processing.
- **Bash exit codes through `tee`** (`docker-entry-script.sh`): after `cmd | tee file`, `$?` reflects `tee`'s exit code, not `cmd`'s — use `${PIPESTATUS[0]}` to check whether the piped command actually failed.
- **Testing a single `autoreg/` module in isolation**: `from autoreg.X import Y` triggers `autoreg/__init__.py`, which eagerly imports every module in the package (Selenium, requests, bs4, 2captcha...) — even to test a pure-pandas module like `solicita_pre_aih_bridge.py`. Without the full `venv` dependencies installed, load the file directly via `importlib.util.spec_from_file_location(...)` or copy the needed files into a throwaway package instead.
- **`autoreg.log` format and concurrent writers**: lines are `YYYY-MM-DD HH:MM:SS,mmm -0500 [pid N] - LEVEL - msg`. The host cron runs `cron-autoreg-docker.sh` at 9/12/15/18/21h. The cycle runs **inside the `autoreg` container** with `TZ=America/Rio_Branco`, while TUIs opened inside the container (KASM) launch commands too, and all of them share `~/AutoReg`. Lines written before the offset/pid were added mix local time and UTC with no marker. `autoreg.py` logs `===== autoreg.py iniciado: <flags> | TZ=… =====` and `>>> Etapa X iniciada` / `<<< Etapa X concluída|falhou`, which you can use to delimit runs.
- **`-ign` fails closed** (`lembretes_lidos` column): when `-ign` can't read a prontuário (e.g. a Chrome read timeout), `dados` comes out empty. That looks exactly like "patient has no lembretes", which made `-std`'s "already solicited" filters pass the RA and `-ssr` solicit it a second time (RA 642852, 01/10/2026). So `-ign` sets `lembretes_lidos = sim` only on a real read, and `-std`/`-spaa` (`ras_paciente.filtrar_lembretes_nao_lidos`) drop every row without it. That includes the whole CSV when the column is missing because `-ign` crashed before saving or never ran. Don't reintroduce a path where a read failure leaves a row eligible.
- **Local solicitation history** (`autoreg/historico_solicitacoes.py`, `~/AutoReg/historico_solicitacoes.csv`): `-ssr` appends every successful SISREG solicitation, and `-spaa` skips any RA solicited in the last `DIAS_BLOQUEIO_RESOLICITACAO` (15) days. This is needed because SISREG only rejects a duplicate for the *same procedure while the previous one is still pending*: once `-interna` admits the ficha, a new solicitation goes through.
- **RA duplicado na mesma data/24h** (`autoreg/ras_paciente.py`): `/pr/interns/{RA}` shows the patient's prontuário for that RA, while the patient's RA list (`container-procedimentos` → `RAitem`, with entry date+time) lives at `/historicopacs/{prontuario}`. `-ign` builds that URL from the prontuário link in the `#paciente` banner and opens it only when the lembretes contain a dated clinic solicitation. If an older HUERB RA was entered the same calendar day or within 24h, and the lembretes show a clinic solicitation dated on or after that older RA's entry, `-ign` writes the older RA into `ra_anterior_solicitado`. `-std` and `-spaa` then drop those rows. **Lembretes (`#paclembretes`) belong to the patient, not the RA**: every RA of the patient shows the same list, so only a lembrete's date ties it to an admission. Almost every internação has an earlier HUERB RA within 24h (the emergency visit), and the patient's own solicitation always satisfies "dated after RA1's entry". So the 15-day upper bound is what keeps long-stay patients from being blocked forever, and in practice this filter overlaps heavily with `-std`'s ±15-day rule. A lembrete counts as a solicitation if it has a 9-digit SISREG number and a date and doesn't mention UTI. `-std`'s older "any date within ±15 days" rule also ignores UTI lembretes (`remover_lembretes_uti`). Real lembretes are mostly hand-written ("SISREG CM 23/09 123456789"), and they're split one per block of 3+ spaces or a newline. The check is fail-open. The `rc001` report never lists two RAs of the same patient at once, so this can't be done from the CSV alone.
- **`sessao_sisreg.sessao_expirada()` false positive**: it detects expired sessions by looking for the substring "erro de sistema" anywhere in `driver.page_source` — but that's also the exact business-error message SISREG shows for a single ficha that can't be internada/dada alta (not a session problem). `internacao_sisreg.internar_ficha_sisreg()` avoids the collision by always doing `driver.get()` to a fresh page *before* calling `garantir_sessao_sisreg()`, so a leftover error div from a previous ficha is never on screen when the check runs. Keep that ordering in any new loop that checks session state.

## Important Files

| File | Purpose |
|------|---------|
| `config.ini` | Runtime credentials — **gitignored**, never commit |
| `config.ini.example` | Template for `config.ini` (includes `[2CAPTCHA]` section) |
| `correlacoes_aih.json` | Procedure×clinic correlation/conversion rules for `-spaa` (`solicita_pre_aih_auto.py`) and `-sresg` (`solicita_resgate.py`) — lives in the project root next to `autoreg.py` and **is committed to git**, unlike other `~/AutoReg` runtime data, because it's tuned over time through real use and must survive a machine loss. Both modules resolve its path from `__file__` (two `dirname()` calls up from `autoreg/`), not from `~/AutoReg` |
| `autoreg/__init__.py` | Exports all public functions (source of truth for available API) |
| `~/AutoReg/*.csv` | Runtime data files (inter-module exchange, not in repo) |
| `~/AutoReg/autoreg.log` | Runtime log file |
| `CAPTCHA_2CAPTCHA.md` | Complete 2Captcha integration documentation |
| `INSTALACAO_2CAPTCHA.md` | Step-by-step installation guide for 2Captcha |
| `test_2captcha_integration.py` | Test script to validate 2Captcha setup |
