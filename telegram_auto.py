#!/usr/bin/env python3
"""
Sistema de Notificações Telegram Automático para Predições MaraBet AI
Execução automática sem input do usuário
"""

import json
import os
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramNotifierAuto:
    def __init__(self):
        self.config_file = "telegram_config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Carrega configuração do Telegram"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
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
    
    def simulate_telegram_send(self, message):
        """Simula envio para o Telegram (para demonstração)"""
        print("📱 SIMULAÇÃO DE ENVIO PARA TELEGRAM:")
        print("=" * 50)
        print(message)
        print("=" * 50)
        print("✅ Mensagem 'enviada' com sucesso!")
        return True
    
    def send_predictions_demo(self):
        """Envia predições (simulação)"""
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
            if self.simulate_telegram_send(message):
                sent_count += 1
                time.sleep(1)  # Pausa entre mensagens
        
        print(f"\n✅ {sent_count}/{len(predictions)} mensagens 'enviadas' com sucesso!")
        return sent_count > 0
    
    def save_telegram_message(self, message, filename=None):
        """Salva mensagem em arquivo para envio manual"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telegram_message_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"💾 Mensagem salva em: {filename}")
        return filename
    
    def generate_telegram_messages(self):
        """Gera mensagens do Telegram e salva em arquivos"""
        predictions = self.load_predictions()
        if not predictions:
            print("❌ Nenhuma predição encontrada!")
            return False
        
        print(f"📊 Gerando mensagens para {len(predictions)} partidas...")
        
        messages_saved = 0
        for i, prediction in enumerate(predictions, 1):
            message = self.format_prediction_message(prediction)
            filename = f"telegram_message_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            if self.save_telegram_message(message, filename):
                messages_saved += 1
        
        print(f"\n✅ {messages_saved} mensagens salvas para envio manual!")
        print("\n📋 COMO ENVIAR MANUALMENTE:")
        print("1. Abra o Telegram")
        print("2. Envie as mensagens dos arquivos .txt para seu chat")
        print("3. Ou configure um bot real usando telegram_notifier.py")
        
        return messages_saved > 0

def main():
    notifier = TelegramNotifierAuto()
    
    print("🎯 MARABET AI - SISTEMA DE NOTIFICAÇÕES TELEGRAM")
    print("=" * 60)
    
    # Executar automaticamente
    print("\n📤 Simulando envio de predições...")
    notifier.send_predictions_demo()
    
    print("\n💾 Gerando mensagens para envio manual...")
    notifier.generate_telegram_messages()
    
    print("\n📊 Predições disponíveis:")
    predictions = notifier.load_predictions()
    for i, pred in enumerate(predictions, 1):
        print(f"{i}. {pred['match']} ({pred['league']}) - {pred['total_predictions']} predições")

if __name__ == "__main__":
    main()
