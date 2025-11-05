#!/usr/bin/env python3
"""
Teste de configuração segura do MaraBet AI
"""

import os
from dotenv import load_dotenv

def test_secure_config():
    """Testa se as credenciais estão configuradas corretamente"""
    
    print("🧪 TESTE DE CONFIGURAÇÃO SEGURA - MARABET AI")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar credenciais
    credentials = {
        'API_FOOTBALL_KEY': os.getenv('API_FOOTBALL_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
    }
    
    print("🔍 VERIFICANDO CREDENCIAIS:")
    print("-" * 30)
    
    all_configured = True
    
    for key, value in credentials.items():
        if not value or value.startswith('your_') or value == '':
            print(f"❌ {key}: NÃO CONFIGURADA")
            all_configured = False
        else:
            # Mostrar apenas parte da credencial por segurança
            if 'PASSWORD' in key:
                print(f"✅ {key}: {'*' * len(value)}")
            else:
                print(f"✅ {key}: {value[:10]}...")
    
    print("\n" + "=" * 50)
    
    if all_configured:
        print("🎉 CONFIGURAÇÃO SEGURA CONCLUÍDA!")
        print("✅ Todas as credenciais estão configuradas")
        print("✅ Sistema pronto para uso")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Execute: python test_api_keys.py")
        print("2. Execute: python test_notifications.py")
        print("3. Inicie o sistema: python run_automated_collector.py")
        
        return True
    else:
        print("❌ CONFIGURAÇÃO INCOMPLETA")
        print("💡 Edite o arquivo .env com suas credenciais")
        print("📝 Use: notepad .env")
        
        return False

if __name__ == "__main__":
    test_secure_config()
