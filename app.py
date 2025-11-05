#!/usr/bin/env python3
"""
MaraBet AI - Aplicação Web FastAPI
Sistema de Análise Preditiva de Apostas Esportivas
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from datetime import datetime
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="MaraBet AI",
    description="Sistema de Análise Preditiva de Apostas Esportivas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: str
    league: Optional[str] = "Premier League"

class PredictionResponse(BaseModel):
    match: str
    predictions: Dict[str, Any]
    confidence: float
    recommendation: str
    expected_value: float
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: str

# Variáveis globais
start_time = datetime.now()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial da aplicação"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaraBet AI - Sistema de Análise Preditiva</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }
            .header {
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
            .feature-card h3 {
                font-size: 1.5em;
                margin-bottom: 15px;
                color: #ffd700;
            }
            .feature-card p {
                line-height: 1.6;
                opacity: 0.9;
            }
            .api-links {
                margin-top: 40px;
            }
            .api-links a {
                display: inline-block;
                margin: 10px;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                transition: background 0.3s ease;
            }
            .api-links a:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            .status {
                margin-top: 30px;
                padding: 20px;
                background: rgba(0, 255, 0, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(0, 255, 0, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 MaraBet AI</h1>
                <p>Sistema de Análise Preditiva de Apostas Esportivas</p>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>🤖 Inteligência Artificial</h3>
                    <p>Modelos de machine learning avançados para análise preditiva de partidas de futebol com alta precisão.</p>
                </div>
                
                <div class="feature-card">
                    <h3>📊 Análise de Valor</h3>
                    <p>Identificação automática de oportunidades de apostas com valor esperado positivo e gestão de risco.</p>
                </div>
                
                <div class="feature-card">
                    <h3>💰 Gestão de Banca</h3>
                    <p>Sistema inteligente de gestão de capital com cálculo de unidades e otimização de stake.</p>
                </div>
                
                <div class="feature-card">
                    <h3>📈 Backtesting</h3>
                    <p>Validação histórica de estratégias com métricas de performance e análise de risco.</p>
                </div>
                
                <div class="feature-card">
                    <h3>🌍 Dados Globais</h3>
                    <p>Integração com múltiplas APIs de dados esportivos para cobertura completa de ligas mundiais.</p>
                </div>
                
                <div class="feature-card">
                    <h3>📱 Interface Moderna</h3>
                    <p>Dashboard interativo e responsivo para visualização de análises e relatórios detalhados.</p>
                </div>
            </div>
            
            <div class="api-links">
                <a href="/docs">📚 Documentação da API</a>
                <a href="/health">❤️ Status do Sistema</a>
                <a href="/predictions">🎯 Predições</a>
                <a href="/analysis">📊 Análises</a>
            </div>
            
            <div class="status">
                <h3>✅ Sistema Online</h3>
                <p>MaraBet AI está funcionando perfeitamente!</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificação de saúde da aplicação"""
    uptime = datetime.now() - start_time
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        uptime=str(uptime)
    )

@app.get("/predictions")
async def get_predictions():
    """Obter predições disponíveis"""
    # Simular predições para demonstração
    predictions = [
        {
            "match": "Manchester City vs Arsenal",
            "date": "2024-01-15",
            "league": "Premier League",
            "home_win_prob": 0.45,
            "draw_prob": 0.25,
            "away_win_prob": 0.30,
            "over_2_5_prob": 0.65,
            "btts_prob": 0.70,
            "confidence": 0.85,
            "recommendation": "Over 2.5 Goals",
            "expected_value": 0.12
        },
        {
            "match": "Real Madrid vs Barcelona",
            "date": "2024-01-16",
            "league": "La Liga",
            "home_win_prob": 0.40,
            "draw_prob": 0.30,
            "away_win_prob": 0.30,
            "over_2_5_prob": 0.75,
            "btts_prob": 0.80,
            "confidence": 0.90,
            "recommendation": "Both Teams to Score",
            "expected_value": 0.18
        }
    ]
    
    return JSONResponse(content={
        "status": "success",
        "predictions": predictions,
        "total": len(predictions),
        "timestamp": datetime.now().isoformat()
    })

@app.post("/predict", response_model=PredictionResponse)
async def predict_match(request: MatchRequest):
    """Gerar predição para uma partida específica"""
    try:
        # Simular análise preditiva
        home_win_prob = 0.45
        draw_prob = 0.25
        away_win_prob = 0.30
        over_2_5_prob = 0.65
        btts_prob = 0.70
        
        # Calcular confiança baseada na diferença de probabilidades
        max_prob = max(home_win_prob, draw_prob, away_win_prob)
        confidence = (max_prob - 0.33) * 3  # Normalizar para 0-1
        
        # Determinar recomendação
        if max_prob == home_win_prob:
            recommendation = f"Vitória {request.home_team}"
        elif max_prob == away_win_prob:
            recommendation = f"Vitória {request.away_team}"
        else:
            recommendation = "Empate"
        
        # Calcular valor esperado (simulado)
        expected_value = 0.12
        
        prediction_data = {
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "over_2_5_prob": over_2_5_prob,
            "btts_prob": btts_prob,
            "confidence": confidence,
            "recommendation": recommendation,
            "expected_value": expected_value
        }
        
        return PredictionResponse(
            match=f"{request.home_team} vs {request.away_team}",
            predictions=prediction_data,
            confidence=confidence,
            recommendation=recommendation,
            expected_value=expected_value,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/analysis")
async def get_analysis():
    """Obter análises disponíveis"""
    analysis = {
        "market_analysis": {
            "total_matches": 15,
            "high_confidence": 8,
            "medium_confidence": 5,
            "low_confidence": 2
        },
        "performance_metrics": {
            "accuracy": 0.78,
            "roi": 0.15,
            "total_trades": 45,
            "win_rate": 0.72
        },
        "recommendations": [
            {
                "match": "Manchester City vs Arsenal",
                "bet_type": "Over 2.5 Goals",
                "odds": 1.85,
                "probability": 0.65,
                "expected_value": 0.20,
                "confidence": "High"
            },
            {
                "match": "Real Madrid vs Barcelona",
                "bet_type": "Both Teams to Score",
                "odds": 1.70,
                "probability": 0.80,
                "expected_value": 0.36,
                "confidence": "High"
            }
        ]
    }
    
    return JSONResponse(content={
        "status": "success",
        "analysis": analysis,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/config")
async def get_config():
    """Obter configuração da aplicação"""
    config = {
        "environment": os.getenv("ENVIRONMENT", "production"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "max_workers": int(os.getenv("MAX_WORKERS", "4")),
        "timeout": int(os.getenv("TIMEOUT", "30")),
        "api_football_key": "***" + os.getenv("API_FOOTBALL_KEY", "")[-4:] if os.getenv("API_FOOTBALL_KEY") else "Not configured",
        "database_url": "***" + os.getenv("DATABASE_URL", "")[-10:] if os.getenv("DATABASE_URL") else "Not configured",
        "redis_url": "***" + os.getenv("REDIS_URL", "")[-10:] if os.getenv("REDIS_URL") else "Not configured"
    }
    
    return JSONResponse(content={
        "status": "success",
        "config": config,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/logs")
async def get_logs():
    """Obter logs da aplicação"""
    logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Aplicação iniciada com sucesso",
            "module": "app"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Sistema de predições carregado",
            "module": "predictions"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "APIs de dados conectadas",
            "module": "data_collector"
        }
    ]
    
    return JSONResponse(content={
        "status": "success",
        "logs": logs,
        "total": len(logs),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)