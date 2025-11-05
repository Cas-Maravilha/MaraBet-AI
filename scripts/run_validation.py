#!/usr/bin/env python3
"""
Script Principal de Validação - MaraBet AI
Executa backtesting completo e gera relatórios de transparência
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation import (
    BacktestingEngine, PerformanceAnalyzer, TransparencyReporter,
    ROICalculator, LeagueAnalyzer
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_complete_validation(
    matches_file: str,
    predictions_file: str,
    odds_file: str,
    output_dir: str = "validation/results",
    initial_capital: float = 10000.0,
    stake_strategy: str = "percentage",
    stake_percentage: float = 0.02,
    min_confidence: float = 0.6,
    max_confidence: float = 0.95
) -> bool:
    """
    Executa validação completa do sistema
    
    Args:
        matches_file: Arquivo com dados de partidas
        predictions_file: Arquivo com predições
        odds_file: Arquivo com odds
        output_dir: Diretório de saída
        initial_capital: Capital inicial
        stake_strategy: Estratégia de stake
        stake_percentage: Percentual de stake
        min_confidence: Confiança mínima
        max_confidence: Confiança máxima
        
    Returns:
        True se executado com sucesso
    """
    try:
        logger.info("🚀 Iniciando validação completa do MaraBet AI")
        
        # Criar diretório de saída
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Executar Backtesting
        logger.info("📊 Executando backtesting...")
        engine = BacktestingEngine(
            initial_capital=initial_capital,
            stake_strategy=stake_strategy,
            stake_percentage=stake_percentage,
            min_confidence=min_confidence,
            max_confidence=max_confidence
        )
        
        if not engine.load_historical_data(matches_file, predictions_file, odds_file):
            logger.error("❌ Erro ao carregar dados históricos")
            return False
        
        results = engine.run_backtest()
        
        # Salvar resultados do backtesting
        engine.save_results(f"{output_dir}/backtest_results.json")
        
        # 2. Análise de Performance
        logger.info("📈 Executando análise de performance...")
        performance_analyzer = PerformanceAnalyzer(results, engine.bet_records)
        performance_report = performance_analyzer.generate_performance_report()
        
        # Salvar relatório de performance
        performance_analyzer.export_report(f"{output_dir}/performance_report.json")
        
        # Criar visualizações
        performance_analyzer.create_visualizations(f"{output_dir}/charts")
        
        # 3. Relatório de Transparência
        logger.info("🔍 Gerando relatório de transparência...")
        transparency_reporter = TransparencyReporter(results, engine.bet_records)
        public_report = transparency_reporter.generate_public_report()
        
        # Salvar relatório público
        transparency_reporter.export_public_report(f"{output_dir}/public_report.json")
        
        # Criar dashboard público
        transparency_reporter.create_public_dashboard(f"{output_dir}/public_dashboard")
        
        # 4. Análise de ROI
        logger.info("💰 Executando análise de ROI...")
        roi_calculator = ROICalculator(initial_capital)
        roi_calculator.load_data(engine.bet_records)
        roi_report = roi_calculator.generate_roi_report()
        
        # Salvar relatório de ROI
        roi_calculator.export_roi_report(f"{output_dir}/roi_report.json")
        
        # 5. Análise de Ligas
        logger.info("🏆 Executando análise de ligas...")
        league_analyzer = LeagueAnalyzer()
        league_analyzer.load_data(engine.bet_records)
        league_analyzer.analyze_all_leagues()
        
        # Salvar relatório de ligas
        league_analyzer.export_league_report(f"{output_dir}/league_report.json")
        
        # 6. Gerar Relatório Consolidado
        logger.info("📋 Gerando relatório consolidado...")
        consolidated_report = generate_consolidated_report(
            results, performance_report, public_report, roi_report, league_analyzer
        )
        
        # Salvar relatório consolidado
        save_consolidated_report(consolidated_report, f"{output_dir}/consolidated_report.json")
        
        # 7. Gerar Relatório HTML
        logger.info("🌐 Gerando relatório HTML...")
        generate_html_report(consolidated_report, f"{output_dir}/validation_report.html")
        
        logger.info("✅ Validação completa concluída com sucesso!")
        logger.info(f"📁 Resultados salvos em: {output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na validação completa: {e}")
        return False

def generate_consolidated_report(
    backtest_results,
    performance_report,
    public_report,
    roi_report,
    league_analyzer
) -> dict:
    """Gera relatório consolidado"""
    try:
        return {
            'report_info': {
                'title': 'Relatório Consolidado de Validação - MaraBet AI',
                'generated_at': datetime.now().isoformat(),
                'version': '1.0'
            },
            'executive_summary': {
                'total_roi': backtest_results.total_roi,
                'win_rate': backtest_results.win_rate,
                'total_bets': backtest_results.total_bets,
                'total_profit': backtest_results.total_profit,
                'sharpe_ratio': backtest_results.sharpe_ratio,
                'max_drawdown': backtest_results.max_drawdown,
                'performance_rating': public_report.get('executive_summary', {}).get('performance_rating', 'N/A')
            },
            'backtest_results': {
                'period': {
                    'start_date': backtest_results.start_date.isoformat(),
                    'end_date': backtest_results.end_date.isoformat()
                },
                'financial_metrics': {
                    'total_stake': backtest_results.total_stake,
                    'total_profit': backtest_results.total_profit,
                    'total_roi': backtest_results.total_roi,
                    'average_odds': backtest_results.average_odds
                },
                'performance_metrics': {
                    'win_rate': backtest_results.win_rate,
                    'sharpe_ratio': backtest_results.sharpe_ratio,
                    'max_drawdown': backtest_results.max_drawdown,
                    'profit_factor': backtest_results.profit_factor
                }
            },
            'monthly_analysis': performance_report.get('monthly_analysis', {}),
            'league_analysis': league_analyzer.get_league_summary(),
            'roi_analysis': roi_report.get('basic_metrics', {}),
            'risk_analysis': performance_report.get('risk_metrics', {}),
            'recommendations': performance_report.get('recommendations', []),
            'transparency_metrics': public_report.get('performance_metrics', {}),
            'methodology': public_report.get('methodology', {}),
            'disclaimers': public_report.get('disclaimers', [])
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório consolidado: {e}")
        return {}

def save_consolidated_report(report: dict, output_file: str) -> bool:
    """Salva relatório consolidado"""
    try:
        import json
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✅ Relatório consolidado salvo em {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar relatório consolidado: {e}")
        return False

def generate_html_report(report: dict, output_file: str) -> bool:
    """Gera relatório HTML"""
    try:
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report['report_info']['title']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        .header h1 {{
            color: #667eea;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.2em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 0;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .chart-placeholder {{
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            color: #6c757d;
        }}
        .recommendations {{
            background: #e8f5e8;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }}
        .recommendations h3 {{
            color: #28a745;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .disclaimers {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
        }}
        .disclaimers h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .disclaimers ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{report['report_info']['title']}</h1>
            <p>Relatório de Validação e Transparência</p>
            <p>Gerado em: {report['report_info']['generated_at']}</p>
        </div>
        
        <div class="summary">
            <div class="metric-card">
                <h3>ROI Total</h3>
                <div class="value">{report['executive_summary']['total_roi']:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Taxa de Acerto</h3>
                <div class="value">{report['executive_summary']['win_rate']:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Total de Apostas</h3>
                <div class="value">{report['executive_summary']['total_bets']:,}</div>
            </div>
            <div class="metric-card">
                <h3>Lucro Total</h3>
                <div class="value">R$ {report['executive_summary']['total_profit']:,.2f}</div>
            </div>
            <div class="metric-card">
                <h3>Sharpe Ratio</h3>
                <div class="value">{report['executive_summary']['sharpe_ratio']:.2f}</div>
            </div>
            <div class="metric-card">
                <h3>Classificação</h3>
                <div class="value">{report['executive_summary']['performance_rating']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Métricas Financeiras</h2>
            <p><strong>Período:</strong> {report['backtest_results']['period']['start_date']} a {report['backtest_results']['period']['end_date']}</p>
            <p><strong>Total Apostado:</strong> R$ {report['backtest_results']['financial_metrics']['total_stake']:,.2f}</p>
            <p><strong>Lucro Total:</strong> R$ {report['backtest_results']['financial_metrics']['total_profit']:,.2f}</p>
            <p><strong>ROI Total:</strong> {report['backtest_results']['financial_metrics']['total_roi']:.2f}%</p>
            <p><strong>Odds Médias:</strong> {report['backtest_results']['financial_metrics']['average_odds']:.2f}</p>
        </div>
        
        <div class="section">
            <h2>📈 Métricas de Performance</h2>
            <p><strong>Taxa de Acerto:</strong> {report['backtest_results']['performance_metrics']['win_rate']:.2f}%</p>
            <p><strong>Sharpe Ratio:</strong> {report['backtest_results']['performance_metrics']['sharpe_ratio']:.3f}</p>
            <p><strong>Maximum Drawdown:</strong> R$ {report['backtest_results']['performance_metrics']['max_drawdown']:,.2f}</p>
            <p><strong>Profit Factor:</strong> {report['backtest_results']['performance_metrics']['profit_factor']:.2f}</p>
        </div>
        
        <div class="section">
            <h2>🏆 Análise de Ligas</h2>
            <p><strong>Total de Ligas:</strong> {report['league_analysis']['overview']['total_leagues']}</p>
            <p><strong>Ligas Lucrativas:</strong> {report['league_analysis']['overview']['profitable_leagues']} ({report['league_analysis']['overview']['profitability_rate']:.1f}%)</p>
            <p><strong>Ligas Altamente Lucrativas:</strong> {report['league_analysis']['overview']['highly_profitable_leagues']} ({report['league_analysis']['overview']['high_profitability_rate']:.1f}%)</p>
            <p><strong>Melhor Liga (ROI):</strong> {report['league_analysis']['best_performers']['best_roi']['league']} ({report['league_analysis']['best_performers']['best_roi']['roi']:.1f}%)</p>
        </div>
        
        <div class="section">
            <h2>💰 Análise de ROI</h2>
            <p><strong>ROI Anualizado:</strong> {report['roi_analysis'].get('annualized_roi', 'N/A')}%</p>
            <p><strong>ROI Composto:</strong> {report['roi_analysis'].get('compound_roi', 'N/A')}%</p>
            <p><strong>ROI Ajustado ao Risco:</strong> {report['roi_analysis'].get('risk_adjusted_roi', 'N/A')}%</p>
        </div>
        
        <div class="section">
            <h2>📊 Gráficos e Visualizações</h2>
            <div class="chart-placeholder">
                <p>📈 Gráficos de performance disponíveis na pasta 'charts'</p>
                <p>🌐 Dashboard público disponível na pasta 'public_dashboard'</p>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Recomendações</h2>
            <div class="recommendations">
                <h3>Insights e Sugestões</h3>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report.get('recommendations', []))}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Avisos Legais</h2>
            <div class="disclaimers">
                <h3>Importante</h3>
                <ul>
                    {''.join(f'<li>{disclaimer}</li>' for disclaimer in report.get('disclaimers', []))}
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Relatório gerado automaticamente pelo MaraBet AI</p>
            <p>Para mais informações, consulte os arquivos JSON detalhados</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Relatório HTML gerado em {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório HTML: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Validação Completa - MaraBet AI")
    parser.add_argument("--matches", required=True, help="Arquivo com dados de partidas")
    parser.add_argument("--predictions", required=True, help="Arquivo com predições")
    parser.add_argument("--odds", required=True, help="Arquivo com odds")
    parser.add_argument("--output", default="validation/results", help="Diretório de saída")
    parser.add_argument("--capital", type=float, default=10000.0, help="Capital inicial")
    parser.add_argument("--stake-strategy", choices=["fixed", "percentage", "kelly"], 
                       default="percentage", help="Estratégia de stake")
    parser.add_argument("--stake-percentage", type=float, default=0.02, 
                       help="Percentual de stake")
    parser.add_argument("--min-confidence", type=float, default=0.6, 
                       help="Confiança mínima")
    parser.add_argument("--max-confidence", type=float, default=0.95, 
                       help="Confiança máxima")
    
    args = parser.parse_args()
    
    # Verificar se arquivos existem
    for file_path in [args.matches, args.predictions, args.odds]:
        if not os.path.exists(file_path):
            logger.error(f"❌ Arquivo não encontrado: {file_path}")
            sys.exit(1)
    
    # Executar validação
    success = run_complete_validation(
        matches_file=args.matches,
        predictions_file=args.predictions,
        odds_file=args.odds,
        output_dir=args.output,
        initial_capital=args.capital,
        stake_strategy=args.stake_strategy,
        stake_percentage=args.stake_percentage,
        min_confidence=args.min_confidence,
        max_confidence=args.max_confidence
    )
    
    if success:
        logger.info("🎉 Validação concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Validação falhou")
        sys.exit(1)

if __name__ == "__main__":
    main()
