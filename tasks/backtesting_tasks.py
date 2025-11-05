"""
Tarefas de Backtesting para MaraBet AI
Processamento assíncrono de testes históricos de estratégias
"""

from celery import current_task
from tasks.celery_app import celery_app
from cache.redis_cache import cache, cache_predictions, get_predictions
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
import traceback

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.backtesting_tasks.run_backtesting')
def run_backtesting(self, strategy_name: str, league_id: int, 
                   start_date: str, end_date: str, 
                   initial_capital: float = 10000.0,
                   bet_size: float = 0.02):
    """
    Executa backtesting de uma estratégia específica
    
    Args:
        strategy_name: Nome da estratégia
        league_id: ID da liga
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        initial_capital: Capital inicial
        bet_size: Tamanho da aposta como % do capital
    
    Returns:
        Dict com resultados do backtesting
    """
    try:
        # Atualiza status da tarefa
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando backtesting', 'progress': 0}
        )
        
        logger.info(f"Iniciando backtesting da estratégia {strategy_name} para liga {league_id}")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Carregando dados históricos', 'progress': 20}
        )
        
        # Carrega dados históricos
        query = """
        SELECT m.*, p.prediction, p.prediction_proba, o.home_odds, o.draw_odds, o.away_odds
        FROM matches m
        LEFT JOIN predictions p ON m.id = p.match_id
        LEFT JOIN odds o ON m.id = o.match_id
        WHERE m.league_id = ? 
        AND m.match_date >= ? AND m.match_date <= ?
        AND m.result IS NOT NULL
        ORDER BY m.match_date
        """
        
        data = db.execute_query(query, (league_id, start_date, end_date))
        
        if not data or len(data) < 10:
            raise ValueError(f"Dados insuficientes para backtesting: {len(data) if data else 0} partidas")
        
        # Converte para DataFrame
        df = pd.DataFrame(data)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Aplicando estratégia', 'progress': 40}
        )
        
        # Aplica estratégia
        bets = self._apply_strategy(df, strategy_name, bet_size)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Calculando resultados', 'progress': 60}
        )
        
        # Calcula resultados
        results = self._calculate_results(bets, initial_capital)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Salvando resultados', 'progress': 80}
        )
        
        # Salva resultados no banco
        backtesting_id = self._save_backtesting_results(
            db, strategy_name, league_id, start_date, end_date, 
            initial_capital, bet_size, results
        )
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Backtesting concluído', 'progress': 100}
        )
        
        logger.info(f"Backtesting da estratégia {strategy_name} concluído")
        
        return {
            'status': 'success',
            'backtesting_id': backtesting_id,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro no backtesting: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no backtesting', 'error': str(e)}
        )
        
        raise

def _apply_strategy(self, df: pd.DataFrame, strategy_name: str, bet_size: float) -> List[Dict]:
    """
    Aplica estratégia de apostas aos dados históricos
    
    Args:
        df: DataFrame com dados das partidas
        strategy_name: Nome da estratégia
        bet_size: Tamanho da aposta
    
    Returns:
        Lista de apostas geradas
    """
    bets = []
    
    if strategy_name == 'value_betting':
        bets = self._value_betting_strategy(df, bet_size)
    elif strategy_name == 'kelly_criterion':
        bets = self._kelly_criterion_strategy(df, bet_size)
    elif strategy_name == 'fixed_stake':
        bets = self._fixed_stake_strategy(df, bet_size)
    elif strategy_name == 'confidence_based':
        bets = self._confidence_based_strategy(df, bet_size)
    else:
        raise ValueError(f"Estratégia {strategy_name} não implementada")
    
    return bets

