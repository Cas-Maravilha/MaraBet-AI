#!/usr/bin/env python3
"""
Demonstração de Plano de Ação - MaraBet AI
Mostra o sistema completo de checklist pré-aposta e condições de entrada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from action_plan import ActionPlanGenerator
from datetime import datetime

def main():
    print("🎯 MARABET AI - PLANO DE AÇÃO")
    print("=" * 70)
    print("Demonstração do sistema completo de checklist pré-aposta")
    print("=" * 70)
    
    # Cria gerador de plano de ação
    generator = ActionPlanGenerator()
    
    print("\n🎯 GERANDO PLANO DE AÇÃO")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
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
    
    print("✅ Plano de ação gerado!")
    print("\n" + "="*80)
    print("📊 PLANO DE AÇÃO COMPLETO")
    print("="*80)
    print(report)
    
    # Mostra métricas específicas
    print("\n📈 MÉTRICAS ESPECÍFICAS DO PLANO")
    print("=" * 50)
    print(f"• Nível de Risco: {action_plan.risk_level}")
    print(f"• Prioridade de Execução: {action_plan.execution_priority}")
    print(f"• Itens do Checklist: {len(action_plan.pre_bet_checklist)}")
    print(f"• Condições de Entrada: {len(action_plan.entry_conditions)}")
    print(f"• Situações para Evitar: {len(action_plan.avoid_situations)}")
    
    # Mostra detalhes do checklist
    print(f"\n🔍 DETALHES DO CHECKLIST")
    print("=" * 30)
    for i, item in enumerate(action_plan.pre_bet_checklist, 1):
        print(f"{i}. {item.item}")
        print(f"   Status: {item.status}")
        print(f"   Prioridade: {item.priority}")
        print(f"   Crítico: {'Sim' if item.critical else 'Não'}")
        print()
    
    return action_plan

def show_action_plan_features():
    """Mostra características do plano de ação"""
    
    print("\n🔧 CARACTERÍSTICAS DO PLANO DE AÇÃO")
    print("=" * 50)
    print("""
✅ CHECKLIST PRÉ-APOSTA
   • Confirmação de odds disponíveis
   • Verificação de notícias de última hora
   • Confirmação de escalações oficiais
   • Verificação de condições climáticas
   • Cálculo de stake baseado na banca
   • Definição de estratégia de cash out

✅ CONDIÇÕES PARA ENTRADA
   • Odd mínima aceitável (≥1.60)
   • Confiança mínima (≥70%)
   • EV mínimo (≥+5%)
   • Estabilidade das escalações (≥90%)

✅ SITUAÇÕES PARA EVITAR
   • Jogadores-chave fora da escalação
   • Condições climáticas adversas
   • Queda significativa das odds
   • Múltiplas lesões de última hora

✅ ANÁLISE DE RISCO
   • Níveis: BAIXO, MÉDIO, ALTO
   • Cores: 🟢, 🟡, 🔴
   • Ações: APOSTAR, AVALIAR, EVITAR
   • Prioridades de execução automáticas
