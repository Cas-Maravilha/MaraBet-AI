#!/usr/bin/env python3
"""
Script para executar testes no CI/CD
Otimizado para ambientes de integração contínua
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_ci_command(command, description=""):
    """Executa comando no CI e retorna resultado"""
    print(f"\n🚀 {description}")
    print(f"Comando: {command}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    print(f"⏱️  Duração: {duration:.2f}s")
    print(f"📊 Código de saída: {result.returncode}")
    
    if result.stdout:
        print("📤 Saída:")
        print(result.stdout)
    
    if result.stderr:
        print("❌ Erro:")
        print(result.stderr)
    
    return result.returncode == 0, duration, result.stdout, result.stderr

def setup_test_environment():
    """Configura ambiente de teste para CI"""
    print("🔧 Configurando ambiente de teste...")
    
    # Instalar dependências de teste
    commands = [
        "pip install pytest pytest-cov pytest-xdist pytest-html pytest-json-report",
        "pip install pytest-asyncio pytest-mock pytest-timeout",
        "pip install coverage[toml]",
        "pip install -r requirements.txt"
    ]
    
    for cmd in commands:
        success, duration, stdout, stderr = run_ci_command(cmd, f"Executando: {cmd}")
        if not success:
            print(f"❌ Falha ao executar: {cmd}")
            return False
    
    print("✅ Ambiente de teste configurado")
    return True

def run_unit_tests_ci():
    """Executa testes unitários no CI"""
    print("🧪 Executando testes unitários...")
    
    command = """
    pytest tests/test_units/ \
        -m unit \
        --cov=. \
        --cov-report=xml:coverage-unit.xml \
        --cov-report=term-missing \
        --junitxml=test-results-unit.xml \
        --json-report --json-report-file=test-report-unit.json \
        --html=test-report-unit.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Testes Unitários")
    
    if success:
        print(f"✅ Testes unitários: {duration:.2f}s")
    else:
        print(f"❌ Testes unitários falharam: {duration:.2f}s")
    
    return success

def run_integration_tests_ci():
    """Executa testes de integração no CI"""
    print("🔗 Executando testes de integração...")
    
    command = """
    pytest tests/test_integration/ \
        -m integration \
        --cov=. \
        --cov-report=xml:coverage-integration.xml \
        --cov-report=term-missing \
        --junitxml=test-results-integration.xml \
        --json-report --json-report-file=test-report-integration.json \
        --html=test-report-integration.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Testes de Integração")
    
    if success:
        print(f"✅ Testes de integração: {duration:.2f}s")
    else:
        print(f"❌ Testes de integração falharam: {duration:.2f}s")
    
    return success

def run_ml_tests_ci():
    """Executa testes de ML no CI"""
    print("🤖 Executando testes de ML...")
    
    command = """
    pytest tests/ \
        -m ml \
        --cov=. \
        --cov-report=xml:coverage-ml.xml \
        --cov-report=term-missing \
        --junitxml=test-results-ml.xml \
        --json-report --json-report-file=test-report-ml.json \
        --html=test-report-ml.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Testes de ML")
    
    if success:
        print(f"✅ Testes de ML: {duration:.2f}s")
    else:
        print(f"❌ Testes de ML falharam: {duration:.2f}s")
    
    return success

def run_auth_tests_ci():
    """Executa testes de autenticação no CI"""
    print("🔐 Executando testes de autenticação...")
    
    command = """
    pytest tests/ \
        -m auth \
        --cov=. \
        --cov-report=xml:coverage-auth.xml \
        --cov-report=term-missing \
        --junitxml=test-results-auth.xml \
        --json-report --json-report-file=test-report-auth.json \
        --html=test-report-auth.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Testes de Autenticação")
    
    if success:
        print(f"✅ Testes de autenticação: {duration:.2f}s")
    else:
        print(f"❌ Testes de autenticação falharam: {duration:.2f}s")
    
    return success

def run_api_tests_ci():
    """Executa testes de API no CI"""
    print("🌐 Executando testes de API...")
    
    command = """
    pytest tests/ \
        -m api \
        --cov=. \
        --cov-report=xml:coverage-api.xml \
        --cov-report=term-missing \
        --junitxml=test-results-api.xml \
        --json-report --json-report-file=test-report-api.json \
        --html=test-report-api.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Testes de API")
    
    if success:
        print(f"✅ Testes de API: {duration:.2f}s")
    else:
        print(f"❌ Testes de API falharam: {duration:.2f}s")
    
    return success

def run_all_tests_ci():
    """Executa todos os testes no CI"""
    print("🎯 Executando todos os testes...")
    
    command = """
    pytest tests/ \
        --cov=. \
        --cov-report=xml:coverage.xml \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --junitxml=test-results.xml \
        --json-report --json-report-file=test-report.json \
        --html=test-report.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers \
        --maxfail=5
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Todos os Testes")
    
    if success:
        print(f"✅ Todos os testes: {duration:.2f}s")
    else:
        print(f"❌ Alguns testes falharam: {duration:.2f}s")
    
    return success

def run_parallel_tests_ci():
    """Executa testes em paralelo no CI"""
    print("⚡ Executando testes em paralelo...")
    
    command = """
    pytest tests/ \
        -n auto \
        --cov=. \
        --cov-report=xml:coverage.xml \
        --cov-report=term-missing \
        --junitxml=test-results.xml \
        --json-report --json-report-file=test-report.json \
        --html=test-report.html \
        --self-contained-html \
        -v \
        --tb=short \
        --strict-markers
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Testes Paralelos")
    
    if success:
        print(f"✅ Testes paralelos: {duration:.2f}s")
    else:
        print(f"❌ Testes paralelos falharam: {duration:.2f}s")
    
    return success

