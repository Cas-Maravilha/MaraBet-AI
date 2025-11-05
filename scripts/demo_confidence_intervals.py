#!/usr/bin/env python3
"""
Demonstração de Intervalos de Confiança - MaraBet AI
Script de demonstração do sistema de intervalos de confiança
"""

import os
import sys
import argparse
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from confidence import (
    ConfidenceCalculator, UncertaintyAnalyzer, ConfidenceVisualizer,
    PredictionIntervals, BootstrapConfidence
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_data(n_predictions: int = 100) -> tuple:
    """
    Gera dados de exemplo para demonstração
    
    Args:
        n_predictions: Número de previsões
        
    Returns:
        Tupla com (predictions, actual_values, historical_errors)
    """
    try:
        np.random.seed(42)
        
        # Gerar previsões (probabilidades entre 0.3 e 0.9)
        base_predictions = np.random.uniform(0.3, 0.9, n_predictions)
        
        # Adicionar ruído para simular incerteza do modelo
        model_uncertainty = np.random.normal(0, 0.05, n_predictions)
        predictions = np.clip(base_predictions + model_uncertainty, 0.1, 0.95)
        
        # Gerar valores reais (com algum viés sistemático)
        systematic_bias = 0.02  # Viés de 2%
        noise = np.random.normal(0, 0.08, n_predictions)
        actual_values = np.clip(predictions + systematic_bias + noise, 0, 1)
        
        # Gerar erros históricos para cada previsão
        historical_errors = []
        for i in range(n_predictions):
            # Simular erros históricos com distribuição normal
            n_historical = np.random.randint(10, 50)
            historical_error = np.random.normal(0, 0.1, n_historical)
            historical_errors.append(historical_error.tolist())
        
        return predictions.tolist(), actual_values.tolist(), historical_errors
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dados de exemplo: {e}")
        return [], [], []

def demo_confidence_calculator():
    """Demonstra o calculador de intervalos de confiança"""
    try:
        logger.info("🔍 Demonstração do ConfidenceCalculator")
        
        # Criar calculador
        calculator = ConfidenceCalculator()
        
        # Exemplo 1: Previsão única
        logger.info("\n📊 Exemplo 1: Previsão única")
        prediction = 0.75
        interval = calculator.calculate_confidence_interval([prediction])
        
        print(f"Previsão: {prediction:.3f}")
        print(f"Intervalo de 95%: {interval.lower_bound:.3f} - {interval.upper_bound:.3f}")
        print(f"Formato: {calculator.format_confidence_interval(interval)}")
        
        # Exemplo 2: Múltiplas previsões
        logger.info("\n📊 Exemplo 2: Múltiplas previsões")
        predictions = [0.65, 0.72, 0.68, 0.75, 0.71]
        interval = calculator.calculate_confidence_interval(predictions)
        
        print(f"Previsões: {predictions}")
        print(f"Intervalo de 95%: {interval.lower_bound:.3f} - {interval.upper_bound:.3f}")
        print(f"Formato: {calculator.format_confidence_interval(interval)}")
        
        # Exemplo 3: Múltiplos níveis de confiança
        logger.info("\n📊 Exemplo 3: Múltiplos níveis de confiança")
        confidence_levels = [0.68, 0.80, 0.90, 0.95, 0.99]
        intervals = calculator.calculate_multiple_confidence_levels(predictions, confidence_levels)
        
        print("Intervalos para diferentes níveis de confiança:")
        for level, interval in intervals.items():
            print(f"  {level*100:.0f}%: {interval.lower_bound:.3f} - {interval.upper_bound:.3f}")
        
        # Exemplo 4: Análise de incerteza
        logger.info("\n📊 Exemplo 4: Análise de incerteza")
        uncertainty = calculator.calculate_prediction_uncertainty(predictions)
        
        print(f"Previsão média: {uncertainty.mean_prediction:.3f}")
        print(f"Score de incerteza: {uncertainty.uncertainty_score:.1f}")
        print(f"Score de confiabilidade: {uncertainty.reliability_score:.1f}")
        print(f"Score de calibração: {uncertainty.calibration_score:.1f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do ConfidenceCalculator: {e}")
        return False

def demo_uncertainty_analyzer():
    """Demonstra o analisador de incerteza"""
    try:
        logger.info("🔍 Demonstração do UncertaintyAnalyzer")
        
        # Gerar dados de exemplo
        predictions, actual_values, _ = generate_sample_data(50)
        
        # Criar analisador
        analyzer = UncertaintyAnalyzer()
        
        # Analisar incerteza
        report = analyzer.analyze_prediction_uncertainty(predictions, actual_values)
        
        # Mostrar métricas gerais
        metrics = report.overall_metrics
        print(f"\n📊 Métricas Gerais:")
        print(f"  Incerteza média: {metrics.mean_uncertainty:.1f}")
        print(f"  Score de confiabilidade: {metrics.reliability_score:.1f}")
        print(f"  Score de calibração: {metrics.calibration_score:.1f}")
        print(f"  Taxa de overconfidence: {metrics.overconfidence_rate:.1f}%")
        print(f"  Taxa de underconfidence: {metrics.underconfidence_rate:.1f}%")
        print(f"  Precisão das previsões: {metrics.prediction_accuracy:.1f}")
        print(f"  Precisão da confiança: {metrics.confidence_accuracy:.1f}")
        
        # Mostrar recomendações
        print(f"\n💡 Recomendações:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Criar visualizações
        output_dir = "confidence/demo_visualizations"
        analyzer.create_uncertainty_visualizations(output_dir)
        print(f"\n📊 Visualizações criadas em: {output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do UncertaintyAnalyzer: {e}")
        return False

def demo_prediction_intervals():
    """Demonstra o sistema de intervalos de predição"""
    try:
        logger.info("🔍 Demonstração do PredictionIntervals")
        
        # Gerar dados de exemplo
        predictions, actual_values, historical_errors = generate_sample_data(30)
        
        # Criar sistema de intervalos
        intervals_system = PredictionIntervals()
        
        # Exemplo 1: Intervalo de predição único
        logger.info("\n📊 Exemplo 1: Intervalo de predição único")
        prediction = 0.75
        historical_error = historical_errors[0]
        
        interval = intervals_system.calculate_prediction_interval(
            prediction, historical_error
        )
        
        print(f"Previsão: {prediction:.3f}")
        print(f"Intervalo de predição: {interval.lower_bound:.3f} - {interval.upper_bound:.3f}")
        print(f"Largura do intervalo: {interval.interval_width:.3f}")
        print(f"Formato: {intervals_system.format_prediction_interval(interval)}")
        
        # Exemplo 2: Múltiplos intervalos
        logger.info("\n📊 Exemplo 2: Múltiplos intervalos de predição")
        confidence_levels = [0.68, 0.80, 0.90, 0.95, 0.99]
        multiple_intervals = intervals_system.calculate_multiple_prediction_intervals(
            predictions[:5], historical_errors[:5], confidence_levels
        )
        
        print("Intervalos para diferentes níveis de confiança:")
        for level, interval_list in multiple_intervals.items():
            interval = interval_list[0]  # Primeira previsão
            print(f"  {level*100:.0f}%: {interval.lower_bound:.3f} - {interval.upper_bound:.3f}")
        
        # Exemplo 3: Avaliação de qualidade
        logger.info("\n📊 Exemplo 3: Avaliação de qualidade")
        all_intervals = []
        for i, pred in enumerate(predictions[:10]):
            interval = intervals_system.calculate_prediction_interval(
                pred, historical_errors[i]
            )
            all_intervals.append(interval)
        
        metrics = intervals_system.evaluate_prediction_intervals(
            all_intervals, actual_values[:10]
        )
        
        print(f"Taxa de cobertura: {metrics.coverage_rate:.1f}%")
        print(f"Largura média: {metrics.average_width:.3f}")
        print(f"Score de calibração: {metrics.calibration_score:.1f}")
        print(f"Score de sharpness: {metrics.sharpness_score:.1f}")
        print(f"Score de confiabilidade: {metrics.reliability_score:.1f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do PredictionIntervals: {e}")
        return False

def demo_bootstrap_confidence():
    """Demonstra o sistema de bootstrap"""
    try:
        logger.info("🔍 Demonstração do BootstrapConfidence")
        
        # Gerar dados de exemplo
        predictions, actual_values, _ = generate_sample_data(50)
        
        # Criar sistema de bootstrap
        bootstrap_system = BootstrapConfidence(n_bootstrap=500)
        
        # Exemplo 1: Bootstrap básico
        logger.info("\n📊 Exemplo 1: Bootstrap básico")
        data = predictions[:20]
        
        result = bootstrap_system.bootstrap_confidence_interval(
            data, np.mean, "percentile"
        )
        
        print(f"Estatística original: {result.original_statistic:.3f}")
        print(f"Intervalo de confiança: {result.confidence_interval[0]:.3f} - {result.confidence_interval[1]:.3f}")
        print(f"Viés: {result.bias:.3f}")
        print(f"Erro padrão: {result.standard_error:.3f}")
        
        # Exemplo 2: Comparação de métodos
        logger.info("\n📊 Exemplo 2: Comparação de métodos")
        methods_comparison = bootstrap_system.compare_bootstrap_methods(
            data, confidence_levels=[0.90, 0.95, 0.99]
        )
        
        print("Comparação de métodos:")
        for method, levels in methods_comparison.items():
            print(f"  {method}:")
            for level, result in levels.items():
                ci_lower, ci_upper = result.confidence_interval
                print(f"    {level*100:.0f}%: {ci_lower:.3f} - {ci_upper:.3f}")
        
        # Exemplo 3: Análise de incerteza
        logger.info("\n📊 Exemplo 3: Análise de incerteza")
        uncertainty_analysis = bootstrap_system.bootstrap_uncertainty_analysis(
            predictions, actual_values
        )
        
        quality = uncertainty_analysis['quality_metrics']
        uncertainty = uncertainty_analysis['uncertainty_metrics']
        
        print(f"Viés médio: {quality.mean_bias:.3f}")
        print(f"Taxa de cobertura: {quality.coverage_rate:.1f}%")
        print(f"Eficiência: {quality.efficiency:.1f}")
        print(f"Estabilidade: {quality.stability:.1f}")
        print(f"Incerteza média: {uncertainty['mean_uncertainty']:.3f}")
        print(f"Precisão das previsões: {uncertainty['prediction_accuracy']:.1f}")
        
        # Mostrar recomendações
        print(f"\n💡 Recomendações:")
        for i, rec in enumerate(uncertainty_analysis['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do BootstrapConfidence: {e}")
        return False

def demo_confidence_visualizer():
    """Demonstra o visualizador de confiança"""
    try:
        logger.info("🔍 Demonstração do ConfidenceVisualizer")
        
        # Gerar dados de exemplo
        predictions, actual_values, _ = generate_sample_data(20)
        
        # Criar visualizador
        visualizer = ConfidenceVisualizer()
        
        # Exemplo 1: Intervalos de confiança
        logger.info("\n📊 Exemplo 1: Gráfico de intervalos de confiança")
        from confidence.confidence_calculator import ConfidenceCalculator
        calculator = ConfidenceCalculator()
        
        # Calcular intervalos para diferentes níveis
        confidence_levels = [0.68, 0.80, 0.90, 0.95, 0.99]
        intervals = {}
        for level in confidence_levels:
            interval = calculator.calculate_confidence_interval([0.75], confidence_level=level)
            intervals[level] = interval
        
        # Criar gráfico
        output_file = "confidence/demo_confidence_intervals.png"
        visualizer.create_confidence_interval_plot(
            intervals, "Intervalos de Confiança - Demonstração", output_file
        )
        print(f"Gráfico salvo em: {output_file}")
        
        # Exemplo 2: Fan chart
        logger.info("\n📊 Exemplo 2: Gráfico de leque de confiança")
        fan_chart_file = "confidence/demo_fan_chart.png"
        visualizer.create_confidence_fan_chart(
            predictions[:10], confidence_levels, "Fan Chart - Demonstração", fan_chart_file
        )
        print(f"Fan chart salvo em: {fan_chart_file}")
        
        # Exemplo 3: Dashboard de incerteza
        logger.info("\n📊 Exemplo 3: Dashboard de incerteza")
        from confidence.uncertainty_analyzer import UncertaintyAnalyzer
        analyzer = UncertaintyAnalyzer()
        
        # Gerar dados de incerteza
        uncertainty_data = []
        for pred in predictions[:10]:
            uncertainty = calculator.calculate_prediction_uncertainty([pred])
            uncertainty_data.append(uncertainty)
        
        # Criar dashboard
        dashboard_file = "confidence/demo_uncertainty_dashboard.png"
        visualizer.create_uncertainty_dashboard(
            uncertainty_data, "Dashboard de Incerteza - Demonstração", dashboard_file
        )
        print(f"Dashboard salvo em: {dashboard_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do ConfidenceVisualizer: {e}")
        return False

def create_comprehensive_demo():
    """Cria demonstração abrangente do sistema"""
    try:
        logger.info("🚀 Iniciando demonstração abrangente do sistema de intervalos de confiança")
        
        # Criar diretório de saída
        os.makedirs("confidence/demo_results", exist_ok=True)
        
        # Executar todas as demonstrações
        demos = [
            ("ConfidenceCalculator", demo_confidence_calculator),
            ("UncertaintyAnalyzer", demo_uncertainty_analyzer),
            ("PredictionIntervals", demo_prediction_intervals),
            ("BootstrapConfidence", demo_bootstrap_confidence),
            ("ConfidenceVisualizer", demo_confidence_visualizer)
        ]
        
        results = {}
        for name, demo_func in demos:
            logger.info(f"\n{'='*50}")
            logger.info(f"Executando demonstração: {name}")
            logger.info(f"{'='*50}")
            
            try:
                success = demo_func()
                results[name] = success
                if success:
                    logger.info(f"✅ {name} - Demonstração concluída com sucesso")
                else:
                    logger.error(f"❌ {name} - Demonstração falhou")
            except Exception as e:
                logger.error(f"❌ {name} - Erro: {e}")
                results[name] = False
        
        # Resumo final
        logger.info(f"\n{'='*50}")
        logger.info("RESUMO DA DEMONSTRAÇÃO")
        logger.info(f"{'='*50}")
        
        successful = sum(results.values())
        total = len(results)
        
        for name, success in results.items():
            status = "✅ SUCESSO" if success else "❌ FALHOU"
            logger.info(f"{name}: {status}")
        
        logger.info(f"\nTotal: {successful}/{total} demonstrações bem-sucedidas")
        
        if successful == total:
            logger.info("🎉 Todas as demonstrações foram executadas com sucesso!")
        else:
            logger.warning(f"⚠️ {total - successful} demonstrações falharam")
        
        return successful == total
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração abrangente: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Demonstração de Intervalos de Confiança - MaraBet AI")
    parser.add_argument("--demo", choices=[
        "confidence", "uncertainty", "prediction", "bootstrap", "visualizer", "all"
    ], default="all", help="Tipo de demonstração a executar")
    parser.add_argument("--n-predictions", type=int, default=100, 
                       help="Número de previsões para gerar")
    parser.add_argument("--output-dir", default="confidence/demo_results",
                       help="Diretório de saída")
    
    args = parser.parse_args()
    
    # Configurar diretório de saída
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        if args.demo == "all":
            success = create_comprehensive_demo()
        elif args.demo == "confidence":
            success = demo_confidence_calculator()
        elif args.demo == "uncertainty":
            success = demo_uncertainty_analyzer()
        elif args.demo == "prediction":
            success = demo_prediction_intervals()
        elif args.demo == "bootstrap":
            success = demo_bootstrap_confidence()
        elif args.demo == "visualizer":
            success = demo_confidence_visualizer()
        else:
            logger.error(f"❌ Demonstração desconhecida: {args.demo}")
            success = False
        
        if success:
            logger.info("🎉 Demonstração concluída com sucesso!")
            sys.exit(0)
        else:
            logger.error("❌ Demonstração falhou")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Demonstração cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
