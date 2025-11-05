import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestingEngine:
    def __init__(self, predictor, analyzer):
        self.predictor = predictor
        self.analyzer = analyzer
        self.config = Config()
        self.results = []
        
    def run_backtest(self, historical_data, start_date=None, end_date=None, initial_capital=1000):
        """
        Executa backtesting completo
        """
        logger.info("Iniciando backtesting...")
        
        # Filtra dados por período
        if start_date or end_date:
            historical_data = self._filter_by_date(historical_data, start_date, end_date)
        
        # Simula apostas
        portfolio = self._simulate_betting(historical_data, initial_capital)
        
        # Calcula métricas
        metrics = self._calculate_metrics(portfolio)
        
        # Gera relatórios
        self._generate_reports(portfolio, metrics)
        
        return {
            'portfolio': portfolio,
            'metrics': metrics,
            'total_trades': len(portfolio),
            'period': {
                'start': start_date,
                'end': end_date
            }
        }
    
    def _filter_by_date(self, data, start_date, end_date):
        """Filtra dados por período"""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered_data = []
        for match in data:
            match_date = datetime.strptime(match['date'], '%Y-%m-%d %H:%M')
            
            if start_date and match_date < start_date:
                continue
            if end_date and match_date > end_date:
                continue
                
            filtered_data.append(match)
        
        return filtered_data
    
    def _simulate_betting(self, matches, initial_capital):
        """
        Simula estratégia de apostas
        """
        portfolio = []
        current_capital = initial_capital
        bet_size = 0.02  # 2% do capital por aposta
        
        for i, match in enumerate(matches):
            try:
                # Prepara dados da partida
                home_team_data = self._get_team_data(match['home_team'])
                away_team_data = self._get_team_data(match['away_team'])
                
                # Cria features
                from feature_engineering import FeatureEngineer
                engineer = FeatureEngineer()
                features = engineer.create_match_features(home_team_data, away_team_data, match)
                match_df = pd.DataFrame([features])
                
                # Analisa a partida
                analysis = self.analyzer.analyze_match(match_df)
                
                if not analysis:
                    continue
                
                # Encontra melhor aposta
                best_bet = self._find_best_bet(analysis)
                
                if best_bet and best_bet['ev'] > 0.1:  # Só aposta se EV > 10%
                    # Calcula tamanho da aposta
                    bet_amount = current_capital * bet_size
                    kelly_bet = current_capital * best_bet['kelly_percentage']
                    final_bet = min(bet_amount, kelly_bet)
                    
                    # Simula resultado
                    actual_result = self._simulate_match_result(match)
                    is_winner = self._check_bet_result(best_bet['outcome'], actual_result)
                    
                    # Calcula lucro/prejuízo
                    if is_winner:
                        profit = final_bet * (best_bet['odds'] - 1)
                    else:
                        profit = -final_bet
                    
                    current_capital += profit
                    
                    # Registra trade
                    trade = {
                        'match_id': match.get('id', f'match_{i}'),
                        'date': match['date'],
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'bet_outcome': best_bet['outcome'],
                        'bet_odds': best_bet['odds'],
                        'bet_amount': final_bet,
                        'kelly_percentage': best_bet['kelly_percentage'],
                        'ev': best_bet['ev'],
                        'actual_result': actual_result,
                        'is_winner': is_winner,
                        'profit': profit,
                        'capital_after': current_capital,
                        'roi': (current_capital - initial_capital) / initial_capital * 100
                    }
                    
                    portfolio.append(trade)
                    
            except Exception as e:
                logger.error(f"Erro ao processar partida {i}: {e}")
                continue
        
        return portfolio
    
    def _get_team_data(self, team_name):
        """Obtém dados históricos de um time"""
        from data_collector import SportsDataCollector
        collector = SportsDataCollector()
        return collector.get_historical_results(team_name)
    
    def _find_best_bet(self, analysis):
        """Encontra a melhor aposta baseada na análise"""
        best_bet = None
        best_ev = -1
        
        for rec in analysis['recommendations']:
            if rec['recommendation'] == 'BET' and rec['expected_value'] > best_ev:
                best_ev = rec['expected_value']
                best_bet = rec
        
        return best_bet
    
    def _simulate_match_result(self, match):
        """Simula resultado de uma partida"""
        import random
        
        # Simula resultado baseado nas odds
        home_odds = match.get('home_odds', 2.0)
        draw_odds = match.get('draw_odds', 3.0)
        away_odds = match.get('away_odds', 2.5)
        
        # Calcula probabilidades implícitas
        home_prob = 1 / home_odds
        draw_prob = 1 / draw_odds
        away_prob = 1 / away_odds
        
        # Normaliza probabilidades
        total_prob = home_prob + draw_prob + away_prob
        home_prob /= total_prob
        draw_prob /= total_prob
        away_prob /= total_prob
        
        # Simula resultado
        rand = random.random()
        
        if rand < home_prob:
            return 'home_win'
        elif rand < home_prob + draw_prob:
            return 'draw'
        else:
            return 'away_win'
    
    def _check_bet_result(self, bet_outcome, actual_result):
        """Verifica se a aposta foi vencedora"""
        return bet_outcome == actual_result
    
    def _calculate_metrics(self, portfolio):
        """Calcula métricas de performance"""
        if not portfolio:
            return {}
        
        df = pd.DataFrame(portfolio)
        
        # Métricas básicas
        total_trades = len(df)
        winning_trades = len(df[df['is_winner'] == True])
        losing_trades = len(df[df['is_winner'] == False])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Métricas financeiras
        total_profit = df['profit'].sum()
        total_bet_amount = df['bet_amount'].sum()
        roi = (total_profit / total_bet_amount * 100) if total_bet_amount > 0 else 0
        
        # Métricas de risco
        max_drawdown = self._calculate_max_drawdown(df['capital_after'])
        sharpe_ratio = self._calculate_sharpe_ratio(df['profit'])
        
        # Métricas de precisão
        accuracy = accuracy_score(df['actual_result'], df['bet_outcome'])
        
        # Análise por tipo de aposta
        bet_analysis = {}
        for outcome in ['home_win', 'draw', 'away_win']:
            outcome_trades = df[df['bet_outcome'] == outcome]
            if len(outcome_trades) > 0:
                bet_analysis[outcome] = {
                    'count': len(outcome_trades),
                    'win_rate': len(outcome_trades[outcome_trades['is_winner'] == True]) / len(outcome_trades),
                    'avg_profit': outcome_trades['profit'].mean(),
                    'total_profit': outcome_trades['profit'].sum()
                }
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_bet_amount': total_bet_amount,
            'roi': roi,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'accuracy': accuracy,
            'bet_analysis': bet_analysis,
            'avg_bet_amount': df['bet_amount'].mean(),
            'max_bet_amount': df['bet_amount'].max(),
            'min_bet_amount': df['bet_amount'].min()
        }
    
    def _calculate_max_drawdown(self, capital_series):
        """Calcula drawdown máximo"""
        peak = capital_series.expanding().max()
        drawdown = (capital_series - peak) / peak
        return drawdown.min() * 100
    
    def _calculate_sharpe_ratio(self, returns):
        """Calcula Sharpe ratio"""
        if len(returns) < 2:
            return 0
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        if std_return == 0:
            return 0
        
        return mean_return / std_return
    
    def _generate_reports(self, portfolio, metrics):
        """Gera relatórios de backtesting"""
        logger.info("Gerando relatórios...")
        
        # Relatório de performance
        self._generate_performance_report(metrics)
        
        # Gráficos
        self._generate_charts(portfolio, metrics)
        
        # Relatório de trades
        self._generate_trades_report(portfolio)
    
    def _generate_performance_report(self, metrics):
        """Gera relatório de performance"""
        report = f"""
=== RELATÓRIO DE PERFORMANCE ===

Métricas Gerais:
- Total de Trades: {metrics['total_trades']}
- Trades Vencedores: {metrics['winning_trades']}
- Trades Perdedores: {metrics['losing_trades']}
- Taxa de Acerto: {metrics['win_rate']:.2%}
- ROI: {metrics['roi']:.2f}%

Métricas de Risco:
- Drawdown Máximo: {metrics['max_drawdown']:.2f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}

Análise por Tipo de Aposta:
"""
        
        for outcome, analysis in metrics['bet_analysis'].items():
            report += f"""
{outcome.upper()}:
- Quantidade: {analysis['count']}
- Taxa de Acerto: {analysis['win_rate']:.2%}
- Lucro Médio: R$ {analysis['avg_profit']:.2f}
- Lucro Total: R$ {analysis['total_profit']:.2f}
"""
        
        logger.info(report)
    
    def _generate_charts(self, portfolio, metrics):
        """Gera gráficos de análise"""
        if not portfolio:
            return
        
        df = pd.DataFrame(portfolio)
        
        # Configura estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Relatório de Backtesting - MaraBet AI', fontsize=16)
        
        # 1. Evolução do Capital
        axes[0, 0].plot(df.index, df['capital_after'], linewidth=2, color='blue')
        axes[0, 0].set_title('Evolução do Capital')
        axes[0, 0].set_xlabel('Trade')
        axes[0, 0].set_ylabel('Capital (R$)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Distribuição de Lucros/Prejuízos
        axes[0, 1].hist(df['profit'], bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[0, 1].set_title('Distribuição de Lucros/Prejuízos')
        axes[0, 1].set_xlabel('Lucro/Prejuízo (R$)')
        axes[0, 1].set_ylabel('Frequência')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. ROI Acumulado
        df['cumulative_roi'] = df['roi']
        axes[1, 0].plot(df.index, df['cumulative_roi'], linewidth=2, color='purple')
        axes[1, 0].set_title('ROI Acumulado')
        axes[1, 0].set_xlabel('Trade')
        axes[1, 0].set_ylabel('ROI (%)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Análise por Tipo de Aposta
        bet_counts = df['bet_outcome'].value_counts()
        axes[1, 1].pie(bet_counts.values, labels=bet_counts.index, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Distribuição por Tipo de Aposta')
        
        plt.tight_layout()
        plt.savefig('backtesting_report.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _generate_trades_report(self, portfolio):
        """Gera relatório detalhado de trades"""
        if not portfolio:
            return
        
        df = pd.DataFrame(portfolio)
        
        # Salva relatório em CSV
        df.to_csv('trades_report.csv', index=False, encoding='utf-8')
        
        # Relatório resumido
        logger.info(f"Relatório de trades salvo em 'trades_report.csv'")
        logger.info(f"Total de trades: {len(df)}")
        logger.info(f"Trades vencedores: {len(df[df['is_winner'] == True])}")
        logger.info(f"Trades perdedores: {len(df[df['is_winner'] == False])}")
    
    def cross_validate_strategy(self, historical_data, n_folds=5):
        """
        Executa validação cruzada da estratégia
        """
        logger.info(f"Iniciando validação cruzada com {n_folds} folds...")
        
        # Divide dados em folds
        fold_size = len(historical_data) // n_folds
        fold_results = []
        
        for i in range(n_folds):
            start_idx = i * fold_size
            end_idx = (i + 1) * fold_size if i < n_folds - 1 else len(historical_data)
            
            test_data = historical_data[start_idx:end_idx]
            train_data = historical_data[:start_idx] + historical_data[end_idx:]
            
            # Treina modelo com dados de treino
            # (Em produção, retreinaria o modelo aqui)
            
            # Testa com dados de teste
            portfolio = self._simulate_betting(test_data, 1000)
            metrics = self._calculate_metrics(portfolio)
            
            fold_results.append({
                'fold': i + 1,
                'metrics': metrics,
                'trades': len(portfolio)
            })
        
        # Calcula métricas médias
        avg_metrics = self._calculate_average_metrics(fold_results)
        
        return {
            'fold_results': fold_results,
            'average_metrics': avg_metrics
        }
    
    def _calculate_average_metrics(self, fold_results):
        """Calcula métricas médias da validação cruzada"""
        metrics_list = [fold['metrics'] for fold in fold_results if fold['metrics']]
        
        if not metrics_list:
            return {}
        
        avg_metrics = {}
        for key in metrics_list[0].keys():
            if key != 'bet_analysis':
                values = [m[key] for m in metrics_list if key in m]
                if values:
                    avg_metrics[key] = np.mean(values)
        
        return avg_metrics

if __name__ == "__main__":
    # Teste do sistema de backtesting
    from data_collector import SportsDataCollector
    from ml_models import BettingPredictor, BettingAnalyzer
    
    # Coleta dados
    collector = SportsDataCollector()
    matches = collector.get_football_matches()
    
    # Inicializa componentes
    predictor = BettingPredictor()
    analyzer = BettingAnalyzer(predictor)
    backtester = BacktestingEngine(predictor, analyzer)
    
    # Executa backtesting
    results = backtester.run_backtest(matches, initial_capital=1000)
    print("Backtesting concluído!")
    print(f"Total de trades: {results['total_trades']}")
    print(f"ROI: {results['metrics']['roi']:.2f}%")
