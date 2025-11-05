import psycopg2

# Teste de conexão LOCAL primeiro (localhost/WSL)
# Use este script para testar se o PostgreSQL está funcionando localmente

config_local = {
    "host": "localhost",
    "port": "5432",
    "database": "marabet",
    "user": "meu_root$marabet",
    "password": "dudbeeGdNBSxjpEWlop"
}

config_remoto = {
    "host": "37.27.220.67",
    "port": "5432",
    "database": "marabet",
    "user": "meu_root$marabet",
    "password": "dudbeeGdNBSxjpEWlop"
}

print("=" * 60)
print("TESTE 1: Conexão LOCAL (localhost)")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar ao PostgreSQL LOCAL...")
    conn = psycopg2.connect(**config_local)
    print("✅ Conexão LOCAL bem-sucedida!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version(), current_database(), current_user;")
    result = cursor.fetchone()
    
    print(f"\n📊 PostgreSQL: {result[0]}")
    print(f"📊 Database: {result[1]}")
    print(f"📊 User: {result[2]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro na conexão LOCAL: {e}")

print("\n" + "=" * 60)
print("TESTE 2: Conexão REMOTA (37.27.220.67)")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar ao PostgreSQL REMOTO...")
    print(f"   IP: {config_remoto['host']}")
    print(f"   Porta: {config_remoto['port']}")
    
    conn = psycopg2.connect(**config_remoto)
    print("✅ Conexão REMOTA bem-sucedida!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version(), current_database(), current_user;")
    result = cursor.fetchone()
    
    print(f"\n📊 PostgreSQL: {result[0]}")
    print(f"📊 Database: {result[1]}")
    print(f"📊 User: {result[2]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro na conexão REMOTA: {e}")
    print("\n💡 Verificações necessárias:")
    print("   1. O PostgreSQL no servidor 37.27.220.67 está em execução?")
    print("   2. O firewall do servidor permite conexões na porta 5432?")
    print("   3. O postgresql.conf tem listen_addresses = '*'?")
    print("   4. O pg_hba.conf permite conexões remotas do seu IP?")

