"""
Visualizador de Confiança - MaraBet AI
Visualizações avançadas de intervalos de confiança e incerteza
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Any, Optional, Tuple
import warnings

from .confidence_calculator import ConfidenceInterval, PredictionUncertainty

logger = logging.getLogger(__name__)

class ConfidenceVisualizer:
    """
    Visualizador de intervalos de confiança para MaraBet AI
    Cria visualizações interativas e estáticas
    """
    
    def __init__(self, style: str = "seaborn-v0_8"):
        """
        Inicializa o visualizador
        
        Args:
            style: Estilo do matplotlib
        """
        self.style = style
        plt.style.use(style)
        sns.set_palette("husl")
        
        logger.info("ConfidenceVisualizer inicializado")
    
    def create_confidence_interval_plot(self,
                                      intervals: Dict[float, ConfidenceInterval],
                                      title: str = "Intervalos de Confiança",
                                      output_file: Optional[str] = None,
                                      interactive: bool = False) -> bool:
        """
        Cria gráfico de intervalos de confiança
        
        Args:
            intervals: Dicionário com intervalos por nível de confiança
            title: Título do gráfico
            output_file: Arquivo de saída (opcional)
            interactive: Se deve criar versão interativa
            
        Returns:
            True se criado com sucesso
        """
        try:
            if interactive:
                return self._create_interactive_confidence_plot(intervals, title, output_file)
            else:
                return self._create_static_confidence_plot(intervals, title, output_file)
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de confiança: {e}")
            return False
    
    def _create_static_confidence_plot(self,
                                     intervals: Dict[float, ConfidenceInterval],
                                     title: str,
                                     output_file: Optional[str]) -> bool:
        """Cria gráfico estático de intervalos de confiança"""
        try:
            if not intervals:
                logger.warning("⚠️ Nenhum intervalo para visualizar")
                return False
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Ordenar intervalos por nível de confiança
            sorted_intervals = sorted(intervals.items(), key=lambda x: x[0])
            
            # Cores para diferentes níveis de confiança
            colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_intervals)))
            
            # Plotar intervalos
            for i, (level, interval) in enumerate(sorted_intervals):
                confidence_pct = level * 100
                width = interval.upper_bound - interval.lower_bound
                
                # Barra horizontal para o intervalo
                ax.barh(i, width, left=interval.lower_bound, 
                       height=0.6, alpha=0.7, color=colors[i],
                       label=f'{confidence_pct:.0f}% CI')
                
                # Linha vertical para a previsão
                ax.axvline(interval.prediction, ymin=i-0.3, ymax=i+0.3, 
                          color='red', linewidth=2, alpha=0.8)
                
                # Adicionar texto com valores
                ax.text(interval.prediction, i, 
                       f'{interval.prediction:.3f}', 
                       ha='center', va='center', fontweight='bold')
            
            # Configurar eixo Y
            ax.set_yticks(range(len(sorted_intervals)))
            ax.set_yticklabels([f'{level*100:.0f}%' for level, _ in sorted_intervals])
            ax.set_ylabel('Nível de Confiança')
            ax.set_xlabel('Valor da Previsão')
            ax.set_title(title, fontweight='bold', fontsize=14)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Gráfico salvo em {output_file}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico estático: {e}")
            return False
    
    def _create_interactive_confidence_plot(self,
                                          intervals: Dict[float, ConfidenceInterval],
                                          title: str,
                                          output_file: Optional[str]) -> bool:
        """Cria gráfico interativo de intervalos de confiança"""
        try:
            if not intervals:
                logger.warning("⚠️ Nenhum intervalo para visualizar")
                return False
            
            # Criar figura
            fig = go.Figure()
            
            # Ordenar intervalos por nível de confiança
            sorted_intervals = sorted(intervals.items(), key=lambda x: x[0])
            
            # Adicionar intervalos
            for level, interval in sorted_intervals:
                confidence_pct = level * 100
                
                # Adicionar intervalo como barra
                fig.add_trace(go.Bar(
                    y=[f'{confidence_pct:.0f}%'],
                    x=[interval.upper_bound - interval.lower_bound],
                    base=[interval.lower_bound],
                    orientation='h',
                    name=f'{confidence_pct:.0f}% CI',
                    text=[f'{interval.prediction:.3f}'],
                    textposition='inside',
                    hovertemplate=f'<b>{confidence_pct:.0f}% CI</b><br>' +
                                f'Previsão: {interval.prediction:.3f}<br>' +
                                f'Limite Inferior: {interval.lower_bound:.3f}<br>' +
                                f'Limite Superior: {interval.upper_bound:.3f}<br>' +
                                f'Margem de Erro: ±{interval.margin_of_error:.3f}<extra></extra>'
                ))
                
                # Adicionar linha da previsão
                fig.add_vline(
                    x=interval.prediction,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"{interval.prediction:.3f}",
                    annotation_position="top"
                )
            
            # Configurar layout
            fig.update_layout(
                title=title,
                xaxis_title="Valor da Previsão",
                yaxis_title="Nível de Confiança",
                showlegend=True,
                height=600,
                width=1000,
                template="plotly_white"
            )
            
            if output_file:
                fig.write_html(output_file)
                logger.info(f"✅ Gráfico interativo salvo em {output_file}")
            else:
                fig.show()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico interativo: {e}")
            return False
    
    def create_uncertainty_heatmap(self,
                                 uncertainty_data: List[PredictionUncertainty],
                                 title: str = "Mapa de Calor de Incerteza",
                                 output_file: Optional[str] = None) -> bool:
        """
        Cria mapa de calor de incerteza
        
        Args:
            uncertainty_data: Lista de dados de incerteza
            title: Título do gráfico
            output_file: Arquivo de saída (opcional)
            
        Returns:
            True se criado com sucesso
        """
        try:
            if not uncertainty_data:
                logger.warning("⚠️ Nenhum dado de incerteza para visualizar")
                return False
            
            # Extrair dados
            uncertainty_scores = [u.uncertainty_score for u in uncertainty_data]
            reliability_scores = [u.reliability_score for u in uncertainty_data]
            calibration_scores = [u.calibration_score for u in uncertainty_data]
            
            # Criar matriz de dados
            data_matrix = np.array([uncertainty_scores, reliability_scores, calibration_scores])
            
            # Criar heatmap
            fig, ax = plt.subplots(figsize=(12, 8))
            
            im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto')
            
            # Configurar eixos
            ax.set_xticks(range(len(uncertainty_data)))
            ax.set_yticks(range(3))
            ax.set_yticklabels(['Incerteza', 'Confiabilidade', 'Calibração'])
            ax.set_xlabel('Índice da Previsão')
            ax.set_title(title, fontweight='bold')
            
            # Adicionar barra de cores
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Score (0-100)', rotation=270, labelpad=20)
            
            # Adicionar valores nas células
            for i in range(3):
                for j in range(len(uncertainty_data)):
                    text = ax.text(j, i, f'{data_matrix[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontweight='bold')
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Heatmap salvo em {output_file}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar heatmap: {e}")
            return False
    
    def create_confidence_fan_chart(self,
                                  predictions: List[float],
                                  confidence_levels: List[float] = [0.68, 0.80, 0.90, 0.95, 0.99],
                                  title: str = "Gráfico de Leque de Confiança",
                                  output_file: Optional[str] = None) -> bool:
        """
        Cria gráfico de leque de confiança (fan chart)
        
        Args:
            predictions: Lista de previsões
            confidence_levels: Níveis de confiança
            title: Título do gráfico
            output_file: Arquivo de saída (opcional)
            
        Returns:
            True se criado com sucesso
        """
        try:
            if not predictions:
                logger.warning("⚠️ Nenhuma previsão para visualizar")
                return False
            
            # Calcular intervalos para cada previsão
            from .confidence_calculator import ConfidenceCalculator
            calculator = ConfidenceCalculator()
            
            all_intervals = []
            for pred in predictions:
                intervals = calculator.calculate_multiple_confidence_levels(
                    [pred], confidence_levels
                )
                all_intervals.append(intervals)
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(14, 8))
            
            x = np.arange(len(predictions))
            
            # Cores para diferentes níveis de confiança
            colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(confidence_levels)))
            
            # Plotar intervalos (do maior para o menor)
            for i, level in enumerate(reversed(confidence_levels)):
                upper_bounds = [intervals[level].upper_bound for intervals in all_intervals]
                lower_bounds = [intervals[level].lower_bound for intervals in all_intervals]
                
                ax.fill_between(x, lower_bounds, upper_bounds, 
                               alpha=0.3, color=colors[i],
                               label=f'{level*100:.0f}% CI')
            
            # Plotar previsões
            ax.plot(x, predictions, 'ro-', linewidth=2, markersize=6, 
                   label='Previsões', color='red')
            
            # Configurar gráfico
            ax.set_xlabel('Índice da Previsão')
            ax.set_ylabel('Valor da Previsão')
            ax.set_title(title, fontweight='bold')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Fan chart salvo em {output_file}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar fan chart: {e}")
            return False
    
    def create_uncertainty_dashboard(self,
                                   uncertainty_data: List[PredictionUncertainty],
                                   title: str = "Dashboard de Incerteza",
                                   output_file: Optional[str] = None) -> bool:
        """
        Cria dashboard completo de incerteza
        
        Args:
            uncertainty_data: Lista de dados de incerteza
            title: Título do dashboard
            output_file: Arquivo de saída (opcional)
            
        Returns:
            True se criado com sucesso
        """
        try:
            if not uncertainty_data:
                logger.warning("⚠️ Nenhum dado de incerteza para visualizar")
                return False
            
            # Criar subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Distribuição de incerteza
            uncertainty_scores = [u.uncertainty_score for u in uncertainty_data]
            ax1.hist(uncertainty_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.axvline(np.mean(uncertainty_scores), color='red', linestyle='--', 
                       label=f'Média: {np.mean(uncertainty_scores):.1f}')
            ax1.set_title('Distribuição de Incerteza', fontweight='bold')
            ax1.set_xlabel('Score de Incerteza')
            ax1.set_ylabel('Frequência')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. Distribuição de confiabilidade
            reliability_scores = [u.reliability_score for u in uncertainty_data]
            ax2.hist(reliability_scores, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
            ax2.axvline(np.mean(reliability_scores), color='red', linestyle='--', 
                       label=f'Média: {np.mean(reliability_scores):.1f}')
            ax2.set_title('Distribuição de Confiabilidade', fontweight='bold')
            ax2.set_xlabel('Score de Confiabilidade')
            ax2.set_ylabel('Frequência')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. Scatter plot: Incerteza vs Confiabilidade
            ax3.scatter(uncertainty_scores, reliability_scores, alpha=0.6, s=50)
            ax3.set_xlabel('Score de Incerteza')
            ax3.set_ylabel('Score de Confiabilidade')
            ax3.set_title('Incerteza vs Confiabilidade', fontweight='bold')
            ax3.grid(True, alpha=0.3)
            
            # Adicionar linha de correlação
            z = np.polyfit(uncertainty_scores, reliability_scores, 1)
            p = np.poly1d(z)
            ax3.plot(uncertainty_scores, p(uncertainty_scores), "r--", alpha=0.8)
            
            # 4. Métricas resumidas
            calibration_scores = [u.calibration_score for u in uncertainty_data]
            
            metrics_text = f"""
            Métricas Resumidas:
            
            Incerteza Média: {np.mean(uncertainty_scores):.1f}
            Confiabilidade Média: {np.mean(reliability_scores):.1f}
            Calibração Média: {np.mean(calibration_scores):.1f}
            
            Desvio Padrão Incerteza: {np.std(uncertainty_scores):.1f}
            Desvio Padrão Confiabilidade: {np.std(reliability_scores):.1f}
            
            Total de Previsões: {len(uncertainty_data)}
            """
            
            ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, 
                    fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            ax4.set_title('Métricas Resumidas', fontweight='bold')
            ax4.axis('off')
            
            # Título geral
            fig.suptitle(title, fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Dashboard salvo em {output_file}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar dashboard: {e}")
            return False
    
    def create_interactive_uncertainty_plot(self,
                                          uncertainty_data: List[PredictionUncertainty],
                                          title: str = "Visualização Interativa de Incerteza",
                                          output_file: Optional[str] = None) -> bool:
        """
        Cria visualização interativa de incerteza
        
        Args:
            uncertainty_data: Lista de dados de incerteza
            title: Título da visualização
            output_file: Arquivo de saída (opcional)
            
        Returns:
            True se criado com sucesso
        """
        try:
            if not uncertainty_data:
                logger.warning("⚠️ Nenhum dado de incerteza para visualizar")
                return False
            
            # Criar subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Distribuição de Incerteza', 'Distribuição de Confiabilidade',
                              'Incerteza vs Confiabilidade', 'Evolução Temporal'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Extrair dados
            uncertainty_scores = [u.uncertainty_score for u in uncertainty_data]
            reliability_scores = [u.reliability_score for u in uncertainty_data]
            calibration_scores = [u.calibration_score for u in uncertainty_data]
            
            # 1. Histograma de incerteza
            fig.add_trace(
                go.Histogram(x=uncertainty_scores, name='Incerteza', nbinsx=20),
                row=1, col=1
            )
            
            # 2. Histograma de confiabilidade
            fig.add_trace(
                go.Histogram(x=reliability_scores, name='Confiabilidade', nbinsx=20),
                row=1, col=2
            )
            
            # 3. Scatter plot
            fig.add_trace(
                go.Scatter(x=uncertainty_scores, y=reliability_scores, 
                          mode='markers', name='Incerteza vs Confiabilidade'),
                row=2, col=1
            )
            
            # 4. Evolução temporal
            x_vals = list(range(len(uncertainty_scores)))
            fig.add_trace(
                go.Scatter(x=x_vals, y=uncertainty_scores, mode='lines+markers', 
                          name='Incerteza Temporal'),
                row=2, col=2
            )
            fig.add_trace(
                go.Scatter(x=x_vals, y=reliability_scores, mode='lines+markers', 
                          name='Confiabilidade Temporal'),
                row=2, col=2
            )
            
            # Configurar layout
            fig.update_layout(
                title=title,
                showlegend=True,
                height=800,
                width=1200,
                template="plotly_white"
            )
            
            if output_file:
                fig.write_html(output_file)
                logger.info(f"✅ Visualização interativa salva em {output_file}")
            else:
                fig.show()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar visualização interativa: {e}")
            return False
    
    def create_confidence_comparison_plot(self,
                                        method_results: Dict[str, List[ConfidenceInterval]],
                                        title: str = "Comparação de Métodos de Confiança",
                                        output_file: Optional[str] = None) -> bool:
        """
        Cria gráfico de comparação de métodos de confiança
        
        Args:
            method_results: Resultados por método
            title: Título do gráfico
            output_file: Arquivo de saída (opcional)
            
        Returns:
            True se criado com sucesso
        """
        try:
            if not method_results:
                logger.warning("⚠️ Nenhum resultado de método para visualizar")
                return False
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            methods = list(method_results.keys())
            n_methods = len(methods)
            
            # Calcular métricas para cada método
            method_metrics = {}
            for method, intervals in method_results.items():
                if not intervals:
                    continue
                
                margins = [interval.margin_of_error for interval in intervals]
                predictions = [interval.prediction for interval in intervals]
                
                method_metrics[method] = {
                    'mean_margin': np.mean(margins),
                    'std_margin': np.std(margins),
                    'mean_prediction': np.mean(predictions),
                    'coverage': len([i for i in intervals if i.upper_bound > i.lower_bound]) / len(intervals)
                }
            
            # Criar gráfico de barras
            x = np.arange(n_methods)
            mean_margins = [method_metrics[method]['mean_margin'] for method in methods]
            std_margins = [method_metrics[method]['std_margin'] for method in methods]
            
            bars = ax.bar(x, mean_margins, yerr=std_margins, capsize=5, alpha=0.7)
            
            # Configurar gráfico
            ax.set_xlabel('Métodos')
            ax.set_ylabel('Margem de Erro Média')
            ax.set_title(title, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(methods, rotation=45)
            ax.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar, mean, std in zip(bars, mean_margins, std_margins):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                       f'{mean:.3f}±{std:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Gráfico de comparação salvo em {output_file}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de comparação: {e}")
            return False
