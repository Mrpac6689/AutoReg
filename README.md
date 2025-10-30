# AutoReg
Operação automatizada de Sistemas de Saúde - SISREG & G-HOSP

## 🌌 Versão 9.6.5 Universe - Outubro de 2025

### 🆕 Novas Funcionalidades v9.6.5

- **Empacotamento com Docker + Integração Kasm VNC**: Imagem Docker pronta para uso em ambientes Kasm Workspaces (VNC/noVNC)
  - Imagem baseada em Python slim com todas as dependências do AutoReg instaladas
  - Entrypoint que inicia a aplicação e mantém um ambiente gráfico acessível via VNC/noVNC
  - Orientações para registrar a imagem no Kasm e disponibilizar a interface pelo painel Kasm
  - Exemplos de Dockerfile e docker-compose para teste local e para preparação do artefato a ser importado no Kasm
  - Recomendações de volumes e variáveis de ambiente para persistência de dados e configuração de credenciais
- Atualizações menores de compatibilidade e correções de dependências para execução em container
- Documentação básica para criação da imagem e publicação em registry privado

### Empacotamento Docker + Kasm VNC (guia rápido)

Objetivo: gerar uma imagem Docker que execute AutoReg em um ambiente com interface gráfica acessível via VNC/noVNC; essa imagem pode ser importada no Kasm Workspaces para uso centralizado.

Passos resumidos:
1. Criar Dockerfile (exemplo abaixo).
2. Construir a imagem localmente: docker build -t autoreg:9.6.5 .
3. Testar localmente com docker-compose (exemplo incluído).
4. Subir a imagem para registry (opcional) e registrar no Kasm.
5. No Kasm, criar um Workspace que utilize a imagem e configurar portas/recursos.

Exemplo mínimo de Dockerfile (ajustar conforme política de base do Kasm):
```bash
# Dockerfile mínimo de exemplo (teste local)
FROM python:3.11-slim

# Dependências para ambiente gráfico/VNC (exemplos; ajustar conforme distribuição)
RUN apt-get update && apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal tigervnc-standalone-server xvfb wget curl git supervisor \
  && rm -rf /var/lib/apt/lists/*

# Diretório da aplicação
WORKDIR /opt/autoreg

# Copia código e instala dependências
COPY . /opt/autoreg
RUN python -m pip install --upgrade pip \
  && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Cria usuário não-root
RUN useradd -m -s /bin/bash autoreg
RUN chown -R autoreg:autoreg /opt/autoreg
USER autoreg

# Porta padrão VNC (se for usar diretamente) e porta da aplicação se necessário
EXPOSE 5901 6901

# Entrypoint: exemplo que inicia o VNC e a aplicação (ajustar conforme necessidade)
CMD ["bash", "-lc", "vncserver :1 -geometry 1280x800 -depth 24 && tail -f /dev/null"]
```

Exemplo de docker-compose para teste local:
```yaml
version: '3.8'
services:
  autoreg:
    build: .
    image: autoreg:9.6.5
    container_name: autoreg_kasm_test
    volumes:
      - ./data:/home/autoreg/data
    environment:
      - TZ=America/Sao_Paulo
      - AUTOREG_CONFIG=/home/autoreg/data/config.ini
    ports:
      - "5901:5901"   # VNC
      - "6901:6901"   # noVNC (se configurado)
    restart: unless-stopped
```

Observações para uso com Kasm:
- Kasm Workspaces espera imagens preparadas com um serviço de sessão (ex.: supervisord iniciando ambiente de desktop + noVNC). Recomenda-se criar um Dockerfile baseado nas imagens oficiais do Kasm ou adaptar o Dockerfile acima para iniciar supervisor e noVNC.
- Após construir e testar a imagem, faça push para o registry que o Kasm pode acessar (ex.: registry.local/empresa/autoreg:9.6.5).
- No painel do Kasm, crie um novo Workspace Image apontando para a imagem, configure a sessão e permissões (GPU, memória, tempo de sessão).
- Mapear volumes para persistência: ~/.autoreg ou /home/autoreg/data para manter logs, CSVs e venv.
- Variáveis de ambiente sensíveis (credenciais) devem ser gerenciadas pelo Kasm Secrets ou mounted files, não em ENV públicos.

