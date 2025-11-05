#!/usr/bin/env python3
"""
Sistema de CI/CD Pipeline
MaraBet AI - Pipeline completo de integração e deploy contínuo
"""

import json
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class PipelineProvider(Enum):
    """Provedores de CI/CD"""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"
    AWS_CODEPIPELINE = "aws_codepipeline"

class Environment(Enum):
    """Ambientes"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class PipelineConfig:
    """Configuração do pipeline"""
    provider: PipelineProvider
    repository: str
    branch: str
    environments: List[Environment]
    docker_registry: str
    k8s_cluster: str
    notification_webhook: str = ""

class CICDPipelineManager:
    """Gerenciador de pipeline CI/CD"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.templates_dir = "infrastructure/templates"
        self.pipelines_dir = ".github/workflows"
        
        # Criar diretórios
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.pipelines_dir, exist_ok=True)
        os.makedirs("infrastructure/kubernetes", exist_ok=True)
        os.makedirs("infrastructure/docker", exist_ok=True)
    
    def generate_github_actions_workflow(self) -> str:
        """Gera workflow do GitHub Actions"""
        workflow = {
            "name": "MaraBet AI CI/CD Pipeline",
            "on": {
                "push": {
                    "branches": ["main", "develop"]
                },
                "pull_request": {
                    "branches": ["main"]
                },
                "workflow_dispatch": {
                    "inputs": {
                        "environment": {
                            "description": "Environment to deploy",
                            "required": True,
                            "default": "staging",
                            "type": "choice",
                            "options": ["staging", "production"]
                        }
                    }
                }
            },
            "env": {
                "DOCKER_REGISTRY": self.config.docker_registry,
                "K8S_CLUSTER": self.config.k8s_cluster,
                "APP_NAME": "marabet-ai"
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.11"
                            }
                        },
                        {
                            "name": "Cache dependencies",
                            "uses": "actions/cache@v3",
                            "with": {
                                "path": "~/.cache/pip",
                                "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run linting",
                            "run": "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
                        },
                        {
                            "name": "Run security scan",
                            "run": "bandit -r . -f json -o bandit-report.json"
                        },
                        {
                            "name": "Run unit tests",
                            "run": "pytest tests/unit/ -v --cov=. --cov-report=xml"
                        },
                        {
                            "name": "Run integration tests",
                            "run": "pytest tests/integration/ -v"
                        },
                        {
                            "name": "Upload coverage to Codecov",
                            "uses": "codecov/codecov-action@v3",
                            "with": {
                                "file": "./coverage.xml"
                            }
                        },
                        {
                            "name": "Upload security report",
                            "uses": "actions/upload-artifact@v3",
                            "with": {
                                "name": "security-report",
                                "path": "bandit-report.json"
                            }
                        }
                    ]
                },
                "build": {
                    "runs-on": "ubuntu-latest",
                    "needs": "test",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3"
                        },
                        {
                            "name": "Login to Docker Registry",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "registry": self.config.docker_registry,
                                "username": "${{ secrets.DOCKER_USERNAME }}",
                                "password": "${{ secrets.DOCKER_PASSWORD }}"
                            }
                        },
                        {
                            "name": "Build and push Docker image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "file": "./Dockerfile",
                                "push": True,
                                "tags": [
                                    f"{self.config.docker_registry}/marabet-ai:${{ github.sha }}",
                                    f"{self.config.docker_registry}/marabet-ai:latest"
                                ],
                                "cache-from": "type=gha",
                                "cache-to": "type=gha,mode=max"
                            }
                        }
                    ]
                },
                "deploy-staging": {
                    "runs-on": "ubuntu-latest",
                    "needs": "build",
                    "if": "github.ref == 'refs/heads/develop'",
                    "environment": "staging",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Configure AWS credentials",
                            "uses": "aws-actions/configure-aws-credentials@v4",
                            "with": {
                                "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
                                "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
                                "aws-region": "us-east-1"
                            }
                        },
                        {
                            "name": "Update kubeconfig",
                            "run": "aws eks update-kubeconfig --region us-east-1 --name ${{ env.K8S_CLUSTER }}"
                        },
                        {
                            "name": "Deploy to staging",
                            "run": "kubectl apply -f infrastructure/kubernetes/staging/"
                        },
                        {
                            "name": "Wait for deployment",
                            "run": "kubectl rollout status deployment/marabet-ai -n marabet-staging --timeout=300s"
                        },
                        {
                            "name": "Run smoke tests",
                            "run": "pytest tests/e2e/ -v --env=staging"
                        },
                        {
                            "name": "Notify deployment",
                            "uses": "8398a7/action-slack@v3",
                            "with": {
                                "status": "success",
                                "text": "MaraBet AI deployed to staging successfully! 🚀"
                            },
                            "env": {
                                "SLACK_WEBHOOK_URL": "${{ secrets.SLACK_WEBHOOK_URL }}"
                            }
                        }
                    ]
                },
                "deploy-production": {
                    "runs-on": "ubuntu-latest",
                    "needs": "build",
                    "if": "github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'",
                    "environment": "production",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Configure AWS credentials",
                            "uses": "aws-actions/configure-aws-credentials@v4",
                            "with": {
                                "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
                                "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
                                "aws-region": "us-east-1"
                            }
                        },
                        {
                            "name": "Update kubeconfig",
                            "run": "aws eks update-kubeconfig --region us-east-1 --name ${{ env.K8S_CLUSTER }}"
                        },
                        {
                            "name": "Create backup",
                            "run": "kubectl exec -n marabet deployment/marabet-ai -- /scripts/backup.sh full"
                        },
                        {
                            "name": "Deploy to production",
                            "run": "kubectl apply -f infrastructure/kubernetes/production/"
                        },
                        {
                            "name": "Wait for deployment",
                            "run": "kubectl rollout status deployment/marabet-ai -n marabet --timeout=600s"
                        },
                        {
                            "name": "Run health checks",
                            "run": "kubectl exec -n marabet deployment/marabet-ai -- /scripts/health-check.sh"
                        },
                        {
                            "name": "Run smoke tests",
                            "run": "pytest tests/e2e/ -v --env=production"
                        },
                        {
                            "name": "Notify deployment",
                            "uses": "8398a7/action-slack@v3",
                            "with": {
                                "status": "success",
                                "text": "MaraBet AI deployed to production successfully! 🎉"
                            },
                            "env": {
                                "SLACK_WEBHOOK_URL": "${{ secrets.SLACK_WEBHOOK_URL }}"
                            }
                        }
                    ]
                },
                "rollback": {
                    "runs-on": "ubuntu-latest",
                    "if": "failure()",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Configure AWS credentials",
                            "uses": "aws-actions/configure-aws-credentials@v4",
                            "with": {
                                "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
                                "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
                                "aws-region": "us-east-1"
                            }
                        },
                        {
                            "name": "Update kubeconfig",
                            "run": "aws eks update-kubeconfig --region us-east-1 --name ${{ env.K8S_CLUSTER }}"
                        },
                        {
                            "name": "Rollback deployment",
                            "run": "kubectl rollout undo deployment/marabet-ai -n marabet"
                        },
                        {
                            "name": "Notify rollback",
                            "uses": "8398a7/action-slack@v3",
                            "with": {
                                "status": "warning",
                                "text": "MaraBet AI deployment rolled back due to failure! ⚠️"
                            },
                            "env": {
                                "SLACK_WEBHOOK_URL": "${{ secrets.SLACK_WEBHOOK_URL }}"
                            }
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False)
    
    def generate_jenkins_pipeline(self) -> str:
        """Gera pipeline do Jenkins"""
        pipeline = f"""pipeline {{
    agent any
    
    environment {{
        DOCKER_REGISTRY = '{self.config.docker_registry}'
        K8S_CLUSTER = '{self.config.k8s_cluster}'
        APP_NAME = 'marabet-ai'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Test') {{
            parallel {{
                stage('Unit Tests') {{
                    steps {{
                        sh 'pip install -r requirements.txt'
                        sh 'pytest tests/unit/ -v --cov=. --cov-report=xml'
                    }}
                    post {{
                        always {{
                            publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                        }}
                    }}
                }}
                
                stage('Integration Tests') {{
                    steps {{
                        sh 'pytest tests/integration/ -v'
                    }}
                }}
                
                stage('Security Scan') {{
                    steps {{
                        sh 'bandit -r . -f json -o bandit-report.json'
                    }}
                    post {{
                        always {{
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: '.',
                                reportFiles: 'bandit-report.json',
                                reportName: 'Security Report'
                            ])
                        }}
                    }}
                }}
            }}
        }}
        
        stage('Build') {{
            when {{
                anyOf {{
                    branch 'main'
                    branch 'develop'
                }}
            }}
            steps {{
                script {{
                    def image = docker.build("${{DOCKER_REGISTRY}}/${{APP_NAME}}:${{BUILD_NUMBER}}")
                    docker.withRegistry('https://${{DOCKER_REGISTRY}}', 'docker-registry-credentials') {{
                        image.push()
                        image.push('latest')
                    }}
                }}
            }}
        }}
        
        stage('Deploy Staging') {{
            when {{
                branch 'develop'
            }}
            steps {{
                sh 'kubectl apply -f infrastructure/kubernetes/staging/'
                sh 'kubectl rollout status deployment/marabet-ai -n marabet-staging --timeout=300s'
                sh 'pytest tests/e2e/ -v --env=staging'
            }}
        }}
        
        stage('Deploy Production') {{
            when {{
                branch 'main'
            }}
            steps {{
                sh 'kubectl exec -n marabet deployment/marabet-ai -- /scripts/backup.sh full'
                sh 'kubectl apply -f infrastructure/kubernetes/production/'
                sh 'kubectl rollout status deployment/marabet-ai -n marabet --timeout=600s'
                sh 'kubectl exec -n marabet deployment/marabet-ai -- /scripts/health-check.sh'
                sh 'pytest tests/e2e/ -v --env=production'
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            slackSend channel: '#deployments',
                      color: 'good',
                      message: 'MaraBet AI deployment successful! 🚀'
        }}
        failure {{
            slackSend channel: '#deployments',
                      color: 'danger',
                      message: 'MaraBet AI deployment failed! ⚠️'
        }}
    }}
}}"""
        return pipeline
    
    def generate_dockerfile(self) -> str:
        """Gera Dockerfile otimizado"""
        dockerfile = """# Multi-stage build for MaraBet AI
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \\
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    redis-tools \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r marabet && useradd -r -g marabet marabet

# Create app directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs backups data && \\
    chown -R marabet:marabet /app

# Switch to non-root user
USER marabet

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start application
CMD ["python", "app.py"]
"""
        return dockerfile
    
    def generate_kubernetes_manifests(self) -> str:
        """Gera manifestos do Kubernetes"""
        # Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "marabet-ai",
                "namespace": "marabet",
                "labels": {
                    "app": "marabet-ai",
                    "version": "v1.0.0"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "marabet-ai"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "marabet-ai",
                            "version": "v1.0.0"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "marabet-ai",
                            "image": f"{self.config.docker_registry}/marabet-ai:latest",
                            "ports": [{
                                "containerPort": 5000,
                                "name": "http"
                            }],
                            "env": [
                                {"name": "FLASK_ENV", "value": "production"},
                                {"name": "DATABASE_URL", "valueFrom": {"secretKeyRef": {"name": "marabet-secrets", "key": "db-url"}}},
                                {"name": "REDIS_URL", "valueFrom": {"secretKeyRef": {"name": "marabet-secrets", "key": "redis-url"}}},
                                {"name": "JWT_SECRET", "valueFrom": {"secretKeyRef": {"name": "marabet-secrets", "key": "jwt-secret"}}}
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "512Mi",
                                    "cpu": "250m"
                                },
                                "limits": {
                                    "memory": "1Gi",
                                    "cpu": "500m"
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
                            "persistentVolumeClaim": {
                                "claimName": "marabet-data-pvc"
                            }
                        }],
                        "imagePullSecrets": [{
                            "name": "docker-registry-secret"
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
                "name": "marabet-ai-service",
                "namespace": "marabet"
            },
            "spec": {
                "selector": {
                    "app": "marabet-ai"
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 5000,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
        
        # ConfigMap
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "marabet-config",
                "namespace": "marabet"
            },
            "data": {
                "app.conf": """
[app]
debug = false
host = 0.0.0.0
port = 5000

[database]
pool_size = 20
max_overflow = 30
pool_timeout = 30
pool_recycle = 3600

[redis]
max_connections = 20
socket_timeout = 5
socket_connect_timeout = 5

[logging]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
            }
        }
        
        return {
            "deployment": yaml.dump(deployment, default_flow_style=False),
            "service": yaml.dump(service, default_flow_style=False),
            "configmap": yaml.dump(configmap, default_flow_style=False)
        }
    
    def generate_terraform_infrastructure(self) -> str:
        """Gera infraestrutura Terraform"""
        terraform_config = {
            "terraform": {
                "required_version": ">= 1.0",
                "required_providers": {
                    "aws": {
                        "source": "hashicorp/aws",
                        "version": "~> 5.0"
                    },
                    "kubernetes": {
                        "source": "hashicorp/kubernetes",
                        "version": "~> 2.0"
                    }
                }
            },
            "provider": {
                "aws": {
                    "region": "us-east-1"
                }
            },
            "resource": {
                "aws_eks_cluster": {
                    "marabet_cluster": {
                        "name": self.config.k8s_cluster,
                        "role_arn": "${aws_iam_role.eks_cluster_role.arn}",
                        "vpc_config": {
                            "subnet_ids": ["${aws_subnet.private_1.id}", "${aws_subnet.private_2.id}"],
                            "endpoint_private_access": True,
                            "endpoint_public_access": True
                        },
                        "enabled_cluster_log_types": ["api", "audit", "authenticator", "controllerManager", "scheduler"],
                        "tags": {
                            "Name": "MaraBet EKS Cluster",
                            "Environment": "production"
                        }
                    }
                },
                "aws_eks_node_group": {
                    "marabet_nodes": {
                        "cluster_name": "${aws_eks_cluster.marabet_cluster.name}",
                        "node_group_name": "marabet-nodes",
                        "node_role_arn": "${aws_iam_role.eks_node_role.arn}",
                        "subnet_ids": ["${aws_subnet.private_1.id}", "${aws_subnet.private_2.id}"],
                        "instance_types": ["t3.medium"],
                        "capacity_type": "ON_DEMAND",
                        "scaling_config": {
                            "desired_size": 3,
                            "max_size": 10,
                            "min_size": 1
                        },
                        "update_config": {
                            "max_unavailable_percentage": 25
                        },
                        "tags": {
                            "Name": "MaraBet EKS Nodes",
                            "Environment": "production"
                        }
                    }
                }
            }
        }
        
        return json.dumps(terraform_config, indent=2)
    
    def generate_all_configs(self):
        """Gera todas as configurações de CI/CD"""
        print("🚀 GERANDO CONFIGURAÇÕES DE CI/CD PIPELINE")
        print("=" * 60)
        
        # GitHub Actions
        if self.config.provider == PipelineProvider.GITHUB_ACTIONS:
            github_workflow = self.generate_github_actions_workflow()
            with open(f"{self.pipelines_dir}/ci-cd.yml", "w") as f:
                f.write(github_workflow)
            print("✅ Workflow GitHub Actions gerado")
        
        # Jenkins
        elif self.config.provider == PipelineProvider.JENKINS:
            jenkins_pipeline = self.generate_jenkins_pipeline()
            with open(f"{self.templates_dir}/Jenkinsfile", "w") as f:
                f.write(jenkins_pipeline)
            print("✅ Pipeline Jenkins gerado")
        
        # Dockerfile
        dockerfile = self.generate_dockerfile()
        with open(f"{self.templates_dir}/Dockerfile", "w") as f:
            f.write(dockerfile)
        print("✅ Dockerfile gerado")
        
        # Kubernetes manifests
        k8s_manifests = self.generate_kubernetes_manifests()
        
        # Create staging directory
        os.makedirs("infrastructure/kubernetes/staging", exist_ok=True)
        os.makedirs("infrastructure/kubernetes/production", exist_ok=True)
        
        # Staging manifests
        with open("infrastructure/kubernetes/staging/deployment.yaml", "w") as f:
            f.write(k8s_manifests["deployment"])
        with open("infrastructure/kubernetes/staging/service.yaml", "w") as f:
            f.write(k8s_manifests["service"])
        with open("infrastructure/kubernetes/staging/configmap.yaml", "w") as f:
            f.write(k8s_manifests["configmap"])
        
        # Production manifests
        with open("infrastructure/kubernetes/production/deployment.yaml", "w") as f:
            f.write(k8s_manifests["deployment"])
        with open("infrastructure/kubernetes/production/service.yaml", "w") as f:
            f.write(k8s_manifests["service"])
        with open("infrastructure/kubernetes/production/configmap.yaml", "w") as f:
            f.write(k8s_manifests["configmap"])
        
        print("✅ Manifestos Kubernetes gerados")
        
        # Terraform infrastructure
        terraform_config = self.generate_terraform_infrastructure()
        with open(f"{self.templates_dir}/infrastructure.tf", "w") as f:
            f.write(terraform_config)
        print("✅ Configuração Terraform gerada")
        
        print("\n🎉 TODAS AS CONFIGURAÇÕES DE CI/CD GERADAS COM SUCESSO!")

def create_production_cicd_config():
    """Cria configuração de CI/CD para produção"""
    cicd_config = PipelineConfig(
        provider=PipelineProvider.GITHUB_ACTIONS,
        repository="maravilha/marabet-ai",
        branch="main",
        environments=[Environment.STAGING, Environment.PRODUCTION],
        docker_registry="your-registry.com",
        k8s_cluster="marabet-cluster",
        notification_webhook="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    )
    
    return cicd_config

if __name__ == "__main__":
    # Criar configuração de produção
    cicd_config = create_production_cicd_config()
    
    # Gerar configurações
    manager = CICDPipelineManager(cicd_config)
    manager.generate_all_configs()
    
    print("\n🎉 CONFIGURAÇÕES DE CI/CD PIPELINE GERADAS!")
