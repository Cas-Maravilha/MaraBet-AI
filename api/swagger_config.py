#!/usr/bin/env python3
"""
Configuração do Swagger/OpenAPI para o MaraBet AI
Documentação interativa da API
"""

from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os
from typing import Dict, Any

class SwaggerConfig:
    """Configuração do Swagger para documentação da API"""
    
    def __init__(self, app: Flask = None):
        """Inicializa configuração do Swagger"""
        self.app = app
        self.swagger_url = '/api/docs'
        self.api_url = '/static/swagger.json'
        self.swagger_config = {
            'app_name': "MaraBet AI API",
            'validatorUrl': None,
            'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],
            'docExpansion': 'list',
            'apisSorter': 'alpha',
            'operationsSorter': 'alpha',
            'defaultModelsExpandDepth': 3,
            'defaultModelExpandDepth': 3,
            'showRequestHeaders': True,
            'showCommonExtensions': True,
            'tryItOutEnabled': True
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializa Swagger na aplicação Flask"""
        # Configurar Swagger UI
        swagger_ui_blueprint = get_swaggerui_blueprint(
            self.swagger_url,
            self.api_url,
            config=self.swagger_config
        )
        
        app.register_blueprint(swagger_ui_blueprint, url_prefix=self.swagger_url)
        
        # Rota para servir o arquivo swagger.json
        @app.route(self.api_url)
        def swagger_spec():
            return jsonify(self.get_openapi_spec())
        
        # Rota de redirecionamento para docs
        @app.route('/docs')
        def redirect_to_docs():
            from flask import redirect
            return redirect(self.swagger_url)
        
        # Rota de redirecionamento para api
        @app.route('/api')
        def redirect_to_api():
            from flask import redirect
            return redirect(self.swagger_url)
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Gera especificação OpenAPI 3.0"""
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "MaraBet AI API",
                "description": "API completa para análise preditiva de apostas esportivas com machine learning",
                "version": "1.0.0",
                "contact": {
                    "name": "Equipe MaraBet AI",
                    "email": "suporte@marabet.ai",
                    "url": "https://marabet.ai"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:5000",
                    "description": "Servidor de desenvolvimento"
                },
                {
                    "url": "https://api.marabet.ai",
                    "description": "Servidor de produção"
                }
            ],
            "tags": [
                {
                    "name": "Predictions",
                    "description": "Endpoints para predições de partidas"
                },
                {
                    "name": "Odds",
                    "description": "Endpoints para consulta de odds"
                },
                {
                    "name": "Analysis",
                    "description": "Endpoints para análise de dados"
                },
                {
                    "name": "Matches",
                    "description": "Endpoints para dados de partidas"
                },
                {
                    "name": "Teams",
                    "description": "Endpoints para dados de times"
                },
                {
                    "name": "Leagues",
                    "description": "Endpoints para dados de ligas"
                },
                {
                    "name": "Bets",
                    "description": "Endpoints para gestão de apostas"
                },
                {
                    "name": "Monitoring",
                    "description": "Endpoints para monitoramento do sistema"
                }
            ],
            "paths": self._get_api_paths(),
            "components": self._get_components(),
            "security": [
                {
                    "ApiKeyAuth": []
                }
            ]
        }
    
    def _get_api_paths(self) -> Dict[str, Any]:
        """Define todos os endpoints da API"""
        return {
            "/api/health": {
                "get": {
                    "tags": ["Monitoring"],
                    "summary": "Health Check",
                    "description": "Verifica se a API está funcionando",
                    "responses": {
                        "200": {
                            "description": "API funcionando",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/predictions": {
                "get": {
                    "tags": ["Predictions"],
                    "summary": "Listar Predições",
                    "description": "Lista predições de partidas com paginação",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Número da página",
                            "required": False,
                            "schema": {"type": "integer", "default": 1}
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Itens por página",
                            "required": False,
                            "schema": {"type": "integer", "default": 20}
                        },
                        {
                            "name": "league_id",
                            "in": "query",
                            "description": "ID da liga para filtrar",
                            "required": False,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de predições",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PredictionsListResponse"
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Predictions"],
                    "summary": "Criar Predição",
                    "description": "Cria uma nova predição para uma partida",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PredictionRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Predição criada com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PredictionResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Dados inválidos",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/predictions/{match_id}": {
                "get": {
                    "tags": ["Predictions"],
                    "summary": "Obter Predição",
                    "description": "Obtém predição específica de uma partida",
                    "parameters": [
                        {
                            "name": "match_id",
                            "in": "path",
                            "required": True,
                            "description": "ID da partida",
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Predição encontrada",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PredictionResponse"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Predição não encontrada",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/odds": {
                "get": {
                    "tags": ["Odds"],
                    "summary": "Listar Odds",
                    "description": "Lista odds de partidas com filtros",
                    "parameters": [
                        {
                            "name": "match_id",
                            "in": "query",
                            "description": "ID da partida",
                            "required": False,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "bookmaker",
                            "in": "query",
                            "description": "Nome do bookmaker",
                            "required": False,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de odds",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OddsListResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/analysis/roi": {
                "get": {
                    "tags": ["Analysis"],
                    "summary": "Análise de ROI",
                    "description": "Obtém análise de ROI para um período",
                    "parameters": [
                        {
                            "name": "days",
                            "in": "query",
                            "description": "Número de dias para análise",
                            "required": False,
                            "schema": {"type": "integer", "default": 30}
                        },
                        {
                            "name": "bet_type",
                            "in": "query",
                            "description": "Tipo de aposta para filtrar",
                            "required": False,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Análise de ROI",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ROIAnalysisResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/matches": {
                "get": {
                    "tags": ["Matches"],
                    "summary": "Listar Partidas",
                    "description": "Lista partidas com filtros e paginação",
                    "parameters": [
                        {
                            "name": "league_id",
                            "in": "query",
                            "description": "ID da liga",
                            "required": False,
                            "schema": {"type": "integer"}
                        },
                        {
                            "name": "date",
                            "in": "query",
                            "description": "Data das partidas (YYYY-MM-DD)",
                            "required": False,
                            "schema": {"type": "string", "format": "date"}
                        },
                        {
                            "name": "status",
                            "in": "query",
                            "description": "Status da partida",
                            "required": False,
                            "schema": {"type": "string", "enum": ["scheduled", "live", "finished"]}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de partidas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/MatchesListResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/teams": {
                "get": {
                    "tags": ["Teams"],
                    "summary": "Listar Times",
                    "description": "Lista times de uma liga",
                    "parameters": [
                        {
                            "name": "league_id",
                            "in": "query",
                            "description": "ID da liga",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de times",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TeamsListResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/leagues": {
                "get": {
                    "tags": ["Leagues"],
                    "summary": "Listar Ligas",
                    "description": "Lista ligas disponíveis",
                    "responses": {
                        "200": {
                            "description": "Lista de ligas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LeaguesListResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/bets": {
                "get": {
                    "tags": ["Bets"],
                    "summary": "Listar Apostas",
                    "description": "Lista apostas do usuário",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Lista de apostas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/BetsListResponse"
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Bets"],
                    "summary": "Criar Aposta",
                    "description": "Cria uma nova aposta",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/BetRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Aposta criada com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/BetResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _get_components(self) -> Dict[str, Any]:
        """Define componentes reutilizáveis (schemas, security, etc.)"""
        return {
            "schemas": self._get_schemas(),
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Chave de API para autenticação"
                }
            }
        }
    
    def _get_schemas(self) -> Dict[str, Any]:
        """Define schemas de dados"""
        return {
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "version": {"type": "string", "example": "1.0.0"},
                    "uptime": {"type": "number", "example": 3600}
                }
            },
            "PredictionRequest": {
                "type": "object",
                "required": ["match_id", "home_team", "away_team", "league_id"],
                "properties": {
                    "match_id": {"type": "string", "example": "39_12345"},
                    "home_team": {"type": "string", "example": "Manchester City"},
                    "away_team": {"type": "string", "example": "Liverpool"},
                    "league_id": {"type": "integer", "example": 39},
                    "match_date": {"type": "string", "format": "date", "example": "2024-01-15"}
                }
            },
            "PredictionResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "pred_123"},
                    "match_id": {"type": "string", "example": "39_12345"},
                    "home_team": {"type": "string", "example": "Manchester City"},
                    "away_team": {"type": "string", "example": "Liverpool"},
                    "predictions": {
                        "type": "object",
                        "properties": {
                            "home_win": {"type": "number", "example": 0.45},
                            "draw": {"type": "number", "example": 0.30},
                            "away_win": {"type": "number", "example": 0.25}
                        }
                    },
                    "confidence": {"type": "number", "example": 0.85},
                    "expected_value": {"type": "number", "example": 0.12},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "PredictionsListResponse": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/PredictionResponse"}
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "example": 1},
                            "per_page": {"type": "integer", "example": 20},
                            "total": {"type": "integer", "example": 100},
                            "pages": {"type": "integer", "example": 5}
                        }
                    }
                }
            },
            "OddsListResponse": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "match_id": {"type": "string", "example": "39_12345"},
                                "bookmaker": {"type": "string", "example": "Bet365"},
                                "odds": {
                                    "type": "object",
                                    "properties": {
                                        "home_win": {"type": "number", "example": 2.20},
                                        "draw": {"type": "number", "example": 3.40},
                                        "away_win": {"type": "number", "example": 3.10}
                                    }
                                },
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            },
            "ROIAnalysisResponse": {
                "type": "object",
                "properties": {
                    "period_days": {"type": "integer", "example": 30},
                    "overall": {
                        "type": "object",
                        "properties": {
                            "total_bets": {"type": "integer", "example": 50},
                            "total_stake": {"type": "number", "example": 5000.0},
                            "total_profit": {"type": "number", "example": 750.0},
                            "roi": {"type": "number", "example": 0.15}
                        }
                    },
                    "by_bet_type": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "bet_type": {"type": "string", "example": "home_win"},
                                "total_bets": {"type": "integer", "example": 20},
                                "roi": {"type": "number", "example": 0.18},
                                "win_rate": {"type": "number", "example": 0.65}
                            }
                        }
                    }
                }
            },
            "MatchesListResponse": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "example": "39_12345"},
                                "home_team": {"type": "string", "example": "Manchester City"},
                                "away_team": {"type": "string", "example": "Liverpool"},
                                "league_id": {"type": "integer", "example": 39},
                                "match_date": {"type": "string", "format": "date-time"},
                                "status": {"type": "string", "example": "scheduled"}
                            }
                        }
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "example": 1},
                            "per_page": {"type": "integer", "example": 20},
                            "total": {"type": "integer", "example": 100}
                        }
                    }
                }
            },
            "TeamsListResponse": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "name": {"type": "string", "example": "Manchester City"},
                                "league_id": {"type": "integer", "example": 39},
                                "logo": {"type": "string", "example": "https://example.com/logo.png"}
                            }
                        }
                    }
                }
            },
            "LeaguesListResponse": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 39},
                                "name": {"type": "string", "example": "Premier League"},
                                "country": {"type": "string", "example": "England"},
                                "logo": {"type": "string", "example": "https://example.com/logo.png"}
                            }
                        }
                    }
                }
            },
            "BetRequest": {
                "type": "object",
                "required": ["match_id", "bet_type", "stake", "odds"],
                "properties": {
                    "match_id": {"type": "string", "example": "39_12345"},
                    "bet_type": {"type": "string", "example": "home_win"},
                    "stake": {"type": "number", "example": 100.0},
                    "odds": {"type": "number", "example": 2.20}
                }
            },
            "BetResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "bet_123"},
                    "match_id": {"type": "string", "example": "39_12345"},
                    "bet_type": {"type": "string", "example": "home_win"},
                    "stake": {"type": "number", "example": 100.0},
                    "odds": {"type": "number", "example": 2.20},
                    "potential_profit": {"type": "number", "example": 120.0},
                    "status": {"type": "string", "example": "pending"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "BetsListResponse": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/BetResponse"}
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "example": 1},
                            "per_page": {"type": "integer", "example": 20},
                            "total": {"type": "integer", "example": 50}
                        }
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "validation_error"},
                            "message": {"type": "string", "example": "Dados inválidos"},
                            "details": {"type": "string", "example": "Campo obrigatório não fornecido"}
                        }
                    },
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        }

# Instância global
swagger_config = SwaggerConfig()

if __name__ == "__main__":
    # Teste da configuração do Swagger
    print("🧪 TESTANDO CONFIGURAÇÃO DO SWAGGER")
    print("=" * 40)
    
    # Gerar especificação OpenAPI
    spec = swagger_config.get_openapi_spec()
    
    print(f"OpenAPI Version: {spec['openapi']}")
    print(f"API Title: {spec['info']['title']}")
    print(f"API Version: {spec['info']['version']}")
    print(f"Endpoints: {len(spec['paths'])}")
    print(f"Schemas: {len(spec['components']['schemas'])}")
    print(f"Tags: {len(spec['tags'])}")
    
    # Salvar especificação em arquivo
    with open('static/swagger.json', 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    print(f"\nEspecificação salva em: static/swagger.json")
    print("Acesse a documentação em: http://localhost:5000/api/docs")
    
    print("\n🎉 CONFIGURAÇÃO DO SWAGGER CONCLUÍDA!")
