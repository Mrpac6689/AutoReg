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

# --- Configurações de Diretórios ---
RELATORIODIR="/home/kasm-user/Autoreg-web"
WORKDIR="/home/kasm-user/AutoReg"
RELATORIO_CSV="$RELATORIODIR/relatorio.csv"
USUARIO="michel"

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
# 1. Executar: -eci (Extrair Códigos de Internação)
# ----------------------------------------
execute_and_log "eci"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# Contar registros em codigos_internacao.csv e gravar no relatório
gravar_relatorio "Internar Pacientes" "$WORKDIR/codigos_internacao.csv"

# ----------------------------------------
# 2. Executar: -ip (Internar Pacientes)
# ----------------------------------------
execute_and_log "ip"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# ----------------------------------------
# 3. Executar: -analisa
# ----------------------------------------
execute_and_log "analisa"
if [ $? -ne 0 ]; then
    send_whatsapp_log # Envia o log parcial de erro
    exit 1
fi

# Contar registros em pacientes_de_alta.csv e gravar no relatório
gravar_relatorio "Altas" "$WORKDIR/pacientes_de_alta.csv"

# ----------------------------------------
# 4. Executar: -alta
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
