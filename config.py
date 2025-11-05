import os
from dotenv import load_dotenv
from settings.settings import *

load_dotenv()

class Config:
    # Configurações da API
    API_KEY = os.getenv('API_KEY', '')
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '')
    THE_ODDS_API_KEY = THE_ODDS_API_KEY
    
    # Configurações do banco de dados
    DATABASE_URL = DATABASE_URL
    
    # Configurações de scraping
    SCRAPING_DELAY = 1  # segundos entre requisições
    MAX_RETRIES = MAX_RETRIES
    REQUEST_TIMEOUT = REQUEST_TIMEOUT
    
    # Configurações de modelos
    MODEL_UPDATE_FREQUENCY = 24  # horas
    MIN_GAMES_FOR_TRAINING = 50
    
    # Configurações de análise
    MIN_CONFIDENCE = MIN_CONFIDENCE
    MAX_CONFIDENCE = MAX_CONFIDENCE
    MIN_VALUE_EV = MIN_VALUE_EV
    
    # Ligas monitoradas
    MONITORED_LEAGUES = MONITORED_LEAGUES
    
    # Configurações de features
    FEATURE_WINDOW_DAYS = 30  # janela de tempo para features
    STATS_TO_TRACK = [
        'goals_scored', 'goals_conceded', 'shots', 'shots_on_target',
        'possession', 'passes', 'pass_accuracy', 'fouls', 'yellow_cards',
        'red_cards', 'corners', 'offsides'
    ]
    
    # Configurações de predição
    CONFIDENCE_THRESHOLD = 0.6
    MIN_ODDS = 1.5
    MAX_ODDS = 10.0
    
    # Configurações da aplicação web
    SECRET_KEY = os.getenv('SECRET_KEY', 'mara-bet-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
