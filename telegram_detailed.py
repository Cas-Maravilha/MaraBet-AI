#!/usr/bin/env python3
"""
Sistema de Notificações Telegram com Análise Detalhada
Envia predições com valor esperado, chances de green e recomendações de stake
"""

import json
import os
import requests
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramDetailedNotifier:
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
    
    def load_detailed_analyses(self):
        """Carrega análises detalhadas dos arquivos"""
        analysis_files = [f for f in os.listdir('.') if f.startswith('detailed_analysis_') and f.endswith('.txt')]
        analyses = []
        
        for filename in analysis_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair informações básicas do arquivo
                lines = content.split('\n')
                match_line = next((line for line in lines if line.startswith('🏆 *') and 'vs' in line), '')
                league_line = next((line for line in lines if line.startswith('🏟️')), '')
                
                if match_line and league_line:
                    match = match_line.replace('🏆 *', '').replace('*', '')
                    league = league_line.replace('🏟️ ', '')
                    
                    analyses.append({
                        'match': match,
                        'league': league,
                        'content': content,
                        'filename': filename
                    })
                
            except Exception as e:
                logger.error(f"Erro ao carregar {filename}: {e}")
        
        return analyses
    
    def send_detailed_analyses(self):
        """Envia análises detalhadas para o Telegram"""
        analyses = self.load_detailed_analyses()
        if not analyses:
            logger.error("❌ Nenhuma análise detalhada encontrada!")
            return False
        
        logger.info(f"📊 Encontradas {len(analyses)} análises detalhadas")
        
        # Enviar análises
        sent_count = 0
        for analysis in analyses:
            logger.info(f"📤 Enviando análise detalhada: {analysis['match']}")
            
            # Dividir mensagem se muito longa
            content = analysis['content']
            if len(content) > 4000:  # Limite do Telegram
                # Dividir em partes
                parts = self.split_message(content)
                for i, part in enumerate(parts, 1):
                    if self.send_message(part):
                        sent_count += 1
                        time.sleep(1)
            else:
                if self.send_message(content):
                    sent_count += 1
                    time.sleep(2)  # Pausa entre mensagens
        
        logger.info(f"✅ {sent_count} análises detalhadas enviadas com sucesso!")
        return sent_count > 0
    
    def split_message(self, message, max_length=4000):
        """Divide mensagem longa em partes menores"""
        lines = message.split('\n')
        parts = []
        current_part = ""
        
        for line in lines:
            if len(current_part + line + '\n') > max_length:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = line + '\n'
                else:
                    # Linha muito longa, dividir por palavras
                    words = line.split(' ')
                    for word in words:
                        if len(current_part + word + ' ') > max_length:
                            parts.append(current_part.strip())
                            current_part = word + ' '
                        else:
                            current_part += word + ' '
            else:
                current_part += line + '\n'
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts
    
    def send_summary_message(self):
        """Envia mensagem resumo das análises"""
        analyses = self.load_detailed_analyses()
        
        summary = f"🎯 *RESUMO DAS ANÁLISES MARABET AI*\n\n"
        summary += f"📊 Total de partidas analisadas: {len(analyses)}\n"
        summary += f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        summary += f"🏆 *PARTIDAS ANALISADAS:*\n"
        for analysis in analyses:
            summary += f"• {analysis['match']} ({analysis['league']})\n"
        
        summary += f"\n📈 *CARACTERÍSTICAS DAS ANÁLISES:*\n"
        summary += f"• Valor Esperado calculado\n"
        summary += f"• Chances mínimas e máximas de green\n"
        summary += f"• Recomendações de stake baseadas no Kelly\n"
        summary += f"• Níveis de confiança (Alta/Média/Baixa)\n"
        summary += f"• ROI potencial estimado\n"
        summary += f"• Threshold mínimo: 2% EV\n\n"
        
        summary += f"⚠️ *AVISOS IMPORTANTES:*\n"
        summary += f"• Stake máximo recomendado: 5% do bankroll\n"
        summary += f"• Gestão de risco é fundamental\n"
        summary += f"• Nunca aposte mais do que pode perder\n\n"
        
        summary += f"🤖 *Sistema MaraBet AI - Análise Profissional*"
        
        return self.send_message(summary)

def main():
    notifier = TelegramDetailedNotifier()
    
    print("🎯 MARABET AI - NOTIFICAÇÕES TELEGRAM DETALHADAS")
    print("=" * 60)
    
    # Enviar mensagem resumo
    print("📤 Enviando mensagem resumo...")
    notifier.send_summary_message()
    
    # Enviar análises detalhadas
    print("\n📊 Enviando análises detalhadas...")
    notifier.send_detailed_analyses()
    
    print("\n✅ Notificações detalhadas enviadas!")

if __name__ == "__main__":
    main()
