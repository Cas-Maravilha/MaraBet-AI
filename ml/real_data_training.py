#!/usr/bin/env python3
"""
Sistema de Treinamento com Dados Reais
MaraBet AI - Treinamento de modelos com dados históricos reais
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import sqlite3
import joblib
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, log_loss
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

logger = logging.getLogger(__name__)

class RealDataTrainer:
    """Treinador de modelos com dados reais"""
    
    def __init__(self, db_path: str = "data/simulated_data.db"):
        """Inicializa treinador com dados reais"""
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.training_data = None
        
        # Configurações de treinamento
        self.test_size = 0.2
        self.random_state = 42
        self.cv_folds = 5
        
        # Modelos a treinar
        self.model_configs = {
            'random_forest': {
                'class': RandomForestClassifier,
                'params': {
                    'n_estimators': 200,
                    'max_depth': 15,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': self.random_state,
                    'n_jobs': -1
                }
            },
            'xgboost': {
                'class': xgb.XGBClassifier,
                'params': {
                    'n_estimators': 200,
                    'learning_rate': 0.1,
                    'max_depth': 8,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'random_state': self.random_state,
                    'eval_metric': 'mlogloss'
                }
            },
            'lightgbm': {
                'class': lgb.LGBMClassifier,
                'params': {
                    'n_estimators': 200,
                    'learning_rate': 0.1,
                    'max_depth': 8,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'random_state': self.random_state,
                    'verbose': -1
                }
            },
            'catboost': {
                'class': cb.CatBoostClassifier,
                'params': {
                    'iterations': 200,
                    'learning_rate': 0.1,
                    'depth': 8,
                    'random_state': self.random_state,
                    'verbose': False
                }
            },
            'logistic_regression': {
                'class': LogisticRegression,
                'params': {
                    'random_state': self.random_state,
                    'max_iter': 1000
                }
            }
        }
    
    def load_data_from_database(self) -> pd.DataFrame:
        """Carrega dados do banco de dados"""
        logger.info("Carregando dados do banco de dados...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Query principal com joins
        query = """
        SELECT 
            m.match_id,
            m.league_id,
            m.season,
            m.date,
            m.home_team_id,
            m.home_team_name,
            m.away_team_id,
            m.away_team_name,
            m.home_score,
            m.away_score,
            m.status,
            hs.shots_total AS home_shots_total,
            hs.shots_on_goal AS home_shots_on_goal,
            hs.possession AS home_possession,
            hs.passes_total AS home_passes_total,
            hs.passes_accurate AS home_passes_accurate,
            hs.fouls AS home_fouls,
            hs.yellow_cards AS home_yellow_cards,
            hs.red_cards AS home_red_cards,
            away_stats.shots_total AS away_shots_total,
            away_stats.shots_on_goal AS away_shots_on_goal,
            away_stats.possession AS away_possession,
            away_stats.passes_total AS away_passes_total,
            away_stats.passes_accurate AS away_passes_accurate,
            away_stats.fouls AS away_fouls,
            away_stats.yellow_cards AS away_yellow_cards,
            away_stats.red_cards AS away_red_cards,
            o.home_win,
            o.draw,
            o.away_win
        FROM matches m
        LEFT JOIN match_stats hs ON m.match_id = hs.match_id AND hs.team_id = m.home_team_id
        LEFT JOIN match_stats away_stats ON m.match_id = away_stats.match_id AND away_stats.team_id = m.away_team_id
        LEFT JOIN odds o ON m.match_id = o.match_id
        WHERE m.status = 'FT' 
        AND m.home_score IS NOT NULL 
        AND m.away_score IS NOT NULL
        ORDER BY m.date
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logger.info(f"Carregados {len(df)} registros do banco de dados")
        return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features para treinamento"""
        logger.info("Criando features...")
        
        # Converter data
        df['date'] = pd.to_datetime(df['date'])
        
        # Criar target (resultado da partida)
        def get_result(row):
            if row['home_score'] > row['away_score']:
                return 'home_win'
            elif row['home_score'] < row['away_score']:
                return 'away_win'
            else:
                return 'draw'
        
        df['result'] = df.apply(get_result, axis=1)
        
        # Features básicas
        df['total_goals'] = df['home_score'] + df['away_score']
        df['goal_difference'] = df['home_score'] - df['away_score']
        df['is_home_advantage'] = 1  # Simplificado
        
        # Features de estatísticas
        df['home_shots_ratio'] = df['home_shots_on_goal'] / (df['home_shots_total'] + 1)
        df['away_shots_ratio'] = df['away_shots_on_goal'] / (df['away_shots_total'] + 1)
        df['home_pass_accuracy'] = df['home_passes_accurate'] / (df['home_passes_total'] + 1)
        df['away_pass_accuracy'] = df['away_passes_accurate'] / (df['away_passes_total'] + 1)
        
        # Features de odds
        df['home_win_prob'] = 1 / df['home_win']
        df['draw_prob'] = 1 / df['draw']
        df['away_win_prob'] = 1 / df['away_win']
        
        # Features temporais
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Features de liga
        df['league_id'] = df['league_id'].astype('category')
        
        # Remover colunas não utilizadas
        columns_to_drop = [
            'match_id', 'date', 'home_team_id', 'away_team_id', 
            'home_team_name', 'away_team_name', 'status',
            'home_score', 'away_score'
        ]
        
        df = df.drop(columns=columns_to_drop, errors='ignore')
        
        # Tratar valores nulos
        # Converter colunas categóricas para string antes de fillna
        categorical_columns = df.select_dtypes(include=['category']).columns
        for col in categorical_columns:
            df[col] = df[col].astype(str)
        
        df = df.fillna(0)
        
        logger.info(f"Features criadas. Shape final: {df.shape}")
        return df
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Prepara dados para treinamento"""
        logger.info("Preparando dados para treinamento...")
        
        # Separar features e target
        target_column = 'result'
        feature_columns = [col for col in df.columns if col != target_column]
        
        X = df[feature_columns]
        y = df[target_column]
        
        # Codificar target
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        self.encoders['target'] = label_encoder
        
        # Separar features numéricas e categóricas
        numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = X.select_dtypes(include=['category', 'object']).columns.tolist()
        
        # Codificar features categóricas
        for col in categorical_features:
            if col in X.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
        
        # Normalizar features numéricas
        scaler = StandardScaler()
        X[numeric_features] = scaler.fit_transform(X[numeric_features])
        self.scalers['main'] = scaler
        
        self.feature_columns = feature_columns
        self.training_data = X
        
        logger.info(f"Dados preparados. Features: {len(feature_columns)}, Amostras: {len(X)}")
        return X, y_encoded, feature_columns
    
    def train_models(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, Any]:
        """Treina todos os modelos"""
        logger.info("Iniciando treinamento de modelos...")
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        results = {}
        
        for model_name, config in self.model_configs.items():
            logger.info(f"Treinando modelo: {model_name}")
            
            try:
                # Criar modelo
                model_class = config['class']
                model_params = config['params']
                model = model_class(**model_params)
                
                # Treinar modelo
                model.fit(X_train, y_train)
                
                # Avaliar modelo
                train_score = model.score(X_train, y_train)
                test_score = model.score(X_test, y_test)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds)
                
                # Predições
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
                
                # Métricas
                accuracy = accuracy_score(y_test, y_pred)
                logloss = log_loss(y_test, y_pred_proba) if y_pred_proba is not None else None
                
                # Salvar modelo
                self.models[model_name] = model
                
                # Resultados
                results[model_name] = {
                    'model': model,
                    'train_score': train_score,
                    'test_score': test_score,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'accuracy': accuracy,
                    'logloss': logloss,
                    'feature_importance': self._get_feature_importance(model, X.columns) if hasattr(model, 'feature_importances_') else None
                }
                
                logger.info(f"{model_name}: Test Score = {test_score:.3f}, CV = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
                
            except Exception as e:
                logger.error(f"Erro ao treinar {model_name}: {e}")
                results[model_name] = {'error': str(e)}
        
        return results
    
    def _get_feature_importance(self, model, feature_names):
        """Obtém importância das features"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            return dict(zip(feature_names, importance))
        return None
    
    def create_ensemble_model(self, X: pd.DataFrame, y: np.ndarray) -> Any:
        """Cria modelo ensemble"""
        logger.info("Criando modelo ensemble...")
        
        from sklearn.ensemble import VotingClassifier
        
        # Selecionar melhores modelos
        ensemble_models = []
        for model_name, model in self.models.items():
            if hasattr(model, 'predict_proba'):
                ensemble_models.append((model_name, model))
        
        if len(ensemble_models) < 2:
            logger.warning("Poucos modelos para ensemble")
            return None
        
        # Criar ensemble
        ensemble = VotingClassifier(
            estimators=ensemble_models,
            voting='soft'  # Usar probabilidades
        )
        
        # Treinar ensemble
        ensemble.fit(X, y)
        
        # Avaliar
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        ensemble.fit(X_train, y_train)
        ensemble_score = ensemble.score(X_test, y_test)
        
        logger.info(f"Ensemble Score: {ensemble_score:.3f}")
        
        self.models['ensemble'] = ensemble
        return ensemble
    
    def save_models(self, output_dir: str = "models"):
        """Salva modelos treinados"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar modelos
        for model_name, model in self.models.items():
            model_path = f"{output_dir}/{model_name}_model.joblib"
            joblib.dump(model, model_path)
            logger.info(f"Modelo {model_name} salvo em {model_path}")
        
        # Salvar scalers e encoders
        joblib.dump(self.scalers, f"{output_dir}/scalers.joblib")
        joblib.dump(self.encoders, f"{output_dir}/encoders.joblib")
        
        # Salvar feature columns
        with open(f"{output_dir}/feature_columns.txt", 'w') as f:
            f.write('\n'.join(self.feature_columns))
        
        logger.info(f"Modelos salvos em {output_dir}")
    
    def load_models(self, model_dir: str = "models"):
        """Carrega modelos treinados"""
        # Carregar modelos
        for model_name in self.model_configs.keys():
            model_path = f"{model_dir}/{model_name}_model.joblib"
            if os.path.exists(model_path):
                self.models[model_name] = joblib.load(model_path)
                logger.info(f"Modelo {model_name} carregado")
        
        # Carregar ensemble se existir
        ensemble_path = f"{model_dir}/ensemble_model.joblib"
        if os.path.exists(ensemble_path):
            self.models['ensemble'] = joblib.load(ensemble_path)
            logger.info("Modelo ensemble carregado")
        
        # Carregar scalers e encoders
        if os.path.exists(f"{model_dir}/scalers.joblib"):
            self.scalers = joblib.load(f"{model_dir}/scalers.joblib")
        
        if os.path.exists(f"{model_dir}/encoders.joblib"):
            self.encoders = joblib.load(f"{model_dir}/encoders.joblib")
        
        # Carregar feature columns
        if os.path.exists(f"{model_dir}/feature_columns.txt"):
            with open(f"{model_dir}/feature_columns.txt", 'r') as f:
                self.feature_columns = f.read().strip().split('\n')
    
    def predict(self, X: pd.DataFrame, model_name: str = 'ensemble') -> Tuple[np.ndarray, np.ndarray]:
        """Faz predições"""
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado")
        
        model = self.models[model_name]
        
        # Aplicar transformações
        X_processed = X.copy()
        
        # Codificar features categóricas
        for col in X_processed.columns:
            if col in self.encoders and col != 'target':
                X_processed[col] = self.encoders[col].transform(X_processed[col].astype(str))
        
        # Normalizar features numéricas
        numeric_features = X_processed.select_dtypes(include=[np.number]).columns
        if 'main' in self.scalers:
            X_processed[numeric_features] = self.scalers['main'].transform(X_processed[numeric_features])
        
        # Fazer predições
        predictions = model.predict(X_processed)
        probabilities = model.predict_proba(X_processed) if hasattr(model, 'predict_proba') else None
        
        return predictions, probabilities
    
    def generate_training_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório de treinamento"""
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE TREINAMENTO - MARABET AI")
        report.append("=" * 60)
        
        # Resumo geral
        report.append(f"\nRESUMO GERAL:")
        report.append(f"  Modelos Treinados: {len([r for r in results.values() if 'error' not in r])}")
        report.append(f"  Features: {len(self.feature_columns)}")
        report.append(f"  Amostras: {len(self.training_data) if self.training_data is not None else 'N/A'}")
        
        # Resultados por modelo
        report.append(f"\nRESULTADOS POR MODELO:")
        for model_name, result in results.items():
            if 'error' in result:
                report.append(f"  {model_name}: ❌ ERRO - {result['error']}")
            else:
                report.append(f"  {model_name}:")
                report.append(f"    Test Score: {result['test_score']:.3f}")
                report.append(f"    CV Score: {result['cv_mean']:.3f} ± {result['cv_std']:.3f}")
                report.append(f"    Accuracy: {result['accuracy']:.3f}")
                if result['logloss']:
                    report.append(f"    Log Loss: {result['logloss']:.3f}")
        
        # Melhor modelo
        best_model = None
        best_score = -1
        for model_name, result in results.items():
            if 'error' not in result and result['test_score'] > best_score:
                best_score = result['test_score']
                best_model = model_name
        
        if best_model:
            report.append(f"\nMELHOR MODELO: {best_model} (Score: {best_score:.3f})")
        
        # Feature importance (se disponível)
        if best_model and results[best_model].get('feature_importance'):
            report.append(f"\nTOP 10 FEATURES MAIS IMPORTANTES:")
            importance = results[best_model]['feature_importance']
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            for feature, imp in sorted_features[:10]:
                report.append(f"  {feature}: {imp:.3f}")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Instância global
real_data_trainer = RealDataTrainer()

if __name__ == "__main__":
    # Teste do treinador com dados reais
    print("🧪 TESTANDO TREINADOR COM DADOS REAIS")
    print("=" * 50)
    
    # Verificar se banco de dados existe
    if not os.path.exists("data/simulated_data.db"):
        print("❌ Banco de dados não encontrado. Execute o simulador de dados primeiro.")
        exit(1)
    
    # Inicializar treinador
    trainer = RealDataTrainer()
    
    # Carregar dados
    print("Carregando dados do banco...")
    df = trainer.load_data_from_database()
    
    if len(df) == 0:
        print("❌ Nenhum dado encontrado no banco de dados.")
        exit(1)
    
    print(f"Carregados {len(df)} registros")
    
    # Criar features
    print("Criando features...")
    df_features = trainer.create_features(df)
    
    # Preparar dados de treinamento
    print("Preparando dados de treinamento...")
    X, y, feature_columns = trainer.prepare_training_data(df_features)
    
    # Treinar modelos
    print("Treinando modelos...")
    results = trainer.train_models(X, y)
    
    # Criar ensemble
    print("Criando ensemble...")
    ensemble = trainer.create_ensemble_model(X, y)
    
    # Salvar modelos
    print("Salvando modelos...")
    trainer.save_models()
    
    # Gerar relatório
    report = trainer.generate_training_report(results)
    print(f"\n{report}")
    
    print("\n🎉 TESTE DE TREINAMENTO COM DADOS REAIS CONCLUÍDO!")
