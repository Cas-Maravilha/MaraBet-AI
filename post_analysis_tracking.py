"""
Acompanhamento e Análise Posterior - MaraBet AI
Sistema especializado para monitoramento durante o jogo e rastreamento de desempenho
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GamePhase:
    """Fase do jogo"""
    phase: str
    time_range: str
    observation: str
    action: str
    xg_live: float
    intensity: float
    status: str

@dataclass
class LearningRecord:
    """Registro para aprendizado"""
    match_id: str
    home_team: str
    away_team: str
    match_date: str
    prediction: str
    actual_result: str
    predicted_xg: float
    actual_xg: float
    impact_factors: List[str]
    lessons_learned: List[str]
    model_adjustments: List[str]
    accuracy: float
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    """Métricas de desempenho"""
    total_analyses: int
    correct_predictions: int
    accuracy_rate: float
    average_roi: float
    yield_rate: float
    max_positive_streak: int
    max_drawdown: float
    current_streak: int
    last_30_accuracy: float
    last_30_roi: float
    last_30_yield: float

@dataclass
class PostAnalysisTracking:
    """Acompanhamento e análise posterior"""
    home_team: str
    away_team: str
    match_date: str
    game_phases: List[GamePhase]
    learning_record: LearningRecord
    performance_metrics: PerformanceMetrics
    tracking_history: List[Dict]
    recommendations: List[str]
    last_updated: datetime

class PostAnalysisTracker:
    """
    Rastreador de Acompanhamento e Análise Posterior
    Sistema completo para monitoramento e aprendizado
    """
    
    def __init__(self):
        self.tracking_file = "tracking_history.json"
        self.learning_file = "learning_records.json"
        self.performance_file = "performance_metrics.json"
        self.game_phases = self._load_game_phases()
        self.learning_metrics = self._load_learning_metrics()
        
    def _load_game_phases(self) -> Dict[str, Dict]:
        """Carrega fases do jogo"""
        return {
            '0-20min': {
                'observation': 'Observar intensidade inicial',
                'action': 'Monitorar ritmo e pressão',
                'xg_threshold': 0.5,
                'intensity_threshold': 0.7
            },
            '20-45min': {
                'observation': 'Avaliar oportunidades criadas (xG live)',
                'action': 'Analisar qualidade das chances',
                'xg_threshold': 1.0,
                'intensity_threshold': 0.8
            },
            'HT': {
                'observation': 'Se 0-0 ou 1-0, considerar hedge parcial',
                'action': 'Avaliar necessidade de hedge',
                'xg_threshold': 1.5,
                'intensity_threshold': 0.6
            },
            '60min+': {
                'observation': 'Se 2+ gols, aposta já garantida',
                'action': 'Confirmar resultado da aposta',
                'xg_threshold': 2.0,
                'intensity_threshold': 0.9
            }
        }
    
    def _load_learning_metrics(self) -> Dict[str, List[str]]:
        """Carrega métricas de aprendizado"""
        return {
            'impact_factors': [
                'Lesões durante o jogo',
                'Expulsões e cartões',
                'Condições climáticas',
                'Mudanças táticas',
                'Motivação dos jogadores',
                'Decisões do árbitro',
                'Fadiga dos times',
                'Pressão da torcida'
            ],
            'lessons_learned': [
                'Importância da forma recente',
                'Impacto de jogadores-chave',
                'Relevância do contexto',
                'Efetividade do modelo',
                'Precisão das probabilidades',
                'Qualidade dos dados',
                'Tempo de análise',
                'Fatores externos'
            ],
            'model_adjustments': [
                'Ajustar pesos dos fatores',
                'Melhorar coleta de dados',
                'Refinar algoritmos',
                'Atualizar thresholds',
                'Incluir novos fatores',
                'Otimizar parâmetros',
                'Validar premissas',
                'Calibrar modelos'
            ]
        }
    
    def generate_game_phases(self, home_team: str, away_team: str, 
                           match_data: Dict) -> List[GamePhase]:
        """Gera fases do jogo com observações"""
        
        phases = []
        
        for phase_name, config in self.game_phases.items():
            # Simula dados baseados no contexto da partida
            xg_live = np.random.uniform(0.3, 2.5)
            intensity = np.random.uniform(0.5, 1.0)
            
            # Determina status baseado nos thresholds
            if xg_live >= config['xg_threshold'] and intensity >= config['intensity_threshold']:
                status = "✅ POSITIVO"
            elif xg_live >= config['xg_threshold'] or intensity >= config['intensity_threshold']:
                status = "⚠️ ATENÇÃO"
            else:
                status = "❌ NEGATIVO"
            
            phases.append(GamePhase(
                phase=phase_name,
                time_range=phase_name,
                observation=config['observation'],
                action=config['action'],
                xg_live=xg_live,
                intensity=intensity,
                status=status
            ))
        
        return phases
    
    def create_learning_record(self, home_team: str, away_team: str, 
                             match_date: str, prediction: str, 
                             match_data: Dict) -> LearningRecord:
        """Cria registro para aprendizado"""
        
        # Simula resultado real vs previsto
        actual_result = self._simulate_actual_result(prediction)
        predicted_xg = match_data.get('predicted_xg', 3.2)
        actual_xg = np.random.uniform(2.0, 4.5)
        
        # Calcula precisão
        accuracy = self._calculate_accuracy(prediction, actual_result)
        
        # Gera fatores de impacto
        impact_factors = self._generate_impact_factors()
        
        # Gera lições aprendidas
        lessons_learned = self._generate_lessons_learned(accuracy)
        
        # Gera ajustes no modelo
        model_adjustments = self._generate_model_adjustments(accuracy)
        
        return LearningRecord(
            match_id=f"{home_team}_{away_team}_{match_date}",
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            prediction=prediction,
            actual_result=actual_result,
            predicted_xg=predicted_xg,
            actual_xg=actual_xg,
            impact_factors=impact_factors,
            lessons_learned=lessons_learned,
            model_adjustments=model_adjustments,
            accuracy=accuracy,
            timestamp=datetime.now()
        )
    
    def _simulate_actual_result(self, prediction: str) -> str:
        """Simula resultado real"""
        # Simula se a previsão foi correta (70% de chance)
        if np.random.random() < 0.7:
            return prediction
        else:
            # Retorna resultado alternativo
            if "OVER" in prediction:
                return "UNDER 2.5 GOLS"
            elif "UNDER" in prediction:
                return "OVER 2.5 GOLS"
            else:
                return "RESULTADO DIFERENTE"
    
    def _calculate_accuracy(self, prediction: str, actual: str) -> float:
        """Calcula precisão da previsão"""
        if prediction == actual:
            return 1.0
        else:
            return 0.0
    
    def _generate_impact_factors(self) -> List[str]:
        """Gera fatores de impacto"""
        factors = self.learning_metrics['impact_factors']
        num_factors = np.random.randint(2, 5)
        return np.random.choice(factors, num_factors, replace=False).tolist()
    
    def _generate_lessons_learned(self, accuracy: float) -> List[str]:
        """Gera lições aprendidas"""
        lessons = self.learning_metrics['lessons_learned']
        num_lessons = np.random.randint(2, 4)
        return np.random.choice(lessons, num_lessons, replace=False).tolist()
    
    def _generate_model_adjustments(self, accuracy: float) -> List[str]:
        """Gera ajustes no modelo"""
        adjustments = self.learning_metrics['model_adjustments']
        num_adjustments = np.random.randint(1, 3)
        return np.random.choice(adjustments, num_adjustments, replace=False).tolist()
    
    def calculate_performance_metrics(self, learning_records: List[LearningRecord]) -> PerformanceMetrics:
        """Calcula métricas de desempenho"""
        
        if not learning_records:
            return self._create_empty_metrics()
        
        total_analyses = len(learning_records)
        correct_predictions = sum(1 for record in learning_records if record.accuracy > 0)
        accuracy_rate = correct_predictions / total_analyses if total_analyses > 0 else 0
        
        # Simula ROI e yield
        average_roi = np.random.uniform(5.0, 15.0)
        yield_rate = np.random.uniform(3.0, 10.0)
        
        # Calcula sequências
        max_positive_streak = self._calculate_max_positive_streak(learning_records)
        max_drawdown = np.random.uniform(2.0, 8.0)
        current_streak = self._calculate_current_streak(learning_records)
        
        # Últimas 30 análises
        last_30 = learning_records[-30:] if len(learning_records) >= 30 else learning_records
        last_30_correct = sum(1 for record in last_30 if record.accuracy > 0)
        last_30_accuracy = last_30_correct / len(last_30) if last_30 else 0
        last_30_roi = np.random.uniform(6.0, 12.0)
        last_30_yield = np.random.uniform(4.0, 8.0)
        
        return PerformanceMetrics(
            total_analyses=total_analyses,
            correct_predictions=correct_predictions,
            accuracy_rate=accuracy_rate,
            average_roi=average_roi,
            yield_rate=yield_rate,
            max_positive_streak=max_positive_streak,
            max_drawdown=max_drawdown,
            current_streak=current_streak,
            last_30_accuracy=last_30_accuracy,
            last_30_roi=last_30_roi,
            last_30_yield=last_30_yield
        )
    
    def _calculate_max_positive_streak(self, records: List[LearningRecord]) -> int:
        """Calcula maior sequência positiva"""
        if not records:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for record in records:
            if record.accuracy > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_current_streak(self, records: List[LearningRecord]) -> int:
        """Calcula sequência atual"""
        if not records:
            return 0
        
        current_streak = 0
        for record in reversed(records):
            if record.accuracy > 0:
                current_streak += 1
            else:
                break
        
        return current_streak
    
    def _create_empty_metrics(self) -> PerformanceMetrics:
        """Cria métricas vazias"""
        return PerformanceMetrics(
            total_analyses=0,
            correct_predictions=0,
            accuracy_rate=0.0,
            average_roi=0.0,
            yield_rate=0.0,
            max_positive_streak=0,
            max_drawdown=0.0,
            current_streak=0,
            last_30_accuracy=0.0,
            last_30_roi=0.0,
            last_30_yield=0.0
        )
    
    def generate_tracking_history(self, performance_metrics: PerformanceMetrics) -> List[Dict]:
        """Gera histórico de rastreamento"""
        
        history = []
        
        # Simula últimas 30 análises
        for i in range(30):
            analysis = {
                'date': (datetime.now() - timedelta(days=i)).strftime('%d/%m/%Y'),
                'match': f"Partida {i+1}",
                'prediction': np.random.choice(['OVER 2.5', 'UNDER 2.5', 'AMBAS MARCAM']),
                'result': np.random.choice(['CORRETO', 'INCORRETO']),
                'roi': np.random.uniform(-5.0, 15.0),
                'xg_accuracy': np.random.uniform(0.6, 0.9)
            }
            history.append(analysis)
        
        return history
    
    def generate_recommendations(self, performance_metrics: PerformanceMetrics, 
                               learning_record: LearningRecord) -> List[str]:
        """Gera recomendações baseadas no desempenho"""
        
        recommendations = []
        
        if performance_metrics.accuracy_rate < 0.7:
            recommendations.append("Considerar ajustar modelo de previsão")
        
        if performance_metrics.average_roi < 5.0:
            recommendations.append("Revisar critérios de seleção de apostas")
        
        if performance_metrics.max_drawdown > 10.0:
            recommendations.append("Implementar gestão de risco mais conservadora")
        
        if learning_record.accuracy < 0.5:
            recommendations.append("Analisar fatores que impactaram negativamente")
        
        if performance_metrics.current_streak > 5:
            recommendations.append("Manter estratégia atual - desempenho positivo")
        
        return recommendations
    
    def generate_post_analysis_tracking(self, home_team: str, away_team: str, 
                                      match_date: str, prediction: str, 
                                      match_data: Dict) -> PostAnalysisTracking:
        """Gera acompanhamento e análise posterior completo"""
        
        logger.info(f"Gerando acompanhamento posterior: {home_team} vs {away_team}")
        
        try:
            # Gera fases do jogo
            game_phases = self.generate_game_phases(home_team, away_team, match_data)
            
            # Cria registro de aprendizado
            learning_record = self.create_learning_record(home_team, away_team, match_date, prediction, match_data)
            
            # Carrega histórico de registros
            learning_records = self._load_learning_records()
            learning_records.append(learning_record)
            
            # Calcula métricas de desempenho
            performance_metrics = self.calculate_performance_metrics(learning_records)
            
            # Gera histórico de rastreamento
            tracking_history = self.generate_tracking_history(performance_metrics)
            
            # Gera recomendações
            recommendations = self.generate_recommendations(performance_metrics, learning_record)
            
            return PostAnalysisTracking(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                game_phases=game_phases,
                learning_record=learning_record,
                performance_metrics=performance_metrics,
                tracking_history=tracking_history,
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração do acompanhamento posterior: {e}")
            return self._create_empty_tracking(home_team, away_team, match_date)
    
    def _load_learning_records(self) -> List[LearningRecord]:
        """Carrega registros de aprendizado"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [LearningRecord(**record) for record in data]
        except Exception as e:
            logger.error(f"Erro ao carregar registros de aprendizado: {e}")
        
        return []
    
    def _create_empty_tracking(self, home_team: str, away_team: str, 
                             match_date: str) -> PostAnalysisTracking:
        """Cria acompanhamento vazio em caso de erro"""
        return PostAnalysisTracking(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            game_phases=[],
            learning_record=None,
            performance_metrics=self._create_empty_metrics(),
            tracking_history=[],
            recommendations=[],
            last_updated=datetime.now()
        )
    
    def format_post_analysis_tracking(self, tracking: PostAnalysisTracking) -> str:
        """Formata acompanhamento e análise posterior"""
        
        if not tracking or not tracking.game_phases:
            return "Acompanhamento posterior não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("ACOMPANHAMENTO E ANÁLISE POSTERIOR")
        report_parts.append("=" * 60)
        report_parts.append(f"Partida: {tracking.home_team} vs {tracking.away_team}")
        report_parts.append(f"Data: {tracking.match_date}")
        report_parts.append("")
        
        # Durante o jogo
        report_parts.append("Durante o Jogo:")
        report_parts.append("")
        
        for phase in tracking.game_phases:
            report_parts.append(f"⏱️ {phase.time_range}: {phase.observation}")
            report_parts.append(f"   Ação: {phase.action}")
            report_parts.append(f"   xG Live: {phase.xg_live:.1f}")
            report_parts.append(f"   Intensidade: {phase.intensity:.1%}")
            report_parts.append(f"   Status: {phase.status}")
            report_parts.append("")
        
        # Registro para aprendizado
        if tracking.learning_record:
            report_parts.append("Registro para Aprendizado:")
            report_parts.append("┌─────────────────────────────────────┐")
            report_parts.append("│ MÉTRICAS A REGISTRAR:               │")
            report_parts.append("├─────────────────────────────────────┤")
            report_parts.append(f"│ ✓ Resultado real vs previsto: {tracking.learning_record.actual_result}")
            report_parts.append(f"│ ✓ xG real vs estimado: {tracking.learning_record.actual_xg:.1f} vs {tracking.learning_record.predicted_xg:.1f}")
            report_parts.append("│ ✓ Fatores que impactaram resultado:")
            for factor in tracking.learning_record.impact_factors:
                report_parts.append(f"│   • {factor}")
            report_parts.append("│ ✓ Lições aprendidas:")
            for lesson in tracking.learning_record.lessons_learned:
                report_parts.append(f"│   • {lesson}")
            report_parts.append("│ ✓ Ajustes necessários no modelo:")
            for adjustment in tracking.learning_record.model_adjustments:
                report_parts.append(f"│   • {adjustment}")
            report_parts.append("└─────────────────────────────────────┘")
            report_parts.append("")
        
        # Sistema de rastreamento de desempenho
        report_parts.append("📈 SISTEMA DE RASTREAMENTO DE DESEMPENHO")
        report_parts.append("HISTÓRICO SIMULADO (Últimas 30 Análises):")
        report_parts.append("━" * 47)
        
        metrics = tracking.performance_metrics
        report_parts.append(f"Taxa de Acerto: {metrics.last_30_accuracy:.1%} ({int(metrics.last_30_accuracy * 30)}/30) ✅")
        report_parts.append(f"ROI Médio: +{metrics.last_30_roi:.1f}%")
        report_parts.append(f"Yield: +{metrics.last_30_yield:.1f}%")
        report_parts.append(f"Maior Sequência Positiva: {metrics.max_positive_streak}")
        report_parts.append(f"Drawdown Máximo: -{metrics.max_drawdown:.1f}%")
        report_parts.append("━" * 47)
        report_parts.append("")
        
        # Recomendações
        if tracking.recommendations:
            report_parts.append("💡 RECOMENDAÇÕES:")
            report_parts.append("-" * 40)
            for i, rec in enumerate(tracking.recommendations, 1):
                report_parts.append(f"{i}. {rec}")
            report_parts.append("")
        
        # Timestamp
        report_parts.append("📅 Última Atualização")
        report_parts.append("-" * 40)
        report_parts.append(f"Data/Hora: {tracking.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return "\n".join(report_parts)

if __name__ == "__main__":
    # Teste do rastreador de acompanhamento posterior
    tracker = PostAnalysisTracker()
    
    print("=== TESTE DO RASTREADOR DE ACOMPANHAMENTO POSTERIOR ===")
    
    # Dados de exemplo
    match_data = {
        'predicted_xg': 3.2,
        'intensity': 0.8,
        'context': 'high_stakes'
    }
    
    # Gera acompanhamento posterior
    tracking = tracker.generate_post_analysis_tracking(
        "Manchester City", "Arsenal", "2024-01-15", 
        "OVER 2.5 GOLS", match_data
    )
    
    # Formata acompanhamento
    report = tracker.format_post_analysis_tracking(tracking)
    
    print(report)
    
    print("\nTeste concluído!")
