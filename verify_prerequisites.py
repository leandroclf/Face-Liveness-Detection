#!/usr/bin/env python3
"""
Script de Verificação de Pré-requisitos para Face Liveness Detection
Valida todos os componentes necessários para validação real (sem modo mock)
"""

import os
import sys
import subprocess
from pathlib import Path

class PrerequisiteChecker:
    """Verificador completo de pré-requisitos do sistema"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_success(self, message):
        """Registra sucesso"""
        print(f"✅ {message}")
        self.success_count += 1
        
    def log_error(self, message):
        """Registra erro crítico"""
        print(f"❌ {message}")
        self.errors.append(message)
        
    def log_warning(self, message):
        """Registra aviso"""
        print(f"⚠️  {message}")
        self.warnings.append(message)
        
    def check_native_library(self):
        """Verifica biblioteca nativa principal"""
        print("\n🔍 Verificando biblioteca nativa...")
        
        lib_path = self.project_root / "facewrapper" / "libs" / "libttvfaceengine7.so"
        
        if lib_path.exists():
            self.log_success(f"Biblioteca nativa encontrada: {lib_path}")
            
            # Verificar tamanho do arquivo
            size_mb = lib_path.stat().st_size / (1024 * 1024)
            if size_mb > 1:  # Biblioteca deve ter pelo menos 1MB
                self.log_success(f"Tamanho da biblioteca: {size_mb:.2f} MB")
            else:
                self.log_warning(f"Biblioteca muito pequena: {size_mb:.2f} MB - pode estar corrompida")
                
        else:
            self.log_error(f"Biblioteca nativa NÃO encontrada: {lib_path}")
            self.log_error("REQUISITO OBRIGATÓRIO: Baixar libttvfaceengine7.so do fornecedor")
            
    def check_openvino_dependencies(self):
        """Verifica dependências OpenVINO"""
        print("\n🔍 Verificando dependências OpenVINO...")
        
        openvino_path = self.project_root / "openvino"
        
        if openvino_path.exists():
            self.log_success(f"Diretório OpenVINO encontrado: {openvino_path}")
            
            # Verificar bibliotecas essenciais
            essential_libs = [
                "libopenvino.so",
                "libopenvino_intel_cpu_plugin.so",
                "libopenvino_c.so"
            ]
            
            for lib in essential_libs:
                lib_file = openvino_path / lib
                if lib_file.exists():
                    self.log_success(f"Biblioteca OpenVINO: {lib}")
                else:
                    self.log_warning(f"Biblioteca OpenVINO não encontrada: {lib}")
                    
        else:
            self.log_error(f"Diretório OpenVINO NÃO encontrado: {openvino_path}")
            self.log_error("Execute: git lfs pull para baixar dependências")
            
    def check_models_directory(self):
        """Verifica diretório de modelos"""
        print("\n🔍 Verificando diretório de modelos...")
        
        models_path = self.project_root / "facewrapper" / "dict"
        
        if models_path.exists():
            self.log_success(f"Diretório de modelos encontrado: {models_path}")
            
            # Listar conteúdo
            model_files = list(models_path.glob("*"))
            if model_files:
                self.log_success(f"Arquivos de modelo encontrados: {len(model_files)}")
                for model_file in model_files:
                    print(f"   📄 {model_file.name}")
            else:
                self.log_warning("Diretório de modelos está vazio")
                
        else:
            self.log_error(f"Diretório de modelos NÃO encontrado: {models_path}")
            
    def check_license_configuration(self):
        """Verifica configuração de licença"""
        print("\n🔍 Verificando configuração de licença...")
        
        # Verificar variável de ambiente
        license_key = os.environ.get('LICENSE_KEY')
        if license_key:
            if license_key.startswith('your-license-key') or len(license_key) < 10:
                self.log_warning("LICENSE_KEY parece ser um placeholder")
            else:
                self.log_success("LICENSE_KEY configurada via variável de ambiente")
        else:
            self.log_warning("LICENSE_KEY não definida como variável de ambiente")
            
        # Verificar arquivo de licença
        license_file = self.project_root / "license.txt"
        if license_file.exists():
            self.log_success(f"Arquivo de licença encontrado: {license_file}")
            
            # Verificar conteúdo
            try:
                content = license_file.read_text().strip()
                if content and not content.startswith('your-license-key'):
                    self.log_success("Arquivo de licença contém chave válida")
                else:
                    self.log_warning("Arquivo de licença contém placeholder")
            except Exception as e:
                self.log_error(f"Erro ao ler arquivo de licença: {e}")
        else:
            self.log_warning("Arquivo license.txt não encontrado")
            
        if not license_key and not license_file.exists():
            self.log_error("NENHUMA configuração de licença encontrada")
            
    def check_python_dependencies(self):
        """Verifica dependências Python"""
        print("\n🔍 Verificando dependências Python...")
        
        required_packages = [
            'numpy',
            'opencv-python',
            'flask',
            'gradio',
            'pillow'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.log_success(f"Pacote Python: {package}")
            except ImportError:
                self.log_error(f"Pacote Python NÃO encontrado: {package}")
                
    def check_system_compatibility(self):
        """Verifica compatibilidade do sistema"""
        print("\n🔍 Verificando compatibilidade do sistema...")
        
        # Verificar sistema operacional
        if sys.platform.startswith('linux'):
            self.log_success(f"Sistema operacional: Linux ({sys.platform})")
        elif sys.platform.startswith('win'):
            self.log_warning(f"Sistema operacional: Windows ({sys.platform}) - biblioteca nativa pode não ser compatível")
        else:
            self.log_warning(f"Sistema operacional: {sys.platform} - compatibilidade não testada")
            
        # Verificar arquitetura
        import platform
        arch = platform.machine()
        if arch in ['x86_64', 'AMD64']:
            self.log_success(f"Arquitetura: {arch}")
        else:
            self.log_warning(f"Arquitetura: {arch} - pode não ser suportada")
            
    def generate_report(self):
        """Gera relatório final"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE VERIFICAÇÃO DE PRÉ-REQUISITOS")
        print("="*60)
        
        print(f"✅ Verificações bem-sucedidas: {self.success_count}")
        print(f"⚠️  Avisos: {len(self.warnings)}")
        print(f"❌ Erros críticos: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ ERROS CRÍTICOS QUE IMPEDEM O FUNCIONAMENTO:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
                
        if self.warnings:
            print("\n⚠️  AVISOS QUE PODEM AFETAR O DESEMPENHO:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
                
        print("\n" + "="*60)
        
        if self.errors:
            print("🚫 SISTEMA NÃO PODE FUNCIONAR - Resolva os erros críticos")
            return False
        elif self.warnings:
            print("⚠️  SISTEMA PODE FUNCIONAR COM LIMITAÇÕES - Verifique os avisos")
            return True
        else:
            print("🚀 SISTEMA PRONTO PARA VALIDAÇÃO REAL")
            return True
            
    def run_full_check(self):
        """Executa verificação completa"""
        print("🔍 INICIANDO VERIFICAÇÃO COMPLETA DE PRÉ-REQUISITOS")
        print("="*60)
        
        self.check_native_library()
        self.check_openvino_dependencies()
        self.check_models_directory()
        self.check_license_configuration()
        self.check_python_dependencies()
        self.check_system_compatibility()
        
        return self.generate_report()

if __name__ == "__main__":
    checker = PrerequisiteChecker()
    success = checker.run_full_check()
    
    # Código de saída para scripts automatizados
    sys.exit(0 if success else 1)