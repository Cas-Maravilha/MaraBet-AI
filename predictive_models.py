"""
ETAPA 2: MODELAGEM PREDITIVA - MaraBet AI
Implementa algoritmos especializados para análise preditiva de apostas esportivas
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error, log_loss
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier, CatBoostRegressor
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal, Categorical
import logging
from typing import Dict, List, Tuple, Optional, Union
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoissonModel:
    """
    Modelo Poisson para esportes com pontuação (futebol)
    Modela a distribuição de gols como processos de Poisson independentes
    """
    
    def __init__(self):
        self.home_attack = None
        self.home_defense = None
        self.away_attack = None
        self.away_defense = None
        self.home_advantage = None
        self.fitted = False
        
    def fit(self, matches_data: pd.DataFrame):
        """
        Ajusta o modelo Poisson aos dados históricos
        """
        logger.info("Ajustando modelo Poisson...")
        
        try:
            # Prepara dados
            X = self._prepare_poisson_data(matches_data)
            
            # Otimiza parâmetros usando Maximum Likelihood
            result = self._optimize_poisson_parameters(X)
            
            if result.success:
                self.home_attack = result.x[0]
                self.home_defense = result.x[1]
                self.away_attack = result.x[2]
                self.away_defense = result.x[3]
                self.home_advantage = result.x[4]
                self.fitted = True
                
                logger.info("Modelo Poisson ajustado com sucesso")
                logger.info(f"Parâmetros: Home Attack={self.home_attack:.3f}, "
                          f"Home Defense={self.home_defense:.3f}, "
                          f"Away Attack={self.away_attack:.3f}, "
                          f"Away Defense={self.away_defense:.3f}, "
                          f"Home Advantage={self.home_advantage:.3f}")
            else:
                logger.error("Falha na otimização do modelo Poisson")
                
        except Exception as e:
            logger.error(f"Erro ao ajustar modelo Poisson: {e}")
    
    def predict(self, home_team: str, away_team: str, home_team_stats: Dict, away_team_stats: Dict) -> Dict:
        """
        Faz predição usando o modelo Poisson
        """
        if not self.fitted:
            raise ValueError("Modelo não foi ajustado. Execute fit() primeiro.")
        
        # Calcula lambda (taxa de gols esperada)
        lambda_home = np.exp(self.home_attack + self.away_defense + self.home_advantage)
        lambda_away = np.exp(self.away_attack + self.home_defense)
        
        # Ajusta baseado nas estatísticas dos times
        home_form_factor = self._calculate_form_factor(home_team_stats)
        away_form_factor = self._calculate_form_factor(away_team_stats)
        
        lambda_home *= home_form_factor
        lambda_away *= away_form_factor
        
        # Calcula probabilidades para diferentes resultados
        max_goals = 6  # Máximo de gols para calcular
        probabilities = {}
        
        # Probabilidades de vitória da casa, empate, vitória do visitante
        prob_home_win = 0
        prob_draw = 0
        prob_away_win = 0
        
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                prob = stats.poisson.pmf(home_goals, lambda_home) * stats.poisson.pmf(away_goals, lambda_away)
                
                if home_goals > away_goals:
                    prob_home_win += prob
                elif home_goals == away_goals:
                    prob_draw += prob
                else:
                    prob_away_win += prob
        
        # Normaliza probabilidades
        total_prob = prob_home_win + prob_draw + prob_away_win
        prob_home_win /= total_prob
        prob_draw /= total_prob
        prob_away_win /= total_prob
        
        # Calcula odds
        odds_home = 1 / prob_home_win if prob_home_win > 0 else 1000
        odds_draw = 1 / prob_draw if prob_draw > 0 else 1000
        odds_away = 1 / prob_away_win if prob_away_win > 0 else 1000
        
        # Predição mais provável
        if prob_home_win > max(prob_draw, prob_away_win):
            predicted_result = 'home_win'
        elif prob_draw > prob_away_win:
            predicted_result = 'draw'
        else:
            predicted_result = 'away_win'
        
        return {
            'model_type': 'poisson',
            'predicted_result': predicted_result,
            'probabilities': {
                'home_win': prob_home_win,
                'draw': prob_draw,
                'away_win': prob_away_win
            },
            'odds': {
                'home': odds_home,
                'draw': odds_draw,
                'away': odds_away
            },
            'expected_goals': {
                'home': lambda_home,
                'away': lambda_away
            },
            'confidence': max(prob_home_win, prob_draw, prob_away_win)
        }
    
    def _prepare_poisson_data(self, matches_data: pd.DataFrame) -> np.ndarray:
        """Prepara dados para o modelo Poisson"""
        # Cria matriz de dados: [home_goals, away_goals, home_team_id, away_team_id, is_home]
        data = []
        
        for _, match in matches_data.iterrows():
            home_goals = match.get('home_goals', 0)
            away_goals = match.get('away_goals', 0)
            home_team_id = hash(match.get('home_team', '')) % 1000
            away_team_id = hash(match.get('away_team', '')) % 1000
            is_home = 1  # Sempre 1 para o time da casa
            
            data.append([home_goals, away_goals, home_team_id, away_team_id, is_home])
        
        return np.array(data)
    
    def _optimize_poisson_parameters(self, X: np.ndarray) -> object:
        """Otimiza parâmetros do modelo Poisson usando Maximum Likelihood"""
        
        def negative_log_likelihood(params):
            home_attack, home_defense, away_attack, away_defense, home_advantage = params
            
            log_likelihood = 0
            
            for home_goals, away_goals, home_team_id, away_team_id, is_home in X:
                # Calcula lambda para cada time
                lambda_home = np.exp(home_attack + away_defense + home_advantage * is_home)
                lambda_away = np.exp(away_attack + home_defense)
                
                # Calcula log-likelihood
                log_likelihood += (home_goals * np.log(lambda_home) - lambda_home - 
                                 np.log(np.math.factorial(home_goals)))
                log_likelihood += (away_goals * np.log(lambda_away) - lambda_away - 
                                 np.log(np.math.factorial(away_goals)))
            
            return -log_likelihood
        
        # Parâmetros iniciais
        initial_params = [0.5, 0.5, 0.5, 0.5, 0.1]
        
        # Otimização
        result = minimize(negative_log_likelihood, initial_params, method='L-BFGS-B')
        
        return result
    
    def _calculate_form_factor(self, team_stats: Dict) -> float:
        """Calcula fator de forma para ajustar predições"""
        if not team_stats:
            return 1.0
        
        # Usa forma recente se disponível
        recent_form = team_stats.get('recent_form', {})
        if recent_form:
            form = recent_form.get('form', 'average')
            form_factors = {'excellent': 1.2, 'good': 1.1, 'average': 1.0, 'poor': 0.9}
            return form_factors.get(form, 1.0)
        
        return 1.0

class MLEnsemble:
    """
    Machine Learning Ensemble (Random Forest + XGBoost)
    Combina múltiplos algoritmos para máxima precisão
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.fitted = False
        
    def fit(self, X: pd.DataFrame, y: pd.Series, feature_columns: List[str]):
        """
        Treina ensemble de modelos
        """
        logger.info("Treinando ensemble de modelos ML...")
        
        try:
            self.feature_columns = feature_columns
            X_clean = X[feature_columns].fillna(0)
            
            # Divide dados
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Normaliza dados
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            self.scalers['main'] = scaler
            
            # Treina Random Forest
            rf = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            rf.fit(X_train, y_train)
            self.models['random_forest'] = rf
            
            # Treina XGBoost
            xgb_model = xgb.XGBClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='mlogloss'
            )
            xgb_model.fit(X_train, y_train)
            self.models['xgboost'] = xgb_model
            
            # Treina LightGBM
            lgb_model = lgb.LGBMClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )
            lgb_model.fit(X_train, y_train)
            self.models['lightgbm'] = lgb_model
            
            # Treina CatBoost
            cat_model = CatBoostClassifier(
                iterations=200,
                learning_rate=0.1,
                depth=8,
                random_state=42,
                verbose=False
            )
            cat_model.fit(X_train, y_train)
            self.models['catboost'] = cat_model
            
            # Treina Logistic Regression
            lr = LogisticRegression(
                random_state=42,
                max_iter=1000,
                C=1.0
            )
            lr.fit(X_train_scaled, y_train)
            self.models['logistic_regression'] = lr
            
            self.fitted = True
            
            # Avalia performance
            self._evaluate_models(X_test, X_test_scaled, y_test)
            
            logger.info("Ensemble ML treinado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao treinar ensemble ML: {e}")
    
    def predict(self, X: pd.DataFrame) -> Dict:
        """
        Faz predição usando ensemble
        """
        if not self.fitted:
            raise ValueError("Modelos não foram treinados. Execute fit() primeiro.")
        
        X_clean = X[self.feature_columns].fillna(0)
        X_scaled = self.scalers['main'].transform(X_clean)
        
        predictions = []
        probabilities = []
        
        # Coleta predições de todos os modelos
        for name, model in self.models.items():
            try:
                if name == 'logistic_regression':
                    pred = model.predict(X_scaled)
                    proba = model.predict_proba(X_scaled)
                else:
                    pred = model.predict(X_clean)
                    proba = model.predict_proba(X_clean)
                
                predictions.append(pred)
                probabilities.append(proba)
                
            except Exception as e:
                logger.error(f"Erro na predição com {name}: {e}")
                continue
        
        if not predictions:
            raise ValueError("Nenhum modelo conseguiu fazer predição")
        
        # Média das probabilidades (ensemble)
        avg_probabilities = np.mean(probabilities, axis=0)
        final_predictions = np.argmax(avg_probabilities, axis=1)
        
        # Calcula odds
        odds = 1 / avg_probabilities[0]
        
        # Mapeia resultado
        result_map = {0: 'home_win', 1: 'draw', 2: 'away_win'}
        predicted_result = result_map[final_predictions[0]]
        
        return {
            'model_type': 'ml_ensemble',
            'predicted_result': predicted_result,
            'probabilities': {
                'home_win': avg_probabilities[0][0],
                'draw': avg_probabilities[0][1],
                'away_win': avg_probabilities[0][2]
            },
            'odds': {
                'home': odds[0],
                'draw': odds[1],
                'away': odds[2]
            },
            'confidence': max(avg_probabilities[0]),
            'model_contributions': self._get_model_contributions(probabilities)
        }
    
    def _evaluate_models(self, X_test: pd.DataFrame, X_test_scaled: np.ndarray, y_test: pd.Series):
        """Avalia performance dos modelos"""
        for name, model in self.models.items():
            try:
                if name == 'logistic_regression':
                    y_pred = model.predict(X_test_scaled)
                    y_proba = model.predict_proba(X_test_scaled)
                else:
                    y_pred = model.predict(X_test)
                    y_proba = model.predict_proba(X_test)
                
                accuracy = accuracy_score(y_test, y_pred)
                logloss = log_loss(y_test, y_proba)
                
                logger.info(f"{name}: Accuracy={accuracy:.4f}, LogLoss={logloss:.4f}")
                
            except Exception as e:
                logger.error(f"Erro na avaliação de {name}: {e}")
    
    def _get_model_contributions(self, probabilities: List[np.ndarray]) -> Dict:
        """Calcula contribuição de cada modelo"""
        contributions = {}
        model_names = list(self.models.keys())
        
        for i, (name, prob) in enumerate(zip(model_names, probabilities)):
            if i < len(prob):
                contributions[name] = {
                    'prediction': np.argmax(prob[0]),
                    'confidence': max(prob[0]),
                    'probabilities': prob[0].tolist()
                }
        
        return contributions

