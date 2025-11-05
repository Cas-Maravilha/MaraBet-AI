#!/usr/bin/env python3
"""
Script para configurar novas chaves seguras no MaraBet AI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def configurar_novas_chaves():
    """Configura novas chaves seguras no sistema"""
    
    print("🔐 MARABET AI - CONFIGURAÇÃO DE NOVAS CHAVES SEGURAS")
    print("=" * 70)
    print("⚠️  IMPORTANTE: Suas chaves antigas foram expostas!")
    print("✅ Agora vamos configurar novas chaves seguras.")
    print()
    
    # Verificar se .env existe
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado!")
        print("💡 Execute primeiro: python configurar_credenciais.py")
        return False
    
    print("🔑 CONFIGURAÇÃO DAS NOVAS CHAVES SEGURAS")
    print("=" * 50)
    
    # Coletar novas credenciais do usuário
    print("\n⚽ API FOOTBALL:")
    print("   Acesse: https://www.api-football.com/")
    print("   Gere uma nova chave de API")
    nova_api_football = input("   Digite sua nova chave API-Football: ").strip()
    
    print("\n🤖 TELEGRAM BOT:")
    print("   Acesse: https://t.me/botfather")
    print("   Crie um novo bot com /newbot")
    novo_telegram_token = input("   Digite o novo token do bot: ").strip()
    
    print("\n📱 TELEGRAM CHAT:")
    print("   Use o mesmo Chat ID ou gere um novo")
    novo_chat_id = input("   Digite seu Chat ID (ou pressione Enter para manter 5550091597): ").strip()
    if not novo_chat_id:
        novo_chat_id = "5550091597"
    
    print("\n📧 EMAIL YAHOO:")
    print("   Use o mesmo email ou configure um novo")
    novo_email = input("   Digite seu email Yahoo (ou pressione Enter para manter kilamu_10@yahoo.com.br): ").strip()
    if not novo_email:
        novo_email = "kilamu_10@yahoo.com.br"
    
    print("\n🔐 SENHA DO EMAIL:")
    print("   Configure uma senha de app específica no Yahoo")
    nova_senha = input("   Digite a senha de app do Yahoo: ").strip()
    
    # Chaves opcionais
    print("\n🎲 THE ODDS API (opcional):")
    print("   Acesse: https://the-odds-api.com/")
    nova_odds_key = input("   Digite sua chave The Odds API (ou pressione Enter para pular): ").strip()
    
    # Gerar chave secreta
    import secrets
    nova_secret_key = secrets.token_urlsafe(32)
    
    # Criar novo arquivo .env
    env_content = f"""# Configurações seguras do MaraBet AI
# NUNCA commite este arquivo para o repositório!

# Configurações da API
API_FOOTBALL_KEY={nova_api_football}
THE_ODDS_API_KEY={nova_odds_key if nova_odds_key else 'your_the_odds_api_key_here'}

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Configurações da aplicação
SECRET_KEY={nova_secret_key}
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Configurações de notificações
# Telegram - Bot: @MaraBetAIBot
TELEGRAM_BOT_TOKEN={novo_telegram_token}
TELEGRAM_CHAT_ID={novo_chat_id}

# Email - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME={novo_email}
SMTP_PASSWORD={nova_senha}
NOTIFICATION_EMAIL={novo_email}
ADMIN_EMAIL={novo_email}
"""
    
    # Fazer backup do arquivo atual
    if env_file.exists():
        print("\n📁 Fazendo backup do arquivo .env atual...")
        backup_file = Path(".env.backup")
        if backup_file.exists():
            backup_file.unlink()
        env_file.rename(backup_file)
        print("✅ Backup criado: .env.backup")
    
    # Escrever novo arquivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ ARQUIVO .env ATUALIZADO COM NOVAS CHAVES!")
    print("=" * 50)
    print("🔒 Suas novas credenciais estão agora protegidas")
    print("📁 Arquivo: .env (já está no .gitignore)")
    print("⚠️  NUNCA compartilhe este arquivo!")
    
    return True

def testar_novas_credenciais():
    """Testa as novas credenciais configuradas"""
    print("\n🧪 TESTANDO NOVAS CREDENCIAIS")
    print("=" * 40)
    
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
        
        print("✅ Todas as novas credenciais carregadas com sucesso!")
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
    print("🚀 INICIANDO CONFIGURAÇÃO DE NOVAS CHAVES SEGURAS")
    print("=" * 70)
    
    # Configurar novas chaves
    if configurar_novas_chaves():
        print("\n🔧 CONFIGURAÇÃO CONCLUÍDA!")
        
        # Testar novas credenciais
        if testar_novas_credenciais():
            print("\n🎉 NOVAS CHAVES CONFIGURADAS COM SUCESSO!")
            print("=" * 50)
            print("✅ Novas credenciais seguras configuradas")
            print("✅ Sistema protegido contra exposição")
            print("✅ Pronto para uso em produção")
            
            print("\n🚀 COMANDOS PARA TESTAR:")
            print("-" * 30)
            print("python teste_final_sistema.py")
            print("python test_api_keys.py")
            print("python test_notifications.py")
            print("python run_automated_collector.py")
        else:
            print("\n❌ Erro na configuração das novas credenciais")
            print("💡 Verifique se inseriu as credenciais corretamente")
    else:
        print("\n❌ Erro ao configurar novas chaves")
        print("💡 Verifique se o arquivo .env existe")

if __name__ == "__main__":
    main()
