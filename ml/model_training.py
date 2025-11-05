#!/usr/bin/env python3
"""
Sistema de Treinamento e Validação de Modelos de ML
MaraBet AI - Sistema de Apostas Esportivas Inteligentes
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, log_loss
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from datetime import datetime, timedelta
import joblib
import logging
from typing import Dict, List, Tuple, Any, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Classe para treinamento e validação de modelos"""
    
    def __init__(self):
        self.models = {}
        self.best_models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.training_history = {}
        self.is_trained = False
    
    def prepare_data(self, df: pd.DataFrame, target_column: str = 'result') -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepara dados para treinamento"""
        logger.info("📊 Preparando dados para treinamento...")
        
        # Selecionar features numéricas
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_columns = [col for col in numeric_columns if col != target_column]
        
        # Preparar X e y
        X = df[feature_columns].fillna(0)
        y = df[target_column]
        
        # Normalizar features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        self.scalers['main'] = scaler
        
        logger.info(f"✅ Dados preparados: {X_scaled.shape[0]} amostras, {X_scaled.shape[1]} features")
        return X_scaled, y.values, feature_columns
    
    def train_single_model(self, model_name: str, model: Any, X: np.ndarray, y: np.ndarray, 
                          use_grid_search: bool = False) -> Dict[str, Any]:
        """Treina um modelo individual"""
        logger.info(f"🤖 Treinando {model_name}...")
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Grid search se solicitado
        if use_grid_search:
            model = self._get_grid_search_model(model_name, model)
        
        # Treinar modelo
        start_time = datetime.now()
        model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Avaliar modelo
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        
        try:
            logloss = log_loss(y_test, y_proba) if y_proba is not None else float('inf')
        except:
            logloss = float('inf')
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        
        # Feature importance
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(range(len(model.feature_importances_)), model.feature_importances_))
        elif hasattr(model, 'coef_'):
            feature_importance = dict(zip(range(len(model.coef_[0])), abs(model.coef_[0])))
        
        # Salvar modelo
        self.models[model_name] = model
        
        # Salvar resultados
        results = {
            'model': model,
            'accuracy': accuracy,
            'log_loss': logloss,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'training_time': training_time,
            'feature_importance': feature_importance,
            'test_size': len(X_test)
        }
        
        self.training_history[model_name] = results
        
        logger.info(f"✅ {model_name}: Accuracy = {accuracy:.4f}, CV = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        return results
    
    def _get_grid_search_model(self, model_name: str, base_model: Any) -> Any:
        """Retorna modelo com grid search"""
        param_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2]
            },
            'lightgbm': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }
        
        if model_name in param_grids:
            return GridSearchCV(
                base_model,
                param_grids[model_name],
                cv=3,
                scoring='accuracy',
                n_jobs=-1
            )
        else:
            return base_model
    
    def train_all_models(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        """Treina todos os modelos"""
        logger.info("🚀 Treinando todos os modelos...")
        
        # Modelos para treinar
        models_config = {
            'random_forest': {
                'model': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
                'use_grid_search': True
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'use_grid_search': False
            },
            'logistic_regression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'use_grid_search': False
            },
            'xgboost': {
                'model': xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss'),
                'use_grid_search': True
            },
            'lightgbm': {
                'model': lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1),
                'use_grid_search': True
            },
            'catboost': {
                'model': cb.CatBoostClassifier(iterations=100, random_state=42, verbose=False),
                'use_grid_search': False
            }
        }
        
        # Treinar cada modelo
        for name, config in models_config.items():
            try:
                self.train_single_model(
                    name, 
                    config['model'], 
                    X, 
                    y, 
                    config['use_grid_search']
                )
            except Exception as e:
                logger.error(f"❌ Erro ao treinar {name}: {e}")
        
        self.is_trained = True
        logger.info("🎉 Treinamento de todos os modelos concluído!")
    
    def find_best_model(self) -> str:
        """Encontra o melhor modelo baseado na performance"""
        if not self.training_history:
            raise ValueError("Nenhum modelo foi treinado ainda!")
        
        best_model = None
        best_score = -1
        
        for name, results in self.training_history.items():
            # Usar CV score como critério principal
            score = results['cv_mean']
            if score > best_score:
                best_score = score
                best_model = name
        
        logger.info(f"🏆 Melhor modelo: {best_model} (CV Score: {best_score:.4f})")
        return best_model
    
    def evaluate_model(self, model_name: str, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Avalia um modelo específico"""
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado!")
        
        model = self.models[model_name]
        
        # Predições
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X) if hasattr(model, 'predict_proba') else None
        
        # Métricas
        accuracy = accuracy_score(y, y_pred)
        
        try:
            logloss = log_loss(y, y_proba) if y_proba is not None else float('inf')
        except:
            logloss = float('inf')
        
        # Relatório de classificação
        report = classification_report(y, y_pred, output_dict=True)
        
        # Matriz de confusão
        cm = confusion_matrix(y, y_pred)
        
        return {
            'accuracy': accuracy,
            'log_loss': logloss,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'predictions': y_pred.tolist(),
            'probabilities': y_proba.tolist() if y_proba is not None else None
        }
    
    def get_model_performance_summary(self) -> pd.DataFrame:
        """Retorna resumo da performance de todos os modelos"""
        if not self.training_history:
            return pd.DataFrame()
        
        summary_data = []
        for name, results in self.training_history.items():
            summary_data.append({
                'Model': name,
                'Accuracy': results['accuracy'],
                'CV_Mean': results['cv_mean'],
                'CV_Std': results['cv_std'],
                'Log_Loss': results['log_loss'],
                'Training_Time': results['training_time']
            })
        
        return pd.DataFrame(summary_data).sort_values('CV_Mean', ascending=False)
    
    def save_models(self, filepath: str):
        """Salva todos os modelos treinados"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'encoders': self.encoders,
            'training_history': self.training_history,
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
        self.training_history = model_data['training_history']
        self.is_trained = model_data['is_trained']
        logger.info(f"📂 Modelos carregados de: {filepath}")

class TimeSeriesValidator:
    """Validador para dados de séries temporais"""
    
    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits
        self.tscv = TimeSeriesSplit(n_splits=n_splits)
    
    def validate_model(self, model: Any, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Valida modelo com time series split"""
        logger.info(f"📅 Validando modelo com {self.n_splits} splits temporais...")
        
        scores = []
        
        for train_idx, test_idx in self.tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Treinar e avaliar
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            scores.append(score)
        
        return {
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'scores': scores
        }

