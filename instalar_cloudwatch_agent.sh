#!/bin/bash

################################################################################
# MARABET AI - INSTALAR CLOUDWATCH AGENT
# Monitoramento completo de métricas e logs
################################################################################

set -e

echo "========================================================================"
echo "📊 MaraBet AI - Instalar CloudWatch Agent"
echo "========================================================================"
echo ""

################################################################################
# 1. DOWNLOAD CLOUDWATCH AGENT
################################################################################

echo "1. Baixando CloudWatch Agent..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /tmp

wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

echo "[✓] CloudWatch Agent baixado"

################################################################################
# 2. INSTALAR
################################################################################

echo ""
echo "2. Instalando CloudWatch Agent..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo dpkg -i amazon-cloudwatch-agent.deb

echo "[✓] CloudWatch Agent instalado"

# Verificar versão
AGENT_VERSION=$(/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a query | jq -r '.version' 2>/dev/null || echo "N/A")
echo "[ℹ] Versão: $AGENT_VERSION"

################################################################################
# 3. CRIAR CONFIGURAÇÃO
################################################################################

echo ""
echo "3. Criando configuração..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo tee /opt/aws/amazon-cloudwatch-agent/etc/config.json > /dev/null << 'EOF'
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/opt/marabet/logs/app.log",
            "log_group_name": "/marabet/application",
            "log_stream_name": "{instance_id}",
            "timezone": "Local"
          },
          {
            "file_path": "/opt/marabet/logs/celery.log",
            "log_group_name": "/marabet/celery",
            "log_stream_name": "{instance_id}",
            "timezone": "Local"
          },
          {
            "file_path": "/var/log/nginx/marabet-access.log",
            "log_group_name": "/marabet/nginx",
            "log_stream_name": "{instance_id}-access",
            "timezone": "Local"
          },
          {
            "file_path": "/var/log/nginx/marabet-error.log",
            "log_group_name": "/marabet/nginx",
            "log_stream_name": "{instance_id}-error",
            "timezone": "Local"
          },
          {
            "file_path": "/var/log/marabet/backup.log",
            "log_group_name": "/marabet/backup",
            "log_stream_name": "{instance_id}",
            "timezone": "Local"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "MaraBet/EC2",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "rename": "CPU_IDLE",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_iowait",
            "rename": "CPU_IOWAIT",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_system",
            "rename": "CPU_SYSTEM",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_user",
            "rename": "CPU_USER",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60,
        "totalcpu": true
      },
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DISK_USED",
            "unit": "Percent"
          },
          {
            "name": "free",
            "rename": "DISK_FREE",
            "unit": "Gigabytes"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "diskio": {
        "measurement": [
          {
            "name": "io_time",
            "rename": "DISK_IO_TIME",
            "unit": "Milliseconds"
          },
          {
            "name": "reads",
            "rename": "DISK_READS",
            "unit": "Count"
          },
          {
            "name": "writes",
            "rename": "DISK_WRITES",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MEM_USED",
            "unit": "Percent"
          },
          {
            "name": "mem_available",
            "rename": "MEM_AVAILABLE",
            "unit": "Megabytes"
          }
        ],
        "metrics_collection_interval": 60
      },
      "netstat": {
        "measurement": [
          {
            "name": "tcp_established",
            "rename": "TCP_CONNECTIONS",
            "unit": "Count"
          },
          {
            "name": "tcp_time_wait",
            "rename": "TCP_TIME_WAIT",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60
      },
      "swap": {
        "measurement": [
          {
            "name": "swap_used_percent",
            "rename": "SWAP_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

echo "[✓] Configuração criada"

################################################################################
# 4. INICIAR AGENT
################################################################################

echo ""
echo "4. Iniciando CloudWatch Agent..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json

sleep 3

# Verificar status
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a query \
    -m ec2 \
    -c default

echo ""
echo "[✓] CloudWatch Agent iniciado"

################################################################################
# 5. HABILITAR NO BOOT
################################################################################

echo ""
echo "5. Habilitando no boot..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo systemctl enable amazon-cloudwatch-agent

echo "[✓] CloudWatch Agent habilitado no boot"

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ CLOUDWATCH AGENT INSTALADO!"
echo "========================================================================"
echo ""

echo "Configuração:"
echo "  • Config:        /opt/aws/amazon-cloudwatch-agent/etc/config.json"
echo "  • Namespace:     MaraBet/EC2"
echo "  • Intervalo:     60 segundos"
echo ""

echo "Logs Monitorados:"
echo "  • /opt/marabet/logs/app.log          → /marabet/application"
echo "  • /opt/marabet/logs/celery.log       → /marabet/celery"
echo "  • /var/log/nginx/marabet-access.log  → /marabet/nginx"
echo "  • /var/log/nginx/marabet-error.log   → /marabet/nginx"
echo "  • /var/log/marabet/backup.log        → /marabet/backup"
echo ""

echo "Métricas Coletadas:"
echo "  • CPU (Idle, IOWait, System, User)"
echo "  • Disk (Used%, Free, IO)"
echo "  • Memory (Used%, Available)"
echo "  • Network (Connections)"
echo "  • Swap (Used%)"
echo ""

echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Ver logs no CloudWatch:"
echo "     AWS Console > CloudWatch > Log groups"
echo ""
echo "  2. Ver métricas:"
echo "     AWS Console > CloudWatch > Metrics > MaraBet/EC2"
echo ""
echo "  3. Criar alarmes:"
echo "     ./criar_alarmes_cloudwatch.sh"
echo ""
echo "  4. Criar dashboard:"
echo "     AWS Console > CloudWatch > Dashboards"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Comandos Úteis:"
echo "  Status:  sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a query -m ec2 -c default"
echo "  Stop:    sudo systemctl stop amazon-cloudwatch-agent"
echo "  Start:   sudo systemctl start amazon-cloudwatch-agent"
echo "  Restart: sudo systemctl restart amazon-cloudwatch-agent"
echo ""

echo "✅ CloudWatch Agent configurado!"
echo ""

