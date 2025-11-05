"""
Analisador de Ligas - MaraBet AI
Análise detalhada de performance por liga e competição
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class LeagueMetrics:
    """Métricas de uma liga específica"""
    league_name: str
    total_bets: int
    winning_bets: int
    losing_bets: int
    win_rate: float
    total_stake: float
    total_profit: float
    roi: float
    average_odds: float
    average_confidence: float
    best_month: str
    worst_month: str
    best_month_roi: float
    worst_month_roi: float
    consistency_score: float
    risk_score: float
    profitability_rating: str

class LeagueAnalyzer:
    """
    Analisador de performance por liga para MaraBet AI
    Análise detalhada de cada competição e liga
    """
    
    def __init__(self):
        """Inicializa o analisador de ligas"""
        self.df = None
        self.league_metrics: Dict[str, LeagueMetrics] = {}
        
        logger.info("LeagueAnalyzer inicializado")
    
    def load_data(self, bet_records: List[Any]) -> bool:
        """
        Carrega dados de apostas para análise
        
        Args:
            bet_records: Lista de registros de apostas
            
        Returns:
            True se carregado com sucesso
        """
        try:
            data = []
            for bet in bet_records:
                data.append({
                    'date': bet.date,
                    'league': bet.league,
                    'home_team': bet.home_team,
                    'away_team': bet.away_team,
                    'bet_type': bet.bet_type,
                    'prediction': bet.prediction,
                    'odds': bet.odds,
                    'stake': bet.stake,
                    'confidence': bet.confidence,
                    'actual_result': bet.actual_result,
                    'bet_result': bet.bet_result.value if bet.bet_result else None,
                    'profit_loss': bet.profit_loss,
                    'roi': bet.roi
                })
            
            self.df = pd.DataFrame(data)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['month'] = self.df['date'].dt.to_period('M')
            self.df['week'] = self.df['date'].dt.to_period('W')
            
            logger.info(f"✅ Dados carregados: {len(self.df)} registros, {self.df['league'].nunique()} ligas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analyze_all_leagues(self) -> Dict[str, LeagueMetrics]:
        """
        Analisa todas as ligas
        
        Returns:
            Dicionário com métricas de cada liga
        """
        try:
            if self.df is None or self.df.empty:
                logger.error("❌ Dados não carregados")
                return {}
            
            leagues = self.df['league'].unique()
            self.league_metrics = {}
            
            for league in leagues:
                league_data = self.df[self.df['league'] == league]
                metrics = self._analyze_league(league, league_data)
                self.league_metrics[league] = metrics
            
            logger.info(f"✅ Análise concluída para {len(leagues)} ligas")
            return self.league_metrics
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar ligas: {e}")
            return {}
    
    def _analyze_league(self, league_name: str, league_data: pd.DataFrame) -> LeagueMetrics:
        """
        Analisa uma liga específica
        
        Args:
            league_name: Nome da liga
            league_data: Dados da liga
            
        Returns:
            Métricas da liga
        """
        try:
            # Métricas básicas
            total_bets = len(league_data)
            winning_bets = len(league_data[league_data['bet_result'] == 'win'])
            losing_bets = len(league_data[league_data['bet_result'] == 'loss'])
            win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0
            
            # Métricas financeiras
            total_stake = league_data['stake'].sum()
            total_profit = league_data['profit_loss'].sum()
            roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
            
            # Métricas de qualidade
            average_odds = league_data['odds'].mean()
            average_confidence = league_data['confidence'].mean()
            
            # Análise mensal
            monthly_analysis = self._analyze_monthly_performance(league_data)
            best_month = monthly_analysis['best_month']
            worst_month = monthly_analysis['worst_month']
            best_month_roi = monthly_analysis['best_month_roi']
            worst_month_roi = monthly_analysis['worst_month_roi']
            
            # Scores de qualidade
            consistency_score = self._calculate_consistency_score(league_data)
            risk_score = self._calculate_risk_score(league_data)
            profitability_rating = self._calculate_profitability_rating(roi, win_rate, consistency_score)
            
            return LeagueMetrics(
                league_name=league_name,
                total_bets=total_bets,
                winning_bets=winning_bets,
                losing_bets=losing_bets,
                win_rate=round(win_rate, 2),
                total_stake=round(total_stake, 2),
                total_profit=round(total_profit, 2),
                roi=round(roi, 2),
                average_odds=round(average_odds, 2),
                average_confidence=round(average_confidence, 3),
                best_month=best_month,
                worst_month=worst_month,
                best_month_roi=round(best_month_roi, 2),
                worst_month_roi=round(worst_month_roi, 2),
                consistency_score=round(consistency_score, 2),
                risk_score=round(risk_score, 2),
                profitability_rating=profitability_rating
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar liga {league_name}: {e}")
            return self._empty_league_metrics(league_name)
    
    def _analyze_monthly_performance(self, league_data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa performance mensal de uma liga"""
        try:
            monthly_data = league_data.groupby('month').agg({
                'stake': 'sum',
                'profit_loss': 'sum'
            })
            
            monthly_roi = {}
            for month, row in monthly_data.iterrows():
                if row['stake'] > 0:
                    roi = (row['profit_loss'] / row['stake']) * 100
                    monthly_roi[str(month)] = roi
                else:
                    monthly_roi[str(month)] = 0.0
            
            if monthly_roi:
                best_month = max(monthly_roi.items(), key=lambda x: x[1])[0]
                worst_month = min(monthly_roi.items(), key=lambda x: x[1])[0]
                best_month_roi = monthly_roi[best_month]
                worst_month_roi = monthly_roi[worst_month]
            else:
                best_month = ""
                worst_month = ""
                best_month_roi = 0.0
                worst_month_roi = 0.0
            
            return {
                'best_month': best_month,
                'worst_month': worst_month,
                'best_month_roi': best_month_roi,
                'worst_month_roi': worst_month_roi,
                'monthly_roi': monthly_roi
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar performance mensal: {e}")
            return {
                'best_month': "",
                'worst_month': "",
                'best_month_roi': 0.0,
                'worst_month_roi': 0.0,
                'monthly_roi': {}
            }
    
    def _calculate_consistency_score(self, league_data: pd.DataFrame) -> float:
        """Calcula score de consistência de uma liga"""
        try:
            if league_data.empty:
                return 0.0
            
            # Calcular ROI mensal
            monthly_data = league_data.groupby('month').agg({
                'stake': 'sum',
                'profit_loss': 'sum'
            })
            
            monthly_rois = []
            for month, row in monthly_data.iterrows():
                if row['stake'] > 0:
                    roi = (row['profit_loss'] / row['stake']) * 100
                    monthly_rois.append(roi)
            
            if len(monthly_rois) < 2:
                return 0.0
            
            # Score baseado na consistência (menor desvio padrão = maior score)
            roi_std = np.std(monthly_rois)
            roi_mean = np.mean(monthly_rois)
            
            if roi_mean == 0:
                return 0.0
            
            # Score de 0 a 100 (100 = perfeitamente consistente)
            consistency_score = max(0, 100 - (roi_std / abs(roi_mean)) * 100)
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular score de consistência: {e}")
            return 0.0
    
    def _calculate_risk_score(self, league_data: pd.DataFrame) -> float:
        """Calcula score de risco de uma liga"""
        try:
            if league_data.empty:
                return 100.0  # Máximo risco se não há dados
            
            # Calcular volatilidade dos retornos
            returns = league_data['profit_loss'] / league_data['stake'] * 100
            volatility = returns.std()
            
            # Calcular drawdown máximo
            cumulative_returns = returns.cumsum()
            running_max = cumulative_returns.expanding().max()
            drawdown = running_max - cumulative_returns
            max_drawdown = drawdown.max()
            
            # Score de risco (0 = baixo risco, 100 = alto risco)
            volatility_score = min(100, volatility * 10)  # Escalar volatilidade
            drawdown_score = min(100, max_drawdown * 2)   # Escalar drawdown
            
            risk_score = (volatility_score + drawdown_score) / 2
            
            return risk_score
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular score de risco: {e}")
            return 50.0
    
    def _calculate_profitability_rating(self, roi: float, win_rate: float, consistency: float) -> str:
        """Calcula classificação de lucratividade"""
        try:
            # Score composto baseado em ROI, win rate e consistência
            roi_score = min(100, max(0, roi * 2))  # ROI * 2, limitado a 100
            win_rate_score = min(100, win_rate * 1.5)  # Win rate * 1.5, limitado a 100
            consistency_score = consistency  # Já está em 0-100
            
            # Peso: ROI 50%, Win Rate 30%, Consistência 20%
            composite_score = (roi_score * 0.5) + (win_rate_score * 0.3) + (consistency_score * 0.2)
            
            if composite_score >= 80:
                return "EXCELENTE"
            elif composite_score >= 65:
                return "MUITO BOM"
            elif composite_score >= 50:
                return "BOM"
            elif composite_score >= 35:
                return "REGULAR"
            else:
                return "NECESSITA MELHORIAS"
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular classificação de lucratividade: {e}")
            return "N/A"
    
    def get_league_rankings(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtém rankings de ligas por diferentes métricas
        
        Returns:
            Rankings por diferentes critérios
        """
        try:
            if not self.league_metrics:
                return {}
            
            # Converter para lista para ordenação
            leagues_list = list(self.league_metrics.values())
            
            # Ranking por ROI
            roi_ranking = sorted(leagues_list, key=lambda x: x.roi, reverse=True)
            roi_ranking_data = []
            for i, league in enumerate(roi_ranking, 1):
                roi_ranking_data.append({
                    'rank': i,
                    'league': league.league_name,
                    'roi': league.roi,
                    'total_bets': league.total_bets,
                    'win_rate': league.win_rate
                })
            
            # Ranking por Win Rate
            win_rate_ranking = sorted(leagues_list, key=lambda x: x.win_rate, reverse=True)
            win_rate_ranking_data = []
            for i, league in enumerate(win_rate_ranking, 1):
                win_rate_ranking_data.append({
                    'rank': i,
                    'league': league.league_name,
                    'win_rate': league.win_rate,
                    'roi': league.roi,
                    'total_bets': league.total_bets
                })
            
            # Ranking por Consistência
            consistency_ranking = sorted(leagues_list, key=lambda x: x.consistency_score, reverse=True)
            consistency_ranking_data = []
            for i, league in enumerate(consistency_ranking, 1):
                consistency_ranking_data.append({
                    'rank': i,
                    'league': league.league_name,
                    'consistency_score': league.consistency_score,
                    'roi': league.roi,
                    'risk_score': league.risk_score
                })
            
            # Ranking por Baixo Risco
            low_risk_ranking = sorted(leagues_list, key=lambda x: x.risk_score)
            low_risk_ranking_data = []
            for i, league in enumerate(low_risk_ranking, 1):
                low_risk_ranking_data.append({
                    'rank': i,
                    'league': league.league_name,
                    'risk_score': league.risk_score,
                    'roi': league.roi,
                    'consistency_score': league.consistency_score
                })
            
            # Ranking por Volume de Apostas
            volume_ranking = sorted(leagues_list, key=lambda x: x.total_bets, reverse=True)
            volume_ranking_data = []
            for i, league in enumerate(volume_ranking, 1):
                volume_ranking_data.append({
                    'rank': i,
                    'league': league.league_name,
                    'total_bets': league.total_bets,
                    'roi': league.roi,
                    'total_stake': league.total_stake
                })
            
            return {
                'by_roi': roi_ranking_data,
                'by_win_rate': win_rate_ranking_data,
                'by_consistency': consistency_ranking_data,
                'by_low_risk': low_risk_ranking_data,
                'by_volume': volume_ranking_data
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar rankings: {e}")
            return {}
    
    def get_league_insights(self) -> Dict[str, List[str]]:
        """
        Gera insights sobre as ligas
        
        Returns:
            Insights por liga
        """
        try:
            insights = {}
            
            for league_name, metrics in self.league_metrics.items():
                league_insights = []
                
                # Insight sobre ROI
                if metrics.roi > 15:
                    league_insights.append(f"🎯 ROI excepcional de {metrics.roi:.1f}% - Liga altamente lucrativa")
                elif metrics.roi > 10:
                    league_insights.append(f"📈 ROI sólido de {metrics.roi:.1f}% - Boa performance")
                elif metrics.roi > 5:
                    league_insights.append(f"📊 ROI positivo de {metrics.roi:.1f}% - Performance adequada")
                elif metrics.roi > 0:
                    league_insights.append(f"⚠️ ROI baixo de {metrics.roi:.1f}% - Necessita otimização")
                else:
                    league_insights.append(f"❌ ROI negativo de {metrics.roi:.1f}% - Revisar estratégia")
                
                # Insight sobre Win Rate
                if metrics.win_rate > 70:
                    league_insights.append(f"🏆 Alta taxa de acerto de {metrics.win_rate:.1f}% - Modelo muito preciso")
                elif metrics.win_rate > 60:
                    league_insights.append(f"✅ Boa taxa de acerto de {metrics.win_rate:.1f}% - Modelo confiável")
                elif metrics.win_rate > 50:
                    league_insights.append(f"📊 Taxa de acerto de {metrics.win_rate:.1f}% - Acima da média")
                else:
                    league_insights.append(f"🔍 Taxa de acerto de {metrics.win_rate:.1f}% - Melhorar seleção")
                
                # Insight sobre Consistência
                if metrics.consistency_score > 80:
                    league_insights.append(f"🛡️ Alta consistência ({metrics.consistency_score:.0f}/100) - Performance estável")
                elif metrics.consistency_score > 60:
                    league_insights.append(f"📊 Consistência moderada ({metrics.consistency_score:.0f}/100) - Alguma variabilidade")
                else:
                    league_insights.append(f"⚠️ Baixa consistência ({metrics.consistency_score:.0f}/100) - Alta variabilidade")
                
                # Insight sobre Risco
                if metrics.risk_score < 30:
                    league_insights.append(f"🛡️ Baixo risco ({metrics.risk_score:.0f}/100) - Investimento seguro")
                elif metrics.risk_score < 60:
                    league_insights.append(f"📊 Risco moderado ({metrics.risk_score:.0f}/100) - Equilíbrio risco/retorno")
                else:
                    league_insights.append(f"⚠️ Alto risco ({metrics.risk_score:.0f}/100) - Cuidado com volatilidade")
                
                # Insight sobre Volume
                if metrics.total_bets > 100:
                    league_insights.append(f"📈 Alto volume ({metrics.total_bets} apostas) - Dados confiáveis")
                elif metrics.total_bets > 50:
                    league_insights.append(f"📊 Volume moderado ({metrics.total_bets} apostas) - Dados adequados")
                else:
                    league_insights.append(f"🔍 Baixo volume ({metrics.total_bets} apostas) - Dados limitados")
                
                # Insight sobre Classificação
                league_insights.append(f"🏅 Classificação: {metrics.profitability_rating}")
                
                insights[league_name] = league_insights
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar insights: {e}")
            return {}
    
    def get_league_summary(self) -> Dict[str, Any]:
        """
        Gera resumo geral das ligas
        
        Returns:
            Resumo estatístico das ligas
        """
        try:
            if not self.league_metrics:
                return {}
            
            leagues_list = list(self.league_metrics.values())
            
            # Estatísticas gerais
            total_leagues = len(leagues_list)
            profitable_leagues = len([l for l in leagues_list if l.roi > 0])
            highly_profitable = len([l for l in leagues_list if l.roi > 10])
            
            # Métricas agregadas
            total_bets = sum(l.total_bets for l in leagues_list)
            total_stake = sum(l.total_stake for l in leagues_list)
            total_profit = sum(l.total_profit for l in leagues_list)
            avg_roi = np.mean([l.roi for l in leagues_list])
            avg_win_rate = np.mean([l.win_rate for l in leagues_list])
            avg_consistency = np.mean([l.consistency_score for l in leagues_list])
            avg_risk = np.mean([l.risk_score for l in leagues_list])
            
            # Melhores e piores
            best_roi_league = max(leagues_list, key=lambda x: x.roi)
            worst_roi_league = min(leagues_list, key=lambda x: x.roi)
            most_consistent = max(leagues_list, key=lambda x: x.consistency_score)
            least_risky = min(leagues_list, key=lambda x: x.risk_score)
            
            return {
                'overview': {
                    'total_leagues': total_leagues,
                    'profitable_leagues': profitable_leagues,
                    'highly_profitable_leagues': highly_profitable,
                    'profitability_rate': round((profitable_leagues / total_leagues) * 100, 1),
                    'high_profitability_rate': round((highly_profitable / total_leagues) * 100, 1)
                },
                'aggregate_metrics': {
                    'total_bets': total_bets,
                    'total_stake': round(total_stake, 2),
                    'total_profit': round(total_profit, 2),
                    'average_roi': round(avg_roi, 2),
                    'average_win_rate': round(avg_win_rate, 2),
                    'average_consistency': round(avg_consistency, 2),
                    'average_risk': round(avg_risk, 2)
                },
                'best_performers': {
                    'best_roi': {
                        'league': best_roi_league.league_name,
                        'roi': best_roi_league.roi,
                        'bets': best_roi_league.total_bets
                    },
                    'most_consistent': {
                        'league': most_consistent.league_name,
                        'consistency': most_consistent.consistency_score,
                        'roi': most_consistent.roi
                    },
                    'least_risky': {
                        'league': least_risky.league_name,
                        'risk_score': least_risky.risk_score,
                        'roi': least_risky.roi
                    }
                },
                'worst_performers': {
                    'worst_roi': {
                        'league': worst_roi_league.league_name,
                        'roi': worst_roi_league.roi,
                        'bets': worst_roi_league.total_bets
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return {}
    
    def generate_league_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de ligas
        
        Returns:
            Relatório completo
        """
        try:
            rankings = self.get_league_rankings()
            insights = self.get_league_insights()
            summary = self.get_league_summary()
            
            return {
                'summary': summary,
                'rankings': rankings,
                'insights': insights,
                'detailed_metrics': {
                    league_name: {
                        'total_bets': metrics.total_bets,
                        'winning_bets': metrics.winning_bets,
                        'win_rate': metrics.win_rate,
                        'total_stake': metrics.total_stake,
                        'total_profit': metrics.total_profit,
                        'roi': metrics.roi,
                        'average_odds': metrics.average_odds,
                        'average_confidence': metrics.average_confidence,
                        'best_month': metrics.best_month,
                        'worst_month': metrics.worst_month,
                        'best_month_roi': metrics.best_month_roi,
                        'worst_month_roi': metrics.worst_month_roi,
                        'consistency_score': metrics.consistency_score,
                        'risk_score': metrics.risk_score,
                        'profitability_rating': metrics.profitability_rating
                    }
                    for league_name, metrics in self.league_metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório de ligas: {e}")
            return {}
    
    def _empty_league_metrics(self, league_name: str) -> LeagueMetrics:
        """Retorna métricas vazias para uma liga"""
        return LeagueMetrics(
            league_name=league_name,
            total_bets=0,
            winning_bets=0,
            losing_bets=0,
            win_rate=0.0,
            total_stake=0.0,
            total_profit=0.0,
            roi=0.0,
            average_odds=0.0,
            average_confidence=0.0,
            best_month="",
            worst_month="",
            best_month_roi=0.0,
            worst_month_roi=0.0,
            consistency_score=0.0,
            risk_score=100.0,
            profitability_rating="N/A"
        )
    
    def export_league_report(self, output_file: str) -> bool:
        """
        Exporta relatório de ligas
        
        Args:
            output_file: Arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            report = self.generate_league_report()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Relatório de ligas exportado para {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar relatório de ligas: {e}")
            return False
