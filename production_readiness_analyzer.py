#!/usr/bin/env python3
"""
Análise de Prontidão para Produção - MaraBet AI
Verifica se o sistema está pronto para uso em produção
"""

import json
import os
import sys
import subprocess
import importlib
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionReadinessAnalyzer:
    """Analisador de prontidão para produção do MaraBet AI"""
    
    def __init__(self):
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'Unknown',
            'components': {},
            'issues': [],
            'recommendations': [],
            'production_score': 0
        }
        
    def analyze_system_components(self):
        """Analisa todos os componentes do sistema"""
        logger.info("🔍 Iniciando análise de componentes do sistema...")
        
        components = [
            'enhanced_predictions_system',
            'interactive_dashboard',
            'concise_alerts',
            'data_collection_system',
            'realtime_monitor',
            'integrated_system',
            'complete_marabetsystem',
            'simple_future_predictions'
        ]
        
        for component in components:
            self.analyze_component(component)
        
        logger.info("✅ Análise de componentes concluída")
    
    def analyze_component(self, component_name: str):
        """Analisa um componente específico"""
        try:
            component_info = {
                'status': 'Unknown',
                'file_exists': False,
                'imports_ok': False,
                'functions_ok': False,
                'issues': [],
                'score': 0
            }
            
            # Verificar se o arquivo existe
            file_path = f"{component_name}.py"
            if os.path.exists(file_path):
                component_info['file_exists'] = True
                component_info['score'] += 25
            else:
                component_info['issues'].append(f"Arquivo {file_path} não encontrado")
                self.analysis_results['issues'].append(f"Componente {component_name}: Arquivo não encontrado")
            
            # Verificar imports
            try:
                if component_info['file_exists']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Verificar imports básicos
                    required_imports = ['import json', 'import requests', 'import datetime']
                    imports_found = sum(1 for imp in required_imports if imp in content)
                    
                    if imports_found >= 2:
                        component_info['imports_ok'] = True
                        component_info['score'] += 25
                    else:
                        component_info['issues'].append("Imports básicos não encontrados")
            except Exception as e:
                component_info['issues'].append(f"Erro ao verificar imports: {e}")
            
            # Verificar funções principais
            try:
                if component_info['file_exists']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar se tem função main
                    if 'def main():' in content or 'if __name__ == "__main__":' in content:
                        component_info['functions_ok'] = True
                        component_info['score'] += 25
                    else:
                        component_info['issues'].append("Função main não encontrada")
            except Exception as e:
                component_info['issues'].append(f"Erro ao verificar funções: {e}")
            
            # Verificar se é executável
            try:
                if component_info['file_exists'] and component_info['imports_ok']:
                    # Tentar executar o arquivo (apenas verificar sintaxe)
                    result = subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        component_info['score'] += 25
                    else:
                        component_info['issues'].append(f"Erro de sintaxe: {result.stderr}")
            except Exception as e:
                component_info['issues'].append(f"Erro ao verificar sintaxe: {e}")
            
            # Determinar status
            if component_info['score'] >= 75:
                component_info['status'] = 'Ready'
            elif component_info['score'] >= 50:
                component_info['status'] = 'Needs Work'
            else:
                component_info['status'] = 'Not Ready'
            
            self.analysis_results['components'][component_name] = component_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar componente {component_name}: {e}")
            self.analysis_results['components'][component_name] = {
                'status': 'Error',
                'file_exists': False,
                'imports_ok': False,
                'functions_ok': False,
                'issues': [f"Erro na análise: {e}"],
                'score': 0
            }
    
    def analyze_dependencies(self):
        """Analisa dependências do sistema"""
        logger.info("🔍 Analisando dependências...")
        
        required_packages = [
            'requests', 'flask', 'sqlite3', 'json', 'datetime', 
            'random', 'logging', 'time', 'os', 'sys'
        ]
        
        dependencies_status = {
            'status': 'Unknown',
            'packages': {},
            'issues': [],
            'score': 0
        }
        
        for package in required_packages:
            try:
                if package in ['json', 'datetime', 'random', 'logging', 'time', 'os', 'sys']:
                    # Módulos built-in
                    dependencies_status['packages'][package] = {
                        'status': 'Available',
                        'version': 'Built-in',
                        'installed': True
                    }
                    dependencies_status['score'] += 10
                else:
                    # Módulos externos
                    try:
                        module = importlib.import_module(package)
                        version = getattr(module, '__version__', 'Unknown')
                        dependencies_status['packages'][package] = {
                            'status': 'Available',
                            'version': version,
                            'installed': True
                        }
                        dependencies_status['score'] += 10
                    except ImportError:
                        dependencies_status['packages'][package] = {
                            'status': 'Missing',
                            'version': 'N/A',
                            'installed': False
                        }
                        dependencies_status['issues'].append(f"Pacote {package} não instalado")
            except Exception as e:
                dependencies_status['packages'][package] = {
                    'status': 'Error',
                    'version': 'N/A',
                    'installed': False
                }
                dependencies_status['issues'].append(f"Erro ao verificar {package}: {e}")
        
        # Determinar status das dependências
        if dependencies_status['score'] >= 80:
            dependencies_status['status'] = 'Ready'
        elif dependencies_status['score'] >= 60:
            dependencies_status['status'] = 'Needs Work'
        else:
            dependencies_status['status'] = 'Not Ready'
        
        self.analysis_results['dependencies'] = dependencies_status
        logger.info("✅ Análise de dependências concluída")
    
    def analyze_configuration(self):
        """Analisa configuração do sistema"""
        logger.info("🔍 Analisando configuração...")
        
        config_status = {
            'status': 'Unknown',
            'files': {},
            'issues': [],
            'score': 0
        }
        
        # Verificar arquivos de configuração
        config_files = [
            'telegram_config.json',
            'config_personal.env',
            'config_production.env',
            'requirements.txt',
            'README.md'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                config_status['files'][config_file] = {
                    'exists': True,
                    'size': os.path.getsize(config_file),
                    'readable': True
                }
                config_status['score'] += 20
            else:
                config_status['files'][config_file] = {
                    'exists': False,
                    'size': 0,
                    'readable': False
                }
                config_status['issues'].append(f"Arquivo de configuração {config_file} não encontrado")
        
        # Verificar configurações específicas
        try:
            # Verificar telegram_config.json
            if os.path.exists('telegram_config.json'):
                with open('telegram_config.json', 'r') as f:
                    telegram_config = json.load(f)
                    if 'telegram_bot_token' in telegram_config and 'telegram_chat_id' in telegram_config:
                        config_status['score'] += 10
                    else:
                        config_status['issues'].append("Configuração do Telegram incompleta")
        except Exception as e:
            config_status['issues'].append(f"Erro ao verificar configuração do Telegram: {e}")
        
        # Determinar status da configuração
        if config_status['score'] >= 80:
            config_status['status'] = 'Ready'
        elif config_status['score'] >= 60:
            config_status['status'] = 'Needs Work'
        else:
            config_status['status'] = 'Not Ready'
        
        self.analysis_results['configuration'] = config_status
        logger.info("✅ Análise de configuração concluída")
    
    def analyze_functionality(self):
        """Analisa funcionalidades do sistema"""
        logger.info("🔍 Analisando funcionalidades...")
        
        functionality_status = {
            'status': 'Unknown',
            'features': {},
            'issues': [],
            'score': 0
        }
        
        # Funcionalidades principais
        features = [
            'Predições de Apostas',
            'Dashboard Interativo',
            'Notificações Telegram',
            'Coleta de Dados',
            'Monitoramento em Tempo Real',
            'Sistema de Alertas',
            'Integração com APIs',
            'Análise de Dados Históricos'
        ]
        
        for feature in features:
            # Verificar se a funcionalidade está implementada
            feature_score = 0
            
            if feature == 'Predições de Apostas':
                if 'enhanced_predictions_system.py' in os.listdir('.'):
                    feature_score += 25
                if 'simple_future_predictions.py' in os.listdir('.'):
                    feature_score += 25
                if 'complete_marabetsystem.py' in os.listdir('.'):
                    feature_score += 25
                if 'test_enhanced_predictions.py' in os.listdir('.'):
                    feature_score += 25
            
            elif feature == 'Dashboard Interativo':
                if 'interactive_dashboard.py' in os.listdir('.'):
                    feature_score += 50
                if 'simple_dashboard.py' in os.listdir('.'):
                    feature_score += 50
            
            elif feature == 'Notificações Telegram':
                if 'concise_alerts.py' in os.listdir('.'):
                    feature_score += 50
                if 'telegram_config.json' in os.listdir('.'):
                    feature_score += 50
            
            elif feature == 'Coleta de Dados':
                if 'data_collection_system.py' in os.listdir('.'):
                    feature_score += 50
                if 'robust_real_data_collector.py' in os.listdir('.'):
                    feature_score += 50
            
            elif feature == 'Monitoramento em Tempo Real':
                if 'realtime_monitor.py' in os.listdir('.'):
                    feature_score += 50
                if 'integrated_system.py' in os.listdir('.'):
                    feature_score += 50
            
            elif feature == 'Sistema de Alertas':
                if 'prediction_alerts_auto.py' in os.listdir('.'):
                    feature_score += 50
                if 'detailed_alerts_professional.py' in os.listdir('.'):
                    feature_score += 50
            
            elif feature == 'Integração com APIs':
                if 'multi_api_football_system.py' in os.listdir('.'):
                    feature_score += 50
                if 'final_integrated_football_system.py' in os.listdir('.'):
                    feature_score += 50
            
            elif feature == 'Análise de Dados Históricos':
                if 'detailed_analysis_final.py' in os.listdir('.'):
                    feature_score += 50
                if 'statistical_analysis.py' in os.listdir('.'):
                    feature_score += 50
            
            functionality_status['features'][feature] = {
                'score': feature_score,
                'status': 'Ready' if feature_score >= 75 else 'Needs Work' if feature_score >= 50 else 'Not Ready'
            }
            
            functionality_status['score'] += feature_score
        
        # Determinar status das funcionalidades
        if functionality_status['score'] >= 600:  # 75% de 800 pontos possíveis
            functionality_status['status'] = 'Ready'
        elif functionality_status['score'] >= 400:  # 50% de 800 pontos possíveis
            functionality_status['status'] = 'Needs Work'
        else:
            functionality_status['status'] = 'Not Ready'
        
        self.analysis_results['functionality'] = functionality_status
        logger.info("✅ Análise de funcionalidades concluída")
    
    def analyze_security(self):
        """Analisa aspectos de segurança"""
        logger.info("🔍 Analisando segurança...")
        
        security_status = {
            'status': 'Unknown',
            'checks': {},
            'issues': [],
            'score': 0
        }
        
        # Verificar se há chaves de API expostas
        api_keys_exposed = False
        try:
            for file in os.listdir('.'):
                if file.endswith('.py'):
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '71b2b62386f2d1275cd3201a73e1e045' in content or '721b0aaec5794327bab715da2abc7a7b' in content:
                            api_keys_exposed = True
                            break
        except Exception as e:
            security_status['issues'].append(f"Erro ao verificar chaves de API: {e}")
        
        if not api_keys_exposed:
            security_status['checks']['api_keys_secure'] = True
            security_status['score'] += 30
        else:
            security_status['checks']['api_keys_secure'] = False
            security_status['issues'].append("Chaves de API expostas no código")
        
        # Verificar se há arquivos de configuração seguros
        if os.path.exists('config_personal.env') and os.path.exists('config_production.env'):
            security_status['checks']['config_files'] = True
            security_status['score'] += 20
        else:
            security_status['checks']['config_files'] = False
            security_status['issues'].append("Arquivos de configuração de ambiente não encontrados")
        
        # Verificar se há tratamento de erros
        error_handling_score = 0
        try:
            for file in os.listdir('.'):
                if file.endswith('.py'):
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'try:' in content and 'except' in content:
                            error_handling_score += 1
        except Exception as e:
            security_status['issues'].append(f"Erro ao verificar tratamento de erros: {e}")
        
        if error_handling_score >= 5:
            security_status['checks']['error_handling'] = True
            security_status['score'] += 25
        else:
            security_status['checks']['error_handling'] = False
            security_status['issues'].append("Tratamento de erros insuficiente")
        
        # Verificar se há logging
        logging_score = 0
        try:
            for file in os.listdir('.'):
                if file.endswith('.py'):
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'logging' in content:
                            logging_score += 1
        except Exception as e:
            security_status['issues'].append(f"Erro ao verificar logging: {e}")
        
        if logging_score >= 5:
            security_status['checks']['logging'] = True
            security_status['score'] += 25
        else:
            security_status['checks']['logging'] = False
            security_status['issues'].append("Sistema de logging insuficiente")
        
        # Determinar status de segurança
        if security_status['score'] >= 80:
            security_status['status'] = 'Ready'
        elif security_status['score'] >= 60:
            security_status['status'] = 'Needs Work'
        else:
            security_status['status'] = 'Not Ready'
        
        self.analysis_results['security'] = security_status
        logger.info("✅ Análise de segurança concluída")
    
    def calculate_production_score(self):
        """Calcula pontuação geral para produção"""
        logger.info("🔍 Calculando pontuação de produção...")
        
        total_score = 0
        max_score = 0
        
        # Pontuação dos componentes
        for component, info in self.analysis_results['components'].items():
            total_score += info['score']
            max_score += 100
        
        # Pontuação das dependências
        if 'dependencies' in self.analysis_results:
            total_score += self.analysis_results['dependencies']['score']
            max_score += 100
        
        # Pontuação da configuração
        if 'configuration' in self.analysis_results:
            total_score += self.analysis_results['configuration']['score']
            max_score += 100
        
        # Pontuação das funcionalidades
        if 'functionality' in self.analysis_results:
            total_score += self.analysis_results['functionality']['score']
            max_score += 800
        
        # Pontuação de segurança
        if 'security' in self.analysis_results:
            total_score += self.analysis_results['security']['score']
            max_score += 100
        
        # Calcular percentual
        if max_score > 0:
            production_score = (total_score / max_score) * 100
        else:
            production_score = 0
        
        self.analysis_results['production_score'] = round(production_score, 2)
        
        # Determinar status geral
        if production_score >= 80:
            self.analysis_results['overall_status'] = 'Ready for Production'
        elif production_score >= 60:
            self.analysis_results['overall_status'] = 'Needs Work'
        else:
            self.analysis_results['overall_status'] = 'Not Ready for Production'
        
        logger.info(f"✅ Pontuação de produção calculada: {production_score:.2f}%")
    
    def generate_recommendations(self):
        """Gera recomendações para produção"""
        logger.info("🔍 Gerando recomendações...")
        
        recommendations = []
        
        # Recomendações baseadas na análise
        if self.analysis_results['production_score'] < 80:
            recommendations.append("Melhorar pontuação geral do sistema para produção")
        
        # Recomendações de segurança
        if 'security' in self.analysis_results:
            if not self.analysis_results['security']['checks'].get('api_keys_secure', False):
                recommendations.append("Mover chaves de API para variáveis de ambiente")
            if not self.analysis_results['security']['checks'].get('config_files', False):
                recommendations.append("Criar arquivos de configuração de ambiente")
            if not self.analysis_results['security']['checks'].get('error_handling', False):
                recommendations.append("Implementar mais tratamento de erros")
            if not self.analysis_results['security']['checks'].get('logging', False):
                recommendations.append("Implementar sistema de logging mais robusto")
        
        # Recomendações de funcionalidades
        if 'functionality' in self.analysis_results:
            for feature, info in self.analysis_results['functionality']['features'].items():
                if info['status'] != 'Ready':
                    recommendations.append(f"Melhorar implementação de {feature}")
        
        # Recomendações de componentes
        for component, info in self.analysis_results['components'].items():
            if info['status'] != 'Ready':
                recommendations.append(f"Corrigir problemas no componente {component}")
        
        self.analysis_results['recommendations'] = recommendations
        logger.info(f"✅ {len(recommendations)} recomendações geradas")
    
    def save_analysis_report(self):
        """Salva relatório de análise"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"production_readiness_report_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório salvo em {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
            return None
    
    def print_analysis_summary(self):
        """Imprime resumo da análise"""
        print("\n" + "="*80)
        print("🎯 MARABET AI - ANÁLISE DE PRONTIDÃO PARA PRODUÇÃO")
        print("="*80)
        
        print(f"\n📊 STATUS GERAL: {self.analysis_results['overall_status']}")
        print(f"📈 PONTUAÇÃO: {self.analysis_results['production_score']:.2f}%")
        print(f"🕐 TIMESTAMP: {self.analysis_results['timestamp']}")
        
        # Resumo dos componentes
        print(f"\n🔧 COMPONENTES ANALISADOS:")
        print("-" * 50)
        for component, info in self.analysis_results['components'].items():
            status_emoji = "✅" if info['status'] == 'Ready' else "⚠️" if info['status'] == 'Needs Work' else "❌"
            print(f"{status_emoji} {component}: {info['status']} ({info['score']}/100)")
        
        # Resumo das funcionalidades
        if 'functionality' in self.analysis_results:
            print(f"\n🎯 FUNCIONALIDADES:")
            print("-" * 50)
            for feature, info in self.analysis_results['functionality']['features'].items():
                status_emoji = "✅" if info['status'] == 'Ready' else "⚠️" if info['status'] == 'Needs Work' else "❌"
                print(f"{status_emoji} {feature}: {info['status']} ({info['score']}/100)")
        
        # Resumo de segurança
        if 'security' in self.analysis_results:
            print(f"\n🔒 SEGURANÇA:")
            print("-" * 50)
            for check, status in self.analysis_results['security']['checks'].items():
                status_emoji = "✅" if status else "❌"
                print(f"{status_emoji} {check}: {'OK' if status else 'NOK'}")
        
        # Problemas encontrados
        if self.analysis_results['issues']:
            print(f"\n⚠️ PROBLEMAS ENCONTRADOS:")
            print("-" * 50)
            for issue in self.analysis_results['issues']:
                print(f"• {issue}")
        
        # Recomendações
        if self.analysis_results['recommendations']:
            print(f"\n💡 RECOMENDAÇÕES:")
            print("-" * 50)
            for i, recommendation in enumerate(self.analysis_results['recommendations'], 1):
                print(f"{i}. {recommendation}")
        
        # Conclusão
        print(f"\n🎯 CONCLUSÃO:")
        print("-" * 50)
        if self.analysis_results['overall_status'] == 'Ready for Production':
            print("✅ O sistema MaraBet AI está PRONTO para produção!")
            print("🚀 Pode ser implantado em ambiente de produção com confiança.")
        elif self.analysis_results['overall_status'] == 'Needs Work':
            print("⚠️ O sistema MaraBet AI precisa de TRABALHOS antes da produção.")
            print("🔧 Implemente as recomendações antes de implantar.")
        else:
            print("❌ O sistema MaraBet AI NÃO está pronto para produção.")
            print("🛠️ Corrija os problemas críticos antes de considerar produção.")
        
        print("\n" + "="*80)
    
    def run_complete_analysis(self):
        """Executa análise completa do sistema"""
        logger.info("🚀 Iniciando análise completa de prontidão para produção...")
        
        try:
            # Analisar componentes
            self.analyze_system_components()
            
            # Analisar dependências
            self.analyze_dependencies()
            
            # Analisar configuração
            self.analyze_configuration()
            
            # Analisar funcionalidades
            self.analyze_functionality()
            
            # Analisar segurança
            self.analyze_security()
            
            # Calcular pontuação de produção
            self.calculate_production_score()
            
            # Gerar recomendações
            self.generate_recommendations()
            
            # Salvar relatório
            report_file = self.save_analysis_report()
            
            # Imprimir resumo
            self.print_analysis_summary()
            
            logger.info("✅ Análise completa concluída")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na análise completa: {e}")
            return False

def main():
    print("🎯 MARABET AI - ANÁLISE DE PRONTIDÃO PARA PRODUÇÃO")
    print("=" * 60)
    
    # Inicializar analisador
    analyzer = ProductionReadinessAnalyzer()
    
    print("🔍 Iniciando análise completa do sistema...")
    
    # Executar análise completa
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n✅ ANÁLISE COMPLETA FINALIZADA!")
        print("📊 Relatório detalhado salvo em arquivo JSON")
    else:
        print("\n❌ ERRO NA ANÁLISE!")
        print("🔧 Verifique os logs para mais detalhes")

if __name__ == "__main__":
    main()
