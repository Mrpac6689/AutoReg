#!/bin/bash
#
# AutoReg - Script de Desinstalação
# Versão 7.0.0-1 - Julho de 2025
# Autor: Michel Ribeiro Paes (MrPaC6689)
#

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                            AutoReg Uninstaller                               ║${NC}"
    echo -e "${RED}║                    Automatização de Sistemas de Saúde                        ║${NC}"
    echo -e "${RED}║                               SISREG & G-HOSP                                ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

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

# Definir diretório de instalação
if [[ $OS == "windows" ]]; then
    INSTALL_DIR="$USERPROFILE/.autoreg"
else
    INSTALL_DIR="$HOME/.autoreg"
fi

print_header

print_warning "Esta ação irá remover completamente o AutoReg do seu sistema!"
print_info "Diretório a ser removido: $INSTALL_DIR"
echo

# Confirmar desinstalação
read -p "Tem certeza que deseja desinstalar o AutoReg? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Desinstalação cancelada"
    exit 0
fi

# Remover diretório de instalação
if [[ -d "$INSTALL_DIR" ]]; then
    print_info "Removendo diretório de instalação..."
    rm -rf "$INSTALL_DIR"
    if [[ $? -eq 0 ]]; then
        print_success "Diretório removido com sucesso"
    else
        print_error "Falha ao remover diretório"
    fi
else
    print_warning "Diretório de instalação não encontrado"
fi

# Remover do PATH (Unix)
if [[ $OS == "linux" ]] || [[ $OS == "macos" ]]; then
    # Remover link simbólico
    if [[ -L "/usr/local/bin/autoreg" ]]; then
        print_info "Removendo link simbólico..."
        if sudo rm "/usr/local/bin/autoreg" 2>/dev/null; then
            print_success "Link simbólico removido"
        else
            print_warning "Não foi possível remover link simbólico (pode requerer sudo)"
        fi
    fi
    
    # Remover do shell RC
    for rc_file in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
        if [[ -f "$rc_file" ]] && grep -q "autoreg" "$rc_file"; then
            print_info "Removendo entradas do $rc_file..."
            sed -i.bak '/autoreg/d' "$rc_file"
            print_success "Entradas removidas de $rc_file"
        fi
    done
fi

# Instruções para Windows
if [[ $OS == "windows" ]]; then
    print_warning "No Windows, você pode precisar remover manualmente do PATH:"
    print_info "1. Abra as Configurações do Sistema"
    print_info "2. Vá em Variáveis de Ambiente"
    print_info "3. Remova $INSTALL_DIR do PATH"
fi

echo
print_success "═══════════════════════════════════════════════════════════════"
print_success "           DESINSTALAÇÃO CONCLUÍDA!"
print_success "═══════════════════════════════════════════════════════════════"
echo
print_info "AutoReg foi removido do sistema"
print_warning "Reinicie o terminal para que as mudanças tenham efeito"
echo
