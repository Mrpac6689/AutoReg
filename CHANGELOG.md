# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [9.7.0] - 2026-01

### Adicionado
- **Sistema Completo de Gestão de Exames Ambulatoriais**:
  - Função `-eae` (`exames_ambulatorio_extrai`): Extrai dados de exames a solicitar do G-Hosp
    - Login automático no G-HOSP
    - Extração de procedimentos de tomografia por atendimento (RA)
    - Suporte a múltiplos procedimentos por atendimento (separados por `|`)
    - Extração de CNS/CPF do modal de dados do paciente
    - Filtragem inteligente por número de atendimento
    - Saída: `~/AutoReg/exames_solicitar.csv` com colunas: `ra`, `procedimento`, `cns`
  
  - Função `-eas` (`exames_ambulatorio_solicita`): Executa solicitações de exames no SISREG
    - Login automático no SISREG
    - Processamento baseado em CSV com CNS e procedimentos
    - Seleção automática de procedimentos por similaridade (múltiplos procedimentos suportados)
    - Seleção aleatória de profissional solicitante
    - Seleção automática de unidade de execução
    - Seleção de primeira vaga disponível
    - Extração automática de chave e número de solicitação
    - Proteção contra duplicidades (pula registros já processados)
    - Saída: `~/AutoReg/exames_solicitar.csv` atualizado com `chave` e `solicitacao`
  
  - Função `-ear` (`exames_ambulatorio_relatorio`): Extrai relatórios de exames solicitados no SISREG
    - Login automático no SISREG
    - Geração de PDFs individuais por solicitação
    - Numeração sequencial automática (001, 002, 003...)
    - Junção automática de todos os PDFs em um único arquivo
    - Remoção automática de PDFs individuais após junção
    - Processa apenas registros com chave e solicitação preenchidos
    - Saída: `~/AutoReg/solicitacoes_exames_imprimir.pdf` (PDF unificado)

### Melhorado
- Sistema de similaridade de strings para matching de procedimentos
- Tratamento inteligente de valores numéricos (remoção de `.0`)
- Validação de campos obrigatórios antes do processamento
- Salvamento incremental de CSV durante processamento
- Tratamento de erros com continuidade do processamento

## [9.6.7] - 2025-11

### Adicionado
- **Extração de Produção Ambulatorial GMUs**:
  - Função `-pag` (`producao_ambulatorial_gmus`): Extrai dados detalhados de produção ambulatorial para GMUs (Gestão de Múltiplas Unidades)
    - Login automático no G-HOSP
    - Interface para seleção de mês e ano
    - Identificação automática de dias úteis (exclui sábados e domingos)
    - Navegação direta por URL para cada dia
    - Extração de dados completos por paciente:
      - Data do atendimento
      - Período (Manhã/Tarde)
      - Posição na agenda
      - Nome do paciente
      - Nome do agendador (via tooltip hover)
    - Salvamento incremental após cada dia processado
    - Sistema de pausa/retomada interativo (P/C + ENTER)
    - Thread daemon para não bloquear o Selenium durante pausa
    - Navegador permanece responsivo durante pausas
    - Saída: `~/AutoReg/producao_ambulatorial_gmus.csv`

- **Sistema de Pausa/Retomada para Processos Longos**:
  - Implementado em `producao_ambulatorial_dados`
  - Comandos simples: `P` + ENTER para pausar, `C` + ENTER para continuar
  - Thread separada que não bloqueia o driver do Selenium
  - Navegador permanece totalmente funcional durante pausa
  - Thread-safe com locks para evitar race conditions
  - Permite interação manual com o navegador se necessário

## [9.6.6] - 2025-11

### Adicionado
- **Extração de Produção Ambulatorial SISREG**:
  - Função `-pra` (`producao_ambulatorial`): Extrai códigos de solicitação de produção ambulatorial com navegação multi-página automática
    - Login automático no SISREG
    - Interface para configuração manual de filtros
    - Extração inteligente de tabelas (identifica segunda tabela com dados)
    - Navegação automática entre páginas
    - Sistema de checkpoint: salva progresso a cada 10 páginas
    - Retomada automática em caso de interrupção
    - Suporte a grandes volumes (200+ páginas)
    - Saída: `~/AutoReg/producao_ambulatorial.csv`
  
  - Função `-pad` (`producao_ambulatorial_dados`): Extrai dados detalhados de cada solicitação
    - Acesso direto via URL para cada código
    - Extração de 5 campos essenciais:
      - Data da solicitação
      - Unidade solicitante
      - Unidade autorizadora
      - Unidade executante
      - Procedimento solicitado
    - Processamento em lote de todos os códigos do CSV anterior
    - Feedback detalhado por solicitação
    - Saída: `~/AutoReg/producao_ambulatorial_dados.csv`

