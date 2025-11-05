"""
Otimizador de UX - MaraBet AI
Otimizações de experiência do usuário e acessibilidade
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class UXOptimization:
    """Otimização de UX"""
    type: str
    priority: str
    title: str
    description: str
    implementation: str
    impact: str
    effort: str

@dataclass
class UXReport:
    """Relatório de UX"""
    timestamp: datetime
    total_optimizations: int
    high_priority: int
    medium_priority: int
    low_priority: int
    optimizations: List[UXOptimization]
    recommendations: List[str]
    score: float

class UXOptimizer:
    """
    Otimizador de experiência do usuário para MaraBet AI
    Identifica e sugere melhorias de UX e acessibilidade
    """
    
    def __init__(self, config_file: str = "accessibility/ux_config.json"):
        """
        Inicializa o otimizador de UX
        
        Args:
            config_file: Arquivo de configuração
        """
        self.config_file = config_file
        self.optimizations = self._load_optimizations()
        self.config = self._load_config()
        
        logger.info("UXOptimizer inicializado")
    
    def _load_optimizations(self) -> List[UXOptimization]:
        """Carrega otimizações de UX"""
        return [
            # Acessibilidade
            UXOptimization(
                type="accessibility",
                priority="high",
                title="Contraste de Cores",
                description="Melhorar contraste de cores para melhor legibilidade",
                implementation="Use ferramentas como WebAIM Contrast Checker para verificar contraste mínimo de 4.5:1",
                impact="Alto - Melhora legibilidade para usuários com deficiência visual",
                effort="Médio - Requer revisão de paleta de cores"
            ),
            UXOptimization(
                type="accessibility",
                priority="high",
                title="Navegação por Teclado",
                description="Garantir que todos os elementos interativos sejam acessíveis via teclado",
                implementation="Adicione tabindex apropriado e indicadores de foco visíveis",
                impact="Alto - Essencial para usuários que não usam mouse",
                effort="Médio - Requer revisão de todos os elementos interativos"
            ),
            UXOptimization(
                type="accessibility",
                priority="high",
                title="Textos Alternativos",
                description="Adicionar textos alternativos descritivos para todas as imagens",
                implementation="Use o atributo alt com descrições específicas e úteis",
                impact="Alto - Essencial para usuários com leitores de tela",
                effort="Baixo - Pode ser feito durante desenvolvimento"
            ),
            
            # Performance
            UXOptimization(
                type="performance",
                priority="high",
                title="Carregamento Rápido",
                description="Otimizar tempo de carregamento da página",
                implementation="Use lazy loading, compressão de imagens e minificação de CSS/JS",
                impact="Alto - Melhora experiência geral do usuário",
                effort="Médio - Requer otimização de assets"
            ),
            UXOptimization(
                type="performance",
                priority="medium",
                title="Responsividade",
                description="Garantir que o dashboard funcione bem em todos os dispositivos",
                implementation="Use CSS Grid/Flexbox e media queries responsivas",
                impact="Alto - Essencial para usuários móveis",
                effort="Médio - Requer revisão de layout"
            ),
            
            # Usabilidade
            UXOptimization(
                type="usability",
                priority="high",
                title="Feedback Visual",
                description="Adicionar feedback visual para ações do usuário",
                implementation="Use animações sutis, estados de loading e confirmações",
                impact="Alto - Melhora compreensão das ações",
                effort="Baixo - Pode ser implementado incrementalmente"
            ),
            UXOptimization(
                type="usability",
                priority="medium",
                title="Navegação Intuitiva",
                description="Melhorar estrutura de navegação e hierarquia de informações",
                implementation="Use breadcrumbs, menu claro e organização lógica",
                impact="Médio - Melhora descoberta de funcionalidades",
                effort="Médio - Requer reorganização de interface"
            ),
            UXOptimization(
                type="usability",
                priority="medium",
                title="Formulários Acessíveis",
                description="Melhorar acessibilidade e usabilidade de formulários",
                implementation="Use labels apropriados, validação em tempo real e mensagens claras",
                impact="Alto - Essencial para entrada de dados",
                effort="Médio - Requer revisão de todos os formulários"
            ),
            
            # Funcionalidade
            UXOptimization(
                type="functionality",
                priority="high",
                title="Modo Escuro",
                description="Implementar modo escuro para melhor experiência noturna",
                implementation="Use CSS custom properties e toggle de tema",
                impact="Médio - Melhora conforto visual",
                effort="Médio - Requer implementação de sistema de temas"
            ),
            UXOptimization(
                type="functionality",
                priority="medium",
                title="Exportação de Dados",
                description="Permitir exportação de relatórios em múltiplos formatos",
                implementation="Implemente exportação para PDF, CSV, Excel e JSON",
                impact="Médio - Melhora utilidade do sistema",
                effort="Alto - Requer implementação de múltiplos formatos"
            ),
            UXOptimization(
                type="functionality",
                priority="low",
                title="Personalização",
                description="Permitir personalização de interface pelo usuário",
                implementation="Implemente configurações de tema, tamanho de fonte e layout",
                impact="Baixo - Melhora satisfação do usuário",
                effort="Alto - Requer sistema de preferências"
            )
        ]
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do otimizador"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "weights": {
                        "accessibility": 0.4,
                        "performance": 0.3,
                        "usability": 0.2,
                        "functionality": 0.1
                    },
                    "priority_scores": {
                        "high": 3,
                        "medium": 2,
                        "low": 1
                    }
                }
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return {}
    
    def analyze_ux(self, current_features: List[str] = None) -> UXReport:
        """
        Analisa UX atual e sugere otimizações
        
        Args:
            current_features: Lista de funcionalidades atuais
            
        Returns:
            Relatório de análise UX
        """
        try:
            if current_features is None:
                current_features = []
            
            # Filtrar otimizações baseadas em funcionalidades atuais
            relevant_optimizations = self._filter_relevant_optimizations(current_features)
            
            # Calcular métricas
            total_optimizations = len(relevant_optimizations)
            high_priority = len([o for o in relevant_optimizations if o.priority == "high"])
            medium_priority = len([o for o in relevant_optimizations if o.priority == "medium"])
            low_priority = len([o for o in relevant_optimizations if o.priority == "low"])
            
            # Calcular score
            score = self._calculate_ux_score(relevant_optimizations)
            
            # Gerar recomendações
            recommendations = self._generate_ux_recommendations(relevant_optimizations, score)
            
            report = UXReport(
                timestamp=datetime.now(),
                total_optimizations=total_optimizations,
                high_priority=high_priority,
                medium_priority=medium_priority,
                low_priority=low_priority,
                optimizations=relevant_optimizations,
                recommendations=recommendations,
                score=score
            )
            
            # Salvar relatório
            self._save_ux_report(report)
            
            logger.info(f"✅ Análise UX concluída - Score: {score:.1f}%")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro na análise UX: {e}")
            return self._empty_ux_report()
    
    def _filter_relevant_optimizations(self, current_features: List[str]) -> List[UXOptimization]:
        """Filtra otimizações relevantes baseadas em funcionalidades atuais"""
        relevant = []
        
        for optimization in self.optimizations:
            # Verificar se a otimização é relevante
            is_relevant = True
            
            # Se já tem modo escuro, não sugerir novamente
            if optimization.title == "Modo Escuro" and "dark_mode" in current_features:
                is_relevant = False
            
            # Se já tem exportação, não sugerir novamente
            if optimization.title == "Exportação de Dados" and "export" in current_features:
                is_relevant = False
            
            if is_relevant:
                relevant.append(optimization)
        
        return relevant
    
    def _calculate_ux_score(self, optimizations: List[UXOptimization]) -> float:
        """Calcula score de UX baseado nas otimizações"""
        if not optimizations:
            return 100.0
        
        # Calcular score por categoria
        category_scores = {}
        weights = self.config.get("weights", {})
        priority_scores = self.config.get("priority_scores", {})
        
        for optimization in optimizations:
            category = optimization.type
            priority = optimization.priority
            
            if category not in category_scores:
                category_scores[category] = []
            
            category_scores[category].append(priority_scores.get(priority, 1))
        
        # Calcular score ponderado
        total_score = 0
        total_weight = 0
        
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            weight = weights.get(category, 0.25)
            total_score += avg_score * weight
            total_weight += weight
        
        # Normalizar para 0-100
        if total_weight > 0:
            normalized_score = (total_score / total_weight) * 33.33  # 3 é o máximo de prioridade
            return min(100, max(0, normalized_score))
        
        return 0.0
    
    def _generate_ux_recommendations(self, optimizations: List[UXOptimization], score: float) -> List[str]:
        """Gera recomendações de UX"""
        recommendations = []
        
        # Recomendação geral baseada no score
        if score >= 80:
            recommendations.append("🎉 Excelente UX! Continue mantendo os padrões atuais.")
        elif score >= 60:
            recommendations.append("📈 Boa UX. Algumas melhorias podem ser implementadas.")
        elif score >= 40:
            recommendations.append("⚠️ UX moderada. Melhorias significativas necessárias.")
        else:
            recommendations.append("🚨 UX crítica. Revisão urgente necessária.")
        
        # Recomendações por prioridade
        high_priority = [o for o in optimizations if o.priority == "high"]
        medium_priority = [o for o in optimizations if o.priority == "medium"]
        
        if high_priority:
            recommendations.append(f"🔴 {len(high_priority)} otimizações de alta prioridade - Implementar primeiro")
        
        if medium_priority:
            recommendations.append(f"🟡 {len(medium_priority)} otimizações de média prioridade - Planejar implementação")
        
        # Recomendações específicas por categoria
        categories = set(o.type for o in optimizations)
        
        if "accessibility" in categories:
            recommendations.append("♿ Foque em acessibilidade - Essencial para inclusão")
        
        if "performance" in categories:
            recommendations.append("⚡ Otimize performance - Melhora experiência geral")
        
        if "usability" in categories:
            recommendations.append("🎯 Melhore usabilidade - Facilita uso do sistema")
        
        if "functionality" in categories:
            recommendations.append("🔧 Adicione funcionalidades - Aumenta valor do produto")
        
        return recommendations
    
    def generate_implementation_plan(self, optimizations: List[UXOptimization]) -> Dict[str, Any]:
        """Gera plano de implementação das otimizações"""
        try:
            # Agrupar por prioridade
            by_priority = {
                "high": [o for o in optimizations if o.priority == "high"],
                "medium": [o for o in optimizations if o.priority == "medium"],
                "low": [o for o in optimizations if o.priority == "low"]
            }
            
            # Agrupar por esforço
            by_effort = {
                "low": [o for o in optimizations if o.effort == "Baixo"],
                "medium": [o for o in optimizations if o.effort == "Médio"],
                "high": [o for o in optimizations if o.effort == "Alto"]
            }
            
            # Gerar cronograma sugerido
            timeline = self._generate_timeline(optimizations)
            
            return {
                "by_priority": by_priority,
                "by_effort": by_effort,
                "timeline": timeline,
                "total_optimizations": len(optimizations),
                "estimated_effort": self._estimate_total_effort(optimizations)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar plano: {e}")
            return {}
    
    def _generate_timeline(self, optimizations: List[UXOptimization]) -> Dict[str, List[str]]:
        """Gera cronograma de implementação"""
        timeline = {
            "Sprint 1 (2 semanas)": [],
            "Sprint 2 (2 semanas)": [],
            "Sprint 3 (2 semanas)": [],
            "Backlog": []
        }
        
        # Priorizar por prioridade e esforço
        sorted_optimizations = sorted(optimizations, key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}[x.priority],
            {"Baixo": 0, "Médio": 1, "Alto": 2}[x.effort]
        ))
        
        sprint = 1
        for optimization in sorted_optimizations:
            if sprint <= 3:
                timeline[f"Sprint {sprint} (2 semanas)"].append(optimization.title)
                if optimization.effort == "Alto":
                    sprint += 1
            else:
                timeline["Backlog"].append(optimization.title)
        
        return timeline
    
    def _estimate_total_effort(self, optimizations: List[UXOptimization]) -> Dict[str, int]:
        """Estima esforço total das otimizações"""
        effort_counts = {"Baixo": 0, "Médio": 0, "Alto": 0}
        
        for optimization in optimizations:
            effort_counts[optimization.effort] += 1
        
        return effort_counts
    
    def create_ux_dashboard(self, report: UXReport) -> str:
        """Cria dashboard de UX"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard UX - MaraBet AI</title>
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
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .score-display {{
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
            font-size: 2.5em;
            font-weight: bold;
            color: white;
            background: {'#28a745' if report.score >= 70 else '#ffc107' if report.score >= 50 else '#dc3545'};
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 5px solid #667eea;
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .optimizations {{
            padding: 30px;
        }}
        .optimization {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #667eea;
        }}
        .optimization.high {{
            border-left-color: #dc3545;
        }}
        .optimization.medium {{
            border-left-color: #ffc107;
        }}
        .optimization.low {{
            border-left-color: #28a745;
        }}
        .priority-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .priority-badge.high {{
            background: #dc3545;
            color: white;
        }}
        .priority-badge.medium {{
            background: #ffc107;
            color: #333;
        }}
        .priority-badge.low {{
            background: #28a745;
            color: white;
        }}
        .recommendations {{
            background: #e8f5e8;
            padding: 20px;
            margin: 30px;
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
            <h1>Dashboard de UX - MaraBet AI</h1>
            <p>Análise de Experiência do Usuário e Otimizações</p>
            <p>Data: {report.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="score-display">
            <div class="score-circle">
                {report.score:.0f}%
            </div>
            <div>
                <h2>Score de UX</h2>
                <p>{'Excelente' if report.score >= 80 else 'Bom' if report.score >= 60 else 'Moderado' if report.score >= 40 else 'Crítico'}</p>
            </div>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <h3>Total de Otimizações</h3>
                <div class="value">{report.total_optimizations}</div>
            </div>
            <div class="metric-card">
                <h3>Alta Prioridade</h3>
                <div class="value">{report.high_priority}</div>
            </div>
            <div class="metric-card">
                <h3>Média Prioridade</h3>
                <div class="value">{report.medium_priority}</div>
            </div>
            <div class="metric-card">
                <h3>Baixa Prioridade</h3>
                <div class="value">{report.low_priority}</div>
            </div>
        </div>
        
        <div class="optimizations">
            <h2>Otimizações Sugeridas</h2>
            {self._generate_optimizations_html(report.optimizations)}
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
            logger.error(f"❌ Erro ao criar dashboard: {e}")
            return ""
    
    def _generate_optimizations_html(self, optimizations: List[UXOptimization]) -> str:
        """Gera HTML para otimizações"""
        if not optimizations:
            return "<p>Nenhuma otimização sugerida! 🎉</p>"
        
        html = ""
        for optimization in optimizations:
            html += f"""
            <div class="optimization {optimization.priority}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4>{optimization.title}</h4>
                    <span class="priority-badge {optimization.priority}">{optimization.priority}</span>
                </div>
                <p><strong>Descrição:</strong> {optimization.description}</p>
                <p><strong>Implementação:</strong> {optimization.implementation}</p>
                <p><strong>Impacto:</strong> {optimization.impact}</p>
                <p><strong>Esforço:</strong> {optimization.effort}</p>
            </div>
            """
        
        return html
    
    def _save_ux_report(self, report: UXReport):
        """Salva relatório de UX"""
        try:
            filename = f"ux_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("accessibility", filename)
            
            # Converter para dicionário
            report_dict = {
                "timestamp": report.timestamp.isoformat(),
                "total_optimizations": report.total_optimizations,
                "high_priority": report.high_priority,
                "medium_priority": report.medium_priority,
                "low_priority": report.low_priority,
                "score": report.score,
                "optimizations": [
                    {
                        "type": opt.type,
                        "priority": opt.priority,
                        "title": opt.title,
                        "description": opt.description,
                        "implementation": opt.implementation,
                        "impact": opt.impact,
                        "effort": opt.effort
                    }
                    for opt in report.optimizations
                ],
                "recommendations": report.recommendations
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório UX salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
    
    def _empty_ux_report(self) -> UXReport:
        """Retorna relatório vazio"""
        return UXReport(
            timestamp=datetime.now(),
            total_optimizations=0,
            high_priority=0,
            medium_priority=0,
            low_priority=0,
            optimizations=[],
            recommendations=[],
            score=0.0
        )
