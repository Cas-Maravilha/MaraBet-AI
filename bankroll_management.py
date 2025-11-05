"""
ETAPA 5: GESTÃO DE BANCA - MaraBet AI
Sistema especializado para gestão de banca usando Kelly Fracionado
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Níveis de risco para gestão de banca"""
    CONSERVATIVE = "CONSERVATIVE"  # f = 0.25
    MODERATE = "MODERATE"          # f = 0.50
    AGGRESSIVE = "AGGRESSIVE"      # f = 0.75
    MAXIMUM = "MAXIMUM"            # f = 1.00

@dataclass
class BankrollConfig:
    """Configuração de gestão de banca"""
    initial_capital: float = 1000.0
    conservative_fraction: float = 0.25  # f = 0.25 (padrão)
    max_stake_percentage: float = 0.10   # Máximo 10% por aposta
    min_stake_percentage: float = 0.01   # Mínimo 1% por aposta
    max_drawdown_percentage: float = 0.20  # Máximo 20% de drawdown
    stop_loss_percentage: float = 0.15    # Stop loss em 15%
    take_profit_percentage: float = 0.30  # Take profit em 30%
    risk_level: RiskLevel = RiskLevel.CONSERVATIVE

@dataclass
class BetSizing:
    """Resultado do cálculo de sizing de aposta"""
    stake_percentage: float
    stake_amount: float
    kelly_fraction: float
    risk_level: RiskLevel
    probability: float
    odds: float
    expected_value: float
    recommendation: str
    risk_factors: Dict
    timestamp: datetime

@dataclass
class BankrollStatus:
    """Status atual da banca"""
    current_capital: float
    initial_capital: float
    total_profit: float
    profit_percentage: float
    drawdown: float
    drawdown_percentage: float
    max_drawdown: float
    max_drawdown_percentage: float
    active_bets: int
    total_bets: int
    win_rate: float
    average_stake: float
    risk_level: RiskLevel
    status: str

