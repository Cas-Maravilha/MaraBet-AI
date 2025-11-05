#!/usr/bin/env python3
"""
Métricas de Negócio para o MaraBet AI
Monitoramento de ROI, lucro/prejuízo e performance financeira
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import logging

logger = logging.getLogger(__name__)

@dataclass
class BetResult:
    """Resultado de uma aposta"""
    bet_id: str
    match_id: str
    bet_type: str
    stake: float
    odds: float
    predicted_outcome: str
    actual_outcome: str
    profit_loss: float
    roi: float
    timestamp: datetime

@dataclass
class BusinessMetrics:
    """Métricas de negócio"""
    total_bets: int
    total_stake: float
    total_profit_loss: float
    total_roi: float
    win_rate: float
    avg_odds: float
    avg_stake: float
    best_bet: Optional[BetResult]
    worst_bet: Optional[BetResult]
    period_start: datetime
    period_end: datetime

class BusinessMetricsCollector:
    """Coletor de métricas de negócio"""
    
    def __init__(self):
        """Inicializa coletor de métricas"""
        self.registry = CollectorRegistry()
        self.bet_results: List[BetResult] = []
        
        # Métricas Prometheus
        self.total_bets = Counter(
            'marabet_total_bets',
            'Total de apostas realizadas',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.total_stake = Counter(
            'marabet_total_stake',
            'Total apostado',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.total_profit_loss = Gauge(
            'marabet_total_profit_loss',
            'Lucro/Prejuízo total',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.current_roi = Gauge(
            'marabet_current_roi',
            'ROI atual',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.win_rate = Gauge(
            'marabet_win_rate',
            'Taxa de acerto',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.avg_odds = Gauge(
            'marabet_avg_odds',
            'Odds média',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.avg_stake = Gauge(
            'marabet_avg_stake',
            'Aposta média',
            ['bet_type', 'league'],
            registry=self.registry
        )
        
        self.bet_value_distribution = Histogram(
            'marabet_bet_value_distribution',
            'Distribuição de valores de apostas',
            ['bet_type'],
            buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000, float('inf')],
            registry=self.registry
        )
        
        self.roi_distribution = Histogram(
            'marabet_roi_distribution',
            'Distribuição de ROI',
            ['bet_type'],
            buckets=[-1.0, -0.5, -0.2, -0.1, 0.0, 0.1, 0.2, 0.5, 1.0, float('inf')],
            registry=self.registry
        )
    
    def add_bet_result(self, bet_result: BetResult):
        """Adiciona resultado de aposta"""
        self.bet_results.append(bet_result)
        
        # Atualizar métricas Prometheus
        self.total_bets.labels(
            bet_type=bet_result.bet_type,
            league=self._get_league_from_match(bet_result.match_id)
        ).inc()
        
        self.total_stake.labels(
            bet_type=bet_result.bet_type,
            league=self._get_league_from_match(bet_result.match_id)
        ).inc(bet_result.stake)
        
        # Usar Gauge para profit/loss (pode ser negativo)
        self.total_profit_loss.labels(
            bet_type=bet_result.bet_type,
            league=self._get_league_from_match(bet_result.match_id)
        ).set(self._get_total_profit_loss(bet_result.bet_type, bet_result.match_id))
        
        self.bet_value_distribution.labels(
            bet_type=bet_result.bet_type
        ).observe(bet_result.stake)
        
        self.roi_distribution.labels(
            bet_type=bet_result.bet_type
        ).observe(bet_result.roi)
        
        # Atualizar métricas calculadas
        self._update_calculated_metrics()
    
    def _get_total_profit_loss(self, bet_type: str, match_id: str) -> float:
        """Obtém total de profit/loss para tipo de aposta e liga"""
        league = self._get_league_from_match(match_id)
        return sum(
            bet.profit_loss for bet in self.bet_results
            if bet.bet_type == bet_type and self._get_league_from_match(bet.match_id) == league
        )
    
    def _get_league_from_match(self, match_id: str) -> str:
        """Obtém liga do match (simulado)"""
        # Em produção, consultar banco de dados
        leagues = {
            '39': 'premier_league',
            '140': 'laliga',
            '78': 'bundesliga',
            '135': 'serie_a',
            '61': 'ligue_1'
        }
        return leagues.get(match_id[:2], 'unknown')
    
    def _update_calculated_metrics(self):
        """Atualiza métricas calculadas"""
        if not self.bet_results:
            return
        
        # Agrupar por tipo de aposta e liga
        grouped_results = {}
        for bet in self.bet_results:
            key = (bet.bet_type, self._get_league_from_match(bet.match_id))
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(bet)
        
        # Calcular métricas para cada grupo
        for (bet_type, league), bets in grouped_results.items():
            total_stake = sum(b.stake for b in bets)
            total_profit_loss = sum(b.profit_loss for b in bets)
            wins = sum(1 for b in bets if b.profit_loss > 0)
            
            # ROI atual
            roi = (total_profit_loss / total_stake) if total_stake > 0 else 0
            self.current_roi.labels(bet_type=bet_type, league=league).set(roi)
            
            # Taxa de acerto
            win_rate = (wins / len(bets)) if bets else 0
            self.win_rate.labels(bet_type=bet_type, league=league).set(win_rate)
            
            # Odds média
            avg_odds = sum(b.odds for b in bets) / len(bets) if bets else 0
            self.avg_odds.labels(bet_type=bet_type, league=league).set(avg_odds)
            
            # Aposta média
            avg_stake = total_stake / len(bets) if bets else 0
            self.avg_stake.labels(bet_type=bet_type, league=league).set(avg_stake)
    
    def get_business_metrics(self, period_days: int = 30) -> BusinessMetrics:
        """Obtém métricas de negócio para um período"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Filtrar apostas do período
        period_bets = [
            bet for bet in self.bet_results
            if start_date <= bet.timestamp <= end_date
        ]
        
        if not period_bets:
            return BusinessMetrics(
                total_bets=0,
                total_stake=0.0,
                total_profit_loss=0.0,
                total_roi=0.0,
                win_rate=0.0,
                avg_odds=0.0,
                avg_stake=0.0,
                best_bet=None,
                worst_bet=None,
                period_start=start_date,
                period_end=end_date
            )
        
        # Calcular métricas
        total_bets = len(period_bets)
        total_stake = sum(bet.stake for bet in period_bets)
        total_profit_loss = sum(bet.profit_loss for bet in period_bets)
        total_roi = (total_profit_loss / total_stake) if total_stake > 0 else 0
        win_rate = sum(1 for bet in period_bets if bet.profit_loss > 0) / total_bets
        avg_odds = sum(bet.odds for bet in period_bets) / total_bets
        avg_stake = total_stake / total_bets
        
        # Melhor e pior aposta
        best_bet = max(period_bets, key=lambda x: x.profit_loss) if period_bets else None
        worst_bet = min(period_bets, key=lambda x: x.profit_loss) if period_bets else None
        
        return BusinessMetrics(
            total_bets=total_bets,
            total_stake=total_stake,
            total_profit_loss=total_profit_loss,
            total_roi=total_roi,
            win_rate=win_rate,
            avg_odds=avg_odds,
            avg_stake=avg_stake,
            best_bet=best_bet,
            worst_bet=worst_bet,
            period_start=start_date,
            period_end=end_date
        )
    
    def get_roi_analysis(self, period_days: int = 30) -> Dict:
        """Análise detalhada de ROI"""
        metrics = self.get_business_metrics(period_days)
        
        # Análise por tipo de aposta
        bet_type_analysis = {}
        for bet_type in ['home_win', 'draw', 'away_win', 'over_2_5', 'under_2_5']:
            type_bets = [b for b in self.bet_results if b.bet_type == bet_type]
            if type_bets:
                total_stake = sum(b.stake for b in type_bets)
                total_profit = sum(b.profit_loss for b in type_bets)
                roi = (total_profit / total_stake) if total_stake > 0 else 0
                win_rate = sum(1 for b in type_bets if b.profit_loss > 0) / len(type_bets)
                
                bet_type_analysis[bet_type] = {
                    'total_bets': len(type_bets),
                    'total_stake': total_stake,
                    'total_profit': total_profit,
                    'roi': roi,
                    'win_rate': win_rate
                }
        
        return {
            'overall_metrics': {
                'total_bets': metrics.total_bets,
                'total_stake': metrics.total_stake,
                'total_profit_loss': metrics.total_profit_loss,
                'roi': metrics.total_roi,
                'win_rate': metrics.win_rate
            },
            'bet_type_analysis': bet_type_analysis,
            'period': f"{period_days} days",
            'best_bet': {
                'bet_id': metrics.best_bet.bet_id,
                'profit': metrics.best_bet.profit_loss,
                'roi': metrics.best_bet.roi
            } if metrics.best_bet else None,
            'worst_bet': {
                'bet_id': metrics.worst_bet.bet_id,
                'loss': metrics.worst_bet.profit_loss,
                'roi': metrics.worst_bet.roi
            } if metrics.worst_bet else None
        }
    
    def get_performance_trends(self, days: int = 7) -> Dict:
        """Tendências de performance"""
        trends = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            day_bets = [
                bet for bet in self.bet_results
                if bet.timestamp.date() == date.date()
            ]
            
            if day_bets:
                total_stake = sum(bet.stake for bet in day_bets)
                total_profit = sum(bet.profit_loss for bet in day_bets)
                roi = (total_profit / total_stake) if total_stake > 0 else 0
                win_rate = sum(1 for bet in day_bets if bet.profit_loss > 0) / len(day_bets)
            else:
                total_stake = 0
                total_profit = 0
                roi = 0
                win_rate = 0
            
            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'total_bets': len(day_bets),
                'total_stake': total_stake,
                'total_profit': total_profit,
                'roi': roi,
                'win_rate': win_rate
            })
        
        return {
            'trends': trends,
            'period_days': days
        }
    
    def export_metrics(self) -> str:
        """Exporta métricas em formato Prometheus"""
        from prometheus_client import generate_latest
        return generate_latest(self.registry)

