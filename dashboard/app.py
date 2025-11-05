from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import json

from armazenamento.banco_de_dados import SessionLocal, Match, Odds, Prediction, BettingHistory
from scheduler.automated_collector import AutomatedCollector
from settings.settings import MIN_CONFIDENCE, MAX_CONFIDENCE, MIN_VALUE_EV

# Importações de autenticação
from auth.models import User, UserRole, UserStatus
from auth.jwt_auth import (
    get_current_user, get_current_active_user, require_role, require_superuser,
    authenticate_user, get_user_by_id, log_user_activity
)
from auth.endpoints import router as auth_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="MaraBet AI Dashboard",
    description="Dashboard interativo para análise de apostas esportivas com autenticação JWT",
    version="1.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# Incluir rotas de autenticação
app.include_router(auth_router)

# Incluir rotas de otimização
from optimization.api.optimization_endpoints import router as optimization_router
app.include_router(optimization_router)

# Dependência para banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar coletor automatizado
collector = AutomatedCollector()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Página principal do dashboard"""
    
    # Verificar se usuário está autenticado
    try:
        current_user = get_current_user(request)
        user = get_user_by_id(db, current_user["user_id"])
        is_authenticated = True
    except:
        is_authenticated = False
        user = None
    
    # Estatísticas gerais
    stats = {
        'total_matches': db.query(Match).count(),
        'total_odds': db.query(Odds).count(),
        'total_predictions': db.query(Prediction).count(),
        'recommended_predictions': db.query(Prediction).filter(Prediction.recommended == True).count(),
        'live_matches': db.query(Match).filter(Match.status == 'LIVE').count(),
        'today_matches': db.query(Match).filter(
            Match.date >= datetime.now().date(),
            Match.date < datetime.now().date() + timedelta(days=1)
        ).count()
    }
    
    # Predições recentes
    recent_predictions = db.query(Prediction).filter(
        Prediction.recommended == True
    ).order_by(Prediction.created_at.desc()).limit(10).all()
    
    # Partidas de hoje
    today_matches = db.query(Match).filter(
        Match.date >= datetime.now().date(),
        Match.date < datetime.now().date() + timedelta(days=1)
    ).order_by(Match.date).limit(20).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_predictions": recent_predictions,
        "today_matches": today_matches,
        "min_confidence": MIN_CONFIDENCE,
        "max_confidence": MAX_CONFIDENCE,
        "min_value_ev": MIN_VALUE_EV,
        "is_authenticated": is_authenticated,
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Página de registro"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/api/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """API para estatísticas do sistema (requer autenticação)"""
    
    # Estatísticas básicas
    stats = {
        'total_matches': db.query(Match).count(),
        'total_odds': db.query(Odds).count(),
        'total_predictions': db.query(Prediction).count(),
        'recommended_predictions': db.query(Prediction).filter(Prediction.recommended == True).count(),
        'live_matches': db.query(Match).filter(Match.status == 'LIVE').count(),
        'today_matches': db.query(Match).filter(
            Match.date >= datetime.now().date(),
            Match.date < datetime.now().date() + timedelta(days=1)
        ).count()
    }
    
    # Estatísticas por liga
    league_stats = db.query(
        Match.league_name,
        db.func.count(Match.id).label('count')
    ).group_by(Match.league_name).all()
    
    stats['leagues'] = [{'name': league, 'count': count} for league, count in league_stats]
    
    # Estatísticas de predições por mercado
    market_stats = db.query(
        Prediction.market,
        db.func.count(Prediction.id).label('count')
    ).group_by(Prediction.market).all()
    
    stats['markets'] = [{'name': market, 'count': count} for market, count in market_stats]
    
    return stats

@app.get("/api/predictions")
async def get_predictions(
    limit: int = 50,
    recommended_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """API para predições (requer autenticação)"""
    
    query = db.query(Prediction)
    
    if recommended_only:
        query = query.filter(Prediction.recommended == True)
    
    predictions = query.order_by(Prediction.created_at.desc()).limit(limit).all()
    
    result = []
    for pred in predictions:
        # Buscar dados da partida
        match = db.query(Match).filter(Match.fixture_id == pred.fixture_id).first()
        
        result.append({
            'id': pred.id,
            'fixture_id': pred.fixture_id,
            'market': pred.market,
            'selection': pred.selection,
            'predicted_probability': pred.predicted_probability,
            'implied_probability': pred.implied_probability,
            'recommended_odd': pred.recommended_odd,
            'current_odd': pred.current_odd,
            'expected_value': pred.expected_value,
            'confidence': pred.confidence,
            'stake_percentage': pred.stake_percentage,
            'recommended': pred.recommended,
            'created_at': pred.created_at.isoformat(),
            'match': {
                'home_team': match.home_team_name if match else 'N/A',
                'away_team': match.away_team_name if match else 'N/A',
                'date': match.date.isoformat() if match else None,
                'league': match.league_name if match else 'N/A'
            } if match else None
        })
    
    return result

@app.get("/api/matches")
async def get_matches(
    limit: int = 50,
    status: Optional[str] = None,
    league: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """API para partidas (requer autenticação)"""
    
    query = db.query(Match)
    
    if status:
        query = query.filter(Match.status == status)
    
    if league:
        query = query.filter(Match.league_name == league)
    
    matches = query.order_by(Match.date.desc()).limit(limit).all()
    
    result = []
    for match in matches:
        # Buscar odds para a partida
        odds = db.query(Odds).filter(Odds.fixture_id == match.fixture_id).all()
        
        # Agrupar odds por bookmaker
        bookmakers = {}
        for odd in odds:
            if odd.bookmaker not in bookmakers:
                bookmakers[odd.bookmaker] = {}
            if odd.market not in bookmakers[odd.bookmaker]:
                bookmakers[odd.bookmaker][odd.market] = []
            bookmakers[odd.bookmaker][odd.market].append({
                'selection': odd.selection,
                'odd': odd.odd
            })
        
        result.append({
            'fixture_id': match.fixture_id,
            'league_name': match.league_name,
            'date': match.date.isoformat(),
            'home_team': match.home_team_name,
            'away_team': match.away_team_name,
            'status': match.status,
            'home_score': match.home_score,
            'away_score': match.away_score,
            'odds': bookmakers
        })
    
    return result

@app.get("/api/odds/{fixture_id}")
async def get_odds_for_match(
    fixture_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """API para odds de uma partida específica (requer autenticação)"""
    
    odds = db.query(Odds).filter(Odds.fixture_id == fixture_id).all()
    
    if not odds:
        raise HTTPException(status_code=404, detail="Odds não encontradas")
    
    # Agrupar por bookmaker e mercado
    result = {}
    for odd in odds:
        if odd.bookmaker not in result:
            result[odd.bookmaker] = {}
        if odd.market not in result[odd.bookmaker]:
            result[odd.bookmaker][odd.market] = []
        
        result[odd.bookmaker][odd.market].append({
            'selection': odd.selection,
            'odd': odd.odd,
            'timestamp': odd.timestamp.isoformat()
        })
    
    return result

@app.post("/api/collector/start")
async def start_collector(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Inicia o coletor automatizado (apenas admin)"""
    try:
        if not collector.running:
            collector.start_scheduler()
            return {"message": "Coletor iniciado com sucesso", "status": "running"}
        else:
            return {"message": "Coletor já está em execução", "status": "running"}
    except Exception as e:
        logger.error(f"Erro ao iniciar coletor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collector/stop")
