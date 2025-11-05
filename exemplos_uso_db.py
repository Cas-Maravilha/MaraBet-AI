"""
MaraBet AI - Exemplos de Uso do Database Config
Demonstra como usar o módulo db_config.py em diferentes cenários
"""

# =============================================================================
# EXEMPLO 1: USO DIRETO COM PSYCOPG2
# =============================================================================

def exemplo_psycopg2():
    """Exemplo com psycopg2 puro"""
    import psycopg2
    from db_config import get_credentials, db_config
    
    # Obter configuração
    config = db_config.get_psycopg2_config()
    
    # Conectar
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    
    # Executar query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL: {version[0]}")
    
    # Criar tabela
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Inserir dados
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        ("Admin MaraBet", "admin@marabet.ao")
    )
    
    # Commit e fechar
    conn.commit()
    cursor.close()
    conn.close()


# =============================================================================
# EXEMPLO 2: SQLAlchemy
# =============================================================================

def exemplo_sqlalchemy():
    """Exemplo com SQLAlchemy ORM"""
    from sqlalchemy import create_engine, Column, Integer, String, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    from db_config import get_connection_string
    
    # Criar engine
    engine = create_engine(get_connection_string())
    
    # Base para modelos
    Base = declarative_base()
    
    # Definir modelo
    class User(Base):
        __tablename__ = 'users'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        email = Column(String(100))
        created_at = Column(DateTime, default=datetime.now)
    
    # Criar tabelas
    Base.metadata.create_all(engine)
    
    # Criar sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Inserir dados
    user = User(name="Admin MaraBet", email="admin@marabet.ao")
    session.add(user)
    session.commit()
    
    # Consultar
    users = session.query(User).all()
    for user in users:
        print(f"User: {user.name} ({user.email})")
    
    session.close()


# =============================================================================
# EXEMPLO 3: Django Settings
# =============================================================================

def exemplo_django_settings():
    """Exemplo de configuração para Django"""
    from db_config import db_config
    
    # settings.py
    DATABASES = {
        'default': db_config.get_django_config()
    }
    
    print("Django DATABASES configurado:")
    print(DATABASES)


# =============================================================================
# EXEMPLO 4: Flask-SQLAlchemy
# =============================================================================

def exemplo_flask():
    """Exemplo com Flask"""
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from db_config import get_connection_string
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_string()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Definir modelo
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
        email = db.Column(db.String(100))
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
        
        # Inserir dados
        user = User(name="Admin MaraBet", email="admin@marabet.ao")
        db.session.add(user)
        db.session.commit()
        
        # Consultar
        users = User.query.all()
        for user in users:
            print(f"User: {user.name}")


# =============================================================================
# EXEMPLO 5: FastAPI
# =============================================================================

def exemplo_fastapi():
    """Exemplo com FastAPI"""
    from fastapi import FastAPI, Depends
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from db_config import get_connection_string
    
    # Database
    engine = create_engine(get_connection_string())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Modelo
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String)
        email = Column(String)
    
    Base.metadata.create_all(bind=engine)
    
    # App
    app = FastAPI()
    
    # Dependency
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Routes
    @app.get("/users")
    def read_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    
    print("FastAPI app configurada com RDS")


# =============================================================================
# EXEMPLO 6: Pandas
# =============================================================================

def exemplo_pandas():
    """Exemplo com Pandas para análise de dados"""
    import pandas as pd
    from sqlalchemy import create_engine
    from db_config import get_connection_string
    
    # Criar engine
    engine = create_engine(get_connection_string())
    
    # Ler dados
    df = pd.read_sql("SELECT * FROM users", engine)
    print(df)
    
    # Escrever dados
    new_data = pd.DataFrame({
        'name': ['User 1', 'User 2'],
        'email': ['user1@marabet.ao', 'user2@marabet.ao']
    })
    new_data.to_sql('users', engine, if_exists='append', index=False)


# =============================================================================
# EXEMPLO 7: Context Manager
# =============================================================================

class DatabaseConnection:
    """Context manager para conexões ao banco"""
    
    def __init__(self):
        from db_config import db_config
        self.config = db_config.get_psycopg2_config()
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        import psycopg2
        self.conn = psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()


