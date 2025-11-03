#!/usr/bin/env bash
#
# setup-autoreg-full.sh
# Script completo por Michel Ribeiro Paes
#
# Funções:
#  - adiciona o usuário atual ao grupo 'docker' (se necessário)
#  - detecta shell padrão (bash/zsh) e insere alias autoreg
#  - verifica existência de Dockerfile e docker-compose.yml no diretório atual
#  - baixa requirements.txt (com fallback local)
#  - executa sudo docker compose up --build -d
#
# Uso:
# chmod +x setup-autoreg-full.sh
# ./setup-autoreg-full.sh
#

set -o errexit
set -o nounset
set -o pipefail

# ---------- utilitários ----------
echoinfo()  { printf "ℹ️  %s\n" "$*"; }
echowarn()  { printf "⚠️  %s\n" "$*"; }
echoerr()   { printf "❌ %s\n" "$*" >&2; }
echook()    { printf "✅ %s\n" "$*"; }

# ---------- detectar usuário e shell ----------
USER_NAME="$(whoami)"
SHELL_PATH="${SHELL:-/bin/bash}"

if [[ "$SHELL_PATH" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [[ "$SHELL_PATH" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash (fallback)"
fi

echoinfo "Usuário: $USER_NAME"
echoinfo "Shell detectado: $SHELL_NAME"
echoinfo "Arquivo de configuração alvo: $SHELL_RC"
echo

# ---------- 1) adiciona usuário ao grupo docker ----------
echoinfo "1) Verificando associação ao grupo 'docker'..."
if groups "$USER_NAME" | grep -qw docker; then
    echook "Usuário já é membro do grupo 'docker'."
else
    echoinfo "Adicionando $USER_NAME ao grupo 'docker' (poderá pedir senha sudo)..."
    if sudo usermod -aG docker "$USER_NAME"; then
        echook "Usuário adicionado ao grupo 'docker'."
        echoinfo "OBS: faça logout/login ou reboot para que a mudança de grupo tenha efeito."
    else
        echoerr "Falha ao adicionar usuário ao grupo docker."
        exit 1
    fi
fi
echo

# ---------- 2) inserir alias no rc do shell ----------
ALIAS_LINE='alias autoreg="docker exec -it autoreg bash"'
echoinfo "2) Inserindo alias no $SHELL_RC (se ainda não existir)..."

if [[ ! -f "$SHELL_RC" ]]; then
    echoinfo "$SHELL_RC não existe — criando."
    touch "$SHELL_RC"
fi

if grep -Fqx "$ALIAS_LINE" "$SHELL_RC"; then
    echook "Alias já presente em $SHELL_RC."
else
    {
        printf "\n# Alias para acesso ao container kasm-autoreg\n"
        printf "%s\n" "$ALIAS_LINE"
    } >> "$SHELL_RC"
    echook "Alias adicionado em $SHELL_RC."
fi
echo

# ---------- 3) verificar Dockerfile e docker-compose.yml ----------
echoinfo "3) Verificando presença de Dockerfile e docker-compose.yml no diretório atual: $(pwd)"
MISSING_FILES=()
[[ -f "Dockerfile" ]] || MISSING_FILES+=("Dockerfile")
[[ -f "docker-compose.yml" ]] || MISSING_FILES+=("docker-compose.yml")

if (( ${#MISSING_FILES[@]} > 0 )); then
    echoerr "Arquivos faltando: ${MISSING_FILES[*]}"
    echoerr "Adicione os arquivos indicados ao diretório $(pwd) e execute o script novamente."
    exit 2
else
    echook "Dockerfile e docker-compose.yml encontrados."
fi
echo

# ---------- 4) baixar requirements.txt (com fallback) ----------
REQUIREMENTS_FILE="requirements.txt"
RAW_URL="https://raw.githubusercontent.com/Mrpac6689/AutoReg/main/${REQUIREMENTS_FILE}"

if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echook "${REQUIREMENTS_FILE} já presente localmente. Pulando download."
else
    echoinfo "Baixando ${REQUIREMENTS_FILE} de:"
    echoinfo "   $RAW_URL"
    if curl -fSL --connect-timeout 10 --max-time 60 -o "$REQUIREMENTS_FILE" "$RAW_URL"; then
        echook "${REQUIREMENTS_FILE} baixado com sucesso."
    else
        echowarn "Falha ao baixar ${REQUIREMENTS_FILE} de $RAW_URL."
        if [[ -f "$REQUIREMENTS_FILE" ]]; then
            echowarn "Mas o arquivo está presente localmente — prosseguindo."
        else
            echoerr "Arquivo ${REQUIREMENTS_FILE} não encontrado e não pôde ser baixado."
            echoerr "Baixe manualmente em: https://github.com/Mrpac6689/AutoReg/blob/main/requirements.txt"
            exit 3
        fi
    fi
fi
echo

# ---------- 5) subir containers com docker compose ----------
echoinfo "5) Subindo containers: sudo docker compose up --build -d"

if ! command -v docker >/dev/null 2>&1; then
    echoerr "Docker não encontrado no sistema. Instale o Docker antes de prosseguir."
    exit 4
fi

if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    echowarn "'docker compose' não disponível — usando 'docker-compose' fallback."
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echoerr "Nem 'docker compose' nem 'docker-compose' estão disponíveis. Instale um deles."
    exit 5
fi

if sudo $DOCKER_COMPOSE_CMD up --build -d; then
    echook "Containers subidos com sucesso (usando: sudo $DOCKER_COMPOSE_CMD up --build -d)."
else
    echoerr "Falha ao executar sudo $DOCKER_COMPOSE_CMD up. Verifique logs e permissões."
    exit 6
fi
echo

# ---------- final ----------
echoinfo "Script concluído com sucesso."
echoinfo "Observações finais:"
echoinfo "  - Alias e associação ao grupo docker exigirão logout/login ou reboot."
echoinfo "  - Para aplicar o alias agora, rode:"
printf "      source %s\n" "$SHELL_RC"
echoinfo "  - Para instalar dependências Python (caso necessário):"
printf "      pip install -r %s\n" "$REQUIREMENTS_FILE"
echook "Fim."

exit 0
