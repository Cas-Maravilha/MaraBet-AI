#!/usr/bin/env python3
"""
Diagnóstico Completo de Falha de Conexão
MaraBet AI - Verifica todas as possíveis causas
"""

import psycopg2
import sys
from urllib.parse import urlparse

print("=" * 60)
print("🔍 DIAGNÓSTICO COMPLETO - FALHA DE CONEXÃO")
print("=" * 60)
print()

# Credenciais confirmadas pelo usuário
CREDENCIAIS = {
    "host": "37.27.220.67",
    "port": 5432,
    "database": "meu_banco",
    "user": "meu_usuario",
    "password": "ctcaddTcMaRVioDY4kso"
}

# String de conexão confirmada
DATABASE_URL = "postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco"

print("📋 Credenciais Confirmadas:")
print(f"   Host: {CREDENCIAIS['host']}")
print(f"   Port: {CREDENCIAIS['port']}")
print(f"   Database: {CREDENCIAIS['database']}")
print(f"   User: {CREDENCIAIS['user']}")
print(f"   Password: {CREDENCIAIS['password']} ({len(CREDENCIAIS['password'])} caracteres)")
print()

# Verificar caracteres na senha
password = CREDENCIAIS['password']
print("🔍 Análise da Senha:")
print(f"   Comprimento: {len(password)}")
print(f"   Caracteres: {repr(password)}")
print(f"   Bytes: {password.encode('utf-8')}")
print()

# TESTE 1: Verificar configuração do módulo
print("=" * 60)
print("TESTE 1: Configuração do Módulo database_connection")
print("=" * 60)

try:
    from database_connection import db
    
    print(f"\n📋 Configuração do módulo:")
    print(f"   Host: {db.config['host']}")
    print(f"   Port: {db.config['port']}")
    print(f"   Database: {db.config['database']}")
    print(f"   User: {db.config['user']}")
    print(f"   Password: {db.config['password']} ({len(db.config['password'])} caracteres)")
    print(f"   Connection String: {db.get_connection_string()}")
    
    # Comparar senhas
    if db.config['password'] == CREDENCIAIS['password']:
        print("\n✅ Senha do módulo está correta")
    else:
        print(f"\n❌ Senha do módulo está DIFERENTE!")
        print(f"   Esperado: {CREDENCIAIS['password']}")
        print(f"   Atual: {db.config['password']}")
        print(f"   Diferença: {set(CREDENCIAIS['password']) ^ set(db.config['password'])}")
    
    # Comparar outros campos
    if db.config['host'] == CREDENCIAIS['host']:
        print("✅ Host está correto")
    else:
        print(f"❌ Host está diferente: {db.config['host']} vs {CREDENCIAIS['host']}")
    
    if db.config['user'] == CREDENCIAIS['user']:
        print("✅ User está correto")
    else:
        print(f"❌ User está diferente: {db.config['user']} vs {CREDENCIAIS['user']}")
    
    if db.config['database'] == CREDENCIAIS['database']:
        print("✅ Database está correto")
    else:
        print(f"❌ Database está diferente: {db.config['database']} vs {CREDENCIAIS['database']}")
        
except Exception as e:
    print(f"❌ Erro ao carregar módulo: {e}")
    import traceback
    traceback.print_exc()

print()

# TESTE 2: Testar conexão direta com credenciais confirmadas
print("=" * 60)
print("TESTE 2: Conexão Direta com Credenciais Confirmadas")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar com credenciais confirmadas...")
    conn = psycopg2.connect(**CREDENCIAIS)
    print("✅ Conexão estabelecida com sucesso!\n")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version(), current_database(), current_user, now();")
    result = cursor.fetchone()
    
    print("📊 Informações da Conexão:")
    print(f"   PostgreSQL: {result[0][:60]}...")
    print(f"   Database: {result[1]}")
    print(f"   User: {result[2]}")
    print(f"   Data/Hora: {result[3]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ TESTE 2 CONCLUÍDO COM SUCESSO!")
    print("💡 A conexão funciona com credenciais diretas!")
    print("   O problema está na configuração do módulo database_connection.py")
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"\n❌ Erro de conexão: {error_msg}\n")
    
    if "password authentication failed" in error_msg:
        print("💡 Problema: Autenticação falhou mesmo com credenciais confirmadas")
        print("\n🔧 Verificações:")
        print("   1. Verificar se há espaços extras ou caracteres invisíveis na senha")
        print("   2. Verificar se a senha está sendo passada corretamente")
        print("   3. Testar com diferentes formatos de conexão")
        
except Exception as e:
    print(f"\n❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()

print()

# TESTE 3: Testar com DATABASE_URL
print("=" * 60)
print("TESTE 3: Conexão via DATABASE_URL")
print("=" * 60)

try:
    print(f"\n🔄 Tentando conectar via DATABASE_URL...")
    print(f"   URL: {DATABASE_URL[:50]}...")
    
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Conexão estabelecida com sucesso!\n")
    
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user;")
    result = cursor.fetchone()
    
    print(f"📊 Database: {result[0]}, User: {result[1]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ TESTE 3 CONCLUÍDO COM SUCESSO!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")

print()

# TESTE 4: Verificar arquivo .env
print("=" * 60)
print("TESTE 4: Verificar Arquivo .env")
print("=" * 60)

try:
    from pathlib import Path
    env_file = Path(".env")
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "DATABASE_URL" in content:
            for line in content.split('\n'):
                if "DATABASE_URL" in line:
                    print(f"\n📋 Linha encontrada no .env:")
                    print(f"   {line}")
                    
                    # Extrair senha da URL
                    if "DATABASE_URL=" in line:
                        url_part = line.split("DATABASE_URL=")[1].strip()
                        if url_part.startswith("postgresql://"):
                            try:
                                parsed = urlparse(url_part)
                                senha_env = parsed.password
                                if senha_env == CREDENCIAIS['password']:
                                    print("✅ Senha no .env está correta")
                                else:
                                    print(f"❌ Senha no .env está DIFERENTE!")
                                    print(f"   Esperado: {CREDENCIAIS['password']}")
                                    print(f"   Atual: {senha_env}")
                            except Exception as e:
                                print(f"⚠️  Erro ao parsear URL: {e}")
                    break
        else:
            print("⚠️  DATABASE_URL não encontrado no .env")
    else:
        print("⚠️  Arquivo .env não encontrado")
        
except Exception as e:
    print(f"❌ Erro ao verificar .env: {e}")

print()

# RESUMO E RECOMENDAÇÕES
print("=" * 60)
print("📋 RESUMO E RECOMENDAÇÕES")
print("=" * 60)
print()

print("💡 Se o TESTE 2 funcionou:")
print("   - O problema está na configuração do módulo database_connection.py")
print("   - Atualize o módulo para usar as credenciais corretas")
print()
print("💡 Se o TESTE 2 falhou:")
print("   - Verifique se há espaços extras ou caracteres invisíveis")
print("   - Teste a conexão diretamente no servidor")
print()
print("💡 Se o TESTE 3 funcionou:")
print("   - Use DATABASE_URL diretamente em vez do módulo")
print()
print("=" * 60)

