"""
Tarefas de Coleta de Dados para MaraBet AI
Processamento assíncrono de coleta de odds e estatísticas
"""

from celery import current_task
from tasks.celery_app import celery_app
from cache.redis_cache import cache, cache_odds, get_odds, cache_stats, get_stats
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback
import time

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.data_collection_tasks.collect_odds_data')
def collect_odds_data(self):
    """
    Coleta dados de odds de todas as ligas monitoradas
    
    Returns:
        Dict com resumo da coleta
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando coleta de odds', 'progress': 0}
        )
        
        logger.info("Iniciando coleta de odds")
        
        from armazenamento.banco_de_dados import DatabaseManager
        from coletores.odds_collector import OddsCollector
        
        db = DatabaseManager()
        
        # Obtém ligas monitoradas
        leagues = db.execute_query("SELECT id, name, api_football_id FROM leagues WHERE active = 1")
        
        if not leagues:
            raise ValueError("Nenhuma liga ativa encontrada")
        
        # Inicializa coletor de odds
        odds_collector = OddsCollector()
        
        results = []
        total_leagues = len(leagues)
        
        for i, league in enumerate(leagues):
            try:
                # Atualiza progresso
                progress = int((i / total_leagues) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Coletando odds para {league["name"]}',
                        'progress': progress
                    }
                )
                
                # Coleta odds para a liga
                league_odds = odds_collector.collect_league_odds(league['api_football_id'])
                
                if league_odds:
                    # Salva odds no banco
                    saved_count = self._save_odds_to_db(db, league['id'], league_odds)
                    
                    # Cache das odds
                    cache_key = f"odds_league_{league['id']}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    cache_odds(cache_key, league_odds, ttl=300)  # 5 minutos
                    
                    results.append({
                        'league_id': league['id'],
                        'league_name': league['name'],
                        'odds_collected': len(league_odds),
                        'saved_to_db': saved_count,
                        'cached': True
                    })
                else:
                    results.append({
                        'league_id': league['id'],
                        'league_name': league['name'],
                        'odds_collected': 0,
                        'saved_to_db': 0,
                        'cached': False,
                        'error': 'Nenhuma odd coletada'
                    })
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar odds para {league['name']}: {e}")
                results.append({
                    'league_id': league['id'],
                    'league_name': league['name'],
                    'error': str(e)
                })
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Coleta de odds concluída', 'progress': 100}
        )
        
        logger.info("Coleta de odds concluída")
        
        return {
            'status': 'success',
            'total_leagues': total_leagues,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro na coleta de odds: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na coleta de odds', 'error': str(e)}
        )
        
        raise

def _save_odds_to_db(self, db: DatabaseManager, league_id: int, odds_data: List[Dict]) -> int:
    """
    Salva odds no banco de dados
    
    Args:
        db: Instância do banco de dados
        league_id: ID da liga
        odds_data: Dados das odds
    
    Returns:
        Número de odds salvas
    """
    saved_count = 0
    
    for odds in odds_data:
        try:
            # Verifica se a partida existe
            match_query = """
                SELECT id FROM matches 
                WHERE league_id = ? AND home_team = ? AND away_team = ? AND match_date = ?
            """
            
            match_data = db.execute_query(match_query, (
                league_id,
                odds.get('home_team'),
                odds.get('away_team'),
                odds.get('match_date')
            ))
            
            if not match_data:
                # Cria partida se não existir
                match_id = self._create_match(db, league_id, odds)
            else:
                match_id = match_data[0]['id']
            
            # Salva odds
            db.execute_query("""
                INSERT OR REPLACE INTO odds 
                (match_id, home_odds, draw_odds, away_odds, over_odds, under_odds, 
                 btts_yes_odds, btts_no_odds, handicap_home_odds, handicap_away_odds,
                 bookmaker, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                odds.get('home_odds'),
                odds.get('draw_odds'),
                odds.get('away_odds'),
                odds.get('over_odds'),
                odds.get('under_odds'),
                odds.get('btts_yes_odds'),
                odds.get('btts_no_odds'),
                odds.get('handicap_home_odds'),
                odds.get('handicap_away_odds'),
                odds.get('bookmaker', 'unknown'),
                datetime.now()
            ))
            
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao salvar odds: {e}")
            continue
    
    return saved_count

