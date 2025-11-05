#!/usr/bin/env python3
"""
Teste rápido de validação do MaraBet AI
"""

import os
from dotenv import load_dotenv

def quick_validation():
    """Teste rápido de validação"""
    
    print("⚡ TESTE RÁPIDO - MARABET AI")
    print("=" * 40)
    
    # Carregar .env
    load_dotenv()
    
    # Verificar credenciais essenciais
    credentials = {
        'API_FOOTBALL_KEY': os.getenv('API_FOOTBALL_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME')
    }
    
    print("🔍 VERIFICANDO CREDENCIAIS:")
    print("-" * 30)
    
    configured = 0
    total = len(credentials)
    
    for key, value in credentials.items():
        if value and not value.startswith('your_') and value != '':
            print(f"✅ {key}: OK")
            configured += 1
        else:
            print(f"❌ {key}: NÃO CONFIGURADA")
    
    print(f"\n📊 Status: {configured}/{total} configuradas")
    
    if configured == total:
        print("\n🎉 SISTEMA CONFIGURADO!")
        print("✅ Pronto para uso")
        return True
    else:
        print("\n⚠️ CONFIGURAÇÃO INCOMPLETA")
        print("💡 Edite o arquivo .env com suas credenciais")
        return False

if __name__ == "__main__":
    quick_validation()