class AdvancedLogisticRegression:
    """
    Análise de Regressão Logística Avançada
    Inclui regularização, validação cruzada e análise de significância
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_importance = {}
        self.fitted = False
        
    def fit(self, X: pd.DataFrame, y: pd.Series, feature_columns: List[str]):
        """
        Treina regressão logística com validação cruzada
        """
        logger.info("Treinando regressão logística avançada...")
        
        try:
            X_clean = X[feature_columns].fillna(0)
            
            # Normaliza features
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X_clean)
            
            # Testa diferentes valores de regularização
            C_values = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
            best_score = 0
            best_C = 1.0
            
            for C in C_values:
                model = LogisticRegression(
                    C=C,
                    random_state=42,
                    max_iter=1000,
                    penalty='l2'
                )
                
                # Validação cruzada
                scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
                mean_score = scores.mean()
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_C = C
            
            # Treina modelo final
            self.model = LogisticRegression(
                C=best_C,
                random_state=42,
                max_iter=1000,
                penalty='l2'
            )
            self.model.fit(X_scaled, y)
            
            # Calcula importância das features
            self._calculate_feature_importance(feature_columns)
            
            self.fitted = True
            
            logger.info(f"Regressão logística treinada (C={best_C}, CV Score={best_score:.4f})")
            
        except Exception as e:
            logger.error(f"Erro ao treinar regressão logística: {e}")
    
    def predict(self, X: pd.DataFrame) -> Dict:
        """
        Faz predição usando regressão logística
        """
        if not self.fitted:
            raise ValueError("Modelo não foi treinado. Execute fit() primeiro.")
        
        X_scaled = self.scaler.transform(X)
        
        # Predição
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Calcula odds
        odds = 1 / probabilities
        
        # Mapeia resultado
        result_map = {0: 'home_win', 1: 'draw', 2: 'away_win'}
        predicted_result = result_map[prediction]
        
        return {
            'model_type': 'logistic_regression',
            'predicted_result': predicted_result,
            'probabilities': {
                'home_win': probabilities[0],
                'draw': probabilities[1],
                'away_win': probabilities[2]
            },
            'odds': {
                'home': odds[0],
                'draw': odds[1],
                'away': odds[2]
            },
            'confidence': max(probabilities),
            'feature_importance': self.feature_importance
        }
    
    def _calculate_feature_importance(self, feature_columns: List[str]):
        """Calcula importância das features"""
        if self.model is not None:
            coefficients = np.abs(self.model.coef_[0])
            self.feature_importance = dict(zip(feature_columns, coefficients))

class BayesianNeuralNetwork(nn.Module):
    """
    Rede Neural Bayesiana para modelar incertezas
    Usa aproximações variacionais para inferência bayesiana
    """
    
    def __init__(self, input_size: int, hidden_size: int = 64, output_size: int = 3):
        super(BayesianNeuralNetwork, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Camadas com parâmetros variacionais
        self.fc1_mu = nn.Linear(input_size, hidden_size)
        self.fc1_rho = nn.Linear(input_size, hidden_size)
        
        self.fc2_mu = nn.Linear(hidden_size, hidden_size)
        self.fc2_rho = nn.Linear(hidden_size, hidden_size)
        
        self.fc3_mu = nn.Linear(hidden_size, output_size)
        self.fc3_rho = nn.Linear(hidden_size, output_size)
        
        self.activation = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        # Primeira camada
        mu1 = self.fc1_mu(x)
        rho1 = self.fc1_rho(x)
        sigma1 = torch.log(1 + torch.exp(rho1))
        z1 = mu1 + sigma1 * torch.randn_like(mu1)
        h1 = self.activation(z1)
        h1 = self.dropout(h1)
        
        # Segunda camada
        mu2 = self.fc2_mu(h1)
        rho2 = self.fc2_rho(h1)
        sigma2 = torch.log(1 + torch.exp(rho2))
        z2 = mu2 + sigma2 * torch.randn_like(mu2)
        h2 = self.activation(z2)
        h2 = self.dropout(h2)
        
        # Camada de saída
        mu3 = self.fc3_mu(h2)
        rho3 = self.fc3_rho(h2)
        sigma3 = torch.log(1 + torch.exp(rho3))
        z3 = mu3 + sigma3 * torch.randn_like(mu3)
        
        return z3, (mu1, sigma1, mu2, sigma2, mu3, sigma3)
    
    def kl_divergence(self, mu, sigma):
        """Calcula divergência KL para regularização"""
        kl = 0.5 * torch.sum(mu**2 + sigma**2 - torch.log(sigma**2) - 1)
        return kl

class BayesianNeuralNetworkWrapper:
    """
    Wrapper para Rede Neural Bayesiana
    """
    
    def __init__(self, input_size: int, hidden_size: int = 64):
        self.model = BayesianNeuralNetwork(input_size, hidden_size)
        self.optimizer = None
        self.fitted = False
        self.input_size = input_size
        
    def fit(self, X: pd.DataFrame, y: pd.Series, feature_columns: List[str], epochs: int = 100):
        """
        Treina rede neural bayesiana
        """
        logger.info("Treinando rede neural bayesiana...")
        
        try:
            # Prepara dados
            X_tensor = torch.FloatTensor(X[feature_columns].fillna(0).values)
            y_tensor = torch.LongTensor(y.values)
            
            # Otimizador
            self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            
            # Treinamento
            self.model.train()
            for epoch in range(epochs):
                self.optimizer.zero_grad()
                
                # Forward pass
                output, (mu1, sigma1, mu2, sigma2, mu3, sigma3) = self.model(X_tensor)
                
                # Loss de classificação
                criterion = nn.CrossEntropyLoss()
                classification_loss = criterion(output, y_tensor)
                
                # Loss de regularização (KL divergence)
                kl_loss = (self.model.kl_divergence(mu1, sigma1) + 
                          self.model.kl_divergence(mu2, sigma2) + 
                          self.model.kl_divergence(mu3, sigma3))
                
                # Loss total
                total_loss = classification_loss + 0.01 * kl_loss
                
                # Backward pass
                total_loss.backward()
                self.optimizer.step()
                
                if epoch % 20 == 0:
                    logger.info(f"Epoch {epoch}, Loss: {total_loss.item():.4f}")
            
            self.fitted = True
            logger.info("Rede neural bayesiana treinada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao treinar rede neural bayesiana: {e}")
    
    def predict(self, X: pd.DataFrame, feature_columns: List[str], n_samples: int = 100) -> Dict:
        """
        Faz predição com incerteza usando Monte Carlo
        """
        if not self.fitted:
            raise ValueError("Modelo não foi treinado. Execute fit() primeiro.")
        
        X_tensor = torch.FloatTensor(X[feature_columns].fillna(0).values)
        
        self.model.eval()
        predictions = []
        
        # Monte Carlo sampling para incerteza
        with torch.no_grad():
            for _ in range(n_samples):
                output, _ = self.model(X_tensor)
                probabilities = torch.softmax(output, dim=1)
                predictions.append(probabilities.numpy())
        
        # Média das predições
        avg_predictions = np.mean(predictions, axis=0)
        std_predictions = np.std(predictions, axis=0)
        
        # Predição final
        predicted_class = np.argmax(avg_predictions[0])
        confidence = max(avg_predictions[0])
        uncertainty = np.mean(std_predictions[0])
        
        # Mapeia resultado
        result_map = {0: 'home_win', 1: 'draw', 2: 'away_win'}
        predicted_result = result_map[predicted_class]
        
        return {
            'model_type': 'bayesian_neural_network',
            'predicted_result': predicted_result,
            'probabilities': {
                'home_win': avg_predictions[0][0],
                'draw': avg_predictions[0][1],
                'away_win': avg_predictions[0][2]
            },
            'odds': {
                'home': 1 / avg_predictions[0][0],
                'draw': 1 / avg_predictions[0][1],
                'away': 1 / avg_predictions[0][2]
            },
            'confidence': confidence,
            'uncertainty': uncertainty,
            'uncertainty_breakdown': {
                'home_win': std_predictions[0][0],
                'draw': std_predictions[0][1],
                'away_win': std_predictions[0][2]
            }
        }

class PredictiveModelEnsemble:
    """
    Ensemble de todos os modelos preditivos
    Combina Poisson, ML Ensemble, Logistic Regression e Bayesian Neural Network
    """
    
    def __init__(self):
        self.poisson_model = PoissonModel()
        self.ml_ensemble = MLEnsemble()
        self.logistic_regression = AdvancedLogisticRegression()
        self.bayesian_nn = None
        self.fitted = False
        
    def fit(self, matches_data: pd.DataFrame, X: pd.DataFrame, y: pd.Series, feature_columns: List[str]):
        """
        Treina todos os modelos
        """
        logger.info("Treinando ensemble completo de modelos preditivos...")
        
        try:
            # Treina modelo Poisson
            self.poisson_model.fit(matches_data)
            
            # Treina ML Ensemble
            self.ml_ensemble.fit(X, y, feature_columns)
            
            # Treina Regressão Logística
            self.logistic_regression.fit(X, y, feature_columns)
            
            # Treina Rede Neural Bayesiana (se PyTorch disponível)
            try:
                self.bayesian_nn = BayesianNeuralNetworkWrapper(len(feature_columns))
                self.bayesian_nn.fit(X, y, feature_columns, epochs=50)
            except Exception as e:
                logger.warning(f"Rede Neural Bayesiana não disponível: {e}")
                self.bayesian_nn = None
            
            self.fitted = True
            logger.info("Ensemble completo treinado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao treinar ensemble completo: {e}")
    
    def predict(self, home_team: str, away_team: str, home_team_stats: Dict, 
                away_team_stats: Dict, X: pd.DataFrame, feature_columns: List[str]) -> Dict:
        """
        Faz predição usando todos os modelos
        """
        if not self.fitted:
            raise ValueError("Modelos não foram treinados. Execute fit() primeiro.")
        
        predictions = {}
        
        # Predição Poisson
        try:
            poisson_pred = self.poisson_model.predict(home_team, away_team, home_team_stats, away_team_stats)
            predictions['poisson'] = poisson_pred
        except Exception as e:
            logger.error(f"Erro na predição Poisson: {e}")
        
        # Predição ML Ensemble
        try:
            ml_pred = self.ml_ensemble.predict(X)
            predictions['ml_ensemble'] = ml_pred
        except Exception as e:
            logger.error(f"Erro na predição ML Ensemble: {e}")
        
        # Predição Regressão Logística
        try:
            lr_pred = self.logistic_regression.predict(X)
            predictions['logistic_regression'] = lr_pred
        except Exception as e:
            logger.error(f"Erro na predição Regressão Logística: {e}")
        
        # Predição Rede Neural Bayesiana
        if self.bayesian_nn:
            try:
                bnn_pred = self.bayesian_nn.predict(X, feature_columns)
                predictions['bayesian_nn'] = bnn_pred
            except Exception as e:
                logger.error(f"Erro na predição Rede Neural Bayesiana: {e}")
        
        # Combina predições
        combined_prediction = self._combine_predictions(predictions)
        
        return combined_prediction
    
    def _combine_predictions(self, predictions: Dict) -> Dict:
        """
        Combina predições de todos os modelos
        """
        if not predictions:
            raise ValueError("Nenhuma predição disponível")
        
        # Peso dos modelos (pode ser ajustado baseado na performance)
        model_weights = {
            'poisson': 0.25,
            'ml_ensemble': 0.35,
            'logistic_regression': 0.25,
            'bayesian_nn': 0.15
        }
        
        # Calcula probabilidades médias ponderadas
        total_weight = 0
        weighted_probs = {'home_win': 0, 'draw': 0, 'away_win': 0}
        weighted_odds = {'home': 0, 'draw': 0, 'away': 0}
        confidences = []
        uncertainties = []
        
        for model_name, pred in predictions.items():
            weight = model_weights.get(model_name, 0.1)
            total_weight += weight
            
            # Probabilidades
            for outcome in ['home_win', 'draw', 'away_win']:
                weighted_probs[outcome] += pred['probabilities'][outcome] * weight
            
            # Odds
            for outcome in ['home', 'draw', 'away']:
                weighted_odds[outcome] += pred['odds'][outcome] * weight
            
            # Confiança
            confidences.append(pred['confidence'])
            
            # Incerteza (se disponível)
            if 'uncertainty' in pred:
                uncertainties.append(pred['uncertainty'])
        
        # Normaliza probabilidades
        for outcome in weighted_probs:
            weighted_probs[outcome] /= total_weight
        
        # Normaliza odds
        for outcome in weighted_odds:
            weighted_odds[outcome] /= total_weight
        
        # Predição final
        predicted_result = max(weighted_probs, key=weighted_probs.get)
        confidence = np.mean(confidences)
        uncertainty = np.mean(uncertainties) if uncertainties else 0
        
        return {
            'model_type': 'ensemble_all',
            'predicted_result': predicted_result,
            'probabilities': weighted_probs,
            'odds': weighted_odds,
            'confidence': confidence,
            'uncertainty': uncertainty,
            'individual_predictions': predictions,
            'model_weights': model_weights
        }

if __name__ == "__main__":
    # Teste dos modelos preditivos
    print("=== TESTE DOS MODELOS PREDITIVOS ===")
    
    # Dados simulados para teste
    import pandas as pd
    import numpy as np
    
    # Cria dados de teste
    np.random.seed(42)
    n_matches = 100
    
    matches_data = pd.DataFrame({
        'home_team': [f'Team_{i%10}' for i in range(n_matches)],
        'away_team': [f'Team_{(i+5)%10}' for i in range(n_matches)],
        'home_goals': np.random.poisson(1.5, n_matches),
        'away_goals': np.random.poisson(1.2, n_matches)
    })
    
    # Cria features
    X = pd.DataFrame(np.random.randn(n_matches, 20))
    feature_columns = [f'feature_{i}' for i in range(20)]
    X.columns = feature_columns
    
    # Cria target
    y = np.random.choice([0, 1, 2], n_matches)
    
    # Testa ensemble completo
    ensemble = PredictiveModelEnsemble()
    ensemble.fit(matches_data, X, y, feature_columns)
    
    # Testa predição
    test_X = X.iloc[:1]
    prediction = ensemble.predict('Team_A', 'Team_B', {}, {}, test_X, feature_columns)
    
    print(f"Predição: {prediction['predicted_result']}")
    print(f"Confiança: {prediction['confidence']:.3f}")
    print(f"Probabilidades: {prediction['probabilities']}")
    print(f"Odds: {prediction['odds']}")
