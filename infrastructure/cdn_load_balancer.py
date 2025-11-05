#!/usr/bin/env python3
"""
Sistema de CDN e Load Balancer
MaraBet AI - Infraestrutura de produção com CDN e Load Balancer
"""

import json
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class CDNProvider(Enum):
    """Provedores de CDN"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    GOOGLE_CLOUD_CDN = "google_cloud_cdn"
    AZURE_CDN = "azure_cdn"

class LoadBalancerType(Enum):
    """Tipos de Load Balancer"""
    APPLICATION = "application"
    NETWORK = "network"
    CLASSIC = "classic"

@dataclass
class CDNConfig:
    """Configuração de CDN"""
    provider: CDNProvider
    domain: str
    origin: str
    ssl_enabled: bool = True
    compression_enabled: bool = True
    cache_ttl: int = 3600
    custom_headers: Dict[str, str] = None

@dataclass
class LoadBalancerConfig:
    """Configuração de Load Balancer"""
    type: LoadBalancerType
    health_check_path: str = "/api/health"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_healthy_threshold: int = 2
    health_check_unhealthy_threshold: int = 3
    sticky_sessions: bool = False
    ssl_termination: bool = True

class CDNLoadBalancerManager:
    """Gerenciador de CDN e Load Balancer"""
    
    def __init__(self, cdn_config: CDNConfig, lb_config: LoadBalancerConfig):
        self.cdn_config = cdn_config
        self.lb_config = lb_config
        self.templates_dir = "infrastructure/templates"
        
        # Criar diretórios
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs("infrastructure/terraform", exist_ok=True)
        os.makedirs("infrastructure/kubernetes", exist_ok=True)
    
    def generate_cloudflare_config(self) -> str:
        """Gera configuração do Cloudflare"""
        config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "cloudflare-config",
                "namespace": "marabet"
            },
            "data": {
                "cloudflare.toml": f"""
# Cloudflare configuration for MaraBet AI
[env.production]
zone_id = "{self.cdn_config.domain}"
account_id = "your_account_id"

[[env.production.routes]]
pattern = "marabet.com/*"
custom_domain = true

[[env.production.routes]]
pattern = "api.marabet.com/*"
custom_domain = true

[env.production.routes.origin]
url = "{self.cdn_config.origin}"

[env.production.routes.origin.originRequest]
httpHostHeader = "marabet.com"

[env.production.routes.origin.originRequest.originServerName]
"marabet.com" = "marabet.com"

[env.production.routes.origin.originRequest.originServerName]
"api.marabet.com" = "api.marabet.com"

# Cache rules
[[env.production.routes.rules]]
type = "Cache"
action = "Cache"
ttl = {self.cdn_config.cache_ttl}

# Security headers
[[env.production.routes.rules]]
type = "Rewrite"
action = "Rewrite"
headers = {{
    "X-Content-Type-Options" = "nosniff"
    "X-Frame-Options" = "DENY"
    "X-XSS-Protection" = "1; mode=block"
    "Strict-Transport-Security" = "max-age=31536000; includeSubDomains"
    "Content-Security-Policy" = "default-src 'self'"
}}

# Compression
[[env.production.routes.rules]]
type = "Rewrite"
action = "Rewrite"
headers = {{
    "Accept-Encoding" = "gzip, deflate, br"
}}

