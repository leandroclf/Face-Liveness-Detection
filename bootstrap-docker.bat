@echo off
REM ============================================================================
REM Face Liveness Detection - Bootstrap Docker para Windows
REM ============================================================================
REM Este script configura e executa o ambiente Docker completo
REM Resolve problemas de compatibilidade e bibliotecas nativas
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo  🐳 Face Liveness Detection - Bootstrap Docker
echo ============================================================================
echo  Configurando ambiente Docker completo...
echo.

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Docker não está instalado ou não está no PATH
    echo.
    echo 📋 Instruções de instalação:
    echo    1. Baixe Docker Desktop: https://www.docker.com/products/docker-desktop
    echo    2. Execute a instalação
    echo    3. Reinicie o sistema
    echo    4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Docker detectado: 
docker --version

REM Verificar se Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Docker não está rodando
    echo.
    echo 📋 Soluções:
    echo    1. Inicie Docker Desktop
    echo    2. Aguarde a inicialização completa
    echo    3. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Docker está rodando

REM Configurar variáveis
set IMAGE_NAME=face-liveness-detection
set CONTAINER_NAME=face-liveness-container
set FLASK_PORT=8000
set GRADIO_PORT=7860

REM Solicitar LICENSE_KEY se não estiver definida
if "%LICENSE_KEY%"=="" (
    echo.
    echo 🔑 LICENSE_KEY não encontrada nas variáveis de ambiente
    echo.
    set /p LICENSE_KEY="Digite sua LICENSE_KEY (ou pressione Enter para continuar sem): "
    if "!LICENSE_KEY!"=="" (
        echo ⚠️  Continuando sem LICENSE_KEY - funcionalidade limitada
        set LICENSE_KEY=demo_key
    )
)

echo.
echo 📋 Configuração:
echo    🏷️  Imagem: %IMAGE_NAME%
echo    📦 Container: %CONTAINER_NAME%
echo    🌐 Flask API: http://localhost:%FLASK_PORT%
echo    🎨 Gradio UI: http://localhost:%GRADIO_PORT%
echo    🔑 LICENSE_KEY: %LICENSE_KEY%
echo.

REM Parar container existente se estiver rodando
echo 🛑 Parando containers existentes...
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1

REM Construir imagem Docker
echo.
echo 🔨 Construindo imagem Docker...
echo    Isso pode levar alguns minutos na primeira execução...
echo.

docker build -t %IMAGE_NAME% . --no-cache
if errorlevel 1 (
    echo ❌ ERRO: Falha ao construir imagem Docker
    echo.
    echo 📋 Possíveis soluções:
    echo    1. Verifique se o Dockerfile existe
    echo    2. Verifique conexão com internet
    echo    3. Verifique espaço em disco
    echo    4. Execute: docker system prune -f
    echo.
    pause
    exit /b 1
)

echo ✅ Imagem construída com sucesso

REM Executar container
echo.
echo 🚀 Iniciando container...
echo.

docker run -d ^
    --name %CONTAINER_NAME% ^
    -p %FLASK_PORT%:%FLASK_PORT% ^
    -p %GRADIO_PORT%:%GRADIO_PORT% ^
    -e LICENSE_KEY=%LICENSE_KEY% ^
    -e FLASK_HOST=0.0.0.0 ^
    -e FLASK_PORT=%FLASK_PORT% ^
    -e GRADIO_HOST=0.0.0.0 ^
    -e GRADIO_PORT=%GRADIO_PORT% ^
    -v "%cd%":/workspace ^
    --platform linux/amd64 ^
    %IMAGE_NAME%

if errorlevel 1 (
    echo ❌ ERRO: Falha ao iniciar container
    echo.
    echo 📋 Verificando logs...
    docker logs %CONTAINER_NAME%
    echo.
    pause
    exit /b 1
)

echo ✅ Container iniciado com sucesso

REM Aguardar inicialização dos serviços
echo.
echo ⏳ Aguardando inicialização dos serviços...
timeout /t 10 /nobreak >nul

REM Verificar status dos serviços
echo.
echo 🔍 Verificando status dos serviços...

REM Testar Flask API
curl -s http://localhost:%FLASK_PORT%/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Flask API ainda não está respondendo
) else (
    echo ✅ Flask API: http://localhost:%FLASK_PORT%
)

REM Testar Gradio Interface
curl -s http://localhost:%GRADIO_PORT% >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Gradio Interface ainda não está respondendo
) else (
    echo ✅ Gradio Interface: http://localhost:%GRADIO_PORT%
)

echo.
echo ============================================================================
echo  🎉 Ambiente Docker configurado com sucesso!
echo ============================================================================
echo.
echo 📱 Acesse as interfaces:
echo    🌐 Flask API: http://localhost:%FLASK_PORT%
echo    🎨 Gradio UI: http://localhost:%GRADIO_PORT%
echo.
echo 📋 Comandos úteis:
echo    📊 Ver logs:        docker logs -f %CONTAINER_NAME%
echo    🛑 Parar:          docker stop %CONTAINER_NAME%
echo    🗑️  Remover:        docker rm %CONTAINER_NAME%
echo    🔄 Reiniciar:      docker restart %CONTAINER_NAME%
echo    💻 Acessar shell:  docker exec -it %CONTAINER_NAME% /bin/bash
echo.
echo 🔧 Resolução de problemas:
echo    Se os serviços não estiverem respondendo, aguarde mais alguns segundos
echo    ou verifique os logs com: docker logs %CONTAINER_NAME%
echo.

REM Abrir navegador automaticamente
echo 🌐 Abrindo Gradio Interface no navegador...
start http://localhost:%GRADIO_PORT%

echo.
echo Pressione qualquer tecla para ver os logs em tempo real...
pause >nul

REM Mostrar logs em tempo real
echo.
echo 📊 Logs em tempo real (Ctrl+C para sair):
echo ============================================================================
docker logs -f %CONTAINER_NAME%