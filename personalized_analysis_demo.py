#!/usr/bin/env python3
"""
Demonstração de Análise Personalizada - MaraBet AI
Mostra o sistema completo de análise customizada baseada em perfil do usuário
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personalized_analysis import PersonalizedAnalysisGenerator
from datetime import datetime

def main():
    print("🎯 MARABET AI - ANÁLISE PERSONALIZADA")
    print("=" * 70)
    print("Demonstração do sistema completo de análise customizada")
    print("=" * 70)
    
    # Cria gerador de análise personalizada
    generator = PersonalizedAnalysisGenerator()
    
    print("\n🎯 GERANDO ANÁLISE PERSONALIZADA")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Cria perfil do usuário
    user_profile = generator.create_user_profile(
        name="João Silva",
        risk_profile="moderado",
        bankroll=1000.0,
        currency="BRL",
        experience_level="intermediario",
        preferred_leagues=["Premier League", "La Liga"],
        preferred_markets=["Over/Under 2.5", "Ambas Marcam"]
    )
    
    # Cria solicitação de análise
    match_request = generator.create_match_request(
        home_team="Manchester City",
        away_team="Arsenal",
        league="Premier League",
        match_date="2024-01-15",
        current_odds={
            "Over/Under 2.5": 1.65,
            "Ambas Marcam": 1.45,
            "Resultado": 2.10
        },
        user_profile=user_profile
    )
    
    # Gera análise personalizada
    analysis = generator.generate_personalized_analysis(match_request)
    
    # Formata análise
    report = generator.format_personalized_analysis(analysis)
    
    print("✅ Análise personalizada gerada!")
    print("\n" + "="*80)
    print("📊 ANÁLISE PERSONALIZADA COMPLETA")
    print("="*80)
    print(report)
    
    # Mostra métricas específicas
    print("\n📈 MÉTRICAS ESPECÍFICAS DA ANÁLISE")
    print("=" * 50)
    print(f"• Mercados Recomendados: {len([m for m in analysis.recommended_markets if m['recommended']])}")
    print(f"• Stake Total: {analysis.risk_assessment['total_stake_percent']:.2f}%")
    print(f"• Confiança Média: {analysis.risk_assessment['avg_confidence']:.1%}")
    print(f"• EV Médio: {analysis.risk_assessment['avg_expected_value']:.1%}")
    print(f"• Nível de Risco: {analysis.risk_assessment['risk_level']}")
    print(f"• Alertas: {len(analysis.warnings)}")
    print(f"• Oportunidades: {len(analysis.opportunities)}")
    
    # Mostra detalhes dos mercados
    print(f"\n🔍 DETALHES DOS MERCADOS")
    print("=" * 30)
    for i, market_data in enumerate(analysis.recommended_markets, 1):
        if market_data['recommended']:
            print(f"{i}. {market_data['market']}")
            print(f"   Odd: {market_data['odd']:.2f}")
            print(f"   Probabilidade: {market_data['probability']:.1%}")
            print(f"   EV: {market_data['expected_value']:.1%}")
            print(f"   Confiança: {market_data['confidence']:.1%}")
            print(f"   Dificuldade: {market_data['difficulty']}")
            print()
    
    return analysis

def show_personalized_features():
    """Mostra características da análise personalizada"""
    
    print("\n🔧 CARACTERÍSTICAS DA ANÁLISE PERSONALIZADA")
    print("=" * 50)
    print("""
✅ PERFIS DE RISCO
   • Conservador: Foco na preservação do capital
   • Moderado: Equilíbrio entre risco e retorno
   • Agressivo: Busca por retornos elevados

✅ COLETA DE DADOS ESPECÍFICOS
   • Times e Campeonato específicos
   • Odds atuais do mercado
   • Banca disponível
   • Perfil de risco personalizado

✅ CÁLCULO DE STAKE PERSONALIZADO
   • Kelly Criterion ajustado ao perfil
   • Limites de risco personalizados
   • Multiplicadores de confiança
   • Proteções de capital