### Melhorado
- Sistema de checkpoint com arquivo `producao_ambulatorial_checkpoint.txt`
- Salvamento incremental para evitar perda de dados
- Tratamento de interrupção por Ctrl+C com salvamento automático
- Detecção de página atual e total de páginas
- Retomada inteligente de onde parou

## [9.6.5] - 2025-10

### Adicionado
- **Empacotamento com Docker + Integração Kasm VNC**: Imagem Docker pronta para uso em ambientes Kasm Workspaces (VNC/noVNC)
  - Imagem baseada em Python slim com todas as dependências do AutoReg instaladas
  - Entrypoint que inicia a aplicação e mantém um ambiente gráfico acessível via VNC/noVNC
  - Orientações para registrar a imagem no Kasm e disponibilizar a interface pelo painel Kasm
  - Exemplos de Dockerfile e docker-compose para teste local e para preparação do artefato a ser importado no Kasm
  - Recomendações de volumes e variáveis de ambiente para persistência de dados e configuração de credenciais

### Melhorado
- Atualizações menores de compatibilidade e correções de dependências para execução em container
- Documentação básica para criação da imagem e publicação em registry privado

## [9.6.2] - 2025-10

### Melhorado
- Sanitização completa de dados: Remoção de quebras de linha e caracteres problemáticos em CSV/Selenium
- XPaths dinâmicos: Seletores que se adaptam a IDs variáveis em formulários e laudos
- Localização semântica: Campos identificados por nome ao invés de posição fixa
- Gerenciamento robusto de modais: Sistema de fechamento com tentativa de botão X e fallback para ESC
- Hover automático: Revelação de elementos ocultos via ActionChains
- URLs com intern_id: Acesso a formulários eletrônicos via RA ao invés de prontuário
- Pausas entre workflows: Time.sleep(1) entre funções de `-solicita` para estabilidade
- Suporte a múltiplos tipos de laudo: Extração adaptativa para formeletronicos e printernlaudos
- Extração de CNS/CPF via fieldset: Busca por "Documentos" com classes semânticas
- Tratamento de TextAreas por name: Campos identificados por attributes ao invés de XPath
- Melhorias de robustez: Código mais resiliente a mudanças na estrutura HTML

## [9.6.0] - 2025-10

### Melhorado
- Performance 4x mais rápida: Acesso direto a prontuários via URL em `-ign` e `-snt`
- Eliminação de navegação desnecessária: Sem preenchimento de campos ou cliques em botões
- Verificação automática de CNS/CPF: Loop adicional em `-snt` para detectar e tratar dados faltantes
- Lembretes automáticos: Inserção de avisos sobre CNS/CPF faltante em prontuários
- Abertura automática de planilhas: CSVs abertos no programa padrão após processamento
- Workflow `-solicita` expandido: Agora inclui `-spa` no início (-spa -sia -ssr -snt)
- Renomeação de workflow: `-nota` renomeado para `-aihs` para melhor clareza
- Tratamento de dados em `-spa`: Preparação automática de solicita_inf_aih.csv
- Extração inteligente: Transferência automática de dados de internados_ghosp_avancado.csv
- Validações robustas: Verificação completa de arquivos e colunas com feedback detalhado
- Suporte multiplataforma: Abertura de arquivos em Windows, macOS e Linux

## [9.5.9] - 2025-10

### Adicionado
- Função `-std` (`solicita_trata_dados`): Filtra e organiza dados de solicitação de AIH
- Função `-spa` (`solicita_pre_aih`): Extração interativa de links de formulários do GHOSP
- Sistema de captura de URLs com comandos simples ('s' para salvar, 'p' para pular)
- Clique automático no botão "Gravar" após captura de URL
- Workflow `-nota` aprimorado com tratamento de dados integrado (-iga → -std → -ign)

### Melhorado
- Filtros inteligentes: remoção de setores específicos, filtro temporal de 48h, filtro de datas ±15 dias
- Organização automática de registros com campo 'dados' vazio
- Interface interativa para processamento manual de formulários
- Melhorias na robustez do tratamento de dados CSV

## [9.5.8] - 2025-10

