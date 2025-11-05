from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from storage.database import get_db, Match, Prediction, BettingHistory
from services.collector_service import CollectorService
from services.analyzer_service import AnalyzerService
from api.models import *
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Services
collector_service = CollectorService()
analyzer_service = AnalyzerService()

@router.get("/matches/live", response_model=List[MatchResponse])
async def get_live_matches(
    league_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retorna jogos ao vivo"""
    try:
        matches = collector_service.get_live_matches(league_id)
        return matches
    except Exception as e:
        logger.error(f"Erro ao buscar jogos ao vivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matches/upcoming", response_model=List[MatchResponse])
async def get_upcoming_matches(
    hours: int = Query(24, ge=1, le=168),
    league_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retorna próximos jogos"""
    try:
        matches = collector_service.get_upcoming_matches(hours, league_id)
        return matches
    except Exception as e:
        logger.error(f"Erro ao buscar próximos jogos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions", response_model=List[PredictionResponse])
async def get_predictions(
    min_confidence: float = Query(0.70, ge=0, le=1),
    min_ev: float = Query(0.05, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retorna previsões recentes"""
    try:
        predictions = db.query(Prediction).filter(
            Prediction.confidence >= min_confidence,
            Prediction.expected_value >= min_ev,
            Prediction.recommended == True
        ).order_by(
            Prediction.created_at.desc()
        ).limit(limit).all()
        
        return predictions
    except Exception as e:
        logger.error(f"Erro ao buscar previsões: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/value-bets", response_model=List[ValueBetResponse])
async def get_value_bets(
    db: Session = Depends(get_db)
):
    """Retorna apostas com valor identificadas"""
    try:
        value_bets = analyzer_service.find_value_bets()
        return value_bets
    except Exception as e:
        logger.error(f"Erro ao buscar value bets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/{fixture_id}", response_model=AnalysisResponse)
async def analyze_match(
    fixture_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analisa um jogo específico"""
    try:
        # Buscar dados do jogo
        match_data = collector_service.get_match_details(fixture_id)
        
        if not match_data:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")
        
        # Analisar em background
        background_tasks.add_task(
            analyzer_service.analyze_match,
            match_data
        )
        
        return {
            "status": "analyzing",
            "fixture_id": fixture_id,
            "message": "Análise iniciada"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao analisar jogo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/performance")
async def get_performance_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Retorna estatísticas de desempenho"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        bets = db.query(BettingHistory).filter(
            BettingHistory.placed_at >= cutoff_date,
            BettingHistory.result != 'pending'
        ).all()
        
        total_bets = len(bets)
        wins = sum(1 for b in bets if b.result == 'win')
        losses = sum(1 for b in bets if b.result == 'loss')
        
        total_stake = sum(b.stake for b in bets)
        total_return = sum(b.potential_return for b in bets if b.result == 'win')
        profit_loss = total_return - total_stake
        
        roi = (profit_loss / total_stake * 100) if total_stake > 0 else 0
        hit_rate = (wins / total_bets * 100) if total_bets > 0 else 0
        
        return {
            "period_days": days,
            "total_bets": total_bets,
            "wins": wins,
            "losses": losses,
            "hit_rate": round(hit_rate, 2),
            "total_stake": round(total_stake, 2),
            "total_return": round(total_return, 2),
            "profit_loss": round(profit_loss, 2),
            "roi": round(roi, 2)
        }
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collect/trigger")
async def trigger_collection(
    background_tasks: BackgroundTasks,
    mode: str = Query("live", regex="^(live|today|upcoming)$")
):
    """Dispara coleta manual de dados"""
    try:
        background_tasks.add_task(
            collector_service.collect_data,
            mode
        )
        
        return {
            "status": "triggered",
            "mode": mode,
            "message": f"Coleta '{mode}' iniciada"
        }
    except Exception as e:
        logger.error(f"Erro ao disparar coleta: {e}")
        raise HTTPException(status_code=500, detail=str(e))
