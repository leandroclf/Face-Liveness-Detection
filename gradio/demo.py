import gradio as gr
import requests
import json
import os

def face_liveness(frame):
    """
    Função de detecção de vivacidade facial
    Conecta com a API Flask local ou externa
    """
    # Configurar URL da API baseada em variáveis de ambiente
    api_host = os.getenv('FLASK_HOST', '127.0.0.1')
    api_port = os.getenv('FLASK_PORT', '8000')
    url = f"http://{api_host}:{api_port}/api/liveness"
    
    if frame is None:
        return {
            "status": "error",
            "message": "Nenhuma imagem fornecida"
        }

    try:
        files = {'image': open(frame, 'rb')}
        response = requests.post(url=url, files=files, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"Erro na API: {response.status_code}",
                "details": response.text
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Não foi possível conectar com a API Flask",
            "api_url": url,
            "solution": "Verifique se a API Flask está rodando na porta correta"
        }
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Timeout na conexão com a API",
            "api_url": url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro inesperado: {str(e)}",
            "api_url": url
        }

css = """
.example-image img{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    object-fit: contain;
}
.example-image{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 350px;
    object-fit: contain;
}
.status-info {
    background-color: #e3f2fd;
    border: 1px solid #2196f3;
    border-radius: 5px;
    padding: 15px;
    margin: 10px 0;
    color: #1565c0;
}
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown(
        """
    # Face Liveness Detection - Versão Docker
    
    **🐳 Ambiente Docker Completo**
    
    Esta versão resolve todos os problemas de compatibilidade e bibliotecas nativas:
    
    **✅ Funcionalidades Disponíveis:**
    - Interface Gradio totalmente funcional
    - API Flask com bibliotecas nativas (libttvfaceengine7.so)
    - Detecção de vivacidade facial completa
    - Compatibilidade cross-platform
    
    **🔧 Configuração:**
    - Flask API: Porta 8000
    - Gradio Interface: Porta 7860
    - Ambiente: Ubuntu 22.04 LTS
    - Bibliotecas: OpenVINO, OpenCV, TensorFlow
    """
    )
    
    # Informações de status
    api_host = os.getenv('FLASK_HOST', '127.0.0.1')
    api_port = os.getenv('FLASK_PORT', '8000')
    license_key = os.getenv('LICENSE_KEY', '')
    
    gr.Markdown(
        f"""
    <div class="status-info">
    <strong>Status da Configuração:</strong><br/>
    📡 API Flask: http://{api_host}:{api_port}<br/>
    🔑 LICENSE_KEY: {'✅ Configurada' if license_key else '❌ Não configurada'}<br/>
    🌐 Gradio Interface: Porta {os.getenv('GRADIO_PORT', '7860')}
    </div>
    """
    )
    
    with gr.Row():
        with gr.Column(scale=5):
            image_input = gr.Image(type='filepath', elem_classes="example-image")
            gr.Examples(['gradio/examples/1.jpg', 'gradio/examples/2.jpg', 'gradio/examples/3.jpg', 'gradio/examples/4.jpg'], 
                            inputs=image_input)
            face_liveness_button = gr.Button("🔍 Detectar Vivacidade Facial", variant="primary")
        with gr.Column(scale=5):
            liveness_result_output = gr.JSON()
    
    gr.Markdown(
        """
    ### 📋 Instruções de Uso
    
    1. **Faça upload de uma imagem** com rosto humano
    2. **Clique em "Detectar Vivacidade Facial"** para análise
    3. **Visualize o resultado** no painel JSON à direita
    
    ### 🔧 Informações Técnicas
    
    **Algoritmos Utilizados:**
    - Detecção facial com OpenCV
    - Análise de vivacidade com TensorFlow
    - Processamento com OpenVINO
    
    **Formatos Suportados:**
    - Imagens: JPG, PNG, BMP, TIFF
    - Resolução mínima: 640x480
    - Tamanho máximo: 10MB
    
    **Contato:** https://faceonlive.com para suporte e licenças
    """
    )
    
    face_liveness_button.click(face_liveness, inputs=image_input, outputs=liveness_result_output, api_name=False)

    gr.HTML('<a href="https://visitorbadge.io/status?path=https%3A%2F%2Fhuggingface.co%2Fspaces%2FFaceOnLive%2FFace-Liveness-Detection-SDK"><img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fhuggingface.co%2Fspaces%2FFaceOnLive%2FFace-Liveness-Detection-SDK&labelColor=%23ff8a65&countColor=%2337d67a&style=flat&labelStyle=upper" /></a>')

if __name__ == "__main__":
    # Configurar porta baseada em variável de ambiente
    gradio_port = int(os.getenv('GRADIO_PORT', '7860'))
    gradio_host = os.getenv('GRADIO_HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando Gradio Interface em {gradio_host}:{gradio_port}")
    demo.queue(api_open=False).launch(
        server_name=gradio_host, 
        server_port=gradio_port, 
        show_api=False,
        share=False
    )