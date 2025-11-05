#!/usr/bin/env python3
"""
Gestão de Risco Mínima Necessária
MaraBet AI - Parâmetros críticos de risco antes do deploy
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
class RiskLimits:
    """Limites de risco"""
    max_daily_loss: float = 0.05  # 5% do bankroll
    max_weekly_loss: float = 0.15  # 15% do bankroll
    max_position_size: float = 0.02  # 2% por aposta (Kelly fracionado)
    circuit_breaker_losses: int = 5  # Para após 5 perdas consecutivas
    min_edge_required: float = 0.05  # 5% de edge mínimo
    max_simultaneous_bets: int = 3  # Limitar exposição

@dataclass
class RiskMetrics:
    """Métricas de risco atuais"""
    current_drawdown: float
    daily_pnl: float
    weekly_pnl: float
    consecutive_losses: int
    active_bets: int
    current_edge: float
    risk_level: RiskLevel

class RiskManagement:
    """Gestão de risco mínima necessária"""
    
    def __init__(self, 
                 initial_bankroll: float = 10000,
                 limits: RiskLimits = None):
        """Inicializa gestão de risco"""
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.peak_bankroll = initial_bankroll
        
        # Limites de risco
        self.limits = limits or RiskLimits()
        
        # Estado atual
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.consecutive_losses = 0
        self.active_bets = 0
        self.trading_halted = False
        self.emergency_stop = False
        
        # Histórico de trades
        self.trade_history: List[Dict] = []
        self.daily_history: List[Dict] = []
        self.weekly_history: List[Dict] = []
        
        # Configurar logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para gestão de risco"""
        log_dir = "logs/risk_management"
        import os
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/risk_management_{datetime.now().strftime('%Y%m%d')}.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def calculate_position_size(self, 
                              win_prob: float, 
                              odds: float, 
                              edge: float = None) -> float:
        """Calcula tamanho da posição baseado em Kelly fracionado"""
        
        # Verificar se trading está habilitado
        if self.trading_halted or self.emergency_stop:
            return 0.0
        
        # Verificar edge mínimo
        if edge is None:
            edge = self._calculate_edge(win_prob, odds)
        
        if edge < self.limits.min_edge_required:
            logger.warning(f"Edge {edge:.2%} abaixo do mínimo {self.limits.min_edge_required:.2%}")
            return 0.0
        
        # Verificar limite de apostas simultâneas
        if self.active_bets >= self.limits.max_simultaneous_bets:
            logger.warning(f"Limite de apostas simultâneas atingido: {self.active_bets}")
            return 0.0
        
        # Kelly Criterion fracionado
        kelly_fraction = self._calculate_kelly_fraction(win_prob, odds)
        
        # Aplicar limite máximo de posição
        position_size = min(kelly_fraction, self.limits.max_position_size)
        
        # Ajustar baseado no estado de risco atual
        risk_multiplier = self._calculate_risk_multiplier()
        position_size *= risk_multiplier
        
        # Verificar se há capital suficiente
        max_position_value = position_size * self.current_bankroll
        if max_position_value > self.current_bankroll * 0.95:  # Deixar 5% de reserva
            max_position_value = self.current_bankroll * 0.95
            position_size = max_position_value / self.current_bankroll
        
        return max(0, position_size)
    
    def _calculate_edge(self, win_prob: float, odds: float) -> float:
        """Calcula edge da aposta"""
        if win_prob <= 0 or win_prob >= 1 or odds <= 1:
            return 0.0
        
        expected_value = (win_prob * odds) - 1
        return expected_value
    
    def _calculate_kelly_fraction(self, win_prob: float, odds: float) -> float:
        """Calcula fração Kelly"""
        if win_prob <= 0 or win_prob >= 1 or odds <= 1:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # onde b = odds - 1, p = win_prob, q = 1 - win_prob
        b = odds - 1
        p = win_prob
        q = 1 - win_prob
        
        kelly_fraction = (b * p - q) / b
        
        # Limitar Kelly fraction
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Máximo 25%
        
        return kelly_fraction
    
    def _calculate_risk_multiplier(self) -> float:
        """Calcula multiplicador de risco baseado no estado atual"""
        multiplier = 1.0
        
        # Reduzir tamanho se há muitas perdas consecutivas
        if self.consecutive_losses >= 3:
            multiplier *= 0.5
        elif self.consecutive_losses >= 2:
            multiplier *= 0.75
        
        # Reduzir tamanho se drawdown está alto
        current_drawdown = (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
        if current_drawdown > 0.10:  # 10%
            multiplier *= 0.5
        elif current_drawdown > 0.05:  # 5%
            multiplier *= 0.75
        
        # Reduzir tamanho se PnL diário está negativo
        if self.daily_pnl < -self.current_bankroll * 0.02:  # -2%
            multiplier *= 0.5
        
        return multiplier
    
    def validate_bet(self, 
                    win_prob: float, 
                    odds: float, 
                    stake: float) -> Tuple[bool, str]:
        """Valida se uma aposta pode ser feita"""
        
        # Verificar se trading está habilitado
        if self.trading_halted:
            return False, "Trading haltado"
        
        if self.emergency_stop:
            return False, "Parada de emergência ativa"
        
        # Verificar edge mínimo
        edge = self._calculate_edge(win_prob, odds)
        if edge < self.limits.min_edge_required:
            return False, f"Edge {edge:.2%} abaixo do mínimo {self.limits.min_edge_required:.2%}"
        
        # Verificar limite de apostas simultâneas
        if self.active_bets >= self.limits.max_simultaneous_bets:
            return False, f"Limite de apostas simultâneas atingido: {self.active_bets}"
        
        # Verificar tamanho da posição
        position_size = stake / self.current_bankroll
        if position_size > self.limits.max_position_size:
            return False, f"Posição {position_size:.2%} excede limite {self.limits.max_position_size:.2%}"
        
        # Verificar limites de perda
        if self.daily_pnl < -self.current_bankroll * self.limits.max_daily_loss:
            return False, f"Perda diária {abs(self.daily_pnl):.2f} excede limite {self.limits.max_daily_loss:.1%}"
        
        if self.weekly_pnl < -self.current_bankroll * self.limits.max_weekly_loss:
            return False, f"Perda semanal {abs(self.weekly_pnl):.2f} excede limite {self.limits.max_weekly_loss:.1%}"
        
        return True, "Aposta aprovada"
    
    def record_bet(self, 
                   bet_id: str,
                   win_prob: float, 
                   odds: float, 
                   stake: float,
                   prediction: str) -> bool:
        """Registra uma nova aposta"""
        
        # Validar aposta
        is_valid, message = self.validate_bet(win_prob, odds, stake)
        if not is_valid:
            logger.warning(f"Aposta rejeitada: {message}")
            return False
        
        # Registrar aposta
        bet_record = {
            'bet_id': bet_id,
            'timestamp': datetime.now(),
            'win_prob': win_prob,
            'odds': odds,
            'stake': stake,
            'prediction': prediction,
            'edge': self._calculate_edge(win_prob, odds),
            'position_size': stake / self.current_bankroll
        }
        
        self.trade_history.append(bet_record)
        self.active_bets += 1
        
        logger.info(f"Aposta registrada: {bet_id} - Stake: {stake:.2f} - Edge: {bet_record['edge']:.2%}")
        
        return True
    
    def record_bet_result(self, bet_id: str, result: str, pnl: float):
        """Registra resultado de uma aposta"""
        
        # Encontrar aposta no histórico
        bet_record = None
        for bet in self.trade_history:
            if bet['bet_id'] == bet_id:
                bet_record = bet
                break
        
        if not bet_record:
            logger.error(f"Aposta {bet_id} não encontrada")
            return
        
        # Atualizar resultado
        bet_record['result'] = result
        bet_record['pnl'] = pnl
        bet_record['settled_at'] = datetime.now()
        
        # Atualizar métricas
        self.current_bankroll += pnl
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        self.active_bets -= 1
        
        # Atualizar peak bankroll
        if self.current_bankroll > self.peak_bankroll:
            self.peak_bankroll = self.current_bankroll
            self.consecutive_losses = 0
        
        # Atualizar perdas consecutivas
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Verificar circuit breakers
        self._check_circuit_breakers()
        
        logger.info(f"Resultado registrado: {bet_id} - PnL: {pnl:.2f} - Bankroll: {self.current_bankroll:.2f}")
    
    def _check_circuit_breakers(self):
        """Verifica circuit breakers e toma ações"""
        
        # Circuit breaker: Perdas consecutivas
        if self.consecutive_losses >= self.limits.circuit_breaker_losses:
            self._trigger_circuit_breaker(
                ActionType.CIRCUIT_BREAKER,
                f"{self.consecutive_losses} perdas consecutivas excede limite de {self.limits.circuit_breaker_losses}"
            )
        
        # Circuit breaker: Perda diária
        elif self.daily_pnl < -self.current_bankroll * self.limits.max_daily_loss:
            self._trigger_circuit_breaker(
                ActionType.CIRCUIT_BREAKER,
                f"Perda diária {abs(self.daily_pnl):.2f} excede limite de {self.limits.max_daily_loss:.1%}"
            )
        
        # Circuit breaker: Perda semanal
        elif self.weekly_pnl < -self.current_bankroll * self.limits.max_weekly_loss:
            self._trigger_circuit_breaker(
                ActionType.CIRCUIT_BREAKER,
                f"Perda semanal {abs(self.weekly_pnl):.2f} excede limite de {self.limits.max_weekly_loss:.1%}"
            )
        
        # Stop loss: Drawdown significativo
        current_drawdown = (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
        if current_drawdown > 0.15:  # 15%
            self._trigger_stop_loss(f"Drawdown de {current_drawdown:.1%} ativa stop loss")
    
    def _trigger_circuit_breaker(self, action_type: ActionType, message: str):
        """Ativa circuit breaker"""
        self.trading_halted = True
        
        logger.critical(f"CIRCUIT BREAKER ATIVADO: {message}")
        
        # Notificar administradores
        self._notify_risk_alert(action_type, message)
    
    def _trigger_stop_loss(self, message: str):
        """Ativa stop loss"""
        logger.warning(f"STOP LOSS ATIVADO: {message}")
        
        # Notificar administradores
        self._notify_risk_alert(ActionType.STOP_LOSS, message)
    
    def _notify_risk_alert(self, action_type: ActionType, message: str):
        """Notifica alertas de risco"""
        # Implementar notificações (Telegram, Email, etc.)
        logger.critical(f"ALERTA DE RISCO: {action_type.value} - {message}")
    
    def reset_daily_metrics(self):
        """Reseta métricas diárias"""
        self.daily_pnl = 0.0
        logger.info("Métricas diárias resetadas")
    
    def reset_weekly_metrics(self):
        """Reseta métricas semanais"""
        self.weekly_pnl = 0.0
        logger.info("Métricas semanais resetadas")
    
    def resume_trading(self, reason: str = "Manual"):
        """Retoma trading após circuit breaker"""
        if self.trading_halted and not self.emergency_stop:
            self.trading_halted = False
            logger.info(f"Trading retomado: {reason}")
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Obtém métricas de risco atuais"""
        current_drawdown = (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
        
        # Calcular edge médio das apostas ativas
        active_bets = [bet for bet in self.trade_history if 'result' not in bet]
        current_edge = np.mean([bet['edge'] for bet in active_bets]) if active_bets else 0.0
        
        # Determinar nível de risco
        if current_drawdown > 0.15 or self.consecutive_losses >= 5:
            risk_level = RiskLevel.CRITICAL
        elif current_drawdown > 0.10 or self.consecutive_losses >= 3:
            risk_level = RiskLevel.HIGH
        elif current_drawdown > 0.05 or self.consecutive_losses >= 2:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return RiskMetrics(
            current_drawdown=current_drawdown,
            daily_pnl=self.daily_pnl,
            weekly_pnl=self.weekly_pnl,
            consecutive_losses=self.consecutive_losses,
            active_bets=self.active_bets,
            current_edge=current_edge,
            risk_level=risk_level
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
        elif metrics.risk_level == RiskLevel.CRITICAL:
            status = "🔴 CRÍTICO"
        elif metrics.risk_level == RiskLevel.HIGH:
            status = "🟠 ALTO RISCO"
        
        report.append(f"\nSTATUS DO SISTEMA: {status}")
        report.append(f"Trading Halted: {'Sim' if self.trading_halted else 'Não'}")
        report.append(f"Emergency Stop: {'Sim' if self.emergency_stop else 'Não'}")
        report.append(f"Nível de Risco: {metrics.risk_level.value.upper()}")
        
        # Bankroll
        report.append(f"\nBANKROLL:")
        report.append(f"  Bankroll Inicial: R$ {self.initial_bankroll:,.2f}")
        report.append(f"  Bankroll Atual: R$ {self.current_bankroll:,.2f}")
        report.append(f"  Peak Bankroll: R$ {self.peak_bankroll:,.2f}")
        report.append(f"  PnL Total: R$ {self.current_bankroll - self.initial_bankroll:,.2f}")
        
        # Métricas de risco
        report.append(f"\nMÉTRICAS DE RISCO:")
        report.append(f"  Drawdown Atual: {metrics.current_drawdown:.1%}")
        report.append(f"  PnL Diário: R$ {metrics.daily_pnl:,.2f}")
        report.append(f"  PnL Semanal: R$ {metrics.weekly_pnl:,.2f}")
        report.append(f"  Perdas Consecutivas: {metrics.consecutive_losses}")
        report.append(f"  Apostas Ativas: {metrics.active_bets}")
        report.append(f"  Edge Atual: {metrics.current_edge:.2%}")
        
        # Limites
        report.append(f"\nLIMITES CONFIGURADOS:")
        report.append(f"  Max Perda Diária: {self.limits.max_daily_loss:.1%}")
        report.append(f"  Max Perda Semanal: {self.limits.max_weekly_loss:.1%}")
        report.append(f"  Max Tamanho Posição: {self.limits.max_position_size:.1%}")
        report.append(f"  Circuit Breaker: {self.limits.circuit_breaker_losses} perdas")
        report.append(f"  Edge Mínimo: {self.limits.min_edge_required:.1%}")
        report.append(f"  Max Apostas Simultâneas: {self.limits.max_simultaneous_bets}")
        
        # Recomendações
        report.append(f"\nRECOMENDAÇÕES:")
        if metrics.risk_level == RiskLevel.CRITICAL:
            report.append(f"  🚨 RISCO CRÍTICO - Parar trading imediatamente")
        elif metrics.risk_level == RiskLevel.HIGH:
            report.append(f"  ⚠️ ALTO RISCO - Reduzir tamanho das posições")
        elif metrics.risk_level == RiskLevel.MEDIUM:
            report.append(f"  ⚠️ RISCO MÉDIO - Monitorar de perto")
        else:
            report.append(f"  ✅ RISCO BAIXO - Sistema operando normalmente")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Instância global
risk_management = RiskManagement()

if __name__ == "__main__":
    # Teste da gestão de risco mínima
    print("🧪 TESTANDO GESTÃO DE RISCO MÍNIMA")
    print("=" * 50)
    
    # Criar instância
    rm = RiskManagement(initial_bankroll=10000)
    
    # Testar validação de apostas
    print("Testando validação de apostas...")
    
    # Aposta válida
    is_valid, message = rm.validate_bet(0.6, 2.0, 100)
    print(f"Aposta válida: {is_valid} - {message}")
    
    # Aposta com edge baixo
    is_valid, message = rm.validate_bet(0.4, 2.0, 100)
    print(f"Aposta com edge baixo: {is_valid} - {message}")
    
    # Testar cálculo de posição
    position_size = rm.calculate_position_size(0.6, 2.0)
    print(f"Tamanho da posição: {position_size:.2%}")
    
    # Simular algumas apostas
    print("\nSimulando apostas...")
    rm.record_bet("bet_1", 0.6, 2.0, 200, "home_win")
    rm.record_bet("bet_2", 0.55, 2.2, 150, "away_win")
    
    # Simular resultados
    rm.record_bet_result("bet_1", "win", 200)
    rm.record_bet_result("bet_2", "loss", -150)
    
    # Gerar relatório
    report = rm.generate_risk_report()
    print(f"\n{report}")
    
    print("\n🎉 TESTE DE GESTÃO DE RISCO MÍNIMA CONCLUÍDO!")
