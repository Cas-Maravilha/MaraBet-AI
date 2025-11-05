#!/usr/bin/env python3
"""
Script para executar testes do MaraBet AI
Suporte para diferentes tipos de testes e configurações
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description=""):
    """Executa comando e retorna resultado"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Comando: {command}")
    print()
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    print(f"⏱️  Duração: {duration:.2f} segundos")
    print(f"📊 Código de saída: {result.returncode}")
    
    if result.stdout:
        print(f"\n📤 Saída padrão:")
        print(result.stdout)
    
    if result.stderr:
        print(f"\n❌ Erro:")
        print(result.stderr)
    
    return result.returncode == 0, duration

def run_unit_tests(parallel=False, coverage=True, verbose=False):
    """Executa testes unitários"""
    print("🧪 Executando testes unitários...")
    
    command = "pytest tests/test_units/ -m unit"
    
    if parallel:
        command += " -n auto"
    
    if coverage:
        command += " --cov=. --cov-report=html:htmlcov/unit --cov-report=term-missing"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes Unitários")
    
    if success:
        print(f"✅ Testes unitários executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes unitários falharam em {duration:.2f}s")
    
    return success

def run_integration_tests(parallel=False, coverage=True, verbose=False):
    """Executa testes de integração"""
    print("🔗 Executando testes de integração...")
    
    command = "pytest tests/test_integration/ -m integration"
    
    if parallel:
        command += " -n auto"
    
    if coverage:
        command += " --cov=. --cov-report=html:htmlcov/integration --cov-report=term-missing"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes de Integração")
    
    if success:
        print(f"✅ Testes de integração executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes de integração falharam em {duration:.2f}s")
    
    return success

def run_ml_tests(parallel=False, coverage=True, verbose=False):
    """Executa testes de ML"""
    print("🤖 Executando testes de Machine Learning...")
    
    command = "pytest tests/ -m ml"
    
    if parallel:
        command += " -n auto"
    
    if coverage:
        command += " --cov=. --cov-report=html:htmlcov/ml --cov-report=term-missing"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes de ML")
    
    if success:
        print(f"✅ Testes de ML executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes de ML falharam em {duration:.2f}s")
    
    return success

def run_auth_tests(parallel=False, coverage=True, verbose=False):
    """Executa testes de autenticação"""
    print("🔐 Executando testes de autenticação...")
    
    command = "pytest tests/ -m auth"
    
    if parallel:
        command += " -n auto"
    
    if coverage:
        command += " --cov=. --cov-report=html:htmlcov/auth --cov-report=term-missing"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes de Autenticação")
    
    if success:
        print(f"✅ Testes de autenticação executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes de autenticação falharam em {duration:.2f}s")
    
    return success

def run_api_tests(parallel=False, coverage=True, verbose=False):
    """Executa testes de API"""
    print("🌐 Executando testes de API...")
    
    command = "pytest tests/ -m api"
    
    if parallel:
        command += " -n auto"
    
    if coverage:
        command += " --cov=. --cov-report=html:htmlcov/api --cov-report=term-missing"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes de API")
    
    if success:
        print(f"✅ Testes de API executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes de API falharam em {duration:.2f}s")
    
    return success

def run_all_tests(parallel=False, coverage=True, verbose=False):
    """Executa todos os testes"""
    print("🎯 Executando todos os testes...")
    
    command = "pytest tests/"
    
    if parallel:
        command += " -n auto"
    
    if coverage:
        command += " --cov=. --cov-report=html:htmlcov/all --cov-report=term-missing --cov-report=xml:coverage.xml"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Todos os Testes")
    
    if success:
        print(f"✅ Todos os testes executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Alguns testes falharam em {duration:.2f}s")
    
    return success

def run_specific_test(test_path, verbose=False):
    """Executa teste específico"""
    print(f"🎯 Executando teste específico: {test_path}")
    
    command = f"pytest {test_path}"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, f"Teste Específico: {test_path}")
    
    if success:
        print(f"✅ Teste executado com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Teste falhou em {duration:.2f}s")
    
    return success

def run_slow_tests(parallel=False, verbose=False):
    """Executa apenas testes lentos"""
    print("🐌 Executando testes lentos...")
    
    command = "pytest tests/ -m slow"
    
    if parallel:
        command += " -n auto"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes Lentos")
    
    if success:
        print(f"✅ Testes lentos executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes lentos falharam em {duration:.2f}s")
    
    return success

