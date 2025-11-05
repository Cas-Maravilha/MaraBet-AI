import psycopg2

# Credenciais de conexão remota ao PostgreSQL
config = {
    "host": "37.27.220.67",
    "port": "5432",
    "database": "marabet",  # Banco criado anteriormente
    "user": "meu_root$marabet",
    "password": "dudbeeGdNBSxjpEWlop"
}

try:
    print("🔄 Tentando conectar ao PostgreSQL...")
    print(f"   Host: {config['host']}")
    print(f"   Porta: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    print("")
    
    conn = psycopg2.connect(**config)
    print("✅ Conexão bem-sucedida!")
    
    # Executar uma query de teste
    cursor = conn.cursor()
    cursor.execute("SELECT version(), current_database(), current_user;")
    result = cursor.fetchone()
    
    print("\n📊 Informações da conexão:")
    print(f"   PostgreSQL: {result[0]}")
    print(f"   Database: {result[1]}")
    print(f"   User: {result[2]}")
    
    cursor.close()
    conn.close()
    print("\n✅ Conexão fechada com sucesso!")
    
except psycopg2.OperationalError as e:
    print(f"❌ Erro de conexão: {e}")
    print("\n💡 Verificações:")
    print("   1. Verifique se o servidor PostgreSQL está em execução")
    print("   2. Verifique se o firewall permite conexões na porta 5432")
    print("   3. Verifique se o IP 37.27.220.67 está correto")
    print("   4. Verifique se o pg_hba.conf permite conexões remotas")
except psycopg2.ProgrammingError as e:
    print(f"❌ Erro de programação: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")

