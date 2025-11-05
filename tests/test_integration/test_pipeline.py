"""
Testes de integração para Pipeline de Coleta-Processamento-Predição
Testa o fluxo completo do sistema MaraBet AI
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json
import os

from colecionadores.api_football_collector import APIFootballCollector
from colecionadores.odds_collector import OddsCollector
from processadores.data_processor import DataProcessor
from ml.ml_models import MLModelManager
from probability_calculator import ProbabilityCalculator
from value_identification import ValueIdentifier
from notifications.telegram_notifications import TelegramNotifier
from cache.redis_cache import RedisCache

class TestDataCollectionPipeline:
    """Testes de integração para pipeline de coleta de dados"""
    
    def test_api_football_collection_integration(self, mock_api_football, test_db):
        """Testa integração completa da coleta da API-Football"""
        collector = APIFootballCollector()
        
        # Mock da API
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": 2,
                "response": [
                    {
                        "fixture": {
                            "id": 12345,
                            "date": "2024-01-15T15:00:00Z",
                            "status": {"short": "NS"}
                        },
                        "teams": {
                            "home": {"name": "Manchester United", "id": 33},
                            "away": {"name": "Liverpool", "id": 40}
                        },
                        "league": {"name": "Premier League", "id": 39}
                    },
                    {
                        "fixture": {
                            "id": 12346,
                            "date": "2024-01-15T17:30:00Z",
                            "status": {"short": "NS"}
                        },
                        "teams": {
                            "home": {"name": "Arsenal", "id": 42},
                            "away": {"name": "Tottenham", "id": 47}
                        },
                        "league": {"name": "Premier League", "id": 39}
                    }
                ]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Executar coleta
            result = collector.collect_fixtures(league_id=39, season=2024)
            
            # Verificações
            assert result['success'] == True
            assert result['fixtures_collected'] == 2
            assert len(result['fixtures']) == 2
            
            # Verificar se dados foram salvos no banco
            from armazenamento.banco_de_dados import Match
            matches = test_db.query(Match).all()
            assert len(matches) == 2
            
            # Verificar dados da primeira partida
            match1 = matches[0]
            assert match1.fixture_id == 12345
            assert match1.home_team_name == "Manchester United"
            assert match1.away_team_name == "Liverpool"
            assert match1.league_name == "Premier League"
    
    def test_odds_collection_integration(self, mock_odds_api, test_db):
        """Testa integração completa da coleta de odds"""
        collector = OddsCollector()
        
        # Mock da API
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "12345",
                        "sport_key": "soccer_epl",
                        "home_team": "Manchester United",
                        "away_team": "Liverpool",
                        "commence_time": "2024-01-15T15:00:00Z",
                        "bookmakers": [
                            {
                                "key": "bet365",
                                "title": "Bet365",
                                "markets": [
                                    {
                                        "key": "h2h",
                                        "outcomes": [
                                            {"name": "Manchester United", "price": 2.10},
                                            {"name": "Liverpool", "price": 3.20},
                                            {"name": "Draw", "price": 3.40}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Executar coleta
            result = collector.collect_odds(sport="soccer_epl", regions=["uk"])
            
            # Verificações
            assert result['success'] == True
            assert result['odds_collected'] > 0
            
            # Verificar se dados foram salvos no banco
            from armazenamento.banco_de_dados import Odds
            odds = test_db.query(Odds).all()
            assert len(odds) > 0
            
            # Verificar dados da primeira odd
            odd1 = odds[0]
            assert odd1.fixture_id == 12345
            assert odd1.bookmaker == "bet365"
            assert odd1.market == "h2h"
            assert odd1.selection in ["Manchester United", "Liverpool", "Draw"]
    
    def test_data_processing_integration(self, test_db, sample_match_data, sample_odds_data):
        """Testa integração completa do processamento de dados"""
        processor = DataProcessor()
        
        # Criar dados de teste no banco
        from armazenamento.banco_de_dados import Match, Odds
        
        # Adicionar partida
        match = Match(**sample_match_data)
        test_db.add(match)
        test_db.commit()
        
        # Adicionar odds
        odds = Odds(**sample_odds_data)
        test_db.add(odds)
        test_db.commit()
        
        # Processar dados
        result = processor.process_matches()
        
        # Verificações
        assert result['success'] == True
        assert result['matches_processed'] > 0
        
        # Verificar se features foram criadas
        assert 'features_created' in result
        assert result['features_created'] > 0

class TestMLPipeline:
    """Testes de integração para pipeline de ML"""
    
    def test_ml_training_pipeline(self, test_db, sample_ml_data):
        """Testa pipeline completo de treinamento de ML"""
        manager = MLModelManager()
        
        # Criar e treinar modelo
        model = manager.create_model('random_forest')
        training_result = manager.train_model(
            model, 
            sample_ml_data['X_train'], 
            sample_ml_data['y_train']
        )
        
        # Verificações
        assert training_result is not None
        assert model.is_trained == True
        
        # Fazer predições
        predictions = manager.predict(model, sample_ml_data['X_test'])
        probabilities = model.predict_proba(sample_ml_data['X_test'])
        
        # Verificações
        assert len(predictions) == len(sample_ml_data['X_test'])
        assert probabilities.shape[0] == len(sample_ml_data['X_test'])
        assert probabilities.shape[1] == 3  # 3 classes
        
        # Avaliar modelo
        metrics = manager.evaluate_model(
            model, 
            sample_ml_data['X_test'], 
            sample_ml_data['y_test']
        )
        
        # Verificações
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert metrics['accuracy'] > 0
    
    def test_ensemble_prediction_pipeline(self, sample_ml_data):
        """Testa pipeline de predição com ensemble"""
        manager = MLModelManager()
        calculator = ProbabilityCalculator()
        
        # Criar múltiplos modelos
        models = []
        for model_type in ['random_forest', 'xgboost', 'lightgbm']:
            model = manager.create_model(model_type)
            manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
            models.append(model)
        
        # Fazer predição com ensemble
        probability = calculator.calculate_probability(models, sample_ml_data['X_test'][:1])
        
        # Verificações
        assert probability is not None
        assert 0 <= probability <= 1
        
        # Verificar se todos os modelos foram usados
        for model in models:
            assert model.is_trained == True
    
    def test_value_bet_identification_pipeline(self, sample_ml_data):
        """Testa pipeline completo de identificação de value bets"""
        manager = MLModelManager()
        calculator = ProbabilityCalculator()
        identifier = ValueIdentifier()
        
        # Treinar modelo
        model = manager.create_model('random_forest')
        manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        # Calcular probabilidade
        probability = calculator.calculate_probability(model, sample_ml_data['X_test'][:1])
        
        # Identificar value bet
        prediction_data = {
            'predicted_probability': probability,
            'current_odd': 2.0,
            'confidence': 0.8,
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        expected_value = calculator.calculate_expected_value(probability, 2.0)
        kelly_percentage = identifier.calculate_kelly_criterion(probability, 2.0)
        
        # Verificações
        assert isinstance(is_value_bet, bool)
        assert isinstance(expected_value, float)
        assert isinstance(kelly_percentage, float)
        assert kelly_percentage >= 0

class TestNotificationPipeline:
    """Testes de integração para pipeline de notificações"""
    
    def test_telegram_notification_pipeline(self, mock_telegram):
        """Testa pipeline completo de notificação via Telegram"""
        notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
        
        # Dados de value bet
        value_bet_data = {
            'match': 'Manchester United vs Liverpool',
            'market': '1x2',
            'selection': 'home_win',
            'odd': 2.10,
            'value': 0.15,
            'confidence': 0.8,
            'stake_percentage': 0.02
        }
        
        # Enviar notificação
        result = notifier.send_value_bet_alert(value_bet_data)
        
        # Verificações
        assert result == True
        mock_telegram.assert_called_once()
        
        # Verificar conteúdo da mensagem
        call_args = mock_telegram.call_args
        assert 'data' in call_args.kwargs
        data = call_args.kwargs['data']
        assert 'text' in data
        assert 'Manchester United vs Liverpool' in data['text']
        assert '2.10' in data['text']
    
    def test_email_notification_pipeline(self, mock_email):
        """Testa pipeline completo de notificação via email"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="test_password"
        )
        
        # Dados de value bet
        value_bet_data = {
            'match': 'Manchester United vs Liverpool',
            'market': '1x2',
            'selection': 'home_win',
            'odd': 2.10,
            'value': 0.15,
            'confidence': 0.8,
            'stake_percentage': 0.02
        }
        
        # Enviar notificação
        result = notifier.send_value_bet_alert(value_bet_data, "recipient@example.com")
        
        # Verificações
        assert result == True
        mock_email.sendmail.assert_called_once()
        
        # Verificar conteúdo do email
        call_args = mock_email.sendmail.call_args
        assert 'recipient@example.com' in call_args[0]
        assert 'Value Bet Alert' in call_args[1]['Subject']

