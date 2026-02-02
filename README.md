# AutoReg

**Sistema de Automação para Operação de Sistemas de Saúde - SISREG & G-HOSP**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/Version-9.7.0-orange.svg)](https://github.com/Mrpac6689/AutoReg)

---

## 📋 Índice

- [Sobre o AutoReg](#sobre-o-autoreg)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Integração com KASM Workspaces](#integração-com-kasm-workspaces)
- [Interface Web - Autoreg-WEB](#interface-web---autoreg-web)
- [Instalação](#instalação)
- [Uso](#uso)
- [Configuração](#configuração)
- [Licença](#licença)
- [Contribuindo](#contribuindo)
- [Contato](#contato)

---

## 🌟 Sobre o AutoReg

O **AutoReg** é uma solução completa de automação desenvolvida especificamente para otimizar e automatizar processos operacionais em sistemas de saúde, com foco na integração entre os sistemas **SISREG** (Sistema de Regulação) e **G-HOSP** (Sistema de Gestão Hospitalar).

Desenvolvido com uma arquitetura modular e interface de linha de comando intuitiva, o AutoReg permite que profissionais de saúde e equipes administrativas hospitalares automatizem tarefas repetitivas e complexas, reduzindo significativamente o tempo de processamento e minimizando erros manuais.

### 🎯 Objetivos Principais

- **Automatização Completa**: Reduzir a necessidade de intervenção manual em processos rotineiros
- **Integração de Sistemas**: Facilitar a comunicação e sincronização entre SISREG e G-HOSP
- **Eficiência Operacional**: Aumentar a produtividade das equipes hospitalares
- **Confiabilidade**: Garantir precisão e consistência nas operações automatizadas
- **Flexibilidade**: Suportar diferentes ambientes e configurações hospitalares

---

## ⚡ Funcionalidades Principais

### 🏥 Módulo de Internação

- **Extração Automática de Códigos** (`-eci`): Coleta códigos de internação diretamente do SISREG
- **Internação Automatizada** (`-ip`): Processa internações de pacientes de forma automatizada
- **Detecção de Duplicatas** (`-eid`, `-td`): Identifica e trata internações duplicadas automaticamente
- **Extração Avançada** (`-iga`): Extrai dados detalhados de pacientes internados no G-HOSP

### 🚪 Módulo de Alta

- **Comparação de Sistemas** (`-ci`): Compara listas de internados entre SISREG e G-HOSP
- **Captura de Motivos** (`-ma`): Extrai automaticamente motivos de alta do G-HOSP
- **Tratamento de Altas** (`-tat`): Processa e organiza motivos de alta capturados
- **Execução de Altas** (`-ea`): Realiza altas no SISREG de forma automatizada
- **Gestão de Pendências** (`-ar`): Atualiza e gerencia pacientes restantes

### 📊 Módulo de Dados e Relatórios

- **Extração SISREG** (`-eis`): Extrai listas completas de internados do SISREG
- **Extração G-HOSP** (`-eig`): Coleta dados de pacientes do sistema hospitalar
- **Produção Ambulatorial** (`-pra`, `-pad`): Extrai códigos e dados detalhados de produção ambulatorial
- **Produção GMUs** (`-pag`): Extração especializada para Gestão de Múltiplas Unidades
- **Consulta de Status** (`-css`): Consulta status de solicitações no SISREG

### 🔬 Módulo de Exames Ambulatoriais

- **Extração de Exames** (`-eae`): Extrai dados de exames a solicitar do G-HOSP
- **Solicitação Automatizada** (`-eas`): Executa solicitações de exames no SISREG
- **Geração de Relatórios** (`-ear`): Gera PDFs unificados de solicitações de exames

### 📋 Módulo de Solicitações e AIHs

- **Solicitação de AIH** (`-sia`): Extrai informações de Autorização de Internação Hospitalar
- **Processamento SISREG** (`-ssr`): Executa solicitações no sistema SISREG
- **Tratamento de Dados** (`-std`): Ajusta e organiza dados para processamento
- **Extração de Links** (`-spa`): Extrai links de formulários do G-HOSP
- **Inserção de Notas** (`-snt`): Insere números de solicitação em notas de prontuário

### 🔄 Workflows Agrupados

- **`-interna`**: Executa rotina completa de internação
- **`-analisa`**: Executa análise e comparação entre sistemas
- **`-alta`**: Executa rotina completa de alta (inclui tratamento e limpeza)
- **`-solicita`**: Executa rotina completa de solicitação
- **`-aihs`**: Executa rotina completa de processamento de AIHs
- **`--all`**: Executa todas as funções principais com repetição interativa

### 🛠️ Utilitários

- **Limpeza de Cache** (`-clc`): Limpa arquivos temporários mantendo dados importantes
- **Processamento de Devolvidos** (`-dev`): Trata solicitações devolvidas
- **Conversão PDF para CSV** (`-p2c`): Converte PDFs de solicitações em formato CSV
- **Extração de Notas** (`-ghn`): Extrai notas de prontuários do G-HOSP
- **Extração de CNS** (`-ghc`): Extrai números de CNS dos prontuários

---

## 🛠️ Tecnologias Utilizadas

O AutoReg é construído utilizando uma stack tecnológica moderna e robusta, garantindo alta performance, confiabilidade e facilidade de manutenção:

### 🐍 Linguagem e Ambiente

- **Python 3.7+** (compatível até 3.13): Linguagem principal de desenvolvimento
- **Virtual Environment (venv)**: Isolamento de dependências
- **ConfigParser**: Gerenciamento de configurações

### 🌐 Automação Web

- **Selenium 4.32.0**: Framework principal para automação de navegadores
  - Automação de interações com sistemas web
  - Navegação e preenchimento de formulários
  - Extração de dados de páginas dinâmicas
- **ChromeDriver**: Driver para automação do Google Chrome
- **BeautifulSoup4 4.13.4**: Parsing e extração de dados HTML/XML
- **Requests 2.32.3**: Cliente HTTP para comunicação com APIs

### 📊 Processamento de Dados

- **Pandas 2.2.3**: Manipulação e análise de dados estruturados
  - Leitura e escrita de arquivos CSV
  - Transformação e limpeza de dados
  - Operações de agregação e filtragem
- **NumPy 2.2.5**: Computação numérica e operações matemáticas
- **Python-dateutil 2.9.0**: Manipulação avançada de datas e horários
- **Pytz 2025.2**: Suporte a fusos horários

### 📄 Processamento de Documentos

- **PyPDF2**: Manipulação de arquivos PDF
- **pdf2image 1.17.0**: Conversão de PDFs para imagens
- **Pillow 11.2.1**: Processamento de imagens
- **Pytesseract 0.3.13**: OCR (Optical Character Recognition) para extração de texto de imagens

### 🖥️ Interface e Interação

- **Pyperclip 1.9.0**: Manipulação da área de transferência
- **Pynput**: Controle de mouse e teclado
- **PyScreeze 1.0.1**: Captura de telas
- **PyRect 0.2.0**: Manipulação de coordenadas e retângulos
- **Pytweening 1.2.0**: Animações e transições suaves

### 🔐 Segurança e Comunicação

- **Certifi 2025.4.26**: Certificados SSL/TLS
- **Urllib3 2.4.0**: Cliente HTTP de baixo nível
- **WebSocket-client 1.8.0**: Comunicação WebSocket
- **Trio 0.30.0**: Framework assíncrono para I/O
- **Trio-websocket 0.12.2**: WebSocket assíncrono

### 🐳 Containerização e Deploy

- **Docker**: Empacotamento em containers
- **Kasm Workspaces**: Integração com ambientes VNC/noVNC para sistemas headless

### 📦 Outras Dependências

- **Attrs 25.3.0**: Classes de dados e validação
- **Charset-normalizer 3.4.2**: Detecção de encoding
- **Exceptiongroup 1.3.0**: Tratamento de exceções agrupadas
- **Sortedcontainers 2.4.0**: Estruturas de dados ordenadas
- **Zope.interface 7.2**: Sistema de interfaces

---

## 🖥️ Integração com KASM Workspaces

O AutoReg oferece suporte completo para execução em ambientes **headless** através da integração com **KASM Workspaces**, permitindo que o sistema seja executado em servidores sem interface gráfica, acessível remotamente via VNC/noVNC.

### 🎯 Benefícios da Integração KASM

- **Execução em Servidores**: Permite rodar o AutoReg em servidores sem interface gráfica
- **Acesso Remoto**: Interface gráfica acessível via navegador web através do noVNC
- **Centralização**: Gerenciamento centralizado de múltiplas instâncias
- **Isolamento**: Cada execução roda em um container isolado
- **Escalabilidade**: Fácil escalonamento horizontal conforme demanda

### 🐳 Configuração Docker + KASM

O projeto inclui um Dockerfile otimizado baseado na imagem oficial do Kasm Workspaces (`kasmweb/ubuntu-jammy-desktop`), que inclui:

- Ambiente gráfico completo (XFCE Desktop)
- Servidor VNC/noVNC configurado
- Google Chrome e ChromeDriver pré-instalados
- Todas as dependências Python necessárias
- Estrutura de diretórios do AutoReg configurada

### 📝 Como Usar com KASM

1. **Construir a Imagem Docker**:
   ```bash
   cd empacotar_kasmvnc
   docker build -t autoreg-kasm:latest .
   ```

2. **Registrar no Kasm Workspaces**:
   - Importe a imagem no painel administrativo do Kasm
   - Configure as portas VNC/noVNC necessárias
   - Defina recursos (CPU, memória) conforme necessário

3. **Configurar Volumes**:
   - Mapeie volumes para persistência de dados (`~/AutoReg`, `~/.autoreg`)
   - Configure variáveis de ambiente para credenciais (usando Kasm Secrets)

4. **Acessar via Interface Web**:
   - Acesse o workspace através do painel do Kasm
   - Interface gráfica disponível via noVNC no navegador
   - Execute o AutoReg normalmente através do terminal

### 🔒 Segurança

- **Credenciais Protegidas**: Use Kasm Secrets para gerenciar credenciais sensíveis
- **Isolamento de Rede**: Containers isolados com controle de acesso
- **SSL/TLS**: Comunicação segura via HTTPS
- **Auditoria**: Logs de acesso e execução disponíveis

Para mais detalhes sobre a configuração, consulte a pasta `empacotar_kasmvnc/` no repositório.

---

## 🌐 Interface Web - Autoreg-WEB

O AutoReg possui uma **interface web complementar** que oferece uma experiência visual e interativa para gerenciamento e operação do sistema através de chamadas de API.

### 🔗 Autoreg-WEB

**Repositório**: [github.com/mrpac6689/web-autoreg](https://github.com/mrpac6689/web-autoreg)

O **Autoreg-WEB** é uma aplicação web desenvolvida para fornecer:

- **Dashboard Interativo**: Visualização de estatísticas e métricas em tempo real
- **Gerenciamento de Rotinas**: Interface gráfica para executar workflows do AutoReg
- **Monitoramento**: Acompanhamento de execuções e logs
- **Configuração Visual**: Interface para gerenciar credenciais e configurações
- **Relatórios**: Geração e visualização de relatórios de produção
- **API RESTful**: Endpoints para integração com outros sistemas

### 🚀 Funcionalidades do Autoreg-WEB

- Execução de rotinas via interface web
- Visualização de logs em tempo real
- Gerenciamento de arquivos CSV gerados
- Configuração de credenciais de forma segura
- Histórico de execuções
- Estatísticas e gráficos de produção

### 🔌 Integração

O AutoReg pode enviar relatórios de produção para o Autoreg-WEB através da flag `-R` (registro de produção), que envia dados via API REST para registro e análise.

Para mais informações e documentação completa, visite o repositório do [Autoreg-WEB](https://github.com/mrpac6689/web-autoreg).

---

## 🚀 Instalação

### 📋 Pré-requisitos

- **Python 3.7 ou superior** (testado até Python 3.13)
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonar o repositório)
- **Google Chrome** (navegador atualizado)
- **Conexão à Internet** (para instalação de dependências)

### Passo-a-passo:

```bash
# Clone o repositório
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg

# Crie o ambiente virtual
python3 -m venv ~/.autoreg/venv

# Ative o ambiente virtual
source ~/.autoreg/venv/bin/activate  # Linux/macOS
# ou
~/.autoreg/venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o alias (Linux/macOS)
echo 'alias autoreg="~/.autoreg/venv/bin/python3 ~/.autoreg/autoreg.py"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📖 Uso

### 🎯 Comandos Básicos

```bash
# Ver todas as opções disponíveis
autoreg --help

# Configurar credenciais de acesso
autoreg --config

# Abrir pasta de arquivos gerados
autoreg --directory
```

### 🔧 Execução de Funções Individuais

```bash
# Extração de códigos de internação
autoreg -eci

# Internação de pacientes
autoreg -ip

# Captura de motivos de alta
autoreg -ma

# Tratamento de altas
autoreg -tat

# Limpeza de cache
autoreg -clc
```

### 🔄 Execução de Workflows Agrupados

```bash
# Rotina completa de internação
autoreg -interna

# Rotina de análise/comparação
autoreg -analisa

# Rotina completa de alta (inclui tratamento e limpeza)
autoreg -alta

# Rotina completa de solicitação
autoreg -solicita

# Rotina completa de AIHs
autoreg -aihs

# Executa todas as funções principais com repetição interativa
autoreg --all
```

### 📤 Registro de Produção na API

```bash
# Executa solicitação e envia relatório para AUTOREG-API
autoreg -solicita -R

# Executa internação e envia relatório
autoreg -interna -R

# Executa alta e envia relatório
autoreg -alta -R
```

### 💡 Exemplos Práticos

```bash
# Rotina matinal de internação
autoreg -interna

# Rotina de alta de pacientes (com tratamento e limpeza)
autoreg -alta

# Sistema completo de exames ambulatoriais
autoreg -eae    # Extrai dados de exames
autoreg -eas    # Executa solicitações
autoreg -ear    # Gera relatórios PDF

# Extração de produção ambulatorial
autoreg -pra    # Extrai códigos (com checkpoint)
autoreg -pad    # Extrai dados detalhados
```

---

## ⚙️ Configuração

### 📝 Configuração de Credenciais

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

[AUTOREG-API]   # Opcional: para registro de produção com a flag -R
autoreg_api_key = sua_chave_api
autoreg_api_relatorio_url = https://exemplo.com/api/externa/relatorio/registrar
```

### 📁 Estrutura de Arquivos

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

~/AutoReg/                     # Diretório de trabalho
├── autoreg.log                # Arquivo de log
├── *.csv                      # Arquivos CSV gerados
└── *.pdf                      # Arquivos PDF gerados
```

---

## 📜 Licença

Este projeto é licenciado sob a **GNU General Public License v3.0 (GPL-3.0)**.

### 📄 Termos da Licença GPL v3

A GPL é uma licença de software livre que garante aos usuários as seguintes liberdades:

- ✅ **Liberdade 0**: Executar o programa para qualquer propósito
- ✅ **Liberdade 1**: Estudar como o programa funciona e adaptá-lo às suas necessidades
- ✅ **Liberdade 2**: Redistribuir cópias do programa
- ✅ **Liberdade 3**: Melhorar o programa e liberar suas melhorias ao público

### ⚖️ O que isso Significa

- **Uso Comercial**: Permitido
- **Modificação**: Permitida
- **Distribuição**: Permitida
- **Uso Privado**: Permitido
- **Patente**: Qualquer patente deve ser licenciada para uso livre
- **Licenciamento de Código Derivado**: Qualquer código derivado deve usar a mesma licença GPL v3

### 📋 Condições

Ao usar, modificar ou distribuir este software, você concorda em:

1. Manter os avisos de copyright e licença
2. Disponibilizar o código-fonte completo
3. Licenciar trabalhos derivados sob a GPL v3
4. Incluir uma cópia da licença GPL v3

### 📖 Texto Completo da Licença

Para o texto completo da licença GNU GPL v3, consulte:
- [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)
- Arquivo `LICENSE` no repositório

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você deseja contribuir com o projeto:

1. **Fork** o repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. **Push** para a branch (`git push origin feature/MinhaFeature`)
5. Abra um **Pull Request**

### 📝 Diretrizes de Contribuição

- Mantenha o código limpo e documentado
- Siga os padrões de código existentes
- Adicione testes quando apropriado
- Atualize a documentação conforme necessário
- Respeite a licença GPL v3

---

## 📞 Contato

### 👨‍💻 Desenvolvedor Principal

- **Nome**: Michel Ribeiro Paes
- **GitHub**: [@Mrpac6689](https://github.com/Mrpac6689)
- **Email**: michelrpaes@gmail.com

### 🔗 Links Úteis

- **Repositório**: [github.com/Mrpac6689/AutoReg](https://github.com/Mrpac6689/AutoReg)
- **Interface Web**: [github.com/mrpac6689/web-autoreg](https://github.com/mrpac6689/web-autoreg)
- **Issues**: [github.com/Mrpac6689/AutoReg/issues](https://github.com/Mrpac6689/AutoReg/issues)

### 🤖 Desenvolvido com Suporte de IA

- **ChatGPT 4.1**: Desenvolvimento e arquitetura
- **Claude 3.7 Sonnet**: Refatoração e otimização

---

## 📚 Documentação Adicional

- [CHANGELOG.md](CHANGELOG.md) - Histórico completo de versões e mudanças
- [LICENSE](LICENSE) - Texto completo da licença GNU GPL v3

---

## 🎯 Finalidade

O AutoReg foi desenvolvido para facilitar e automatizar processos hospitalares, contribuindo para a eficiência dos profissionais de saúde e melhor atendimento aos pacientes. Este software visa reduzir a carga de trabalho manual, minimizar erros e permitir que as equipes hospitalares se concentrem em atividades que requerem atenção humana.

---

**AutoReg v9.7.0 Universe** - *Automatização inteligente para sistemas de saúde* 🚀

*Esperamos que o AutoReg continue facilitando sua rotina e contribuindo para processos hospitalares mais eficientes!*

---

---

# AutoReg

**Automated System Operation for Healthcare Systems - SISREG & G-HOSP**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/Version-9.7.0-orange.svg)](https://github.com/Mrpac6689/AutoReg)

---

## 📋 Table of Contents

- [About AutoReg](#about-autoreg)
- [Main Features](#main-features)
- [Technologies Used](#technologies-used)
- [KASM Workspaces Integration](#kasm-workspaces-integration)
- [Web Interface - Autoreg-WEB](#web-interface---autoreg-web)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

---

## 🌟 About AutoReg

**AutoReg** is a complete automation solution specifically developed to optimize and automate operational processes in healthcare systems, focusing on integration between **SISREG** (Regulation System) and **G-HOSP** (Hospital Management System).

Developed with a modular architecture and intuitive command-line interface, AutoReg allows healthcare professionals and hospital administrative teams to automate repetitive and complex tasks, significantly reducing processing time and minimizing manual errors.

### 🎯 Main Objectives

- **Complete Automation**: Reduce the need for manual intervention in routine processes
- **System Integration**: Facilitate communication and synchronization between SISREG and G-HOSP
- **Operational Efficiency**: Increase productivity of hospital teams
- **Reliability**: Ensure accuracy and consistency in automated operations
- **Flexibility**: Support different environments and hospital configurations

---

## ⚡ Main Features

### 🏥 Admission Module

- **Automatic Code Extraction** (`-eci`): Collects admission codes directly from SISREG
- **Automated Admission** (`-ip`): Processes patient admissions automatically
- **Duplicate Detection** (`-eid`, `-td`): Identifies and handles duplicate admissions automatically
- **Advanced Extraction** (`-iga`): Extracts detailed data from patients admitted in G-HOSP

### 🚪 Discharge Module

- **System Comparison** (`-ci`): Compares lists of admitted patients between SISREG and G-HOSP
- **Reason Capture** (`-ma`): Automatically extracts discharge reasons from G-HOSP
- **Discharge Processing** (`-tat`): Processes and organizes captured discharge reasons
- **Discharge Execution** (`-ea`): Performs discharges in SISREG automatically
- **Pending Management** (`-ar`): Updates and manages remaining patients

### 📊 Data and Reports Module

- **SISREG Extraction** (`-eis`): Extracts complete lists of admitted patients from SISREG
- **G-HOSP Extraction** (`-eig`): Collects patient data from the hospital system
- **Outpatient Production** (`-pra`, `-pad`): Extracts codes and detailed data from outpatient production
- **GMUs Production** (`-pag`): Specialized extraction for Multiple Units Management
- **Status Query** (`-css`): Queries request status in SISREG

### 🔬 Outpatient Exams Module

- **Exam Extraction** (`-eae`): Extracts exam data to request from G-HOSP
- **Automated Request** (`-eas`): Executes exam requests in SISREG
- **Report Generation** (`-ear`): Generates unified PDFs of exam requests

### 📋 Requests and AIHs Module

- **AIH Request** (`-sia`): Extracts Hospital Admission Authorization information
- **SISREG Processing** (`-ssr`): Executes requests in the SISREG system
- **Data Processing** (`-std`): Adjusts and organizes data for processing
- **Link Extraction** (`-spa`): Extracts form links from G-HOSP
- **Note Insertion** (`-snt`): Inserts request numbers in medical record notes

### 🔄 Grouped Workflows

- **`-interna`**: Executes complete admission routine
- **`-analisa`**: Executes analysis and comparison between systems
- **`-alta`**: Executes complete discharge routine (includes processing and cleanup)
- **`-solicita`**: Executes complete request routine
- **`-aihs`**: Executes complete AIH processing routine
- **`--all`**: Executes all main functions with interactive repetition

### 🛠️ Utilities

- **Cache Cleanup** (`-clc`): Cleans temporary files keeping important data
- **Returned Processing** (`-dev`): Handles returned requests
- **PDF to CSV Conversion** (`-p2c`): Converts request PDFs to CSV format
- **Note Extraction** (`-ghn`): Extracts notes from G-HOSP medical records
- **CNS Extraction** (`-ghc`): Extracts CNS numbers from medical records

---

## 🛠️ Technologies Used

AutoReg is built using a modern and robust technology stack, ensuring high performance, reliability, and ease of maintenance:

### 🐍 Language and Environment

- **Python 3.7+** (compatible up to 3.13): Main development language
- **Virtual Environment (venv)**: Dependency isolation
- **ConfigParser**: Configuration management

### 🌐 Web Automation

- **Selenium 4.32.0**: Main framework for browser automation
  - Automation of web system interactions
  - Navigation and form filling
  - Data extraction from dynamic pages
- **ChromeDriver**: Driver for Google Chrome automation
- **BeautifulSoup4 4.13.4**: HTML/XML parsing and data extraction
- **Requests 2.32.3**: HTTP client for API communication

### 📊 Data Processing

- **Pandas 2.2.3**: Structured data manipulation and analysis
  - CSV file reading and writing
  - Data transformation and cleaning
  - Aggregation and filtering operations
- **NumPy 2.2.5**: Numerical computation and mathematical operations
- **Python-dateutil 2.9.0**: Advanced date and time manipulation
- **Pytz 2025.2**: Timezone support

### 📄 Document Processing

- **PyPDF2**: PDF file manipulation
- **pdf2image 1.17.0**: PDF to image conversion
- **Pillow 11.2.1**: Image processing
- **Pytesseract 0.3.13**: OCR (Optical Character Recognition) for text extraction from images

### 🖥️ Interface and Interaction

- **Pyperclip 1.9.0**: Clipboard manipulation
- **Pynput**: Mouse and keyboard control
- **PyScreeze 1.0.1**: Screen capture
- **PyRect 0.2.0**: Coordinate and rectangle manipulation
- **Pytweening 1.2.0**: Smooth animations and transitions

### 🔐 Security and Communication

- **Certifi 2025.4.26**: SSL/TLS certificates
- **Urllib3 2.4.0**: Low-level HTTP client
- **WebSocket-client 1.8.0**: WebSocket communication
- **Trio 0.30.0**: Asynchronous I/O framework
- **Trio-websocket 0.12.2**: Asynchronous WebSocket

### 🐳 Containerization and Deploy

- **Docker**: Container packaging
- **Kasm Workspaces**: Integration with VNC/noVNC environments for headless systems

### 📦 Other Dependencies

- **Attrs 25.3.0**: Data classes and validation
- **Charset-normalizer 3.4.2**: Encoding detection
- **Exceptiongroup 1.3.0**: Grouped exception handling
- **Sortedcontainers 2.4.0**: Ordered data structures
- **Zope.interface 7.2**: Interface system

---

## 🖥️ KASM Workspaces Integration

AutoReg offers complete support for execution in **headless** environments through integration with **KASM Workspaces**, allowing the system to run on servers without a graphical interface, accessible remotely via VNC/noVNC.

### 🎯 Benefits of KASM Integration

- **Server Execution**: Allows running AutoReg on servers without a graphical interface
- **Remote Access**: Graphical interface accessible via web browser through noVNC
- **Centralization**: Centralized management of multiple instances
- **Isolation**: Each execution runs in an isolated container
- **Scalability**: Easy horizontal scaling according to demand

### 🐳 Docker + KASM Configuration

The project includes an optimized Dockerfile based on the official Kasm Workspaces image (`kasmweb/ubuntu-jammy-desktop`), which includes:

- Complete graphical environment (XFCE Desktop)
- Configured VNC/noVNC server
- Pre-installed Google Chrome and ChromeDriver
- All necessary Python dependencies
- Configured AutoReg directory structure

### 📝 How to Use with KASM

1. **Build Docker Image**:
   ```bash
   cd empacotar_kasmvnc
   docker build -t autoreg-kasm:latest .
   ```

2. **Register in Kasm Workspaces**:
   - Import the image in the Kasm administrative panel
   - Configure necessary VNC/noVNC ports
   - Set resources (CPU, memory) as needed

3. **Configure Volumes**:
   - Map volumes for data persistence (`~/AutoReg`, `~/.autoreg`)
   - Configure environment variables for credentials (using Kasm Secrets)

4. **Access via Web Interface**:
   - Access the workspace through the Kasm panel
   - Graphical interface available via noVNC in the browser
   - Run AutoReg normally through the terminal

### 🔒 Security

- **Protected Credentials**: Use Kasm Secrets to manage sensitive credentials
- **Network Isolation**: Isolated containers with access control
- **SSL/TLS**: Secure communication via HTTPS
- **Auditing**: Access and execution logs available

For more details on configuration, see the `empacotar_kasmvnc/` folder in the repository.

---

## 🌐 Web Interface - Autoreg-WEB

AutoReg has a **complementary web interface** that provides a visual and interactive experience for system management and operation through API calls.

### 🔗 Autoreg-WEB

**Repository**: [github.com/mrpac6689/autoreg-web](https://github.com/mrpac6689/autoreg-web)

**Autoreg-WEB** is a web application developed to provide:

- **Interactive Dashboard**: Real-time statistics and metrics visualization
- **Routine Management**: Graphical interface to execute AutoReg workflows
- **Monitoring**: Execution and log tracking
- **Visual Configuration**: Interface to manage credentials and settings
- **Reports**: Production report generation and visualization
- **RESTful API**: Endpoints for integration with other systems

### 🚀 Autoreg-WEB Features

- Routine execution via web interface
- Real-time log visualization
- CSV file management
- Secure credential configuration
- Execution history
- Production statistics and charts

### 🔌 Integration

AutoReg can send production reports to Autoreg-WEB through the `-R` flag (production registration), which sends data via REST API for registration and analysis.

For more information and complete documentation, visit the [Autoreg-WEB](https://github.com/mrpac6689/autoreg-web) repository.

---

## 🚀 Installation

### 📋 Prerequisites

- **Python 3.7 or higher** (tested up to Python 3.13)
- **pip** (Python package manager)
- **Git** (to clone the repository)
- **Google Chrome** (updated browser)
- **Internet Connection** (for dependency installation)

### ⚡ Automatic Installation

#### 🐧 Linux / 🍎 macOS

```bash
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg
chmod +x install.sh
./install.sh
```

#### 🪟 Windows

```cmd
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg
install.bat
```

### 🛠️ What the Installer Does

The automatic installation script performs the following operations:

1. ✅ Identifies the user's home directory
2. ✅ Moves application data to `~/.autoreg`
3. ✅ Creates the `~/AutoReg` folder for work files
4. ✅ Creates the log file `~/AutoReg/autoreg.log`
5. ✅ Verifies Python 3.x existence
6. ✅ Creates virtual environment (`venv`) in `~/.autoreg/venv`
7. ✅ Installs all dependencies from `requirements.txt`
8. ✅ Configures global alias for the `autoreg` command
9. ✅ Makes the command available from any system directory

### 📦 Manual Installation

If you prefer to install manually:

```bash
# Clone the repository
git clone https://github.com/Mrpac6689/AutoReg.git
cd AutoReg

# Create virtual environment
python3 -m venv ~/.autoreg/venv

# Activate virtual environment
source ~/.autoreg/venv/bin/activate  # Linux/macOS
# or
~/.autoreg/venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure alias (Linux/macOS)
echo 'alias autoreg="~/.autoreg/venv/bin/python3 ~/.autoreg/autoreg.py"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📖 Usage

### 🎯 Basic Commands

```bash
# View all available options
autoreg --help

# Configure access credentials
autoreg --config

# Open generated files folder
autoreg --directory
```

### 🔧 Individual Function Execution

```bash
# Extract admission codes
autoreg -eci

# Admit patients
autoreg -ip

# Capture discharge reasons
autoreg -ma

# Process discharges
autoreg -tat

# Clean cache
autoreg -clc
```

### 🔄 Grouped Workflow Execution

```bash
# Complete admission routine
autoreg -interna

# Analysis/comparison routine
autoreg -analisa

# Complete discharge routine (includes processing and cleanup)
autoreg -alta

# Complete request routine
autoreg -solicita

# Complete AIH routine
autoreg -aihs

# Execute all main functions with interactive repetition
autoreg --all
```

### 📤 Production Registration in API

```bash
# Execute request and send report to AUTOREG-API
autoreg -solicita -R

# Execute admission and send report
autoreg -interna -R

# Execute discharge and send report
autoreg -alta -R
```

### 💡 Practical Examples

```bash
# Morning admission routine
autoreg -interna

# Patient discharge routine (with processing and cleanup)
autoreg -alta

# Complete outpatient exam system
autoreg -eae    # Extract exam data
autoreg -eas    # Execute requests
autoreg -ear    # Generate PDF reports

# Outpatient production extraction
autoreg -pra    # Extract codes (with checkpoint)
autoreg -pad    # Extract detailed data
```

---

## ⚙️ Configuration

### 📝 Credential Configuration

After installation, configure your credentials:

```bash
autoreg --config
```

Edit the `config.ini` file with your information:

```ini
[SISREG]
usuario = your_sisreg_user
senha = your_sisreg_password

[G-HOSP]
usuario = your_ghosp_user
senha = your_ghosp_password
caminho = http://10.0.0.0:4001  # Your G-HOSP server address

[AUTOREG-API]   # Optional: for production registration with -R flag
autoreg_api_key = your_api_key
autoreg_api_relatorio_url = https://example.com/api/externa/relatorio/registrar
```

### 📁 File Structure

```
~/.autoreg/                    # Installation directory
├── autoreg.py                 # Main coordinator
├── autoreg/                   # System modules
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
├── venv/                      # Virtual environment
├── config.ini                 # Configuration (create after installation)
└── requirements.txt           # Python dependencies

~/AutoReg/                     # Work directory
├── autoreg.log                # Log file
├── *.csv                      # Generated CSV files
└── *.pdf                      # Generated PDF files
```

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

### 📄 GPL v3 License Terms

GPL is a free software license that guarantees users the following freedoms:

- ✅ **Freedom 0**: Run the program for any purpose
- ✅ **Freedom 1**: Study how the program works and adapt it to your needs
- ✅ **Freedom 2**: Redistribute copies of the program
- ✅ **Freedom 3**: Improve the program and release your improvements to the public

### ⚖️ What This Means

- **Commercial Use**: Allowed
- **Modification**: Allowed
- **Distribution**: Allowed
- **Private Use**: Allowed
- **Patent**: Any patent must be licensed for free use
- **Derivative Code Licensing**: Any derivative code must use the same GPL v3 license

### 📋 Conditions

By using, modifying, or distributing this software, you agree to:

1. Maintain copyright and license notices
2. Provide complete source code
3. License derivative works under GPL v3
4. Include a copy of the GPL v3 license

### 📖 Full License Text

For the full text of the GNU GPL v3 license, see:
- [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)
- `LICENSE` file in the repository

---

## 🤝 Contributing

Contributions are welcome! If you want to contribute to the project:

1. **Fork** the repository
2. Create a **branch** for your feature (`git checkout -b feature/MyFeature`)
3. **Commit** your changes (`git commit -m 'Add MyFeature'`)
4. **Push** to the branch (`git push origin feature/MyFeature`)
5. Open a **Pull Request**

### 📝 Contribution Guidelines

- Keep code clean and documented
- Follow existing code standards
- Add tests when appropriate
- Update documentation as needed
- Respect the GPL v3 license

---

## 📞 Contact

### 👨‍💻 Main Developer

- **Name**: Michel Ribeiro Paes
- **GitHub**: [@Mrpac6689](https://github.com/Mrpac6689)
- **Email**: michelrpaes@gmail.com

### 🔗 Useful Links

- **Repository**: [github.com/Mrpac6689/AutoReg](https://github.com/Mrpac6689/AutoReg)
- **Web Interface**: [github.com/mrpac6689/autoreg-web](https://github.com/mrpac6689/autoreg-web)
- **Issues**: [github.com/Mrpac6689/AutoReg/issues](https://github.com/Mrpac6689/AutoReg/issues)

### 🤖 Developed with AI Support

- **ChatGPT 4.1**: Development and architecture
- **Claude 3.7 Sonnet**: Refactoring and optimization

---

## 📚 Additional Documentation

- [CHANGELOG.md](CHANGELOG.md) - Complete version history and changes
- [LICENSE](LICENSE) - Full GNU GPL v3 license text

---

## 🎯 Purpose

AutoReg was developed to facilitate and automate hospital processes, contributing to the efficiency of healthcare professionals and better patient care. This software aims to reduce manual workload, minimize errors, and allow hospital teams to focus on activities that require human attention.

---

**AutoReg v9.7.0 Universe** - *Intelligent automation for healthcare systems* 🚀

*We hope AutoReg continues to facilitate your routine and contribute to more efficient hospital processes!*
