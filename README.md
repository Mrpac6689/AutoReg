# AutoReg
Operação automatizada de Sistemas de Saúde - SISREG & G-HOSP

## 🌌 Versão 9.0.0 Universe - Outubro de 2025

# Instruções de instalação em INSTALL.md

### 🆕 Novas Funcionalidades v9.0.0

- **Workflow de Solicitações**: Nova sequência `-solicita` que executa automaticamente as funções de solicitação `-sia -ssr -snt`
- **Verificação de dados**: Sistema inteligente para detecção e tratamento de dados faltantes nos CSVs
- **Rotina de solicitação**: Nova função `-snt` para inserção de números de solicitação SISREG nas notas de prontuário
- **Tratamento de dados**: Limpeza automática de formatos numéricos (.0) nos códigos de solicitação
- **Dados para revisão**: Marcação automática de registros com dados faltantes para revisão posterior

- **Instalador Universal Refeito**: Scripts `install.sh` (Linux/macOS) e `install.bat` (Windows) totalmente reconstruídos para a versão 8.5.0.
- **Instalação inteligente**: Detecta pasta do usuário, move dados para `~/.autoreg`, cria pasta `~/AutoReg`, gera log vazio, verifica Python3, cria venv se necessário, instala dependências, configura alias global no terminal padrão (bash/zsh).
- **Workflows agrupados**: Novas flags `-interna`, `-analisa`, `-alta` para execução de rotinas agrupadas (internação, análise, alta) diretamente pelo CLI.
- **Ajuda CLI aprimorada**: Todas as flags e agrupamentos agora aparecem corretamente no `--help`.
- **Logs e arquivos**: Criação automática de `autoreg.log` e organização dos arquivos de trabalho.

- **pdf2csv**: Conversão automática de PDF para CSV, extraindo nome, código e data, com limpeza de dados.
- **ghosp_nota**: Automação completa para extração de notas de prontuários do G-HOSP, processando múltiplos códigos do CSV e salvando resultados na coluna 'dados'.
- **Loop automatizado**: Busca sequencial de prontuários e extração de lembretes para todos os códigos presentes em lista_same.csv.
- **Atualização dinâmica do CSV**: Criação automática da coluna 'dados' e salvamento dos resultados extraídos.


### 📋 Funções Disponíveis e Workflows Agrupados

| Flag         | Função                        | Descrição |
|--------------|-------------------------------|-----------|
| `-eci`       | extrai_codigos_internacao     | Extrai códigos de internação do SISREG |
| `-ip`        | interna_pacientes             | Realiza internação de pacientes no SISREG |
| `-eis`       | extrai_internados_sisreg      | Extrai lista de internados do SISREG |
| `-eig`       | extrai_internados_ghosp       | Extrai lista de internados do G-HOSP |
| `-ci`        | compara_internados            | Compara listas de internados entre sistemas |
| `-ma`        | motivo_alta                   | Captura motivos de alta no G-HOSP |
| `-ecsa`      | extrai_codigos_sisreg_alta    | Extrai códigos SISREG para alta |
| `-ea`        | executa_alta                  | Executa altas no SISREG |
| `-ar`        | atualiza_restos               | Atualiza arquivo de pacientes restantes |
| `-eid`       | extrai_internacoes_duplicadas | Identifica internações duplicadas |
| `-td`        | trata_duplicados              | Processa pacientes com duplicações |
| `-dev`       | devolvidos                    | Processa solicitações devolvidas |
| `-p2c`       | pdf2csv                       | Converte PDF de solicitações em CSV |
| `-ghn`       | ghosp_nota                    | Extrair notas de prontuários Ghosp |
| `-especial`   | [workflow agrupado]           | Extração de dados personalizados do GHOSP |
| `-sia`       | solicita_inf_aih             | Extrai informações da AIH |
| `-ssr`       | solicita_sisreg              | Executa Solicitações no Sistema SISREG |
| `-snt`       | solicita_nota                | Insere numero da solicitação SISREG na nota de prontuário |
| `-interna`   | [workflow agrupado]           | Executa rotina de internação completa |
| `-analisa`   | [workflow agrupado]           | Executa rotina de análise/comparação |
| `-alta`      | [workflow agrupado]           | Executa rotina de alta completa |
| `-solicita`  | [workflow agrupado]           | Executa rotina de Solicitação: -sia -ssr -snt |
| `--all`      | [workflow completo]           | Executa todas as funções principais |

