#!/usr/bin/env python3
"""
Modelos de Validação de Dados para o MaraBet AI
Validação robusta e sanitização de dados de entrada
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import re
import html

# Constantes de validação
VALID_LEAGUES = [39, 140, 78, 135, 61, 88, 94, 203, 262, 71]  # Principais ligas
VALID_BET_TYPES = [
    # Mercados básicos
    'home_win', 'draw', 'away_win',
    # Mercados de golos
    'over_0_5', 'under_0_5', 'over_1_5', 'under_1_5', 'over_2_5', 'under_2_5', 
    'over_3_5', 'under_3_5', 'btts_yes', 'btts_no',
    # Mercados de handicap
    'asian_handicap_home', 'asian_handicap_away', 'european_handicap_home', 'european_handicap_away',
    # Mercados de dupla chance
    'double_chance_1x', 'double_chance_x2', 'double_chance_12',
    # Mercados de cartões
    'cards_over_1_5', 'cards_under_1_5', 'cards_over_2_5', 'cards_under_2_5',
    'cards_over_3_5', 'cards_under_3_5', 'yellow_cards_over', 'yellow_cards_under',
    'red_cards_yes', 'red_cards_no',
    # Mercados de cantos
    'corners_over_8_5', 'corners_under_8_5', 'corners_over_9_5', 'corners_under_9_5',
    'corners_over_10_5', 'corners_under_10_5', 'corners_over_11_5', 'corners_under_11_5',
    # Mercados de resultado exato
    'exact_score_1_0', 'exact_score_2_0', 'exact_score_2_1', 'exact_score_3_0',
    'exact_score_3_1', 'exact_score_3_2', 'exact_score_0_0', 'exact_score_1_1',
    'exact_score_2_2', 'exact_score_3_3', 'exact_score_0_1', 'exact_score_0_2',
    'exact_score_1_2', 'exact_score_0_3', 'exact_score_1_3', 'exact_score_2_3'
]
VALID_CURRENCIES = ['USD', 'EUR', 'BRL', 'GBP', 'AOA']  # Adicionado AOA para Angola
VALID_TIMEZONES = ['UTC', 'America/Sao_Paulo', 'Europe/London', 'America/New_York', 'Africa/Luanda']

class LeagueEnum(str, Enum):
    """Enum para ligas válidas"""
    PREMIER_LEAGUE = "39"
    LALIGA = "140"
    BUNDESLIGA = "78"
    SERIE_A = "135"
    LIGUE_1 = "61"
    CHAMPIONS_LEAGUE = "2"
    EUROPA_LEAGUE = "3"

class BetTypeEnum(str, Enum):
    """Enum para tipos de aposta"""
    # Mercados básicos
    HOME_WIN = "home_win"
    DRAW = "draw"
    AWAY_WIN = "away_win"
    
    # Mercados de golos
    OVER_0_5 = "over_0_5"
    UNDER_0_5 = "under_0_5"
    OVER_1_5 = "over_1_5"
    UNDER_1_5 = "under_1_5"
    OVER_2_5 = "over_2_5"
    UNDER_2_5 = "under_2_5"
    OVER_3_5 = "over_3_5"
    UNDER_3_5 = "under_3_5"
    BTTS_YES = "btts_yes"
    BTTS_NO = "btts_no"
    
    # Mercados de handicap
    ASIAN_HANDICAP_HOME = "asian_handicap_home"
    ASIAN_HANDICAP_AWAY = "asian_handicap_away"
    EUROPEAN_HANDICAP_HOME = "european_handicap_home"
    EUROPEAN_HANDICAP_AWAY = "european_handicap_away"
    
    # Mercados de dupla chance
    DOUBLE_CHANCE_1X = "double_chance_1x"
    DOUBLE_CHANCE_X2 = "double_chance_x2"
    DOUBLE_CHANCE_12 = "double_chance_12"
    
    # Mercados de cartões
    CARDS_OVER_1_5 = "cards_over_1_5"
    CARDS_UNDER_1_5 = "cards_under_1_5"
    CARDS_OVER_2_5 = "cards_over_2_5"
    CARDS_UNDER_2_5 = "cards_under_2_5"
    CARDS_OVER_3_5 = "cards_over_3_5"
    CARDS_UNDER_3_5 = "cards_under_3_5"
    YELLOW_CARDS_OVER = "yellow_cards_over"
    YELLOW_CARDS_UNDER = "yellow_cards_under"
    RED_CARDS_YES = "red_cards_yes"
    RED_CARDS_NO = "red_cards_no"
    
    # Mercados de cantos
    CORNERS_OVER_8_5 = "corners_over_8_5"
    CORNERS_UNDER_8_5 = "corners_under_8_5"
    CORNERS_OVER_9_5 = "corners_over_9_5"
    CORNERS_UNDER_9_5 = "corners_under_9_5"
    CORNERS_OVER_10_5 = "corners_over_10_5"
    CORNERS_UNDER_10_5 = "corners_under_10_5"
    CORNERS_OVER_11_5 = "corners_over_11_5"
    CORNERS_UNDER_11_5 = "corners_under_11_5"
    
    # Mercados de resultado exato
    EXACT_SCORE_1_0 = "exact_score_1_0"
    EXACT_SCORE_2_0 = "exact_score_2_0"
    EXACT_SCORE_2_1 = "exact_score_2_1"
    EXACT_SCORE_3_0 = "exact_score_3_0"
    EXACT_SCORE_3_1 = "exact_score_3_1"
    EXACT_SCORE_3_2 = "exact_score_3_2"
    EXACT_SCORE_0_0 = "exact_score_0_0"
    EXACT_SCORE_1_1 = "exact_score_1_1"
    EXACT_SCORE_2_2 = "exact_score_2_2"
    EXACT_SCORE_3_3 = "exact_score_3_3"
    EXACT_SCORE_0_1 = "exact_score_0_1"
    EXACT_SCORE_0_2 = "exact_score_0_2"
    EXACT_SCORE_1_2 = "exact_score_1_2"
    EXACT_SCORE_0_3 = "exact_score_0_3"
    EXACT_SCORE_1_3 = "exact_score_1_3"
    EXACT_SCORE_2_3 = "exact_score_2_3"

class PredictionRequest(BaseModel):
    """Modelo para requisições de predição"""
    home_team: str = Field(..., min_length=2, max_length=100, description="Nome do time da casa")
    away_team: str = Field(..., min_length=2, max_length=100, description="Nome do time visitante")
    league_id: int = Field(..., description="ID da liga")
    match_date: Optional[date] = Field(None, description="Data da partida")
    include_odds: bool = Field(True, description="Incluir odds na predição")
    
    @validator('home_team', 'away_team')
    def validate_team_names(cls, v):
        """Valida e sanitiza nomes dos times"""
        if not v or not v.strip():
            raise ValueError('Nome do time não pode estar vazio')
        
        # Sanitizar HTML
        v = html.escape(v.strip())
        
        # Verificar caracteres válidos
        if not re.match(r'^[a-zA-Z0-9\s\-\.\']+$', v):
            raise ValueError('Nome do time contém caracteres inválidos')
        
        # Limitar tamanho
        if len(v) > 100:
            raise ValueError('Nome do time muito longo')
        
        return v
    
    @validator('league_id')
    def validate_league_id(cls, v):
        """Valida ID da liga"""
        if v not in VALID_LEAGUES:
            raise ValueError(f'Liga inválida. Ligas válidas: {VALID_LEAGUES}')
        return v
    
    @validator('match_date')
    def validate_match_date(cls, v):
        """Valida data da partida"""
        if v and v < date.today():
            raise ValueError('Data da partida não pode ser no passado')
        return v

class OddsRequest(BaseModel):
    """Modelo para requisições de odds"""
    match_id: Optional[int] = Field(None, description="ID da partida")
    home_team: Optional[str] = Field(None, min_length=2, max_length=100)
    away_team: Optional[str] = Field(None, min_length=2, max_length=100)
    league_id: Optional[int] = Field(None)
    bookmaker: Optional[str] = Field(None, max_length=50)
    
    @validator('home_team', 'away_team')
    def validate_team_names(cls, v):
        """Valida nomes dos times"""
        if v:
            v = html.escape(v.strip())
            if not re.match(r'^[a-zA-Z0-9\s\-\.\']+$', v):
                raise ValueError('Nome do time contém caracteres inválidos')
        return v
    
    @validator('league_id')
    def validate_league_id(cls, v):
        """Valida ID da liga"""
        if v and v not in VALID_LEAGUES:
            raise ValueError(f'Liga inválida. Ligas válidas: {VALID_LEAGUES}')
        return v
    
    @validator('bookmaker')
    def validate_bookmaker(cls, v):
        """Valida nome da casa de apostas"""
        if v:
            v = html.escape(v.strip())
            if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
                raise ValueError('Nome da casa de apostas contém caracteres inválidos')
        return v

class NotificationRequest(BaseModel):
    """Modelo para requisições de notificação"""
    type: str = Field(..., description="Tipo de notificação")
    message: str = Field(..., min_length=1, max_length=1000, description="Mensagem")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    priority: str = Field("normal", description="Prioridade da notificação")
    channels: List[str] = Field(["telegram"], description="Canais de notificação")
    
    @validator('type')
    def validate_type(cls, v):
        """Valida tipo de notificação"""
        valid_types = ['prediction', 'alert', 'error', 'info', 'warning']
        if v not in valid_types:
            raise ValueError(f'Tipo inválido. Tipos válidos: {valid_types}')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Valida e sanitiza mensagem"""
        if not v or not v.strip():
            raise ValueError('Mensagem não pode estar vazia')
        
        # Sanitizar HTML
        v = html.escape(v.strip())
        
        # Verificar tamanho
        if len(v) > 1000:
            raise ValueError('Mensagem muito longa')
        
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Valida prioridade"""
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Prioridade inválida. Prioridades válidas: {valid_priorities}')
        return v
    
    @validator('channels')
    def validate_channels(cls, v):
        """Valida canais de notificação"""
        valid_channels = ['telegram', 'email', 'sms', 'push']
        for channel in v:
            if channel not in valid_channels:
                raise ValueError(f'Canal inválido: {channel}. Canais válidos: {valid_channels}')
        return v

class UserRequest(BaseModel):
    """Modelo para requisições de usuário"""
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário")
    email: str = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=8, max_length=128, description="Senha")
    full_name: Optional[str] = Field(None, max_length=100, description="Nome completo")
    timezone: str = Field("UTC", description="Fuso horário")
    currency: str = Field("USD", description="Moeda preferida")
    
    @validator('username')
    def validate_username(cls, v):
        """Valida nome de usuário"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Nome de usuário deve conter apenas letras, números e underscore')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Valida senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        # Verificar complexidade
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Valida nome completo"""
        if v:
            v = html.escape(v.strip())
            if not re.match(r'^[a-zA-Z\s]+$', v):
                raise ValueError('Nome completo deve conter apenas letras e espaços')
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Valida fuso horário"""
        if v not in VALID_TIMEZONES:
            raise ValueError(f'Fuso horário inválido. Fuso horários válidos: {VALID_TIMEZONES}')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """Valida moeda"""
        if v not in VALID_CURRENCIES:
            raise ValueError(f'Moeda inválida. Moedas válidas: {VALID_CURRENCIES}')
        return v

