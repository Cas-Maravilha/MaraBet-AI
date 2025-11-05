#!/bin/bash
# Script de Teste Bash - MaraBet AI
# Execute no servidor Ubuntu

PUBLIC_IP="3.218.152.100"
BASE_URL="http://$PUBLIC_IP:8000"

echo "🧪 MARABET AI - TESTES DA APLICAÇÃO"
echo "=================================="
echo "📅 Data/Hora: $(date '+%d/%m/%Y %H:%M:%S')"
echo "🌐 URL Base: $BASE_URL"

# Teste 1: Health Check
echo ""
echo "🔍 TESTE 1: HEALTH CHECK"
echo "------------------------"
if curl -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ Health Check: OK"
    curl -s "$BASE_URL/health" | head -5
else
    echo "❌ Health Check: Falha"
fi

# Teste 2: Documentação Swagger
echo ""
echo "🔍 TESTE 2: DOCUMENTAÇÃO SWAGGER"
echo "--------------------------------"
if curl -f "$BASE_URL/docs" > /dev/null 2>&1; then
    echo "✅ Documentação Swagger: OK"
    echo "🌐 Acesse no navegador: $BASE_URL/docs"
else
    echo "❌ Documentação Swagger: Falha"
fi

# Teste 3: Predições
echo ""
echo "🔍 TESTE 3: PREDIÇÕES"
echo "--------------------"
if curl -f "$BASE_URL/predictions" > /dev/null 2>&1; then
    echo "✅ Predições: OK"
    curl -s "$BASE_URL/predictions" | head -5
else
    echo "❌ Predições: Falha"
fi

# Teste 4: Análise
echo ""
echo "🔍 TESTE 4: ANÁLISE"
echo "-------------------"
if curl -f "$BASE_URL/analysis" > /dev/null 2>&1; then
    echo "✅ Análise: OK"
    curl -s "$BASE_URL/analysis" | head -5
else
    echo "❌ Análise: Falha"
fi

# Teste 5: Configuração
echo ""
echo "🔍 TESTE 5: CONFIGURAÇÃO"
echo "------------------------"
if curl -f "$BASE_URL/config" > /dev/null 2>&1; then
    echo "✅ Configuração: OK"
    curl -s "$BASE_URL/config" | head -5
else
    echo "❌ Configuração: Falha"
fi

# Teste 6: Página Inicial
echo ""
echo "🔍 TESTE 6: PÁGINA INICIAL"
echo "--------------------------"
if curl -f "$BASE_URL/" > /dev/null 2>&1; then
    echo "✅ Página Inicial: OK"
    echo "🌐 Acesse no navegador: $BASE_URL"
else
    echo "❌ Página Inicial: Falha"
fi

echo ""
echo "🎉 TESTES CONCLUÍDOS!"
echo "====================="
echo "🌐 URLs para acessar no navegador:"
echo "  • Página Principal: $BASE_URL"
echo "  • Documentação: $BASE_URL/docs"
echo "  • Health Check: $BASE_URL/health"
echo "  • Predições: $BASE_URL/predictions"
echo "  • Análise: $BASE_URL/analysis"
echo "  • Configuração: $BASE_URL/config"