### 📜 Histórico de Versões

## 🌌 v9.0.0 Universe - Outubro de 2025

- Nova sequência de workflow `-solicita` para automatizar o processo completo de solicitações
- Nova função `-snt` para inserir números de solicitação SISREG em notas de prontuário
- Sistema inteligente de detecção e tratamento de dados faltantes em CSVs
- Limpeza automática de formatos numéricos (.0) nos códigos de solicitação
- Marcação automática de registros que precisam de revisão
- Interface CLI atualizada com novas opções e feedbacks
- Melhorias na robustez do tratamento de dados

## 🌌 v8.5.0 Universe - Setembro de 2025

- Instalador universal refeito: install.sh (Linux/macOS) e install.bat (Windows) agora detectam pasta do usuário, movem dados para ~/.autoreg, criam pasta ~/AutoReg, geram log, verificam Python3, criam venv, instalam dependências e configuram alias global.
- Novos workflows agrupados: flags -interna, -analisa, -alta para execução de rotinas completas.
- Ajuda CLI aprimorada: todas as flags e agrupamentos aparecem corretamente no --help.
- Função pdf2csv para conversão de PDF em CSV com extração e limpeza de dados.
- Função ghosp_nota para extração automatizada de notas de prontuários do G-HOSP, processando múltiplos códigos do CSV e salvando resultados.
- Loop automatizado para busca sequencial de prontuários e extração de lembretes.
- Atualização dinâmica do CSV com coluna 'dados'.

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


# 🚀 Instalação Rápida (v8.5.0)

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

### 🛠️ O que o instalador faz (v8.5.0)
1. Identifica a pasta do usuário
2. Move os dados da aplicação para `~/.autoreg`
3. Cria a pasta `~/AutoReg`
4. Cria o arquivo vazio `~/AutoReg/autoreg.log`
5. Acessa o diretório da aplicação `~/.autoreg`
6. Verifica a existência do Python3.x, se não houver, avisa o usuário para instalar
7. Verifica a existência do ambiente virtual venv. Se não houver, cria em `~/.autoreg/venv`
8. No ambiente virtual, executa `pip install -r requirements.txt`
9. Determina o caminho absoluto de `~/.autoreg/venv/bin/python3` e de `~/.autoreg/autoreg.py`
10. Identifica o terminal padrão, bash ou zsh
11. Acrescenta em `~/.bashrc` ou `~/.zshrc` o alias para execução global:
	```bash
	alias autoreg="/caminho/absoluto/venv/bin/python3 /caminho/absoluto/.autoreg/autoreg.py"
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


### 🔧 **Execução de Funções e Workflows Agrupados**
```bash
# Função individual
autoreg -eci                    # Extrai códigos de internação
autoreg -ip                     # Interna pacientes
autoreg -ma                     # Captura motivos de alta
autoreg -snt                    # Insere número da solicitação na nota

# Múltiplas funções em sequência
autoreg -eci -ip                # Extrai códigos e interna
autoreg -eis -eig -ci           # Extrai listas e compara
autoreg -ma -ecsa -ea           # Workflow de alta completo
autoreg -sia -ssr -snt          # Workflow de solicitação manual

# Workflows agrupados
autoreg -interna                # Executa rotina de internação completa
autoreg -analisa                # Executa rotina de análise/comparação
autoreg -alta                   # Executa rotina de alta completa
autoreg -solicita              # Executa rotina de solicitação completa

# Workflow completo (todas as funções principais)
autoreg --all                   # Executa tudo exceto devolvidos

# Função especializada
autoreg -dev                    # Processa devolvidos (separadamente)
```

### 💡 **Exemplos Práticos**
```bash
# Rotina matinal de internação
autoreg -interna

# Rotina de alta de pacientes
autoreg -alta

# Rotina de análise/comparação
autoreg -analisa

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