def _create_match(self, db: DatabaseManager, league_id: int, odds: Dict) -> int:
    """
    Cria nova partida no banco de dados
    
    Args:
        db: Instância do banco de dados
        league_id: ID da liga
        odds: Dados das odds
    
    Returns:
        ID da partida criada
    """
    db.execute_query("""
        INSERT INTO matches 
        (league_id, home_team, away_team, match_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        league_id,
        odds.get('home_team'),
        odds.get('away_team'),
        odds.get('match_date'),
        'scheduled',
        datetime.now()
    ))
    
    # Obtém ID da partida criada
    match_data = db.execute_query("""
        SELECT id FROM matches 
        WHERE league_id = ? AND home_team = ? AND away_team = ? AND match_date = ?
        ORDER BY id DESC LIMIT 1
    """, (
        league_id,
        odds.get('home_team'),
        odds.get('away_team'),
        odds.get('match_date')
    ))
    
    return match_data[0]['id'] if match_data else None

@celery_app.task(bind=True, name='tasks.data_collection_tasks.collect_stats_data')
def collect_stats_data(self):
    """
    Coleta dados de estatísticas de todas as ligas monitoradas
    
    Returns:
        Dict com resumo da coleta
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando coleta de estatísticas', 'progress': 0}
        )
        
        logger.info("Iniciando coleta de estatísticas")
        
        from armazenamento.banco_de_dados import DatabaseManager
        from coletores.stats_collector import StatsCollector
        
        db = DatabaseManager()
        
        # Obtém ligas monitoradas
        leagues = db.execute_query("SELECT id, name, api_football_id FROM leagues WHERE active = 1")
        
        if not leagues:
            raise ValueError("Nenhuma liga ativa encontrada")
        
        # Inicializa coletor de estatísticas
        stats_collector = StatsCollector()
        
        results = []
        total_leagues = len(leagues)
        
        for i, league in enumerate(leagues):
            try:
                # Atualiza progresso
                progress = int((i / total_leagues) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Coletando estatísticas para {league["name"]}',
                        'progress': progress
                    }
                )
                
                # Coleta estatísticas para a liga
                league_stats = stats_collector.collect_league_stats(league['api_football_id'])
                
                if league_stats:
                    # Salva estatísticas no banco
                    saved_count = self._save_stats_to_db(db, league['id'], league_stats)
                    
                    # Cache das estatísticas
                    cache_key = f"stats_league_{league['id']}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    cache_stats(cache_key, league_stats, ttl=1800)  # 30 minutos
                    
                    results.append({
                        'league_id': league['id'],
                        'league_name': league['name'],
                        'stats_collected': len(league_stats),
                        'saved_to_db': saved_count,
                        'cached': True
                    })
                else:
                    results.append({
                        'league_id': league['id'],
                        'league_name': league['name'],
                        'stats_collected': 0,
                        'saved_to_db': 0,
                        'cached': False,
                        'error': 'Nenhuma estatística coletada'
                    })
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Erro ao coletar estatísticas para {league['name']}: {e}")
                results.append({
                    'league_id': league['id'],
                    'league_name': league['name'],
                    'error': str(e)
                })
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Coleta de estatísticas concluída', 'progress': 100}
        )
        
        logger.info("Coleta de estatísticas concluída")
        
        return {
            'status': 'success',
            'total_leagues': total_leagues,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro na coleta de estatísticas: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na coleta de estatísticas', 'error': str(e)}
        )
        
        raise

