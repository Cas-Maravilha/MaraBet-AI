#!/usr/bin/env python3
"""
Otimizações de Banco de Dados para o MaraBet AI
Índices, consultas otimizadas e cache de consultas
"""

import sqlite3
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from performance.caching_system import cache_manager

logger = logging.getLogger(__name__)

@dataclass
class QueryStats:
    """Estatísticas de consulta"""
    query: str
    execution_time: float
    rows_returned: int
    cache_hit: bool

class DatabaseOptimizer:
    """Otimizador de banco de dados"""
    
    def __init__(self, db_path: str):
        """Inicializa otimizador"""
        self.db_path = db_path
        self.query_cache = {}
        self.query_stats = []
        
        # Criar índices otimizados
        self._create_optimized_indexes()
    
    def _create_optimized_indexes(self):
        """Cria índices otimizados para performance"""
        conn = sqlite3.connect(self.db_path)
        
        indexes = [
            # Índices para tabela bets
            "CREATE INDEX IF NOT EXISTS idx_bets_match_id ON bets(match_id)",
            "CREATE INDEX IF NOT EXISTS idx_bets_timestamp ON bets(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_bets_bet_type ON bets(bet_type)",
            "CREATE INDEX IF NOT EXISTS idx_bets_profit_loss ON bets(profit_loss)",
            "CREATE INDEX IF NOT EXISTS idx_bets_created_at ON bets(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_bets_match_type ON bets(match_id, bet_type)",
            "CREATE INDEX IF NOT EXISTS idx_bets_timestamp_type ON bets(timestamp, bet_type)",
            
            # Índices para tabela predictions
            "CREATE INDEX IF NOT EXISTS idx_predictions_match_id ON predictions(match_id)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions(confidence)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_expected_value ON predictions(expected_value)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_match_confidence ON predictions(match_id, confidence)",
            
            # Índices para tabela matches
            "CREATE INDEX IF NOT EXISTS idx_matches_league_id ON matches(league_id)",
            "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date)",
            "CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status)",
            "CREATE INDEX IF NOT EXISTS idx_matches_league_date ON matches(league_id, match_date)",
            "CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team)",
            "CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team)",
            
            # Índices para tabela teams
            "CREATE INDEX IF NOT EXISTS idx_teams_league_id ON teams(league_id)",
            "CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name)",
            "CREATE INDEX IF NOT EXISTS idx_teams_league_name ON teams(league_id, name)",
            
            # Índices para tabela odds
            "CREATE INDEX IF NOT EXISTS idx_odds_match_id ON odds(match_id)",
            "CREATE INDEX IF NOT EXISTS idx_odds_bookmaker ON odds(bookmaker)",
            "CREATE INDEX IF NOT EXISTS idx_odds_bet_type ON odds(bet_type)",
            "CREATE INDEX IF NOT EXISTS idx_odds_timestamp ON odds(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_odds_match_bookmaker ON odds(match_id, bookmaker)",
            "CREATE INDEX IF NOT EXISTS idx_odds_match_type ON odds(match_id, bet_type)",
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
                logger.debug(f"Índice criado: {index_sql}")
            except Exception as e:
                logger.error(f"Erro ao criar índice: {e}")
        
        conn.commit()
        conn.close()
        logger.info("Índices otimizados criados")
    
    def execute_optimized_query(self, query: str, params: Tuple = (), cache_key: str = None, cache_timeout: int = 300) -> List[Dict]:
        """Executa consulta otimizada com cache"""
        start_time = time.time()
        
        # Verificar cache se chave fornecida
        if cache_key and cache_manager.connected:
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                execution_time = time.time() - start_time
                self.query_stats.append(QueryStats(
                    query=query,
                    execution_time=execution_time,
                    rows_returned=len(cached_result),
                    cache_hit=True
                ))
                logger.debug(f"Cache hit para consulta: {cache_key}")
                return cached_result
        
        # Executar consulta
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        # Converter para lista de dicionários
        result = [dict(row) for row in rows]
        
        execution_time = time.time() - start_time
        
        # Armazenar no cache se chave fornecida
        if cache_key and cache_manager.connected:
            cache_manager.set(cache_key, result, cache_timeout)
        
        # Registrar estatísticas
        self.query_stats.append(QueryStats(
            query=query,
            execution_time=execution_time,
            rows_returned=len(result),
            cache_hit=False
        ))
        
        conn.close()
        
        logger.debug(f"Consulta executada em {execution_time:.3f}s: {len(result)} linhas")
        return result
    
    def get_bets_by_match(self, match_id: str, cache: bool = True) -> List[Dict]:
        """Obtém apostas de uma partida (otimizado)"""
        cache_key = f"bets:match:{match_id}" if cache else None
        
        query = """
            SELECT b.*, m.home_team, m.away_team, m.match_date
            FROM bets b
            JOIN matches m ON b.match_id = m.id
            WHERE b.match_id = ?
            ORDER BY b.created_at DESC
        """
        
        return self.execute_optimized_query(query, (match_id,), cache_key)
    
    def get_predictions_by_match(self, match_id: str, cache: bool = True) -> List[Dict]:
        """Obtém predições de uma partida (otimizado)"""
        cache_key = f"predictions:match:{match_id}" if cache else None
        
        query = """
            SELECT p.*, m.home_team, m.away_team, m.match_date
            FROM predictions p
            JOIN matches m ON p.match_id = m.id
            WHERE p.match_id = ?
            ORDER BY p.confidence DESC
        """
        
        return self.execute_optimized_query(query, (match_id,), cache_key)
    
    def get_roi_analysis(self, days: int = 30, cache: bool = True) -> Dict[str, Any]:
        """Análise de ROI otimizada"""
        cache_key = f"roi_analysis:{days}" if cache else None
        
        if cache_key and cache_manager.connected:
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Consulta otimizada para análise de ROI
        query = """
            SELECT 
                bet_type,
                COUNT(*) as total_bets,
                SUM(stake) as total_stake,
                SUM(profit_loss) as total_profit,
                AVG(profit_loss) as avg_profit,
                AVG(odds) as avg_odds,
                COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
                ROUND(COUNT(CASE WHEN profit_loss > 0 THEN 1 END) * 100.0 / COUNT(*), 2) as win_rate,
                ROUND(SUM(profit_loss) * 100.0 / SUM(stake), 2) as roi
            FROM bets 
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY bet_type
            ORDER BY roi DESC
        """.format(days)
        
        result = self.execute_optimized_query(query)
        
        # Calcular métricas gerais
        total_bets = sum(row['total_bets'] for row in result)
        total_stake = sum(row['total_stake'] for row in result)
        total_profit = sum(row['total_profit'] for row in result)
        overall_roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        
        analysis = {
            "period_days": days,
            "overall": {
                "total_bets": total_bets,
                "total_stake": total_stake,
                "total_profit": total_profit,
                "roi": round(overall_roi, 2)
            },
            "by_bet_type": result
        }
        
        # Armazenar no cache
        if cache_key and cache_manager.connected:
            cache_manager.set(cache_key, analysis, 300)  # 5 minutos
        
        return analysis
    
    def get_team_performance(self, team_id: int, cache: bool = True) -> Dict[str, Any]:
        """Performance de time otimizada"""
        cache_key = f"team_performance:{team_id}" if cache else None
        
        query = """
            SELECT 
                t.name as team_name,
                COUNT(b.id) as total_bets,
                SUM(b.stake) as total_stake,
                SUM(b.profit_loss) as total_profit,
                AVG(b.profit_loss) as avg_profit,
                COUNT(CASE WHEN b.profit_loss > 0 THEN 1 END) as wins,
                ROUND(COUNT(CASE WHEN b.profit_loss > 0 THEN 1 END) * 100.0 / COUNT(b.id), 2) as win_rate,
                ROUND(SUM(b.profit_loss) * 100.0 / SUM(b.stake), 2) as roi
            FROM teams t
            JOIN matches m ON t.id = m.home_team_id OR t.id = m.away_team_id
            JOIN bets b ON m.id = b.match_id
            WHERE t.id = ?
            GROUP BY t.id, t.name
        """
        
        result = self.execute_optimized_query(query, (team_id,), cache_key)
        return result[0] if result else {}
    
    def get_league_standings(self, league_id: int, cache: bool = True) -> List[Dict]:
        """Tabela de classificação otimizada"""
        cache_key = f"league_standings:{league_id}" if cache else None
        
        query = """
            SELECT 
                t.id,
                t.name,
                COUNT(m.id) as matches_played,
                COUNT(CASE WHEN (m.home_team_id = t.id AND m.home_score > m.away_score) 
                          OR (m.away_team_id = t.id AND m.away_score > m.home_score) THEN 1 END) as wins,
                COUNT(CASE WHEN m.home_score = m.away_score THEN 1 END) as draws,
                COUNT(CASE WHEN (m.home_team_id = t.id AND m.home_score < m.away_score) 
                          OR (m.away_team_id = t.id AND m.away_score < m.home_score) THEN 1 END) as losses,
                SUM(CASE WHEN m.home_team_id = t.id THEN m.home_score ELSE m.away_score END) as goals_for,
                SUM(CASE WHEN m.home_team_id = t.id THEN m.away_score ELSE m.home_score END) as goals_against
            FROM teams t
            LEFT JOIN matches m ON (m.home_team_id = t.id OR m.away_team_id = t.id) 
                                AND m.league_id = ? 
                                AND m.status = 'finished'
            WHERE t.league_id = ?
            GROUP BY t.id, t.name
            ORDER BY (wins * 3 + draws) DESC, (goals_for - goals_against) DESC
        """
        
        return self.execute_optimized_query(query, (league_id, league_id), cache_key)
    
    def get_recent_matches(self, limit: int = 10, cache: bool = True) -> List[Dict]:
        """Partidas recentes otimizadas"""
        cache_key = f"recent_matches:{limit}" if cache else None
        
        query = """
            SELECT 
                m.*,
                ht.name as home_team_name,
                at.name as away_team_name,
                l.name as league_name
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams at ON m.away_team_id = at.id
            JOIN leagues l ON m.league_id = l.id
            WHERE m.status = 'finished'
            ORDER BY m.match_date DESC
            LIMIT ?
        """
        
        return self.execute_optimized_query(query, (limit,), cache_key)
    
    def get_betting_trends(self, days: int = 7, cache: bool = True) -> List[Dict]:
        """Tendências de apostas otimizadas"""
        cache_key = f"betting_trends:{days}" if cache else None
        
        query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_bets,
                SUM(stake) as total_stake,
                SUM(profit_loss) as total_profit,
                COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
                ROUND(COUNT(CASE WHEN profit_loss > 0 THEN 1 END) * 100.0 / COUNT(*), 2) as win_rate
            FROM bets
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """.format(days)
        
        return self.execute_optimized_query(query, (), cache_key)
    
    def get_query_stats(self) -> List[Dict]:
        """Obtém estatísticas de consultas"""
        stats = []
        for stat in self.query_stats[-100:]:  # Últimas 100 consultas
            stats.append({
                "query": stat.query[:100] + "..." if len(stat.query) > 100 else stat.query,
                "execution_time": round(stat.execution_time, 3),
                "rows_returned": stat.rows_returned,
                "cache_hit": stat.cache_hit
            })
        
        return stats
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Resumo de performance do banco"""
        if not self.query_stats:
            return {"message": "Nenhuma consulta executada ainda"}
        
        total_queries = len(self.query_stats)
        cache_hits = sum(1 for stat in self.query_stats if stat.cache_hit)
        avg_execution_time = sum(stat.execution_time for stat in self.query_stats) / total_queries
        total_rows = sum(stat.rows_returned for stat in self.query_stats)
        
        return {
            "total_queries": total_queries,
            "cache_hit_rate": round(cache_hits / total_queries * 100, 2),
            "avg_execution_time": round(avg_execution_time, 3),
            "total_rows_returned": total_rows,
            "slowest_query": max(self.query_stats, key=lambda x: x.execution_time).query[:100],
            "fastest_query": min(self.query_stats, key=lambda x: x.execution_time).query[:100]
        }
    
    def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """Analisa performance de uma consulta específica"""
        # Executar EXPLAIN QUERY PLAN
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(f"EXPLAIN QUERY PLAN {query}")
        explain_result = cursor.fetchall()
        conn.close()
        
        # Analisar resultado
        uses_index = any("INDEX" in str(row) for row in explain_result)
        scan_type = "FULL TABLE SCAN" if not uses_index else "INDEX SCAN"
        
        return {
            "query": query,
            "uses_index": uses_index,
            "scan_type": scan_type,
            "explain_plan": explain_result
        }

# Instância global
db_optimizer = DatabaseOptimizer("mara_bet.db")

if __name__ == "__main__":
    # Teste do otimizador de banco
    print("🧪 TESTANDO OTIMIZAÇÕES DE BANCO DE DADOS")
    print("=" * 50)
    
    # Testar consulta otimizada
    start_time = time.time()
    bets = db_optimizer.get_bets_by_match("39_12345")
    execution_time = time.time() - start_time
    
    print(f"Consulta de apostas: {execution_time:.3f}s")
    print(f"Resultados: {len(bets)} apostas")
    
    # Testar análise de ROI
    start_time = time.time()
    roi_analysis = db_optimizer.get_roi_analysis(30)
    execution_time = time.time() - start_time
    
    print(f"Análise de ROI: {execution_time:.3f}s")
    print(f"Tipos de aposta: {len(roi_analysis.get('by_bet_type', []))}")
    
    # Estatísticas de performance
    stats = db_optimizer.get_performance_summary()
    print(f"\nEstatísticas de Performance:")
    print(f"  Total de consultas: {stats.get('total_queries', 0)}")
    print(f"  Taxa de cache hit: {stats.get('cache_hit_rate', 0)}%")
    print(f"  Tempo médio: {stats.get('avg_execution_time', 0)}s")
    
    print("\n🎉 TESTES DE OTIMIZAÇÃO CONCLUÍDOS!")
