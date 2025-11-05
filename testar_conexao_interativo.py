#!/usr/bin/env python3
"""
Teste Interativo de Conexão PostgreSQL
MaraBet AI - Testa conexão com diferentes credenciais
"""

import psycopg2
import sys

def test_connection(host, port, database, user, password):
    """Testa conexão com credenciais fornecidas"""
    print(f"\n{'='*60}")
    print(f"🔍 TESTANDO CONEXÃO")
    print(f"{'='*60}")
    print(f"\n📋 Credenciais:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   User: {user}")
    print(f"   Password: {'*' * len(password)}")
    print()
    
    try:
        print("🔄 Tentando conectar...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print("✅ Conexão estabelecida com sucesso!\n")
        
        cursor = conn.cursor()
        
        # Informações básicas
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
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("\n📋 Nenhuma tabela encontrada")
            print("   💡 Execute as migrações: python migrate.py --migrate")
        
        # Verificar permissões
        cursor.execute("""
            SELECT 
                has_database_privilege(current_user, current_database(), 'CREATE'),
                has_database_privilege(current_user, current_database(), 'CONNECT')
        """)
        perms = cursor.fetchone()
        
        print(f"\n🔐 Permissões:")
        print(f"   CREATE: {'✅' if perms[0] else '❌'}")
        print(f"   CONNECT: {'✅' if perms[1] else '❌'}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n❌ Erro de conexão: {error_msg}")
        
        if "password authentication failed" in error_msg:
            print("\n💡 Problema: Autenticação falhou")
            print("   Possíveis causas:")
            print("   1. Usuário não existe no servidor")
            print("   2. Senha está incorreta")
            print("   3. Usuário não tem permissão para acessar o database")
            print("\n🔧 Solução:")
            print("   Conecte-se ao servidor PostgreSQL e execute:")
            print("   CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';")
            print("   CREATE DATABASE meu_banco OWNER meu_usuario;")
            print("   GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;")
            
        elif "could not connect" in error_msg or "Connection refused" in error_msg:
            print("\n💡 Problema: Não foi possível conectar ao servidor")
            print("   Verifique:")
            print("   1. Servidor está acessível? (ping 37.27.220.67)")
            print("   2. Porta 5432 está aberta?")
            print("   3. Firewall permite conexões?")
            
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            print("\n💡 Problema: Database não existe")
            print("   Conecte-se ao servidor e execute:")
            print("   CREATE DATABASE meu_banco OWNER meu_usuario;")
            
        return False
        
    except psycopg2.ProgrammingError as e:
        print(f"\n❌ Erro de programação: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "🔍 TESTE DE CONEXÃO POSTGRESQL - MARABET AI".center(60))
    print("=" * 60)
    
    # Credenciais padrão
    config = {
        "host": "37.27.220.67",
        "port": 5432,
        "database": "meu_banco",
        "user": "meu_usuario",
        "password": "ctcaddTcMaRVioDY4kso"
    }
    
    # Permitir entrada interativa
    print("\n💡 Pressione Enter para usar credenciais padrão")
    print("   Ou digite novas credenciais\n")
    
    user_input = input("Usuário [meu_usuario]: ").strip()
    if user_input:
        config["user"] = user_input
    
    password_input = input("Senha [********]: ").strip()
    if password_input:
        config["password"] = password_input
    
    db_input = input("Database [meu_banco]: ").strip()
    if db_input:
        config["database"] = db_input
    
    # Testar conexão
    success = test_connection(**config)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ CONEXÃO CONFIGURADA COM SUCESSO!")
        print("=" * 60)
        print("\n💡 Próximos passos:")
        print("   1. Execute as migrações: python migrate.py --migrate")
        print("   2. Inicie a aplicação: python app.py")
        print("   3. Acesse o dashboard: http://localhost:8000")
    else:
        print("\n" + "=" * 60)
        print("❌ CONEXÃO NÃO FOI ESTABELECIDA")
        print("=" * 60)
        print("\n💡 Veja o arquivo DIAGNOSTICO_CONEXAO_BANCO.md para mais detalhes")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