def generate_coverage_report_ci():
    """Gera relatório de cobertura final no CI"""
    print("📊 Gerando relatório de cobertura final...")
    
    command = """
    coverage combine coverage-*.xml
    coverage html -d htmlcov/final
    coverage report --show-missing
    """
    
    success, duration, stdout, stderr = run_ci_command(command, "Relatório de Cobertura")
    
    if success:
        print(f"✅ Relatório de cobertura gerado: {duration:.2f}s")
        print("📁 Relatório disponível em: htmlcov/final/index.html")
    else:
        print(f"❌ Falha ao gerar relatório: {duration:.2f}s")
    
    return success

def check_coverage_threshold():
    """Verifica se cobertura atende ao threshold"""
    print("📊 Verificando threshold de cobertura...")
    
    command = "coverage report --fail-under=80"
    
    success, duration, stdout, stderr = run_ci_command(command, "Verificação de Cobertura")
    
    if success:
        print(f"✅ Cobertura atende ao threshold: {duration:.2f}s")
    else:
        print(f"❌ Cobertura abaixo do threshold: {duration:.2f}s")
        print("📊 Cobertura atual:")
        print(stdout)
    
    return success

def run_linting_ci():
    """Executa linting no CI"""
    print("🔍 Executando linting...")
    
    commands = [
        "black --check .",
        "isort --check-only .",
        "flake8 .",
        "bandit -r . -f json -o bandit-report.json",
        "safety check -r requirements.txt --json --output safety-report.json"
    ]
    
    all_success = True
    
    for cmd in commands:
        success, duration, stdout, stderr = run_ci_command(cmd, f"Linting: {cmd.split()[0]}")
        if not success:
            print(f"❌ Falha no linting: {cmd.split()[0]}")
            all_success = False
    
    if all_success:
        print("✅ Linting passou em todos os checks")
    else:
        print("❌ Alguns checks de linting falharam")
    
    return all_success

def run_security_scan_ci():
    """Executa scan de segurança no CI"""
    print("🔒 Executando scan de segurança...")
    
    commands = [
        "bandit -r . -f json -o security-report.json",
        "safety check -r requirements.txt --json --output safety-report.json"
    ]
    
    all_success = True
    
    for cmd in commands:
        success, duration, stdout, stderr = run_ci_command(cmd, f"Segurança: {cmd.split()[0]}")
        if not success:
            print(f"⚠️  Aviso de segurança: {cmd.split()[0]}")
            # Não falhar por avisos de segurança, apenas reportar
    
    print("✅ Scan de segurança concluído")
    return True

def create_test_summary():
    """Cria resumo dos testes"""
    print("📋 Criando resumo dos testes...")
    
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": "CI",
        "python_version": sys.version,
        "test_results": {
            "unit_tests": "pending",
            "integration_tests": "pending",
            "ml_tests": "pending",
            "auth_tests": "pending",
            "api_tests": "pending",
            "all_tests": "pending"
        },
        "coverage": "pending",
        "linting": "pending",
        "security": "pending"
    }
    
    # Salvar resumo
    with open("test-summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Resumo dos testes criado: test-summary.json")
    return True

def main():
    """Função principal do CI"""
    print("🚀 Iniciando testes no CI/CD")
    print("=" * 60)
    
    # Configurar ambiente
    if not setup_test_environment():
        print("❌ Falha na configuração do ambiente")
        sys.exit(1)
    
    # Criar resumo
    create_test_summary()
    
    # Executar testes
    test_results = {}
    
    # Testes unitários
    test_results["unit"] = run_unit_tests_ci()
    
    # Testes de integração
    test_results["integration"] = run_integration_tests_ci()
    
    # Testes de ML
    test_results["ml"] = run_ml_tests_ci()
    
    # Testes de autenticação
    test_results["auth"] = run_auth_tests_ci()
    
    # Testes de API
    test_results["api"] = run_api_tests_ci()
    
    # Todos os testes
    test_results["all"] = run_all_tests_ci()
    
    # Linting
    test_results["linting"] = run_linting_ci()
    
    # Scan de segurança
    test_results["security"] = run_security_scan_ci()
    
    # Relatório de cobertura
    test_results["coverage"] = generate_coverage_report_ci()
    
    # Verificar threshold de cobertura
    test_results["coverage_threshold"] = check_coverage_threshold()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_type, success in test_results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_type.upper():<20} {status}")
    
    # Determinar se CI passou
    ci_success = all(test_results.values())
    
    if ci_success:
        print("\n🎉 CI/CD executado com sucesso!")
        sys.exit(0)
    else:
        print("\n💥 CI/CD falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
