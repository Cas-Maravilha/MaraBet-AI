#!/usr/bin/env python3
"""
Teste de Conexão PostgreSQL
MaraBet AI - Teste rápido de conexão
"""

from database_connection import db

print("=" * 60)
print("🔍 TESTE DE CONEXÃO POSTGRESQL")
print("=" * 60)
print()

try:
    # Usar context manager (recomendado)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        
        print("✅ Conexão estabelecida com sucesso!")
        print()
        print("📊 Resultado:")
        print(f"   {result}")
        print()
        print("📋 Detalhes:")
        print(f"   Versão PostgreSQL: {result['version']}")
        
        # Testar mais informações
        cursor.execute("SELECT current_database(), current_user, now();")
        info = cursor.fetchone()
        
        print(f"   Database: {info['current_database']}")
        print(f"   User: {info['current_user']}")
        print(f"   Data/Hora: {info['now']}")
        
        cursor.close()
        
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
    print()
    print("💡 Verificações:")
    print("   1. Verifique se o usuário 'meu_usuario' existe no servidor")
    print("   2. Verifique se a senha está correta")
    print("   3. Verifique se o database 'meu_banco' existe")
    print("   4. Verifique se o servidor está acessível")

print()
print("=" * 60)

