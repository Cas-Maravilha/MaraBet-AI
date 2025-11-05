"""
Gerenciador de Escalabilidade - MaraBet AI
Sistema completo de escalabilidade de infraestrutura
"""

import os
import json
import yaml
import logging
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ScalingConfig:
    """Configuração de escalabilidade"""
    min_instances: int = 2
    max_instances: int = 10
    target_cpu: float = 70.0
    target_memory: float = 80.0
    target_response_time: float = 2.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0
    cooldown_period: int = 300
    scale_up_cooldown: int = 60
    scale_down_cooldown: int = 300

@dataclass
class InfrastructureMetrics:
    """Métricas de infraestrutura"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    response_time: float
    throughput: float
    error_rate: float
    active_instances: int
    timestamp: datetime

@dataclass
class ScalingDecision:
    """Decisão de escalabilidade"""
    action: str  # 'scale_up', 'scale_down', 'no_action'
    reason: str
    current_instances: int
    target_instances: int
    confidence: float
    timestamp: datetime

class ScalabilityManager:
    """
    Gerenciador de escalabilidade para MaraBet AI
    Implementa auto-scaling e gerenciamento de infraestrutura
    """
    
    def __init__(self, config_file: str = "infrastructure/scaling_config.yaml"):
        """
        Inicializa o gerenciador de escalabilidade
        
        Args:
            config_file: Arquivo de configuração
        """
        self.config_file = config_file
        self.config = self._load_scaling_config()
        self.metrics_history = []
        self.last_scale_time = None
        
        logger.info("ScalabilityManager inicializado")
    
    def _load_scaling_config(self) -> ScalingConfig:
        """Carrega configuração de escalabilidade"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                return ScalingConfig(**data)
            else:
                default_config = ScalingConfig()
                self._save_scaling_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return ScalingConfig()
    
    def _save_scaling_config(self, config: ScalingConfig):
        """Salva configuração de escalabilidade"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config.__dict__, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
    
    def collect_metrics(self) -> InfrastructureMetrics:
        """
        Coleta métricas de infraestrutura
        
        Returns:
            Métricas coletadas
        """
        try:
            # Métricas do sistema
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Métricas de rede
            network = psutil.net_io_counters()
            network_usage = (network.bytes_sent + network.bytes_recv) / (1024 * 1024)  # MB
            
            # Métricas de aplicação
            response_time, throughput, error_rate = self._get_application_metrics()
            
            # Número de instâncias ativas
            active_instances = self._get_active_instances()
            
            metrics = InfrastructureMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_usage=network_usage,
                response_time=response_time,
                throughput=throughput,
                error_rate=error_rate,
                active_instances=active_instances,
                timestamp=datetime.now()
            )
            
            # Adicionar ao histórico
            self.metrics_history.append(metrics)
            
            # Manter apenas últimas 100 métricas
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas: {e}")
            return self._empty_metrics()
    
    def _get_application_metrics(self) -> Tuple[float, float, float]:
        """Obtém métricas da aplicação"""
        try:
            # Fazer request para endpoint de métricas
            response = requests.get(
                "http://localhost:8000/metrics",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return (
                    data.get('response_time', 0.0),
                    data.get('throughput', 0.0),
                    data.get('error_rate', 0.0)
                )
            else:
                return 0.0, 0.0, 0.0
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter métricas da aplicação: {e}")
            return 0.0, 0.0, 0.0
    
    def _get_active_instances(self) -> int:
        """Obtém número de instâncias ativas"""
        try:
            # Verificar containers Docker ativos
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=marabet', '--format', '{{.Names}}'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                instances = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return len(instances)
            else:
                return 1  # Assumir 1 instância se não conseguir verificar
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter instâncias ativas: {e}")
            return 1
    
    def make_scaling_decision(self, metrics: InfrastructureMetrics) -> ScalingDecision:
        """
        Toma decisão de escalabilidade baseada nas métricas
        
        Args:
            metrics: Métricas atuais
            
        Returns:
            Decisão de escalabilidade
        """
        try:
            current_instances = metrics.active_instances
            
            # Verificar cooldown
            if self.last_scale_time:
                time_since_last_scale = (datetime.now() - self.last_scale_time).total_seconds()
                if time_since_last_scale < self.config.cooldown_period:
                    return ScalingDecision(
                        action="no_action",
                        reason="Cooldown period active",
                        current_instances=current_instances,
                        target_instances=current_instances,
                        confidence=1.0,
                        timestamp=datetime.now()
                    )
            
            # Analisar métricas
            scale_up_reasons = []
            scale_down_reasons = []
            
            # Verificar CPU
            if metrics.cpu_usage > self.config.scale_up_threshold:
                scale_up_reasons.append(f"CPU usage high: {metrics.cpu_usage:.1f}%")
            elif metrics.cpu_usage < self.config.scale_down_threshold:
                scale_down_reasons.append(f"CPU usage low: {metrics.cpu_usage:.1f}%")
            
            # Verificar memória
            if metrics.memory_usage > self.config.scale_up_threshold:
                scale_up_reasons.append(f"Memory usage high: {metrics.memory_usage:.1f}%")
            elif metrics.memory_usage < self.config.scale_down_threshold:
                scale_down_reasons.append(f"Memory usage low: {metrics.memory_usage:.1f}%")
            
            # Verificar tempo de resposta
            if metrics.response_time > self.config.target_response_time:
                scale_up_reasons.append(f"Response time high: {metrics.response_time:.2f}s")
            
            # Verificar taxa de erro
            if metrics.error_rate > 0.05:  # 5%
                scale_up_reasons.append(f"Error rate high: {metrics.error_rate:.2f}%")
            
            # Verificar throughput
            if metrics.throughput < 50:  # req/s
                scale_up_reasons.append(f"Throughput low: {metrics.throughput:.1f} req/s")
            
            # Tomar decisão
            if scale_up_reasons and current_instances < self.config.max_instances:
                target_instances = min(current_instances + 1, self.config.max_instances)
                return ScalingDecision(
                    action="scale_up",
                    reason="; ".join(scale_up_reasons),
                    current_instances=current_instances,
                    target_instances=target_instances,
                    confidence=min(len(scale_up_reasons) / 3, 1.0),
                    timestamp=datetime.now()
                )
            elif scale_down_reasons and current_instances > self.config.min_instances:
                target_instances = max(current_instances - 1, self.config.min_instances)
                return ScalingDecision(
                    action="scale_down",
                    reason="; ".join(scale_down_reasons),
                    current_instances=current_instances,
                    target_instances=target_instances,
                    confidence=min(len(scale_down_reasons) / 2, 1.0),
                    timestamp=datetime.now()
                )
            else:
                return ScalingDecision(
                    action="no_action",
                    reason="Metrics within normal range",
                    current_instances=current_instances,
                    target_instances=current_instances,
                    confidence=1.0,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"❌ Erro na decisão de escalabilidade: {e}")
            return ScalingDecision(
                action="no_action",
                reason=f"Error in decision making: {str(e)}",
                current_instances=metrics.active_instances,
                target_instances=metrics.active_instances,
                confidence=0.0,
                timestamp=datetime.now()
            )
    
    def execute_scaling(self, decision: ScalingDecision) -> bool:
        """
        Executa ação de escalabilidade
        
        Args:
            decision: Decisão de escalabilidade
            
        Returns:
            True se executado com sucesso
        """
        try:
            if decision.action == "no_action":
                logger.info("ℹ️ Nenhuma ação de escalabilidade necessária")
                return True
            
            logger.info(f"🔄 Executando {decision.action}: {decision.current_instances} -> {decision.target_instances}")
            
            if decision.action == "scale_up":
                success = self._scale_up(decision.target_instances)
            elif decision.action == "scale_down":
                success = self._scale_down(decision.target_instances)
            else:
                logger.error(f"❌ Ação desconhecida: {decision.action}")
                return False
            
            if success:
                self.last_scale_time = datetime.now()
                logger.info(f"✅ Escalabilidade executada com sucesso")
            else:
                logger.error(f"❌ Falha na execução da escalabilidade")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro na execução da escalabilidade: {e}")
            return False
    
    def _scale_up(self, target_instances: int) -> bool:
        """Escala para cima"""
        try:
            # Usar Docker Compose para escalar
            result = subprocess.run(
                ['docker-compose', 'up', '-d', '--scale', f'app={target_instances}'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Escalado para {target_instances} instâncias")
                return True
            else:
                logger.error(f"❌ Erro no scale up: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no scale up: {e}")
            return False
    
    def _scale_down(self, target_instances: int) -> bool:
        """Escala para baixo"""
        try:
            # Usar Docker Compose para escalar
            result = subprocess.run(
                ['docker-compose', 'up', '-d', '--scale', f'app={target_instances}'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Escalado para {target_instances} instâncias")
                return True
            else:
                logger.error(f"❌ Erro no scale down: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no scale down: {e}")
            return False
    
    def run_auto_scaling_loop(self, interval: int = 60):
        """
        Executa loop de auto-scaling
        
        Args:
            interval: Intervalo entre verificações (segundos)
        """
        try:
            logger.info(f"🔄 Iniciando loop de auto-scaling (intervalo: {interval}s)")
            
            while True:
                # Coletar métricas
                metrics = self.collect_metrics()
                
                # Tomar decisão
                decision = self.make_scaling_decision(metrics)
                
                # Executar ação
                if decision.action != "no_action":
                    self.execute_scaling(decision)
                
                # Log da decisão
                logger.info(f"📊 Decisão: {decision.action} - {decision.reason}")
                
                # Aguardar próximo ciclo
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Loop de auto-scaling interrompido")
        except Exception as e:
            logger.error(f"❌ Erro no loop de auto-scaling: {e}")
    
    def generate_scaling_report(self) -> Dict[str, Any]:
        """Gera relatório de escalabilidade"""
        try:
            if not self.metrics_history:
                return {"message": "Nenhuma métrica disponível"}
            
            # Calcular estatísticas
            cpu_values = [m.cpu_usage for m in self.metrics_history]
            memory_values = [m.memory_usage for m in self.metrics_history]
            response_times = [m.response_time for m in self.metrics_history]
            throughput_values = [m.throughput for m in self.metrics_history]
            
            return {
                "period": {
                    "start": self.metrics_history[0].timestamp.isoformat(),
                    "end": self.metrics_history[-1].timestamp.isoformat(),
                    "duration_minutes": (self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).total_seconds() / 60
                },
                "metrics": {
                    "cpu": {
                        "avg": sum(cpu_values) / len(cpu_values),
                        "max": max(cpu_values),
                        "min": min(cpu_values)
                    },
                    "memory": {
                        "avg": sum(memory_values) / len(memory_values),
                        "max": max(memory_values),
                        "min": min(memory_values)
                    },
                    "response_time": {
                        "avg": sum(response_times) / len(response_times),
                        "max": max(response_times),
                        "min": min(response_times)
                    },
                    "throughput": {
                        "avg": sum(throughput_values) / len(throughput_values),
                        "max": max(throughput_values),
                        "min": min(throughput_values)
                    }
                },
                "instances": {
                    "current": self.metrics_history[-1].active_instances,
                    "min_configured": self.config.min_instances,
                    "max_configured": self.config.max_instances
                },
                "scaling_events": self._get_scaling_events()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {"error": str(e)}
    
    def _get_scaling_events(self) -> List[Dict[str, Any]]:
        """Obtém eventos de escalabilidade"""
        # Implementar lógica para rastrear eventos de escalabilidade
        return []
    
    def create_docker_compose_scaling(self) -> str:
        """Cria configuração Docker Compose para escalabilidade"""
        try:
            compose_content = f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000-8009:8000"
    environment:
      - NODE_ENV=production
      - INSTANCE_ID=${{INSTANCE_ID}}
    deploy:
      replicas: {self.config.min_instances}
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    deploy:
      replicas: 1

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=marabet
      - POSTGRES_USER=marabet
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD}}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      replicas: 1

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    deploy:
      replicas: 1

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${{GRAFANA_PASSWORD}}
    volumes:
      - grafana_data:/var/lib/grafana
    deploy:
      replicas: 1

volumes:
  redis_data:
  postgres_data:
  grafana_data:

networks:
  default:
    driver: overlay
    attachable: true
"""
            
            compose_path = "docker-compose.scaling.yml"
            with open(compose_path, 'w', encoding='utf-8') as f:
                f.write(compose_content)
            
            logger.info(f"✅ Docker Compose de escalabilidade criado em {compose_path}")
            return compose_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar Docker Compose: {e}")
            return ""
    
    def create_kubernetes_scaling(self) -> str:
        """Cria configuração Kubernetes para escalabilidade"""
        try:
            k8s_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: marabet-app
  labels:
    app: marabet
spec:
  replicas: {self.config.min_instances}
  selector:
    matchLabels:
      app: marabet
  template:
    metadata:
      labels:
        app: marabet
    spec:
      containers:
      - name: marabet
        image: marabet:latest
        ports:
        - containerPort: 8000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: marabet-service
spec:
  selector:
    app: marabet
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: marabet-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: marabet-app
  minReplicas: {self.config.min_instances}
  maxReplicas: {self.config.max_instances}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {self.config.target_cpu}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {self.config.target_memory}
"""
            
            k8s_path = "k8s/scaling.yaml"
            os.makedirs(os.path.dirname(k8s_path), exist_ok=True)
            with open(k8s_path, 'w', encoding='utf-8') as f:
                f.write(k8s_content)
            
            logger.info(f"✅ Configuração Kubernetes criada em {k8s_path}")
            return k8s_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar configuração Kubernetes: {e}")
            return ""
    
    def _empty_metrics(self) -> InfrastructureMetrics:
        """Retorna métricas vazias"""
        return InfrastructureMetrics(
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            network_usage=0.0,
            response_time=0.0,
            throughput=0.0,
            error_rate=0.0,
            active_instances=1,
            timestamp=datetime.now()
        )
