"""
Testes unitários para funções de utilidade
Testa funções auxiliares, validações e helpers
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json
import os

from probability_calculator import ProbabilityCalculator
from value_identification import ValueIdentifier
from feature_engineering import FeatureEngineer
from statistical_analysis import StatisticalAnalyzer
from bankroll_management import BankrollManager
from notifications.telegram_notifications import TelegramNotifier
from notifications.email_notifications import EmailNotifier
from cache.redis_cache import RedisCache

class TestProbabilityCalculator:
    """Testes para ProbabilityCalculator"""
    
    def test_init(self):
        """Testa inicialização do ProbabilityCalculator"""
        calculator = ProbabilityCalculator()
        assert calculator is not None
    
    def test_calculate_implied_probability(self):
        """Testa cálculo de probabilidade implícita"""
        calculator = ProbabilityCalculator()
        
        # Teste com odds de 2.0
        prob = calculator.calculate_implied_probability(2.0)
        assert abs(prob - 0.5) < 1e-10
        
        # Teste com odds de 3.0
        prob = calculator.calculate_implied_probability(3.0)
        assert abs(prob - 1/3) < 1e-10
        
        # Teste com odds de 1.5
        prob = calculator.calculate_implied_probability(1.5)
        assert abs(prob - 2/3) < 1e-10
    
    def test_calculate_expected_value(self):
        """Testa cálculo de expected value"""
        calculator = ProbabilityCalculator()
        
        # Teste com EV positivo
        ev = calculator.calculate_expected_value(0.6, 2.0)
        expected = 0.6 * 2.0 - 1  # 0.2
        assert abs(ev - expected) < 1e-10
        
        # Teste com EV negativo
        ev = calculator.calculate_expected_value(0.4, 2.0)
        expected = 0.4 * 2.0 - 1  # -0.2
        assert abs(ev - expected) < 1e-10
        
        # Teste com EV zero
        ev = calculator.calculate_expected_value(0.5, 2.0)
        expected = 0.5 * 2.0 - 1  # 0.0
        assert abs(ev - expected) < 1e-10
    
    def test_calculate_probability_from_odds(self):
        """Testa cálculo de probabilidade a partir de odds"""
        calculator = ProbabilityCalculator()
        
        # Teste com odds válidas
        prob = calculator.calculate_probability_from_odds(2.0)
        assert abs(prob - 0.5) < 1e-10
        
        # Teste com odds inválidas
        with pytest.raises(ValueError):
            calculator.calculate_probability_from_odds(0.5)  # Odds menor que 1
        
        with pytest.raises(ValueError):
            calculator.calculate_probability_from_odds(-1.0)  # Odds negativa
    
    def test_convert_odds_format(self):
        """Testa conversão de formato de odds"""
        calculator = ProbabilityCalculator()
        
        # Decimal para fracionário
        fractional = calculator.decimal_to_fractional(2.0)
        assert fractional == "1/1"
        
        # Decimal para americano
        american = calculator.decimal_to_american(2.0)
        assert american == "+100"
        
        # Fracionário para decimal
        decimal = calculator.fractional_to_decimal("1/1")
        assert abs(decimal - 2.0) < 1e-10
        
        # Americano para decimal
        decimal = calculator.american_to_decimal("+100")
        assert abs(decimal - 2.0) < 1e-10

class TestValueIdentifier:
    """Testes para ValueIdentifier"""
    
    def test_init(self):
        """Testa inicialização do ValueIdentifier"""
        identifier = ValueIdentifier()
        assert identifier is not None
        assert hasattr(identifier, 'min_ev_threshold')
        assert hasattr(identifier, 'min_confidence_threshold')
    
    def test_calculate_kelly_criterion(self):
        """Testa cálculo do Kelly Criterion"""
        identifier = ValueIdentifier()
        
        # Teste com EV positivo
        kelly = identifier.calculate_kelly_criterion(0.6, 2.0)
        expected = (0.6 * 2.0 - 1) / (2.0 - 1)  # 0.2
        assert abs(kelly - expected) < 1e-10
        
        # Teste com EV negativo
        kelly = identifier.calculate_kelly_criterion(0.4, 2.0)
        assert kelly == 0  # Kelly deve ser 0 para EV negativo
        
        # Teste com EV zero
        kelly = identifier.calculate_kelly_criterion(0.5, 2.0)
        assert kelly == 0  # Kelly deve ser 0 para EV zero
    
    def test_calculate_stake_percentage(self):
        """Testa cálculo de percentual de stake"""
        identifier = ValueIdentifier()
        
        # Teste com Kelly Criterion
        stake = identifier.calculate_stake_percentage(0.6, 2.0, method='kelly')
        kelly = identifier.calculate_kelly_criterion(0.6, 2.0)
        assert abs(stake - kelly) < 1e-10
        
        # Teste com método fixo
        stake = identifier.calculate_stake_percentage(0.6, 2.0, method='fixed', fixed_percentage=0.02)
        assert stake == 0.02
        
        # Teste com método percentual do bankroll
        stake = identifier.calculate_stake_percentage(0.6, 2.0, method='percentage', bankroll_percentage=0.05)
        assert stake == 0.05
    
    def test_identify_value_bet(self):
        """Testa identificação de value bet"""
        identifier = ValueIdentifier()
        
        # Teste com value bet válido
        prediction_data = {
            'predicted_probability': 0.6,
            'current_odd': 2.0,
            'confidence': 0.8,
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        assert is_value_bet == True
        
        # Teste com EV insuficiente
        prediction_data['predicted_probability'] = 0.4
        is_value_bet = identifier.identify_value_bet(prediction_data)
        assert is_value_bet == False
        
        # Teste com confiança insuficiente
        prediction_data['predicted_probability'] = 0.6
        prediction_data['confidence'] = 0.5
        is_value_bet = identifier.identify_value_bet(prediction_data)
        assert is_value_bet == False

class TestFeatureEngineer:
    """Testes para FeatureEngineer"""
    
    def test_init(self):
        """Testa inicialização do FeatureEngineer"""
        engineer = FeatureEngineer()
        assert engineer is not None
    
    def test_create_team_features(self, sample_team_stats):
        """Testa criação de features de time"""
        engineer = FeatureEngineer()
        features = engineer.create_team_features(sample_team_stats)
        
        assert isinstance(features, dict)
        assert 'goals_scored' in features
        assert 'goals_conceded' in features
        assert 'form' in features
        assert 'home_form' in features
        assert 'away_form' in features
        assert 'goal_difference' in features
        assert 'win_percentage' in features
    
    def test_create_match_features(self, sample_match_data, sample_team_stats):
        """Testa criação de features de partida"""
        engineer = FeatureEngineer()
        home_stats = sample_team_stats.copy()
        away_stats = sample_team_stats.copy()
        
        features = engineer.create_match_features(sample_match_data, home_stats, away_stats)
        
        assert isinstance(features, dict)
        assert 'home_goals_avg' in features
        assert 'away_goals_avg' in features
        assert 'home_form' in features
        assert 'away_form' in features
        assert 'form_difference' in features
        assert 'goals_difference' in features
    
    def test_create_odds_features(self, sample_odds_data):
        """Testa criação de features de odds"""
        engineer = FeatureEngineer()
        features = engineer.create_odds_features(sample_odds_data)
        
        assert isinstance(features, dict)
        assert 'home_odd' in features
        assert 'draw_odd' in features
        assert 'away_odd' in features
        assert 'total_probability' in features
        assert 'home_implied_prob' in features
        assert 'draw_implied_prob' in features
        assert 'away_implied_prob' in features
    
    def test_normalize_features(self):
        """Testa normalização de features"""
        engineer = FeatureEngineer()
        
        # Dados de teste
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        # Normalização min-max
        normalized = engineer.normalize_features(data, method='minmax')
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)
        
        # Normalização z-score
        normalized = engineer.normalize_features(data, method='zscore')
        assert np.allclose(normalized.mean(axis=0), 0, atol=1e-10)
        assert np.allclose(normalized.std(axis=0), 1, atol=1e-10)

class TestStatisticalAnalyzer:
    """Testes para StatisticalAnalyzer"""
    
    def test_init(self):
        """Testa inicialização do StatisticalAnalyzer"""
        analyzer = StatisticalAnalyzer()
        assert analyzer is not None
    
    def test_calculate_basic_stats(self):
        """Testa cálculo de estatísticas básicas"""
        analyzer = StatisticalAnalyzer()
        
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = analyzer.calculate_basic_stats(data)
        
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert stats['mean'] == 5.5
        assert stats['median'] == 5.5
        assert stats['min'] == 1
        assert stats['max'] == 10
    
    def test_calculate_correlation(self):
        """Testa cálculo de correlação"""
        analyzer = StatisticalAnalyzer()
        
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        correlation = analyzer.calculate_correlation(x, y)
        assert abs(correlation - 1.0) < 1e-10  # Correlação perfeita
    
    def test_calculate_confidence_interval(self):
        """Testa cálculo de intervalo de confiança"""
        analyzer = StatisticalAnalyzer()
        
        data = np.random.normal(100, 15, 1000)  # Distribuição normal
        ci = analyzer.calculate_confidence_interval(data, confidence=0.95)
        
        assert 'lower' in ci
        assert 'upper' in ci
        assert 'mean' in ci
        assert ci['lower'] < ci['mean'] < ci['upper']
    
    def test_detect_outliers(self):
        """Testa detecção de outliers"""
        analyzer = StatisticalAnalyzer()
        
        # Dados com outliers
        data = [1, 2, 3, 4, 5, 100, 6, 7, 8, 9, 10]
        outliers = analyzer.detect_outliers(data)
        
        assert len(outliers) > 0
        assert 100 in outliers  # O valor 100 deve ser detectado como outlier

class TestBankrollManager:
    """Testes para BankrollManager"""
    
    def test_init(self):
        """Testa inicialização do BankrollManager"""
        manager = BankrollManager(initial_bankroll=1000.0)
        assert manager.bankroll == 1000.0
        assert manager.initial_bankroll == 1000.0
    
    def test_calculate_stake(self):
        """Testa cálculo de stake"""
        manager = BankrollManager(initial_bankroll=1000.0)
        
        # Teste com Kelly Criterion
        stake = manager.calculate_stake(0.6, 2.0, method='kelly')
        kelly = (0.6 * 2.0 - 1) / (2.0 - 1)  # 0.2
        expected_stake = kelly * 1000.0
        assert abs(stake - expected_stake) < 1e-10
        
        # Teste com método fixo
        stake = manager.calculate_stake(0.6, 2.0, method='fixed', fixed_percentage=0.02)
        assert stake == 20.0  # 2% de 1000
    
    def test_update_bankroll(self):
        """Testa atualização do bankroll"""
        manager = BankrollManager(initial_bankroll=1000.0)
        
        # Aposta vencedora
        manager.update_bankroll(100.0, 2.0, won=True)
        assert manager.bankroll == 1200.0  # 1000 + 100*2
        
        # Aposta perdedora
        manager.update_bankroll(50.0, 2.0, won=False)
        assert manager.bankroll == 1150.0  # 1200 - 50
    
    def test_calculate_roi(self):
        """Testa cálculo de ROI"""
        manager = BankrollManager(initial_bankroll=1000.0)
        
        # Simular algumas apostas
        manager.update_bankroll(100.0, 2.0, won=True)  # +100
        manager.update_bankroll(50.0, 2.0, won=False)  # -50
        manager.update_bankroll(200.0, 1.5, won=True)  # +100
        
        roi = manager.calculate_roi()
        expected_roi = (manager.bankroll - manager.initial_bankroll) / manager.initial_bankroll
        assert abs(roi - expected_roi) < 1e-10
    
    def test_get_bankroll_history(self):
        """Testa histórico do bankroll"""
        manager = BankrollManager(initial_bankroll=1000.0)
        
        # Fazer algumas apostas
        manager.update_bankroll(100.0, 2.0, won=True)
        manager.update_bankroll(50.0, 2.0, won=False)
        
        history = manager.get_bankroll_history()
        assert len(history) == 3  # Inicial + 2 apostas
        assert history[0]['bankroll'] == 1000.0
        assert history[1]['bankroll'] == 1200.0
        assert history[2]['bankroll'] == 1150.0

class TestTelegramNotifier:
    """Testes para TelegramNotifier"""
    
    def test_init(self):
        """Testa inicialização do TelegramNotifier"""
        notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
        assert notifier.bot_token == "test_token"
        assert notifier.chat_id == "test_chat"
    
    @patch('requests.post')
    def test_send_message(self, mock_post):
        """Testa envio de mensagem"""
        notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
        
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = notifier.send_message("Test message")
        
        assert result == True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_value_bet_alert(self, mock_post):
        """Testa envio de alerta de value bet"""
        notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
        
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        value_bet_data = {
            'match': 'Manchester United vs Liverpool',
            'market': '1x2',
            'selection': 'home_win',
            'odd': 2.10,
            'value': 0.15,
            'confidence': 0.8
        }
        
        result = notifier.send_value_bet_alert(value_bet_data)
        
        assert result == True
        mock_post.assert_called_once()

class TestEmailNotifier:
    """Testes para EmailNotifier"""
    
    def test_init(self):
        """Testa inicialização do EmailNotifier"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="test_password"
        )
        assert notifier.smtp_host == "smtp.gmail.com"
        assert notifier.smtp_port == 587
        assert notifier.username == "test@example.com"
    
    @patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        """Testa envio de email"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="test_password"
        )
        
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = notifier.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        assert result == True
        mock_server.sendmail.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_value_bet_alert(self, mock_smtp):
        """Testa envio de alerta de value bet por email"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="test_password"
        )
        
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        value_bet_data = {
            'match': 'Manchester United vs Liverpool',
            'market': '1x2',
            'selection': 'home_win',
            'odd': 2.10,
            'value': 0.15,
            'confidence': 0.8
        }
        
        result = notifier.send_value_bet_alert(value_bet_data, "recipient@example.com")
        
        assert result == True
        mock_server.sendmail.assert_called_once()

