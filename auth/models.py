"""
Modelos de Usuário e Autenticação para MaraBet AI
Sistema completo de gerenciamento de usuários com JWT
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from enum import Enum as PyEnum
import hashlib
import secrets
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from config_environment import get_config

Base = declarative_base()

# Configurações de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = get_config('security.secret_key')
JWT_SECRET_KEY = get_config('security.jwt_secret_key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class UserRole(PyEnum):
    """Roles de usuário"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    VIEWER = "viewer"

class UserStatus(PyEnum):
    """Status do usuário"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Informações de perfil
    phone = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    timezone = Column(String(50), default="Africa/Luanda", nullable=False)
    language = Column(String(10), default="pt", nullable=False)
    
    # Configurações de notificação
    email_notifications = Column(Boolean, default=True, nullable=False)
    telegram_notifications = Column(Boolean, default=False, nullable=False)
    telegram_chat_id = Column(String(50), nullable=True)
    
    # Configurações de apostas
    default_currency = Column(String(3), default="AOA", nullable=False)
    min_bet_amount = Column(String(20), default="10.0", nullable=False)
    max_bet_amount = Column(String(20), default="10000.0", nullable=False)
    risk_tolerance = Column(String(20), default="medium", nullable=False)  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Campos de auditoria
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def verify_password(self, password: str) -> bool:
        """Verifica senha do usuário"""
        return pwd_context.verify(password, self.hashed_password)
    
    def set_password(self, password: str) -> None:
        """Define nova senha"""
        self.hashed_password = pwd_context.hash(password)
    
    def generate_password_reset_token(self) -> str:
        """Gera token para reset de senha"""
        payload = {
            "user_id": self.id,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    def generate_email_verification_token(self) -> str:
        """Gera token para verificação de email"""
        payload = {
            "user_id": self.id,
            "type": "email_verification",
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte usuário para dicionário"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "phone": self.phone,
            "country": self.country,
            "timezone": self.timezone,
            "language": self.language,
            "email_notifications": self.email_notifications,
            "telegram_notifications": self.telegram_notifications,
            "default_currency": self.default_currency,
            "min_bet_amount": self.min_bet_amount,
            "max_bet_amount": self.max_bet_amount,
            "risk_tolerance": self.risk_tolerance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class UserSession(Base):
    """Sessões de usuário"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
    
    def is_expired(self) -> bool:
        """Verifica se sessão expirou"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte sessão para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_token": self.session_token,
            "ip_address": self.ip_address,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }

class PasswordReset(Base):
    """Tokens de reset de senha"""
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, used={self.is_used})>"
    
    def is_expired(self) -> bool:
        """Verifica se token expirou"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte reset para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "is_used": self.is_used,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "used_at": self.used_at.isoformat() if self.used_at else None
        }

class UserActivity(Base):
    """Log de atividades do usuário"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # login, logout, password_change, etc.
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON com dados adicionais
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte atividade para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Schemas Pydantic para validação
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Schema base para usuário"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: str = "Africa/Luanda"
    language: str = "pt"
    email_notifications: bool = True
    telegram_notifications: bool = False
    telegram_chat_id: Optional[str] = None
    default_currency: str = "AOA"
    min_bet_amount: str = "10.0"
    max_bet_amount: str = "10000.0"
    risk_tolerance: str = "medium"
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username deve ter pelo menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('Username deve ter no máximo 50 caracteres')
        if not v.isalnum():
            raise ValueError('Username deve conter apenas letras e números')
        return v.lower()
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Risk tolerance deve ser low, medium ou high')
        return v

class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if len(v) > 128:
            raise ValueError('Senha deve ter no máximo 128 caracteres')
        return v

class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    email_notifications: Optional[bool] = None
    telegram_notifications: Optional[bool] = None
    telegram_chat_id: Optional[str] = None
    default_currency: Optional[str] = None
    min_bet_amount: Optional[str] = None
    max_bet_amount: Optional[str] = None
    risk_tolerance: Optional[str] = None

class UserResponse(UserBase):
    """Schema de resposta para usuário"""
    id: int
    role: str
    status: str
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str
    remember_me: bool = False

class UserRegister(UserCreate):
    """Schema para registro de usuário"""
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Senhas não coincidem')
        return v

class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Schema para dados do token"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None

class PasswordChange(BaseModel):
    """Schema para mudança de senha"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Senhas não coincidem')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        if len(v) > 128:
            raise ValueError('Nova senha deve ter no máximo 128 caracteres')
        return v

class PasswordResetRequest(BaseModel):
    """Schema para solicitação de reset de senha"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Senhas não coincidem')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        if len(v) > 128:
            raise ValueError('Nova senha deve ter no máximo 128 caracteres')
        return v

class UserActivityResponse(BaseModel):
    """Schema de resposta para atividade do usuário"""
    id: int
    user_id: int
    activity_type: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserSessionResponse(BaseModel):
    """Schema de resposta para sessão do usuário"""
    id: int
    user_id: int
    session_token: str
    ip_address: Optional[str] = None
    is_active: bool
    expires_at: datetime
    created_at: datetime
    last_activity: datetime
    
    class Config:
        from_attributes = True
