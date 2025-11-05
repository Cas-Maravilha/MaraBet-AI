#!/usr/bin/env python3
"""
Módulo de Machine Learning para previsões esportivas
MaraBet AI - Sistema de Apostas Esportivas Inteligentes
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from datetime import datetime, timedelta
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportsPredictor:
    """Classe principal para previsões esportivas com ML"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.is_trained = False
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features avançadas para ML"""
        logger.info("🔧 Criando features para ML...")
        
        # Usar feature engineering simplificado
        from ml.simple_feature_engineering import SimpleFeatureEngineer
        engineer = SimpleFeatureEngineer()
        features_df = engineer.create_all_features(df)
        
        logger.info(f"✅ Features criadas: {len(features_df.columns)} colunas")
        return features_df
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepara dados para treinamento"""
        logger.info("📊 Preparando dados para treinamento...")
        
        # Criar features
        features_df = self.create_features(df)
        
        # Selecionar features numéricas
        feature_columns = [
            'home_form_5', 'away_form_5', 'home_goals_avg', 'away_goals_avg',
            'h2h_home_wins', 'h2h_away_wins', 'home_odd', 'draw_odd', 'away_odd',
            'home_prob', 'draw_prob', 'away_prob', 'home_value', 'draw_value', 'away_value',
            'day_of_week', 'month', 'is_weekend', 'league_goals_avg',
            'home_momentum', 'away_momentum'
        ]
        
        # Filtrar colunas existentes
        available_features = [col for col in feature_columns if col in features_df.columns]
        
        # Preparar X e y
        X = features_df[available_features].fillna(0)
        y = features_df['result']  # 0: away_win, 1: draw, 2: home_win
        
        # Normalizar features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        self.scalers['main'] = scaler
        
        logger.info(f"✅ Dados preparados: {X_scaled.shape[0]} amostras, {X_scaled.shape[1]} features")
        return X_scaled, y.values, available_features
    
    def train_models(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        """Treina múltiplos modelos de ML"""
        logger.info("🤖 Treinando modelos de ML...")
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Modelos para treinar
        models_config = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'xgboost': xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss'),
            'lightgbm': lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1),
            'catboost': cb.CatBoostClassifier(iterations=100, random_state=42, verbose=False)
        }
        
        # Treinar cada modelo
        for name, model in models_config.items():
            logger.info(f"🔄 Treinando {name}...")
            
            try:
                # Treinar modelo
                model.fit(X_train, y_train)
                
                # Avaliar modelo
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Salvar modelo
                self.models[name] = model
                self.model_performance[name] = {
                    'accuracy': accuracy,
                    'test_size': len(X_test)
                }
                
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = dict(zip(feature_names, model.feature_importances_))
                elif hasattr(model, 'coef_'):
                    self.feature_importance[name] = dict(zip(feature_names, abs(model.coef_[0])))
                
                logger.info(f"✅ {name}: Accuracy = {accuracy:.4f}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao treinar {name}: {e}")
        
        self.is_trained = True
        logger.info("🎉 Treinamento concluído!")
    
    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """Faz predições com ensemble de modelos"""
        if not self.is_trained:
            raise ValueError("Modelos não foram treinados ainda!")
        
        predictions = {}
        probabilities = {}
        
        # Predições de cada modelo
        for name, model in self.models.items():
            try:
                pred = model.predict(X)
                proba = model.predict_proba(X)
                
                predictions[name] = pred[0]
                probabilities[name] = proba[0]
                
            except Exception as e:
                logger.error(f"❌ Erro na predição com {name}: {e}")
        
        # Ensemble por votação
        if predictions:
            # Converter predições para lista para evitar erro de hash
            pred_values = [pred[0] if isinstance(pred, np.ndarray) else pred for pred in predictions.values()]
            ensemble_pred = max(set(pred_values), key=pred_values.count)
            
            # Ensemble por média das probabilidades
            if probabilities:
                prob_values = [prob[0] if isinstance(prob, np.ndarray) else prob for prob in probabilities.values()]
                avg_proba = np.mean(prob_values, axis=0)
                ensemble_proba = avg_proba
            else:
                ensemble_proba = None
        else:
            ensemble_pred = 0
            ensemble_proba = None
        
        # Calcular confiança
        if ensemble_proba is not None and hasattr(ensemble_proba, '__len__') and len(ensemble_proba) > 0:
            confidence = np.max(ensemble_proba)
        else:
            confidence = 0
        
        return {
            'prediction': ensemble_pred,
            'probability': ensemble_proba,
            'individual_predictions': predictions,
            'individual_probabilities': probabilities,
            'confidence': confidence
        }
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Retorna importância das features"""
        return self.feature_importance
    
    def get_model_performance(self) -> Dict[str, Dict[str, float]]:
        """Retorna performance dos modelos"""
        return self.model_performance
    
    def save_models(self, filepath: str):
        """Salva modelos treinados"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'encoders': self.encoders,
            'feature_importance': self.feature_importance,
            'model_performance': self.model_performance,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        logger.info(f"💾 Modelos salvos em: {filepath}")
    
    def load_models(self, filepath: str):
        """Carrega modelos treinados"""
        model_data = joblib.load(filepath)
        self.models = model_data['models']
        self.scalers = model_data['scalers']
        self.encoders = model_data['encoders']
        self.feature_importance = model_data['feature_importance']
        self.model_performance = model_data['model_performance']
        self.is_trained = model_data['is_trained']
        logger.info(f"📂 Modelos carregados de: {filepath}")

