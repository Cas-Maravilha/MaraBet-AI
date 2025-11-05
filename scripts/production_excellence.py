#!/usr/bin/env python3
"""
Excelência Operacional - MaraBet AI
Script principal para atingir excelência operacional em produção
"""

import os
import sys
import argparse
import logging
import json
import time
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security import SecurityHardener
from performance import PerformanceValidator
from infrastructure import ScalabilityManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionExcellence:
    """
    Sistema de Excelência Operacional para MaraBet AI
    Integra hardening de segurança, validação de performance e escalabilidade
    """
    
    def __init__(self):
        """Inicializa o sistema de excelência operacional"""
        self.security_hardener = SecurityHardener()
        self.performance_validator = PerformanceValidator()
        self.scalability_manager = ScalabilityManager()
        
        logger.info("🚀 Sistema de Excelência Operacional inicializado")
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Executa auditoria completa de excelência operacional
        
        Returns:
            Relatório completo
        """
        try:
            logger.info("🔍 Iniciando auditoria completa de excelência operacional...")
            
            start_time = time.time()
            
            # 1. Auditoria de Segurança
            logger.info("🔐 Executando auditoria de segurança...")
            security_report = self.security_hardener.run_security_audit()
            
            # 2. Validação de Performance
            logger.info("⚡ Executando validação de performance...")
            performance_report = self.performance_validator.run_load_test()
            
            # 3. Análise de Escalabilidade
            logger.info("📈 Executando análise de escalabilidade...")
            scalability_metrics = self.scalability_manager.collect_metrics()
            scaling_decision = self.scalability_manager.make_scaling_decision(scalability_metrics)
            
            # 4. Correção de Documentação
            logger.info("📝 Executando correção de documentação...")
            from scripts.fix_documentation import DocumentationFixer
            doc_fixer = DocumentationFixer()
            doc_report = doc_fixer.scan_project()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Compilar relatório final
            final_report = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "security": {
                    "overall_score": security_report.overall_score,
                    "vulnerabilities_found": security_report.vulnerabilities_found,
                    "critical_issues": security_report.critical_issues,
                    "high_issues": security_report.high_issues,
                    "medium_issues": security_report.medium_issues,
                    "low_issues": security_report.low_issues,
                    "passed": security_report.overall_score >= 80
                },
                "performance": {
                    "test_name": performance_report.test_name,
                    "duration": performance_report.duration,
                    "total_requests": performance_report.total_requests,
                    "successful_requests": performance_report.successful_requests,
                    "failed_requests": performance_report.failed_requests,
                    "average_response_time": performance_report.average_response_time,
                    "p95_response_time": performance_report.p95_response_time,
                    "p99_response_time": performance_report.p99_response_time,
                    "throughput": performance_report.throughput,
                    "error_rate": performance_report.error_rate,
                    "cpu_usage_avg": performance_report.cpu_usage_avg,
                    "memory_usage_avg": performance_report.memory_usage_avg,
                    "passed": performance_report.passed
                },
                "scalability": {
                    "current_instances": scalability_metrics.active_instances,
                    "cpu_usage": scalability_metrics.cpu_usage,
                    "memory_usage": scalability_metrics.memory_usage,
                    "response_time": scalability_metrics.response_time,
                    "throughput": scalability_metrics.throughput,
                    "scaling_decision": {
                        "action": scaling_decision.action,
                        "reason": scaling_decision.reason,
                        "confidence": scaling_decision.confidence
                    }
                },
                "documentation": {
                    "total_issues": doc_report.total_issues,
                    "critical_issues": doc_report.critical_issues,
                    "high_issues": doc_report.high_issues,
                    "medium_issues": doc_report.medium_issues,
                    "low_issues": doc_report.low_issues
                },
                "overall_score": self._calculate_overall_score(
                    security_report, performance_report, doc_report
                ),
                "recommendations": self._generate_final_recommendations(
                    security_report, performance_report, doc_report, scaling_decision
                )
            }
            
            # Salvar relatório
            self._save_final_report(final_report)
            
            logger.info(f"✅ Auditoria completa concluída em {duration:.2f} segundos")
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Erro na auditoria completa: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_score(self, security_report, performance_report, doc_report) -> float:
        """Calcula score geral de excelência operacional"""
        try:
            # Pesos para cada área
            security_weight = 0.4
            performance_weight = 0.3
            documentation_weight = 0.2
            scalability_weight = 0.1
            
            # Scores individuais
            security_score = security_report.overall_score
            performance_score = 100 if performance_report.passed else 50
            doc_score = max(0, 100 - (doc_report.total_issues * 2))  # Penalizar por problemas
            scalability_score = 80  # Score base para escalabilidade
            
            # Score ponderado
            overall_score = (
                security_score * security_weight +
                performance_score * performance_weight +
                doc_score * documentation_weight +
                scalability_score * scalability_weight
            )
            
            return min(100, max(0, overall_score))
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular score geral: {e}")
            return 0.0
    
    def _generate_final_recommendations(self, security_report, performance_report, 
                                      doc_report, scaling_decision) -> List[str]:
        """Gera recomendações finais"""
        recommendations = []
        
        # Recomendações de segurança
        if security_report.overall_score < 80:
            recommendations.append("🔐 Melhorar segurança - Score atual muito baixo")
        
        if security_report.critical_issues > 0:
            recommendations.append(f"🚨 Resolver {security_report.critical_issues} problemas críticos de segurança")
        
        # Recomendações de performance
        if not performance_report.passed:
            recommendations.append("⚡ Otimizar performance - Teste de carga falhou")
        
        if performance_report.average_response_time > 2.0:
            recommendations.append("🎯 Reduzir tempo de resposta médio")
        
        if performance_report.error_rate > 0.01:
            recommendations.append("🛡️ Reduzir taxa de erro")
        
        # Recomendações de escalabilidade
        if scaling_decision.action == "scale_up":
            recommendations.append(f"📈 Escalar horizontalmente - {scaling_decision.reason}")
        elif scaling_decision.action == "scale_down":
            recommendations.append(f"📉 Otimizar recursos - {scaling_decision.reason}")
        
        # Recomendações de documentação
        if doc_report.total_issues > 50:
            recommendations.append("📝 Melhorar documentação - Muitos problemas encontrados")
        
        if doc_report.critical_issues > 0:
            recommendations.append(f"🔴 Resolver {doc_report.critical_issues} problemas críticos de documentação")
        
        # Recomendações gerais
        recommendations.extend([
            "🔄 Implementar monitoramento contínuo",
            "📊 Estabelecer métricas de SLA",
            "🛡️ Implementar backup e disaster recovery",
            "👥 Treinar equipe em operações",
            "📋 Estabelecer processos de deploy",
            "🔍 Implementar alertas proativos"
        ])
        
        return recommendations
    
    def _save_final_report(self, report: Dict[str, Any]):
        """Salva relatório final"""
        try:
            filename = f"production_excellence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("reports", filename)
            
            os.makedirs("reports", exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório final salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório final: {e}")
    
    def generate_excellence_dashboard(self, report: Dict[str, Any]) -> str:
        """Gera dashboard de excelência operacional"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Excelência Operacional - MaraBet AI</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .overall-score {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin: 30px 0;
        }}
        .score-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            font-weight: bold;
            color: white;
            background: {'#28a745' if report['overall_score'] >= 80 else '#ffc107' if report['overall_score'] >= 60 else '#dc3545'};
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 40px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid #667eea;
        }}
        .metric-card.security {{
            border-left-color: #dc3545;
        }}
        .metric-card.performance {{
            border-left-color: #28a745;
        }}
        .metric-card.scalability {{
            border-left-color: #17a2b8;
        }}
        .metric-card.documentation {{
            border-left-color: #ffc107;
        }}
        .metric-card h3 {{
            margin-top: 0;
            color: #333;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .status {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status.passed {{
            background: #d4edda;
            color: #155724;
        }}
        .status.failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        .recommendations {{
            background: #e8f5e8;
            padding: 30px;
            margin: 20px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }}
        .recommendations h3 {{
            color: #28a745;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard de Excelência Operacional</h1>
            <p>MaraBet AI - Relatório de Produção</p>
            <p>Data: {datetime.fromisoformat(report['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="overall-score">
            <div class="score-circle">
                {report['overall_score']:.0f}%
            </div>
            <div>
                <h2>Score Geral de Excelência</h2>
                <p>{'Excelente' if report['overall_score'] >= 80 else 'Bom' if report['overall_score'] >= 60 else 'Necessita Melhorias'}</p>
                <p>Duração da Auditoria: {report['duration_seconds']:.1f} segundos</p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card security">
                <h3>🔐 Segurança</h3>
                <div class="metric-value">{report['security']['overall_score']:.1f}%</div>
                <p>Vulnerabilidades: {report['security']['vulnerabilities_found']}</p>
                <p>Críticas: {report['security']['critical_issues']}</p>
                <p>Alta: {report['security']['high_issues']}</p>
                <span class="status {'passed' if report['security']['passed'] else 'failed'}">
                    {'✅ APROVADO' if report['security']['passed'] else '❌ REPROVADO'}
                </span>
            </div>
            
            <div class="metric-card performance">
                <h3>⚡ Performance</h3>
                <div class="metric-value">{report['performance']['throughput']:.1f} req/s</div>
                <p>Response Time: {report['performance']['average_response_time']:.2f}s</p>
                <p>P95: {report['performance']['p95_response_time']:.2f}s</p>
                <p>Error Rate: {report['performance']['error_rate']:.2f}%</p>
                <span class="status {'passed' if report['performance']['passed'] else 'failed'}">
                    {'✅ APROVADO' if report['performance']['passed'] else '❌ REPROVADO'}
                </span>
            </div>
            
            <div class="metric-card scalability">
                <h3>📈 Escalabilidade</h3>
                <div class="metric-value">{report['scalability']['current_instances']}</div>
                <p>Instâncias Ativas</p>
                <p>CPU: {report['scalability']['cpu_usage']:.1f}%</p>
                <p>Memória: {report['scalability']['memory_usage']:.1f}%</p>
                <p><strong>Ação:</strong> {report['scalability']['scaling_decision']['action']}</p>
            </div>
            
            <div class="metric-card documentation">
                <h3>📝 Documentação</h3>
                <div class="metric-value">{report['documentation']['total_issues']}</div>
                <p>Problemas Encontrados</p>
                <p>Críticos: {report['documentation']['critical_issues']}</p>
                <p>Alta: {report['documentation']['high_issues']}</p>
                <p>Média: {report['documentation']['medium_issues']}</p>
            </div>
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendações para Excelência Operacional</h3>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in report['recommendations'])}
            </ul>
        </div>
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dashboard: {e}")
            return ""

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Excelência Operacional - MaraBet AI")
    parser.add_argument("--audit", action="store_true", help="Executar auditoria completa")
    parser.add_argument("--security", action="store_true", help="Executar apenas auditoria de segurança")
    parser.add_argument("--performance", action="store_true", help="Executar apenas validação de performance")
    parser.add_argument("--scalability", action="store_true", help="Executar apenas análise de escalabilidade")
    parser.add_argument("--documentation", action="store_true", help="Executar apenas correção de documentação")
    parser.add_argument("--dashboard", action="store_true", help="Gerar dashboard")
    parser.add_argument("--output", default="production_excellence_dashboard.html", help="Arquivo de saída do dashboard")
    
    args = parser.parse_args()
    
    try:
        excellence = ProductionExcellence()
        
        if args.audit or (not any([args.security, args.performance, args.scalability, args.documentation])):
            # Auditoria completa
            report = excellence.run_comprehensive_audit()
            
            if args.dashboard:
                html_content = excellence.generate_excellence_dashboard(report)
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"📊 Dashboard gerado: {args.output}")
            
            print(f"🎯 Score Geral: {report['overall_score']:.1f}%")
            print(f"🔐 Segurança: {report['security']['overall_score']:.1f}%")
            print(f"⚡ Performance: {'✅' if report['performance']['passed'] else '❌'}")
            print(f"📈 Escalabilidade: {report['scalability']['current_instances']} instâncias")
            print(f"📝 Documentação: {report['documentation']['total_issues']} problemas")
            
        else:
            # Executar componentes específicos
            if args.security:
                print("🔐 Executando auditoria de segurança...")
                security_report = excellence.security_hardener.run_security_audit()
                print(f"Score de segurança: {security_report.overall_score:.1f}%")
            
            if args.performance:
                print("⚡ Executando validação de performance...")
                performance_report = excellence.performance_validator.run_load_test()
                print(f"Throughput: {performance_report.throughput:.1f} req/s")
                print(f"Response Time: {performance_report.average_response_time:.2f}s")
            
            if args.scalability:
                print("📈 Executando análise de escalabilidade...")
                metrics = excellence.scalability_manager.collect_metrics()
                decision = excellence.scalability_manager.make_scaling_decision(metrics)
                print(f"Instâncias ativas: {metrics.active_instances}")
                print(f"Decisão: {decision.action} - {decision.reason}")
            
            if args.documentation:
                print("📝 Executando correção de documentação...")
                from scripts.fix_documentation import DocumentationFixer
                doc_fixer = DocumentationFixer()
                doc_report = doc_fixer.scan_project()
                print(f"Problemas encontrados: {doc_report.total_issues}")
        
        print("✅ Excelência operacional concluída!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Operação interrompida pelo usuário")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
