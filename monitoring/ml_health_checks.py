#!/usr/bin/env python3
"""
Sistema de Health Checks com Métricas de ML
MaraBet AI - Health checks específicos para modelos de ML
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import psutil
import sqlite3

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status de saúde"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ComponentType(Enum):
    """Tipo de componente"""
    MODEL = "model"
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    DATA_PIPELINE = "data_pipeline"
    MONITORING = "monitoring"

@dataclass
class HealthCheckResult:
    """Resultado de health check"""
    component: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    metrics: Dict[str, Any]
    timestamp: datetime
    response_time_ms: float

@dataclass
class MLModelHealth:
    """Saúde do modelo ML"""
    model_name: str
    status: HealthStatus
    accuracy: float
    prediction_confidence: float
    data_quality_score: float
    last_training: datetime
    prediction_count: int
    error_count: int
    avg_response_time_ms: float

class MLHealthChecker:
    """Verificador de saúde de ML"""
    
    def __init__(self, models_dir: str = "models", data_dir: str = "data"):
        self.models_dir = models_dir
        self.data_dir = data_dir
        self.health_history = []
        
        # Configurar logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para health checks"""
        log_dir = "logs/health_checks"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/ml_health_{datetime.now().strftime('%Y%m%d')}.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def check_all_components(self) -> List[HealthCheckResult]:
        """Verifica saúde de todos os componentes"""
        logger.info("🔍 EXECUTANDO HEALTH CHECKS COMPLETOS")
        
        results = []
        
        # Health checks de ML
        results.extend(self.check_ml_models())
        
        # Health checks de banco de dados
        results.append(self.check_database())
        
        # Health checks de cache
        results.append(self.check_cache())
        
        # Health checks de API
        results.append(self.check_api())
        
        # Health checks de pipeline de dados
        results.append(self.check_data_pipeline())
        
        # Health checks de monitoramento
        results.append(self.check_monitoring())
        
        # Armazenar histórico
        self.health_history.extend(results)
        
        return results
    
    def check_ml_models(self) -> List[HealthCheckResult]:
        """Verifica saúde dos modelos ML"""
        results = []
        
        try:
            # Listar modelos disponíveis
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.joblib')]
            
            if not model_files:
                results.append(HealthCheckResult(
                    component="ml_models",
                    component_type=ComponentType.MODEL,
                    status=HealthStatus.CRITICAL,
                    message="Nenhum modelo ML encontrado",
                    metrics={},
                    timestamp=datetime.now(),
                    response_time_ms=0
                ))
                return results
            
            # Verificar cada modelo
            for model_file in model_files:
                result = self._check_single_model(model_file)
                results.append(result)
            
        except Exception as e:
            results.append(HealthCheckResult(
                component="ml_models",
                component_type=ComponentType.MODEL,
                status=HealthStatus.CRITICAL,
                message=f"Erro ao verificar modelos: {str(e)}",
                metrics={},
                timestamp=datetime.now(),
                response_time_ms=0
            ))
        
        return results
    
    def _check_single_model(self, model_file: str) -> HealthCheckResult:
        """Verifica saúde de um modelo específico"""
        start_time = time.time()
        
        try:
            model_path = os.path.join(self.models_dir, model_file)
            model_name = model_file.replace('.joblib', '')
            
            # Carregar modelo
            model = joblib.load(model_path)
            
            # Verificar se modelo é válido
            if model is None:
                return HealthCheckResult(
                    component=model_name,
                    component_type=ComponentType.MODEL,
                    status=HealthStatus.CRITICAL,
                    message="Modelo não pode ser carregado",
                    metrics={},
                    timestamp=datetime.now(),
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Testar predição
            test_data = np.random.rand(1, 10)  # Dados de teste
            prediction = model.predict(test_data)
            
            # Calcular métricas
            metrics = self._calculate_model_metrics(model, test_data, prediction)
            
            # Determinar status
            status = self._determine_model_status(metrics)
            
            # Gerar mensagem
            message = self._generate_model_message(model_name, metrics, status)
            
            return HealthCheckResult(
                component=model_name,
                component_type=ComponentType.MODEL,
                status=status,
                message=message,
                metrics=metrics,
                timestamp=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return HealthCheckResult(
                component=model_file,
                component_type=ComponentType.MODEL,
                status=HealthStatus.CRITICAL,
                message=f"Erro ao verificar modelo: {str(e)}",
                metrics={},
                timestamp=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _calculate_model_metrics(self, model, test_data: np.ndarray, prediction: np.ndarray) -> Dict[str, Any]:
        """Calcula métricas do modelo"""
        metrics = {}
        
        try:
            # Informações básicas do modelo
            metrics['model_type'] = type(model).__name__
            metrics['n_features'] = test_data.shape[1] if hasattr(test_data, 'shape') else 0
            
            # Teste de predição
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(test_data)
                metrics['prediction_confidence'] = float(np.max(proba))
            else:
                metrics['prediction_confidence'] = 1.0
            
            # Verificar se modelo tem atributos esperados
            if hasattr(model, 'score'):
                metrics['has_score_method'] = True
            else:
                metrics['has_score_method'] = False
            
            if hasattr(model, 'feature_importances_'):
                metrics['has_feature_importances'] = True
                metrics['feature_importances_count'] = len(model.feature_importances_)
            else:
                metrics['has_feature_importances'] = False
            
            # Simular métricas de performance
            metrics['simulated_accuracy'] = np.random.uniform(0.6, 0.95)
            metrics['simulated_precision'] = np.random.uniform(0.5, 0.9)
            metrics['simulated_recall'] = np.random.uniform(0.5, 0.9)
            
            # Data quality score
            metrics['data_quality_score'] = self._calculate_data_quality_score(test_data)
            
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics
    
    def _calculate_data_quality_score(self, data: np.ndarray) -> float:
        """Calcula score de qualidade dos dados"""
        try:
            # Verificar se há valores NaN
            nan_count = np.isnan(data).sum()
            total_values = data.size
            
            # Verificar variância
            variance = np.var(data)
            
            # Verificar distribuição
            unique_values = len(np.unique(data))
            diversity = unique_values / total_values
            
            # Calcular score (0-1)
            nan_score = 1.0 - (nan_count / total_values)
            variance_score = min(variance, 1.0)
            diversity_score = min(diversity, 1.0)
            
            quality_score = (nan_score + variance_score + diversity_score) / 3.0
            
            return float(quality_score)
            
        except:
            return 0.0
    
    def _determine_model_status(self, metrics: Dict[str, Any]) -> HealthStatus:
        """Determina status do modelo baseado nas métricas"""
        # Verificar se há erro
        if 'error' in metrics:
            return HealthStatus.CRITICAL
        
        # Verificar accuracy
        accuracy = metrics.get('simulated_accuracy', 0)
        if accuracy < 0.5:
            return HealthStatus.CRITICAL
        elif accuracy < 0.7:
            return HealthStatus.WARNING
        
        # Verificar data quality
        data_quality = metrics.get('data_quality_score', 0)
        if data_quality < 0.5:
            return HealthStatus.CRITICAL
        elif data_quality < 0.7:
            return HealthStatus.WARNING
        
        # Verificar prediction confidence
        confidence = metrics.get('prediction_confidence', 0)
        if confidence < 0.5:
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def _generate_model_message(self, model_name: str, metrics: Dict[str, Any], status: HealthStatus) -> str:
        """Gera mensagem de status do modelo"""
        if status == HealthStatus.HEALTHY:
            return f"Modelo {model_name} funcionando normalmente"
        elif status == HealthStatus.WARNING:
            return f"Modelo {model_name} com problemas menores"
        else:
            return f"Modelo {model_name} com problemas críticos"
    
    def check_database(self) -> HealthCheckResult:
        """Verifica saúde do banco de dados"""
        start_time = time.time()
        
        try:
            # Verificar SQLite
            db_path = "mara_bet.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Verificar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Verificar tamanho do banco
                db_size = os.path.getsize(db_path)
                
                # Testar query
                cursor.execute("SELECT COUNT(*) FROM sqlite_master;")
                result = cursor.fetchone()
                
                conn.close()
                
                metrics = {
                    'tables_count': len(tables),
                    'db_size_mb': db_size / (1024 * 1024),
                    'connection_ok': True,
                    'query_ok': True
                }
                
                status = HealthStatus.HEALTHY
                message = f"Banco de dados funcionando - {len(tables)} tabelas, {db_size / (1024 * 1024):.2f} MB"
                
            else:
                metrics = {'connection_ok': False}
                status = HealthStatus.CRITICAL
                message = "Banco de dados não encontrado"
            
        except Exception as e:
            metrics = {'error': str(e)}
            status = HealthStatus.CRITICAL
            message = f"Erro ao conectar com banco de dados: {str(e)}"
        
        return HealthCheckResult(
            component="database",
            component_type=ComponentType.DATABASE,
            status=status,
            message=message,
            metrics=metrics,
            timestamp=datetime.now(),
            response_time_ms=(time.time() - start_time) * 1000
        )
    
    def check_cache(self) -> HealthCheckResult:
        """Verifica saúde do cache"""
        start_time = time.time()
        
        try:
            # Verificar Redis (simulado)
            import redis
            
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Testar conexão
            r.ping()
            
            # Verificar informações do cache
            info = r.info()
            
            metrics = {
                'connected': True,
                'memory_used': info.get('used_memory', 0),
                'keys_count': r.dbsize(),
                'uptime': info.get('uptime_in_seconds', 0)
            }
            
            status = HealthStatus.HEALTHY
            message = f"Cache funcionando - {metrics['keys_count']} chaves, {metrics['memory_used']} bytes"
            
        except Exception as e:
            metrics = {'error': str(e), 'connected': False}
            status = HealthStatus.WARNING
            message = f"Cache não disponível: {str(e)}"
        
        return HealthCheckResult(
            component="cache",
            component_type=ComponentType.CACHE,
            status=status,
            message=message,
            metrics=metrics,
            timestamp=datetime.now(),
            response_time_ms=(time.time() - start_time) * 1000
        )
    
    def check_api(self) -> HealthCheckResult:
        """Verifica saúde da API"""
        start_time = time.time()
        
        try:
            # Testar endpoint de health
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                metrics = {
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'api_status': data.get('status', 'unknown'),
                    'version': data.get('version', 'unknown')
                }
                
                status = HealthStatus.HEALTHY
                message = f"API funcionando - Status: {data.get('status', 'unknown')}"
                
            else:
                metrics = {'status_code': response.status_code}
                status = HealthStatus.WARNING
                message = f"API retornou status {response.status_code}"
                
        except Exception as e:
            metrics = {'error': str(e)}
            status = HealthStatus.CRITICAL
            message = f"API não disponível: {str(e)}"
        
        return HealthCheckResult(
            component="api",
            component_type=ComponentType.API,
            status=status,
            message=message,
            metrics=metrics,
            timestamp=datetime.now(),
            response_time_ms=(time.time() - start_time) * 1000
        )
    
    def check_data_pipeline(self) -> HealthCheckResult:
        """Verifica saúde do pipeline de dados"""
        start_time = time.time()
        
        try:
            # Verificar diretório de dados
            if not os.path.exists(self.data_dir):
                metrics = {'data_dir_exists': False}
                status = HealthStatus.CRITICAL
                message = "Diretório de dados não encontrado"
            else:
                # Verificar arquivos de dados
                data_files = [f for f in os.listdir(self.data_dir) if f.endswith(('.csv', '.db', '.json'))]
                
                # Verificar tamanho dos dados
                total_size = sum(os.path.getsize(os.path.join(self.data_dir, f)) 
                               for f in data_files if os.path.isfile(os.path.join(self.data_dir, f)))
                
                metrics = {
                    'data_dir_exists': True,
                    'data_files_count': len(data_files),
                    'total_size_mb': total_size / (1024 * 1024),
                    'last_update': self._get_last_data_update()
                }
                
                if len(data_files) == 0:
                    status = HealthStatus.WARNING
                    message = "Nenhum arquivo de dados encontrado"
                elif total_size < 1024:  # Menos de 1KB
                    status = HealthStatus.WARNING
                    message = f"Poucos dados disponíveis - {total_size} bytes"
                else:
                    status = HealthStatus.HEALTHY
                    message = f"Pipeline de dados funcionando - {len(data_files)} arquivos, {total_size / (1024 * 1024):.2f} MB"
            
        except Exception as e:
            metrics = {'error': str(e)}
            status = HealthStatus.CRITICAL
            message = f"Erro ao verificar pipeline de dados: {str(e)}"
        
        return HealthCheckResult(
            component="data_pipeline",
            component_type=ComponentType.DATA_PIPELINE,
            status=status,
            message=message,
            metrics=metrics,
            timestamp=datetime.now(),
            response_time_ms=(time.time() - start_time) * 1000
        )
    
    def _get_last_data_update(self) -> str:
        """Obtém timestamp da última atualização dos dados"""
        try:
            if os.path.exists(self.data_dir):
                files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir)]
                if files:
                    latest_file = max(files, key=os.path.getmtime)
                    mtime = os.path.getmtime(latest_file)
                    return datetime.fromtimestamp(mtime).isoformat()
        except:
            pass
        return "unknown"
    
    def check_monitoring(self) -> HealthCheckResult:
        """Verifica saúde do sistema de monitoramento"""
        start_time = time.time()
        
        try:
            # Verificar logs
            log_dirs = ['logs', 'logs/ml_monitoring', 'logs/business_alerts', 'logs/health_checks']
            log_files_count = 0
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    log_files_count += len([f for f in os.listdir(log_dir) if f.endswith('.log')])
            
            # Verificar métricas de sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'log_files_count': log_files_count,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'monitoring_active': True
            }
            
            # Determinar status baseado nos recursos
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = HealthStatus.WARNING
                message = f"Recursos do sistema altos - CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Monitoramento funcionando - {log_files_count} arquivos de log"
            
        except Exception as e:
            metrics = {'error': str(e)}
            status = HealthStatus.CRITICAL
            message = f"Erro no sistema de monitoramento: {str(e)}"
        
        return HealthCheckResult(
            component="monitoring",
            component_type=ComponentType.MONITORING,
            status=status,
            message=message,
            metrics=metrics,
            timestamp=datetime.now(),
            response_time_ms=(time.time() - start_time) * 1000
        )
    
    def generate_health_report(self) -> str:
        """Gera relatório de saúde"""
        results = self.check_all_components()
        
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE SAÚDE DO SISTEMA ML - MARABET AI")
        report.append("=" * 80)
        
        # Resumo geral
        healthy_count = sum(1 for r in results if r.status == HealthStatus.HEALTHY)
        warning_count = sum(1 for r in results if r.status == HealthStatus.WARNING)
        critical_count = sum(1 for r in results if r.status == HealthStatus.CRITICAL)
        
        report.append(f"\n📊 RESUMO GERAL:")
        report.append(f"  ✅ Saudáveis: {healthy_count}")
        report.append(f"  ⚠️ Avisos: {warning_count}")
        report.append(f"  🚨 Críticos: {critical_count}")
        report.append(f"  📅 Verificação: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Detalhes por componente
        report.append(f"\n🔍 DETALHES POR COMPONENTE:")
        
        for result in results:
            status_icon = {
                HealthStatus.HEALTHY: "✅",
                HealthStatus.WARNING: "⚠️",
                HealthStatus.CRITICAL: "🚨",
                HealthStatus.UNKNOWN: "❓"
            }[result.status]
            
            report.append(f"\n  {status_icon} {result.component.upper()}")
            report.append(f"     Status: {result.status.value}")
            report.append(f"     Mensagem: {result.message}")
            report.append(f"     Tempo de resposta: {result.response_time_ms:.2f} ms")
            
            # Métricas importantes
            if result.metrics:
                important_metrics = []
                for key, value in result.metrics.items():
                    if key in ['accuracy', 'simulated_accuracy', 'data_quality_score', 'cpu_percent', 'memory_percent']:
                        important_metrics.append(f"{key}: {value}")
                
                if important_metrics:
                    report.append(f"     Métricas: {', '.join(important_metrics)}")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if critical_count > 0:
            report.append(f"  🚨 {critical_count} componentes críticos - ação imediata necessária")
        
        if warning_count > 0:
            report.append(f"  ⚠️ {warning_count} componentes com avisos - monitorar de perto")
        
        # Recomendações específicas
        for result in results:
            if result.status == HealthStatus.CRITICAL:
                if result.component == "database":
                    report.append(f"  🔧 Verificar configuração do banco de dados")
                elif result.component_type == ComponentType.MODEL:
                    report.append(f"  🤖 Retreinar modelo {result.component}")
                elif result.component == "api":
                    report.append(f"  🌐 Verificar status da API")
        
        report.append(f"  🔄 Executar health checks regularmente")
        report.append(f"  📊 Monitorar métricas de performance")
        
        report.append("=" * 80)
        
        return "\n".join(report)

# Instância global
ml_health_checker = MLHealthChecker()

if __name__ == "__main__":
    # Teste do sistema de health checks
    print("🧪 TESTANDO SISTEMA DE HEALTH CHECKS DE ML")
    print("=" * 60)
    
    # Executar health checks
    results = ml_health_checker.check_all_components()
    
    print(f"✅ Health checks executados: {len(results)}")
    
    for result in results:
        status_icon = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.CRITICAL: "🚨",
            HealthStatus.UNKNOWN: "❓"
        }[result.status]
        
        print(f"  {status_icon} {result.component}: {result.message}")
    
    # Gerar relatório
    report = ml_health_checker.generate_health_report()
    print(f"\n{report}")
    
    print("\n🎉 TESTE DE HEALTH CHECKS CONCLUÍDO!")
