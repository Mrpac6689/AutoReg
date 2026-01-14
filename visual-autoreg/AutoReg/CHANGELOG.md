# Changelog - AutoReg Visual

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AutoReg - Interface Gráfica                        │
├──────────────────────────────────────┬──────────────────────────────────────────┤
│                                      │                                          │
│   ╔══════════════════════════════╗   │   ╔════════════════════════════════╗    │
│   ║   🌐 Navegador Embutido      ║   │   ║   📊 Planilha de Dados         ║    │
│   ║   (QWebEngineView)           ║   │   ║   (Editável)                   ║    │
│   ║                              ║   │   ║                                ║    │
│   ║   Exibe páginas SISREG/GHOSP║   │   ║  Código │ Paciente │ Data ...  ║    │
│   ║   durante automação          ║   │   ║  ──────┼──────────┼──────...  ║    │
│   ╚══════════════════════════════╝   │   ║  001   │ João     │ 15/11 ... ║    │
│                                      │   ║  002   │ Maria    │ 16/11 ... ║    │
│   ╔══════════════════════════════╗   │   ║                                ║    │
│   ║  📟 Console de Logs          ║   │   ║  [➕ Linha] [➖ Linha]         ║    │
│   ║  ✅ Iniciando processo...    ║   │   ║  [➕ Col]   [➖ Col]           ║    │
│   ║  ⏳ Processando dados...     ║   │   ║  [💾 Salvar] [📤 Exportar]    ║    │
│   ╚══════════════════════════════╝   │   ╚════════════════════════════════╝    │
│                                      │                                          │
│   🔧 Selecione a Função AutoReg:    │                                          │
│   ┌──────────────────────────────┐   │                                          │
│   │ extrai_codigos_internacao  ▼│   │                                          │
│   └──────────────────────────────┘   │                                          │
│                                      │                                          │
│   ┌──────────────────────────────┐   │                                          │
│   │ ▶️ Executar Função Selecionada│   │                                          │
│   └──────────────────────────────┘   │                                          │
└──────────────────────────────────────┴──────────────────────────────────────────┘
```

# Changelog - AutoReg Visual

## [18/11/2025] - Integração Completa com AutoReg Real

### 🎯 ATUALIZAÇÃO MAJOR: Execução Real das Funções

A aplicação agora **executa as funções reais** do sistema AutoReg original, com:
- **Redirecionamento de stdout/stderr** para o console de logs
- **Captura do navegador Selenium** e sincronização com QWebEngineView
- **Detecção automática de CSVs** gerados pelas funções
- **Tratamento de erros** robusto com traceback completo

#### 🔧 Sistema de Captura de Driver
- **DriverCapture**: Intercepta instâncias do WebDriver do Selenium
- **Monitoramento de URL**: Atualiza o navegador embutido em tempo real
- **Integração transparente**: Funções originais rodam sem modificações

#### 📟 Redirecionamento de I/O
- **OutputRedirector**: Captura `print()` e `logging` para a GUI
- **Auto-scroll**: Console sempre mostra as mensagens mais recentes
- **Preservação de stdout/stderr**: Restaurados após execução

### ✨ Funcionalidades Anteriores

## [18/11/2025] - Widget de Planilhas e Dropdown de Funções

### ✨ Novas Funcionalidades

#### 🔽 Dropdown de Funções AutoReg
- **Localização**: Acima do botão "Executar", no painel esquerdo
- **Funcionalidades**:
  - 📋 Lista completa com 33 funções disponíveis do sistema AutoReg
  - 🎨 Interface estilizada com cores e ícones
  - 🔄 Desabilitado durante execução para evitar conflitos
  - ⚡ Seleção dinâmica da função a ser executada
- **Funções Disponíveis**:
  - Extração: `extrai_codigos_internacao`, `extrai_internados_sisreg`, `extrai_internados_ghosp`, etc.
  - Internação: `interna_pacientes`, `compara_internados`
  - Alta: `motivo_alta`, `executa_alta`, `dar_alta`, `trata_altas`
  - Solicitações: `solicita_sisreg`, `solicita_nota`, `solicita_inf_aih`, `solicita_pre_aih`
  - G-HOSP: `ghosp_nota`, `ghosp_cns`, `ghosp_especial`, `internados_ghosp_avancado`
  - Produção: `producao_ambulatorial`, `producao_ambulatorial_dados`, `producao_ambulatorial_gmus`
  - Utilidades: `pdf2csv`, `limpa_cache`, `devolvidos`

### ✨ Funcionalidades Anteriores

#### 🗂️ Widget de Planilhas
- **Localização**: Painel direito da interface principal
- **Funcionalidades**:
  - ✏️ Edição de células em tempo real
  - ➕ Adicionar/remover linhas e colunas
  - 💾 Salvar alterações no arquivo original
  - 📤 Exportar para novo arquivo CSV
  - 🗑️ Limpar toda a planilha
  - 🖱️ Menu de contexto (botão direito)
  - 🎨 Cores alternadas nas linhas para melhor legibilidade
  - 📊 Redimensionamento automático de colunas

#### 🔄 Integração Automática
- Ao finalizar uma rotina, o CSV gerado é **automaticamente carregado** no widget de planilhas
- Console de logs mostra o caminho do arquivo gerado
- Botão "Iniciar Exemplo" desabilitado durante processamento

#### 🎨 Layout Aprimorado
- **Splitter Horizontal**: Divide a interface em duas áreas redimensionáveis
  - **Esquerda** (60%): Navegador + Console de Logs + Botões
  - **Direita** (40%): Widget de Planilhas
- Layout responsivo e ajustável pelo usuário

### 🎯 Fluxo de Uso

1. **Selecionar Função**: Escolha uma das 33 funções disponíveis no dropdown
2. **Executar**: Clique no botão "▶️ Executar Função Selecionada"
3. **Acompanhar**: Veja o progresso no console de logs
4. **Visualizar**: O CSV gerado aparece automaticamente na planilha à direita
5. **Editar**: Modifique os dados diretamente na planilha
6. **Salvar**: Use os botões da toolbar para salvar ou exportar

### 📝 Arquivos da Integração Real

1. **`src/workers/thread_worker.py`** (REESCRITO)
   - Classe `OutputRedirector` para capturar stdout/stderr
   - Integração com `DriverCapture` para capturar Selenium
   - Método `execute_autoreg_function()` executa funções reais
   - Monitoramento de URL com `check_driver_url()`
   - Busca automática de CSVs em múltiplos diretórios
   - Tratamento de exceções com traceback completo

2. **`src/core/driver_capture.py`** (NOVO)
   - Intercepta criação de instâncias WebDriver
   - Mantém lista de drivers ativos
   - Permite acesso ao driver mais recente
   - Restaura comportamento original após uso

3. **`src/core/selenium_integration.py`** (NOVO)
   - Funções auxiliares para integração Selenium+Qt
   - Classe `SeleniumMonitor` para sincronização
   - Opções customizadas de Chrome para debug remoto
   - (Preparado para expansões futuras)

4. **`src/ui/main_window.py`** (MODIFICADO)
   - Conecta sinal `url_changed` ao navegador
   - Método `update_browser_url()` sincroniza QWebEngineView
   - Método `handle_error()` exibe mensagens de erro
   - Auto-scroll no console de logs
   - Tratamento de erros com QMessageBox

5. **`run.sh`** (MODIFICADO)
   - PYTHONPATH inclui raiz do autoreg
   - Permite importação do módulo `autoreg`

### 📝 Arquivos Anteriores

1. **`src/ui/main_window.py`** (MODIFICADO ANTERIORMENTE)
   - Adicionado QComboBox com todas as funções do autoreg
   - Método `get_autoreg_functions()` retorna lista de 33 funções
   - Estilização CSS para ComboBox e botão
   - Label descritivo "🛠️ Selecione a Função AutoReg"
   - Desabilita combo durante execução

2. **`src/workers/thread_worker.py`** (MODIFICADO)
   - Atributo `selected_function` para armazenar função escolhida
   - Nome do CSV gerado inclui nome da função
   - Logs dinâmicos baseados na função selecionada

3. **`src/ui/spreadsheet_widget.py`** (NOVO)
   - Widget completo de planilhas com QTableWidget
   - Toolbar com botões de ação
   - Suporte a CSV com encoding UTF-8
   - Menu de contexto com atalhos

4. **`src/ui/spreadsheet_widget.py`** (ANTERIOR)
   - Widget de planilhas com QTableWidget
   - Toolbar com botões de ação
   - Suporte a CSV com encoding UTF-8
   - Menu de contexto com atalhos

### 🚀 Como Usar

1. **Executar a aplicação**:
   ```bash
   cd /home/michel/code/AutoReg/visual-autoreg/AutoReg
   source /home/michel/code/AutoReg/venv/bin/activate
   PYTHONPATH=/home/michel/code/AutoReg/visual-autoreg/AutoReg/src python3 src/main.py
   ```

2. **Fluxo de trabalho**:
   - Clique em "Iniciar Exemplo"
   - Aguarde o processamento (logs aparecem no console)
   - O CSV é automaticamente carregado no painel direito
   - Edite as células diretamente clicando nelas
   - Use os botões da toolbar para manipular dados
   - Salve as alterações com o botão "💾 Salvar"

3. **Atalhos e Recursos**:
   - **Botão Direito** → Menu de contexto com ações rápidas
   - **➕ Linha/Coluna** → Adiciona após a seleção atual
   - **➖ Linha/Coluna** → Remove a seleção atual
   - **📤 Exportar** → Salva em novo arquivo
   - **🗑️ Limpar** → Remove todos os dados (com confirmação)

### 📂 Estrutura de Saída

Os CSVs gerados são salvos em:
```
visual-autoreg/AutoReg/output/
├── codigos_internacao_20251118_143022.csv
├── codigos_internacao_20251118_143155.csv
└── ...
```

### 🔧 Dependências

Nenhuma nova dependência foi adicionada. O projeto continua usando:
- PyQt6
- PyQt6-WebEngine

### 🎯 Próximos Passos

- [ ] Integrar com as funções reais do `autoreg.py`
- [ ] Adicionar validação de dados nas células
- [ ] Implementar filtros e ordenação de colunas
- [ ] Adicionar exportação para outros formatos (Excel, JSON)
- [ ] Implementar busca/substituição em massa
- [ ] Adicionar formatação condicional
