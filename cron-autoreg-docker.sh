#!/bin/bash
CONTAINER_NAME="autoreg"
SCRIPT_SOURCE="/home/michel/code/AutoReg/docker-entry-script.sh"
SCRIPT_DEST="/tmp/entry.sh"
DOCKER_USER="kasm-user"

# Verificar se o contêiner está rodando
if ! docker ps --format '{{.Names}}' | grep -q $CONTAINER_NAME; then
    echo "ERRO: O contêiner '$CONTAINER_NAME' não está rodando. Abortando execução." >> /tmp/docker_cron_error.log
    exit 1
fi

# Não sobrepõe ciclos: todos compartilham os CSVs de ~/AutoReg. Em 23/10/2026
# o ciclo das 15h travou até 22h45 e os das 18h e 21h rodaram em paralelo a ele.
exec 9>/tmp/autoreg-cron.lock
if ! flock -n 9; then
    echo "$(date '+%F %T') ciclo anterior ainda em execução — pulando este" >> /tmp/docker_cron_error.log
    exit 0
fi

# Agenda para a TUI dentro do container, que não enxerga o crontab do host
# (tui/ciclo_cron.py). ~/AutoReg do host é montado em ~/AutoReg do container.
crontab -l 2>/dev/null | grep -F "cron-autoreg-docker.sh" | grep -v '^\s*#' > "$HOME/AutoReg/cron_agenda.txt"

# 1. Copia o script
docker cp $SCRIPT_SOURCE $CONTAINER_NAME:$SCRIPT_DEST

# 2. Permissão de execução
docker exec -e TZ="America/Rio_Branco" -u $DOCKER_USER $CONTAINER_NAME chmod +x $SCRIPT_DEST

# 3. Execução (AQUI ESTÁ A CORREÇÃO MÁGICA)
# Adicionamos -e DISPLAY=:1 para o Chrome achar o Xvnc
# Adicionamos -e HOME para garantir que ele ache as configs do usuário
echo "Executando script dentro do contêiner $CONTAINER_NAME..."

docker exec -e DISPLAY=:1 -e HOME=/home/kasm-user -u $DOCKER_USER $CONTAINER_NAME bash $SCRIPT_DEST

# Fim
