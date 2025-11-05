"""
Utilitários e helpers para testes
Funções auxiliares para facilitar a criação e execução de testes
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import tempfile
import shutil

def create_test_match_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de partida para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "league_name": "Premier League",
        "home_team_name": "Manchester United",
        "away_team_name": "Liverpool",
        "date": datetime.now() + timedelta(hours=2),
        "status": "NS",
        "home_score": None,
        "away_score": None
    }
    default_data.update(kwargs)
    return default_data

def create_test_odds_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de odds para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "bookmaker": "bet365",
        "market": "1x2",
        "selection": "home_win",
        "odd": 2.10,
        "timestamp": datetime.now()
    }
    default_data.update(kwargs)
    return default_data

def create_test_prediction_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de predição para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "market": "1x2",
        "selection": "home_win",
        "predicted_probability": 0.65,
        "implied_probability": 0.48,
        "recommended_odd": 2.10,
        "current_odd": 2.05,
        "expected_value": 0.15,
        "confidence": 0.75,
        "stake_percentage": 0.02,
        "recommended": True
    }
    default_data.update(kwargs)
    return default_data

def create_test_team_stats(team_id: int = 789, **kwargs) -> Dict[str, Any]:
    """Cria estatísticas de time para testes"""
    default_data = {
        "team_id": team_id,
        "team_name": "Arsenal",
        "goals_scored": 45,
        "goals_conceded": 32,
        "wins": 15,
        "draws": 8,
        "losses": 7,
        "form": 0.75,
        "home_form": 0.80,
        "away_form": 0.70,
        "updated_at": datetime.now()
    }
    default_data.update(kwargs)
    return default_data

def create_test_ml_dataset(n_samples: int = 100, n_features: int = 10, n_classes: int = 3) -> Dict[str, np.ndarray]:
    """Cria dataset de ML para testes"""
    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, n_classes, n_samples)
    
    # Dividir em treino e teste
    split_idx = int(n_samples * 0.8)
    X_train = X[:split_idx]
    y_train = y[:split_idx]
    X_test = X[split_idx:]
    y_test = y[split_idx:]
    
    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "feature_names": [f"feature_{i}" for i in range(n_features)]
    }

def create_test_user_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de usuário para testes"""
    default_data = {
        "username": "testuser",
        "email": "test@marabet.ai",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "full_name": "Test User",
        "phone": "+244123456789",
        "country": "AO",
        "timezone": "Africa/Luanda",
        "language": "pt",
        "default_currency": "AOA",
        "min_bet_amount": "10.0",
        "max_bet_amount": "1000.0",
        "risk_tolerance": "medium",
        "email_notifications": True,
        "telegram_notifications": False
    }
    default_data.update(kwargs)
    return default_data

def create_test_csv_file(data: List[Dict[str, Any]], file_path: str) -> str:
    """Cria arquivo CSV para testes"""
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return file_path

