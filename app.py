import sys
sys.path.append('.')

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_restx import reqparse
from time import gmtime, strftime
import os
import base64
import binascii
import json
import cv2
import numpy as np
from werkzeug.datastructures import FileStorage

# Importações com validação rigorosa
try:
    from facewrapper.facewrapper import ttv_version
    from facewrapper.facewrapper import ttv_get_hwid
    from facewrapper.facewrapper import ttv_init
    from facewrapper.facewrapper import ttv_init_offline
    from facewrapper.facewrapper import ttv_detect_face
    from facewrapper.facewrapper import FaceEngineError
    print("✅ Módulo facewrapper carregado com sucesso")
except Exception as e:
    print(f"❌ ERRO CRÍTICO: Falha ao carregar facewrapper: {e}")
    print("🚫 Sistema não pode funcionar sem biblioteca nativa")
    sys.exit(1)

class LicenseValidator:
    """Validador rigoroso de licença"""
    
    @staticmethod
    def validate_license_key():
        """Valida LICENSE_KEY obrigatória"""
        license_key = os.environ.get("LICENSE_KEY")
        
        if not license_key:
            print("⚠️  LICENSE_KEY não definida como variável de ambiente")
            
            # Tentar arquivo de licença
            license_file = "license.txt"
            if os.path.exists(license_file):
                try:
                    with open(license_file, 'r') as f:
                        license_key = f.read().strip()
                    print(f"✅ LICENSE_KEY carregada do arquivo: {license_file}")
                except Exception as e:
                    raise FaceEngineError(f"❌ Erro ao ler arquivo de licença: {e}")
            else:
                raise FaceEngineError(
                    "❌ ERRO CRÍTICO: Nenhuma configuração de licença encontrada\n"
                    "📋 REQUISITOS OBRIGATÓRIOS:\n"
                    "   1. Definir variável de ambiente LICENSE_KEY, OU\n"
                    "   2. Criar arquivo license.txt com chave válida\n"
                    "🚫 Sistema não pode funcionar sem licença válida"
                )
        
        # Validar formato da licença
        if not license_key or len(license_key) < 10:
            raise FaceEngineError("❌ LICENSE_KEY inválida: muito curta")
            
        if license_key.startswith('your-license-key'):
            raise FaceEngineError("❌ LICENSE_KEY é um placeholder - configure chave real")
            
        return license_key
    
    @staticmethod
    def validate_model_folder():
        """Valida diretório de modelos"""
        model_folder = os.path.abspath(os.path.dirname(__file__)) + '/facewrapper/dict'
        
        if not os.path.exists(model_folder):
            raise FaceEngineError(f"❌ Diretório de modelos não encontrado: {model_folder}")
            
        return model_folder

# Configuração da aplicação Flask
app = Flask(__name__) 
app.config['SITE'] = "http://0.0.0.0:8000/"
app.config['DEBUG'] = False

# Validação rigorosa de pré-requisitos
print("🔍 Iniciando validação rigorosa de pré-requisitos...")

try:
    # Validar licença
    licenseKey = LicenseValidator.validate_license_key()
    print("✅ LICENSE_KEY validada com sucesso")
    
    # Validar diretório de modelos
    modelFolder = LicenseValidator.validate_model_folder()
    print(f"✅ Diretório de modelos validado: {modelFolder}")
    
    # Obter versão da biblioteca
    version = ttv_version()
    print(f"✅ Versão da biblioteca: {version.decode('utf-8')}")
    
    # Inicialização online
    print("🔄 Tentando inicialização online...")
    ret = ttv_init(modelFolder.encode('utf-8'), licenseKey.encode('utf-8'))
    
    if ret != 0:
        print(f"⚠️  Inicialização online falhou (código: {ret})")
        
        # Obter HWID para diagnóstico
        hwid = ttv_get_hwid()
        print(f"📋 HWID do sistema: {hwid.decode('utf-8')}")
        
        # Tentar inicialização offline
        print("🔄 Tentando inicialização offline...")
        licensePath = "license.txt"
        
        if not os.path.exists(licensePath):
            raise FaceEngineError(
                f"❌ Arquivo de licença offline não encontrado: {licensePath}\n"
                f"📋 Para modo offline, criar arquivo license.txt com licença válida"
            )
        
        ret = ttv_init_offline(modelFolder.encode('utf-8'), licensePath.encode('utf-8'))
        
        if ret != 0:
            raise FaceEngineError(
                f"❌ FALHA CRÍTICA: Inicialização offline falhou (código: {ret})\n"
                f"📋 POSSÍVEIS CAUSAS:\n"
                f"   1. LICENSE_KEY inválida ou expirada\n"
                f"   2. HWID não autorizado: {hwid.decode('utf-8')}\n"
                f"   3. Modelos corrompidos ou ausentes\n"
                f"   4. Biblioteca nativa incompatível\n"
                f"🚫 Sistema não pode funcionar sem inicialização válida"
            )
        else:
            print("✅ Inicialização offline bem-sucedida")
    else:
        print("✅ Inicialização online bem-sucedida")
        
    print("🚀 Sistema inicializado com validação real - MODO MOCK DESABILITADO")
    
except Exception as e:
    print(f"❌ FALHA NA INICIALIZAÇÃO: {e}")
    print("🚫 Aplicação não pode continuar")
    sys.exit(1)

LIB_VERSION = version.decode('utf-8') if version else "unknown"

