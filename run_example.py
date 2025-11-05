#!/usr/bin/env python3
"""
Exemplo de execução do MaraBet AI
Este arquivo demonstra como usar o sistema de análise preditiva
"""

from main import MaraBetAI
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=== MARABET AI - EXEMPLO DE EXECUÇÃO ===")
    print("Sistema de Análise Preditiva de Apostas Esportivas")
    print("=" * 50)
    
    # Inicializa o sistema
    marabet = MaraBetAI()
    
    print("\n1. Coletando dados esportivos...")
    matches = marabet.collect_data('all', 7)
    print(f"   ✓ Coletados {len(matches)} jogos")
    
    print("\n2. Treinando modelos de machine learning...")
    success = marabet.train_models(matches)
    if success:
        print("   ✓ Modelos treinados com sucesso")
    else:
        print("   ✗ Erro no treinamento")
        return
    
    print("\n3. Analisando partidas...")
    predictions = marabet.analyze_matches(matches)
    print(f"   ✓ {len(predictions)} partidas analisadas")
    
    # Mostra exemplo de análise
    if predictions:
        print("\n4. Exemplo de análise:")
        example = predictions[0]
        analysis = example['analysis']
        match = example['match']
        
        print(f"   Partida: {match['home_team']} vs {match['away_team']}")
        print(f"   Data: {match['date']}")
        print(f"   Predição: {analysis['predicted_result']}")
        print(f"   Probabilidades:")
        print(f"     - Casa: {analysis['probabilities']['home_win']:.1%}")
        print(f"     - Empate: {analysis['probabilities']['draw']:.1%}")
        print(f"     - Fora: {analysis['probabilities']['away_win']:.1%}")
        print(f"   Odds de Mercado:")
        print(f"     - Casa: {analysis['market_odds']['home']:.2f}")
        print(f"     - Empate: {analysis['market_odds']['draw']:.2f}")
        print(f"     - Fora: {analysis['market_odds']['away']:.2f}")
        
        print(f"\n   Recomendações:")
        for rec in analysis['recommendations']:
            status = "✓ APOSTAR" if rec['recommendation'] == 'BET' else "✗ EVITAR"
            print(f"     - {rec['outcome'].upper()}: {status} (EV: {rec['expected_value']:.1%})")
    
    print("\n5. Executando backtesting...")
    results = marabet.run_backtesting(matches, 1000)
    if results:
        print(f"   ✓ Backtesting concluído")
        print(f"   - Total de trades: {results['total_trades']}")
        print(f"   - ROI: {results['metrics']['roi']:.2f}%")
        print(f"   - Taxa de acerto: {results['metrics']['win_rate']:.1%}")
        print(f"   - Drawdown máximo: {results['metrics']['max_drawdown']:.2f}%")
    
    print("\n=== EXECUÇÃO CONCLUÍDA ===")
    print("\nPara iniciar a interface web, execute:")
    print("python main.py --web")
    print("\nPara mais opções, execute:")
    print("python main.py --help")

if __name__ == "__main__":
    main()
