#!/bin/bash
# Setup Grafana + Prometheus - MaraBet AI

set -e

echo "📈 MARABET AI - SETUP MONITORAMENTO"
echo "=========================================="
echo "📅 Data/Hora: $(date)"
echo ""

# 1. Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p monitoring/prometheus/alerts
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning
mkdir -p monitoring/alertmanager

# 2. Definir permissões
echo "🔐 Configurando permissões..."
chmod -R 755 monitoring/
chmod 644 monitoring/prometheus/prometheus.yml
chmod 644 monitoring/grafana/grafana.ini

# 3. Iniciar serviços
echo "🚀 Iniciando serviços de monitoramento..."
docker-compose -f docker-compose.monitoring.yml up -d

# 4. Aguardar inicialização
echo "⏰ Aguardando inicialização..."
sleep 10

# 5. Verificar serviços
echo "🔍 Verificando serviços..."
echo ""

# Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus: OK (http://localhost:9090)"
else
    echo "❌ Prometheus: ERRO"
fi

# Grafana
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana: OK (http://localhost:3000)"
    echo "   Login: admin / marabet123"
else
    echo "❌ Grafana: ERRO"
fi

# Alertmanager
if curl -s http://localhost:9093/-/healthy > /dev/null; then
    echo "✅ Alertmanager: OK (http://localhost:9093)"
else
    echo "❌ Alertmanager: ERRO"
fi

# Node Exporter
if curl -s http://localhost:9100/metrics > /dev/null; then
    echo "✅ Node Exporter: OK (http://localhost:9100)"
else
    echo "❌ Node Exporter: ERRO"
fi

echo ""
echo "🎉 SETUP CONCLUÍDO!"
echo "=========================================="
echo "📊 Acessos:"
echo "   • Grafana: http://localhost:3000 (admin/marabet123)"
echo "   • Prometheus: http://localhost:9090"
echo "   • Alertmanager: http://localhost:9093"
echo ""
echo "📞 Suporte: +224 932027393"
