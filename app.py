import sys
sys.path.append('.')

from flask import Flask, request, jsonify
from time import gmtime, strftime
import os
import base64
import json
import cv2
import numpy as np

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

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificação de saúde para Docker healthcheck
    """
    return jsonify({
        "status": "healthy",
        "service": "Face Liveness Detection API",
        "version": version.decode('utf-8') if version else "unknown",
        "mode": "REAL_VALIDATION",
        "mock_disabled": True,
        "timestamp": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        "endpoints": {
            "liveness": "/api/liveness",
            "liveness_base64": "/api/liveness_base64"
        },
        "requirements": {
            "native_library": "libttvfaceengine7.so",
            "license_required": True,
            "models_directory": "facewrapper/dict"
        }
    }), 200

@app.route('/api/liveness', methods=['POST'])
def check_liveness():
  file = request.files['image']
  image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
  
  faceRect = np.zeros([4], dtype=np.int32)
  livenessScore = np.zeros([1], dtype=np.double)
  angles = np.zeros([3], dtype=np.double)
  ret = ttv_detect_face(image, image.shape[1], image.shape[0], faceRect, livenessScore, angles)
  if ret == -1:
      result = "license error!"
  elif ret == -2:
      result = "init error!"
  elif ret == 0:
      result = "no face detected!"
  elif ret > 1:
      result = "multiple face detected!"
  elif faceRect[0] < 0 or faceRect[1] < 0 or faceRect[2] >= image.shape[1] or faceRect[2] >= image.shape[0]:
      result = "face is in boundary!"
  elif livenessScore[0] > 0.5:
      result = "genuine"
  else:
      result = "spoof"
  
  status = "ok"
  response = jsonify({"status": status, "data": {"result": result, "face_rect": {"x": int(faceRect[0]), "y": int(faceRect[1]), "w": int(faceRect[2] - faceRect[0] + 1), "h" : int(faceRect[3] - faceRect[1] + 1)}, "liveness_score": livenessScore[0],
    "angles": {"yaw": angles[0], "roll": angles[1], "pitch": angles[2]}}})

  response.status_code = 200
  response.headers["Content-Type"] = "application/json; charset=utf-8"
  return response

@app.route('/api/liveness_base64', methods=['POST'])
def check_liveness_base64():
  content = request.get_json()
  imageBase64 = content['image']
  image = cv2.imdecode(np.frombuffer(base64.b64decode(imageBase64), dtype=np.uint8), cv2.IMREAD_COLOR)

  faceRect = np.zeros([4], dtype=np.int32)
  livenessScore = np.zeros([1], dtype=np.double)
  angles = np.zeros([3], dtype=np.double)
  ret = ttv_detect_face(image, image.shape[1], image.shape[0], faceRect, livenessScore, angles)
  if ret == -1:
      result = "license error!"
  elif ret == -2:
      result = "init error!"
  elif ret == 0:
      result = "no face detected!"
  elif ret > 1:
      result = "multiple face detected!"
  elif faceRect[0] < 0 or faceRect[1] < 0 or faceRect[2] >= image.shape[1] or faceRect[2] >= image.shape[0]:
      result = "face is in boundary!"
  elif livenessScore[0] > 0.5:
      result = "genuine"
  else:
      result = "spoof"
  
  status = "ok"
  response = jsonify({"status": status, "data": {"result": result, "face_rect": {"x": int(faceRect[0]), "y": int(faceRect[1]), "w": int(faceRect[2] - faceRect[0] + 1), "h" : int(faceRect[3] - faceRect[1] + 1)}, "liveness_score": livenessScore[0],
    "angles": {"yaw": angles[0], "roll": angles[1], "pitch": angles[2]}}})

  response.status_code = 200
  response.headers["Content-Type"] = "application/json; charset=utf-8"
  return response


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
