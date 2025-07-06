#!/bin/bash
#
# AutoReg - Script de Instalação
# Versão 7.0.0-1 - Julho de 2025
# Autor: Michel Ribeiro Paes (MrPaC6689)
#
# Script de instalação multiplataforma para AutoReg
# Compatível com Linux, macOS e Windows (Git Bash/WSL)
#

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_header() {
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                              AutoReg Installer                               ║${NC}"
    echo -e "${PURPLE}║                    Automatização de Sistemas de Saúde                        ║${NC}"
    echo -e "${PURPLE}║                               SISREG & G-HOSP                                ║${NC}"
    echo -e "${PURPLE}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${PURPLE}║ Versão: 7.0.0-1                                                             ║${NC}"
    echo -e "${PURPLE}║ Autor: Michel Ribeiro Paes (MrPaC6689)                                      ║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
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

print_step() {
    echo -e "${CYAN}🔄 $1${NC}"
}

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        DISTRO="Windows"
    else
        OS="unknown"
        DISTRO="Unknown"
    fi
    
    print_info "Sistema detectado: $DISTRO ($OS)"
}

# Verificar se Python3 está instalado
check_python() {
    print_step "Verificando instalação do Python3..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "Python3 encontrado: $PYTHON_VERSION"
        PYTHON_CMD="python3"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
            print_success "Python3 encontrado: $PYTHON_VERSION"
            PYTHON_CMD="python"
            return 0
        else
            print_error "Python 3 não encontrado. Versão atual: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python3 não está instalado no sistema"
        return 1
    fi
}

# Verificar se pip está instalado
check_pip() {
    print_step "Verificando instalação do pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 encontrado"
        PIP_CMD="pip3"
        return 0
    elif command -v pip &> /dev/null; then
        print_success "pip encontrado"
        PIP_CMD="pip"
        return 0
    else
        print_error "pip não está instalado"
        return 1
    fi
}

# Verificar se venv está disponível
check_venv() {
    print_step "Verificando disponibilidade do venv..."
    
    if $PYTHON_CMD -m venv --help &> /dev/null; then
        print_success "venv está disponível"
        return 0
    else
        print_error "venv não está disponível"
        return 1
    fi
}

# Instalar dependências baseado no sistema operacional
install_dependencies() {
    if ! check_python || ! check_pip || ! check_venv; then
        print_warning "Algumas dependências estão faltando. Tentando instalar..."
        
        case $OS in
            "linux")
                if command -v apt-get &> /dev/null; then
                    print_step "Instalando dependências com apt-get..."
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip python3-venv python3-dev
                elif command -v yum &> /dev/null; then
                    print_step "Instalando dependências com yum..."
                    sudo yum install -y python3 python3-pip python3-venv python3-devel
                elif command -v dnf &> /dev/null; then
                    print_step "Instalando dependências com dnf..."
                    sudo dnf install -y python3 python3-pip python3-venv python3-devel
                elif command -v pacman &> /dev/null; then
                    print_step "Instalando dependências com pacman..."
                    sudo pacman -S python python-pip python-venv
                else
                    print_error "Gerenciador de pacotes não suportado. Por favor, instale Python3, pip e venv manualmente."
                    exit 1
                fi
                ;;
            "macos")
                if command -v brew &> /dev/null; then
                    print_step "Instalando dependências com Homebrew..."
                    brew install python3
                else
                    print_warning "Homebrew não encontrado. Recomendamos instalar o Homebrew:"
                    print_info "Execute: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                    print_info "Depois execute: brew install python3"
                    exit 1
                fi
                ;;
            "windows")
                print_error "No Windows, baixe o Python do site oficial: https://python.org"
                print_info "Certifique-se de marcar 'Add Python to PATH' durante a instalação"
                exit 1
                ;;
            *)
                print_error "Sistema operacional não suportado para instalação automática"
                exit 1
                ;;
        esac
        
        # Verificar novamente após instalação
        if ! check_python || ! check_pip || ! check_venv; then
            print_error "Falha ao instalar dependências. Por favor, instale manualmente."
            exit 1
        fi
    fi
}

# Criar diretório de instalação
create_install_dir() {
    print_step "Criando diretório de instalação..."
    
    # Definir diretório home baseado no sistema
    if [[ $OS == "windows" ]]; then
        HOME_DIR="$USERPROFILE"
    else
        HOME_DIR="$HOME"
    fi
    
    INSTALL_DIR="$HOME_DIR/.autoreg"
    
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "Diretório $INSTALL_DIR já existe. Removendo versão anterior..."
        rm -rf "$INSTALL_DIR"
    fi
    
    mkdir -p "$INSTALL_DIR"
    print_success "Diretório criado: $INSTALL_DIR"
}

# Copiar arquivos
copy_files() {
    print_step "Copiando arquivos do AutoReg..."
    
    # Copiar todos os arquivos exceto alguns desnecessários
    cp -r . "$INSTALL_DIR/"
    
    # Remover arquivos desnecessários
    cd "$INSTALL_DIR"
    rm -rf .git __pycache__ "Versoes Historicas" *.pyc .DS_Store
    
    print_success "Arquivos copiados com sucesso"
}

