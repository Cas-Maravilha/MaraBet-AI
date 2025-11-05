#!/usr/bin/env python3
"""
Sistema Integrado MaraBet AI - Coleta, Monitoramento e Alertas
Sistema completo que integra todas as funcionalidades de coleta de dados
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import schedule

# Importar módulos do sistema
from data_collection_system import DataCollectionManager
from realtime_monitor import RealTimeMonitor
from concise_alerts import ConciseAlertSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedMaraBetSystem:
    """Sistema integrado MaraBet AI"""
    
    def __init__(self):
        self.data_manager = DataCollectionManager()
        self.monitor = RealTimeMonitor()
        self.alert_system = ConciseAlertSystem()
        
        # Configurações do sistema
        self.collection_interval = 30  # minutos
        self.monitoring_interval = 5   # minutos
        self.alert_interval = 60      # minutos
        
        # Status do sistema
        self.is_running = False
        self.threads = []
        
    def start_system(self):
        """Inicia o sistema completo"""
        logger.info("🚀 Iniciando Sistema Integrado MaraBet AI...")
        
        self.is_running = True
        
        # Iniciar threads para diferentes funcionalidades
        self._start_data_collection_thread()
        self._start_monitoring_thread()
        self._start_alert_thread()
        
        logger.info("✅ Sistema Integrado MaraBet AI iniciado com sucesso!")
        
        # Manter o sistema rodando
        try:
            while self.is_running:
                time.sleep(60)
                self._print_system_status()
        except KeyboardInterrupt:
            self.stop_system()
    
    def stop_system(self):
        """Para o sistema"""
        logger.info("🛑 Parando Sistema Integrado MaraBet AI...")
        self.is_running = False
        
        # Aguardar threads terminarem
        for thread in self.threads:
            thread.join(timeout=5)
        
        logger.info("✅ Sistema Integrado MaraBet AI parado!")
    
    def _start_data_collection_thread(self):
        """Inicia thread de coleta de dados"""
        def collect_data():
            while self.is_running:
                try:
                    logger.info("📊 Executando coleta de dados...")
                    
                    # Coletar dados para partidas importantes
                    important_matches = [
                        ("RM_vs_FCB_2025", "Real Madrid", "Barcelona", "La Liga", "Madrid"),
                        ("ARS_vs_CHE_2025", "Arsenal", "Chelsea", "Premier League", "London"),
                        ("MC_vs_ARS_2025", "Manchester City", "Arsenal", "Premier League", "Manchester")
                    ]
                    
                    for match_id, home_team, away_team, league, city in important_matches:
                        self.data_manager.collect_all_data(match_id, home_team, away_team, league, city)
                        time.sleep(2)
                    
                    logger.info("✅ Coleta de dados concluída")
                    
                except Exception as e:
                    logger.error(f"❌ Erro na coleta de dados: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(self.collection_interval * 60)
        
        thread = threading.Thread(target=collect_data, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def _start_monitoring_thread(self):
        """Inicia thread de monitoramento"""
        def monitor_data():
            while self.is_running:
                try:
                    logger.info("🔍 Executando monitoramento...")
                    
                    # Executar verificações de monitoramento
                    self.monitor.monitor_odds_changes()
                    time.sleep(2)
                    
                    self.monitor.monitor_injury_updates()
                    time.sleep(2)
                    
                    self.monitor.monitor_weather_changes()
                    time.sleep(2)
                    
                    self.monitor.monitor_team_form_changes()
                    
                    logger.info("✅ Monitoramento concluído")
                    
                except Exception as e:
                    logger.error(f"❌ Erro no monitoramento: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(self.monitoring_interval * 60)
        
        thread = threading.Thread(target=monitor_data, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def _start_alert_thread(self):
        """Inicia thread de alertas"""
        def send_alerts():
            while self.is_running:
                try:
                    logger.info("🚨 Executando sistema de alertas...")
                    
                    # Enviar alertas de predições
                    self.alert_system.scan_and_send_concise_alerts()
                    
                    logger.info("✅ Alertas enviados")
                    
                except Exception as e:
                    logger.error(f"❌ Erro nos alertas: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(self.alert_interval * 60)
        
        thread = threading.Thread(target=send_alerts, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def _print_system_status(self):
        """Imprime status do sistema"""
        status = "🟢 ATIVO" if self.is_running else "🔴 INATIVO"
        
        print(f"\n📊 STATUS DO SISTEMA MARABET AI - {status}")
        print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Coleta de dados: A cada {self.collection_interval} minutos")
        print(f"🔍 Monitoramento: A cada {self.monitoring_interval} minutos")
        print(f"🚨 Alertas: A cada {self.alert_interval} minutos")
        print(f"🧵 Threads ativas: {len([t for t in self.threads if t.is_alive()])}")
        print("-" * 50)
    
    def run_demo_collection(self):
        """Executa demonstração de coleta de dados"""
        print("🎯 MARABET AI - DEMONSTRAÇÃO DE COLETA DE DADOS")
        print("=" * 60)
        
        # Coletar dados para demonstração
        matches = [
            ("DEMO_RM_vs_FCB", "Real Madrid", "Barcelona", "La Liga", "Madrid"),
            ("DEMO_ARS_vs_CHE", "Arsenal", "Chelsea", "Premier League", "London"),
            ("DEMO_PETRO_vs_1AGO", "Petro de Luanda", "1º de Agosto", "Girabola", "Luanda")
        ]
        
        for match_id, home_team, away_team, league, city in matches:
            print(f"\n📊 Coletando dados para: {home_team} vs {away_team}")
            
            match_data = self.data_manager.collect_all_data(
                match_id, home_team, away_team, league, city
            )
            
            print(f"✅ Dados coletados:")
            print(f"   📊 Odds: {len(match_data.odds)} mercados")
            print(f"   🏥 Lesões/Suspensões: {len(match_data.injuries + match_data.suspensions)}")
            print(f"   🌤️ Clima: {match_data.weather.get('condition', 'N/A')}")
            print(f"   📅 Data: {match_data.date.strftime('%d/%m/%Y %H:%M')}")
            
            time.sleep(1)
        
        print(f"\n✅ Demonstração concluída! {len(matches)} partidas processadas.")
    
    def run_demo_monitoring(self):
        """Executa demonstração de monitoramento"""
        print("\n🔍 MARABET AI - DEMONSTRAÇÃO DE MONITORAMENTO")
        print("=" * 60)
        
        print("📊 Verificando mudanças nas odds...")
        self.monitor.monitor_odds_changes()
        
        print("🏥 Verificando atualizações de lesões...")
        self.monitor.monitor_injury_updates()
        
        print("🌤️ Verificando condições meteorológicas...")
        self.monitor.monitor_weather_changes()
        
        print("📈 Verificando forma das equipes...")
        self.monitor.monitor_team_form_changes()
        
        print("✅ Demonstração de monitoramento concluída!")
    
    def run_demo_alerts(self):
        """Executa demonstração de alertas"""
        print("\n🚨 MARABET AI - DEMONSTRAÇÃO DE ALERTAS")
        print("=" * 60)
        
        print("📊 Enviando alertas de predições...")
        self.alert_system.scan_and_send_concise_alerts()
        
        print("✅ Demonstração de alertas concluída!")

def main():
    system = IntegratedMaraBetSystem()
    
    print("🎯 MARABET AI - SISTEMA INTEGRADO DE COLETA E MONITORAMENTO")
    print("=" * 70)
    
    print("\n📋 OPÇÕES DISPONÍVEIS:")
    print("1. 🚀 Iniciar Sistema Completo (Coleta + Monitoramento + Alertas)")
    print("2. 📊 Demonstração de Coleta de Dados")
    print("3. 🔍 Demonstração de Monitoramento")
    print("4. 🚨 Demonstração de Alertas")
    print("5. ❌ Sair")
    
    while True:
        try:
            choice = input("\n🎯 Escolha uma opção (1-5): ").strip()
            
            if choice == "1":
                print("\n🚀 Iniciando Sistema Completo...")
                print("⚠️ Pressione Ctrl+C para parar")
                system.start_system()
                break
                
            elif choice == "2":
                system.run_demo_collection()
                
            elif choice == "3":
                system.run_demo_monitoring()
                
            elif choice == "4":
                system.run_demo_alerts()
                
            elif choice == "5":
                print("\n👋 Sistema encerrado!")
                break
                
            else:
                print("❌ Opção inválida! Escolha entre 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Sistema encerrado pelo usuário!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
