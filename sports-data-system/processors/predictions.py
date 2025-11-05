"""
Processador de Predições - Sistema Básico
Modelos de machine learning para predições esportivas
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import joblib

logger = logging.getLogger(__name__)

class PredictionsProcessor:
    """Processador de predições usando ML"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}
        self.feature_columns = []
        self.is_trained = False
        
        # Cria diretório de modelos se não existir
        os.makedirs(models_dir, exist_ok=True)
        
        # Inicializa modelos
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa modelos de ML"""
        self.models = {
            'match_result': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'total_goals': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'both_teams_score': RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                min_samples_split=3,
                min_samples_leaf=1,
                random_state=42
            )
        }
        
        # Define features padrão
        self.feature_columns = [
            'home_form_points', 'away_form_points',
            'home_avg_goals_scored', 'away_avg_goals_scored',
            'home_avg_goals_conceded', 'away_avg_goals_conceded',
            'home_win_percentage', 'away_win_percentage',
            'h2h_home_wins', 'h2h_away_wins', 'h2h_draws',
            'home_clean_sheet_percentage', 'away_clean_sheet_percentage',
            'home_failed_to_score_percentage', 'away_failed_to_score_percentage',
            'is_weekend', 'days_since_last_match'
        ]
    
    def prepare_training_data(self, matches_data: List[Dict[str, Any]], 
                            team_stats: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Prepara dados para treinamento"""
        if not matches_data:
            logger.warning("Nenhum dado de partidas fornecido")
            return np.array([]), {}
        
        # Converte para DataFrame
        df = pd.DataFrame(matches_data)
        
        # Cria features
        features = []
        targets = {
            'match_result': [],
            'total_goals': [],
            'both_teams_score': []
        }
        
        for _, match in df.iterrows():
            feature_vector = self._extract_features(match, team_stats)
            if feature_vector is not None:
                features.append(feature_vector)
                
                # Extrai targets
                goals = match.get('goals', {})
                home_goals = goals.get('home', 0)
                away_goals = goals.get('away', 0)
                total_goals = home_goals + away_goals
                
                # Resultado da partida (0: away_win, 1: draw, 2: home_win)
                if home_goals > away_goals:
                    targets['match_result'].append(2)
                elif away_goals > home_goals:
                    targets['match_result'].append(0)
                else:
                    targets['match_result'].append(1)
                
                # Total de gols
                targets['total_goals'].append(total_goals)
                
                # Ambas marcam (0: não, 1: sim)
                bts = 1 if home_goals > 0 and away_goals > 0 else 0
                targets['both_teams_score'].append(bts)
        
        if not features:
            logger.warning("Nenhuma feature válida extraída")
            return np.array([]), {}
        
        X = np.array(features)
        y = {k: np.array(v) for k, v in targets.items()}
        
        logger.info(f"Dados preparados: {X.shape[0]} amostras, {X.shape[1]} features")
        return X, y
    
    def _extract_features(self, match: Dict[str, Any], 
                         team_stats: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extrai features de uma partida"""
        try:
            features = []
            
            # IDs dos times
            home_team_id = match.get('teams', {}).get('home', {}).get('id')
            away_team_id = match.get('teams', {}).get('away', {}).get('id')
            
            if not home_team_id or not away_team_id:
                return None
            
            # Busca estatísticas dos times
            home_stats = team_stats.get(str(home_team_id), {})
            away_stats = team_stats.get(str(away_team_id), {})
            
            # Features de forma (últimos 5 jogos)
            features.extend([
                home_stats.get('form_points', 0),
                away_stats.get('form_points', 0)
            ])
            
            # Features de gols
            features.extend([
                home_stats.get('avg_goals_scored', 1.5),
                away_stats.get('avg_goals_scored', 1.5),
                home_stats.get('avg_goals_conceded', 1.5),
                away_stats.get('avg_goals_conceded', 1.5)
            ])
            
            # Features de percentuais
            features.extend([
                home_stats.get('win_percentage', 50),
                away_stats.get('win_percentage', 50)
            ])
            
            # Features de H2H (simuladas)
            h2h_stats = match.get('h2h_stats', {})
            features.extend([
                h2h_stats.get('home_wins', 0),
                h2h_stats.get('away_wins', 0),
                h2h_stats.get('draws', 0)
            ])
            
            # Features de clean sheets
            features.extend([
                home_stats.get('clean_sheet_percentage', 30),
                away_stats.get('clean_sheet_percentage', 30)
            ])
            
            # Features de failed to score
            features.extend([
                home_stats.get('failed_to_score_percentage', 20),
                away_stats.get('failed_to_score_percentage', 20)
            ])
            
            # Features contextuais
            match_date = match.get('date', '')
            is_weekend = 1 if match_date and 'saturday' in match_date.lower() or 'sunday' in match_date.lower() else 0
            features.append(is_weekend)
            
            # Dias desde último jogo (simulado)
            days_since_last = np.random.randint(3, 14)
            features.append(days_since_last)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Erro ao extrair features: {e}")
            return None
    
    def train_models(self, X: np.ndarray, y: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """Treina todos os modelos"""
        if X.size == 0:
            logger.error("Dados de treinamento vazios")
            return {}
        
        results = {}
        
        for model_name, model in self.models.items():
            if model_name not in y:
                continue
            
            logger.info(f"Treinando modelo: {model_name}")
            
            try:
                # Divide dados
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y[model_name], test_size=0.2, random_state=42
                )
                
                # Treina modelo
                model.fit(X_train, y_train)
                
                # Predições
                y_pred = model.predict(X_test)
                
                # Calcula métricas
                if model_name == 'total_goals':
                    # Regressão
                    mse = mean_squared_error(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    mae = np.mean(np.abs(y_test - y_pred))
                    
                    results[model_name] = {
                        'mse': mse,
                        'rmse': rmse,
                        'mae': mae,
                        'r2': model.score(X_test, y_test)
                    }
                else:
                    # Classificação
                    accuracy = accuracy_score(y_test, y_pred)
                    
                    results[model_name] = {
                        'accuracy': accuracy,
                        'precision': 0.0,  # Implementar se necessário
                        'recall': 0.0,
                        'f1_score': 0.0
                    }
                
                logger.info(f"Modelo {model_name} treinado com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao treinar modelo {model_name}: {e}")
                results[model_name] = {'error': str(e)}
        
        self.is_trained = True
        return results
    
    def predict_match(self, home_team_id: int, away_team_id: int, 
                     team_stats: Dict[str, Any], h2h_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """Faz predição para uma partida"""
        if not self.is_trained:
            logger.warning("Modelos não foram treinados")
            return {}
        
        try:
            # Cria dados da partida simulados
            match_data = {
                'teams': {
                    'home': {'id': home_team_id},
                    'away': {'id': away_team_id}
                },
                'date': datetime.now().isoformat(),
                'h2h_stats': h2h_stats or {}
            }
            
            # Extrai features
            features = self._extract_features(match_data, team_stats)
            if features is None:
                return {}
            
            features = features.reshape(1, -1)
            
            # Faz predições
            predictions = {}
            
            # Resultado da partida
            result_pred = self.models['match_result'].predict(features)[0]
            result_proba = self.models['match_result'].predict_proba(features)[0]
            
            result_labels = ['Away Win', 'Draw', 'Home Win']
            predictions['match_result'] = {
                'prediction': result_labels[result_pred],
                'confidence': float(max(result_proba)),
                'probabilities': {
                    'away_win': float(result_proba[0]),
                    'draw': float(result_proba[1]),
                    'home_win': float(result_proba[2])
                }
            }
            
            # Total de gols
            total_goals_pred = self.models['total_goals'].predict(features)[0]
            predictions['total_goals'] = {
                'prediction': round(float(total_goals_pred), 1),
                'over_1_5': total_goals_pred > 1.5,
                'over_2_5': total_goals_pred > 2.5,
                'over_3_5': total_goals_pred > 3.5
            }
            
            # Ambas marcam
            bts_pred = self.models['both_teams_score'].predict(features)[0]
            bts_proba = self.models['both_teams_score'].predict_proba(features)[0]
            
            predictions['both_teams_score'] = {
                'prediction': 'Yes' if bts_pred == 1 else 'No',
                'confidence': float(max(bts_proba)),
                'probability': float(bts_proba[1])  # Probabilidade de 'Yes'
            }
            
            # Calcula odds justas
            predictions['fair_odds'] = self._calculate_fair_odds(predictions)
            
            # Calcula value bets
            predictions['value_bets'] = self._calculate_value_bets(predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return {}
    
    def _calculate_fair_odds(self, predictions: Dict[str, Any]) -> Dict[str, float]:
        """Calcula odds justas baseadas nas probabilidades"""
        fair_odds = {}
        
        # Odds do resultado
        result_probs = predictions.get('match_result', {}).get('probabilities', {})
        for outcome, prob in result_probs.items():
            if prob > 0:
                fair_odds[f'{outcome}_odd'] = round(1 / prob, 2)
        
        # Odds de Over/Under
        total_goals = predictions.get('total_goals', {}).get('prediction', 2.5)
        over_2_5_prob = 1 if total_goals > 2.5 else 0.5
        under_2_5_prob = 1 - over_2_5_prob
        
        fair_odds['over_2_5_odd'] = round(1 / over_2_5_prob, 2)
        fair_odds['under_2_5_odd'] = round(1 / under_2_5_prob, 2)
        
        # Odds de Ambas Marcam
        bts_prob = predictions.get('both_teams_score', {}).get('probability', 0.5)
        fair_odds['btts_yes_odd'] = round(1 / bts_prob, 2)
        fair_odds['btts_no_odd'] = round(1 / (1 - bts_prob), 2)
        
        return fair_odds
    
    def _calculate_value_bets(self, predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calcula value bets baseado em odds do mercado"""
        value_bets = []
        
        # Simula odds do mercado
        market_odds = {
            'home_win_odd': 2.1,
            'draw_odd': 3.4,
            'away_win_odd': 3.8,
            'over_2_5_odd': 1.8,
            'under_2_5_odd': 2.0,
            'btts_yes_odd': 1.9,
            'btts_no_odd': 1.9
        }
        
        fair_odds = predictions.get('fair_odds', {})
        
        for market, market_odd in market_odds.items():
            fair_odd = fair_odds.get(market, 0)
            if fair_odd > 0:
                # Calcula valor esperado
                implied_prob = 1 / market_odd
                fair_prob = 1 / fair_odd
                expected_value = (fair_prob * market_odd) - 1
                
                if expected_value > 0.05:  # 5% de value mínimo
                    value_bets.append({
                        'market': market,
                        'market_odd': market_odd,
                        'fair_odd': fair_odd,
                        'expected_value': round(expected_value, 3),
                        'value_percentage': round(expected_value * 100, 1),
                        'recommendation': 'BET' if expected_value > 0.1 else 'CONSIDER'
                    })
        
        return value_bets
    
    def save_models(self) -> bool:
        """Salva modelos treinados"""
        try:
            for model_name, model in self.models.items():
                model_path = os.path.join(self.models_dir, f"{model_name}_model.pkl")
                joblib.dump(model, model_path)
                logger.info(f"Modelo {model_name} salvo em {model_path}")
            
            # Salva feature columns
            features_path = os.path.join(self.models_dir, "feature_columns.pkl")
            with open(features_path, 'wb') as f:
                pickle.dump(self.feature_columns, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {e}")
            return False
    
    def load_models(self) -> bool:
        """Carrega modelos treinados"""
        try:
            for model_name in self.models.keys():
                model_path = os.path.join(self.models_dir, f"{model_name}_model.pkl")
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"Modelo {model_name} carregado")
            
            # Carrega feature columns
            features_path = os.path.join(self.models_dir, "feature_columns.pkl")
            if os.path.exists(features_path):
                with open(features_path, 'rb') as f:
                    self.feature_columns = pickle.load(f)
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações dos modelos"""
        return {
            'is_trained': self.is_trained,
            'models_available': list(self.models.keys()),
            'feature_columns': self.feature_columns,
            'models_dir': self.models_dir
        }