# Instância global
business_metrics = BusinessMetricsCollector()

if __name__ == "__main__":
    # Teste das métricas de negócio
    print("🧪 TESTANDO MÉTRICAS DE NEGÓCIO")
    print("=" * 40)
    
    # Adicionar alguns resultados de teste
    test_bets = [
        BetResult(
            bet_id="bet_001",
            match_id="39_12345",
            bet_type="home_win",
            stake=100.0,
            odds=1.85,
            predicted_outcome="home_win",
            actual_outcome="home_win",
            profit_loss=85.0,
            roi=0.85,
            timestamp=datetime.now() - timedelta(days=1)
        ),
        BetResult(
            bet_id="bet_002",
            match_id="140_67890",
            bet_type="draw",
            stake=50.0,
            odds=3.40,
            predicted_outcome="draw",
            actual_outcome="away_win",
            profit_loss=-50.0,
            roi=-1.0,
            timestamp=datetime.now() - timedelta(days=2)
        ),
        BetResult(
            bet_id="bet_003",
            match_id="78_11111",
            bet_type="over_2_5",
            stake=75.0,
            odds=2.10,
            predicted_outcome="over_2_5",
            actual_outcome="over_2_5",
            profit_loss=82.5,
            roi=1.1,
            timestamp=datetime.now() - timedelta(days=3)
        )
    ]
    
    # Adicionar apostas
    for bet in test_bets:
        business_metrics.add_bet_result(bet)
    
    # Obter métricas
    metrics = business_metrics.get_business_metrics(30)
    print(f"Total de apostas: {metrics.total_bets}")
    print(f"Total apostado: R$ {metrics.total_stake:.2f}")
    print(f"Lucro/Prejuízo: R$ {metrics.total_profit_loss:.2f}")
    print(f"ROI: {metrics.total_roi:.2%}")
    print(f"Taxa de acerto: {metrics.win_rate:.2%}")
    
    # Análise de ROI
    roi_analysis = business_metrics.get_roi_analysis(30)
    print(f"\nAnálise de ROI:")
    for bet_type, analysis in roi_analysis['bet_type_analysis'].items():
        print(f"  {bet_type}: ROI {analysis['roi']:.2%}, Acerto {analysis['win_rate']:.2%}")
    
    print("\n🎉 TESTES DE MÉTRICAS CONCLUÍDOS!")
