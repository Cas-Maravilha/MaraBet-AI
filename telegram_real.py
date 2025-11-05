#!/usr/bin/env python3
"""
Sistema de Notificações Telegram Real para Predições MaraBet AI
Usa token real e obtém Chat ID automaticamente
"""

import json
import os
import requests
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramNotifierReal:
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
    
    def test_bot_connection(self):
        """Testa conexão com o bot"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logger.info(f"✅ Bot conectado: {bot_info['result']['first_name']}")
                    logger.info(f"📱 Username: @{bot_info['result']['username']}")
                    return True
            logger.error(f"❌ Erro na conexão: {response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def get_chat_id(self):
        """Obtém Chat ID das mensagens recebidas"""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                updates = response.json()
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        if 'message' in update:
                            chat_id = update['message']['chat']['id']
                            chat_type = update['message']['chat']['type']
                            chat_title = update['message']['chat'].get('title', '')
                            chat_username = update['message']['chat'].get('username', '')
                            
                            logger.info(f"📱 Chat encontrado:")
                            logger.info(f"   ID: {chat_id}")
                            logger.info(f"   Tipo: {chat_type}")
                            logger.info(f"   Título: {chat_title}")
                            logger.info(f"   Username: @{chat_username}")
                            
                            return chat_id
                else:
                    logger.info("📱 Nenhuma mensagem encontrada. Envie uma mensagem para o bot primeiro!")
                    return None
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao obter Chat ID: {e}")
            return None
    
    def send_message(self, message, parse_mode='Markdown'):
        """Envia mensagem real para o Telegram"""
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
        
        message = f"🎯 *PREDIÇÕES MARABET AI*\n\n"
        message += f"🏆 *{match}*\n"
        message += f"🏟️ {league}\n"
        message += f"📊 {total} predições geradas\n\n"
        
        # Adicionar predições por categoria
        for category, preds in predictions.items():
            if isinstance(preds, dict) and preds:
                message += f"*{category.upper()}:*\n"
                
                # Mostrar predições com probabilidade > 0.6
                best_predictions = [(k, v) for k, v in preds.items() if v > 0.6]
                best_predictions.sort(key=lambda x: x[1], reverse=True)
                
                for bet_type, prob in best_predictions[:5]:  # Top 5 por categoria
                    emoji = "🟢" if prob > 0.75 else "🟡" if prob > 0.65 else "🔴"
                    message += f"{emoji} {bet_type}: {prob:.1%}\n"
                
                message += "\n"
        
        message += f"⏰ Gerado em: {prediction['generated_at'][:16]}\n"
        message += f"🤖 Sistema MaraBet AI"
        
        return message
    
    def send_predictions(self):
        """Envia predições reais para o Telegram"""
        if not self.config.get('telegram_chat_id') or self.config.get('telegram_chat_id') == 'DEMO_CHAT_ID_123456789':
            logger.info("📱 Obtendo Chat ID automaticamente...")
            chat_id = self.get_chat_id()
            if chat_id:
                self.config['telegram_chat_id'] = str(chat_id)
                self.save_config()
                logger.info(f"✅ Chat ID salvo: {chat_id}")
            else:
                logger.error("❌ Não foi possível obter Chat ID!")
                return False
        
        predictions = self.load_predictions()
        if not predictions:
            logger.error("❌ Nenhuma predição encontrada!")
            return False
        
        logger.info(f"📊 Encontradas {len(predictions)} partidas com predições")
        
        # Enviar predições
        sent_count = 0
        for prediction in predictions:
            message = self.format_prediction_message(prediction)
            
            logger.info(f"📤 Enviando predições para: {prediction['match']}")
            if self.send_message(message):
                sent_count += 1
                time.sleep(2)  # Pausa entre mensagens
            else:
                logger.error("❌ Falha ao enviar mensagem")
        
        logger.info(f"✅ {sent_count}/{len(predictions)} mensagens enviadas com sucesso!")
        return sent_count > 0
    
    def send_test_message(self):
        """Envia mensagem de teste"""
        test_message = """
🎯 *TESTE MARABET AI*

✅ Sistema de notificações Telegram funcionando!

🤖 Bot configurado com sucesso
📱 Chat ID configurado corretamente
🔗 Conexão estabelecida

Sistema pronto para enviar predições!
        """
        
        return self.send_message(test_message)

def main():
    notifier = TelegramNotifierReal()
    
    print("🎯 MARABET AI - SISTEMA DE NOTIFICAÇÕES TELEGRAM REAL")
    print("=" * 60)
    
    # Testar conexão do bot
    print("🔍 Testando conexão com o bot...")
    if not notifier.test_bot_connection():
        print("❌ Falha na conexão com o bot!")
        return
    
    print("✅ Bot conectado com sucesso!")
    
    # Obter Chat ID se necessário
    if not notifier.config.get('telegram_chat_id') or notifier.config.get('telegram_chat_id') == 'DEMO_CHAT_ID_123456789':
        print("\n📱 Obtendo Chat ID...")
        print("💬 Envie uma mensagem para o bot no Telegram primeiro!")
        chat_id = notifier.get_chat_id()
        if chat_id:
            notifier.config['telegram_chat_id'] = str(chat_id)
            notifier.save_config()
            print(f"✅ Chat ID salvo: {chat_id}")
        else:
            print("❌ Não foi possível obter Chat ID!")
            print("💬 Envie uma mensagem para o bot e execute novamente!")
            return
    
    # Enviar mensagem de teste
    print("\n📤 Enviando mensagem de teste...")
    if notifier.send_test_message():
        print("✅ Mensagem de teste enviada!")
    else:
        print("❌ Falha ao enviar mensagem de teste!")
        return
    
    # Enviar predições
    print("\n📊 Enviando predições...")
    notifier.send_predictions()

if __name__ == "__main__":
    main()
