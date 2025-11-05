"""
Testes de integração para sistema de autenticação
Testa fluxos completos de login, registro e gerenciamento de usuários
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from auth.models import User, UserRole, UserStatus
from auth.jwt_auth import create_access_token, verify_token
from auth.endpoints import router as auth_router

class TestAuthenticationFlow:
    """Testes de integração para fluxo de autenticação"""
    
    def test_user_registration_flow(self, test_client):
        """Testa fluxo completo de registro de usuário"""
        # Dados de registro
        registration_data = {
            "username": "newuser",
            "email": "newuser@marabet.ai",
            "password": "newpass123",
            "confirm_password": "newpass123",
            "full_name": "New User",
            "phone": "+244123456789",
            "country": "AO",
            "default_currency": "AOA",
            "risk_tolerance": "medium"
        }
        
        # Fazer registro
        response = test_client.post("/auth/register", json=registration_data)
        
        # Verificações
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@marabet.ai"
        assert data["role"] == "user"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
    
    def test_user_login_flow(self, test_client, test_user):
        """Testa fluxo completo de login de usuário"""
        # Dados de login
        login_data = {
            "username": test_user.username,
            "password": "testpass123",
            "remember_me": False
        }
        
        # Fazer login
        response = test_client.post("/auth/login", json=login_data)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        
        # Verificar token
        token = data["access_token"]
        payload = verify_token(token, "access")
        assert payload["user_id"] == test_user.id
        assert payload["username"] == test_user.username
        assert payload["role"] == test_user.role.value
    
    def test_protected_endpoint_access(self, test_client, auth_headers):
        """Testa acesso a endpoints protegidos"""
        # Tentar acessar endpoint protegido sem token
        response = test_client.get("/api/stats")
        assert response.status_code == 401
        
        # Acessar endpoint protegido com token
        response = test_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_matches" in data
        assert "total_odds" in data
        assert "total_predictions" in data
    
    def test_token_refresh_flow(self, test_client, test_user):
        """Testa fluxo de renovação de token"""
        # Fazer login para obter tokens
        login_data = {
            "username": test_user.username,
            "password": "testpass123"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Renovar token
        refresh_data = {"refresh_token": refresh_token}
        response = test_client.post("/auth/refresh", json=refresh_data)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Verificar que o novo token funciona
        new_token = data["access_token"]
        headers = {"Authorization": f"Bearer {new_token}"}
        response = test_client.get("/api/stats", headers=headers)
        assert response.status_code == 200
    
    def test_logout_flow(self, test_client, auth_headers):
        """Testa fluxo de logout"""
        # Fazer logout
        response = test_client.post("/auth/logout", headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout realizado com sucesso"
    
    def test_password_change_flow(self, test_client, auth_headers):
        """Testa fluxo de mudança de senha"""
        # Dados de mudança de senha
        password_data = {
            "current_password": "testpass123",
            "new_password": "newpass456",
            "confirm_password": "newpass456"
        }
        
        # Alterar senha
        response = test_client.post("/auth/change-password", json=password_data, headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Senha alterada com sucesso"
        
        # Tentar fazer login com nova senha
        login_data = {
            "username": "testuser",
            "password": "newpass456"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        # Tentar fazer login com senha antiga
        old_login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        old_login_response = test_client.post("/auth/login", json=old_login_data)
        assert old_login_response.status_code == 401

class TestUserManagement:
    """Testes de integração para gerenciamento de usuários"""
    
    def test_get_current_user_info(self, test_client, auth_headers, test_user):
        """Testa obtenção de informações do usuário atual"""
        response = test_client.get("/auth/me", headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value
        assert data["status"] == test_user.status.value
    
    def test_update_user_profile(self, test_client, auth_headers, test_user):
        """Testa atualização de perfil do usuário"""
        # Dados de atualização
        update_data = {
            "full_name": "Updated Name",
            "phone": "+244987654321",
            "country": "BR",
            "timezone": "America/Sao_Paulo",
            "language": "pt-BR",
            "default_currency": "BRL",
            "risk_tolerance": "high"
        }
        
        # Atualizar perfil
        response = test_client.put("/auth/me", json=update_data, headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["phone"] == "+244987654321"
        assert data["country"] == "BR"
        assert data["timezone"] == "America/Sao_Paulo"
        assert data["language"] == "pt-BR"
        assert data["default_currency"] == "BRL"
        assert data["risk_tolerance"] == "high"
    
    def test_admin_user_management(self, test_client, admin_headers, test_user):
        """Testa gerenciamento de usuários por admin"""
        # Listar usuários
        response = test_client.get("/auth/users", headers=admin_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Pelo menos o usuário de teste
        
        # Buscar usuário específico
        response = test_client.get(f"/auth/users/{test_user.id}", headers=admin_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
    
    def test_admin_update_user(self, test_client, admin_headers, test_user):
        """Testa atualização de usuário por admin"""
        # Dados de atualização
        update_data = {
            "full_name": "Admin Updated Name",
            "role": "moderator",
            "status": "active"
        }
        
        # Atualizar usuário
        response = test_client.put(f"/auth/users/{test_user.id}", json=update_data, headers=admin_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Admin Updated Name"
        assert data["role"] == "moderator"
        assert data["status"] == "active"
    
    def test_admin_delete_user(self, test_client, admin_headers, test_db):
        """Testa deleção de usuário por admin"""
        # Criar usuário para deletar
        user_to_delete = User(
            username="tobedeleted",
            email="delete@marabet.ai",
            full_name="To Be Deleted",
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        user_to_delete.set_password("deletepass123")
        test_db.add(user_to_delete)
        test_db.commit()
        test_db.refresh(user_to_delete)
        
        # Deletar usuário
        response = test_client.delete(f"/auth/users/{user_to_delete.id}", headers=admin_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usuário deletado com sucesso"
        
        # Verificar se usuário foi deletado
        deleted_user = test_db.query(User).filter(User.id == user_to_delete.id).first()
        assert deleted_user is None
    
    def test_non_admin_cannot_manage_users(self, test_client, auth_headers):
        """Testa que usuários não-admin não podem gerenciar outros usuários"""
        # Tentar listar usuários
        response = test_client.get("/auth/users", headers=auth_headers)
        assert response.status_code == 403
        
        # Tentar buscar usuário
        response = test_client.get("/auth/users/1", headers=auth_headers)
        assert response.status_code == 403
        
        # Tentar atualizar usuário
        response = test_client.put("/auth/users/1", json={"full_name": "Test"}, headers=auth_headers)
        assert response.status_code == 403
        
        # Tentar deletar usuário
        response = test_client.delete("/auth/users/1", headers=auth_headers)
        assert response.status_code == 403

class TestPasswordReset:
    """Testes de integração para reset de senha"""
    
    def test_forgot_password_flow(self, test_client, test_user):
        """Testa fluxo de solicitação de reset de senha"""
        # Solicitar reset
        reset_data = {"email": test_user.email}
        response = test_client.post("/auth/forgot-password", json=reset_data)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Se o email existir, você receberá instruções para reset de senha"
    
    def test_forgot_password_invalid_email(self, test_client):
        """Testa solicitação de reset com email inválido"""
        # Solicitar reset com email inexistente
        reset_data = {"email": "nonexistent@marabet.ai"}
        response = test_client.post("/auth/forgot-password", json=reset_data)
        
        # Verificações (deve retornar mesma mensagem por segurança)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Se o email existir, você receberá instruções para reset de senha"
    
    def test_reset_password_flow(self, test_client, test_user, test_db):
        """Testa fluxo completo de reset de senha"""
        from auth.models import PasswordReset
        
        # Criar token de reset
        reset_token = "test-reset-token-123"
        password_reset = PasswordReset(
            user_id=test_user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        test_db.add(password_reset)
        test_db.commit()
        
        # Confirmar reset
        reset_data = {
            "token": reset_token,
            "new_password": "newresetpass123",
            "confirm_password": "newresetpass123"
        }
        
        response = test_client.post("/auth/reset-password", json=reset_data)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Senha alterada com sucesso"
        
        # Verificar se token foi marcado como usado
        used_reset = test_db.query(PasswordReset).filter(PasswordReset.token == reset_token).first()
        assert used_reset.is_used == True
        assert used_reset.used_at is not None
        
        # Verificar se login funciona com nova senha
        login_data = {
            "username": test_user.username,
            "password": "newresetpass123"
        }
        
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
    
    def test_reset_password_invalid_token(self, test_client):
        """Testa reset de senha com token inválido"""
        # Tentar reset com token inválido
        reset_data = {
            "token": "invalid-token",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        }
        
        response = test_client.post("/auth/reset-password", json=reset_data)
        
        # Verificações
        assert response.status_code == 400
        data = response.json()
        assert "Token inválido ou expirado" in data["detail"]

class TestUserActivities:
    """Testes de integração para atividades de usuário"""
    
    def test_user_activities_logging(self, test_client, auth_headers, test_user):
        """Testa logging de atividades do usuário"""
        # Fazer algumas ações que geram atividades
        test_client.get("/auth/me", headers=auth_headers)
        test_client.get("/api/stats", headers=auth_headers)
        
        # Buscar atividades
        response = test_client.get("/auth/activities", headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verificar tipos de atividades
        activity_types = [activity["activity_type"] for activity in data]
        assert "user_login" in activity_types
    
    def test_user_sessions_management(self, test_client, auth_headers, test_user):
        """Testa gerenciamento de sessões do usuário"""
        # Buscar sessões ativas
        response = test_client.get("/auth/sessions", headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verificar dados da sessão
        session = data[0]
        assert "id" in session
        assert "user_id" in session
        assert "is_active" in session
        assert "created_at" in session
        assert "last_activity" in session
    
    def test_revoke_session(self, test_client, auth_headers, test_user, test_db):
        """Testa revogação de sessão específica"""
        from auth.models import UserSession
        
        # Criar sessão de teste
        test_session = UserSession(
            user_id=test_user.id,
            session_token="test-session-token",
            refresh_token="test-refresh-token",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        test_db.add(test_session)
        test_db.commit()
        test_db.refresh(test_session)
        
        # Revogar sessão
        response = test_client.delete(f"/auth/sessions/{test_session.id}", headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Sessão revogada com sucesso"
        
        # Verificar se sessão foi desativada
        revoked_session = test_db.query(UserSession).filter(UserSession.id == test_session.id).first()
        assert revoked_session.is_active == False
    
    def test_revoke_all_sessions(self, test_client, auth_headers, test_user, test_db):
        """Testa revogação de todas as sessões"""
        from auth.models import UserSession
        
        # Criar múltiplas sessões
        for i in range(3):
            session = UserSession(
                user_id=test_user.id,
                session_token=f"test-session-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            test_db.add(session)
        test_db.commit()
        
        # Revogar todas as sessões
        response = test_client.post("/auth/sessions/revoke-all", headers=auth_headers)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "sessões revogadas com sucesso" in data["message"]
        assert "3" in data["message"]  # 3 sessões revogadas
        
        # Verificar se todas as sessões foram desativadas
        active_sessions = test_db.query(UserSession).filter(
            UserSession.user_id == test_user.id,
            UserSession.is_active == True
        ).all()
        assert len(active_sessions) == 0

class TestRoleBasedAccess:
    """Testes de integração para controle de acesso baseado em roles"""
    
    def test_admin_access_to_all_endpoints(self, test_client, admin_headers):
        """Testa que admin tem acesso a todos os endpoints"""
        # Endpoints de usuário
        response = test_client.get("/auth/me", headers=admin_headers)
        assert response.status_code == 200
        
        # Endpoints de admin
        response = test_client.get("/auth/users", headers=admin_headers)
        assert response.status_code == 200
        
        # Endpoints de API
        response = test_client.get("/api/stats", headers=admin_headers)
        assert response.status_code == 200
        
        # Endpoints administrativos
        response = test_client.post("/api/collector/start", headers=admin_headers)
        assert response.status_code == 200
    
    def test_user_access_restrictions(self, test_client, auth_headers):
        """Testa que usuário comum tem acesso restrito"""
        # Endpoints de usuário (permitidos)
        response = test_client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        response = test_client.get("/api/stats", headers=auth_headers)
        assert response.status_code == 200
        
        # Endpoints de admin (negados)
        response = test_client.get("/auth/users", headers=auth_headers)
        assert response.status_code == 403
        
        # Endpoints administrativos (negados)
        response = test_client.post("/api/collector/start", headers=auth_headers)
        assert response.status_code == 403
    
    def test_viewer_access_restrictions(self, test_client, test_db):
        """Testa que viewer tem acesso muito restrito"""
        # Criar usuário viewer
        viewer_user = User(
            username="viewer",
            email="viewer@marabet.ai",
            full_name="Viewer User",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE
        )
        viewer_user.set_password("viewerpass123")
        test_db.add(viewer_user)
        test_db.commit()
        
        # Fazer login
        login_data = {
            "username": "viewer",
            "password": "viewerpass123"
        }
        login_response = test_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        viewer_token = login_response.json()["access_token"]
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        
        # Endpoints básicos (permitidos)
        response = test_client.get("/auth/me", headers=viewer_headers)
        assert response.status_code == 200
        
        # Endpoints de API (pode ser restrito dependendo da implementação)
        response = test_client.get("/api/stats", headers=viewer_headers)
        # Pode ser 200 ou 403 dependendo da implementação
        
        # Endpoints de admin (negados)
        response = test_client.get("/auth/users", headers=viewer_headers)
        assert response.status_code == 403

class TestSecurityFeatures:
    """Testes de integração para recursos de segurança"""
    
    def test_token_expiration(self, test_client, test_user):
        """Testa expiração de token"""
        # Criar token com expiração muito curta
        with patch('auth.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES', 0.001):  # 0.06 segundos
            token = create_access_token({
                "user_id": test_user.id,
                "username": test_user.username,
                "role": test_user.role.value
            })
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Aguardar expiração
            import time
            time.sleep(0.1)
            
            # Tentar usar token expirado
            response = test_client.get("/api/stats", headers=headers)
            assert response.status_code == 401
    
    def test_invalid_token_handling(self, test_client):
        """Testa tratamento de token inválido"""
        # Token malformado
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.get("/api/stats", headers=headers)
        assert response.status_code == 401
        
        # Token sem Bearer
        headers = {"Authorization": "invalid-token"}
        response = test_client.get("/api/stats", headers=headers)
        assert response.status_code == 401
        
        # Sem token
        response = test_client.get("/api/stats")
        assert response.status_code == 401
    
    def test_password_validation(self, test_client):
        """Testa validação de senha"""
        # Senha muito curta
        registration_data = {
            "username": "testuser2",
            "email": "test2@marabet.ai",
            "password": "123",
            "confirm_password": "123"
        }
        
        response = test_client.post("/auth/register", json=registration_data)
        assert response.status_code == 400
        assert "Senha deve ter pelo menos 8 caracteres" in response.json()["detail"]
        
        # Senhas não coincidem
        registration_data = {
            "username": "testuser3",
            "email": "test3@marabet.ai",
            "password": "password123",
            "confirm_password": "password456"
        }
        
        response = test_client.post("/auth/register", json=registration_data)
        assert response.status_code == 400
        assert "Senhas não coincidem" in response.json()["detail"]
    
    def test_username_email_uniqueness(self, test_client, test_user):
        """Testa unicidade de username e email"""
        # Username duplicado
        registration_data = {
            "username": test_user.username,  # Username já existe
            "email": "newemail@marabet.ai",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        response = test_client.post("/auth/register", json=registration_data)
        assert response.status_code == 400
        assert "Username já está em uso" in response.json()["detail"]
        
        # Email duplicado
        registration_data = {
            "username": "newusername",
            "email": test_user.email,  # Email já existe
            "password": "password123",
            "confirm_password": "password123"
        }
        
        response = test_client.post("/auth/register", json=registration_data)
        assert response.status_code == 400
        assert "Email já está em uso" in response.json()["detail"]
