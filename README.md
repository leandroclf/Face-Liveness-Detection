# Face Liveness Detection SDK - Solução Docker Completa

## 🐳 Ambiente Docker Otimizado

Esta solução Docker resolve todos os problemas de compatibilidade e bibliotecas nativas, fornecendo um ambiente completo e portável para detecção de vivacidade facial.

### ✅ Problemas Resolvidos

- **✅ Interface Gradio**: Totalmente funcional
- **✅ API Flask**: Disponível com bibliotecas nativas
- **✅ Biblioteca libttvfaceengine7.so**: Incluída no container Linux
- **✅ Compatibilidade**: Funciona em Windows, Linux e macOS

## 🚀 Execução Rápida

### Windows
```bash
.\bootstrap-docker.bat
```

### Linux/Mac
```bash
chmod +x bootstrap-docker.sh
./bootstrap-docker.sh
```

### Docker Compose
```bash
# Definir LICENSE_KEY (opcional)
export LICENSE_KEY="sua_chave_aqui"

# Executar com Docker Compose
docker-compose up --build
```

## 📋 Pré-requisitos

- **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux) para execução containerizada
- **Python 3.8+**, `pip` e `venv` para execução local
- **Git LFS** e **huggingface_hub** (`pip install huggingface_hub`) para baixar modelos proprietários
- **10GB** de espaço livre em disco (modelos + bibliotecas nativas)
- **LICENSE_KEY** fornecida pela FaceOnLive (obrigatória para produção)

### 🔄 Sincronização de modelos e bibliotecas (execução local)

1. Autentique-se na Hugging Face:
   ```bash
   huggingface-cli login  # informe o token com acesso à organização FaceOnLive
   ```
2. Baixe o pacote de modelos (`≈1.5 GB`):
   ```bash
HF_HUB_ENABLE_XET=0 python - <<'PY'
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="FaceOnLive/IDL-Models",
    filename="model.tar.gz",
    repo_type="dataset",
    local_dir="FaceOnLiveModels"
)
PY
tar -xf FaceOnLiveModels/model.tar.gz -C FaceOnLiveModels
```
   O pacote entrega modelos auxiliares (`spoof`, `detection`, `quality_checker`, etc.). Copie os diretórios que desejar utilizar para o pipeline complementar.
3. Extraia as bibliotecas nativas e OpenVINO do espaço oficial:
   ```bash
   HF_HUB_ENABLE_XET=0 python - <<'PY'
   from huggingface_hub import hf_hub_download
   files = [
       "facewrapper/libs/libttvfaceengine7.so",
       "facewrapper/libs/libimutils.so",
       "facewrapper/dict/data1.bin",
       "facewrapper/dict/data2.bin",
       "facewrapper/dict/data3.bin",
       "facewrapper/dict/detect.bin",
   ]
   openvino_libs = [
       "openvino/libopenvino.so",
       "openvino/libopenvino_c.so",
       "openvino/libopenvino_auto_plugin.so",
       "openvino/libopenvino_auto_batch_plugin.so",
       "openvino/libopenvino_gapi_preproc.so",
       "openvino/libopenvino_intel_cpu_plugin.so",
       "openvino/libopenvino_intel_gna_plugin.so",
       "openvino/libopenvino_intel_hddl_plugin.so",
       "openvino/libopenvino_intel_myriad_plugin.so",
       "openvino/libopenvino_ir_frontend.so",
       "openvino/libopenvino_onnx_frontend.so",
       "openvino/libopenvino_paddle_frontend.so",
       "openvino/libopenvino_tensorflow_fe.so",
       "openvino/libgna.so",
       "openvino/libgna.so.2",
       "openvino/libgna.so.3.0.0.1455",
       "openvino/cache.json",
       "openvino/pcie-ma2x8x.mvcmd",
       "openvino/usb-ma2x8x.mvcmd",
   ]
   for path in files + openvino_libs:
       hf_hub_download(
           repo_id="FaceOnLive/Face-Liveness-Detection-SDK",
           filename=path,
           repo_type="space",
           local_dir="FaceOnLiveSpace"
       )
   PY
   cp FaceOnLiveSpace/facewrapper/libs/* facewrapper/libs/
   cp FaceOnLiveSpace/facewrapper/dict/* facewrapper/dict/
   cp FaceOnLiveSpace/openvino/* openvino/
   cp FaceOnLiveSpace/openvino/vpu_custom_kernels/* openvino/vpu_custom_kernels/
   ```
4. Instale dependências TBB (essa versão exige a libc++ antiga):
   ```bash
   apt download libtbb12                                  # Ubuntu 24.04+
   dpkg-deb -x libtbb12_* libtbb_extracted
   cp libtbb_extracted/usr/lib/x86_64-linux-gnu/libtbb*.so* openvino/

   wget https://github.com/oneapi-src/oneTBB/releases/download/v2020.3/tbb-2020.3-lin.tgz
   tar -xzf tbb-2020.3-lin.tgz
   cp tbb/lib/intel64/gcc4.8/libtbb*.so* openvino/
   cp tbb/lib/intel64/gcc4.8/libtbbmalloc*.so* openvino/
   cp tbb/lib/intel64/gcc4.8/libtbbmalloc_proxy*.so* openvino/
   ```
