#!/usr/bin/env python3
"""
Configuração global de testes para o MaraBet AI
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Carregar variáveis de ambiente de teste
load_dotenv()

@pytest.fixture(scope="session")
def test_env():
    """Configura ambiente de teste"""
    # Configurar variáveis de ambiente para testes
    os.environ.update({
        'API_FOOTBALL_KEY': 'test_api_key_123',
        'TELEGRAM_BOT_TOKEN': 'test_telegram_token_123',
        'TELEGRAM_CHAT_ID': '123456789',
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'test_password',
        'NOTIFICATION_EMAIL': 'test@example.com',
        'ADMIN_EMAIL': 'test@example.com',
        'DATABASE_URL': 'sqlite:///:memory:',
        'DEBUG': 'True',
        'TESTING': 'True'
    })
    return os.environ

@pytest.fixture
def temp_dir():
    """Cria diretório temporário para testes"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_api_response():
    """Mock de resposta da API Football"""
    return {
        "get": "fixtures",
        "parameters": {
            "league": "39",
            "season": "2024",
            "date": "2024-01-01"
        },
        "errors": [],
        "results": 1,
        "paging": {
            "current": 1,
            "total": 1
        },
        "response": [
            {
                "fixture": {
                    "id": 12345,
                    "referee": "John Doe",
                    "timezone": "UTC",
                    "date": "2024-01-01T15:00:00+00:00",
                    "timestamp": 1704110400,
                    "periods": {
                        "first": 1704110400,
                        "second": 1704114000
                    },
                    "venue": {
                        "id": 1,
                        "name": "Test Stadium",
                        "city": "Test City"
                    },
                    "status": {
                        "long": "Match Finished",
                        "short": "FT",
                        "elapsed": 90
                    }
                },
                "league": {
                    "id": 39,
                    "name": "Premier League",
                    "country": "England",
                    "logo": "https://media.api-sports.io/football/leagues/39.png",
                    "flag": "https://media.api-sports.io/flags/gb.svg",
                    "season": 2024,
                    "round": "Regular Season - 1"
                },
                "teams": {
                    "home": {
                        "id": 50,
                        "name": "Manchester City",
                        "logo": "https://media.api-sports.io/football/teams/50.png",
                        "winner": True
                    },
                    "away": {
                        "id": 33,
                        "name": "Manchester United",
                        "logo": "https://media.api-sports.io/football/teams/33.png",
                        "winner": False
                    }
                },
                "goals": {
                    "home": 2,
                    "away": 1
                },
                "score": {
                    "halftime": {
                        "home": 1,
                        "away": 0
                    },
                    "fulltime": {
                        "home": 2,
                        "away": 1
                    },
                    "extratime": {
                        "home": None,
                        "away": None
                    },
                    "penalty": {
                        "home": None,
                        "away": None
                    }
                }
            }
        ]
    }

@pytest.fixture
def mock_odds_response():
    """Mock de resposta da API de odds"""
    return {
        "success": True,
        "data": [
            {
                "sport_key": "soccer_epl",
                "sport_nice": "EPL",
                "teams": ["Manchester City", "Manchester United"],
                "commence_time": "2024-01-01T15:00:00Z",
                "home_team": "Manchester City",
                "sites": [
                    {
                        "site_key": "bet365",
                        "site_nice": "Bet365",
                        "last_update": 1704110400,
                        "odds": {
                            "h2h": [1.85, 3.40, 4.20]
                        }
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_telegram_response():
    """Mock de resposta do Telegram"""
    return {
        "ok": True,
        "result": {
            "message_id": 123,
            "from": {
                "id": 123456789,
                "is_bot": True,
                "first_name": "MaraBet AI Bot",
                "username": "marabet_ai_bot"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "type": "private"
            },
            "date": 1704110400,
            "text": "Test message"
        }
    }

@pytest.fixture
def sample_match_data():
    """Dados de exemplo de partida"""
    return {
        "fixture_id": 12345,
        "league_id": 39,
        "league_name": "Premier League",
        "home_team": "Manchester City",
        "away_team": "Manchester United",
        "home_team_id": 50,
        "away_team_id": 33,
        "date": "2024-01-01T15:00:00Z",
        "status": "FT",
        "home_score": 2,
        "away_score": 1,
        "home_odds": 1.85,
        "draw_odds": 3.40,
        "away_odds": 4.20
    }

@pytest.fixture
def sample_prediction_data():
    """Dados de exemplo de predição"""
    return {
        "match_id": 12345,
        "home_team": "Manchester City",
        "away_team": "Manchester United",
        "prediction": "home_win",
        "confidence": 0.75,
        "expected_value": 0.12,
        "recommended_bet": "home_win",
        "odds": 1.85,
        "stake_percentage": 0.05,
        "features": {
            "home_form": 0.8,
            "away_form": 0.6,
            "head_to_head": 0.7,
            "home_advantage": 0.1
        }
    }

@pytest.fixture
def mock_database():
    """Mock de banco de dados"""
    db_mock = Mock()
    db_mock.query.return_value.all.return_value = []
    db_mock.add.return_value = None
    db_mock.commit.return_value = None
    return db_mock

@pytest.fixture
def mock_ml_model():
    """Mock de modelo de ML"""
    model_mock = Mock()
    model_mock.predict.return_value = [0.75]
    model_mock.predict_proba.return_value = [[0.25, 0.75]]
    model_mock.score.return_value = 0.85
    return model_mock

@pytest.fixture
def mock_notification_manager():
    """Mock do gerenciador de notificações"""
    manager_mock = Mock()
    manager_mock.send_notification.return_value = True
    manager_mock.send_telegram.return_value = True
    manager_mock.send_email.return_value = True
    return manager_mock

# Configurações de pytest
def pytest_configure(config):
    """Configuração do pytest"""
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "e2e: marca testes end-to-end"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )

def pytest_collection_modifyitems(config, items):
    """Modifica itens de coleção de testes"""
    for item in items:
        # Marcar testes baseado no caminho do arquivo
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Marcar testes lentos baseado no nome
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)