✅ ANÁLISE POR LIGA
   • Premier League: Dificuldade alta, dados excelentes
   • La Liga: Dificuldade alta, volatilidade baixa
   • Serie A: Dificuldade média, dados bons
   • Bundesliga: Dificuldade média, volatilidade alta
   • Ligue 1: Dificuldade baixa, volatilidade alta
   • Champions League: Dificuldade muito alta, dados excelentes

✅ ANÁLISE POR MERCADO
   • Over/Under 2.5: Dificuldade baixa, dados excelentes
   • Ambas Marcam: Dificuldade média, volatilidade baixa
   • Resultado: Dificuldade alta, volatilidade alta
   • Over/Under 1.5: Dificuldade baixa, volatilidade baixa
   • Over/Under 3.5: Dificuldade média, volatilidade alta
""")

def demonstrate_risk_profiles():
    """Demonstra perfis de risco"""
    
    print("\n⚠️ DEMONSTRAÇÃO DOS PERFIS DE RISCO")
    print("=" * 50)
    
    print("PERFIS DE RISCO DISPONÍVEIS:")
    print("1. 🔴 CONSERVADOR")
    print("   • Max Stake: 2% da banca")
    print("   • Kelly Fraction: 1/8 (0.125)")
    print("   • Stop Loss: 10% da banca")
    print("   • Min Confiança: 80%")
    print("   • Min EV: 10%")
    print("   • Max Drawdown: 15%")
    print("   • Descrição: Foco na preservação do capital")
    print()
    
    print("2. 🟡 MODERADO")
    print("   • Max Stake: 5% da banca")
    print("   • Kelly Fraction: 1/4 (0.25)")
    print("   • Stop Loss: 20% da banca")
    print("   • Min Confiança: 70%")
    print("   • Min EV: 5%")
    print("   • Max Drawdown: 25%")
    print("   • Descrição: Equilíbrio entre risco e retorno")
    print()
    
    print("3. 🔴 AGRESSIVO")
    print("   • Max Stake: 10% da banca")
    print("   • Kelly Fraction: 1/2 (0.50)")
    print("   • Stop Loss: 30% da banca")
    print("   • Min Confiança: 60%")
    print("   • Min EV: 3%")
    print("   • Max Drawdown: 40%")
    print("   • Descrição: Busca por retornos elevados")
    print()

def demonstrate_league_analysis():
    """Demonstra análise por liga"""
    
    print("\n🏆 DEMONSTRAÇÃO DA ANÁLISE POR LIGA")
    print("=" * 50)
    
    print("LIGAS ANALISADAS:")
    print("1. 🏴󠁧󠁢󠁥󠁮󠁧󠁿 PREMIER LEAGUE")
    print("   • Dificuldade: Alta")
    print("   • Volatilidade: Média")
    print("   • Qualidade dos Dados: Excelente")
    print("   • Mercados Recomendados: Over/Under 2.5, Ambas Marcam, Resultado")
    print("   • Multiplicador de Confiança: 1.0")
    print()
    
    print("2. 🇪🇸 LA LIGA")
    print("   • Dificuldade: Alta")
    print("   • Volatilidade: Baixa")
    print("   • Qualidade dos Dados: Excelente")
    print("   • Mercados Recomendados: Over/Under 2.5, Ambas Marcam, Resultado")
    print("   • Multiplicador de Confiança: 1.0")
    print()
    
    print("3. 🇮🇹 SERIE A")
    print("   • Dificuldade: Média")
    print("   • Volatilidade: Média")
    print("   • Qualidade dos Dados: Boa")
    print("   • Mercados Recomendados: Over/Under 2.5, Ambas Marcam, Resultado")
    print("   • Multiplicador de Confiança: 0.95")
    print()
    
    print("4. 🇩🇪 BUNDESLIGA")
    print("   • Dificuldade: Média")
    print("   • Volatilidade: Alta")
    print("   • Qualidade dos Dados: Boa")
    print("   • Mercados Recomendados: Over/Under 2.5, Ambas Marcam, Resultado")
    print("   • Multiplicador de Confiança: 0.90")
    print()
    
    print("5. 🇫🇷 LIGUE 1")
    print("   • Dificuldade: Baixa")
    print("   • Volatilidade: Alta")
    print("   • Qualidade dos Dados: Média")
    print("   • Mercados Recomendados: Over/Under 2.5, Ambas Marcam, Resultado")
    print("   • Multiplicador de Confiança: 0.85")
    print()
    
    print("6. 🏆 CHAMPIONS LEAGUE")
    print("   • Dificuldade: Muito Alta")
    print("   • Volatilidade: Baixa")
    print("   • Qualidade dos Dados: Excelente")
    print("   • Mercados Recomendados: Over/Under 2.5, Ambas Marcam, Resultado")
    print("   • Multiplicador de Confiança: 1.1")
    print()

def demonstrate_market_analysis():
    """Demonstra análise por mercado"""
    
    print("\n🎯 DEMONSTRAÇÃO DA ANÁLISE POR MERCADO")
    print("=" * 50)
    
    print("MERCADOS ANALISADOS:")
    print("1. 📊 OVER/UNDER 2.5")
    print("   • Dificuldade: Baixa")
    print("   • Volatilidade: Média")
    print("   • Disponibilidade de Dados: Excelente")
    print("   • Recomendado para: Iniciante, Intermediário, Avançado")
    print("   • Multiplicador de Confiança: 1.0")
    print()
    
    print("2. ⚽ AMBAS MARCAM")
    print("   • Dificuldade: Média")
    print("   • Volatilidade: Baixa")
    print("   • Disponibilidade de Dados: Boa")
    print("   • Recomendado para: Intermediário, Avançado")
    print("   • Multiplicador de Confiança: 0.95")
    print()
    
    print("3. 🏆 RESULTADO")
    print("   • Dificuldade: Alta")
    print("   • Volatilidade: Alta")
    print("   • Disponibilidade de Dados: Excelente")
    print("   • Recomendado para: Avançado")
    print("   • Multiplicador de Confiança: 0.90")
    print()
    
    print("4. 📈 OVER/UNDER 1.5")
    print("   • Dificuldade: Baixa")
    print("   • Volatilidade: Baixa")
    print("   • Disponibilidade de Dados: Excelente")
    print("   • Recomendado para: Iniciante, Intermediário")
    print("   • Multiplicador de Confiança: 1.05")
    print()
    
    print("5. 📊 OVER/UNDER 3.5")
    print("   • Dificuldade: Média")
    print("   • Volatilidade: Alta")
    print("   • Disponibilidade de Dados: Boa")
    print("   • Recomendado para: Intermediário, Avançado")
    print("   • Multiplicador de Confiança: 0.90")
    print()

def demonstrate_stake_calculation():
    """Demonstra cálculo de stake"""
    
    print("\n💰 DEMONSTRAÇÃO DO CÁLCULO DE STAKE")
    print("=" * 50)
    
    print("FÓRMULAS DE CÁLCULO:")
    print("1. Kelly Criterion Base")
    print("   Stake = (Kelly Fraction × EV × Bankroll) / (Odd - 1)")
    print("   Exemplo: (0.25 × 0.08 × 1000) / (1.65 - 1) = R$ 30.77")
    print()
    
    print("2. Ajuste por Perfil de Risco")
    print("   Stake = Base Stake × Risk Profile Multiplier")
    print("   Exemplo: R$ 30.77 × 0.8 = R$ 24.62")
    print()
    
    print("3. Limite Máximo")
    print("   Max Stake = Bankroll × Max Stake Percent")
    print("   Exemplo: 1000 × 0.05 = R$ 50.00")
    print()
    
    print("4. Limite Mínimo")
    print("   Min Stake = Bankroll × 0.001")
    print("   Exemplo: 1000 × 0.001 = R$ 1.00")
    print()
    
    print("5. Ajuste por Confiança")
    print("   Confidence Multiplier = min(Confidence / 0.8, 1.0)")
    print("   Exemplo: min(0.85 / 0.8, 1.0) = 1.0")
    print()

def demonstrate_user_input():
    """Demonstra entrada de dados do usuário"""
    
    print("\n📝 DEMONSTRAÇÃO DA ENTRADA DE DADOS")
    print("=" * 50)
    
    print("DADOS NECESSÁRIOS PARA ANÁLISE PERSONALIZADA:")
    print("1. 👤 INFORMAÇÕES PESSOAIS")
    print("   • Nome do usuário")
    print("   • Perfil de risco (conservador/moderado/agressivo)")
    print("   • Banca disponível")
    print("   • Moeda preferida")
    print("   • Nível de experiência")
    print()
    
    print("2. ⚽ INFORMAÇÕES DA PARTIDA")
    print("   • Time da casa")
    print("   • Time visitante")
    print("   • Campeonato/Liga")
    print("   • Data da partida")
    print("   • Odds atuais do mercado")
    print()
    
    print("3. 🎯 PREFERÊNCIAS")
    print("   • Ligas preferidas")
    print("   • Mercados preferidos")
    print("   • Horários preferidos")
    print("   • Tipos de análise")
    print()
    
    print("4. ⚙️ CONFIGURAÇÕES AVANÇADAS")
    print("   • Limite máximo de stake")
    print("   • Percentual de stop loss")
    print("   • ROI alvo")
    print("   • Tolerância ao risco")
    print()

def show_analysis_workflow():
    """Mostra fluxo de análise"""
    
    print("\n🔄 FLUXO DE ANÁLISE PERSONALIZADA")
    print("=" * 50)
    print("""
