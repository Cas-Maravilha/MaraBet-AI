#!/usr/bin/env python3
"""
Sistema de Gestão de Risco Financeiro
MaraBet AI - Proteção contra perdas e gestão de capital
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(Enum):
    """Tipos de ação de risco"""
    STOP_LOSS = "stop_loss"
    CIRCUIT_BREAKER = "circuit_breaker"
    POSITION_REDUCTION = "position_reduction"
    TRADING_HALT = "trading_halt"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class RiskMetrics:
    """Métricas de risco"""
    current_drawdown: float
    max_drawdown: float
    consecutive_losses: int
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    var_95: float
    cvar_95: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float

@dataclass
class RiskAction:
    """Ação de gestão de risco"""
    action_type: ActionType
    risk_level: RiskLevel
    message: str
    parameters: Dict[str, Any]
    timestamp: datetime

class FinancialRiskManager:
    """Gerenciador de risco financeiro"""
    
    def __init__(self, 
                 initial_capital: float = 10000,
                 max_drawdown_limit: float = 0.20,  # 20%
                 daily_loss_limit: float = 0.05,    # 5%
                 consecutive_loss_limit: int = 5,
                 position_size_limit: float = 0.05,  # 5% do capital
                 var_limit: float = 0.03):           # 3% VaR
        """Inicializa gerenciador de risco"""
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_drawdown_limit = max_drawdown_limit
        self.daily_loss_limit = daily_loss_limit
        self.consecutive_loss_limit = consecutive_loss_limit
        self.position_size_limit = position_size_limit
        self.var_limit = var_limit
        
        # Estado do sistema
        self.trading_halted = False
        self.emergency_stop = False
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.monthly_pnl = 0.0
        self.peak_capital = initial_capital
        
        # Histórico de ações
        self.risk_actions: List[RiskAction] = []
        self.trade_history: List[Dict] = []
        
        # Configurações de Kelly Criterion
        self.kelly_enabled = True
        self.kelly_fraction = 0.25  # Usar 25% do Kelly optimal
        
        # Circuit breakers
        self.circuit_breakers = {
            'daily_loss': 0.05,      # 5% perda diária
            'weekly_loss': 0.15,     # 15% perda semanal
            'monthly_loss': 0.25,    # 25% perda mensal
            'consecutive_losses': 5, # 5 perdas consecutivas
            'drawdown': 0.20        # 20% drawdown
        }
    
    def calculate_kelly_size(self, win_prob: float, odds: float) -> float:
        """Calcula tamanho da posição usando Kelly Criterion"""
        if not self.kelly_enabled or win_prob <= 0 or win_prob >= 1 or odds <= 1:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # onde b = odds - 1, p = win_prob, q = 1 - win_prob
        b = odds - 1
        p = win_prob
        q = 1 - win_prob
        
        kelly_fraction = (b * p - q) / b
        
        # Limitar Kelly fraction
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Máximo 25%
        
        # Aplicar fração do Kelly
        position_size = kelly_fraction * self.kelly_fraction * self.current_capital
        
        # Limitar pelo limite de posição
        max_position = self.position_size_limit * self.current_capital
        position_size = min(position_size, max_position)
        
        return position_size
    
    def calculate_position_size(self, 
                              win_prob: float, 
                              odds: float, 
                              confidence: float = 1.0) -> float:
        """Calcula tamanho da posição considerando risco"""
        
        # Verificar se trading está habilitado
        if self.trading_halted or self.emergency_stop:
            return 0.0
        
        # Ajustar probabilidade pela confiança
        adjusted_prob = win_prob * confidence
        
        # Calcular Kelly size
        kelly_size = self.calculate_kelly_size(adjusted_prob, odds)
        
        # Aplicar ajustes de risco baseados no estado atual
        risk_multiplier = self._calculate_risk_multiplier()
        position_size = kelly_size * risk_multiplier
        
        # Verificar limites de posição
        max_position = self.position_size_limit * self.current_capital
        position_size = min(position_size, max_position)
        
        # Verificar se há capital suficiente
        if position_size > self.current_capital * 0.95:  # Deixar 5% de reserva
            position_size = self.current_capital * 0.95
        
        return max(0, position_size)
    
    def _calculate_risk_multiplier(self) -> float:
        """Calcula multiplicador de risco baseado no estado atual"""
        multiplier = 1.0
        
        # Reduzir tamanho se há muitas perdas consecutivas
        if self.consecutive_losses >= 3:
            multiplier *= 0.5
        elif self.consecutive_losses >= 2:
            multiplier *= 0.75
        
        # Reduzir tamanho se drawdown está alto
        current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        if current_drawdown > 0.15:
            multiplier *= 0.5
        elif current_drawdown > 0.10:
            multiplier *= 0.75
        
        # Reduzir tamanho se PnL diário está negativo
        if self.daily_pnl < -self.current_capital * 0.02:  # -2%
            multiplier *= 0.5
        
        return multiplier
    
    def update_trade_result(self, trade_result: Dict[str, Any]):
        """Atualiza resultado de uma trade"""
        pnl = trade_result.get('pnl', 0)
        is_winner = pnl > 0
        
        # Atualizar capital
        self.current_capital += pnl
        
        # Atualizar peak capital
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
            self.consecutive_losses = 0
        
        # Atualizar perdas consecutivas
        if not is_winner:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Atualizar PnL
        self.daily_pnl += pnl
        
        # Adicionar ao histórico
        trade_record = {
            'timestamp': datetime.now(),
            'pnl': pnl,
            'is_winner': is_winner,
            'capital_after': self.current_capital,
            'consecutive_losses': self.consecutive_losses
        }
        self.trade_history.append(trade_record)
        
        # Verificar circuit breakers
        self._check_circuit_breakers()
    
    def _check_circuit_breakers(self):
        """Verifica circuit breakers e toma ações"""
        current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        
        # Circuit breaker: Perda diária
        if self.daily_pnl < -self.current_capital * self.circuit_breakers['daily_loss']:
            self._trigger_circuit_breaker(
                ActionType.CIRCUIT_BREAKER,
                RiskLevel.HIGH,
                f"Perda diária de {abs(self.daily_pnl):.2f} excede limite de {self.circuit_breakers['daily_loss']:.1%}"
            )
        
        # Circuit breaker: Drawdown
        elif current_drawdown > self.circuit_breakers['drawdown']:
            self._trigger_circuit_breaker(
                ActionType.CIRCUIT_BREAKER,
                RiskLevel.CRITICAL,
                f"Drawdown de {current_drawdown:.1%} excede limite de {self.circuit_breakers['drawdown']:.1%}"
            )
        
        # Circuit breaker: Perdas consecutivas
        elif self.consecutive_losses >= self.circuit_breakers['consecutive_losses']:
            self._trigger_circuit_breaker(
                ActionType.CIRCUIT_BREAKER,
                RiskLevel.HIGH,
                f"{self.consecutive_losses} perdas consecutivas excede limite de {self.circuit_breakers['consecutive_losses']}"
            )
        
        # Stop loss: Perda significativa
        elif current_drawdown > 0.15:  # 15%
            self._trigger_stop_loss(
                f"Drawdown de {current_drawdown:.1%} ativa stop loss"
            )
    
    def _trigger_circuit_breaker(self, action_type: ActionType, risk_level: RiskLevel, message: str):
        """Ativa circuit breaker"""
        self.trading_halted = True
        
        action = RiskAction(
            action_type=action_type,
            risk_level=risk_level,
            message=message,
            parameters={'trading_halted': True},
            timestamp=datetime.now()
        )
        
        self.risk_actions.append(action)
        logger.critical(f"CIRCUIT BREAKER ATIVADO: {message}")
    
    def _trigger_stop_loss(self, message: str):
        """Ativa stop loss"""
        action = RiskAction(
            action_type=ActionType.STOP_LOSS,
            risk_level=RiskLevel.MEDIUM,
            message=message,
            parameters={'stop_loss_active': True},
            timestamp=datetime.now()
        )
        
        self.risk_actions.append(action)
        logger.warning(f"STOP LOSS ATIVADO: {message}")
    
    def reset_daily_metrics(self):
        """Reseta métricas diárias"""
        self.daily_pnl = 0.0
        logger.info("Métricas diárias resetadas")
    
    def reset_weekly_metrics(self):
        """Reseta métricas semanais"""
        self.weekly_pnl = 0.0
        logger.info("Métricas semanais resetadas")
    
    def reset_monthly_metrics(self):
        """Reseta métricas mensais"""
        self.monthly_pnl = 0.0
        logger.info("Métricas mensais resetadas")
    
    def resume_trading(self, reason: str = "Manual"):
        """Retoma trading após circuit breaker"""
        if self.trading_halted and not self.emergency_stop:
            self.trading_halted = False
            
            action = RiskAction(
                action_type=ActionType.TRADING_HALT,
                risk_level=RiskLevel.LOW,
                message=f"Trading retomado: {reason}",
                parameters={'trading_halted': False},
                timestamp=datetime.now()
            )
            
            self.risk_actions.append(action)
            logger.info(f"Trading retomado: {reason}")
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Obtém métricas de risco atuais"""
        current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        max_drawdown = max([(self.peak_capital - trade['capital_after']) / self.peak_capital 
                           for trade in self.trade_history]) if self.trade_history else 0
        
        # Calcular VaR e CVaR dos últimos 30 trades
        recent_trades = self.trade_history[-30:] if len(self.trade_history) >= 30 else self.trade_history
        if recent_trades:
            pnls = [trade['pnl'] for trade in recent_trades]
            var_95 = np.percentile(pnls, 5)
            cvar_95 = np.mean([p for p in pnls if p <= var_95])
            
            # Calcular Sharpe ratio
            if len(pnls) > 1:
                sharpe_ratio = np.mean(pnls) / np.std(pnls) if np.std(pnls) > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Calcular win rate
            win_rate = sum(1 for trade in recent_trades if trade['is_winner']) / len(recent_trades)
            
            # Calcular profit factor
            gross_profit = sum(trade['pnl'] for trade in recent_trades if trade['pnl'] > 0)
            gross_loss = abs(sum(trade['pnl'] for trade in recent_trades if trade['pnl'] < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        else:
            var_95 = 0
            cvar_95 = 0
            sharpe_ratio = 0
            win_rate = 0
            profit_factor = 0
        
        return RiskMetrics(
            current_drawdown=current_drawdown,
            max_drawdown=max_drawdown,
            consecutive_losses=self.consecutive_losses,
            daily_pnl=self.daily_pnl,
            weekly_pnl=self.weekly_pnl,
            monthly_pnl=self.monthly_pnl,
            var_95=var_95,
            cvar_95=cvar_95,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor
        )
    
    def generate_risk_report(self) -> str:
        """Gera relatório de risco"""
        metrics = self.get_risk_metrics()
        
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE GESTÃO DE RISCO - MARABET AI")
        report.append("=" * 60)
        
        # Status do sistema
        status = "🟢 NORMAL"
        if self.emergency_stop:
            status = "🔴 EMERGÊNCIA"
        elif self.trading_halted:
            status = "🟡 HALTED"
        elif metrics.current_drawdown > 0.10:
            status = "🟠 ALTO RISCO"
        
        report.append(f"\nSTATUS DO SISTEMA: {status}")
        report.append(f"Trading Halted: {'Sim' if self.trading_halted else 'Não'}")
        report.append(f"Emergency Stop: {'Sim' if self.emergency_stop else 'Não'}")
        
        # Capital
        report.append(f"\nCAPITAL:")
        report.append(f"  Capital Inicial: R$ {self.initial_capital:,.2f}")
        report.append(f"  Capital Atual: R$ {self.current_capital:,.2f}")
        report.append(f"  Peak Capital: R$ {self.peak_capital:,.2f}")
        report.append(f"  PnL Total: R$ {self.current_capital - self.initial_capital:,.2f}")
        
        # Métricas de risco
        report.append(f"\nMÉTRICAS DE RISCO:")
        report.append(f"  Drawdown Atual: {metrics.current_drawdown:.1%}")
        report.append(f"  Max Drawdown: {metrics.max_drawdown:.1%}")
        report.append(f"  Perdas Consecutivas: {metrics.consecutive_losses}")
        report.append(f"  PnL Diário: R$ {metrics.daily_pnl:,.2f}")
        report.append(f"  VaR 95%: R$ {metrics.var_95:,.2f}")
        report.append(f"  CVaR 95%: R$ {metrics.cvar_95:,.2f}")
        
        # Performance
        report.append(f"\nPERFORMANCE:")
        report.append(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        report.append(f"  Win Rate: {metrics.win_rate:.1%}")
        report.append(f"  Profit Factor: {metrics.profit_factor:.2f}")
        
        # Ações de risco recentes
        if self.risk_actions:
            report.append(f"\nAÇÕES DE RISCO RECENTES:")
            for action in self.risk_actions[-5:]:  # Últimas 5 ações
                report.append(f"  {action.timestamp.strftime('%H:%M:%S')} - {action.action_type.value}: {action.message}")
        
        # Recomendações
        report.append(f"\nRECOMENDAÇÕES:")
        if metrics.current_drawdown > 0.15:
            report.append(f"  🚨 Drawdown crítico - considerar parada")
        elif metrics.consecutive_losses >= 3:
            report.append(f"  ⚠️ Muitas perdas consecutivas - reduzir tamanho das posições")
        elif metrics.sharpe_ratio < 0.5:
            report.append(f"  ⚠️ Sharpe ratio baixo - revisar estratégia")
        else:
            report.append(f"  ✅ Sistema operando dentro dos parâmetros de risco")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Instância global
risk_manager = FinancialRiskManager()

if __name__ == "__main__":
    # Teste do sistema de gestão de risco
    print("🧪 TESTANDO SISTEMA DE GESTÃO DE RISCO")
    print("=" * 50)
    
    # Simular algumas trades
    trades = [
        {'pnl': 100, 'is_winner': True},
        {'pnl': -50, 'is_winner': False},
        {'pnl': 200, 'is_winner': True},
        {'pnl': -75, 'is_winner': False},
        {'pnl': -100, 'is_winner': False},
        {'pnl': -150, 'is_winner': False},
        {'pnl': -200, 'is_winner': False},
        {'pnl': -250, 'is_winner': False},
    ]
    
    for trade in trades:
        risk_manager.update_trade_result(trade)
        print(f"Trade: R$ {trade['pnl']:+.0f} | Capital: R$ {risk_manager.current_capital:,.0f}")
    
    # Gerar relatório
    report = risk_manager.generate_risk_report()
    print(f"\n{report}")
    
    print("\n🎉 TESTE DE GESTÃO DE RISCO CONCLUÍDO!")
