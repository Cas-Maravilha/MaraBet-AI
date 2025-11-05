"""
ETAPA 3: CÁLCULO DE PROBABILIDADES - MaraBet AI
Sistema especializado para cálculo de probabilidades com pesos específicos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProbabilityWeights:
    """Pesos para cálculo de probabilidades"""
    historico_recente: float = 0.40      # 40%
    confrontos_diretos: float = 0.25     # 25%
    estatisticas_avancadas: float = 0.15 # 15%
    fatores_contextuais: float = 0.10    # 10%
    analise_momentum: float = 0.10       # 10%
    
    def __post_init__(self):
        # Normaliza pesos para somar 1.0
        total = sum([self.historico_recente, self.confrontos_diretos, 
                    self.estatisticas_avancadas, self.fatores_contextuais, 
                    self.analise_momentum])
        
        if total > 0:
            self.historico_recente /= total
            self.confrontos_diretos /= total
            self.estatisticas_avancadas /= total
            self.fatores_contextuais /= total
            self.analise_momentum /= total

@dataclass
class ProbabilityResult:
    """Resultado do cálculo de probabilidades"""
    home_win: float
    draw: float
    away_win: float
    confidence: float
    breakdown: Dict[str, Dict[str, float]]
    weights_used: ProbabilityWeights
    calculation_method: str

class ProbabilityCalculator:
    """
    Calculador de Probabilidades com Pesos Específicos
    Implementa a estrutura: 40% Histórico + 25% H2H + 15% Avançadas + 10% Contexto + 10% Momentum
    """
    
    def __init__(self, weights: Optional[ProbabilityWeights] = None):
        self.weights = weights or ProbabilityWeights()
        self.calculation_history = []
        
    def calculate_probabilities(self, match_data: Dict) -> ProbabilityResult:
        """
        Calcula probabilidades usando a estrutura de pesos definida
        """
        logger.info("Calculando probabilidades com estrutura de pesos específica")
        
        try:
            # 1. Histórico Recente (40%)
            historico_probs = self._calculate_historico_recente(match_data)
            
            # 2. Confrontos Diretos (25%)
            h2h_probs = self._calculate_confrontos_diretos(match_data)
            
            # 3. Estatísticas Avançadas (15%)
            avancadas_probs = self._calculate_estatisticas_avancadas(match_data)
            
            # 4. Fatores Contextuais (10%)
            contextuais_probs = self._calculate_fatores_contextuais(match_data)
            
            # 5. Análise de Momentum (10%)
            momentum_probs = self._calculate_analise_momentum(match_data)
            
            # Combina probabilidades com pesos
            final_probs = self._combine_probabilities(
                historico_probs, h2h_probs, avancadas_probs, 
                contextuais_probs, momentum_probs
            )
            
            # Calcula confiança
            confidence = self._calculate_confidence(final_probs, match_data)
            
            # Cria breakdown detalhado
            breakdown = self._create_breakdown(
                historico_probs, h2h_probs, avancadas_probs,
                contextuais_probs, momentum_probs
            )
            
            result = ProbabilityResult(
                home_win=final_probs['home_win'],
                draw=final_probs['draw'],
                away_win=final_probs['away_win'],
                confidence=confidence,
                breakdown=breakdown,
                weights_used=self.weights,
                calculation_method='weighted_combination'
            )
            
            # Registra no histórico
            self.calculation_history.append({
                'timestamp': datetime.now(),
                'match': f"{match_data.get('home_team', '')} vs {match_data.get('away_team', '')}",
                'result': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no cálculo de probabilidades: {e}")
            # Retorna probabilidades neutras em caso de erro
            return ProbabilityResult(
                home_win=0.33, draw=0.34, away_win=0.33,
                confidence=0.0, breakdown={}, weights_used=self.weights,
                calculation_method='error_fallback'
            )
    
    def _calculate_historico_recente(self, match_data: Dict) -> Dict[str, float]:
        """
        Calcula probabilidades baseadas no histórico recente (40%)
        """
        logger.info("Calculando probabilidades do histórico recente")
        
        try:
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            # Simula dados do histórico recente
            home_recent = self._simulate_team_recent_form(home_team)
            away_recent = self._simulate_team_recent_form(away_team)
            
            # Calcula probabilidades baseadas na forma recente
            home_strength = self._calculate_team_strength(home_recent)
            away_strength = self._calculate_team_strength(away_recent)
            
            # Aplica fator casa
            home_advantage = 0.1  # 10% de vantagem em casa
            home_strength += home_advantage
            
            # Calcula probabilidades usando modelo logístico
            home_win_prob = self._logistic_probability(home_strength - away_strength)
            away_win_prob = self._logistic_probability(away_strength - home_strength)
            draw_prob = 1 - home_win_prob - away_win_prob
            
            # Normaliza
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            return {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob,
                'confidence': self._calculate_component_confidence(home_recent, away_recent)
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo do histórico recente: {e}")
            return {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33, 'confidence': 0.0}
    
    def _calculate_confrontos_diretos(self, match_data: Dict) -> Dict[str, float]:
        """
        Calcula probabilidades baseadas em confrontos diretos (25%)
        """
        logger.info("Calculando probabilidades dos confrontos diretos")
        
        try:
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            # Simula dados de confrontos diretos
            h2h_data = self._simulate_h2h_data(home_team, away_team)
            
            # Calcula probabilidades baseadas no H2H
            total_matches = h2h_data['total_matches']
            
            if total_matches == 0:
                return {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33, 'confidence': 0.0}
            
            home_wins = h2h_data['home_wins']
            draws = h2h_data['draws']
            away_wins = h2h_data['away_wins']
            
            # Probabilidades diretas do H2H
            home_win_prob = home_wins / total_matches
            draw_prob = draws / total_matches
            away_win_prob = away_wins / total_matches
            
            # Ajusta baseado na recência dos confrontos
            recency_factor = self._calculate_recency_factor(h2h_data)
            home_win_prob *= recency_factor
            away_win_prob *= recency_factor
            draw_prob *= recency_factor
            
            # Normaliza
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            return {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob,
                'confidence': min(total_matches / 10, 1.0)  # Confiança baseada no número de confrontos
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo dos confrontos diretos: {e}")
            return {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33, 'confidence': 0.0}
    
    def _calculate_estatisticas_avancadas(self, match_data: Dict) -> Dict[str, float]:
        """
        Calcula probabilidades baseadas em estatísticas avançadas (15%)
        """
        logger.info("Calculando probabilidades das estatísticas avançadas")
        
        try:
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            # Simula estatísticas avançadas
            home_advanced = self._simulate_advanced_stats(home_team)
            away_advanced = self._simulate_advanced_stats(away_team)
            
            # Calcula diferenças nas estatísticas
            xg_diff = home_advanced['xg_for'] - away_advanced['xg_for']
            possession_diff = home_advanced['possession'] - away_advanced['possession']
            shots_diff = home_advanced['shots_per_game'] - away_advanced['shots_per_game']
            defense_diff = away_advanced['xg_against'] - home_advanced['xg_against']
            
            # Combina estatísticas em score
            advanced_score = (
                xg_diff * 0.4 +           # xG é mais importante
                possession_diff * 0.2 +    # Posse de bola
                shots_diff * 0.2 +         # Finalizações
                defense_diff * 0.2         # Defesa
            )
            
            # Converte score em probabilidades
            home_win_prob = self._logistic_probability(advanced_score)
            away_win_prob = self._logistic_probability(-advanced_score)
            draw_prob = 1 - home_win_prob - away_win_prob
            
            # Normaliza
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            return {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob,
                'confidence': self._calculate_advanced_confidence(home_advanced, away_advanced)
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo das estatísticas avançadas: {e}")
            return {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33, 'confidence': 0.0}
    
    def _calculate_fatores_contextuais(self, match_data: Dict) -> Dict[str, float]:
        """
        Calcula probabilidades baseadas em fatores contextuais (10%)
        """
        logger.info("Calculando probabilidades dos fatores contextuais")
        
        try:
            # Simula fatores contextuais
            context = self._simulate_contextual_factors(match_data)
            
            # Calcula impacto dos fatores
            home_advantage = context['home_advantage']
            weather_impact = context['weather_impact']
            injury_impact = context['injury_impact']
            referee_impact = context['referee_impact']
            pressure_impact = context['pressure_impact']
            
            # Combina fatores contextuais
            contextual_score = (
                home_advantage * 0.3 +
                weather_impact * 0.2 +
                injury_impact * 0.2 +
                referee_impact * 0.15 +
                pressure_impact * 0.15
            )
            
            # Converte em probabilidades
            home_win_prob = self._logistic_probability(contextual_score)
            away_win_prob = self._logistic_probability(-contextual_score)
            draw_prob = 1 - home_win_prob - away_win_prob
            
            # Normaliza
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            return {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob,
                'confidence': self._calculate_contextual_confidence(context)
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo dos fatores contextuais: {e}")
            return {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33, 'confidence': 0.0}
    
    def _calculate_analise_momentum(self, match_data: Dict) -> Dict[str, float]:
        """
        Calcula probabilidades baseadas na análise de momentum (10%)
        """
        logger.info("Calculando probabilidades da análise de momentum")
        
        try:
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            # Simula dados de momentum
            home_momentum = self._simulate_team_momentum(home_team)
            away_momentum = self._simulate_team_momentum(away_team)
            
            # Calcula diferença de momentum
            momentum_diff = home_momentum['momentum'] - away_momentum['momentum']
            
            # Aplica fatores de momentum
            form_trend_diff = home_momentum['form_trend'] - away_momentum['form_trend']
            goals_momentum_diff = home_momentum['goals_momentum'] - away_momentum['goals_momentum']
            
            # Combina fatores de momentum
            total_momentum = (
                momentum_diff * 0.5 +
                form_trend_diff * 0.3 +
                goals_momentum_diff * 0.2
            )
            
            # Converte em probabilidades
            home_win_prob = self._logistic_probability(total_momentum)
            away_win_prob = self._logistic_probability(-total_momentum)
            draw_prob = 1 - home_win_prob - away_win_prob
            
            # Normaliza
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            return {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob,
                'confidence': self._calculate_momentum_confidence(home_momentum, away_momentum)
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo da análise de momentum: {e}")
            return {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33, 'confidence': 0.0}
    
    def _combine_probabilities(self, historico: Dict, h2h: Dict, avancadas: Dict, 
                             contextuais: Dict, momentum: Dict) -> Dict[str, float]:
        """
        Combina probabilidades usando os pesos definidos
        """
        # Aplica pesos
        home_win = (
            historico['home_win'] * self.weights.historico_recente +
            h2h['home_win'] * self.weights.confrontos_diretos +
            avancadas['home_win'] * self.weights.estatisticas_avancadas +
            contextuais['home_win'] * self.weights.fatores_contextuais +
            momentum['home_win'] * self.weights.analise_momentum
        )
        
        draw = (
            historico['draw'] * self.weights.historico_recente +
            h2h['draw'] * self.weights.confrontos_diretos +
            avancadas['draw'] * self.weights.estatisticas_avancadas +
            contextuais['draw'] * self.weights.fatores_contextuais +
            momentum['draw'] * self.weights.analise_momentum
        )
        
        away_win = (
            historico['away_win'] * self.weights.historico_recente +
            h2h['away_win'] * self.weights.confrontos_diretos +
            avancadas['away_win'] * self.weights.estatisticas_avancadas +
            contextuais['away_win'] * self.weights.fatores_contextuais +
            momentum['away_win'] * self.weights.analise_momentum
        )
        
        # Normaliza para garantir que soma = 1
        total = home_win + draw + away_win
        if total > 0:
            home_win /= total
            draw /= total
            away_win /= total
        
        return {
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win
        }
    
    def _calculate_confidence(self, final_probs: Dict, match_data: Dict) -> float:
        """
        Calcula confiança geral da predição
        """
        # Confiança baseada na clareza da predição
        max_prob = max(final_probs.values())
        clarity_confidence = (max_prob - 0.33) / 0.67  # Normaliza entre 0 e 1
        
        # Confiança baseada na consistência dos dados
        data_consistency = self._assess_data_consistency(match_data)
        
        # Confiança baseada na recência dos dados
        data_recency = self._assess_data_recency(match_data)
        
        # Combina fatores de confiança
        total_confidence = (
            clarity_confidence * 0.5 +
            data_consistency * 0.3 +
            data_recency * 0.2
        )
        
        return min(max(total_confidence, 0.0), 1.0)
    
    def _create_breakdown(self, historico: Dict, h2h: Dict, avancadas: Dict,
                         contextuais: Dict, momentum: Dict) -> Dict[str, Dict[str, float]]:
        """
        Cria breakdown detalhado das probabilidades por componente
        """
        return {
            'historico_recente': {
                'probabilities': {
                    'home_win': historico['home_win'],
                    'draw': historico['draw'],
                    'away_win': historico['away_win']
                },
                'weight': self.weights.historico_recente,
                'confidence': historico['confidence'],
                'contribution': {
                    'home_win': historico['home_win'] * self.weights.historico_recente,
                    'draw': historico['draw'] * self.weights.historico_recente,
                    'away_win': historico['away_win'] * self.weights.historico_recente
                }
            },
            'confrontos_diretos': {
                'probabilities': {
                    'home_win': h2h['home_win'],
                    'draw': h2h['draw'],
                    'away_win': h2h['away_win']
                },
                'weight': self.weights.confrontos_diretos,
                'confidence': h2h['confidence'],
                'contribution': {
                    'home_win': h2h['home_win'] * self.weights.confrontos_diretos,
                    'draw': h2h['draw'] * self.weights.confrontos_diretos,
                    'away_win': h2h['away_win'] * self.weights.confrontos_diretos
                }
            },
            'estatisticas_avancadas': {
                'probabilities': {
                    'home_win': avancadas['home_win'],
                    'draw': avancadas['draw'],
                    'away_win': avancadas['away_win']
                },
                'weight': self.weights.estatisticas_avancadas,
                'confidence': avancadas['confidence'],
                'contribution': {
                    'home_win': avancadas['home_win'] * self.weights.estatisticas_avancadas,
                    'draw': avancadas['draw'] * self.weights.estatisticas_avancadas,
                    'away_win': avancadas['away_win'] * self.weights.estatisticas_avancadas
                }
            },
            'fatores_contextuais': {
                'probabilities': {
                    'home_win': contextuais['home_win'],
                    'draw': contextuais['draw'],
                    'away_win': contextuais['away_win']
                },
                'weight': self.weights.fatores_contextuais,
                'confidence': contextuais['confidence'],
                'contribution': {
                    'home_win': contextuais['home_win'] * self.weights.fatores_contextuais,
                    'draw': contextuais['draw'] * self.weights.fatores_contextuais,
                    'away_win': contextuais['away_win'] * self.weights.fatores_contextuais
                }
            },
            'analise_momentum': {
                'probabilities': {
                    'home_win': momentum['home_win'],
                    'draw': momentum['draw'],
                    'away_win': momentum['away_win']
                },
                'weight': self.weights.analise_momentum,
                'confidence': momentum['confidence'],
                'contribution': {
                    'home_win': momentum['home_win'] * self.weights.analise_momentum,
                    'draw': momentum['draw'] * self.weights.analise_momentum,
                    'away_win': momentum['away_win'] * self.weights.analise_momentum
                }
            }
        }
    
    # Métodos auxiliares para simulação de dados
    def _simulate_team_recent_form(self, team_name: str) -> Dict:
        """Simula forma recente de um time"""
        import random
        np.random.seed(hash(team_name) % 2**32)
        
        return {
            'wins': random.randint(2, 5),
            'draws': random.randint(0, 2),
            'losses': random.randint(0, 3),
            'goals_scored': random.uniform(1.0, 2.5),
            'goals_conceded': random.uniform(0.8, 2.0),
            'form_trend': random.choice(['improving', 'stable', 'declining'])
        }
    
    def _simulate_h2h_data(self, home_team: str, away_team: str) -> Dict:
        """Simula dados de confrontos diretos"""
        import random
        np.random.seed(hash(f"{home_team}_{away_team}") % 2**32)
        
        total_matches = random.randint(3, 12)
        home_wins = random.randint(0, total_matches // 2)
        draws = random.randint(0, total_matches // 3)
        away_wins = total_matches - home_wins - draws
        
        return {
            'total_matches': total_matches,
            'home_wins': home_wins,
            'draws': draws,
            'away_wins': away_wins,
            'last_meeting_days_ago': random.randint(30, 365)
        }
    
    def _simulate_advanced_stats(self, team_name: str) -> Dict:
        """Simula estatísticas avançadas"""
        import random
        np.random.seed(hash(team_name) % 2**32)
        
        return {
            'xg_for': random.uniform(1.0, 2.5),
            'xg_against': random.uniform(0.8, 2.2),
            'possession': random.uniform(40, 70),
            'shots_per_game': random.uniform(8, 16),
            'pass_accuracy': random.uniform(75, 90)
        }
    
    def _simulate_contextual_factors(self, match_data: Dict) -> Dict:
        """Simula fatores contextuais"""
        import random
        
        return {
            'home_advantage': random.uniform(0.05, 0.15),
            'weather_impact': random.uniform(-0.1, 0.1),
            'injury_impact': random.uniform(-0.2, 0.2),
            'referee_impact': random.uniform(-0.05, 0.05),
            'pressure_impact': random.uniform(-0.1, 0.1)
        }
    
    def _simulate_team_momentum(self, team_name: str) -> Dict:
        """Simula momentum de um time"""
        import random
        np.random.seed(hash(team_name) % 2**32)
        
        return {
            'momentum': random.uniform(-0.5, 0.5),
            'form_trend': random.uniform(-0.3, 0.3),
            'goals_momentum': random.uniform(-0.4, 0.4)
        }
    
    # Métodos auxiliares para cálculos
    def _calculate_team_strength(self, team_data: Dict) -> float:
        """Calcula força de um time baseada nos dados"""
        wins = team_data['wins']
        draws = team_data['draws']
        losses = team_data['losses']
        
        points = wins * 3 + draws
        total_matches = wins + draws + losses
        
        if total_matches == 0:
            return 0.5
        
        # Normaliza pontos (0-1)
        max_points = total_matches * 3
        point_ratio = points / max_points
        
        # Ajusta por gols
        goal_ratio = team_data['goals_scored'] / (team_data['goals_scored'] + team_data['goals_conceded'])
        
        # Combina fatores
        strength = point_ratio * 0.7 + goal_ratio * 0.3
        
        return strength
    
    def _logistic_probability(self, score: float) -> float:
        """Converte score em probabilidade usando função logística"""
        return 1 / (1 + np.exp(-score))
    
    def _calculate_recency_factor(self, h2h_data: Dict) -> float:
        """Calcula fator de recência dos confrontos"""
        days_ago = h2h_data['last_meeting_days_ago']
        
        if days_ago <= 90:
            return 1.2  # Confrontos recentes têm mais peso
        elif days_ago <= 180:
            return 1.0
        elif days_ago <= 365:
            return 0.8
        else:
            return 0.6  # Confrontos antigos têm menos peso
    
    def _calculate_component_confidence(self, home_data: Dict, away_data: Dict) -> float:
        """Calcula confiança de um componente"""
        # Confiança baseada na consistência dos dados
        home_consistency = min(home_data['wins'] + home_data['draws'] + home_data['losses'], 10) / 10
        away_consistency = min(away_data['wins'] + away_data['draws'] + away_data['losses'], 10) / 10
        
        return (home_consistency + away_consistency) / 2
    
    def _calculate_advanced_confidence(self, home_stats: Dict, away_stats: Dict) -> float:
        """Calcula confiança das estatísticas avançadas"""
        # Confiança baseada na diferença clara nas estatísticas
        xg_diff = abs(home_stats['xg_for'] - away_stats['xg_for'])
        possession_diff = abs(home_stats['possession'] - away_stats['possession'])
        
        # Maior diferença = maior confiança
        confidence = min((xg_diff + possession_diff / 10) / 2, 1.0)
        
        return confidence
    
    def _calculate_contextual_confidence(self, context: Dict) -> float:
        """Calcula confiança dos fatores contextuais"""
        # Confiança baseada na magnitude dos fatores
        factors = [abs(context[key]) for key in context.keys()]
        avg_factor = np.mean(factors)
        
        return min(avg_factor * 2, 1.0)
    
    def _calculate_momentum_confidence(self, home_momentum: Dict, away_momentum: Dict) -> float:
        """Calcula confiança da análise de momentum"""
        # Confiança baseada na clareza da diferença de momentum
        momentum_diff = abs(home_momentum['momentum'] - away_momentum['momentum'])
        
        return min(momentum_diff * 2, 1.0)
    
    def _assess_data_consistency(self, match_data: Dict) -> float:
        """Avalia consistência dos dados"""
        # Simula avaliação de consistência
        return np.random.uniform(0.7, 0.9)
    
    def _assess_data_recency(self, match_data: Dict) -> float:
        """Avalia recência dos dados"""
        # Simula avaliação de recência
        return np.random.uniform(0.8, 1.0)
    
    def get_calculation_summary(self) -> Dict:
        """Retorna resumo dos cálculos realizados"""
        if not self.calculation_history:
            return {'total_calculations': 0}
        
        recent_calculations = self.calculation_history[-10:]  # Últimas 10
        
        avg_confidence = np.mean([calc['result'].confidence for calc in recent_calculations])
        
        return {
            'total_calculations': len(self.calculation_history),
            'recent_calculations': len(recent_calculations),
            'average_confidence': avg_confidence,
            'weights_used': {
                'historico_recente': self.weights.historico_recente,
                'confrontos_diretos': self.weights.confrontos_diretos,
                'estatisticas_avancadas': self.weights.estatisticas_avancadas,
                'fatores_contextuais': self.weights.fatores_contextuais,
                'analise_momentum': self.weights.analise_momentum
            }
        }

if __name__ == "__main__":
    # Teste do calculador de probabilidades
    print("=== TESTE DO CALCULADOR DE PROBABILIDADES ===")
    
    calculator = ProbabilityCalculator()
    
    # Dados de teste
    match_data = {
        'home_team': 'Flamengo',
        'away_team': 'Palmeiras',
        'date': '2024-01-15'
    }
    
    # Calcula probabilidades
    result = calculator.calculate_probabilities(match_data)
    
    print(f"\nProbabilidades Finais:")
    print(f"  Casa: {result.home_win:.3f} ({result.home_win*100:.1f}%)")
    print(f"  Empate: {result.draw:.3f} ({result.draw*100:.1f}%)")
    print(f"  Fora: {result.away_win:.3f} ({result.away_win*100:.1f}%)")
    print(f"  Confiança: {result.confidence:.3f}")
    
    print(f"\nBreakdown por Componente:")
    for component, data in result.breakdown.items():
        print(f"  {component}:")
        print(f"    Peso: {data['weight']:.1%}")
        print(f"    Confiança: {data['confidence']:.3f}")
        print(f"    Casa: {data['probabilities']['home_win']:.3f}")
        print(f"    Empate: {data['probabilities']['draw']:.3f}")
        print(f"    Fora: {data['probabilities']['away_win']:.3f}")
    
    print(f"\nResumo dos Cálculos:")
    summary = calculator.get_calculation_summary()
    print(f"  Total de cálculos: {summary['total_calculations']}")
    print(f"  Confiança média: {summary['average_confidence']:.3f}")