### Adicionado
- Função `-tat` (`trata_altas`): Tratamento automatizado de motivos de alta
- Função `-clc` (`limpa_cache`): Limpeza inteligente de cache com proteção de arquivos
- Workflow `-alta` aprimorado com tratamento de dados e limpeza automática
- Workflow `-all` interativo com sistema de repetição personalizável
- Contadores visuais de progresso por ciclo e função
- Relatórios estatísticos detalhados de execução

### Melhorado
- Otimizações de performance em todo o sistema
- Melhorias na experiência do usuário com prompts interativos

## [9.5.6] - 2025-10

### Adicionado
- Função `-iga` (`internados_ghosp_avancado`): Extração avançada de dados de internados do GHOSP
- Função `-ign` (`internados_ghosp_nota`): Extração de notas de prontuários com atualização de setor
- Workflow `-nota` para processamento completo de dados e notas
- Sistema de mapeamento inteligente de setores hospitalares
- Ordenação automática de dados por setor nos CSVs
- Tratamento universal de dados numéricos (remoção de pontos e .0)
- Fallback automático CNS/CPF para identificação de pacientes
- Contadores de progresso em tempo real [x/xx]
- Limpeza automática de CSVs mantendo apenas registros para revisão
- Relatórios estatísticos de distribuição de pacientes por setor

### Melhorado
- Melhorias na robustez do tratamento de dados em todos os módulos

## [9.5.0] - 2025-10

### Adicionado
- Função `-css` (`consulta_solicitacao_sisreg`): Consulta de status de solicitações no SISREG
- Sistema automático de atualização de status em CSVs
- Processamento em lote de múltiplas solicitações
- Feedback em tempo real durante as consultas
- Logs detalhados de todas as operações
- Tratamento inteligente de diferentes status

## [9.0.0] - 2025-10

### Adicionado
- Nova sequência de workflow `-solicita` para automatizar o processo completo de solicitações
- Função `-snt` (`solicita_nota`): Insere números de solicitação SISREG em notas de prontuário
- Sistema inteligente de detecção e tratamento de dados faltantes em CSVs
- Limpeza automática de formatos numéricos (.0) nos códigos de solicitação
- Marcação automática de registros que precisam de revisão
- Interface CLI atualizada com novas opções e feedbacks

### Melhorado
- Melhorias na robustez do tratamento de dados

## [8.5.0] - 2025-09

### Adicionado
- Instalador universal refeito: install.sh (Linux/macOS) e install.bat (Windows)
  - Detecta pasta do usuário
  - Move dados para ~/.autoreg
  - Cria pasta ~/AutoReg
  - Gera log
  - Verifica Python3
  - Cria venv
  - Instala dependências
  - Configura alias global
- Novos workflows agrupados: flags -interna, -analisa, -alta para execução de rotinas completas
- Ajuda CLI aprimorada: todas as flags e agrupamentos aparecem corretamente no --help
- Função `pdf2csv`: Conversão de PDF em CSV com extração e limpeza de dados
- Função `ghosp_nota`: Extração automatizada de notas de prontuários do G-HOSP
  - Processa múltiplos códigos do CSV
  - Loop automatizado para busca sequencial de prontuários
  - Extração de lembretes
  - Atualização dinâmica do CSV com coluna 'dados'

### Adicionado
- Flag `-R` (`--registro-producao`): Permite enviar relatório de execução para a AUTOREG-API
  - Funciona com rotinas `-solicita`, `-interna` ou `-alta`
  - Envio via POST JSON com `rotina` e `registros`
  - Configuração em `config.ini` na seção `[AUTOREG-API]`

## [8.0.0] - 2025-07

### Adicionado
- **Arquitetura Modular Completa**:
  - Refatoração total: Código dividido em módulos independentes na pasta `autoreg/`
  - Coordenador de Workflow: `autoreg.py` como orquestrador principal
  - Imports otimizados: Sistema de importação limpo e organizados

- **Interface de Linha de Comando Avançada**:
  - 12 funções individuais com flags específicas (`-eci`, `-ip`, `-eis`, etc.)
  - Execução sequencial: Múltiplas funções em uma chamada (`autoreg -eci -ip -eis`)
  - Workflow completo: Flag `--all` executa todas as funções automaticamente
  - Configuração integrada: `--config` para editar credenciais
  - Gestão de arquivos: `--directory` para acessar pasta de trabalho

- **Sistema de Instalação Universal**:
  - Scripts multiplataforma: `install.sh` (Linux/macOS) e `install.bat` (Windows)
  - Detecção automática: Sistema operacional, Python, pip e venv
  - Instalação de dependências: Automática por distro Linux/Homebrew/Manual Windows
  - Ambiente virtual isolado: Instalação em `~/.autoreg/` sem conflitos
  - PATH global: Comando `autoreg` disponível globalmente
  - Desinstalação limpa: Script `uninstall.sh` para remoção completa

