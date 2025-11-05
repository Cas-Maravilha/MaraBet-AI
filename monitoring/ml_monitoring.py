#!/usr/bin/env python3
"""
Sistema de Monitoramento Avançado de ML
MaraBet AI - Monitoramento de modelo drift, anomalias e métricas de negócio
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import logging
import json
import joblib
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Severidade dos alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ModelStatus(Enum):
    """Status do modelo"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DRIFT_DETECTED = "drift_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    FAILED = "failed"

@dataclass
class ModelMetrics:
    """Métricas do modelo"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    prediction_confidence: float
    data_quality_score: float
    feature_importance: Dict[str, float]
    timestamp: datetime

@dataclass
class BusinessMetrics:
    """Métricas de negócio"""
    roi: float
    profit_loss: float
    win_rate: float
    average_odds: float
    total_bets: int
    successful_bets: int
    failed_bets: int
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    timestamp: datetime

@dataclass
class DriftMetrics:
    """Métricas de drift"""
    statistical_drift: float
    feature_drift: Dict[str, float]
    prediction_drift: float
    data_drift: float
    concept_drift: float
    severity: AlertSeverity
    timestamp: datetime

@dataclass
class AnomalyMetrics:
    """Métricas de anomalia"""
    anomaly_score: float
    anomaly_type: str
    affected_features: List[str]
    severity: AlertSeverity
    timestamp: datetime

class MLModelMonitor:
    """Monitor de modelos de ML"""
    
    def __init__(self, model_path: str = "models"):
        self.model_path = model_path
        self.baseline_metrics = None
        self.drift_threshold = 0.1
        self.anomaly_threshold = 0.8
        self.alert_history = []
        
        # Configurar logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para monitoramento de ML"""
        log_dir = "logs/ml_monitoring"
        import os
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/ml_monitoring_{datetime.now().strftime('%Y%m%d')}.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def load_baseline_metrics(self, baseline_file: str = "baseline_metrics.json"):
        """Carrega métricas baseline do modelo"""
        try:
            with open(baseline_file, 'r') as f:
                self.baseline_metrics = json.load(f)
            logger.info(f"✅ Métricas baseline carregadas de {baseline_file}")
        except FileNotFoundError:
            logger.warning(f"⚠️ Arquivo de métricas baseline não encontrado: {baseline_file}")
            self.baseline_metrics = None
        except Exception as e:
            logger.error(f"❌ Erro ao carregar métricas baseline: {e}")
    
    def calculate_model_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                               y_proba: np.ndarray = None) -> ModelMetrics:
        """Calcula métricas do modelo"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        # Métricas básicas
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')
        
        # AUC-ROC (se probabilidades disponíveis)
        auc_roc = 0.0
        if y_proba is not None and len(np.unique(y_true)) == 2:
            try:
                auc_roc = roc_auc_score(y_true, y_proba)
            except:
                auc_roc = 0.0
        
        # Confiança média das predições
        prediction_confidence = np.mean(np.max(y_proba, axis=1)) if y_proba is not None else 0.0
        
        # Score de qualidade dos dados (simulado)
        data_quality_score = self._calculate_data_quality_score(y_true, y_pred)
        
        # Feature importance (simulado)
        feature_importance = self._calculate_feature_importance()
        
        return ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_roc=auc_roc,
            prediction_confidence=prediction_confidence,
            data_quality_score=data_quality_score,
            feature_importance=feature_importance,
            timestamp=datetime.now()
        )
    
    def _calculate_data_quality_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calcula score de qualidade dos dados"""
        # Simular cálculo de qualidade baseado em distribuição e consistência
        unique_true = len(np.unique(y_true))
        unique_pred = len(np.unique(y_pred))
        
        # Score baseado na diversidade dos dados
        diversity_score = min(unique_true, unique_pred) / max(unique_true, unique_pred)
        
        # Score baseado na consistência das predições
        consistency_score = 1.0 - np.std(y_pred) if len(y_pred) > 1 else 1.0
        
        return (diversity_score + consistency_score) / 2.0
    
    def _calculate_feature_importance(self) -> Dict[str, float]:
        """Calcula importância das features (simulado)"""
        features = [
            'home_team_strength', 'away_team_strength', 'head_to_head',
            'recent_form_home', 'recent_form_away', 'home_advantage',
            'injuries_home', 'injuries_away', 'weather_conditions',
            'referee_stats', 'league_importance', 'season_stage'
        ]
        
        # Simular importância aleatória
        np.random.seed(42)
        importance = np.random.dirichlet(np.ones(len(features)))
        
        return {feature: float(imp) for feature, imp in zip(features, importance)}
    
    def detect_model_drift(self, current_metrics: ModelMetrics, 
                          current_data: np.ndarray = None) -> DriftMetrics:
        """Detecta drift no modelo"""
        if self.baseline_metrics is None:
            logger.warning("⚠️ Métricas baseline não disponíveis para detecção de drift")
            return DriftMetrics(
                statistical_drift=0.0,
                feature_drift={},
                prediction_drift=0.0,
                data_drift=0.0,
                concept_drift=0.0,
                severity=AlertSeverity.LOW,
                timestamp=datetime.now()
            )
        
        # Drift estatístico
        statistical_drift = self._calculate_statistical_drift(current_metrics)
        
        # Drift de features
        feature_drift = self._calculate_feature_drift(current_data)
        
        # Drift de predições
        prediction_drift = self._calculate_prediction_drift(current_metrics)
        
        # Drift de dados
        data_drift = self._calculate_data_drift(current_data)
        
        # Drift de conceito
        concept_drift = self._calculate_concept_drift(current_metrics)
        
        # Determinar severidade
        max_drift = max(statistical_drift, prediction_drift, data_drift, concept_drift)
        if max_drift > 0.3:
            severity = AlertSeverity.CRITICAL
        elif max_drift > 0.2:
            severity = AlertSeverity.HIGH
        elif max_drift > 0.1:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        return DriftMetrics(
            statistical_drift=statistical_drift,
            feature_drift=feature_drift,
            prediction_drift=prediction_drift,
            data_drift=data_drift,
            concept_drift=concept_drift,
            severity=severity,
            timestamp=datetime.now()
        )
    
    def _calculate_statistical_drift(self, current_metrics: ModelMetrics) -> float:
        """Calcula drift estatístico"""
        if not self.baseline_metrics:
            return 0.0
        
        baseline_acc = self.baseline_metrics.get('accuracy', 0.0)
        current_acc = current_metrics.accuracy
        
        # Drift baseado na diferença de accuracy
        drift = abs(current_acc - baseline_acc)
        
        return min(drift, 1.0)
    
    def _calculate_feature_drift(self, current_data: np.ndarray) -> Dict[str, float]:
        """Calcula drift de features"""
        if current_data is None or not self.baseline_metrics:
            return {}
        
        feature_names = [
            'home_team_strength', 'away_team_strength', 'head_to_head',
            'recent_form_home', 'recent_form_away', 'home_advantage'
        ]
        
        feature_drift = {}
        for i, feature in enumerate(feature_names):
            if i < current_data.shape[1]:
                # Simular drift baseado na variância dos dados
                feature_data = current_data[:, i]
                drift = np.std(feature_data) / (np.mean(feature_data) + 1e-8)
                feature_drift[feature] = min(drift, 1.0)
        
        return feature_drift
    
    def _calculate_prediction_drift(self, current_metrics: ModelMetrics) -> float:
        """Calcula drift de predições"""
        if not self.baseline_metrics:
            return 0.0
        
        baseline_conf = self.baseline_metrics.get('prediction_confidence', 0.0)
        current_conf = current_metrics.prediction_confidence
        
        # Drift baseado na diferença de confiança
        drift = abs(current_conf - baseline_conf)
        
        return min(drift, 1.0)
    
    def _calculate_data_drift(self, current_data: np.ndarray) -> float:
        """Calcula drift de dados"""
        if current_data is None or not self.baseline_metrics:
            return 0.0
        
        # Simular drift baseado na distribuição dos dados
        baseline_mean = self.baseline_metrics.get('data_mean', 0.0)
        current_mean = np.mean(current_data)
        
        drift = abs(current_mean - baseline_mean) / (baseline_mean + 1e-8)
        
        return min(drift, 1.0)
    
    def _calculate_concept_drift(self, current_metrics: ModelMetrics) -> float:
        """Calcula drift de conceito"""
        if not self.baseline_metrics:
            return 0.0
        
        # Drift baseado na mudança de performance
        baseline_f1 = self.baseline_metrics.get('f1_score', 0.0)
        current_f1 = current_metrics.f1_score
        
        drift = abs(current_f1 - baseline_f1)
        
        return min(drift, 1.0)
    
    def detect_anomalies(self, predictions: np.ndarray, 
                        features: np.ndarray = None) -> AnomalyMetrics:
        """Detecta anomalias nas predições"""
        # Calcular score de anomalia baseado na distribuição das predições
        anomaly_score = self._calculate_anomaly_score(predictions)
        
        # Determinar tipo de anomalia
        anomaly_type = self._classify_anomaly_type(predictions, features)
        
        # Features afetadas
        affected_features = self._identify_affected_features(features)
        
        # Determinar severidade
        if anomaly_score > 0.9:
            severity = AlertSeverity.CRITICAL
        elif anomaly_score > 0.7:
            severity = AlertSeverity.HIGH
        elif anomaly_score > 0.5:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        return AnomalyMetrics(
            anomaly_score=anomaly_score,
            anomaly_type=anomaly_type,
            affected_features=affected_features,
            severity=severity,
            timestamp=datetime.now()
        )
    
    def _calculate_anomaly_score(self, predictions: np.ndarray) -> float:
        """Calcula score de anomalia"""
        if len(predictions) == 0:
            return 0.0
        
        # Usar Z-score para detectar outliers
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        if std_pred == 0:
            return 0.0
        
        z_scores = np.abs((predictions - mean_pred) / std_pred)
        max_z_score = np.max(z_scores)
        
        # Normalizar para 0-1
        anomaly_score = min(max_z_score / 3.0, 1.0)  # 3-sigma rule
        
        return anomaly_score
    
    def _classify_anomaly_type(self, predictions: np.ndarray, 
                              features: np.ndarray = None) -> str:
        """Classifica tipo de anomalia"""
        if len(predictions) == 0:
            return "no_data"
        
        # Análise de distribuição
        unique_preds = len(np.unique(predictions))
        total_preds = len(predictions)
        
        if unique_preds == 1:
            return "constant_predictions"
        elif unique_preds / total_preds < 0.1:
            return "low_diversity"
        elif np.std(predictions) > 0.5:
            return "high_variance"
        else:
            return "normal"
    
    def _identify_affected_features(self, features: np.ndarray) -> List[str]:
        """Identifica features afetadas por anomalias"""
        if features is None:
            return []
        
        feature_names = [
            'home_team_strength', 'away_team_strength', 'head_to_head',
            'recent_form_home', 'recent_form_away', 'home_advantage',
            'injuries_home', 'injuries_away', 'weather_conditions',
            'referee_stats', 'league_importance', 'season_stage'
        ]
        
        affected = []
        for i, feature in enumerate(feature_names):
            if i < features.shape[1]:
                feature_data = features[:, i]
                if np.std(feature_data) > 0.5:  # Alta variância
                    affected.append(feature)
        
        return affected
    
    def calculate_business_metrics(self, bet_results: List[Dict[str, Any]]) -> BusinessMetrics:
        """Calcula métricas de negócio"""
        if not bet_results:
            return BusinessMetrics(
                roi=0.0, profit_loss=0.0, win_rate=0.0, average_odds=0.0,
                total_bets=0, successful_bets=0, failed_bets=0,
                daily_pnl=0.0, weekly_pnl=0.0, monthly_pnl=0.0,
                timestamp=datetime.now()
            )
        
        # Calcular métricas básicas
        total_bets = len(bet_results)
        successful_bets = sum(1 for bet in bet_results if bet.get('result') == 'win')
        failed_bets = total_bets - successful_bets
        
        win_rate = successful_bets / total_bets if total_bets > 0 else 0.0
        
        # Calcular PnL
        total_stake = sum(bet.get('stake', 0) for bet in bet_results)
        total_payout = sum(bet.get('payout', 0) for bet in bet_results)
        profit_loss = total_payout - total_stake
        
        roi = profit_loss / total_stake if total_stake > 0 else 0.0
        
        # Calcular odds médias
        average_odds = np.mean([bet.get('odds', 0) for bet in bet_results])
        
        # PnL por período (simulado)
        daily_pnl = profit_loss * 0.1  # 10% do total
        weekly_pnl = profit_loss * 0.3  # 30% do total
        monthly_pnl = profit_loss  # 100% do total
        
        return BusinessMetrics(
            roi=roi,
            profit_loss=profit_loss,
            win_rate=win_rate,
            average_odds=average_odds,
            total_bets=total_bets,
            successful_bets=successful_bets,
            failed_bets=failed_bets,
            daily_pnl=daily_pnl,
            weekly_pnl=weekly_pnl,
            monthly_pnl=monthly_pnl,
            timestamp=datetime.now()
        )
    
    def check_business_alerts(self, business_metrics: BusinessMetrics) -> List[Dict[str, Any]]:
        """Verifica alertas de negócio"""
        alerts = []
        
        # ROI negativo por X dias
        if business_metrics.roi < -0.1:  # ROI < -10%
            alerts.append({
                'type': 'negative_roi',
                'severity': AlertSeverity.HIGH,
                'message': f'ROI negativo: {business_metrics.roi:.2%}',
                'value': business_metrics.roi,
                'threshold': -0.1,
                'timestamp': datetime.now().isoformat()
            })
        
        # Win rate baixo
        if business_metrics.win_rate < 0.4:  # Win rate < 40%
            alerts.append({
                'type': 'low_win_rate',
                'severity': AlertSeverity.MEDIUM,
                'message': f'Win rate baixo: {business_metrics.win_rate:.2%}',
                'value': business_metrics.win_rate,
                'threshold': 0.4,
                'timestamp': datetime.now().isoformat()
            })
        
        # Perda diária alta
        if business_metrics.daily_pnl < -1000:  # Perda > R$ 1000
            alerts.append({
                'type': 'high_daily_loss',
                'severity': AlertSeverity.CRITICAL,
                'message': f'Perda diária alta: R$ {business_metrics.daily_pnl:.2f}',
                'value': business_metrics.daily_pnl,
                'threshold': -1000,
                'timestamp': datetime.now().isoformat()
            })
        
        # Muitas apostas falharam
        if business_metrics.failed_bets > business_metrics.successful_bets * 2:
            alerts.append({
                'type': 'high_failure_rate',
                'severity': AlertSeverity.MEDIUM,
                'message': f'Alto índice de falhas: {business_metrics.failed_bets} falhas',
                'value': business_metrics.failed_bets,
                'threshold': business_metrics.successful_bets * 2,
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def generate_ml_health_report(self) -> str:
        """Gera relatório de saúde do ML"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE SAÚDE DE ML - MARABET AI")
        report.append("=" * 80)
        
        # Status geral
        report.append(f"\n🔍 STATUS GERAL:")
        report.append(f"  Monitoramento ativo: ✅")
        report.append(f"  Métricas baseline: {'✅' if self.baseline_metrics else '❌'}")
        report.append(f"  Threshold de drift: {self.drift_threshold}")
        report.append(f"  Threshold de anomalia: {self.anomaly_threshold}")
        
        # Alertas recentes
        recent_alerts = [alert for alert in self.alert_history 
                        if (datetime.now() - datetime.fromisoformat(alert['timestamp'])).days < 7]
        
        report.append(f"\n🚨 ALERTAS RECENTES: {len(recent_alerts)}")
        for alert in recent_alerts[-5:]:  # Últimos 5 alertas
            report.append(f"  {alert['type']}: {alert['message']} ({alert['severity'].value})")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        if not self.baseline_metrics:
            report.append(f"  ⚠️ Configurar métricas baseline para detecção de drift")
        
        if len(recent_alerts) > 10:
            report.append(f"  ⚠️ Muitos alertas recentes - verificar estabilidade do sistema")
        
        if any(alert['severity'] == AlertSeverity.CRITICAL for alert in recent_alerts):
            report.append(f"  🚨 Alertas críticos detectados - ação imediata necessária")
        
        report.append(f"  🔄 Executar retreinamento se drift detectado")
        report.append(f"  📊 Monitorar métricas de negócio continuamente")
        
        report.append("=" * 80)
        
        return "\n".join(report)

# Instância global
ml_monitor = MLModelMonitor()

if __name__ == "__main__":
    # Teste do sistema de monitoramento de ML
    print("🧪 TESTANDO SISTEMA DE MONITORAMENTO DE ML")
    print("=" * 60)
    
    # Criar dados de teste
    np.random.seed(42)
    y_true = np.random.randint(0, 2, 1000)
    y_pred = np.random.randint(0, 2, 1000)
    y_proba = np.random.rand(1000, 2)
    features = np.random.rand(1000, 12)
    
    # Calcular métricas
    metrics = ml_monitor.calculate_model_metrics(y_true, y_pred, y_proba)
    print(f"✅ Métricas calculadas: Accuracy={metrics.accuracy:.3f}")
    
    # Detectar drift
    drift = ml_monitor.detect_model_drift(metrics, features)
    print(f"✅ Drift detectado: {drift.statistical_drift:.3f} ({drift.severity.value})")
    
    # Detectar anomalias
    anomalies = ml_monitor.detect_anomalies(y_pred, features)
    print(f"✅ Anomalias detectadas: {anomalies.anomaly_score:.3f} ({anomalies.severity.value})")
    
    # Calcular métricas de negócio
    bet_results = [
        {'result': 'win', 'stake': 100, 'payout': 200, 'odds': 2.0},
        {'result': 'loss', 'stake': 100, 'payout': 0, 'odds': 1.5},
        {'result': 'win', 'stake': 150, 'payout': 300, 'odds': 2.0}
    ]
    
    business_metrics = ml_monitor.calculate_business_metrics(bet_results)
    print(f"✅ Métricas de negócio: ROI={business_metrics.roi:.2%}, Win Rate={business_metrics.win_rate:.2%}")
    
    # Verificar alertas
    alerts = ml_monitor.check_business_alerts(business_metrics)
    print(f"✅ Alertas de negócio: {len(alerts)}")
    
    # Gerar relatório
    report = ml_monitor.generate_ml_health_report()
    print(f"\n{report}")
    
    print("\n🎉 TESTE DE MONITORAMENTO DE ML CONCLUÍDO!")