def _save_stats_to_db(self, db: DatabaseManager, league_id: int, stats_data: List[Dict]) -> int:
    """
    Salva estatísticas no banco de dados
    
    Args:
        db: Instância do banco de dados
        league_id: ID da liga
        stats_data: Dados das estatísticas
    
    Returns:
        Número de estatísticas salvas
    """
    saved_count = 0
    
    for stats in stats_data:
        try:
            # Verifica se a partida existe
            match_query = """
                SELECT id FROM matches 
                WHERE league_id = ? AND home_team = ? AND away_team = ? AND match_date = ?
            """
            
            match_data = db.execute_query(match_query, (
                league_id,
                stats.get('home_team'),
                stats.get('away_team'),
                stats.get('match_date')
            ))
            
            if not match_data:
                continue  # Pula se partida não existir
            
            match_id = match_data[0]['id']
            
            # Salva estatísticas
            db.execute_query("""
                INSERT OR REPLACE INTO match_statistics 
                (match_id, home_goals, away_goals, home_possession, away_possession,
                 home_shots, away_shots, home_shots_on_target, away_shots_on_target,
                 home_corners, away_corners, home_fouls, away_fouls, home_yellow_cards,
                 away_yellow_cards, home_red_cards, away_red_cards, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                stats.get('home_goals'),
                stats.get('away_goals'),
                stats.get('home_possession'),
                stats.get('away_possession'),
                stats.get('home_shots'),
                stats.get('away_shots'),
                stats.get('home_shots_on_target'),
                stats.get('away_shots_on_target'),
                stats.get('home_corners'),
                stats.get('away_corners'),
                stats.get('home_fouls'),
                stats.get('away_fouls'),
                stats.get('home_yellow_cards'),
                stats.get('away_yellow_cards'),
                stats.get('home_red_cards'),
                stats.get('away_red_cards'),
                datetime.now()
            ))
            
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
            continue
    
    return saved_count

@celery_app.task(bind=True, name='tasks.data_collection_tasks.update_team_stats')
def update_team_stats(self, team_id: int):
    """
    Atualiza estatísticas de um time específico
    
    Args:
        team_id: ID do time
    
    Returns:
        Dict com estatísticas atualizadas
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Atualizando estatísticas do time', 'progress': 0}
        )
        
        logger.info(f"Atualizando estatísticas do time {team_id}")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Obtém dados do time
        team_data = db.execute_query("SELECT * FROM teams WHERE id = ?", (team_id,))
        
        if not team_data:
            raise ValueError(f"Time {team_id} não encontrado")
        
        team = team_data[0]
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Calculando estatísticas', 'progress': 50}
        )
        
        # Calcula estatísticas do time
        stats = self._calculate_team_stats(db, team_id)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Salvando estatísticas', 'progress': 80}
        )
        
        # Salva estatísticas atualizadas
        db.execute_query("""
            UPDATE teams SET
                goals_scored = ?, goals_conceded = ?, wins = ?, draws = ?, losses = ?,
                form = ?, home_form = ?, away_form = ?, updated_at = ?
            WHERE id = ?
        """, (
            stats['goals_scored'],
            stats['goals_conceded'],
            stats['wins'],
            stats['draws'],
            stats['losses'],
            stats['form'],
            stats['home_form'],
            stats['away_form'],
            datetime.now(),
            team_id
        ))
        
        # Cache das estatísticas
        cache_key = f"team_stats_{team_id}"
        cache_stats(cache_key, stats, ttl=3600)  # 1 hora
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Estatísticas atualizadas', 'progress': 100}
        )
        
        logger.info(f"Estatísticas do time {team_id} atualizadas")
        
        return {
            'status': 'success',
            'team_id': team_id,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar estatísticas do time {team_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na atualização', 'error': str(e)}
        )
        
        raise

def _calculate_team_stats(self, db: DatabaseManager, team_id: int) -> Dict:
    """
    Calcula estatísticas de um time
    
    Args:
        db: Instância do banco de dados
        team_id: ID do time
    
    Returns:
        Dict com estatísticas calculadas
    """
    # Obtém partidas do time (últimos 10 jogos)
    matches = db.execute_query("""
        SELECT m.*, ms.home_goals, ms.away_goals, ms.home_possession, ms.away_possession
        FROM matches m
        LEFT JOIN match_statistics ms ON m.id = ms.match_id
        WHERE (m.home_team_id = ? OR m.away_team_id = ?)
        AND m.match_date < ?
        AND m.status = 'finished'
        ORDER BY m.match_date DESC
        LIMIT 10
    """, (team_id, team_id, datetime.now()))
    
    if not matches:
        return {
            'goals_scored': 0,
            'goals_conceded': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'form': 0.0,
            'home_form': 0.0,
            'away_form': 0.0
        }
    
    goals_scored = 0
    goals_conceded = 0
    wins = 0
    draws = 0
    losses = 0
    home_wins = 0
    home_draws = 0
    home_losses = 0
    away_wins = 0
    away_draws = 0
    away_losses = 0
    
    for match in matches:
        is_home = match['home_team_id'] == team_id
        
        if is_home:
            team_goals = match['home_goals'] or 0
            opponent_goals = match['away_goals'] or 0
        else:
            team_goals = match['away_goals'] or 0
            opponent_goals = match['home_goals'] or 0
        
        goals_scored += team_goals
        goals_conceded += opponent_goals
        
        if team_goals > opponent_goals:
            wins += 1
            if is_home:
                home_wins += 1
            else:
                away_wins += 1
        elif team_goals == opponent_goals:
            draws += 1
            if is_home:
                home_draws += 1
            else:
                away_draws += 1
        else:
            losses += 1
            if is_home:
                home_losses += 1
            else:
                away_losses += 1
    
    # Calcula formas
    total_matches = len(matches)
    form = (wins * 3 + draws) / (total_matches * 3) if total_matches > 0 else 0.0
    
    home_matches = home_wins + home_draws + home_losses
    home_form = (home_wins * 3 + home_draws) / (home_matches * 3) if home_matches > 0 else 0.0
    
    away_matches = away_wins + away_draws + away_losses
    away_form = (away_wins * 3 + away_draws) / (away_matches * 3) if away_matches > 0 else 0.0
    
    return {
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'form': form,
        'home_form': home_form,
        'away_form': away_form
    }

@celery_app.task(bind=True, name='tasks.data_collection_tasks.collect_live_data')
def collect_live_data(self):
    """
    Coleta dados em tempo real de partidas ao vivo
    
    Returns:
        Dict com resumo da coleta
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando coleta de dados ao vivo', 'progress': 0}
        )
        
        logger.info("Iniciando coleta de dados ao vivo")
        
        from armazenamento.banco_de_dados import DatabaseManager
        from coletores.live_collector import LiveCollector
        
        db = DatabaseManager()
        
        # Obtém partidas ao vivo
        live_matches = db.execute_query("""
            SELECT m.*, l.name as league_name
            FROM matches m
            JOIN leagues l ON m.league_id = l.id
            WHERE m.status = 'live'
            AND m.match_date >= ?
        """, (datetime.now() - timedelta(hours=2)))
        
        if not live_matches:
            return {
                'status': 'success',
                'message': 'Nenhuma partida ao vivo encontrada',
                'matches_updated': 0
            }
        
        # Inicializa coletor ao vivo
        live_collector = LiveCollector()
        
        results = []
        total_matches = len(live_matches)
        
        for i, match in enumerate(live_matches):
            try:
                # Atualiza progresso
                progress = int((i / total_matches) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Coletando dados ao vivo: {match["home_team"]} vs {match["away_team"]}',
                        'progress': progress
                    }
                )
                
                # Coleta dados ao vivo
                live_data = live_collector.collect_match_data(match['id'])
                
                if live_data:
                    # Atualiza partida
                    db.execute_query("""
                        UPDATE matches SET
                            home_goals = ?, away_goals = ?, status = ?, updated_at = ?
                        WHERE id = ?
                    """, (
                        live_data.get('home_goals'),
                        live_data.get('away_goals'),
                        live_data.get('status'),
                        datetime.now(),
                        match['id']
                    ))
                    
                    # Salva estatísticas ao vivo
                    if live_data.get('statistics'):
                        db.execute_query("""
                            INSERT OR REPLACE INTO live_statistics 
                            (match_id, home_possession, away_possession, home_shots, away_shots,
                             home_shots_on_target, away_shots_on_target, home_corners, away_corners,
                             home_fouls, away_fouls, home_yellow_cards, away_yellow_cards,
                             home_red_cards, away_red_cards, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            match['id'],
                            live_data['statistics'].get('home_possession'),
                            live_data['statistics'].get('away_possession'),
                            live_data['statistics'].get('home_shots'),
                            live_data['statistics'].get('away_shots'),
                            live_data['statistics'].get('home_shots_on_target'),
                            live_data['statistics'].get('away_shots_on_target'),
                            live_data['statistics'].get('home_corners'),
                            live_data['statistics'].get('away_corners'),
                            live_data['statistics'].get('home_fouls'),
                            live_data['statistics'].get('away_fouls'),
                            live_data['statistics'].get('home_yellow_cards'),
                            live_data['statistics'].get('away_yellow_cards'),
                            live_data['statistics'].get('home_red_cards'),
                            live_data['statistics'].get('away_red_cards'),
                            datetime.now()
                        ))
                    
                    results.append({
                        'match_id': match['id'],
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'status': 'updated',
                        'live_data': live_data
                    })
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Erro ao coletar dados ao vivo para partida {match['id']}: {e}")
                results.append({
                    'match_id': match['id'],
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'error': str(e)
                })
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Coleta de dados ao vivo concluída', 'progress': 100}
        )
        
        logger.info("Coleta de dados ao vivo concluída")
        
        return {
            'status': 'success',
            'total_matches': total_matches,
            'matches_updated': len([r for r in results if 'status' in r]),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro na coleta de dados ao vivo: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na coleta ao vivo', 'error': str(e)}
        )
        
        raise