class TestRedisCache:
    """Testes para RedisCache"""
    
    def test_init(self, mock_redis):
        """Testa inicialização do RedisCache"""
        cache = RedisCache()
        assert cache is not None
        assert hasattr(cache, 'redis_client')
    
    def test_set_and_get(self, mock_redis):
        """Testa operações set e get"""
        cache = RedisCache()
        
        # Mock do redis_client
        cache.redis_client = mock_redis
        
        # Teste set
        result = cache.set('test', 'key', {'data': 'value'}, ttl=60)
        assert result == True
        mock_redis.set.assert_called_once()
        
        # Teste get
        mock_redis.get.return_value = '{"data": "value"}'
        value = cache.get('test', 'key')
        assert value == {'data': 'value'}
    
    def test_delete(self, mock_redis):
        """Testa operação delete"""
        cache = RedisCache()
        cache.redis_client = mock_redis
        
        result = cache.delete('test', 'key')
        assert result == True
        mock_redis.delete.assert_called_once()
    
    def test_exists(self, mock_redis):
        """Testa operação exists"""
        cache = RedisCache()
        cache.redis_client = mock_redis
        
        mock_redis.exists.return_value = True
        result = cache.exists('test', 'key')
        assert result == True
    
    def test_ttl(self, mock_redis):
        """Testa operação ttl"""
        cache = RedisCache()
        cache.redis_client = mock_redis
        
        mock_redis.ttl.return_value = 60
        result = cache.ttl('test', 'key')
        assert result == 60
    
    def test_clear_type(self, mock_redis):
        """Testa limpeza por tipo"""
        cache = RedisCache()
        cache.redis_client = mock_redis
        
        mock_redis.scan_iter.return_value = ['test:key1', 'test:key2']
        result = cache.clear_type('test')
        assert result == 2
        assert mock_redis.delete.call_count == 2

