#!/bin/bash
# Script para executar AutoReg com venv ativado

# Diretório do script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ativa o venv
source "$DIR/venv/bin/activate"

# Executa o autoreg.py com todos os argumentos passados
python "$DIR/autoreg.py" "$@"

# Desativa o venv ao sair
deactivate
