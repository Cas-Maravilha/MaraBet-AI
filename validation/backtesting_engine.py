"""
Motor de Backtesting - MaraBet AI
Sistema completo de backtesting com métricas reais de performance
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class BetResult(Enum):
    """Resultado de uma aposta"""
    WIN = "win"
    LOSS = "loss"
    PUSH = "push"  # Empate (odds 1.0)

@dataclass
class BetRecord:
    """Registro de uma aposta individual"""
    date: datetime
    league: str
    home_team: str
    away_team: str
    bet_type: str  # 1X2, Over/Under, etc.
    prediction: str  # 1, X, 2, Over, Under
    odds: float
    stake: float
    confidence: float
    actual_result: Optional[str] = None
    bet_result: Optional[BetResult] = None
    profit_loss: Optional[float] = None
    roi: Optional[float] = None

@dataclass
class BacktestResults:
    """Resultados completos do backtesting"""
    start_date: datetime
    end_date: datetime
    total_bets: int
    winning_bets: int
    losing_bets: int
    push_bets: int
    win_rate: float
    total_stake: float
    total_profit: float
    total_roi: float
    monthly_roi: Dict[str, float]
    league_performance: Dict[str, Dict[str, float]]
    bet_type_performance: Dict[str, Dict[str, float]]
    confidence_analysis: Dict[str, float]
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    average_odds: float
    best_month: str
    worst_month: str
    best_league: str
    worst_league: str

class BacktestingEngine:
    """
    Motor principal de backtesting para MaraBet AI
    Executa simulações históricas com métricas reais
    """
    
    def __init__(self, 
                 initial_capital: float = 10000.0,
                 stake_strategy: str = "fixed",
                 stake_percentage: float = 0.02,
                 min_confidence: float = 0.6,
                 max_confidence: float = 0.95):
        """
        Inicializa o motor de backtesting
        
        Args:
            initial_capital: Capital inicial para simulação
            stake_strategy: Estratégia de stake ('fixed', 'percentage', 'kelly')
            stake_percentage: Percentual do capital por aposta
            min_confidence: Confiança mínima para apostar
            max_confidence: Confiança máxima para apostar
        """
        self.initial_capital = initial_capital
        self.stake_strategy = stake_strategy
        self.stake_percentage = stake_percentage
        self.min_confidence = min_confidence
        self.max_confidence = max_confidence
        
        self.bet_records: List[BetRecord] = []
        self.current_capital = initial_capital
        self.results: Optional[BacktestResults] = None
        
        logger.info(f"BacktestingEngine inicializado - Capital: R$ {initial_capital:,.2f}")
    
    def load_historical_data(self, 
                           matches_file: str,
                           predictions_file: str,
                           odds_file: str) -> bool:
        """
        Carrega dados históricos para backtesting
        
        Args:
            matches_file: Arquivo com resultados de partidas
            predictions_file: Arquivo com predições do modelo
            odds_file: Arquivo com odds históricas
            
        Returns:
            True se carregado com sucesso
        """
        try:
            # Carregar dados de partidas
            self.matches_df = pd.read_csv(matches_file)
            self.matches_df['date'] = pd.to_datetime(self.matches_df['date'])
            
            # Carregar predições
            self.predictions_df = pd.read_csv(predictions_file)
            self.predictions_df['date'] = pd.to_datetime(self.predictions_df['date'])
            
            # Carregar odds
            self.odds_df = pd.read_csv(odds_file)
            self.odds_df['date'] = pd.to_datetime(self.odds_df['date'])
            
            logger.info(f"✅ Dados históricos carregados:")
            logger.info(f"   Partidas: {len(self.matches_df)}")
            logger.info(f"   Predições: {len(self.predictions_df)}")
            logger.info(f"   Odds: {len(self.odds_df)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados históricos: {e}")
            return False
    
    def calculate_stake(self, 
                       confidence: float, 
                       odds: float,
                       current_capital: float) -> float:
        """
        Calcula o valor da aposta baseado na estratégia
        
        Args:
            confidence: Confiança da predição
            odds: Odds da aposta
            current_capital: Capital atual
            
        Returns:
            Valor da aposta
        """
        if self.stake_strategy == "fixed":
            return self.initial_capital * self.stake_percentage
        elif self.stake_strategy == "percentage":
            return current_capital * self.stake_percentage
        elif self.stake_strategy == "kelly":
            # Fórmula de Kelly: f = (bp - q) / b
            # onde b = odds - 1, p = probabilidade, q = 1 - p
            probability = confidence
            b = odds - 1
            p = probability
            q = 1 - probability
            kelly_fraction = (b * p - q) / b
            # Limitar Kelly a 5% do capital
            kelly_fraction = max(0, min(kelly_fraction, 0.05))
            return current_capital * kelly_fraction
        else:
            return current_capital * self.stake_percentage
    
    def determine_bet_result(self, 
                           prediction: str,
                           actual_result: str,
                           bet_type: str) -> BetResult:
        """
        Determina o resultado de uma aposta
        
        Args:
            prediction: Predição feita
            actual_result: Resultado real
            bet_type: Tipo de aposta
            
        Returns:
            Resultado da aposta
        """
        if bet_type == "1X2":
            if prediction == actual_result:
                return BetResult.WIN
            else:
                return BetResult.LOSS
        elif bet_type == "Over/Under":
            # Lógica para Over/Under (simplificada)
            if prediction == actual_result:
                return BetResult.WIN
            else:
                return BetResult.LOSS
        else:
            return BetResult.LOSS
    
    def calculate_profit_loss(self, 
                            bet_result: BetResult,
                            stake: float,
                            odds: float) -> float:
        """
        Calcula lucro/prejuízo de uma aposta
        
        Args:
            bet_result: Resultado da aposta
            stake: Valor apostado
            odds: Odds da aposta
            
        Returns:
            Lucro/prejuízo
        """
        if bet_result == BetResult.WIN:
            return stake * (odds - 1)
        elif bet_result == BetResult.LOSS:
            return -stake
        else:  # PUSH
            return 0
    
    def run_backtest(self, 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> BacktestResults:
        """
        Executa o backtesting completo
        
        Args:
            start_date: Data de início (opcional)
            end_date: Data de fim (opcional)
            
        Returns:
            Resultados do backtesting
        """
        try:
            logger.info("🚀 Iniciando backtesting...")
            
            # Filtrar dados por período
            if start_date:
                self.matches_df = self.matches_df[self.matches_df['date'] >= start_date]
            if end_date:
                self.matches_df = self.matches_df[self.matches_df['date'] <= end_date]
            
            # Resetar estado
            self.bet_records = []
            self.current_capital = self.initial_capital
            
            # Processar cada predição
            for _, pred_row in self.predictions_df.iterrows():
                pred_date = pred_row['date']
                
                # Filtrar partidas do mesmo dia
                day_matches = self.matches_df[
                    self.matches_df['date'].dt.date == pred_date.date()
                ]
                
                if day_matches.empty:
                    continue
                
                # Processar cada partida do dia
                for _, match_row in day_matches.iterrows():
                    self._process_match_prediction(pred_row, match_row)
            
            # Calcular resultados
            self.results = self._calculate_results()
            
            logger.info("✅ Backtesting concluído com sucesso")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Erro no backtesting: {e}")
            raise
    
    def _process_match_prediction(self, pred_row: pd.Series, match_row: pd.Series):
        """Processa uma predição para uma partida específica"""
        try:
            # Verificar se há predição para esta partida
            if pred_row['fixture_id'] != match_row['fixture_id']:
                return
            
            confidence = pred_row['confidence']
            
            # Verificar confiança mínima
            if confidence < self.min_confidence or confidence > self.max_confidence:
                return
            
            # Obter odds para esta partida
            match_odds = self.odds_df[
                self.odds_df['fixture_id'] == match_row['fixture_id']
            ]
            
            if match_odds.empty:
                return
            
            # Processar diferentes tipos de aposta
            bet_types = ['1X2', 'Over/Under']
            
            for bet_type in bet_types:
                self._process_bet_type(pred_row, match_row, match_odds, bet_type)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar predição: {e}")
    
    def _process_bet_type(self, 
                         pred_row: pd.Series, 
                         match_row: pd.Series, 
                         match_odds: pd.DataFrame,
                         bet_type: str):
        """Processa um tipo específico de aposta"""
        try:
            if bet_type == "1X2":
                prediction = pred_row['prediction_1x2']
                odds_col = 'odds_1x2'
            elif bet_type == "Over/Under":
                prediction = pred_row['prediction_ou']
                odds_col = 'odds_ou'
            else:
                return
            
            # Obter odds
            odds_value = match_odds[odds_col].iloc[0] if odds_col in match_odds.columns else 1.0
            
            if odds_value <= 1.0:
                return
            
            # Calcular stake
            stake = self.calculate_stake(
                pred_row['confidence'],
                odds_value,
                self.current_capital
            )
            
            if stake <= 0:
                return
            
            # Determinar resultado real
            actual_result = self._get_actual_result(match_row, bet_type)
            
            # Criar registro da aposta
            bet_record = BetRecord(
                date=pred_row['date'],
                league=match_row['league_name'],
                home_team=match_row['home_team'],
                away_team=match_row['away_team'],
                bet_type=bet_type,
                prediction=prediction,
                odds=odds_value,
                stake=stake,
                confidence=pred_row['confidence'],
                actual_result=actual_result
            )
            
            # Determinar resultado da aposta
            bet_record.bet_result = self.determine_bet_result(
                prediction, actual_result, bet_type
            )
            
            # Calcular lucro/prejuízo
            bet_record.profit_loss = self.calculate_profit_loss(
                bet_record.bet_result, stake, odds_value
            )
            
            # Calcular ROI
            bet_record.roi = (bet_record.profit_loss / stake) * 100 if stake > 0 else 0
            
            # Atualizar capital
            self.current_capital += bet_record.profit_loss
            
            # Adicionar ao registro
            self.bet_records.append(bet_record)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar tipo de aposta {bet_type}: {e}")
    
    def _get_actual_result(self, match_row: pd.Series, bet_type: str) -> str:
        """Obtém o resultado real da partida"""
        try:
            if bet_type == "1X2":
                home_score = match_row['home_score']
                away_score = match_row['away_score']
                
                if home_score > away_score:
                    return "1"
                elif away_score > home_score:
                    return "2"
                else:
                    return "X"
            elif bet_type == "Over/Under":
                total_goals = match_row['home_score'] + match_row['away_score']
                threshold = 2.5  # Padrão
                
                if total_goals > threshold:
                    return "Over"
                else:
                    return "Under"
            else:
                return "Unknown"
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter resultado real: {e}")
            return "Unknown"
    
    def _calculate_results(self) -> BacktestResults:
        """Calcula os resultados completos do backtesting"""
        try:
            if not self.bet_records:
                return BacktestResults(
                    start_date=datetime.now(),
                    end_date=datetime.now(),
                    total_bets=0,
                    winning_bets=0,
                    losing_bets=0,
                    push_bets=0,
                    win_rate=0.0,
                    total_stake=0.0,
                    total_profit=0.0,
                    total_roi=0.0,
                    monthly_roi={},
                    league_performance={},
                    bet_type_performance={},
                    confidence_analysis={},
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    profit_factor=0.0,
                    average_odds=0.0,
                    best_month="",
                    worst_month="",
                    best_league="",
                    worst_league=""
                )
            
            # Métricas básicas
            total_bets = len(self.bet_records)
            winning_bets = sum(1 for bet in self.bet_records if bet.bet_result == BetResult.WIN)
            losing_bets = sum(1 for bet in self.bet_records if bet.bet_result == BetResult.LOSS)
            push_bets = sum(1 for bet in self.bet_records if bet.bet_result == BetResult.PUSH)
            
            win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0
            
            total_stake = sum(bet.stake for bet in self.bet_records)
            total_profit = sum(bet.profit_loss for bet in self.bet_records)
            total_roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
            
            # ROI mensal
            monthly_roi = self._calculate_monthly_roi()
            
            # Performance por liga
            league_performance = self._calculate_league_performance()
            
            # Performance por tipo de aposta
            bet_type_performance = self._calculate_bet_type_performance()
            
            # Análise de confiança
            confidence_analysis = self._calculate_confidence_analysis()
            
            # Métricas avançadas
            sharpe_ratio = self._calculate_sharpe_ratio()
            max_drawdown = self._calculate_max_drawdown()
            profit_factor = self._calculate_profit_factor()
            average_odds = np.mean([bet.odds for bet in self.bet_records])
            
            # Melhores e piores
            best_month = max(monthly_roi.items(), key=lambda x: x[1])[0] if monthly_roi else ""
            worst_month = min(monthly_roi.items(), key=lambda x: x[1])[0] if monthly_roi else ""
            best_league = max(league_performance.items(), key=lambda x: x[1]['roi'])[0] if league_performance else ""
            worst_league = min(league_performance.items(), key=lambda x: x[1]['roi'])[0] if league_performance else ""
            
            return BacktestResults(
                start_date=min(bet.date for bet in self.bet_records),
                end_date=max(bet.date for bet in self.bet_records),
                total_bets=total_bets,
                winning_bets=winning_bets,
                losing_bets=losing_bets,
                push_bets=push_bets,
                win_rate=win_rate,
                total_stake=total_stake,
                total_profit=total_profit,
                total_roi=total_roi,
                monthly_roi=monthly_roi,
                league_performance=league_performance,
                bet_type_performance=bet_type_performance,
                confidence_analysis=confidence_analysis,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                profit_factor=profit_factor,
                average_odds=average_odds,
                best_month=best_month,
                worst_month=worst_month,
                best_league=best_league,
                worst_league=worst_league
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular resultados: {e}")
            raise
    
    def _calculate_monthly_roi(self) -> Dict[str, float]:
        """Calcula ROI mensal"""
        try:
            monthly_data = {}
            
            for bet in self.bet_records:
                month_key = bet.date.strftime("%Y-%m")
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'stake': 0, 'profit': 0}
                
                monthly_data[month_key]['stake'] += bet.stake
                monthly_data[month_key]['profit'] += bet.profit_loss
            
            monthly_roi = {}
            for month, data in monthly_data.items():
                roi = (data['profit'] / data['stake']) * 100 if data['stake'] > 0 else 0
                monthly_roi[month] = roi
            
            return monthly_roi
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI mensal: {e}")
            return {}
    
    def _calculate_league_performance(self) -> Dict[str, Dict[str, float]]:
        """Calcula performance por liga"""
        try:
            league_data = {}
            
            for bet in self.bet_records:
                league = bet.league
                
                if league not in league_data:
                    league_data[league] = {
                        'bets': 0, 'wins': 0, 'stake': 0, 'profit': 0
                    }
                
                league_data[league]['bets'] += 1
                league_data[league]['stake'] += bet.stake
                league_data[league]['profit'] += bet.profit_loss
                
                if bet.bet_result == BetResult.WIN:
                    league_data[league]['wins'] += 1
            
            # Calcular métricas
            league_performance = {}
            for league, data in league_data.items():
                win_rate = (data['wins'] / data['bets']) * 100 if data['bets'] > 0 else 0
                roi = (data['profit'] / data['stake']) * 100 if data['stake'] > 0 else 0
                
                league_performance[league] = {
                    'bets': data['bets'],
                    'wins': data['wins'],
                    'win_rate': win_rate,
                    'stake': data['stake'],
                    'profit': data['profit'],
                    'roi': roi
                }
            
            return league_performance
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular performance por liga: {e}")
            return {}
    
    def _calculate_bet_type_performance(self) -> Dict[str, Dict[str, float]]:
        """Calcula performance por tipo de aposta"""
        try:
            bet_type_data = {}
            
            for bet in self.bet_records:
                bet_type = bet.bet_type
                
                if bet_type not in bet_type_data:
                    bet_type_data[bet_type] = {
                        'bets': 0, 'wins': 0, 'stake': 0, 'profit': 0
                    }
                
                bet_type_data[bet_type]['bets'] += 1
                bet_type_data[bet_type]['stake'] += bet.stake
                bet_type_data[bet_type]['profit'] += bet.profit_loss
                
                if bet.bet_result == BetResult.WIN:
                    bet_type_data[bet_type]['wins'] += 1
            
            # Calcular métricas
            bet_type_performance = {}
            for bet_type, data in bet_type_data.items():
                win_rate = (data['wins'] / data['bets']) * 100 if data['bets'] > 0 else 0
                roi = (data['profit'] / data['stake']) * 100 if data['stake'] > 0 else 0
                
                bet_type_performance[bet_type] = {
                    'bets': data['bets'],
                    'wins': data['wins'],
                    'win_rate': win_rate,
                    'stake': data['stake'],
                    'profit': data['profit'],
                    'roi': roi
                }
            
            return bet_type_performance
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular performance por tipo de aposta: {e}")
            return {}
    
    def _calculate_confidence_analysis(self) -> Dict[str, float]:
        """Calcula análise de confiança"""
        try:
            confidence_ranges = {
                '60-70%': [],
                '70-80%': [],
                '80-90%': [],
                '90-95%': []
            }
            
            for bet in self.bet_records:
                conf = bet.confidence
                if 0.6 <= conf < 0.7:
                    confidence_ranges['60-70%'].append(bet)
                elif 0.7 <= conf < 0.8:
                    confidence_ranges['70-80%'].append(bet)
                elif 0.8 <= conf < 0.9:
                    confidence_ranges['80-90%'].append(bet)
                elif 0.9 <= conf <= 0.95:
                    confidence_ranges['90-95%'].append(bet)
            
            analysis = {}
            for range_name, bets in confidence_ranges.items():
                if bets:
                    win_rate = sum(1 for bet in bets if bet.bet_result == BetResult.WIN) / len(bets) * 100
                    total_stake = sum(bet.stake for bet in bets)
                    total_profit = sum(bet.profit_loss for bet in bets)
                    roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
                    
                    analysis[range_name] = {
                        'bets': len(bets),
                        'win_rate': win_rate,
                        'roi': roi
                    }
                else:
                    analysis[range_name] = {
                        'bets': 0,
                        'win_rate': 0,
                        'roi': 0
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular análise de confiança: {e}")
            return {}
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calcula Sharpe Ratio"""
        try:
            if len(self.bet_records) < 2:
                return 0.0
            
            returns = [bet.profit_loss for bet in self.bet_records]
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return == 0:
                return 0.0
            
            # Assumir risk-free rate de 0.5% ao mês
            risk_free_rate = 0.005
            sharpe = (mean_return - risk_free_rate) / std_return
            
            return sharpe
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Sharpe Ratio: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self) -> float:
        """Calcula Maximum Drawdown"""
        try:
            if not self.bet_records:
                return 0.0
            
            cumulative_profit = 0
            peak = 0
            max_dd = 0
            
            for bet in self.bet_records:
                cumulative_profit += bet.profit_loss
                peak = max(peak, cumulative_profit)
                drawdown = peak - cumulative_profit
                max_dd = max(max_dd, drawdown)
            
            return max_dd
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Maximum Drawdown: {e}")
            return 0.0
    
    def _calculate_profit_factor(self) -> float:
        """Calcula Profit Factor"""
        try:
            total_wins = sum(bet.profit_loss for bet in self.bet_records if bet.profit_loss > 0)
            total_losses = abs(sum(bet.profit_loss for bet in self.bet_records if bet.profit_loss < 0))
            
            if total_losses == 0:
                return float('inf') if total_wins > 0 else 0.0
            
            return total_wins / total_losses
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Profit Factor: {e}")
            return 0.0
    
    def save_results(self, output_file: str) -> bool:
        """
        Salva resultados do backtesting
        
        Args:
            output_file: Arquivo de saída
            
        Returns:
            True se salvo com sucesso
        """
        try:
            if not self.results:
                logger.error("❌ Nenhum resultado para salvar")
                return False
            
            # Converter resultados para dicionário
            results_dict = {
                'start_date': self.results.start_date.isoformat(),
                'end_date': self.results.end_date.isoformat(),
                'total_bets': self.results.total_bets,
                'winning_bets': self.results.winning_bets,
                'losing_bets': self.results.losing_bets,
                'push_bets': self.results.push_bets,
                'win_rate': self.results.win_rate,
                'total_stake': self.results.total_stake,
                'total_profit': self.results.total_profit,
                'total_roi': self.results.total_roi,
                'monthly_roi': self.results.monthly_roi,
                'league_performance': self.results.league_performance,
                'bet_type_performance': self.results.bet_type_performance,
                'confidence_analysis': self.results.confidence_analysis,
                'sharpe_ratio': self.results.sharpe_ratio,
                'max_drawdown': self.results.max_drawdown,
                'profit_factor': self.results.profit_factor,
                'average_odds': self.results.average_odds,
                'best_month': self.results.best_month,
                'worst_month': self.results.worst_month,
                'best_league': self.results.best_league,
                'worst_league': self.results.worst_league
            }
            
            # Salvar em JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Resultados salvos em {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")
            return False
