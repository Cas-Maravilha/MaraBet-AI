#!/usr/bin/env python3
"""
Agendador Automático de Previsões Telegram - MaraBet AI
Envia previsões automaticamente em horários programados
"""

import schedule
import time
import subprocess
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramScheduler:
    def __init__(self):
        self.running = True
        
    def send_predictions(self):
        """Envia previsões"""
        logger.info("🔄 Executando envio de previsões...")
        
        try:
            # Executar script de envio
            result = subprocess.run(
                ['python', 'send_today_predictions_telegram.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Previsões enviadas com sucesso")
            else:
                logger.error(f"❌ Erro ao enviar previsões: {result.stderr}")
        
        except Exception as e:
            logger.error(f"❌ Exceção ao enviar previsões: {e}")
    
    def morning_update(self):
        """Atualização da manhã"""
        logger.info("🌅 Envio matinal...")
        self.send_predictions()
    
    def afternoon_update(self):
        """Atualização da tarde"""
        logger.info("☀️ Envio vespertino...")
        self.send_predictions()
    
    def evening_update(self):
        """Atualização da noite"""
        logger.info("🌙 Envio noturno...")
        self.send_predictions()
    
    def start(self):
        """Inicia o agendador"""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                            ║")
        print("║     🤖 AGENDADOR AUTOMÁTICO TELEGRAM - MARABET AI         ║")
        print("║                                                            ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print(f"📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        print("⏰ HORÁRIOS DE ENVIO:")
        print("   • 08:00 - Previsões da manhã")
        print("   • 14:00 - Previsões da tarde")
        print("   • 20:00 - Previsões da noite")
        print()
        print("📋 FUNCIONALIDADES:")
        print("   • Busca automática de partidas")
        print("   • Análise com IA")
        print("   • Envio automático para Telegram")
        print("   • Logs salvos em logs/telegram_scheduler.log")
        print()
        print("🛑 Pressione Ctrl+C para parar")
        print("=" * 60)
        print()
        
        # Agendar tarefas
        schedule.every().day.at("08:00").do(self.morning_update)
        schedule.every().day.at("14:00").do(self.afternoon_update)
        schedule.every().day.at("20:00").do(self.evening_update)
        
        # Executar imediatamente na inicialização
        logger.info("🚀 Executando envio inicial...")
        self.send_predictions()
        
        # Loop principal
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        except KeyboardInterrupt:
            print("\n")
            print("🛑 Agendador parado pelo usuário")
            logger.info("🛑 Sistema parado pelo usuário")
            self.running = False
        
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            logger.error(f"❌ Erro crítico: {e}")
            self.running = False

def main():
    """Função principal"""
    scheduler = TelegramScheduler()
    scheduler.start()

if __name__ == "__main__":
    main()

