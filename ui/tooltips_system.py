#!/usr/bin/env python3
"""
Sistema de Tooltips Explicativos para o MaraBet AI
Tooltips informativos para melhorar UX
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json

class TooltipPosition(Enum):
    """Posições do tooltip"""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    AUTO = "auto"

class TooltipTrigger(Enum):
    """Gatilhos do tooltip"""
    HOVER = "hover"
    CLICK = "click"
    FOCUS = "focus"
    MANUAL = "manual"

@dataclass
class TooltipContent:
    """Conteúdo do tooltip"""
    title: str
    description: str
    examples: List[str]
    tips: List[str]
    warnings: List[str]
    links: List[Dict[str, str]]
    position: TooltipPosition
    trigger: TooltipTrigger
    delay: int  # milissegundos
    max_width: int  # pixels

class TooltipManager:
    """Gerenciador de tooltips"""
    
    def __init__(self):
        """Inicializa gerenciador de tooltips"""
        self.tooltips: Dict[str, TooltipContent] = {}
        self._load_default_tooltips()
    
    def _load_default_tooltips(self):
        """Carrega tooltips padrão do sistema"""
        default_tooltips = {
            "prediction_confidence": TooltipContent(
                title="Confiança da Predição",
                description="A confiança indica quão certo o modelo está sobre a predição. Valores mais altos significam maior certeza.",
                examples=[
                    "0.85 = 85% de confiança",
                    "0.60 = 60% de confiança",
                    "0.30 = 30% de confiança"
                ],
                tips=[
                    "Use predições com confiança > 70% para apostas mais seguras",
                    "Predições com confiança < 50% são consideradas incertas",
                    "A confiança é calculada baseada na qualidade dos dados históricos"
                ],
                warnings=[
                    "Alta confiança não garante resultado correto",
                    "Considere outros fatores além da confiança"
                ],
                links=[
                    {"text": "Como interpretar confiança", "url": "/help/confidence"},
                    {"text": "Fatores que afetam confiança", "url": "/help/confidence-factors"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=300
            ),
            
            "expected_value": TooltipContent(
                title="Valor Esperado (EV)",
                description="O valor esperado é o retorno médio esperado de uma aposta, considerando a probabilidade e as odds.",
                examples=[
                    "EV positivo = aposta favorável",
                    "EV negativo = aposta desfavorável",
                    "EV = (Probabilidade × Odds) - 1"
                ],
                tips=[
                    "Aposte apenas em valores com EV positivo",
                    "EV > 0.10 é considerado muito bom",
                    "EV entre 0.05 e 0.10 é bom",
                    "EV < 0.05 é marginal"
                ],
                warnings=[
                    "EV positivo não garante lucro a curto prazo",
                    "Considere a variância e o bankroll"
                ],
                links=[
                    {"text": "Calculadora de EV", "url": "/tools/ev-calculator"},
                    {"text": "Gestão de bankroll", "url": "/help/bankroll-management"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=350
            ),
            
            "roi": TooltipContent(
                title="ROI (Return on Investment)",
                description="O ROI mostra o retorno sobre o investimento, calculado como (Lucro/Prejuízo) ÷ Investimento Total × 100.",
                examples=[
                    "ROI 15% = R$ 15 de lucro para cada R$ 100 apostados",
                    "ROI -5% = R$ 5 de prejuízo para cada R$ 100 apostados",
                    "ROI 0% = break-even (sem lucro nem prejuízo)"
                ],
                tips=[
                    "ROI > 10% é considerado excelente",
                    "ROI entre 5% e 10% é bom",
                    "ROI entre 0% e 5% é marginal",
                    "ROI negativo indica prejuízo"
                ],
                warnings=[
                    "ROI pode variar significativamente no curto prazo",
                    "Considere o período de análise do ROI"
                ],
                links=[
                    {"text": "Como calcular ROI", "url": "/help/roi-calculation"},
                    {"text": "Análise de performance", "url": "/help/performance-analysis"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=300
            ),
            
            "win_rate": TooltipContent(
                title="Taxa de Acerto",
                description="A taxa de acerto mostra a porcentagem de apostas que resultaram em lucro.",
                examples=[
                    "60% = 6 de cada 10 apostas foram vencedoras",
                    "40% = 4 de cada 10 apostas foram vencedoras",
                    "80% = 8 de cada 10 apostas foram vencedoras"
                ],
                tips=[
                    "Taxa > 60% é considerada excelente",
                    "Taxa entre 50% e 60% é boa",
                    "Taxa < 50% pode ser problemática",
                    "Considere o tipo de aposta ao avaliar"
                ],
                warnings=[
                    "Taxa alta com odds baixas pode não ser lucrativa",
                    "Taxa baixa com odds altas pode ser lucrativa"
                ],
                links=[
                    {"text": "Interpretando taxa de acerto", "url": "/help/win-rate"},
                    {"text": "Estratégias de apostas", "url": "/help/betting-strategies"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=300
            ),
            
            "odds": TooltipContent(
                title="Odds",
                description="As odds representam a probabilidade implícita de um resultado e o pagamento potencial.",
                examples=[
                    "Odds 2.00 = 50% de probabilidade implícita",
                    "Odds 1.50 = 66.7% de probabilidade implícita",
                    "Odds 3.00 = 33.3% de probabilidade implícita"
                ],
                tips=[
                    "Odds mais altas = menor probabilidade, maior pagamento",
                    "Odds mais baixas = maior probabilidade, menor pagamento",
                    "Compare odds entre diferentes bookmakers",
                    "Considere o valor das odds, não apenas o preço"
                ],
                warnings=[
                    "Odds podem mudar rapidamente",
                    "Odds baixas não garantem vitória"
                ],
                links=[
                    {"text": "Como ler odds", "url": "/help/reading-odds"},
                    {"text": "Comparador de odds", "url": "/tools/odds-comparison"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=300
            ),
            
            "bankroll_management": TooltipContent(
                title="Gestão de Bankroll",
                description="A gestão de bankroll é o controle do dinheiro disponível para apostas, incluindo tamanho das apostas e limites.",
                examples=[
                    "Bankroll R$ 1000, aposta R$ 50 = 5% do bankroll",
                    "Bankroll R$ 500, aposta R$ 25 = 5% do bankroll",
                    "Nunca aposte mais de 5% do bankroll em uma única aposta"
                ],
                tips=[
                    "Use apenas 1-5% do bankroll por aposta",
                    "Nunca aposte dinheiro que não pode perder",
                    "Mantenha um registro de todas as apostas",
                    "Ajuste o tamanho das apostas baseado na performance"
                ],
                warnings=[
                    "Apostar muito do bankroll pode levar à falência",
                    "Gestão inadequada é a principal causa de perdas"
                ],
                links=[
                    {"text": "Calculadora de bankroll", "url": "/tools/bankroll-calculator"},
                    {"text": "Estratégias de gestão", "url": "/help/bankroll-strategies"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=350
            ),
            
            "match_statistics": TooltipContent(
                title="Estatísticas da Partida",
                description="Estatísticas históricas das equipes que podem influenciar o resultado da partida.",
                examples=[
                    "Gols por jogo: média de gols marcados/sofridos",
                    "Forma recente: resultados dos últimos 5 jogos",
                    "Confronto direto: histórico entre as equipes"
                ],
                tips=[
                    "Considere estatísticas dos últimos 10 jogos",
                    "Atenção especial para jogos em casa/fora",
                    "Verifique lesões e suspensões importantes",
                    "Considere a importância da partida para cada time"
                ],
                warnings=[
                    "Estatísticas passadas não garantem resultados futuros",
                    "Considere o contexto de cada estatística"
                ],
                links=[
                    {"text": "Como interpretar estatísticas", "url": "/help/statistics"},
                    {"text": "Fatores importantes", "url": "/help/match-factors"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=300
            ),
            
            "prediction_model": TooltipContent(
                title="Modelo de Predição",
                description="O modelo de machine learning usado para gerar as predições, baseado em dados históricos e estatísticas.",
                examples=[
                    "Algoritmo: Random Forest com 100 árvores",
                    "Dados: Últimos 2 anos de partidas",
                    "Features: 50+ variáveis estatísticas"
                ],
                tips=[
                    "O modelo é treinado com dados históricos",
                    "Predições são atualizadas conforme novos dados",
                    "Diferentes modelos podem ter diferentes performances",
                    "Considere a confiança junto com a predição"
                ],
                warnings=[
                    "Modelos de ML não são 100% precisos",
                    "Performance passada não garante resultados futuros"
                ],
                links=[
                    {"text": "Como funciona o modelo", "url": "/help/prediction-model"},
                    {"text": "Precisão do modelo", "url": "/help/model-accuracy"}
                ],
                position=TooltipPosition.TOP,
                trigger=TooltipTrigger.HOVER,
                delay=500,
                max_width=300
            )
        }
        
        self.tooltips.update(default_tooltips)
    
    def get_tooltip(self, tooltip_id: str) -> Optional[TooltipContent]:
        """Obtém tooltip por ID"""
        return self.tooltips.get(tooltip_id)
    
    def add_tooltip(self, tooltip_id: str, content: TooltipContent):
        """Adiciona novo tooltip"""
        self.tooltips[tooltip_id] = content
    
    def get_tooltip_for_ui(self, tooltip_id: str) -> Optional[Dict[str, Any]]:
        """Obtém tooltip formatado para UI"""
        tooltip = self.get_tooltip(tooltip_id)
        if not tooltip:
            return None
        
        return {
            "id": tooltip_id,
            "title": tooltip.title,
            "description": tooltip.description,
            "examples": tooltip.examples,
            "tips": tooltip.tips,
            "warnings": tooltip.warnings,
            "links": tooltip.links,
            "position": tooltip.position.value,
            "trigger": tooltip.trigger.value,
            "delay": tooltip.delay,
            "max_width": tooltip.max_width
        }
    
    def get_all_tooltips(self) -> Dict[str, Dict[str, Any]]:
        """Obtém todos os tooltips formatados"""
        return {
            tooltip_id: self.get_tooltip_for_ui(tooltip_id)
            for tooltip_id in self.tooltips.keys()
        }
    
    def search_tooltips(self, query: str) -> List[Dict[str, Any]]:
        """Busca tooltips por palavra-chave"""
        query_lower = query.lower()
        results = []
        
        for tooltip_id, tooltip in self.tooltips.items():
            if (query_lower in tooltip.title.lower() or 
                query_lower in tooltip.description.lower() or
                any(query_lower in tip.lower() for tip in tooltip.tips)):
                results.append(self.get_tooltip_for_ui(tooltip_id))
        
        return results

class ContextualTooltipManager:
    """Gerenciador de tooltips contextuais"""
    
    def __init__(self):
        """Inicializa gerenciador contextual"""
        self.tooltip_manager = TooltipManager()
        self.context_mappings = {
            "prediction_page": [
                "prediction_confidence",
                "expected_value",
                "prediction_model"
            ],
            "analysis_page": [
                "roi",
                "win_rate",
                "bankroll_management"
            ],
            "odds_page": [
                "odds",
                "expected_value",
                "match_statistics"
            ],
            "betting_page": [
                "bankroll_management",
                "odds",
                "expected_value"
            ]
        }
    
    def get_tooltips_for_context(self, context: str) -> List[Dict[str, Any]]:
        """Obtém tooltips para um contexto específico"""
        tooltip_ids = self.context_mappings.get(context, [])
        return [
            self.tooltip_manager.get_tooltip_for_ui(tooltip_id)
            for tooltip_id in tooltip_ids
        ]
    
    def get_tooltip_suggestions(self, current_page: str, user_actions: List[str]) -> List[Dict[str, Any]]:
        """Obtém sugestões de tooltips baseadas no contexto"""
        suggestions = []
        
        # Tooltips baseados na página atual
        page_tooltips = self.get_tooltips_for_context(current_page)
        suggestions.extend(page_tooltips)
        
        # Tooltips baseados nas ações do usuário
        action_mappings = {
            "viewing_predictions": ["prediction_confidence", "prediction_model"],
            "analyzing_roi": ["roi", "win_rate"],
            "comparing_odds": ["odds", "expected_value"],
            "managing_bankroll": ["bankroll_management"],
            "viewing_statistics": ["match_statistics"]
        }
        
        for action in user_actions:
            if action in action_mappings:
                for tooltip_id in action_mappings[action]:
                    tooltip = self.tooltip_manager.get_tooltip_for_ui(tooltip_id)
                    if tooltip and tooltip not in suggestions:
                        suggestions.append(tooltip)
        
        return suggestions

# Instância global
tooltip_manager = TooltipManager()
contextual_tooltip_manager = ContextualTooltipManager()

if __name__ == "__main__":
    # Teste do sistema de tooltips
    print("🧪 TESTANDO SISTEMA DE TOOLTIPS")
    print("=" * 40)
    
    # Testar tooltip específico
    tooltip = tooltip_manager.get_tooltip_for_ui("prediction_confidence")
    if tooltip:
        print(f"Tooltip: {tooltip['title']}")
        print(f"Descrição: {tooltip['description']}")
        print(f"Exemplos: {len(tooltip['examples'])}")
        print(f"Dicas: {len(tooltip['tips'])}")
        print(f"Avisos: {len(tooltip['warnings'])}")
    
    # Testar busca
    search_results = tooltip_manager.search_tooltips("roi")
    print(f"\nBusca por 'roi': {len(search_results)} resultados")
    
    # Testar contexto
    context_tooltips = contextual_tooltip_manager.get_tooltips_for_context("prediction_page")
    print(f"Tooltips para página de predições: {len(context_tooltips)}")
    
    # Testar sugestões
    suggestions = contextual_tooltip_manager.get_tooltip_suggestions(
        "prediction_page", 
        ["viewing_predictions", "analyzing_roi"]
    )
    print(f"Sugestões contextuais: {len(suggestions)}")
    
    print("\n🎉 TESTES DE TOOLTIPS CONCLUÍDOS!")
