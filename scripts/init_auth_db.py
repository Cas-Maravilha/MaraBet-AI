#!/usr/bin/env python3
"""
Script para inicializar banco de dados de autenticação
Cria tabelas de usuários e dados iniciais
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth.models import Base, User, UserRole, UserStatus
from auth.jwt_auth import get_password_hash
from armazenamento.banco_de_dados import DATABASE_URL

def init_auth_database():
    """Inicializa banco de dados de autenticação"""
    print("🔐 Inicializando banco de dados de autenticação...")
    
    try:
        # Criar engine
        engine = create_engine(DATABASE_URL)
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas de autenticação criadas com sucesso")
        
        # Criar sessão
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Verificar se já existe usuário admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # Criar usuário administrador padrão
            admin_user = User(
                username="admin",
                email="admin@marabet.ai",
                full_name="Administrador",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                is_verified=True,
                is_superuser=True,
                default_currency="AOA",
                min_bet_amount="10.0",
                max_bet_amount="10000.0",
                risk_tolerance="medium",
                timezone="Africa/Luanda",
                language="pt",
                email_notifications=True,
                telegram_notifications=False
            )
            
            # Definir senha padrão
            admin_user.set_password("admin123")
            
            db.add(admin_user)
            db.commit()
            
            print("✅ Usuário administrador criado:")
            print(f"   Username: admin")
            print(f"   Email: admin@marabet.ai")
            print(f"   Senha: admin123")
            print("   ⚠️  ALTERE A SENHA PADRÃO IMEDIATAMENTE!")
        else:
            print("ℹ️  Usuário administrador já existe")
        
        # Criar usuário de demonstração
        demo_user = db.query(User).filter(User.username == "demo").first()
        
        if not demo_user:
            demo_user = User(
                username="demo",
                email="demo@marabet.ai",
                full_name="Usuário Demonstração",
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                is_verified=True,
                is_superuser=False,
                default_currency="AOA",
                min_bet_amount="10.0",
                max_bet_amount="1000.0",
                risk_tolerance="medium",
                timezone="Africa/Luanda",
                language="pt",
                email_notifications=True,
                telegram_notifications=False
            )
            
            # Definir senha padrão
            demo_user.set_password("demo123")
            
            db.add(demo_user)
            db.commit()
            
            print("✅ Usuário de demonstração criado:")
            print(f"   Username: demo")
            print(f"   Email: demo@marabet.ai")
            print(f"   Senha: demo123")
        else:
            print("ℹ️  Usuário de demonstração já existe")
        
        # Listar usuários criados
        users = db.query(User).all()
        print(f"\n📊 Total de usuários no sistema: {len(users)}")
        
        for user in users:
            print(f"   • {user.username} ({user.email}) - {user.role.value}")
        
        db.close()
        print("\n🎉 Banco de dados de autenticação inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        sys.exit(1)

def create_test_users():
    """Cria usuários de teste"""
    print("\n🧪 Criando usuários de teste...")
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        test_users = [
            {
                "username": "moderator1",
                "email": "moderator1@marabet.ai",
                "full_name": "Moderador 1",
                "role": UserRole.MODERATOR,
                "password": "mod123"
            },
            {
                "username": "user1",
                "email": "user1@marabet.ai",
                "full_name": "Usuário 1",
                "role": UserRole.USER,
                "password": "user123"
            },
            {
                "username": "viewer1",
                "email": "viewer1@marabet.ai",
                "full_name": "Visualizador 1",
                "role": UserRole.VIEWER,
                "password": "view123"
            }
        ]
        
        for user_data in test_users:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            
            if not existing_user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    status=UserStatus.ACTIVE,
                    is_verified=True,
                    is_superuser=False,
                    default_currency="AOA",
                    min_bet_amount="10.0",
                    max_bet_amount="5000.0",
                    risk_tolerance="medium",
                    timezone="Africa/Luanda",
                    language="pt",
                    email_notifications=True,
                    telegram_notifications=False
                )
                
                user.set_password(user_data["password"])
                db.add(user)
                
                print(f"✅ Usuário {user_data['username']} criado (senha: {user_data['password']})")
            else:
                print(f"ℹ️  Usuário {user_data['username']} já existe")
        
        db.commit()
        db.close()
        
        print("🎉 Usuários de teste criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários de teste: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicializar banco de dados de autenticação')
    parser.add_argument('--test-users', action='store_true', help='Criar usuários de teste')
    
    args = parser.parse_args()
    
    # Inicializar banco de dados
    init_auth_database()
    
    # Criar usuários de teste se solicitado
    if args.test_users:
        create_test_users()
    
    print("\n📋 Próximos passos:")
    print("1. Acesse o dashboard: http://localhost:8000")
    print("2. Faça login com admin/admin123")
    print("3. Altere a senha padrão do administrador")
    print("4. Configure as permissões de usuários")
    print("5. Teste o sistema de autenticação")

if __name__ == '__main__':
    main()
