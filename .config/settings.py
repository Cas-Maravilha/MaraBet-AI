import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# APIs
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '')
API_FOOTBALL_HOST = 'v3.football.api-sports.io'

THE_ODDS_API_KEY = os.getenv('THE_ODDS_API_KEY', '')

# Banco de Dados
DATABASE_URL = f"sqlite:///{DATA_DIR}/sports_data.db"

# Redis (opcional)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Configurações de Coleta
COLLECTION_INTERVAL = 60  # segundos
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Ligas para monitorar (IDs da API-Football)
MONITORED_LEAGUES = [
    39,   # Premier League
    140,  # La Liga
    78,   # Bundesliga
    135,  # Serie A
    61,   # Ligue 1
    71,   # Brasileirão Série A
]

# Configurações de Análise
MIN_CONFIDENCE = 0.70
MAX_CONFIDENCE = 0.90
MIN_VALUE_EV = 0.05  # 5% de EV mínimo

# Logs
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
