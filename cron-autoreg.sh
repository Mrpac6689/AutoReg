#!/bin/bash

# --- Configurações ---
# Diretório base do projeto (para facilitar a manutenção)
BASE_DIR="/home/michel/code/AutoReg"
# Executável Python com o ambiente virtual (venv)
PYTHON_EXEC="$BASE_DIR/venv/bin/python3"
# Script principal
SCRIPT="$BASE_DIR/autoreg.py"
# Arquivo temporário para armazenar os logs
LOG_FILE="$BASE_DIR/cron_execution_log.txt"
# API de WhatsApp
WHATSAPP_API_URL="http://100.98.29.11:9080/message/sendText/instancia2"
API_KEY="429683C4C977415CAAFCCE10F7D57E11"
WHATSAPP_NUMBER="5568984063903"

# --- Limpar Log Anterior ---
echo "--- Início da Execução Automatizada: $(date) ---" > $LOG_FILE
echo "" >> $LOG_FILE

# ----------------------------------------
# Função para Executar e Capturar Log
# Argumento 1: Nome da etapa (ex: interna, analisa, alta)
# ----------------------------------------
execute_and_log() {
    local etapa=$1
    echo "## Etapa: -$etapa (Início em $(date))" >> $LOG_FILE
    
    # Executa o script e redireciona a saída (stdout e stderr) para um pipe
    # O comando "tail -n 10" pega as últimas 10 linhas e o "tee -a" as salva no arquivo de log
    # Nota: O uso do `tee` garante que a saída seja vista, se necessário, e salva.
    
    # 1. Executa a aplicação e salva a saída completa em um arquivo temporário de execução
    $PYTHON_EXEC $SCRIPT -$etapa 2>&1 | tee /tmp/temp_output_$etapa.txt
    
    # 2. Pega as últimas 10 linhas desse arquivo temporário e as adiciona ao Log Final
    echo "--- Últimas 10 Linhas de Log da Etapa -$etapa ---" >> $LOG_FILE
    tail -n 10 /tmp/temp_output_$etapa.txt >> $LOG_FILE
    echo "----------------------------------------------------" >> $LOG_FILE
    echo "" >> $LOG_FILE
    
    # 3. Remove o arquivo temporário
    rm /tmp/temp_output_$etapa.txt
    
    # $? é o código de saída do último comando (0 = sucesso)
    if [ $? -ne 0 ]; then
        echo "ERRO: O script -$etapa falhou! Abortando." >> $LOG_FILE
        # Você pode adicionar uma função para enviar uma notificação de ERRO aqui, se desejar.
        return 1 # Retorna código de erro para parar a execução subsequente
    fi
    return 0
}

# ----------------------------------------
# 1. Executar e Logar: -interna
# ----------------------------------------
execute_and_log "interna"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# ----------------------------------------
# 2. Executar e Logar: -analisa
# ----------------------------------------
execute_and_log "analisa"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# ----------------------------------------
# 3. Executar e Logar: -alta
# ----------------------------------------
execute_and_log "alta"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# --- Fim da Execução ---
echo "--- Fim da Execução Automatizada: $(date) ---" >> $LOG_FILE
echo "" >> $LOG_FILE

# ----------------------------------------
# Função para Enviar o Log via API de WhatsApp
# ----------------------------------------
send_whatsapp_log() {
    # Lê todo o conteúdo do log e escapa as quebras de linha/caracteres especiais para JSON
    local LOG_CONTENT=$(cat $LOG_FILE | sed -e 's/"/\\"/g' -e ':a;N;$!ba;s/\n/\\n/g')
    local MESSAGE_TEXT="Log de Execução $SCRIPT:\n$LOG_CONTENT"

    # Constrói o payload JSON
    local JSON_PAYLOAD=$(cat <<EOF
{
    "number": "$WHATSAPP_NUMBER",
    "text": "$MESSAGE_TEXT"
}
EOF
)

    # Envia a requisição curl
    RESPONSE=$(curl -s -X POST \
        $WHATSAPP_API_URL \
        -H 'Content-Type: application/json' \
        -H "apikey: $API_KEY" \
        -d "$JSON_PAYLOAD")

    # Opcional: Logar o status do envio da mensagem no próprio log
    echo "Status do Envio via WhatsApp: $RESPONSE" >> $LOG_FILE
}

# ----------------------------------------
# Enviar o Log Final
# ----------------------------------------
send_whatsapp_log

# Fim do Script
exit 0
