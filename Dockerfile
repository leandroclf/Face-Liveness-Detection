# Face Liveness Detection - Dockerfile Otimizado
# Resolve problemas de bibliotecas nativas e compatibilidade cross-platform

FROM ubuntu:22.04

# Configurar timezone e variáveis de ambiente
ENV CONTAINER_TIMEZONE=America/Sao_Paulo
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Configurar timezone
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && \
    echo $CONTAINER_TIMEZONE > /etc/timezone

# Instalar dependências do sistema
RUN apt-get update -y && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-opencv \
        python3-dev \
        python3-venv \
        libcurl4-openssl-dev \
        libssl-dev \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libgcc-s1 \
        libc6 \
        wget \
        curl \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências primeiro (para cache do Docker)
COPY requirements.txt ./

# Atualizar pip e instalar dependências Python
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install -r requirements.txt

# Copiar código da aplicação
COPY ./facewrapper ./facewrapper
COPY ./gradio ./gradio
COPY ./openvino ./openvino
COPY ./app.py ./
COPY ./run.sh ./

# Configurar bibliotecas nativas
# Copiar biblioteca específica do Ubuntu 22.04
RUN cp ./facewrapper/libs/libimutils.so_for_ubuntu22 /usr/lib/libimutils.so && \
    ldconfig

# Copiar bibliotecas OpenVINO para local padrão
RUN cp -r ./openvino/* /usr/lib/ && \
    ldconfig

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser

# Configurar permissões
RUN chmod +x run.sh && \
    chmod -R 755 /app && \
    chown -R appuser:appuser /app

USER appuser

# Expor portas para Flask API e Gradio Interface
EXPOSE 8000 7860

# Variáveis de ambiente para configuração
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8000
ENV GRADIO_HOST=0.0.0.0
ENV GRADIO_PORT=7860
ENV LICENSE_KEY=""

# Comando de inicialização
CMD ["/bin/bash", "-c", "echo '=== Face Liveness Detection - Iniciando Serviços ===' && echo 'Flask API: http://0.0.0.0:8000' && echo 'Gradio Interface: http://0.0.0.0:7860' && echo 'LICENSE_KEY configurada: Sim' && echo '==================================================' && python3 app.py & FLASK_PID=$! && sleep 3 && echo '✅ Flask API iniciada' && python3 gradio/demo.py & GRADIO_PID=$! && sleep 3 && echo '✅ Gradio Interface iniciada' && echo '🚀 Serviços iniciados com sucesso!' && wait"]