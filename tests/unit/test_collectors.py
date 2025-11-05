#!/usr/bin/env python3
"""
Testes unitários para coletores de dados
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock dos módulos que não existem ainda
class FootballCollector:
    def __init__(self):
        self.api_key = "test_key"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {"X-API-Key": self.api_key}
    
    def get_live_matches(self):
        return []
    
    def get_fixtures_by_date(self, date):
        return []
    
    def get_team_statistics(self, team_id, league_id, season):
        return {}
    
    def get_head_to_head(self, team1_id, team2_id):
        return []

class OddsCollector:
    def __init__(self):
        self.api_key = "test_key"
        self.base_url = "https://api.the-odds-api.com/v4"
    
    def get_odds(self, sport):
        return []
    
    def get_odds_by_sport(self, sport, markets):
        return []
    
    def get_odds_by_event(self, event_id):
        return []
    
    def parse_odds_data(self, data):
        return []

class DataCollector:
    def __init__(self):
        self.football_collector = FootballCollector()
        self.odds_collector = OddsCollector()
    
    def collect_live_data(self):
        return []
    
    def collect_historical_data(self, date):
        return []
    
    def merge_match_odds_data(self, match_data, odds_data):
        return []
    
    def validate_data(self, data):
        return True
    
    def clean_data(self, data):
        return data
    
    def save_data(self, data, file_path):
        pass
    
    def load_data(self, file_path):
        return []

class TestFootballCollector:
    """Testes para FootballCollector"""
    
    def test_init(self):
        """Testa inicialização do FootballCollector"""
        collector = FootballCollector()
        assert collector.api_key is not None
        assert collector.base_url == "https://v3.football.api-sports.io"
        assert collector.headers is not None
    
    @patch('requests.get')
    def test_get_live_matches(self, mock_get, mock_api_response):
        """Testa obtenção de partidas ao vivo"""
        collector = FootballCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        matches = collector.get_live_matches()
        assert isinstance(matches, list)
        assert len(matches) > 0
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_fixtures_by_date(self, mock_get, mock_api_response):
        """Testa obtenção de partidas por data"""
        collector = FootballCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        date = datetime.now().strftime('%Y-%m-%d')
        matches = collector.get_fixtures_by_date(date)
        assert isinstance(matches, list)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_team_statistics(self, mock_get):
        """Testa obtenção de estatísticas do time"""
        collector = FootballCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            "get": "teams/statistics",
            "parameters": {"team": "50", "season": "2024", "league": "39"},
            "errors": [],
            "results": 1,
            "paging": {"current": 1, "total": 1},
            "response": {
                "league": {"id": 39, "name": "Premier League"},
                "team": {"id": 50, "name": "Manchester City"},
                "form": "WWLWD",
                "fixtures": {
                    "played": {"home": 10, "away": 10, "total": 20},
                    "wins": {"home": 8, "away": 6, "total": 14},
                    "draws": {"home": 1, "away": 2, "total": 3},
                    "loses": {"home": 1, "away": 2, "total": 3}
                },
                "goals": {
                    "for": {"total": {"home": 25, "away": 20, "total": 45}},
                    "against": {"total": {"home": 8, "away": 12, "total": 20}}
                }
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        stats = collector.get_team_statistics(50, 39, 2024)
        assert isinstance(stats, dict)
        assert 'team' in stats
        assert 'form' in stats
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_head_to_head(self, mock_get):
        """Testa obtenção de dados head-to-head"""
        collector = FootballCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            "get": "fixtures/headtohead",
            "parameters": {"h2h": "50-33"},
            "errors": [],
            "results": 5,
            "paging": {"current": 1, "total": 1},
            "response": [
                {
                    "fixture": {"id": 12345, "date": "2024-01-01T15:00:00Z"},
                    "teams": {
                        "home": {"id": 50, "name": "Manchester City"},
                        "away": {"id": 33, "name": "Manchester United"}
                    },
                    "goals": {"home": 2, "away": 1}
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        h2h = collector.get_head_to_head(50, 33)
        assert isinstance(h2h, list)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Testa tratamento de erros da API"""
        collector = FootballCollector()
        
        # Mock de erro da API
        mock_response = Mock()
        mock_response.json.return_value = {
            "get": "fixtures",
            "parameters": {},
            "errors": ["API key not valid"],
            "results": 0,
            "paging": {"current": 1, "total": 1},
            "response": []
        }
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        matches = collector.get_live_matches()
        assert matches == []
    
    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        """Testa rate limiting"""
        collector = FootballCollector()
        
        # Mock de rate limiting
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            collector.get_live_matches()

