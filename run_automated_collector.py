#!/usr/bin/env python3
"""
Script principal para executar o sistema de coleta automatizada do MaraBet AI
"""

import sys
import os
import signal
import time
import logging
from datetime import datetime

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from scheduler.automated_collector import AutomatedCollector
from settings.api_keys import validate_keys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_collector.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutomatedCollectorManager:
    """Gerenciador do sistema de coleta automatizada"""
    
    def __init__(self):
        self.collector = None
        self.scheduler_thread = None
        self.running = False
        
        # Configurar handlers de sinal para parada graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start(self):
        """Inicia o sistema de coleta automatizada"""
        print("🚀 MARABET AI - SISTEMA DE COLETA AUTOMATIZADA")
        print("=" * 60)
        
        # Verificar configuração
        print("\n📋 Verificando configuração...")
        if not validate_keys():
            print("⚠️  AVISO: API Keys não configuradas!")
            print("O sistema funcionará com dados simulados.")
            print("Para dados reais, configure as API Keys no arquivo .env")
        
        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
        
        try:
            # Inicializar coletor
            print("\n🔧 Inicializando sistema...")
            self.collector = AutomatedCollector()
            
            # Iniciar agendador
            print("📅 Iniciando agendador...")
            self.scheduler_thread = self.collector.start_scheduler()
            
            self.running = True
            
            print("\n✅ Sistema iniciado com sucesso!")
            print("\n📊 TAREFAS AGENDADAS:")
            print("   ⚽ Coleta de futebol: a cada 30 minutos")
            print("   🎯 Coleta de odds: a cada 15 minutos")
            print("   🔍 Análise de valor: a cada 10 minutos")
            print("   🧹 Limpeza de dados: diariamente às 2:00")
            print("   📊 Relatório de status: diariamente às 8:00")
            
            print("\n⏰ PRÓXIMAS EXECUÇÕES:")
            status = self.collector.get_status()
            print(f"   Futebol: {status['next_football']}")
            print(f"   Odds: {status['next_odds']}")
            print(f"   Análise: {status['next_analysis']}")
            
            print(f"\n📈 ESTATÍSTICAS ATUAIS:")
            print(f"   Partidas: {status['total_matches']:,}")
            print(f"   Odds: {status['total_odds']:,}")
            print(f"   Predições: {status['total_predictions']:,}")
            
            print("\n🔄 Sistema em execução... (Ctrl+C para parar)")
            
            # Loop principal
            self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema: {e}")
            print(f"\n❌ Erro ao iniciar sistema: {e}")
            sys.exit(1)
    
    def _main_loop(self):
        """Loop principal do sistema"""
        try:
            while self.running:
                time.sleep(60)  # Verificar a cada minuto
                
                # Mostrar status a cada 10 minutos
                if int(time.time()) % 600 == 0:
                    self._show_status()
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupção detectada...")
            self.stop()
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            print(f"\n❌ Erro no sistema: {e}")
            self.stop()
    
    def _show_status(self):
        """Mostra status do sistema"""
        try:
            status = self.collector.get_status()
            print(f"\n📊 STATUS - {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Partidas: {status['total_matches']:,}")
            print(f"   Odds: {status['total_odds']:,}")
            print(f"   Predições: {status['total_predictions']:,}")
            print(f"   Próxima coleta futebol: {status['next_football']}")
            print(f"   Próxima coleta odds: {status['next_odds']}")
        except Exception as e:
            logger.error(f"Erro ao mostrar status: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de parada"""
        print(f"\n🛑 Sinal {signum} recebido...")
        self.stop()
    
    def stop(self):
        """Para o sistema"""
        if self.running:
            print("\n🛑 Parando sistema...")
            self.running = False
            
            if self.collector:
                self.collector.stop_scheduler()
            
            print("✅ Sistema parado com sucesso!")
            sys.exit(0)

def main():
    """Função principal"""
    try:
        manager = AutomatedCollectorManager()
        manager.start()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