def create_sample_data() -> pd.DataFrame:
    """Cria dados de exemplo para teste"""
    np.random.seed(42)
    
    n_matches = 2000
    
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
    
    # Adicionar features básicas
    df['home_form_5'] = df.groupby('home_team_id')['home_score'].rolling(5).mean().reset_index(0, drop=True)
    df['away_form_5'] = df.groupby('away_team_id')['away_score'].rolling(5).mean().reset_index(0, drop=True)
    df['home_goals_avg'] = df.groupby('home_team_id')['home_score'].expanding().mean().reset_index(0, drop=True)
    df['away_goals_avg'] = df.groupby('away_team_id')['away_score'].expanding().mean().reset_index(0, drop=True)
    
    return df.fillna(0)

def main():
    """Função principal para teste"""
    print("🤖 MARABET AI - MODEL TRAINING")
    print("=" * 50)
    
    # Criar dados de exemplo
    print("📊 Criando dados de exemplo...")
    df = create_sample_data()
    print(f"✅ Dados criados: {len(df)} partidas")
    
    # Criar trainer
    trainer = ModelTrainer()
    
    # Preparar dados
    X, y, feature_names = trainer.prepare_data(df)
    
    # Treinar todos os modelos
    trainer.train_all_models(X, y, feature_names)
    
    # Mostrar resumo
    print("\n📊 Resumo da Performance:")
    summary = trainer.get_model_performance_summary()
    print(summary.to_string(index=False))
    
    # Encontrar melhor modelo
    best_model = trainer.find_best_model()
    print(f"\n🏆 Melhor modelo: {best_model}")
    
    # Validar com time series
    print("\n📅 Validação temporal...")
    validator = TimeSeriesValidator()
    best_model_obj = trainer.models[best_model]
    ts_validation = validator.validate_model(best_model_obj, X, y)
    print(f"Score temporal: {ts_validation['mean_score']:.4f} ± {ts_validation['std_score']:.4f}")
    
    print("\n🎉 Treinamento concluído!")

if __name__ == "__main__":
    main()
