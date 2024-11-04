AUTOREG

Automação de Pacientes a Dar Alta - SISREG & G-HOSP
Versão 3.0 - Outubro de 2024
Autor: Michel Ribeiro Paes (MrPaC6689)
Contato michelrpaes@gmail.com
Desenvolvido com o apoio do ChatGPT em Python 3.2

Descrição:
  Este programa automatiza o processo de extração e comparação de informações de pacientes internados no sistema SISREG e G-HOSP, com o objetivo de identificar os pacientes aptos para alta hospitalar. Além disso, o sistema agora verifica automaticamente as versões do ChromeDriver e realiza atualizações quando necessário, garantindo compatibilidade com o navegador Google Chrome.

A automação utiliza Selenium para navegação e manipulação de páginas web de forma automatizada. A interface gráfica foi implementada utilizando Tkinter, proporcionando uma experiência mais interativa e amigável.

Funcionalidades principais:
  Extrair internados do SISREG: Executa um script automatizado para obter a lista de pacientes internados no sistema SISREG.
  Extrair internados do G-HOSP: Executa um script automatizado para obter a lista de pacientes internados no sistema G-HOSP.
  Comparar e tratar dados: Compara os dados de ambos os sistemas e identifica pacientes que podem receber alta.
  Executar alta automática no SISREG com base nos motivos de alta capturados.
  Verificar e atualizar o ChromeDriver: Verifica a versão do Google Chrome instalada e atualiza automaticamente o ChromeDriver para garantir compatibilidade.
  Interface interativa: Menu simples e intuitivo para facilitar a escolha das funções.
  Exibir informações de versão e documentação: Funções de menu para visualizar a versão do programa e abrir o conteúdo do arquivo README.md.

Novidades da Versão 3.0:
  Inclusão de função para extrair o código da internação SISREG para todos os pacientes internados no sistema.
  Inclusão de função para ajustar o rol em .csv para correlacionar Nome, Motivo de Alta G-HOSP e Código SISREG.
  Incusão de função para dar alta automática no SISREG conforme motivo de alta capturado.
  Melhorada interface visual

Novidades da Versão 2.0:
  Atualização automática do ChromeDriver: O programa agora detecta a versão do Google Chrome e baixa automaticamente a versão compatível do ChromeDriver a partir de um JSON fornecido pela Google.
  Nova Interface Gráfica: A interface foi redesenhada com Tkinter para melhorar a interatividade e facilitar o uso do programa.
  Verificação de versão e documentação: O novo menu "Informações" inclui a opção de visualizar a versão do programa e acessar o conteúdo do arquivo README.md diretamente pela interface gráfica.

Dependências:
Caso opte-se por não executar o programa já compilado, é necessário instalar as seguintes bibliotecas e ferramentas:

  Python (versão 3.6 ou superior)
  Selenium: Biblioteca para automação de navegadores.
  ConfigParser: Para ler arquivos de configuração.
  Colorama: Para adicionar cores ao terminal. (datado para v.3.0)
  Tkinter: Biblioteca gráfica para criar a interface (geralmente incluída com o Python).

Como instalar as dependências:
Abra o Prompt de Comando ou Terminal no diretório do programa e execute os seguintes comandos:

  pip install selenium
  pip install configparser
  pip install colorama (datado para v.3.0)
  pip install pandas

Ferramentas externas:
  Google Chrome: O navegador utilizado para a automação.
  ChromeDriver: Ferramenta necessária para automatizar o Chrome. A versão correta do ChromeDriver será baixada automaticamente com base na versão do Google Chrome instalada.

Configuração de Credenciais:
  Antes de rodar o programa ou script, é necessário configurar suas credenciais de acesso ao SISREG e G-HOSP.

Passo a passo para inserir suas credenciais:
  Após abrir o programa, clique em 'Configurações >  Editar cofig.ini' 
  Edite o arquivo config.ini e insira suas credenciais conforme o exemplo abaixo:

    [SISREG]
    usuario = seu_usuario_sisreg
    senha = sua_senha_sisreg

    [G-HOSP]
    usuario = seu_usuario_ghosp
    senha = sua_senha_ghosp

  Salve o arquivo após adicionar suas credenciais.
  Agora você está pronto para executar o programa.

Como executar o programa:
    Se Compilado, execute o arquivo Autoreg3.exe

    Como script python, no terminal, execute:
      python ./Autoreg3.py

Erros Comuns e Soluções:
  Erro de versão do ChromeDriver:
    Se receber uma mensagem de erro indicando que a versão do ChromeDriver não é compatível, o programa já foi atualizado para corrigir isso automaticamente. Caso persista, baixe a versão correta manualmente ou verifique se o ChromeDriver foi atualizado corretamente no diretório do programa.

  Erro de conexão ou acesso negado:
    Certifique-se de que suas credenciais de acesso ao SISREG e G-HOSP estão corretas no arquivo config.ini.

Créditos:
  Desenvolvimento: MrPaC6689
  Suporte técnico e IA de apoio: ChatGPT
Licença:
  Este projeto foi desenvolvido para fins educacionais e não possui uma licença formal. Todos os direitos são reservados ao autor.

Esperamos que o programa continue a facilitar sua rotina e ajude no processo de alta de pacientes!

FIM DO LEIA-ME