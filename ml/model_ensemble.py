#!/usr/bin/env python3
"""
Sistema de Ensemble para combinar múltiplos modelos de ML
MaraBet AI - Sistema de Apostas Esportivas Inteligentes
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, log_loss
import logging
import joblib
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelEnsemble:
    """Classe para combinar múltiplos modelos de ML"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.ensemble_model = None
        self.performance_history = {}
        self.is_trained = False
    
    def add_model(self, name: str, model: Any, weight: float = 1.0):
        """Adiciona um modelo ao ensemble"""
        self.models[name] = model
        self.weights[name] = weight
        logger.info(f"✅ Modelo {name} adicionado com peso {weight}")
    
    def create_voting_ensemble(self, voting_type: str = 'soft'):
        """Cria ensemble por votação"""
        if not self.models:
            raise ValueError("Nenhum modelo adicionado ao ensemble!")
        
        # Criar lista de estimadores
        estimators = [(name, model) for name, model in self.models.items()]
        
        # Criar ensemble
        self.ensemble_model = VotingClassifier(
            estimators=estimators,
            voting=voting_type,
            weights=list(self.weights.values())
        )
        
        logger.info(f"✅ Ensemble de votação criado com {len(self.models)} modelos")
    
    def create_weighted_ensemble(self, X: np.ndarray, y: np.ndarray):
        """Cria ensemble com pesos baseados na performance"""
        logger.info("🔧 Criando ensemble com pesos otimizados...")
        
        # Avaliar cada modelo individualmente
        model_scores = {}
        
        for name, model in self.models.items():
            try:
                # Cross-validation
                scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
                model_scores[name] = scores.mean()
                logger.info(f"  {name}: {scores.mean():.4f} ± {scores.std():.4f}")
            except Exception as e:
                logger.error(f"❌ Erro ao avaliar {name}: {e}")
                model_scores[name] = 0.0
        
        # Calcular pesos baseados na performance
        total_score = sum(model_scores.values())
        if total_score > 0:
            for name in self.models.keys():
                self.weights[name] = model_scores[name] / total_score
        else:
            # Pesos iguais se todos falharem
            for name in self.models.keys():
                self.weights[name] = 1.0 / len(self.models)
        
        logger.info("✅ Pesos otimizados calculados")
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray):
        """Treina o ensemble"""
        if not self.ensemble_model:
            self.create_voting_ensemble()
        
        logger.info("🤖 Treinando ensemble...")
        
        try:
            self.ensemble_model.fit(X, y)
            self.is_trained = True
            logger.info("✅ Ensemble treinado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao treinar ensemble: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """Faz predição com o ensemble"""
        if not self.is_trained:
            raise ValueError("Ensemble não foi treinado ainda!")
        
        # Predição do ensemble
        ensemble_pred = self.ensemble_model.predict(X)
        ensemble_proba = self.ensemble_model.predict_proba(X)
        
        # Predições individuais
        individual_predictions = {}
        individual_probabilities = {}
        
        for name, model in self.models.items():
            try:
                pred = model.predict(X)
                proba = model.predict_proba(X)
                
                individual_predictions[name] = pred[0]
                individual_probabilities[name] = proba[0]
            except Exception as e:
                logger.error(f"❌ Erro na predição com {name}: {e}")
        
        # Calcular confiança
        confidence = np.max(ensemble_proba[0]) if len(ensemble_proba[0]) > 0 else 0
        
        # Calcular acordo entre modelos
        agreement = self._calculate_agreement(individual_predictions)
        
        return {
            'prediction': ensemble_pred[0],
            'probability': ensemble_proba[0],
            'confidence': confidence,
            'agreement': agreement,
            'individual_predictions': individual_predictions,
            'individual_probabilities': individual_probabilities,
            'weights': self.weights
        }
    
    def _calculate_agreement(self, predictions: Dict[str, Any]) -> float:
        """Calcula o acordo entre as predições dos modelos"""
        if not predictions:
            return 0.0
        
        pred_values = list(predictions.values())
        if not pred_values:
            return 0.0
        
        # Converter predições para valores hasháveis
        hashable_values = []
        for pred in pred_values:
            if isinstance(pred, np.ndarray):
                hashable_values.append(pred[0])
            else:
                hashable_values.append(pred)
        
        # Contar quantas predições são iguais à mais comum
        from collections import Counter
        most_common = Counter(hashable_values).most_common(1)[0][0]
        agreement_count = sum(1 for pred in hashable_values if pred == most_common)
        
        return agreement_count / len(hashable_values)
    
    def evaluate_ensemble(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Avalia o performance do ensemble"""
        if not self.is_trained:
            raise ValueError("Ensemble não foi treinado ainda!")
        
        # Predições
        y_pred = self.ensemble_model.predict(X)
        y_proba = self.ensemble_model.predict_proba(X)
        
        # Métricas
        accuracy = accuracy_score(y, y_pred)
        
        try:
            logloss = log_loss(y, y_proba)
        except:
            logloss = float('inf')
        
        # Cross-validation
        cv_scores = cross_val_score(self.ensemble_model, X, y, cv=5, scoring='accuracy')
        
        performance = {
            'accuracy': accuracy,
            'log_loss': logloss,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_min': cv_scores.min(),
            'cv_max': cv_scores.max()
        }
        
        # Salvar histórico
        self.performance_history[datetime.now().isoformat()] = performance
        
        logger.info(f"📊 Performance do ensemble: {accuracy:.4f}")
        return performance
    
    def get_model_weights(self) -> Dict[str, float]:
        """Retorna os pesos dos modelos"""
        return self.weights.copy()
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Atualiza os pesos dos modelos"""
        for name, weight in new_weights.items():
            if name in self.weights:
                self.weights[name] = weight
                logger.info(f"✅ Peso do modelo {name} atualizado para {weight}")
    
    def save_ensemble(self, filepath: str):
        """Salva o ensemble treinado"""
        ensemble_data = {
            'ensemble_model': self.ensemble_model,
            'models': self.models,
            'weights': self.weights,
            'performance_history': self.performance_history,
            'is_trained': self.is_trained
        }
        joblib.dump(ensemble_data, filepath)
        logger.info(f"💾 Ensemble salvo em: {filepath}")
    
    def load_ensemble(self, filepath: str):
        """Carrega o ensemble treinado"""
        ensemble_data = joblib.load(filepath)
        self.ensemble_model = ensemble_data['ensemble_model']
        self.models = ensemble_data['models']
        self.weights = ensemble_data['weights']
        self.performance_history = ensemble_data['performance_history']
        self.is_trained = ensemble_data['is_trained']
        logger.info(f"📂 Ensemble carregado de: {filepath}")

class AdvancedEnsemble:
    """Ensemble avançado com múltiplas estratégias"""
    
    def __init__(self):
        self.ensembles = {}
        self.meta_model = None
        self.is_trained = False
    
    def add_ensemble(self, name: str, ensemble: ModelEnsemble):
        """Adiciona um ensemble"""
        self.ensembles[name] = ensemble
        logger.info(f"✅ Ensemble {name} adicionado")
    
    def create_meta_ensemble(self, X: np.ndarray, y: np.ndarray):
        """Cria meta-ensemble que combina outros ensembles"""
        logger.info("🚀 Criando meta-ensemble...")
        
        # Treinar todos os ensembles
        for name, ensemble in self.ensembles.items():
            if not ensemble.is_trained:
                ensemble.train_ensemble(X, y)
        
        # Criar features para meta-modelo
        meta_features = self._create_meta_features(X)
        
        # Treinar meta-modelo
        from sklearn.ensemble import RandomForestClassifier
        self.meta_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.meta_model.fit(meta_features, y)
        
        self.is_trained = True
        logger.info("✅ Meta-ensemble criado!")
    
    def _create_meta_features(self, X: np.ndarray) -> np.ndarray:
        """Cria features para o meta-modelo"""
        meta_features_list = []
        
        for name, ensemble in self.ensembles.items():
            if ensemble.is_trained:
                # Predições do ensemble
                pred = ensemble.ensemble_model.predict(X)
                proba = ensemble.ensemble_model.predict_proba(X)
                
                # Adicionar predições e probabilidades
                meta_features_list.append(pred.reshape(-1, 1))
                meta_features_list.append(proba)
        
        # Combinar features
        if meta_features_list:
            return np.hstack(meta_features_list)
        else:
            return X
    
    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """Faz predição com meta-ensemble"""
        if not self.is_trained:
            raise ValueError("Meta-ensemble não foi treinado ainda!")
        
        # Features do meta-modelo
        meta_features = self._create_meta_features(X)
        
        # Predição do meta-modelo
        meta_pred = self.meta_model.predict(meta_features)
        meta_proba = self.meta_model.predict_proba(meta_features)
        
        # Predições dos ensembles individuais
        ensemble_predictions = {}
        ensemble_probabilities = {}
        
        for name, ensemble in self.ensembles.items():
            if ensemble.is_trained:
                pred = ensemble.predict(X)
                ensemble_predictions[name] = pred
                ensemble_probabilities[name] = pred['probability']
        
        return {
            'prediction': meta_pred[0],
            'probability': meta_proba[0],
            'confidence': np.max(meta_proba[0]),
            'ensemble_predictions': ensemble_predictions,
            'ensemble_probabilities': ensemble_probabilities
        }

def main():
    """Função principal para teste"""
    print("🤖 MARABET AI - MODEL ENSEMBLE")
    print("=" * 50)
    
    # Criar dados de exemplo
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, random_state=42)
    
    print(f"📊 Dados: {X.shape[0]} amostras, {X.shape[1]} features")
    
    # Criar ensemble
    ensemble = ModelEnsemble()
    
    # Adicionar modelos
    ensemble.add_model('rf', RandomForestClassifier(n_estimators=100, random_state=42))
    ensemble.add_model('gb', GradientBoostingClassifier(n_estimators=100, random_state=42))
    ensemble.add_model('lr', LogisticRegression(random_state=42, max_iter=1000))
    
    # Treinar ensemble
    ensemble.train_ensemble(X, y)
    
    # Avaliar performance
    performance = ensemble.evaluate_ensemble(X, y)
    print(f"📊 Performance: {performance['accuracy']:.4f}")
    
    # Testar predição
    sample_X = X[:1]
    prediction = ensemble.predict(sample_X)
    print(f"🔮 Predição: {prediction['prediction']}")
    print(f"🎯 Confiança: {prediction['confidence']:.4f}")
    print(f"🤝 Acordo: {prediction['agreement']:.4f}")
    
    print("\n🎉 Teste do ensemble concluído!")

if __name__ == "__main__":
    main()