def create_test_json_file(data: List[Dict[str, Any]], file_path: str) -> str:
    """Cria arquivo JSON para testes"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    return file_path

def create_temp_directory() -> str:
    """Cria diretório temporário para testes"""
    return tempfile.mkdtemp()

def cleanup_temp_directory(directory: str) -> None:
    """Remove diretório temporário"""
    if os.path.exists(directory):
        shutil.rmtree(directory)

def create_mock_api_response(data: Dict[str, Any], status_code: int = 200) -> Any:
    """Cria mock de resposta de API"""
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.json.return_value = data
    mock_response.status_code = status_code
    return mock_response

def create_mock_database_session():
    """Cria mock de sessão de banco de dados"""
    from unittest.mock import Mock
    
    mock_session = Mock()
    mock_session.query.return_value = Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    mock_session.close.return_value = None
    return mock_session

def create_mock_redis_client():
    """Cria mock de cliente Redis"""
    from unittest.mock import Mock
    
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.set.return_value = True
    mock_redis.get.return_value = None
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    mock_redis.ttl.return_value = -1
    mock_redis.scan_iter.return_value = []
    return mock_redis

def create_mock_telegram_bot():
    """Cria mock de bot do Telegram"""
    from unittest.mock import Mock, patch
    
    mock_bot = Mock()
    mock_bot.send_message.return_value = {"message_id": 123}
    return mock_bot

def create_mock_smtp_server():
    """Cria mock de servidor SMTP"""
    from unittest.mock import Mock
    
    mock_server = Mock()
    mock_server.starttls.return_value = None
    mock_server.login.return_value = None
    mock_server.sendmail.return_value = None
    mock_server.quit.return_value = None
    return mock_server

def assert_dataframe_equals(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> None:
    """Verifica se dois DataFrames são iguais"""
    pd.testing.assert_frame_equal(df1, df2, **kwargs)

def assert_dict_contains(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> None:
    """Verifica se dict1 contém todas as chaves e valores de dict2"""
    for key, value in dict2.items():
        assert key in dict1, f"Chave '{key}' não encontrada em dict1"
        assert dict1[key] == value, f"Valor da chave '{key}' não coincide: {dict1[key]} != {value}"

def assert_list_contains(list1: List[Any], list2: List[Any]) -> None:
    """Verifica se list1 contém todos os elementos de list2"""
    for item in list2:
        assert item in list1, f"Item '{item}' não encontrado em list1"

def assert_approx_equals(value1: float, value2: float, tolerance: float = 1e-10) -> None:
    """Verifica se dois valores float são aproximadamente iguais"""
    assert abs(value1 - value2) < tolerance, f"Valores não são aproximadamente iguais: {value1} != {value2} (tolerância: {tolerance})"

def assert_datetime_equals(dt1: datetime, dt2: datetime, tolerance_seconds: int = 1) -> None:
    """Verifica se dois datetimes são iguais (com tolerância)"""
    diff = abs((dt1 - dt2).total_seconds())
    assert diff <= tolerance_seconds, f"Datetimes não são iguais: {dt1} != {dt2} (diferença: {diff}s)"

def create_test_league_data(league_id: int = 39, **kwargs) -> Dict[str, Any]:
    """Cria dados de liga para testes"""
    default_data = {
        "league_id": league_id,
        "name": "Premier League",
        "country": "England",
        "type": "League",
        "season": 2024,
        "start_date": "2024-08-17",
        "end_date": "2025-05-25",
        "logo": "https://media.api-sports.io/football/leagues/39.png"
    }
    default_data.update(kwargs)
    return default_data

def create_test_bookmaker_data(bookmaker_id: str = "bet365", **kwargs) -> Dict[str, Any]:
    """Cria dados de casa de apostas para testes"""
    default_data = {
        "bookmaker_id": bookmaker_id,
        "name": "Bet365",
        "country": "UK",
        "website": "https://www.bet365.com",
        "logo": "https://media.api-sports.io/bookmakers/bet365.png",
        "active": True
    }
    default_data.update(kwargs)
    return default_data

def create_test_market_data(market_id: str = "1x2", **kwargs) -> Dict[str, Any]:
    """Cria dados de mercado para testes"""
    default_data = {
        "market_id": market_id,
        "name": "Match Winner",
        "description": "1X2 - Home Win, Draw, Away Win",
        "selections": ["home_win", "draw", "away_win"],
        "active": True
    }
    default_data.update(kwargs)
    return default_data

def create_test_fixture_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de fixture para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "league_id": 39,
        "season": 2024,
        "date": datetime.now() + timedelta(hours=2),
        "status": "NS",
        "home_team_id": 33,
        "away_team_id": 40,
        "home_team_name": "Manchester United",
        "away_team_name": "Liverpool",
        "home_score": None,
        "away_score": None,
        "referee": "John Smith",
        "venue": "Old Trafford"
    }
    default_data.update(kwargs)
    return default_data

def create_test_odds_collection_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de coleta de odds para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "bookmaker": "bet365",
        "market": "1x2",
        "selections": [
            {"selection": "home_win", "odd": 2.10},
            {"selection": "draw", "odd": 3.40},
            {"selection": "away_win", "odd": 3.20}
        ],
        "timestamp": datetime.now(),
        "collection_status": "success"
    }
    default_data.update(kwargs)
    return default_data

def create_test_prediction_collection_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de coleta de predições para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "model_name": "random_forest",
        "market": "1x2",
        "predictions": [
            {"selection": "home_win", "probability": 0.65, "confidence": 0.75},
            {"selection": "draw", "probability": 0.20, "confidence": 0.60},
            {"selection": "away_win", "probability": 0.15, "confidence": 0.70}
        ],
        "timestamp": datetime.now(),
        "collection_status": "success"
    }
    default_data.update(kwargs)
    return default_data

def create_test_value_bet_data(fixture_id: int = 12345, **kwargs) -> Dict[str, Any]:
    """Cria dados de value bet para testes"""
    default_data = {
        "fixture_id": fixture_id,
        "match": "Manchester United vs Liverpool",
        "market": "1x2",
        "selection": "home_win",
        "bookmaker": "bet365",
        "odd": 2.10,
        "predicted_probability": 0.65,
        "implied_probability": 0.48,
        "expected_value": 0.15,
        "confidence": 0.75,
        "kelly_percentage": 0.02,
        "is_value_bet": True,
        "timestamp": datetime.now()
    }
    default_data.update(kwargs)
    return default_data

def create_test_notification_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de notificação para testes"""
    default_data = {
        "type": "value_bet_alert",
        "title": "Value Bet Encontrado!",
        "message": "Manchester United vs Liverpool - Home Win @ 2.10",
        "priority": "high",
        "channels": ["telegram", "email"],
        "data": {
            "fixture_id": 12345,
            "market": "1x2",
            "selection": "home_win",
            "odd": 2.10,
            "value": 0.15
        },
        "timestamp": datetime.now()
    }
    default_data.update(kwargs)
    return default_data

def create_test_cache_data(key: str = "test_key", **kwargs) -> Dict[str, Any]:
    """Cria dados de cache para testes"""
    default_data = {
        "key": key,
        "value": {"data": "test_value"},
        "ttl": 300,
        "type": "odds",
        "timestamp": datetime.now()
    }
    default_data.update(kwargs)
    return default_data

