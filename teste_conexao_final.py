#!/usr/bin/env python3
"""
Teste Final de Conexão PostgreSQL
MaraBet AI - Teste completo com todas as possibilidades
"""

import psycopg2
from urllib.parse import quote_plus

print("=" * 60)
print("🔍 TESTE FINAL DE CONEXÃO POSTGRESQL")
print("=" * 60)
print()

# Credenciais confirmadas
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
print(f"   Password: {'*' * len(config['password'])} ({len(config['password'])} caracteres)")
print()

# Verificar caracteres na senha
password = config['password']
print("🔍 Análise da Senha:")
print(f"   Comprimento: {len(password)} caracteres")
print(f"   Contém maiúsculas: {any(c.isupper() for c in password)}")
print(f"   Contém minúsculas: {any(c.islower() for c in password)}")
print(f"   Contém números: {any(c.isdigit() for c in password)}")
print(f"   Caracteres especiais: {[c for c in password if not c.isalnum()]}")
print()

# TESTE 1: Conexão direta
print("=" * 60)
print("TESTE 1: Conexão Direta (psycopg2)")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar...")
    conn = psycopg2.connect(**config)
    print("✅ Conexão estabelecida com sucesso!\n")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version(), current_database(), current_user, now();")
    result = cursor.fetchone()
    
    print("📊 Informações da Conexão:")
    print(f"   PostgreSQL: {result[0][:60]}...")
    print(f"   Database: {result[1]}")
    print(f"   User: {result[2]}")
    print(f"   Data/Hora: {result[3]}")
    
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
    print("\n💡 A conexão está funcionando perfeitamente!")
    print("   Você pode usar o módulo database_connection normalmente:")
    print()
    print("   from database_connection import db")
    print("   with db.get_connection() as conn:")
    print("       cursor = conn.cursor()")
    print("       cursor.execute('SELECT * FROM sua_tabela')")
    print("       results = cursor.fetchall()")
    print()
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"\n❌ Erro de conexão: {error_msg}\n")
    
    if "password authentication failed" in error_msg:
        print("💡 Problema: Autenticação falhou")
        print("\n🔧 Possíveis causas:")
        print("   1. A senha no servidor está diferente da configurada")
        print("   2. O usuário foi criado com senha diferente")
        print("   3. Caracteres especiais na senha podem estar causando problemas")
        print()
        print("🔧 Soluções:")
        print("   1. Verificar a senha no servidor:")
        print("      sudo -u postgres psql")
        print("      SELECT usename FROM pg_user WHERE usename = 'meu_usuario';")
        print()
        print("   2. Alterar a senha no servidor:")
        print("      ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
        print()
        print("   3. Verificar pg_hba.conf permite conexões remotas:")
        print("      sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario")
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
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ Erro inesperado: {e}")
    print("\n" + "=" * 60)

