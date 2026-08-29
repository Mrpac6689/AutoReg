#!/bin/bash

export TZ="America/Rio_Branco"

# --- Configurações DENTRO DO CONTAINER ---
PYTHON_EXEC="/usr/bin/python3"
SCRIPT="/home/kasm-user/.autoreg/autoreg.py"
PROJECT_DIR="$(dirname "$SCRIPT")"

# --- Configurações de Log ---
LOG_FILE="/tmp/cron_execution_log.txt"

# --- Configurações de Diretórios ---
RELATORIODIR="/home/kasm-user/Autoreg-web"
WORKDIR="/home/kasm-user/AutoReg"
RELATORIO_CSV="$RELATORIODIR/relatorio.csv"
RESUMO_FILE="$WORKDIR/resumo_execucao.txt"
USUARIO="michel"

# --- Limpar Log e Resumo da Execução Anterior ---
echo "--- Início da Execução Automatizada (Dentro do Container): $(date) ---" > $LOG_FILE
echo "" >> $LOG_FILE
mkdir -p "$WORKDIR"
> "$RESUMO_FILE"

# ----------------------------------------
# Função para Executar e Capturar Log
# ----------------------------------------
execute_and_log() {
    local etapa=$1
    echo "## Etapa: -$etapa (Início em $(date))" >> $LOG_FILE

    # Executa o script e redireciona a saída para um arquivo temporário
    $PYTHON_EXEC $SCRIPT -$etapa 2>&1 | tee /tmp/temp_output_$etapa.txt
    # Captura o exit code do PYTHON_EXEC (primeiro comando do pipe), não do 'tee'
    local exit_code=${PIPESTATUS[0]}

    # Mantém as últimas 10 linhas no log técnico local (depuração)
    echo "--- Últimas 10 Linhas de Log da Etapa -$etapa ---" >> $LOG_FILE
    tail -n 10 /tmp/temp_output_$etapa.txt >> $LOG_FILE
    echo "----------------------------------------------------" >> $LOG_FILE
    echo "" >> $LOG_FILE

    rm /tmp/temp_output_$etapa.txt

    if [ $exit_code -ne 0 ]; then
        echo "ERRO: O script -$etapa falhou (exit code $exit_code)! Abortando." >> $LOG_FILE
        return 1
    fi
    return 0
}

# ----------------------------------------
# Função para Gravar no Relatório CSV
# ----------------------------------------
gravar_relatorio() {
    local rotina=$1
    local arquivo_csv=$2

    # Verifica se o diretório existe, se não, cria
    mkdir -p "$RELATORIODIR"

    # Verifica se o arquivo CSV existe
    if [ ! -f "$arquivo_csv" ]; then
        echo "AVISO: Arquivo $arquivo_csv não encontrado. Registros = 0" >> $LOG_FILE
        local registros=0
    else
        # Conta o número de registros (linhas não vazias, excluindo cabeçalho se houver)
        local registros=$(tail -n +2 "$arquivo_csv" 2>/dev/null | grep -v '^$' | wc -l)
        # Se não tiver cabeçalho ou se o arquivo tiver apenas cabeçalho, conta todas as linhas não vazias
        if [ "$registros" -eq 0 ]; then
            registros=$(grep -v '^$' "$arquivo_csv" 2>/dev/null | wc -l)
        fi
    fi

    # Obtém data e hora atual
    local data=$(date +"%Y-%m-%d")
    local hora=$(date +"%H:%M:%S")

    # Verifica se o arquivo de relatório existe, se não, cria com cabeçalho
    if [ ! -f "$RELATORIO_CSV" ]; then
        echo "data,hora,rotina,usuario,registros" > "$RELATORIO_CSV"
    fi

    # Adiciona a linha ao relatório
    echo "$data,$hora,$rotina,$USUARIO,$registros" >> "$RELATORIO_CSV"

    echo "Relatório gravado: $rotina - $registros registros" >> $LOG_FILE
}

# ----------------------------------------
# Função para Enviar o Resumo Consolidado via WhatsApp
# ----------------------------------------
# O resumo (o que foi feito / não feito / erros, por módulo) é montado e
# acumulado em $RESUMO_FILE pelo próprio autoreg.py durante -interna, -alta
# e -solicita-auto (ver autoreg/relatorio_execucao.py). Esta função só
# dispara o envio final, lendo as credenciais de config.ini [EVOLUTION-API]
# (sem hardcode de URL/chave/número).
send_resumo_whatsapp() {
    echo "Enviando resumo consolidado via WhatsApp..." >> $LOG_FILE
    (cd "$PROJECT_DIR" && $PYTHON_EXEC -m autoreg.relatorio_execucao) >> $LOG_FILE 2>&1
}

# ----------------------------------------
# 1. Executar: -interna
# ----------------------------------------
execute_and_log "interna"
if [ $? -ne 0 ]; then
    send_resumo_whatsapp
    exit 1
fi

# ----------------------------------------
# 2. Executar: -aihs
# ----------------------------------------
execute_and_log "aihs"
if [ $? -ne 0 ]; then
    send_resumo_whatsapp
    exit 1
fi

# ----------------------------------------
# 3. Executar: -solicita-auto
# ----------------------------------------
execute_and_log "solicita-auto"
if [ $? -ne 0 ]; then
    send_resumo_whatsapp
    exit 1
fi

# ----------------------------------------
# 4. Executar: -alta
# ----------------------------------------
execute_and_log "alta"
if [ $? -ne 0 ]; then
    send_resumo_whatsapp
    exit 1
fi

# Contar registros em pacientes_de_alta.csv e gravar no relatório
gravar_relatorio "Altas" "$WORKDIR/pacientes_de_alta.csv"

# --- Fim da Execução ---
echo "--- Fim da Execução Automatizada: $(date) ---" >> $LOG_FILE
echo "" >> $LOG_FILE

# ----------------------------------------
# Enviar o Resumo Final
# ----------------------------------------
send_resumo_whatsapp

# Fim do Script
exit 0