Segurança e recomendações:
- Não exponha VNC diretamente à internet; use o noVNC via Kasm ou túnel seguro.
- Rode containers com usuários não-root e limite recursos (CPU/memória).
- Use registry privado e imagens assinadas quando possível.
- Verifique políticas de compliance do hospital antes de disponibilizar workspaces que contenham credenciais.

### Comandos úteis
- Construir imagem:
  - docker build -t autoreg:9.6.5 .
- Testar com docker-compose:
  - docker-compose up --build
- Enviar para registry:
  - docker tag autoreg:9.6.5 registry.exemplo.com/autoreg:9.6.5
  - docker push registry.exemplo.com/autoreg:9.6.5

### 📋 Funções Disponíveis e Workflows Agrupados

| Flag         | Função                        | Descrição |
|--------------|-------------------------------|-----------|
| `-css`       | consulta_solicitacao_sisreg   | Consulta status de solicitações no SISREG |
| `-eci`       | extrai_codigos_internacao     | Extrai códigos de internação do SISREG |
| `-ip`        | interna_pacientes             | Realiza internação de pacientes no SISREG |
| `-eis`       | extrai_internados_sisreg      | Extrai lista de internados do SISREG |
| `-eig`       | extrai_internados_ghosp       | Extrai lista de internados do G-HOSP |
| `-ci`        | compara_internados            | Compara listas de internados entre sistemas |
| `-ma`        | motivo_alta                   | Captura motivos de alta no G-HOSP |
| `-tat`       | trata_altas                   | Trata Motivos de Alta capturados |
| `-ecsa`      | extrai_codigos_sisreg_alta    | Extrai códigos SISREG para alta |
| `-ea`        | executa_alta                  | Executa altas no SISREG |
| `-ar`        | atualiza_restos               | Atualiza arquivo de pacientes restantes |
| `-eid`       | extrai_internacoes_duplicadas | Identifica internações duplicadas |
| `-td`        | trata_duplicados              | Processa pacientes com duplicações |
| `-clc`       | limpa_cache                   | Limpa todos os arquivos da pasta ~/AutoReg, mantendo apenas solicita_inf_aih.csv |
| `-dev`       | devolvidos                    | Processa solicitações devolvidas |
| `-p2c`       | pdf2csv                       | Converte PDF de solicitações em CSV |
| `-ghn`       | ghosp_nota                    | Extrair notas de prontuários Ghosp |
| `-ghc`       | ghosp_cns                     | Extrai CNSs dos prontuários |
| `-iga`       | internados_ghosp_avancado     | Extrai pacientes internados no GHOSP com informações adicionais |
| `-ign`       | internados_ghosp_nota         | Extrai o conteúdo das notas dos prontuários do GHOSP |
| `-std`       | solicita_trata_dados          | Ajusta CSV para tratamento das solicitações de AIH previamente ao SISREG |
| `-spa`       | solicita_pre_aih              | Extrai link para solicitação de AIH do GHOSP |
| `-especial`  | [workflow agrupado]           | Extração de dados personalizados do GHOSP |
| `-sia`       | solicita_inf_aih              | Extrai informações da AIH |
| `-ssr`       | solicita_sisreg               | Executa Solicitações no Sistema SISREG |
| `-snt`       | solicita_nota                 | Insere numero da solicitação SISREG na nota de prontuário |
| `-interna`   | [workflow agrupado]           | Executa rotina de internação completa: -eci -ip |
| `-analisa`   | [workflow agrupado]           | Executa rotina de análise/comparação: -eis -eig -ci -ma |
| `-alta`      | [workflow agrupado]           | Executa rotina de alta completa: -tat -ecsa -ea -ar -eid -td -clc |
| `-solicita`  | [workflow agrupado]           | Executa rotina de Solicitação: -spa -sia -ssr -snt |
| `-aihs`      | [workflow agrupado]           | Executa rotina de AIHs: -iga -ign -std |
| `--all`      | [workflow completo]           | Executa todas as funções principais com repetição interativa |

