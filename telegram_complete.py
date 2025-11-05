#!/usr/bin/env python3
"""
Sistema de Notificações Telegram Completo para Predições MaraBet AI
Inclui predições detalhadas com probabilidades específicas
"""

import json
import os
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramNotifierComplete:
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
                    'generated_at': data.get('generated_at', 'N/A'),
                    'filename': filename
                })
                
            except Exception as e:
                logger.error(f"Erro ao carregar {filename}: {e}")
        
        return predictions
    
    def format_prediction_message_complete(self, prediction):
        """Formata mensagem completa de predição para o Telegram"""
        match = prediction['match']
        league = prediction['league']
        predictions = prediction['predictions']
        total = prediction['total_predictions']
        
        message = f"🎯 *PREDIÇÕES MARABET AI*\n\n"
        message += f"🏆 *{match}*\n"
        message += f"🏟️ {league}\n"
        message += f"📊 {total} predições geradas\n\n"
        
        # Adicionar predições por categoria com detalhes
        for category, preds in predictions.items():
            if isinstance(preds, dict) and preds:
                message += f"*{category.upper()}:*\n"
                
                # Mostrar todas as predições com probabilidade > 0.5
                valid_predictions = [(k, v) for k, v in preds.items() if v > 0.5]
                valid_predictions.sort(key=lambda x: x[1], reverse=True)
                
                for bet_type, prob in valid_predictions:
                    emoji = "🟢" if prob > 0.75 else "🟡" if prob > 0.65 else "🔴"
                    message += f"{emoji} {bet_type}: {prob:.1%}\n"
                
                message += "\n"
        
        message += f"⏰ Gerado em: {prediction['generated_at'][:16]}\n"
        message += f"🤖 Sistema MaraBet AI"
        
        return message
    
    def format_top_recommendations(self, prediction):
        """Formata apenas as melhores recomendações"""
        match = prediction['match']
        league = prediction['league']
        predictions = prediction['predictions']
        
        message = f"🎯 *TOP RECOMENDAÇÕES MARABET AI*\n\n"
        message += f"🏆 *{match}*\n"
        message += f"🏟️ {league}\n\n"
        
        # Coletar todas as predições com alta probabilidade
        all_predictions = []
        for category, preds in predictions.items():
            if isinstance(preds, dict):
                for bet_type, prob in preds.items():
                    if prob > 0.7:  # Apenas alta confiança
                        all_predictions.append((category, bet_type, prob))
        
        # Ordenar por probabilidade
        all_predictions.sort(key=lambda x: x[2], reverse=True)
        
        message += "*🏆 TOP 10 RECOMENDAÇÕES:*\n\n"
        for i, (category, bet_type, prob) in enumerate(all_predictions[:10], 1):
            emoji = "🟢" if prob > 0.8 else "🟡"
            message += f"{i}. {emoji} *{bet_type}* ({category})\n"
            message += f"   Probabilidade: {prob:.1%}\n\n"
        
        message += f"⏰ Gerado em: {prediction['generated_at'][:16]}\n"
        message += f"🤖 Sistema MaraBet AI"
        
        return message
    
    def simulate_telegram_send(self, message):
        """Simula envio para o Telegram"""
        print("📱 SIMULAÇÃO DE ENVIO PARA TELEGRAM:")
        print("=" * 50)
        print(message)
        print("=" * 50)
        print("✅ Mensagem 'enviada' com sucesso!")
        return True
    
    def save_telegram_message(self, message, filename=None):
        """Salva mensagem em arquivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telegram_message_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"💾 Mensagem salva em: {filename}")
        return filename
    
    def generate_complete_messages(self):
        """Gera mensagens completas do Telegram"""
        predictions = self.load_predictions()
        if not predictions:
            print("❌ Nenhuma predição encontrada!")
            return False
        
        print(f"📊 Gerando mensagens completas para {len(predictions)} partidas...")
        
        messages_saved = 0
        for i, prediction in enumerate(predictions, 1):
            # Mensagem completa
            complete_message = self.format_prediction_message_complete(prediction)
            complete_filename = f"telegram_complete_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            if self.save_telegram_message(complete_message, complete_filename):
                messages_saved += 1
            
            # Mensagem de top recomendações
            top_message = self.format_top_recommendations(prediction)
            top_filename = f"telegram_top_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            self.save_telegram_message(top_message, top_filename)
        
        print(f"\n✅ {messages_saved} mensagens completas salvas!")
        print(f"✅ {messages_saved} mensagens de top recomendações salvas!")
        
        return messages_saved > 0
    
    def send_predictions_complete(self):
        """Envia predições completas (simulação)"""
        predictions = self.load_predictions()
        if not predictions:
            print("❌ Nenhuma predição encontrada!")
            return False
        
        print(f"📊 Encontradas {len(predictions)} partidas com predições")
        
        sent_count = 0
        for prediction in predictions:
            message = self.format_prediction_message_complete(prediction)
            
            print(f"\n📤 Enviando predições completas para: {prediction['match']}")
            if self.simulate_telegram_send(message):
                sent_count += 1
                time.sleep(1)
        
        print(f"\n✅ {sent_count}/{len(predictions)} mensagens completas 'enviadas'!")
        return sent_count > 0

def main():
    notifier = TelegramNotifierComplete()
    
    print("🎯 MARABET AI - SISTEMA DE NOTIFICAÇÕES TELEGRAM COMPLETO")
    print("=" * 60)
    
    # Executar automaticamente
    print("\n📤 Simulando envio de predições completas...")
    notifier.send_predictions_complete()
    
    print("\n💾 Gerando mensagens completas para envio manual...")
    notifier.generate_complete_messages()
    
    print("\n📋 INSTRUÇÕES PARA ENVIO MANUAL:")
    print("1. Abra o Telegram")
    print("2. Envie as mensagens dos arquivos .txt para seu chat")
    print("3. Use telegram_complete_*.txt para predições detalhadas")
    print("4. Use telegram_top_*.txt para top recomendações")
    print("5. Para bot real, configure usando telegram_notifier.py")

if __name__ == "__main__":
    main()
