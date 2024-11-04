# AutoReg
Operação automatizada de Sistemas de Saúde- SISREG &amp; G-HOSP

Versão 4.0 - Novembro de 2024
Autor: Michel Ribeiro Paes (MrPaC6689)
Contato michelrpaes@gmail.com
Desenvolvido com o apoio do ChatGPT em Python 3.2

# Descrição:
O AUTOREG 4.0 é um programa desenvolvido para automatizar o processo de internação e alta de pacientes nos sistemas SISREG e G-HOSP, proporcionando maior eficiência e reduzindo o tempo gasto em processos manuais. Utilizando Python 3.11, Selenium e Tkinter, o programa oferece uma interface amigável para operar de forma automática o fluxo de trabalho hospitalar.

A automação utiliza Selenium para navegação e manipulação de páginas web de forma automatizada. A interface gráfica foi implementada utilizando Tkinter, proporcionando uma experiência mais interativa e amigável.

# Funcionalidades principais:
Internação automatizada: Captura automaticamente os pacientes a serem internados, identificando nome e número de ficha no SISREG. Executa a internação automaticamente, abre a ficha do paciente, tira um screenshot, escolhe aleatoriamente o profissional internador e permite a entrada da data de internação diretamente pelo ambiente do programa.

Alta automatizada: Extrai as informações dos pacientes do G-HOSP e SISREG, identifica os pacientes aptos para alta e realiza a alta automaticamente no SISREG com base nos motivos capturados.

Comparar e tratar dados: Compara os dados de ambos os sistemas e identifica pacientes que podem ser internados ou receber alta.

Verificação e atualização do ChromeDriver: O programa verifica automaticamente a versão do Google Chrome instalada e atualiza o ChromeDriver para garantir compatibilidade.

Interface gráfica amigável: Dividida em módulos de Internação e Alta, permitindo uma experiência independente e flexível. Um menu intuitivo facilita a escolha das funções e o uso das funcionalidades de forma direta.

Compilação para binário único:

   Windows: Arquivo .exe que inclui todas as dependências, eliminando a necessidade de instalação do Python e das bibliotecas.

# Utilização - Aplicativo para Windows

Baixe o último Release para windows pelo link abaixo, descompacte o .tar e execute o arquivo Autoreg_v4_2.exe. Certifique-se de ter o Google Chrome instalado, e de realizar a verificação de compatibilidade do Driver pelo menu superior 'Configurações'.

      https://github.com/Mrpac6689/AutoReg/releases/tag/v4.2.0

# Utilização - Script global

Para desenvolvedores, o Script pode ser baixado utilizando Pypi com o comando abaixo, transformando-o em um comando global

No terminal digite:
      
      pip install AutoReg-Mrpac6689

Execute com:

      autoreg

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

  Python (versão 3.6 ou superior)
  Selenium: Biblioteca para automação de navegadores.
  ConfigParser: Para ler arquivos de configuração.
  Tkinter: Biblioteca gráfica para criar a interface (geralmente incluída com o Python)

    Bibliotecas e versões específicas
      attrs==24.2.0
      beautifulsoup4==4.12.3
      bs4==0.0.2
      certifi==2024.8.30
      cffi==1.17.1
      charset-normalizer==3.4.0
      configparser==7.1.0
      h11==0.14.0
      idna==3.10
      numpy==2.1.2
      outcome==1.3.0.post0
      packaging==24.1
      pandas==2.2.2
      pillow==11.0.0
      pycparser==2.22
      PyGetWindow==0.0.9
      PyRect==0.2.0
      PySocks==1.7.1
      python-dateutil==2.9.0.post0
      python-dotenv==1.0.1
      pytz==2024.2
      requests==2.32.0
      selenium==4.24.0
      six==1.16.0
      sniffio==1.3.1
      sortedcontainers==2.4.0
      soupsieve==2.6
      trio==0.27.0
      trio-websocket==0.11.1
      typing_extensions==4.12.2
      tzdata==2024.2
      Unidecode==1.3.8
      urllib3==2.2.3
      webdriver-manager==4.0.2
      websocket-client==1.8.0
      wsproto==1.2.0

Abra o Prompt de Comando ou Terminal no diretório do programa e execute os seguintes comandos:

    pip install -r requirements.txt

Para executar:
     
     python ./Autoreg4.py

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
  Este projeto foi desenvolvido para fins educacionais e não possui uma licença formal. Todos os direitos são reservados ao autor.

Esperamos que o AUTOREG 4.0 continue a facilitar sua rotina e ajude no processo de internação e alta de pacientes!

FIM DO LEIA-ME
