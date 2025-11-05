#!/usr/bin/env python3
"""
Teste de Conexão PostgreSQL com scram-sha-256
MaraBet AI - Teste específico para autenticação scram-sha-256
"""

import psycopg2
import sys

print("=" * 60)
print("🔍 TESTE DE CONEXÃO POSTGRESQL - SCRAM-SHA-256")
print("=" * 60)
print()

# Credenciais
config = {
    "host": "37.27.220.67",
    "port": 5432,
    "database": "meu_banco",
    "user": "meu_usuario",
    "password": "ctcaddTcMaRVioDY4kso"
}

print("📋 Credenciais de Conexão:")
print(f"   Host: {config['host']}")
print(f"   Port: {config['port']}")
print(f"   Database: {config['database']}")
print(f"   User: {config['user']}")
print(f"   Password: {'*' * len(config['password'])}")
print()

# Verificar versão do psycopg2
try:
    import psycopg2
    print(f"📦 psycopg2 versão: {psycopg2.__version__}")
    
    # psycopg2 2.7+ suporta scram-sha-256
    version_parts = psycopg2.__version__.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])
    
    if major > 2 or (major == 2 and minor >= 7):
        print("✅ psycopg2 suporta scram-sha-256")
    else:
        print("⚠️  psycopg2 pode não suportar scram-sha-256 completamente")
        print("   Recomendado: psycopg2 >= 2.7.0")
        print("   Atualize: pip install --upgrade psycopg2-binary")
    
except Exception as e:
    print(f"⚠️  Erro ao verificar versão: {e}")

print()

# Testar conexão
print("=" * 60)
print("TESTE DE CONEXÃO")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar...")
    print("   Método de autenticação esperado: scram-sha-256")
    print()
    
    # Tentar conexão
    conn = psycopg2.connect(**config)
    print("✅ Conexão estabelecida com sucesso!\n")
    
    cursor = conn.cursor()
    
    # Informações da conexão
    cursor.execute("SELECT version(), current_database(), current_user, now();")
    result = cursor.fetchone()
    
    print("📊 Informações da Conexão:")
    print(f"   PostgreSQL: {result[0][:60]}...")
    print(f"   Database: {result[1]}")
    print(f"   User: {result[2]}")
    print(f"   Data/Hora: {result[3]}")
    
    # Verificar método de autenticação usado
    try:
        cursor.execute("SHOW password_encryption;")
        encryption = cursor.fetchone()
        print(f"   Password Encryption: {encryption[0]}")
    except:
        pass
    
    # Listar tabelas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n📋 Tabelas encontradas ({len(tables)}):")
        for table in tables[:10]:
            print(f"   - {table[0]}")
        if len(tables) > 10:
            print(f"   ... e mais {len(tables) - 10} tabelas")
    else:
        print("\n📋 Nenhuma tabela encontrada")
        print("   💡 Execute as migrações: python migrate.py --migrate")
    
    cursor.close()
    conn.close()
    
    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\n💡 A conexão está funcionando perfeitamente com scram-sha-256!")
    print("   Você pode usar o módulo database_connection normalmente:")
    print()
    print("   from database_connection import db")
    print("   with db.get_connection() as conn:")
    print("       cursor = conn.cursor()")
    print("       cursor.execute('SELECT * FROM sua_tabela')")
    print("       results = cursor.fetchall()")
    print()
    
    sys.exit(0)
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"\n❌ Erro de conexão: {error_msg}\n")
    
    if "password authentication failed" in error_msg:
        print("💡 Problema: Autenticação falhou")
        print("\n🔧 Possíveis causas:")
        print("   1. A senha no servidor está diferente da configurada")
        print("   2. O usuário foi criado com senha diferente")
        print("   3. O pg_hba.conf não está configurado corretamente")
        print("   4. O psycopg2 não suporta scram-sha-256 (versão antiga)")
        print()
        print("🔧 Soluções:")
        print("   1. Verificar/alterar senha no servidor:")
        print("      sudo -u postgres psql")
        print("      ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
        print()
        print("   2. Verificar pg_hba.conf:")
        print("      sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario")
        print("      Deve mostrar: host meu_banco meu_usuario 0.0.0.0/0 scram-sha-256")
        print()
        print("   3. Atualizar psycopg2:")
        print("      pip install --upgrade psycopg2-binary")
        print()
        print("   4. Reiniciar PostgreSQL após alterações:")
        print("      sudo systemctl restart postgresql")
        
    elif "could not connect" in error_msg or "Connection refused" in error_msg:
        print("💡 Problema: Não foi possível conectar ao servidor")
        print("\n🔧 Verificações:")
        print("   1. Servidor está acessível? (ping 37.27.220.67)")
        print("   2. Porta 5432 está aberta no firewall?")
        print("   3. PostgreSQL está rodando? (sudo systemctl status postgresql)")
        
    elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
        print("💡 Problema: Database não existe")
        print("\n🔧 Solução:")
        print("   CREATE DATABASE meu_banco OWNER meu_usuario;")
    
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