class TestDataValidation:
    """Testes para validação de dados"""
    
    def test_validate_odds(self):
        """Testa validação de odds"""
        from utils.data_validation import validate_odds
        
        # Odds válidas
        assert validate_odds(2.0) == True
        assert validate_odds(1.5) == True
        assert validate_odds(10.0) == True
        
        # Odds inválidas
        assert validate_odds(0.5) == False  # Menor que 1
        assert validate_odds(-1.0) == False  # Negativa
        assert validate_odds(0) == False  # Zero
    
    def test_validate_probability(self):
        """Testa validação de probabilidade"""
        from utils.data_validation import validate_probability
        
        # Probabilidades válidas
        assert validate_probability(0.5) == True
        assert validate_probability(0.0) == True
        assert validate_probability(1.0) == True
        
        # Probabilidades inválidas
        assert validate_probability(-0.1) == False  # Negativa
        assert validate_probability(1.1) == False  # Maior que 1
    
    def test_validate_team_name(self):
        """Testa validação de nome de time"""
        from utils.data_validation import validate_team_name
        
        # Nomes válidos
        assert validate_team_name("Manchester United") == True
        assert validate_team_name("Real Madrid") == True
        assert validate_team_name("FC Barcelona") == True
        
        # Nomes inválidos
        assert validate_team_name("") == False  # Vazio
        assert validate_team_name("A" * 101) == False  # Muito longo
        assert validate_team_name("123") == False  # Apenas números
    
    def test_validate_match_data(self, sample_match_data):
        """Testa validação de dados de partida"""
        from utils.data_validation import validate_match_data
        
        # Dados válidos
        assert validate_match_data(sample_match_data) == True
        
        # Dados inválidos
        invalid_data = sample_match_data.copy()
        invalid_data['fixture_id'] = None
        assert validate_match_data(invalid_data) == False
        
        invalid_data = sample_match_data.copy()
        invalid_data['home_team_name'] = ""
        assert validate_match_data(invalid_data) == False