# Criar ambiente virtual
create_venv() {
    print_step "Criando ambiente virtual..."
    
    cd "$INSTALL_DIR"
    $PYTHON_CMD -m venv venv
    
    if [[ $OS == "windows" ]]; then
        VENV_PYTHON="$INSTALL_DIR/venv/Scripts/python"
        VENV_PIP="$INSTALL_DIR/venv/Scripts/pip"
    else
        VENV_PYTHON="$INSTALL_DIR/venv/bin/python"
        VENV_PIP="$INSTALL_DIR/venv/bin/pip"
    fi
    
    print_success "Ambiente virtual criado"
}

# Instalar dependências Python
install_python_deps() {
    print_step "Instalando dependências Python..."
    
    cd "$INSTALL_DIR"
    
    if [[ -f "requirements.txt" ]]; then
        $VENV_PIP install --upgrade pip
        $VENV_PIP install -r requirements.txt
        print_success "Dependências instaladas com sucesso"
    else
        print_warning "Arquivo requirements.txt não encontrado. Instalando dependências básicas..."
        $VENV_PIP install selenium pandas beautifulsoup4 pillow
    fi
}

# Criar script executável
create_executable() {
    print_step "Criando script executável..."
    
    if [[ $OS == "windows" ]]; then
        # Criar script batch para Windows
        EXEC_SCRIPT="$INSTALL_DIR/autoreg.bat"
        cat > "$EXEC_SCRIPT" << EOF
@echo off
cd /d "$INSTALL_DIR"
"$VENV_PYTHON" autoreg.py %*
EOF
        ALIAS_TARGET="autoreg.bat"
    else
        # Criar script shell para Unix
        EXEC_SCRIPT="$INSTALL_DIR/autoreg"
        cat > "$EXEC_SCRIPT" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
"$VENV_PYTHON" autoreg.py "\$@"
EOF
        chmod +x "$EXEC_SCRIPT"
        ALIAS_TARGET="autoreg"
    fi
    
    print_success "Script executável criado: $EXEC_SCRIPT"
}

# Criar alias no PATH
create_alias() {
    print_step "Configurando alias no PATH..."
    
    case $OS in
        "linux" | "macos")
            # Criar link simbólico em /usr/local/bin
            if [[ -w "/usr/local/bin" ]]; then
                ln -sf "$EXEC_SCRIPT" "/usr/local/bin/autoreg"
                print_success "Alias criado em /usr/local/bin/autoreg"
            else
                # Tentar com sudo
                if sudo ln -sf "$EXEC_SCRIPT" "/usr/local/bin/autoreg" 2>/dev/null; then
                    print_success "Alias criado em /usr/local/bin/autoreg (com sudo)"
                else
                    # Adicionar ao PATH do usuário
                    SHELL_RC=""
                    if [[ -f "$HOME/.bashrc" ]]; then
                        SHELL_RC="$HOME/.bashrc"
                    elif [[ -f "$HOME/.zshrc" ]]; then
                        SHELL_RC="$HOME/.zshrc"
                    elif [[ -f "$HOME/.profile" ]]; then
                        SHELL_RC="$HOME/.profile"
                    fi
                    
                    if [[ -n "$SHELL_RC" ]]; then
                        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
                        print_success "PATH atualizado em $SHELL_RC"
                        print_warning "Execute 'source $SHELL_RC' ou reinicie o terminal"
                    else
                        print_warning "Adicione manualmente ao PATH: export PATH=\"$INSTALL_DIR:\$PATH\""
                    fi
                fi
            fi
            ;;
        "windows")
            print_warning "No Windows, adicione manualmente ao PATH do sistema:"
            print_info "1. Abra as Configurações do Sistema"
            print_info "2. Vá em Variáveis de Ambiente"
            print_info "3. Adicione $INSTALL_DIR ao PATH"
            print_info "Ou execute: setx PATH \"%PATH%;$INSTALL_DIR\""
            ;;
    esac
}

# Função principal
main() {
    print_header
    
    # Detectar sistema operacional
    detect_os
    
    # Verificar e instalar dependências
    install_dependencies
    
    # Criar diretório de instalação
    create_install_dir
    
    # Copiar arquivos
    copy_files
    
    # Criar ambiente virtual
    create_venv
    
    # Instalar dependências Python
    install_python_deps
    
    # Criar script executável
    create_executable
    
    # Criar alias
    create_alias
    
    echo
    print_success "═══════════════════════════════════════════════════════════════"
    print_success "           INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    print_success "═══════════════════════════════════════════════════════════════"
    echo
    print_info "AutoReg foi instalado em: $INSTALL_DIR"
    print_info "Para usar, digite: autoreg --help"
    echo
    print_info "Exemplos de uso:"
    print_info "  autoreg -eci                  # Extrai códigos de internação"
    print_info "  autoreg --all                 # Executa workflow completo"
    print_info "  autoreg --config              # Edita configuração"
    echo
    print_warning "Não esqueça de configurar o arquivo config.ini antes do primeiro uso!"
    print_info "Execute: autoreg --config"
    echo
}

# Verificar se está sendo executado como root (não recomendado)
if [[ $EUID -eq 0 ]] && [[ $OS != "windows" ]]; then
    print_warning "Executando como root não é recomendado para instalação de usuário"
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Instalação cancelada"
        exit 1
    fi
fi

# Executar instalação
main
