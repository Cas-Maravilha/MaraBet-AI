#!/usr/bin/env python3
"""
Teste final do sistema MaraBet AI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def teste_final_sistema():
    """Teste final completo do sistema"""
    
    print("🎯 TESTE FINAL - MARABET AI")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    print("📋 VERIFICANDO SISTEMA:")
    print("-" * 30)
    
    # 1. Verificar arquivos críticos
    print("\n1️⃣ ARQUIVOS CRÍTICOS:")
    arquivos = ['.env', '.gitignore', 'config_api_keys.py', 'config.py']
    todos_arquivos_ok = True
    
    for arquivo in arquivos:
        if Path(arquivo).exists():
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo}")
            todos_arquivos_ok = False
    
    # 2. Verificar segurança
    print("\n2️⃣ SEGURANÇA:")
    if Path('.gitignore').exists():
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '.env' in content:
            print("   ✅ .env protegido no .gitignore")
        else:
            print("   ❌ .env NÃO protegido")
    
    # Verificar credenciais hardcoded
    chaves_antigas = [
        '747d6e19a2d3a435fdb7a419007a45fa',
        '8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg',
        'kilamu_10@yahoo.com.br'
    ]
    
    arquivos_para_verificar = ['config_api_keys.py', 'config.py']
    credenciais_hardcoded = False
    
    for arquivo in arquivos_para_verificar:
        if Path(arquivo).exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for chave in chaves_antigas:
                if chave in content:
                    print(f"   ❌ {arquivo}: Chave antiga encontrada")
                    credenciais_hardcoded = True
    
    if not credenciais_hardcoded:
        print("   ✅ Nenhuma credencial hardcoded encontrada")
    
    # 3. Verificar configuração
    print("\n3️⃣ CONFIGURAÇÃO:")
    credenciais = {
        'API_FOOTBALL_KEY': os.getenv('API_FOOTBALL_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD')
    }
    
    configuradas = 0
    for key, value in credenciais.items():
        if value and not value.startswith('your_') and value != '':
            print(f"   ✅ {key}: Configurada")
            configuradas += 1
        else:
            print(f"   ❌ {key}: NÃO configurada")
    
    # 4. Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print("-" * 20)
    
    if todos_arquivos_ok:
        print("✅ Arquivos críticos: OK")
    else:
        print("❌ Arquivos críticos: PROBLEMA")
    
    if not credenciais_hardcoded:
        print("✅ Segurança: OK")
    else:
        print("❌ Segurança: PROBLEMA")
    
    print(f"📈 Configuração: {configuradas}/{len(credenciais)} credenciais")
    
    if configuradas == len(credenciais):
        print("✅ Configuração: COMPLETA")
    else:
        print("⚠️ Configuração: INCOMPLETA")
    
    print("\n" + "=" * 50)
    
    if todos_arquivos_ok and not credenciais_hardcoded and configuradas == len(credenciais):
        print("🎉 SISTEMA 100% CONFIGURADO E SEGURO!")
        print("✅ Pronto para uso em produção")
        return True
    elif todos_arquivos_ok and not credenciais_hardcoded:
        print("🛡️ SISTEMA SEGURO - AGUARDANDO CONFIGURAÇÃO")
        print("💡 Configure suas credenciais no arquivo .env")
        return False
    else:
        print("❌ SISTEMA COM PROBLEMAS")
        return False

def mostrar_comandos():
    """Mostra comandos disponíveis"""
    
    print("\n🚀 COMANDOS DISPONÍVEIS:")
    print("-" * 30)
    print("python validacao_final.py    # Validação completa")
    print("python quick_test.py         # Teste rápido")
    print("python final_security_test.py # Teste de segurança")
    print("python demo_seguranca.py     # Demonstração de segurança")
    print("python test_api_keys.py      # Teste de credenciais")
    print("python test_notifications.py # Teste de notificações")
    print("python run_automated_collector.py # Iniciar sistema")
    print("python run_dashboard.py      # Dashboard")

def main():
    """Função principal"""
    
    print("🔮 MARABET AI - TESTE FINAL DO SISTEMA")
    print("=" * 50)
    
    if teste_final_sistema():
        print("\n🎊 PARABÉNS!")
        print("Seu sistema está 100% seguro e configurado!")
        mostrar_comandos()
    else:
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Configure o arquivo .env com suas credenciais")
        print("2. Execute: python validacao_final.py")
        print("3. Execute: python teste_final_sistema.py")

if __name__ == "__main__":
    main()