class TestDataProcessing:
    """Testes para processamento de dados"""
    
    def test_clean_team_name(self):
        """Testa limpeza de nome de time"""
        from utils.data_processing import clean_team_name
        
        # Nomes com caracteres especiais
        assert clean_team_name("Manchester United FC") == "Manchester United"
        assert clean_team_name("Real Madrid C.F.") == "Real Madrid"
        assert clean_team_name("FC Barcelona") == "Barcelona"
        
        # Nomes com espaços extras
        assert clean_team_name("  Liverpool  ") == "Liverpool"
    
    def test_normalize_odds(self):
        """Testa normalização de odds"""
        from utils.data_processing import normalize_odds
        
        # Odds fracionárias
        assert abs(normalize_odds("1/1", "fractional") - 2.0) < 1e-10
        assert abs(normalize_odds("2/1", "fractional") - 3.0) < 1e-10
        
        # Odds americanas
        assert abs(normalize_odds("+100", "american") - 2.0) < 1e-10
        assert abs(normalize_odds("-200", "american") - 1.5) < 1e-10
    
    def test_convert_currency(self):
        """Testa conversão de moeda"""
        from utils.data_processing import convert_currency
        
        # Conversão USD para AOA (taxa fictícia)
        with patch('utils.data_processing.get_exchange_rate', return_value=500.0):
            amount = convert_currency(100.0, "USD", "AOA")
            assert amount == 50000.0
        
        # Conversão AOA para USD
        with patch('utils.data_processing.get_exchange_rate', return_value=0.002):
            amount = convert_currency(50000.0, "AOA", "USD")
            assert amount == 100.0

