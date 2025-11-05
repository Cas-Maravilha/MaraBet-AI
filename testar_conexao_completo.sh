#!/bin/bash

# =============================================
# Script: Teste Completo de Conexão PostgreSQL
# Executa todos os testes: rede, psql e Python
# =============================================

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     TESTE COMPLETO DE CONEXÃO POSTGRESQL REMOTA            ║"
echo "║     Servidor: 37.27.220.67:5432                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESULTS=()

# === TESTE 1: Conectividade de Rede ===
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 1: Conectividade de Rede"
echo "═══════════════════════════════════════════════════════════"
echo ""

if command -v ping > /dev/null 2>&1; then
    if ping -c 1 -W 2 37.27.220.67 > /dev/null 2>&1; then
        echo "✅ Ping: PASSOU"
        RESULTS+=("Ping: ✅")
    else
        echo "❌ Ping: FALHOU"
        RESULTS+=("Ping: ❌")
    fi
else
    echo "⚠️  ping não está disponível, pulando teste"
fi

if command -v nc > /dev/null 2>&1; then
    if nc -z -v -w 5 37.27.220.67 5432 2>&1 | grep -q "succeeded"; then
        echo "✅ Porta 5432: PASSOU"
        RESULTS+=("Porta 5432: ✅")
    else
        echo "❌ Porta 5432: FALHOU"
        RESULTS+=("Porta 5432: ❌")
    fi
else
    echo "⚠️  nc (netcat) não está instalado, pulando teste de porta"
fi

echo ""

# === TESTE 2: Teste via psql ===
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 2: Conexão via psql"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ -f "$SCRIPT_DIR/testar_conexao_remota.sh" ]; then
    if bash "$SCRIPT_DIR/testar_conexao_remota.sh"; then
        echo "✅ Teste psql: PASSOU"
        RESULTS+=("Teste psql: ✅")
    else
        echo "❌ Teste psql: FALHOU"
        RESULTS+=("Teste psql: ❌")
    fi
else
    echo "⚠️  Script testar_conexao_remota.sh não encontrado"
fi

echo ""

# === TESTE 3: Teste via Python ===
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 3: Conexão via Python (psycopg2)"
echo "═══════════════════════════════════════════════════════════"
echo ""

if command -v python3 > /dev/null 2>&1; then
    if python3 -c "import psycopg2" 2>/dev/null; then
        if [ -f "$SCRIPT_DIR/testar_conexao_remota.py" ]; then
            if python3 "$SCRIPT_DIR/testar_conexao_remota.py"; then
                echo "✅ Teste Python: PASSOU"
                RESULTS+=("Teste Python: ✅")
            else
                echo "❌ Teste Python: FALHOU"
                RESULTS+=("Teste Python: ❌")
            fi
        else
            echo "⚠️  Script testar_conexao_remota.py não encontrado"
        fi
    else
        echo "⚠️  psycopg2 não está instalado"
        echo "   Instale com: pip install psycopg2-binary"
    fi
else
    echo "⚠️  Python3 não está instalado"
fi

echo ""

# === RESUMO FINAL ===
echo "═══════════════════════════════════════════════════════════"
echo "RESUMO FINAL DOS TESTES"
echo "═══════════════════════════════════════════════════════════"
echo ""

for result in "${RESULTS[@]}"; do
    echo "   $result"
done

PASSED=$(echo "${RESULTS[@]}" | grep -o "✅" | wc -l)
TOTAL=${#RESULTS[@]}

echo ""
echo "📊 Resultado: $PASSED/$TOTAL testes passaram"
echo ""

if [ $PASSED -eq $TOTAL ] && [ $TOTAL -gt 0 ]; then
    echo "🎉 TODOS OS TESTES PASSARAM! Conexão funcionando perfeitamente!"
    exit 0
else
    echo "⚠️  Alguns testes falharam. Verifique as configurações."
    echo ""
    echo "💡 Execute no servidor remoto:"
    echo "   sudo bash verificar_configuracao_postgresql.sh"
    exit 1
fi

