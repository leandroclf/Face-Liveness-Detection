import ctypes, ctypes.util
from ctypes import *
from numpy.ctypeslib import ndpointer
import sys
import os
import numpy as np

# Configuração de paths para OpenVINO
sys.path.append('/opt/intel/openvino_2022/runtime/lib/intel64')

# Configuração rigorosa - SEM MODO MOCK
class FaceEngineError(Exception):
    """Exceção personalizada para erros do motor de detecção facial"""
    pass

class FaceEngineValidator:
    """Validador rigoroso de pré-requisitos do sistema"""
    
    @staticmethod
    def validate_native_library():
        """Valida a presença da biblioteca nativa obrigatória"""
        lib_path = os.path.abspath(os.path.dirname(__file__)) + '/libs/libttvfaceengine7.so'
        
        if not os.path.exists(lib_path):
            raise FaceEngineError(
                f"❌ ERRO CRÍTICO: Biblioteca nativa não encontrada em {lib_path}\n"
                f"📋 REQUISITOS OBRIGATÓRIOS:\n"
                f"   1. Baixar libttvfaceengine7.so do fornecedor\n"
                f"   2. Colocar em facewrapper/libs/\n"
                f"   3. Verificar permissões de execução\n"
                f"   4. Validar compatibilidade do sistema operacional\n"
                f"🚫 MODO MOCK DESABILITADO - Sistema não pode funcionar sem biblioteca nativa"
            )
        
        return lib_path
    
    @staticmethod
    def validate_openvino_dependencies():
        """Valida dependências do OpenVINO"""
        openvino_path = os.path.abspath(os.path.dirname(__file__)) + '/../openvino'
        
        if not os.path.exists(openvino_path):
            raise FaceEngineError(
                f"❌ ERRO: Dependências OpenVINO não encontradas em {openvino_path}\n"
                f"📋 Execute: git lfs pull para baixar dependências"
            )
    
    @staticmethod
    def validate_models_directory():
        """Valida diretório de modelos"""
        models_path = os.path.abspath(os.path.dirname(__file__)) + '/dict'
        
        if not os.path.exists(models_path):
            raise FaceEngineError(
                f"❌ ERRO: Diretório de modelos não encontrado: {models_path}\n"
                f"📋 Criar diretório e adicionar modelos necessários"
            )

# Validação rigorosa de pré-requisitos
print("🔍 Iniciando validação rigorosa de pré-requisitos...")

try:
    # Validar biblioteca nativa
    lib_path = FaceEngineValidator.validate_native_library()
    print(f"✅ Biblioteca nativa encontrada: {lib_path}")
    
    # Validar dependências OpenVINO
    FaceEngineValidator.validate_openvino_dependencies()
    print("✅ Dependências OpenVINO validadas")
    
    # Validar diretório de modelos
    FaceEngineValidator.validate_models_directory()
    print("✅ Diretório de modelos validado")
    
    # Carregar biblioteca nativa
    print("🔄 Carregando biblioteca nativa...")
    liveness_engine = cdll.LoadLibrary(lib_path)
    print("✅ Biblioteca nativa carregada com sucesso")
    
except Exception as e:
    print(f"❌ FALHA NA VALIDAÇÃO: {e}")
    raise FaceEngineError(f"Sistema não pode inicializar: {e}")

# Configuração das funções da biblioteca nativa
print("🔧 Configurando interfaces da biblioteca nativa...")

ttv_version = liveness_engine.ttv_version
ttv_version.argtypes = []
ttv_version.restype = ctypes.c_char_p

ttv_get_hwid = liveness_engine.ttv_get_hwid
ttv_get_hwid.argtypes = []
ttv_get_hwid.restype = ctypes.c_char_p

ttv_init = liveness_engine.ttv_init
ttv_init.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
ttv_init.restype = ctypes.c_int32

ttv_init_offline = liveness_engine.ttv_init_offline
ttv_init_offline.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
ttv_init_offline.restype = ctypes.c_int32

ttv_detect_face = liveness_engine.ttv_detect_face
ttv_detect_face.argtypes = [ndpointer(ctypes.c_ubyte, flags='C_CONTIGUOUS'), ctypes.c_int32, ctypes.c_int32, ndpointer(ctypes.c_int32, flags='C_CONTIGUOUS'), ndpointer(ctypes.c_double, flags='C_CONTIGUOUS'), ndpointer(ctypes.c_double, flags='C_CONTIGUOUS')]
ttv_detect_face.restype = ctypes.c_int32

print("✅ Interfaces da biblioteca configuradas com sucesso")
print("🚀 Sistema pronto para validação real - MODO MOCK DESABILITADO")