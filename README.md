# AutoReg
Operação automatizada de Sistemas de Saúde - SISREG & G-HOSP

## 🌌 Versão 8.0.0 Universe - Julho de 2025

**Coordenador de Workflow Multiplataforma**

- **Autor**: Michel Ribeiro Paes (MrPaC6689)
- **Repositório**: https://github.com/Mrpac6689/AutoReg
- **Contato**: michelrpaes@gmail.com
- **Desenvolvido com**: ChatGPT 4.1 e Claude 3.7 Sonnet
- **Python**: 3.7+ (Compatível com 3.12.8)
- **Plataformas**: Windows, macOS, Linux

---

## 🎯 Principais Novidades da v8.0.0 Universe

### 🔄 **Arquitetura Modular Completa**
- **Refatoração total**: Código dividido em módulos independentes na pasta `autoreg/`
- **Coordenador de Workflow**: `autoreg.py` como orquestrador principal
- **Imports otimizados**: Sistema de importação limpo e organizados

### 🖥️ **Interface de Linha de Comando Avançada**
- **12 funções individuais** com flags específicas (`-eci`, `-ip`, `-eis`, etc.)
- **Execução sequencial**: Múltiplas funções em uma chamada (`autoreg -eci -ip -eis`)
- **Workflow completo**: Flag `--all` executa todas as funções automaticamente
- **Configuração integrada**: `--config` para editar credenciais
- **Gestão de arquivos**: `--directory` para acessar pasta de trabalho

### 🚀 **Sistema de Instalação Universal**
- **Scripts multiplataforma**: `install.sh` (Linux/macOS) e `install.bat` (Windows)
- **Detecção automática**: Sistema operacional, Python, pip e venv
- **Instalação de dependências**: Automática por distro Linux/Homebrew/Manual Windows
- **Ambiente virtual isolado**: Instalação em `~/.autoreg/` sem conflitos
- **PATH global**: Comando `autoreg` disponível globalmente
- **Desinstalação limpa**: Script `uninstall.sh` para remoção completa

### 📋 **Funções Disponíveis**
| Flag | Função | Descrição |
|------|--------|-----------|
| `-eci` | `extrai_codigos_internacao` | Extrai códigos de internação do SISREG |
| `-ip` | `interna_pacientes` | Realiza internação de pacientes no SISREG |
| `-eis` | `extrai_internados_sisreg` | Extrai lista de internados do SISREG |
| `-eig` | `extrai_internados_ghosp` | Extrai lista de internados do G-HOSP |
| `-ci` | `compara_internados` | Compara listas de internados entre sistemas |
| `-ma` | `motivo_alta` | Captura motivos de alta no G-HOSP |
| `-ecsa` | `extrai_codigos_sisreg_alta` | Extrai códigos SISREG para alta |
| `-ea` | `executa_alta` | Executa altas no SISREG |
| `-ar` | `atualiza_restos` | Atualiza arquivo de pacientes restantes |
| `-eid` | `extrai_internacoes_duplicadas` | Identifica internações duplicadas |
| `-td` | `trata_duplicados` | Processa pacientes com duplicações |
| `-dev` | `devolvidos` | Processa solicitações devolvidas |

### 🛠️ **Melhorias Técnicas**
- **Logging estruturado**: Sistema de logs melhorado
- **Tratamento de erros**: Feedback detalhado e recuperação automática
- **Configuração flexível**: Suporte a diferentes ambientes hospitalares
- **Performance otimizada**: Execução mais rápida e eficiente

---

# 📝 Descrição

O **AutoReg v8.0.0 Universe** é um sistema completo de automação para processos hospitalares, oferecendo um **coordenador de workflow inteligente** que integra os sistemas SISREG e G-HOSP. Esta versão representa uma evolução significativa com **arquitetura modular**, **interface de linha de comando avançada** e **instalação universal**.

## 🎯 **Características Principais**

### 🔧 **Coordenador de Workflow**
- **Execução orquestrada**: Controle centralizado de todas as funções
- **Linha de comando intuitiva**: Interface CLI com flags mnêmicas
- **Execução flexível**: Individual, sequencial ou workflow completo
- **Feedback em tempo real**: Progresso detalhado com emojis e cores

