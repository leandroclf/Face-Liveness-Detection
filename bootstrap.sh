#!/bin/bash

set -e

echo "========================================"
echo "  Face Liveness Detection Bootstrap"
echo "========================================"
echo

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se Python está instalado
echo "[1/6] Verificando instalação do Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 não encontrado. Por favor, instale Python 3.8+ antes de continuar."
    echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "macOS: brew install python3"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
log_info "Python $PYTHON_VERSION encontrado!"
echo

# Verificar se pip está disponível
echo "[2/6] Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 não encontrado. Por favor, instale pip3."
    echo "Ubuntu/Debian: sudo apt-get install python3-pip"
    echo "macOS: python3 -m ensurepip --upgrade"
    exit 1
fi
log_info "pip3 disponível!"
echo

# Criar ambiente virtual se não existir
echo "[3/6] Configurando ambiente virtual..."
if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        log_error "Falha ao criar ambiente virtual."
        exit 1
    fi
    log_info "Ambiente virtual criado com sucesso!"
else
    log_info "Ambiente virtual já existe."
fi
echo

# Ativar ambiente virtual
echo "[4/6] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    log_error "Falha ao ativar ambiente virtual."
    exit 1
fi
log_info "Ambiente virtual ativado!"
echo

# Instalar dependências
echo "[5/6] Instalando dependências..."
log_info "Atualizando pip..."
python -m pip install --upgrade pip

log_info "Instalando pacotes do requirements.txt..."
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    log_error "Falha ao instalar dependências."
    log_error "Verifique se o arquivo requirements.txt existe e está correto."
    exit 1
fi
log_info "Dependências instaladas com sucesso!"
echo

# Verificar LICENSE_KEY
echo "[6/6] Verificando configuração..."
if [ -z "$LICENSE_KEY" ]; then
    echo
    echo "=========================================="
    echo "   ATENÇÃO: LICENSE_KEY NÃO CONFIGURADA"
    echo "=========================================="
    echo
    echo "Para usar este projeto, você precisa configurar a LICENSE_KEY."
    echo
    echo "Opções:"
    echo "1. Definir variável de ambiente: export LICENSE_KEY=sua_chave_aqui"
    echo "2. Criar arquivo license.txt na raiz do projeto"
    echo "3. Obter uma chave em: https://faceonlive.com"
    echo
    echo "O projeto tentará usar o modo offline se disponível."
    echo
    read -p "Deseja continuar mesmo assim? (s/n): " continue
    if [[ $continue != "s" && $continue != "S" ]]; then
        echo "Execução cancelada."
        exit 1
    fi
else
    log_info "LICENSE_KEY configurada: ${LICENSE_KEY:0:10}..."
fi
echo

# Configurar portas padrão se não definidas
export PORT=${PORT:-8000}
export GRADIO_PORT=${GRADIO_PORT:-7860}

echo "========================================"
echo "   INICIANDO SERVIÇOS"
echo "========================================"
echo
echo "Flask API será executada em: http://localhost:$PORT"
echo "Gradio Interface será executada em: http://localhost:$GRADIO_PORT"
echo
echo "Pressione Ctrl+C para parar os serviços."
echo

# Criar arquivo temporário para controlar processos
touch .bootstrap_running

# Função para cleanup
cleanup() {
    echo
    echo "Parando serviços..."
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "python.*demo.py" 2>/dev/null || true
    rm -f .bootstrap_running
    echo "Bootstrap finalizado."
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

# Iniciar Flask API em background
log_info "Iniciando Flask API..."
python app.py &
FLASK_PID=$!

# Aguardar um pouco para Flask inicializar
sleep 3

# Verificar se Flask está rodando
if ! kill -0 $FLASK_PID 2>/dev/null; then
    log_error "Falha ao iniciar Flask API."
    cleanup
fi

# Iniciar Gradio Interface
log_info "Iniciando Gradio Interface..."
python gradio/demo.py

# Se chegou aqui, Gradio foi interrompido
cleanup