""")

def demonstrate_checklist_system():
    """Demonstra sistema de checklist"""
    
    print("\n🧮 DEMONSTRAÇÃO DO SISTEMA DE CHECKLIST")
    print("=" * 50)
    
    # Dados do exemplo
    print("Dados do Exemplo:")
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print()
    
    print("CHECKLIST PRÉ-APOSTA:")
    print("1. 🔴 Confirmar odds ainda disponíveis (≥1.62)")
    print("   Status: ✅ CONFIRMADO")
    print("   Prioridade: CRÍTICA")
    print("   Verificação: 30 minutos antes da partida")
    print()
    
    print("2. 🔴 Verificar notícias de última hora (1h antes)")
    print("   Status: ✅ VERIFICADO")
    print("   Prioridade: CRÍTICA")
    print("   Verificação: 1 hora antes da partida")
    print()
    
    print("3. 🔴 Confirmar escalações oficiais")
    print("   Status: ✅ CONFIRMADO")
    print("   Prioridade: CRÍTICA")
    print("   Verificação: 1 hora antes da partida")
    print()
    
    print("4. 🟡 Verificar condições climáticas atualizadas")
    print("   Status: ✅ FAVORÁVEL")
    print("   Prioridade: MÉDIA")
    print("   Verificação: 2 horas antes da partida")
    print()
    
    print("5. 🔴 Calcular stake de acordo com sua banca atual")
    print("   Status: ✅ CALCULADO")
    print("   Prioridade: CRÍTICA")
    print("   Verificação: Antes de cada aposta")
    print()
    
    print("6. 🟢 Definir estratégia de cash out (se aplicável)")
    print("   Status: ✅ DEFINIDA")
    print("   Prioridade: BAIXA")
    print("   Verificação: Antes de cada aposta")
    print()

def demonstrate_entry_conditions():
    """Demonstra condições de entrada"""
    
    print("\n📌 DEMONSTRAÇÃO DAS CONDIÇÕES DE ENTRADA")
    print("=" * 50)
    
    print("CONDIÇÕES PARA ENTRADA:")
    print("1. ✅ Odd mínima aceitável: 1.60")
    print("   Valor Atual: 1.65")
    print("   Status: ✅ ATENDIDA")
    print("   Descrição: Odd deve ser pelo menos 1.60 para compensar o risco")
    print()
    
    print("2. ✅ Confiança mínima: 70%")
    print("   Valor Atual: 75%")
    print("   Status: ✅ ATENDIDA")
    print("   Descrição: Confiança deve ser pelo menos 70% para justificar a aposta")
    print()
    
    print("3. ✅ EV mínimo: +5%")
    print("   Valor Atual: +8%")
    print("   Status: ✅ ATENDIDA")
    print("   Descrição: Valor esperado deve ser pelo menos +5% para ser lucrativo")
    print()
    
    print("4. ✅ Sem mudanças significativas nas escalações: 90%")
    print("   Valor Atual: 95%")
    print("   Status: ✅ ATENDIDA")
    print("   Descrição: Escalações devem estar estáveis sem mudanças importantes")
    print()

def demonstrate_avoid_situations():
    """Demonstra situações para evitar"""
    
    print("\n⛔ DEMONSTRAÇÃO DAS SITUAÇÕES PARA EVITAR")
    print("=" * 50)
    
    print("SITUAÇÕES PARA EVITAR A APOSTA:")
    print("1. 🔴 Haaland ou Saka fora da escalação")
    print("   Status: ✅ OK")
    print("   Impacto: ALTO")
    print("   Prevenção: Verificar escalações oficiais 1h antes")
    print("   Descrição: Jogadores-chave ausentes podem mudar completamente o jogo")
    print()
    
    print("2. 🟡 Chuva forte prevista")
    print("   Status: ✅ OK")
    print("   Impacto: MÉDIO")
    print("   Prevenção: Verificar previsão do tempo 2h antes")
    print("   Descrição: Condições climáticas adversas podem afetar o estilo de jogo")
    print()
    
    print("3. 🔴 Odd cair abaixo de 1.60")
    print("   Status: ✅ OK")
    print("   Impacto: ALTO")
    print("   Prevenção: Monitorar odds constantemente")
    print("   Descrição: Queda da odd indica mudança no mercado ou informações")
    print()
    
    print("4. 🔴 Notícia de múltiplas lesões de última hora")
    print("   Status: ✅ OK")
    print("   Impacto: ALTO")
    print("   Prevenção: Acompanhar notícias de última hora")
    print("   Descrição: Múltiplas lesões podem alterar drasticamente o equilíbrio")
    print()

def demonstrate_risk_analysis():
    """Demonstra análise de risco"""
    
    print("\n🎯 DEMONSTRAÇÃO DA ANÁLISE DE RISCO")
    print("=" * 50)
    
    print("NÍVEIS DE RISCO:")
    print("🟢 BAIXO - Todas as condições atendidas, baixo risco")
    print("   Ação: APOSTAR")
    print("   Execução: EXECUTAR IMEDIATAMENTE")
    print()
    
    print("🟡 MÉDIO - Algumas condições em alerta, risco moderado")
    print("   Ação: AVALIAR CUIDADOSAMENTE")
    print("   Execução: AVALIAR ANTES DE EXECUTAR")
    print()
    
    print("🔴 ALTO - Muitas condições não atendidas, alto risco")
    print("   Ação: EVITAR APOSTA")
    print("   Execução: NÃO EXECUTAR")
    print()
    
    print("CÁLCULO DO RISCO:")
    print("• Itens Críticos: 6")
    print("• Itens Críticos Falhados: 0")
    print("• Taxa de Falha: 0%")
    print("• Nível de Risco: BAIXO 🟢")
    print("• Ação Recomendada: APOSTAR")
    print()

def show_priority_system():
    """Mostra sistema de prioridades"""
    
    print("\n📊 SISTEMA DE PRIORIDADES")
    print("=" * 30)
    print("""
PRIORIDADES DO CHECKLIST:
────────────────────────────────────────────────────
🔴 CRÍTICA - Itens essenciais para a aposta
   • Confirmação de odds
   • Verificação de notícias
   • Confirmação de escalações
   • Cálculo de stake

🟡 ALTA - Itens importantes para a qualidade
   • Verificação de notícias de última hora
   • Cálculo de stake

🟢 MÉDIA - Itens relevantes mas não críticos
   • Verificação de condições climáticas

🟢 BAIXA - Itens opcionais
   • Estratégia de cash out

SISTEMA DE CORES:
────────────────────────────────────────────────────
🔴 Vermelho: Crítico ou Falhou
🟡 Amarelo: Atenção ou Alta Prioridade
🟢 Verde: OK ou Baixa Prioridade
✅ Verde com Check: Sucesso
❌ Vermelho com X: Falha
⚠️ Amarelo com Exclamação: Atenção
""")

if __name__ == "__main__":
    # Mostra características
    show_action_plan_features()
    
    # Demonstra sistema de checklist
    demonstrate_checklist_system()
    
    # Demonstra condições de entrada
    demonstrate_entry_conditions()
    
    # Demonstra situações para evitar
    demonstrate_avoid_situations()
    
    # Demonstra análise de risco
    demonstrate_risk_analysis()
    
    # Mostra sistema de prioridades
    show_priority_system()
    
    # Gera plano de ação completo
    action_plan = main()
    
    if action_plan:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de plano de ação implementado")
        print("✅ Checklist pré-aposta completo")
        print("✅ Condições de entrada definidas")
        print("✅ Situações para evitar identificadas")
        print("✅ Análise de risco automatizada")
        print("✅ Sistema de prioridades implementado")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python action_plan_demo.py")
        print("from action_plan import ActionPlanGenerator")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Checklist pré-aposta completo")
        print("• Condições de entrada claras")
        print("• Situações para evitar identificadas")
        print("• Análise de risco automatizada")
        print("• Sistema de prioridades")
        print("• Formatação profissional")
        print("• Ações recomendadas")
        print("• Verificação em tempo real")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
