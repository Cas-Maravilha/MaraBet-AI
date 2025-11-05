#!/usr/bin/env python3
"""
Demonstração dos Modelos Preditivos Avançados - MaraBet AI
Mostra todos os algoritmos de modelagem preditiva implementados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from predictive_models import (
    PoissonModel, MLEnsemble, AdvancedLogisticRegression, 
    BayesianNeuralNetworkWrapper, PredictiveModelEnsemble
)
from predictive_integration import AdvancedPredictiveSystem
import pandas as pd
import numpy as np

def main():
    print("🤖 MARABET AI - MODELOS PREDITIVOS AVANÇADOS")
    print("=" * 60)
    print("ETAPA 2: MODELAGEM PREDITIVA")
    print("=" * 60)
    
    # Cria dados simulados para demonstração
    print("\n📊 PREPARANDO DADOS DE DEMONSTRAÇÃO")
    print("-" * 40)
    
    np.random.seed(42)
    n_matches = 200
    
    # Dados de partidas
    matches_data = pd.DataFrame({
        'home_team': [f'Team_{i%20}' for i in range(n_matches)],
        'away_team': [f'Team_{(i+10)%20}' for i in range(n_matches)],
        'home_goals': np.random.poisson(1.5, n_matches),
        'away_goals': np.random.poisson(1.2, n_matches),
        'date': [f'2024-01-{i%30+1:02d}' for i in range(n_matches)]
    })
    
    # Features simuladas
    X = pd.DataFrame(np.random.randn(n_matches, 25))
    feature_columns = [f'feature_{i}' for i in range(25)]
    X.columns = feature_columns
    
    # Target (resultado da partida)
    y = np.random.choice([0, 1, 2], n_matches)
    
    print(f"   Partidas: {len(matches_data)}")
    print(f"   Features: {len(feature_columns)}")
    print(f"   Classes: {len(np.unique(y))}")
    
    print("\n🎯 MODELO 1: POISSON (Para esportes com pontuação)")
    print("-" * 50)
    
    # Testa modelo Poisson
    poisson_model = PoissonModel()
    poisson_model.fit(matches_data)
    
    # Simula dados de times para predição
    home_team_stats = {
        'recent_form': {'form': 'good'},
        'historical_stats': {'goals_scored': 1.8, 'goals_conceded': 1.2}
    }
    away_team_stats = {
        'recent_form': {'form': 'average'},
        'historical_stats': {'goals_scored': 1.5, 'goals_conceded': 1.4}
    }
    
    poisson_pred = poisson_model.predict('Team_A', 'Team_B', home_team_stats, away_team_stats)
    
    print(f"   Predição: {poisson_pred['predicted_result']}")
    print(f"   Confiança: {poisson_pred['confidence']:.3f}")
    print(f"   Gols esperados: {poisson_pred['expected_goals']['home']:.2f} vs {poisson_pred['expected_goals']['away']:.2f}")
    print(f"   Probabilidades:")
    for outcome, prob in poisson_pred['probabilities'].items():
        print(f"     {outcome}: {prob:.3f}")
    
    print("\n🌲 MODELO 2: MACHINE LEARNING ENSEMBLE")
    print("-" * 50)
    print("   (Random Forest + XGBoost + LightGBM + CatBoost)")
    
    # Testa ML Ensemble
    ml_ensemble = MLEnsemble()
    ml_ensemble.fit(X, y, feature_columns)
    
    # Testa predição
    test_X = X.iloc[:1]
    ml_pred = ml_ensemble.predict(test_X)
    
    print(f"   Predição: {ml_pred['predicted_result']}")
    print(f"   Confiança: {ml_pred['confidence']:.3f}")
    print(f"   Modelos treinados: {len(ml_ensemble.models)}")
    print(f"   Contribuições dos modelos:")
    for model_name, contrib in ml_pred['model_contributions'].items():
        print(f"     {model_name}: {contrib['confidence']:.3f}")
    
    print("\n📈 MODELO 3: REGRESSÃO LOGÍSTICA AVANÇADA")
    print("-" * 50)
    
    # Testa Regressão Logística
    lr_model = AdvancedLogisticRegression()
    lr_model.fit(X, y, feature_columns)
    
    lr_pred = lr_model.predict(test_X)
    
    print(f"   Predição: {lr_pred['predicted_result']}")
    print(f"   Confiança: {lr_pred['confidence']:.3f}")
    print(f"   Features mais importantes:")
    top_features = sorted(lr_pred['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:5]
    for feature, importance in top_features:
        print(f"     {feature}: {importance:.3f}")
    
    print("\n🧠 MODELO 4: REDE NEURAL BAYESIANA")
    print("-" * 50)
    print("   (Para modelar incertezas)")
    
    # Testa Rede Neural Bayesiana
    try:
        bnn_model = BayesianNeuralNetworkWrapper(len(feature_columns))
        bnn_model.fit(X, y, feature_columns, epochs=30)
        
        bnn_pred = bnn_model.predict(test_X, feature_columns, n_samples=50)
        
        print(f"   Predição: {bnn_pred['predicted_result']}")
        print(f"   Confiança: {bnn_pred['confidence']:.3f}")
        print(f"   Incerteza: {bnn_pred['uncertainty']:.3f}")
        print(f"   Breakdown de incerteza:")
        for outcome, uncertainty in bnn_pred['uncertainty_breakdown'].items():
            print(f"     {outcome}: {uncertainty:.3f}")
        
    except Exception as e:
        print(f"   Rede Neural Bayesiana não disponível: {e}")
        print("   (Requer PyTorch instalado)")
    
    print("\n🎭 ENSEMBLE COMPLETO DE MODELOS")
    print("-" * 50)
    
    # Testa ensemble completo
    ensemble = PredictiveModelEnsemble()
    ensemble.fit(matches_data, X, y, feature_columns)
    
    ensemble_pred = ensemble.predict('Team_A', 'Team_B', home_team_stats, away_team_stats, test_X, feature_columns)
    
    print(f"   Predição Final: {ensemble_pred['predicted_result']}")
    print(f"   Confiança: {ensemble_pred['confidence']:.3f}")
    print(f"   Incerteza: {ensemble_pred['uncertainty']:.3f}")
    print(f"   Modelos utilizados: {len(ensemble_pred['individual_predictions'])}")
    print(f"   Peso dos modelos:")
    for model, weight in ensemble_pred['model_weights'].items():
        print(f"     {model}: {weight:.2f}")
    
    print("\n🔬 SISTEMA PREDITIVO AVANÇADO INTEGRADO")
    print("-" * 50)
    
    # Testa sistema integrado
    system = AdvancedPredictiveSystem()
    
    # Converte dados para formato do sistema
    historical_matches = []
    for i in range(50):
        match = {
            'id': f'match_{i}',
            'home_team': f'Team_{i%10}',
            'away_team': f'Team_{(i+5)%10}',
            'date': f'2024-01-{i%30+1:02d}',
            'result': ['win', 'draw', 'loss'][y[i]],
            'home_goals': matches_data.iloc[i]['home_goals'],
            'away_goals': matches_data.iloc[i]['away_goals']
        }
        historical_matches.append(match)
    
    # Treina sistema
    training_result = system.train_advanced_models(historical_matches)
    
    if training_result['success']:
        print(f"   Treinamento: Sucesso")
        print(f"   Amostras: {training_result['training_samples']}")
        print(f"   Features: {len(training_result['features_used'])}")
        print(f"   Modelos: {len(training_result['models_trained'])}")
        
        # Testa predição avançada
        advanced_pred = system.predict_advanced('Team_A', 'Team_B', '2024-01-15')
        
        if advanced_pred:
            print(f"\n   📊 ANÁLISE AVANÇADA:")
            print(f"   Predição: {advanced_pred['prediction']['predicted_result']}")
            print(f"   Confiança: {advanced_pred['prediction']['confidence']:.3f}")
            print(f"   Incerteza: {advanced_pred['uncertainty_analysis']['overall_uncertainty']:.3f}")
            print(f"   Nível de confiança: {advanced_pred['uncertainty_analysis']['confidence_level']}")
            print(f"   Concordância de modelos: {advanced_pred['uncertainty_analysis']['model_agreement']:.3f}")
            print(f"   Estabilidade: {advanced_pred['uncertainty_analysis']['prediction_stability']}")
            
            print(f"\n   💰 RECOMENDAÇÕES DE APOSTAS:")
            recommendations = advanced_pred['recommendations']['recommendations']
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec['outcome']}: {rec['recommendation']} (EV: {rec['expected_value']:.1%})")
            
            print(f"\n   ⚠️ ANÁLISE DE RISCO:")
            risk = advanced_pred['risk_analysis']
            print(f"   Nível: {risk['risk_level']}")
            print(f"   Score: {risk['risk_score']}/{risk['max_risk_score']}")
            print(f"   Recomendação: {risk['recommendation']}")
            
            print(f"\n   💡 INSIGHTS DOS MODELOS:")
            insights = advanced_pred['model_insights']['insights']
            for insight in insights[:3]:
                print(f"   • {insight}")
        
        # Testa backtesting avançado
        print(f"\n   📈 BACKTESTING AVANÇADO:")
        backtest_result = system.run_advanced_backtesting(historical_matches, 1000)
        
        if backtest_result['success']:
            metrics = backtest_result['metrics']
            print(f"   Trades: {metrics['total_trades']}")
            print(f"   ROI: {metrics['roi']:.2f}%")
            print(f"   Taxa de acerto: {metrics['win_rate']:.1%}")
            print(f"   Incerteza média: {metrics['avg_uncertainty']:.3f}")
            print(f"   ROI ajustado: {metrics['uncertainty_adjusted_roi']:.2f}%")
        else:
            print(f"   Falha no backtesting: {backtest_result['error']}")
    
    else:
        print(f"   Falha no treinamento: {training_result['error']}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO DOS MODELOS PREDITIVOS CONCLUÍDA!")
    print("=" * 60)
    
    print(f"\n📋 RESUMO DOS ALGORITMOS IMPLEMENTADOS:")
    print(f"   ✅ Modelo Poisson - Para esportes com pontuação")
    print(f"   ✅ ML Ensemble - Random Forest + XGBoost + LightGBM + CatBoost")
    print(f"   ✅ Regressão Logística Avançada - Com validação cruzada")
    print(f"   ✅ Rede Neural Bayesiana - Para modelar incertezas")
    print(f"   ✅ Ensemble Completo - Combinação de todos os modelos")
    print(f"   ✅ Sistema Integrado - Análise completa com framework")
    
    print(f"\n🚀 COMO USAR:")
    print(f"   python main.py --mode advanced")
    print(f"   python predictive_demo.py")
    print(f"   python main.py --web")
    
    print(f"\n🔧 PRÓXIMOS PASSOS:")
    print(f"   • Integração com APIs reais de dados")
    print(f"   • Otimização de hiperparâmetros")
    print(f"   • Deploy em produção")
    print(f"   • Monitoramento de performance")

if __name__ == "__main__":
    main()
