#!/usr/bin/env python3
"""
Teste de Conexão do Banco de Dados (estilo Cliente)
MaraBet AI - Teste completo de conexão PostgreSQL
"""

import psycopg2
import sys
from datetime import datetime

print("=" * 60)
print("🔍 TESTE DE CONEXÃO DO BANCO DE DADOS")
print("=" * 60)
print()

# Credenciais
CREDENCIAIS = {
    "host": "37.27.220.67",
    "port": 5432,
    "database": "meu_banco",
    "user": "meu_usuario",
    "password": "ctcaddTcMARvioDY4kso"
}

print("📋 Credenciais:")
print(f"   Host: {CREDENCIAIS['host']}")
print(f"   Porta: {CREDENCIAIS['port']}")
print(f"   Database: {CREDENCIAIS['database']}")
print(f"   Usuário: {CREDENCIAIS['user']}")
print(f"   Senha: {'*' * len(CREDENCIAIS['password'])}")
print()

print("=" * 60)
print("🔄 Tentando conectar...")
print("=" * 60)
print()

try:
    # Conectar ao banco de dados
    conn = psycopg2.connect(**CREDENCIAIS)
    print("✅ Conexão estabelecida com sucesso!")
    print()
    
    # Criar cursor
    cursor = conn.cursor()
    
    # Teste 1: Versão do PostgreSQL
    print("=" * 60)
    print("TESTE 1: Versão do PostgreSQL")
    print("=" * 60)
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   PostgreSQL: {version[:60]}...")
    print()
    
    # Teste 2: Database e usuário atual
    print("=" * 60)
    print("TESTE 2: Database e Usuário Atual")
    print("=" * 60)
    cursor.execute("SELECT current_database(), current_user, now();")
    db, user, now = cursor.fetchone()
    print(f"   Database: {db}")
    print(f"   Usuário: {user}")
    print(f"   Data/Hora: {now}")
    print()
    
    # Teste 3: Listar tabelas
    print("=" * 60)
    print("TESTE 3: Listar Tabelas")
    print("=" * 60)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"   ✅ {len(tables)} tabela(s) encontrada(s):")
        for table in tables:
            print(f"      - {table[0]}")
    else:
        print("   ℹ️  Nenhuma tabela encontrada")
        print("   💡 Execute as migrações para criar as tabelas")
    print()
    
    # Teste 4: Verificar permissões
    print("=" * 60)
    print("TESTE 4: Verificar Permissões")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            has_database_privilege(current_user, current_database(), 'CREATE') as pode_criar,
            has_database_privilege(current_user, current_database(), 'CONNECT') as pode_conectar,
            has_database_privilege(current_user, current_database(), 'TEMP') as pode_temp;
    """)
    perms = cursor.fetchone()
    print(f"   Pode criar objetos: {'✅' if perms[0] else '❌'}")
    print(f"   Pode conectar: {'✅' if perms[1] else '❌'}")
    print(f"   Pode criar temporários: {'✅' if perms[2] else '❌'}")
    print()
    
    # Teste 5: Teste de escrita (criar tabela temporária)
    print("=" * 60)
    print("TESTE 5: Teste de Escrita (Tabela Temporária)")
    print("=" * 60)
    try:
        cursor.execute("""
            CREATE TEMPORARY TABLE teste_conexao (
                id SERIAL PRIMARY KEY,
                mensagem TEXT,
                data_criacao TIMESTAMP DEFAULT NOW()
            );
        """)
        cursor.execute("""
            INSERT INTO teste_conexao (mensagem) 
            VALUES ('Teste de conexão bem-sucedido!');
        """)
        cursor.execute("SELECT * FROM teste_conexao;")
        resultado = cursor.fetchone()
        print(f"   ✅ Tabela temporária criada com sucesso!")
        print(f"   ✅ Registro inserido: {resultado[1]}")
        print(f"   ✅ Data: {resultado[2]}")
        conn.rollback()  # Rollback para não deixar a tabela temporária
    except Exception as e:
        print(f"   ⚠️  Erro ao criar tabela temporária: {e}")
        conn.rollback()
    print()
    
    # Fechar cursor e conexão
    cursor.close()
    conn.close()
    
    print("=" * 60)
    print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)
    print()
    print("💡 A conexão está funcionando perfeitamente!")
    print("   Você pode usar ferramentas como pgAdmin, DBeaver ou")
    print("   código Python para conectar ao banco de dados.")
    print()
    
except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"❌ Erro de conexão: {error_msg}\n")
    
    if "password authentication failed" in error_msg:
        print("💡 Problema: Autenticação falhou")
        print("   Verifique:")
        print("   1. Se a senha está correta: ctcaddTcMARvioDY4kso")
        print("   2. Se não há espaços extras na senha")
        print("   3. Se o usuário existe no servidor")
    elif "could not connect" in error_msg:
        print("💡 Problema: Não foi possível conectar ao servidor")
        print("   Verifique:")
        print("   1. Se o servidor está acessível: ping 37.27.220.67")
        print("   2. Se a porta está aberta: Test-NetConnection -ComputerName 37.27.220.67 -Port 5432")
        print("   3. Se o firewall não está bloqueando")
    
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

