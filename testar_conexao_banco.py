#!/usr/bin/env python3
"""
Teste de Conexão com Banco de Dados PostgreSQL
MaraBet AI - Testa conexão com as credenciais configuradas
"""

import os
import sys

try:
    import psycopg2
except ImportError:
    print("❌ Erro: psycopg2 não está instalado")
    print("   Instale com: pip install psycopg2-binary")
    sys.exit(1)

# Credenciais do arquivo .env
DATABASE_URL = "postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco"

# Parse da URL
# postgresql://usuario:senha@host:porta/database
try:
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    
    config = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip('/'),
        "user": parsed.username,
        "password": parsed.password
    }
except Exception as e:
    print(f"❌ Erro ao parsear DATABASE_URL: {e}")
    sys.exit(1)

def test_connection():
    """Testa conexão com o banco de dados"""
    print("=" * 60)
    print("🔍 TESTE DE CONEXÃO - PostgreSQL")
    print("=" * 60)
    print(f"\n📋 Configuração:")
    print(f"   Host: {config['host']}")
    print(f"   Porta: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    print()
    
    try:
        print("🔄 Tentando conectar...")
        conn = psycopg2.connect(**config)
        print("✅ Conexão estabelecida com sucesso!\n")
        
        # Executar query de teste
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user, now();")
        result = cursor.fetchone()
        
        print("📊 Informações da conexão:")
        print(f"   PostgreSQL: {result[0][:50]}...")
        print(f"   Database: {result[1]}")
        print(f"   User: {result[2]}")
        print(f"   Data/Hora Servidor: {result[3]}")
        
        # Listar tabelas (se existirem)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📋 Tabelas encontradas ({len(tables)}):")
            for table in tables[:10]:  # Mostrar apenas as primeiras 10
                print(f"   - {table[0]}")
            if len(tables) > 10:
                print(f"   ... e mais {len(tables) - 10} tabelas")
        else:
            print("\n📋 Nenhuma tabela encontrada no banco de dados")
            print("   💡 Execute as migrações: python migrate.py --migrate")
        
        cursor.close()
        conn.close()
        print("\n✅ Conexão fechada com sucesso!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("\n💡 Verificações necessárias:")
        print("   1. Servidor PostgreSQL está em execução?")
        print("   2. Firewall permite conexões na porta 5432?")
        print("   3. IP 37.27.220.67 está correto e acessível?")
        print("   4. pg_hba.conf permite conexões remotas?")
        print("   5. Credenciais (usuário/senha) estão corretas?")
        return False
        
    except psycopg2.ProgrammingError as e:
        print(f"\n❌ Erro de programação: {e}")
        print("\n💡 Possíveis causas:")
        print("   - Database 'meu_banco' não existe")
        print("   - Usuário não tem permissões")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

