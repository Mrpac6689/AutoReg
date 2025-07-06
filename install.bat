@echo off
REM AutoReg - Script de Instalação para Windows
REM Versão 7.0.0-1 - Julho de 2025
REM Autor: Michel Ribeiro Paes (MrPaC6689)

setlocal enabledelayedexpansion

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════════╗
echo ║                              AutoReg Installer                                ║
echo ║                    Automatização de Sistemas de Saúde                         ║
echo ║                               SISREG ^& G-HOSP                                ║
echo ╠═══════════════════════════════════════════════════════════════════════════════╣
echo ║ Versão: 7.0.0-1                                                               ║
echo ║ Autor: Michel Ribeiro Paes (MrPaC6689)                                        ║
echo ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar se Python está instalado
echo [INFO] Verificando instalação do Python...
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python não está instalado ou não está no PATH
        echo [INFO] Baixe o Python em: https://python.org
        echo [INFO] Certifique-se de marcar 'Add Python to PATH' durante a instalação
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
        echo [OK] Python3 encontrado
    )
) else (
    set PYTHON_CMD=python
    echo [OK] Python encontrado
)

REM Verificar versão do Python
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Versão do Python: !PYTHON_VERSION!

REM Verificar se pip está instalado
echo [INFO] Verificando instalação do pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip não está instalado
    echo [INFO] Execute: %PYTHON_CMD% -m ensurepip --upgrade
    pause
    exit /b 1
) else (
    echo [OK] pip encontrado
)

REM Verificar se venv está disponível
echo [INFO] Verificando disponibilidade do venv...
%PYTHON_CMD% -m venv --help >nul 2>&1
if errorlevel 1 (
    echo [ERRO] venv não está disponível
    echo [INFO] Execute: %PYTHON_CMD% -m pip install virtualenv
    pause
    exit /b 1
) else (
    echo [OK] venv está disponível
)

REM Definir diretório de instalação
set INSTALL_DIR=%USERPROFILE%\.autoreg

REM Remover instalação anterior se existir
if exist "%INSTALL_DIR%" (
    echo [INFO] Removendo instalação anterior...
    rmdir /s /q "%INSTALL_DIR%"
)

REM Criar diretório de instalação
echo [INFO] Criando diretório de instalação...
mkdir "%INSTALL_DIR%"
if errorlevel 1 (
    echo [ERRO] Não foi possível criar o diretório %INSTALL_DIR%
    pause
    exit /b 1
)

echo [OK] Diretório criado: %INSTALL_DIR%

REM Copiar arquivos
echo [INFO] Copiando arquivos do AutoReg...
xcopy /E /I /Q . "%INSTALL_DIR%" >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao copiar arquivos
    pause
    exit /b 1
)

REM Limpar arquivos desnecessários
cd /d "%INSTALL_DIR%"
if exist ".git" rmdir /s /q ".git" >nul 2>&1
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
if exist "Versoes Historicas" rmdir /s /q "Versoes Historicas" >nul 2>&1
del /q *.pyc >nul 2>&1

echo [OK] Arquivos copiados com sucesso

REM Criar ambiente virtual
echo [INFO] Criando ambiente virtual...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual
    pause
    exit /b 1
)

echo [OK] Ambiente virtual criado

REM Instalar dependências
echo [INFO] Instalando dependências Python...
"%INSTALL_DIR%\venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1

if exist "requirements.txt" (
    "%INSTALL_DIR%\venv\Scripts\pip.exe" install -r requirements.txt
    if errorlevel 1 (
        echo [AVISO] Falha ao instalar algumas dependências do requirements.txt
        echo [INFO] Instalando dependências básicas...
        "%INSTALL_DIR%\venv\Scripts\pip.exe" install selenium pandas beautifulsoup4 pillow
    ) else (
        echo [OK] Dependências instaladas com sucesso
    )
) else (
    echo [AVISO] Arquivo requirements.txt não encontrado
    echo [INFO] Instalando dependências básicas...
    "%INSTALL_DIR%\venv\Scripts\pip.exe" install selenium pandas beautifulsoup4 pillow
)

REM Criar script executável
echo [INFO] Criando script executável...
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo "%INSTALL_DIR%\venv\Scripts\python.exe" autoreg.py %%*
) > "%INSTALL_DIR%\autoreg.bat"

echo [OK] Script executável criado

REM Adicionar ao PATH do usuário
echo [INFO] Configurando PATH do usuário...
for /f "tokens=3*" %%i in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set USER_PATH=%%i %%j
if "!USER_PATH!"=="" set USER_PATH=%INSTALL_DIR%
if "!USER_PATH!"=="!USER_PATH:%INSTALL_DIR%=!" (
    set NEW_PATH=!USER_PATH!;%INSTALL_DIR%
) else (
    set NEW_PATH=!USER_PATH!
)

reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Não foi possível atualizar o PATH automaticamente
    echo [INFO] Adicione manualmente ao PATH: %INSTALL_DIR%
) else (
    echo [OK] PATH atualizado
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo           INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ═══════════════════════════════════════════════════════════════
echo.
echo [INFO] AutoReg foi instalado em: %INSTALL_DIR%
echo [INFO] Para usar, abra um novo prompt de comando e digite: autoreg --help
echo.
echo [INFO] Exemplos de uso:
echo   autoreg -eci                  # Extrai códigos de internação
echo   autoreg --all                 # Executa workflow completo
echo   autoreg --config              # Edita configuração
echo.
echo [AVISO] Não esqueça de configurar o arquivo config.ini antes do primeiro uso!
echo [INFO] Execute: autoreg --config
echo.
echo [INFO] Reinicie o prompt de comando para usar o comando 'autoreg'
echo.

pause
