#!/usr/bin/env python3
"""
Testes de integração para endpoints da API
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import app

class TestAPIEndpoints:
    """Testes de integração para endpoints da API"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para a API"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_check(self, client):
        """Testa endpoint de health check"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_get_matches(self, client):
        """Testa endpoint de obtenção de partidas"""
        with patch('coletores.data_collector.DataCollector.collect_live_data') as mock_collect:
            mock_collect.return_value = [
                {
                    'fixture_id': 12345,
                    'home_team': 'Manchester City',
                    'away_team': 'Manchester United',
                    'date': '2024-01-01T15:00:00Z',
                    'status': 'FT',
                    'home_score': 2,
                    'away_score': 1
                }
            ]
            
            response = client.get('/api/matches')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'matches' in data
            assert len(data['matches']) == 1
            assert data['matches'][0]['fixture_id'] == 12345
    
    def test_get_matches_by_date(self, client):
        """Testa endpoint de obtenção de partidas por data"""
        with patch('coletores.data_collector.DataCollector.collect_historical_data') as mock_collect:
            mock_collect.return_value = [
                {
                    'fixture_id': 12345,
                    'home_team': 'Manchester City',
                    'away_team': 'Manchester United',
                    'date': '2024-01-01T15:00:00Z',
                    'status': 'FT',
                    'home_score': 2,
                    'away_score': 1
                }
            ]
            
            response = client.get('/api/matches/2024-01-01')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'matches' in data
            assert len(data['matches']) == 1
    
    def test_get_predictions(self, client):
        """Testa endpoint de obtenção de predições"""
        with patch('ml.ml_models.MLModelManager.predict') as mock_predict:
            mock_predict.return_value = {
                'match_id': 12345,
                'home_team': 'Manchester City',
                'away_team': 'Manchester United',
                'prediction': 'home_win',
                'confidence': 0.75,
                'expected_value': 0.12,
                'recommended_bet': 'home_win',
                'odds': 1.85,
                'stake_percentage': 0.05
            }
            
            response = client.get('/api/predictions')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'predictions' in data
            assert len(data['predictions']) == 1
            assert data['predictions'][0]['match_id'] == 12345
    
    def test_get_predictions_by_match(self, client):
        """Testa endpoint de obtenção de predições por partida"""
        with patch('ml.ml_models.MLModelManager.predict') as mock_predict:
            mock_predict.return_value = {
                'match_id': 12345,
                'home_team': 'Manchester City',
                'away_team': 'Manchester United',
                'prediction': 'home_win',
                'confidence': 0.75,
                'expected_value': 0.12,
                'recommended_bet': 'home_win',
                'odds': 1.85,
                'stake_percentage': 0.05
            }
            
            response = client.get('/api/predictions/12345')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'prediction' in data
            assert data['prediction']['match_id'] == 12345
    
    def test_get_statistics(self, client):
        """Testa endpoint de obtenção de estatísticas"""
        with patch('coletores.football_collector.FootballCollector.get_team_statistics') as mock_stats:
            mock_stats.return_value = {
                'team': {'id': 50, 'name': 'Manchester City'},
                'form': 'WWLWD',
                'fixtures': {
                    'played': {'home': 10, 'away': 10, 'total': 20},
                    'wins': {'home': 8, 'away': 6, 'total': 14},
                    'draws': {'home': 1, 'away': 2, 'total': 3},
                    'loses': {'home': 1, 'away': 2, 'total': 3}
                },
                'goals': {
                    'for': {'total': {'home': 25, 'away': 20, 'total': 45}},
                    'against': {'total': {'home': 8, 'away': 12, 'total': 20}}
                }
            }
            
            response = client.get('/api/statistics/50')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'statistics' in data
            assert data['statistics']['team']['id'] == 50
    
    def test_get_odds(self, client):
        """Testa endpoint de obtenção de odds"""
        with patch('coletores.odds_collector.OddsCollector.get_odds') as mock_odds:
            mock_odds.return_value = [
                {
                    'event_id': '12345',
                    'home_team': 'Manchester City',
                    'away_team': 'Manchester United',
                    'home_odds': 1.85,
                    'draw_odds': 3.40,
                    'away_odds': 4.20,
                    'bookmaker': 'bet365'
                }
            ]
            
            response = client.get('/api/odds')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'odds' in data
            assert len(data['odds']) == 1
            assert data['odds'][0]['event_id'] == '12345'
    
    def test_get_odds_by_match(self, client):
        """Testa endpoint de obtenção de odds por partida"""
        with patch('coletores.odds_collector.OddsCollector.get_odds_by_event') as mock_odds:
            mock_odds.return_value = [
                {
                    'event_id': '12345',
                    'home_team': 'Manchester City',
                    'away_team': 'Manchester United',
                    'home_odds': 1.85,
                    'draw_odds': 3.40,
                    'away_odds': 4.20,
                    'bookmaker': 'bet365'
                }
            ]
            
            response = client.get('/api/odds/12345')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'odds' in data
            assert len(data['odds']) == 1
            assert data['odds'][0]['event_id'] == '12345'
    
    def test_get_notifications(self, client):
        """Testa endpoint de obtenção de notificações"""
        with patch('notifications.notification_manager.NotificationManager.get_notifications') as mock_notifications:
            mock_notifications.return_value = [
                {
                    'id': 1,
                    'type': 'prediction',
                    'message': 'Nova predição disponível',
                    'data': {'match_id': 12345, 'prediction': 'home_win'},
                    'timestamp': '2024-01-01T15:00:00Z',
                    'sent': True
                }
            ]
            
            response = client.get('/api/notifications')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'notifications' in data
            assert len(data['notifications']) == 1
            assert data['notifications'][0]['id'] == 1
    
    def test_send_notification(self, client):
        """Testa endpoint de envio de notificação"""
        with patch('notifications.notification_manager.NotificationManager.send_notification') as mock_send:
            mock_send.return_value = True
            
            notification_data = {
                'type': 'prediction',
                'message': 'Nova predição disponível',
                'data': {'match_id': 12345, 'prediction': 'home_win'}
            }
            
            response = client.post('/api/notifications', 
                                 data=json.dumps(notification_data),
                                 content_type='application/json')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_get_system_status(self, client):
        """Testa endpoint de status do sistema"""
        with patch('main.PredictionPipeline.get_system_status') as mock_status:
            mock_status.return_value = {
                'status': 'running',
                'last_update': '2024-01-01T15:00:00Z',
                'active_models': 3,
                'total_predictions': 150,
                'success_rate': 0.85
            }
            
            response = client.get('/api/status')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] == 'running'
            assert 'active_models' in data
            assert 'total_predictions' in data
    
    def test_get_metrics(self, client):
        """Testa endpoint de métricas"""
        with patch('main.PredictionPipeline.get_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'accuracy': 0.85,
                'precision': 0.82,
                'recall': 0.88,
                'f1_score': 0.85,
                'auc': 0.90,
                'total_predictions': 150,
                'successful_predictions': 128
            }
            
            response = client.get('/api/metrics')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'metrics' in data
            assert 'accuracy' in data['metrics']
            assert 'precision' in data['metrics']
            assert 'recall' in data['metrics']
            assert 'f1_score' in data['metrics']
    
    def test_error_handling(self, client):
        """Testa tratamento de erros nos endpoints"""
        with patch('coletores.data_collector.DataCollector.collect_live_data', side_effect=Exception("API Error")):
            response = client.get('/api/matches')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'API Error'
    
    def test_authentication(self, client):
        """Testa autenticação nos endpoints"""
        # Endpoint sem autenticação
        response = client.get('/api/matches')
        assert response.status_code == 200
        
        # Endpoint com autenticação (se implementado)
        # response = client.get('/api/admin/status')
        # assert response.status_code == 401
    
    def test_rate_limiting(self, client):
        """Testa rate limiting nos endpoints"""
        # Fazer múltiplas requisições rapidamente
        for _ in range(10):
            response = client.get('/api/matches')
            # Verificar se não há rate limiting implementado
            assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Testa headers CORS"""
        response = client.get('/api/matches')
        assert response.status_code == 200
        
        # Verificar headers CORS (se implementados)
        # assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_content_type(self, client):
        """Testa tipo de conteúdo das respostas"""
        response = client.get('/api/matches')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_response_format(self, client):
        """Testa formato das respostas"""
        with patch('coletores.data_collector.DataCollector.collect_live_data') as mock_collect:
            mock_collect.return_value = []
            
            response = client.get('/api/matches')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert isinstance(data, dict)
            assert 'matches' in data
            assert isinstance(data['matches'], list)
    
    def test_pagination(self, client):
        """Testa paginação nos endpoints"""
        with patch('coletores.data_collector.DataCollector.collect_live_data') as mock_collect:
            # Mock de dados paginados
            mock_collect.return_value = [
                {'fixture_id': i, 'home_team': f'Team {i}', 'away_team': f'Team {i+1}'}
                for i in range(20)
            ]
            
            # Primeira página
            response = client.get('/api/matches?page=1&limit=10')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'matches' in data
            assert 'pagination' in data
            assert data['pagination']['page'] == 1
            assert data['pagination']['limit'] == 10
    
    def test_filtering(self, client):
        """Testa filtros nos endpoints"""
        with patch('coletores.data_collector.DataCollector.collect_live_data') as mock_collect:
            mock_collect.return_value = [
                {
                    'fixture_id': 12345,
                    'home_team': 'Manchester City',
                    'away_team': 'Manchester United',
                    'league_id': 39,
                    'status': 'FT'
                }
            ]
            
            # Filtrar por liga
            response = client.get('/api/matches?league=39')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'matches' in data
    
    def test_sorting(self, client):
        """Testa ordenação nos endpoints"""
        with patch('coletores.data_collector.DataCollector.collect_live_data') as mock_collect:
            mock_collect.return_value = [
                {'fixture_id': 12345, 'date': '2024-01-01T15:00:00Z'},
                {'fixture_id': 12346, 'date': '2024-01-01T17:00:00Z'},
                {'fixture_id': 12347, 'date': '2024-01-01T19:00:00Z'}
            ]
            
            # Ordenar por data
            response = client.get('/api/matches?sort=date&order=asc')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'matches' in data

if __name__ == "__main__":
    pytest.main([__file__])
