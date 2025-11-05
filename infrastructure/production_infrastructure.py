#!/usr/bin/env python3
"""
Configuração de Infraestrutura de Produção
MaraBet AI - Infraestrutura completa com Disaster Recovery
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    """Ambientes de deploy"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class CloudProvider(Enum):
    """Provedores de nuvem"""
    AWS = "aws"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    DIGITAL_OCEAN = "digital_ocean"
    LINODE = "linode"

@dataclass
class InfrastructureConfig:
    """Configuração de infraestrutura"""
    environment: Environment
    cloud_provider: CloudProvider
    region: str
    availability_zones: List[str]
    vpc_cidr: str
    subnet_cidrs: List[str]
    security_groups: List[Dict[str, Any]]
    load_balancer: Dict[str, Any]
    database: Dict[str, Any]
    cache: Dict[str, Any]
    storage: Dict[str, Any]
    monitoring: Dict[str, Any]
    disaster_recovery: Dict[str, Any]

class ProductionInfrastructure:
    """Gerenciador de infraestrutura de produção"""
    
    def __init__(self, config: InfrastructureConfig):
        self.config = config
        self.templates_dir = "infrastructure/templates"
        self.deployments_dir = "infrastructure/deployments"
        
        # Criar diretórios
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.deployments_dir, exist_ok=True)
    
    def generate_terraform_config(self) -> str:
        """Gera configuração Terraform"""
        terraform_config = {
            "terraform": {
                "required_version": ">= 1.0",
                "required_providers": {
                    "aws": {
                        "source": "hashicorp/aws",
                        "version": "~> 5.0"
                    }
                }
            },
            "provider": {
                "aws": {
                    "region": self.config.region,
                    "default_tags": {
                        "Project": "MaraBet-AI",
                        "Environment": self.config.environment.value
                    }
                }
            },
            "data": {
                "aws_availability_zones": {
                    "available": {
                        "state": "available"
                    }
                }
            },
            "locals": {
                "common_tags": {
                    "Project": "MaraBet-AI",
                    "Environment": self.config.environment.value,
                    "ManagedBy": "Terraform"
                }
            }
        }
        
        # VPC
        terraform_config["resource"] = {
            "aws_vpc": {
                "main": {
                    "cidr_block": self.config.vpc_cidr,
                    "enable_dns_hostnames": True,
                    "enable_dns_support": True,
                    "tags": {
                        "Name": "marabet-vpc",
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
        }
        
        # Subnets
        for i, cidr in enumerate(self.config.subnet_cidrs):
            az = self.config.availability_zones[i % len(self.config.availability_zones)]
            terraform_config["resource"][f"aws_subnet_subnet_{i}"] = {
                "vpc_id": "${aws_vpc.main.id}",
                "cidr_block": cidr,
                "availability_zone": az,
                "map_public_ip_on_launch": True,
                "tags": {
                    "Name": f"marabet-subnet-{i}",
                    **terraform_config["locals"]["common_tags"]
                }
            }
        
        # Security Groups
        for sg in self.config.security_groups:
            terraform_config["resource"][f"aws_security_group_{sg['name']}"] = {
                "name": sg["name"],
                "description": sg["description"],
                "vpc_id": "${aws_vpc.main.id}",
                "ingress": sg["ingress"],
                "egress": sg["egress"],
                "tags": {
                    **terraform_config["locals"]["common_tags"]
                }
            }
        
        # Load Balancer
        if self.config.load_balancer:
            lb_config = self.config.load_balancer
            terraform_config["resource"]["aws_lb"] = {
                "main": {
                    "name": "marabet-alb",
                    "internal": False,
                    "load_balancer_type": "application",
                    "security_groups": [f"${{aws_security_group_{lb_config['security_group']}.id}}"],
                    "subnets": [f"${{aws_subnet_subnet_{i}.id}}" for i in range(len(self.config.subnet_cidrs))],
                    "tags": {
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
        
        # RDS Database
        if self.config.database:
            db_config = self.config.database
            terraform_config["resource"]["aws_db_instance"] = {
                "main": {
                    "identifier": "marabet-db",
                    "engine": db_config["engine"],
                    "engine_version": db_config["engine_version"],
                    "instance_class": db_config["instance_class"],
                    "allocated_storage": db_config["allocated_storage"],
                    "storage_type": db_config["storage_type"],
                    "storage_encrypted": True,
                    "vpc_security_group_ids": [f"${{aws_security_group_{db_config['security_group']}.id}}"],
                    "db_subnet_group_name": "${aws_db_subnet_group.main.name}",
                    "backup_retention_period": db_config["backup_retention_period"],
                    "backup_window": db_config["backup_window"],
                    "maintenance_window": db_config["maintenance_window"],
                    "multi_az": db_config["multi_az"],
                    "deletion_protection": True,
                    "tags": {
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
            
            terraform_config["resource"]["aws_db_subnet_group"] = {
                "main": {
                    "name": "marabet-db-subnet-group",
                    "subnet_ids": [f"${{aws_subnet_subnet_{i}.id}}" for i in range(len(self.config.subnet_cidrs))],
                    "tags": {
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
        
        # ElastiCache Redis
        if self.config.cache:
            cache_config = self.config.cache
            terraform_config["resource"]["aws_elasticache_subnet_group"] = {
                "main": {
                    "name": "marabet-cache-subnet-group",
                    "subnet_ids": [f"${{aws_subnet_subnet_{i}.id}}" for i in range(len(self.config.subnet_cidrs))]
                }
            }
            
            terraform_config["resource"]["aws_elasticache_replication_group"] = {
                "main": {
                    "replication_group_id": "marabet-redis",
                    "description": "MaraBet Redis cluster",
                    "node_type": cache_config["node_type"],
                    "port": 6379,
                    "parameter_group_name": "default.redis7",
                    "num_cache_clusters": cache_config["num_nodes"],
                    "subnet_group_name": "${aws_elasticache_subnet_group.main.name}",
                    "security_group_ids": [f"${{aws_security_group_{cache_config['security_group']}.id}}"],
                    "at_rest_encryption_enabled": True,
                    "transit_encryption_enabled": True,
                    "tags": {
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
        
        # S3 Bucket para backups
        if self.config.storage:
            storage_config = self.config.storage
            terraform_config["resource"]["aws_s3_bucket"] = {
                "backups": {
                    "bucket": f"marabet-backups-{self.config.environment.value}",
                    "tags": {
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
            
            terraform_config["resource"]["aws_s3_bucket_versioning"] = {
                "backups": {
                    "bucket": "${aws_s3_bucket.backups.id}",
                    "versioning_configuration": {
                        "status": "Enabled"
                    }
                }
            }
            
            terraform_config["resource"]["aws_s3_bucket_encryption"] = {
                "backups": {
                    "bucket": "${aws_s3_bucket.backups.id}",
                    "server_side_encryption_configuration": {
                        "rule": {
                            "apply_server_side_encryption_by_default": {
                                "sse_algorithm": "AES256"
                            }
                        }
                    }
                }
            }
        
        # CloudWatch Logs
        if self.config.monitoring:
            monitoring_config = self.config.monitoring
            terraform_config["resource"]["aws_cloudwatch_log_group"] = {
                "main": {
                    "name": "/aws/ecs/marabet",
                    "retention_in_days": monitoring_config["log_retention_days"],
                    "tags": {
                        **terraform_config["locals"]["common_tags"]
                    }
                }
            }
        
        return json.dumps(terraform_config, indent=2)
    
    def generate_docker_compose(self) -> str:
        """Gera docker-compose para produção"""
        compose_config = {
            "version": "3.8",
            "services": {
                "app": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile.production"
                    },
                    "ports": ["5000:5000"],
                    "environment": [
                        "FLASK_ENV=production",
                        "DATABASE_URL=${DATABASE_URL}",
                        "REDIS_URL=${REDIS_URL}",
                        "API_FOOTBALL_KEY=${API_FOOTBALL_KEY}"
                    ],
                    "depends_on": ["redis", "postgres"],
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:5000/api/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx/nginx.conf:/etc/nginx/nginx.conf",
                        "./nginx/ssl:/etc/nginx/ssl"
                    ],
                    "depends_on": ["app"],
                    "restart": "unless-stopped"
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"],
                    "command": "redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}",
                    "volumes": ["redis_data:/data"],
                    "restart": "unless-stopped"
                },
                "postgres": {
                    "image": "postgres:15-alpine",
                    "ports": ["5432:5432"],
                    "environment": [
                        "POSTGRES_DB=${POSTGRES_DB}",
                        "POSTGRES_USER=${POSTGRES_USER}",
                        "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"
                    ],
                    "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    "restart": "unless-stopped"
                },
                "backup": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile.backup"
                    },
                    "environment": [
                        "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}",
                        "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}",
                        "S3_BUCKET=${S3_BUCKET}",
                        "DATABASE_URL=${DATABASE_URL}"
                    ],
                    "depends_on": ["postgres"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "redis_data": {},
                "postgres_data": {}
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False)
    
    def generate_kubernetes_config(self) -> str:
        """Gera configuração Kubernetes"""
        k8s_config = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "marabet"
            }
        }
        
        # Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "marabet-app",
                "namespace": "marabet"
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "marabet"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "marabet"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "marabet",
                            "image": "marabet:latest",
                            "ports": [{"containerPort": 5000}],
                            "env": [
                                {"name": "FLASK_ENV", "value": "production"},
                                {"name": "DATABASE_URL", "valueFrom": {"secretKeyRef": {"name": "marabet-secrets", "key": "database-url"}}},
                                {"name": "REDIS_URL", "valueFrom": {"secretKeyRef": {"name": "marabet-secrets", "key": "redis-url"}}}
                            ],
                            "resources": {
                                "requests": {"memory": "512Mi", "cpu": "250m"},
                                "limits": {"memory": "1Gi", "cpu": "500m"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/api/health", "port": 5000},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/api/health", "port": 5000},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        # Service
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "marabet-service",
                "namespace": "marabet"
            },
            "spec": {
                "selector": {"app": "marabet"},
                "ports": [{"port": 80, "targetPort": 5000}],
                "type": "LoadBalancer"
            }
        }
        
        # Ingress
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "marabet-ingress",
                "namespace": "marabet",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": ["marabet.example.com"],
                    "secretName": "marabet-tls"
                }],
                "rules": [{
                    "host": "marabet.example.com",
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {"name": "marabet-service", "port": {"number": 80}}
                            }
                        }]
                    }
                }]
            }
        }
        
        return yaml.dump([k8s_config, deployment, service, ingress], default_flow_style=False)
    
    def generate_monitoring_config(self) -> str:
        """Gera configuração de monitoramento"""
        prometheus_config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "rule_files": ["rules/*.yml"],
            "scrape_configs": [
                {
                    "job_name": "marabet-app",
                    "static_configs": [{"targets": ["app:5000"]}],
                    "metrics_path": "/api/metrics",
                    "scrape_interval": "5s"
                },
                {
                    "job_name": "redis",
                    "static_configs": [{"targets": ["redis:6379"]}],
                    "scrape_interval": "15s"
                },
                {
                    "job_name": "postgres",
                    "static_configs": [{"targets": ["postgres:5432"]}],
                    "scrape_interval": "15s"
                }
            ]
        }
        
        return yaml.dump(prometheus_config, default_flow_style=False)
    
    def generate_dr_plan(self) -> str:
        """Gera plano de Disaster Recovery"""
        dr_plan = {
            "disaster_recovery_plan": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "rto_rpo": {
                    "critical": {"rto_minutes": 15, "rpo_minutes": 5},
                    "high": {"rto_minutes": 60, "rpo_minutes": 15},
                    "medium": {"rto_minutes": 240, "rpo_minutes": 60},
                    "low": {"rto_minutes": 1440, "rpo_minutes": 360}
                },
                "backup_strategy": {
                    "frequency": "hourly",
                    "retention_days": 30,
                    "encryption": True,
                    "compression": True,
                    "providers": ["aws_s3", "google_cloud", "azure_blob"]
                },
                "recovery_procedures": {
                    "database": {
                        "rto_minutes": 15,
                        "rpo_minutes": 5,
                        "steps": [
                            "1. Identificar backup mais recente",
                            "2. Restaurar banco de dados",
                            "3. Validar integridade dos dados",
                            "4. Atualizar DNS/load balancer",
                            "5. Verificar conectividade da aplicação"
                        ]
                    },
                    "application": {
                        "rto_minutes": 30,
                        "rpo_minutes": 15,
                        "steps": [
                            "1. Provisionar instâncias de aplicação",
                            "2. Deploy do código da aplicação",
                            "3. Configurar variáveis de ambiente",
                            "4. Iniciar serviços da aplicação",
                            "5. Verificar health checks"
                        ]
                    },
                    "infrastructure": {
                        "rto_minutes": 60,
                        "rpo_minutes": 30,
                        "steps": [
                            "1. Provisionar infraestrutura base",
                            "2. Configurar rede e segurança",
                            "3. Deploy de serviços de apoio",
                            "4. Restaurar dados e configurações",
                            "5. Validar funcionamento completo"
                        ]
                    }
                },
                "testing_schedule": {
                    "backup_validation": "daily",
                    "restore_testing": "weekly",
                    "full_dr_test": "monthly"
                },
                "contact_information": {
                    "primary": "admin@marabet.com",
                    "secondary": "ops@marabet.com",
                    "emergency": "+1-555-0123"
                }
            }
        }
        
        return json.dumps(dr_plan, indent=2)
    
    def generate_all_configs(self):
        """Gera todas as configurações de infraestrutura"""
        print("🏗️ GERANDO CONFIGURAÇÕES DE INFRAESTRUTURA")
        print("=" * 60)
        
        # Terraform
        terraform_config = self.generate_terraform_config()
        with open(f"{self.templates_dir}/main.tf", "w") as f:
            f.write(terraform_config)
        print("✅ Configuração Terraform gerada")
        
        # Docker Compose
        docker_compose = self.generate_docker_compose()
        with open(f"{self.templates_dir}/docker-compose.production.yml", "w") as f:
            f.write(docker_compose)
        print("✅ Docker Compose gerado")
        
        # Kubernetes
        k8s_config = self.generate_kubernetes_config()
        with open(f"{self.templates_dir}/k8s.yaml", "w") as f:
            f.write(k8s_config)
        print("✅ Configuração Kubernetes gerada")
        
        # Monitoramento
        monitoring_config = self.generate_monitoring_config()
        with open(f"{self.templates_dir}/prometheus.yml", "w") as f:
            f.write(monitoring_config)
        print("✅ Configuração de monitoramento gerada")
        
        # Plano de DR
        dr_plan = self.generate_dr_plan()
        with open(f"{self.templates_dir}/dr_plan.json", "w") as f:
            f.write(dr_plan)
        print("✅ Plano de Disaster Recovery gerado")
        
        print("\n🎉 TODAS AS CONFIGURAÇÕES GERADAS COM SUCESSO!")

def create_production_config():
    """Cria configuração de produção padrão"""
    config = InfrastructureConfig(
        environment=Environment.PRODUCTION,
        cloud_provider=CloudProvider.AWS,
        region="us-east-1",
        availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"],
        vpc_cidr="10.0.0.0/16",
        subnet_cidrs=["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
        security_groups=[
            {
                "name": "web_sg",
                "description": "Security group for web traffic",
                "ingress": [
                    {"from_port": 80, "to_port": 80, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]},
                    {"from_port": 443, "to_port": 443, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]}
                ],
                "egress": [{"from_port": 0, "to_port": 0, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}]
            },
            {
                "name": "db_sg",
                "description": "Security group for database",
                "ingress": [
                    {"from_port": 5432, "to_port": 5432, "protocol": "tcp", "source_security_group_id": "${aws_security_group_web_sg.id}"}
                ],
                "egress": [{"from_port": 0, "to_port": 0, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}]
            }
        ],
        load_balancer={
            "security_group": "web_sg",
            "type": "application"
        },
        database={
            "engine": "postgres",
            "engine_version": "15.4",
            "instance_class": "db.t3.micro",
            "allocated_storage": 20,
            "storage_type": "gp2",
            "backup_retention_period": 7,
            "backup_window": "03:00-04:00",
            "maintenance_window": "sun:04:00-sun:05:00",
            "multi_az": True,
            "security_group": "db_sg"
        },
        cache={
            "node_type": "cache.t3.micro",
            "num_nodes": 2,
            "security_group": "db_sg"
        },
        storage={
            "backup_bucket": "marabet-backups-production",
            "encryption": True,
            "versioning": True
        },
        monitoring={
            "log_retention_days": 30,
            "metrics_retention_days": 90
        },
        disaster_recovery={
            "rto_minutes": 15,
            "rpo_minutes": 5,
            "backup_frequency": "hourly",
            "retention_days": 30
        }
    )
    
    return config

if __name__ == "__main__":
    # Criar configuração de produção
    config = create_production_config()
    
    # Gerar infraestrutura
    infra = ProductionInfrastructure(config)
    infra.generate_all_configs()
    
    print("\n🎉 INFRAESTRUTURA DE PRODUÇÃO CONFIGURADA!")
