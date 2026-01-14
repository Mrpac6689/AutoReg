# 🔌 Integração com AutoReg Original

## Como Funciona

### 1. 🎯 Execução de Funções Reais

Quando você seleciona uma função no dropdown e clica em "Executar":

```python
# ThreadWorker importa o módulo autoreg dinamicamente
import autoreg
func = getattr(autoreg, self.selected_function)
func()  # Executa a função real!
```

### 2. 📟 Redirecionamento de Logs

Todo `print()` e `logging.info()` das funções originais é capturado:

```
Original: print("Acessando SISREG...")
         ↓
OutputRedirector captura
         ↓
log_signal.emit("Acessando SISREG...")
         ↓
Console GUI: "Acessando SISREG..."
```

### 3. 🌐 Captura do Navegador Selenium

O sistema intercepta a criação do WebDriver:

```
autoreg função cria: driver = webdriver.Chrome()
         ↓
DriverCapture intercepta __init__
         ↓
Driver armazenado em lista
         ↓
ThreadWorker monitora URL
         ↓
url_changed signal emitido
         ↓
QWebEngineView sincronizado!
```

### 4. 📊 Detecção de CSVs

Após a execução, o sistema procura CSVs novos:

```python
# Busca em múltiplos diretórios
~/AutoReg/*.csv
visual-autoreg/AutoReg/output/*.csv
$(pwd)/*.csv

# Filtra por data (últimos 60 segundos)
# Carrega automaticamente na planilha
```

## 🔧 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        MainWindow                            │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ QWebEngineView │  │ Log Console  │  │ SpreadsheetWidget││
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└───────────────┬─────────────────────────────────────────────┘
                │ signals (log_signal, url_changed, csv_generated)
                ↓
┌───────────────────────────────────────────────────────────────┐
│                      ThreadWorker (QThread)                   │
│                                                               │
│  stdout ─→ OutputRedirector ─→ log_signal                    │
│                                                               │
│  import autoreg                                               │
│  func = getattr(autoreg, selected_function)                  │
│  func() ←─── Executa função REAL                             │
│       │                                                       │
│       └──→ cria WebDriver                                    │
│              │                                                │
│              ↓                                                │
│       DriverCapture intercepta                                │
│              │                                                │
│              └──→ check_driver_url() ─→ url_changed signal   │
└───────────────────────────────────────────────────────────────┘
                │
                ↓
┌───────────────────────────────────────────────────────────────┐
│                    Módulo autoreg                             │
│                                                               │
│  extrai_codigos_internacao()                                  │
│  interna_pacientes()                                          │
│  solicita_sisreg()                                            │
│  ... 30+ funções                                              │
└───────────────────────────────────────────────────────────────┘
```

## 🚀 Fluxo de Execução Completo

1. **Usuário seleciona função** no dropdown
2. **Clica em "Executar"**
3. **ThreadWorker inicia** em thread separada
4. **stdout/stderr redirecionados** para GUI
5. **DriverCapture ativado** para interceptar Selenium
6. **Função real importada** do módulo `autoreg`
7. **Função executada** (pode levar minutos)
8. **Logs aparecem** em tempo real no console
9. **WebDriver criado** durante execução
10. **Driver capturado** pelo DriverCapture
11. **URL monitorada** a cada 500ms
12. **QWebEngineView atualizado** com URL do Selenium
13. **Função termina** e gera CSV
14. **CSV detectado** automaticamente
15. **Planilha carregada** com dados
16. **Botões reabilitados** para nova execução

## ⚙️ Configurações Importantes

### PYTHONPATH
```bash
export PYTHONPATH="$PWD/src:$PWD/../../../"
#                   ↑           ↑
#                   |           └─ Raiz do AutoReg (para import autoreg)
#                   └─ src/ (para imports internos)
```

### Diretórios de Busca de CSV
```python
search_paths = [
    os.path.expanduser('~/AutoReg'),          # Padrão do autoreg
    'visual-autoreg/AutoReg/output',           # Output da GUI
    os.getcwd(),                               # Diretório atual
]
```

## 🌐 Sincronização do Navegador

### Duas Abordagens Implementadas:

#### 1. **Sincronização de URL (Padrão)**
- O QWebEngineView carrega a mesma URL que o Selenium
- Vantagem: Leve, não consome recursos
- Desvantagem: Sessão separada (cookies diferentes)

#### 2. **Modo Screenshot (Opcional)**
- Captura screenshots do Selenium a cada segundo
- Vantagem: Mostra exatamente o que o Selenium vê
- Desvantagem: Consome mais recursos

### Como Ativar Modo Screenshot:

No `main_window.py`, método `connect_driver()`, descomente:
```python
self.browser.enable_screenshot_mode()
```

### Limitação Conhecida:

O QWebEngineView e o Selenium usam **sessões separadas**. Isso significa:
- ✅ Você vê a mesma página
- ❌ Cookies e sessões não são compartilhados
- ❌ Login do Selenium não reflete no QWebEngineView

Para visualização **real** do que o Selenium está fazendo:
- Use o **Modo Screenshot**
- Ou mantenha a janela do Chrome visível (comportamento atual)

## 🐛 Debug e Troubleshooting

### Logs não aparecem
- Verifique se a função usa `print()` ou `logging`
- stdout/stderr devem estar sendo redirecionados corretamente

### Navegador não sincroniza
- Função pode não usar Selenium
- DriverCapture pode não ter interceptado o __init__
- URL pode ser "data:," (ignorada)

### CSV não carrega
- Verifique se foi gerado em um dos diretórios monitorados
- Arquivo deve ter menos de 60 segundos
- Extensão deve ser `.csv`

### Erros de Import
- Verifique PYTHONPATH
- Módulo `autoreg` deve estar acessível
- Ambiente virtual deve estar ativado

## 📚 Próximos Passos

- [ ] Implementar sincronização bidirecional (GUI → Selenium)
- [ ] Adicionar controles de pausa/retomar
- [ ] Capturar screenshots do Selenium
- [ ] Implementar debug remoto do Chrome
- [ ] Adicionar cache de credenciais na GUI
- [ ] Permitir input de parâmetros por função