### 🏗️ **Arquitetura Modular**
- **Módulos independentes**: Cada função em arquivo separado
- **Imports otimizados**: Sistema de dependências limpo
- **Manutenibilidade**: Código organizado e documentado
- **Escalabilidade**: Fácil adição de novas funcionalidades

### 🌐 **Multiplataforma Universal**
- **Instalação automática**: Scripts para Windows, macOS e Linux
- **Detecção inteligente**: Identificação automática de dependências
- **Ambiente isolado**: Virtual environment dedicado
- **Comando global**: Acesso via `autoreg` de qualquer local

# ⚡ **Funcionalidades Principais**

## 🏥 **Módulo de Internação**
- **Extração automática**: Códigos de internação do SISREG (`-eci`)
- **Internação inteligente**: Processo automatizado de internação (`-ip`)
- **Identificação de duplicatas**: Detecção e tratamento de internações duplicadas (`-eid`, `-td`)

## 🚪 **Módulo de Alta**
- **Comparação de sistemas**: Análise entre SISREG e G-HOSP (`-ci`)
- **Captura de motivos**: Extração automática de motivos de alta (`-ma`)
- **Execução de altas**: Processamento automatizado no SISREG (`-ea`)
- **Gestão de pendências**: Tratamento de pacientes restantes (`-ar`)

## 📊 **Módulo de Dados**
- **Extração SISREG**: Lista completa de internados (`-eis`)
- **Extração G-HOSP**: Lista de pacientes no sistema hospitalar (`-eig`)
- **Códigos para alta**: Extração de códigos SISREG específicos (`-ecsa`)
- **Solicitações devolvidas**: Processamento de devoluções (`-dev`)

## 🔄 **Workflows Inteligentes**
- **Execução individual**: Funções específicas conforme necessidade
- **Execução sequencial**: Múltiplas funções em ordem (`autoreg -eci -ip -eis`)
- **Workflow completo**: Todas as funções automaticamente (`autoreg --all`)
- **Recuperação de erros**: Parada inteligente e relatórios detalhados

# 🚀 Instalação Rápida

## 📋 Pré-requisitos
- Python 3.7+
- pip
- Git (para clonar o repositório)

## ⚡ Instalação Automática

### 🐧 Linux / 🍎 macOS
```bash
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg
./install.sh
```

### 🪟 Windows
```cmd
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg
install.bat
```

## 🎯 Uso Rápido

Após a instalação, use o comando `autoreg` de qualquer lugar no sistema:

### 📋 **Comandos Básicos**
```bash
# Ver todas as opções disponíveis
autoreg --help

# Configurar credenciais de acesso
autoreg --config

# Abrir pasta de arquivos gerados
autoreg --directory
```

### 🔧 **Execução de Funções**
```bash
# Função individual
autoreg -eci                    # Extrai códigos de internação
autoreg -ip                     # Interna pacientes
autoreg -ma                     # Captura motivos de alta

# Múltiplas funções em sequência
autoreg -eci -ip                # Extrai códigos e interna
autoreg -eis -eig -ci           # Extrai listas e compara
autoreg -ma -ecsa -ea           # Workflow de alta completo

# Workflow completo (11 funções automaticamente)
autoreg --all                   # Executa tudo exceto devolvidos

# Função especializada
autoreg -dev                    # Processa devolvidos (separadamente)
```

### 💡 **Exemplos Práticos**
```bash
# Rotina matinal de internação
autoreg -eci -ip -eid -td

# Rotina de alta de pacientes
autoreg -eis -eig -ci -ma -ecsa -ea -ar

# Verificação e limpeza de dados
autoreg -eid -td -ar

# Processamento completo automatizado
autoreg --all && autoreg -dev
```