class BankrollManager:
    """
    Gerenciador de Banca com Kelly Fracionado
    Implementa: Stake % = (f/4) × [(P × O) - 1] / (O - 1)
    """
    
    def __init__(self, config: Optional[BankrollConfig] = None):
        self.config = config or BankrollConfig()
        self.bet_history = []
        self.capital_history = []
        self.current_capital = self.config.initial_capital
        self.max_capital = self.config.initial_capital
        self.total_bets = 0
        self.winning_bets = 0
        
    def calculate_kelly_fractional(self, probability: float, odds: float, 
                                 risk_level: Optional[RiskLevel] = None) -> BetSizing:
        """
        Calcula Kelly Fracionado usando a fórmula:
        Stake % = (f/4) × [(P × O) - 1] / (O - 1)
        
        Onde:
        f = fração conservadora (0.25)
        P = probabilidade estimada
        O = odd decimal
        """
        logger.info(f"Calculando Kelly Fracionado: P={probability:.3f}, O={odds:.2f}")
        
        try:
            # Validações
            if probability <= 0 or probability >= 1:
                raise ValueError("Probabilidade deve estar entre 0 e 1")
            if odds <= 1:
                raise ValueError("Odds devem ser maiores que 1")
            
            # Usa nível de risco especificado ou padrão
            risk_level = risk_level or self.config.risk_level
            
            # Determina fração conservadora baseada no nível de risco
            fraction_map = {
                RiskLevel.CONSERVATIVE: 0.25,
                RiskLevel.MODERATE: 0.50,
                RiskLevel.AGGRESSIVE: 0.75,
                RiskLevel.MAXIMUM: 1.00
            }
            f = fraction_map[risk_level]
            
            # Calcula Kelly Fracionado
            # Stake % = (f/4) × [(P × O) - 1] / (O - 1)
            kelly_fraction = (f / 4) * ((probability * odds) - 1) / (odds - 1)
            
            # Aplica limites de segurança
            kelly_fraction = max(0, kelly_fraction)  # Não pode ser negativo
            kelly_fraction = min(kelly_fraction, self.config.max_stake_percentage)
            
            # Calcula valor da aposta
            stake_amount = self.current_capital * kelly_fraction
            
            # Aplica limite mínimo
            min_stake = self.current_capital * self.config.min_stake_percentage
            if kelly_fraction > 0 and stake_amount < min_stake:
                kelly_fraction = self.config.min_stake_percentage
                stake_amount = min_stake
            
            # Calcula EV para análise
            expected_value = (probability * odds) - 1
            
            # Determina recomendação
            recommendation = self._determine_bet_recommendation(
                kelly_fraction, expected_value, probability, odds
            )
            
            # Analisa fatores de risco
            risk_factors = self._analyze_risk_factors(
                kelly_fraction, expected_value, probability, odds
            )
            
            return BetSizing(
                stake_percentage=kelly_fraction,
                stake_amount=stake_amount,
                kelly_fraction=kelly_fraction,
                risk_level=risk_level,
                probability=probability,
                odds=odds,
                expected_value=expected_value,
                recommendation=recommendation,
                risk_factors=risk_factors,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro no cálculo de Kelly Fracionado: {e}")
            # Retorna sizing zero em caso de erro
            return BetSizing(
                stake_percentage=0.0,
                stake_amount=0.0,
                kelly_fraction=0.0,
                risk_level=risk_level or self.config.risk_level,
                probability=probability,
                odds=odds,
                expected_value=0.0,
                recommendation='AVOID',
                risk_factors={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def execute_bet(self, bet_sizing: BetSizing, actual_result: str, 
                   bet_outcome: str) -> Dict:
        """
        Executa uma aposta e atualiza o status da banca
        """
        logger.info(f"Executando aposta: {bet_sizing.stake_amount:.2f} ({bet_sizing.stake_percentage:.1%})")
        
        try:
            # Verifica se a aposta foi vencedora
            is_winner = self._check_bet_result(bet_outcome, actual_result)
            
            # Calcula resultado financeiro
            if is_winner:
                profit = bet_sizing.stake_amount * (bet_sizing.odds - 1)
                result = 'WIN'
            else:
                profit = -bet_sizing.stake_amount
                result = 'LOSS'
            
            # Atualiza capital
            self.current_capital += profit
            self.max_capital = max(self.max_capital, self.current_capital)
            
            # Atualiza estatísticas
            self.total_bets += 1
            if is_winner:
                self.winning_bets += 1
            
            # Registra no histórico
            bet_record = {
                'timestamp': bet_sizing.timestamp,
                'stake_amount': bet_sizing.stake_amount,
                'stake_percentage': bet_sizing.stake_percentage,
                'odds': bet_sizing.odds,
                'probability': bet_sizing.probability,
                'expected_value': bet_sizing.expected_value,
                'bet_outcome': bet_outcome,
                'actual_result': actual_result,
                'is_winner': is_winner,
                'profit': profit,
                'capital_before': self.current_capital - profit,
                'capital_after': self.current_capital,
                'result': result
            }
            
            self.bet_history.append(bet_record)
            self.capital_history.append({
                'timestamp': bet_sizing.timestamp,
                'capital': self.current_capital,
                'profit': profit
            })
            
            return {
                'success': True,
                'bet_record': bet_record,
                'new_capital': self.current_capital,
                'profit': profit,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar aposta: {e}")
            return {
                'success': False,
                'error': str(e),
                'bet_record': None
            }
    
    def get_bankroll_status(self) -> BankrollStatus:
        """
        Retorna status atual da banca
        """
        # Calcula métricas básicas
        total_profit = self.current_capital - self.config.initial_capital
        profit_percentage = (total_profit / self.config.initial_capital) * 100
        
        # Calcula drawdown
        drawdown = self.max_capital - self.current_capital
        drawdown_percentage = (drawdown / self.max_capital) * 100 if self.max_capital > 0 else 0
        
        # Calcula drawdown máximo histórico
        if self.capital_history:
            max_historical = max([record['capital'] for record in self.capital_history])
            max_drawdown = max_historical - min([record['capital'] for record in self.capital_history])
            max_drawdown_percentage = (max_drawdown / max_historical) * 100 if max_historical > 0 else 0
        else:
            max_drawdown = 0
            max_drawdown_percentage = 0
        
        # Calcula estatísticas de apostas
        win_rate = (self.winning_bets / self.total_bets) if self.total_bets > 0 else 0
        
        if self.bet_history:
            average_stake = np.mean([bet['stake_amount'] for bet in self.bet_history])
            active_bets = len([bet for bet in self.bet_history 
                             if (datetime.now() - bet['timestamp']).days < 1])
        else:
            average_stake = 0
            active_bets = 0
        
        # Determina status da banca
        status = self._determine_bankroll_status(
            profit_percentage, drawdown_percentage, win_rate
        )
        
        return BankrollStatus(
            current_capital=self.current_capital,
            initial_capital=self.config.initial_capital,
            total_profit=total_profit,
            profit_percentage=profit_percentage,
            drawdown=drawdown,
            drawdown_percentage=drawdown_percentage,
            max_drawdown=max_drawdown,
            max_drawdown_percentage=max_drawdown_percentage,
            active_bets=active_bets,
            total_bets=self.total_bets,
            win_rate=win_rate,
            average_stake=average_stake,
            risk_level=self.config.risk_level,
            status=status
        )
    
    def check_risk_limits(self) -> Dict:
        """
        Verifica se os limites de risco foram atingidos
        """
        status = self.get_bankroll_status()
        alerts = []
        
        # Verifica drawdown máximo
        if status.drawdown_percentage > self.config.max_drawdown_percentage:
            alerts.append({
                'type': 'MAX_DRAWDOWN_EXCEEDED',
                'level': 'CRITICAL',
                'message': f'Drawdown máximo excedido: {status.drawdown_percentage:.1f}%',
                'current': status.drawdown_percentage,
                'limit': self.config.max_drawdown_percentage
            })
        
        # Verifica stop loss
        if status.profit_percentage < -self.config.stop_loss_percentage * 100:
            alerts.append({
                'type': 'STOP_LOSS_TRIGGERED',
                'level': 'CRITICAL',
                'message': f'Stop loss ativado: {status.profit_percentage:.1f}%',
                'current': status.profit_percentage,
                'limit': -self.config.stop_loss_percentage * 100
            })
        
        # Verifica take profit
        if status.profit_percentage > self.config.take_profit_percentage * 100:
            alerts.append({
                'type': 'TAKE_PROFIT_TRIGGERED',
                'level': 'INFO',
                'message': f'Take profit atingido: {status.profit_percentage:.1f}%',
                'current': status.profit_percentage,
                'limit': self.config.take_profit_percentage * 100
            })
        
        # Verifica taxa de acerto baixa
        if status.total_bets > 10 and status.win_rate < 0.4:
            alerts.append({
                'type': 'LOW_WIN_RATE',
                'level': 'WARNING',
                'message': f'Taxa de acerto baixa: {status.win_rate:.1%}',
                'current': status.win_rate,
                'threshold': 0.4
            })
        
        return {
            'alerts': alerts,
            'total_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['level'] == 'CRITICAL']),
            'status': status
        }
    
    def adjust_risk_level(self, new_risk_level: RiskLevel) -> Dict:
        """
        Ajusta o nível de risco da gestão de banca
        """
        old_risk_level = self.config.risk_level
        self.config.risk_level = new_risk_level
        
        # Atualiza fração conservadora
        fraction_map = {
            RiskLevel.CONSERVATIVE: 0.25,
            RiskLevel.MODERATE: 0.50,
            RiskLevel.AGGRESSIVE: 0.75,
            RiskLevel.MAXIMUM: 1.00
        }
        self.config.conservative_fraction = fraction_map[new_risk_level]
        
        logger.info(f"Nível de risco alterado: {old_risk_level.value} → {new_risk_level.value}")
        
        return {
            'success': True,
            'old_risk_level': old_risk_level.value,
            'new_risk_level': new_risk_level.value,
            'new_fraction': self.config.conservative_fraction
        }
    
    def reset_bankroll(self, new_capital: Optional[float] = None) -> Dict:
        """
        Reseta a banca para capital inicial ou novo valor
        """
        old_capital = self.current_capital
        self.current_capital = new_capital or self.config.initial_capital
        self.max_capital = self.current_capital
        self.bet_history = []
        self.capital_history = []
        self.total_bets = 0
        self.winning_bets = 0
        
        logger.info(f"Banca resetada: {old_capital:.2f} → {self.current_capital:.2f}")
        
        return {
            'success': True,
            'old_capital': old_capital,
            'new_capital': self.current_capital
        }
    
    def get_betting_statistics(self) -> Dict:
        """
        Retorna estatísticas detalhadas das apostas
        """
        if not self.bet_history:
            return {'total_bets': 0}
        
        df = pd.DataFrame(self.bet_history)
        
        # Estatísticas básicas
        total_bets = len(df)
        winning_bets = len(df[df['is_winner'] == True])
        losing_bets = len(df[df['is_winner'] == False])
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        
        # Estatísticas financeiras
        total_staked = df['stake_amount'].sum()
        total_profit = df['profit'].sum()
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        
        # Estatísticas de sizing
        avg_stake_percentage = df['stake_percentage'].mean()
        max_stake_percentage = df['stake_percentage'].max()
        avg_odds = df['odds'].mean()
        avg_probability = df['probability'].mean()
        avg_expected_value = df['expected_value'].mean()
        
        # Análise de sequências
        win_streak = self._calculate_max_streak(df, True)
        loss_streak = self._calculate_max_streak(df, False)
        
        # Análise por nível de risco
        risk_analysis = self._analyze_risk_performance(df)
        
        return {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'losing_bets': losing_bets,
            'win_rate': win_rate,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi': roi,
            'avg_stake_percentage': avg_stake_percentage,
            'max_stake_percentage': max_stake_percentage,
            'avg_odds': avg_odds,
            'avg_probability': avg_probability,
            'avg_expected_value': avg_expected_value,
            'max_win_streak': win_streak,
            'max_loss_streak': loss_streak,
            'risk_analysis': risk_analysis
        }
    
    def _determine_bet_recommendation(self, stake_percentage: float, expected_value: float,
                                    probability: float, odds: float) -> str:
        """Determina recomendação baseada no sizing e EV"""
        if stake_percentage <= 0:
            return 'AVOID'
        elif expected_value < 0:
            return 'AVOID'
        elif stake_percentage < self.config.min_stake_percentage:
            return 'CONSIDER'
        elif expected_value < 0.05:
            return 'CONSIDER'
        elif expected_value < 0.10:
            return 'BET'
        else:
            return 'STRONG_BET'
    
    def _analyze_risk_factors(self, stake_percentage: float, expected_value: float,
                            probability: float, odds: float) -> Dict:
        """Analisa fatores de risco da aposta"""
        factors = {}
        
        # Risco de concentração
        factors['concentration_risk'] = 'HIGH' if stake_percentage > 0.05 else 'LOW'
        
        # Risco de EV
        factors['ev_risk'] = 'HIGH' if expected_value < 0.05 else 'LOW'
        
        # Risco de probabilidade
        factors['probability_risk'] = 'HIGH' if probability < 0.3 or probability > 0.7 else 'LOW'
        
        # Risco de odds
        factors['odds_risk'] = 'HIGH' if odds < 1.5 or odds > 5.0 else 'LOW'
        
        # Score de risco geral
        risk_score = 0
        if factors['concentration_risk'] == 'HIGH': risk_score += 2
        if factors['ev_risk'] == 'HIGH': risk_score += 2
        if factors['probability_risk'] == 'HIGH': risk_score += 1
        if factors['odds_risk'] == 'HIGH': risk_score += 1
        
        factors['overall_risk'] = 'HIGH' if risk_score >= 4 else 'MEDIUM' if risk_score >= 2 else 'LOW'
        factors['risk_score'] = risk_score
        
        return factors
    
    def _determine_bankroll_status(self, profit_percentage: float, drawdown_percentage: float,
                                 win_rate: float) -> str:
        """Determina status geral da banca"""
        if drawdown_percentage > self.config.max_drawdown_percentage:
            return 'CRITICAL'
        elif profit_percentage < -10:
            return 'DANGER'
        elif profit_percentage < 0:
            return 'LOSS'
        elif profit_percentage < 10:
            return 'STABLE'
        elif profit_percentage < 25:
            return 'GROWING'
        else:
            return 'EXCELLENT'
    
    def _check_bet_result(self, bet_outcome: str, actual_result: str) -> bool:
        """Verifica se a aposta foi vencedora"""
        return bet_outcome == actual_result
    
    def _calculate_max_streak(self, df: pd.DataFrame, is_win: bool) -> int:
        """Calcula sequência máxima de vitórias ou derrotas"""
        if df.empty:
            return 0
        
        current_streak = 0
        max_streak = 0
        
        for _, row in df.iterrows():
            if row['is_winner'] == is_win:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _analyze_risk_performance(self, df: pd.DataFrame) -> Dict:
        """Analisa performance por nível de risco"""
        if df.empty:
            return {}
        
        # Agrupa por faixas de stake percentage
        df['stake_range'] = pd.cut(df['stake_percentage'], 
                                 bins=[0, 0.01, 0.02, 0.05, 1.0], 
                                 labels=['Very Low', 'Low', 'Medium', 'High'])
        
        performance = {}
        for range_name in df['stake_range'].cat.categories:
            range_data = df[df['stake_range'] == range_name]
            if not range_data.empty:
                performance[range_name] = {
                    'count': len(range_data),
                    'win_rate': range_data['is_winner'].mean(),
                    'avg_profit': range_data['profit'].mean(),
                    'total_profit': range_data['profit'].sum()
                }
        
        return performance

if __name__ == "__main__":
    # Teste do gerenciador de banca
    print("=== TESTE DO GERENCIADOR DE BANCA ===")
    
    # Configuração de teste
    config = BankrollConfig(
        initial_capital=1000.0,
        conservative_fraction=0.25,
        max_stake_percentage=0.10,
        risk_level=RiskLevel.CONSERVATIVE
    )
    
    manager = BankrollManager(config)
    
    # Testa cálculo de Kelly Fracionado
    print("\nTeste de Cálculo de Kelly Fracionado:")
    test_cases = [
        {'probability': 0.50, 'odds': 2.00, 'description': 'Probabilidade 50%, Odds 2.00'},
        {'probability': 0.45, 'odds': 2.20, 'description': 'Probabilidade 45%, Odds 2.20'},
        {'probability': 0.30, 'odds': 3.50, 'description': 'Probabilidade 30%, Odds 3.50'},
        {'probability': 0.25, 'odds': 4.00, 'description': 'Probabilidade 25%, Odds 4.00'},
    ]
    
    for case in test_cases:
        sizing = manager.calculate_kelly_fractional(
            case['probability'], 
            case['odds']
        )
        
        print(f"\n  {case['description']}:")
        print(f"    Stake %: {sizing.stake_percentage:.2%}")
        print(f"    Stake Amount: R$ {sizing.stake_amount:.2f}")
        print(f"    EV: {sizing.expected_value:.3f}")
        print(f"    Recomendação: {sizing.recommendation}")
        print(f"    Risco: {sizing.risk_factors['overall_risk']}")
    
    # Testa execução de apostas
    print(f"\nTeste de Execução de Apostas:")
    
    # Simula algumas apostas
    bets = [
        {'probability': 0.45, 'odds': 2.20, 'outcome': 'home_win', 'result': 'home_win'},
        {'probability': 0.30, 'odds': 3.50, 'outcome': 'draw', 'result': 'away_win'},
        {'probability': 0.25, 'odds': 4.00, 'outcome': 'away_win', 'result': 'away_win'},
    ]
    
    for i, bet in enumerate(bets, 1):
        sizing = manager.calculate_kelly_fractional(bet['probability'], bet['odds'])
        result = manager.execute_bet(sizing, bet['result'], bet['outcome'])
        
        print(f"\n  Aposta {i}:")
        print(f"    Stake: R$ {sizing.stake_amount:.2f} ({sizing.stake_percentage:.1%})")
        print(f"    Resultado: {result['result']}")
        print(f"    Lucro: R$ {result['profit']:.2f}")
        print(f"    Capital: R$ {result['new_capital']:.2f}")
    
    # Status da banca
    print(f"\nStatus da Banca:")
    status = manager.get_bankroll_status()
    print(f"  Capital atual: R$ {status.current_capital:.2f}")
    print(f"  Lucro total: R$ {status.total_profit:.2f} ({status.profit_percentage:.1f}%)")
    print(f"  Drawdown: {status.drawdown_percentage:.1f}%")
    print(f"  Taxa de acerto: {status.win_rate:.1%}")
    print(f"  Status: {status.status}")
    
    # Verifica limites de risco
    print(f"\nVerificação de Limites de Risco:")
    risk_check = manager.check_risk_limits()
    print(f"  Alertas: {risk_check['total_alerts']}")
    print(f"  Críticos: {risk_check['critical_alerts']}")
    
    if risk_check['alerts']:
        for alert in risk_check['alerts']:
            print(f"    {alert['level']}: {alert['message']}")
    
    # Estatísticas
    print(f"\nEstatísticas de Apostas:")
    stats = manager.get_betting_statistics()
    print(f"  Total de apostas: {stats['total_bets']}")
    print(f"  Taxa de acerto: {stats['win_rate']:.1%}")
    print(f"  ROI: {stats['roi']:.1f}%")
    print(f"  Stake médio: {stats['avg_stake_percentage']:.1%}")
    print(f"  EV médio: {stats['avg_expected_value']:.3f}")
    
    print("\nTeste concluído!")
