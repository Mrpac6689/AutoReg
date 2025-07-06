#!/bin/bash
# Script de teste para validar as funções do instalador

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Teste das Funções do Instalador AutoReg ===${NC}"
echo

# Detectar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    OS="unknown"
fi

echo -e "${BLUE}1. Detecção do OS:${NC} $OS ($OSTYPE)"

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}2. Python3:${NC} ✅ $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        echo -e "${GREEN}2. Python:${NC} ✅ $PYTHON_VERSION"
        PYTHON_CMD="python"
    else
        echo -e "${RED}2. Python:${NC} ❌ Versão incorreta: $PYTHON_VERSION"
        exit 1
    fi
else
    echo -e "${RED}2. Python:${NC} ❌ Não encontrado"
    exit 1
fi

# Verificar pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1)
    echo -e "${GREEN}3. pip3:${NC} ✅ $(echo $PIP_VERSION | cut -d' ' -f1-2)"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_VERSION=$(pip --version 2>&1)
    echo -e "${GREEN}3. pip:${NC} ✅ $(echo $PIP_VERSION | cut -d' ' -f1-2)"
    PIP_CMD="pip"
else
    echo -e "${RED}3. pip:${NC} ❌ Não encontrado"
    exit 1
fi

# Verificar venv
if $PYTHON_CMD -m venv --help &> /dev/null; then
    echo -e "${GREEN}4. venv:${NC} ✅ Disponível"
else
    echo -e "${RED}4. venv:${NC} ❌ Não disponível"
    exit 1
fi

# Verificar diretório home
if [[ $OS == "windows" ]]; then
    HOME_DIR="$USERPROFILE"
else
    HOME_DIR="$HOME"
fi

echo -e "${BLUE}5. Diretório Home:${NC} $HOME_DIR"

# Simular criação do diretório de instalação
INSTALL_DIR="$HOME_DIR/.autoreg"
echo -e "${BLUE}6. Diretório de Instalação:${NC} $INSTALL_DIR"

# Verificar se pode criar o diretório
if mkdir -p "$INSTALL_DIR/test" 2>/dev/null; then
    echo -e "${GREEN}7. Permissões:${NC} ✅ Pode criar diretórios"
    rmdir "$INSTALL_DIR/test" 2>/dev/null
    if [[ -d "$INSTALL_DIR" ]] && [[ ! "$(ls -A $INSTALL_DIR)" ]]; then
        rmdir "$INSTALL_DIR" 2>/dev/null
    fi
else
    echo -e "${RED}7. Permissões:${NC} ❌ Não pode criar diretórios"
fi

# Verificar arquivos necessários
echo -e "${BLUE}8. Arquivos do projeto:${NC}"
for file in "autoreg.py" "requirements.txt" "autoreg/__init__.py"; do
    if [[ -f "$file" ]]; then
        echo -e "   ${GREEN}✅${NC} $file"
    else
        echo -e "   ${RED}❌${NC} $file"
    fi
done

echo
echo -e "${GREEN}=== Validação das Dependências Concluída ===${NC}"
echo -e "${BLUE}Sistema está pronto para instalação do AutoReg!${NC}"
