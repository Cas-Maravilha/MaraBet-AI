#!/usr/bin/env python3
"""
Atualizar Token do Telegram
MaraBet AI - Atualiza o token do Telegram no arquivo .env
"""

import os

def update_telegram_token():
    """Atualiza o token do Telegram no arquivo .env"""
    new_token = "7646701850:AAGuBMODMggvyWt54Uh8AV7Vt4_DGm47va0"
    chat_id = "5550091597"
    
    env_content = f"""# Configurações do Telegram para MaraBet AI
TELEGRAM_BOT_TOKEN={new_token}
TELEGRAM_CHAT_ID={chat_id}

# Configurações da API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env atualizado com sucesso!")
        print(f"   Novo Token: {new_token[:10]}...")
        print(f"   Chat ID: {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar .env: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 ATUALIZANDO TOKEN DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    if update_telegram_token():
        print("\n🎉 TOKEN ATUALIZADO COM SUCESSO!")
        print("=" * 40)
        print("✅ Novo token configurado")
        print("✅ Chat ID mantido")
        print("✅ API Football mantida")
        print("✅ Banco de dados mantido")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("=" * 20)
        print("1. Execute: python test_telegram_config.py")
        print("2. Se funcionar, execute: python run_telegram_auto.py")
        
        return True
    else:
        print("\n❌ Erro na atualização")
        return False

if __name__ == "__main__":
    main()
