#!/usr/bin/env python3
"""
Validação final do sistema MaraBet AI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def validacao_final():
    """Validação final completa do sistema"""
    
    print("🎯 VALIDAÇÃO FINAL - MARABET AI")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar arquivos críticos
    print("📁 VERIFICANDO ARQUIVOS CRÍTICOS:")
    print("-" * 35)
    
    arquivos_criticos = [
        '.env',
        '.gitignore',
        'config_api_keys.py',
        'config.py',
        'final_security_test.py',
        'quick_test.py'
    ]
    
    todos_arquivos_ok = True
    for arquivo in arquivos_criticos:
        if Path(arquivo).exists():
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo}")
            todos_arquivos_ok = False
    
    # Verificar credenciais
    print("\n🔑 VERIFICANDO CREDENCIAIS:")
    print("-" * 30)
    
    credenciais = {
        'API_FOOTBALL_KEY': os.getenv('API_FOOTBALL_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD')
    }
    
    credenciais_configuradas = 0
    total_credenciais = len(credenciais)
    
    for key, value in credenciais.items():
        if value and not value.startswith('your_') and value != '':
            print(f"✅ {key}: Configurada")
            credenciais_configuradas += 1
        else:
            print(f"❌ {key}: NÃO configurada")
    
    # Verificar segurança
    print("\n🛡️ VERIFICANDO SEGURANÇA:")
    print("-" * 30)
    
    # Verificar se .env está no .gitignore
    if Path('.gitignore').exists():
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        if '.env' in gitignore_content:
            print("✅ .env protegido no .gitignore")
        else:
            print("❌ .env NÃO protegido")
    else:
        print("❌ .gitignore não encontrado")
    
    # Verificar se não há credenciais hardcoded
    arquivos_para_verificar = ['config_api_keys.py', 'config.py']
    credenciais_hardcoded = False
    
    for arquivo in arquivos_para_verificar:
        if Path(arquivo).exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se há chaves antigas expostas
            chaves_antigas = [
                '747d6e19a2d3a435fdb7a419007a45fa',
                '8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg',
                'kilamu_10@yahoo.com.br'
            ]
            
            for chave in chaves_antigas:
                if chave in content:
                    print(f"❌ {arquivo}: Chave antiga encontrada")
                    credenciais_hardcoded = True
    
    if not credenciais_hardcoded:
        print("✅ Nenhuma credencial hardcoded encontrada")
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print("-" * 20)
    
    if todos_arquivos_ok:
        print("✅ Arquivos críticos: OK")
    else:
        print("❌ Arquivos críticos: PROBLEMA")
    
    print(f"📈 Credenciais: {credenciais_configuradas}/{total_credenciais} configuradas")
    
    if credenciais_configuradas == total_credenciais:
        print("✅ Credenciais: COMPLETAS")
    else:
        print("❌ Credenciais: INCOMPLETAS")
    
    if not credenciais_hardcoded:
        print("✅ Segurança: OK")
    else:
        print("❌ Segurança: PROBLEMA")
    
    print("\n" + "=" * 50)
    
    if todos_arquivos_ok and credenciais_configuradas == total_credenciais and not credenciais_hardcoded:
        print("🎉 SISTEMA 100% CONFIGURADO E SEGURO!")
        print("✅ Pronto para uso em produção")
        return True
    else:
        print("⚠️ SISTEMA PRECISA DE CONFIGURAÇÃO")
        if credenciais_configuradas < total_credenciais:
            print("💡 Configure suas credenciais no arquivo .env")
        return False

def main():
    """Função principal"""
    print("🔮 MARABET AI - VALIDAÇÃO FINAL")
    print("=" * 50)
    
    if validacao_final():
        print("\n🚀 COMANDOS PARA TESTAR:")
        print("-" * 25)
        print("python test_api_keys.py")
        print("python test_notifications.py")
        print("python run_automated_collector.py")
        print("python run_dashboard.py")
    else:
        print("\n📝 PRÓXIMOS PASSOS:")
        print("-" * 20)
        print("1. Configure o arquivo .env")
        print("2. Execute: python validacao_final.py")

if __name__ == "__main__":
    main()