5. Instale OpenSSL 1.1 para compatibilidade:
   ```bash
   wget https://old-releases.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1-1ubuntu2.2_amd64.deb
   dpkg-deb -x libssl1.1_1.1.1-1ubuntu2.2_amd64.deb libssl_extracted
   cp libssl_extracted/usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 openvino/
   cp libssl_extracted/usr/lib/x86_64-linux-gnu/libssl.so.1.1 openvino/
   ```
6. Exporte o `LD_LIBRARY_PATH` antes de qualquer execução local:
   ```bash
   export LD_LIBRARY_PATH="$(pwd)/openvino:$(pwd)/facewrapper/libs:${LD_LIBRARY_PATH}"
   ```
7. Crie e ative o ambiente virtual, depois instale as dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
8. Valide a instalação:
   ```bash
   source venv/bin/activate
   python verify_prerequisites.py
   ```
9. Para obter o HWID e solicitar licença, execute:
   ```bash
   source venv/bin/activate
   LICENSE_KEY=placeholder \
   LD_LIBRARY_PATH="$(pwd)/openvino:$(pwd)/facewrapper/libs:${LD_LIBRARY_PATH}" \
   python app.py
   ```
   O log exibirá `HWID: ...`, que deve ser encaminhado à FaceOnLive para emissão da licença definitiva.

## 🔧 Configuração

### Variáveis de Ambiente

```bash
LICENSE_KEY=sua_chave_de_licenca    # Obtenha em https://faceonlive.com
FLASK_PORT=8000                     # Porta da API Flask
GRADIO_PORT=7860                    # Porta da Interface Gradio
LD_LIBRARY_PATH=/caminho/para/openvino:/caminho/para/facewrapper/libs:$LD_LIBRARY_PATH
```

### Portas Expostas

- **8000**: API Flask (endpoints REST)
- **7860**: Interface Gradio (interface web)

## 📱 Interfaces Disponíveis

### 🌐 API Flask
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Endpoint Principal**: http://localhost:8000/api/liveness

### 🎨 Interface Gradio
- **URL**: http://localhost:7860
- **Funcionalidade**: Upload e análise de imagens
- **Integração**: Conecta automaticamente com a API Flask

## 🛠️ Comandos Úteis

### Gerenciamento de Containers
```bash
# Ver logs em tempo real
docker logs -f face-liveness-container

# Parar container
docker stop face-liveness-container

# Remover container
docker rm face-liveness-container

# Reiniciar container
docker restart face-liveness-container

# Acessar shell do container
docker exec -it face-liveness-container /bin/bash
```

### Limpeza do Sistema
```bash
# Remover imagens não utilizadas
docker system prune -f

# Remover tudo relacionado ao projeto
docker-compose down --rmi all --volumes
```

## 🔍 Resolução de Problemas

### Docker não está instalado
```bash
# Windows: Baixe Docker Desktop
https://www.docker.com/products/docker-desktop

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install docker.io

# CentOS/RHEL
sudo yum install docker

# macOS
brew install docker
```

### Serviços não respondem
1. Aguarde 1-2 minutos para inicialização completa
2. Verifique logs: `docker logs face-liveness-container`
3. Verifique portas: `docker port face-liveness-container`

### Erro de memória
```bash
# Aumentar memória do Docker Desktop (Windows/Mac)
# Configurações > Resources > Memory > 4GB+
```

### Erro de plataforma
```bash
# Forçar plataforma Linux (necessário para bibliotecas nativas)
docker run --platform linux/amd64 ...
```

## 📊 Monitoramento

### Health Checks
```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Verificar interface Gradio
curl http://localhost:7860
```

### Logs Estruturados
```bash
# Logs da API Flask
docker logs face-liveness-container | grep "Flask"

# Logs da Interface Gradio
docker logs face-liveness-container | grep "Gradio"
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────┐
│           Docker Container              │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Flask API   │  │ Gradio Interface│   │
│  │ Port: 8000  │  │ Port: 7860      │   │
│  └─────────────┘  └─────────────────┘   │
│  ┌─────────────────────────────────────┐ │
│  │     Bibliotecas Nativas             │ │
│  │ • libttvfaceengine7.so              │ │
│  │ • OpenVINO                          │ │
│  │ • OpenCV                            │ │
│  │ • TensorFlow                        │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 📄 Licença

MIT License - Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

- **Documentação**: https://faceonlive.com/docs
- **Licenças**: https://faceonlive.com
- **Issues**: Abra uma issue neste repositório

### 📞 Solicitação de licença

1. Execute o aplicativo com uma `LICENSE_KEY` provisória (`LICENSE_KEY=fake LD_LIBRARY_PATH=... python app.py`).
2. Copie o HWID registrado no log (ex.: `HWID: b+0gnDts...`).
3. Encaminhe o HWID para o suporte FaceOnLive (contact@faceonlive.com ou canais oficiais).
4. Salve a chave fornecida em `license.txt` ou exporte `LICENSE_KEY` antes das execuções subsequentes.

---

**Desenvolvido com ❤️ usando Docker para máxima compatibilidade e portabilidade.**
