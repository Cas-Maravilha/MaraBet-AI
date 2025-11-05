#!/usr/bin/env python3
"""
Testes de integração para pipeline completo
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from coletores.data_collector import DataCollector
from feature_engineering import FeatureEngineer
from ml.ml_models import MLModelManager
from notifications.notification_manager import NotificationManager

class TestDataCollectionPipeline:
    """Testes de integração para pipeline de coleta de dados"""
    
    @patch('coletores.football_collector.FootballCollector.get_live_matches')
    @patch('coletores.odds_collector.OddsCollector.get_odds')
    def test_live_data_pipeline(self, mock_odds, mock_matches, mock_api_response, mock_odds_response):
        """Testa pipeline completo de coleta de dados ao vivo"""
        collector = DataCollector()
        
        # Mock das respostas
        mock_matches.return_value = mock_api_response['response']
        mock_odds.return_value = mock_odds_response['data']
        
        # Executar pipeline
        data = collector.collect_live_data()
        
        # Verificações
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verificar estrutura dos dados
        for match in data:
            assert 'fixture_id' in match
            assert 'home_team' in match
            assert 'away_team' in match
            assert 'date' in match
            assert 'odds' in match
            assert 'home_odds' in match['odds']
            assert 'draw_odds' in match['odds']
            assert 'away_odds' in match['odds']
    
    @patch('coletores.football_collector.FootballCollector.get_fixtures_by_date')
    def test_historical_data_pipeline(self, mock_fixtures, mock_api_response):
        """Testa pipeline de coleta de dados históricos"""
        collector = DataCollector()
        
        # Mock da resposta
        mock_fixtures.return_value = mock_api_response['response']
        
        # Executar pipeline
        date = datetime.now().strftime('%Y-%m-%d')
        data = collector.collect_historical_data(date)
        
        # Verificações
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verificar estrutura dos dados
        for match in data:
            assert 'fixture_id' in match
            assert 'home_team' in match
            assert 'away_team' in match
            assert 'date' in match
    
    def test_data_validation_pipeline(self, sample_match_data):
        """Testa pipeline de validação de dados"""
        collector = DataCollector()
        
        # Dados válidos
        valid_data = [sample_match_data]
        assert collector.validate_data(valid_data) == True
        
        # Dados inválidos
        invalid_data = [
            {**sample_match_data, 'fixture_id': None},
            {**sample_match_data, 'home_team': ''},
            {**sample_match_data, 'away_team': None}
        ]
        assert collector.validate_data(invalid_data) == False
    
    def test_data_cleaning_pipeline(self, sample_match_data):
        """Testa pipeline de limpeza de dados"""
        collector = DataCollector()
        
        # Dados com problemas
        dirty_data = [
            {**sample_match_data, 'home_score': None},
            {**sample_match_data, 'away_score': -1},
            {**sample_match_data, 'home_odds': 0},
            {**sample_match_data, 'draw_odds': None}
        ]
        
        clean_data = collector.clean_data(dirty_data)
        
        # Verificações
        assert isinstance(clean_data, list)
        assert len(clean_data) > 0
        
        for match in clean_data:
            assert match['home_score'] is not None
            assert match['away_score'] >= 0
            assert match['home_odds'] > 0
            assert match['draw_odds'] is not None

class TestMLPipeline:
    """Testes de integração para pipeline de ML"""
    
    def test_feature_extraction_pipeline(self, sample_match_data):
        """Testa pipeline de extração de features"""
        engineer = FeatureEngineer()
        
        # Mock de dados históricos
        historical_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 20,
            'away_team': ['Manchester United'] * 20,
            'home_score': np.random.randint(0, 5, 20),
            'away_score': np.random.randint(0, 5, 20),
            'result': np.random.randint(0, 3, 20),
            'date': pd.date_range('2024-01-01', periods=20, freq='D')
        })
        
        # Extrair features
        feature_matrix = engineer.create_feature_matrix(sample_match_data, historical_data)
        
        # Verificações
        assert isinstance(feature_matrix, np.ndarray)
        assert len(feature_matrix) > 0
        assert not np.any(np.isnan(feature_matrix))
        assert not np.any(np.isinf(feature_matrix))
    
    def test_model_training_pipeline(self, mock_ml_model):
        """Testa pipeline de treinamento de modelo"""
        manager = MLModelManager()
        
        # Dados de treino
        X_train = np.array([[0.8, 0.6, 0.7, 0.1], [0.7, 0.5, 0.6, 0.2], [0.9, 0.8, 0.8, 0.1]])
        y_train = np.array([1, 0, 1])
        
        # Treinar modelo
        score = manager.train_model('test_model', mock_ml_model, X_train, y_train)
        
        # Verificações
        assert score == 0.85
        mock_ml_model.fit.assert_called_once_with(X_train, y_train)
    
    def test_prediction_pipeline(self, mock_ml_model, sample_match_data):
        """Testa pipeline de predição"""
        manager = MLModelManager()
        engineer = FeatureEngineer()
        
        # Configurar modelo
        manager.load_model('test_model', mock_ml_model)
        manager.feature_extractor = engineer
        
        # Mock do feature extractor
        manager.feature_extractor.extract_features = Mock(return_value=np.array([[0.8, 0.6, 0.7, 0.1]]))
        
        # Fazer predição
        prediction = manager.predict('test_model', sample_match_data)
        
        # Verificações
        assert prediction is not None
        mock_ml_model.predict.assert_called_once()
    
    def test_model_evaluation_pipeline(self, mock_ml_model):
        """Testa pipeline de avaliação de modelo"""
        manager = MLModelManager()
        
        # Dados de teste
        X_test = np.array([[0.8, 0.6, 0.7, 0.1], [0.7, 0.5, 0.6, 0.2]])
        y_test = np.array([1, 0])
        
        # Mock das predições
        mock_ml_model.predict.return_value = np.array([1, 0])
        mock_ml_model.predict_proba.return_value = np.array([[0.2, 0.8], [0.7, 0.3]])
        
        # Avaliar modelo
        metrics = manager.evaluate_model('test_model', X_test, y_test)
        
        # Verificações
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 'auc' in metrics
        
        # Verificar valores das métricas
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1_score'] <= 1
        assert 0 <= metrics['auc'] <= 1

class TestNotificationPipeline:
    """Testes de integração para pipeline de notificações"""
    
    def test_notification_creation_pipeline(self, sample_prediction_data):
        """Testa pipeline de criação de notificações"""
        manager = NotificationManager()
        
        # Criar notificação
        notification = manager.create_prediction_notification(sample_prediction_data)
        
        # Verificações
        assert isinstance(notification, dict)
        assert 'type' in notification
        assert 'message' in notification
        assert 'data' in notification
        assert notification['type'] == 'prediction'
    
    @patch('requests.post')
    def test_telegram_notification_pipeline(self, mock_post, mock_telegram_response, sample_prediction_data):
        """Testa pipeline de notificação via Telegram"""
        manager = NotificationManager()
        
        # Mock da resposta do Telegram
        mock_response = Mock()
        mock_response.json.return_value = mock_telegram_response
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Enviar notificação
        result = manager.send_telegram_notification(sample_prediction_data)
        
        # Verificações
        assert result is True
        mock_post.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_email_notification_pipeline(self, mock_smtp, sample_prediction_data):
        """Testa pipeline de notificação via email"""
        manager = NotificationManager()
        
        # Mock do SMTP
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Enviar notificação
        result = manager.send_email_notification(sample_prediction_data)
        
        # Verificações
        assert result is True
        mock_smtp.assert_called_once()
    
    def test_notification_filtering_pipeline(self, sample_prediction_data):
        """Testa pipeline de filtragem de notificações"""
        manager = NotificationManager()
        
        # Predição com EV baixo (não deve ser notificada)
        low_ev_data = {**sample_prediction_data, 'expected_value': 0.02}
        should_notify = manager.should_notify(low_ev_data)
        assert should_notify is False
        
        # Predição com EV alto (deve ser notificada)
        high_ev_data = {**sample_prediction_data, 'expected_value': 0.15}
        should_notify = manager.should_notify(high_ev_data)
        assert should_notify is True
        
        # Predição com confiança baixa (não deve ser notificada)
        low_conf_data = {**sample_prediction_data, 'confidence': 0.5}
        should_notify = manager.should_notify(low_conf_data)
        assert should_notify is False

class TestEndToEndPipeline:
    """Testes de integração end-to-end"""
    
    @patch('coletores.football_collector.FootballCollector.get_live_matches')
    @patch('coletores.odds_collector.OddsCollector.get_odds')
    @patch('ml.ml_models.MLModelManager.predict')
    @patch('notifications.notification_manager.NotificationManager.send_notification')
    def test_complete_prediction_pipeline(self, mock_notification, mock_predict, mock_odds, mock_matches, 
                                        mock_api_response, mock_odds_response, sample_prediction_data):
        """Testa pipeline completo de predição"""
        from main import PredictionPipeline
        
        # Mock das respostas
        mock_matches.return_value = mock_api_response['response']
        mock_odds.return_value = mock_odds_response['data']
        mock_predict.return_value = sample_prediction_data
        mock_notification.return_value = True
        
        # Executar pipeline
        pipeline = PredictionPipeline()
        result = pipeline.run_prediction_cycle()
        
        # Verificações
        assert result is True
        mock_matches.assert_called_once()
        mock_odds.assert_called_once()
        mock_predict.assert_called_once()
        mock_notification.assert_called_once()
    
    def test_error_handling_pipeline(self):
        """Testa tratamento de erros no pipeline"""
        from main import PredictionPipeline
        
        # Mock de erro na coleta de dados
        with patch('coletores.data_collector.DataCollector.collect_live_data', side_effect=Exception("API Error")):
            pipeline = PredictionPipeline()
            result = pipeline.run_prediction_cycle()
            
            # Deve lidar com erro graciosamente
            assert result is False
    
    def test_data_flow_pipeline(self, sample_match_data, sample_prediction_data):
        """Testa fluxo de dados através do pipeline"""
        from main import PredictionPipeline
        
        # Mock dos componentes
        with patch('coletores.data_collector.DataCollector.collect_live_data', return_value=[sample_match_data]):
            with patch('ml.ml_models.MLModelManager.predict', return_value=sample_prediction_data):
                with patch('notifications.notification_manager.NotificationManager.send_notification', return_value=True):
                    pipeline = PredictionPipeline()
                    result = pipeline.run_prediction_cycle()
                    
                    # Verificar fluxo de dados
                    assert result is True
    
    def test_performance_pipeline(self):
        """Testa performance do pipeline"""
        import time
        from main import PredictionPipeline
        
        # Medir tempo de execução
        start_time = time.time()
        
        with patch('coletores.data_collector.DataCollector.collect_live_data', return_value=[]):
            pipeline = PredictionPipeline()
            result = pipeline.run_prediction_cycle()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verificar que o pipeline executa em tempo razoável
        assert execution_time < 5.0  # Menos de 5 segundos
        assert result is True

class TestPipelineIntegration:
    """Testes de integração entre componentes"""
    
    def test_data_collector_to_feature_engineer(self, sample_match_data):
        """Testa integração entre DataCollector e FeatureEngineer"""
        collector = DataCollector()
        engineer = FeatureEngineer()
        
        # Dados coletados
        collected_data = [sample_match_data]
        
        # Extrair features
        feature_matrix = engineer.create_feature_matrix(sample_match_data, pd.DataFrame())
        
        # Verificações
        assert isinstance(feature_matrix, np.ndarray)
        assert len(feature_matrix) > 0
    
    def test_feature_engineer_to_ml_models(self, sample_match_data, mock_ml_model):
        """Testa integração entre FeatureEngineer e MLModels"""
        engineer = FeatureEngineer()
        manager = MLModelManager()
        
        # Extrair features
        feature_matrix = engineer.create_feature_matrix(sample_match_data, pd.DataFrame())
        
        # Configurar modelo
        manager.load_model('test_model', mock_ml_model)
        
        # Fazer predição
        prediction = manager.predict('test_model', sample_match_data)
        
        # Verificações
        assert prediction is not None
    
    def test_ml_models_to_notifications(self, sample_prediction_data):
        """Testa integração entre MLModels e Notifications"""
        manager = NotificationManager()
        
        # Criar notificação baseada na predição
        notification = manager.create_prediction_notification(sample_prediction_data)
        
        # Verificações
        assert isinstance(notification, dict)
        assert 'type' in notification
        assert 'message' in notification

if __name__ == "__main__":
    pytest.main([__file__])
