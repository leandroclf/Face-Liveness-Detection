#!/bin/bash
# ============================================================================
# Face Liveness Detection - Bootstrap Docker para Linux/Mac
# ============================================================================
# Este script configura e executa o ambiente Docker completo
# Resolve problemas de compatibilidade e bibliotecas nativas
# ============================================================================

set -e

echo ""
echo "============================================================================"
echo "  🐳 Face Liveness Detection - Bootstrap Docker"
echo "============================================================================"
echo "  Configurando ambiente Docker completo..."
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ ERRO: Docker não está instalado"
    echo ""
    echo "📋 Instruções de instalação:"
    echo "   Ubuntu/Debian: sudo apt-get update && sudo apt-get install docker.io"
    echo "   CentOS/RHEL:   sudo yum install docker"
    echo "   macOS:         brew install docker"
    echo "   Ou baixe em:   https://www.docker.com/products/docker-desktop"
    echo ""
    exit 1
fi

echo "✅ Docker detectado: $(docker --version)"

# Verificar se Docker está rodando
if ! docker info &> /dev/null; then
    echo "❌ ERRO: Docker não está rodando"
    echo ""
    echo "📋 Soluções:"
    echo "   Linux: sudo systemctl start docker"
    echo "   macOS: Inicie Docker Desktop"
    echo ""
    exit 1
fi

echo "✅ Docker está rodando"

# Configurar variáveis
IMAGE_NAME="face-liveness-detection"
CONTAINER_NAME="face-liveness-container"
FLASK_PORT=8000
GRADIO_PORT=7860

# Solicitar LICENSE_KEY se não estiver definida
if [ -z "$LICENSE_KEY" ]; then
    echo ""
    echo "🔑 LICENSE_KEY não encontrada nas variáveis de ambiente"
    echo ""
    read -p "Digite sua LICENSE_KEY (ou pressione Enter para continuar sem): " LICENSE_KEY
    if [ -z "$LICENSE_KEY" ]; then
        echo "⚠️  Continuando sem LICENSE_KEY - funcionalidade limitada"
        LICENSE_KEY="demo_key"
    fi
fi

echo ""
echo "📋 Configuração:"
echo "   🏷️  Imagem: $IMAGE_NAME"
echo "   📦 Container: $CONTAINER_NAME"
echo "   🌐 Flask API: http://localhost:$FLASK_PORT"
echo "   🎨 Gradio UI: http://localhost:$GRADIO_PORT"
echo "   🔑 LICENSE_KEY: $LICENSE_KEY"
echo ""

# Parar container existente se estiver rodando
echo "🛑 Parando containers existentes..."
docker stop $CONTAINER_NAME &> /dev/null || true
docker rm $CONTAINER_NAME &> /dev/null || true

# Construir imagem Docker
echo ""
echo "🔨 Construindo imagem Docker..."
echo "   Isso pode levar alguns minutos na primeira execução..."
echo ""

if ! docker build -t $IMAGE_NAME . --no-cache; then
    echo "❌ ERRO: Falha ao construir imagem Docker"
    echo ""
    echo "📋 Possíveis soluções:"
    echo "   1. Verifique se o Dockerfile existe"
    echo "   2. Verifique conexão com internet"
    echo "   3. Verifique espaço em disco"
    echo "   4. Execute: docker system prune -f"
    echo ""
    exit 1
fi

echo "✅ Imagem construída com sucesso"

# Executar container
echo ""
echo "🚀 Iniciando container..."
echo ""

if ! docker run -d \
    --name $CONTAINER_NAME \
    -p $FLASK_PORT:$FLASK_PORT \
    -p $GRADIO_PORT:$GRADIO_PORT \
    -e LICENSE_KEY="$LICENSE_KEY" \
    -e FLASK_HOST=0.0.0.0 \
    -e FLASK_PORT=$FLASK_PORT \
    -e GRADIO_HOST=0.0.0.0 \
    -e GRADIO_PORT=$GRADIO_PORT \
    -v "$(pwd)":/workspace \
    --platform linux/amd64 \
    $IMAGE_NAME; then
    
    echo "❌ ERRO: Falha ao iniciar container"
    echo ""
    echo "📋 Verificando logs..."
    docker logs $CONTAINER_NAME
    echo ""
    exit 1
fi

echo "✅ Container iniciado com sucesso"

# Aguardar inicialização dos serviços
echo ""
echo "⏳ Aguardando inicialização dos serviços..."
sleep 10

# Verificar status dos serviços
echo ""
echo "🔍 Verificando status dos serviços..."

# Testar Flask API
if curl -s http://localhost:$FLASK_PORT/health &> /dev/null; then
    echo "✅ Flask API: http://localhost:$FLASK_PORT"
else
    echo "⚠️  Flask API ainda não está respondendo"
fi

# Testar Gradio Interface
if curl -s http://localhost:$GRADIO_PORT &> /dev/null; then
    echo "✅ Gradio Interface: http://localhost:$GRADIO_PORT"
else
    echo "⚠️  Gradio Interface ainda não está respondendo"
fi

echo ""
echo "============================================================================"
echo "  🎉 Ambiente Docker configurado com sucesso!"
echo "============================================================================"
echo ""
echo "📱 Acesse as interfaces:"
echo "   🌐 Flask API: http://localhost:$FLASK_PORT"
echo "   🎨 Gradio UI: http://localhost:$GRADIO_PORT"
echo ""
echo "📋 Comandos úteis:"
echo "   📊 Ver logs:        docker logs -f $CONTAINER_NAME"
echo "   🛑 Parar:          docker stop $CONTAINER_NAME"
echo "   🗑️  Remover:        docker rm $CONTAINER_NAME"
echo "   🔄 Reiniciar:      docker restart $CONTAINER_NAME"
echo "   💻 Acessar shell:  docker exec -it $CONTAINER_NAME /bin/bash"
echo ""
echo "🔧 Resolução de problemas:"
echo "   Se os serviços não estiverem respondendo, aguarde mais alguns segundos"
echo "   ou verifique os logs com: docker logs $CONTAINER_NAME"
echo ""

# Abrir navegador automaticamente (se disponível)
if command -v xdg-open &> /dev/null; then
    echo "🌐 Abrindo Gradio Interface no navegador..."
    xdg-open http://localhost:$GRADIO_PORT &> /dev/null &
elif command -v open &> /dev/null; then
    echo "🌐 Abrindo Gradio Interface no navegador..."
    open http://localhost:$GRADIO_PORT &> /dev/null &
fi

echo ""
echo "Pressione Ctrl+C para sair dos logs em tempo real..."
echo ""

# Mostrar logs em tempo real
echo "📊 Logs em tempo real:"
echo "============================================================================"
docker logs -f $CONTAINER_NAME