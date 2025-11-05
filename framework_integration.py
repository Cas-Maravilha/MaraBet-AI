"""
Framework de Análise MaraBet AI - Integração
Conecta o framework avançado com o sistema existente
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import json

from data_framework import DataProcessor, AdvancedDataCollector
from advanced_features import AdvancedFeatureEngineer, FeatureSelector
from ml_models import BettingPredictor, BettingAnalyzer
from backtesting import BacktestingEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaraBetFramework:
    """Classe principal que integra todo o framework de análise"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.feature_engineer = AdvancedFeatureEngineer()
        self.feature_selector = FeatureSelector()
        self.predictor = BettingPredictor()
        self.analyzer = BettingAnalyzer(self.predictor)
        self.backtester = BacktestingEngine(self.predictor, self.analyzer)
        
    def analyze_match_comprehensive(self, home_team: str, away_team: str, match_date: str) -> Dict:
        """
        Análise abrangente de uma partida usando o framework completo
        """
        logger.info(f"Iniciando análise abrangente: {home_team} vs {away_team}")
        
        # 1. Coleta de dados completa
        match_analysis = self.data_processor.process_match_analysis(home_team, away_team, match_date)
        
        # 2. Criação de features avançadas
        features = self.feature_engineer.create_comprehensive_features(home_team, away_team, match_date)
        
        # 3. Seleção de features mais importantes
        selected_features = self.feature_selector.select_features(features)
        
        # 4. Análise preditiva
        prediction_analysis = self._create_prediction_analysis(selected_features, match_analysis)
        
        # 5. Recomendações de apostas
        betting_recommendations = self._create_betting_recommendations(prediction_analysis, match_analysis)
        
        # 6. Análise de risco
        risk_analysis = self._create_risk_analysis(match_analysis, prediction_analysis)
        
        # 7. Resumo executivo
        executive_summary = self._create_executive_summary(match_analysis, prediction_analysis, betting_recommendations)
        
        return {
            'match_info': {
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'data_analysis': match_analysis,
            'features': {
                'total_features': len(features),
                'selected_features': len(selected_features),
                'feature_list': list(selected_features.keys())
            },
            'prediction': prediction_analysis,
            'betting_recommendations': betting_recommendations,
            'risk_analysis': risk_analysis,
            'executive_summary': executive_summary
        }
    
    def analyze_multiple_matches(self, matches: List[Dict]) -> List[Dict]:
        """
        Analisa múltiplas partidas usando o framework
        """
        logger.info(f"Analisando {len(matches)} partidas")
        
        analyses = []
        for match in matches:
            try:
                analysis = self.analyze_match_comprehensive(
                    match['home_team'],
                    match['away_team'],
                    match['date']
                )
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Erro ao analisar partida {match}: {e}")
                continue
        
        return analyses
    
    def train_models_with_framework(self, historical_matches: List[Dict]) -> Dict:
        """
        Treina modelos usando o framework avançado
        """
        logger.info("Treinando modelos com framework avançado")
        
        # Prepara dados de treinamento
        training_data = []
        
        for match in historical_matches:
            try:
                # Cria features usando o framework
                features = self.feature_engineer.create_comprehensive_features(
                    match['home_team'],
                    match['away_team'],
                    match['date']
                )
                
                # Seleciona features importantes
                selected_features = self.feature_selector.select_features(features)
                
                # Adiciona resultado se disponível
                if 'result' in match:
                    selected_features['result'] = match['result']
                    selected_features['home_goals'] = match.get('home_goals', 0)
                    selected_features['away_goals'] = match.get('away_goals', 0)
                
                training_data.append(selected_features)
                
            except Exception as e:
                logger.error(f"Erro ao processar partida para treinamento: {e}")
                continue
        
        if not training_data:
            return {'success': False, 'error': 'Nenhum dado válido para treinamento'}
        
        # Converte para DataFrame
        df = pd.DataFrame(training_data)
        
        # Prepara dados para treinamento
        X, y, feature_columns = self.predictor.prepare_data(df)
        
        # Treina modelos
        X_test, y_test = self.predictor.train_models(X, y, feature_columns)
        
        # Salva modelos
        self.predictor.save_models()
        
        # Calcula métricas
        performance = {}
        for name, perf in self.predictor.model_performance.items():
            performance[name] = {
                'accuracy': perf['accuracy'],
                'features_used': len(feature_columns)
            }
        
        return {
            'success': True,
            'performance': performance,
            'training_samples': len(training_data),
            'features_used': feature_columns,
            'feature_importance': self.predictor.get_feature_importance_summary()
        }
    
    def run_framework_backtesting(self, historical_matches: List[Dict], initial_capital: float = 1000) -> Dict:
        """
        Executa backtesting usando o framework completo
        """
        logger.info("Executando backtesting com framework")
        
        # Treina modelos primeiro
        training_result = self.train_models_with_framework(historical_matches)
        if not training_result['success']:
            return {'success': False, 'error': 'Falha no treinamento dos modelos'}
        
        # Executa backtesting
        backtest_results = self.backtester.run_backtest(historical_matches, initial_capital=initial_capital)
        
        if not backtest_results:
            return {'success': False, 'error': 'Falha no backtesting'}
        
        # Adiciona análise do framework
        framework_analysis = self._analyze_framework_performance(backtest_results, historical_matches)
        
        return {
            'success': True,
            'backtest_results': backtest_results,
            'framework_analysis': framework_analysis,
            'training_performance': training_result['performance']
        }
    
    def _create_prediction_analysis(self, features: Dict, match_analysis: Dict) -> Dict:
        """Cria análise preditiva usando features do framework"""
        try:
            # Converte features para DataFrame
            features_df = pd.DataFrame([features])
            
            # Faz predição usando ensemble
            predictions, probabilities = self.predictor.ensemble_predict(features_df)
            
            if predictions is None:
                # Fallback para análise baseada em features
                return self._create_fallback_prediction(features, match_analysis)
            
            # Calcula odds
            odds = self.predictor.calculate_betting_odds(probabilities[0])
            
            return {
                'predicted_result': ['home_win', 'draw', 'away_win'][predictions[0]],
                'probabilities': {
                    'home_win': probabilities[0][0],
                    'draw': probabilities[0][1],
                    'away_win': probabilities[0][2]
                },
                'calculated_odds': {
                    'home': odds[0],
                    'draw': odds[1],
                    'away': odds[2]
                },
                'confidence': max(probabilities[0]),
                'prediction_method': 'ml_ensemble'
            }
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return self._create_fallback_prediction(features, match_analysis)
    
    def _create_fallback_prediction(self, features: Dict, match_analysis: Dict) -> Dict:
        """Cria predição baseada em features quando ML falha"""
        # Usa features do framework para predição simples
        home_win_rate = features.get('home_win_rate', 0.33)
        away_win_rate = features.get('away_win_rate', 0.33)
        draw_rate = 1 - home_win_rate - away_win_rate
        
        # Ajusta baseado em fatores do framework
        home_advantage = features.get('home_advantage', 0)
        form_difference = features.get('form_difference', 0)
        h2h_advantage = features.get('h2h_advantage', 0)
        
        # Aplica ajustes
        home_win_rate += (home_advantage * 0.1) + (form_difference * 0.05) + (h2h_advantage * 0.05)
        away_win_rate -= (home_advantage * 0.1) + (form_difference * 0.05) + (h2h_advantage * 0.05)
        
        # Normaliza
        total = home_win_rate + away_win_rate + draw_rate
        home_win_rate /= total
        away_win_rate /= total
        draw_rate /= total
        
        # Calcula odds
        odds = [1/home_win_rate, 1/draw_rate, 1/away_win_rate]
        
        return {
            'predicted_result': 'home_win' if home_win_rate > max(away_win_rate, draw_rate) else 
                               'away_win' if away_win_rate > draw_rate else 'draw',
            'probabilities': {
                'home_win': home_win_rate,
                'draw': draw_rate,
                'away_win': away_win_rate
            },
            'calculated_odds': {
                'home': odds[0],
                'draw': odds[1],
                'away': odds[2]
            },
            'confidence': max(home_win_rate, draw_rate, away_win_rate),
            'prediction_method': 'framework_features'
        }
    
    def _create_betting_recommendations(self, prediction: Dict, match_analysis: Dict) -> Dict:
        """Cria recomendações de apostas baseadas no framework"""
        recommendations = []
        
        # Simula odds de mercado (em produção, viria de API)
        market_odds = {
            'home': 2.0,
            'draw': 3.2,
            'away': 3.5
        }
        
        probabilities = prediction['probabilities']
        calculated_odds = prediction['calculated_odds']
        
        for outcome, prob in probabilities.items():
            market_odd = market_odds[outcome]
            calculated_odd = calculated_odds[outcome]
            
            # Calcula valor esperado
            ev = (prob * market_odd) - 1
            
            # Calcula Kelly Criterion
            kelly = (prob * market_odd - 1) / (market_odd - 1) if market_odd > 1 else 0
            kelly = max(0, min(kelly, 0.25))  # Limita entre 0 e 25%
            
            # Determina recomendação
            if ev > 0.15 and kelly > 0.03:
                recommendation = 'STRONG_BET'
            elif ev > 0.10 and kelly > 0.02:
                recommendation = 'BET'
            elif ev > 0.05:
                recommendation = 'CONSIDER'
            else:
                recommendation = 'AVOID'
            
            recommendations.append({
                'outcome': outcome,
                'probability': prob,
                'market_odds': market_odd,
                'calculated_odds': calculated_odd,
                'expected_value': ev,
                'kelly_percentage': kelly,
                'recommendation': recommendation,
                'confidence': prediction['confidence']
            })
        
        # Ordena por valor esperado
        recommendations.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return {
            'recommendations': recommendations,
            'best_bet': recommendations[0] if recommendations else None,
            'total_recommendations': len(recommendations),
            'strong_bets': len([r for r in recommendations if r['recommendation'] == 'STRONG_BET']),
            'avoid_bets': len([r for r in recommendations if r['recommendation'] == 'AVOID'])
        }
    
    def _create_risk_analysis(self, match_analysis: Dict, prediction: Dict) -> Dict:
        """Cria análise de risco baseada no framework"""
        # Analisa fatores de risco
        risk_factors = []
        risk_score = 0
        
        # Risco baseado em forma
        home_form = match_analysis['home_team_analysis']['recent_form']['form']
        away_form = match_analysis['away_team_analysis']['recent_form']['form']
        
        if home_form == 'poor' or away_form == 'poor':
            risk_factors.append('Forma ruim de um dos times')
            risk_score += 2
        
        # Risco baseado em lesões
        home_injuries = len(match_analysis['match_context'].home_team_injuries)
        away_injuries = len(match_analysis['match_context'].away_team_injuries)
        
        if home_injuries > 3 or away_injuries > 3:
            risk_factors.append('Muitas lesões')
            risk_score += 1
        
        # Risco baseado em pressão competitiva
        home_pressure = match_analysis['home_team_analysis']['competitive_context']['pressure_level']
        away_pressure = match_analysis['away_team_analysis']['competitive_context']['pressure_level']
        
        if home_pressure == 'high' and away_pressure == 'high':
            risk_factors.append('Alta pressão competitiva')
            risk_score += 1
        
        # Risco baseado em confiança da predição
        confidence = prediction['confidence']
        if confidence < 0.6:
            risk_factors.append('Baixa confiança na predição')
            risk_score += 2
        
        # Determina nível de risco
        if risk_score >= 5:
            risk_level = 'HIGH'
        elif risk_score >= 3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'confidence': confidence,
            'recommendation': 'AVOID' if risk_level == 'HIGH' else 'CAUTION' if risk_level == 'MEDIUM' else 'NORMAL'
        }
    
    def _create_executive_summary(self, match_analysis: Dict, prediction: Dict, betting: Dict) -> Dict:
        """Cria resumo executivo da análise"""
        home_team = match_analysis['match_info']['home_team']
        away_team = match_analysis['match_info']['away_team']
        
        # Análise dos times
        home_form = match_analysis['home_team_analysis']['recent_form']['form']
        away_form = match_analysis['away_team_analysis']['recent_form']['form']
        
        home_position = match_analysis['home_team_analysis']['competitive_context']['position']
        away_position = match_analysis['away_team_analysis']['competitive_context']['position']
        
        # Predição
        predicted_result = prediction['predicted_result']
        confidence = prediction['confidence']
        
        # Melhor aposta
        best_bet = betting['best_bet']
        
        # Cria resumo
        summary = {
            'match': f"{home_team} vs {away_team}",
            'prediction': {
                'result': predicted_result,
                'confidence': f"{confidence:.1%}",
                'method': prediction['prediction_method']
            },
            'team_analysis': {
                'home_team': {
                    'form': home_form,
                    'position': home_position,
                    'recent_trend': match_analysis['home_team_analysis']['recent_form']['trend']
                },
                'away_team': {
                    'form': away_form,
                    'position': away_position,
                    'recent_trend': match_analysis['away_team_analysis']['recent_form']['trend']
                }
            },
            'betting_analysis': {
                'best_bet': best_bet['outcome'] if best_bet else 'N/A',
                'expected_value': f"{best_bet['expected_value']:.1%}" if best_bet else 'N/A',
                'recommendation': best_bet['recommendation'] if best_bet else 'N/A',
                'total_options': betting['total_recommendations']
            },
            'key_insights': self._generate_key_insights(match_analysis, prediction, betting)
        }
        
        return summary
    
    def _generate_key_insights(self, match_analysis: Dict, prediction: Dict, betting: Dict) -> List[str]:
        """Gera insights-chave da análise"""
        insights = []
        
        # Insight sobre forma
        home_form = match_analysis['home_team_analysis']['recent_form']['form']
        away_form = match_analysis['away_team_analysis']['recent_form']['form']
        
        if home_form == 'excellent' and away_form == 'poor':
            insights.append(f"Forte vantagem de forma para o time da casa")
        elif away_form == 'excellent' and home_form == 'poor':
            insights.append(f"Forte vantagem de forma para o time visitante")
        
        # Insight sobre posição
        home_pos = match_analysis['home_team_analysis']['competitive_context']['position']
        away_pos = match_analysis['away_team_analysis']['competitive_context']['position']
        
        if abs(home_pos - away_pos) > 10:
            insights.append(f"Grande diferença de posição na tabela ({home_pos} vs {away_pos})")
        
        # Insight sobre H2H
        h2h_advantage = match_analysis['comparative_analysis']['head_to_head_summary']['home_h2h_advantage']
        if abs(h2h_advantage) > 0.3:
            insights.append(f"Histórico de confrontos favorável a um dos times")
        
        # Insight sobre apostas
        if betting['strong_bets'] > 0:
            insights.append(f"Encontradas {betting['strong_bets']} oportunidades de apostas fortes")
        elif betting['avoid_bets'] == betting['total_recommendations']:
            insights.append("Todas as apostas apresentam baixo valor esperado")
        
        return insights
    
    def _analyze_framework_performance(self, backtest_results: Dict, historical_matches: List[Dict]) -> Dict:
        """Analisa performance do framework no backtesting"""
        metrics = backtest_results['metrics']
        
        # Análise de performance
        performance_analysis = {
            'roi': metrics['roi'],
            'win_rate': metrics['win_rate'],
            'total_trades': metrics['total_trades'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'max_drawdown': metrics['max_drawdown']
        }
        
        # Análise por tipo de aposta
        bet_analysis = metrics.get('bet_analysis', {})
        
        # Análise de features
        feature_importance = self.predictor.get_feature_importance_summary()
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'performance': performance_analysis,
            'bet_analysis': bet_analysis,
            'top_features': top_features,
            'framework_effectiveness': 'HIGH' if metrics['roi'] > 10 else 'MEDIUM' if metrics['roi'] > 0 else 'LOW'
        }

if __name__ == "__main__":
    # Teste do framework integrado
    framework = MaraBetFramework()
    
    print("=== TESTE DO FRAMEWORK INTEGRADO ===")
    
    # Teste análise de partida
    analysis = framework.analyze_match_comprehensive('Flamengo', 'Palmeiras', '2024-01-15')
    
    print(f"\nAnálise da partida:")
    print(f"Predição: {analysis['prediction']['predicted_result']}")
    print(f"Confiança: {analysis['prediction']['confidence']:.1%}")
    print(f"Total de features: {analysis['features']['total_features']}")
    print(f"Features selecionadas: {analysis['features']['selected_features']}")
    
    if analysis['betting_recommendations']['best_bet']:
        best = analysis['betting_recommendations']['best_bet']
        print(f"Melhor aposta: {best['outcome']} (EV: {best['expected_value']:.1%})")
    
    print(f"Nível de risco: {analysis['risk_analysis']['risk_level']}")
    
    print("\nResumo executivo:")
    summary = analysis['executive_summary']
    print(f"Match: {summary['match']}")
    print(f"Predição: {summary['prediction']['result']} ({summary['prediction']['confidence']})")
    print(f"Insights: {', '.join(summary['key_insights'])}")
