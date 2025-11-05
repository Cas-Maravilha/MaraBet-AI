"""
Cenários e Probabilidades - MaraBet AI
Sistema especializado para distribuição probabilística de gols e visualizações
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GoalScenario:
    """Cenário de gols"""
    goals: str
    probability: float
    bar_length: int
    bar_visual: str
    description: str

@dataclass
class ProbabilityDistribution:
    """Distribuição de probabilidades"""
    home_team: str
    away_team: str
    match_date: str
    scenarios: List[GoalScenario]
    over_2_5_probability: float
    under_2_5_probability: float
    probability_ratio: float
    most_likely_scenario: GoalScenario
    confidence_level: float
    analysis_timestamp: datetime

class ScenariosProbabilityAnalyzer:
    """
    Analisador de Cenários e Probabilidades
    Sistema completo para distribuição probabilística de gols
    """
    
    def __init__(self):
        self.scenario_templates = self._load_scenario_templates()
        self.probability_models = self._load_probability_models()
        self.visualization_config = self._load_visualization_config()
        
    def _load_scenario_templates(self) -> Dict[str, Dict]:
        """Carrega templates de cenários"""
        return {
            '0-1_goals': {
                'description': 'Jogo de poucos gols',
                'characteristics': ['Defesas sólidas', 'Ataques ineficazes', 'Jogo fechado'],
                'typical_odds': (1.8, 2.2)
            },
            '2_goals': {
                'description': 'Jogo equilibrado',
                'characteristics': ['Equilíbrio ofensivo', 'Defesas moderadas', 'Jogo controlado'],
                'typical_odds': (2.5, 3.5)
            },
            '3_goals': {
                'description': 'Jogo movimentado',
                'characteristics': ['Ataques eficazes', 'Defesas vulneráveis', 'Jogo aberto'],
                'typical_odds': (3.0, 4.0)
            },
            '4_goals': {
                'description': 'Jogo de muitos gols',
                'characteristics': ['Alta qualidade ofensiva', 'Defesas frágeis', 'Jogo muito aberto'],
                'typical_odds': (4.0, 6.0)
            },
            '5+_goals': {
                'description': 'Jogo de muitos gols',
                'characteristics': ['Excelência ofensiva', 'Defesas muito frágeis', 'Jogo extremamente aberto'],
                'typical_odds': (6.0, 15.0)
            }
        }
    
    def _load_probability_models(self) -> Dict[str, Dict]:
        """Carrega modelos de probabilidade"""
        return {
            'poisson': {
                'description': 'Modelo Poisson',
                'parameters': ['lambda_home', 'lambda_away'],
                'weight': 0.4
            },
            'negative_binomial': {
                'description': 'Modelo Binomial Negativo',
                'parameters': ['r', 'p'],
                'weight': 0.3
            },
            'zero_inflated': {
                'description': 'Modelo Zero-Inflated',
                'parameters': ['lambda', 'pi'],
                'weight': 0.3
            }
        }
    
    def _load_visualization_config(self) -> Dict[str, Any]:
        """Carrega configuração de visualização"""
        return {
            'max_bar_length': 20,
            'bar_character': '█',
            'bar_character_empty': '░',
            'show_percentages': True,
            'show_most_likely': True,
            'highlight_threshold': 0.25
        }
    
    def generate_goal_scenarios(self, home_team: str, away_team: str, 
                              match_data: Dict) -> List[GoalScenario]:
        """Gera cenários de gols baseados em dados da partida"""
        
        # Simula dados baseados no contexto da partida
        home_attack = match_data.get('home_form', 0.7)
        away_attack = match_data.get('away_form', 0.6)
        h2h_goals = match_data.get('h2h_goals_avg', 3.0)
        
        # Calcula probabilidades usando modelo Poisson simplificado
        lambda_home = 1.5 + (home_attack - 0.5) * 1.0  # 1.0 a 2.0
        lambda_away = 1.2 + (away_attack - 0.5) * 0.8  # 0.8 a 1.6
        lambda_total = lambda_home + lambda_away
        
        # Calcula probabilidades para cada cenário
        scenarios = []
        
        # 0-1 gols
        prob_0_1 = self._calculate_poisson_probability(0, lambda_total) + \
                  self._calculate_poisson_probability(1, lambda_total)
        scenarios.append(GoalScenario(
            goals="0-1 gols",
            probability=prob_0_1,
            bar_length=int(prob_0_1 * self.visualization_config['max_bar_length']),
            bar_visual=self._create_bar_visual(prob_0_1),
            description="Jogo de poucos gols"
        ))
        
        # 2 gols
        prob_2 = self._calculate_poisson_probability(2, lambda_total)
        scenarios.append(GoalScenario(
            goals="2 gols",
            probability=prob_2,
            bar_length=int(prob_2 * self.visualization_config['max_bar_length']),
            bar_visual=self._create_bar_visual(prob_2),
            description="Jogo equilibrado"
        ))
        
        # 3 gols
        prob_3 = self._calculate_poisson_probability(3, lambda_total)
        scenarios.append(GoalScenario(
            goals="3 gols",
            probability=prob_3,
            bar_length=int(prob_3 * self.visualization_config['max_bar_length']),
            bar_visual=self._create_bar_visual(prob_3),
            description="Jogo movimentado"
        ))
        
        # 4 gols
        prob_4 = self._calculate_poisson_probability(4, lambda_total)
        scenarios.append(GoalScenario(
            goals="4 gols",
            probability=prob_4,
            bar_length=int(prob_4 * self.visualization_config['max_bar_length']),
            bar_visual=self._create_bar_visual(prob_4),
            description="Jogo de muitos gols"
        ))
        
        # 5+ gols
        prob_5_plus = 1 - (prob_0_1 + prob_2 + prob_3 + prob_4)
        scenarios.append(GoalScenario(
            goals="5+ gols",
            probability=prob_5_plus,
            bar_length=int(prob_5_plus * self.visualization_config['max_bar_length']),
            bar_visual=self._create_bar_visual(prob_5_plus),
            description="Jogo de muitos gols"
        ))
        
        return scenarios
    
    def _calculate_poisson_probability(self, k: int, lambda_param: float) -> float:
        """Calcula probabilidade Poisson"""
        if lambda_param <= 0:
            return 0.0
        
        # Fórmula Poisson: P(X=k) = (λ^k * e^(-λ)) / k!
        if k == 0:
            return np.exp(-lambda_param)
        
        probability = np.exp(-lambda_param)
        for i in range(1, k + 1):
            probability *= lambda_param / i
        
        return probability
    
    def _create_bar_visual(self, probability: float) -> str:
        """Cria visualização em barra ASCII"""
        bar_length = int(probability * self.visualization_config['max_bar_length'])
        bar_char = self.visualization_config['bar_character']
        
        # Cria barra com caracteres
        bar = bar_char * bar_length
        
        # Adiciona caracteres vazios se necessário
        remaining = self.visualization_config['max_bar_length'] - bar_length
        if remaining > 0:
            bar += self.visualization_config['bar_character_empty'] * remaining
        
        return bar
    
    def calculate_over_under_probabilities(self, scenarios: List[GoalScenario]) -> Tuple[float, float]:
        """Calcula probabilidades Over/Under 2.5"""
        
        over_2_5 = 0.0
        under_2_5 = 0.0
        
        for scenario in scenarios:
            if scenario.goals == "0-1 gols":
                under_2_5 += scenario.probability
            elif scenario.goals == "2 gols":
                under_2_5 += scenario.probability
            elif scenario.goals == "3 gols":
                over_2_5 += scenario.probability
            elif scenario.goals == "4 gols":
                over_2_5 += scenario.probability
            elif scenario.goals == "5+ gols":
                over_2_5 += scenario.probability
        
        return over_2_5, under_2_5
    
    def calculate_probability_ratio(self, over_prob: float, under_prob: float) -> float:
        """Calcula razão de probabilidades"""
        if under_prob == 0:
            return float('inf')
        return over_prob / under_prob
    
    def find_most_likely_scenario(self, scenarios: List[GoalScenario]) -> GoalScenario:
        """Encontra cenário mais provável"""
        return max(scenarios, key=lambda x: x.probability)
    
    def calculate_confidence_level(self, scenarios: List[GoalScenario]) -> float:
        """Calcula nível de confiança baseado na distribuição"""
        if not scenarios:
            return 0.0
        
        # Confiança baseada na concentração de probabilidade
        max_prob = max(scenario.probability for scenario in scenarios)
        second_max = sorted([s.probability for s in scenarios], reverse=True)[1] if len(scenarios) > 1 else 0
        
        # Se há um cenário claramente dominante, confiança é alta
        if max_prob > 0.4 and max_prob > second_max * 1.5:
            return min(0.95, max_prob + 0.2)
        elif max_prob > 0.3:
            return max_prob
        else:
            return max_prob * 0.8
    
    def generate_probability_distribution(self, home_team: str, away_team: str, 
                                        match_date: str, match_data: Dict) -> ProbabilityDistribution:
        """Gera distribuição de probabilidades completa"""
        
        logger.info(f"Gerando distribuição de probabilidades: {home_team} vs {away_team}")
        
        try:
            # Gera cenários de gols
            scenarios = self.generate_goal_scenarios(home_team, away_team, match_data)
            
            # Calcula probabilidades Over/Under
            over_2_5, under_2_5 = self.calculate_over_under_probabilities(scenarios)
            
            # Calcula razão de probabilidades
            probability_ratio = self.calculate_probability_ratio(over_2_5, under_2_5)
            
            # Encontra cenário mais provável
            most_likely = self.find_most_likely_scenario(scenarios)
            
            # Calcula nível de confiança
            confidence = self.calculate_confidence_level(scenarios)
            
            return ProbabilityDistribution(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                scenarios=scenarios,
                over_2_5_probability=over_2_5,
                under_2_5_probability=under_2_5,
                probability_ratio=probability_ratio,
                most_likely_scenario=most_likely,
                confidence_level=confidence,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração da distribuição de probabilidades: {e}")
            return self._create_empty_distribution(home_team, away_team, match_date)
    
    def _create_empty_distribution(self, home_team: str, away_team: str, 
                                 match_date: str) -> ProbabilityDistribution:
        """Cria distribuição vazia em caso de erro"""
        return ProbabilityDistribution(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            scenarios=[],
            over_2_5_probability=0.0,
            under_2_5_probability=0.0,
            probability_ratio=0.0,
            most_likely_scenario=None,
            confidence_level=0.0,
            analysis_timestamp=datetime.now()
        )
    
    def format_probability_distribution(self, distribution: ProbabilityDistribution) -> str:
        """Formata distribuição de probabilidades"""
        
        if not distribution or not distribution.scenarios:
            return "Distribuição de probabilidades não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("CENÁRIOS E PROBABILIDADES")
        report_parts.append("=" * 60)
        report_parts.append(f"Partida: {distribution.home_team} vs {distribution.away_team}")
        report_parts.append(f"Data: {distribution.match_date}")
        report_parts.append("")
        
        # Distribuição probabilística de gols
        report_parts.append("DISTRIBUIÇÃO PROBABILÍSTICA DE GOLS:")
        report_parts.append("─" * 40)
        
        for scenario in distribution.scenarios:
            # Formata linha com barra visual
            line = f"{scenario.goals:>8}: {scenario.probability:>4.0%} {scenario.bar_visual}"
            
            # Adiciona indicador de mais provável
            if scenario == distribution.most_likely_scenario:
                line += " ← MAIS PROVÁVEL"
            
            report_parts.append(line)
        
        report_parts.append("")
        
        # Probabilidades Over/Under
        report_parts.append("PROBABILIDADES OVER/UNDER:")
        report_parts.append("─" * 40)
        report_parts.append(f"Probabilidade de Over 2.5: {distribution.over_2_5_probability:.0%}")
        report_parts.append(f"Probabilidade de Under 2.5: {distribution.under_2_5_probability:.0%}")
        report_parts.append("")
        
        # Razão de probabilidades
        report_parts.append("ANÁLISE DE PROBABILIDADES:")
        report_parts.append("─" * 40)
        report_parts.append(f"Razão de Probabilidades: {distribution.probability_ratio:.2f}")
        
        if distribution.probability_ratio > 2.0:
            report_parts.append("Interpretação: Forte favoritismo para Over 2.5")
        elif distribution.probability_ratio > 1.5:
            report_parts.append("Interpretação: Moderado favoritismo para Over 2.5")
        elif distribution.probability_ratio > 1.0:
            report_parts.append("Interpretação: Leve favoritismo para Over 2.5")
        else:
            report_parts.append("Interpretação: Favoritismo para Under 2.5")
        
        report_parts.append("")
        
        # Cenário mais provável
        if distribution.most_likely_scenario:
            report_parts.append("CENÁRIO MAIS PROVÁVEL:")
            report_parts.append("─" * 40)
            report_parts.append(f"Cenário: {distribution.most_likely_scenario.goals}")
            report_parts.append(f"Probabilidade: {distribution.most_likely_scenario.probability:.1%}")
            report_parts.append(f"Descrição: {distribution.most_likely_scenario.description}")
            report_parts.append("")
        
        # Nível de confiança
        report_parts.append("NÍVEL DE CONFIANÇA:")
        report_parts.append("─" * 40)
        report_parts.append(f"Confiança: {distribution.confidence_level:.1%}")
        
        if distribution.confidence_level > 0.8:
            report_parts.append("Interpretação: Alta confiança na distribuição")
        elif distribution.confidence_level > 0.6:
            report_parts.append("Interpretação: Confiança moderada na distribuição")
        else:
            report_parts.append("Interpretação: Baixa confiança na distribuição")
        
        return "\n".join(report_parts)

if __name__ == "__main__":
    # Teste do analisador de cenários e probabilidades
    analyzer = ScenariosProbabilityAnalyzer()
    
    print("=== TESTE DO ANALISADOR DE CENÁRIOS E PROBABILIDADES ===")
    
    # Dados de exemplo
    match_data = {
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_goals_avg': 3.0
    }
    
    # Gera distribuição de probabilidades
    distribution = analyzer.generate_probability_distribution(
        "Manchester City", "Arsenal", "2024-01-15", match_data
    )
    
    # Formata distribuição
    report = analyzer.format_probability_distribution(distribution)
    
    print(report)
    
    print("\nTeste concluído!")
