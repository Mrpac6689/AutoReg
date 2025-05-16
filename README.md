# AutoReg
Operação automatizada de Sistemas de Saúde- SISREG &amp; G-HOSP

## Branch Linux

Versão 6.5.1-linux - Maio de 2025
Autor: Michel Ribeiro Paes (MrPaC6689)
Repo: https://github.com/Mrpac6689/AutoReg
Contato michelrpaes@gmail.com
Desenvolvido com o apoio do ChatGPT 4o em Python 3.10.12
Funcional em Ubuntu 24.04 LTS POP_OS

Alterações no port para Linux:
- Removidos os imports de bibliotecas não utilizadas.
- Removido o argumento zoomed do ChromeOptions, pois não é compativel com Linux.
- Adicionado o argumento headless=new para rodar o Chrome em modo oculto.
- Removidos os reajustes da janela de internação.
- Removidos os reajustes da janela de alta.
- Ajuste de foco para frame f_principal antes de chamar configFicha em executar_ficha() para todas as rotinas que acessam fichas no SISREG.
- Substituidos pop-ups de criação de janela extra por prints no campo de logs.
- Removidas bibliotecas inócuas.
- Código de complilação yinstaller --onefile --windowed --icon=icone.png --hidden-import=PIL._tkinter_finder autoreg.py
- Realizados ajustes diversos de caminho de arquivos para o ambiente Linux.
- Ajustado empacotamento em .deb.

# Descrição:
O AUTOREG é um programa desenvolvido para automatizar o processo de internação e alta de pacientes nos sistemas SISREG e G-HOSP, proporcionando maior eficiência e reduzindo o tempo gasto em processos manuais. Utilizando Python, Selenium e Tkinter, o programa oferece uma interface amigável para operar de forma automática o fluxo de trabalho hospitalar.

A automação utiliza Selenium para navegação e manipulação de páginas web de forma automatizada. A interface gráfica foi implementada utilizando Tkinter, proporcionando uma experiência mais interativa e amigável.

# Funcionalidades principais:
Internação automatizada: Captura automaticamente os pacientes a serem internados, identificando nome e número de ficha no SISREG. Executa a internação automaticamente, abre a ficha do paciente, tira um screenshot, escolhe aleatoriamente o profissional internador e permite a entrada da data de internação diretamente pelo ambiente do programa.

Alta automatizada: Extrai as informações dos pacientes do G-HOSP e SISREG, identifica os pacientes aptos para alta e realiza a alta automaticamente no SISREG com base nos motivos capturados.

Comparar e tratar dados: Compara os dados de ambos os sistemas e identifica pacientes que podem ser internados ou receber alta.

Verificação e atualização do ChromeDriver: O programa verifica automaticamente a versão do Google Chrome instalada e atualiza o ChromeDriver para garantir compatibilidade.

Interface gráfica amigável: Dividida em módulos de Internação e Alta, permitindo uma experiência independente e flexível. Um menu intuitivo facilita a escolha das funções e o uso das funcionalidades de forma direta.

# Intalação e utilização

## Requisitos Linux
  - Google Chrome atualizado
  - Ubuntu 24.04 LTS (não testado em outras distros)
  

# Novidades da Versão 6.0
 - Implementada função de internação automatizada
 - Implementada função de alta automatizada

# Novidades da Versão 5.0
 - Acrescentadas as funções captura_cns_restos_alta(), motivo_alta_cns(), executa_saidas_cns() para trabalhar os pacientes não capturados em primeiro momento a dar alta.
 - Acrescentada estrutura de diretorios com versões anteriores
 - Redesenhada interfaçe do módulo alta
 - Redesenhada interfaçe do módulo principal
 - Versão python atualizada para 3.13 de 7 de outubro de 2024

# Versão 5.0.1
 - Acrescentadas as funções captura_cns_restos_alta(), motivo_alta_cns(), executa_saidas_cns() para trabalhar os pacientes não capturados em primeiro momento a dar alta.
 - Acrescentada estrutura de diretorios com versões anteriores
 - Redesenhada interfaçe do módulo alta
 - Redesenhada interfaçe do módulo principal
 - Restaurada função trazer_terminal(), com o G-Hosp, o selenium não consegue trabalhar se a pagina não estiver visível. Assim, foi necessário utilizaer o drive como um serviço do windows e utilizar a função para trazer a janela principal do programa à frente apos rodar o driver.

# Versão 5.1.2
 - Acrescentados motivos de saida ausentes
 - Acrescentada rotina para execução autônoma do modulo de Alta
 - Reduzido tempo para captura de altas

# Novidades da Versão 4.0
  Funções de Internação:
    Captura de pacientes a serem internados com nome e número de ficha.
    Processo de internação automatizado: abertura de ficha, captura de print, escolha aleatória do profissional, e entrada manual da data de internação.
    Retornos em tempo real no ambiente do programa.
  Melhorias nas Funções de Alta:
    Inclusão da opção de configurar o caminho HTTP do sistema G-HOSP, possibilitando adaptação às variações entre diferentes servidores nas unidades de saúde.
    Aumento da velocidade do processo de alta, resultando em uma experiência mais fluida e rápida.
  Ambiente Gráfico Dividido em Dois Módulos: Internação e Alta
    Janela inicial permite selecionar o módulo desejado.
    Independência total entre os módulos, facilitando o uso e prevenindo interferências entre rotinas.
  Compilação em Binário Único
    Windows: Arquivo .exe que agrega todas as bibliotecas necessárias e imagens em Base64, permitindo executar sem necessidade de instalações adicionais.
    MacOS: Versão .app em fase beta com funcionalidades similares, trazendo praticidade.
    Splash Screen acrescentada com a ultima versão do Pyinstaller.

