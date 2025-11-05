#!/usr/bin/env python3
"""
Configuração do arquivo .env
MaraBet AI - Configura o arquivo .env com as credenciais fornecidas
"""

import os

def create_env_file():
    """Cria arquivo .env com as configurações fornecidas"""
    env_content = """# Configurações do Telegram para MaraBet AI
TELEGRAM_BOT_TOKEN=8227157482:AAHqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq
TELEGRAM_CHAT_ID=5550091597

# Configurações da API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso!")
        print("   Token: 8227157482...")
        print("   Chat ID: 5550091597")
        print("   Nome: Mara Maravilha")
        print("   Idioma: pt-br")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CONFIGURANDO ARQUIVO .ENV - MARABET AI")
    print("=" * 50)
    
    if create_env_file():
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 30)
        print("✅ Token configurado")
        print("✅ Chat ID configurado")
        print("✅ API Football configurada")
        print("✅ Banco de dados configurado")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("=" * 20)
        print("1. Execute: python test_telegram_config.py")
        print("2. Se funcionar, execute: python run_telegram_auto.py")
        
        return True
    else:
        print("\n❌ Erro na configuração")
        return False

if __name__ == "__main__":
    main()
