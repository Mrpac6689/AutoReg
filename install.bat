@echo off
@echo off
REM AutoReg - Script de Instalação para Windows
REM Versão 8.5.0 - Setembro de 2025
REM Autor: Michel Ribeiro Paes (MrPaC6689)

setlocal enabledelayedexpansion

REM 1. Identifica pasta do usuário
set USERDIR=%USERPROFILE%

REM 2. Move dados da aplicação para %USERDIR%\.autoreg
set INSTALLDIR=%USERDIR%\.autoreg
if exist "%INSTALLDIR%" (
    echo [AVISO] Removendo instalação anterior em %INSTALLDIR%...
    rmdir /s /q "%INSTALLDIR%"
)
mkdir "%INSTALLDIR%"
xcopy /E /I /Q . "%INSTALLDIR%" >nul

REM 3. Cria pasta %USERDIR%\AutoReg
set LOGDIR=%USERDIR%\AutoReg
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM 4. Cria arquivo vazio %USERDIR%\AutoReg\autoreg.log
type nul > "%LOGDIR%\autoreg.log"

REM 5. Acessa o diretório da aplicação
cd /d "%INSTALLDIR%"

REM 6. Verifica existência do Python3
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python3 não encontrado. Instale Python 3.7+ antes de continuar.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM 7. Verifica/cria ambiente virtual venv
if not exist "%INSTALLDIR%\venv" (
    echo [INFO] Criando ambiente virtual...
    %PYTHON_CMD% -m venv "%INSTALLDIR%\venv"
)

REM 8. Instala dependências
if exist "requirements.txt" (
    "%INSTALLDIR%\venv\Scripts\pip.exe" install --upgrade pip
    "%INSTALLDIR%\venv\Scripts\pip.exe" install -r requirements.txt
) else (
    "%INSTALLDIR%\venv\Scripts\pip.exe" install selenium pandas beautifulsoup4 pillow
)

REM 9. Determina caminhos absolutos
set PYTHONBIN=%INSTALLDIR%\venv\Scripts\python.exe
set AUTOREGPY=%INSTALLDIR%\autoreg.py

REM 10. Cria script autoreg.bat
(echo @echo off
echo cd /d "%INSTALLDIR%"
echo "%PYTHONBIN%" "%AUTOREGPY%" %%*
) > "%INSTALLDIR%\autoreg.bat"

REM 11. Adiciona ao PATH
set KEY="HKCU\Environment"
for /f "tokens=3*" %%i in ('reg query %KEY% /v PATH 2^>nul') do set USER_PATH=%%i %%j
if "!USER_PATH!"=="" set USER_PATH=%INSTALLDIR%
if "!USER_PATH!"=="!USER_PATH:%INSTALLDIR%=!" (
    set NEW_PATH=!USER_PATH!;%INSTALLDIR%
) else (
    set NEW_PATH=!USER_PATH!
)
reg add %KEY% /v PATH /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Não foi possível atualizar o PATH automaticamente.
    echo [INFO] Adicione manualmente ao PATH: %INSTALLDIR%
) else (
    echo [OK] PATH atualizado.
)

echo.
echo [OK] Instalação do AutoReg 8.5.0 concluída!
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
