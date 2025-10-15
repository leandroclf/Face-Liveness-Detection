# Mapa de Funcionalidades do Projeto

## Visão Geral Funcional
- Plataforma de detecção de vivacidade facial que expõe uma API Flask robusta e uma interface Gradio para experimentação.
- Resolve o problema de validar se um rosto capturado em imagem é genuíno, delegando a inferência ao motor nativo `libttvfaceengine7.so` e às dependências OpenVINO.
- Componentes centrais: `facewrapper` (integração com engine nativa), `app.py` (API Flask e fluxo de inicialização), `gradio/demo.py` (UI cliente), scripts de bootstrap/infra (`bootstrap*.sh|bat`, `run.sh`, `Dockerfile`, `docker-compose.yml`) e utilitários de verificação (`verify_prerequisites.py`).

## Funcionalidades Principais

### 1. Inicialização e validação do motor nativo
- **Localização:** `facewrapper/facewrapper.py` (`FaceEngineValidator`, configuração das funções `ttv_*`)
- **Descrição:** Garante que a biblioteca `libttvfaceengine7.so`, as dependências OpenVINO e o diretório de modelos existam antes de carregar o engine via `ctypes`. Após a validação, registra assinaturas das funções expostas pelo SDK (`ttv_version`, `ttv_get_hwid`, `ttv_init`, `ttv_init_offline`, `ttv_detect_face`), disponibilizando-as para o restante do sistema.
- **Entradas/Saídas:** Entradas indiretas via filesystem (bibliotecas e modelos). Saídas sob a forma de objetos `ctypes` prontos para uso e exceções `FaceEngineError` em caso de falha.
- **Dependências:** `libttvfaceengine7.so`, diretório `facewrapper/dict`, pacote OpenVINO (arquivos sob `openvino/`), NumPy para buffers C-contíguos.
- **Observações técnicas:** Falha em qualquer validação aborta o carregamento; não existe modo mock. O módulo imprime logs explicativos durante o bootstrap.

### 2. Orquestração de licença e ativação do SDK
- **Localização:** `app.py` (`LicenseValidator`, bloco de inicialização global)
- **Descrição:** Valida a chave de licença via variável de ambiente `LICENSE_KEY` ou arquivo `license.txt`, checa diretório de modelos e invoca `ttv_init`. Em caso de erro, coleta o HWID via `ttv_get_hwid` e tenta ativação offline com `ttv_init_offline`, encerrando a aplicação se nenhum modo funcionar.
- **Entradas/Saídas:** Entradas: variável de ambiente `LICENSE_KEY`, arquivo `license.txt`, diretório `facewrapper/dict`. Saídas: inicialização do engine em memória ou encerramento (`sys.exit(1)`), com logs detalhados de status.
- **Dependências:** Funções `ttv_version`, `ttv_init`, `ttv_get_hwid`, `ttv_init_offline` providas por `facewrapper`; módulo `os` para IO.
- **Observações técnicas:** Implementa validações rígidas (ex.: bloqueia placeholders) e emite mensagens de troubleshooting orientando passos corretivos.

### 3. Monitoramento de saúde da API
- **Localização:** `app.py:140` (`health_check`)
- **Descrição:** Endpoint GET `/health` que reporta estado da API, versão do engine, modo de operação e requisitos mínimos para uso, servindo também ao healthcheck do Docker.
- **Entradas/Saídas:** Entrada: requisições HTTP GET. Saída: JSON com status, versão, endpoints disponíveis, timestamp e pré-requisitos.
- **Dependências:** Flask (`jsonify`), variável `version` carregada durante a inicialização.
- **Observações técnicas:** Retorna HTTP 200 independentemente de métricas de uso; assume que o bootstrap inicial foi bem-sucedido.

### 4. Detecção de vivacidade via upload multipart
- **Localização:** `app.py:163` (`check_liveness`)
- **Descrição:** Endpoint POST `/api/liveness` que consome imagens enviadas em formulário multipart (`image`), decodifica com OpenCV, aloca buffers NumPy para retângulo facial, pontuação e ângulos e invoca `ttv_detect_face`. Traduz códigos de retorno em mensagens de domínio (face ausente, múltiplas faces, spoof, etc.).
- **Entradas/Saídas:** Entrada: arquivo binário de imagem. Saída: JSON contendo status, classificação (`genuine`, `spoof`, mensagens de erro), bounding box e valores de yaw/roll/pitch e score numérico.
- **Dependências:** `ttv_detect_face`, OpenCV (`cv2.imdecode`), NumPy para buffers, Flask `request`.
- **Observações técnicas:** Threshold fixo de 0,5 para score de vivacidade; usa `np.fromstring`, deprecado para bytes sem especificar `np.frombuffer`. Falhas retornam respostas 200 com mensagens no payload em vez de códigos de erro específicos.

