# Manutenção: versão, changelog e documentação

Para humanos e IAs. Vale para toda mudança de comportamento.

## Versão (SemVer, fonte: `autoreg/versao.py`)
- **Patch** (10.1.x): correção. **Minor** (10.x.0): flag, arquivo ou regra nova. **Major**: quebra de `config.ini`, CSV ou flag.
- Atualize também `autoreg.py`, `README.md` (PT e EN) e `CHANGELOG.md`; `python test_versao.py` acusa o que faltar.
- Tag: `vX.Y.Z` no commit da versão.

## Onde documentar
| Mudança | Arquivo |
|---|---|
| O que mudou e por quê (com caso real e data) | `CHANGELOG.md`, em `[Não lançado]` |
| Invariante ou armadilha que uma IA precisa saber | `CLAUDE.md` |
| Resumo curto da armadilha | `AGENTS.md` |
| Uso | `README.md` (PT e EN) |
| Fluxo de alta | `docs/ALTAS.md` |
| Nova flag | `autoreg.py` (6 pontos, ver CLAUDE.md) e `tui/catalogo.py` |

## Antes de concluir
1. `python test_vinculos.py && python test_versao.py`
2. O container lê `~/code/AutoReg` ao vivo: não edite durante um ciclo (`/tmp/autoreg-cron.lock`).
3. Nunca pôr nome, CNS ou CPF de paciente em documento versionado; use RA/solicitação.