def _value_betting_strategy(self, df: pd.DataFrame, bet_size: float) -> List[Dict]:
    """
    Estratégia de Value Betting
    """
    bets = []
    
    for _, match in df.iterrows():
        if pd.isna(match['prediction']) or pd.isna(match['prediction_proba']):
            continue
        
        # Calcula probabilidade implícita das odds
        home_odds = match['home_odds']
        draw_odds = match['draw_odds']
        away_odds = match['away_odds']
        
        if pd.isna(home_odds) or pd.isna(draw_odds) or pd.isna(away_odds):
            continue
        
        # Probabilidades implícitas
        home_prob = 1 / home_odds
        draw_prob = 1 / draw_odds
        away_prob = 1 / away_odds
        
        # Probabilidades do modelo
        model_probs = json.loads(match['prediction_proba']) if isinstance(match['prediction_proba'], str) else match['prediction_proba']
        
        if not model_probs or len(model_probs) != 3:
            continue
        
        # Verifica value bets
        if model_probs[0] > home_prob * 1.1:  # 10% de margem
            bets.append({
                'match_id': match['id'],
                'bet_type': 'home_win',
                'odds': home_odds,
                'stake': bet_size,
                'model_prob': model_probs[0],
                'implied_prob': home_prob,
                'value': model_probs[0] / home_prob - 1
            })
        
        if model_probs[1] > draw_prob * 1.1:
            bets.append({
                'match_id': match['id'],
                'bet_type': 'draw',
                'odds': draw_odds,
                'stake': bet_size,
                'model_prob': model_probs[1],
                'implied_prob': draw_prob,
                'value': model_probs[1] / draw_prob - 1
            })
        
        if model_probs[2] > away_prob * 1.1:
            bets.append({
                'match_id': match['id'],
                'bet_type': 'away_win',
                'odds': away_odds,
                'stake': bet_size,
                'model_prob': model_probs[2],
                'implied_prob': away_prob,
                'value': model_probs[2] / away_prob - 1
            })
    
    return bets

def _kelly_criterion_strategy(self, df: pd.DataFrame, bet_size: float) -> List[Dict]:
    """
    Estratégia baseada no Critério de Kelly
    """
    bets = []
    
    for _, match in df.iterrows():
        if pd.isna(match['prediction']) or pd.isna(match['prediction_proba']):
            continue
        
        # Probabilidades do modelo
        model_probs = json.loads(match['prediction_proba']) if isinstance(match['prediction_proba'], str) else match['prediction_proba']
        
        if not model_probs or len(model_probs) != 3:
            continue
        
        # Aplica Critério de Kelly para cada resultado
        for i, (bet_type, odds) in enumerate([('home_win', match['home_odds']), 
                                            ('draw', match['draw_odds']), 
                                            ('away_win', match['away_odds'])]):
            
            if pd.isna(odds):
                continue
            
            # Kelly Criterion: f = (bp - q) / b
            # onde b = odds - 1, p = probabilidade de ganhar, q = 1 - p
            b = odds - 1
            p = model_probs[i]
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # Só aposta se Kelly > 0 e < 0.25 (limite de segurança)
            if 0 < kelly_fraction < 0.25:
                bets.append({
                    'match_id': match['id'],
                    'bet_type': bet_type,
                    'odds': odds,
                    'stake': kelly_fraction,
                    'model_prob': p,
                    'kelly_fraction': kelly_fraction,
                    'value': p / (1/odds) - 1
                })
    
    return bets

def _fixed_stake_strategy(self, df: pd.DataFrame, bet_size: float) -> List[Dict]:
    """
    Estratégia de stake fixo
    """
    bets = []
    
    for _, match in df.iterrows():
        if pd.isna(match['prediction']) or pd.isna(match['prediction_proba']):
            continue
        
        # Probabilidades do modelo
        model_probs = json.loads(match['prediction_proba']) if isinstance(match['prediction_proba'], str) else match['prediction_proba']
        
        if not model_probs or len(model_probs) != 3:
            continue
        
        # Encontra a predição com maior probabilidade
        max_prob_idx = np.argmax(model_probs)
        bet_types = ['home_win', 'draw', 'away_win']
        odds_values = [match['home_odds'], match['draw_odds'], match['away_odds']]
        
        if pd.isna(odds_values[max_prob_idx]):
            continue
        
        # Só aposta se probabilidade > 0.6
        if model_probs[max_prob_idx] > 0.6:
            bets.append({
                'match_id': match['id'],
                'bet_type': bet_types[max_prob_idx],
                'odds': odds_values[max_prob_idx],
                'stake': bet_size,
                'model_prob': model_probs[max_prob_idx],
                'value': model_probs[max_prob_idx] / (1/odds_values[max_prob_idx]) - 1
            })
    
    return bets

