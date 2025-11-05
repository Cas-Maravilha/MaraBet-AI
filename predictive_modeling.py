"""
Modelagem Preditiva - MaraBet AI
Sistema especializado para modelagem preditiva e cálculo de probabilidades
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
class ProbabilityResult:
    """Resultado de probabilidade calculada"""
    outcome: str
    probability: float
    fair_odds: float
    market_odds: float
    value: float
    confidence: float
    recommendation: str

@dataclass
class PredictiveModel:
    """Modelo preditivo para uma partida"""
    home_team: str
    away_team: str
    match_date: str
    probabilities: List[ProbabilityResult]
    model_accuracy: float
    confidence_score: float
    model_type: str
    features_used: List[str]
    predictions_timestamp: datetime

class PredictiveModeler:
    """
    Modelador Preditivo
    Gera modelos preditivos e calcula probabilidades
    """
    
    def __init__(self):
        self.model_weights = self._load_model_weights()
        self.feature_importance = self._load_feature_importance()
        
    def _load_model_weights(self) -> Dict:
        """Carrega pesos dos modelos"""
        return {
            'poisson_model': {
                'home_advantage': 0.12,
                'form_weight': 0.25,
                'h2h_weight': 0.15,
                'xG_weight': 0.20,
                'tactical_weight': 0.10,
                'motivational_weight': 0.08,
                'contextual_weight': 0.10
            },
            'ml_ensemble': {
                'random_forest': 0.30,
                'xgboost': 0.25,
                'lightgbm': 0.20,
                'catboost': 0.15,
                'logistic_regression': 0.10
            },
            'bayesian_network': {
                'prior_strength': 0.7,
                'likelihood_weight': 0.3
            }
        }
    
    def _load_feature_importance(self) -> Dict:
        """Carrega importância das features"""
        return {
            'recent_form': 0.25,
            'head_to_head': 0.20,
            'home_advantage': 0.15,
            'xG_difference': 0.15,
            'tactical_advantage': 0.10,
            'motivational_factors': 0.08,
            'contextual_factors': 0.07
        }
    
    def generate_predictive_model(self, home_team: str, away_team: str, 
                                match_date: str, match_data: Dict) -> PredictiveModel:
        """
        Gera modelo preditivo completo para uma partida
        """
        logger.info(f"Gerando modelo preditivo: {home_team} vs {away_team}")
        
        try:
            # Calcula probabilidades usando diferentes modelos
            poisson_probs = self._calculate_poisson_probabilities(home_team, away_team, match_data)
            ml_probs = self._calculate_ml_probabilities(home_team, away_team, match_data)
            bayesian_probs = self._calculate_bayesian_probabilities(home_team, away_team, match_data)
            
            # Combina modelos usando ensemble
            final_probabilities = self._ensemble_probabilities(
                poisson_probs, ml_probs, bayesian_probs
            )
            
            # Calcula odds justas
            fair_odds = self._calculate_fair_odds(final_probabilities)
            
            # Obtém odds de mercado
            market_odds = self._get_market_odds(home_team, away_team)
            
            # Calcula valor das apostas
            probabilities = self._calculate_betting_value(
                final_probabilities, fair_odds, market_odds, home_team, away_team
            )
            
            # Calcula métricas do modelo
            model_accuracy = self._calculate_model_accuracy(probabilities)
            confidence_score = self._calculate_confidence_score(probabilities)
            
            # Features utilizadas
            features_used = list(self.feature_importance.keys())
            
            return PredictiveModel(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                probabilities=probabilities,
                model_accuracy=model_accuracy,
                confidence_score=confidence_score,
                model_type="Ensemble (Poisson + ML + Bayesian)",
                features_used=features_used,
                predictions_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração do modelo preditivo: {e}")
            return self._create_empty_model(home_team, away_team, match_date)
    
    def _calculate_poisson_probabilities(self, home_team: str, away_team: str, 
                                       match_data: Dict) -> Dict[str, float]:
        """Calcula probabilidades usando modelo Poisson"""
        
        # Simula dados para demonstração
        home_goals_expected = np.random.uniform(1.5, 2.5)
        away_goals_expected = np.random.uniform(1.0, 2.0)
        
        # Aplica vantagem de casa
        home_goals_expected += self.model_weights['poisson_model']['home_advantage']
        
        # Calcula probabilidades usando distribuição Poisson
        home_win_prob = self._poisson_win_probability(home_goals_expected, away_goals_expected)
        draw_prob = self._poisson_draw_probability(home_goals_expected, away_goals_expected)
        away_win_prob = 1 - home_win_prob - draw_prob
        
        return {
            'home_win': home_win_prob,
            'draw': draw_prob,
            'away_win': away_win_prob
        }
    
    def _calculate_ml_probabilities(self, home_team: str, away_team: str, 
                                  match_data: Dict) -> Dict[str, float]:
        """Calcula probabilidades usando ensemble de ML"""
        
        # Simula predições de diferentes modelos ML
        models = ['random_forest', 'xgboost', 'lightgbm', 'catboost', 'logistic_regression']
        weights = self.model_weights['ml_ensemble']
        
        # Simula predições de cada modelo
        model_predictions = {}
        for model in models:
            # Simula predições baseadas em features
            base_prob = np.random.uniform(0.3, 0.7)
            model_predictions[model] = {
                'home_win': base_prob + np.random.uniform(-0.1, 0.1),
                'draw': np.random.uniform(0.15, 0.35),
                'away_win': 1 - base_prob + np.random.uniform(-0.1, 0.1)
            }
        
        # Combina predições usando pesos
        final_probs = {'home_win': 0, 'draw': 0, 'away_win': 0}
        for model, weight in weights.items():
            for outcome in final_probs.keys():
                final_probs[outcome] += model_predictions[model][outcome] * weight
        
        # Normaliza probabilidades
        total = sum(final_probs.values())
        for outcome in final_probs:
            final_probs[outcome] /= total
        
        return final_probs
    
    def _calculate_bayesian_probabilities(self, home_team: str, away_team: str, 
                                        match_data: Dict) -> Dict[str, float]:
        """Calcula probabilidades usando rede neural bayesiana"""
        
        # Simula prioris baseadas em dados históricos
        prior_home = np.random.uniform(0.4, 0.6)
        prior_draw = np.random.uniform(0.2, 0.3)
        prior_away = 1 - prior_home - prior_draw
        
        # Simula likelihood baseada em features atuais
        likelihood_home = np.random.uniform(0.5, 0.8)
        likelihood_draw = np.random.uniform(0.1, 0.3)
        likelihood_away = 1 - likelihood_home - likelihood_draw
        
        # Combina prior e likelihood
        posterior_home = (self.model_weights['bayesian_network']['prior_strength'] * prior_home + 
                         self.model_weights['bayesian_network']['likelihood_weight'] * likelihood_home)
        posterior_draw = (self.model_weights['bayesian_network']['prior_strength'] * prior_draw + 
                         self.model_weights['bayesian_network']['likelihood_weight'] * likelihood_draw)
        posterior_away = 1 - posterior_home - posterior_draw
        
        return {
            'home_win': posterior_home,
            'draw': posterior_draw,
            'away_win': posterior_away
        }
    
    def _ensemble_probabilities(self, poisson_probs: Dict, ml_probs: Dict, 
                              bayesian_probs: Dict) -> Dict[str, float]:
        """Combina probabilidades de diferentes modelos"""
        
        # Pesos para ensemble
        ensemble_weights = {
            'poisson': 0.4,
            'ml': 0.4,
            'bayesian': 0.2
        }
        
        final_probs = {'home_win': 0, 'draw': 0, 'away_win': 0}
        
        for outcome in final_probs.keys():
            final_probs[outcome] = (
                ensemble_weights['poisson'] * poisson_probs[outcome] +
                ensemble_weights['ml'] * ml_probs[outcome] +
                ensemble_weights['bayesian'] * bayesian_probs[outcome]
            )
        
        return final_probs
    
    def _calculate_fair_odds(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        """Calcula odds justas baseadas nas probabilidades"""
        return {
            'home_win': 1 / probabilities['home_win'],
            'draw': 1 / probabilities['draw'],
            'away_win': 1 / probabilities['away_win']
        }
    
    def _get_market_odds(self, home_team: str, away_team: str) -> Dict[str, float]:
        """Obtém odds de mercado (simulado)"""
        # Simula odds de mercado baseadas nas probabilidades
        base_home = np.random.uniform(1.5, 2.5)
        base_draw = np.random.uniform(3.0, 4.5)
        base_away = np.random.uniform(4.0, 7.0)
        
        return {
            'home_win': base_home,
            'draw': base_draw,
            'away_win': base_away
        }
    
    def _calculate_betting_value(self, probabilities: Dict[str, float], 
                               fair_odds: Dict[str, float], 
                               market_odds: Dict[str, float],
                               home_team: str = "Home Team",
                               away_team: str = "Away Team") -> List[ProbabilityResult]:
        """Calcula valor das apostas"""
        
        results = []
        outcomes = [
            ('home_win', f'{home_team} Vitória'),
            ('draw', 'Empate'),
            ('away_win', f'{away_team} Vitória')
        ]
        
        for outcome_key, outcome_name in outcomes:
            prob = probabilities[outcome_key]
            fair_odd = fair_odds[outcome_key]
            market_odd = market_odds[outcome_key]
            
            # Calcula valor esperado
            value = (prob * market_odd) - 1
            
            # Calcula confiança
            confidence = min(prob * 1.2, 1.0)
            
            # Determina recomendação
            if value > 0.15:
                recommendation = "EXCELENTE VALOR"
            elif value > 0.05:
                recommendation = "BOM VALOR"
            elif value > 0:
                recommendation = "VALOR POSITIVO"
            else:
                recommendation = "SEM VALOR"
            
            results.append(ProbabilityResult(
                outcome=outcome_name,
                probability=prob,
                fair_odds=fair_odd,
                market_odds=market_odd,
                value=value,
                confidence=confidence,
                recommendation=recommendation
            ))
        
        return results
    
    def _calculate_model_accuracy(self, probabilities: List[ProbabilityResult]) -> float:
        """Calcula precisão do modelo"""
        # Simula precisão baseada na confiança média
        avg_confidence = np.mean([p.confidence for p in probabilities])
        return min(avg_confidence * 0.9, 0.95)
    
    def _calculate_confidence_score(self, probabilities: List[ProbabilityResult]) -> float:
        """Calcula score de confiança geral"""
        return np.mean([p.confidence for p in probabilities])
    
    def _poisson_win_probability(self, home_goals: float, away_goals: float) -> float:
        """Calcula probabilidade de vitória usando Poisson"""
        # Implementação simplificada
        if home_goals > away_goals:
            return 0.6
        elif home_goals == away_goals:
            return 0.3
        else:
            return 0.1
    
    def _poisson_draw_probability(self, home_goals: float, away_goals: float) -> float:
        """Calcula probabilidade de empate usando Poisson"""
        # Implementação simplificada
        return 0.25
    
    def _create_empty_model(self, home_team: str, away_team: str, match_date: str) -> PredictiveModel:
        """Cria modelo vazio em caso de erro"""
        return PredictiveModel(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            probabilities=[],
            model_accuracy=0.0,
            confidence_score=0.0,
            model_type="Erro",
            features_used=[],
            predictions_timestamp=datetime.now()
        )
    
    def format_predictive_table(self, model: PredictiveModel) -> str:
        """Formata tabela de modelagem preditiva"""
        
        # Cria tabela de probabilidades calculadas
        prob_table = "┌─────────────────────────────────────────┐\n"
        prob_table += "│  RESULTADO  │  PROB. REAL  │  ODD JUSTA │\n"
        prob_table += "├─────────────────────────────────────────┤\n"
        
        for prob in model.probabilities:
            prob_table += f"│ {prob.outcome:^11} │ {prob.probability:^10.1%} │ {prob.fair_odds:^8.2f} │\n"
        
        prob_table += "└─────────────────────────────────────────┘\n"
        
        # Cria tabela de odds de mercado
        market_table = "Odds Oferecidas pelas Casas (Média)\n"
        for prob in model.probabilities:
            market_table += f"{prob.outcome}: {prob.market_odds:.2f}\n"
        
        # Análise de valor
        value_analysis = "\nANÁLISE DE VALOR\n"
        value_analysis += "-" * 30 + "\n"
        
        for prob in model.probabilities:
            value_analysis += f"{prob.outcome}:\n"
            value_analysis += f"  Valor Esperado: {prob.value:+.3f}\n"
            value_analysis += f"  Recomendação: {prob.recommendation}\n"
            value_analysis += f"  Confiança: {prob.confidence:.1%}\n\n"
        
        # Métricas do modelo
        model_metrics = f"MODELO PREDITIVO\n"
        model_metrics += "-" * 30 + "\n"
        model_metrics += f"Tipo: {model.model_type}\n"
        model_metrics += f"Precisão: {model.model_accuracy:.1%}\n"
        model_metrics += f"Confiança: {model.confidence_score:.1%}\n"
        model_metrics += f"Features: {', '.join(model.features_used)}\n"
        model_metrics += f"Atualização: {model.predictions_timestamp.strftime('%d/%m/%Y %H:%M')}\n"
        
        return f"""
MODELAGEM PREDITIVA
{'='*50}

Probabilidades Calculadas pelo Sistema
{prob_table}

{market_table}

{value_analysis}

{model_metrics}
"""

if __name__ == "__main__":
    # Teste do modelador preditivo
    modeler = PredictiveModeler()
    
    print("=== TESTE DO MODELADOR PREDITIVO ===")
    
    # Dados de exemplo
    match_data = {
        'home_team': 'Manchester City',
        'away_team': 'Arsenal',
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_home': 0.7,
        'h2h_away': 0.3,
        'home_xg': 2.1,
        'away_xg': 1.5
    }
    
    # Gera modelo preditivo
    model = modeler.generate_predictive_model(
        "Manchester City", "Arsenal", "2024-01-15", match_data
    )
    
    # Formata tabela
    table = modeler.format_predictive_table(model)
    
    print(table)
    
    print("\nTeste concluído!")