class TestCachePipeline:
    """Testes de integração para pipeline de cache"""
    
    def test_redis_cache_pipeline(self, test_redis):
        """Testa pipeline completo de cache Redis"""
        cache = test_redis
        
        # Dados de teste
        test_data = {
            'fixture_id': 12345,
            'home_team': 'Manchester United',
            'away_team': 'Liverpool',
            'odds': {
                'home_win': 2.10,
                'draw': 3.40,
                'away_win': 3.20
            }
        }
        
        # Salvar no cache
        result = cache.set('odds', '12345', test_data, ttl=300)
        assert result == True
        
        # Recuperar do cache
        cached_data = cache.get('odds', '12345')
        assert cached_data == test_data
        
        # Verificar TTL
        ttl = cache.ttl('odds', '12345')
        assert ttl > 0
        assert ttl <= 300
        
        # Verificar existência
        exists = cache.exists('odds', '12345')
        assert exists == True
        
        # Deletar do cache
        delete_result = cache.delete('odds', '12345')
        assert delete_result == True
        
        # Verificar se foi deletado
        exists = cache.exists('odds', '12345')
        assert exists == False
    
    def test_cache_invalidation_pipeline(self, test_redis):
        """Testa pipeline de invalidação de cache"""
        cache = test_redis
        
        # Adicionar múltiplos itens
        for i in range(5):
            cache.set('odds', f'fixture_{i}', {'odd': 2.0 + i}, ttl=300)
        
        # Verificar que todos existem
        for i in range(5):
            assert cache.exists('odds', f'fixture_{i}') == True
        
        # Limpar por tipo
        cleared = cache.clear_type('odds')
        assert cleared == 5
        
        # Verificar que todos foram removidos
        for i in range(5):
            assert cache.exists('odds', f'fixture_{i}') == False