def evaluate_liveness(image: np.ndarray) -> dict:
    """Executa a avaliação de vivacidade usando o motor nativo."""
    face_rect = np.zeros([4], dtype=np.int32)
    liveness_score = np.zeros([1], dtype=np.double)
    angles = np.zeros([3], dtype=np.double)

    ret = ttv_detect_face(
        image,
        image.shape[1],
        image.shape[0],
        face_rect,
        liveness_score,
        angles
    )

    if ret == -1:
        result = "license error!"
    elif ret == -2:
        result = "init error!"
    elif ret == 0:
        result = "no face detected!"
    elif ret > 1:
        result = "multiple face detected!"
    elif (
        face_rect[0] < 0
        or face_rect[1] < 0
        or face_rect[2] >= image.shape[1]
        or face_rect[2] >= image.shape[0]
    ):
        result = "face is in boundary!"
    elif liveness_score[0] > 0.5:
        result = "genuine"
    else:
        result = "spoof"

    return {
        "status": "ok",
        "data": {
            "result": result,
            "face_rect": {
                "x": int(face_rect[0]),
                "y": int(face_rect[1]),
                "w": int(face_rect[2] - face_rect[0] + 1),
                "h": int(face_rect[3] - face_rect[1] + 1)
            },
            "liveness_score": float(liveness_score[0]),
            "angles": {
                "yaw": float(angles[0]),
                "roll": float(angles[1]),
                "pitch": float(angles[2])
            }
        }
    }

# Configuração da documentação e namespaces (Swagger UI em /docs)
api = Api(
    app,
    version="1.0",
    title="Face Liveness Detection API",
    description="API oficial para detecção de vivacidade facial em tempo real",
    doc="/docs"
)

error_model = api.model(
    "ErrorResponse",
    {
        "status": fields.String(example="error"),
        "message": fields.String(description="Descrição do erro")
    }
)

face_rect_model = api.model(
    "FaceRect",
    {
        "x": fields.Integer(description="Coordenada X do retângulo facial"),
        "y": fields.Integer(description="Coordenada Y do retângulo facial"),
        "w": fields.Integer(description="Largura do retângulo facial"),
        "h": fields.Integer(description="Altura do retângulo facial")
    }
)

angles_model = api.model(
    "Angles",
    {
        "yaw": fields.Float(description="Ângulo de yaw"),
        "roll": fields.Float(description="Ângulo de roll"),
        "pitch": fields.Float(description="Ângulo de pitch")
    }
)

liveness_data_model = api.model(
    "LivenessData",
    {
        "result": fields.String(description="Classificação do motor de vivacidade"),
        "face_rect": fields.Nested(face_rect_model),
        "liveness_score": fields.Float(description="Score bruto de vivacidade"),
        "angles": fields.Nested(angles_model)
    }
)

liveness_response_model = api.model(
    "LivenessResponse",
    {
        "status": fields.String(example="ok"),
        "data": fields.Nested(liveness_data_model)
    }
)

base64_request_model = api.model(
    "LivenessBase64Request",
    {
        "image": fields.String(
            required=True,
            description="Imagem codificada em base64 (formatos suportados: JPG, PNG, BMP, TIFF)"
        )
    }
)

liveness_namespace = api.namespace(
    "liveness",
    path="/api",
    description="Operações de detecção de vivacidade facial"
)

upload_parser = liveness_namespace.parser()
upload_parser.add_argument(
    "image",
    type=FileStorage,
    location="files",
    required=True,
    help="Arquivo de imagem (JPG, PNG, BMP, TIFF)"
)

@liveness_namespace.route("/liveness")
class LivenessUploadResource(Resource):
    """Detecção de vivacidade através de upload de arquivo."""

    @liveness_namespace.expect(upload_parser)
    @liveness_namespace.response(200, "Resultado da detecção de vivacidade", liveness_response_model)
    @liveness_namespace.response(400, "Requisição inválida", error_model)
    def post(self):
        args = upload_parser.parse_args()
        uploaded_file = args.get("image")

        if uploaded_file is None:
            return {"status": "error", "message": "Arquivo de imagem não informado"}, 400

        file_bytes = uploaded_file.read()
        if not file_bytes:
            return {"status": "error", "message": "Arquivo de imagem vazio"}, 400

        image_array = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return {"status": "error", "message": "Não foi possível decodificar a imagem"}, 400

        return evaluate_liveness(image)

@liveness_namespace.route("/liveness_base64")
class LivenessBase64Resource(Resource):
    """Detecção de vivacidade através de payload base64."""

    @liveness_namespace.expect(base64_request_model, validate=True)
    @liveness_namespace.response(200, "Resultado da detecção de vivacidade", liveness_response_model)
    @liveness_namespace.response(400, "Requisição inválida", error_model)
    def post(self):
        payload = api.payload or {}
        image_b64 = payload.get("image")

        if not image_b64:
            return {"status": "error", "message": "Campo 'image' obrigatório"}, 400

        try:
            image_bytes = base64.b64decode(image_b64, validate=True)
        except (binascii.Error, ValueError):
            return {"status": "error", "message": "Payload base64 inválido"}, 400

        if not image_bytes:
            return {"status": "error", "message": "Imagem vazia após decodificação"}, 400

        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return {"status": "error", "message": "Não foi possível decodificar a imagem"}, 400

        return evaluate_liveness(image)

@api.route("/health")
class HealthCheckResource(Resource):
    """Endpoint de verificação de saúde da aplicação."""

    def get(self):
        return {
            "status": "healthy",
            "service": "Face Liveness Detection API",
            "version": LIB_VERSION,
            "mode": "REAL_VALIDATION",
            "mock_disabled": True,
            "timestamp": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            "endpoints": {
                "liveness": "/api/liveness",
                "liveness_base64": "/api/liveness_base64",
                "documentation": "/docs"
            },
            "requirements": {
                "native_library": "libttvfaceengine7.so",
                "license_required": True,
                "models_directory": "facewrapper/dict"
            }
        }, 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