### 5. Detecção de vivacidade via payload base64
- **Localização:** `app.py:195` (`check_liveness_base64`)
- **Descrição:** Endpoint POST `/api/liveness_base64` que aceita JSON com a chave `image`, decodifica a string base64 e reaproveita o mesmo fluxo de inferência e interpretação de resultados do endpoint multipart.
- **Entradas/Saídas:** Entrada: JSON `{ "image": "<base64>" }`. Saída: JSON idêntico ao endpoint multipart.
- **Dependências:** `base64.b64decode`, NumPy, `ttv_detect_face`, Flask `request`.
- **Observações técnicas:** Duplica a lógica do endpoint multipart, o que pode ser fator para refatoração; não valida existência da chave `image` antes de usar.

### 6. Interface operadora Gradio
- **Localização:** `gradio/demo.py` (`face_liveness`, bloco `gr.Blocks`)
- **Descrição:** Fornece UI web para envio de imagens e consumo da API Flask. Configura layout com previews, exemplos de imagens e instruções técnicas. A função `face_liveness` envia a imagem selecionada para `/api/liveness`, trata erros de conexão/timeout e exibe o JSON retornado.
- **Entradas/Saídas:** Entrada: caminho de arquivo gerado pelo componente `gr.Image`. Saída: dicionário JSON exibido no componente `gr.JSON`.
- **Dependências:** Pacotes `gradio`, `requests`, variáveis de ambiente `FLASK_HOST`, `FLASK_PORT`, `GRADIO_HOST`, `GRADIO_PORT`.
- **Observações técnicas:** Executa `demo.queue(...).launch(...)` sem expor a API do Gradio; interface assume que a API Flask já está ativa e autenticada.

## Funcionalidades Secundárias e Suporte

### S1. Verificação automatizada de pré-requisitos
- **Localização:** `verify_prerequisites.py` (`PrerequisiteChecker`)
- **Descrição:** Script CLI que percorre verificações de biblioteca nativa, OpenVINO, modelos, licença, pacotes Python e compatibilidade do sistema, emitindo relatório agregado de sucessos, avisos e erros críticos.
- **Entradas/Saídas:** Entradas: estado do filesystem, variáveis de ambiente, pacotes instalados. Saída: logs no stdout e código de saída `0/1` conforme sucesso.
- **Dependências:** `pathlib`, `os`, `sys`, módulos padrão; acesso aos diretórios `facewrapper/libs`, `facewrapper/dict`, `openvino`.
- **Observações técnicas:** Usa heurística de tamanho para validar integridade da biblioteca nativa e lista arquivos de modelo quando presentes.

### S2. Bootstrap local interativo (Unix/Windows)
- **Localização:** `bootstrap.sh`, `bootstrap.bat`
- **Descrição:** Automatiza criação de ambiente virtual, instalação de dependências, verificação de `LICENSE_KEY` e inicialização simultânea da API Flask e do Gradio em ambiente local, com logs coloridos e rotinas de cleanup.
- **Entradas/Saídas:** Entradas: comandos do usuário (confirmação), variáveis `PORT`, `GRADIO_PORT`, `LICENSE_KEY`. Saída: processos em execução (`app.py`, `gradio/demo.py`) e logs no terminal.
- **Dependências:** Python 3, `pip`, arquivo `requirements.txt`, scripts do projeto.
- **Observações técnicas:** Assegura ativação do ambiente virtual (`venv`) e, no Windows, espera interações via prompt; encerra serviços ao receber `Ctrl+C`.

### S3. Provisionamento Docker multiplataforma
- **Localização:** `bootstrap-docker.sh`, `bootstrap-docker.bat`
- **Descrição:** Realiza verificação do Docker, coleta ou solicita `LICENSE_KEY`, recompila a imagem local `face-liveness-detection` (sem cache) e sobe container com portas mapeadas e variáveis apropriadas, além de validar disponibilidade dos serviços.
- **Entradas/Saídas:** Entradas: instalação do Docker, porta livre, variáveis de ambiente. Saídas: container `face-liveness-container` rodando, logs no console, abertura opcional do navegador na UI Gradio.
- **Dependências:** Docker CLI, `docker-compose` não é exigido (rodando via `docker run`), scripts `Dockerfile`, diretório do projeto para bind mount.
- **Observações técnicas:** Força `--platform linux/amd64`, útil para hosts ARM; coleta logs com `docker logs -f` ao final.

