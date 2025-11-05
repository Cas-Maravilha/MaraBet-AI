#!/usr/bin/env python3
"""
Script para configurar credenciais seguras no MaraBet AI
"""

import os
import sys
from pathlib import Path

def create_secure_env():
    """Cria arquivo .env seguro com credenciais do usuário"""
    
    print("🔐 MARABET AI - CONFIGURAÇÃO SEGURA DE CREDENCIAIS")
    print("=" * 60)
    print("⚠️  IMPORTANTE: Suas credenciais antigas foram comprometidas!")
    print("✅ Agora vamos configurar novas credenciais seguras.")
    print()
    
    # Verificar se .env já existe
    env_file = Path(".env")
    if env_file.exists():
        print("📁 Arquivo .env encontrado. Fazendo backup...")
        backup_file = Path(".env.backup")
        if backup_file.exists():
            backup_file.unlink()
        env_file.rename(backup_file)
        print("✅ Backup criado: .env.backup")
    
    print("\n🔑 CONFIGURAÇÃO DAS NOVAS CREDENCIAIS")
    print("=" * 40)
    
    # Coletar credenciais do usuário
    credentials = {}
    
    print("\n⚽ API FOOTBALL:")
    print("   Acesse: https://www.api-football.com/")
    print("   Gere uma nova chave de API")
    credentials['API_FOOTBALL_KEY'] = input("   Digite sua nova chave API-Football: ").strip()
    
    print("\n🤖 TELEGRAM BOT:")
    print("   Acesse: https://t.me/botfather")
    print("   Crie um novo bot com /newbot")
    credentials['TELEGRAM_BOT_TOKEN'] = input("   Digite o novo token do bot: ").strip()
    
    print("\n📱 TELEGRAM CHAT:")
    print("   Use o mesmo Chat ID ou gere um novo")
    chat_id = input("   Digite seu Chat ID (ou pressione Enter para manter 5550091597): ").strip()
    credentials['TELEGRAM_CHAT_ID'] = chat_id if chat_id else "5550091597"
    
    print("\n📧 EMAIL YAHOO:")
    print("   Use o mesmo email ou configure um novo")
    email = input("   Digite seu email Yahoo (ou pressione Enter para manter kilamu_10@yahoo.com.br): ").strip()
    credentials['SMTP_USERNAME'] = email if email else "kilamu_10@yahoo.com.br"
    credentials['NOTIFICATION_EMAIL'] = email if email else "kilamu_10@yahoo.com.br"
    credentials['ADMIN_EMAIL'] = email if email else "kilamu_10@yahoo.com.br"
    
    print("\n🔐 SENHA DO EMAIL:")
    print("   Configure uma senha de app específica no Yahoo")
    credentials['SMTP_PASSWORD'] = input("   Digite a senha de app do Yahoo: ").strip()
    
    # Chaves opcionais
    print("\n🎲 THE ODDS API (opcional):")
    print("   Acesse: https://the-odds-api.com/")
    odds_key = input("   Digite sua chave The Odds API (ou pressione Enter para pular): ").strip()
    credentials['THE_ODDS_API_KEY'] = odds_key if odds_key else "your_the_odds_api_key_here"
    
    # Gerar chave secreta
    import secrets
    credentials['SECRET_KEY'] = secrets.token_urlsafe(32)
    
    # Criar arquivo .env
    env_content = f"""# Configurações seguras do MaraBet AI
# NUNCA commite este arquivo para o repositório!

# Configurações da API
API_FOOTBALL_KEY={credentials['API_FOOTBALL_KEY']}
THE_ODDS_API_KEY={credentials['THE_ODDS_API_KEY']}

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Configurações da aplicação
SECRET_KEY={credentials['SECRET_KEY']}
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Configurações de notificações
# Telegram - Bot: @MaraBetAIBot
TELEGRAM_BOT_TOKEN={credentials['TELEGRAM_BOT_TOKEN']}
TELEGRAM_CHAT_ID={credentials['TELEGRAM_CHAT_ID']}

# Email - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME={credentials['SMTP_USERNAME']}
SMTP_PASSWORD={credentials['SMTP_PASSWORD']}
NOTIFICATION_EMAIL={credentials['NOTIFICATION_EMAIL']}
ADMIN_EMAIL={credentials['ADMIN_EMAIL']}
"""
    
    # Escrever arquivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ ARQUIVO .env CRIADO COM SUCESSO!")
    print("=" * 40)
    print("🔒 Suas credenciais estão agora protegidas")
    print("📁 Arquivo: .env (já está no .gitignore)")
    print("⚠️  NUNCA compartilhe este arquivo!")
    
    return True

def test_credentials():
    """Testa as credenciais configuradas"""
    print("\n🧪 TESTANDO CREDENCIAIS")
    print("=" * 30)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verificar se as variáveis estão carregadas
        api_key = os.getenv('API_FOOTBALL_KEY')
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        smtp_user = os.getenv('SMTP_USERNAME')
        
        if not api_key or api_key == 'your_api_football_key_here':
            print("❌ API_FOOTBALL_KEY não configurada")
            return False
        
        if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
            print("❌ TELEGRAM_BOT_TOKEN não configurado")
            return False
        
        if not smtp_user or smtp_user == 'your_yahoo_email_here':
            print("❌ SMTP_USERNAME não configurado")
            return False
        
        print("✅ Todas as credenciais carregadas com sucesso!")
        print(f"   ⚽ API Football: {api_key[:10]}...")
        print(f"   🤖 Telegram: {telegram_token[:10]}...")
        print(f"   📧 Email: {smtp_user}")
        print(f"   📱 Chat ID: {telegram_chat}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar credenciais: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 INICIANDO CONFIGURAÇÃO SEGURA")
    print("=" * 50)
    
    # Criar .env seguro
    if create_secure_env():
        print("\n🔧 CONFIGURAÇÃO CONCLUÍDA!")
        
        # Testar credenciais
        if test_credentials():
            print("\n🎉 SISTEMA CONFIGURADO COM SUCESSO!")
            print("=" * 40)
            print("✅ Credenciais seguras configuradas")
            print("✅ Arquivo .env protegido")
            print("✅ Sistema pronto para uso")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. Execute: python test_api_keys.py")
            print("2. Execute: python test_notifications.py")
            print("3. Inicie o sistema: python run_automated_collector.py")
        else:
            print("\n❌ Erro na configuração das credenciais")
            print("💡 Verifique se inseriu as credenciais corretamente")
    else:
        print("\n❌ Erro ao criar arquivo .env")
        print("💡 Verifique as permissões do diretório")

if __name__ == "__main__":
    main()
