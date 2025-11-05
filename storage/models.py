"""
Modelos SQLAlchemy para o sistema MaraBet AI
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="USER", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relacionamentos
    bets = relationship("BettingHistory", back_populates="user")

class League(Base):
    """Modelo de liga"""
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
    type = Column(String(20), default="league")
    logo = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    matches = relationship("Match", back_populates="league")

class Team(Base):
    """Modelo de time"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
    logo = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")

class Match(Base):
    """Modelo de jogo"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    match_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="scheduled")
    home_score = Column(Integer)
    away_score = Column(Integer)
    venue = Column(String(100))
    referee = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    odds = relationship("Odds", back_populates="match")
    statistics = relationship("Statistics", back_populates="match")
    predictions = relationship("Prediction", back_populates="match")
    bets = relationship("BettingHistory", back_populates="match")

class Odds(Base):
    """Modelo de odds"""
    __tablename__ = "odds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(Integer, ForeignKey("matches.id"))
    bookmaker = Column(String(50), nullable=False)
    market_type = Column(String(50), nullable=False)
    selection = Column(String(100), nullable=False)
    odds = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    match = relationship("Match", back_populates="odds")

class Statistics(Base):
    """Modelo de estatísticas"""
    __tablename__ = "statistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(Integer, ForeignKey("matches.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    stat_type = Column(String(50), nullable=False)
    stat_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    match = relationship("Match", back_populates="statistics")
    team = relationship("Team")

class Prediction(Base):
    """Modelo de previsão"""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(Integer, ForeignKey("matches.id"))
    model_name = Column(String(100), nullable=False)
    prediction_type = Column(String(50), nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    expected_value = Column(Float)
    kelly_fraction = Column(Float)
    recommended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    match = relationship("Match", back_populates="predictions")

class BettingHistory(Base):
    """Modelo de histórico de apostas"""
    __tablename__ = "betting_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"))
    bookmaker = Column(String(50), nullable=False)
    market_type = Column(String(50), nullable=False)
    selection = Column(String(100), nullable=False)
    odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    potential_return = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    result = Column(String(20))
    profit_loss = Column(Float)
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="bets")
    match = relationship("Match", back_populates="bets")
    prediction = relationship("Prediction")

class BacktestingResults(Base):
    """Modelo de resultados de backtesting"""
    __tablename__ = "backtesting_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_bets = Column(Integer, nullable=False)
    winning_bets = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    total_profit = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class SystemLog(Base):
    """Modelo de log do sistema"""
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function = Column(String(100))
    line_number = Column(Integer)
    exception_info = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Notification(Base):
    """Modelo de notificação"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), default="info")
    priority = Column(String(20), default="normal")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    
    # Relacionamentos
    user = relationship("User")