### 📜 Histórico de Versões

## 🌌 v9.6.5 Universe - Outubro de 2025
- **Empacotamento com Docker + Integração Kasm VNC**: Imagem Docker pronta para uso em ambientes Kasm Workspaces (VNC/noVNC)
- Imagem baseada em Python slim com todas as dependências do AutoReg instaladas
- Entrypoint que inicia a aplicação e mantém um ambiente gráfico acessível via VNC/noVNC
- Orientações para registrar a imagem no Kasm e disponibilizar a interface pelo painel Kasm
- Exemplos de Dockerfile e docker-compose para teste local e para preparação do artefato a ser importado no Kasm
- Recomendações de volumes e variáveis de ambiente para persistência de dados e configuração de credenciais
- Atualizações menores de compatibilidade e correções de dependências para execução em container
- Documentação básica para criação da imagem e publicação em registry privado

## 🌌 v9.6.2 Universe - Outubro de 2025
- **Sanitização completa de dados**: Remoção de quebras de linha e caracteres problemáticos em CSV/Selenium
- **XPaths dinâmicos**: Seletores que se adaptam a IDs variáveis em formulários e laudos
- **Localização semântica**: Campos identificados por nome ao invés de posição fixa
- **Gerenciamento robusto de modais**: Sistema de fechamento com tentativa de botão X e fallback para ESC
- **Hover automático**: Revelação de elementos ocultos via ActionChains
- **URLs com intern_id**: Acesso a formulários eletrônicos via RA ao invés de prontuário
- **Pausas entre workflows**: Time.sleep(1) entre funções de `-solicita` para estabilidade
- **Suporte a múltiplos tipos de laudo**: Extração adaptativa para formeletronicos e printernlaudos
- **Extração de CNS/CPF via fieldset**: Busca por "Documentos" com classes semânticas
- **Tratamento de TextAreas por name**: Campos identificados por attributes ao invés de XPath
- **Melhorias de robustez**: Código mais resiliente a mudanças na estrutura HTML

## 🌌 v9.6.0 Universe - Outubro de 2025
- **Performance 4x mais rápida**: Acesso direto a prontuários via URL em `-ign` e `-snt`
- **Eliminação de navegação desnecessária**: Sem preenchimento de campos ou cliques em botões
- **Verificação automática de CNS/CPF**: Loop adicional em `-snt` para detectar e tratar dados faltantes
- **Lembretes automáticos**: Inserção de avisos sobre CNS/CPF faltante em prontuários
- **Abertura automática de planilhas**: CSVs abertos no programa padrão após processamento
- **Workflow `-solicita` expandido**: Agora inclui `-spa` no início (-spa -sia -ssr -snt)
- **Renomeação de workflow**: `-nota` renomeado para `-aihs` para melhor clareza
- **Tratamento de dados em `-spa`**: Preparação automática de solicita_inf_aih.csv
- **Extração inteligente**: Transferência automática de dados de internados_ghosp_avancado.csv
- **Validações robustas**: Verificação completa de arquivos e colunas com feedback detalhado
- **Suporte multiplataforma**: Abertura de arquivos em Windows, macOS e Linux

## 🌌 v9.5.9 Universe - Outubro de 2025
- Nova função `-std` para filtrar e organizar dados de solicitação de AIH
- Nova função `-spa` para extração interativa de links de formulários do GHOSP
- Sistema de captura de URLs com comandos simples ('s' para salvar, 'p' para pular)
- Clique automático no botão "Gravar" após captura de URL
- Workflow `-nota` aprimorado com tratamento de dados integrado (-iga → -std → -ign)
- Filtros inteligentes: remoção de setores específicos, filtro temporal de 48h, filtro de datas ±15 dias
- Organização automática de registros com campo 'dados' vazio
- Interface interativa para processamento manual de formulários
- Melhorias na robustez do tratamento de dados CSV

