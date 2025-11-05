#!/usr/bin/env python3
"""
Teste Detalhado de Conexão com Banco de Dados PostgreSQL
Testa diferentes formatos de conexão e URL encoding
"""

import psycopg2
from urllib.parse import quote_plus

# Credenciais confirmadas
CONFIG = {
    "host": "37.27.220.67",
    "port": 5432,
    "database": "meu_banco",
    "user": "meu_usuario",
    "password": "ctcaddTcMaRVioDY4kso"
}

def test_connection_direct():
    """Testa conexão direta com psycopg2"""
    print("=" * 60)
    print("TESTE 1: Conexão Direta (psycopg2)")
    print("=" * 60)
    
    try:
        print(f"\n📋 Configuração:")
        print(f"   Host: {CONFIG['host']}")
        print(f"   Porta: {CONFIG['port']}")
        print(f"   Database: {CONFIG['database']}")
        print(f"   User: {CONFIG['user']}")
        print(f"   Password: {'*' * len(CONFIG['password'])}")
        print()
        
        print("🔄 Tentando conectar...")
        conn = psycopg2.connect(**CONFIG)
        print("✅ Conexão estabelecida com sucesso!\n")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user, now();")
        result = cursor.fetchone()
        
        print("📊 Informações da conexão:")
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
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("\n📋 Nenhuma tabela encontrada")
        
        cursor.close()
        conn.close()
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

def test_connection_url():
    """Testa conexão usando URL com e sem encoding"""
    print("\n" + "=" * 60)
    print("TESTE 2: Conexão via URL String")
    print("=" * 60)
    
    # Teste sem encoding
    url1 = f"postgresql://{CONFIG['user']}:{CONFIG['password']}@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['database']}"
    
    # Teste com encoding
    password_encoded = quote_plus(CONFIG['password'])
    url2 = f"postgresql://{CONFIG['user']}:{password_encoded}@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['database']}"
    
    print(f"\n📋 URL sem encoding:")
    print(f"   {url1[:50]}...")
    print(f"\n📋 URL com encoding:")
    print(f"   {url2[:50]}...")
    
    for i, url in enumerate([url1, url2], 1):
        try:
            print(f"\n🔄 Tentando conexão {i}...")
            conn = psycopg2.connect(url)
            print(f"✅ Conexão {i} bem-sucedida!")
            
            cursor = conn.cursor()
            cursor.execute("SELECT current_database(), current_user;")
            result = cursor.fetchone()
            print(f"   Database: {result[0]}, User: {result[1]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Conexão {i} falhou: {e}")
    
    return False

def test_connection_with_ssl():
    """Testa conexão com diferentes opções SSL"""
    print("\n" + "=" * 60)
    print("TESTE 3: Conexão com Opções SSL")
    print("=" * 60)
    
    ssl_options = [
        {"sslmode": "disable"},
        {"sslmode": "require"},
        {"sslmode": "prefer"},
    ]
    
    for ssl_option in ssl_options:
        try:
            print(f"\n🔄 Testando com {ssl_option}...")
            config_with_ssl = {**CONFIG, **ssl_option}
            conn = psycopg2.connect(**config_with_ssl)
            print(f"✅ Conexão bem-sucedida com {ssl_option}!")
            
            cursor = conn.cursor()
            cursor.execute("SELECT current_database();")
            result = cursor.fetchone()
            print(f"   Database: {result[0]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Falhou: {e}")
    
    return False

if __name__ == "__main__":
    print("\n" + "🔍 TESTE DETALHADO DE CONEXÃO - PostgreSQL".center(60))
    print("=" * 60)
    
    # Teste 1: Conexão direta
    success1 = test_connection_direct()
    
    # Teste 2: Conexão via URL
    if not success1:
        success2 = test_connection_url()
    
    # Teste 3: Conexão com SSL
    if not success1:
        success3 = test_connection_with_ssl()
    
    print("\n" + "=" * 60)
    if success1:
        print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        print("\n💡 Use a conexão direta (psycopg2.connect) para sua aplicação")
    else:
        print("❌ NENHUMA CONEXÃO FOI BEM-SUCEDIDA")
        print("\n💡 Verificações adicionais:")
        print("   1. Verifique se o usuário 'meu_usuario' existe no servidor")
        print("   2. Verifique se a senha está correta (sem espaços extras)")
        print("   3. Verifique se o database 'meu_banco' existe")
        print("   4. Verifique permissões do usuário no pg_hba.conf")
        print("   5. Teste a conexão diretamente no servidor PostgreSQL")
    print("=" * 60 + "\n")