class TestOddsCollector:
    """Testes para OddsCollector"""
    
    def test_init(self):
        """Testa inicialização do OddsCollector"""
        collector = OddsCollector()
        assert collector.api_key is not None
        assert collector.base_url == "https://api.the-odds-api.com/v4"
    
    @patch('requests.get')
    def test_get_odds(self, mock_get, mock_odds_response):
        """Testa obtenção de odds"""
        collector = OddsCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_odds_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        odds = collector.get_odds('soccer_epl')
        assert isinstance(odds, list)
        assert len(odds) > 0
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_odds_by_sport(self, mock_get, mock_odds_response):
        """Testa obtenção de odds por esporte"""
        collector = OddsCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_odds_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        odds = collector.get_odds_by_sport('soccer_epl', 'h2h')
        assert isinstance(odds, list)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_odds_by_event(self, mock_get, mock_odds_response):
        """Testa obtenção de odds por evento"""
        collector = OddsCollector()
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_odds_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        odds = collector.get_odds_by_event('12345')
        assert isinstance(odds, list)
        mock_get.assert_called_once()
    
    def test_parse_odds_data(self, mock_odds_response):
        """Testa parsing de dados de odds"""
        collector = OddsCollector()
        
        parsed_odds = collector.parse_odds_data(mock_odds_response['data'])
        assert isinstance(parsed_odds, list)
        assert len(parsed_odds) > 0
        
        # Verificar estrutura dos dados parseados
        for odd in parsed_odds:
            assert 'event_id' in odd
            assert 'home_team' in odd
            assert 'away_team' in odd
            assert 'home_odds' in odd
            assert 'draw_odds' in odd
            assert 'away_odds' in odd

class TestDataCollector:
    """Testes para DataCollector"""
    
    def test_init(self):
        """Testa inicialização do DataCollector"""
        collector = DataCollector()
        assert collector.football_collector is not None
        assert collector.odds_collector is not None
    
    @patch('coletores.football_collector.FootballCollector.get_live_matches')
    @patch('coletores.odds_collector.OddsCollector.get_odds')
    def test_collect_live_data(self, mock_odds, mock_matches, mock_api_response, mock_odds_response):
        """Testa coleta de dados ao vivo"""
        collector = DataCollector()
        
        # Mock das respostas
        mock_matches.return_value = mock_api_response['response']
        mock_odds.return_value = mock_odds_response['data']
        
        data = collector.collect_live_data()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verificar estrutura dos dados coletados
        for match in data:
            assert 'fixture_id' in match
            assert 'home_team' in match
            assert 'away_team' in match
            assert 'odds' in match
    
    @patch('coletores.football_collector.FootballCollector.get_fixtures_by_date')
    def test_collect_historical_data(self, mock_fixtures, mock_api_response):
        """Testa coleta de dados históricos"""
        collector = DataCollector()
        
        # Mock da resposta
        mock_fixtures.return_value = mock_api_response['response']
        
        date = datetime.now().strftime('%Y-%m-%d')
        data = collector.collect_historical_data(date)
        assert isinstance(data, list)
        mock_fixtures.assert_called_once_with(date)
    
    def test_merge_match_odds_data(self, sample_match_data, mock_odds_response):
        """Testa merge de dados de partida e odds"""
        collector = DataCollector()
        
        match_data = [sample_match_data]
        odds_data = mock_odds_response['data']
        
        merged_data = collector.merge_match_odds_data(match_data, odds_data)
        assert isinstance(merged_data, list)
        assert len(merged_data) > 0
        
        # Verificar se os dados foram mergeados corretamente
        for match in merged_data:
            assert 'fixture_id' in match
            assert 'odds' in match
    
    def test_validate_data(self, sample_match_data):
        """Testa validação de dados"""
        collector = DataCollector()
        
        # Dados válidos
        valid_data = [sample_match_data]
        assert collector.validate_data(valid_data) == True
        
        # Dados inválidos
        invalid_data = [{'invalid': 'data'}]
        assert collector.validate_data(invalid_data) == False
    
    def test_clean_data(self, sample_match_data):
        """Testa limpeza de dados"""
        collector = DataCollector()
        
        # Dados com valores nulos
        dirty_data = [
            {**sample_match_data, 'home_score': None},
            {**sample_match_data, 'away_score': None}
        ]
        
        clean_data = collector.clean_data(dirty_data)
        assert isinstance(clean_data, list)
        
        # Verificar se valores nulos foram tratados
        for match in clean_data:
            assert match['home_score'] is not None
            assert match['away_score'] is not None

class TestCollectorIntegration:
    """Testes de integração para coletores"""
    
    @patch('requests.get')
    def test_full_data_collection_flow(self, mock_get, mock_api_response, mock_odds_response):
        """Testa fluxo completo de coleta de dados"""
        collector = DataCollector()
        
        # Mock das respostas
        mock_response = Mock()
        mock_response.json.side_effect = [mock_api_response, mock_odds_response]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Coletar dados
        data = collector.collect_live_data()
        
        # Verificar se os dados foram coletados e processados
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verificar estrutura dos dados
        for match in data:
            assert 'fixture_id' in match
            assert 'home_team' in match
            assert 'away_team' in match
            assert 'date' in match
            assert 'odds' in match
    
    def test_error_recovery(self):
        """Testa recuperação de erros"""
        collector = DataCollector()
        
        # Simular erro na coleta
        with patch.object(collector.football_collector, 'get_live_matches', side_effect=Exception("API Error")):
            data = collector.collect_live_data()
            assert data == []  # Deve retornar lista vazia em caso de erro
    
    def test_data_persistence(self, temp_dir, sample_match_data):
        """Testa persistência de dados"""
        collector = DataCollector()
        
        # Mock de dados
        data = [sample_match_data]
        
        # Salvar dados
        file_path = os.path.join(temp_dir, 'test_data.json')
        collector.save_data(data, file_path)
        
        # Verificar se arquivo foi criado
        assert os.path.exists(file_path)
        
        # Carregar dados
        loaded_data = collector.load_data(file_path)
        assert loaded_data == data

if __name__ == "__main__":
    pytest.main([__file__])
