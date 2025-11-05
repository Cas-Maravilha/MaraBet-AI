#!/usr/bin/env python3
"""
Sistema de Coleta Contínua de Dados
MaraBet AI - Coleta automática e contínua de dados em tempo real
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import time
import json
import os
import sqlite3
from pathlib import Path
import schedule
import threading
from dataclasses import dataclass
import signal
import sys

logger = logging.getLogger(__name__)

@dataclass
class CollectionConfig:
    """Configuração para coleta contínua"""
    api_key: str
    collection_interval: int = 300  # 5 minutos
    odds_interval: int = 60  # 1 minuto para odds
    stats_interval: int = 300  # 5 minutos para estatísticas
    max_retries: int = 3
    timeout: int = 30
    enabled_collections: List[str] = None

class ContinuousDataCollector:
    """Coletor contínuo de dados"""
    
    def __init__(self, config: CollectionConfig):
        """Inicializa coletor contínuo"""
        self.config = config
        self.running = False
        self.threads = []
        
        # Configurar coleções habilitadas
        if not config.enabled_collections:
            self.config.enabled_collections = [
                'live_matches',
                'odds',
                'statistics',
                'standings',
                'fixtures'
            ]
        
        # Inicializar banco de dados
        self.db_path = "data/continuous_data.db"
        self._init_database()
        
        # Importar API real
        from api.real_football_api import initialize_real_football_api
        self.api = initialize_real_football_api(config.api_key)
        
        # Configurar logging
        self._setup_logging()
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _init_database(self):
        """Inicializa banco de dados para coleta contínua"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de partidas ao vivo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER UNIQUE,
                league_id INTEGER,
                league_name TEXT,
                home_team TEXT,
                away_team TEXT,
                home_score INTEGER,
                away_score INTEGER,
                status TEXT,
                minute INTEGER,
                date TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de odds
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                bookmaker TEXT,
                home_win REAL,
                draw REAL,
                away_win REAL,
                over_2_5 REAL,
                under_2_5 REAL,
                btts_yes REAL,
                btts_no REAL,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de estatísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_id INTEGER,
                team_name TEXT,
                shots_total INTEGER,
                shots_on_goal INTEGER,
                possession INTEGER,
                passes_total INTEGER,
                passes_accurate INTEGER,
                fouls INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de standings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_standings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER,
                season INTEGER,
                position INTEGER,
                team_id INTEGER,
                team_name TEXT,
                points INTEGER,
                played INTEGER,
                won INTEGER,
                drawn INTEGER,
                lost INTEGER,
                goals_for INTEGER,
                goals_against INTEGER,
                goal_difference INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de partidas futuras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS upcoming_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER UNIQUE,
                league_id INTEGER,
                league_name TEXT,
                home_team TEXT,
                away_team TEXT,
                date TEXT,
                status TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados de coleta contínua inicializado")
    
    def _setup_logging(self):
        """Configura logging para coleta contínua"""
        log_dir = "logs/continuous_collection"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/continuous_collection_{datetime.now().strftime('%Y%m%d')}.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de parada"""
        logger.info(f"Recebido sinal {signum}, parando coleta...")
        self.stop()
        sys.exit(0)
    
    def collect_live_matches(self):
        """Coleta partidas ao vivo"""
        try:
            logger.info("Coletando partidas ao vivo...")
            matches = self.api.get_live_matches()
            
            if matches:
                self._save_live_matches(matches)
                logger.info(f"Coletadas {len(matches)} partidas ao vivo")
            else:
                logger.info("Nenhuma partida ao vivo encontrada")
                
        except Exception as e:
            logger.error(f"Erro ao coletar partidas ao vivo: {e}")
    
    def collect_odds(self):
        """Coleta odds de partidas ao vivo"""
        try:
            logger.info("Coletando odds...")
            
            # Obter partidas ao vivo do banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT match_id FROM live_matches 
                WHERE status IN ('1H', '2H', 'HT', 'ET', 'P', 'LIVE')
                AND collected_at > datetime('now', '-1 hour')
            ''')
            
            match_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            total_odds = 0
            for match_id in match_ids:
                odds = self.api.get_match_odds(match_id)
                if odds:
                    self._save_odds(odds)
                    total_odds += len(odds)
                
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Coletadas {total_odds} odds de {len(match_ids)} partidas")
            
        except Exception as e:
            logger.error(f"Erro ao coletar odds: {e}")
    
    def collect_statistics(self):
        """Coleta estatísticas de partidas ao vivo"""
        try:
            logger.info("Coletando estatísticas...")
            
            # Obter partidas ao vivo do banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT match_id FROM live_matches 
                WHERE status IN ('1H', '2H', 'HT', 'ET', 'P', 'LIVE')
                AND collected_at > datetime('now', '-1 hour')
            ''')
            
            match_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            total_stats = 0
            for match_id in match_ids:
                stats = self.api.get_match_statistics(match_id)
                if stats:
                    self._save_statistics(stats)
                    total_stats += len(stats)
                
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Coletadas {total_stats} estatísticas de {len(match_ids)} partidas")
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas: {e}")
    
    def collect_standings(self):
        """Coleta tabelas de classificação"""
        try:
            logger.info("Coletando tabelas de classificação...")
            
            # Ligas principais
            leagues = [39, 140, 78, 135, 61]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1
            
            total_standings = 0
            for league_id in leagues:
                standings = self.api.get_league_standings(league_id)
                if standings:
                    self._save_standings(standings)
                    total_standings += len(standings)
                
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Coletadas {total_standings} posições de {len(leagues)} ligas")
            
        except Exception as e:
            logger.error(f"Erro ao coletar tabelas: {e}")
    
    def collect_upcoming_matches(self):
        """Coleta partidas futuras"""
        try:
            logger.info("Coletando partidas futuras...")
            
            # Coletar partidas dos próximos 7 dias
            matches = self.api.get_upcoming_matches(7)
            
            if matches:
                self._save_upcoming_matches(matches)
                logger.info(f"Coletadas {len(matches)} partidas futuras")
            else:
                logger.info("Nenhuma partida futura encontrada")
                
        except Exception as e:
            logger.error(f"Erro ao coletar partidas futuras: {e}")
    
    def _save_live_matches(self, matches: List[Dict]):
        """Salva partidas ao vivo no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for match in matches:
            cursor.execute('''
                INSERT OR REPLACE INTO live_matches 
                (match_id, league_id, league_name, home_team, away_team, 
                 home_score, away_score, status, minute, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match['match_id'], match['league_id'], match['league_name'],
                match['home_team'], match['away_team'], match['home_score'],
                match['away_score'], match['status'], match.get('minute', 0),
                match['date']
            ))
        
        conn.commit()
        conn.close()
    
    def _save_odds(self, odds: List[Dict]):
        """Salva odds no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for odd in odds:
            cursor.execute('''
                INSERT INTO live_odds 
                (match_id, bookmaker, home_win, draw, away_win, 
                 over_2_5, under_2_5, btts_yes, btts_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                odd['match_id'], odd['bookmaker'], odd['home_win'],
                odd['draw'], odd['away_win'], odd.get('over_2_5'),
                odd.get('under_2_5'), odd.get('btts_yes'), odd.get('btts_no')
            ))
        
        conn.commit()
        conn.close()
    
    def _save_statistics(self, stats: List[Dict]):
        """Salva estatísticas no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for stat in stats:
            cursor.execute('''
                INSERT INTO live_statistics 
                (match_id, team_id, team_name, shots_total, shots_on_goal, 
                 possession, passes_total, passes_accurate, fouls, 
                 yellow_cards, red_cards)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stat['match_id'], stat['team_id'], stat['team_name'],
                stat['shots_total'], stat['shots_on_goal'], stat['possession'],
                stat['passes_total'], stat['passes_accurate'], stat['fouls'],
                stat['yellow_cards'], stat['red_cards']
            ))
        
        conn.commit()
        conn.close()
    
    def _save_standings(self, standings: List[Dict]):
        """Salva tabelas no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for standing in standings:
            cursor.execute('''
                INSERT OR REPLACE INTO live_standings 
                (league_id, season, position, team_id, team_name, 
                 points, played, won, drawn, lost, goals_for, 
                 goals_against, goal_difference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                standing['league_id'], standing['season'], standing['position'],
                standing['team_id'], standing['team_name'], standing['points'],
                standing['played'], standing['won'], standing['drawn'],
                standing['lost'], standing['goals_for'], standing['goals_against'],
                standing['goal_difference']
            ))
        
        conn.commit()
        conn.close()
    
    def _save_upcoming_matches(self, matches: List[Dict]):
        """Salva partidas futuras no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for match in matches:
            cursor.execute('''
                INSERT OR REPLACE INTO upcoming_matches 
                (match_id, league_id, league_name, home_team, away_team, date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                match['match_id'], match['league_id'], match['league_name'],
                match['home_team'], match['away_team'], match['date'], match['status']
            ))
        
        conn.commit()
        conn.close()
    
    def start(self):
        """Inicia coleta contínua"""
        if self.running:
            logger.warning("Coleta já está rodando")
            return
        
        logger.info("Iniciando coleta contínua de dados...")
        self.running = True
        
        # Configurar schedule
        if 'live_matches' in self.config.enabled_collections:
            schedule.every(self.config.collection_interval).seconds.do(self.collect_live_matches)
        
        if 'odds' in self.config.enabled_collections:
            schedule.every(self.config.odds_interval).seconds.do(self.collect_odds)
        
        if 'statistics' in self.config.enabled_collections:
            schedule.every(self.config.stats_interval).seconds.do(self.collect_statistics)
        
        if 'standings' in self.config.enabled_collections:
            schedule.every(self.config.collection_interval).seconds.do(self.collect_standings)
        
        if 'fixtures' in self.config.enabled_collections:
            schedule.every(self.config.collection_interval).seconds.do(self.collect_upcoming_matches)
        
        # Executar coleta inicial
        logger.info("Executando coleta inicial...")
        self._run_initial_collection()
        
        # Iniciar thread de schedule
        schedule_thread = threading.Thread(target=self._run_scheduler)
        schedule_thread.daemon = True
        schedule_thread.start()
        self.threads.append(schedule_thread)
        
        logger.info("Coleta contínua iniciada")
    
    def _run_initial_collection(self):
        """Executa coleta inicial"""
        try:
            if 'live_matches' in self.config.enabled_collections:
                self.collect_live_matches()
            
            if 'odds' in self.config.enabled_collections:
                self.collect_odds()
            
            if 'statistics' in self.config.enabled_collections:
                self.collect_statistics()
            
            if 'standings' in self.config.enabled_collections:
                self.collect_standings()
            
            if 'fixtures' in self.config.enabled_collections:
                self.collect_upcoming_matches()
                
        except Exception as e:
            logger.error(f"Erro na coleta inicial: {e}")
    
    def _run_scheduler(self):
        """Executa scheduler em loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Erro no scheduler: {e}")
                time.sleep(5)
    
    def stop(self):
        """Para coleta contínua"""
        logger.info("Parando coleta contínua...")
        self.running = False
        
        # Aguardar threads terminarem
        for thread in self.threads:
            thread.join(timeout=5)
        
        logger.info("Coleta contínua parada")
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Obtém status da coleta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contar registros por tabela
        tables = ['live_matches', 'live_odds', 'live_statistics', 'live_standings', 'upcoming_matches']
        counts = {}
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        # Última coleta
        cursor.execute("SELECT MAX(collected_at) FROM live_matches")
        last_collection = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'running': self.running,
            'enabled_collections': self.config.enabled_collections,
            'collection_interval': self.config.collection_interval,
            'odds_interval': self.config.odds_interval,
            'stats_interval': self.config.stats_interval,
            'record_counts': counts,
            'last_collection': last_collection,
            'database_path': self.db_path
        }

# Instância global
continuous_collector = None

def initialize_continuous_collector(api_key: str):
    """Inicializa coletor contínuo"""
    global continuous_collector
    config = CollectionConfig(api_key=api_key)
    continuous_collector = ContinuousDataCollector(config)
    return continuous_collector

if __name__ == "__main__":
    # Teste do coletor contínuo
    print("🧪 TESTANDO COLETOR CONTÍNUO DE DADOS")
    print("=" * 50)
    
    # Usar API key do ambiente
    import os
    api_key = os.getenv('API_FOOTBALL_KEY', 'your-api-key-here')
    
    if api_key == 'your-api-key-here':
        print("❌ API key não configurada. Configure API_FOOTBALL_KEY no .env")
        exit(1)
    
    # Inicializar coletor
    collector = initialize_continuous_collector(api_key)
    
    # Testar coleta inicial
    print("Executando coleta inicial...")
    collector._run_initial_collection()
    
    # Obter status
    status = collector.get_collection_status()
    print(f"\nStatus da coleta:")
    print(f"  Rodando: {'Sim' if status['running'] else 'Não'}")
    print(f"  Coleções Habilitadas: {status['enabled_collections']}")
    print(f"  Intervalo de Coleta: {status['collection_interval']}s")
    print(f"  Intervalo de Odds: {status['odds_interval']}s")
    print(f"  Intervalo de Stats: {status['stats_interval']}s")
    print(f"  Última Coleta: {status['last_collection']}")
    
    print(f"\nRegistros coletados:")
    for table, count in status['record_counts'].items():
        print(f"  {table}: {count}")
    
    print("\n🎉 TESTE DE COLETOR CONTÍNUO CONCLUÍDO!")