class TestFullSystemPipeline:
    """Testes de integração para pipeline completo do sistema"""
    
    def test_complete_value_bet_pipeline(self, test_db, mock_api_football, mock_odds_api, mock_telegram, test_redis):
        """Testa pipeline completo de identificação de value bets"""
        # 1. Coletar dados de partidas
        api_collector = APIFootballCollector()
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": 1,
                "response": [{
                    "fixture": {"id": 12345, "date": "2024-01-15T15:00:00Z", "status": {"short": "NS"}},
                    "teams": {"home": {"name": "Manchester United", "id": 33}, "away": {"name": "Liverpool", "id": 40}},
                    "league": {"name": "Premier League", "id": 39}
                }]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            fixtures_result = api_collector.collect_fixtures(league_id=39, season=2024)
            assert fixtures_result['success'] == True
        
        # 2. Coletar odds
        odds_collector = OddsCollector()
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": [{
                    "id": "12345",
                    "sport_key": "soccer_epl",
                    "home_team": "Manchester United",
                    "away_team": "Liverpool",
                    "commence_time": "2024-01-15T15:00:00Z",
                    "bookmakers": [{
                        "key": "bet365",
                        "title": "Bet365",
                        "markets": [{
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Manchester United", "price": 2.10},
                                {"name": "Liverpool", "price": 3.20},
                                {"name": "Draw", "price": 3.40}
                            ]
                        }]
                    }]
                }]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            odds_result = odds_collector.collect_odds(sport="soccer_epl", regions=["uk"])
            assert odds_result['success'] == True
        
        # 3. Processar dados
        processor = DataProcessor()
        processing_result = processor.process_matches()
        assert processing_result['success'] == True
        
        # 4. Treinar modelo ML
        manager = MLModelManager()
        model = manager.create_model('random_forest')
        
        # Dados de treinamento simulados
        X_train = np.random.rand(100, 10)
        y_train = np.random.randint(0, 3, 100)
        X_test = np.random.rand(1, 10)
        
        training_result = manager.train_model(model, X_train, y_train)
        assert training_result is not None
        
        # 5. Fazer predição
        calculator = ProbabilityCalculator()
        probability = calculator.calculate_probability(model, X_test)
        assert 0 <= probability <= 1
        
        # 6. Identificar value bet
        identifier = ValueIdentifier()
        prediction_data = {
            'predicted_probability': probability,
            'current_odd': 2.10,
            'confidence': 0.8,
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        expected_value = calculator.calculate_expected_value(probability, 2.10)
        kelly_percentage = identifier.calculate_kelly_criterion(probability, 2.10)
        
        # 7. Salvar no cache
        value_bet_data = {
            'fixture_id': 12345,
            'match': 'Manchester United vs Liverpool',
            'market': '1x2',
            'selection': 'home_win',
            'odd': 2.10,
            'predicted_probability': probability,
            'expected_value': expected_value,
            'confidence': 0.8,
            'stake_percentage': kelly_percentage,
            'is_value_bet': is_value_bet,
            'timestamp': datetime.now().isoformat()
        }
        
        cache_result = test_redis.set('value_bets', '12345_home_win', value_bet_data, ttl=3600)
        assert cache_result == True
        
        # 8. Enviar notificação se for value bet
        if is_value_bet:
            notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
            notification_result = notifier.send_value_bet_alert(value_bet_data)
            assert notification_result == True
        
        # 9. Verificar dados no banco
        from armazenamento.banco_de_dados import Match, Odds, Prediction
        
        matches = test_db.query(Match).all()
        assert len(matches) > 0
        
        odds = test_db.query(Odds).all()
        assert len(odds) > 0
        
        # Verificar se predição foi salva
        predictions = test_db.query(Prediction).all()
        assert len(predictions) > 0
        
        # Verificar dados da predição
        prediction = predictions[0]
        assert prediction.fixture_id == 12345
        assert prediction.market == '1x2'
        assert prediction.predicted_probability == probability
        assert prediction.expected_value == expected_value
        assert prediction.recommended == is_value_bet

class TestErrorHandlingPipeline:
    """Testes de integração para tratamento de erros"""
    
    def test_api_error_handling(self):
        """Testa tratamento de erros de API"""
        collector = APIFootballCollector()
        
        # Mock de erro de API
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal Server Error"}
            mock_get.return_value = mock_response
            
            result = collector.collect_fixtures(league_id=39, season=2024)
            
            # Verificações
            assert result['success'] == False
            assert 'error' in result
            assert 'Internal Server Error' in result['error']
    
    def test_database_error_handling(self, test_db):
        """Testa tratamento de erros de banco de dados"""
        from armazenamento.banco_de_dados import Match
        
        # Tentar inserir dados inválidos
        invalid_match = Match(
            fixture_id=None,  # ID inválido
            home_team_name="",  # Nome vazio
            away_team_name="",  # Nome vazio
            league_name="",  # Liga vazia
            date=None  # Data inválida
        )
        
        test_db.add(invalid_match)
        
        with pytest.raises(Exception):  # Deve gerar exceção
            test_db.commit()
    
    def test_ml_error_handling(self, sample_ml_data):
        """Testa tratamento de erros de ML"""
        manager = MLModelManager()
        
        # Tentar treinar com dados inválidos
        X_invalid = np.array([])  # Array vazio
        y_invalid = np.array([])  # Array vazio
        
        model = manager.create_model('random_forest')
        
        with pytest.raises(ValueError):  # Deve gerar exceção
            manager.train_model(model, X_invalid, y_invalid)
    
    def test_cache_error_handling(self, mock_redis):
        """Testa tratamento de erros de cache"""
        cache = RedisCache()
        cache.redis_client = mock_redis
        
        # Mock de erro de conexão
        mock_redis.set.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            cache.set('test', 'key', {'data': 'value'})

class TestPerformancePipeline:
    """Testes de integração para performance"""
    
    def test_large_dataset_processing(self, temp_directory):
        """Testa processamento de dataset grande"""
        # Criar dataset grande
        large_data = pd.DataFrame({
            'fixture_id': range(10000),
            'home_team': ['Team A'] * 10000,
            'away_team': ['Team B'] * 10000,
            'home_goals': np.random.randint(0, 5, 10000),
            'away_goals': np.random.randint(0, 5, 10000),
            'home_odds': np.random.uniform(1.1, 10.0, 10000),
            'away_odds': np.random.uniform(1.1, 10.0, 10000),
            'draw_odds': np.random.uniform(1.1, 10.0, 10000)
        })
        
        # Salvar dataset
        csv_path = os.path.join(temp_directory, "large_dataset.csv")
        large_data.to_csv(csv_path, index=False)
        
        # Processar dataset
        processor = DataProcessor()
        start_time = datetime.now()
        
        result = processor.process_csv(csv_path)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Verificações
        assert result['success'] == True
        assert processing_time < 60  # Deve processar em menos de 1 minuto
        assert result['records_processed'] == 10000
    
    def test_concurrent_requests(self, test_client, auth_headers):
        """Testa requisições concorrentes"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_client.get("/api/stats", headers=auth_headers)
            results.append(response.status_code)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Executar threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificações
        assert len(results) == 10
        assert all(status == 200 for status in results)
        assert total_time < 5  # Deve responder em menos de 5 segundos
    
    def test_memory_usage(self, sample_ml_data):
        """Testa uso de memória durante processamento"""
        import psutil
        import os
        
        # Obter uso de memória inicial
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Executar processamento intensivo
        manager = MLModelManager()
        models = []
        
        for model_type in ['random_forest', 'xgboost', 'lightgbm', 'catboost']:
            model = manager.create_model(model_type)
            manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
            models.append(model)
        
        # Obter uso de memória final
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verificações
        assert memory_increase < 500  # Aumento de memória deve ser menor que 500MB
        assert len(models) == 4
        assert all(model.is_trained for model in models)