# SSL/TLS
[env.production.routes.origin.tls]
verify = true
"""
            }
        }
        
        return yaml.dump(config, default_flow_style=False)
    
    def generate_aws_cloudfront_config(self) -> str:
        """Gera configuração do AWS CloudFront"""
        terraform_config = {
            "resource": {
                "aws_cloudfront_distribution": {
                    "marabet_distribution": {
                        "origin": [{
                            "domain_name": self.cdn_config.origin,
                            "origin_id": "marabet-origin",
                            "custom_origin_config": {
                                "http_port": 80,
                                "https_port": 443,
                                "origin_protocol_policy": "https-only",
                                "origin_ssl_protocols": ["TLSv1.2"]
                            }
                        }],
                        "enabled": True,
                        "is_ipv6_enabled": True,
                        "default_root_object": "index.html",
                        "default_cache_behavior": {
                            "allowed_methods": ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
                            "cached_methods": ["GET", "HEAD"],
                            "target_origin_id": "marabet-origin",
                            "forwarded_values": {
                                "query_string": False,
                                "cookies": {
                                    "forward": "none"
                                }
                            },
                            "viewer_protocol_policy": "redirect-to-https",
                            "min_ttl": 0,
                            "default_ttl": self.cdn_config.cache_ttl,
                            "max_ttl": 31536000,
                            "compress": self.cdn_config.compression_enabled
                        },
                        "custom_error_response": [{
                            "error_code": 404,
                            "response_code": 200,
                            "response_page_path": "/index.html"
                        }],
                        "price_class": "PriceClass_100",
                        "restrictions": {
                            "geo_restriction": {
                                "restriction_type": "none"
                            }
                        },
                        "viewer_certificate": {
                            "cloudfront_default_certificate": True
                        },
                        "tags": {
                            "Name": "MaraBet AI CDN",
                            "Environment": "production"
                        }
                    }
                }
            }
        }
        
        return json.dumps(terraform_config, indent=2)
    
    def generate_load_balancer_config(self) -> str:
        """Gera configuração do Load Balancer"""
        if self.lb_config.type == LoadBalancerType.APPLICATION:
            return self._generate_alb_config()
        elif self.lb_config.type == LoadBalancerType.NETWORK:
            return self._generate_nlb_config()
        else:
            return self._generate_classic_lb_config()
    
    def _generate_alb_config(self) -> str:
        """Gera configuração do Application Load Balancer"""
        terraform_config = {
            "resource": {
                "aws_lb": {
                    "marabet_alb": {
                        "name": "marabet-alb",
                        "internal": False,
                        "load_balancer_type": "application",
                        "security_groups": ["${aws_security_group.alb_sg.id}"],
                        "subnets": ["${aws_subnet.public_1.id}", "${aws_subnet.public_2.id}"],
                        "enable_deletion_protection": True,
                        "tags": {
                            "Name": "MaraBet ALB",
                            "Environment": "production"
                        }
                    }
                },
                "aws_lb_target_group": {
                    "marabet_tg": {
                        "name": "marabet-tg",
                        "port": 5000,
                        "protocol": "HTTP",
                        "vpc_id": "${aws_vpc.main.id}",
                        "target_type": "ip",
                        "health_check": {
                            "enabled": True,
                            "healthy_threshold": self.lb_config.health_check_healthy_threshold,
                            "interval": self.lb_config.health_check_interval,
                            "matcher": "200",
                            "path": self.lb_config.health_check_path,
                            "port": "traffic-port",
                            "protocol": "HTTP",
                            "timeout": self.lb_config.health_check_timeout,
                            "unhealthy_threshold": self.lb_config.health_check_unhealthy_threshold
                        },
                        "stickiness": {
                            "enabled": self.lb_config.sticky_sessions,
                            "type": "lb_cookie",
                            "cookie_duration": 86400
                        },
                        "tags": {
                            "Name": "MaraBet Target Group",
                            "Environment": "production"
                        }
                    }
                },
                "aws_lb_listener": {
                    "marabet_listener": {
                        "load_balancer_arn": "${aws_lb.marabet_alb.arn}",
                        "port": "443",
                        "protocol": "HTTPS",
                        "ssl_policy": "ELBSecurityPolicy-TLS-1-2-2017-01",
                        "certificate_arn": "${aws_acm_certificate.marabet_cert.arn}",
                        "default_action": {
                            "type": "forward",
                            "target_group_arn": "${aws_lb_target_group.marabet_tg.arn}"
                        }
                    }
                },
                "aws_lb_listener_rule": {
                    "marabet_rule": {
                        "listener_arn": "${aws_lb_listener.marabet_listener.arn}",
                        "priority": 100,
                        "action": {
                            "type": "forward",
                            "target_group_arn": "${aws_lb_target_group.marabet_tg.arn}"
                        },
                        "condition": {
                            "field": "path-pattern",
                            "values": ["/*"]
                        }
                    }
                }
            }
        }
        
        return json.dumps(terraform_config, indent=2)
    
    def _generate_nlb_config(self) -> str:
        """Gera configuração do Network Load Balancer"""
        terraform_config = {
            "resource": {
                "aws_lb": {
                    "marabet_nlb": {
                        "name": "marabet-nlb",
                        "internal": False,
                        "load_balancer_type": "network",
                        "subnets": ["${aws_subnet.public_1.id}", "${aws_subnet.public_2.id}"],
                        "enable_deletion_protection": True,
                        "tags": {
                            "Name": "MaraBet NLB",
                            "Environment": "production"
                        }
                    }
                },
                "aws_lb_target_group": {
                    "marabet_tg": {
                        "name": "marabet-tg",
                        "port": 5000,
                        "protocol": "TCP",
                        "vpc_id": "${aws_vpc.main.id}",
                        "target_type": "ip",
                        "health_check": {
                            "enabled": True,
                            "healthy_threshold": self.lb_config.health_check_healthy_threshold,
                            "interval": self.lb_config.health_check_interval,
                            "port": "traffic-port",
                            "protocol": "TCP",
                            "timeout": self.lb_config.health_check_timeout,
                            "unhealthy_threshold": self.lb_config.health_check_unhealthy_threshold
                        },
                        "tags": {
                            "Name": "MaraBet Target Group",
                            "Environment": "production"
                        }
                    }
                },
                "aws_lb_listener": {
                    "marabet_listener": {
                        "load_balancer_arn": "${aws_lb.marabet_nlb.arn}",
                        "port": "443",
                        "protocol": "TCP",
                        "default_action": {
                            "type": "forward",
                            "target_group_arn": "${aws_lb_target_group.marabet_tg.arn}"
                        }
                    }
                }
            }
        }
        
        return json.dumps(terraform_config, indent=2)
    
    def _generate_classic_lb_config(self) -> str:
        """Gera configuração do Classic Load Balancer"""
        terraform_config = {
            "resource": {
                "aws_elb": {
                    "marabet_elb": {
                        "name": "marabet-elb",
                        "availability_zones": ["us-east-1a", "us-east-1b"],
                        "security_groups": ["${aws_security_group.elb_sg.id}"],
                        "listener": [{
                            "instance_port": 5000,
                            "instance_protocol": "HTTP",
                            "lb_port": 80,
                            "lb_protocol": "HTTP"
                        }, {
                            "instance_port": 5000,
                            "instance_protocol": "HTTP",
                            "lb_port": 443,
                            "lb_protocol": "HTTPS",
                            "ssl_certificate_id": "${aws_acm_certificate.marabet_cert.arn}"
                        }],
                        "health_check": {
                            "healthy_threshold": self.lb_config.health_check_healthy_threshold,
                            "unhealthy_threshold": self.lb_config.health_check_unhealthy_threshold,
                            "timeout": self.lb_config.health_check_timeout,
                            "interval": self.lb_config.health_check_interval,
                            "target": f"HTTP:5000{self.lb_config.health_check_path}"
                        },
                        "cross_zone_load_balancing": True,
                        "idle_timeout": 60,
                        "connection_draining": True,
                        "connection_draining_timeout": 300,
                        "tags": {
                            "Name": "MaraBet ELB",
                            "Environment": "production"
                        }
                    }
                }
            }
        }
        
        return json.dumps(terraform_config, indent=2)
    
    def generate_kubernetes_ingress(self) -> str:
        """Gera configuração de Ingress do Kubernetes"""
        ingress_config = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "marabet-ingress",
                "namespace": "marabet",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/proxy-body-size": "10m",
                    "nginx.ingress.kubernetes.io/proxy-read-timeout": "300",
                    "nginx.ingress.kubernetes.io/proxy-send-timeout": "300",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": [self.cdn_config.domain],
                    "secretName": "marabet-tls"
                }],
                "rules": [{
                    "host": self.cdn_config.domain,
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "marabet-service",
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
        
        return yaml.dump(ingress_config, default_flow_style=False)
    
    def generate_nginx_config(self) -> str:
        """Gera configuração do Nginx"""
        nginx_config = f"""
