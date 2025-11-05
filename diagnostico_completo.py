#!/usr/bin/env python3
"""
Diagnóstico Completo de Conexão PostgreSQL
MaraBet AI - Verifica todas as possíveis causas do problema
"""

import psycopg2
from urllib.parse import urlparse
import socket

print("=" * 60)
print("🔍 DIAGNÓSTICO COMPLETO - CONEXÃO POSTGRESQL")
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

# ============================================
# TESTE 1: Verificar se o servidor está acessível
# ============================================
print("📡 TESTE 1: Conectividade de Rede")
print("-" * 60)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((config["host"], config["port"]))
    sock.close()
    
    if result == 0:
        print(f"✅ Servidor {config['host']}:{config['port']} está acessível")
    else:
        print(f"❌ Servidor {config['host']}:{config['port']} NÃO está acessível")
        print("   - Porta pode estar fechada no firewall")
        print("   - Servidor pode estar offline")
except Exception as e:
    print(f"❌ Erro ao testar conectividade: {e}")

print()

# ============================================
# TESTE 2: Tentar conexão com diferentes credenciais
# ============================================
print("🔐 TESTE 2: Autenticação")
print("-" * 60)

# Testar conexão com usuário postgres (padrão)
test_configs = [
    {
        "name": "Usuário configurado (meu_usuario)",
        "config": config
    },
    {
        "name": "Usuário postgres (padrão)",
        "config": {
            "host": config["host"],
            "port": config["port"],
            "database": "postgres",
            "user": "postgres",
            "password": "postgres"  # Senha padrão comum
        }
    },
    {
        "name": "Database postgres com meu_usuario",
        "config": {
            "host": config["host"],
            "port": config["port"],
            "database": "postgres",
            "user": config["user"],
            "password": config["password"]
        }
    }
]

for test in test_configs:
    print(f"\n🔄 Testando: {test['name']}")
    try:
        conn = psycopg2.connect(**test["config"])
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user, version();")
        result = cursor.fetchone()
        print(f"✅ Conexão bem-sucedida!")
        print(f"   Database: {result[0]}")
        print(f"   User: {result[1]}")
        cursor.close()
        conn.close()
        
        # Se conseguiu conectar, verificar se o usuário existe
        if test["config"]["user"] == "postgres":
            print("\n💡 Conseguiu conectar como postgres!")
            print("   Execute no servidor:")
            print("   CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
            print("   CREATE DATABASE meu_banco OWNER meu_usuario;")
        break
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"❌ Autenticação falhou: usuário ou senha incorretos")
        elif "could not connect" in error_msg:
            print(f"❌ Não foi possível conectar: {error_msg}")
        else:
            print(f"❌ Erro: {error_msg}")
    except Exception as e:
        print(f"❌ Erro: {e}")

print()

# ============================================
# TESTE 3: Verificar configuração do módulo
# ============================================
print("⚙️  TESTE 3: Configuração do Módulo")
print("-" * 60)

try:
    from database_connection import db
    
    print(f"Host: {db.config['host']}")
    print(f"Port: {db.config['port']}")
    print(f"Database: {db.config['database']}")
    print(f"User: {db.config['user']}")
    print(f"Password: {'*' * len(db.config['password'])} ({len(db.config['password'])} caracteres)")
    print(f"Connection String: {db.get_connection_string()}")
    
    # Verificar se a senha tem caracteres especiais
    password = db.config['password']
    if any(c in password for c in ['@', '#', '$', '%', '&', '*', '(', ')', '!']):
        print("\n⚠️  A senha contém caracteres especiais que podem precisar de URL encoding")
    
except Exception as e:
    print(f"❌ Erro ao carregar configuração: {e}")

print()

# ============================================
# RESUMO E RECOMENDAÇÕES
# ============================================
print("=" * 60)
print("📋 RESUMO E RECOMENDAÇÕES")
print("=" * 60)
print()

print("🔧 PRÓXIMOS PASSOS:")
print()
print("1. Verificar se o usuário existe no servidor:")
print("   ssh usuario@37.27.220.67")
print("   sudo -u postgres psql")
print("   SELECT usename FROM pg_user WHERE usename = 'meu_usuario';")
print()
print("2. Se o usuário não existir, criar:")
print("   CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
print()
print("3. Verificar se o database existe:")
print("   SELECT datname FROM pg_database WHERE datname = 'meu_banco';")
print()
print("4. Se o database não existir, criar:")
print("   CREATE DATABASE meu_banco OWNER meu_usuario;")
print()
print("5. Verificar pg_hba.conf permite conexões remotas:")
print("   sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario")
print()
print("6. Reiniciar PostgreSQL após alterações:")
print("   sudo systemctl restart postgresql")
print()
print("=" * 60)

