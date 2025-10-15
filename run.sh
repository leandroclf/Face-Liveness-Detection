#!/bin/bash

# Face Liveness Detection - Script de Inicialização Docker
# Inicia Flask API e Gradio Interface simultaneamente

set -e

echo "=== Face Liveness Detection - Iniciando Serviços ==="
echo "Flask API: http://0.0.0.0:${FLASK_PORT:-8000}"
echo "Gradio Interface: http://0.0.0.0:${GRADIO_PORT:-7860}"
echo "LICENSE_KEY configurada: $([ -n "$LICENSE_KEY" ] && echo "Sim" || echo "Não")"
echo "=================================================="

# Função para cleanup em caso de interrupção
cleanup() {
    echo "Parando serviços..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGTERM SIGINT

# Verificar se a biblioteca nativa está disponível
if [ ! -f "/usr/lib/libimutils.so" ]; then
    echo "AVISO: Biblioteca libimutils.so não encontrada. Copiando..."
    cp ./facewrapper/libs/libimutils.so_for_ubuntu22 /usr/lib/libimutils.so 2>/dev/null || true
    ldconfig 2>/dev/null || true
fi

# Iniciar Flask API em background
echo "Iniciando Flask API na porta ${FLASK_PORT:-8000}..."
python3 app.py &
FLASK_PID=$!

# Aguardar um momento para Flask inicializar
sleep 3

# Verificar se Flask está rodando
if kill -0 $FLASK_PID 2>/dev/null; then
    echo "✅ Flask API iniciada com sucesso (PID: $FLASK_PID)"
else
    echo "❌ Erro ao iniciar Flask API"
fi

# Iniciar Gradio Interface
echo "Iniciando Gradio Interface na porta ${GRADIO_PORT:-7860}..."
python3 gradio/demo.py &
GRADIO_PID=$!

# Aguardar um momento para Gradio inicializar
sleep 3

# Verificar se Gradio está rodando
if kill -0 $GRADIO_PID 2>/dev/null; then
    echo "✅ Gradio Interface iniciada com sucesso (PID: $GRADIO_PID)"
else
    echo "❌ Erro ao iniciar Gradio Interface"
fi

echo "=================================================="
echo "🚀 Serviços iniciados com sucesso!"
echo "📡 Flask API: http://localhost:${FLASK_PORT:-8000}"
echo "🌐 Gradio Interface: http://localhost:${GRADIO_PORT:-7860}"
echo "=================================================="

# Aguardar ambos os processos
wait