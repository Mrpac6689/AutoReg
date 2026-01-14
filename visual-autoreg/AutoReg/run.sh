#!/bin/bash
# Script para executar a aplicação AutoReg GUI

# Caminho para o ambiente virtual
VENV_PYTHON="/home/michel/code/AutoReg/venv/bin/python"

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Diretório raiz do AutoReg (para importar módulo autoreg)
AUTOREG_ROOT="$(cd "${PROJECT_DIR}/../../../" && pwd)"

# Adiciona o diretório src e raiz do autoreg ao PYTHONPATH
export PYTHONPATH="${PROJECT_DIR}/src:${AUTOREG_ROOT}:${PYTHONPATH}"

# Executa a aplicação
"${VENV_PYTHON}" "${PROJECT_DIR}/src/main.py"