class TestFileOperations:
    """Testes para operações de arquivo"""
    
    def test_save_json(self, temp_directory):
        """Testa salvamento de JSON"""
        from utils.file_operations import save_json
        
        data = {"key": "value", "number": 123}
        file_path = os.path.join(temp_directory, "test.json")
        
        result = save_json(data, file_path)
        assert result == True
        assert os.path.exists(file_path)
        
        # Verificar conteúdo
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == data
    
    def test_load_json(self, temp_directory):
        """Testa carregamento de JSON"""
        from utils.file_operations import load_json
        
        data = {"key": "value", "number": 123}
        file_path = os.path.join(temp_directory, "test.json")
        
        # Salvar dados
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        # Carregar dados
        loaded_data = load_json(file_path)
        assert loaded_data == data
    
    def test_save_csv(self, temp_directory):
        """Testa salvamento de CSV"""
        from utils.file_operations import save_csv
        
        data = pd.DataFrame({
            'team': ['Manchester United', 'Liverpool'],
            'goals': [2, 1],
            'odds': [2.1, 3.2]
        })
        
        file_path = os.path.join(temp_directory, "test.csv")
        result = save_csv(data, file_path)
        
        assert result == True
        assert os.path.exists(file_path)
        
        # Verificar conteúdo
        loaded_data = pd.read_csv(file_path)
        pd.testing.assert_frame_equal(loaded_data, data)
    
    def test_load_csv(self, temp_directory):
        """Testa carregamento de CSV"""
        from utils.file_operations import load_csv
        
        data = pd.DataFrame({
            'team': ['Manchester United', 'Liverpool'],
            'goals': [2, 1],
            'odds': [2.1, 3.2]
        })
        
        file_path = os.path.join(temp_directory, "test.csv")
        data.to_csv(file_path, index=False)
        
        loaded_data = load_csv(file_path)
        pd.testing.assert_frame_equal(loaded_data, data)
