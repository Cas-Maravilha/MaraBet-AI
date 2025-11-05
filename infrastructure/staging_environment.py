#!/usr/bin/env python3
"""
Sistema de Staging Environment
MaraBet AI - Ambiente de staging idêntico à produção
"""

import json
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EnvironmentType(Enum):
    """Tipos de ambiente"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class StagingConfig:
    """Configuração do ambiente de staging"""
    environment: EnvironmentType
    namespace: str
    domain: str
    database_url: str
    redis_url: str
    s3_bucket: str
    replicas: int = 2
    resources: Dict[str, Any] = None

class StagingEnvironmentManager:
    """Gerenciador do ambiente de staging"""
    
    def __init__(self, config: StagingConfig):
        self.config = config
        self.templates_dir = "infrastructure/templates"
        self.staging_dir = "infrastructure/kubernetes/staging"
        
        # Criar diretórios
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.staging_dir, exist_ok=True)
    
    def generate_staging_namespace(self) -> str:
        """Gera namespace do staging"""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace,
                "labels": {
                    "name": self.config.namespace,
                    "environment": "staging",
                    "app": "marabet-ai"
                }
            }
        }
        
        return yaml.dump(namespace, default_flow_style=False)
    
    def generate_staging_deployment(self) -> str:
        """Gera deployment do staging"""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "marabet-ai-staging",
                "namespace": self.config.namespace,
                "labels": {
                    "app": "marabet-ai",
                    "environment": "staging",
                    "version": "v1.0.0"
                }
            },
            "spec": {
                "replicas": self.config.replicas,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": "marabet-ai",
                        "environment": "staging"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "marabet-ai",
                            "environment": "staging",
                            "version": "v1.0.0"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "marabet-ai",
                            "image": "your-registry.com/marabet-ai:staging",
                            "imagePullPolicy": "Always",
                            "ports": [{
                                "containerPort": 5000,
                                "name": "http",
                                "protocol": "TCP"
                            }],
                            "env": [
                                {"name": "FLASK_ENV", "value": "staging"},
                                {"name": "ENVIRONMENT", "value": "staging"},
                                {"name": "DATABASE_URL", "value": self.config.database_url},
                                {"name": "REDIS_URL", "value": self.config.redis_url},
                                {"name": "S3_BUCKET", "value": self.config.s3_bucket},
                                {"name": "LOG_LEVEL", "value": "DEBUG"},
                                {"name": "DEBUG", "value": "true"}
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "256Mi",
                                    "cpu": "100m"
                                },
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "250m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/api/health",
                                    "port": 5000
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/api/health",
                                    "port": 5000
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5,
                                "timeoutSeconds": 3,
                                "failureThreshold": 3
                            },
                            "volumeMounts": [{
                                "name": "app-logs",
                                "mountPath": "/app/logs"
                            }, {
                                "name": "app-data",
                                "mountPath": "/app/data"
                            }]
                        }],
                        "volumes": [{
                            "name": "app-logs",
                            "emptyDir": {}
                        }, {
                            "name": "app-data",
                            "emptyDir": {}
                        }],
                        "imagePullSecrets": [{
                            "name": "docker-registry-secret"
                        }]
                    }
                }
            }
        }
        
        return yaml.dump(deployment, default_flow_style=False)
    
    def generate_staging_service(self) -> str:
        """Gera service do staging"""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "marabet-ai-staging-service",
                "namespace": self.config.namespace,
                "labels": {
                    "app": "marabet-ai",
                    "environment": "staging"
                }
            },
            "spec": {
                "selector": {
                    "app": "marabet-ai",
                    "environment": "staging"
                },
                "ports": [{
                    "name": "http",
                    "port": 80,
                    "targetPort": 5000,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
        
        return yaml.dump(service, default_flow_style=False)
    
    def generate_staging_ingress(self) -> str:
        """Gera ingress do staging"""
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "marabet-ai-staging-ingress",
                "namespace": self.config.namespace,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-staging",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/proxy-body-size": "10m",
                    "nginx.ingress.kubernetes.io/proxy-read-timeout": "300",
                    "nginx.ingress.kubernetes.io/proxy-send-timeout": "300",
                    "nginx.ingress.kubernetes.io/rate-limit": "50",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": [self.config.domain],
                    "secretName": "marabet-staging-tls"
                }],
                "rules": [{
                    "host": self.config.domain,
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "marabet-ai-staging-service",
                                    "port": {
                                        "number": 80
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
        
        return yaml.dump(ingress, default_flow_style=False)
    
    def generate_staging_configmap(self) -> str:
        """Gera configmap do staging"""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "marabet-staging-config",
                "namespace": self.config.namespace
            },
            "data": {
                "app.conf": """
