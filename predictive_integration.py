"""
Integração dos Modelos Preditivos - MaraBet AI
Conecta os modelos preditivos avançados com o framework de análise
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import json

from predictive_models import (
    PoissonModel, MLEnsemble, AdvancedLogisticRegression, 
    BayesianNeuralNetworkWrapper, PredictiveModelEnsemble
)
from framework_integration import MaraBetFramework
from data_framework import DataProcessor
from advanced_features import AdvancedFeatureEngineer, FeatureSelector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedPredictiveSystem:
    """
    Sistema Avançado de Predição
    Integra todos os modelos preditivos com o framework de análise
    """
    
    def __init__(self):
        self.framework = MaraBetFramework()
        self.data_processor = DataProcessor()
        self.feature_engineer = AdvancedFeatureEngineer()
        self.feature_selector = FeatureSelector()
        self.predictive_ensemble = PredictiveModelEnsemble()
        self.trained = False
        
    def train_advanced_models(self, historical_matches: List[Dict]) -> Dict:
        """
        Treina todos os modelos preditivos avançados
        """
        logger.info("Treinando modelos preditivos avançados...")
        
        try:
            # Converte para DataFrame
            matches_df = pd.DataFrame(historical_matches)
            
            # Prepara dados de treinamento
            training_data = []
            feature_columns = []
            
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
                    
                    # Coleta colunas de features
                    if not feature_columns:
                        feature_columns = [k for k in selected_features.keys() 
                                         if k not in ['result', 'home_goals', 'away_goals']]
                    
                except Exception as e:
                    logger.error(f"Erro ao processar partida para treinamento: {e}")
                    continue
            
            if not training_data:
                return {'success': False, 'error': 'Nenhum dado válido para treinamento'}
            
            # Converte para DataFrame
            df = pd.DataFrame(training_data)
            
            # Prepara dados para treinamento
            X = df[feature_columns].fillna(0)
            y = df['result'].map({'win': 0, 'draw': 1, 'loss': 2}) if 'result' in df.columns else np.random.choice([0, 1, 2], len(df))
            
            # Treina ensemble preditivo
            self.predictive_ensemble.fit(matches_df, X, y, feature_columns)
            
            self.trained = True
            
            # Avalia performance
            performance = self._evaluate_models(X, y, feature_columns)
            
            return {
                'success': True,
                'performance': performance,
                'training_samples': len(training_data),
                'features_used': feature_columns,
                'models_trained': ['poisson', 'ml_ensemble', 'logistic_regression', 'bayesian_nn']
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento dos modelos avançados: {e}")
            return {'success': False, 'error': str(e)}
    
    def predict_advanced(self, home_team: str, away_team: str, match_date: str) -> Dict:
        """
        Faz predição avançada usando todos os modelos
        """
        logger.info(f"Fazendo predição avançada: {home_team} vs {away_team}")
        
        if not self.trained:
            raise ValueError("Modelos não foram treinados. Execute train_advanced_models() primeiro.")
        
        try:
            # Análise completa usando o framework
            match_analysis = self.data_processor.process_match_analysis(home_team, away_team, match_date)
            
            # Cria features avançadas
            features = self.feature_engineer.create_comprehensive_features(home_team, away_team, match_date)
            selected_features = self.feature_selector.select_features(features)
            
            # Prepara dados para predição
            feature_columns = list(selected_features.keys())
            X = pd.DataFrame([selected_features])
            
            # Dados dos times para modelo Poisson
            home_team_stats = match_analysis['home_team_analysis']
            away_team_stats = match_analysis['away_team_analysis']
            
            # Predição usando ensemble completo
            prediction = self.predictive_ensemble.predict(
                home_team, away_team, home_team_stats, away_team_stats, X, feature_columns
            )
            
            # Análise de incerteza e confiança
            uncertainty_analysis = self._analyze_uncertainty(prediction)
            
            # Recomendações baseadas em todos os modelos
            recommendations = self._create_advanced_recommendations(prediction, match_analysis)
            
            # Análise de risco avançada
            risk_analysis = self._create_advanced_risk_analysis(prediction, match_analysis, uncertainty_analysis)
            
            return {
                'match_info': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match_date,
                    'analysis_timestamp': datetime.now().isoformat()
                },
                'prediction': prediction,
                'uncertainty_analysis': uncertainty_analysis,
                'recommendations': recommendations,
                'risk_analysis': risk_analysis,
                'model_insights': self._generate_model_insights(prediction),
                'data_analysis': match_analysis
            }
            
        except Exception as e:
            logger.error(f"Erro na predição avançada: {e}")
            return None
    
    def _evaluate_models(self, X: pd.DataFrame, y: pd.Series, feature_columns: List[str]) -> Dict:
        """Avalia performance dos modelos individuais"""
        performance = {}
        
        try:
            # Avalia ML Ensemble
            if hasattr(self.predictive_ensemble.ml_ensemble, 'models'):
                for name, model in self.predictive_ensemble.ml_ensemble.models.items():
                    try:
                        if name == 'logistic_regression':
                            X_scaled = self.predictive_ensemble.ml_ensemble.scalers['main'].transform(X)
                            y_pred = model.predict(X_scaled)
                        else:
                            y_pred = model.predict(X)
                        
                        accuracy = np.mean(y_pred == y)
                        performance[f'ml_ensemble_{name}'] = accuracy
                    except Exception as e:
                        logger.error(f"Erro na avaliação de {name}: {e}")
            
            # Avalia Regressão Logística
            if hasattr(self.predictive_ensemble.logistic_regression, 'model'):
                try:
                    X_scaled = self.predictive_ensemble.logistic_regression.scaler.transform(X)
                    y_pred = self.predictive_ensemble.logistic_regression.model.predict(X_scaled)
                    accuracy = np.mean(y_pred == y)
                    performance['logistic_regression'] = accuracy
                except Exception as e:
                    logger.error(f"Erro na avaliação da regressão logística: {e}")
            
        except Exception as e:
            logger.error(f"Erro na avaliação dos modelos: {e}")
        
        return performance
    
    def _analyze_uncertainty(self, prediction: Dict) -> Dict:
        """Analisa incerteza da predição"""
        uncertainty_analysis = {
            'overall_uncertainty': prediction.get('uncertainty', 0),
            'confidence_level': self._classify_confidence(prediction['confidence']),
            'model_agreement': self._calculate_model_agreement(prediction),
            'prediction_stability': self._assess_prediction_stability(prediction)
        }
        
        # Análise de incerteza por modelo
        individual_predictions = prediction.get('individual_predictions', {})
        model_uncertainties = {}
        
        for model_name, model_pred in individual_predictions.items():
            if 'uncertainty' in model_pred:
                model_uncertainties[model_name] = model_pred['uncertainty']
            else:
                # Calcula incerteza baseada na confiança
                model_uncertainties[model_name] = 1 - model_pred['confidence']
        
        uncertainty_analysis['model_uncertainties'] = model_uncertainties
        
        return uncertainty_analysis
    
    def _classify_confidence(self, confidence: float) -> str:
        """Classifica nível de confiança"""
        if confidence >= 0.8:
            return 'very_high'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        elif confidence >= 0.5:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_model_agreement(self, prediction: Dict) -> float:
        """Calcula concordância entre modelos"""
        individual_predictions = prediction.get('individual_predictions', {})
        
        if len(individual_predictions) < 2:
            return 1.0
        
        # Conta quantos modelos concordam com a predição final
        final_result = prediction['predicted_result']
        agreement_count = 0
        
        for model_pred in individual_predictions.values():
            if model_pred['predicted_result'] == final_result:
                agreement_count += 1
        
        return agreement_count / len(individual_predictions)
    
    def _assess_prediction_stability(self, prediction: Dict) -> str:
        """Avalia estabilidade da predição"""
        agreement = self._calculate_model_agreement(prediction)
        confidence = prediction['confidence']
        
        if agreement >= 0.8 and confidence >= 0.7:
            return 'very_stable'
        elif agreement >= 0.6 and confidence >= 0.6:
            return 'stable'
        elif agreement >= 0.4 and confidence >= 0.5:
            return 'moderate'
        else:
            return 'unstable'
    
    def _create_advanced_recommendations(self, prediction: Dict, match_analysis: Dict) -> Dict:
        """Cria recomendações avançadas baseadas em todos os modelos"""
        recommendations = []
        
        # Simula odds de mercado
        market_odds = {
            'home': 2.0,
            'draw': 3.2,
            'away': 3.5
        }
        
        probabilities = prediction['probabilities']
        calculated_odds = prediction['odds']
        
        for outcome, prob in probabilities.items():
            market_odd = market_odds[outcome]
            calculated_odd = calculated_odds[outcome]
            
            # Calcula valor esperado
            ev = (prob * market_odd) - 1
            
            # Calcula Kelly Criterion
            kelly = (prob * market_odd - 1) / (market_odd - 1) if market_odd > 1 else 0
            kelly = max(0, min(kelly, 0.25))
            
            # Ajusta recomendação baseada na incerteza
            uncertainty = prediction.get('uncertainty', 0)
            if uncertainty > 0.3:
                ev *= 0.8  # Reduz EV se alta incerteza
                kelly *= 0.7
            
            # Determina recomendação
            if ev > 0.2 and kelly > 0.05 and uncertainty < 0.4:
                recommendation = 'STRONG_BET'
            elif ev > 0.15 and kelly > 0.03 and uncertainty < 0.5:
                recommendation = 'BET'
            elif ev > 0.1 and kelly > 0.02:
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
                'confidence': prediction['confidence'],
                'uncertainty': uncertainty
            })
        
        # Ordena por valor esperado
        recommendations.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return {
            'recommendations': recommendations,
            'best_bet': recommendations[0] if recommendations else None,
            'total_recommendations': len(recommendations),
            'strong_bets': len([r for r in recommendations if r['recommendation'] == 'STRONG_BET']),
            'avoid_bets': len([r for r in recommendations if r['recommendation'] == 'AVOID']),
            'uncertainty_adjusted': True
        }
    
    def _create_advanced_risk_analysis(self, prediction: Dict, match_analysis: Dict, uncertainty_analysis: Dict) -> Dict:
        """Cria análise de risco avançada"""
        risk_factors = []
        risk_score = 0
        
        # Risco baseado em incerteza
        uncertainty = prediction.get('uncertainty', 0)
        if uncertainty > 0.4:
            risk_factors.append('Alta incerteza na predição')
            risk_score += 3
        elif uncertainty > 0.3:
            risk_factors.append('Incerteza moderada na predição')
            risk_score += 2
        
        # Risco baseado em concordância de modelos
        agreement = uncertainty_analysis.get('model_agreement', 1.0)
        if agreement < 0.5:
            risk_factors.append('Baixa concordância entre modelos')
            risk_score += 2
        elif agreement < 0.7:
            risk_factors.append('Concordância moderada entre modelos')
            risk_score += 1
        
        # Risco baseado em estabilidade
        stability = uncertainty_analysis.get('prediction_stability', 'stable')
        if stability == 'unstable':
            risk_factors.append('Predição instável')
            risk_score += 3
        elif stability == 'moderate':
            risk_factors.append('Predição moderadamente estável')
            risk_score += 1
        
        # Risco baseado em confiança
        confidence = prediction['confidence']
        if confidence < 0.5:
            risk_factors.append('Baixa confiança na predição')
            risk_score += 2
        elif confidence < 0.6:
            risk_factors.append('Confiança moderada na predição')
            risk_score += 1
        
        # Risco baseado em fatores contextuais
        if match_analysis:
            home_injuries = len(match_analysis['match_context'].home_team_injuries)
            away_injuries = len(match_analysis['match_context'].away_team_injuries)
            
            if home_injuries > 3 or away_injuries > 3:
                risk_factors.append('Muitas lesões')
                risk_score += 1
        
        # Determina nível de risco
        if risk_score >= 8:
            risk_level = 'VERY_HIGH'
        elif risk_score >= 6:
            risk_level = 'HIGH'
        elif risk_score >= 4:
            risk_level = 'MEDIUM'
        elif risk_score >= 2:
            risk_level = 'LOW'
        else:
            risk_level = 'VERY_LOW'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'max_risk_score': 10,
            'risk_factors': risk_factors,
            'confidence': confidence,
            'uncertainty': uncertainty,
            'model_agreement': agreement,
            'prediction_stability': stability,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Retorna recomendação baseada no nível de risco"""
        risk_recommendations = {
            'VERY_HIGH': 'AVOID_STRONGLY',
            'HIGH': 'AVOID',
            'MEDIUM': 'CAUTION',
            'LOW': 'NORMAL',
            'VERY_LOW': 'CONFIDENT'
        }
        return risk_recommendations.get(risk_level, 'UNKNOWN')
    
    def _generate_model_insights(self, prediction: Dict) -> Dict:
        """Gera insights dos modelos"""
        insights = []
        
        # Insight sobre concordância de modelos
        individual_predictions = prediction.get('individual_predictions', {})
        if individual_predictions:
            model_results = [pred['predicted_result'] for pred in individual_predictions.values()]
            most_common = max(set(model_results), key=model_results.count)
            agreement_count = model_results.count(most_common)
            
            if agreement_count == len(model_results):
                insights.append("Todos os modelos concordam na predição")
            elif agreement_count >= len(model_results) * 0.7:
                insights.append(f"Maioria dos modelos ({agreement_count}/{len(model_results)}) concorda na predição")
            else:
                insights.append("Modelos apresentam divergências significativas")
        
        # Insight sobre incerteza
        uncertainty = prediction.get('uncertainty', 0)
        if uncertainty < 0.2:
            insights.append("Predição apresenta baixa incerteza")
        elif uncertainty > 0.4:
            insights.append("Predição apresenta alta incerteza - considere cautela")
        
        # Insight sobre confiança
        confidence = prediction['confidence']
        if confidence > 0.8:
            insights.append("Alta confiança na predição")
        elif confidence < 0.6:
            insights.append("Confiança moderada na predição")
        
        # Insight sobre modelo Poisson
        if 'poisson' in individual_predictions:
            poisson_pred = individual_predictions['poisson']
            if 'expected_goals' in poisson_pred:
                home_xg = poisson_pred['expected_goals']['home']
                away_xg = poisson_pred['expected_goals']['away']
                insights.append(f"Modelo Poisson: {home_xg:.1f} vs {away_xg:.1f} gols esperados")
        
        return {
            'insights': insights,
            'total_insights': len(insights),
            'model_count': len(individual_predictions),
            'uncertainty_level': 'low' if uncertainty < 0.3 else 'high' if uncertainty > 0.4 else 'medium'
        }
    
    def run_advanced_backtesting(self, historical_matches: List[Dict], initial_capital: float = 1000) -> Dict:
        """
        Executa backtesting usando modelos avançados
        """
        logger.info("Executando backtesting com modelos avançados...")
        
        try:
            # Treina modelos primeiro
            training_result = self.train_advanced_models(historical_matches)
            if not training_result['success']:
                return {'success': False, 'error': 'Falha no treinamento dos modelos'}
            
            # Executa backtesting
            portfolio = []
            current_capital = initial_capital
            bet_size = 0.02
            
            for match in historical_matches[:50]:  # Limita para performance
                try:
                    # Faz predição avançada
                    prediction = self.predict_advanced(
                        match['home_team'],
                        match['away_team'],
                        match['date']
                    )
                    
                    if not prediction:
                        continue
                    
                    # Encontra melhor aposta
                    recommendations = prediction['recommendations']['recommendations']
                    best_bet = None
                    
                    for rec in recommendations:
                        if rec['recommendation'] in ['STRONG_BET', 'BET'] and rec['expected_value'] > 0.1:
                            best_bet = rec
                            break
                    
                    if best_bet:
                        # Calcula tamanho da aposta
                        bet_amount = current_capital * bet_size
                        kelly_bet = current_capital * best_bet['kelly_percentage']
                        final_bet = min(bet_amount, kelly_bet)
                        
                        # Simula resultado
                        actual_result = self._simulate_match_result(match)
                        is_winner = self._check_bet_result(best_bet['outcome'], actual_result)
                        
                        # Calcula lucro/prejuízo
                        if is_winner:
                            profit = final_bet * (best_bet['market_odds'] - 1)
                        else:
                            profit = -final_bet
                        
                        current_capital += profit
                        
                        # Registra trade
                        trade = {
                            'match_id': match.get('id', f'match_{len(portfolio)}'),
                            'date': match['date'],
                            'home_team': match['home_team'],
                            'away_team': match['away_team'],
                            'bet_outcome': best_bet['outcome'],
                            'bet_odds': best_bet['market_odds'],
                            'bet_amount': final_bet,
                            'expected_value': best_bet['expected_value'],
                            'uncertainty': prediction['uncertainty_analysis']['overall_uncertainty'],
                            'actual_result': actual_result,
                            'is_winner': is_winner,
                            'profit': profit,
                            'capital_after': current_capital,
                            'roi': (current_capital - initial_capital) / initial_capital * 100
                        }
                        
                        portfolio.append(trade)
                        
                except Exception as e:
                    logger.error(f"Erro ao processar partida no backtesting: {e}")
                    continue
            
            # Calcula métricas
            metrics = self._calculate_advanced_metrics(portfolio)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'metrics': metrics,
                'training_performance': training_result['performance']
            }
            
        except Exception as e:
            logger.error(f"Erro no backtesting avançado: {e}")
            return {'success': False, 'error': str(e)}
    
    def _simulate_match_result(self, match: Dict) -> str:
        """Simula resultado de uma partida"""
        import random
        
        # Simula resultado baseado nas odds
        home_odds = match.get('home_odds', 2.0)
        draw_odds = match.get('draw_odds', 3.0)
        away_odds = match.get('away_odds', 2.5)
        
        # Calcula probabilidades implícitas
        home_prob = 1 / home_odds
        draw_prob = 1 / draw_odds
        away_prob = 1 / away_odds
        
        # Normaliza probabilidades
        total_prob = home_prob + draw_prob + away_prob
        home_prob /= total_prob
        draw_prob /= total_prob
        away_prob /= total_prob
        
        # Simula resultado
        rand = random.random()
        
        if rand < home_prob:
            return 'home_win'
        elif rand < home_prob + draw_prob:
            return 'draw'
        else:
            return 'away_win'
    
    def _check_bet_result(self, bet_outcome: str, actual_result: str) -> bool:
        """Verifica se a aposta foi vencedora"""
        return bet_outcome == actual_result
    
    def _calculate_advanced_metrics(self, portfolio: List[Dict]) -> Dict:
        """Calcula métricas avançadas do backtesting"""
        if not portfolio:
            return {}
        
        df = pd.DataFrame(portfolio)
        
        # Métricas básicas
        total_trades = len(df)
        winning_trades = len(df[df['is_winner'] == True])
        losing_trades = len(df[df['is_winner'] == False])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Métricas financeiras
        total_profit = df['profit'].sum()
        total_bet_amount = df['bet_amount'].sum()
        roi = (total_profit / total_bet_amount * 100) if total_bet_amount > 0 else 0
        
        # Métricas de incerteza
        avg_uncertainty = df['uncertainty'].mean() if 'uncertainty' in df.columns else 0
        high_uncertainty_trades = len(df[df['uncertainty'] > 0.4]) if 'uncertainty' in df.columns else 0
        
        # Métricas de valor esperado
        avg_ev = df['expected_value'].mean() if 'expected_value' in df.columns else 0
        positive_ev_trades = len(df[df['expected_value'] > 0]) if 'expected_value' in df.columns else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_bet_amount': total_bet_amount,
            'roi': roi,
            'avg_uncertainty': avg_uncertainty,
            'high_uncertainty_trades': high_uncertainty_trades,
            'avg_expected_value': avg_ev,
            'positive_ev_trades': positive_ev_trades,
            'uncertainty_adjusted_roi': roi * (1 - avg_uncertainty) if avg_uncertainty > 0 else roi
        }

