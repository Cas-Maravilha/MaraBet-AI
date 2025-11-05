#!/usr/bin/env python3
"""
Script para testar o sistema completo de Machine Learning
MaraBet AI - Sistema de Apostas Esportivas Inteligentes
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml.predictive_models import SportsPredictor, PoissonPredictor, create_sample_data
from ml.simple_feature_engineering import SimpleFeatureEngineer
from ml.model_ensemble import ModelEnsemble
from ml.model_training import ModelTrainer, create_sample_data as create_training_data

def test_feature_engineering():
    """Testa o sistema de feature engineering"""
    print("🔧 TESTANDO FEATURE ENGINEERING")
    print("=" * 50)
    
    # Criar dados de exemplo
    df = create_sample_data()
    print(f"📊 Dados originais: {len(df.columns)} colunas")
    
    # Criar features
    engineer = SimpleFeatureEngineer()
    features_df = engineer.create_all_features(df)
    
    print(f"✅ Dados com features: {len(features_df.columns)} colunas")
    print(f"📈 Features criadas: {len(features_df.columns) - len(df.columns)}")
    
    # Mostrar algumas features
    print("\n🔍 Exemplos de features criadas:")
    new_features = [col for col in features_df.columns if col not in df.columns]
    for feature in new_features[:10]:
        print(f"  - {feature}")
    
    return features_df

def test_predictive_models():
    """Testa os modelos preditivos"""
    print("\n🔮 TESTANDO MODELOS PREDITIVOS")
    print("=" * 50)
    
    # Criar dados
    df = create_sample_data()
    
    # Testar SportsPredictor
    print("🤖 Testando SportsPredictor...")
    predictor = SportsPredictor()
    
    # Preparar dados
    X, y, feature_names = predictor.prepare_training_data(df)
    
    # Treinar modelos
    predictor.train_models(X, y, feature_names)
    
    # Mostrar performance
    print("\n📊 Performance dos Modelos:")
    for name, perf in predictor.get_model_performance().items():
        print(f"  {name}: {perf['accuracy']:.4f}")
    
    # Testar predição
    print("\n🔮 Testando predição...")
    sample_X = X[:1]
    prediction = predictor.predict(sample_X)
    print(f"Predição: {prediction['prediction']}")
    print(f"Confiança: {prediction['confidence']:.4f}")
    
    # Testar PoissonPredictor
    print("\n📊 Testando PoissonPredictor...")
    poisson_predictor = PoissonPredictor()
    poisson_predictor.train(df)
    
    # Predição de exemplo
    sample_prediction = poisson_predictor.predict(1, 2)
    print(f"Probabilidade Vitória Casa: {sample_prediction['home_win_prob']:.4f}")
    print(f"Probabilidade Empate: {sample_prediction['draw_prob']:.4f}")
    print(f"Probabilidade Vitória Fora: {sample_prediction['away_win_prob']:.4f}")
    
    return predictor, poisson_predictor

def test_model_ensemble():
    """Testa o sistema de ensemble"""
    print("\n🤖 TESTANDO MODEL ENSEMBLE")
    print("=" * 50)
    
    # Criar dados
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, n_informative=10, random_state=42)
    
    print(f"📊 Dados: {X.shape[0]} amostras, {X.shape[1]} features")
    
    # Criar ensemble
    ensemble = ModelEnsemble()
    
    # Adicionar modelos
    ensemble.add_model('rf', RandomForestClassifier(n_estimators=100, random_state=42))
    ensemble.add_model('gb', GradientBoostingClassifier(n_estimators=100, random_state=42))
    ensemble.add_model('lr', LogisticRegression(random_state=42, max_iter=1000))
    
    # Treinar ensemble
    ensemble.train_ensemble(X, y)
    
    # Avaliar performance
    performance = ensemble.evaluate_ensemble(X, y)
    print(f"📊 Performance: {performance['accuracy']:.4f}")
    
    # Testar predição
    sample_X = X[:1]
    prediction = ensemble.predict(sample_X)
    print(f"🔮 Predição: {prediction['prediction']}")
    print(f"🎯 Confiança: {prediction['confidence']:.4f}")
    print(f"🤝 Acordo: {prediction['agreement']:.4f}")
    
    return ensemble

def test_model_training():
    """Testa o sistema de treinamento"""
    print("\n🚀 TESTANDO MODEL TRAINING")
    print("=" * 50)
    
    # Criar dados
    df = create_training_data()
    print(f"📊 Dados criados: {len(df)} partidas")
    
    # Criar trainer
    trainer = ModelTrainer()
    
    # Preparar dados
    X, y, feature_names = trainer.prepare_data(df)
    
    # Treinar todos os modelos
    trainer.train_all_models(X, y, feature_names)
    
    # Mostrar resumo
    print("\n📊 Resumo da Performance:")
    summary = trainer.get_model_performance_summary()
    print(summary.to_string(index=False))
    
    # Encontrar melhor modelo
    best_model = trainer.find_best_model()
    print(f"\n🏆 Melhor modelo: {best_model}")
    
    return trainer

def test_integration():
    """Testa integração completa do sistema"""
    print("\n🔗 TESTANDO INTEGRAÇÃO COMPLETA")
    print("=" * 50)
    
    # Criar dados
    df = create_sample_data()
    
    # Feature Engineering
    engineer = SimpleFeatureEngineer()
    features_df = engineer.create_all_features(df)
    
    # Preparar dados para ML
    trainer = ModelTrainer()
    X, y, feature_names = trainer.prepare_data(features_df)
    
    # Treinar modelos
    trainer.train_all_models(X, y, feature_names)
    
    # Criar ensemble
    ensemble = ModelEnsemble()
    for name, model in trainer.models.items():
        ensemble.add_model(name, model)
    
    # Treinar ensemble
    ensemble.train_ensemble(X, y)
    
    # Testar predição completa
    sample_X = X[:1]
    prediction = ensemble.predict(sample_X)
    
    print("🎯 Predição Integrada:")
    print(f"  Predição: {prediction['prediction']}")
    print(f"  Confiança: {prediction['confidence']:.4f}")
    print(f"  Acordo: {prediction['agreement']:.4f}")
    
    # Mostrar predições individuais
    print("\n📊 Predições Individuais:")
    for name, pred in prediction['individual_predictions'].items():
        print(f"  {name}: {pred}")
    
    return ensemble

def main():
    """Função principal"""
    print("🤖 MARABET AI - TESTE COMPLETO DO SISTEMA ML")
    print("=" * 70)
    
    try:
        # Teste 1: Feature Engineering
        features_df = test_feature_engineering()
        
        # Teste 2: Modelos Preditivos
        predictor, poisson_predictor = test_predictive_models()
        
        # Teste 3: Model Ensemble
        ensemble = test_model_ensemble()
        
        # Teste 4: Model Training
        trainer = test_model_training()
        
        # Teste 5: Integração Completa
        final_ensemble = test_integration()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 70)
        print("✅ Feature Engineering: OK")
        print("✅ Modelos Preditivos: OK")
        print("✅ Model Ensemble: OK")
        print("✅ Model Training: OK")
        print("✅ Integração Completa: OK")
        
        print("\n🚀 SISTEMA DE ML TOTALMENTE FUNCIONAL!")
        print("📊 Recursos disponíveis:")
        print("  - Feature Engineering avançado")
        print("  - Múltiplos algoritmos de ML")
        print("  - Sistema de ensemble")
        print("  - Validação temporal")
        print("  - Integração completa")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
