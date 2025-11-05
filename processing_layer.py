"""
CAMADA DE PROCESSAMENTO - MaraBet AI
Sistema modular para análise, cálculos e machine learning
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedData:
    """Dados processados"""
    id: str
    data_type: str
    processed_data: Dict[str, Any]
    features: List[str]
    predictions: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

@dataclass
class ModelMetrics:
    """Métricas do modelo"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    r2_score: float
    training_time: float
    prediction_time: float

class DataProcessor(ABC):
    """Classe abstrata para processadores de dados"""
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> ProcessedData:
        """Processa dados"""
        pass
    
    @abstractmethod
    def get_features(self) -> List[str]:
        """Retorna features disponíveis"""
        pass

class MatchDataProcessor(DataProcessor):
    """Processador de dados de partidas"""
    
    def __init__(self):
        self.features = [
            'home_goals_avg', 'away_goals_avg', 'home_conceded_avg', 'away_conceded_avg',
            'home_form', 'away_form', 'h2h_goals_avg', 'home_possession', 'away_possession',
            'home_shots_avg', 'away_shots_avg', 'home_xg_avg', 'away_xg_avg',
            'temperature', 'humidity', 'wind_speed', 'is_weekend', 'days_since_last_match'
        ]
    
    def process(self, data: Dict[str, Any]) -> ProcessedData:
        """Processa dados de partida"""
        try:
            processed_data = self._extract_features(data)
            
            return ProcessedData(
                id=f"match_{data.get('id', 'unknown')}",
                data_type="match_processed",
                processed_data=processed_data,
                features=self.features,
                timestamp=datetime.now(),
                metadata={
                    'original_data_keys': list(data.keys()),
                    'processing_version': '1.0',
                    'feature_count': len(self.features)
                }
            )
        except Exception as e:
            logger.error(f"Erro no processamento de partida: {e}")
            return self._create_error_data(data, str(e))
    
    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai features dos dados"""
        features = {}
        
        # Dados básicos da partida
        match_info = data.get('fixtures', [{}])[0] if 'fixtures' in data else {}
        
        # Simula extração de features (em produção, processaria dados reais)
        features['home_goals_avg'] = np.random.uniform(1.5, 3.0)
        features['away_goals_avg'] = np.random.uniform(1.0, 2.5)
        features['home_conceded_avg'] = np.random.uniform(0.8, 2.0)
        features['away_conceded_avg'] = np.random.uniform(0.8, 2.0)
        features['home_form'] = np.random.uniform(0.3, 0.9)
        features['away_form'] = np.random.uniform(0.3, 0.9)
        features['h2h_goals_avg'] = np.random.uniform(2.0, 4.0)
        features['home_possession'] = np.random.uniform(45, 70)
        features['away_possession'] = np.random.uniform(30, 55)
        features['home_shots_avg'] = np.random.uniform(8, 18)
        features['away_shots_avg'] = np.random.uniform(6, 15)
        features['home_xg_avg'] = np.random.uniform(1.2, 2.8)
        features['away_xg_avg'] = np.random.uniform(1.0, 2.2)
        
        # Dados ambientais
        features['temperature'] = np.random.uniform(5, 25)
        features['humidity'] = np.random.uniform(40, 90)
        features['wind_speed'] = np.random.uniform(5, 25)
        features['is_weekend'] = np.random.choice([0, 1])
        features['days_since_last_match'] = np.random.randint(3, 14)
        
        return features
    
    def get_features(self) -> List[str]:
        """Retorna features disponíveis"""
        return self.features
    
    def _create_error_data(self, original_data: Dict[str, Any], error: str) -> ProcessedData:
        """Cria dados de erro"""
        return ProcessedData(
            id=f"error_{datetime.now().timestamp()}",
            data_type="error",
            processed_data={'error': error},
            features=[],
            timestamp=datetime.now(),
            metadata={'error': error, 'original_data': original_data}
        )

class OddsDataProcessor(DataProcessor):
    """Processador de dados de odds"""
    
    def __init__(self):
        self.features = [
            'home_odd', 'draw_odd', 'away_odd', 'over_2_5_odd', 'under_2_5_odd',
            'both_teams_score_odd', 'home_win_prob', 'draw_prob', 'away_win_prob',
            'over_2_5_prob', 'under_2_5_prob', 'both_teams_score_prob',
            'home_value', 'draw_value', 'away_value', 'over_2_5_value', 'under_2_5_value',
            'both_teams_score_value', 'market_movement', 'bookmaker_count'
        ]
    
    def process(self, data: Dict[str, Any]) -> ProcessedData:
        """Processa dados de odds"""
        try:
            processed_data = self._extract_odds_features(data)
            
            return ProcessedData(
                id=f"odds_{data.get('id', 'unknown')}",
                data_type="odds_processed",
                processed_data=processed_data,
                features=self.features,
                timestamp=datetime.now(),
                metadata={
                    'original_data_keys': list(data.keys()),
                    'processing_version': '1.0',
                    'feature_count': len(self.features)
                }
            )
        except Exception as e:
            logger.error(f"Erro no processamento de odds: {e}")
            return self._create_error_data(data, str(e))
    
    def _extract_odds_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai features das odds"""
        features = {}
        
        # Simula extração de odds (em produção, processaria dados reais)
        features['home_odd'] = np.random.uniform(1.2, 5.0)
        features['draw_odd'] = np.random.uniform(2.5, 4.5)
        features['away_odd'] = np.random.uniform(1.5, 8.0)
        features['over_2_5_odd'] = np.random.uniform(1.3, 2.5)
        features['under_2_5_odd'] = np.random.uniform(1.4, 3.0)
        features['both_teams_score_odd'] = np.random.uniform(1.2, 2.8)
        
        # Calcula probabilidades implícitas
        features['home_win_prob'] = 1 / features['home_odd']
        features['draw_prob'] = 1 / features['draw_odd']
        features['away_win_prob'] = 1 / features['away_odd']
        features['over_2_5_prob'] = 1 / features['over_2_5_odd']
        features['under_2_5_prob'] = 1 / features['under_2_5_odd']
        features['both_teams_score_prob'] = 1 / features['both_teams_score_odd']
        
        # Calcula valores (assumindo probabilidades reais)
        real_home_prob = np.random.uniform(0.4, 0.8)
        features['home_value'] = (real_home_prob * features['home_odd']) - 1
        features['draw_value'] = (0.2 * features['draw_odd']) - 1
        features['away_value'] = (0.3 * features['away_odd']) - 1
        
        real_over_prob = np.random.uniform(0.5, 0.8)
        features['over_2_5_value'] = (real_over_prob * features['over_2_5_odd']) - 1
        features['under_2_5_value'] = ((1 - real_over_prob) * features['under_2_5_odd']) - 1
        
        real_bts_prob = np.random.uniform(0.4, 0.7)
        features['both_teams_score_value'] = (real_bts_prob * features['both_teams_score_odd']) - 1
        
        # Features adicionais
        features['market_movement'] = np.random.uniform(-0.2, 0.2)
        features['bookmaker_count'] = np.random.randint(5, 20)
        
        return features
    
    def get_features(self) -> List[str]:
        """Retorna features disponíveis"""
        return self.features
    
    def _create_error_data(self, original_data: Dict[str, Any], error: str) -> ProcessedData:
        """Cria dados de erro"""
        return ProcessedData(
            id=f"error_{datetime.now().timestamp()}",
            data_type="error",
            processed_data={'error': error},
            features=[],
            timestamp=datetime.now(),
            metadata={'error': error, 'original_data': original_data}
        )

