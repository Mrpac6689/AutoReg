#!/bin/bash

export TZ="America/Rio_Branco"

# --- Configurações DENTRO DO CONTAINER ---
# Nota: O Dockerfile do seu contêiner deve ter o `curl` instalado.
PYTHON_EXEC="/usr/bin/python3"
SCRIPT="/home/kasm-user/.autoreg/autoreg.py"

# Parâmetros de Log e API (São mantidos no container ou definidos aqui)
LOG_FILE="/tmp/cron_execution_log.txt"
WHATSAPP_API_URL="http://100.98.29.11:9080/message/sendText/instancia2"
API_KEY="429683C4C977415CAAFCCE10F7D57E11"
WHATSAPP_NUMBER="5568984063903"

# --- Limpar Log Anterior ---
echo "--- Início da Execução Automatizada (Dentro do Container): $(date) ---" > $LOG_FILE
echo "" >> $LOG_FILE

# ----------------------------------------
# Função para Executar e Capturar Log
# ----------------------------------------
execute_and_log() {
    local etapa=$1
    echo "## Etapa: -$etapa (Início em $(date))" >> $LOG_FILE
    
    # Executa o script e redireciona a saída para um arquivo temporário
    $PYTHON_EXEC $SCRIPT -$etapa 2>&1 | tee /tmp/temp_output_$etapa.txt
    
    # Captura as últimas 10 linhas do output
    echo "--- Últimas 10 Linhas de Log da Etapa -$etapa ---" >> $LOG_FILE
    tail -n 10 /tmp/temp_output_$etapa.txt >> $LOG_FILE
    echo "----------------------------------------------------" >> $LOG_FILE
    echo "" >> $LOG_FILE
    
    rm /tmp/temp_output_$etapa.txt
    
    if [ $? -ne 0 ]; then
        echo "ERRO: O script -$etapa falhou! Abortando." >> $LOG_FILE
        return 1
    fi
    return 0
}

# ----------------------------------------
# 1. Executar: -interna
# ----------------------------------------
execute_and_log "interna"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# ----------------------------------------
# 2. Executar: -analisa
# ----------------------------------------
execute_and_log "analisa"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# ----------------------------------------
# 3. Executar: -alta
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

    # Opcional: Logar o status do envio da mensagem no log
    echo "Status do Envio via WhatsApp: $RESPONSE" >> $LOG_FILE
}

# ----------------------------------------
# Enviar o Log Final
# ----------------------------------------
send_whatsapp_log

# Fim do Script
exit 0