## 📖 Documentação Completa
- [**INSTALL.md**](INSTALL.md) - Guia detalhado de instalação
- [**Histórico de Versões**](#-histórico-de-versões) - Changelog completo

---

# 💻 Requisitos do Sistema

## 🖥️ **Sistemas Operacionais Suportados**
- **Linux**: Ubuntu 20.04+, Debian 10+, CentOS 8+, Arch Linux
- **macOS**: 10.14+ (Mojave ou superior)
- **Windows**: 10/11 (x64)

## 🐍 **Dependências Python**
- **Python**: 3.7 ou superior (testado até 3.12.8)
- **pip**: Gerenciador de pacotes Python
- **venv**: Ambiente virtual (incluído no Python 3.3+)

## 🌐 **Ferramentas Externas**
- **Google Chrome**: Navegador atualizado (instalação automática do ChromeDriver)
- **Git**: Para clonagem do repositório
- **Conexão à Internet**: Para instalação de dependências

## 🏥 **Acesso aos Sistemas**
- **Credenciais SISREG**: Usuário e senha válidos
- **Credenciais G-HOSP**: Usuário, senha e endereço do servidor
- **Rede hospitalar**: Acesso aos sistemas de gestão hospitalar

---

# ⚙️ Configuração

## 📝 **Configuração de Credenciais**

Após a instalação, configure suas credenciais:

```bash
autoreg --config
```

Edite o arquivo `config.ini` com suas informações:

```ini
[SISREG]
usuario = seu_usuario_sisreg
senha = sua_senha_sisreg

[G-HOSP]
usuario = seu_usuario_ghosp
senha = sua_senha_ghosp
caminho = http://10.0.0.0:4001  # Endereço do seu servidor G-HOSP
```

## 📁 **Estrutura de Arquivos**

Após a instalação, os arquivos ficam organizados em:

```
~/.autoreg/                    # Diretório de instalação
├── autoreg.py                 # Coordenador principal
├── autoreg/                   # Módulos do sistema
│   ├── __init__.py
│   ├── extrai_codigos_internacao.py
│   ├── interna_pacientes.py
│   ├── extrai_internados_sisreg.py
│   ├── extrai_internados_ghosp.py
│   ├── compara_internados.py
│   ├── motivo_alta.py
│   ├── extrai_codigos_sisreg_alta.py
│   ├── executa_alta.py
│   ├── trata_restos.py
│   ├── extrai_internacoes_duplicadas.py
│   ├── trata_duplicados.py
│   ├── devolvidos.py
│   ├── ler_credenciais.py
│   ├── chrome_options.py
│   └── logging.py
├── venv/                      # Ambiente virtual
├── config.ini                 # Configurações (criar após instalação)
└── requirements.txt           # Dependências Python
```

---

# 🔧 Solução de Problemas

## ⚠️ **Erros Comuns**

### 🐍 Python não encontrado
```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install python3 python3-pip python3-venv

# Linux (CentOS/RHEL)
sudo yum install python3 python3-pip

# macOS (com Homebrew)
brew install python3

# Windows
# Baixar de python.org e marcar "Add to PATH"
```

### 🌐 Erro de ChromeDriver
```bash
# O AutoReg baixa automaticamente a versão correta
# Se persistir o erro, atualize o Chrome:
# - Linux: sudo apt update && sudo apt upgrade google-chrome-stable
# - macOS: Atualizar via Chrome ou App Store
# - Windows: Atualizar via Chrome
```

### 🔑 Erro de credenciais
```bash
# Verificar configuração
autoreg --config

# Testar acesso manual aos sistemas
# Verificar se as credenciais estão corretas
```

### 📁 Permissões de arquivo
```bash
# Linux/macOS - Corrigir permissões
chmod +x ~/.autoreg/autoreg
chmod -R 755 ~/.autoreg/

# Verificar proprietário
chown -R $USER:$USER ~/.autoreg/
```

---
  

# 📜 Histórico de Versões

## 🌌 **v8.0.0 Universe** - Julho de 2025
### 🔄 **Refatoração Completa**
- **Arquitetura modular**: Código dividido em módulos independentes na pasta `autoreg/`
- **Coordenador de workflow**: `autoreg.py` como orquestrador principal com CLI avançada
- **12 funções especializadas**: Cada módulo com responsabilidade única
- **Sistema de instalação universal**: Scripts para Windows, macOS e Linux
- **Comando global**: `autoreg` disponível em qualquer local do sistema
- **Ambiente virtual isolado**: Instalação em `~/.autoreg/` sem conflitos
- **Interface CLI intuitiva**: Flags mnêmicas e execução sequencial
- **Documentação completa**: README, INSTALL.md e scripts de exemplo

## 🐧 **v7.0.0-linux** - Maio de 2025
- Reajustado destino do Download na Função Internhosp
- Corrigidos destinos de arquivos temporários para concentrar na pasta ~/AutoReg
- Testes e ajustes de empacotamento e distribuição .deb

## 🔧 **v6.5.1-linux** - Maio de 2025
- Removidos imports de bibliotecas não utilizadas
- Removido argumento `zoomed` do ChromeOptions (incompatível com Linux)
- Adicionado argumento `headless=new` para Chrome em modo oculto
- Ajuste de foco para frame `f_principal` antes de chamar `configFicha`
- Substituídos pop-ups por prints no campo de logs
- Ajustes diversos de caminho de arquivos para ambiente Linux

## 🚀 **v6.0** - 2024
- Implementada função de internação automatizada
- Implementada função de alta automatizada

## 🔧 **v5.1.2** - 2024
- Acrescentados motivos de saída ausentes
- Rotina para execução autônoma do módulo de Alta
- Reduzido tempo para captura de altas

## 📊 **v5.0.1** - 2024
- Funções `captura_cns_restos_alta()`, `motivo_alta_cns()`, `executa_saidas_cns()`
- Estrutura de diretórios com versões anteriores
- Interface do módulo alta redesenhada
- Restaurada função `trazer_terminal()`
- Atualizada para Python 3.13

## 🏥 **v4.2.3** - 2023
- Publicado em PyPI.org
- Pop-ups concentrados em três funções
- Convertido .ico em base64

## 🎯 **v4.0** - 2023
- **Funções de Internação**: Captura automatizada e processo completo
- **Melhorias de Alta**: Configuração HTTP do G-HOSP
- **Módulos independentes**: Internação e Alta separados
- **Compilação binária**: .exe para Windows, .app beta para macOS

## 📝 **v3.0** - 2022
- Extração de códigos de internação SISREG
- Correlação Nome, Motivo de Alta G-HOSP e Código SISREG
- Alta automática conforme motivo capturado
- Interface visual melhorada

## 🔄 **v2.0** - 2021
- Atualização automática do ChromeDriver
- Interface gráfica redesenhada com Tkinter
- Menu "Informações" com documentação integrada

---

# 📄 Licença e Créditos

## 👨‍💻 **Desenvolvimento**
- **Autor Principal**: Michel Ribeiro Paes ([MrPaC6689](https://github.com/MrPaC6689))
- **Contato**: michelrpaes@gmail.com
- **Repositório**: https://github.com/Mrpac6689/AutoReg

## 🤖 **Suporte de IA**
- **ChatGPT 4.1**: Desenvolvimento e arquitetura
- **Claude 3.7 Sonnet**: Refatoração e otimização

## 📜 **Licença**
Este projeto é desenvolvido sob **licença MIT** para fins educacionais e de automação hospitalar. 

### ⚖️ **Termos de Uso**
- ✅ Uso comercial permitido
- ✅ Modificação permitida
- ✅ Distribuição permitida
- ✅ Uso privado permitido
- ❗ Sem garantia explícita
- ❗ Responsabilidade do usuário

## 🏥 **Finalidade**
O AutoReg foi desenvolvido para facilitar e automatizar processos hospitalares, contribuindo para a eficiência dos profissionais de saúde e melhor atendimento aos pacientes.

---

**AutoReg v8.0.0 Universe** - *Automatização inteligente para sistemas de saúde* 🚀

*Esperamos que o AutoReg continue facilitando sua rotina e contribuindo para processos hospitalares mais eficientes!*
