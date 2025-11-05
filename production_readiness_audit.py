#!/usr/bin/env python3
"""
Auditoria Técnica Profunda - MaraBet AI
Verificação completa do que falta para finalizar a produção
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_command(command):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_file_exists(file_path):
    """Verifica se arquivo existe"""
    return os.path.exists(file_path)

def check_file_content(file_path, required_content=None):
    """Verifica se arquivo existe e tem conteúdo"""
    if not check_file_exists(file_path):
        return False, "Arquivo não existe"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if required_content and required_content not in content:
            return False, f"Conteúdo necessário não encontrado: {required_content}"
        
        return True, f"Arquivo OK ({len(content)} caracteres)"
    except Exception as e:
        return False, f"Erro ao ler arquivo: {e}"

def audit_production_readiness():
    """Auditoria completa de prontidão para produção"""
    print("🔍 MARABET AI - AUDITORIA TÉCNICA PROFUNDA")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📞 Contato: +224 932027393")
    
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": 0,
        "categories": {},
        "critical_issues": [],
        "warnings": [],
        "recommendations": [],
        "production_ready": False
    }
    
    print("\n🔧 1. VERIFICAÇÃO DE ARQUIVOS ESSENCIAIS")
    print("-" * 60)
    
    # Arquivos essenciais para produção
    essential_files = {
        "main.py": "Arquivo principal da aplicação",
        "app.py": "Aplicação FastAPI",
        "requirements.txt": "Dependências Python",
        "Dockerfile": "Containerização",
        "docker-compose.yml": "Orquestração de containers",
        "docker-compose.production.yml": "Configuração de produção",
        ".env.production": "Variáveis de ambiente de produção",
        "nginx.conf": "Configuração do Nginx",
        "README.md": "Documentação principal"
    }
    
    files_score = 0
    total_files = len(essential_files)
    
    for file_path, description in essential_files.items():
        exists, content = check_file_content(file_path)
        if exists:
            files_score += 1
            print(f"✅ {file_path}: {content}")
        else:
            print(f"❌ {file_path}: {content}")
            audit_results["critical_issues"].append(f"Arquivo essencial ausente: {file_path}")
    
    files_percentage = (files_score / total_files) * 100
    audit_results["categories"]["essential_files"] = {
        "score": files_score,
        "total": total_files,
        "percentage": files_percentage,
        "status": "PASS" if files_percentage >= 90 else "FAIL"
    }
    
    print(f"\n📊 Arquivos Essenciais: {files_score}/{total_files} ({files_percentage:.1f}%)")
    
    print("\n🐳 2. VERIFICAÇÃO DE DOCKER E CONTAINERIZAÇÃO")
    print("-" * 60)
    
    docker_score = 0
    docker_total = 0
    
    # Verificar Dockerfile
    docker_total += 1
    if check_file_exists("Dockerfile"):
        docker_score += 1
        print("✅ Dockerfile existe")
    else:
        print("❌ Dockerfile ausente")
        audit_results["critical_issues"].append("Dockerfile ausente")
    
    # Verificar docker-compose
    docker_total += 1
    if check_file_exists("docker-compose.yml"):
        docker_score += 1
        print("✅ docker-compose.yml existe")
    else:
        print("❌ docker-compose.yml ausente")
        audit_results["critical_issues"].append("docker-compose.yml ausente")
    
    # Verificar docker-compose.production.yml
    docker_total += 1
    if check_file_exists("docker-compose.production.yml"):
        docker_score += 1
        print("✅ docker-compose.production.yml existe")
    else:
        print("❌ docker-compose.production.yml ausente")
        audit_results["critical_issues"].append("docker-compose.production.yml ausente")
    
    # Verificar se Docker está instalado
    docker_total += 1
    success, stdout, stderr = run_command("docker --version")
    if success:
        docker_score += 1
        print(f"✅ Docker instalado: {stdout.strip()}")
    else:
        print("❌ Docker não instalado")
        audit_results["critical_issues"].append("Docker não instalado")
    
    # Verificar se Docker Compose está instalado
    docker_total += 1
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        docker_score += 1
        print(f"✅ Docker Compose instalado: {stdout.strip()}")
    else:
        print("❌ Docker Compose não instalado")
        audit_results["critical_issues"].append("Docker Compose não instalado")
    
    docker_percentage = (docker_score / docker_total) * 100
    audit_results["categories"]["docker"] = {
        "score": docker_score,
        "total": docker_total,
        "percentage": docker_percentage,
        "status": "PASS" if docker_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Docker: {docker_score}/{docker_total} ({docker_percentage:.1f}%)")
    
    print("\n🔐 3. VERIFICAÇÃO DE SEGURANÇA")
    print("-" * 60)
    
    security_score = 0
    security_total = 0
    
    # Verificar variáveis de ambiente
    security_total += 1
    if check_file_exists(".env.production"):
        security_score += 1
        print("✅ .env.production existe")
    else:
        print("❌ .env.production ausente")
        audit_results["critical_issues"].append(".env.production ausente")
    
    # Verificar se não há credenciais hardcoded
    security_total += 1
    hardcoded_creds = False
    sensitive_files = ["main.py", "app.py", "config.py"]
    
    for file_path in sensitive_files:
        if check_file_exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(cred in content.lower() for cred in ['password', 'secret', 'key', 'token']):
                    if not any(env_var in content for env_var in ['os.getenv', 'os.environ']):
                        hardcoded_creds = True
                        break
    
    if not hardcoded_creds:
        security_score += 1
        print("✅ Sem credenciais hardcoded")
    else:
        print("❌ Possíveis credenciais hardcoded encontradas")
        audit_results["warnings"].append("Possíveis credenciais hardcoded encontradas")
    
    # Verificar HTTPS/SSL
    security_total += 1
    if check_file_exists("nginx.conf"):
        with open("nginx.conf", 'r', encoding='utf-8') as f:
            nginx_content = f.read()
            if 'ssl' in nginx_content.lower() or 'https' in nginx_content.lower():
                security_score += 1
                print("✅ Configuração SSL/HTTPS encontrada")
            else:
                print("❌ Configuração SSL/HTTPS não encontrada")
                audit_results["warnings"].append("Configuração SSL/HTTPS não encontrada")
    else:
        print("❌ nginx.conf não encontrado")
        audit_results["warnings"].append("nginx.conf não encontrado")
    
    security_percentage = (security_score / security_total) * 100
    audit_results["categories"]["security"] = {
        "score": security_score,
        "total": security_total,
        "percentage": security_percentage,
        "status": "PASS" if security_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Segurança: {security_score}/{security_total} ({security_percentage:.1f}%)")
    
    print("\n📊 4. VERIFICAÇÃO DE BANCO DE DADOS")
    print("-" * 60)
    
    database_score = 0
    database_total = 0
    
    # Verificar configuração de banco
    database_total += 1
    if check_file_exists(".env.production"):
        with open(".env.production", 'r', encoding='utf-8') as f:
            env_content = f.read()
            if 'DATABASE_URL' in env_content:
                database_score += 1
                print("✅ DATABASE_URL configurado")
            else:
                print("❌ DATABASE_URL não configurado")
                audit_results["critical_issues"].append("DATABASE_URL não configurado")
    else:
        print("❌ .env.production não encontrado")
        audit_results["critical_issues"].append(".env.production não encontrado")
    
    # Verificar migrações
    database_total += 1
    migration_files = ["migrations/", "alembic/", "migrate.py"]
    migration_found = any(check_file_exists(f) for f in migration_files)
    
    if migration_found:
        database_score += 1
        print("✅ Sistema de migrações encontrado")
    else:
        print("❌ Sistema de migrações não encontrado")
        audit_results["warnings"].append("Sistema de migrações não encontrado")
    
    # Verificar backup
    database_total += 1
    backup_files = ["backup.py", "backup.sh", "backup/"]
    backup_found = any(check_file_exists(f) for f in backup_files)
    
    if backup_found:
        database_score += 1
        print("✅ Sistema de backup encontrado")
    else:
        print("❌ Sistema de backup não encontrado")
        audit_results["warnings"].append("Sistema de backup não encontrado")
    
    database_percentage = (database_score / database_total) * 100
    audit_results["categories"]["database"] = {
        "score": database_score,
        "total": database_total,
        "percentage": database_percentage,
        "status": "PASS" if database_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Banco de Dados: {database_score}/{database_total} ({database_percentage:.1f}%)")
    
    print("\n🧪 5. VERIFICAÇÃO DE TESTES")
    print("-" * 60)
    
    tests_score = 0
    tests_total = 0
    
    # Verificar testes unitários
    tests_total += 1
    test_files = ["test_", "tests/", "pytest.ini"]
    test_found = any(check_file_exists(f) for f in test_files)
    
    if test_found:
        tests_score += 1
        print("✅ Testes encontrados")
    else:
        print("❌ Testes não encontrados")
        audit_results["warnings"].append("Testes não encontrados")
    
    # Verificar testes de carga
    tests_total += 1
    load_test_files = ["load_testing", "locust", "jmeter", "artillery", "k6"]
    load_test_found = any(check_file_exists(f) for f in load_test_files)
    
    if load_test_found:
        tests_score += 1
        print("✅ Testes de carga encontrados")
    else:
        print("❌ Testes de carga não encontrados")
        audit_results["warnings"].append("Testes de carga não encontrados")
    
    # Verificar cobertura de código
    tests_total += 1
    coverage_files = ["coverage.xml", ".coverage", "codecov.yml"]
    coverage_found = any(check_file_exists(f) for f in coverage_files)
    
    if coverage_found:
        tests_score += 1
        print("✅ Cobertura de código encontrada")
    else:
        print("❌ Cobertura de código não encontrada")
        audit_results["warnings"].append("Cobertura de código não encontrada")
    
    tests_percentage = (tests_score / tests_total) * 100
    audit_results["categories"]["tests"] = {
        "score": tests_score,
        "total": tests_total,
        "percentage": tests_percentage,
        "status": "PASS" if tests_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Testes: {tests_score}/{tests_total} ({tests_percentage:.1f}%)")
    
    print("\n📈 6. VERIFICAÇÃO DE MONITORAMENTO")
    print("-" * 60)
    
    monitoring_score = 0
    monitoring_total = 0
    
    # Verificar Prometheus
    monitoring_total += 1
    prometheus_files = ["prometheus.yml", "prometheus/", "monitoring/"]
    prometheus_found = any(check_file_exists(f) for f in prometheus_files)
    
    if prometheus_found:
        monitoring_score += 1
        print("✅ Prometheus configurado")
    else:
        print("❌ Prometheus não configurado")
        audit_results["warnings"].append("Prometheus não configurado")
    
    # Verificar Grafana
    monitoring_total += 1
    grafana_files = ["grafana/", "dashboards/", "grafana-dashboard.json"]
    grafana_found = any(check_file_exists(f) for f in grafana_files)
    
    if grafana_found:
        monitoring_score += 1
        print("✅ Grafana configurado")
    else:
        print("❌ Grafana não configurado")
        audit_results["warnings"].append("Grafana não configurado")
    
    # Verificar logs
    monitoring_total += 1
    log_files = ["logs/", "logging.py", "log_config.py"]
    log_found = any(check_file_exists(f) for f in log_files)
    
    if log_found:
        monitoring_score += 1
        print("✅ Sistema de logs encontrado")
    else:
        print("❌ Sistema de logs não encontrado")
        audit_results["warnings"].append("Sistema de logs não encontrado")
    
    monitoring_percentage = (monitoring_score / monitoring_total) * 100
    audit_results["categories"]["monitoring"] = {
        "score": monitoring_score,
        "total": monitoring_total,
        "percentage": monitoring_percentage,
        "status": "PASS" if monitoring_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Monitoramento: {monitoring_score}/{monitoring_total} ({monitoring_percentage:.1f}%)")
    
    print("\n🚀 7. VERIFICAÇÃO DE DEPLOYMENT")
    print("-" * 60)
    
    deployment_score = 0
    deployment_total = 0
    
    # Verificar scripts de deploy
    deployment_total += 1
    deploy_files = ["deploy.sh", "deploy.py", "deploy/", "scripts/"]
    deploy_found = any(check_file_exists(f) for f in deploy_files)
    
    if deploy_found:
        deployment_score += 1
        print("✅ Scripts de deploy encontrados")
    else:
        print("❌ Scripts de deploy não encontrados")
        audit_results["warnings"].append("Scripts de deploy não encontrados")
    
    # Verificar CI/CD
    deployment_total += 1
    cicd_files = [".github/workflows/", "jenkinsfile", ".gitlab-ci.yml", "azure-pipelines.yml"]
    cicd_found = any(check_file_exists(f) for f in cicd_files)
    
    if cicd_found:
        deployment_score += 1
        print("✅ CI/CD configurado")
    else:
        print("❌ CI/CD não configurado")
        audit_results["warnings"].append("CI/CD não configurado")
    
    # Verificar health checks
    deployment_total += 1
    if check_file_exists("app.py"):
        with open("app.py", 'r', encoding='utf-8') as f:
            app_content = f.read()
            if 'health' in app_content.lower() or '/health' in app_content:
                deployment_score += 1
                print("✅ Health checks encontrados")
            else:
                print("❌ Health checks não encontrados")
                audit_results["warnings"].append("Health checks não encontrados")
    else:
        print("❌ app.py não encontrado")
        audit_results["warnings"].append("app.py não encontrado")
    
    deployment_percentage = (deployment_score / deployment_total) * 100
    audit_results["categories"]["deployment"] = {
        "score": deployment_score,
        "total": deployment_total,
        "percentage": deployment_percentage,
        "status": "PASS" if deployment_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Deployment: {deployment_score}/{deployment_total} ({deployment_percentage:.1f}%)")
    
    print("\n📚 8. VERIFICAÇÃO DE DOCUMENTAÇÃO")
    print("-" * 60)
    
    docs_score = 0
    docs_total = 0
    
    # Verificar README
    docs_total += 1
    if check_file_exists("README.md"):
        with open("README.md", 'r', encoding='utf-8') as f:
            readme_content = f.read()
            if len(readme_content) > 1000:  # README substancial
                docs_score += 1
                print("✅ README.md completo")
            else:
                print("❌ README.md muito curto")
                audit_results["warnings"].append("README.md muito curto")
    else:
        print("❌ README.md não encontrado")
        audit_results["critical_issues"].append("README.md não encontrado")
    
    # Verificar documentação da API
    docs_total += 1
    if check_file_exists("app.py"):
        with open("app.py", 'r', encoding='utf-8') as f:
            app_content = f.read()
            if 'docs_url' in app_content or 'swagger' in app_content.lower():
                docs_score += 1
                print("✅ Documentação da API encontrada")
            else:
                print("❌ Documentação da API não encontrada")
                audit_results["warnings"].append("Documentação da API não encontrada")
    else:
        print("❌ app.py não encontrado")
        audit_results["warnings"].append("app.py não encontrado")
    
    # Verificar guias
    docs_total += 1
    guide_files = ["GUIDE", "DOCS", "SETUP", "INSTALL"]
    guide_found = any(check_file_exists(f) for f in guide_files)
    
    if guide_found:
        docs_score += 1
        print("✅ Guias encontrados")
    else:
        print("❌ Guias não encontrados")
        audit_results["warnings"].append("Guias não encontrados")
    
    docs_percentage = (docs_score / docs_total) * 100
    audit_results["categories"]["documentation"] = {
        "score": docs_score,
        "total": docs_total,
        "percentage": docs_percentage,
        "status": "PASS" if docs_percentage >= 80 else "FAIL"
    }
    
    print(f"\n📊 Documentação: {docs_score}/{docs_total} ({docs_percentage:.1f}%)")
    
    # Calcular score geral
    total_score = 0
    total_possible = 0
    
    for category, data in audit_results["categories"].items():
        total_score += data["score"]
        total_possible += data["total"]
    
    overall_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
    audit_results["overall_score"] = overall_percentage
    audit_results["production_ready"] = overall_percentage >= 85 and len(audit_results["critical_issues"]) == 0
    
    print("\n🎯 RESUMO DA AUDITORIA")
    print("=" * 80)
    print(f"📊 Score Geral: {overall_percentage:.1f}%")
    print(f"🚀 Pronto para Produção: {'SIM' if audit_results['production_ready'] else 'NÃO'}")
    
    print(f"\n📋 Categorias:")
    for category, data in audit_results["categories"].items():
        status_icon = "✅" if data["status"] == "PASS" else "❌"
        print(f"  {status_icon} {category.title()}: {data['percentage']:.1f}%")
    
    if audit_results["critical_issues"]:
        print(f"\n🚨 Problemas Críticos ({len(audit_results['critical_issues'])}):")
        for issue in audit_results["critical_issues"]:
            print(f"  ❌ {issue}")
    
    if audit_results["warnings"]:
        print(f"\n⚠️ Avisos ({len(audit_results['warnings'])}):")
        for warning in audit_results["warnings"]:
            print(f"  ⚠️ {warning}")
    
    # Gerar recomendações
    print(f"\n💡 RECOMENDAÇÕES PARA PRODUÇÃO:")
    print("-" * 60)
    
    if not audit_results["production_ready"]:
        print("🔧 AÇÕES CRÍTICAS NECESSÁRIAS:")
        
        if len(audit_results["critical_issues"]) > 0:
            print("1. Resolver problemas críticos listados acima")
        
        if overall_percentage < 85:
            print("2. Melhorar score geral para pelo menos 85%")
        
        print("3. Implementar todas as verificações de segurança")
        print("4. Configurar monitoramento completo")
        print("5. Criar scripts de deploy automatizados")
        print("6. Implementar testes de carga")
        print("7. Configurar backup e disaster recovery")
        print("8. Documentar procedimentos de produção")
    else:
        print("✅ Sistema pronto para produção!")
        print("📋 Próximos passos recomendados:")
        print("1. Fazer deploy em ambiente de staging")
        print("2. Executar testes de carga completos")
        print("3. Configurar monitoramento em produção")
        print("4. Implementar backup automatizado")
        print("5. Treinar equipe de operações")
    
    # Salvar relatório
    with open("production_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: production_audit_report.json")
    print(f"📞 Contato para suporte: +224 932027393")
    
    return audit_results

def main():
    print("🚀 Iniciando auditoria técnica profunda...")
    
    # Executar auditoria
    results = audit_production_readiness()
    
    if results["production_ready"]:
        print("\n🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("Todas as verificações críticas passaram!")
    else:
        print("\n⚠️ SISTEMA NÃO ESTÁ PRONTO PARA PRODUÇÃO")
        print("Resolva os problemas críticos antes do deploy!")
    
    return results

if __name__ == "__main__":
    main()