upstream marabet_backend {{
    least_conn;
    server app1:5000 weight=1 max_fails=3 fail_timeout=30s;
    server app2:5000 weight=1 max_fails=3 fail_timeout=30s;
    server app3:5000 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 32;
}}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=marabet_cache:10m max_size=1g inactive=60m use_temp_path=off;

server {{
    listen 80;
    server_name {self.cdn_config.domain};
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {self.cdn_config.domain};
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/marabet.crt;
    ssl_certificate_key /etc/ssl/private/marabet.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # API endpoints
    location /api/ {{
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://marabet_backend;
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
        
        # Cache
        proxy_cache marabet_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        proxy_cache_lock on;
    }}
    
    # Static files
    location /static/ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
        
        # Cache
        proxy_cache marabet_cache;
        proxy_cache_valid 200 1y;
        proxy_cache_use_stale error timeout updating;
    }}
    
    # Health check
    location /health {{
        access_log off;
        proxy_pass http://marabet_backend/api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Main application
    location / {{
        proxy_pass http://marabet_backend;
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
    }}
}}
"""
        return nginx_config
    
    def generate_failover_config(self) -> str:
        """Gera configuração de failover"""
        failover_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "failover-config",
                "namespace": "marabet"
            },
            "data": {
                "failover.sh": """
#!/bin/bash
# Failover script for MaraBet AI

PRIMARY_ENDPOINT="https://api1.marabet.com"
SECONDARY_ENDPOINT="https://api2.marabet.com"
HEALTH_CHECK_PATH="/api/health"
TIMEOUT=5
MAX_RETRIES=3

