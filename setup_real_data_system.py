#!/usr/bin/env python3
"""
Script de Configuração do Sistema de Dados Reais
MaraBet AI - Configuração e teste do sistema completo
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Verifica configuração do ambiente"""
    logger.info("Verificando configuração do ambiente...")
    
    # Verificar arquivo .env
    env_file = Path('.env')
    if not env_file.exists():
        logger.error("❌ Arquivo .env não encontrado")
        return False
    
    # Verificar API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('API_FOOTBALL_KEY')
    if not api_key or api_key == 'your-api-key-here':
        logger.error("❌ API_FOOTBALL_KEY não configurada no .env")
        return False
    
    logger.info("✅ Ambiente configurado corretamente")
    return True

def test_api_connection():
    """Testa conexão com API-Football"""
    logger.info("Testando conexão com API-Football...")
    
    try:
        from api.real_football_api import initialize_real_football_api
        
        api_key = os.getenv('API_FOOTBALL_KEY')
        api = initialize_real_football_api(api_key)
        
        if api.test_api_connection():
            logger.info("✅ Conexão com API-Football funcionando")
            return True
        else:
            logger.error("❌ Falha na conexão com API-Football")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar API: {e}")
        return False

def collect_historical_data():
    """Coleta dados históricos"""
    logger.info("Iniciando coleta de dados históricos...")
    
    try:
        from data_collection.historical_data_collector import initialize_historical_collector
        
        api_key = os.getenv('API_FOOTBALL_KEY')
        collector = initialize_historical_collector(api_key)
        
        # Configurar para coleta limitada (teste)
        collector.config.leagues = [39, 140]  # Premier League e La Liga
        collector.config.seasons = [2023, 2024]  # Últimas 2 temporadas
        
        logger.info("Coletando dados históricos (pode demorar alguns minutos)...")
        results = collector.collect_all_historical_data()
        
        logger.info(f"✅ Coleta concluída:")
        logger.info(f"  Partidas: {results['matches']}")
        logger.info(f"  Estatísticas: {results['stats']}")
        logger.info(f"  Odds: {results['odds']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta de dados históricos: {e}")
        return False

def train_models():
    """Treina modelos com dados reais"""
    logger.info("Iniciando treinamento de modelos...")
    
    try:
        from ml.real_data_training import RealDataTrainer
        
        trainer = RealDataTrainer()
        
        # Carregar dados
        logger.info("Carregando dados do banco...")
        df = trainer.load_data_from_database()
        
        if len(df) == 0:
            logger.error("❌ Nenhum dado encontrado no banco de dados")
            return False
        
        logger.info(f"Carregados {len(df)} registros")
        
        # Criar features
        logger.info("Criando features...")
        df_features = trainer.create_features(df)
        
        # Preparar dados de treinamento
        logger.info("Preparando dados de treinamento...")
        X, y, feature_columns = trainer.prepare_training_data(df_features)
        
        # Treinar modelos
        logger.info("Treinando modelos...")
        results = trainer.train_models(X, y)
        
        # Criar ensemble
        logger.info("Criando ensemble...")
        ensemble = trainer.create_ensemble_model(X, y)
        
        # Salvar modelos
        logger.info("Salvando modelos...")
        trainer.save_models()
        
        # Gerar relatório
        report = trainer.generate_training_report(results)
        logger.info(f"\n{report}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no treinamento de modelos: {e}")
        return False

def test_continuous_collection():
    """Testa coleta contínua"""
    logger.info("Testando coleta contínua...")
    
    try:
        from data_collection.continuous_data_collector import initialize_continuous_collector
        
        api_key = os.getenv('API_FOOTBALL_KEY')
        collector = initialize_continuous_collector(api_key)
        
        # Executar coleta inicial
        logger.info("Executando coleta inicial...")
        collector._run_initial_collection()
        
        # Obter status
        status = collector.get_collection_status()
        logger.info(f"✅ Coleta contínua testada:")
        logger.info(f"  Coleções Habilitadas: {status['enabled_collections']}")
        logger.info(f"  Intervalo de Coleta: {status['collection_interval']}s")
        
        for table, count in status['record_counts'].items():
            logger.info(f"  {table}: {count} registros")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta contínua: {e}")
        return False

def run_validation_tests():
    """Executa testes de validação"""
    logger.info("Executando testes de validação...")
    
    try:
        from validation.rigorous_backtesting import rigorous_backtester
        from validation.walk_forward_analysis import walk_forward_analyzer
        from validation.monte_carlo_simulation import monte_carlo_simulator
        from risk_management.financial_risk_manager import risk_manager
        
        # Teste de backtesting
        logger.info("Testando backtesting rigoroso...")
        import pandas as pd
        import numpy as np
        
        # Criar dados de teste
        np.random.seed(42)
        dates = pd.date_range('2021-01-01', '2024-01-01', freq='D')
        n_trades = len(dates)
        
        data = pd.DataFrame({
            'date': dates,
            'prediction': np.random.choice(['home_win', 'draw', 'away_win'], n_trades),
            'actual': np.random.choice(['home_win', 'draw', 'away_win'], n_trades),
            'odds': np.random.uniform(1.5, 3.0, n_trades),
            'stake': np.random.uniform(50, 200, n_trades)
        })
        
        result = rigorous_backtester.run_backtest(data)
        logger.info(f"✅ Backtesting executado: {result.validation_status.value}")
        
        # Teste de walk-forward
        logger.info("Testando walk-forward analysis...")
        wf_result = walk_forward_analyzer.run_analysis(data)
        logger.info(f"✅ Walk-forward executado: {len(wf_result.windows)} janelas")
        
        # Teste de Monte Carlo
        logger.info("Testando simulação Monte Carlo...")
        mc_result = monte_carlo_simulator.run_simulation(monte_carlo_simulator.scenarios['NORMAL'])
        logger.info(f"✅ Monte Carlo executado: {mc_result.simulations} simulações")
        
        # Teste de gestão de risco
        logger.info("Testando gestão de risco...")
        risk_metrics = risk_manager.get_risk_metrics()
        logger.info(f"✅ Gestão de risco: Drawdown {risk_metrics.current_drawdown:.1%}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos testes de validação: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO CONFIGURAÇÃO DO SISTEMA DE DADOS REAIS")
    logger.info("=" * 60)
    
    # Verificar ambiente
    if not check_environment():
        logger.error("❌ Configuração do ambiente falhou")
        return False
    
    # Testar API
    if not test_api_connection():
        logger.error("❌ Teste de API falhou")
        return False
    
    # Coletar dados históricos
    if not collect_historical_data():
        logger.error("❌ Coleta de dados históricos falhou")
        return False
    
    # Treinar modelos
    if not train_models():
        logger.error("❌ Treinamento de modelos falhou")
        return False
    
    # Testar coleta contínua
    if not test_continuous_collection():
        logger.error("❌ Teste de coleta contínua falhou")
        return False
    
    # Executar validação
    if not run_validation_tests():
        logger.error("❌ Testes de validação falharam")
        return False
    
    logger.info("🎉 CONFIGURAÇÃO DO SISTEMA CONCLUÍDA COM SUCESSO!")
    logger.info("=" * 60)
    logger.info("✅ Dados históricos coletados")
    logger.info("✅ Modelos treinados com dados reais")
    logger.info("✅ Integração real com API-Football funcionando")
    logger.info("✅ Coleta contínua configurada")
    logger.info("✅ Sistemas de validação funcionando")
    logger.info("✅ Gestão de risco implementada")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
