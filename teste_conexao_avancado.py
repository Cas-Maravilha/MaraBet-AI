#!/usr/bin/env python3
"""
Teste Avançado de Conexão PostgreSQL
MaraBet AI - Testa diferentes formas de conexão
"""

import psycopg2
from urllib.parse import quote_plus
import sys

print("=" * 60)
print("🔍 TESTE AVANÇADO DE CONEXÃO POSTGRESQL")
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

# Senha em diferentes formatos
password_variants = [
    ("Original", "ctcaddTcMaRVioDY4kso"),
    ("Trim", "ctcaddTcMaRVioDY4kso".strip()),
    ("Sem espaços", "".join("ctcaddTcMaRVioDY4kso".split())),
]

print("📋 Testando diferentes formas de conexão...")
print()

# TESTE 1: Conexão direta com diferentes formatos de senha
print("=" * 60)
print("TESTE 1: Diferentes Formatos de Senha")
print("=" * 60)

for nome, senha in password_variants:
    print(f"\n🔄 Testando: {nome}")
    print(f"   Senha: {senha} ({len(senha)} caracteres)")
    
    try:
        config = CREDENCIAIS.copy()
        config["password"] = senha
        
        conn = psycopg2.connect(**config)
        print(f"✅ {nome}: Conexão bem-sucedida!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        result = cursor.fetchone()
        print(f"   Database: {result[0]}, User: {result[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ CONEXÃO FUNCIONA!")
        sys.exit(0)
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"❌ {nome}: Autenticação falhou")
        else:
            print(f"❌ {nome}: {error_msg}")
    except Exception as e:
        print(f"❌ {nome}: {e}")

print()

# TESTE 2: Conexão com diferentes opções de SSL
print("=" * 60)
print("TESTE 2: Diferentes Opções SSL")
print("=" * 60)

ssl_options = [
    (None, "Sem SSL"),
    ({"sslmode": "disable"}, "SSL Desabilitado"),
    ({"sslmode": "prefer"}, "SSL Preferido"),
    ({"sslmode": "require"}, "SSL Requerido"),
]

for ssl_config, nome in ssl_options:
    print(f"\n🔄 Testando: {nome}")
    
    try:
        config = CREDENCIAIS.copy()
        if ssl_config:
            config.update(ssl_config)
        
        conn = psycopg2.connect(**config)
        print(f"✅ {nome}: Conexão bem-sucedida!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        result = cursor.fetchone()
        print(f"   Database: {result[0]}, User: {result[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ CONEXÃO FUNCIONA!")
        sys.exit(0)
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"❌ {nome}: Autenticação falhou")
        else:
            print(f"❌ {nome}: {error_msg}")
    except Exception as e:
        print(f"❌ {nome}: {e}")

print()

# TESTE 3: Conexão via URL com encoding
print("=" * 60)
print("TESTE 3: Conexão via URL com Encoding")
print("=" * 60)

url_variants = [
    ("URL Normal", f"postgresql://{CREDENCIAIS['user']}:{CREDENCIAIS['password']}@{CREDENCIAIS['host']}:{CREDENCIAIS['port']}/{CREDENCIAIS['database']}"),
    ("URL com Encoding", f"postgresql://{CREDENCIAIS['user']}:{quote_plus(CREDENCIAIS['password'])}@{CREDENCIAIS['host']}:{CREDENCIAIS['port']}/{CREDENCIAIS['database']}"),
]

for nome, url in url_variants:
    print(f"\n🔄 Testando: {nome}")
    print(f"   URL: {url[:50]}...")
    
    try:
        conn = psycopg2.connect(url)
        print(f"✅ {nome}: Conexão bem-sucedida!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        result = cursor.fetchone()
        print(f"   Database: {result[0]}, User: {result[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ CONEXÃO FUNCIONA!")
        sys.exit(0)
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"❌ {nome}: Autenticação falhou")
        else:
            print(f"❌ {nome}: {error_msg}")
    except Exception as e:
        print(f"❌ {nome}: {e}")

print()

# TESTE 4: Testar conexão com diferentes databases
print("=" * 60)
print("TESTE 4: Testar com Diferentes Databases")
print("=" * 60)

databases = ["meu_banco", "postgres"]

for db_name in databases:
    print(f"\n🔄 Testando database: {db_name}")
    
    try:
        config = CREDENCIAIS.copy()
        config["database"] = db_name
        
        conn = psycopg2.connect(**config)
        print(f"✅ Database {db_name}: Conexão bem-sucedida!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        result = cursor.fetchone()
        print(f"   Database: {result[0]}, User: {result[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ CONEXÃO FUNCIONA!")
        sys.exit(0)
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"❌ Database {db_name}: Autenticação falhou")
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            print(f"⚠️  Database {db_name}: Não existe")
        else:
            print(f"❌ Database {db_name}: {error_msg}")
    except Exception as e:
        print(f"❌ Database {db_name}: {e}")

print()

# RESUMO FINAL
print("=" * 60)
print("📋 RESUMO FINAL")
print("=" * 60)
print()

print("❌ NENHUMA CONEXÃO FOI BEM-SUCEDIDA")
print()
print("💡 Conclusão:")
print("   O problema está no servidor PostgreSQL, não nas configurações locais.")
print()
print("🔧 Verificações Necessárias no Servidor:")
print("   1. Verificar se o usuário existe:")
print("      sudo -u postgres psql")
print("      SELECT usename FROM pg_user WHERE usename = 'meu_usuario';")
print()
print("   2. Verificar/alterar senha do usuário:")
print("      ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
print()
print("   3. Verificar pg_hba.conf:")
print("      sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario")
print("      Deve mostrar: host meu_banco meu_usuario 0.0.0.0/0 scram-sha-256")
print()
print("   4. Reiniciar PostgreSQL após alterações:")
print("      sudo systemctl restart postgresql")
print()
print("   5. Testar conexão localmente no servidor:")
print("      psql -h localhost -U meu_usuario -d meu_banco")
print()
print("=" * 60)

