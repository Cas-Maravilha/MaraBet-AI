"""
Verificador de Acessibilidade - MaraBet AI
Verificação automática de acessibilidade web
"""

import re
import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class AccessibilityIssue:
    """Problema de acessibilidade"""
    type: str
    severity: str
    element: str
    message: str
    suggestion: str
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class AccessibilityReport:
    """Relatório de acessibilidade"""
    url: str
    timestamp: datetime
    total_issues: int
    critical_issues: int
    warning_issues: int
    info_issues: int
    score: float
    issues: List[AccessibilityIssue]
    recommendations: List[str]
    passed: bool

class AccessibilityChecker:
    """
    Verificador de acessibilidade para MaraBet AI
    Verifica conformidade com WCAG 2.1 e outras diretrizes
    """
    
    def __init__(self, output_dir: str = "accessibility/audits"):
        """
        Inicializa o verificador de acessibilidade
        
        Args:
            output_dir: Diretório para relatórios de auditoria
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Regras de acessibilidade
        self.rules = self._load_accessibility_rules()
        
        logger.info("AccessibilityChecker inicializado")
    
    def _load_accessibility_rules(self) -> Dict[str, Dict[str, Any]]:
        """Carrega regras de acessibilidade"""
        return {
            "alt_text": {
                "pattern": r'<img[^>]*(?!alt=)[^>]*>',
                "severity": "critical",
                "message": "Imagem sem texto alternativo",
                "suggestion": "Adicione o atributo alt com descrição da imagem"
            },
            "heading_structure": {
                "pattern": r'<h([1-6])[^>]*>',
                "severity": "warning",
                "message": "Verificar estrutura de cabeçalhos",
                "suggestion": "Use h1 para título principal, h2-h6 para subtítulos em ordem"
            },
            "form_labels": {
                "pattern": r'<input[^>]*(?!aria-label)[^>]*(?!id=)[^>]*>',
                "severity": "critical",
                "message": "Input sem label associado",
                "suggestion": "Use <label> ou aria-label para descrever o input"
            },
            "color_contrast": {
                "pattern": r'color:\s*#[0-9a-fA-F]{3,6}',
                "severity": "warning",
                "message": "Verificar contraste de cores",
                "suggestion": "Use ferramentas para verificar contraste mínimo de 4.5:1"
            },
            "keyboard_navigation": {
                "pattern": r'<a[^>]*(?!tabindex)[^>]*>',
                "severity": "info",
                "message": "Verificar navegação por teclado",
                "suggestion": "Teste navegação usando apenas Tab e Enter"
            },
            "aria_attributes": {
                "pattern": r'<[^>]*(role|aria-)[^>]*>',
                "severity": "info",
                "message": "Atributos ARIA encontrados",
                "suggestion": "Verifique se os atributos ARIA estão corretos"
            },
            "focus_indicators": {
                "pattern": r':focus\s*\{[^}]*\}',
                "severity": "warning",
                "message": "Indicadores de foco",
                "suggestion": "Certifique-se de que elementos focáveis têm indicadores visuais"
            },
            "skip_links": {
                "pattern": r'<a[^>]*href=["\']#main["\'][^>]*>',
                "severity": "info",
                "message": "Link de pular conteúdo",
                "suggestion": "Adicione link para pular para o conteúdo principal"
            }
        }
    
    def check_url(self, url: str) -> AccessibilityReport:
        """
        Verifica acessibilidade de uma URL
        
        Args:
            url: URL para verificar
            
        Returns:
            Relatório de acessibilidade
        """
        try:
            logger.info(f"🔍 Verificando acessibilidade: {url}")
            
            # Obter conteúdo da página
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Analisar HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = str(soup)
            
            # Verificar regras
            issues = self._check_html_content(html_content, soup)
            
            # Calcular score
            score = self._calculate_accessibility_score(issues)
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(issues, score)
            
            # Criar relatório
            report = AccessibilityReport(
                url=url,
                timestamp=datetime.now(),
                total_issues=len(issues),
                critical_issues=len([i for i in issues if i.severity == "critical"]),
                warning_issues=len([i for i in issues if i.severity == "warning"]),
                info_issues=len([i for i in issues if i.severity == "info"]),
                score=score,
                issues=issues,
                recommendations=recommendations,
                passed=score >= 90
            )
            
            # Salvar relatório
            self._save_report(report)
            
            logger.info(f"✅ Verificação concluída - Score: {score:.1f}%")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")
            return self._empty_report(url)
    
    def check_html_file(self, file_path: str) -> AccessibilityReport:
        """
        Verifica acessibilidade de arquivo HTML
        
        Args:
            file_path: Caminho do arquivo HTML
            
        Returns:
            Relatório de acessibilidade
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            issues = self._check_html_content(html_content, soup)
            
            score = self._calculate_accessibility_score(issues)
            recommendations = self._generate_recommendations(issues, score)
            
            report = AccessibilityReport(
                url=f"file://{file_path}",
                timestamp=datetime.now(),
                total_issues=len(issues),
                critical_issues=len([i for i in issues if i.severity == "critical"]),
                warning_issues=len([i for i in issues if i.severity == "warning"]),
                info_issues=len([i for i in issues if i.severity == "info"]),
                score=score,
                issues=issues,
                recommendations=recommendations,
                passed=score >= 90
            )
            
            self._save_report(report)
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar arquivo: {e}")
            return self._empty_report(f"file://{file_path}")
    
    def _check_html_content(self, html_content: str, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Verifica conteúdo HTML contra regras de acessibilidade"""
        issues = []
        
        # Verificar regras básicas
        for rule_name, rule in self.rules.items():
            matches = re.finditer(rule["pattern"], html_content, re.IGNORECASE)
            for match in matches:
                issue = AccessibilityIssue(
                    type=rule_name,
                    severity=rule["severity"],
                    element=match.group(0),
                    message=rule["message"],
                    suggestion=rule["suggestion"],
                    line=self._get_line_number(html_content, match.start())
                )
                issues.append(issue)
        
        # Verificações específicas
        issues.extend(self._check_images(soup))
        issues.extend(self._check_forms(soup))
        issues.extend(self._check_headings(soup))
        issues.extend(self._check_links(soup))
        issues.extend(self._check_tables(soup))
        issues.extend(self._check_colors(html_content))
        
        return issues
    
    def _check_images(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Verifica acessibilidade de imagens"""
        issues = []
        
        for img in soup.find_all('img'):
            if not img.get('alt'):
                issues.append(AccessibilityIssue(
                    type="image_alt",
                    severity="critical",
                    element=str(img),
                    message="Imagem sem texto alternativo",
                    suggestion="Adicione o atributo alt com descrição da imagem"
                ))
            elif img.get('alt') == "":
                issues.append(AccessibilityIssue(
                    type="image_alt_empty",
                    severity="warning",
                    element=str(img),
                    message="Imagem com alt vazio (decorativa)",
                    suggestion="Se a imagem é decorativa, use alt=''"
                ))
        
        return issues
    
    def _check_forms(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Verifica acessibilidade de formulários"""
        issues = []
        
        for input_elem in soup.find_all(['input', 'select', 'textarea']):
            input_id = input_elem.get('id')
            aria_label = input_elem.get('aria-label')
            aria_labelledby = input_elem.get('aria-labelledby')
            
            # Verificar se tem label associado
            has_label = False
            if input_id:
                label = soup.find('label', {'for': input_id})
                if label:
                    has_label = True
            
            if not has_label and not aria_label and not aria_labelledby:
                issues.append(AccessibilityIssue(
                    type="form_label",
                    severity="critical",
                    element=str(input_elem),
                    message="Elemento de formulário sem label",
                    suggestion="Use <label>, aria-label ou aria-labelledby"
                ))
        
        return issues
    
    def _check_headings(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Verifica estrutura de cabeçalhos"""
        issues = []
        
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            issues.append(AccessibilityIssue(
                type="no_headings",
                severity="warning",
                element="",
                message="Nenhum cabeçalho encontrado",
                suggestion="Use cabeçalhos para estruturar o conteúdo"
            ))
            return issues
        
        # Verificar se há h1
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            issues.append(AccessibilityIssue(
                type="no_h1",
                severity="critical",
                element="",
                message="Nenhum h1 encontrado",
                suggestion="Use h1 para o título principal da página"
            ))
        elif h1_count > 1:
            issues.append(AccessibilityIssue(
                type="multiple_h1",
                severity="warning",
                element="",
                message="Múltiplos h1 encontrados",
                suggestion="Use apenas um h1 por página"
            ))
        
        # Verificar hierarquia
        prev_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if level > prev_level + 1:
                issues.append(AccessibilityIssue(
                    type="heading_hierarchy",
                    severity="warning",
                    element=str(heading),
                    message=f"Hierarquia de cabeçalhos quebrada: h{level} após h{prev_level}",
                    suggestion="Mantenha hierarquia sequencial de cabeçalhos"
                ))
            prev_level = level
        
        return issues
    
    def _check_links(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Verifica acessibilidade de links"""
        issues = []
        
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # Verificar links vazios
            if not href or href == "#":
                issues.append(AccessibilityIssue(
                    type="empty_link",
                    severity="warning",
                    element=str(link),
                    message="Link sem destino",
                    suggestion="Remova ou adicione href válido"
                ))
            
            # Verificar links sem texto
            if not text:
                issues.append(AccessibilityIssue(
                    type="link_no_text",
                    severity="critical",
                    element=str(link),
                    message="Link sem texto",
                    suggestion="Adicione texto descritivo ao link"
                ))
            
            # Verificar links genéricos
            if text.lower() in ['clique aqui', 'leia mais', 'saiba mais', 'aqui']:
                issues.append(AccessibilityIssue(
                    type="generic_link_text",
                    severity="warning",
                    element=str(link),
                    message="Texto de link genérico",
                    suggestion="Use texto descritivo específico"
                ))
        
        return issues
    
    def _check_tables(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Verifica acessibilidade de tabelas"""
        issues = []
        
        for table in soup.find_all('table'):
            # Verificar se tem caption
            if not table.find('caption'):
                issues.append(AccessibilityIssue(
                    type="table_caption",
                    severity="warning",
                    element=str(table),
                    message="Tabela sem caption",
                    suggestion="Adicione <caption> para descrever a tabela"
                ))
            
            # Verificar cabeçalhos
            headers = table.find_all(['th'])
            if not headers:
                issues.append(AccessibilityIssue(
                    type="table_headers",
                    severity="critical",
                    element=str(table),
                    message="Tabela sem cabeçalhos",
                    suggestion="Use <th> para cabeçalhos de tabela"
                ))
            
            # Verificar scope
            for th in headers:
                if not th.get('scope'):
                    issues.append(AccessibilityIssue(
                        type="table_scope",
                        severity="warning",
                        element=str(th),
                        message="Cabeçalho sem scope",
                        suggestion="Adicione scope='col' ou scope='row'"
                    ))
        
        return issues
    
    def _check_colors(self, html_content: str) -> List[AccessibilityIssue]:
        """Verifica uso de cores"""
        issues = []
        
        # Verificar uso de cores em texto
        color_pattern = r'color:\s*#[0-9a-fA-F]{3,6}'
        color_matches = re.findall(color_pattern, html_content)
        
        if color_matches:
            issues.append(AccessibilityIssue(
                type="color_usage",
                severity="info",
                element="",
                message="Cores definidas em CSS",
                suggestion="Verifique contraste mínimo de 4.5:1 para texto normal"
            ))
        
        return issues
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Obtém número da linha para uma posição"""
        return content[:position].count('\n') + 1
    
    def _calculate_accessibility_score(self, issues: List[AccessibilityIssue]) -> float:
        """Calcula score de acessibilidade"""
        if not issues:
            return 100.0
        
        # Penalidades por severidade
        penalties = {
            "critical": 20,
            "warning": 5,
            "info": 1
        }
        
        total_penalty = sum(penalties.get(issue.severity, 0) for issue in issues)
        score = max(0, 100 - total_penalty)
        
        return score
    
    def _generate_recommendations(self, issues: List[AccessibilityIssue], score: float) -> List[str]:
        """Gera recomendações baseadas nos problemas encontrados"""
        recommendations = []
        
        # Recomendação geral baseada no score
        if score >= 90:
            recommendations.append("🎉 Excelente acessibilidade! Continue mantendo os padrões atuais.")
        elif score >= 70:
            recommendations.append("📈 Boa acessibilidade. Pequenas melhorias podem ser feitas.")
        elif score >= 50:
            recommendations.append("⚠️ Acessibilidade moderada. Melhorias significativas necessárias.")
        else:
            recommendations.append("🚨 Acessibilidade crítica. Revisão urgente necessária.")
        
        # Recomendações específicas
        issue_types = set(issue.type for issue in issues)
        
        if "image_alt" in issue_types:
            recommendations.append("🖼️ Adicione texto alternativo para todas as imagens")
        
        if "form_label" in issue_types:
            recommendations.append("📝 Associe labels a todos os elementos de formulário")
        
        if "no_h1" in issue_types:
            recommendations.append("📄 Use h1 para o título principal da página")
        
        if "link_no_text" in issue_types:
            recommendations.append("🔗 Adicione texto descritivo a todos os links")
        
        if "table_headers" in issue_types:
            recommendations.append("📊 Use cabeçalhos apropriados em tabelas")
        
        if "color_usage" in issue_types:
            recommendations.append("🎨 Verifique contraste de cores (mínimo 4.5:1)")
        
        return recommendations
    
    def _save_report(self, report: AccessibilityReport):
        """Salva relatório de acessibilidade"""
        try:
            filename = f"accessibility_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Converter para dicionário
            report_dict = {
                "url": report.url,
                "timestamp": report.timestamp.isoformat(),
                "total_issues": report.total_issues,
                "critical_issues": report.critical_issues,
                "warning_issues": report.warning_issues,
                "info_issues": report.info_issues,
                "score": report.score,
                "issues": [
                    {
                        "type": issue.type,
                        "severity": issue.severity,
                        "element": issue.element,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                        "line": issue.line,
                        "column": issue.column
                    }
                    for issue in report.issues
                ],
                "recommendations": report.recommendations,
                "passed": report.passed
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
    
    def generate_accessibility_report_html(self, report: AccessibilityReport) -> str:
        """Gera relatório HTML de acessibilidade"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Acessibilidade - MaraBet AI</title>
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
        .score-display {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin: 30px 0;
        }}
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            font-weight: bold;
            color: white;
            background: {'#28a745' if report.passed else '#dc3545'};
        }}
        .issues-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .issue-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .issue-card.critical {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
        .issue-card.warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }}
        .issue-card.info {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }}
        .issue-details {{
            margin: 30px 0;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Relatório de Acessibilidade - MaraBet AI</h1>
            <p>URL: {report.url}</p>
            <p>Data: {report.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="score-display">
            <div class="score-circle">
                {report.score:.0f}%
            </div>
            <div>
                <h2>{'✅ APROVADO' if report.passed else '❌ REPROVADO'}</h2>
                <p>Acessibilidade: {report.score:.1f}% {'(≥ 90%)' if report.passed else '(< 90%)'}</p>
            </div>
        </div>
        
        <div class="issues-summary">
            <div class="issue-card critical">
                <h3>{report.critical_issues}</h3>
                <p>Problemas Críticos</p>
            </div>
            <div class="issue-card warning">
                <h3>{report.warning_issues}</h3>
                <p>Avisos</p>
            </div>
            <div class="issue-card info">
                <h3>{report.info_issues}</h3>
                <p>Informações</p>
            </div>
        </div>
        
        <div class="issue-details">
            <h2>Problemas Encontrados ({report.total_issues})</h2>
            {self._generate_issues_html(report.issues)}
        </div>
        
        <div class="recommendations">
            <h3>Recomendações</h3>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
            </ul>
        </div>
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar HTML: {e}")
            return ""
    
    def _generate_issues_html(self, issues: List[AccessibilityIssue]) -> str:
        """Gera HTML para problemas de acessibilidade"""
        if not issues:
            return "<p>Nenhum problema encontrado! 🎉</p>"
        
        html = ""
        for issue in issues:
            severity_class = issue.severity
            html += f"""
            <div class="issue {severity_class}">
                <h4>{issue.message}</h4>
                <p><strong>Tipo:</strong> {issue.type}</p>
                <p><strong>Severidade:</strong> {issue.severity.upper()}</p>
                <p><strong>Sugestão:</strong> {issue.suggestion}</p>
                {f'<p><strong>Linha:</strong> {issue.line}</p>' if issue.line else ''}
                <details>
                    <summary>Elemento HTML</summary>
                    <pre><code>{issue.element}</code></pre>
                </details>
            </div>
            """
        
        return html
    
    def _empty_report(self, url: str) -> AccessibilityReport:
        """Retorna relatório vazio"""
        return AccessibilityReport(
            url=url,
            timestamp=datetime.now(),
            total_issues=0,
            critical_issues=0,
            warning_issues=0,
            info_issues=0,
            score=0.0,
            issues=[],
            recommendations=[],
            passed=False
        )