check_health() {
    local endpoint=$1
    local url="${endpoint}${HEALTH_CHECK_PATH}"
    
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -s --max-time $TIMEOUT "$url" | grep -q "healthy"; then
            return 0
        fi
        sleep 2
    done
    return 1
}

failover() {
    echo "$(date): Starting failover process"
    
    # Check primary endpoint
    if check_health $PRIMARY_ENDPOINT; then
        echo "$(date): Primary endpoint is healthy"
        exit 0
    fi
    
    echo "$(date): Primary endpoint is unhealthy, checking secondary"
    
    # Check secondary endpoint
    if check_health $SECONDARY_ENDPOINT; then
        echo "$(date): Secondary endpoint is healthy, updating DNS"
        # Update DNS to point to secondary
        # This would typically use your DNS provider's API
        update_dns_to_secondary
    else
        echo "$(date): Both endpoints are unhealthy, alerting"
        send_alert "Both primary and secondary endpoints are down"
    fi
}

update_dns_to_secondary() {
    # This would be implemented based on your DNS provider
    echo "$(date): Updating DNS to secondary endpoint"
    # Example for AWS Route 53:
    # aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://failover.json
}

send_alert() {
    local message=$1
    echo "$(date): ALERT: $message"
    # Send alert via email, Slack, etc.
}

# Run failover check
failover
"""
            }
        }
        
        return yaml.dump(failover_config, default_flow_style=False)
    
    def generate_all_configs(self):
        """Gera todas as configurações"""
        print("🌐 GERANDO CONFIGURAÇÕES DE CDN E LOAD BALANCER")
        print("=" * 60)
        
        # CDN configurations
        if self.cdn_config.provider == CDNProvider.CLOUDFLARE:
            cloudflare_config = self.generate_cloudflare_config()
            with open(f"{self.templates_dir}/cloudflare-config.yaml", "w") as f:
                f.write(cloudflare_config)
            print("✅ Configuração Cloudflare gerada")
        
        elif self.cdn_config.provider == CDNProvider.AWS_CLOUDFRONT:
            cloudfront_config = self.generate_aws_cloudfront_config()
            with open(f"{self.templates_dir}/cloudfront.tf", "w") as f:
                f.write(cloudfront_config)
            print("✅ Configuração CloudFront gerada")
        
        # Load Balancer configuration
        lb_config = self.generate_load_balancer_config()
        with open(f"{self.templates_dir}/load_balancer.tf", "w") as f:
            f.write(lb_config)
        print("✅ Configuração Load Balancer gerada")
        
        # Kubernetes Ingress
        ingress_config = self.generate_kubernetes_ingress()
        with open(f"{self.templates_dir}/ingress.yaml", "w") as f:
            f.write(ingress_config)
        print("✅ Configuração Ingress gerada")
        
        # Nginx configuration
        nginx_config = self.generate_nginx_config()
        with open(f"{self.templates_dir}/nginx.conf", "w") as f:
            f.write(nginx_config)
        print("✅ Configuração Nginx gerada")
        
        # Failover configuration
        failover_config = self.generate_failover_config()
        with open(f"{self.templates_dir}/failover.yaml", "w") as f:
            f.write(failover_config)
        print("✅ Configuração Failover gerada")
        
        print("\n🎉 TODAS AS CONFIGURAÇÕES GERADAS COM SUCESSO!")

def create_production_cdn_lb_config():
    """Cria configuração de produção para CDN e Load Balancer"""
    cdn_config = CDNConfig(
        provider=CDNProvider.CLOUDFLARE,
        domain="marabet.com",
        origin="https://api.marabet.com",
        ssl_enabled=True,
        compression_enabled=True,
        cache_ttl=3600,
        custom_headers={
            "X-Custom-Header": "MaraBet-AI",
            "X-Cache-Control": "public, max-age=3600"
        }
    )
    
    lb_config = LoadBalancerConfig(
        type=LoadBalancerType.APPLICATION,
        health_check_path="/api/health",
        health_check_interval=30,
        health_check_timeout=5,
        health_check_healthy_threshold=2,
        health_check_unhealthy_threshold=3,
        sticky_sessions=False,
        ssl_termination=True
    )
    
    return cdn_config, lb_config

if __name__ == "__main__":
    # Criar configuração de produção
    cdn_config, lb_config = create_production_cdn_lb_config()
    
    # Gerar configurações
    manager = CDNLoadBalancerManager(cdn_config, lb_config)
    manager.generate_all_configs()
    
    print("\n🎉 CONFIGURAÇÕES DE CDN E LOAD BALANCER GERADAS!")
