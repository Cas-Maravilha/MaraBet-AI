import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
try:
    import xgboost as xgb
except ImportError:
    xgb = None

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

try:
    from catboost import CatBoostClassifier
except ImportError:
    CatBoostClassifier = None
import joblib
import logging
from datetime import datetime
import os
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BettingPredictor:
    def __init__(self):
        self.config = Config()
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        
    def prepare_data(self, df):
        """
        Prepara os dados para treinamento
        """
        # Remove colunas não numéricas para features
        feature_columns = [col for col in df.columns if col not in 
                          ['home_team', 'away_team', 'league', 'result', 'home_goals', 'away_goals', 'date']]
        
        X = df[feature_columns].fillna(0)
        
        # Cria target para classificação (resultado da partida)
        if 'result' in df.columns:
            y = df['result'].map({'win': 0, 'draw': 1, 'loss': 2})  # 0=home win, 1=draw, 2=away win
        else:
            # Se não há resultado, cria target simulado para demonstração
            y = np.random.choice([0, 1, 2], size=len(X))
        
        return X, y, feature_columns
    
    def train_models(self, X, y, feature_columns):
        """
        Treina múltiplos modelos de machine learning
        """
        # Divide os dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normaliza os dados
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['main'] = scaler
        
        # Define os modelos
        models_config = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000
            )
        }
        
        # Adiciona modelos opcionais se disponíveis
        if xgb is not None:
            models_config['xgboost'] = xgb.XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                eval_metric='mlogloss'
            )
        
        if lgb is not None:
            models_config['lightgbm'] = lgb.LGBMClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                verbose=-1
            )
        
        if CatBoostClassifier is not None:
            models_config['catboost'] = CatBoostClassifier(
                iterations=100,
                learning_rate=0.1,
                depth=6,
                random_state=42,
                verbose=False
            )
        
        # Treina cada modelo
        for name, model in models_config.items():
            logger.info(f"Treinando modelo {name}...")
            
            try:
                if name in ['logistic_regression']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    y_pred_proba = model.predict_proba(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)
                
                # Calcula métricas
                accuracy = accuracy_score(y_test, y_pred)
                
                # Armazena o modelo e métricas
                self.models[name] = model
                self.model_performance[name] = {
                    'accuracy': accuracy,
                    'predictions': y_pred,
                    'probabilities': y_pred_proba,
                    'test_labels': y_test
                }
                
                # Calcula importância das features
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = dict(zip(feature_columns, model.feature_importances_))
                elif hasattr(model, 'coef_'):
                    self.feature_importance[name] = dict(zip(feature_columns, abs(model.coef_[0])))
                
                logger.info(f"Modelo {name} treinado - Acurácia: {accuracy:.4f}")
                
            except Exception as e:
                logger.error(f"Erro ao treinar modelo {name}: {e}")
        
        return X_test, y_test
    
    def ensemble_predict(self, X):
        """
        Faz predição usando ensemble de modelos
        """
        predictions = []
        probabilities = []
        
        for name, model in self.models.items():
            try:
                if name == 'logistic_regression':
                    X_scaled = self.scalers['main'].transform(X)
                    pred = model.predict(X_scaled)
                    proba = model.predict_proba(X_scaled)
                else:
                    pred = model.predict(X)
                    proba = model.predict_proba(X)
                
                predictions.append(pred)
                probabilities.append(proba)
                
            except Exception as e:
                logger.error(f"Erro na predição com modelo {name}: {e}")
        
        if not predictions:
            return None, None
        
        # Média das probabilidades
        avg_probabilities = np.mean(probabilities, axis=0)
        
        # Predição final baseada na maior probabilidade
        final_predictions = np.argmax(avg_probabilities, axis=1)
        
        return final_predictions, avg_probabilities
    
    def calculate_betting_odds(self, probabilities):
        """
        Calcula odds de apostas baseadas nas probabilidades
        """
        # Adiciona margem da casa (5%)
        margin = 0.05
        adjusted_probs = probabilities * (1 - margin)
        
        # Calcula odds
        odds = 1 / adjusted_probs
        
        return odds
    
    def evaluate_betting_strategy(self, predictions, probabilities, true_labels, odds_data):
        """
        Avalia estratégia de apostas
        """
        results = []
        
        for i, (pred, prob, true_label) in enumerate(zip(predictions, probabilities, true_labels)):
            # Probabilidades para cada resultado
            home_prob = prob[0]  # Vitória da casa
            draw_prob = prob[1]  # Empate
            away_prob = prob[2]  # Vitória do visitante
            
            # Odds correspondentes
            home_odds = odds_data[i]['home_odds'] if i < len(odds_data) else 2.0
            draw_odds = odds_data[i]['draw_odds'] if i < len(odds_data) else 3.0
            away_odds = odds_data[i]['away_odds'] if i < len(odds_data) else 2.5
            
            # Calcula valor esperado para cada aposta
            home_ev = (home_prob * home_odds) - 1
            draw_ev = (draw_prob * draw_odds) - 1
            away_ev = (away_prob * away_odds) - 1
            
            # Escolhe a melhor aposta
            best_bet = max([
                ('home', home_ev, home_odds),
                ('draw', draw_ev, draw_odds),
                ('away', away_ev, away_odds)
            ], key=lambda x: x[1])
            
            # Verifica se a aposta foi vencedora
            bet_type, ev, odds = best_bet
            is_winner = (
                (bet_type == 'home' and true_label == 0) or
                (bet_type == 'draw' and true_label == 1) or
                (bet_type == 'away' and true_label == 2)
            )
            
            result = {
                'prediction': pred,
                'true_label': true_label,
                'bet_type': bet_type,
                'odds': odds,
                'ev': ev,
                'is_winner': is_winner,
                'home_prob': home_prob,
                'draw_prob': draw_prob,
                'away_prob': away_prob
            }
            
            results.append(result)
        
        return results
    
    def get_feature_importance_summary(self):
        """
        Retorna resumo da importância das features
        """
        if not self.feature_importance:
            return {}
        
        # Combina importância de todos os modelos
        all_features = set()
        for model_importance in self.feature_importance.values():
            all_features.update(model_importance.keys())
        
        avg_importance = {}
        for feature in all_features:
            importances = []
            for model_importance in self.feature_importance.values():
                if feature in model_importance:
                    importances.append(model_importance[feature])
            
            if importances:
                avg_importance[feature] = np.mean(importances)
        
        # Ordena por importância
        sorted_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_features)
    
    def save_models(self, directory='models'):
        """
        Salva os modelos treinados
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for name, model in self.models.items():
            filename = f"{directory}/{name}_{timestamp}.joblib"
            joblib.dump(model, filename)
            logger.info(f"Modelo {name} salvo em {filename}")
        
        # Salva scalers e encoders
        if self.scalers:
            joblib.dump(self.scalers, f"{directory}/scalers_{timestamp}.joblib")
        
        if self.label_encoders:
            joblib.dump(self.label_encoders, f"{directory}/encoders_{timestamp}.joblib")
    
    def load_models(self, directory='models', timestamp=None):
        """
        Carrega modelos salvos
        """
        if timestamp is None:
            # Busca o timestamp mais recente
            files = os.listdir(directory)
            model_files = [f for f in files if f.endswith('.joblib') and not f.startswith(('scalers_', 'encoders_'))]
            if not model_files:
                logger.error("Nenhum modelo encontrado")
                return False
            
            # Extrai timestamp do arquivo mais recente
            timestamps = []
            for f in model_files:
                try:
                    ts = f.split('_')[-1].replace('.joblib', '')
                    timestamps.append(ts)
                except:
                    continue
            
            if not timestamps:
                logger.error("Não foi possível extrair timestamp dos modelos")
                return False
            
            timestamp = max(timestamps)
        
        # Carrega modelos
        for name in ['random_forest', 'gradient_boosting', 'logistic_regression', 
                    'xgboost', 'lightgbm', 'catboost']:
            filename = f"{directory}/{name}_{timestamp}.joblib"
            if os.path.exists(filename):
                self.models[name] = joblib.load(filename)
                logger.info(f"Modelo {name} carregado")
        
        # Carrega scalers e encoders
        scalers_file = f"{directory}/scalers_{timestamp}.joblib"
        if os.path.exists(scalers_file):
            self.scalers = joblib.load(scalers_file)
        
        encoders_file = f"{directory}/encoders_{timestamp}.joblib"
        if os.path.exists(encoders_file):
            self.label_encoders = joblib.load(encoders_file)
        
        return True

class BettingAnalyzer:
    def __init__(self, predictor):
        self.predictor = predictor
    
    def analyze_match(self, match_data):
        """
        Analisa uma partida específica
        """
        # Prepara dados da partida
        X = match_data.drop(['home_team', 'away_team', 'league'], axis=1, errors='ignore')
        
        # Faz predição
        predictions, probabilities = self.predictor.ensemble_predict(X)
        
        if predictions is None:
            return None
        
        # Calcula odds
        odds = self.predictor.calculate_betting_odds(probabilities[0])
        
        # Análise da partida
        analysis = {
            'home_team': match_data.get('home_team', ''),
            'away_team': match_data.get('away_team', ''),
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
            'market_odds': {
                'home': match_data.get('home_odds', 0),
                'draw': match_data.get('draw_odds', 0),
                'away': match_data.get('away_odds', 0)
            },
            'recommendations': self._generate_recommendations(probabilities[0], odds, match_data)
        }
        
        return analysis
    
    def _generate_recommendations(self, probabilities, calculated_odds, match_data):
        """
        Gera recomendações de apostas
        """
        market_odds = {
            'home': match_data.get('home_odds', 0),
            'draw': match_data.get('draw_odds', 0),
            'away': match_data.get('away_odds', 0)
        }
        
        recommendations = []
        
        for i, (outcome, prob) in enumerate([('home', probabilities[0]), ('draw', probabilities[1]), ('away', probabilities[2])]):
            market_odd = market_odds[outcome]
            calculated_odd = calculated_odds[i]
            
            if market_odd > 0:
                # Calcula valor esperado
                ev = (prob * market_odd) - 1
                
                # Calcula Kelly Criterion (tamanho da aposta)
                kelly = (prob * market_odd - 1) / (market_odd - 1) if market_odd > 1 else 0
                kelly = max(0, min(kelly, 0.25))  # Limita entre 0 e 25%
                
                recommendation = {
                    'outcome': outcome,
                    'probability': prob,
                    'market_odds': market_odd,
                    'calculated_odds': calculated_odd,
                    'expected_value': ev,
                    'kelly_percentage': kelly,
                    'recommendation': 'BET' if ev > 0.1 and kelly > 0.02 else 'AVOID'
                }
                
                recommendations.append(recommendation)
        
        return recommendations

if __name__ == "__main__":
    # Teste dos modelos
    from data_collector import SportsDataCollector
    from feature_engineering import FeatureEngineer
    
    # Coleta dados
    collector = SportsDataCollector()
    matches = collector.get_football_matches()
    
    # Cria features
    engineer = FeatureEngineer()
    historical_data = {team: collector.get_historical_results(team) for team in ['Flamengo', 'Palmeiras']}
    training_data = engineer.prepare_training_data(matches, historical_data)
    
    # Treina modelos
    predictor = BettingPredictor()
    X, y, feature_columns = predictor.prepare_data(training_data)
    X_test, y_test = predictor.train_models(X, y, feature_columns)
    
    # Testa análise
    analyzer = BettingAnalyzer(predictor)
    if not training_data.empty:
        analysis = analyzer.analyze_match(training_data.iloc[0])
        print("Análise da partida:", analysis)