- **Funções Disponíveis**:
  - `-eci`: Extrai códigos de internação do SISREG
  - `-ip`: Realiza internação de pacientes no SISREG
  - `-eis`: Extrai lista de internados do SISREG
  - `-eig`: Extrai lista de internados do G-HOSP
  - `-ci`: Compara listas de internados entre sistemas
  - `-ma`: Captura motivos de alta no G-HOSP
  - `-ecsa`: Extrai códigos SISREG para alta
  - `-ea`: Executa altas no SISREG
  - `-ar`: Atualiza arquivo de pacientes restantes
  - `-eid`: Identifica internações duplicadas
  - `-td`: Processa pacientes com duplicações
  - `-clc`: Limpa cache mantendo arquivos protegidos
  - `-dev`: Processa solicitações devolvidas

### Melhorado
- Logging estruturado: Sistema de logs melhorado
- Tratamento de erros: Feedback detalhado e recuperação automática
- Configuração flexível: Suporte a diferentes ambientes hospitalares
- Performance otimizada: Execução mais rápida e eficiente

## [7.0.0-linux] - 2025-05

### Corrigido
- Reajustado destino do Download na Função Internhosp
- Corrigidos destinos de arquivos temporários para concentrar na pasta ~/AutoReg
- Testes e ajustes de empacotamento e distribuição .deb

## [6.5.1-linux] - 2025-05

### Corrigido
- Removidos imports de bibliotecas não utilizadas
- Removido argumento `zoomed` do ChromeOptions (incompatível com Linux)
- Adicionado argumento `headless=new` para Chrome em modo oculto
- Ajuste de foco para frame `f_principal` antes de chamar `configFicha`
- Substituídos pop-ups por prints no campo de logs
- Ajustes diversos de caminho de arquivos para ambiente Linux

## [6.0] - 2024

### Adicionado
- Função de internação automatizada
- Função de alta automatizada

## [5.1.2] - 2024

### Adicionado
- Motivos de saída ausentes
- Rotina para execução autônoma do módulo de Alta
- Reduzido tempo para captura de altas

## [5.0.1] - 2024

### Adicionado
- Funções `captura_cns_restos_alta()`, `motivo_alta_cns()`, `executa_saidas_cns()`
- Estrutura de diretórios com versões anteriores
- Interface do módulo alta redesenhada
- Restaurada função `trazer_terminal()`
- Atualizada para Python 3.13

## [4.2.3] - 2023

### Adicionado
- Publicado em PyPI.org
- Pop-ups concentrados em três funções
- Convertido .ico em base64

## [4.0] - 2023

### Adicionado
- Funções de Internação: Captura automatizada e processo completo
- Melhorias de Alta: Configuração HTTP do G-HOSP
- Módulos independentes: Internação e Alta separados
- Compilação binária: .exe para Windows, .app beta para macOS

## [3.0] - 2022

### Adicionado
- Extração de códigos de internação SISREG
- Correlação Nome, Motivo de Alta G-HOSP e Código SISREG
- Alta automática conforme motivo capturado
- Interface visual melhorada

## [2.0] - 2021

### Adicionado
- Atualização automática do ChromeDriver
- Interface gráfica redesenhada com Tkinter
- Menu "Informações" com documentação integrada

---

[9.7.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.7.0
[9.6.7]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.6.7
[9.6.6]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.6.6
[9.6.5]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.6.5
[9.6.2]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.6.2
[9.6.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.6.0
[9.5.9]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.5.9
[9.5.8]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.5.8
[9.5.6]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.5.6
[9.5.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.5.0
[9.0.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v9.0.0
[8.5.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v8.5.0
[8.0.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v8.0.0
[7.0.0-linux]: https://github.com/Mrpac6689/AutoReg/releases/tag/v7.0.0-linux
[6.5.1-linux]: https://github.com/Mrpac6689/AutoReg/releases/tag/v6.5.1-linux
[6.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v6.0
[5.1.2]: https://github.com/Mrpac6689/AutoReg/releases/tag/v5.1.2
[5.0.1]: https://github.com/Mrpac6689/AutoReg/releases/tag/v5.0.1
[4.2.3]: https://github.com/Mrpac6689/AutoReg/releases/tag/v4.2.3
[4.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v4.0
[3.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v3.0
[2.0]: https://github.com/Mrpac6689/AutoReg/releases/tag/v2.0
