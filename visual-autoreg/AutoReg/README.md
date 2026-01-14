# 🏥 AutoReg - Interface Gráfica

Aplicação GUI moderna para o sistema AutoReg, construída com PyQt6 e QWebEngineView.

## 🎯 Características

- **🔧 33 Funções Disponíveis**: Dropdown com todas as funções do AutoReg
- **🌐 Navegador Embutido**: Automação visível em tempo real (QWebEngineView)
- **📊 Planilha Integrada**: Edição de CSVs diretamente na interface
- **📟 Console de Logs**: Acompanhamento do progresso em tempo real
- **⚡ Interface Fluida**: Multithreading evita travamentos
- **🎨 Layout Responsivo**: Painéis redimensionáveis com QSplitter

## 🚀 Como Executar

### Método 1: Script de Execução (Recomendado)
```bash
./run.sh
```

### Método 2: Python Direto
```bash
PYTHONPATH=src /home/michel/code/AutoReg/venv/bin/python src/main.py
```

### Método 3: Usando o ambiente virtual
```bash
source /home/michel/code/AutoReg/venv/bin/activate
PYTHONPATH=src python src/main.py
```

## 📦 Instalação de Dependências

```bash
pip install -r requirements.txt
```

## 🏗️ Estrutura do Projeto

```
AutoReg/
├── src/
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── ui/                  # Componentes de interface
│   │   ├── main_window.py   # Janela principal
│   │   ├── browser_widget.py # Navegador embutido
│   │   └── styles.py        # Estilos CSS/Qt
│   ├── workers/             # Threads de trabalho
│   │   └── thread_worker.py # Worker para tarefas assíncronas
│   ├── core/                # Lógica de negócio
│   │   ├── automation.py    # Automações
│   │   └── config.py        # Configurações
│   ├── utils/               # Utilitários
│   │   └── helpers.py       # Funções auxiliares
│   └── resources/           # Recursos (ícones, etc)
├── requirements.txt
├── run.sh                   # Script de execução
└── README.md
```

## ✨ Funcionalidades

- ✅ Navegador embutido (QWebEngineView)
- ✅ Console de logs integrado
- ✅ Execução assíncrona com QThreads
- ✅ Interface moderna e responsiva
- 🚧 Integração com automações do SISREG/G-HOSP (em desenvolvimento)

## 🔧 Problemas Resolvidos

### ImportError: attempted relative import beyond top-level package
**Solução:** Os imports foram convertidos de relativos para absolutos, e o `sys.path` é configurado no `main.py` para incluir o diretório `src`.

### TypeError: setUrl expects QUrl not str
**Solução:** O `browser_widget.py` agora converte strings para `QUrl` automaticamente.

## 📝 Notas de Desenvolvimento

- Os imports são absolutos a partir do diretório `src/`
- O `PYTHONPATH` deve incluir o diretório `src/` para que os imports funcionem
- Use o script `run.sh` para executar sem preocupações com paths Project

AutoReg é uma aplicação desenvolvida em Python utilizando PyQt6, projetada para automatizar a extração de códigos de internação através de uma interface gráfica moderna. A aplicação inclui um navegador embutido e suporte a multithreading, permitindo que tarefas demoradas sejam executadas em segundo plano sem travar a interface do usuário.

## Estrutura do Projeto

O projeto possui a seguinte estrutura de arquivos:

```
AutoReg
├── src
│   ├── main.py                # Ponto de entrada da aplicação
│   ├── ui
│   │   ├── __init__.py        # Inicializador do pacote ui
│   │   ├── main_window.py      # Classe que define a interface principal
│   │   ├── browser_widget.py    # Classe que encapsula o navegador
│   │   └── styles.py          # Estilos e temas personalizados
│   ├── core
│   │   ├── __init__.py        # Inicializador do pacote core
│   │   ├── automation.py       # Funções de automação
│   │   └── config.py          # Configurações e constantes
│   ├── workers
│   │   ├── __init__.py        # Inicializador do pacote workers
│   │   └── thread_worker.py    # Classe que executa tarefas em segundo plano
│   ├── utils
│   │   ├── __init__.py        # Inicializador do pacote utils
│   │   └── helpers.py         # Funções auxiliares
│   └── resources
│       ├── __init__.py        # Inicializador do pacote resources
│       └── icons               # Ícones e imagens utilizados na interface
├── requirements.txt            # Dependências do projeto
├── setup.py                    # Configuração da instalação do pacote
└── README.md                   # Documentação do projeto
```

## Instalação

Para instalar as dependências do projeto, execute o seguinte comando:

```
pip install -r requirements.txt
```

## Uso

Para iniciar a aplicação, execute o arquivo `main.py`:

```
python src/main.py
```

A interface gráfica será exibida, permitindo que você inicie o processo de extração de códigos de internação. O console de logs exibirá o progresso das operações.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests para melhorias e correções.

## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.