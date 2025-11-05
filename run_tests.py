#!/usr/bin/env python3
"""
Script de execução de testes para o MaraBet AI
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n🔧 {description}")
    print(f"Comando: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Sucesso!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def run_unit_tests():
    """Executa testes unitários"""
    print("\n🧪 EXECUTANDO TESTES UNITÁRIOS")
    print("=" * 50)
    
    command = "python -m pytest tests/unit/ -v --tb=short"
    return run_command(command, "Testes unitários")

def run_integration_tests():
    """Executa testes de integração"""
    print("\n🔗 EXECUTANDO TESTES DE INTEGRAÇÃO")
    print("=" * 50)
    
    command = "python -m pytest tests/integration/ -v --tb=short"
    return run_command(command, "Testes de integração")

def run_e2e_tests():
    """Executa testes end-to-end"""
    print("\n🌐 EXECUTANDO TESTES END-TO-END")
    print("=" * 50)
    
    command = "python -m pytest tests/e2e/ -v --tb=short"
    return run_command(command, "Testes end-to-end")

def run_all_tests():
    """Executa todos os testes"""
    print("\n🚀 EXECUTANDO TODOS OS TESTES")
    print("=" * 50)
    
    command = "python -m pytest tests/ -v --tb=short"
    return run_command(command, "Todos os testes")

def run_coverage():
    """Executa testes com cobertura"""
    print("\n📊 EXECUTANDO TESTES COM COBERTURA")
    print("=" * 50)
    
    # Instalar pytest-cov se não estiver instalado
    install_command = "pip install pytest-cov"
    run_command(install_command, "Instalando pytest-cov")
    
    command = "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term"
    return run_command(command, "Testes com cobertura")

def run_specific_test(test_path):
    """Executa teste específico"""
    print(f"\n🎯 EXECUTANDO TESTE ESPECÍFICO: {test_path}")
    print("=" * 50)
    
    command = f"python -m pytest {test_path} -v --tb=short"
    return run_command(command, f"Teste específico: {test_path}")

def run_tests_by_marker(marker):
    """Executa testes por marcador"""
    print(f"\n🏷️ EXECUTANDO TESTES COM MARCADOR: {marker}")
    print("=" * 50)
    
    command = f"python -m pytest tests/ -m {marker} -v --tb=short"
    return run_command(command, f"Testes com marcador: {marker}")

def run_fast_tests():
    """Executa apenas testes rápidos"""
    print("\n⚡ EXECUTANDO TESTES RÁPIDOS")
    print("=" * 50)
    
    command = "python -m pytest tests/ -v --tb=short -m 'not slow'"
    return run_command(command, "Testes rápidos")

def run_slow_tests():
    """Executa apenas testes lentos"""
    print("\n🐌 EXECUTANDO TESTES LENTOS")
    print("=" * 50)
    
    command = "python -m pytest tests/ -v --tb=short -m 'slow'"
    return run_command(command, "Testes lentos")

def check_test_structure():
    """Verifica estrutura de testes"""
    print("\n📁 VERIFICANDO ESTRUTURA DE TESTES")
    print("=" * 50)
    
    test_dirs = ['tests', 'tests/unit', 'tests/integration', 'tests/e2e']
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            print(f"✅ {test_dir}/ existe")
        else:
            print(f"❌ {test_dir}/ não existe")
    
    # Verificar arquivos de teste
    test_files = [
        'tests/conftest.py',
        'tests/unit/test_ml_models.py',
        'tests/unit/test_collectors.py',
        'tests/unit/test_feature_engineering.py',
        'tests/integration/test_pipeline.py',
        'tests/integration/test_api_endpoints.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✅ {test_file} existe")
        else:
            print(f"❌ {test_file} não existe")

def install_dependencies():
    """Instala dependências de teste"""
    print("\n📦 INSTALANDO DEPENDÊNCIAS DE TESTE")
    print("=" * 50)
    
    dependencies = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'pytest-html',
        'pytest-xdist'
    ]
    
    for dep in dependencies:
        command = f"pip install {dep}"
        run_command(command, f"Instalando {dep}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Script de execução de testes para o MaraBet AI')
    parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'all', 'coverage'], 
                       default='all', help='Tipo de teste a executar')
    parser.add_argument('--test', help='Caminho para teste específico')
    parser.add_argument('--marker', help='Marcador de teste (ex: unit, integration, slow)')
    parser.add_argument('--fast', action='store_true', help='Executar apenas testes rápidos')
    parser.add_argument('--slow', action='store_true', help='Executar apenas testes lentos')
    parser.add_argument('--install', action='store_true', help='Instalar dependências de teste')
    parser.add_argument('--check', action='store_true', help='Verificar estrutura de testes')
    
    args = parser.parse_args()
    
    print("🔮 MARABET AI - SISTEMA DE TESTES AUTOMATIZADOS")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('tests'):
        print("❌ Diretório 'tests' não encontrado!")
        print("   Execute este script no diretório raiz do projeto.")
        return 1
    
    # Instalar dependências se solicitado
    if args.install:
        install_dependencies()
        return 0
    
    # Verificar estrutura se solicitado
    if args.check:
        check_test_structure()
        return 0
    
    # Executar testes baseado nos argumentos
    success = True
    
    if args.test:
        success = run_specific_test(args.test)
    elif args.marker:
        success = run_tests_by_marker(args.marker)
    elif args.fast:
        success = run_fast_tests()
    elif args.slow:
        success = run_slow_tests()
    elif args.type == 'unit':
        success = run_unit_tests()
    elif args.type == 'integration':
        success = run_integration_tests()
    elif args.type == 'e2e':
        success = run_e2e_tests()
    elif args.type == 'coverage':
        success = run_coverage()
    else:  # all
        success = run_all_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES EXECUTADOS COM SUCESSO!")
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