async def stop_collector(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """Para o coletor automatizado (apenas admin)"""
    try:
        if collector.running:
            collector.stop_scheduler()
            return {"message": "Coletor parado com sucesso", "status": "stopped"}
        else:
            return {"message": "Coletor já está parado", "status": "stopped"}
    except Exception as e:
        logger.error(f"Erro ao parar coletor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collector/status")
async def get_collector_status():
    """Status do coletor automatizado"""
    try:
        status = collector.get_status()
        return status
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leagues")
async def get_leagues(db: Session = Depends(get_db)):
    """API para listar ligas"""
    
    leagues = db.query(Match.league_name).distinct().all()
    return [{'name': league[0]} for league in leagues]

@app.get("/api/markets")
async def get_markets(db: Session = Depends(get_db)):
    """API para listar mercados"""
    
    markets = db.query(Prediction.market).distinct().all()
    return [{'name': market[0]} for market in markets]

@app.get("/api/performance")
async def get_performance(db: Session = Depends(get_db)):
    """API para métricas de performance"""
    
    # Predições dos últimos 30 dias
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_predictions = db.query(Prediction).filter(
        Prediction.created_at >= thirty_days_ago
    ).all()
    
    if not recent_predictions:
        return {
            'total_predictions': 0,
            'average_ev': 0,
            'average_confidence': 0,
            'success_rate': 0
        }
    
    # Calcular métricas
    total_predictions = len(recent_predictions)
    average_ev = sum(p.expected_value for p in recent_predictions) / total_predictions
    average_confidence = sum(p.confidence for p in recent_predictions) / total_predictions
    
    # Taxa de sucesso (simulada - em produção, comparar com resultados reais)
    success_rate = 0.65  # 65% de taxa de sucesso simulada
    
    return {
        'total_predictions': total_predictions,
        'average_ev': round(average_ev, 4),
        'average_confidence': round(average_confidence, 4),
        'success_rate': success_rate
    }

@app.get("/optimization", response_class=HTMLResponse)
async def optimization_dashboard(request: Request):
    """Dashboard de otimização de hiperparâmetros"""
    return HTMLResponse(content=open("optimization/dashboard/optimization_dashboard.html", "r", encoding="utf-8").read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
