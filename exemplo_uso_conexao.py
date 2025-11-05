#!/usr/bin/env python3
"""
Exemplo de Uso do Módulo de Conexão PostgreSQL
MaraBet AI - Exemplos práticos de uso
"""

from database_connection import db, get_db_connection, test_db_connection

def exemplo_1_conexao_simples():
    """Exemplo 1: Conexão simples"""
    print("\n" + "="*60)
    print("EXEMPLO 1: Conexão Simples")
    print("="*60)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user;")
        result = cursor.fetchone()
        print(f"✅ Conectado!")
        print(f"   PostgreSQL: {result['version'][:50]}...")
        print(f"   Database: {result['current_database']}")
        print(f"   User: {result['current_user']}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_2_context_manager():
    """Exemplo 2: Usando context manager (recomendado)"""
    print("\n" + "="*60)
    print("EXEMPLO 2: Context Manager (Recomendado)")
    print("="*60)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT now() as data_hora, version() as versao;")
            result = cursor.fetchone()
            print(f"✅ Conectado!")
            print(f"   Data/Hora: {result['data_hora']}")
            print(f"   Versão: {result['versao'][:50]}...")
            cursor.close()
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_3_executar_query():
    """Exemplo 3: Executar query usando método helper"""
    print("\n" + "="*60)
    print("EXEMPLO 3: Executar Query (Método Helper)")
    print("="*60)
    
    try:
        # Listar tabelas
        results = db.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        if results:
            print(f"✅ Tabelas encontradas ({len(results)}):")
            for row in results:
                print(f"   - {row['table_name']}")
        else:
            print("ℹ️  Nenhuma tabela encontrada")
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_4_pool_conexoes():
    """Exemplo 4: Usar pool de conexões"""
    print("\n" + "="*60)
    print("EXEMPLO 4: Pool de Conexões")
    print("="*60)
    
    try:
        # Criar pool
        db.create_connection_pool(min_conn=1, max_conn=5)
        
        # Usar pool
        with db.get_connection(use_pool=True) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_database();")
            result = cursor.fetchone()
            print(f"✅ Conectado via pool!")
            print(f"   Database: {result['current_database']}")
            cursor.close()
        
        # Fechar pool
        db.close_connection_pool()
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_5_info_banco():
    """Exemplo 5: Informações do banco"""
    print("\n" + "="*60)
    print("EXEMPLO 5: Informações do Banco")
    print("="*60)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Informações do banco
            cursor.execute("""
                SELECT 
                    current_database() as database,
                    current_user as usuario,
                    version() as versao_postgres,
                    now() as data_hora
            """)
            info = cursor.fetchone()
            
            print("📊 Informações:")
            print(f"   Database: {info['database']}")
            print(f"   Usuário: {info['usuario']}")
            print(f"   PostgreSQL: {info['versao_postgres'][:60]}...")
            print(f"   Data/Hora: {info['data_hora']}")
            
            # Estatísticas
            cursor.execute("""
                SELECT 
                    count(*) as total_tabelas
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            stats = cursor.fetchone()
            print(f"   Total de Tabelas: {stats['total_tabelas']}")
            
            cursor.close()
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("\n" + "📚 EXEMPLOS DE USO - MÓDULO DE CONEXÃO POSTGRESQL".center(60))
    print("="*60)
    
    # Testar conexão primeiro
    print("\n🔍 Testando conexão...")
    if test_db_connection():
        print("\n✅ Conexão OK! Executando exemplos...\n")
        
        # Executar exemplos
        exemplo_1_conexao_simples()
        exemplo_2_context_manager()
        exemplo_3_executar_query()
        exemplo_4_pool_conexoes()
        exemplo_5_info_banco()
        
        print("\n" + "="*60)
        print("✅ Todos os exemplos executados!")
        print("="*60)
    else:
        print("\n❌ Erro na conexão. Verifique as credenciais.")
        print("\n💡 O problema pode ser:")
        print("   1. Usuário não existe no servidor PostgreSQL")
        print("   2. Senha incorreta")
        print("   3. Database não existe")
        print("   4. Problemas de rede/firewall")