class PoissonPredictor:
    """Preditor baseado no modelo de Poisson para futebol"""
    
    def __init__(self):
        self.home_attack = {}
        self.home_defense = {}
        self.away_attack = {}
        self.away_defense = {}
        self.league_avg = {}
        self.is_trained = False
    
    def train(self, df: pd.DataFrame):
        """Treina o modelo de Poisson"""
        logger.info("📊 Treinando modelo de Poisson...")
        
        # Calcular médias de gols por time
        for team_id in df['home_team_id'].unique():
            home_matches = df[df['home_team_id'] == team_id]
            away_matches = df[df['away_team_id'] == team_id]
            
            # Ataque em casa
            self.home_attack[team_id] = home_matches['home_score'].mean()
            # Defesa em casa
            self.home_defense[team_id] = home_matches['away_score'].mean()
            # Ataque fora
            self.away_attack[team_id] = away_matches['away_score'].mean()
            # Defesa fora
            self.away_defense[team_id] = away_matches['home_score'].mean()
        
        # Média da liga
        self.league_avg['home'] = df['home_score'].mean()
        self.league_avg['away'] = df['away_score'].mean()
        
        self.is_trained = True
        logger.info("✅ Modelo de Poisson treinado!")
    
    def predict(self, home_team_id: int, away_team_id: int) -> Dict[str, float]:
        """Faz predição com modelo de Poisson"""
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ainda!")
        
        # Calcular forças de ataque e defesa
        home_attack = self.home_attack.get(home_team_id, self.league_avg['home'])
        home_defense = self.home_defense.get(home_team_id, self.league_avg['away'])
        away_attack = self.away_attack.get(away_team_id, self.league_avg['away'])
        away_defense = self.away_defense.get(away_team_id, self.league_avg['home'])
        
        # Calcular expectativa de gols
        home_goals = home_attack * away_defense / self.league_avg['home']
        away_goals = away_attack * home_defense / self.league_avg['away']
        
        # Calcular probabilidades usando Poisson
        from scipy.stats import poisson
        
        # Probabilidades para diferentes placares
        home_win_prob = 0
        draw_prob = 0
        away_win_prob = 0
        
        for h in range(10):  # Máximo 10 gols
            for a in range(10):
                prob = poisson.pmf(h, home_goals) * poisson.pmf(a, away_goals)
                
                if h > a:
                    home_win_prob += prob
                elif h == a:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        return {
            'home_win_prob': home_win_prob,
            'draw_prob': draw_prob,
            'away_win_prob': away_win_prob,
            'expected_home_goals': home_goals,
            'expected_away_goals': away_goals
        }

def create_sample_data() -> pd.DataFrame:
    """Cria dados de exemplo para teste"""
    np.random.seed(42)
    
    # Dados de exemplo
    n_matches = 1000
    
    data = {
        'home_team_id': np.random.randint(1, 21, n_matches),
        'away_team_id': np.random.randint(1, 21, n_matches),
        'home_score': np.random.poisson(1.5, n_matches),
        'away_score': np.random.poisson(1.2, n_matches),
        'home_odd': np.random.uniform(1.5, 4.0, n_matches),
        'draw_odd': np.random.uniform(2.8, 4.5, n_matches),
        'away_odd': np.random.uniform(1.5, 4.0, n_matches),
        'league_id': np.random.randint(1, 6, n_matches),
        'date': pd.date_range('2023-01-01', periods=n_matches, freq='D')
    }
    
    df = pd.DataFrame(data)
    
    # Calcular resultado
    df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
    df['draw'] = (df['home_score'] == df['away_score']).astype(int)
    df['away_win'] = (df['home_score'] < df['away_score']).astype(int)
    df['total_goals'] = df['home_score'] + df['away_score']
    
    # Resultado categórico
    df['result'] = 0  # away_win
    df.loc[df['draw'] == 1, 'result'] = 1  # draw
    df.loc[df['home_win'] == 1, 'result'] = 2  # home_win
    
    return df

def main():
    """Função principal para teste"""
    print("🤖 MARABET AI - MÓDULO DE MACHINE LEARNING")
    print("=" * 60)
    
    # Criar dados de exemplo
    print("📊 Criando dados de exemplo...")
    df = create_sample_data()
    print(f"✅ Dados criados: {len(df)} partidas")
    
    # Testar SportsPredictor
    print("\n🔮 Testando SportsPredictor...")
    predictor = SportsPredictor()
    
    # Preparar dados
    X, y, feature_names = predictor.prepare_training_data(df)
    
    # Treinar modelos
    predictor.train_models(X, y, feature_names)
    
    # Mostrar performance
    print("\n📊 Performance dos Modelos:")
    for name, perf in predictor.get_model_performance().items():
        print(f"  {name}: {perf['accuracy']:.4f}")
    
    # Testar predição
    print("\n🔮 Testando predição...")
    sample_X = X[:1]  # Primeira amostra
    prediction = predictor.predict(sample_X)
    print(f"Predição: {prediction['prediction']}")
    print(f"Confiança: {prediction['confidence']:.4f}")
    
    # Testar PoissonPredictor
    print("\n📊 Testando PoissonPredictor...")
    poisson_predictor = PoissonPredictor()
    poisson_predictor.train(df)
    
    # Predição de exemplo
    sample_prediction = poisson_predictor.predict(1, 2)
    print(f"Probabilidade Vitória Casa: {sample_prediction['home_win_prob']:.4f}")
    print(f"Probabilidade Empate: {sample_prediction['draw_prob']:.4f}")
    print(f"Probabilidade Vitória Fora: {sample_prediction['away_win_prob']:.4f}")
    
    print("\n🎉 Teste do módulo de ML concluído!")

if __name__ == "__main__":
    main()
