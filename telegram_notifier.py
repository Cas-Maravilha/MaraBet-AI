#!/usr/bin/env python3
"""
Sistema de Notificações Telegram para Predições MaraBet AI
Envia predições reais para o Telegram
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.config_file = "telegram_config.json"
        self.config = self.load_config()
        self.base_url = f"https://api.telegram.org/bot{self.config.get('telegram_bot_token', '')}"
        
    def load_config(self):
        """Carrega configuração do Telegram"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Salva configuração do Telegram"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def setup_telegram(self):
        """Configura o bot do Telegram"""
        print("🤖 CONFIGURAÇÃO DO TELEGRAM BOT")
        print("=" * 50)
        
        if not self.config.get('telegram_bot_token') or self.config.get('telegram_bot_token') == 'DEMO_TOKEN_123456789:ABCdefGHIjklMNOpqrsTUVwxyz':
            print("❌ Token do bot não configurado!")
            print("\n📋 COMO CONFIGURAR:")
            print("1. Abra o Telegram e procure por @BotFather")
            print("2. Digite /newbot")
            print("3. Escolha um nome para seu bot (ex: MaraBet AI Bot)")
            print("4. Escolha um username (ex: marabet_ai_bot)")
            print("5. Copie o token que o BotFather fornecer")
            print("6. Cole o token abaixo:")
            
            token = input("\n🔑 Cole o token do bot aqui: ").strip()
            if token:
                self.config['telegram_bot_token'] = token
                self.save_config()
                print("✅ Token salvo!")
            else:
                print("❌ Token não fornecido!")
                return False
        
        if not self.config.get('telegram_chat_id') or self.config.get('telegram_chat_id') == 'DEMO_CHAT_ID_123456789':
            print("\n📱 CONFIGURANDO CHAT ID:")
            print("1. Envie uma mensagem para seu bot no Telegram")
            print("2. Acesse: https://api.telegram.org/bot{}/getUpdates".format(self.config['telegram_bot_token']))
            print("3. Procure por 'chat':{'id': e copie o número")
            print("4. Cole o Chat ID abaixo:")
            
            chat_id = input("\n💬 Cole o Chat ID aqui: ").strip()
            if chat_id:
                self.config['telegram_chat_id'] = chat_id
                self.save_config()
                print("✅ Chat ID salvo!")
            else:
                print("❌ Chat ID não fornecido!")
                return False
        
        # Testar conexão
        if self.test_connection():
            print("✅ Telegram configurado com sucesso!")
            return True
        else:
            print("❌ Erro na configuração do Telegram!")
            return False
    
    def test_connection(self):
        """Testa conexão com o Telegram"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logger.info(f"✅ Bot conectado: {bot_info['result']['first_name']}")
                    return True
            logger.error(f"❌ Erro na conexão: {response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def send_message(self, message, parse_mode='HTML'):
        """Envia mensagem para o Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.config.get('telegram_chat_id'),
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("✅ Mensagem enviada com sucesso!")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar: {result.get('description', 'Erro desconhecido')}")
            else:
                logger.error(f"❌ Erro HTTP: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def load_predictions(self):
        """Carrega predições dos arquivos JSON"""
        prediction_files = [f for f in os.listdir('.') if 'predictions' in f and f.endswith('.json')]
        predictions = []
        
        for filename in prediction_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                match_data = data.get('match_data', {})
                pred_data = data.get('predictions', {})
                
                predictions.append({
                    'match': f"{match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}",
                    'league': match_data.get('league', 'N/A'),
                    'predictions': pred_data,
                    'total_predictions': data.get('total_predictions', 0),
                    'generated_at': data.get('generated_at', 'N/A')
                })
                
            except Exception as e:
                logger.error(f"Erro ao carregar {filename}: {e}")
        
        return predictions
    
    def format_prediction_message(self, prediction):
        """Formata mensagem de predição para o Telegram"""
        match = prediction['match']
        league = prediction['league']
        predictions = prediction['predictions']
        total = prediction['total_predictions']
        
        message = f"🎯 <b>PREDIÇÕES MARABET AI</b>\n\n"
        message += f"🏆 <b>{match}</b>\n"
        message += f"🏟️ {league}\n"
        message += f"📊 {total} predições geradas\n\n"
        
        # Adicionar predições por categoria
        for category, preds in predictions.items():
            if isinstance(preds, dict) and preds:
                message += f"<b>{category.upper()}:</b>\n"
                
                # Mostrar apenas as melhores predições (probabilidade > 0.6)
                best_predictions = [(k, v) for k, v in preds.items() if v > 0.6]
                best_predictions.sort(key=lambda x: x[1], reverse=True)
                
                for bet_type, prob in best_predictions[:3]:  # Top 3 por categoria
                    emoji = "🟢" if prob > 0.75 else "🟡" if prob > 0.65 else "🔴"
                    message += f"{emoji} {bet_type}: {prob:.1%}\n"
                
                message += "\n"
        
        message += f"⏰ Gerado em: {prediction['generated_at'][:16]}\n"
        message += f"🤖 Sistema MaraBet AI"
        
        return message
    
    def send_predictions(self):
        """Envia predições para o Telegram"""
        if not self.config.get('telegram_bot_token') or not self.config.get('telegram_chat_id'):
            print("❌ Telegram não configurado!")
            return False
        
        predictions = self.load_predictions()
        if not predictions:
            print("❌ Nenhuma predição encontrada!")
            return False
        
        print(f"📊 Encontradas {len(predictions)} partidas com predições")
        
        # Enviar predições
        sent_count = 0
        for prediction in predictions:
            message = self.format_prediction_message(prediction)
            
            print(f"\n📤 Enviando predições para: {prediction['match']}")
            if self.send_message(message):
                sent_count += 1
                time.sleep(2)  # Pausa entre mensagens
            else:
                print("❌ Falha ao enviar mensagem")
        
        print(f"\n✅ {sent_count}/{len(predictions)} mensagens enviadas com sucesso!")
        return sent_count > 0
    
    def send_test_message(self):
        """Envia mensagem de teste"""
        test_message = """
🎯 <b>TESTE MARABET AI</b>

✅ Sistema de notificações Telegram funcionando!

🤖 Bot configurado com sucesso
📱 Chat ID configurado corretamente
🔗 Conexão estabelecida

Sistema pronto para enviar predições!
        """
        
        return self.send_message(test_message)

def main():
    notifier = TelegramNotifier()
    
    print("🎯 MARABET AI - SISTEMA DE NOTIFICAÇÕES TELEGRAM")
    print("=" * 60)
    
    # Verificar configuração
    if not notifier.config.get('telegram_bot_token') or notifier.config.get('telegram_bot_token') == 'DEMO_TOKEN_123456789:ABCdefGHIjklMNOpqrsTUVwxyz':
        print("🔧 Configurando Telegram...")
        if not notifier.setup_telegram():
            print("❌ Falha na configuração!")
            return
    else:
        print("✅ Telegram já configurado!")
        if not notifier.test_connection():
            print("❌ Erro na conexão! Reconfigurando...")
            if not notifier.setup_telegram():
                return
    
    print("\n📋 OPÇÕES:")
    print("1. Enviar mensagem de teste")
    print("2. Enviar predições atuais")
    print("3. Configurar Telegram novamente")
    
    choice = input("\nEscolha uma opção (1-3): ").strip()
    
    if choice == '1':
        print("\n📤 Enviando mensagem de teste...")
        if notifier.send_test_message():
            print("✅ Mensagem de teste enviada!")
        else:
            print("❌ Falha ao enviar mensagem de teste!")
    
    elif choice == '2':
        print("\n📊 Enviando predições...")
        notifier.send_predictions()
    
    elif choice == '3':
        print("\n🔧 Reconfigurando Telegram...")
        notifier.setup_telegram()
    
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
