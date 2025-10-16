@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Face Liveness Detection Bootstrap
echo ========================================
echo.

:: Verificar se Python está instalado
echo [1/6] Verificando instalacao do Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Por favor, instale Python 3.8+ antes de continuar.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% encontrado!
echo.

:: Verificar se pip está disponível
echo [2/6] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: pip nao encontrado. Por favor, reinstale Python com pip incluido.
    pause
    exit /b 1
)
echo pip disponivel!
echo.

:: Criar ambiente virtual se não existir
echo [3/6] Configurando ambiente virtual...
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso!
) else (
    echo Ambiente virtual ja existe.
)
echo.

:: Ativar ambiente virtual
echo [4/6] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRO: Falha ao ativar ambiente virtual.
    pause
    exit /b 1
)
echo Ambiente virtual ativado!
echo.

:: Configurar bibliotecas dinâmicas
set "LD_LIBRARY_PATH=%cd%\openvino;%cd%\facewrapper\libs;%LD_LIBRARY_PATH%"
set "PATH=%cd%\openvino;%cd%\facewrapper\libs;%PATH%"
echo LD_LIBRARY_PATH/PATH configurados para openvino e facewrapper\libs
echo.

:: Instalar dependências
echo [5/6] Instalando dependencias...
echo Instalando pacotes do requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias.
    echo Verifique se o arquivo requirements.txt existe e esta correto.
    pause
    exit /b 1
)
echo Dependencias instaladas com sucesso!
echo.

:: Verificar LICENSE_KEY
echo [6/6] Verificando configuracao...
if "%LICENSE_KEY%"=="" (
    echo.
    echo ==========================================
    echo   ATENCAO: LICENSE_KEY NAO CONFIGURADA
    echo ==========================================
    echo.
    echo Para usar este projeto, voce precisa configurar a LICENSE_KEY.
    echo.
    echo Opcoes:
    echo 1. Definir variavel de ambiente: set LICENSE_KEY=sua_chave_aqui
    echo 2. Criar arquivo license.txt na raiz do projeto
    echo 3. Obter uma chave em: https://faceonlive.com
    echo.
    echo O projeto tentara usar o modo offline se disponivel.
    echo Continuando automaticamente...
    timeout /t 3 /nobreak >nul
) else (
    echo LICENSE_KEY configurada: %LICENSE_KEY:~0,10%...
)
echo.

:: Configurar portas padrão se não definidas
if "%PORT%"=="" set PORT=8000
if "%GRADIO_PORT%"=="" set GRADIO_PORT=7860

echo ========================================
echo   INICIANDO SERVICOS
echo ========================================
echo.
echo Flask API sera executada em: http://localhost:%PORT%
echo Gradio Interface sera executada em: http://localhost:%GRADIO_PORT%
echo.
echo Pressione Ctrl+C para parar os servicos.
echo.

:: Criar arquivo temporário para controlar processos
echo. > .bootstrap_running

:: Iniciar Flask API em background
echo Iniciando Flask API...
start /b python app.py

:: Aguardar um pouco para Flask inicializar
timeout /t 3 /nobreak >nul

:: Iniciar Gradio Interface
echo Iniciando Gradio Interface...
python gradio\demo.py

:: Cleanup ao sair
echo.
echo Parando servicos...
taskkill /f /im python.exe >nul 2>&1
del .bootstrap_running >nul 2>&1

echo.
echo Bootstrap finalizado.
pause
