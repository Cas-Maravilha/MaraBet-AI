from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from settings.settings import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    fixture_id = Column(Integer, unique=True, index=True)
    league_id = Column(Integer, index=True)
    league_name = Column(String)
    date = Column(DateTime, index=True)
    
    home_team_id = Column(Integer)
    home_team_name = Column(String)
    away_team_id = Column(Integer)
    away_team_name = Column(String)
    
    status = Column(String)
    elapsed_time = Column(Integer)
    
    home_score = Column(Integer)
    away_score = Column(Integer)
    
    statistics = Column(JSON)
    events = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Odds(Base):
    __tablename__ = 'odds'
    
    id = Column(Integer, primary_key=True)
    fixture_id = Column(Integer, index=True)
    bookmaker = Column(String)
    market = Column(String)
    selection = Column(String)
    odd = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    fixture_id = Column(Integer, index=True)
    
    market = Column(String)
    selection = Column(String)
    
    predicted_probability = Column(Float)
    implied_probability = Column(Float)
    recommended_odd = Column(Float)
    current_odd = Column(Float)
    
    expected_value = Column(Float)
    confidence = Column(Float)
    
    stake_percentage = Column(Float)
    recommended = Column(Boolean, default=False)
    
    factors = Column(JSON)  # Justificativa
    
    created_at = Column(DateTime, default=datetime.utcnow)

class BettingHistory(Base):
    __tablename__ = 'betting_history'
    
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer)
    fixture_id = Column(Integer)
    
    stake = Column(Float)
    odd = Column(Float)
    potential_return = Column(Float)
    
    result = Column(String)  # win, loss, pending
    profit_loss = Column(Float)
    
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)

# Criar todas as tabelas
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
