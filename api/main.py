from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import List, Optional

from config.settings import settings
from config.logging_config import setup_logging
from storage.database import engine, Base, get_db
from api.routes import router
from services.collector_service import CollectorService
from utils.logger import get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    logger.info("🚀 Iniciando aplicação...")
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Banco de dados inicializado")
    
    # Iniciar serviços
    collector_service = CollectorService()
    app.state.collector = collector_service
    
    logger.info("✅ Aplicação iniciada com sucesso")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    logger.info("✅ Aplicação encerrada")

# Create app
app = FastAPI(
    title="Sports Betting Analysis System",
    description="Sistema de análise preditiva de apostas esportivas",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Include routers
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sports Betting System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                margin: 10px 5px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .btn:hover { background: #2980b9; }
            .status {
                padding: 10px;
                background: #2ecc71;
                color: white;
                border-radius: 5px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Sports Betting Analysis System</h1>
            <div class="status">
                ✅ Sistema Online e Operacional
            </div>
            <p>Sistema de análise preditiva de apostas esportivas com IA</p>
            
            <h2>📊 Acesso Rápido</h2>
            <a href="/docs" class="btn">📘 Documentação API</a>
            <a href="/dashboard" class="btn">📈 Dashboard</a>
            <a href="/api/v1/health" class="btn">🏥 Health Check</a>
            
            <h2>🔗 Endpoints Principais</h2>
            <ul>
                <li><strong>GET /api/v1/matches/live</strong> - Jogos ao vivo</li>
                <li><strong>GET /api/v1/predictions</strong> - Previsões recentes</li>
                <li><strong>GET /api/v1/value-bets</strong> - Apostas com valor</li>
                <li><strong>POST /api/v1/analyze/{fixture_id}</strong> - Analisar jogo</li>
            </ul>
        </div>
    </body>
    </html>
    """

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "cache": "connected",
            "api": "online"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1
    )