[app]
debug = true
host = 0.0.0.0
port = 5000
environment = staging

[database]
pool_size = 10
max_overflow = 20
pool_timeout = 30
pool_recycle = 3600

[redis]
max_connections = 10
socket_timeout = 5
socket_connect_timeout = 5

[logging]
level = DEBUG
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s

[monitoring]
enabled = true
metrics_port = 9090
health_check_interval = 30

[testing]
enabled = true
test_data_cleanup = true
mock_external_apis = true
""",
                "nginx.conf": """
upstream marabet_staging_backend {
    least_conn;
    server marabet-ai-staging-service:80 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name staging.marabet.com;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=staging:10m rate=10r/s;
    limit_req zone=staging burst=20 nodelay;
    
    # Main application
    location / {
        proxy_pass http://marabet_staging_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://marabet_staging_backend/api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
            }
        }
        
        return yaml.dump(configmap, default_flow_style=False)
    
    def generate_staging_secrets(self) -> str:
        """Gera secrets do staging"""
        secrets = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "marabet-staging-secrets",
                "namespace": self.config.namespace
            },
            "type": "Opaque",
            "data": {
                # Database credentials (staging)
                "db-host": "bWFyYWJldC1zdGFnaW5nLmNsdXN0ZXIueHl6LnVzLWVhc3QtMS5yZHMuYW1hem9uYXdzLmNvbQ==",
                "db-port": "NTQzMg==",
                "db-name": "bWFyYWJldF9zdGFnaW5n",
                "db-username": "bWFyYWJldF91c2Vy",
                "db-password": "c3RhZ2luZ19wYXNzd29yZF8xMjM=",
                
                # API keys (staging)
                "api-football-key": "c3RhZ2luZ19hcGlfZm9vdGJhbGxfa2V5",
                "telegram-bot-token": "c3RhZ2luZ190ZWxlZ3JhbV9ib3RfdG9rZW4=",
                "slack-webhook-url": "c3RhZ2luZ19zbGFja193ZWJob29rX3VybA==",
                
                # JWT secrets (staging)
                "jwt-secret": "c3RhZ2luZ19qd3Rfc2VjcmV0X2tleV9oZXJl",
                "jwt-refresh-secret": "c3RhZ2luZ19qd3RfcmVmcmVzaF9zZWNyZXRfa2V5",
                
                # Encryption keys (staging)
                "encryption-key": "c3RhZ2luZ19lbmNyeXB0aW9uX2tleV9oZXJl",
                "backup-encryption-key": "c3RhZ2luZ19iYWNrdXBfZW5jcnlwdGlvbl9rZXk=",
                
                # SSL certificates (staging)
                "ssl-cert": "c3RhZ2luZ19zc2xfY2VydGlmaWNhdGU=",
                "ssl-key": "c3RhZ2luZ19zc2xfcHJpdmF0ZV9rZXk=",
                
                # OAuth tokens (staging)
                "oauth-client-id": "c3RhZ2luZ19vYXV0aF9jbGllbnRfaWQ=",
                "oauth-client-secret": "c3RhZ2luZ19vYXV0aF9jbGllbnRfc2VjcmV0",
                
                # Monitoring (staging)
                "sentry-dsn": "c3RhZ2luZ19zZW50cnlfZHNu",
                "prometheus-endpoint": "c3RhZ2luZ19wcm9tZXRoZXVzX2VuZHBvaW50",
                
                # Cloud storage (staging)
                "aws-access-key": "c3RhZ2luZ19hd3NfYWNjZXNzX2tleQ==",
                "aws-secret-key": "c3RhZ2luZ19hd3Nfc2VjcmV0X2tleQ==",
                "s3-bucket": "bWFyYWJldC1zdGFnaW5nLWJhY2t1cHM="
            }
        }
        
        return yaml.dump(secrets, default_flow_style=False)
    
    def generate_staging_hpa(self) -> str:
        """Gera HPA do staging"""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "marabet-ai-staging-hpa",
                "namespace": self.config.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "marabet-ai-staging"
                },
                "minReplicas": 1,
                "maxReplicas": 5,
                "metrics": [{
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 70
                        }
                    }
                }, {
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 80
                        }
                    }
                }]
            }
        }
        
        return yaml.dump(hpa, default_flow_style=False)
    
    def generate_staging_pdb(self) -> str:
        """Gera PDB do staging"""
        pdb = {
            "apiVersion": "policy/v1",
            "kind": "PodDisruptionBudget",
            "metadata": {
                "name": "marabet-ai-staging-pdb",
                "namespace": self.config.namespace
            },
            "spec": {
                "minAvailable": 1,
                "selector": {
                    "matchLabels": {
                        "app": "marabet-ai",
                        "environment": "staging"
                    }
                }
            }
        }
        
        return yaml.dump(pdb, default_flow_style=False)
    
    def generate_staging_monitoring(self) -> str:
        """Gera monitoramento do staging"""
        monitoring = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "staging-monitoring-config",
                "namespace": self.config.namespace
            },
            "data": {
                "prometheus-rules.yaml": """
groups:
- name: marabet-staging
  rules:
  - alert: StagingHighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
      environment: staging
    annotations:
      summary: "High CPU usage in staging"
      description: "CPU usage is above 80% for 5 minutes"
  
  - alert: StagingHighMemoryUsage
    expr: memory_usage_percent > 85
    for: 5m
    labels:
      severity: warning
      environment: staging
    annotations:
      summary: "High memory usage in staging"
      description: "Memory usage is above 85% for 5 minutes"
  
  - alert: StagingPodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[5m]) > 0
    for: 2m
    labels:
      severity: critical
      environment: staging
    annotations:
      summary: "Pod crash looping in staging"
      description: "Pod {{ $labels.pod }} is crash looping"
""",
                "grafana-dashboard.json": json.dumps({
                    "dashboard": {
                        "title": "MaraBet AI Staging Dashboard",
                        "panels": [
                            {
                                "title": "CPU Usage",
                                "type": "graph",
                                "targets": [
                                    {
                                        "expr": "cpu_usage_percent",
                                        "legendFormat": "CPU Usage %"
                                    }
                                ]
                            },
                            {
                                "title": "Memory Usage",
                                "type": "graph",
                                "targets": [
                                    {
                                        "expr": "memory_usage_percent",
                                        "legendFormat": "Memory Usage %"
                                    }
                                ]
                            },
                            {
                                "title": "Request Rate",
                                "type": "graph",
                                "targets": [
                                    {
                                        "expr": "rate(http_requests_total[5m])",
                                        "legendFormat": "Requests/sec"
                                    }
                                ]
                            }
                        ]
                    }
                }, indent=2)
            }
        }
        
        return yaml.dump(monitoring, default_flow_style=False)
    
    def generate_staging_tests(self) -> str:
        """Gera testes do staging"""
        tests = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": "marabet-staging-tests",
                "namespace": self.config.namespace
            },
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "staging-tests",
                            "image": "your-registry.com/marabet-ai:staging",
                            "command": ["/bin/bash"],
                            "args": ["-c", "pytest tests/e2e/ -v --env=staging"],
                            "env": [
                                {"name": "ENVIRONMENT", "value": "staging"},
                                {"name": "DATABASE_URL", "value": self.config.database_url},
                                {"name": "REDIS_URL", "value": self.config.redis_url}
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "256Mi",
                                    "cpu": "100m"
                                },
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "250m"
                                }
                            }
                        }],
                        "restartPolicy": "Never"
                    }
                },
                "backoffLimit": 3
            }
        }
        
        return yaml.dump(tests, default_flow_style=False)
    
    def generate_all_staging_configs(self):
        """Gera todas as configurações do staging"""
        print("🧪 GERANDO CONFIGURAÇÕES DO AMBIENTE DE STAGING")
        print("=" * 60)
        
        # Namespace
        namespace = self.generate_staging_namespace()
        with open(f"{self.staging_dir}/namespace.yaml", "w") as f:
            f.write(namespace)
        print("✅ Namespace do staging gerado")
        
        # Deployment
        deployment = self.generate_staging_deployment()
        with open(f"{self.staging_dir}/deployment.yaml", "w") as f:
            f.write(deployment)
        print("✅ Deployment do staging gerado")
        
        # Service
        service = self.generate_staging_service()
        with open(f"{self.staging_dir}/service.yaml", "w") as f:
            f.write(service)
        print("✅ Service do staging gerado")
        
        # Ingress
        ingress = self.generate_staging_ingress()
        with open(f"{self.staging_dir}/ingress.yaml", "w") as f:
            f.write(ingress)
        print("✅ Ingress do staging gerado")
        
        # ConfigMap
        configmap = self.generate_staging_configmap()
        with open(f"{self.staging_dir}/configmap.yaml", "w") as f:
            f.write(configmap)
        print("✅ ConfigMap do staging gerado")
        
        # Secrets
        secrets = self.generate_staging_secrets()
        with open(f"{self.staging_dir}/secrets.yaml", "w") as f:
            f.write(secrets)
        print("✅ Secrets do staging gerados")
        
        # HPA
        hpa = self.generate_staging_hpa()
        with open(f"{self.staging_dir}/hpa.yaml", "w") as f:
            f.write(hpa)
        print("✅ HPA do staging gerado")
        
        # PDB
        pdb = self.generate_staging_pdb()
        with open(f"{self.staging_dir}/pdb.yaml", "w") as f:
            f.write(pdb)
        print("✅ PDB do staging gerado")
        
        # Monitoring
        monitoring = self.generate_staging_monitoring()
        with open(f"{self.staging_dir}/monitoring.yaml", "w") as f:
            f.write(monitoring)
        print("✅ Monitoramento do staging gerado")
        
        # Tests
        tests = self.generate_staging_tests()
        with open(f"{self.staging_dir}/tests.yaml", "w") as f:
            f.write(tests)
        print("✅ Testes do staging gerados")
        
        print("\n🎉 TODAS AS CONFIGURAÇÕES DO STAGING GERADAS COM SUCESSO!")

def create_production_staging_config():
    """Cria configuração de staging para produção"""
    staging_config = StagingConfig(
        environment=EnvironmentType.STAGING,
        namespace="marabet-staging",
        domain="staging.marabet.com",
        database_url="postgresql://marabet_user:staging_password_123@marabet-staging.cluster-xyz.us-east-1.rds.amazonaws.com:5432/marabet_staging",
        redis_url="redis://marabet-staging-redis.cache.amazonaws.com:6379/0",
        s3_bucket="marabet-staging-backups",
        replicas=2,
        resources={
            "requests": {"memory": "256Mi", "cpu": "100m"},
            "limits": {"memory": "512Mi", "cpu": "250m"}
        }
    )
    
    return staging_config

if __name__ == "__main__":
    # Criar configuração de staging
    staging_config = create_production_staging_config()
    
    # Gerar configurações
    manager = StagingEnvironmentManager(staging_config)
    manager.generate_all_staging_configs()
    
    print("\n🎉 CONFIGURAÇÕES DO AMBIENTE DE STAGING GERADAS!")
