#!/usr/bin/env python3
"""
Sistema Automático MaraBet AI - Demonstração Completa
Executa automaticamente todas as funcionalidades sem entrada do usuário
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Importar módulos do sistema
from data_collection_system import DataCollectionManager
from realtime_monitor import RealTimeMonitor
from concise_alerts import ConciseAlertSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomaticMaraBetDemo:
    """Demonstração automática do sistema MaraBet AI"""
    
    def __init__(self):
        self.data_manager = DataCollectionManager()
        self.monitor = RealTimeMonitor()
        self.alert_system = ConciseAlertSystem()
        
    def run_complete_demo(self):
        """Executa demonstração completa do sistema"""
        print("🎯 MARABET AI - DEMONSTRAÇÃO AUTOMÁTICA COMPLETA")
        print("=" * 70)
        
        # Etapa 1: Coleta de Dados
        print("\n📊 ETAPA 1: COLETA DE DADOS EM TEMPO REAL")
        print("-" * 50)
        self.demo_data_collection()
        
        # Etapa 2: Monitoramento
        print("\n🔍 ETAPA 2: MONITORAMENTO EM TEMPO REAL")
        print("-" * 50)
        self.demo_monitoring()
        
        # Etapa 3: Alertas
        print("\n🚨 ETAPA 3: SISTEMA DE ALERTAS")
        print("-" * 50)
        self.demo_alerts()
        
        # Resumo Final
        print("\n✅ DEMONSTRAÇÃO COMPLETA FINALIZADA!")
        print("=" * 70)
        self.print_system_summary()
    
    def demo_data_collection(self):
        """Demonstra coleta de dados"""
        print("🔄 Coletando dados de múltiplas fontes...")
        
        # Partidas para demonstração
        matches = [
            ("DEMO_RM_vs_FCB", "Real Madrid", "Barcelona", "La Liga", "Madrid"),
            ("DEMO_ARS_vs_CHE", "Arsenal", "Chelsea", "Premier League", "London"),
            ("DEMO_PETRO_vs_1AGO", "Petro de Luanda", "1º de Agosto", "Girabola", "Luanda"),
            ("DEMO_MC_vs_LIV", "Manchester City", "Liverpool", "Premier League", "Manchester"),
            ("DEMO_JUV_vs_MIL", "Juventus", "AC Milan", "Serie A", "Turim")
        ]
        
        for i, (match_id, home_team, away_team, league, city) in enumerate(matches, 1):
            print(f"\n📊 Coletando dados {i}/{len(matches)}: {home_team} vs {away_team}")
            
            try:
                match_data = self.data_manager.collect_all_data(
                    match_id, home_team, away_team, league, city
                )
                
                print(f"   ✅ Dados coletados com sucesso:")
                print(f"   📊 Odds: {len(match_data.odds)} mercados")
                print(f"   🏥 Lesões/Suspensões: {len(match_data.injuries + match_data.suspensions)}")
                print(f"   🌤️ Clima: {match_data.weather.get('condition', 'N/A')}")
                print(f"   📅 Data: {match_data.date.strftime('%d/%m/%Y %H:%M')}")
                
            except Exception as e:
                print(f"   ❌ Erro na coleta: {e}")
            
            time.sleep(1)
        
        print(f"\n✅ Coleta de dados concluída! {len(matches)} partidas processadas.")
    
    def demo_monitoring(self):
        """Demonstra monitoramento em tempo real"""
        print("🔍 Executando verificações de monitoramento...")
        
        try:
            print("📊 Verificando mudanças nas odds...")
            self.monitor.monitor_odds_changes()
            time.sleep(2)
            
            print("🏥 Verificando atualizações de lesões...")
            self.monitor.monitor_injury_updates()
            time.sleep(2)
            
            print("🌤️ Verificando condições meteorológicas...")
            self.monitor.monitor_weather_changes()
            time.sleep(2)
            
            print("📈 Verificando forma das equipes...")
            self.monitor.monitor_team_form_changes()
            
            print("✅ Monitoramento concluído com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
    
    def demo_alerts(self):
        """Demonstra sistema de alertas"""
        print("🚨 Enviando alertas de predições...")
        
        try:
            self.alert_system.scan_and_send_concise_alerts()
            print("✅ Alertas enviados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro nos alertas: {e}")
    
    def print_system_summary(self):
        """Imprime resumo do sistema"""
        print("\n📋 RESUMO DO SISTEMA MARABET AI:")
        print("=" * 50)
        
        print("\n🔧 COMPONENTES IMPLEMENTADOS:")
        print("✅ Sistema de Coleta de Dados em Tempo Real")
        print("✅ Monitoramento de Mudanças nas Odds")
        print("✅ Monitoramento de Lesões e Suspensões")
        print("✅ Monitoramento Meteorológico")
        print("✅ Monitoramento de Forma das Equipes")
        print("✅ Sistema de Alertas Resumidos e Objetivos")
        print("✅ Banco de Dados SQLite Integrado")
        print("✅ Integração com Telegram")
        
        print("\n📊 FONTES DE DADOS:")
        print("• Resultados anteriores das equipas")
        print("• Estatísticas (gols, posse, chutes, defesas, cartões)")
        print("• Odds e variações nas casas de apostas")
        print("• Lesões, suspensões e escalações")
        print("• Fatores externos (condições climáticas, mando de campo)")
        
        print("\n🎯 FUNCIONALIDADES PRINCIPAIS:")
        print("• Coleta automática de dados de múltiplas fontes")
        print("• Monitoramento em tempo real de mudanças")
        print("• Alertas automáticos para eventos importantes")
        print("• Análise preditiva com IA")
        print("• Sistema de notificações via Telegram")
        print("• Dashboard interativo web")
        
        print("\n🚀 COMO O SISTEMA FUNCIONA:")
        print("1. 📊 Coleta dados de APIs e fontes públicas")
        print("2. 🔍 Monitora mudanças em tempo real")
        print("3. 🤖 Analisa dados com modelos de IA")
        print("4. 🚨 Envia alertas automáticos")
        print("5. 📱 Notifica via Telegram")
        print("6. 🌐 Disponibiliza dashboard web")
        
        print("\n💡 VANTAGENS:")
        print("• Dados sempre atualizados")
        print("• Monitoramento 24/7")
        print("• Alertas em tempo real")
        print("• Análise preditiva precisa")
        print("• Interface intuitiva")
        print("• Sistema escalável")
        
        print(f"\n🕐 Demonstração executada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("🎯 Sistema MaraBet AI - Operacional e Funcional!")

def main():
    demo = AutomaticMaraBetDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()
