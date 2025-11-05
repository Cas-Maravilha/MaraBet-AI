#!/usr/bin/env python3
"""
Configuração do Bot Telegram
MaraBet AI - Setup do bot Telegram para envio de predições
"""

import requests
import json
import os
from datetime import datetime

class TelegramBotSetup:
    """Configurador do bot Telegram"""
    
    def __init__(self):
        self.setup_instructions = """
🤖 CONFIGURAÇÃO DO BOT TELEGRAM - MARABET AI
===============================================

Para enviar predições via Telegram, você precisa:

1. CRIAR UM BOT NO TELEGRAM:
   - Abra o Telegram e procure por @BotFather
   - Envie o comando /newbot
   - Escolha um nome para o bot (ex: MaraBet AI Predictions)
   - Escolha um username (ex: marabet_ai_bot)
   - Copie o TOKEN que será fornecido

2. OBTER SEU CHAT ID:
   - Envie uma mensagem para o bot criado
   - Execute este script para obter o Chat ID automaticamente

3. CONFIGURAR AS CREDENCIAIS:
   - Edite o arquivo send_predictions_telegram.py
   - Substitua YOUR_TELEGRAM_BOT_TOKEN pelo token do bot
   - Substitua YOUR_TELEGRAM_CHAT_ID pelo seu Chat ID

4. TESTAR O ENVIO:
   - Execute: python send_predictions_telegram.py
"""
    
    def get_bot_token(self):
        """Solicita token do bot"""
        print("🤖 CONFIGURAÇÃO DO BOT TELEGRAM")
        print("=" * 50)
        print(self.setup_instructions)
        
        token = input("\nDigite o TOKEN do seu bot (ou pressione Enter para pular): ").strip()
        return token if token else None
    
    def get_chat_id(self, bot_token):
        """Obtém Chat ID do usuário"""
        if not bot_token:
            print("❌ Token não fornecido")
            return None
        
        print(f"\n🔍 OBTENDO CHAT ID...")
        print("   Envie uma mensagem para o seu bot no Telegram primeiro!")
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get('result', [])
                
                if updates:
                    chat_id = updates[-1]['message']['chat']['id']
                    username = updates[-1]['message']['from'].get('username', 'N/A')
                    first_name = updates[-1]['message']['from'].get('first_name', 'N/A')
                    
                    print(f"✅ Chat ID encontrado: {chat_id}")
                    print(f"   Usuário: {first_name} (@{username})")
                    return str(chat_id)
                else:
                    print("❌ Nenhuma mensagem encontrada")
                    print("   Envie uma mensagem para o bot primeiro!")
                    return None
            else:
                print(f"❌ Erro ao obter updates: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def test_bot_connection(self, bot_token, chat_id):
        """Testa conexão com o bot"""
        if not bot_token or not chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': '🤖 Teste de conexão do MaraBet AI Bot!\n\nSe você recebeu esta mensagem, a configuração está funcionando!',
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ Teste de conexão bem-sucedido!")
                print("   Mensagem de teste enviada para o Telegram")
                return True
            else:
                print(f"❌ Erro no teste: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def create_config_file(self, bot_token, chat_id):
        """Cria arquivo de configuração"""
        config = {
            'telegram_bot_token': bot_token,
            'telegram_chat_id': chat_id,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        try:
            with open('telegram_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Arquivo de configuração criado: telegram_config.json")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar arquivo de configuração: {e}")
            return False
    
    def update_send_script(self, bot_token, chat_id):
        """Atualiza script de envio com as credenciais"""
        try:
            # Ler arquivo atual
            with open('send_predictions_telegram.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir credenciais
            content = content.replace('YOUR_TELEGRAM_BOT_TOKEN', bot_token)
            content = content.replace('YOUR_TELEGRAM_CHAT_ID', chat_id)
            
            # Salvar arquivo atualizado
            with open('send_predictions_telegram.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Script de envio atualizado com as credenciais")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar script: {e}")
            return False
    
    def run_setup(self):
        """Executa configuração completa"""
        print("🚀 CONFIGURAÇÃO DO BOT TELEGRAM - MARABET AI")
        print("=" * 60)
        
        # 1. Obter token do bot
        bot_token = self.get_bot_token()
        if not bot_token:
            print("\n⚠️ Configuração cancelada")
            print("   Execute novamente quando tiver o token do bot")
            return False
        
        # 2. Obter Chat ID
        chat_id = self.get_chat_id(bot_token)
        if not chat_id:
            print("\n⚠️ Não foi possível obter o Chat ID")
            print("   Envie uma mensagem para o bot e tente novamente")
            return False
        
        # 3. Testar conexão
        print(f"\n🧪 TESTANDO CONEXÃO...")
        if not self.test_bot_connection(bot_token, chat_id):
            print("❌ Teste de conexão falhou")
            return False
        
        # 4. Criar arquivo de configuração
        print(f"\n💾 SALVANDO CONFIGURAÇÃO...")
        if not self.create_config_file(bot_token, chat_id):
            return False
        
        # 5. Atualizar script de envio
        if not self.update_send_script(bot_token, chat_id):
            return False
        
        print(f"\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Bot Telegram configurado")
        print("✅ Chat ID obtido")
        print("✅ Conexão testada")
        print("✅ Arquivo de configuração criado")
        print("✅ Script de envio atualizado")
        
        print(f"\n📱 AGORA VOCÊ PODE:")
        print("   - Executar: python send_predictions_telegram.py")
        print("   - Receber predições automaticamente no Telegram")
        print("   - Configurar envios automáticos")
        
        return True

def main():
    """Função principal"""
    setup = TelegramBotSetup()
    return setup.run_setup()

if __name__ == "__main__":
    main()
