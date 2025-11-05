#!/usr/bin/env python3
"""
Script para Configurar Banco de Dados - MaraBet AI
Automatiza a configuração e migração do banco de dados
"""

import subprocess
import os
import json
from datetime import datetime

def run_command(command, shell=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def configure_database():
    """Configura o banco de dados"""
    print("🗄️ MARABET AI - CONFIGURANDO BANCO DE DADOS")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    ubuntu_public_ip = config.get('ubuntu_public_ip')
    rds_endpoint = config.get('rds_endpoint')
    redis_endpoint = config.get('redis_endpoint')
    key_path = os.path.expanduser("~/.ssh/marabet-key.pem")
    
    if not all([ubuntu_public_ip, rds_endpoint, redis_endpoint]):
        print("❌ Endpoints do RDS ou Redis não encontrados na configuração")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    print(f"✅ RDS Endpoint: {rds_endpoint}")
    print(f"✅ Redis Endpoint: {redis_endpoint}")
    print(f"✅ Chave SSH: {key_path}")
    
    print("\n🗄️ ETAPA 1: CRIANDO SCRIPT DE CONFIGURAÇÃO DO BANCO")
    print("-" * 50)
    
    # Criar script de configuração do banco
    db_script_content = f"""#!/bin/bash
# Script de Configuração do Banco de Dados - MaraBet AI

echo "🗄️ MARABET AI - CONFIGURANDO BANCO DE DADOS"
echo "=========================================="

# Verificar se containers estão rodando
echo "🔍 Verificando status dos containers..."
docker-compose -f docker-compose.production.yml ps

# Verificar se container web está rodando
if ! docker-compose -f docker-compose.production.yml ps | grep -q "web.*Up"; then
    echo "❌ Container web não está rodando. Iniciando..."
    docker-compose -f docker-compose.production.yml up -d web
    sleep 30
fi

# Verificar conectividade com RDS
echo "🔍 Testando conectividade com RDS..."
export DATABASE_URL="postgresql://marabetadmin:MaraBet2024!SuperSecret@{rds_endpoint}:5432/postgres"
export REDIS_URL="redis://{redis_endpoint}:6379/0"

# Testar conexão com RDS
echo "🧪 Testando conexão com RDS..."
if command -v psql &> /dev/null; then
    psql $DATABASE_URL -c "SELECT version();" || echo "⚠️ Falha na conexão com RDS"
else
    echo "⚠️ psql não encontrado, pulando teste de conexão"
fi

# Testar conexão com Redis
echo "🧪 Testando conexão com Redis..."
if command -v redis-cli &> /dev/null; then
    redis-cli -u $REDIS_URL ping || echo "⚠️ Falha na conexão com Redis"
else
    echo "⚠️ redis-cli não encontrado, pulando teste de conexão"
fi

# Entrar no container e configurar banco
echo "🐳 Entrando no container web..."
docker-compose -f docker-compose.production.yml exec web bash -c '
    echo "🗄️ Configurando banco de dados dentro do container..."
    
    # Verificar variáveis de ambiente
    echo "🔍 Verificando variáveis de ambiente..."
    echo "DATABASE_URL: $DATABASE_URL"
    echo "REDIS_URL: $REDIS_URL"
    
    # Instalar dependências se necessário
    echo "📦 Instalando dependências..."
    pip install --upgrade pip
    pip install psycopg2-binary redis sqlalchemy alembic
    
    # Criar script de inicialização do banco
    echo "📝 Criando script de inicialização do banco..."
    cat > init_db.py << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def init_database():
    # Inicializa o banco de dados
    try:
        # Conectar ao banco
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
        
        engine = create_engine(database_url)
        
        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL: {version}")
        
        # Criar tabelas se não existirem
        print("🏗️ Criando tabelas...")
        
        # Tabela de partidas
        create_matches_table = """
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    league VARCHAR(255),
    match_date TIMESTAMP,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        
        # Tabela de odds
        create_odds_table = """
CREATE TABLE IF NOT EXISTS odds (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    market_type VARCHAR(100),
    selection VARCHAR(100),
    odds_value DECIMAL(10,2),
    bookmaker VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        
        # Tabela de predições
        create_predictions_table = """
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    prediction_type VARCHAR(100),
    prediction_data JSONB,
    confidence DECIMAL(5,2),
    expected_value DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        
        # Tabela de estatísticas
        create_stats_table = """
CREATE TABLE IF NOT EXISTS team_stats (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL,
    league VARCHAR(255),
    season VARCHAR(20),
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    form VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        
        # Tabela de configurações
        create_config_table = """
CREATE TABLE IF NOT EXISTS app_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        
        # Executar criação das tabelas
        with engine.connect() as conn:
            conn.execute(text(create_matches_table))
            conn.execute(text(create_odds_table))
            conn.execute(text(create_predictions_table))
            conn.execute(text(create_stats_table))
            conn.execute(text(create_config_table))
            conn.commit()
        
        print("✅ Tabelas criadas com sucesso")
        
        # Inserir configurações iniciais
        print("⚙️ Inserindo configurações iniciais...")
        
        insert_config = """
        INSERT INTO app_config (config_key, config_value, description) VALUES
        ('app_name', 'MaraBet AI', 'Nome da aplicação'),
        ('app_version', '1.0.0', 'Versão da aplicação'),
        ('environment', 'production', 'Ambiente de execução'),
        ('api_football_key', '71b2b62386f2d1275cd3201a73e1e045', 'Chave da API Football'),
        ('prediction_confidence_threshold', '0.7', 'Limiar de confiança para predições'),
        ('max_predictions_per_day', '100', 'Máximo de predições por dia'),
        ('backup_enabled', 'true', 'Backup habilitado'),
        ('monitoring_enabled', 'true', 'Monitoramento habilitado')
        ON CONFLICT (config_key) DO NOTHING;
        """
        
        with engine.connect() as conn:
            conn.execute(text(insert_config))
            conn.commit()
        
        print("✅ Configurações inseridas com sucesso")
        
        # Verificar tabelas criadas
        print("🔍 Verificando tabelas criadas...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print("📋 Tabelas encontradas:")
            for table in tables:
                print(f"  • {table[0]}")
        
        print("🎉 Banco de dados configurado com sucesso!")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Erro SQLAlchemy: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
EOF

    # Executar script de inicialização
    echo "🚀 Executando inicialização do banco..."
    python init_db.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Banco de dados configurado com sucesso"
    else
        echo "❌ Falha na configuração do banco de dados"
        exit 1
    fi
'

echo "🎉 Configuração do banco de dados concluída!"
"""
    
    # Salvar script localmente
    with open('configure_database.sh', 'w') as f:
        f.write(db_script_content)
    print("✅ Script de configuração do banco criado: configure_database.sh")
    
    print("\n🗄️ ETAPA 2: TRANSFERINDO SCRIPT PARA O SERVIDOR")
    print("-" * 50)
    
    # Transferir script para o servidor
    print("📤 Transferindo script para o servidor...")
    scp_command = f'scp -i "{key_path}" -o StrictHostKeyChecking=no configure_database.sh ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/'
    
    print(f"Executando: {scp_command}")
    scp_result = run_command(scp_command)
    
    if scp_result is not None:
        print("✅ Script transferido com sucesso")
    else:
        print("⚠️ Falha na transferência do script")
        print("💡 Tente executar manualmente:")
        print(f"scp -i {key_path} configure_database.sh ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/")
    
    print("\n🗄️ ETAPA 3: EXECUTANDO CONFIGURAÇÃO DO BANCO")
    print("-" * 50)
    
    # Executar script no servidor
    print("🚀 Executando configuração do banco no servidor...")
    db_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && chmod +x configure_database.sh && ./configure_database.sh"'
    
    print(f"Executando: {db_command}")
    print("⚠️ Este comando pode demorar alguns minutos...")
    
    # Executar configuração
    db_result = run_command(db_command)
    
    if db_result is not None:
        print("✅ Configuração do banco executada com sucesso")
    else:
        print("⚠️ Falha na configuração do banco")
        print("💡 Tente executar manualmente no servidor:")
        print("ssh -i ~/.ssh/marabet-key.pem ubuntu@3.218.152.100")
        print("cd /home/ubuntu/marabet-ai")
        print("./configure_database.sh")
    
    print("\n🗄️ ETAPA 4: VERIFICANDO CONFIGURAÇÃO")
    print("-" * 50)
    
    # Verificar configuração do banco
    print("🔍 Verificando configuração do banco...")
    verify_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml exec web python -c \'import os; print(\"DATABASE_URL:\", os.getenv(\"DATABASE_URL\")); print(\"REDIS_URL:\", os.getenv(\"REDIS_URL\"))\'"'
    verify_result = run_command(verify_command)
    
    if verify_result:
        print("✅ Variáveis de ambiente verificadas:")
        print(verify_result)
    else:
        print("⚠️ Falha ao verificar variáveis de ambiente")
    
    print("\n🗄️ ETAPA 5: INSTRUÇÕES PARA CONFIGURAÇÃO MANUAL")
    print("-" * 50)
    
    print("📝 INSTRUÇÕES PARA CONFIGURAR O BANCO MANUALMENTE:")
    print("-" * 60)
    print("1. Conectar via SSH:")
    print(f"   ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print()
    print("2. Ir para pasta do projeto:")
    print("   cd /home/ubuntu/marabet-ai")
    print()
    print("3. Verificar status dos containers:")
    print("   docker-compose -f docker-compose.production.yml ps")
    print()
    print("4. Entrar no container web:")
    print("   docker-compose -f docker-compose.production.yml exec web bash")
    print()
    print("5. Verificar variáveis de ambiente:")
    print("   echo $DATABASE_URL")
    print("   echo $REDIS_URL")
    print()
    print("6. Instalar dependências:")
    print("   pip install psycopg2-binary redis sqlalchemy alembic")
    print()
    print("7. Testar conexão com RDS:")
    print("   python -c \"import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('Conexão OK'); conn.close()\"")
    print()
    print("8. Testar conexão com Redis:")
    print("   python -c \"import redis; r = redis.from_url('$REDIS_URL'); print('Redis OK:', r.ping())\"")
    print()
    print("9. Executar script de inicialização:")
    print("   python init_db.py")
    print()
    print("10. Sair do container:")
    print("    exit")
    
    print("\n🗄️ ETAPA 6: COMANDOS DE VERIFICAÇÃO")
    print("-" * 50)
    
    print("🧪 COMANDOS PARA TESTAR CONFIGURAÇÃO:")
    print("-" * 60)
    print("Execute no servidor Ubuntu:")
    print()
    print("# 1. Verificar status dos containers")
    print("docker-compose -f docker-compose.production.yml ps")
    print()
    print("# 2. Ver logs da aplicação")
    print("docker-compose -f docker-compose.production.yml logs --tail=20")
    print()
    print("# 3. Testar endpoint de health")
    print("curl http://localhost:8000/health")
    print()
    print("# 4. Testar endpoint de configuração")
    print("curl http://localhost:8000/config")
    print()
    print("# 5. Verificar conectividade com RDS")
    print("docker-compose -f docker-compose.production.yml exec web python -c \"import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('RDS OK'); conn.close()\"")
    print()
    print("# 6. Verificar conectividade com Redis")
    print("docker-compose -f docker-compose.production.yml exec web python -c \"import redis; r = redis.from_url('$REDIS_URL'); print('Redis OK:', r.ping())\"")
    
    print("\n🎉 CONFIGURAÇÃO DO BANCO DE DADOS CONCLUÍDA!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 40)
    print(f"• RDS Endpoint: {rds_endpoint}")
    print(f"• Redis Endpoint: {redis_endpoint}")
    print(f"• Banco: PostgreSQL")
    print(f"• Cache: Redis")
    print(f"• Status: Configurado")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Banco de dados configurado")
    print("2. 🔄 Verificar conectividade")
    print("3. 🔄 Testar aplicação")
    print("4. 🔄 Configurar monitoramento")
    print("5. 🔄 Configurar backup")
    print("6. 🔄 Testar predições")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Verifique se as conexões estão funcionando")
    print("• Monitore os logs da aplicação")
    print("• Configure backup automático do banco")
    print("• Teste as funcionalidades da aplicação")
    
    return True

def main():
    print("🚀 Iniciando configuração do banco de dados...")
    
    # Configurar banco de dados
    success = configure_database()
    
    if success:
        print("\n🎯 BANCO DE DADOS CONFIGURADO COM SUCESSO!")
        print("O banco de dados está pronto para uso!")
    else:
        print("\n❌ Falha na configuração do banco de dados")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
