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

# Notificações
# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Email
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')

# Configurações de Notificação
NOTIFICATION_ENABLED = bool(TELEGRAM_BOT_TOKEN or SMTP_USERNAME)
NOTIFICATION_PREDICTION_THRESHOLD = 0.05  # 5% EV mínimo para notificar
NOTIFICATION_CONFIDENCE_THRESHOLD = 0.70  # 70% confiança mínima
NOTIFICATION_COOLDOWN = 300  # 5 minutos entre notificações similares