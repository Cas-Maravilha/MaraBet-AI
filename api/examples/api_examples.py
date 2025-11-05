#!/usr/bin/env python3
"""
Exemplos de API Documentados para o MaraBet AI
Exemplos práticos de uso da API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_documentation import api_docs, api_endpoint, api_parameter, api_response, api_request_body
from typing import Dict, List, Any
import json

class APIExamples:
    """Exemplos de uso da API MaraBet AI"""
    
    def __init__(self):
        """Inicializa exemplos da API"""
        self.health_check = None
        self.get_match_predictions = None
        self.list_matches = None
        self.get_roi_analysis = None
        self.create_bet = None
        self.setup_examples()
    
    def setup_examples(self):
        """Configura exemplos de uso"""
        
        # Exemplo 1: Obter predições
        @api_docs.document_endpoint(
            summary="Obter predições de partida",
            description="Retorna predições detalhadas de uma partida específica",
            tags=["Predictions", "Matches"],
            parameters=[
                api_parameter("match_id", "string", "ID único da partida", True, "39_12345"),
                api_parameter("include_odds", "boolean", "Incluir odds na resposta", False, True),
                api_parameter("include_statistics", "boolean", "Incluir estatísticas das equipes", False, False)
            ],
            responses={
                "200": api_response("200", "Predições encontradas com sucesso", "PredictionResponse", {
                    "match_id": "39_12345",
                    "home_team": "Manchester City",
                    "away_team": "Liverpool",
                    "predictions": {
                        "home_win": 0.45,
                        "draw": 0.30,
                        "away_win": 0.25
                    },
                    "confidence": 0.85,
                    "expected_value": 0.12,
                    "odds": {
                        "home_win": 2.20,
                        "draw": 3.40,
                        "away_win": 3.10
                    },
                    "created_at": "2024-01-15T10:30:00Z"
                }),
                "404": api_response("404", "Partida não encontrada", "ErrorResponse", {
                    "error": {
                        "code": "match_not_found",
                        "message": "Partida com ID 39_12345 não foi encontrada"
                    }
                }),
                "400": api_response("400", "Parâmetros inválidos", "ErrorResponse", {
                    "error": {
                        "code": "invalid_parameters",
                        "message": "Match ID deve ser uma string válida"
                    }
                })
            }
        )
        def get_match_predictions_func(match_id: str, include_odds: bool = False, 
                                 include_statistics: bool = False) -> Dict[str, Any]:
            """
            Obtém predições detalhadas de uma partida
            
            Args:
                match_id: ID único da partida
                include_odds: Se deve incluir odds na resposta
                include_statistics: Se deve incluir estatísticas das equipes
                
            Returns:
                Dict com predições e informações da partida
            """
            # Simulação de dados
            return {
                "match_id": match_id,
                "home_team": "Manchester City",
                "away_team": "Liverpool",
                "predictions": {
                    "home_win": 0.45,
                    "draw": 0.30,
                    "away_win": 0.25
                },
                "confidence": 0.85,
                "expected_value": 0.12,
                "odds": {
                    "home_win": 2.20,
                    "draw": 3.40,
                    "away_win": 3.10
                } if include_odds else None,
                "statistics": {
                    "home_team": {
                        "goals_per_game": 2.1,
                        "conceded_per_game": 0.8,
                        "form": "WWLWW"
                    },
                    "away_team": {
                        "goals_per_game": 1.8,
                        "conceded_per_game": 1.2,
                        "form": "LWWLW"
                    }
                } if include_statistics else None,
                "created_at": "2024-01-15T10:30:00Z"
            }
        
        # Atribuir função à instância
        self.get_match_predictions = get_match_predictions_func
        
        # Exemplo 2: Listar partidas
        @api_docs.document_endpoint(
            summary="Listar partidas",
            description="Lista partidas com filtros e paginação",
            tags=["Matches"],
            parameters=[
                api_parameter("league_id", "integer", "ID da liga", False, 39),
                api_parameter("date", "string", "Data das partidas (YYYY-MM-DD)", False, "2024-01-15"),
                api_parameter("status", "string", "Status da partida", False, "scheduled"),
                api_parameter("page", "integer", "Número da página", False, 1),
                api_parameter("per_page", "integer", "Itens por página", False, 20)
            ],
            responses={
                "200": api_response("200", "Lista de partidas", "MatchesListResponse", {
                    "items": [
                        {
                            "id": "39_12345",
                            "home_team": "Manchester City",
                            "away_team": "Liverpool",
                            "league_id": 39,
                            "match_date": "2024-01-15T15:30:00Z",
                            "status": "scheduled"
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "total": 50,
                        "pages": 3
                    }
                })
            }
        )
        def list_matches_func(league_id: int = None, date: str = None, 
                        status: str = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
            """
            Lista partidas com filtros e paginação
            
            Args:
                league_id: ID da liga para filtrar
                date: Data das partidas (YYYY-MM-DD)
                status: Status da partida (scheduled, live, finished)
                page: Número da página
                per_page: Itens por página
                
            Returns:
                Dict com lista de partidas e metadados de paginação
            """
            # Simulação de dados
            matches = [
                {
                    "id": "39_12345",
                    "home_team": "Manchester City",
                    "away_team": "Liverpool",
                    "league_id": 39,
                    "match_date": "2024-01-15T15:30:00Z",
                    "status": "scheduled"
                },
                {
                    "id": "39_12346",
                    "home_team": "Arsenal",
                    "away_team": "Chelsea",
                    "league_id": 39,
                    "match_date": "2024-01-15T18:00:00Z",
                    "status": "scheduled"
                }
            ]
            
            return {
                "items": matches,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": 50,
                    "pages": 3
                }
            }
        
        # Atribuir função à instância
        self.list_matches = list_matches_func
        
        # Exemplo 3: Análise de ROI
        @api_docs.document_endpoint(
            summary="Análise de ROI",
            description="Obtém análise detalhada de ROI para um período",
            tags=["Analysis", "ROI"],
            parameters=[
                api_parameter("days", "integer", "Número de dias para análise", False, 30),
                api_parameter("bet_type", "string", "Tipo de aposta para filtrar", False, "home_win"),
                api_parameter("league_id", "integer", "ID da liga para filtrar", False, 39)
            ],
            responses={
                "200": api_response("200", "Análise de ROI", "ROIAnalysisResponse", {
                    "period_days": 30,
                    "overall": {
                        "total_bets": 50,
                        "total_stake": 5000.0,
                        "total_profit": 750.0,
                        "roi": 0.15
                    },
                    "by_bet_type": [
                        {
                            "bet_type": "home_win",
                            "total_bets": 20,
                            "total_stake": 2000.0,
                            "total_profit": 400.0,
                            "roi": 0.20,
                            "win_rate": 0.65
                        }
                    ]
                })
            }
        )
        def get_roi_analysis_func(days: int = 30, bet_type: str = None, 
                           league_id: int = None) -> Dict[str, Any]:
            """
            Obtém análise detalhada de ROI
            
            Args:
                days: Número de dias para análise
                bet_type: Tipo de aposta para filtrar
                league_id: ID da liga para filtrar
                
            Returns:
                Dict com análise de ROI detalhada
            """
            # Simulação de dados
            return {
                "period_days": days,
                "overall": {
                    "total_bets": 50,
                    "total_stake": 5000.0,
                    "total_profit": 750.0,
                    "roi": 0.15
                },
                "by_bet_type": [
                    {
                        "bet_type": "home_win",
                        "total_bets": 20,
                        "total_stake": 2000.0,
                        "total_profit": 400.0,
                        "roi": 0.20,
                        "win_rate": 0.65
                    },
                    {
                        "bet_type": "draw",
                        "total_bets": 15,
                        "total_stake": 1500.0,
                        "total_profit": 200.0,
                        "roi": 0.13,
                        "win_rate": 0.40
                    }
                ]
            }
        
        # Atribuir função à instância
        self.get_roi_analysis = get_roi_analysis_func
        
        # Exemplo 4: Criar aposta
        @api_docs.document_endpoint(
            summary="Criar aposta",
            description="Cria uma nova aposta para uma partida",
            tags=["Bets"],
            parameters=[],
            request_body=api_request_body("BetRequest", "Dados da aposta", {
                "match_id": "39_12345",
                "bet_type": "home_win",
                "stake": 100.0,
                "odds": 2.20
            }),
            responses={
                "201": api_response("201", "Aposta criada com sucesso", "BetResponse", {
                    "id": "bet_123",
                    "match_id": "39_12345",
                    "bet_type": "home_win",
                    "stake": 100.0,
                    "odds": 2.20,
                    "potential_profit": 120.0,
                    "status": "pending",
                    "created_at": "2024-01-15T10:30:00Z"
                }),
                "400": api_response("400", "Dados inválidos", "ErrorResponse", {
                    "error": {
                        "code": "invalid_bet_data",
                        "message": "Stake deve ser maior que zero"
                    }
                })
            },
            security=[{"ApiKeyAuth": []}]
        )
        def create_bet_func(bet_data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Cria uma nova aposta
            
            Args:
                bet_data: Dados da aposta (match_id, bet_type, stake, odds)
                
            Returns:
                Dict com dados da aposta criada
            """
            # Simulação de criação de aposta
            return {
                "id": "bet_123",
                "match_id": bet_data["match_id"],
                "bet_type": bet_data["bet_type"],
                "stake": bet_data["stake"],
                "odds": bet_data["odds"],
                "potential_profit": bet_data["stake"] * (bet_data["odds"] - 1),
                "status": "pending",
                "created_at": "2024-01-15T10:30:00Z"
            }
        
        # Atribuir função à instância
        self.create_bet = create_bet_func
        
        # Exemplo 5: Health Check
        @api_docs.document_endpoint(
            summary="Health Check",
            description="Verifica se a API está funcionando corretamente",
            tags=["Monitoring", "Health"],
            parameters=[],
            responses={
                "200": api_response("200", "API funcionando", "HealthResponse", {
                    "status": "healthy",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "version": "1.0.0",
                    "uptime": 3600
                })
            }
        )
        def health_check_func() -> Dict[str, Any]:
            """
            Verifica status da API
            
            Returns:
                Dict com status da API
            """
            return {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "uptime": 3600
            }
        
        # Atribuir função à instância
        self.health_check = health_check_func
    
    def get_examples_summary(self) -> Dict[str, Any]:
        """Obtém resumo dos exemplos"""
        endpoints = api_docs.get_all_endpoints()
        
        return {
            "total_endpoints": len(endpoints),
            "endpoints_by_tag": self._group_by_tag(endpoints),
            "endpoints_list": [
                {
                    "function": doc["function"],
                    "summary": doc["summary"],
                    "tags": doc["tags"]
                }
                for doc in endpoints.values()
            ]
        }
    
    def _group_by_tag(self, endpoints: Dict) -> Dict[str, int]:
        """Agrupa endpoints por tag"""
        tag_counts = {}
        
        for doc in endpoints.values():
            for tag in doc["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return tag_counts
    
    def generate_curl_examples(self) -> Dict[str, str]:
        """Gera exemplos de curl para os endpoints"""
        curl_examples = {}
        
        # Exemplo 1: Health Check
        curl_examples["health_check"] = """
curl -X GET "http://localhost:5000/api/health" \\
  -H "Accept: application/json"
        """.strip()
        
        # Exemplo 2: Obter predições
        curl_examples["get_predictions"] = """
curl -X GET "http://localhost:5000/api/predictions?match_id=39_12345&include_odds=true" \\
  -H "Accept: application/json" \\
  -H "X-API-Key: your-api-key"
        """.strip()
        
        # Exemplo 3: Listar partidas
        curl_examples["list_matches"] = """
curl -X GET "http://localhost:5000/api/matches?league_id=39&status=scheduled&page=1&per_page=20" \\
  -H "Accept: application/json"
        """.strip()
        
        # Exemplo 4: Análise de ROI
        curl_examples["roi_analysis"] = """
curl -X GET "http://localhost:5000/api/analysis/roi?days=30&bet_type=home_win" \\
  -H "Accept: application/json" \\
  -H "X-API-Key: your-api-key"
        """.strip()
        
        # Exemplo 5: Criar aposta
        curl_examples["create_bet"] = """
curl -X POST "http://localhost:5000/api/bets" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "match_id": "39_12345",
    "bet_type": "home_win",
    "stake": 100.0,
    "odds": 2.20
  }'
        """.strip()
        
        return curl_examples
    
    def generate_python_examples(self) -> Dict[str, str]:
        """Gera exemplos em Python para os endpoints"""
        python_examples = {}
        
        # Exemplo 1: Health Check
        python_examples["health_check"] = """
import requests

response = requests.get("http://localhost:5000/api/health")
print(response.json())
        """.strip()
        
        # Exemplo 2: Obter predições
        python_examples["get_predictions"] = """
import requests

headers = {
    "Accept": "application/json",
    "X-API-Key": "your-api-key"
}

params = {
    "match_id": "39_12345",
    "include_odds": True
}

response = requests.get("http://localhost:5000/api/predictions", 
                       headers=headers, params=params)
print(response.json())
        """.strip()
        
        # Exemplo 3: Criar aposta
        python_examples["create_bet"] = """
import requests

headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key"
}

data = {
    "match_id": "39_12345",
    "bet_type": "home_win",
    "stake": 100.0,
    "odds": 2.20
}

response = requests.post("http://localhost:5000/api/bets", 
                        headers=headers, json=data)
print(response.json())
        """.strip()
        
        return python_examples

# Instância global
api_examples = APIExamples()

if __name__ == "__main__":
    # Teste dos exemplos da API
    print("🧪 TESTANDO EXEMPLOS DA API")
    print("=" * 40)
    
    # Testar funções documentadas
    print("1. Health Check:")
    health = api_examples.health_check()
    print(f"   Status: {health['status']}")
    
    print("\n2. Obter Predições:")
    predictions = api_examples.get_match_predictions("39_12345", True, True)
    print(f"   Confiança: {predictions['confidence']}")
    print(f"   Predição: {predictions['predictions']['home_win']:.1%}")
    
    print("\n3. Listar Partidas:")
    matches = api_examples.list_matches(league_id=39, page=1, per_page=5)
    print(f"   Total de partidas: {len(matches['items'])}")
    
    print("\n4. Análise de ROI:")
    roi = api_examples.get_roi_analysis(days=30)
    print(f"   ROI geral: {roi['overall']['roi']:.1%}")
    
    print("\n5. Criar Aposta:")
    bet_data = {
        "match_id": "39_12345",
        "bet_type": "home_win",
        "stake": 100.0,
        "odds": 2.20
    }
    bet = api_examples.create_bet(bet_data)
    print(f"   ID da aposta: {bet['id']}")
    print(f"   Lucro potencial: R$ {bet['potential_profit']:.2f}")
    
    # Resumo dos exemplos
    summary = api_examples.get_examples_summary()
    print(f"\nResumo dos Exemplos:")
    print(f"  Total de endpoints: {summary['total_endpoints']}")
    print(f"  Endpoints por tag: {summary['endpoints_by_tag']}")
    
    # Exemplos de curl
    curl_examples = api_examples.generate_curl_examples()
    print(f"\nExemplos de cURL: {len(curl_examples)}")
    
    # Exemplos em Python
    python_examples = api_examples.generate_python_examples()
    print(f"Exemplos em Python: {len(python_examples)}")
    
    print("\n🎉 TESTES DE EXEMPLOS CONCLUÍDOS!")
