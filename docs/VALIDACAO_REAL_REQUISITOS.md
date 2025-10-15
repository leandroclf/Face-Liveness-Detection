# Requisitos para Validação Real - Face Liveness Detection

## Resumo Executivo

O sistema foi configurado para **validação real obrigatória**, com **modo mock completamente desabilitado**. O sistema agora falha imediatamente se os pré-requisitos não estiverem atendidos, garantindo operação apenas com componentes reais.

## Status Atual

✅ **Modo mock desabilitado**  
✅ **Validação rigorosa implementada**  
✅ **Verificação de pré-requisitos obrigatória**  
✅ **Sistema falha sem biblioteca nativa**  

## Pré-requisitos Obrigatórios

### 1. Biblioteca Nativa
**Arquivo:** `libttvfaceengine7.so`  
**Local:** `facewrapper/libs/libttvfaceengine7.so`  
**Status:** ❌ **AUSENTE - CRÍTICO**

```bash
# Verificar presença
ls -la facewrapper/libs/libttvfaceengine7.so

# Se ausente, obter do fornecedor e colocar no local correto
```

### 2. Licença de Validação
**Configuração:** `LICENSE_KEY` (variável de ambiente) ou `license.txt`  
**Status:** ❌ **NÃO CONFIGURADA**

```bash
# Opção 1: Variável de ambiente
export LICENSE_KEY="sua_chave_de_licenca_aqui"

# Opção 2: Arquivo de licença
echo "sua_chave_de_licenca_aqui" > license.txt
```

### 3. Dependências Python
**Status:** ❌ **PARCIALMENTE AUSENTES**

```bash
# Instalar dependências ausentes
pip install opencv-python pillow

# Verificar instalação
python -c "import cv2, PIL; print('Dependências OK')"
```

### 4. Modelos de IA
**Diretório:** `facewrapper/dict/`  
**Status:** ⚠️ **VAZIO**

```bash
# Criar diretório se não existir
mkdir -p facewrapper/dict

# Adicionar modelos necessários (obter do fornecedor)
```

### 5. Dependências OpenVINO
**Diretório:** `openvino/`  
**Status:** ⚠️ **PARCIALMENTE PRESENTE**

```bash
# Baixar dependências via Git LFS
git lfs pull
```

## Execução e Validação

### Script de Verificação
```bash
# Executar verificação completa
python verify_prerequisites.py
```

### Inicialização do Sistema
```bash
# Tentar inicializar (falhará sem pré-requisitos)
python app.py
```

### Resultado Esperado
- **Com pré-requisitos:** Sistema inicia normalmente
- **Sem pré-requisitos:** Falha imediata com mensagens claras

## Mensagens de Erro Típicas

### Biblioteca Nativa Ausente
```
❌ ERRO CRÍTICO: Biblioteca nativa não encontrada em facewrapper/libs/libttvfaceengine7.so
📋 REQUISITOS OBRIGATÓRIOS:
   1. Baixar libttvfaceengine7.so do fornecedor
   2. Colocar em facewrapper/libs/
   3. Verificar permissões de execução
   4. Validar compatibilidade do sistema operacional
🚫 MODO MOCK DESABILITADO - Sistema não pode funcionar sem biblioteca nativa
```

### Licença Não Configurada
```
❌ ERRO CRÍTICO: LICENSE_KEY não configurada
📋 Configure via:
   1. Variável de ambiente: export LICENSE_KEY="sua_chave"
   2. Arquivo license.txt na raiz do projeto
```

## Endpoints de Diagnóstico

### Health Check
```bash
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "mode": "REAL_VALIDATION",
  "mock_disabled": true,
  "required_components": {
    "native_library": "libttvfaceengine7.so",
    "license_required": true,
    "models_directory": "facewrapper/dict"
  }
}
```

## Compatibilidade do Sistema

### Sistemas Suportados
- **Linux:** ✅ Totalmente suportado
- **Windows:** ⚠️ Limitado (biblioteca .so pode não funcionar)
- **macOS:** ⚠️ Não testado

### Arquiteturas
- **x86_64:** ✅ Suportado
- **ARM:** ❓ Verificar com fornecedor

## Troubleshooting

### Problema: Sistema não inicia
**Solução:** Execute `python verify_prerequisites.py` para diagnóstico completo

### Problema: Biblioteca não carrega
**Verificações:**
1. Arquivo existe em `facewrapper/libs/libttvfaceengine7.so`
2. Permissões de execução (`chmod +x`)
3. Dependências do sistema (ldd no Linux)

### Problema: Licença inválida
**Verificações:**
1. LICENSE_KEY configurada corretamente
2. Conectividade para validação online
3. Arquivo license.txt para modo offline

## Próximos Passos

1. **Obter biblioteca nativa** do fornecedor
2. **Configurar licença válida**
3. **Instalar dependências Python** ausentes
4. **Adicionar modelos** necessários
5. **Testar em ambiente de produção**

## Contato e Suporte

Para obter os componentes ausentes:
- **Biblioteca nativa:** Contatar fornecedor do SDK
- **Licença:** Departamento comercial
- **Modelos:** Documentação técnica do fornecedor

---

**Importante:** O sistema agora opera exclusivamente em modo de validação real. Não há fallback para modo mock.