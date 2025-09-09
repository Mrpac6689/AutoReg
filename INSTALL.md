# 🚀 AutoReg - Guia de Instalação

## 📋 Pré-requisitos

### 🐧 Linux / 🍎 macOS
- Python 3.7+ instalado

### 🪟 Windows
- Python 3.7+ (baixar de [python.org](https://python.org))
- Marcar "Add Python to PATH" durante a instalação

## 🔧 Instalação Automática (Versão 8.5.0)

### 🐧 Linux / 🍎 macOS
```bash
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg
chmod +x install.sh
./install.sh
```

### 🪟 Windows
```cmd
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg
install.bat
```

## 📁 O que o instalador faz

1. Identifica a pasta do usuário
2. Move os dados da aplicação para `~/.autoreg` (ou `%USERPROFILE%\.autoreg` no Windows)
3. Cria a pasta `~/AutoReg` (ou `%USERPROFILE%\AutoReg`)
4. Cria o arquivo vazio `~/AutoReg/autoreg.log`
5. Acessa o diretório da aplicação
6. Verifica a existência do Python3 (avisa se não houver)
7. Verifica/cria ambiente virtual venv
8. Instala dependências do `requirements.txt` (ou básicas)
9. Determina o caminho absoluto do Python e do script principal
10. Cria alias no terminal (`~/.bashrc` ou `~/.zshrc`) ou script no Windows
11. Adiciona ao PATH (Windows)

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
├── venv/               # Ambiente virtual
└── README.md           # Documentação
~/AutoReg/
└── autoreg.log         # Log de execução
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
source venv/bin/activate

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Criar alias (adicionar ao ~/.bashrc ou ~/.zshrc)
echo 'alias autoreg="~/.autoreg/venv/bin/python3 ~/.autoreg/autoreg.py"' >> ~/.bashrc
```

## 🚨 Solução de Problemas

### Python não encontrado
- **Linux**: `sudo apt install python3 python3-venv`
- **macOS**: `brew install python3` (instalar Homebrew primeiro)
- **Windows**: Baixar de [python.org](https://python.org)

### Permissões negadas
```bash
chmod +x install.sh
./install.sh
```

### PATH/alias não atualizado
- **Linux/macOS**: `source ~/.bashrc` ou reiniciar terminal
- **Windows**: Reiniciar prompt de comando

### Dependências com falha
```bash
cd ~/.autoreg
source venv/bin/activate
pip install selenium pandas beautifulsoup4 pillow
```

## 🔄 Desinstalação

```bash
rm -rf ~/.autoreg ~/AutoReg
# Remover alias do ~/.bashrc ou ~/.zshrc
# Windows: Remover do PATH nas variáveis de ambiente
```

## 📞 Suporte

- **GitHub**: [Issues](https://github.com/Mrpac6689/AutoReg/issues)
- **Email**: michelrpaes@gmail.com
- **Documentação**: README.md principal
