"""
Modelos Pydantic para a API do sistema MaraBet AI
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MatchStatus(str, Enum):
    """Status dos jogos"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"

class PredictionType(str, Enum):
    """Tipos de previsão"""
    HOME_WIN = "home_win"
    DRAW = "draw"
    AWAY_WIN = "away_win"
    OVER_2_5 = "over_2_5"
    UNDER_2_5 = "under_2_5"
    BTTS = "btts"
    NO_BTTS = "no_btts"

class BetResult(str, Enum):
    """Resultado das apostas"""
    PENDING = "pending"
    WIN = "win"
    LOSS = "loss"
    VOID = "void"

class TeamResponse(BaseModel):
    """Resposta de time"""
    id: int
    name: str
    logo: Optional[str] = None
    country: Optional[str] = None

class LeagueResponse(BaseModel):
    """Resposta de liga"""
    id: int
    name: str
    country: str
    logo: Optional[str] = None
    type: str = "league"

class MatchResponse(BaseModel):
    """Resposta de jogo"""
    id: int
    league: LeagueResponse
    home_team: TeamResponse
    away_team: TeamResponse
    match_date: datetime
    status: MatchStatus
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    minute: Optional[int] = None
    venue: Optional[str] = None
    referee: Optional[str] = None

class PredictionResponse(BaseModel):
    """Resposta de previsão"""
    id: str
    match_id: int
    match: MatchResponse
    model_name: str
    prediction_type: PredictionType
    probability: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    expected_value: float
    kelly_fraction: float = Field(..., ge=0, le=1)
    recommended: bool = False
    created_at: datetime

class ValueBetResponse(BaseModel):
    """Resposta de aposta com valor"""
    id: str
    match_id: int
    match: MatchResponse
    bookmaker: str
    market_type: str
    selection: str
    odds: float = Field(..., gt=1)
    probability: float = Field(..., ge=0, le=1)
    expected_value: float
    kelly_fraction: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    created_at: datetime

class AnalysisResponse(BaseModel):
    """Resposta de análise"""
    status: str
    fixture_id: int
    message: str
    analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None

class PerformanceStatsResponse(BaseModel):
    """Resposta de estatísticas de desempenho"""
    period_days: int
    total_bets: int
    wins: int
    losses: int
    hit_rate: float
    total_stake: float
    total_return: float
    profit_loss: float
    roi: float

class CollectionTriggerResponse(BaseModel):
    """Resposta de trigger de coleta"""
    status: str
    mode: str
    message: str

class ErrorResponse(BaseModel):
    """Resposta de erro"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime

class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

class MatchDetailsRequest(BaseModel):
    """Request para detalhes do jogo"""
    fixture_id: int

class AnalysisRequest(BaseModel):
    """Request para análise"""
    fixture_id: int
    include_statistics: bool = True
    include_predictions: bool = True
    include_value_bets: bool = True

class PredictionRequest(BaseModel):
    """Request para previsão"""
    match_id: int
    model_name: str
    prediction_type: PredictionType
    confidence_threshold: float = Field(0.70, ge=0, le=1)

class ValueBetRequest(BaseModel):
    """Request para value bet"""
    match_id: int
    bookmaker: str
    market_type: str
    selection: str
    odds: float = Field(..., gt=1)
    min_ev: float = Field(0.05, ge=0)

class BettingHistoryRequest(BaseModel):
    """Request para histórico de apostas"""
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    result: Optional[BetResult] = None
    limit: int = Field(100, ge=1, le=1000)

class StatisticsRequest(BaseModel):
    """Request para estatísticas"""
    period_days: int = Field(30, ge=1, le=365)
    league_id: Optional[int] = None
    bookmaker: Optional[str] = None
    include_predictions: bool = True
    include_bets: bool = True

class CollectionRequest(BaseModel):
    """Request para coleta"""
    mode: str = Field("live", pattern="^(live|today|upcoming|historical)$")
    league_ids: Optional[List[int]] = None
    hours_ahead: int = Field(24, ge=1, le=168)
    force_update: bool = False

class NotificationRequest(BaseModel):
    """Request para notificação"""
    message: str
    type: str = Field("info", pattern="^(info|warning|error|success)$")
    channels: List[str] = Field(["telegram"], min_items=1)
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")

class UserRequest(BaseModel):
    """Request para usuário"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8)
    role: str = Field("USER", pattern="^(ADMIN|MODERATOR|USER|VIEWER)$")

class LoginRequest(BaseModel):
    """Request para login"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Resposta de token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """Resposta de usuário"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
