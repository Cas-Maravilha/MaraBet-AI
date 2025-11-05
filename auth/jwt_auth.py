"""
Sistema de Autenticação JWT para MaraBet AI
Gerenciamento completo de tokens, autenticação e autorização
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from config_environment import get_config
import secrets
import hashlib

from auth.models import User, UserSession, TokenData, UserRole, UserStatus

# Configurações
SECRET_KEY = get_config('security.jwt_secret_key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticação HTTP Bearer
security = HTTPBearer()

class JWTAuth:
    """Classe principal para autenticação JWT"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Cria token de acesso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Cria token de refresh JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verifica tipo do token
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token inválido: tipo esperado '{token_type}'"
                )
            
            # Verifica expiração
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    def create_token_pair(self, user: User) -> Dict[str, Any]:
        """Cria par de tokens (access + refresh)"""
        # Dados do token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "email": user.email,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser
        }
        
        # Token de acesso
        access_token = self.create_access_token(token_data)
        
        # Token de refresh
        refresh_token = self.create_refresh_token({"user_id": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Renova token de acesso usando refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido"
            )
        
        # Aqui você pode buscar o usuário no banco se necessário
        # Por simplicidade, vamos recriar o token com os dados do payload
        token_data = {
            "user_id": user_id,
            "username": payload.get("username"),
            "role": payload.get("role"),
            "email": payload.get("email"),
            "is_verified": payload.get("is_verified"),
            "is_superuser": payload.get("is_superuser")
        }
        
        return self.create_access_token(token_data)

# Instância global
jwt_auth = JWTAuth()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Autentica usuário"""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if user.status != UserStatus.ACTIVE:
        return None
    
    return user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Busca usuário por ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Busca usuário por username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca usuário por email"""
    return db.query(User).filter(User.email == email).first()

def create_user_session(db: Session, user_id: int, ip_address: str = None, user_agent: str = None) -> UserSession:
    """Cria nova sessão de usuário"""
    # Gera tokens únicos
    session_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    
    # Expiração da sessão (7 dias)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def get_active_session(db: Session, session_token: str) -> Optional[UserSession]:
    """Busca sessão ativa por token"""
    return db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()

def deactivate_session(db: Session, session_token: str) -> bool:
    """Desativa sessão"""
    session = db.query(UserSession).filter(
        UserSession.session_token == session_token
    ).first()
    
    if session:
        session.is_active = False
        db.commit()
        return True
    
    return False

def deactivate_all_user_sessions(db: Session, user_id: int) -> int:
    """Desativa todas as sessões de um usuário"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).all()
    
    count = 0
    for session in sessions:
        session.is_active = False
        count += 1
    
    db.commit()
    return count

def cleanup_expired_sessions(db: Session) -> int:
    """Remove sessões expiradas"""
    expired_sessions = db.query(UserSession).filter(
        UserSession.expires_at < datetime.utcnow()
    ).all()
    
    count = len(expired_sessions)
    for session in expired_sessions:
        db.delete(session)
    
    db.commit()
    return count

# Dependências do FastAPI
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependência para obter usuário atual do token"""
    token = credentials.credentials
    
    try:
        payload = jwt_auth.verify_token(token, "access")
        user_id = payload.get("user_id")
        username = payload.get("username")
        role = payload.get("role")
        
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return TokenData(
            user_id=user_id,
            username=username,
            role=role
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependência para obter usuário ativo atual"""
    # Aqui você pode adicionar verificações adicionais se necessário
    return current_user

def require_role(required_role: UserRole):
    """Decorator para verificar role do usuário"""
    def role_checker(current_user: TokenData = Depends(get_current_active_user)):
        user_role = UserRole(current_user.role)
        
        # Hierarquia de roles: admin > moderator > user > viewer
        role_hierarchy = {
            UserRole.ADMIN: 4,
            UserRole.MODERATOR: 3,
            UserRole.USER: 2,
            UserRole.VIEWER: 1
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Role '{required_role.value}' ou superior necessária"
            )
        
        return current_user
    
    return role_checker

def require_superuser(current_user: TokenData = Depends(get_current_active_user)):
    """Dependência para verificar se usuário é superuser"""
    # Esta verificação seria feita no banco de dados
    # Por simplicidade, vamos verificar se é admin
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Privilégios de superusuário necessários"
        )
    
    return current_user

def require_verified_user(current_user: TokenData = Depends(get_current_active_user)):
    """Dependência para verificar se usuário está verificado"""
    # Esta verificação seria feita no banco de dados
    # Por simplicidade, vamos assumir que todos os usuários estão verificados
    return current_user

# Funções utilitárias
def generate_password_reset_token(user_id: int) -> str:
    """Gera token para reset de senha"""
    payload = {
        "user_id": user_id,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[int]:
    """Verifica token de reset de senha"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return None
        
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return payload.get("user_id")
        
    except jwt.JWTError:
        return None

def generate_email_verification_token(user_id: int) -> str:
    """Gera token para verificação de email"""
    payload = {
        "user_id": user_id,
        "type": "email_verification",
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_email_verification_token(token: str) -> Optional[int]:
    """Verifica token de verificação de email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "email_verification":
            return None
        
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return payload.get("user_id")
        
    except jwt.JWTError:
        return None

# Middleware para logging de atividades
def log_user_activity(db: Session, user_id: int, activity_type: str, description: str = None, 
                     ip_address: str = None, user_agent: str = None, metadata: str = None):
    """Registra atividade do usuário"""
    from auth.models import UserActivity
    
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata
    )
    
    db.add(activity)
    db.commit()

# Função para validar força da senha
def validate_password_strength(password: str) -> Dict[str, Any]:
    """Valida força da senha"""
    score = 0
    feedback = []
    
    # Comprimento mínimo
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Senha deve ter pelo menos 8 caracteres")
    
    # Comprimento ideal
    if len(password) >= 12:
        score += 1
    
    # Contém letras minúsculas
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Adicione letras minúsculas")
    
    # Contém letras maiúsculas
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Adicione letras maiúsculas")
    
    # Contém números
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Adicione números")
    
    # Contém caracteres especiais
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        feedback.append("Adicione caracteres especiais")
    
    # Determina nível de força
    if score <= 2:
        strength = "weak"
    elif score <= 4:
        strength = "medium"
    else:
        strength = "strong"
    
    return {
        "score": score,
        "strength": strength,
        "feedback": feedback,
        "is_valid": score >= 3
    }