class BetRequest(BaseModel):
    """Modelo para requisições de aposta"""
    match_id: int = Field(..., description="ID da partida")
    bet_type: BetTypeEnum = Field(..., description="Tipo da aposta")
    odds: float = Field(..., gt=1.0, le=100.0, description="Odds da aposta")
    stake: float = Field(..., gt=0, le=10000, description="Valor da aposta")
    expected_value: float = Field(..., ge=0, le=1, description="Valor esperado")
    confidence: float = Field(..., ge=0, le=1, description="Confiança na aposta")
    
    @validator('odds')
    def validate_odds(cls, v):
        """Valida odds"""
        if v <= 1.0:
            raise ValueError('Odds deve ser maior que 1.0')
        if v > 100.0:
            raise ValueError('Odds muito alta (máximo 100.0)')
        return round(v, 2)
    
    @validator('stake')
    def validate_stake(cls, v):
        """Valida valor da aposta"""
        if v <= 0:
            raise ValueError('Valor da aposta deve ser positivo')
        if v > 10000:
            raise ValueError('Valor da aposta muito alto (máximo 10000)')
        return round(v, 2)
    
    @validator('expected_value')
    def validate_expected_value(cls, v):
        """Valida valor esperado"""
        if v < 0:
            raise ValueError('Valor esperado não pode ser negativo')
        if v > 1:
            raise ValueError('Valor esperado não pode ser maior que 1')
        return round(v, 3)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Valida confiança"""
        if v < 0:
            raise ValueError('Confiança não pode ser negativa')
        if v > 1:
            raise ValueError('Confiança não pode ser maior que 1')
        return round(v, 2)

class SearchRequest(BaseModel):
    """Modelo para requisições de busca"""
    query: str = Field(..., min_length=1, max_length=200, description="Termo de busca")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de busca")
    page: int = Field(1, ge=1, le=1000, description="Página")
    limit: int = Field(20, ge=1, le=100, description="Limite por página")
    sort_by: Optional[str] = Field(None, description="Campo para ordenação")
    sort_order: str = Field("desc", description="Ordem de classificação")
    
    @validator('query')
    def validate_query(cls, v):
        """Valida termo de busca"""
        if not v or not v.strip():
            raise ValueError('Termo de busca não pode estar vazio')
        
        # Sanitizar HTML
        v = html.escape(v.strip())
        
        # Verificar caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'Termo de busca contém caractere perigoso: {char}')
        
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Valida campo de ordenação"""
        if v:
            valid_fields = ['date', 'odds', 'confidence', 'expected_value', 'team']
            if v not in valid_fields:
                raise ValueError(f'Campo de ordenação inválido. Campos válidos: {valid_fields}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Valida ordem de classificação"""
        if v not in ['asc', 'desc']:
            raise ValueError('Ordem de classificação deve ser "asc" ou "desc"')
        return v

class DataSanitizer:
    """Classe para sanitização de dados"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitiza string removendo caracteres perigosos"""
        if not value:
            return ""
        
        # Escapar HTML
        value = html.escape(value)
        
        # Remover caracteres de controle
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Limitar tamanho
        return value[:1000]
    
    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """Sanitiza identificador SQL"""
        if not identifier:
            return ""
        
        # Permitir apenas caracteres alfanuméricos e underscore
        return re.sub(r'[^a-zA-Z0-9_]', '', identifier)
    
    @staticmethod
    def sanitize_numeric(value: Union[str, int, float]) -> Union[int, float]:
        """Sanitiza valor numérico"""
        if isinstance(value, str):
            # Remover caracteres não numéricos exceto ponto e vírgula
            value = re.sub(r'[^0-9.,]', '', value)
            # Converter vírgula para ponto
            value = value.replace(',', '.')
        
        try:
            if '.' in str(value):
                return float(value)
            else:
                return int(value)
        except (ValueError, TypeError):
            raise ValueError('Valor numérico inválido')
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitiza email"""
        if not email:
            return ""
        
        # Remover espaços e converter para minúsculo
        email = email.strip().lower()
        
        # Validar formato básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Formato de email inválido')
        
        return email

class ValidationError(Exception):
    """Exceção personalizada para erros de validação"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

def validate_and_sanitize_data(data: Dict[str, Any], model_class: BaseModel) -> BaseModel:
    """Valida e sanitiza dados usando modelo Pydantic"""
    try:
        # Sanitizar dados de entrada
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = DataSanitizer.sanitize_string(value)
            else:
                sanitized_data[key] = value
        
        # Validar com Pydantic
        return model_class(**sanitized_data)
    
    except Exception as e:
        raise ValidationError(f"Erro de validação: {str(e)}")

if __name__ == "__main__":
    # Teste dos modelos de validação
    print("🧪 TESTANDO MODELOS DE VALIDAÇÃO")
    print("=" * 40)
    
    # Teste PredictionRequest
    try:
        pred_request = PredictionRequest(
            home_team="Manchester City",
            away_team="Manchester United",
            league_id=39,
            match_date="2024-01-01"
        )
        print("✅ PredictionRequest válido")
    except Exception as e:
        print(f"❌ PredictionRequest inválido: {e}")
    
    # Teste OddsRequest
    try:
        odds_request = OddsRequest(
            home_team="Barcelona",
            away_team="Real Madrid",
            league_id=140
        )
        print("✅ OddsRequest válido")
    except Exception as e:
        print(f"❌ OddsRequest inválido: {e}")
    
    # Teste NotificationRequest
    try:
        notif_request = NotificationRequest(
            type="prediction",
            message="Nova predição disponível",
            priority="normal"
        )
        print("✅ NotificationRequest válido")
    except Exception as e:
        print(f"❌ NotificationRequest inválido: {e}")
    
    print("\n🎉 TESTES DE VALIDAÇÃO CONCLUÍDOS!")