# Versão 4.2.1:
   - Ajustada função executar_multiplas_internacoes() - movidos excepts para o bloco de looping, evitando a quebra do processo em caso de erro ao internar.
   - Pop-ups concentrados em três funções def - Conclusão, Erro e Alerta - Agora chamam uma janela toplevel temporária paraâncora, evitando arrastar a janela de seleção de modulos de volta ao topo, ou deixando o pop-up escondido atrás da janela ativa.
   - Convertido .ico em base64

# Versão 4.2.3:
   -Publicado em Pypi.org   

# Novidades da Versão 3.0:
  Inclusão de função para extrair o código da internação SISREG para todos os pacientes internados no sistema.
  Inclusão de função para ajustar o rol em .csv para correlacionar Nome, Motivo de Alta G-HOSP e Código SISREG.
  Incusão de função para dar alta automática no SISREG conforme motivo de alta capturado.
  Melhorada interface visual

# Novidades da Versão 2.0:
  Atualização automática do ChromeDriver: O programa agora detecta a versão do Google Chrome e baixa automaticamente a versão compatível do ChromeDriver a partir de um JSON fornecido pela Google.
  Nova Interface Gráfica: A interface foi redesenhada com Tkinter para melhorar a interatividade e facilitar o uso do programa.
  Verificação de versão e documentação: O novo menu "Informações" inclui a opção de visualizar a versão do programa e acessar o conteúdo do arquivo README.md diretamente pela interface gráfica.

# Clonando o Repostirório e instalando Dependências:
Caso opte clonar o repositório, utilize o comando:

      git clone https://github.com/Mrpac6689/AutoReg.git

Nesse caso, é necessário instalar as seguintes bibliotecas e ferramentas:

  Python (versão 3 ou superior)
  Selenium: Biblioteca para automação de navegadores.
  ConfigParser: Para ler arquivos de configuração.
  Tkinter: Biblioteca gráfica para criar a interface (geralmente incluída com o Python)

    Bibliotecas e versões específicas
      altgraph==0.17.4
      attrs==24.2.0
      beautifulsoup4==4.12.3
      bs4==0.0.2
      certifi==2024.8.30
      cffi==1.17.1
      charset-normalizer==3.4.0
      configparser==7.1.0
      h11==0.14.0
      idna==3.10
      numpy==2.1.3
      outcome==1.3.0.post0
      packaging==24.1
      pandas==2.2.3
      pefile==2023.2.7
      pillow==11.0.0
      pycparser==2.22
      PyGetWindow==0.0.9
      pyinstaller==6.11.0
      pyinstaller-hooks-contrib==2024.9
      PyRect==0.2.0
      PySocks==1.7.1
      python-dateutil==2.9.0.post0
      pytz==2024.2
      pywin32-ctypes==0.2.3
      requests==2.32.3
      selenium==4.26.1
      setuptools==75.3.0
      six==1.16.0
      sniffio==1.3.1
      sortedcontainers==2.4.0
      soupsieve==2.6
      tk==0.1.0
      trio==0.27.0
      trio-websocket==0.11.1
      typing_extensions==4.12.2
      tzdata==2024.2
      urllib3==2.2.3
      websocket-client==1.8.0
      wheel==0.44.0
      wsproto==1.2.0


Abra o Prompt de Comando ou Terminal no diretório do programa e execute os seguintes comandos:

    pip install -r requirements.txt
    pip install .
    pip install setup.py install

Para executar:
     
     python ./autoreg.py

# Ferramentas externas necessárias:
  Google Chrome: O navegador utilizado para a automação.
  ChromeDriver: Ferramenta necessária para automatizar o Chrome. Caso a versão disponivel neste repositório seja incompativel com seu navegador, a versão compativel do ChromeDriver pode ser baixada atraves da interface principal.
  
# Configuração de Credenciais:
  Antes de rodar o programa ou script, é necessário configurar suas credenciais de acesso ao SISREG e G-HOSP.

## Passo a passo para inserir suas credenciais:
  Após abrir o programa, clique em 'Configurações >  Editar cofig.ini' 
  Edite o arquivo config.ini e insira suas credenciais conforme o exemplo abaixo:

    [SISREG]
    usuario = seu_usuario_sisreg
    senha = sua_senha_sisreg

    [G-HOSP]
    usuario = seu_usuario_ghosp
    senha = sua_senha_ghosp
    caminho = http://10.0.0.0  #entre com o endereço local do G-Hosp. As portas serão selecionadas automaticamente.

  Salve o arquivo após adicionar suas credenciais.
  Agora você está pronto para executar o programa.

# Erros Comuns e Soluções:
  Erro de versão do ChromeDriver:
    Se receber uma mensagem de erro indicando que a versão do ChromeDriver não é compatível, o programa já foi atualizado para corrigir isso automaticamente. Caso persista, baixe a versão correta manualmente ou verifique se o ChromeDriver foi atualizado corretamente no diretório do programa.

  Erro de conexão ou acesso negado:
    Certifique-se de que suas credenciais de acesso ao SISREG e G-HOSP estão corretas no arquivo config.ini.

Créditos:
  Desenvolvimento: Michel Ribeiro Paes (Github MrPaC6689)
  Suporte técnico e IA de apoio: ChatGPT 4o
Licença:
  Este projeto foi desenvolvido para fins educacionais sob licença Creative Commons 1.0 Universal. Todos os direitos são reservados ao autor.

Esperamos que o AUTOREG continue a facilitar sua rotina e ajude no processo de internação e alta de pacientes!

FIM DO LEIA-ME