1. 📝 COLETA DE DADOS
   • Informações pessoais do usuário
   • Dados da partida específica
   • Odds atuais do mercado
   • Preferências e configurações

2. 🔍 ANÁLISE DE MERCADOS
   • Avaliação de cada mercado disponível
   • Cálculo de probabilidades
   • Cálculo de valores esperados
   • Aplicação de multiplicadores de liga

3. 💰 CÁLCULO DE STAKE
   • Aplicação do Kelly Criterion
   • Ajuste por perfil de risco
   • Aplicação de limites de segurança
   • Ajuste por nível de confiança

4. ⚠️ AVALIAÇÃO DE RISCO
   • Cálculo de métricas de risco
   • Determinação do nível de risco
   • Geração de alertas
   • Identificação de oportunidades

5. 📊 RELATÓRIO PERSONALIZADO
   • Mercados recomendados
   • Recomendações de stake
   • Avaliação de risco
   • Alertas e oportunidades
""")

if __name__ == "__main__":
    # Mostra características
    show_personalized_features()
    
    # Demonstra perfis de risco
    demonstrate_risk_profiles()
    
    # Demonstra análise por liga
    demonstrate_league_analysis()
    
    # Demonstra análise por mercado
    demonstrate_market_analysis()
    
    # Demonstra cálculo de stake
    demonstrate_stake_calculation()
    
    # Demonstra entrada de dados
    demonstrate_user_input()
    
    # Mostra fluxo de análise
    show_analysis_workflow()
    
    # Gera análise personalizada completa
    analysis = main()
    
    if analysis:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de análise personalizada implementado")
        print("✅ Coleta de dados específicos do usuário")
        print("✅ Cálculo de stake personalizado")
        print("✅ Perfis de risco")
        print("✅ Interface de entrada de dados")
        print("✅ Análise por liga e mercado")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python personalized_analysis_demo.py")
        print("from personalized_analysis import PersonalizedAnalysisGenerator")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Análise personalizada por perfil")
        print("• Cálculo de stake otimizado")
        print("• Perfis de risco adaptativos")
        print("• Análise por liga e mercado")
        print("• Interface de entrada intuitiva")
        print("• Relatórios customizados")
        print("• Proteções de capital")
        print("• Oportunidades identificadas")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
