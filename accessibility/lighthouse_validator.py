"""
Validador Lighthouse - MaraBet AI
Validação automática de acessibilidade e performance usando Lighthouse
"""

import subprocess
import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile
import webbrowser

logger = logging.getLogger(__name__)

@dataclass
class LighthouseResult:
    """Resultado da validação Lighthouse"""
    url: str
    accessibility_score: float
    performance_score: float
    best_practices_score: float
    seo_score: float
    pwa_score: float
    timestamp: datetime
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    passed: bool

@dataclass
class AccessibilityAudit:
    """Auditoria de acessibilidade"""
    total_checks: int
    passed_checks: int
    failed_checks: int
    score: float
    critical_issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[str]

class LighthouseValidator:
    """
    Validador de acessibilidade e performance usando Lighthouse
    """
    
    def __init__(self, 
                 lighthouse_path: Optional[str] = None,
                 chrome_path: Optional[str] = None,
                 output_dir: str = "accessibility/reports"):
        """
        Inicializa o validador Lighthouse
        
        Args:
            lighthouse_path: Caminho para o Lighthouse CLI
            chrome_path: Caminho para o Chrome/Chromium
            output_dir: Diretório para relatórios
        """
        self.lighthouse_path = lighthouse_path or "lighthouse"
        self.chrome_path = chrome_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("LighthouseValidator inicializado")
    
    def validate_dashboard(self, 
                          url: str,
                          categories: List[str] = None,
                          output_format: str = "json",
                          generate_html: bool = True) -> LighthouseResult:
        """
        Valida dashboard usando Lighthouse
        
        Args:
            url: URL do dashboard
            categories: Categorias para validar
            output_format: Formato de saída (json, html)
            generate_html: Se deve gerar relatório HTML
            
        Returns:
            Resultado da validação
        """
        try:
            logger.info(f"🔍 Validando dashboard: {url}")
            
            # Configurar categorias
            if categories is None:
                categories = ["accessibility", "performance", "best-practices", "seo"]
            
            # Preparar comando Lighthouse
            cmd = self._build_lighthouse_command(url, categories, output_format)
            
            # Executar Lighthouse
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"❌ Erro no Lighthouse: {result.stderr}")
                return self._empty_lighthouse_result(url)
            
            # Processar resultado
            lighthouse_data = json.loads(result.stdout)
            return self._process_lighthouse_result(url, lighthouse_data, generate_html)
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout na validação Lighthouse")
            return self._empty_lighthouse_result(url)
        except Exception as e:
            logger.error(f"❌ Erro na validação Lighthouse: {e}")
            return self._empty_lighthouse_result(url)
    
    def _build_lighthouse_command(self, 
                                 url: str, 
                                 categories: List[str], 
                                 output_format: str) -> List[str]:
        """Constrói comando Lighthouse"""
        cmd = [
            self.lighthouse_path,
            url,
            "--output=" + output_format,
            "--output-path=" + os.path.join(self.output_dir, f"lighthouse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "--chrome-flags=--headless",
            "--quiet"
        ]
        
        # Adicionar categorias
        for category in categories:
            cmd.append(f"--only-categories={category}")
        
        # Adicionar caminho do Chrome se especificado
        if self.chrome_path:
            cmd.extend(["--chrome-flags", f"--chrome-path={self.chrome_path}"])
        
        return cmd
    
    def _process_lighthouse_result(self, 
                                 url: str, 
                                 data: Dict[str, Any],
                                 generate_html: bool) -> LighthouseResult:
        """Processa resultado do Lighthouse"""
        try:
            # Extrair scores
            categories = data.get("categories", {})
            accessibility_score = categories.get("accessibility", {}).get("score", 0) * 100
            performance_score = categories.get("performance", {}).get("score", 0) * 100
            best_practices_score = categories.get("best-practices", {}).get("score", 0) * 100
            seo_score = categories.get("seo", {}).get("score", 0) * 100
            pwa_score = categories.get("pwa", {}).get("score", 0) * 100
            
            # Extrair auditorias
            audits = data.get("audits", {})
            issues = self._extract_accessibility_issues(audits)
            recommendations = self._generate_recommendations(accessibility_score, issues)
            
            # Verificar se passou (acessibilidade >= 90)
            passed = accessibility_score >= 90
            
            result = LighthouseResult(
                url=url,
                accessibility_score=accessibility_score,
                performance_score=performance_score,
                best_practices_score=best_practices_score,
                seo_score=seo_score,
                pwa_score=pwa_score,
                timestamp=datetime.now(),
                issues=issues,
                recommendations=recommendations,
                passed=passed
            )
            
            # Salvar resultado
            self._save_lighthouse_result(result)
            
            # Gerar relatório HTML se solicitado
            if generate_html:
                self._generate_html_report(result)
            
            logger.info(f"✅ Validação concluída - Acessibilidade: {accessibility_score:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado: {e}")
            return self._empty_lighthouse_result(url)
    
    def _extract_accessibility_issues(self, audits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai problemas de acessibilidade"""
        issues = []
        
        for audit_id, audit_data in audits.items():
            if audit_data.get("score") is not None and audit_data["score"] < 1:
                issue = {
                    "id": audit_id,
                    "title": audit_data.get("title", ""),
                    "description": audit_data.get("description", ""),
                    "score": audit_data.get("score", 0),
                    "severity": self._determine_severity(audit_data),
                    "details": audit_data.get("details", {}),
                    "warnings": audit_data.get("warnings", [])
                }
                issues.append(issue)
        
        return issues
    
    def _determine_severity(self, audit_data: Dict[str, Any]) -> str:
        """Determina severidade do problema"""
        score = audit_data.get("score", 0)
        
        if score is None:
            return "info"
        elif score < 0.5:
            return "critical"
        elif score < 0.8:
            return "warning"
        else:
            return "info"
    
    def _generate_recommendations(self, 
                                 accessibility_score: float,
                                 issues: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas no score e problemas"""
        recommendations = []
        
        # Recomendações baseadas no score
        if accessibility_score < 50:
            recommendations.append("🚨 Acessibilidade crítica - Revisão urgente necessária")
        elif accessibility_score < 70:
            recommendations.append("⚠️ Acessibilidade baixa - Melhorias significativas necessárias")
        elif accessibility_score < 90:
            recommendations.append("📈 Acessibilidade boa - Pequenas melhorias necessárias")
        else:
            recommendations.append("✅ Excelente acessibilidade - Manter padrões atuais")
        
        # Recomendações baseadas em problemas específicos
        critical_issues = [issue for issue in issues if issue["severity"] == "critical"]
        warning_issues = [issue for issue in issues if issue["severity"] == "warning"]
        
        if critical_issues:
            recommendations.append(f"🔴 {len(critical_issues)} problemas críticos encontrados - Resolver imediatamente")
        
        if warning_issues:
            recommendations.append(f"🟡 {len(warning_issues)} avisos encontrados - Revisar e corrigir")
        
        # Recomendações específicas por tipo de problema
        problem_types = set(issue["id"] for issue in issues)
        
        if "color-contrast" in problem_types:
            recommendations.append("🎨 Melhorar contraste de cores para melhor legibilidade")
        
        if "alt-text" in problem_types:
            recommendations.append("🖼️ Adicionar texto alternativo para imagens")
        
        if "keyboard-navigation" in problem_types:
            recommendations.append("⌨️ Melhorar navegação por teclado")
        
        if "aria-labels" in problem_types:
            recommendations.append("🏷️ Adicionar labels ARIA para elementos interativos")
        
        if "heading-structure" in problem_types:
            recommendations.append("📝 Melhorar estrutura de cabeçalhos")
        
        return recommendations
    
    def _save_lighthouse_result(self, result: LighthouseResult):
        """Salva resultado do Lighthouse"""
        try:
            filename = f"lighthouse_result_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Converter para dicionário
            result_dict = {
                "url": result.url,
                "accessibility_score": result.accessibility_score,
                "performance_score": result.performance_score,
                "best_practices_score": result.best_practices_score,
                "seo_score": result.seo_score,
                "pwa_score": result.pwa_score,
                "timestamp": result.timestamp.isoformat(),
                "issues": result.issues,
                "recommendations": result.recommendations,
                "passed": result.passed
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Resultado salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultado: {e}")
    
    def _generate_html_report(self, result: LighthouseResult):
        """Gera relatório HTML"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Lighthouse - MaraBet AI</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        .scores {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .score-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .score-card h3 {{
            margin: 0 0 10px 0;
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .score-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 0;
        }}
        .issues {{
            margin-bottom: 40px;
        }}
        .issue {{
            background: #f8f9fa;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 0 5px 5px 0;
        }}
        .issue.warning {{
            border-left-color: #ffc107;
        }}
        .issue.info {{
            border-left-color: #17a2b8;
        }}
        .recommendations {{
            background: #e8f5e8;
            padding: 20px;
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
        .status {{
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .status.passed {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.failed {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Relatório Lighthouse - MaraBet AI</h1>
            <p>Validação de Acessibilidade e Performance</p>
            <p>URL: {result.url}</p>
            <p>Data: {result.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="status {'passed' if result.passed else 'failed'}">
            <h2>{'✅ APROVADO' if result.passed else '❌ REPROVADO'}</h2>
            <p>Acessibilidade: {result.accessibility_score:.1f}% {'(≥ 90%)' if result.passed else '(< 90%)'}</p>
        </div>
        
        <div class="scores">
            <div class="score-card">
                <h3>Acessibilidade</h3>
                <div class="value">{result.accessibility_score:.1f}%</div>
            </div>
            <div class="score-card">
                <h3>Performance</h3>
                <div class="value">{result.performance_score:.1f}%</div>
            </div>
            <div class="score-card">
                <h3>Melhores Práticas</h3>
                <div class="value">{result.best_practices_score:.1f}%</div>
            </div>
            <div class="score-card">
                <h3>SEO</h3>
                <div class="value">{result.seo_score:.1f}%</div>
            </div>
        </div>
        
        <div class="issues">
            <h2>Problemas Encontrados ({len(result.issues)})</h2>
            {self._generate_issues_html(result.issues)}
        </div>
        
        <div class="recommendations">
            <h3>Recomendações</h3>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in result.recommendations)}
            </ul>
        </div>
    </div>
</body>
</html>
            """
            
            filename = f"lighthouse_report_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Relatório HTML gerado em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório HTML: {e}")
    
    def _generate_issues_html(self, issues: List[Dict[str, Any]]) -> str:
        """Gera HTML para problemas"""
        if not issues:
            return "<p>Nenhum problema encontrado! 🎉</p>"
        
        html = ""
        for issue in issues:
            severity_class = issue["severity"]
            html += f"""
            <div class="issue {severity_class}">
                <h4>{issue['title']}</h4>
                <p>{issue['description']}</p>
                <p><strong>Severidade:</strong> {issue['severity'].upper()}</p>
                <p><strong>Score:</strong> {issue['score']:.2f}</p>
            </div>
            """
        
        return html
    
    def validate_multiple_urls(self, 
                              urls: List[str],
                              categories: List[str] = None) -> List[LighthouseResult]:
        """Valida múltiplas URLs"""
        results = []
        
        for url in urls:
            try:
                result = self.validate_dashboard(url, categories)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Erro ao validar {url}: {e}")
                results.append(self._empty_lighthouse_result(url))
        
        return results
    
    def generate_summary_report(self, results: List[LighthouseResult]) -> Dict[str, Any]:
        """Gera relatório resumo de múltiplas validações"""
        try:
            if not results:
                return {}
            
            total_urls = len(results)
            passed_urls = sum(1 for r in results if r.passed)
            failed_urls = total_urls - passed_urls
            
            avg_accessibility = sum(r.accessibility_score for r in results) / total_urls
            avg_performance = sum(r.performance_score for r in results) / total_urls
            avg_best_practices = sum(r.best_practices_score for r in results) / total_urls
            avg_seo = sum(r.seo_score for r in results) / total_urls
            
            all_issues = []
            for result in results:
                all_issues.extend(result.issues)
            
            critical_issues = [i for i in all_issues if i["severity"] == "critical"]
            warning_issues = [i for i in all_issues if i["severity"] == "warning"]
            
            return {
                "summary": {
                    "total_urls": total_urls,
                    "passed_urls": passed_urls,
                    "failed_urls": failed_urls,
                    "pass_rate": (passed_urls / total_urls) * 100
                },
                "average_scores": {
                    "accessibility": avg_accessibility,
                    "performance": avg_performance,
                    "best_practices": avg_best_practices,
                    "seo": avg_seo
                },
                "issues_summary": {
                    "total_issues": len(all_issues),
                    "critical_issues": len(critical_issues),
                    "warning_issues": len(warning_issues)
                },
                "recommendations": self._generate_summary_recommendations(
                    avg_accessibility, len(critical_issues), len(warning_issues)
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório resumo: {e}")
            return {}
    
    def _generate_summary_recommendations(self, 
                                        avg_accessibility: float,
                                        critical_issues: int,
                                        warning_issues: int) -> List[str]:
        """Gera recomendações para o resumo"""
        recommendations = []
        
        if avg_accessibility >= 90:
            recommendations.append("🎉 Excelente acessibilidade média - Manter padrões atuais")
        elif avg_accessibility >= 70:
            recommendations.append("📈 Boa acessibilidade média - Pequenas melhorias necessárias")
        else:
            recommendations.append("⚠️ Acessibilidade média baixa - Melhorias significativas necessárias")
        
        if critical_issues > 0:
            recommendations.append(f"🚨 {critical_issues} problemas críticos encontrados - Resolver imediatamente")
        
        if warning_issues > 0:
            recommendations.append(f"🟡 {warning_issues} avisos encontrados - Revisar e corrigir")
        
        return recommendations
    
    def _empty_lighthouse_result(self, url: str) -> LighthouseResult:
        """Retorna resultado vazio"""
        return LighthouseResult(
            url=url,
            accessibility_score=0.0,
            performance_score=0.0,
            best_practices_score=0.0,
            seo_score=0.0,
            pwa_score=0.0,
            timestamp=datetime.now(),
            issues=[],
            recommendations=[],
            passed=False
        )
