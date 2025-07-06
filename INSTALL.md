# 🚀 AutoReg - Guia de Instalação

## 📋 Pré-requisitos

### 🐧 Linux / 🍎 macOS
- Python 3.7+ 
- pip
- venv (geralmente incluído com Python 3.3+)

### 🪟 Windows
- Python 3.7+ (baixar de [python.org](https://python.org))
- Marcar "Add Python to PATH" durante a instalação

## 🔧 Instalação Automática

### 🐧 Linux / 🍎 macOS
```bash
# Clonar o repositório
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg

# Executar o instalador
./install.sh

# Ou com bash
bash install.sh
```

### 🪟 Windows
```cmd
# Clonar o repositório
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg

# Executar o instalador
install.bat
```

## 📁 O que o instalador faz

1. **Verifica dependências**: Python3, pip e venv
2. **Instala dependências** automaticamente (se necessário)
3. **Cria diretório**: `~/.autoreg` (ou `%USERPROFILE%\.autoreg` no Windows)
4. **Copia arquivos**: Todo o projeto para o diretório de instalação
5. **Cria ambiente virtual**: Isolado para as dependências do projeto
6. **Instala pacotes Python**: Do arquivo `requirements.txt`
7. **Cria executável**: Script que pode ser chamado de qualquer lugar
8. **Configura PATH**: Para usar o comando `autoreg` globalmente

## 🎯 Após a Instalação

### ✅ Verificar instalação
```bash
autoreg --help
```

### ⚙️ Configurar credenciais
```bash
autoreg --config
```

### 📂 Acessar arquivos
```bash
autoreg --directory
```

### 🏃‍♂️ Executar funções
```bash
# Função específica
autoreg -eci

# Múltiplas funções
autoreg -eci -ip -eis

# Workflow completo
autoreg --all
```

## 🗂️ Estrutura de Arquivos

Após a instalação:
```
~/.autoreg/
├── autoreg.py          # Coordenador principal
├── autoreg/            # Módulos do sistema
│   ├── __init__.py
│   ├── extrai_codigos_internacao.py
│   ├── interna_pacientes.py
│   └── ...
├── config.ini          # Configurações (criar após instalação)
├── requirements.txt    # Dependências Python
├── venv/              # Ambiente virtual
└── README.md          # Documentação
```

## 🔧 Instalação Manual (Alternativa)

Se o instalador automático não funcionar:

```bash
# 1. Criar diretório
mkdir ~/.autoreg
cd ~/.autoreg

# 2. Copiar arquivos do projeto
cp -r /caminho/para/AutoReg/* .

# 3. Criar ambiente virtual
python3 -m venv venv

# 4. Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Criar alias (adicionar ao ~/.bashrc ou ~/.zshrc)
echo 'alias autoreg="~/.autoreg/venv/bin/python ~/.autoreg/autoreg.py"' >> ~/.bashrc
```

## 🚨 Solução de Problemas

### Python não encontrado
- **Linux**: `sudo apt install python3 python3-pip python3-venv`
- **macOS**: `brew install python3` (instalar Homebrew primeiro)
- **Windows**: Baixar de [python.org](https://python.org)

### Permissões negadas
```bash
# Dar permissão ao script
chmod +x install.sh

# Executar como usuário normal (não root)
./install.sh
```

### PATH não atualizado
- **Linux/macOS**: `source ~/.bashrc` ou reiniciar terminal
- **Windows**: Reiniciar prompt de comando

### Dependências com falha
```bash
# Instalar manualmente
cd ~/.autoreg
source venv/bin/activate  # Linux/macOS
pip install selenium pandas beautifulsoup4 pillow
```

## 🔄 Desinstalação

```bash
# Remover diretório
rm -rf ~/.autoreg

# Remover do PATH (Linux/macOS)
# Editar ~/.bashrc e remover linha do autoreg

# Windows: Remover do PATH nas variáveis de ambiente
```

## 📞 Suporte

- **GitHub**: [Issues](https://github.com/Mrpac6689/AutoReg/issues)
- **Email**: michelrpaes@gmail.com
- **Documentação**: README.md principal
