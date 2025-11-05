#!/usr/bin/env python3
"""
Auditoria Técnica Profunda - MaraBet AI
Verificação completa de prontidão para domínio e banco de dados Angoweb
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class TechnicalAudit:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'categories': {},
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'overall_score': 0,
            'ready_for_production': False
        }
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []
        self.total_checks = 0
        self.passed_checks = 0
    
    def print_header(self, text):
        print("\n" + "=" * 80)
        print(f"🔍 {text}")
        print("=" * 80)
    
    def check_file(self, filepath, description):
        """Verifica se arquivo existe"""
        self.total_checks += 1
        exists = os.path.exists(filepath)
        if exists:
            self.passed_checks += 1
            print(f"✅ {description}: {filepath}")
        else:
            print(f"❌ {description}: {filepath}")
            self.critical_issues.append(f"Arquivo faltando: {filepath}")
        return exists
    
    def check_directory(self, dirpath, description):
        """Verifica se diretório existe"""
        self.total_checks += 1
        exists = os.path.isdir(dirpath)
        if exists:
            self.passed_checks += 1
            print(f"✅ {description}: {dirpath}")
        else:
            print(f"❌ {description}: {dirpath}")
            self.critical_issues.append(f"Diretório faltando: {dirpath}")
        return exists
    
    def check_file_content(self, filepath, search_string, description):
        """Verifica conteúdo de arquivo"""
        self.total_checks += 1
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if search_string in content:
                    self.passed_checks += 1
                    print(f"✅ {description}")
                    return True
                else:
                    print(f"⚠️  {description} (não encontrado)")
                    self.warnings.append(f"{description} - revisar {filepath}")
                    return False
        except Exception as e:
            print(f"❌ Erro ao verificar {filepath}: {e}")
            return False
    
    def audit_docker_configuration(self):
        """Audita configuração Docker"""
        self.print_header("1. AUDITORIA DE DOCKER E CONTAINERIZAÇÃO")
        
        score = 0
        total = 12
        
        # Arquivos Docker essenciais
        if self.check_file("Dockerfile", "Dockerfile principal"):
            score += 1
        
        if self.check_file("docker-compose.local.yml", "Docker Compose para VPS local"):
            score += 1
            # Verificar conteúdo
            if self.check_file_content("docker-compose.local.yml", "marabet-web", "Serviço web configurado"):
                score += 1
            if self.check_file_content("docker-compose.local.yml", "postgres", "PostgreSQL configurado"):
                score += 1
            if self.check_file_content("docker-compose.local.yml", "redis", "Redis configurado"):
                score += 1
            if self.check_file_content("docker-compose.local.yml", "nginx", "Nginx configurado"):
                score += 1
        
        if self.check_file("docker-compose.monitoring.yml", "Docker Compose monitoramento"):
            score += 1
        
        if self.check_file(".dockerignore", ".dockerignore"):
            score += 1
        
        # Scripts de instalação Docker
        if self.check_file("install_docker_windows.py", "Script instalação Docker Windows"):
            score += 1
        
        if self.check_file("install_docker.ps1", "Script PowerShell Docker"):
            score += 1
        
        # Documentação Docker
        if self.check_file("DOCKER_INSTALLATION_GUIDE.md", "Guia instalação Docker"):
            score += 1
        
        if self.check_file("docker-compose.test.yml", "Docker Compose teste"):
            score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['docker'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Docker: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_database_configuration(self):
        """Audita configuração de banco de dados"""
        self.print_header("2. AUDITORIA DE BANCO DE DADOS")
        
        score = 0
        total = 10
        
        # Sistema de migrações
        if self.check_directory("migrations", "Diretório migrations"):
            score += 1
        
        if self.check_file("migrations/001_initial_schema.sql", "Migração inicial"):
            score += 1
            # Verificar tabelas essenciais
            if self.check_file_content("migrations/001_initial_schema.sql", "CREATE TABLE users", "Tabela users"):
                score += 1
            if self.check_file_content("migrations/001_initial_schema.sql", "CREATE TABLE predictions", "Tabela predictions"):
                score += 1
            if self.check_file_content("migrations/001_initial_schema.sql", "CREATE TABLE bets", "Tabela bets"):
                score += 1
            if self.check_file_content("migrations/001_initial_schema.sql", "CREATE TABLE bankroll", "Tabela bankroll"):
                score += 1
        
        if self.check_file("migrate.py", "Script de migração Python"):
            score += 1
        
        if self.check_file("migrations/seeds/dev_seeds.sql", "Seeds de desenvolvimento"):
            score += 1
        
        if self.check_file("DATABASE_MIGRATIONS_DOCUMENTATION.md", "Documentação migrações"):
            score += 1
        
        # Verificar diretórios de backup
        if self.check_directory("migrations/backups", "Diretório backups migrações"):
            score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['database'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Banco de Dados: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_nginx_ssl_configuration(self):
        """Audita configuração Nginx e SSL"""
        self.print_header("3. AUDITORIA DE NGINX E SSL/HTTPS")
        
        score = 0
        total = 10
        
        # Diretório Nginx
        if self.check_directory("nginx", "Diretório nginx"):
            score += 1
        
        # Configurações Nginx
        if self.check_file("nginx/nginx-angoweb.conf", "Config Nginx Angoweb"):
            score += 1
            # Verificar configurações essenciais
            if self.check_file_content("nginx/nginx-angoweb.conf", "ssl_certificate", "SSL configurado"):
                score += 1
            if self.check_file_content("nginx/nginx-angoweb.conf", "marabet.ao", "Domínio marabet.ao"):
                score += 1
            if self.check_file_content("nginx/nginx-angoweb.conf", "proxy_pass", "Proxy configurado"):
                score += 1
        
        if self.check_file("nginx/nginx-ssl.conf", "Config Nginx SSL genérica"):
            score += 1
        
        # Scripts SSL
        if self.check_file("setup_ssl.sh", "Script setup SSL"):
            score += 1
        
        if self.check_file("renew_ssl.sh", "Script renovação SSL"):
            score += 1
        
        if self.check_file("test_ssl.sh", "Script teste SSL"):
            score += 1
        
        # Documentação SSL
        if self.check_file("SSL_HTTPS_DOCUMENTATION.md", "Documentação SSL"):
            score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['nginx_ssl'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Nginx/SSL: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_environment_configuration(self):
        """Audita configurações de ambiente"""
        self.print_header("4. AUDITORIA DE VARIÁVEIS DE AMBIENTE")
        
        score = 0
        total = 8
        
        # Arquivos de configuração
        if self.check_file("config_angoweb.env.example", "Template env Angoweb"):
            score += 1
            # Verificar variáveis essenciais
            if self.check_file_content("config_angoweb.env.example", "DOMAIN=marabet.ao", "Domínio configurado"):
                score += 1
            if self.check_file_content("config_angoweb.env.example", "DB_HOST", "Database host"):
                score += 1
            if self.check_file_content("config_angoweb.env.example", "REDIS_HOST", "Redis host"):
                score += 1
            if self.check_file_content("config_angoweb.env.example", "DEFAULT_CURRENCY=AOA", "Moeda Angola"):
                score += 1
        
        if self.check_file("config_local_server.env.example", "Template env servidor local"):
            score += 1
        
        if self.check_file("server_config.json", "Configuração servidor"):
            score += 1
        
        # Verificar se não há .env commitado (segurança)
        if not os.path.exists(".env"):
            print("✅ Arquivo .env não commitado (segurança)")
            score += 1
        else:
            print("⚠️  Arquivo .env existe (verificar se está no .gitignore)")
            self.warnings.append("Arquivo .env encontrado - verificar .gitignore")
        
        percentage = (score / total) * 100
        self.results['categories']['environment'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Ambiente: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_backup_system(self):
        """Audita sistema de backup"""
        self.print_header("5. AUDITORIA DE SISTEMA DE BACKUP")
        
        score = 0
        total = 10
        
        # Estrutura de diretórios
        if self.check_directory("backups", "Diretório backups"):
            score += 1
        
        if self.check_directory("backups/scripts", "Diretório scripts backup"):
            score += 1
        
        # Scripts de backup
        if self.check_file("backups/scripts/backup.sh", "Script backup bash"):
            score += 1
            if self.check_file_content("backups/scripts/backup.sh", "pg_dump", "Backup PostgreSQL"):
                score += 1
            if self.check_file_content("backups/scripts/backup.sh", "redis", "Backup Redis"):
                score += 1
        
        if self.check_file("backups/scripts/backup.py", "Script backup Python"):
            score += 1
        
        if self.check_file("backups/scripts/restore.sh", "Script restauração"):
            score += 1
        
        if self.check_file("backups/scripts/setup_cron.sh", "Script setup cron"):
            score += 1
        
        # Documentação
        if self.check_file("AUTOMATED_BACKUP_DOCUMENTATION.md", "Documentação backup"):
            score += 1
        
        # Verificar executável
        if os.path.exists("backups/scripts/backup.sh"):
            if os.access("backups/scripts/backup.sh", os.X_OK):
                print("✅ Script backup.sh é executável")
                score += 1
            else:
                print("⚠️  Script backup.sh não é executável")
                self.warnings.append("Tornar backup.sh executável: chmod +x")
        
        percentage = (score / total) * 100
        self.results['categories']['backup'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Backup: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_monitoring_system(self):
        """Audita sistema de monitoramento"""
        self.print_header("6. AUDITORIA DE MONITORAMENTO")
        
        score = 0
        total = 12
        
        # Estrutura de diretórios
        if self.check_directory("monitoring", "Diretório monitoring"):
            score += 1
        
        if self.check_directory("monitoring/prometheus", "Diretório Prometheus"):
            score += 1
        
        if self.check_directory("monitoring/grafana", "Diretório Grafana"):
            score += 1
        
        if self.check_directory("monitoring/alertmanager", "Diretório Alertmanager"):
            score += 1
        
        # Configurações
        if self.check_file("monitoring/prometheus/prometheus.yml", "Config Prometheus"):
            score += 1
            if self.check_file_content("monitoring/prometheus/prometheus.yml", "scrape_configs", "Scrape configs"):
                score += 1
        
        if self.check_file("monitoring/prometheus/alerts/marabet_alerts.yml", "Alertas Prometheus"):
            score += 1
        
        if self.check_file("monitoring/grafana/grafana.ini", "Config Grafana"):
            score += 1
        
        if self.check_file("monitoring/alertmanager/config.yml", "Config Alertmanager"):
            score += 1
        
        if self.check_file("monitoring/setup_monitoring.sh", "Script setup monitoramento"):
            score += 1
        
        # Documentação
        if self.check_file("GRAFANA_MONITORING_DOCUMENTATION.md", "Documentação Grafana"):
            score += 1
        
        # Docker compose
        if self.check_file("docker-compose.monitoring.yml", "Docker Compose monitoramento"):
            score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['monitoring'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Monitoramento: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_load_testing(self):
        """Audita sistema de testes de carga"""
        self.print_header("7. AUDITORIA DE TESTES DE CARGA")
        
        score = 0
        total = 10
        
        # Estrutura
        if self.check_directory("load_tests", "Diretório load_tests"):
            score += 1
        
        # Locust
        if self.check_file("load_tests/locust/locustfile.py", "Testes Locust"):
            score += 1
        
        if self.check_file("load_tests/locust/locust.conf", "Config Locust"):
            score += 1
        
        # K6
        if self.check_file("load_tests/k6/k6_test.js", "Testes K6"):
            score += 1
        
        # Artillery
        if self.check_file("load_tests/artillery/artillery.yml", "Testes Artillery"):
            score += 1
        
        # Scripts
        if self.check_file("load_tests/scripts/run_tests.sh", "Script executor testes"):
            score += 1
        
        # Requirements
        if self.check_file("load_tests/requirements.txt", "Requirements testes"):
            score += 1
        
        # Diretórios de reports
        if self.check_directory("load_tests/reports", "Diretório reports"):
            score += 1
        
        # Documentação
        if self.check_file("LOAD_TESTING_DOCUMENTATION.md", "Documentação testes"):
            score += 1
        
        # Verificar executável
        if os.path.exists("load_tests/scripts/run_tests.sh"):
            if os.access("load_tests/scripts/run_tests.sh", os.X_OK):
                print("✅ Script run_tests.sh é executável")
                score += 1
            else:
                print("⚠️  Script run_tests.sh não é executável")
        
        percentage = (score / total) * 100
        self.results['categories']['load_testing'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Testes de Carga: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_angoweb_readiness(self):
        """Audita prontidão específica para Angoweb"""
        self.print_header("8. AUDITORIA DE PRONTIDÃO ANGOWEB")
        
        score = 0
        total = 12
        
        # Documentação Angoweb
        if self.check_file("ANGOWEB_MIGRATION_GUIDE.md", "Guia migração Angoweb"):
            score += 1
        
        if self.check_file("ANGOWEB_SETUP_COMPLETE.md", "Guia setup completo"):
            score += 1
            # Verificar conteúdo
            if self.check_file_content("ANGOWEB_SETUP_COMPLETE.md", "marabet.ao", "Domínio marabet.ao"):
                score += 1
            if self.check_file_content("ANGOWEB_SETUP_COMPLETE.md", "+244 222 638 200", "Contato Angoweb"):
                score += 1
        
        if self.check_file("CHECKLIST_ANGOWEB.md", "Checklist Angoweb"):
            score += 1
        
        # Scripts Angoweb
        if self.check_file("setup_angoweb.sh", "Script setup Angoweb"):
            score += 1
            if self.check_file_content("setup_angoweb.sh", "apt update", "Comandos Ubuntu"):
                score += 1
            if self.check_file_content("setup_angoweb.sh", "docker", "Instalação Docker"):
                score += 1
            if self.check_file_content("setup_angoweb.sh", "postgresql", "Instalação PostgreSQL"):
                score += 1
        
        if self.check_file("validate_angoweb_setup.sh", "Script validação"):
            score += 1
        
        # Configurações específicas Angola
        if self.check_file("config_angoweb.env.example", "Config ambiente Angoweb"):
            score += 1
            if self.check_file_content("config_angoweb.env.example", "Africa/Luanda", "Timezone Angola"):
                score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['angoweb_readiness'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Prontidão Angoweb: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_security(self):
        """Audita configurações de segurança"""
        self.print_header("9. AUDITORIA DE SEGURANÇA")
        
        score = 0
        total = 10
        
        # Verificar .gitignore
        if self.check_file(".gitignore", ".gitignore"):
            score += 1
            if self.check_file_content(".gitignore", ".env", ".env no gitignore"):
                score += 1
            if self.check_file_content(".gitignore", "*.log", "Logs no gitignore"):
                score += 1
        
        # Verificar que senhas não estão hardcoded
        print("\n🔍 Verificando arquivos Python por senhas hardcoded...")
        has_hardcoded = False
        for root, dirs, files in os.walk("."):
            # Ignorar diretórios desnecessários
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Procurar padrões suspeitos
                            if 'password = "' in content.lower() and 'your_password' not in content.lower():
                                print(f"⚠️  Possível senha hardcoded em: {filepath}")
                                has_hardcoded = True
                    except:
                        pass
        
        if not has_hardcoded:
            print("✅ Nenhuma senha hardcoded detectada")
            score += 2
        
        # SSL/HTTPS configurado
        if os.path.exists("nginx/nginx-angoweb.conf"):
            with open("nginx/nginx-angoweb.conf", 'r') as f:
                if "ssl_protocols TLSv1.2 TLSv1.3" in f.read():
                    print("✅ SSL com protocolos seguros")
                    score += 1
        
        # Firewall configurado no setup
        if os.path.exists("setup_angoweb.sh"):
            with open("setup_angoweb.sh", 'r') as f:
                if "ufw" in f.read():
                    print("✅ Firewall UFW configurado no setup")
                    score += 1
        
        # Fail2Ban configurado
        if os.path.exists("setup_angoweb.sh"):
            with open("setup_angoweb.sh", 'r') as f:
                if "fail2ban" in f.read():
                    print("✅ Fail2Ban configurado no setup")
                    score += 1
        
        # Headers de segurança
        if os.path.exists("nginx/nginx-angoweb.conf"):
            with open("nginx/nginx-angoweb.conf", 'r') as f:
                content = f.read()
                if "X-Frame-Options" in content and "X-Content-Type-Options" in content:
                    print("✅ Headers de segurança configurados")
                    score += 1
        
        # Rate limiting
        if os.path.exists("nginx/nginx-angoweb.conf"):
            with open("nginx/nginx-angoweb.conf", 'r') as f:
                if "limit_req_zone" in f.read():
                    print("✅ Rate limiting configurado")
                    score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['security'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Segurança: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def audit_documentation(self):
        """Audita documentação"""
        self.print_header("10. AUDITORIA DE DOCUMENTAÇÃO")
        
        score = 0
        total = 10
        
        # Documentação essencial
        if self.check_file("README.md", "README principal"):
            score += 1
            if self.check_file_content("README.md", "marabet.ao", "Referência Angoweb"):
                score += 1
        
        # Guias técnicos
        if self.check_file("ANGOWEB_SETUP_COMPLETE.md", "Setup completo Angoweb"):
            score += 1
        
        if self.check_file("DATABASE_MIGRATIONS_DOCUMENTATION.md", "Documentação migrações"):
            score += 1
        
        if self.check_file("SSL_HTTPS_DOCUMENTATION.md", "Documentação SSL"):
            score += 1
        
        if self.check_file("AUTOMATED_BACKUP_DOCUMENTATION.md", "Documentação backup"):
            score += 1
        
        if self.check_file("GRAFANA_MONITORING_DOCUMENTATION.md", "Documentação Grafana"):
            score += 1
        
        if self.check_file("LOAD_TESTING_DOCUMENTATION.md", "Documentação testes"):
            score += 1
        
        # Checklist
        if self.check_file("CHECKLIST_ANGOWEB.md", "Checklist Angoweb"):
            score += 1
        
        # Relatório final
        if self.check_file("PRODUCTION_READINESS_FINAL_REPORT.md", "Relatório final"):
            score += 1
        
        percentage = (score / total) * 100
        self.results['categories']['documentation'] = {
            'score': score,
            'total': total,
            'percentage': percentage,
            'status': 'PASS' if percentage >= 80 else 'FAIL'
        }
        
        print(f"\n📊 Score Documentação: {score}/{total} ({percentage:.1f}%)")
        return percentage >= 80
    
    def generate_report(self):
        """Gera relatório final"""
        self.print_header("RELATÓRIO FINAL DA AUDITORIA")
        
        # Atualizar results com listas locais
        self.results['critical_issues'] = self.critical_issues
        self.results['warnings'] = self.warnings
        self.results['recommendations'] = self.recommendations
        
        # Calcular score geral
        self.results['overall_score'] = (self.passed_checks / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"\n📊 SCORE GERAL: {self.results['overall_score']:.1f}%")
        print(f"✅ Checks Passados: {self.passed_checks}/{self.total_checks}")
        
        # Status por categoria
        print("\n📋 STATUS POR CATEGORIA:")
        for category, data in self.results['categories'].items():
            status_icon = "✅" if data['status'] == 'PASS' else "❌"
            print(f"{status_icon} {category.replace('_', ' ').title()}: {data['percentage']:.1f}% ({data['score']}/{data['total']})")
        
        # Problemas críticos
        if self.critical_issues:
            print(f"\n🚨 PROBLEMAS CRÍTICOS ({len(self.critical_issues)}):")
            for issue in self.critical_issues[:10]:
                print(f"   • {issue}")
        else:
            print("\n✅ NENHUM PROBLEMA CRÍTICO!")
        
        # Avisos
        if self.warnings:
            print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"   • {warning}")
        
        # Determinar se está pronto
        self.results['ready_for_production'] = (
            self.results['overall_score'] >= 90 and
            len(self.critical_issues) == 0
        )
        
        print("\n" + "=" * 80)
        if self.results['ready_for_production']:
            print("🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
            print("✅ Pode receber domínio marabet.ao")
            print("✅ Pode hospedar banco de dados PostgreSQL")
            print("✅ Pronto para deploy na Angoweb")
        elif self.results['overall_score'] >= 80:
            print("⚠️  SISTEMA QUASE PRONTO")
            print("Resolver problemas críticos antes do deploy")
        else:
            print("❌ SISTEMA NÃO ESTÁ PRONTO")
            print("Várias correções necessárias")
        print("=" * 80)
        
        # Salvar relatório JSON
        with open('technical_audit_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print("\n💾 Relatório salvo: technical_audit_report.json")

def main():
    print("═" * 80)
    print("🔍 AUDITORIA TÉCNICA PROFUNDA - MARABET AI")
    print("Verificação de Prontidão para Domínio e Banco de Dados Angoweb")
    print("═" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📞 Contato: +224 932027393")
    print("═" * 80)
    
    audit = TechnicalAudit()
    
    # Executar todas as auditorias
    audit.audit_docker_configuration()
    audit.audit_database_configuration()
    audit.audit_nginx_ssl_configuration()
    audit.audit_environment_configuration()
    audit.audit_backup_system()
    audit.audit_monitoring_system()
    audit.audit_load_testing()
    audit.audit_angoweb_readiness()
    audit.audit_security()
    audit.audit_documentation()
    
    # Gerar relatório final
    audit.generate_report()
    
    return 0 if audit.results['ready_for_production'] else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

