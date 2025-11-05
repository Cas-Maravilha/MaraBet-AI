#!/usr/bin/env python3
"""
Corretor de Documentação - MaraBet AI
Corrige erros de documentação e melhora consistência
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentationIssue:
    """Problema de documentação"""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    suggestion: str
    severity: str

@dataclass
class DocumentationReport:
    """Relatório de documentação"""
    timestamp: datetime
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[DocumentationIssue]
    fixed_issues: List[str]
    recommendations: List[str]

class DocumentationFixer:
    """
    Corretor de documentação para MaraBet AI
    Identifica e corrige problemas de documentação
    """
    
    def __init__(self, project_root: str = "."):
        """
        Inicializa o corretor de documentação
        
        Args:
            project_root: Diretório raiz do projeto
        """
        self.project_root = project_root
        self.issues = []
        self.fixed_issues = []
        
        # Padrões de problemas comuns
        self.patterns = {
            "missing_docstring": {
                "pattern": r'^def\s+\w+\([^)]*\):\s*$',
                "description": "Função sem docstring",
                "suggestion": "Adicionar docstring descritiva",
                "severity": "medium"
            },
            "missing_type_hints": {
                "pattern": r'^def\s+\w+\([^)]*\):\s*$',
                "description": "Função sem type hints",
                "suggestion": "Adicionar type hints para parâmetros e retorno",
                "severity": "low"
            },
            "todo_comments": {
                "pattern": r'#\s*TODO|#\s*FIXME|#\s*XXX',
                "description": "Comentário TODO/FIXME/XXX",
                "suggestion": "Resolver ou remover comentário TODO",
                "severity": "low"
            },
            "hardcoded_strings": {
                "pattern": r'"[^"]*"|\'[^\']*\'',
                "description": "String hardcoded",
                "suggestion": "Usar constantes ou variáveis de configuração",
                "severity": "low"
            },
            "long_lines": {
                "pattern": r'^.{120,}$',
                "description": "Linha muito longa (>120 caracteres)",
                "suggestion": "Quebrar linha para melhor legibilidade",
                "severity": "low"
            },
            "missing_imports": {
                "pattern": r'^from\s+\w+\s+import\s+\*$',
                "description": "Import wildcard (*)",
                "suggestion": "Importar apenas o que é necessário",
                "severity": "medium"
            },
            "unused_imports": {
                "pattern": r'^import\s+\w+$|^from\s+\w+\s+import\s+\w+$',
                "description": "Import possivelmente não utilizado",
                "suggestion": "Verificar se import é necessário",
                "severity": "low"
            }
        }
        
        logger.info("DocumentationFixer inicializado")
    
    def scan_project(self) -> DocumentationReport:
        """
        Escaneia projeto em busca de problemas de documentação
        
        Returns:
            Relatório de documentação
        """
        try:
            logger.info("🔍 Escaneando projeto em busca de problemas de documentação...")
            
            # Arquivos para verificar
            file_patterns = [
                "*.py",
                "*.md",
                "*.yml",
                "*.yaml",
                "*.json",
                "*.txt"
            ]
            
            # Diretórios para ignorar
            ignore_dirs = {
                "__pycache__",
                ".git",
                ".pytest_cache",
                "node_modules",
                ".venv",
                "venv",
                "env"
            }
            
            # Encontrar arquivos
            files_to_check = []
            for root, dirs, files in os.walk(self.project_root):
                # Remover diretórios ignorados
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                for file in files:
                    if any(file.endswith(pattern.replace('*', '')) for pattern in file_patterns):
                        files_to_check.append(os.path.join(root, file))
            
            logger.info(f"📁 Encontrados {len(files_to_check)} arquivos para verificar")
            
            # Verificar cada arquivo
            for file_path in files_to_check:
                self._check_file(file_path)
            
            # Gerar relatório
            report = self._generate_report()
            
            logger.info(f"✅ Escaneamento concluído - {len(self.issues)} problemas encontrados")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro no escaneamento: {e}")
            return self._empty_report()
    
    def _check_file(self, file_path: str):
        """Verifica arquivo em busca de problemas"""
        try:
            if not os.path.exists(file_path):
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                self._check_line(file_path, line_num, line)
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar arquivo {file_path}: {e}")
    
    def _check_line(self, file_path: str, line_num: int, line: str):
        """Verifica linha em busca de problemas"""
        try:
            # Verificar padrões
            for pattern_name, pattern_info in self.patterns.items():
                if re.search(pattern_info["pattern"], line.strip()):
                    # Verificações específicas
                    if pattern_name == "missing_docstring":
                        if not self._has_docstring_next_line(file_path, line_num):
                            self._add_issue(file_path, line_num, pattern_name, pattern_info, line)
                    elif pattern_name == "missing_type_hints":
                        if not self._has_type_hints(line):
                            self._add_issue(file_path, line_num, pattern_name, pattern_info, line)
                    elif pattern_name == "long_lines":
                        if len(line.rstrip()) > 120:
                            self._add_issue(file_path, line_num, pattern_name, pattern_info, line)
                    else:
                        self._add_issue(file_path, line_num, pattern_name, pattern_info, line)
            
            # Verificações específicas por tipo de arquivo
            if file_path.endswith('.py'):
                self._check_python_specific(file_path, line_num, line)
            elif file_path.endswith('.md'):
                self._check_markdown_specific(file_path, line_num, line)
            elif file_path.endswith(('.yml', '.yaml')):
                self._check_yaml_specific(file_path, line_num, line)
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar linha {line_num} em {file_path}: {e}")
    
    def _check_python_specific(self, file_path: str, line_num: int, line: str):
        """Verificações específicas para Python"""
        try:
            # Verificar se é função sem docstring
            if re.match(r'^def\s+\w+\([^)]*\):\s*$', line.strip()):
                if not self._has_docstring_next_line(file_path, line_num):
                    self._add_issue(file_path, line_num, "missing_docstring", {
                        "description": "Função sem docstring",
                        "suggestion": "Adicionar docstring descritiva",
                        "severity": "medium"
                    }, line)
            
            # Verificar se é classe sem docstring
            if re.match(r'^class\s+\w+.*:\s*$', line.strip()):
                if not self._has_docstring_next_line(file_path, line_num):
                    self._add_issue(file_path, line_num, "missing_class_docstring", {
                        "description": "Classe sem docstring",
                        "suggestion": "Adicionar docstring descritiva",
                        "severity": "medium"
                    }, line)
            
            # Verificar imports desnecessários
            if re.match(r'^import\s+\w+$', line.strip()):
                if self._is_unused_import(file_path, line):
                    self._add_issue(file_path, line_num, "unused_import", {
                        "description": "Import possivelmente não utilizado",
                        "suggestion": "Remover import não utilizado",
                        "severity": "low"
                    }, line)
                    
        except Exception as e:
            logger.error(f"❌ Erro na verificação Python: {e}")
    
    def _check_markdown_specific(self, file_path: str, line_num: int, line: str):
        """Verificações específicas para Markdown"""
        try:
            # Verificar links quebrados
            if re.search(r'\[([^\]]+)\]\([^)]+\)', line):
                if not self._is_valid_link(line):
                    self._add_issue(file_path, line_num, "broken_link", {
                        "description": "Link possivelmente quebrado",
                        "suggestion": "Verificar e corrigir link",
                        "severity": "medium"
                    }, line)
            
            # Verificar títulos sem espaços
            if re.match(r'^#{1,6}[^#\s]', line):
                self._add_issue(file_path, line_num, "title_format", {
                    "description": "Título sem espaço após #",
                    "suggestion": "Adicionar espaço após #",
                    "severity": "low"
                }, line)
            
            # Verificar linhas muito longas
            if len(line.rstrip()) > 100:
                self._add_issue(file_path, line_num, "long_line", {
                    "description": "Linha muito longa",
                    "suggestion": "Quebrar linha para melhor legibilidade",
                    "severity": "low"
                }, line)
                
        except Exception as e:
            logger.error(f"❌ Erro na verificação Markdown: {e}")
    
    def _check_yaml_specific(self, file_path: str, line_num: int, line: str):
        """Verificações específicas para YAML"""
        try:
            # Verificar indentação inconsistente
            if line.strip() and not line.startswith(' '):
                if line_num > 1:  # Não verificar primeira linha
                    self._add_issue(file_path, line_num, "indentation", {
                        "description": "Indentação inconsistente",
                        "suggestion": "Usar 2 espaços para indentação",
                        "severity": "medium"
                    }, line)
            
            # Verificar chaves duplicadas
            if ':' in line and not line.strip().startswith('#'):
                key = line.split(':')[0].strip()
                if self._is_duplicate_key(file_path, key, line_num):
                    self._add_issue(file_path, line_num, "duplicate_key", {
                        "description": "Chave duplicada",
                        "suggestion": "Remover chave duplicada",
                        "severity": "high"
                    }, line)
                    
        except Exception as e:
            logger.error(f"❌ Erro na verificação YAML: {e}")
    
    def _has_docstring_next_line(self, file_path: str, line_num: int) -> bool:
        """Verifica se há docstring na próxima linha"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num < len(lines):
                next_line = lines[line_num].strip()
                return next_line.startswith('"""') or next_line.startswith("'''")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar docstring: {e}")
            return False
    
    def _has_type_hints(self, line: str) -> bool:
        """Verifica se linha tem type hints"""
        return '->' in line or ':' in line.split('(')[1].split(')')[0] if '(' in line and ')' in line else False
    
    def _is_unused_import(self, file_path: str, import_line: str) -> bool:
        """Verifica se import é não utilizado"""
        try:
            # Extrair nome do módulo/função importado
            if 'from' in import_line:
                imported = import_line.split('import')[1].strip()
            else:
                imported = import_line.split('import')[1].strip()
            
            # Verificar se é usado no arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contar ocorrências (excluindo a linha do import)
            lines = content.split('\n')
            count = 0
            for line in lines:
                if line.strip() != import_line.strip() and imported in line:
                    count += 1
            
            return count == 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar import: {e}")
            return False
    
    def _is_valid_link(self, line: str) -> bool:
        """Verifica se link é válido"""
        # Implementação básica - verificar se não é link local quebrado
        if '](' in line:
            link = line.split('](')[1].split(')')[0]
            if link.startswith('http') or link.startswith('#'):
                return True
            elif link.startswith('./') or link.startswith('../'):
                return os.path.exists(link)
        
        return True
    
    def _is_duplicate_key(self, file_path: str, key: str, current_line: int) -> bool:
        """Verifica se chave é duplicada"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            count = 0
            for line_num, line in enumerate(lines, 1):
                if line_num != current_line and ':' in line:
                    if line.split(':')[0].strip() == key:
                        count += 1
            
            return count > 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar chave duplicada: {e}")
            return False
    
    def _add_issue(self, file_path: str, line_num: int, issue_type: str, pattern_info: Dict, line: str):
        """Adiciona problema à lista"""
        issue = DocumentationIssue(
            file_path=file_path,
            line_number=line_num,
            issue_type=issue_type,
            description=pattern_info["description"],
            suggestion=pattern_info["suggestion"],
            severity=pattern_info["severity"]
        )
        self.issues.append(issue)
    
    def _generate_report(self) -> DocumentationReport:
        """Gera relatório de documentação"""
        try:
            # Contar problemas por severidade
            critical_issues = len([i for i in self.issues if i.severity == "critical"])
            high_issues = len([i for i in self.issues if i.severity == "high"])
            medium_issues = len([i for i in self.issues if i.severity == "medium"])
            low_issues = len([i for i in self.issues if i.severity == "low"])
            
            # Gerar recomendações
            recommendations = self._generate_recommendations()
            
            report = DocumentationReport(
                timestamp=datetime.now(),
                total_issues=len(self.issues),
                critical_issues=critical_issues,
                high_issues=high_issues,
                medium_issues=medium_issues,
                low_issues=low_issues,
                issues=self.issues,
                fixed_issues=self.fixed_issues,
                recommendations=recommendations
            )
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return self._empty_report()
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações de melhoria"""
        recommendations = []
        
        # Recomendações baseadas nos problemas encontrados
        issue_types = set(issue.issue_type for issue in self.issues)
        
        if "missing_docstring" in issue_types:
            recommendations.append("📝 Adicionar docstrings para todas as funções e classes")
        
        if "missing_type_hints" in issue_types:
            recommendations.append("🔍 Adicionar type hints para melhor legibilidade")
        
        if "todo_comments" in issue_types:
            recommendations.append("✅ Resolver ou remover comentários TODO/FIXME")
        
        if "hardcoded_strings" in issue_types:
            recommendations.append("🔧 Usar constantes para strings hardcoded")
        
        if "long_lines" in issue_types:
            recommendations.append("📏 Quebrar linhas longas para melhor legibilidade")
        
        if "missing_imports" in issue_types:
            recommendations.append("📦 Importar apenas o que é necessário")
        
        if "unused_imports" in issue_types:
            recommendations.append("🧹 Remover imports não utilizados")
        
        # Recomendações gerais
        recommendations.extend([
            "📚 Manter documentação atualizada",
            "🔍 Revisar regularmente a qualidade do código",
            "✅ Usar ferramentas de linting (flake8, black, isort)",
            "🧪 Adicionar testes para funções críticas",
            "📋 Seguir padrões de codificação (PEP 8)"
        ])
        
        return recommendations
    
    def fix_issues(self, auto_fix: bool = False) -> List[str]:
        """
        Corrige problemas de documentação
        
        Args:
            auto_fix: Se deve corrigir automaticamente
            
        Returns:
            Lista de problemas corrigidos
        """
        try:
            fixed = []
            
            for issue in self.issues:
                if issue.severity in ["low", "medium"] and auto_fix:
                    if self._fix_issue(issue):
                        fixed.append(f"{issue.file_path}:{issue.line_number} - {issue.description}")
                        self.fixed_issues.append(issue)
            
            logger.info(f"✅ {len(fixed)} problemas corrigidos automaticamente")
            return fixed
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir problemas: {e}")
            return []
    
    def _fix_issue(self, issue: DocumentationIssue) -> bool:
        """Corrige problema específico"""
        try:
            if issue.issue_type == "title_format":
                return self._fix_title_format(issue)
            elif issue.issue_type == "long_line":
                return self._fix_long_line(issue)
            elif issue.issue_type == "indentation":
                return self._fix_indentation(issue)
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir problema: {e}")
            return False
    
    def _fix_title_format(self, issue: DocumentationIssue) -> bool:
        """Corrige formato de título"""
        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Adicionar espaço após #
            line = lines[issue.line_number - 1]
            if line.startswith('#'):
                lines[issue.line_number - 1] = line.replace('#', '# ', 1)
                
                with open(issue.file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir título: {e}")
            return False
    
    def _fix_long_line(self, issue: DocumentationIssue) -> bool:
        """Corrige linha longa"""
        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            line = lines[issue.line_number - 1]
            if len(line.rstrip()) > 120:
                # Quebrar linha em ponto apropriado
                if ' ' in line:
                    words = line.split()
                    new_line = ""
                    current_line = ""
                    
                    for word in words:
                        if len(current_line + word) > 100:
                            new_line += current_line.rstrip() + "\n    "
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    
                    new_line += current_line.rstrip()
                    lines[issue.line_number - 1] = new_line
                    
                    with open(issue.file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir linha longa: {e}")
            return False
    
    def _fix_indentation(self, issue: DocumentationIssue) -> bool:
        """Corrige indentação"""
        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            line = lines[issue.line_number - 1]
            if line.strip() and not line.startswith(' '):
                # Adicionar indentação de 2 espaços
                lines[issue.line_number - 1] = "  " + line
                
                with open(issue.file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir indentação: {e}")
            return False
    
    def generate_report_html(self, report: DocumentationReport) -> str:
        """Gera relatório HTML"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Documentação - MaraBet AI</title>
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
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 5px solid #667eea;
        }}
        .summary-card.critical {{
            border-left-color: #dc3545;
        }}
        .summary-card.high {{
            border-left-color: #fd7e14;
        }}
        .summary-card.medium {{
            border-left-color: #ffc107;
        }}
        .summary-card.low {{
            border-left-color: #28a745;
        }}
        .issue {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .issue.critical {{
            border-left: 5px solid #dc3545;
        }}
        .issue.high {{
            border-left: 5px solid #fd7e14;
        }}
        .issue.medium {{
            border-left: 5px solid #ffc107;
        }}
        .issue.low {{
            border-left: 5px solid #28a745;
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
            <h1>Relatório de Documentação - MaraBet AI</h1>
            <p>Análise de qualidade e consistência da documentação</p>
            <p>Data: {report.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{report.total_issues}</h3>
                <p>Total de Problemas</p>
            </div>
            <div class="summary-card critical">
                <h3>{report.critical_issues}</h3>
                <p>Críticos</p>
            </div>
            <div class="summary-card high">
                <h3>{report.high_issues}</h3>
                <p>Alta Prioridade</p>
            </div>
            <div class="summary-card medium">
                <h3>{report.medium_issues}</h3>
                <p>Média Prioridade</p>
            </div>
            <div class="summary-card low">
                <h3>{report.low_issues}</h3>
                <p>Baixa Prioridade</p>
            </div>
        </div>
        
        <div class="issues">
            <h2>Problemas Encontrados</h2>
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
    
    def _generate_issues_html(self, issues: List[DocumentationIssue]) -> str:
        """Gera HTML para problemas"""
        if not issues:
            return "<p>Nenhum problema encontrado! 🎉</p>"
        
        html = ""
        for issue in issues:
            severity_class = issue.severity
            html += f"""
            <div class="issue {severity_class}">
                <h4>{issue.file_path}:{issue.line_number}</h4>
                <p><strong>Tipo:</strong> {issue.issue_type}</p>
                <p><strong>Descrição:</strong> {issue.description}</p>
                <p><strong>Sugestão:</strong> {issue.suggestion}</p>
                <p><strong>Severidade:</strong> {issue.severity.upper()}</p>
            </div>
            """
        
        return html
    
    def _empty_report(self) -> DocumentationReport:
        """Retorna relatório vazio"""
        return DocumentationReport(
            timestamp=datetime.now(),
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
            issues=[],
            fixed_issues=[],
            recommendations=[]
        )

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Corretor de Documentação - MaraBet AI")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--auto-fix", action="store_true", help="Corrigir problemas automaticamente")
    parser.add_argument("--output", default="documentation_report.html", help="Arquivo de saída")
    
    args = parser.parse_args()
    
    try:
        # Criar corretor
        fixer = DocumentationFixer(args.project_root)
        
        # Escanear projeto
        report = fixer.scan_project()
        
        # Corrigir problemas se solicitado
        if args.auto_fix:
            fixed = fixer.fix_issues(auto_fix=True)
            print(f"✅ {len(fixed)} problemas corrigidos automaticamente")
        
        # Gerar relatório HTML
        html_content = fixer.generate_report_html(report)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Relatório gerado: {args.output}")
        print(f"📋 Total de problemas: {report.total_issues}")
        print(f"🔴 Críticos: {report.critical_issues}")
        print(f"🟠 Alta prioridade: {report.high_issues}")
        print(f"🟡 Média prioridade: {report.medium_issues}")
        print(f"🟢 Baixa prioridade: {report.low_issues}")
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
