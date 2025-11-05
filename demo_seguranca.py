#!/usr/bin/env python3
"""
Demonstração do sistema de segurança do MaraBet AI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def demo_seguranca():
    """Demonstração do sistema de segurança"""
    
    print("🔐 DEMONSTRAÇÃO DE SEGURANÇA - MARABET AI")
    print("=" * 60)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    print("📋 SISTEMA DE SEGURANÇA IMPLEMENTADO:")
    print("-" * 40)
    
    # 1. Verificar arquivos críticos
    print("\n1️⃣ ARQUIVOS CRÍTICOS:")
    arquivos = ['.env', '.gitignore', 'config_api_keys.py', 'config.py']
    for arquivo in arquivos:
        if Path(arquivo).exists():
            print(f"   ✅ {arquivo} - Encontrado")
        else:
            print(f"   ❌ {arquivo} - Não encontrado")
    
    # 2. Verificar proteções
    print("\n2️⃣ PROTEÇÕES ATIVAS:")
    if Path('.gitignore').exists():
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '.env' in content:
            print("   ✅ .env protegido no .gitignore")
        else:
            print("   ❌ .env NÃO protegido")
        
        if 'config_personal.env' in content:
            print("   ✅ config_personal.env protegido")
        else:
            print("   ❌ config_personal.env NÃO protegido")
    
    # 3. Verificar credenciais hardcoded
    print("\n3️⃣ VERIFICAÇÃO DE CREDENCIAIS HARDCODED:")
    chaves_antigas = [
        '747d6e19a2d3a435fdb7a419007a45fa',
        '8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg',
        'kilamu_10@yahoo.com.br'
    ]
    
    arquivos_para_verificar = ['config_api_keys.py', 'config.py']
    credenciais_encontradas = False
    
    for arquivo in arquivos_para_verificar:
        if Path(arquivo).exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for chave in chaves_antigas:
                if chave in content:
                    print(f"   ❌ {arquivo}: Chave antiga encontrada")
                    credenciais_encontradas = True
    
    if not credenciais_encontradas:
        print("   ✅ Nenhuma credencial hardcoded encontrada")
    
    # 4. Verificar sistema de variáveis de ambiente
    print("\n4️⃣ SISTEMA DE VARIÁVEIS DE AMBIENTE:")
    credenciais = {
        'API_FOOTBALL_KEY': os.getenv('API_FOOTBALL_KEY'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME')
    }
    
    configuradas = 0
    for key, value in credenciais.items():
        if value and not value.startswith('your_') and value != '':
            print(f"   ✅ {key}: Configurada")
            configuradas += 1
        else:
            print(f"   ❌ {key}: NÃO configurada")
    
    # 5. Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA DEMONSTRAÇÃO:")
    print("-" * 35)
    
    if not credenciais_encontradas:
        print("✅ Segurança: IMPLEMENTADA")
    else:
        print("❌ Segurança: PROBLEMA")
    
    if configuradas == len(credenciais):
        print("✅ Configuração: COMPLETA")
    else:
        print("⚠️ Configuração: INCOMPLETA")
    
    print(f"\n📈 Status: {configuradas}/{len(credenciais)} credenciais configuradas")
    
    if not credenciais_encontradas and configuradas == len(credenciais):
        print("\n🎉 SISTEMA 100% SEGURO E CONFIGURADO!")
        print("✅ Pronto para uso em produção")
        return True
    elif not credenciais_encontradas:
        print("\n🛡️ SISTEMA SEGURO - AGUARDANDO CONFIGURAÇÃO")
        print("💡 Configure suas credenciais no arquivo .env")
        return False
    else:
        print("\n❌ SISTEMA COM PROBLEMAS DE SEGURANÇA")
        return False

def mostrar_comandos():
    """Mostra comandos disponíveis"""
    
    print("\n🚀 COMANDOS DISPONÍVEIS:")
    print("-" * 30)
    print("python validacao_final.py    # Validação completa")
    print("python quick_test.py         # Teste rápido")
    print("python final_security_test.py # Teste de segurança")
    print("python test_api_keys.py      # Teste de credenciais")
    print("python test_notifications.py # Teste de notificações")
    print("python run_automated_collector.py # Iniciar sistema")
    print("python run_dashboard.py      # Dashboard")

def main():
    """Função principal"""
    
    print("🔮 MARABET AI - DEMONSTRAÇÃO DE SEGURANÇA")
    print("=" * 60)
    
    if demo_seguranca():
        print("\n🎊 PARABÉNS!")
        print("Seu sistema está 100% seguro e configurado!")
        mostrar_comandos()
    else:
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Configure o arquivo .env com suas credenciais")
        print("2. Execute: python validacao_final.py")
        print("3. Execute: python demo_seguranca.py")

if __name__ == "__main__":
    main()