def _confidence_based_strategy(self, df: pd.DataFrame, bet_size: float) -> List[Dict]:
    """
    Estratégia baseada na confiança do modelo
    """
    bets = []
    
    for _, match in df.iterrows():
        if pd.isna(match['prediction']) or pd.isna(match['prediction_proba']):
            continue
        
        # Probabilidades do modelo
        model_probs = json.loads(match['prediction_proba']) if isinstance(match['prediction_proba'], str) else match['prediction_proba']
        
        if not model_probs or len(model_probs) != 3:
            continue
        
        # Calcula confiança (diferença entre maior e segunda maior probabilidade)
        sorted_probs = sorted(model_probs, reverse=True)
        confidence = sorted_probs[0] - sorted_probs[1]
        
        # Ajusta stake baseado na confiança
        adjusted_stake = bet_size * (0.5 + confidence)
        
        # Encontra a predição com maior probabilidade
        max_prob_idx = np.argmax(model_probs)
        bet_types = ['home_win', 'draw', 'away_win']
        odds_values = [match['home_odds'], match['draw_odds'], match['away_odds']]
        
        if pd.isna(odds_values[max_prob_idx]):
            continue
        
        # Só aposta se confiança > 0.3
        if confidence > 0.3:
            bets.append({
                'match_id': match['id'],
                'bet_type': bet_types[max_prob_idx],
                'odds': odds_values[max_prob_idx],
                'stake': adjusted_stake,
                'model_prob': model_probs[max_prob_idx],
                'confidence': confidence,
                'value': model_probs[max_prob_idx] / (1/odds_values[max_prob_idx]) - 1
            })
    
    return bets

def _calculate_results(self, bets: List[Dict], initial_capital: float) -> Dict:
    """
    Calcula resultados do backtesting
    
    Args:
        bets: Lista de apostas
        initial_capital: Capital inicial
    
    Returns:
        Dict com resultados calculados
    """
    if not bets:
        return {
            'total_bets': 0,
            'winning_bets': 0,
            'losing_bets': 0,
            'win_rate': 0.0,
            'total_staked': 0.0,
            'total_winnings': 0.0,
            'net_profit': 0.0,
            'roi': 0.0,
            'final_capital': initial_capital
        }
    
    # Simula resultados das apostas
    total_staked = 0.0
    total_winnings = 0.0
    winning_bets = 0
    losing_bets = 0
    
    for bet in bets:
        stake = bet['stake']
        total_staked += stake
        
        # Simula resultado (em produção, usaria resultado real da partida)
        # Para demonstração, usa probabilidade do modelo
        if np.random.random() < bet['model_prob']:
            winnings = stake * bet['odds']
            total_winnings += winnings
            winning_bets += 1
        else:
            losing_bets += 1
    
    net_profit = total_winnings - total_staked
    final_capital = initial_capital + net_profit
    win_rate = winning_bets / len(bets) if bets else 0.0
    roi = (net_profit / total_staked) * 100 if total_staked > 0 else 0.0
    
    return {
        'total_bets': len(bets),
        'winning_bets': winning_bets,
        'losing_bets': losing_bets,
        'win_rate': win_rate,
        'total_staked': total_staked,
        'total_winnings': total_winnings,
        'net_profit': net_profit,
        'roi': roi,
        'final_capital': final_capital,
        'profit_factor': total_winnings / total_staked if total_staked > 0 else 0.0
    }