def exemplo_context_manager():
    """Exemplo usando context manager"""
    
    # Uso simples e seguro
    with DatabaseConnection() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            print(user)


# =============================================================================
# EXEMPLO 8: Async com asyncpg
# =============================================================================

async def exemplo_asyncpg():
    """Exemplo assíncrono com asyncpg"""
    import asyncpg
    from db_config import get_credentials
    
    creds = get_credentials()
    
    # Conectar
    conn = await asyncpg.connect(
        host=creds['host'],
        port=int(creds['port']),
        user=creds['username'],
        password=creds['password'],
        database='marabet_production',
        ssl='require'
    )
    
    # Executar query
    rows = await conn.fetch('SELECT * FROM users')
    for row in rows:
        print(row)
    
    # Fechar
    await conn.close()


# =============================================================================
# EXEMPLO 9: Alembic Migrations
# =============================================================================

def exemplo_alembic_config():
    """Configuração para Alembic (migrations)"""
    from db_config import get_connection_string
    
    # alembic.ini ou alembic/env.py
    config = {
        'sqlalchemy.url': get_connection_string()
    }
    
    print("Alembic configurado:")
    print(config)


# =============================================================================
# EXEMPLO 10: Backup e Restore
# =============================================================================

def exemplo_backup():
    """Exemplo de backup do banco"""
    import subprocess
    from db_config import get_credentials
    from datetime import datetime
    
    creds = get_credentials()
    
    # Nome do arquivo de backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_marabet_{timestamp}.sql"
    
    # Comando pg_dump
    cmd = [
        'pg_dump',
        '-h', creds['host'],
        '-p', str(creds['port']),
        '-U', creds['username'],
        '-d', 'marabet_production',
        '-F', 'c',  # Custom format
        '-f', backup_file
    ]
    
    # Exportar senha
    env = {'PGPASSWORD': creds['password']}
    
    # Executar
    subprocess.run(cmd, env=env)
    
    print(f"✅ Backup criado: {backup_file}")


# =============================================================================
# EXEMPLO 11: Health Check
# =============================================================================

def health_check():
    """Verifica saúde do banco de dados"""
    import psycopg2
    from db_config import db_config
    
    try:
        config = db_config.get_psycopg2_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Verificar versão
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Verificar databases
        cursor.execute("SELECT datname FROM pg_database;")
        databases = cursor.fetchall()
        
        # Verificar conexões ativas
        cursor.execute("SELECT count(*) FROM pg_stat_activity;")
        connections = cursor.fetchone()[0]
        
        # Verificar tamanho do database
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size('marabet_production'));
        """)
        size = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'status': 'healthy',
            'version': version,
            'databases': len(databases),
            'active_connections': connections,
            'database_size': size
        }
    
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


# =============================================================================
# MAIN - MENU INTERATIVO
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🗄️  MARABET AI - EXEMPLOS DE USO DO DATABASE")
    print("=" * 70)
    print()
    print("Exemplos disponíveis:")
    print("  1. psycopg2 (puro)")
    print("  2. SQLAlchemy")
    print("  3. Django")
    print("  4. Flask")
    print("  5. FastAPI")
    print("  6. Pandas")
    print("  7. Context Manager")
    print("  8. Health Check")
    print()
    
    escolha = input("Escolha um exemplo (1-8): ")
    
    print()
    print("-" * 70)
    
    if escolha == '1':
        print("Executando exemplo psycopg2...")
        exemplo_psycopg2()
    elif escolha == '2':
        print("Executando exemplo SQLAlchemy...")
        exemplo_sqlalchemy()
    elif escolha == '3':
        print("Mostrando configuração Django...")
        exemplo_django_settings()
    elif escolha == '4':
        print("Mostrando configuração Flask...")
        print("(Flask app não será iniciado neste exemplo)")
    elif escolha == '5':
        print("Mostrando configuração FastAPI...")
        exemplo_fastapi()
    elif escolha == '6':
        print("Executando exemplo Pandas...")
        exemplo_pandas()
    elif escolha == '7':
        print("Executando exemplo Context Manager...")
        exemplo_context_manager()
    elif escolha == '8':
        print("Executando Health Check...")
        result = health_check()
        print()
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print("Opção inválida")
    
    print()
    print("-" * 70)
    print("✅ Exemplo concluído!")