def create_test_performance_metrics(**kwargs) -> Dict[str, Any]:
    """Cria métricas de performance para testes"""
    default_data = {
        "total_predictions": 1000,
        "correct_predictions": 650,
        "accuracy": 0.65,
        "precision": 0.68,
        "recall": 0.62,
        "f1_score": 0.65,
        "roi": 0.15,
        "profit_loss": 1500.0,
        "win_rate": 0.65,
        "average_odds": 2.50,
        "total_stake": 10000.0,
        "period": "30_days"
    }
    default_data.update(kwargs)
    return default_data

def create_test_system_status(**kwargs) -> Dict[str, Any]:
    """Cria status do sistema para testes"""
    default_data = {
        "status": "running",
        "uptime": "5 days, 12 hours",
        "version": "1.0.0",
        "last_update": datetime.now(),
        "components": {
            "database": "healthy",
            "redis": "healthy",
            "celery": "healthy",
            "api": "healthy",
            "collectors": "running"
        },
        "metrics": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "active_connections": 15
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_error_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de erro para testes"""
    default_data = {
        "error_type": "APIError",
        "error_message": "API rate limit exceeded",
        "error_code": 429,
        "component": "odds_collector",
        "timestamp": datetime.now(),
        "context": {
            "endpoint": "https://api.the-odds-api.com/v4/sports/soccer_epl/odds",
            "retry_count": 3,
            "last_success": datetime.now() - timedelta(minutes=5)
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_config_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de configuração para testes"""
    default_data = {
        "min_confidence": 0.7,
        "max_confidence": 0.95,
        "min_value_ev": 0.1,
        "max_stake_percentage": 0.05,
        "kelly_fraction": 0.25,
        "default_currency": "AOA",
        "timezone": "Africa/Luanda",
        "language": "pt",
        "notifications": {
            "email_enabled": True,
            "telegram_enabled": True,
            "min_value_threshold": 0.1,
            "min_confidence_threshold": 0.7
        },
        "collectors": {
            "api_football_enabled": True,
            "odds_api_enabled": True,
            "collection_interval": 300,
            "retry_attempts": 3
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_log_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de log para testes"""
    default_data = {
        "level": "INFO",
        "message": "Value bet identified",
        "component": "value_identifier",
        "timestamp": datetime.now(),
        "context": {
            "fixture_id": 12345,
            "selection": "home_win",
            "odd": 2.10,
            "value": 0.15
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_audit_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de auditoria para testes"""
    default_data = {
        "action": "user_login",
        "user_id": 1,
        "username": "testuser",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "timestamp": datetime.now(),
        "success": True,
        "details": {
            "login_method": "password",
            "session_id": "sess_123456789"
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_metrics_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de métricas para testes"""
    default_data = {
        "timestamp": datetime.now(),
        "metrics": {
            "predictions_per_minute": 5.2,
            "value_bets_per_hour": 2.1,
            "api_response_time": 0.45,
            "cache_hit_rate": 0.85,
            "error_rate": 0.02,
            "active_users": 15,
            "total_requests": 1250
        },
        "tags": {
            "environment": "test",
            "version": "1.0.0",
            "region": "us-east-1"
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_alert_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de alerta para testes"""
    default_data = {
        "alert_id": "alert_123456",
        "type": "high_error_rate",
        "severity": "warning",
        "title": "High Error Rate Detected",
        "message": "Error rate has exceeded 5% for the last 5 minutes",
        "timestamp": datetime.now(),
        "status": "active",
        "component": "api",
        "metrics": {
            "error_rate": 0.08,
            "threshold": 0.05,
            "duration": "5 minutes"
        }
    }
    default_data.update(kwargs)
    return default_data

def create_test_backup_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de backup para testes"""
    default_data = {
        "backup_id": "backup_123456",
        "type": "full",
        "status": "completed",
        "start_time": datetime.now() - timedelta(minutes=30),
        "end_time": datetime.now(),
        "duration": 1800,  # 30 minutes
        "size": 1024 * 1024 * 100,  # 100MB
        "files": [
            "database_backup.sql",
            "redis_backup.rdb",
            "logs_backup.tar.gz"
        ],
        "location": "/backups/2024/01/15/",
        "compression": "gzip",
        "encryption": "aes256"
    }
    default_data.update(kwargs)
    return default_data

def create_test_deployment_data(**kwargs) -> Dict[str, Any]:
    """Cria dados de deployment para testes"""
    default_data = {
        "deployment_id": "deploy_123456",
        "version": "1.0.0",
        "environment": "production",
        "status": "success",
        "start_time": datetime.now() - timedelta(minutes=10),
        "end_time": datetime.now(),
        "duration": 600,  # 10 minutes
        "components": [
            "api",
            "collectors",
            "ml_models",
            "notifications"
        ],
        "rollback_available": True,
        "health_check_passed": True
    }
    default_data.update(kwargs)
    return default_data