def run_external_tests(parallel=False, verbose=False):
    """Executa testes que dependem de APIs externas"""
    print("🌍 Executando testes externos...")
    
    command = "pytest tests/ -m external"
    
    if parallel:
        command += " -n auto"
    
    if verbose:
        command += " -v -s"
    
    success, duration = run_command(command, "Testes Externos")
    
    if success:
        print(f"✅ Testes externos executados com sucesso em {duration:.2f}s")
    else:
        print(f"❌ Testes externos falharam em {duration:.2f}s")
    
    return success

def generate_coverage_report():
    """Gera relatório de cobertura"""
    print("📊 Gerando relatório de cobertura...")
    
    command = "coverage html -d htmlcov/final"
    success, duration = run_command(command, "Relatório de Cobertura")
    
    if success:
        print(f"✅ Relatório de cobertura gerado em {duration:.2f}s")
        print("📁 Relatório disponível em: htmlcov/final/index.html")
    else:
        print(f"❌ Falha ao gerar relatório de cobertura em {duration:.2f}s")
    
    return success

def check_test_environment():
    """Verifica ambiente de teste"""
    print("🔍 Verificando ambiente de teste...")
    
    # Verificar se pytest está instalado
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} instalado")
    except ImportError:
        print("❌ pytest não está instalado")
        return False
    
    # Verificar se dependências estão instaladas
    try:
        import pandas
        import numpy
        import sklearn
        print("✅ Dependências de ML instaladas")
    except ImportError as e:
        print(f"❌ Dependência de ML não encontrada: {e}")
        return False
    
    # Verificar se Redis está disponível
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=1)
        r.ping()
        print("✅ Redis disponível")
    except Exception:
        print("⚠️  Redis não disponível (alguns testes podem falhar)")
    
    # Verificar se banco de dados está disponível
    try:
        from armazenamento.banco_de_dados import SessionLocal
        db = SessionLocal()
        db.close()
        print("✅ Banco de dados disponível")
    except Exception as e:
        print(f"❌ Banco de dados não disponível: {e}")
        return False
    
    print("✅ Ambiente de teste verificado")
    return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes do MaraBet AI")
    
    parser.add_argument(
        "test_type",
        choices=[
            "unit", "integration", "ml", "auth", "api", 
            "all", "slow", "external", "specific"
        ],
        help="Tipo de teste a executar"
    )
    
    parser.add_argument(
        "--test-path",
        help="Caminho para teste específico (usado com --test-type specific)"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Executar testes em paralelo"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Não gerar relatório de cobertura"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Saída verbosa"
    )
    
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Verificar ambiente antes de executar testes"
    )
    
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="Apenas gerar relatório de cobertura"
    )
    
    args = parser.parse_args()
    
    # Verificar ambiente se solicitado
    if args.check_env:
        if not check_test_environment():
            print("❌ Ambiente de teste não está pronto")
            sys.exit(1)
    
    # Apenas gerar cobertura se solicitado
    if args.coverage_only:
        generate_coverage_report()
        return
    
    # Configurações
    coverage = not args.no_coverage
    parallel = args.parallel
    verbose = args.verbose
    
    # Executar testes baseado no tipo
    success = False
    start_time = time.time()
    
    if args.test_type == "unit":
        success = run_unit_tests(parallel, coverage, verbose)
    elif args.test_type == "integration":
        success = run_integration_tests(parallel, coverage, verbose)
    elif args.test_type == "ml":
        success = run_ml_tests(parallel, coverage, verbose)
    elif args.test_type == "auth":
        success = run_auth_tests(parallel, coverage, verbose)
    elif args.test_type == "api":
        success = run_api_tests(parallel, coverage, verbose)
    elif args.test_type == "all":
        success = run_all_tests(parallel, coverage, verbose)
    elif args.test_type == "slow":
        success = run_slow_tests(parallel, verbose)
    elif args.test_type == "external":
        success = run_external_tests(parallel, verbose)
    elif args.test_type == "specific":
        if not args.test_path:
            print("❌ Caminho do teste específico é obrigatório")
            sys.exit(1)
        success = run_specific_test(args.test_path, verbose)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Gerar relatório de cobertura se solicitado
    if coverage and success:
        generate_coverage_report()
    
    # Resultado final
    print(f"\n{'='*60}")
    if success:
        print(f"🎉 Testes executados com sucesso em {total_duration:.2f}s")
        sys.exit(0)
    else:
        print(f"💥 Testes falharam em {total_duration:.2f}s")
        sys.exit(1)

if __name__ == "__main__":
    main()