if __name__ == "__main__":
    # Teste do sistema preditivo avançado
    system = AdvancedPredictiveSystem()
    
    print("=== TESTE DO SISTEMA PREDITIVO AVANÇADO ===")
    
    # Dados simulados para teste
    historical_matches = []
    for i in range(100):
        match = {
            'id': f'match_{i}',
            'home_team': f'Team_{i%10}',
            'away_team': f'Team_{(i+5)%10}',
            'date': f'2024-01-{i%30+1:02d}',
            'result': np.random.choice(['win', 'draw', 'loss']),
            'home_goals': np.random.randint(0, 4),
            'away_goals': np.random.randint(0, 4),
            'home_odds': np.random.uniform(1.5, 4.0),
            'draw_odds': np.random.uniform(2.8, 3.5),
            'away_odds': np.random.uniform(1.8, 5.0)
        }
        historical_matches.append(match)
    
    # Treina modelos
    training_result = system.train_advanced_models(historical_matches)
    print(f"Treinamento: {'Sucesso' if training_result['success'] else 'Falha'}")
    
    if training_result['success']:
        # Testa predição
        prediction = system.predict_advanced('Team_A', 'Team_B', '2024-01-15')
        if prediction:
            print(f"Predição: {prediction['prediction']['predicted_result']}")
            print(f"Confiança: {prediction['prediction']['confidence']:.3f}")
            print(f"Incerteza: {prediction['uncertainty_analysis']['overall_uncertainty']:.3f}")
            print(f"Risco: {prediction['risk_analysis']['risk_level']}")
    
    print("Teste concluído!")
