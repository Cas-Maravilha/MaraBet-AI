import psycopg2

# Versão com o banco "meu_banco" (caso você tenha criado)
# Se o banco não existir, ele dará erro
try:
    conn = psycopg2.connect(
        host="37.27.220.67",
        port="5432",
        database="meu_banco",  # Banco "meu_banco"
        user="meu_root$marabet",
        password="dudbeeGdNBSxjpEWlop"
    )
    print("✅ Conexão bem-sucedida!")
    
    # Executar query de teste
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user;")
    result = cursor.fetchone()
    print(f"Database: {result[0]}")
    print(f"User: {result[1]}")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ Erro de conexão: {e}")
    print("\n💡 O banco 'meu_banco' pode não existir.")
    print("   Use 'marabet' ou crie o banco 'meu_banco' primeiro.")
except Exception as e:
    print(f"❌ Erro: {e}")