## 🌌 v9.5.8 Universe - Outubro de 2025
- Nova função `-tat` para tratamento automatizado de motivos de alta
- Nova função `-clc` para limpeza inteligente de cache com proteção de arquivos
- Workflow `-alta` aprimorado com tratamento de dados e limpeza automática
- Workflow `-all` interativo com sistema de repetição personalizável
- Contadores visuais de progresso por ciclo e função
- Relatórios estatísticos detalhados de execução
- Otimizações de performance em todo o sistema
- Melhorias na experiência do usuário com prompts interativos

## 🌌 v9.5.6 Universe - Outubro de 2025
- Nova função `-iga` para extração avançada de dados de internados do GHOSP
- Nova função `-ign` para extração de notas de prontuários com atualização de setor
- Novo workflow `-nota` para processamento completo de dados e notas
- Sistema de mapeamento inteligente de setores hospitalares
- Ordenação automática de dados por setor nos CSVs
- Tratamento universal de dados numéricos (remoção de pontos e .0)
- Fallback automático CNS/CPF para identificação de pacientes
- Contadores de progresso em tempo real [x/xx]
- Limpeza automática de CSVs mantendo apenas registros para revisão
- Relatórios estatísticos de distribuição de pacientes por setor
- Melhorias na robustez do tratamento de dados em todos os módulos

## 🌌 v9.5.0 Universe - Outubro de 2025
- Nova função `-css` para consulta de status de solicitações no SISREG
- Sistema automático de atualização de status em CSVs
- Processamento em lote de múltiplas solicitações
- Feedback em tempo real durante as consultas
- Logs detalhados de todas as operações
- Tratamento inteligente de diferentes status

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
| `-tat` | `trata_altas` | Trata Motivos de Alta capturados |
| `-ecsa` | `extrai_codigos_sisreg_alta` | Extrai códigos SISREG para alta |
| `-ea` | `executa_alta` | Executa altas no SISREG |
| `-ar` | `atualiza_restos` | Atualiza arquivo de pacientes restantes |
| `-eid` | `extrai_internacoes_duplicadas` | Identifica internações duplicadas |
| `-td` | `trata_duplicados` | Processa pacientes com duplicações |
| `-clc` | `limpa_cache` | Limpa cache mantendo arquivos protegidos |
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
autoreg -tat                    # Trata motivos de alta capturados
autoreg -clc                    # Limpa cache da pasta ~/AutoReg
autoreg -snt                    # Insere número da solicitação na nota
autoreg -std                    # Ajusta CSV para tratamento de AIH
autoreg -spa                    # Extrai links de formulários do GHOSP

# Múltiplas funções em sequência
autoreg -eci -ip                # Extrai códigos e interna
autoreg -eis -eig -ci           # Extrai listas e compara
autoreg -ma -tat -ecsa -ea      # Workflow de alta completo
autoreg -spa -sia -ssr -snt     # Workflow de solicitação manual
autoreg -iga -ign -std          # Workflow de AIHs

# Workflows agrupados
autoreg -interna                # Executa rotina de internação completa
autoreg -analisa                # Executa rotina de análise/comparação
autoreg -alta                   # Executa rotina de alta completa (inclui -tat e -clc)
autoreg -solicita               # Executa rotina de solicitação completa (inclui -spa)
autoreg -aihs                   # Executa rotina de AIHs completa (inclui -std)

# Workflow completo (todas as funções principais com repetição interativa)
autoreg --all                   # Executa tudo com prompt de repetição

# Função especializada
autoreg -dev                    # Processa devolvidos (separadamente)
```

### 💡 **Exemplos Práticos**
```bash
# Rotina matinal de internação
autoreg -interna

# Rotina de alta de pacientes (com tratamento e limpeza)
autoreg -alta

# Rotina de análise/comparação
autoreg -analisa

# Rotina de processamento de AIHs (com tratamento de dados)
autoreg -aihs

# Rotina de solicitação completa (com preparação de links)
autoreg -solicita

# Processamento completo automatizado com 3 repetições
autoreg --all
# Quando perguntado: 3

# Limpeza manual de cache
autoreg -clc

# Tratamento de dados e extração de links de AIH
autoreg -std -spa
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