class MLModel(ABC):
    """Classe abstrata para modelos de ML"""
    
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Treina o modelo"""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Faz predições"""
        pass
    
    @abstractmethod
    def save_model(self, filepath: str) -> bool:
        """Salva o modelo"""
        pass
    
    @abstractmethod
    def load_model(self, filepath: str) -> bool:
        """Carrega o modelo"""
        pass

class MatchPredictionModel(MLModel):
    """Modelo de predição de partidas"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.features = []
        self.metrics = None
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Treina o modelo"""
        start_time = datetime.now()
        
        try:
            # Divide os dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Treina o modelo
            self.model.fit(X_train, y_train)
            
            # Faz predições
            y_pred = self.model.predict(X_test)
            
            # Calcula métricas
            mse = mean_squared_error(y_test, y_pred)
            r2 = self.model.score(X_test, y_test)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            self.metrics = ModelMetrics(
                model_name="MatchPredictionModel",
                accuracy=0.0,  # Não aplicável para regressão
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                mse=mse,
                r2_score=r2,
                training_time=training_time,
                prediction_time=0.0
            )
            
            self.is_trained = True
            logger.info(f"Modelo treinado com R² = {r2:.3f}")
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return ModelMetrics(
                model_name="MatchPredictionModel",
                accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
                mse=float('inf'), r2_score=0.0,
                training_time=0.0, prediction_time=0.0
            )
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Faz predições"""
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        start_time = datetime.now()
        predictions = self.model.predict(X)
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        if self.metrics:
            self.metrics.prediction_time = prediction_time
        
        return predictions
    
    def save_model(self, filepath: str) -> bool:
        """Salva o modelo"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'is_trained': self.is_trained,
                'features': self.features,
                'metrics': self.metrics
            }, filepath)
            logger.info(f"Modelo salvo em {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Carrega o modelo"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Arquivo {filepath} não encontrado")
                return False
            
            data = joblib.load(filepath)
            self.model = data['model']
            self.is_trained = data['is_trained']
            self.features = data['features']
            self.metrics = data['metrics']
            
            logger.info(f"Modelo carregado de {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False

class ValueBettingModel(MLModel):
    """Modelo para identificação de value bets"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.features = []
        self.metrics = None
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Treina o modelo"""
        start_time = datetime.now()
        
        try:
            # Divide os dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Treina o modelo
            self.model.fit(X_train, y_train)
            
            # Faz predições
            y_pred = self.model.predict(X_test)
            
            # Calcula métricas
            accuracy = accuracy_score(y_test, y_pred)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            self.metrics = ModelMetrics(
                model_name="ValueBettingModel",
                accuracy=accuracy,
                precision=0.0,  # Implementar cálculo real
                recall=0.0,
                f1_score=0.0,
                mse=0.0,
                r2_score=0.0,
                training_time=training_time,
                prediction_time=0.0
            )
            
            self.is_trained = True
            logger.info(f"Modelo treinado com acurácia = {accuracy:.3f}")
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return ModelMetrics(
                model_name="ValueBettingModel",
                accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
                mse=0.0, r2_score=0.0,
                training_time=0.0, prediction_time=0.0
            )
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Faz predições"""
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        start_time = datetime.now()
        predictions = self.model.predict(X)
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        if self.metrics:
            self.metrics.prediction_time = prediction_time
        
        return predictions
    
    def save_model(self, filepath: str) -> bool:
        """Salva o modelo"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'is_trained': self.is_trained,
                'features': self.features,
                'metrics': self.metrics
            }, filepath)
            logger.info(f"Modelo salvo em {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Carrega o modelo"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Arquivo {filepath} não encontrado")
                return False
            
            data = joblib.load(filepath)
            self.model = data['model']
            self.is_trained = data['is_trained']
            self.features = data['features']
            self.metrics = data['metrics']
            
            logger.info(f"Modelo carregado de {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False

class ProcessingManager:
    """Gerenciador da camada de processamento"""
    
    def __init__(self):
        self.processors: Dict[str, DataProcessor] = {}
        self.models: Dict[str, MLModel] = {}
        self.processed_data: List[ProcessedData] = []
    
    def add_processor(self, name: str, processor: DataProcessor):
        """Adiciona um processador"""
        self.processors[name] = processor
        logger.info(f"Processador {name} adicionado")
    
    def add_model(self, name: str, model: MLModel):
        """Adiciona um modelo"""
        self.models[name] = model
        logger.info(f"Modelo {name} adicionado")
    
    def process_data(self, data: Dict[str, Any], processor_name: str) -> ProcessedData:
        """Processa dados"""
        processor = self.processors.get(processor_name)
        if not processor:
            logger.error(f"Processador {processor_name} não encontrado")
            return ProcessedData(
                id="error",
                data_type="error",
                processed_data={'error': f'Processador {processor_name} não encontrado'},
                features=[],
                timestamp=datetime.now()
            )
        
        processed = processor.process(data)
        self.processed_data.append(processed)
        return processed
    
    def train_model(self, model_name: str, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Treina um modelo"""
        model = self.models.get(model_name)
        if not model:
            logger.error(f"Modelo {model_name} não encontrado")
            return ModelMetrics(
                model_name=model_name,
                accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
                mse=0.0, r2_score=0.0, training_time=0.0, prediction_time=0.0
            )
        
        return model.train(X, y)
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Faz predições com um modelo"""
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Modelo {model_name} não encontrado")
        
        return model.predict(X)
    
    def get_processed_data(self, data_type: str) -> List[ProcessedData]:
        """Retorna dados processados por tipo"""
        return [data for data in self.processed_data if data.data_type == data_type]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        return {
            'total_processed': len(self.processed_data),
            'processors': len(self.processors),
            'models': len(self.models),
            'data_types': {
                data_type: len([d for d in self.processed_data if d.data_type == data_type])
                for data_type in set(data.data_type for data in self.processed_data)
            }
        }

if __name__ == "__main__":
    # Teste da camada de processamento
    manager = ProcessingManager()
    
    # Adiciona processadores
    match_processor = MatchDataProcessor()
    odds_processor = OddsDataProcessor()
    
    manager.add_processor("match", match_processor)
    manager.add_processor("odds", odds_processor)
    
    # Adiciona modelos
    match_model = MatchPredictionModel()
    value_model = ValueBettingModel()
    
    manager.add_model("match_prediction", match_model)
    manager.add_model("value_betting", value_model)
    
    # Testa processamento
    match_data = {"id": "123", "fixtures": [{"home_team": "City", "away_team": "Arsenal"}]}
    odds_data = {"id": "456", "odds": [{"home": 1.65, "away": 5.50}]}
    
    processed_match = manager.process_data(match_data, "match")
    processed_odds = manager.process_data(odds_data, "odds")
    
    print(f"Match processado: {len(processed_match.features)} features")
    print(f"Odds processado: {len(processed_odds.features)} features")
    
    # Testa treinamento (com dados simulados)
    X = np.random.rand(100, 10)
    y = np.random.rand(100)
    
    metrics = manager.train_model("match_prediction", X, y)
    print(f"Métricas do modelo: R² = {metrics.r2_score:.3f}")
    
    # Estatísticas
    stats = manager.get_processing_stats()
    print(f"Estatísticas: {stats}")
    
    print("Teste da camada de processamento concluído!")
