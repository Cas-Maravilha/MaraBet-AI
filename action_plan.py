"""
Plano de Ação - MaraBet AI
Sistema especializado para checklist pré-aposta, condições de entrada e situações para evitar
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PreBetChecklistItem:
    """Item do checklist pré-aposta"""
    item: str
    status: str
    priority: str
    description: str
    verification_time: str
    critical: bool

@dataclass
class EntryCondition:
    """Condição para entrada"""
    condition: str
    threshold: float
    current_value: float
    status: str
    description: str
    critical: bool

@dataclass
class AvoidSituation:
    """Situação para evitar"""
    situation: str
    description: str
    impact: str
    prevention: str
    critical: bool

@dataclass
class ActionPlan:
    """Plano de ação completo"""
    home_team: str
    away_team: str
    match_date: str
    recommendation: str
    pre_bet_checklist: List[PreBetChecklistItem]
    entry_conditions: List[EntryCondition]
    avoid_situations: List[AvoidSituation]
    risk_level: str
    execution_priority: str
    last_updated: datetime

class ActionPlanGenerator:
    """
    Gerador de Plano de Ação
    Sistema completo para checklist pré-aposta e condições de entrada
    """
    
    def __init__(self):
        self.checklist_templates = self._load_checklist_templates()
        self.entry_conditions = self._load_entry_conditions()
        self.avoid_situations = self._load_avoid_situations()
        self.risk_levels = self._load_risk_levels()
        
    def _load_checklist_templates(self) -> Dict[str, Dict]:
        """Carrega templates do checklist"""
        return {
            'odds_verification': {
                'item': 'Confirmar odds ainda disponíveis (≥1.62)',
                'priority': 'CRÍTICA',
                'description': 'Verificar se a odd ainda está disponível e dentro do range aceitável',
                'verification_time': '30 minutos antes da partida',
                'critical': True
            },
            'last_minute_news': {
                'item': 'Verificar notícias de última hora (1h antes)',
                'priority': 'ALTA',
                'description': 'Checar lesões, escalações e mudanças táticas de última hora',
                'verification_time': '1 hora antes da partida',
                'critical': True
            },
            'official_lineups': {
                'item': 'Confirmar escalações oficiais',
                'priority': 'CRÍTICA',
                'description': 'Verificar se os jogadores-chave estão na escalação',
                'verification_time': '1 hora antes da partida',
                'critical': True
            },
            'weather_conditions': {
                'item': 'Verificar condições climáticas atualizadas',
                'priority': 'MÉDIA',
                'description': 'Checar se há mudanças no clima que possam afetar o jogo',
                'verification_time': '2 horas antes da partida',
                'critical': False
            },
            'stake_calculation': {
                'item': 'Calcular stake de acordo com sua banca atual',
                'priority': 'ALTA',
                'description': 'Aplicar critério de Kelly fracionado baseado na banca atual',
                'verification_time': 'Antes de cada aposta',
                'critical': True
            },
            'cashout_strategy': {
                'item': 'Definir estratégia de cash out (se aplicável)',
                'priority': 'BAIXA',
                'description': 'Estabelecer pontos de cash out para proteger lucros',
                'verification_time': 'Antes de cada aposta',
                'critical': False
            }
        }
    
    def _load_entry_conditions(self) -> Dict[str, Dict]:
        """Carrega condições de entrada"""
        return {
            'minimum_odd': {
                'condition': 'Odd mínima aceitável',
                'threshold': 1.60,
                'description': 'Odd deve ser pelo menos 1.60 para compensar o risco',
                'critical': True
            },
            'minimum_confidence': {
                'condition': 'Confiança mínima',
                'threshold': 0.70,
                'description': 'Confiança deve ser pelo menos 70% para justificar a aposta',
                'critical': True
            },
            'minimum_ev': {
                'condition': 'EV mínimo',
                'threshold': 0.05,
                'description': 'Valor esperado deve ser pelo menos +5% para ser lucrativo',
                'critical': True
            },
            'lineup_stability': {
                'condition': 'Sem mudanças significativas nas escalações',
                'threshold': 0.90,
                'description': 'Escalações devem estar estáveis sem mudanças importantes',
                'critical': True
            }
        }
    
    def _load_avoid_situations(self) -> Dict[str, Dict]:
        """Carrega situações para evitar"""
        return {
            'key_player_out': {
                'situation': 'Haaland ou Saka fora da escalação',
                'description': 'Jogadores-chave ausentes podem mudar completamente o jogo',
                'impact': 'ALTO',
                'prevention': 'Verificar escalações oficiais 1h antes',
                'critical': True
            },
            'heavy_rain': {
                'situation': 'Chuva forte prevista',
                'description': 'Condições climáticas adversas podem afetar o estilo de jogo',
                'impact': 'MÉDIO',
                'prevention': 'Verificar previsão do tempo 2h antes',
                'critical': False
            },
            'odd_drop': {
                'situation': 'Odd cair abaixo de 1.60',
                'description': 'Queda da odd indica mudança no mercado ou informações',
                'impact': 'ALTO',
                'prevention': 'Monitorar odds constantemente',
                'critical': True
            },
            'multiple_injuries': {
                'situation': 'Notícia de múltiplas lesões de última hora',
                'description': 'Múltiplas lesões podem alterar drasticamente o equilíbrio',
                'impact': 'ALTO',
                'prevention': 'Acompanhar notícias de última hora',
                'critical': True
            }
        }
    
    def _load_risk_levels(self) -> Dict[str, Dict]:
        """Carrega níveis de risco"""
        return {
            'BAIXO': {
                'description': 'Todas as condições atendidas, baixo risco',
                'color': '🟢',
                'action': 'APOSTAR'
            },
            'MÉDIO': {
                'description': 'Algumas condições em alerta, risco moderado',
                'color': '🟡',
                'action': 'AVALIAR CUIDADOSAMENTE'
            },
            'ALTO': {
                'description': 'Muitas condições não atendidas, alto risco',
                'color': '🔴',
                'action': 'EVITAR APOSTA'
            }
        }
    
    def generate_pre_bet_checklist(self, home_team: str, away_team: str, 
                                 match_data: Dict) -> List[PreBetChecklistItem]:
        """Gera checklist pré-aposta"""
        
        checklist = []
        
        for key, template in self.checklist_templates.items():
            # Simula status baseado em dados da partida
            if key == 'odds_verification':
                current_odd = match_data.get('current_odd', 1.65)
                status = "✅ CONFIRMADO" if current_odd >= 1.62 else "❌ FORA DO RANGE"
            elif key == 'last_minute_news':
                news_impact = match_data.get('news_impact', 'low')
                status = "✅ VERIFICADO" if news_impact == 'low' else "⚠️ ATENÇÃO NECESSÁRIA"
            elif key == 'official_lineups':
                lineup_stable = match_data.get('lineup_stable', True)
                status = "✅ CONFIRMADO" if lineup_stable else "❌ MUDANÇAS DETECTADAS"
            elif key == 'weather_conditions':
                weather_ok = match_data.get('weather_ok', True)
                status = "✅ FAVORÁVEL" if weather_ok else "⚠️ CONDIÇÕES ADVERSAS"
            elif key == 'stake_calculation':
                bankroll_ok = match_data.get('bankroll_ok', True)
                status = "✅ CALCULADO" if bankroll_ok else "❌ REVISAR CÁLCULO"
            else:  # cashout_strategy
                strategy_set = match_data.get('cashout_strategy_set', True)
                status = "✅ DEFINIDA" if strategy_set else "⚠️ PENDENTE"
            
            checklist.append(PreBetChecklistItem(
                item=template['item'],
                status=status,
                priority=template['priority'],
                description=template['description'],
                verification_time=template['verification_time'],
                critical=template['critical']
            ))
        
        return checklist
    
    def generate_entry_conditions(self, home_team: str, away_team: str, 
                                match_data: Dict) -> List[EntryCondition]:
        """Gera condições de entrada"""
        
        conditions = []
        
        for key, template in self.entry_conditions.items():
            # Simula valores atuais baseados em dados da partida
            if key == 'minimum_odd':
                current_value = match_data.get('current_odd', 1.65)
                status = "✅ ATENDIDA" if current_value >= template['threshold'] else "❌ NÃO ATENDIDA"
            elif key == 'minimum_confidence':
                current_value = match_data.get('confidence', 0.75)
                status = "✅ ATENDIDA" if current_value >= template['threshold'] else "❌ NÃO ATENDIDA"
            elif key == 'minimum_ev':
                current_value = match_data.get('expected_value', 0.08)
                status = "✅ ATENDIDA" if current_value >= template['threshold'] else "❌ NÃO ATENDIDA"
            else:  # lineup_stability
                current_value = match_data.get('lineup_stability', 0.95)
                status = "✅ ATENDIDA" if current_value >= template['threshold'] else "❌ NÃO ATENDIDA"
            
            conditions.append(EntryCondition(
                condition=template['condition'],
                threshold=template['threshold'],
                current_value=current_value,
                status=status,
                description=template['description'],
                critical=template['critical']
            ))
        
        return conditions
    
    def generate_avoid_situations(self, home_team: str, away_team: str, 
                                match_data: Dict) -> List[AvoidSituation]:
        """Gera situações para evitar"""
        
        situations = []
        
        for key, template in self.avoid_situations.items():
            # Simula status baseado em dados da partida
            if key == 'key_player_out':
                haaland_out = match_data.get('haaland_out', False)
                saka_out = match_data.get('saka_out', False)
                status = "⚠️ ATENÇÃO" if (haaland_out or saka_out) else "✅ OK"
            elif key == 'heavy_rain':
                heavy_rain = match_data.get('heavy_rain', False)
                status = "⚠️ ATENÇÃO" if heavy_rain else "✅ OK"
            elif key == 'odd_drop':
                odd_dropped = match_data.get('odd_dropped', False)
                status = "⚠️ ATENÇÃO" if odd_dropped else "✅ OK"
            else:  # multiple_injuries
                multiple_injuries = match_data.get('multiple_injuries', False)
                status = "⚠️ ATENÇÃO" if multiple_injuries else "✅ OK"
            
            situations.append(AvoidSituation(
                situation=template['situation'],
                description=template['description'],
                impact=template['impact'],
                prevention=template['prevention'],
                critical=template['critical']
            ))
        
        return situations
    
    def calculate_risk_level(self, checklist: List[PreBetChecklistItem], 
                           conditions: List[EntryCondition], 
                           situations: List[AvoidSituation]) -> str:
        """Calcula nível de risco"""
        
        # Conta itens críticos não atendidos
        critical_failed = 0
        total_critical = 0
        
        # Checklist crítico
        for item in checklist:
            if item.critical:
                total_critical += 1
                if "❌" in item.status or "⚠️" in item.status:
                    critical_failed += 1
        
        # Condições críticas
        for condition in conditions:
            if condition.critical:
                total_critical += 1
                if "❌" in condition.status:
                    critical_failed += 1
        
        # Situações críticas
        for situation in situations:
            if situation.critical:
                total_critical += 1
                if "⚠️" in situation.situation:  # Assumindo que situações ativas têm ⚠️
                    critical_failed += 1
        
        # Calcula nível de risco
        if total_critical == 0:
            return "BAIXO"
        
        failure_rate = critical_failed / total_critical
        
        if failure_rate <= 0.2:
            return "BAIXO"
        elif failure_rate <= 0.5:
            return "MÉDIO"
        else:
            return "ALTO"
    
    def determine_execution_priority(self, risk_level: str, 
                                   conditions: List[EntryCondition]) -> str:
        """Determina prioridade de execução"""
        
        if risk_level == "BAIXO":
            return "EXECUTAR IMEDIATAMENTE"
        elif risk_level == "MÉDIO":
            return "AVALIAR ANTES DE EXECUTAR"
        else:
            return "NÃO EXECUTAR"
    
    def generate_action_plan(self, home_team: str, away_team: str, 
                           match_date: str, recommendation: str, 
                           match_data: Dict) -> ActionPlan:
        """Gera plano de ação completo"""
        
        logger.info(f"Gerando plano de ação: {home_team} vs {away_team}")
        
        try:
            # Gera componentes do plano
            checklist = self.generate_pre_bet_checklist(home_team, away_team, match_data)
            conditions = self.generate_entry_conditions(home_team, away_team, match_data)
            situations = self.generate_avoid_situations(home_team, away_team, match_data)
            
            # Calcula nível de risco
            risk_level = self.calculate_risk_level(checklist, conditions, situations)
            
            # Determina prioridade de execução
            execution_priority = self.determine_execution_priority(risk_level, conditions)
            
            return ActionPlan(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                recommendation=recommendation,
                pre_bet_checklist=checklist,
                entry_conditions=conditions,
                avoid_situations=situations,
                risk_level=risk_level,
                execution_priority=execution_priority,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração do plano de ação: {e}")
            return self._create_empty_action_plan(home_team, away_team, match_date)
    
    def _create_empty_action_plan(self, home_team: str, away_team: str, 
                                match_date: str) -> ActionPlan:
        """Cria plano de ação vazio em caso de erro"""
        return ActionPlan(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            recommendation="N/A",
            pre_bet_checklist=[],
            entry_conditions=[],
            avoid_situations=[],
            risk_level="ALTO",
            execution_priority="NÃO EXECUTAR",
            last_updated=datetime.now()
        )
    
    def format_action_plan(self, action_plan: ActionPlan) -> str:
        """Formata plano de ação"""
        
        if not action_plan or not action_plan.pre_bet_checklist:
            return "Plano de ação não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("PLANO DE AÇÃO")
        report_parts.append("=" * 60)
        report_parts.append(f"Partida: {action_plan.home_team} vs {action_plan.away_team}")
        report_parts.append(f"Data: {action_plan.match_date}")
        report_parts.append(f"Recomendação: {action_plan.recommendation}")
        report_parts.append("")
        
        # Checklist pré-aposta
        report_parts.append("✅ CHECKLIST PRÉ-APOSTA")
        report_parts.append("")
        
        for item in action_plan.pre_bet_checklist:
            priority_icon = "🔴" if item.priority == "CRÍTICA" else "🟡" if item.priority == "ALTA" else "🟢"
            report_parts.append(f"{priority_icon} {item.item}")
            report_parts.append(f"   Status: {item.status}")
            report_parts.append(f"   Prioridade: {item.priority}")
            report_parts.append(f"   Verificação: {item.verification_time}")
            report_parts.append(f"   Descrição: {item.description}")
            report_parts.append("")
        
        # Condições para entrada
        report_parts.append("📌 CONDIÇÕES PARA ENTRADA")
        report_parts.append("")
        
        for condition in action_plan.entry_conditions:
            status_icon = "✅" if "✅" in condition.status else "❌"
            report_parts.append(f"{status_icon} {condition.condition}: {condition.threshold}")
            report_parts.append(f"   Valor Atual: {condition.current_value:.2f}")
            report_parts.append(f"   Status: {condition.status}")
            report_parts.append(f"   Descrição: {condition.description}")
            report_parts.append("")
        
        # Situações para evitar
        report_parts.append("⛔ SITUAÇÕES PARA EVITAR A APOSTA")
        report_parts.append("")
        
        for situation in action_plan.avoid_situations:
            critical_icon = "🔴" if situation.critical else "🟡"
            report_parts.append(f"{critical_icon} {situation.situation}")
            report_parts.append(f"   Descrição: {situation.description}")
            report_parts.append(f"   Impacto: {situation.impact}")
            report_parts.append(f"   Prevenção: {situation.prevention}")
            report_parts.append("")
        
        # Resumo de risco
        risk_config = self.risk_levels[action_plan.risk_level]
        report_parts.append("🎯 RESUMO DE RISCO")
        report_parts.append("-" * 40)
        report_parts.append(f"Nível de Risco: {action_plan.risk_level} {risk_config['color']}")
        report_parts.append(f"Descrição: {risk_config['description']}")
        report_parts.append(f"Ação Recomendada: {risk_config['action']}")
        report_parts.append(f"Prioridade de Execução: {action_plan.execution_priority}")
        report_parts.append("")
        
        # Timestamp
        report_parts.append("📅 Última Atualização")
        report_parts.append("-" * 40)
        report_parts.append(f"Data/Hora: {action_plan.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return "\n".join(report_parts)

if __name__ == "__main__":
    # Teste do gerador de plano de ação
    generator = ActionPlanGenerator()
    
    print("=== TESTE DO GERADOR DE PLANO DE AÇÃO ===")
    
    # Dados de exemplo
    match_data = {
        'current_odd': 1.65,
        'news_impact': 'low',
        'lineup_stable': True,
        'weather_ok': True,
        'bankroll_ok': True,
        'cashout_strategy_set': True,
        'confidence': 0.75,
        'expected_value': 0.08,
        'lineup_stability': 0.95,
        'haaland_out': False,
        'saka_out': False,
        'heavy_rain': False,
        'odd_dropped': False,
        'multiple_injuries': False
    }
    
    # Gera plano de ação
    action_plan = generator.generate_action_plan(
        "Manchester City", "Arsenal", "2024-01-15", 
        "OVER 2.5 GOLS", match_data
    )
    
    # Formata plano de ação
    report = generator.format_action_plan(action_plan)
    
    print(report)
    
    print("\nTeste concluído!")
