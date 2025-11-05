#!/usr/bin/env python3
"""
MaraBet AI - Sistema de Análise Preditiva de Apostas Esportivas
Sistema especializado baseado em inteligência artificial para análise de apostas esportivas
"""

import argparse
import logging
import sys
from datetime import datetime
import os
import pandas as pd

from data_collector import SportsDataCollector
from feature_engineering import FeatureEngineer
from ml_models import BettingPredictor, BettingAnalyzer
from backtesting import BacktestingEngine
from framework_integration import MaraBetFramework
from predictive_integration import AdvancedPredictiveSystem
from probability_integration import AdvancedProbabilitySystem
from value_integration import AdvancedValueSystem
from bankroll_integration import AdvancedBankrollSystem
from unit_integration import AdvancedUnitSystem
from report_generator import ReportGenerator
from config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mara_bet.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MaraBetAI:
    def __init__(self):
        self.config = Config()
        self.collector = SportsDataCollector()
        self.engineer = FeatureEngineer()
        self.predictor = BettingPredictor()
        self.analyzer = BettingAnalyzer(self.predictor)
        self.backtester = BacktestingEngine(self.predictor, self.analyzer)
        self.framework = MaraBetFramework()  # Framework avançado
        self.advanced_predictive = AdvancedPredictiveSystem()  # Sistema preditivo avançado
        self.probability_system = AdvancedProbabilitySystem()  # Sistema de cálculo de probabilidades
        self.value_system = AdvancedValueSystem()  # Sistema de identificação de valor
        self.bankroll_system = AdvancedBankrollSystem()  # Sistema de gestão de banca
        self.unit_system = AdvancedUnitSystem()  # Sistema de gestão de unidades
        self.report_generator = ReportGenerator()  # Gerador de relatórios
        
    def collect_data(self, league='all', days=7):
        """Coleta dados esportivos"""
        logger.info(f"Coletando dados para liga: {league}, dias: {days}")
        
        try:
            matches = self.collector.get_football_matches(league, days)
            logger.info(f"Coletados {len(matches)} jogos")
            
            # Salva dados
            self.collector.save_data_to_csv(matches, f'matches_{league}_{days}d.csv')
            
            return matches
        except Exception as e:
            logger.error(f"Erro ao coletar dados: {e}")
            return []
    
    def train_models(self, matches_data):
        """Treina modelos de machine learning"""
        logger.info("Iniciando treinamento dos modelos...")
        
        try:
            # Prepara dados históricos
            all_teams = set([m['home_team'] for m in matches_data] + [m['away_team'] for m in matches_data])
            historical_data = {}
            
            for team in list(all_teams)[:20]:  # Limita para performance
                historical_data[team] = self.collector.get_historical_results(team)
            
            # Cria features
            training_data = self.engineer.prepare_training_data(matches_data, historical_data)
            
            if training_data.empty:
                logger.error("Dados insuficientes para treinamento")
                return False
            
            # Prepara dados
            X, y, feature_columns = self.predictor.prepare_data(training_data)
            
            # Treina modelos
            X_test, y_test = self.predictor.train_models(X, y, feature_columns)
            
            # Salva modelos
            self.predictor.save_models()
            
            # Log de performance
            for name, perf in self.predictor.model_performance.items():
                logger.info(f"Modelo {name}: Acurácia = {perf['accuracy']:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return False
    
    def analyze_matches(self, matches_data):
        """Analisa partidas e gera predições"""
        logger.info("Analisando partidas...")
        
        predictions = []
        
        for match in matches_data[:10]:  # Limita para demonstração
            try:
                # Dados históricos
                home_team_data = self.collector.get_historical_results(match['home_team'])
                away_team_data = self.collector.get_historical_results(match['away_team'])
                
                # Features
                features = self.engineer.create_match_features(home_team_data, away_team_data, match)
                match_df = pd.DataFrame([features])
                
                # Análise
                analysis = self.analyzer.analyze_match(match_df)
                
                if analysis:
                    predictions.append({
                        'match': match,
                        'analysis': analysis
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao analisar partida {match.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Análise concluída: {len(predictions)} partidas analisadas")
        return predictions
    
    def run_backtesting(self, historical_data, initial_capital=1000):
        """Executa backtesting da estratégia"""
        logger.info("Iniciando backtesting...")
        
        try:
            results = self.backtester.run_backtest(historical_data, initial_capital=initial_capital)
            
            logger.info("Backtesting concluído!")
            logger.info(f"Total de trades: {results['total_trades']}")
            logger.info(f"ROI: {results['metrics']['roi']:.2f}%")
            logger.info(f"Taxa de acerto: {results['metrics']['win_rate']:.2%}")
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no backtesting: {e}")
            return None
    
    def run_full_pipeline(self, league='all', days=7, initial_capital=1000):
        """Executa pipeline completo"""
        logger.info("=== INICIANDO PIPELINE COMPLETO MARABET AI ===")
        
        # 1. Coleta de dados
        matches = self.collect_data(league, days)
        if not matches:
            logger.error("Falha na coleta de dados")
            return False
        
        # 2. Treinamento de modelos
        if not self.train_models(matches):
            logger.error("Falha no treinamento")
            return False
        
        # 3. Análise de partidas
        predictions = self.analyze_matches(matches)
        if not predictions:
            logger.error("Falha na análise")
            return False
        
        # 4. Backtesting
        backtest_results = self.run_backtesting(matches, initial_capital)
        if not backtest_results:
            logger.error("Falha no backtesting")
            return False
        
        logger.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")
        return True
    
    def run_framework_analysis(self, home_team: str, away_team: str, match_date: str):
        """Executa análise usando o framework avançado"""
        logger.info(f"Executando análise com framework: {home_team} vs {away_team}")
        
        try:
            analysis = self.framework.analyze_match_comprehensive(home_team, away_team, match_date)
            return analysis
        except Exception as e:
            logger.error(f"Erro na análise com framework: {e}")
            return None
    
    def run_framework_training(self, historical_matches):
        """Treina modelos usando o framework avançado"""
        logger.info("Treinando modelos com framework avançado")
        
        try:
            result = self.framework.train_models_with_framework(historical_matches)
            return result
        except Exception as e:
            logger.error(f"Erro no treinamento com framework: {e}")
            return None
    
    def run_framework_backtesting(self, historical_matches, initial_capital=1000):
        """Executa backtesting usando o framework avançado"""
        logger.info("Executando backtesting com framework")
        
        try:
            result = self.framework.run_framework_backtesting(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro no backtesting com framework: {e}")
            return None
    
    def run_advanced_prediction(self, home_team: str, away_team: str, match_date: str):
        """Executa predição usando modelos avançados"""
        logger.info(f"Executando predição avançada: {home_team} vs {away_team}")
        
        try:
            # Primeiro treina os modelos se necessário
            if not self.advanced_predictive.trained:
                # Usa dados históricos para treinamento
                historical_matches = self.collect_data('all', 30)
                training_result = self.advanced_predictive.train_advanced_models(historical_matches)
                if not training_result['success']:
                    logger.error("Falha no treinamento dos modelos avançados")
                    return None
            
            # Faz predição
            prediction = self.advanced_predictive.predict_advanced(home_team, away_team, match_date)
            return prediction
        except Exception as e:
            logger.error(f"Erro na predição avançada: {e}")
            return None
    
    def run_advanced_backtesting(self, historical_matches, initial_capital=1000):
        """Executa backtesting usando modelos avançados"""
        logger.info("Executando backtesting com modelos avançados")
        
        try:
            result = self.advanced_predictive.run_advanced_backtesting(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro no backtesting avançado: {e}")
            return None
    
    def run_probability_analysis(self, home_team: str, away_team: str, match_date: str):
        """Executa análise de probabilidades com estrutura de pesos"""
        logger.info(f"Executando análise de probabilidades: {home_team} vs {away_team}")
        
        try:
            result = self.probability_system.calculate_match_probabilities(home_team, away_team, match_date)
            return result
        except Exception as e:
            logger.error(f"Erro na análise de probabilidades: {e}")
            return None
    
    def run_probability_backtesting(self, historical_matches, initial_capital=1000):
        """Executa backtesting usando sistema de probabilidades"""
        logger.info("Executando backtesting com sistema de probabilidades")
        
        try:
            result = self.probability_system.run_probability_backtesting(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro no backtesting de probabilidades: {e}")
            return None
    
    def run_value_analysis(self, home_team: str, away_team: str, match_date: str):
        """Executa análise de valor de uma partida"""
        logger.info(f"Executando análise de valor: {home_team} vs {away_team}")
        
        try:
            result = self.value_system.analyze_match_value(home_team, away_team, match_date)
            return result
        except Exception as e:
            logger.error(f"Erro na análise de valor: {e}")
            return None
    
    def run_value_scanning(self, league: str = 'all', days: int = 7):
        """Executa escaneamento do mercado em busca de valor"""
        logger.info(f"Executando escaneamento de valor: {league}, {days} dias")
        
        try:
            result = self.value_system.scan_market_opportunities(league, days)
            return result
        except Exception as e:
            logger.error(f"Erro no escaneamento de valor: {e}")
            return None
    
    def run_value_backtesting(self, historical_matches, initial_capital=1000):
        """Executa backtesting focado em identificação de valor"""
        logger.info("Executando backtesting de valor")
        
        try:
            result = self.value_system.run_value_backtesting(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro no backtesting de valor: {e}")
            return None
    
    def run_bankroll_analysis(self, home_team: str, away_team: str, match_date: str):
        """Executa análise de oportunidade com gestão de banca"""
        logger.info(f"Executando análise de banca: {home_team} vs {away_team}")
        
        try:
            result = self.bankroll_system.analyze_bet_opportunity(home_team, away_team, match_date)
            return result
        except Exception as e:
            logger.error(f"Erro na análise de banca: {e}")
            return None
    
    def run_bankroll_backtesting(self, historical_matches, initial_capital=1000):
        """Executa backtesting com gestão completa de banca"""
        logger.info("Executando backtesting com gestão de banca")
        
        try:
            result = self.bankroll_system.run_bankroll_backtesting(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro no backtesting de banca: {e}")
            return None
    
    def run_risk_optimization(self, historical_matches, initial_capital=1000):
        """Executa otimização de nível de risco"""
        logger.info("Executando otimização de risco")
        
        try:
            result = self.bankroll_system.optimize_risk_level(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro na otimização de risco: {e}")
            return None
    
    def run_unit_analysis(self, home_team: str, away_team: str, match_date: str):
        """Executa análise de aposta com gestão de unidades"""
        logger.info(f"Executando análise de unidades: {home_team} vs {away_team}")
        
        try:
            result = self.unit_system.analyze_bet_with_units(home_team, away_team, match_date)
            return result
        except Exception as e:
            logger.error(f"Erro na análise de unidades: {e}")
            return None
    
    def run_unit_backtesting(self, historical_matches, initial_capital=1000):
        """Executa backtesting com gestão de unidades"""
        logger.info("Executando backtesting com gestão de unidades")
        
        try:
            result = self.unit_system.run_unit_backtesting(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro no backtesting de unidades: {e}")
            return None
    
    def run_unit_optimization(self, historical_matches, initial_capital=1000):
        """Executa otimização de estratégia de unidades"""
        logger.info("Executando otimização de estratégia de unidades")
        
        try:
            result = self.unit_system.optimize_unit_strategy(historical_matches, initial_capital)
            return result
        except Exception as e:
            logger.error(f"Erro na otimização de unidades: {e}")
            return None
    
    def generate_analysis_report(self, home_team: str, away_team: str, match_date: str, 
                               league: str = "Premier League", season: str = "2024/25"):
        """Gera relatório completo de análise preditiva"""
        logger.info(f"Gerando relatório: {home_team} vs {away_team}")
        
        try:
            result = self.report_generator.generate_complete_analysis_report(
                home_team, away_team, match_date, league, season
            )
            return result
        except Exception as e:
            logger.error(f"Erro na geração do relatório: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='MaraBet AI - Sistema de Análise Preditiva de Apostas Esportivas')
    parser.add_argument('--mode', choices=['collect', 'train', 'analyze', 'backtest', 'full', 'framework', 'advanced', 'probabilities', 'value', 'bankroll', 'units', 'report'], 
                       default='full', help='Modo de execução')
    parser.add_argument('--league', default='all', help='Liga esportiva')
    parser.add_argument('--days', type=int, default=7, help='Número de dias para análise')
    parser.add_argument('--capital', type=float, default=1000, help='Capital inicial para backtesting')
    parser.add_argument('--web', action='store_true', help='Inicia interface web')
    parser.add_argument('--home-team', default='Manchester City', help='Time da casa para relatório')
    parser.add_argument('--away-team', default='Arsenal', help='Time visitante para relatório')
    parser.add_argument('--match-date', default='2024-01-15', help='Data da partida para relatório')
    parser.add_argument('--season', default='2024/25', help='Temporada para relatório')
    
    args = parser.parse_args()
    
    # Inicializa sistema
    marabet = MaraBetAI()
    
    if args.web:
        # Inicia interface web
        from app import app
        logger.info("Iniciando interface web...")
        app.run(host=marabet.config.HOST, port=marabet.config.PORT, debug=marabet.config.DEBUG)
        return
    
    # Executa modo selecionado
    if args.mode == 'collect':
        matches = marabet.collect_data(args.league, args.days)
        print(f"Coletados {len(matches)} jogos")
        
    elif args.mode == 'train':
        matches = marabet.collect_data(args.league, args.days)
        success = marabet.train_models(matches)
        print(f"Treinamento: {'Sucesso' if success else 'Falha'}")
        
    elif args.mode == 'analyze':
        matches = marabet.collect_data(args.league, args.days)
        predictions = marabet.analyze_matches(matches)
        print(f"Análise: {len(predictions)} partidas analisadas")
        
    elif args.mode == 'backtest':
        matches = marabet.collect_data(args.league, args.days)
        results = marabet.run_backtesting(matches, args.capital)
        if results:
            print(f"Backtesting: {results['total_trades']} trades, ROI: {results['metrics']['roi']:.2f}%")
        
    elif args.mode == 'full':
        success = marabet.run_full_pipeline(args.league, args.days, args.capital)
        print(f"Pipeline completo: {'Sucesso' if success else 'Falha'}")
        
    elif args.mode == 'framework':
        # Análise com framework avançado
        matches = marabet.collect_data(args.league, args.days)
        if matches:
            # Treina com framework
            training_result = marabet.run_framework_training(matches)
            if training_result and training_result['success']:
                print(f"Treinamento com framework: Sucesso")
                print(f"Performance: {training_result['performance']}")
                
                # Executa backtesting com framework
                backtest_result = marabet.run_framework_backtesting(matches, args.capital)
                if backtest_result and backtest_result['success']:
                    print(f"Backtesting com framework: Sucesso")
                    print(f"ROI: {backtest_result['backtest_results']['metrics']['roi']:.2f}%")
                else:
                    print("Falha no backtesting com framework")
            else:
                print("Falha no treinamento com framework")
        else:
            print("Falha na coleta de dados")
    
    elif args.mode == 'advanced':
        # Análise com modelos preditivos avançados
        matches = marabet.collect_data(args.league, args.days)
        if matches:
            # Executa backtesting com modelos avançados
            backtest_result = marabet.run_advanced_backtesting(matches, args.capital)
            if backtest_result and backtest_result['success']:
                print(f"Backtesting avançado: Sucesso")
                print(f"ROI: {backtest_result['metrics']['roi']:.2f}%")
                print(f"Trades: {backtest_result['metrics']['total_trades']}")
                print(f"Incerteza média: {backtest_result['metrics']['avg_uncertainty']:.3f}")
                print(f"ROI ajustado por incerteza: {backtest_result['metrics']['uncertainty_adjusted_roi']:.2f}%")
            else:
                print("Falha no backtesting avançado")
        else:
            print("Falha na coleta de dados")
    
    elif args.mode == 'probabilities':
        # Análise com sistema de cálculo de probabilidades
        matches = marabet.collect_data(args.league, args.days)
        if matches:
            # Executa backtesting com sistema de probabilidades
            backtest_result = marabet.run_probability_backtesting(matches, args.capital)
            if backtest_result and backtest_result['success']:
                print(f"Backtesting de probabilidades: Sucesso")
                print(f"ROI: {backtest_result['metrics']['roi']:.2f}%")
                print(f"Trades: {backtest_result['metrics']['total_trades']}")
                print(f"Taxa de acerto: {backtest_result['metrics']['win_rate']:.1%}")
                print(f"Confiança média: {backtest_result['metrics']['avg_confidence']:.3f}")
                print(f"Precisão das probabilidades: {backtest_result['metrics']['probability_accuracy']:.1%}")
            else:
                print("Falha no backtesting de probabilidades")
        else:
            print("Falha na coleta de dados")
    
    elif args.mode == 'value':
        # Análise com sistema de identificação de valor
        matches = marabet.collect_data(args.league, args.days)
        if matches:
            # Executa backtesting de valor
            backtest_result = marabet.run_value_backtesting(matches, args.capital)
            if backtest_result and backtest_result['success']:
                print(f"Backtesting de valor: Sucesso")
                print(f"ROI: {backtest_result['metrics']['roi']:.2f}%")
                print(f"Trades: {backtest_result['metrics']['total_trades']}")
                print(f"Taxa de acerto: {backtest_result['metrics']['win_rate']:.1%}")
                print(f"EV médio: {backtest_result['metrics']['avg_expected_value']:.3f}")
                print(f"Precisão do EV: {backtest_result['metrics']['ev_accuracy']:.1%}")
                print(f"ROI ajustado por valor: {backtest_result['metrics']['value_adjusted_roi']:.2f}%")
            else:
                print("Falha no backtesting de valor")
        else:
            print("Falha na coleta de dados")
    
    elif args.mode == 'bankroll':
        # Análise com sistema de gestão de banca
        matches = marabet.collect_data(args.league, args.days)
        if matches:
            # Executa backtesting com gestão de banca
            backtest_result = marabet.run_bankroll_backtesting(matches, args.capital)
            if backtest_result and backtest_result['success']:
                print(f"Backtesting de gestão de banca: Sucesso")
                print(f"Capital final: R$ {backtest_result['final_bankroll_status']['current_capital']:.2f}")
                print(f"Lucro total: R$ {backtest_result['final_bankroll_status']['total_profit']:.2f}")
                print(f"ROI: {backtest_result['final_bankroll_status']['profit_percentage']:.1f}%")
                print(f"Drawdown máximo: {backtest_result['final_bankroll_status']['max_drawdown_percentage']:.1f}%")
                print(f"Taxa de acerto: {backtest_result['betting_statistics']['win_rate']:.1%}")
                print(f"Total de apostas: {backtest_result['betting_statistics']['total_bets']}")
                print(f"Stake médio: {backtest_result['betting_statistics']['avg_stake_percentage']:.1%}")
            else:
                print("Falha no backtesting de gestão de banca")
        else:
            print("Falha na coleta de dados")
    
    elif args.mode == 'units':
        # Análise com sistema de gestão de unidades
        matches = marabet.collect_data(args.league, args.days)
        if matches:
            # Executa backtesting com gestão de unidades
            backtest_result = marabet.run_unit_backtesting(matches, args.capital)
            if backtest_result and backtest_result['success']:
                print(f"Backtesting de gestão de unidades: Sucesso")
                print(f"Capital final: R$ {backtest_result['summary']['final_capital']:.2f}")
                print(f"Lucro total: R$ {backtest_result['summary']['total_profit']:.2f}")
                print(f"ROI: {backtest_result['summary']['profit_percentage']:.1f}%")
                print(f"Unidades apostadas: {backtest_result['summary']['total_units_staked']:.1f}")
                print(f"Lucro em unidades: {backtest_result['summary']['total_units_profit']:.1f}")
                print(f"Unidades médias por aposta: {backtest_result['summary']['average_units_per_bet']:.1f}")
                print(f"Taxa de execução: {backtest_result['summary']['execution_rate']:.1%}")
            else:
                print("Falha no backtesting de gestão de unidades")
        else:
            print("Falha na coleta de dados")
    
    elif args.mode == 'report':
        # Geração de relatório de análise completa
        print(f"Gerando relatório: {args.home_team} vs {args.away_team}")
        
        report_result = marabet.generate_analysis_report(
            args.home_team, 
            args.away_team, 
            args.match_date,
            args.league,
            args.season
        )
        
        if report_result and report_result['success']:
            print(f"Relatório gerado com sucesso!")
            print(f"Arquivo salvo em: {report_result['file_path']}")
            print(f"Confiança da análise: {report_result['analysis_result'].confidence_score:.1%}")
            print(f"Recomendação: {report_result['analysis_result'].final_recommendation['action']}")
            print(f"Valor esperado: {report_result['analysis_result'].value_analysis['best_opportunity']['expected_value']:+.3f}")
            print(f"Unidades recomendadas: {report_result['analysis_result'].unit_recommendation['recommended_units']:.1f}")
            
            # Mostra preview do relatório
            print(f"\nPreview do relatório:")
            print("-" * 50)
            print(report_result['report'][:1000] + "...")
        else:
            print("Falha na geração do relatório")

if __name__ == "__main__":
    main()
