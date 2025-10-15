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

- **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
- **4GB RAM** mínimo
- **10GB espaço em disco** para imagens Docker
- **LICENSE_KEY** (opcional - para funcionalidade completa)

## 🔧 Configuração

### Variáveis de Ambiente

```bash
LICENSE_KEY=sua_chave_de_licenca    # Obtenha em https://faceonlive.com
FLASK_PORT=8000                     # Porta da API Flask
GRADIO_PORT=7860                    # Porta da Interface Gradio
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

---

**Desenvolvido com ❤️ usando Docker para máxima compatibilidade e portabilidade.**