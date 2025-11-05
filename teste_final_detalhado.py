#!/usr/bin/env python3
"""
Teste Final Detalhado de Conexão PostgreSQL
MaraBet AI - Teste completo com logs detalhados
"""

import psycopg2
import sys
from urllib.parse import urlparse, quote_plus

print("=" * 60)
print("🔍 TESTE FINAL DETALHADO - CONEXÃO POSTGRESQL")
print("=" * 60)
print()

# Credenciais confirmadas
CREDENCIAIS = {
    "host": "37.27.220.67",
    "port": 5432,
    "database": "meu_banco",
    "user": "meu_usuario",
    "password": "ctcaddTcMaRVioDY4kso"
}

print("📋 Credenciais Confirmadas:")
print(f"   Host: {CREDENCIAIS['host']}")
print(f"   Port: {CREDENCIAIS['port']}")
print(f"   Database: {CREDENCIAIS['database']}")
print(f"   User: {CREDENCIAIS['user']}")
print(f"   Password: {repr(CREDENCIAIS['password'])}")
print(f"   Password length: {len(CREDENCIAIS['password'])} caracteres")
print(f"   Password bytes: {CREDENCIAIS['password'].encode('utf-8')}")
print()

# Análise detalhada da senha
password = CREDENCIAIS['password']
print("🔍 Análise Detalhada da Senha:")
print(f"   Original: {repr(password)}")
print(f"   Comprimento: {len(password)}")
print(f"   Bytes (UTF-8): {password.encode('utf-8')}")
print(f"   Hex: {password.encode('utf-8').hex()}")
print(f"   Caracteres individuais: {[c for c in password]}")
print(f"   Códigos ASCII: {[ord(c) for c in password]}")
print()

# TESTE: Conexão direta
print("=" * 60)
print("TESTE: Conexão Direta com Credenciais Confirmadas")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar...")
    print(f"   Config: {CREDENCIAIS}")
    
    # Tentar conexão
    conn = psycopg2.connect(**CREDENCIAIS)
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
    
    # Verificar método de autenticação
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
    print("\n💡 A conexão está funcionando perfeitamente!")
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
        print("\n🔍 Diagnóstico:")
        print("   - Servidor está acessível: ✅")
        print("   - Porta está aberta: ✅")
        print("   - PostgreSQL está respondendo: ✅")
        print("   - Credenciais estão corretas localmente: ✅")
        print("   - Autenticação falha: ❌")
        print()
        print("🔧 Conclusão:")
        print("   O problema está no servidor PostgreSQL:")
        print("   1. A senha do usuário no servidor pode estar diferente")
        print("   2. O usuário pode não existir no servidor")
        print("   3. O pg_hba.conf pode não estar permitindo conexões remotas")
        print()
        print("🔧 Soluções no Servidor:")
        print("   1. Verificar usuário:")
        print("      sudo -u postgres psql")
        print("      SELECT usename FROM pg_user WHERE usename = 'meu_usuario';")
        print()
        print("   2. Alterar senha explicitamente:")
        print("      ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
        print()
        print("   3. Verificar pg_hba.conf:")
        print("      sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario")
        print("      Deve mostrar: host meu_banco meu_usuario 0.0.0.0/0 scram-sha-256")
        print()
        print("   4. Reiniciar PostgreSQL:")
        print("      sudo systemctl restart postgresql")
        print()
        print("   5. Testar conexão localmente no servidor:")
        print("      psql -h localhost -U meu_usuario -d meu_banco")
        print()
        print("💡 IMPORTANTE:")
        print("   Como você disse que funciona no servidor,")
        print("   pode haver diferença entre conexão LOCAL vs REMOTA.")
        print("   Verifique se o pg_hba.conf permite conexões remotas.")
        
    elif "could not connect" in error_msg:
        print("💡 Problema: Não foi possível conectar ao servidor")
        
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