def _save_backtesting_results(self, db: DatabaseManager, strategy_name: str, 
                            league_id: int, start_date: str, end_date: str,
                            initial_capital: float, bet_size: float, 
                            results: Dict) -> int:
    """
    Salva resultados do backtesting no banco de dados
    
    Returns:
        ID do backtesting salvo
    """
    # Insere registro de backtesting
    db.execute_query("""
        INSERT INTO backtesting_results 
        (strategy_name, league_id, start_date, end_date, initial_capital, 
         bet_size, total_bets, winning_bets, losing_bets, win_rate, 
         total_staked, total_winnings, net_profit, roi, final_capital, 
         created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        strategy_name, league_id, start_date, end_date, initial_capital,
        bet_size, results['total_bets'], results['winning_bets'], 
        results['losing_bets'], results['win_rate'], results['total_staked'],
        results['total_winnings'], results['net_profit'], results['roi'],
        results['final_capital'], datetime.now()
    ))
    
    # Obtém ID do backtesting
    backtesting_data = db.execute_query("""
        SELECT id FROM backtesting_results 
        WHERE strategy_name = ? AND league_id = ? AND created_at = (
            SELECT MAX(created_at) FROM backtesting_results 
            WHERE strategy_name = ? AND league_id = ?
        )
    """, (strategy_name, league_id, strategy_name, league_id))
    
    return backtesting_data[0]['id'] if backtesting_data else None

@celery_app.task(bind=True, name='tasks.backtesting_tasks.run_weekly_backtesting')
def run_weekly_backtesting(self):
    """
    Executa backtesting semanal para todas as estratégias e ligas
    
    Returns:
        Dict com resumo dos backtestings
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando backtesting semanal', 'progress': 0}
        )
        
        logger.info("Iniciando backtesting semanal")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Obtém ligas ativas
        leagues = db.execute_query("SELECT id, name FROM leagues WHERE active = 1")
        
        if not leagues:
            raise ValueError("Nenhuma liga ativa encontrada")
        
        # Estratégias para testar
        strategies = ['value_betting', 'kelly_criterion', 'fixed_stake', 'confidence_based']
        
        # Período de teste (últimos 3 meses)
        end_date = datetime.now() - timedelta(days=7)  # Exclui última semana
        start_date = end_date - timedelta(days=90)     # 3 meses atrás
        
        results = []
        total_tasks = len(leagues) * len(strategies)
        completed_tasks = 0
        
        for league in leagues:
            league_id = league['id']
            league_name = league['name']
            
            for strategy in strategies:
                try:
                    # Atualiza progresso
                    progress = int((completed_tasks / total_tasks) * 100)
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'status': f'Testando {strategy} para {league_name}',
                            'progress': progress
                        }
                    )
                    
                    # Executa backtesting
                    result = run_backtesting.delay(
                        strategy_name=strategy,
                        league_id=league_id,
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        initial_capital=10000.0,
                        bet_size=0.02
                    )
                    
                    results.append({
                        'league_id': league_id,
                        'league_name': league_name,
                        'strategy': strategy,
                        'task_id': result.id,
                        'status': 'started'
                    })
                    
                    completed_tasks += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao iniciar backtesting de {strategy} para {league_name}: {e}")
                    results.append({
                        'league_id': league_id,
                        'league_name': league_name,
                        'strategy': strategy,
                        'error': str(e),
                        'status': 'failed'
                    })
                    completed_tasks += 1
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Backtesting semanal iniciado', 'progress': 100}
        )
        
        logger.info(f"Backtesting semanal de {len(results)} combinações iniciado")
        
        return {
            'status': 'success',
            'total_backtests': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro no backtesting semanal: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no backtesting semanal', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.backtesting_tasks.compare_strategies')
def compare_strategies(self, league_id: int, start_date: str, end_date: str):
    """
    Compara performance de diferentes estratégias
    
    Args:
        league_id: ID da liga
        start_date: Data de início
        end_date: Data de fim
    
    Returns:
        Dict com comparação das estratégias
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando comparação de estratégias', 'progress': 0}
        )
        
        logger.info(f"Iniciando comparação de estratégias para liga {league_id}")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Estratégias para comparar
        strategies = ['value_betting', 'kelly_criterion', 'fixed_stake', 'confidence_based']
        
        comparison_results = []
        
        for i, strategy in enumerate(strategies):
            # Atualiza progresso
            progress = int((i / len(strategies)) * 100)
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': f'Testando estratégia {strategy}',
                    'progress': progress
                }
            )
            
            # Executa backtesting
            result = run_backtesting.delay(
                strategy_name=strategy,
                league_id=league_id,
                start_date=start_date,
                end_date=end_date,
                initial_capital=10000.0,
                bet_size=0.02
            )
            
            # Aguarda resultado
            backtesting_result = result.get(timeout=300)  # 5 minutos timeout
            
            if backtesting_result['status'] == 'success':
                comparison_results.append({
                    'strategy': strategy,
                    'results': backtesting_result['results']
                })
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Comparação concluída', 'progress': 100}
        )
        
        logger.info(f"Comparação de estratégias concluída para liga {league_id}")
        
        return {
            'status': 'success',
            'league_id': league_id,
            'comparison_results': comparison_results
        }
        
    except Exception as e:
        logger.error(f"Erro na comparação de estratégias: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na comparação', 'error': str(e)}
        )
        
        raise
