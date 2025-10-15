# Face Liveness Detection - Guia de Bootstrap

## Resumo Executivo

Este documento fornece instruções completas para inicializar e executar o projeto Face Liveness Detection localmente usando os scripts de bootstrap automatizados.

## Scripts Disponíveis

### Windows: `bootstrap.bat`
Script automatizado para ambiente Windows que configura o ambiente Python, instala dependências e inicia os serviços.

### Linux/Mac: `bootstrap.sh`
Script automatizado para ambientes Unix que configura o ambiente Python, instala dependências e inicia os serviços.

## Pré-requisitos

### Requisitos Mínimos
- **Python 3.8+** instalado no sistema
- **pip** (gerenciador de pacotes Python)
- **Conexão com internet** para download de dependências
- **8GB RAM** recomendado
- **2GB espaço livre** em disco

### Instalação do Python

#### Windows
1. Baixe Python em: https://www.python.org/downloads/
2. Execute o instalador marcando "Add Python to PATH"
3. Verifique: `python --version`

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

#### macOS
```bash
brew install python3
```

#### CentOS/RHEL
```bash
sudo yum install python3 python3-pip
```

## Configuração da LICENSE_KEY

### Opção 1: Variável de Ambiente
```bash
# Windows
set LICENSE_KEY=sua_chave_aqui

# Linux/Mac
export LICENSE_KEY=sua_chave_aqui
```

### Opção 2: Arquivo license.txt
Crie um arquivo `license.txt` na raiz do projeto com sua chave de licença.

### Opção 3: Obter Licença
Visite https://faceonlive.com para obter uma chave de licença válida.

## Execução

### Windows
```cmd
# Navegue até o diretório do projeto
cd Face-Liveness-Detection

# Execute o script bootstrap
.\bootstrap.bat
```

### Linux/Mac
```bash
# Navegue até o diretório do projeto
cd Face-Liveness-Detection

# Torne o script executável
chmod +x bootstrap.sh

# Execute o script bootstrap
./bootstrap.sh
```

## Serviços Iniciados

Após execução bem-sucedida, os seguintes serviços estarão disponíveis:

### Flask API
- **URL**: http://localhost:8000
- **Endpoints**:
  - `POST /api/liveness` - Upload de imagem via form-data
  - `POST /api/liveness_base64` - Upload de imagem via base64

### Gradio Interface
- **URL**: http://localhost:7860
- **Funcionalidade**: Interface web para teste de detecção de vivacidade facial

## Estrutura do Projeto

```
Face-Liveness-Detection/
├── app.py                 # Servidor Flask principal
├── bootstrap.bat          # Script bootstrap Windows
├── bootstrap.sh           # Script bootstrap Linux/Mac
├── requirements.txt       # Dependências Python
├── venv/                  # Ambiente virtual (criado automaticamente)
├── facewrapper/           # Módulo de detecção facial
├── gradio/               # Interface Gradio
└── docs/                 # Documentação
```

## Troubleshooting

### Erro: Python não encontrado
**Solução**: Instale Python 3.8+ e adicione ao PATH do sistema.

### Erro: pip não encontrado
**Solução**: Reinstale Python com pip incluído ou instale pip separadamente.

### Erro: Falha ao criar ambiente virtual
**Solução**: 
```bash
# Instale python3-venv (Ubuntu/Debian)
sudo apt-get install python3-venv

# Ou use virtualenv
pip install virtualenv
virtualenv venv
```

### Erro: Falha ao instalar dependências
**Soluções**:
1. Atualize pip: `python -m pip install --upgrade pip`
2. Instale setuptools: `pip install setuptools wheel`
3. Verifique conexão com internet
4. Use mirror alternativo: `pip install -r requirements.txt -i https://pypi.org/simple/`

### Erro: FileNotFoundError - libttvfaceengine7.so
**Causa**: Biblioteca nativa não disponível para Windows.
**Solução**: 
1. Use Docker (recomendado para produção)
2. Execute em ambiente Linux
3. Obtenha biblioteca Windows do fornecedor

### Erro: LICENSE_KEY não configurada
**Solução**: Configure a LICENSE_KEY conforme instruções acima ou continue no modo offline.

### Erro: Porta já em uso
**Solução**: 
```bash
# Altere as portas padrão
set PORT=8001
set GRADIO_PORT=7861

# Ou mate processos existentes
taskkill /f /im python.exe  # Windows
pkill -f python             # Linux/Mac
```

## Configurações Avançadas

### Variáveis de Ambiente Opcionais
```bash
PORT=8000                  # Porta do Flask API
GRADIO_PORT=7860          # Porta do Gradio Interface
LICENSE_KEY=sua_chave     # Chave de licença
```

### Modo de Desenvolvimento
Para desenvolvimento, você pode executar os serviços separadamente:

```bash
# Terminal 1 - Flask API
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows
python app.py

# Terminal 2 - Gradio Interface
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows
python gradio/demo.py
```

## Validação da Instalação

### Teste da API Flask
```bash
curl -X POST http://localhost:8000/api/liveness \
  -F "image=@test_image.jpg"
```

### Teste da Interface Gradio
1. Acesse http://localhost:7860
2. Faça upload de uma imagem de teste
3. Verifique o resultado da detecção

## Parada dos Serviços

### Método 1: Ctrl+C
Pressione `Ctrl+C` no terminal onde o bootstrap está executando.

### Método 2: Comando Manual
```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f "python.*app.py"
pkill -f "python.*demo.py"
```

## Suporte e Contato

- **Documentação**: ./docs/
- **Issues**: Verifique logs de erro no terminal
- **Suporte**: https://faceonlive.com
- **Logs**: Verifique saída do terminal para detalhes de erro

## Notas de Segurança

1. **Não commite** chaves de licença no repositório
2. **Use variáveis de ambiente** para credenciais sensíveis
3. **Mantenha dependências atualizadas** para segurança
4. **Execute em ambiente isolado** (venv) sempre

---

**Última atualização**: 15/10/2025
**Versão**: 1.0