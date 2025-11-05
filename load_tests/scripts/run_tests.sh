#!/bin/bash
# Script para Executar Testes de Carga - MaraBet AI
# Executa Locust, K6 e Artillery

set -e

echo "🧪 MARABET AI - TESTES DE CARGA"
echo "=========================================="
echo "📅 Data/Hora: $(date)"
echo ""

# Variáveis
BASE_URL="${1:-http://localhost:8000}"
REPORT_DIR="load_tests/reports"

# Criar diretório de relatórios
mkdir -p $REPORT_DIR

echo "🎯 URL Base: $BASE_URL"
echo ""

# Menu de seleção
echo "Selecione o teste a executar:"
echo "1) Locust (Python)"
echo "2) K6 (JavaScript)"
echo "3) Artillery (Node.js)"
echo "4) Todos os testes"
echo "5) Teste rápido (smoke test)"
read -p "Opção: " option

case $option in
    1)
        echo ""
        echo "🐝 EXECUTANDO LOCUST"
        echo "----------------------------------------"
        
        # Instalar Locust se necessário
        pip install locust --quiet
        
        # Executar Locust
        cd load_tests/locust
        locust -f locustfile.py \
            --host=$BASE_URL \
            --users=100 \
            --spawn-rate=10 \
            --run-time=5m \
            --html=../reports/locust_report.html \
            --csv=../reports/locust \
            --headless
        
        echo "✅ Teste Locust concluído!"
        echo "📊 Relatório: load_tests/reports/locust_report.html"
        ;;
    
    2)
        echo ""
        echo "📊 EXECUTANDO K6"
        echo "----------------------------------------"
        
        # Verificar se K6 está instalado
        if ! command -v k6 &> /dev/null; then
            echo "⚠️  K6 não instalado. Instalando..."
            # Para Ubuntu/Debian
            sudo gpg -k
            sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
            echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
            sudo apt-get update
            sudo apt-get install k6
        fi
        
        # Executar K6
        k6 run load_tests/k6/k6_test.js \
            --out json=load_tests/reports/k6_results.json \
            --summary-export=load_tests/reports/k6_summary.json
        
        echo "✅ Teste K6 concluído!"
        echo "📊 Relatório: load_tests/reports/k6_summary.json"
        ;;
    
    3)
        echo ""
        echo "🎯 EXECUTANDO ARTILLERY"
        echo "----------------------------------------"
        
        # Instalar Artillery se necessário
        if ! command -v artillery &> /dev/null; then
            echo "⚠️  Artillery não instalado. Instalando..."
            npm install -g artillery
        fi
        
        # Executar Artillery
        artillery run load_tests/artillery/artillery.yml \
            --output load_tests/reports/artillery_report.json
        
        # Gerar relatório HTML
        artillery report load_tests/reports/artillery_report.json \
            --output load_tests/reports/artillery_report.html
        
        echo "✅ Teste Artillery concluído!"
        echo "📊 Relatório: load_tests/reports/artillery_report.html"
        ;;
    
    4)
        echo ""
        echo "🚀 EXECUTANDO TODOS OS TESTES"
        echo "=========================================="
        
        # Locust
        echo ""
        echo "1/3: LOCUST"
        pip install locust --quiet
        cd load_tests/locust
        locust -f locustfile.py --host=$BASE_URL --users=50 --spawn-rate=5 --run-time=3m --html=../reports/locust_report.html --headless
        cd ../..
        
        # K6
        echo ""
        echo "2/3: K6"
        k6 run load_tests/k6/k6_test.js --out json=load_tests/reports/k6_results.json
        
        # Artillery
        echo ""
        echo "3/3: ARTILLERY"
        artillery run load_tests/artillery/artillery.yml --output load_tests/reports/artillery_report.json
        artillery report load_tests/reports/artillery_report.json --output load_tests/reports/artillery_report.html
        
        echo ""
        echo "✅ Todos os testes concluídos!"
        echo "📊 Relatórios em: load_tests/reports/"
        ;;
    
    5)
        echo ""
        echo "💨 EXECUTANDO SMOKE TEST"
        echo "----------------------------------------"
        
        # Teste rápido com Locust
        pip install locust --quiet
        cd load_tests/locust
        locust -f locustfile.py --host=$BASE_URL --users=10 --spawn-rate=2 --run-time=1m --headless
        
        echo "✅ Smoke test concluído!"
        ;;
    
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo "🎉 TESTES FINALIZADOS!"
echo "=========================================="
echo "📊 Relatórios disponíveis em: load_tests/reports/"
echo "📞 Suporte: +224 932027393"