### S4. Orquestração de runtime em contêiner
- **Localização:** `Dockerfile`, `docker-compose.yml`, `run.sh`
- **Descrição:** Define imagem base Ubuntu 22.04 com dependências Python e bibliotecas gráficas, copia o código e modelos, publica porta dupla (Flask/Gradio) e configura execução simultânea dos serviços via `run.sh`. O `docker-compose.yml` adiciona healthcheck, bind mounts e restart policy.
- **Entradas/Saídas:** Entradas: build context do projeto, variáveis de ambiente `LICENSE_KEY`, `FLASK_*`, `GRADIO_*`, `TZ`. Saídas: imagem Docker funcional e, em runtime, processos Flask/Gradio gerenciados pelo script.
- **Dependências:** Sistema apt com acesso a pacotes, diretórios `facewrapper`, `openvino`, `gradio`, `requirements.txt`, biblioteca `libimutils.so_for_ubuntu22`.
- **Observações técnicas:** `run.sh` garante que `/usr/lib/libimutils.so` exista copiando um stub incluso; healthcheck do compose consulta `/health` a cada 30s.

### S5. Recursos de engine e kernels OpenVINO
- **Localização:** `openvino/` (plugins e kernels `.cl`), `facewrapper/libs/libimutils.so_for_ubuntu22`
- **Descrição:** Conjunto de plugins OpenVINO (`plugins.xml`) e kernels personalizados necessários para acelerar o motor de vivacidade, além de biblioteca auxiliar `libimutils` usada em ambientes Ubuntu. São consumidos de forma indireta pelos scripts de inicialização (Dockerfile e `run.sh`).
- **Entradas/Saídas:** Entradas: engine nativo ao carregar bibliotecas. Saída: suporte ao runtime do SDK durante a inferência.
- **Dependências:** Ambiente OpenVINO 2022, GPU/VPU compatíveis (plugins AUTO, CPU, GPU, VPUX, etc.).
- **Observações técnicas:** Scripts orientam executar `git lfs pull` para garantir download completo das dependências (quando armazenadas via LFS).

## Fluxos de Integração
- **Motor nativo TTV FaceEngine:** `facewrapper/facewrapper.py` carrega `libttvfaceengine7.so` e expõe ponteiros `ttv_*` utilizados pelos endpoints Flask.
- **Licenciamento e ativação:** `LicenseValidator` procura chaves em variáveis ou arquivo, aciona `ttv_init`/`ttv_init_offline` e, em caso de falha, obtém HWID para suporte.
- **Clientes HTTP:** Endpoints em `app.py` consomem uploads/base64, traduzem resultados do engine e devolvem JSON; a UI `gradio/demo.py` atua como cliente padrão, mas qualquer consumidor HTTP pode reutilizar os contratos expostos.
- **Infraestrutura de contêiner:** Bootstrap Docker e `run.sh` encapsulam configuração do sistema operacional, cópia de bibliotecas auxiliares e publicação das portas 8000/7860 para acesso externo.

## Comportamentos Específicos
- Inicialização aborta imediatamente se qualquer pré-requisito falhar (biblioteca, modelos, licença), evitando operar em modo degradado.
- Fluxo de ativação tenta modo online e fallback offline com o mesmo diretório de modelos e arquivo de licença.
- Códigos de retorno do engine são traduzidos em mensagens textuais fixas; nenhum HTTP error code diferenciado é enviado.
- Scripts de bootstrap implementam rotinas de limpeza (`trap`/`taskkill`) para impedir processos órfãos.
- `run.sh` e Dockerfile copiam automaticamente `libimutils` caso ausente no sistema, garantindo compatibilidade com Ubuntu 22.04.

## Resumo Final
- **Quantidade total de funcionalidades identificadas:** 11 (6 principais, 5 de suporte).
- **Distribuição por módulo:** `facewrapper` (1 principal, 1 suporte), `app.py` (4 principais), `gradio` (1 principal), `scripts/bootstrap` (2 de suporte), `infra Docker` (2 de suporte), `openvino/libs` (1 suporte).
- **Potenciais áreas de melhoria:** consolidar lógica duplicada dos endpoints de vivacidade, substituir `np.fromstring` por `np.frombuffer`, padronizar códigos HTTP de erro, parametrizar threshold de score e adicionar tratamento para ausência de campo `image` no payload JSON.
