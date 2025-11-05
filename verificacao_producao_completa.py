#!/usr/bin/env python3
"""
MaraBet AI - Verificação Técnica Completa para Produção
Análise profunda de todos os aspectos críticos do sistema
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class ProductionReadinessCheck:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []
        self.score = 0
        self.max_score = 0
        
    def print_header(self):
        """Imprime cabeçalho"""
        print("=" * 80)
        print("🔍 MARABET AI - VERIFICAÇÃO TÉCNICA COMPLETA PARA PRODUÇÃO")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Diretório: {self.base_dir}")
        print("=" * 80)
        print()
    
    def check_essential_files(self):
        """Verifica arquivos essenciais"""
        print("📁 1. ARQUIVOS ESSENCIAIS")
        print("-" * 80)
        
        essential_files = {
            'app.py': 'Aplicação principal',
            'requirements.txt': 'Dependências Python',
            'README.md': 'Documentação principal',
            'docker-compose.local.yml': 'Docker Compose produção',
            'Dockerfile': 'Imagem Docker',
            '.env': 'Variáveis de ambiente (ou .env.example)',
            'nginx/nginx-angoweb.conf': 'Configuração Nginx',
            'migrations/001_initial_schema.sql': 'Schema inicial DB',
        }
        
        for file, description in essential_files.items():
            file_path = self.base_dir / file
            alt_path = self.base_dir / f"{file}.example"
            
            if file_path.exists() or alt_path.exists():
                print(f"  ✅ {file}: {description}")
                self.score += 1
            else:
                print(f"  ❌ {file}: {description} - FALTANDO")
                self.critical_issues.append(f"Arquivo essencial faltando: {file}")
            
            self.max_score += 1
        
        print()
    
    def check_documentation(self):
        """Verifica documentação"""
        print("📚 2. DOCUMENTAÇÃO")
        print("-" * 80)
        
        docs = {
            'README.md': 'Documentação geral',
            'GUIA_RESPONSIVO_COMPLETO.md': 'Sistema responsivo',
            'COMPATIBILIDADE_MULTIPLATAFORMA.md': 'Compatibilidade',
            'ARQUITETURA_PRODUCAO.md': 'Arquitetura produção',
            'legal/LEGAL_COMPLIANCE_ANGOLA.md': 'Legal e compliance',
            'legal/TERMOS_E_CONDICOES.md': 'Termos de uso',
            'legal/POLITICA_PRIVACIDADE.md': 'Política privacidade',
            'ANGOWEB_MIGRATION_GUIDE.md': 'Guia deploy Angola',
        }
        
        for doc, desc in docs.items():
            if (self.base_dir / doc).exists():
                print(f"  ✅ {doc}: {desc}")
                self.score += 1
            else:
                print(f"  ⚠️  {doc}: {desc} - Faltando")
                self.warnings.append(f"Documentação faltando: {doc}")
            
            self.max_score += 1
        
        print()
    
    def check_docker_setup(self):
        """Verifica configuração Docker"""
        print("🐳 3. DOCKER E CONTAINERIZAÇÃO")
        print("-" * 80)
        
        # Verificar Docker instalado
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"  ✅ Docker: {result.stdout.strip()}")
                self.score += 2
            else:
                print(f"  ❌ Docker: Não instalado")
                self.critical_issues.append("Docker não instalado")
        except Exception as e:
            print(f"  ⚠️  Docker: Não disponível ({e})")
            self.warnings.append("Docker não encontrado - necessário para produção")
        
        self.max_score += 2
        
        # Verificar Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"  ✅ Docker Compose: {result.stdout.strip()}")
                self.score += 1
            else:
                # Tentar comando alternativo
                result = subprocess.run(['docker', 'compose', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"  ✅ Docker Compose: {result.stdout.strip()}")
                    self.score += 1
                else:
                    print(f"  ❌ Docker Compose: Não instalado")
                    self.critical_issues.append("Docker Compose não instalado")
        except Exception as e:
            print(f"  ⚠️  Docker Compose: Não disponível")
            self.warnings.append("Docker Compose não encontrado")
        
        self.max_score += 1
        
        # Verificar arquivos Docker
        docker_files = [
            'Dockerfile',
            'docker-compose.yml',
            'docker-compose.local.yml',
            'docker-compose.prod.yml',
            '.dockerignore'
        ]
        
        for df in docker_files:
            if (self.base_dir / df).exists():
                print(f"  ✅ {df}")
                self.score += 0.5
            else:
                print(f"  ⚠️  {df}: Não encontrado")
            self.max_score += 0.5
        
        print()
    
    def check_database(self):
        """Verifica configuração de banco de dados"""
        print("🗄️  4. BANCO DE DADOS")
        print("-" * 80)
        
        # Verificar migrations
        migrations_dir = self.base_dir / 'migrations'
        if migrations_dir.exists():
            migrations = list(migrations_dir.glob('*.sql'))
            print(f"  ✅ Pasta migrations: {len(migrations)} migrations")
            self.score += 2
        else:
            print(f"  ❌ Pasta migrations: Não encontrada")
            self.critical_issues.append("Sistema de migrações não encontrado")
        
        self.max_score += 2
        
        # Verificar script de migração
        if (self.base_dir / 'migrate.py').exists():
            print(f"  ✅ Script migrate.py")
            self.score += 1
        else:
            print(f"  ⚠️  Script migrate.py: Não encontrado")
            self.warnings.append("Script de migração não encontrado")
        
        self.max_score += 1
        
        # Verificar schema inicial
        if (self.base_dir / 'migrations' / '001_initial_schema.sql').exists():
            print(f"  ✅ Schema inicial: 001_initial_schema.sql")
            self.score += 1
        else:
            print(f"  ❌ Schema inicial: Não encontrado")
            self.critical_issues.append("Schema inicial do banco não encontrado")
        
        self.max_score += 1
        
        print()
    
    def check_security(self):
        """Verifica configurações de segurança"""
        print("🔒 5. SEGURANÇA")
        print("-" * 80)
        
        # SSL/HTTPS
        ssl_files = [
            'nginx/nginx-angoweb.conf',
            'ssl/setup_ssl.sh',
            'ssl/renew_ssl.sh'
        ]
        
        ssl_count = 0
        for sf in ssl_files:
            if (self.base_dir / sf).exists():
                print(f"  ✅ {sf}")
                ssl_count += 1
        
        if ssl_count >= 2:
            self.score += 2
            print(f"  ✅ Configuração SSL: {ssl_count}/3 arquivos")
        else:
            print(f"  ⚠️  Configuração SSL: Incompleta ({ssl_count}/3)")
            self.warnings.append("Configuração SSL incompleta")
        
        self.max_score += 2
        
        # Verificar .env.example (não deve ter senhas reais)
        if (self.base_dir / '.env.example').exists():
            print(f"  ✅ .env.example: Presente")
            self.score += 1
        else:
            print(f"  ⚠️  .env.example: Não encontrado")
            self.warnings.append(".env.example não encontrado")
        
        self.max_score += 1
        
        # Verificar se .env não está no Git
        gitignore_path = self.base_dir / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
                if '.env' in content:
                    print(f"  ✅ .gitignore: .env protegido")
                    self.score += 1
                else:
                    print(f"  ⚠️  .gitignore: .env não listado")
                    self.warnings.append(".env deve estar no .gitignore")
        else:
            print(f"  ⚠️  .gitignore: Não encontrado")
        
        self.max_score += 1
        
        print()
    
    def check_apis(self):
        """Verifica integração com APIs"""
        print("🌐 6. APIS INTEGRADAS")
        print("-" * 80)
        
        # Verificar arquivos de teste
        api_tests = [
            'test_api_ultra_plan.py',
            'test_apis_connection.py',
            'test_ip_config.py'
        ]
        
        for test in api_tests:
            if (self.base_dir / test).exists():
                print(f"  ✅ {test}")
                self.score += 0.5
            else:
                print(f"  ⚠️  {test}: Não encontrado")
            self.max_score += 0.5
        
        # Verificar configuração de IP
        if (self.base_dir / 'ip_config.json').exists():
            print(f"  ✅ ip_config.json: Configurado")
            with open(self.base_dir / 'ip_config.json', 'r') as f:
                config = json.load(f)
                ip = config.get('system_ip', 'N/A')
                print(f"     IP Sistema: {ip}")
            self.score += 1
        else:
            print(f"  ⚠️  ip_config.json: Não configurado")
            self.warnings.append("IP do sistema não configurado")
        
        self.max_score += 1
        
        print()
    
    def check_responsive_design(self):
        """Verifica design responsivo"""
        print("📱 7. DESIGN RESPONSIVO E PWA")
        print("-" * 80)
        
        responsive_files = {
            'static/css/responsive.css': 'CSS responsivo',
            'static/js/responsive.js': 'JavaScript mobile-first',
            'static/manifest.json': 'PWA Manifest',
            'static/sw.js': 'Service Worker',
            'templates/base_responsive.html': 'Template base',
            'templates/dashboard_responsive.html': 'Dashboard',
            'templates/offline.html': 'Página offline',
        }
        
        for file, desc in responsive_files.items():
            if (self.base_dir / file).exists():
                print(f"  ✅ {file}: {desc}")
                self.score += 1
            else:
                print(f"  ⚠️  {file}: {desc} - Faltando")
                self.warnings.append(f"Arquivo responsivo faltando: {file}")
            
            self.max_score += 1
        
        print()
    
    def check_legal_compliance(self):
        """Verifica documentação legal"""
        print("⚖️  8. LEGAL E COMPLIANCE")
        print("-" * 80)
        
        legal_docs = {
            'legal/LEGAL_COMPLIANCE_ANGOLA.md': 'Enquadramento legal',
            'legal/TERMOS_E_CONDICOES.md': 'Termos e condições',
            'legal/POLITICA_PRIVACIDADE.md': 'Política de privacidade',
            'legal/LEGAL_COMPLIANCE_RESUMO.md': 'Resumo compliance',
        }
        
        for doc, desc in legal_docs.items():
            if (self.base_dir / doc).exists():
                print(f"  ✅ {doc}: {desc}")
                self.score += 2
            else:
                print(f"  ❌ {doc}: {desc} - FALTANDO")
                self.critical_issues.append(f"Documento legal obrigatório: {doc}")
            
            self.max_score += 2
        
        print()
    
    def check_monitoring(self):
        """Verifica monitoramento"""
        print("📊 9. MONITORAMENTO")
        print("-" * 80)
        
        monitoring_files = [
            'monitoring/prometheus/prometheus.yml',
            'monitoring/grafana/grafana.ini',
            'monitoring/alertmanager/config.yml',
            'docker-compose.monitoring.yml'
        ]
        
        for mf in monitoring_files:
            if (self.base_dir / mf).exists():
                print(f"  ✅ {mf}")
                self.score += 1
            else:
                print(f"  ⚠️  {mf}: Não encontrado")
                self.warnings.append(f"Arquivo de monitoramento: {mf}")
            
            self.max_score += 1
        
        print()
    
    def check_backup_system(self):
        """Verifica sistema de backup"""
        print("💾 10. SISTEMA DE BACKUP")
        print("-" * 80)
        
        backup_files = [
            'backups/scripts/backup.sh',
            'backups/scripts/restore.sh',
            'backups/scripts/setup_cron.sh'
        ]
        
        for bf in backup_files:
            if (self.base_dir / bf).exists():
                print(f"  ✅ {bf}")
                self.score += 1
            else:
                print(f"  ⚠️  {bf}: Não encontrado")
                self.warnings.append(f"Script de backup: {bf}")
            
            self.max_score += 1
        
        print()
    
    def check_environment_config(self):
        """Verifica configurações de ambiente"""
        print("⚙️  11. CONFIGURAÇÃO DE AMBIENTE")
        print("-" * 80)
        
        # Verificar arquivos de ambiente
        env_files = {
            'config_production.env': 'Configuração produção',
            'config_angoweb.env.example': 'Template Angoweb',
            '.env': 'Ambiente atual'
        }
        
        for env_file, desc in env_files.items():
            env_path = self.base_dir / env_file
            example_path = self.base_dir / f"{env_file}.example"
            
            if env_path.exists() or example_path.exists():
                print(f"  ✅ {env_file}: {desc}")
                
                # Verificar variáveis críticas
                file_to_check = env_path if env_path.exists() else example_path
                try:
                    with open(file_to_check, 'r') as f:
                        content = f.read()
                        
                        critical_vars = [
                            'DATABASE_URL',
                            'REDIS_URL',
                            'SECRET_KEY',
                            'API_FOOTBALL_KEY',
                            'ALLOWED_HOSTS'
                        ]
                        
                        for var in critical_vars:
                            if var in content:
                                print(f"     ✅ {var}")
                            else:
                                print(f"     ⚠️  {var}: Não encontrado")
                
                except Exception as e:
                    print(f"     ⚠️  Erro ao ler: {e}")
                
                self.score += 1
            else:
                print(f"  ❌ {env_file}: Não encontrado")
                self.critical_issues.append(f"Arquivo de ambiente: {env_file}")
            
            self.max_score += 1
        
        print()
    
    def check_static_assets(self):
        """Verifica assets estáticos"""
        print("🎨 12. ASSETS ESTÁTICOS (LOGO E IMAGENS)")
        print("-" * 80)
        
        # Logo
        if (self.base_dir / 'static/images/logo-marabet.svg').exists():
            print(f"  ✅ Logo principal (SVG)")
            self.score += 1
        else:
            print(f"  ⚠️  Logo principal: Não encontrado")
            self.warnings.append("Logo MaraBet não encontrado")
        
        self.max_score += 1
        
        # PWA Icons
        pwa_icons = [72, 96, 128, 144, 152, 192, 384, 512]
        pwa_count = 0
        for size in pwa_icons:
            if (self.base_dir / f'static/images/icon-{size}x{size}.png').exists():
                pwa_count += 1
        
        print(f"  {'✅' if pwa_count >= 6 else '⚠️ '} PWA Icons: {pwa_count}/8")
        if pwa_count >= 6:
            self.score += 1
        else:
            self.warnings.append(f"PWA Icons incompletos: {pwa_count}/8")
        
        self.max_score += 1
        
        # Favicons
        favicons = ['favicon-16x16.png', 'favicon-32x32.png', 'apple-touch-icon.png', 'favicon.ico']
        fav_count = sum(1 for f in favicons if (self.base_dir / f'static/images/{f}').exists())
        
        print(f"  {'✅' if fav_count >= 3 else '⚠️ '} Favicons: {fav_count}/4")
        if fav_count >= 3:
            self.score += 1
        else:
            self.warnings.append(f"Favicons incompletos: {fav_count}/4")
        
        self.max_score += 1
        
        print()
    
    def check_scripts(self):
        """Verifica scripts de automação"""
        print("🔧 13. SCRIPTS DE AUTOMAÇÃO")
        print("-" * 80)
        
        scripts = {
            'setup_angoweb.sh': 'Setup servidor Angola (Linux)',
            'install_docker_windows.py': 'Instalação Docker (Windows)',
            'config_ip.py': 'Configuração IP',
            'test_ip_config.py': 'Teste configuração IP'
        }
        
        for script, desc in scripts.items():
            if (self.base_dir / script).exists():
                print(f"  ✅ {script}: {desc}")
                self.score += 0.5
            else:
                print(f"  ⚠️  {script}: {desc}")
            
            self.max_score += 0.5
        
        print()
    
    def check_deployment_readiness(self):
        """Verifica prontidão para deploy"""
        print("🚀 14. PRONTIDÃO PARA DEPLOY")
        print("-" * 80)
        
        # Nginx config
        nginx_configs = [
            'nginx/nginx-angoweb.conf',
            'nginx.conf',
            'nginx/nginx.conf'
        ]
        
        nginx_found = any((self.base_dir / nc).exists() for nc in nginx_configs)
        if nginx_found:
            print(f"  ✅ Configuração Nginx")
            self.score += 1
        else:
            print(f"  ❌ Configuração Nginx: Não encontrada")
            self.critical_issues.append("Configuração Nginx não encontrada")
        
        self.max_score += 1
        
        # systemd service
        if (self.base_dir / 'marabet.service').exists():
            print(f"  ✅ Arquivo systemd service")
            self.score += 1
        else:
            print(f"  ⚠️  Arquivo systemd service: Não encontrado")
            self.recommendations.append("Criar arquivo systemd service para produção Linux")
        
        self.max_score += 1
        
        # Setup scripts
        if (self.base_dir / 'setup_angoweb.sh').exists():
            print(f"  ✅ Script de setup Angoweb")
            self.score += 1
        else:
            print(f"  ⚠️  Script de setup: Não encontrado")
        
        self.max_score += 1
        
        print()
    
    def check_production_architecture(self):
        """Verifica arquitetura de produção"""
        print("🏗️  15. ARQUITETURA DE PRODUÇÃO")
        print("-" * 80)
        
        arch_docs = [
            'ARQUITETURA_PRODUCAO.md',
            'AMBIENTES_DESENVOLVIMENTO_PRODUCAO.md',
            'ANGOWEB_MIGRATION_GUIDE.md'
        ]
        
        for doc in arch_docs:
            if (self.base_dir / doc).exists():
                print(f"  ✅ {doc}")
                self.score += 1
            else:
                print(f"  ⚠️  {doc}: Não encontrado")
                self.warnings.append(f"Documentação de arquitetura: {doc}")
            
            self.max_score += 1
        
        # Verificar se há documentação sobre Linux exclusivo
        readme_path = self.base_dir / 'README.md'
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Linux' in content and 'produção' in content.lower():
                    print(f"  ✅ README menciona Linux para produção")
                    self.score += 1
                else:
                    print(f"  ⚠️  README: Não menciona claramente Linux produção")
                
                self.max_score += 1
        
        print()
    
    def check_testing(self):
        """Verifica testes"""
        print("🧪 16. TESTES E QUALIDADE")
        print("-" * 80)
        
        # Pasta de testes
        if (self.base_dir / 'tests').exists():
            test_files = list((self.base_dir / 'tests').glob('test_*.py'))
            print(f"  ✅ Pasta tests: {len(test_files)} arquivos de teste")
            self.score += 1
        else:
            print(f"  ⚠️  Pasta tests: Não encontrada")
            self.warnings.append("Pasta de testes não encontrada")
        
        self.max_score += 1
        
        # Load tests
        if (self.base_dir / 'load_tests').exists():
            print(f"  ✅ Testes de carga: Configurados")
            self.score += 1
        else:
            print(f"  ⚠️  Testes de carga: Não encontrados")
        
        self.max_score += 1
        
        # pytest.ini
        if (self.base_dir / 'pytest.ini').exists():
            print(f"  ✅ pytest.ini: Configurado")
            self.score += 0.5
        else:
            print(f"  ⚠️  pytest.ini: Não encontrado")
        
        self.max_score += 0.5
        
        print()
    
    def check_ip_configuration(self):
        """Verifica configuração específica de IP"""
        print("📍 17. CONFIGURAÇÃO DE IP")
        print("-" * 80)
        
        # IP configurado
        if (self.base_dir / 'ip_config.json').exists():
            with open(self.base_dir / 'ip_config.json', 'r') as f:
                config = json.load(f)
                ip = config.get('system_ip', 'Não configurado')
                print(f"  ✅ IP do Sistema: {ip}")
                print(f"  ✅ Configurado em: {config.get('configured_at', 'N/A')}")
                
                # Verificar API whitelist info
                if 'api_whitelist' in config:
                    api_fb = config['api_whitelist'].get('api_football', {})
                    print(f"  ✅ API-Football whitelist: Documentado")
                    print(f"     Dashboard: {api_fb.get('dashboard_url', 'N/A')}")
                
                self.score += 2
        else:
            print(f"  ⚠️  IP não configurado")
            print(f"     Execute: python config_ip.py")
            self.warnings.append("IP do sistema não configurado")
        
        self.max_score += 2
        
        # Instruções de whitelist
        if (self.base_dir / 'IP_WHITELIST_INSTRUCTIONS.txt').exists():
            print(f"  ✅ Instruções de whitelist API-Football")
            self.score += 1
        else:
            print(f"  ⚠️  Instruções de whitelist: Não encontradas")
        
        self.max_score += 1
        
        print()
    
    def generate_report(self):
        """Gera relatório final"""
        print("=" * 80)
        print("📊 RELATÓRIO FINAL")
        print("=" * 80)
        print()
        
        # Score
        percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
        print(f"🏆 SCORE DE PRONTIDÃO: {self.score:.1f}/{self.max_score:.1f} ({percentage:.1f}%)")
        print()
        
        # Status
        if percentage >= 95:
            status = "🟢 EXCELENTE - Pronto para produção"
        elif percentage >= 85:
            status = "🟡 BOM - Pequenos ajustes necessários"
        elif percentage >= 70:
            status = "🟠 REGULAR - Vários ajustes necessários"
        else:
            status = "🔴 CRÍTICO - Não recomendado para produção"
        
        print(f"📈 STATUS: {status}")
        print()
        
        # Issues críticos
        if self.critical_issues:
            print("❌ PROBLEMAS CRÍTICOS:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"  {i}. {issue}")
            print()
        
        # Warnings
        if self.warnings:
            print("⚠️  AVISOS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            print()
        
        # Recomendações
        if self.recommendations:
            print("💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
            print()
        
        # Ambiente recomendado
        print("=" * 80)
        print("🎯 AMBIENTE RECOMENDADO PARA PRODUÇÃO")
        print("=" * 80)
        print()
        print("  Sistema Operacional: 🐧 Ubuntu 22.04 LTS")
        print("  Provedor: Angoweb (Angola)")
        print("  Servidor: VPS 8GB RAM, 4 vCores, 100GB SSD")
        print("  Domínio: marabet.ao")
        print("  SSL: Let's Encrypt (Certbot)")
        print("  Backup: Diário automático")
        print("  Monitoramento: Prometheus + Grafana")
        print()
        
        # Ambiente desenvolvimento
        print("=" * 80)
        print("💻 AMBIENTE DESENVOLVIMENTO LOCAL")
        print("=" * 80)
        print()
        print("  ✅ Windows 10/11: Suportado")
        print("  ✅ macOS 11+: Suportado")
        print("  ✅ Linux: Suportado")
        print()
        print("  Você está em Windows - Pode desenvolver localmente!")
        print("  Para produção, use Linux Ubuntu 22.04 (Angoweb)")
        print()
        
        # Próximos passos
        print("=" * 80)
        print("🚀 PRÓXIMOS PASSOS")
        print("=" * 80)
        print()
        
        if self.critical_issues:
            print("  CRÍTICO - Resolver antes de produção:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"    {i}. {issue}")
            print()
        
        if self.warnings:
            print("  RECOMENDADO - Resolver antes de produção:")
            for i, warning in enumerate(self.warnings[:5], 1):
                print(f"    {i}. {warning}")
            print()
        
        if percentage >= 95:
            print("  ✅ Sistema pronto para produção!")
            print()
            print("  Passos finais:")
            print("    1. Provisionar VPS Linux (Angoweb)")
            print("    2. Executar: bash setup_angoweb.sh")
            print("    3. Configurar domínio marabet.ao")
            print("    4. Deploy: docker compose up -d")
            print("    5. Configurar SSL: certbot --nginx")
            print("    6. Monitorar: Grafana")
        
        print()
    
    def save_report(self):
        """Salva relatório em arquivo"""
        report = {
            'date': datetime.now().isoformat(),
            'score': self.score,
            'max_score': self.max_score,
            'percentage': (self.score / self.max_score * 100) if self.max_score > 0 else 0,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'production_ready': (self.score / self.max_score * 100) >= 95 if self.max_score > 0 else False
        }
        
        with open('production_readiness_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("💾 Relatório salvo em: production_readiness_report.json")
        print()
    
    def run(self):
        """Executa verificação completa"""
        self.print_header()
        
        self.check_essential_files()
        self.check_documentation()
        self.check_docker_setup()
        self.check_database()
        self.check_security()
        self.check_apis()
        self.check_responsive_design()
        self.check_legal_compliance()
        self.check_monitoring()
        self.check_backup_system()
        self.check_environment_config()
        self.check_static_assets()
        self.check_scripts()
        self.check_deployment_readiness()
        self.check_production_architecture()
        self.check_testing()
        self.check_ip_configuration()
        
        self.generate_report()
        self.save_report()

def main():
    checker = ProductionReadinessCheck()
    checker.run()

if __name__ == "__main__":
    main()

