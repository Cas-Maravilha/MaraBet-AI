"""
Endpoints de Autenticação para MaraBet AI
Sistema completo de login, registro, gerenciamento de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from auth.models import (
    User, UserSession, UserActivity, PasswordReset,
    UserCreate, UserUpdate, UserResponse, UserLogin, UserRegister,
    Token, PasswordChange, PasswordResetRequest, PasswordResetConfirm,
    UserActivityResponse, UserSessionResponse, UserRole, UserStatus
)
from auth.jwt_auth import (
    jwt_auth, authenticate_user, get_user_by_id, get_user_by_username,
    get_user_by_email, create_user_session, get_active_session,
    deactivate_session, deactivate_all_user_sessions, cleanup_expired_sessions,
    get_current_user, get_current_active_user, require_role, require_superuser,
    generate_password_reset_token, verify_password_reset_token,
    generate_email_verification_token, verify_email_verification_token,
    log_user_activity, validate_password_strength, get_password_hash
)
from armazenamento.banco_de_dados import get_db

# Configuração do router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Logger
logger = logging.getLogger(__name__)

# =============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# =============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registra novo usuário no sistema
    """
    try:
        # Verifica se username já existe
        existing_user = get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já está em uso"
            )
        
        # Verifica se email já existe
        existing_email = get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Valida força da senha
        password_validation = validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Senha muito fraca: {', '.join(password_validation['feedback'])}"
            )
        
        # Cria novo usuário
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            country=user_data.country,
            timezone=user_data.timezone,
            language=user_data.language,
            email_notifications=user_data.email_notifications,
            telegram_notifications=user_data.telegram_notifications,
            telegram_chat_id=user_data.telegram_chat_id,
            default_currency=user_data.default_currency,
            min_bet_amount=user_data.min_bet_amount,
            max_bet_amount=user_data.max_bet_amount,
            risk_tolerance=user_data.risk_tolerance,
            role=UserRole.USER,
            status=UserStatus.PENDING
        )
        
        # Define senha
        db_user.set_password(user_data.password)
        
        # Salva no banco
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Log da atividade
        log_user_activity(
            db, db_user.id, "user_registered",
            f"Usuário {db_user.username} registrado",
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        logger.info(f"Novo usuário registrado: {db_user.username} ({db_user.email})")
        
        return UserResponse.from_orm(db_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna tokens JWT
    """
    try:
        # Autentica usuário
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        
        # Verifica se usuário está ativo
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Conta inativa. Entre em contato com o suporte"
            )
        
        # Atualiza último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Cria sessão
        session = create_user_session(
            db, user.id,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        # Gera tokens
        tokens = jwt_auth.create_token_pair(user)
        
        # Log da atividade
        log_user_activity(
            db, user.id, "user_login",
            f"Usuário {user.username} fez login",
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        logger.info(f"Usuário {user.username} fez login")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Desloga usuário e invalida sessão
    """
    try:
        # Aqui você pode implementar lógica para invalidar o token
        # Por simplicidade, vamos apenas logar a atividade
        
        log_user_activity(
            db, current_user["user_id"], "user_logout",
            f"Usuário {current_user['username']} fez logout",
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        logger.info(f"Usuário {current_user['username']} fez logout")
        
        return {"message": "Logout realizado com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Renova token de acesso usando refresh token
    """
    try:
        # Verifica refresh token
        new_access_token = jwt_auth.refresh_access_token(refresh_token)
        
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": jwt_auth.access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# =============================================================================
# ENDPOINTS DE GERENCIAMENTO DE USUÁRIOS
# =============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retorna informações do usuário atual
    """
    try:
        user = get_user_by_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar usuário atual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza informações do usuário atual
    """
    try:
        user = get_user_by_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Atualiza campos fornecidos
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Log da atividade
        log_user_activity(
            db, user.id, "user_updated",
            f"Usuário {user.username} atualizou perfil"
        )
        
        logger.info(f"Usuário {user.username} atualizou perfil")
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Altera senha do usuário atual
    """
    try:
        user = get_user_by_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verifica senha atual
        if not user.verify_password(password_data.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Valida nova senha
        password_validation = validate_password_strength(password_data.new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Senha muito fraca: {', '.join(password_validation['feedback'])}"
            )
        
        # Atualiza senha
        user.set_password(password_data.new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Log da atividade
        log_user_activity(
            db, user.id, "password_changed",
            f"Usuário {user.username} alterou senha"
        )
        
        logger.info(f"Usuário {user.username} alterou senha")
        
        return {"message": "Senha alterada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# =============================================================================
# ENDPOINTS DE RESET DE SENHA
# =============================================================================

@router.post("/forgot-password")
async def forgot_password(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita reset de senha
    """
    try:
        user = get_user_by_email(db, reset_request.email)
        
        if not user:
            # Por segurança, não revela se email existe
            return {"message": "Se o email existir, você receberá instruções para reset de senha"}
        
        # Gera token de reset
        reset_token = generate_password_reset_token(user.id)
        
        # Salva token no banco
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        db.add(password_reset)
        db.commit()
        
        # Aqui você enviaria o email com o token
        # Por simplicidade, vamos apenas logar
        logger.info(f"Token de reset gerado para {user.email}: {reset_token}")
        
        return {"message": "Se o email existir, você receberá instruções para reset de senha"}
        
    except Exception as e:
        logger.error(f"Erro ao solicitar reset de senha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirma reset de senha
    """
    try:
        # Verifica token
        user_id = verify_password_reset_token(reset_data.token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado"
            )
        
        # Busca usuário
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Valida nova senha
        password_validation = validate_password_strength(reset_data.new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Senha muito fraca: {', '.join(password_validation['feedback'])}"
            )
        
        # Atualiza senha
        user.set_password(reset_data.new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Invalida token
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.token == reset_data.token
        ).first()
        
        if password_reset:
            password_reset.is_used = True
            password_reset.used_at = datetime.utcnow()
            db.commit()
        
        # Log da atividade
        log_user_activity(
            db, user.id, "password_reset",
            f"Usuário {user.username} resetou senha"
        )
        
        logger.info(f"Usuário {user.username} resetou senha")
        
        return {"message": "Senha alterada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# =============================================================================
# ENDPOINTS DE ADMINISTRAÇÃO (APENAS ADMIN)
# =============================================================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários (apenas admin)
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserResponse.from_orm(user) for user in users]
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: dict = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Busca usuário por ID (apenas admin)
    """
    try:
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Atualiza usuário (apenas admin)
    """
    try:
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Atualiza campos fornecidos
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        user.updated_by = current_user["user_id"]
        db.commit()
        db.refresh(user)
        
        # Log da atividade
        log_user_activity(
            db, current_user["user_id"], "user_updated_by_admin",
            f"Admin {current_user['username']} atualizou usuário {user.username}"
        )
        
        logger.info(f"Admin {current_user['username']} atualizou usuário {user.username}")
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Deleta usuário (apenas admin)
    """
    try:
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Não permite deletar a si mesmo
        if user.id == current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível deletar sua própria conta"
            )
        
        # Log da atividade
        log_user_activity(
            db, current_user["user_id"], "user_deleted_by_admin",
            f"Admin {current_user['username']} deletou usuário {user.username}"
        )
        
        # Deleta usuário
        db.delete(user)
        db.commit()
        
        logger.info(f"Admin {current_user['username']} deletou usuário {user.username}")
        
        return {"message": "Usuário deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# =============================================================================
# ENDPOINTS DE ATIVIDADES E SESSÕES
# =============================================================================

@router.get("/activities", response_model=List[UserActivityResponse])
async def get_user_activities(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista atividades do usuário atual
    """
    try:
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == current_user["user_id"]
        ).order_by(UserActivity.created_at.desc()).offset(skip).limit(limit).all()
        
        return [UserActivityResponse.from_orm(activity) for activity in activities]
        
    except Exception as e:
        logger.error(f"Erro ao buscar atividades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/sessions", response_model=List[UserSessionResponse])
async def get_user_sessions(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista sessões ativas do usuário atual
    """
    try:
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user["user_id"],
            UserSession.is_active == True
        ).order_by(UserSession.last_activity.desc()).all()
        
        return [UserSessionResponse.from_orm(session) for session in sessions]
        
    except Exception as e:
        logger.error(f"Erro ao buscar sessões: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoga sessão específica
    """
    try:
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user["user_id"]
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        session.is_active = False
        db.commit()
        
        # Log da atividade
        log_user_activity(
            db, current_user["user_id"], "session_revoked",
            f"Usuário {current_user['username']} revogou sessão {session_id}"
        )
        
        logger.info(f"Usuário {current_user['username']} revogou sessão {session_id}")
        
        return {"message": "Sessão revogada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao revogar sessão: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoga todas as sessões do usuário atual
    """
    try:
        count = deactivate_all_user_sessions(db, current_user["user_id"])
        
        # Log da atividade
        log_user_activity(
            db, current_user["user_id"], "all_sessions_revoked",
            f"Usuário {current_user['username']} revogou todas as sessões"
        )
        
        logger.info(f"Usuário {current_user['username']} revogou {count} sessões")
        
        return {"message": f"{count} sessões revogadas com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao revogar todas as sessões: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
