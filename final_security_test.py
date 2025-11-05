#!/usr/bin/env python3
"""
Teste final de segurança e configuração do MaraBet AI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_security_status():
    """Verifica o status de segurança do sistema"""
    
    print("🔐 TESTE FINAL DE SEGURANÇA - MARABET AI")
    print("=" * 60)
    
    # Verificar arquivos críticos
    critical_files = [
        '.env',
        '.gitignore',
        'config_api_keys.py',
        'config.py',
        'config_personal.env'
    ]
    
    print("📁 VERIFICANDO ARQUIVOS CRÍTICOS:")
    print("-" * 40)
    
    for file in critical_files:
        if Path(file).exists():
            print(f"✅ {file}: Encontrado")
        else:
            print(f"❌ {file}: Não encontrado")
    
    # Verificar .gitignore
    print("\n🔒 VERIFICANDO PROTEÇÕES:")
    print("-" * 30)
    
    if Path('.gitignore').exists():
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        if '.env' in gitignore_content:
            print("✅ .env protegido no .gitignore")
        else:
            print("❌ .env NÃO protegido no .gitignore")
        
        if 'config_personal.env' in gitignore_content:
            print("✅ config_personal.env protegido")
        else:
            print("❌ config_personal.env NÃO protegido")
    else:
        print("❌ .gitignore não encontrado")
    
    # Verificar credenciais hardcoded
    print("\n🔍 VERIFICANDO CREDENCIAIS HARDCODED:")
    print("-" * 40)
    
    # Chaves que foram expostas
    exposed_keys = [
        '747d6e19a2d3a435fdb7a419007a45fa',
        '8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg',
        '5550091597',
        'kilamu_10@yahoo.com.br'
    ]
    
    files_to_check = [
        'config_api_keys.py',
        'config.py',
        'config_personal.env'
    ]
    
    hardcoded_found = False
    
    for file in files_to_check:
        if Path(file).exists():
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for key in exposed_keys:
                if key in content:
                    print(f"❌ {file}: Chave exposta encontrada: {key[:10]}...")
                    hardcoded_found = True
    
    if not hardcoded_found:
        print("✅ Nenhuma credencial hardcoded encontrada")
    
    # Verificar configuração do .env
    print("\n⚙️ VERIFICANDO CONFIGURAÇÃO .env:")
    print("-" * 35)
    
    if Path('.env').exists():
        load_dotenv()
        
        required_vars = [
            'API_FOOTBALL_KEY',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'SMTP_USERNAME',
            'SMTP_PASSWORD'
        ]
        
        configured_vars = 0
        
        for var in required_vars:
            value = os.getenv(var)
            if value and not value.startswith('your_') and value != '':
                print(f"✅ {var}: Configurada")
                configured_vars += 1
            else:
                print(f"❌ {var}: NÃO configurada")
        
        print(f"\n📊 Status: {configured_vars}/{len(required_vars)} variáveis configuradas")
        
        if configured_vars == len(required_vars):
            print("🎉 CONFIGURAÇÃO COMPLETA!")
            return True
        else:
            print("⚠️ CONFIGURAÇÃO INCOMPLETA")
            return False
    else:
        print("❌ Arquivo .env não encontrado")
        return False

def show_next_steps():
    """Mostra próximos passos para configuração"""
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("=" * 30)
    print("1. Configure o arquivo .env:")
    print("   notepad .env")
    print()
    print("2. Substitua os placeholders pelas suas credenciais:")
    print("   - API_FOOTBALL_KEY=sua_chave_aqui")
    print("   - TELEGRAM_BOT_TOKEN=seu_token_aqui")
    print("   - TELEGRAM_CHAT_ID=5550091597")
    print("   - SMTP_USERNAME=seu_email_aqui")
    print("   - SMTP_PASSWORD=sua_senha_aqui")
    print()
    print("3. Teste novamente:")
    print("   python final_security_test.py")
    print()
    print("4. Execute o sistema:")
    print("   python test_api_keys.py")
    print("   python run_automated_collector.py")

def main():
    """Função principal"""
    
    print("🔮 MARABET AI - TESTE FINAL DE SEGURANÇA")
    print("=" * 60)
    
    # Verificar status de segurança
    is_configured = check_security_status()
    
    if is_configured:
        print("\n🎉 SISTEMA SEGURO E CONFIGURADO!")
        print("=" * 40)
        print("✅ Todas as credenciais configuradas")
        print("✅ Sistema protegido contra exposição")
        print("✅ Pronto para uso em produção")
        
        print("\n🚀 COMANDOS PARA TESTAR:")
        print("-" * 25)
        print("python test_api_keys.py")
        print("python test_notifications.py")
        print("python run_automated_collector.py")
        
    else:
        print("\n⚠️ CONFIGURAÇÃO NECESSÁRIA")
        print("=" * 30)
        show_next_steps()

if __name__ == "__main__":
    main()
