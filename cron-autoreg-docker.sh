#!/bin/bash

CONTAINER_NAME="autoreg"
SCRIPT_SOURCE="/home/michel/code/AutoReg/docker-entry-script.sh"
SCRIPT_DEST="/tmp/entry.sh"
DOCKER_USER="kasm-user" # Substitua pelo usuário correto se for diferente

# Verificar se o contêiner está rodando
if ! docker ps --format '{{.Names}}' | grep -q $CONTAINER_NAME; then
    echo "ERRO: O contêiner '$CONTAINER_NAME' não está rodando. Abortando execução." >> /tmp/docker_cron_error.log
    # Implementar notificação de erro aqui, se necessário.
    exit 1
fi

# 1. Copia o script de entrada para dentro do contêiner
# Usamos 'docker cp' para garantir que o script esteja no lugar certo.
docker cp $SCRIPT_SOURCE $CONTAINER_NAME:$SCRIPT_DEST

# 2. Garante que o script seja executável dentro do contêiner
docker exec -e TZ="America/Rio_Branco" -u $DOCKER_USER $CONTAINER_NAME chmod +x $SCRIPT_DEST

# 3. Executa o script com o usuário não-root (kasm-user) dentro do contêiner
# A saída será logada pelo script interno (no /tmp/cron_execution_log.txt no container)
# e enviada via API.
# Usamos -d para execução "detachada" se a sessão for longa, mas o 'exec' já é bloqueante.
echo "Executando script dentro do contêiner $CONTAINER_NAME..."

# O comando 'docker exec' vai bloquear até que o script interno termine,
# garantindo a espera pela execução sequencial.
docker exec -u $DOCKER_USER $CONTAINER_NAME bash $SCRIPT_DEST

# 4. Opcional: Copiar o log de volta para o host (para auditoria)
# docker cp $CONTAINER_NAME:/tmp/cron_execution_log.txt /home/michel/logs/autoreg_$(date +\%Y\%m\%d_\%H\%M\%S).log
