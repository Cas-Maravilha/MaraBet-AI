#!/bin/bash

# =============================================
# Script: Teste de Conexão PostgreSQL Remota
# Testa conexão ao servidor remoto via psql
# =============================================

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     TESTE DE CONEXÃO POSTGRESQL REMOTA                    ║"
echo "║     Servidor: 37.27.220.67:5432                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Configurações
HOST="37.27.220.67"
PORT="5432"
DATABASE="marabet"
USER="meu_root\$marabet"
PASSWORD="dudbeeGdNBSxjpEWlop"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}💡 $1${NC}"
}

# === TESTE 1: Conectividade de Rede ===
print_header "TESTE 1: Conectividade de Rede"

echo "🔄 Testando ping ao servidor..."
if ping -c 1 -W 2 "$HOST" > /dev/null 2>&1; then
    PING_TIME=$(ping -c 1 "$HOST" | grep "time=" | awk -F'time=' '{print $2}' | awk '{print $1}')
    print_success "Servidor está online (Latência: ${PING_TIME}ms)"
else
    print_error "Servidor não está respondendo ao ping"
    echo ""
    print_info "Verifique se o IP 37.27.220.67 está correto"
    exit 1
fi

echo ""
echo "🔄 Testando conectividade na porta $PORT..."
if command -v nc > /dev/null 2>&1; then
    if nc -z -v -w 5 "$HOST" "$PORT" 2>&1 | grep -q "succeeded"; then
        print_success "Porta $PORT está acessível"
    else
        print_error "Porta $PORT não está acessível"
        echo ""
        print_info "Possíveis causas:"
        echo "   1. Firewall bloqueando a porta"
        echo "   2. PostgreSQL não está em execução"
        echo "   3. PostgreSQL não está escutando externamente"
    fi
else
    print_info "nc (netcat) não está instalado, pulando teste de porta"
fi

# === TESTE 2: Conexão PostgreSQL ===
print_header "TESTE 2: Conexão PostgreSQL"

echo "📋 Configurações de conexão:"
echo "   Host: $HOST"
echo "   Porta: $PORT"
echo "   Database: $DATABASE"
echo "   User: $USER"
echo ""

# Verificar se psql está instalado
if ! command -v psql > /dev/null 2>&1; then
    print_error "psql não está instalado"
    print_info "Instale com: sudo apt install postgresql-client"
    exit 1
fi

# Teste de conexão
echo "🔄 Tentando conectar ao PostgreSQL..."
export PGPASSWORD="$PASSWORD"

if psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -c "\conninfo" > /dev/null 2>&1; then
    print_success "Conexão estabelecida com sucesso!"
    echo ""
    
    # Obter informações da conexão
    echo "📊 Informações da conexão:"
    psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -c "
        SELECT 
            'PostgreSQL: ' || version() as info
        UNION ALL
        SELECT 'Database: ' || current_database()
        UNION ALL
        SELECT 'User: ' || current_user
        UNION ALL
        SELECT 'Data/Hora Servidor: ' || now()::text;
    " 2>/dev/null
    
    # Teste de query simples
    echo ""
    echo "🧪 Testando query simples..."
    if psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -c "SELECT 1 as teste;" > /dev/null 2>&1; then
        print_success "Query executada com sucesso!"
    else
        print_error "Falha ao executar query"
    fi
    
    CONNECTION_SUCCESS=true
else
    ERROR_OUTPUT=$(psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -c "\conninfo" 2>&1)
    print_error "Falha na conexão"
    echo ""
    echo "Detalhes do erro:"
    echo "$ERROR_OUTPUT" | grep -i "error\|fatal\|connection" | head -5
    
    echo ""
    print_info "Verificações necessárias:"
    echo "   1. PostgreSQL está em execução no servidor remoto?"
    echo "   2. postgresql.conf tem listen_addresses = '*'?"
    echo "   3. pg_hba.conf permite conexões remotas?"
    echo "   4. Firewall permite conexões na porta 5432?"
    echo "   5. Credenciais estão corretas?"
    
    CONNECTION_SUCCESS=false
fi

unset PGPASSWORD

# === TESTE 3: Performance ===
if [ "$CONNECTION_SUCCESS" = true ]; then
    print_header "TESTE 3: Performance da Conexão"
    
    echo "⏱️  Medindo tempo de conexão..."
    export PGPASSWORD="$PASSWORD
    
    START_TIME=$(date +%s%N)
    psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DATABASE" -c "SELECT 1;" > /dev/null 2>&1
    END_TIME=$(date +%s%N)
    
    CONNECTION_TIME_MS=$(( (END_TIME - START_TIME) / 1000000 ))
    
    if [ $CONNECTION_TIME_MS -lt 100 ]; then
        print_success "Tempo de conexão: ${CONNECTION_TIME_MS}ms (EXCELENTE)"
    elif [ $CONNECTION_TIME_MS -lt 500 ]; then
        print_info "Tempo de conexão: ${CONNECTION_TIME_MS}ms (BOM)"
    elif [ $CONNECTION_TIME_MS -lt 2000 ]; then
        print_info "Tempo de conexão: ${CONNECTION_TIME_MS}ms (ACEITÁVEL)"
    else
        print_error "Tempo de conexão: ${CONNECTION_TIME_MS}ms (ALTO)"
    fi
    
    unset PGPASSWORD
fi

# === RESUMO FINAL ===
print_header "RESUMO DOS TESTES"

if [ "$CONNECTION_SUCCESS" = true ]; then
    print_success "✅ Conexão PostgreSQL: FUNCIONANDO"
    print_success "✅ Operações no banco: FUNCIONANDO"
    echo ""
    print_success "🎉 TODOS OS TESTES PASSARAM! Conexão funcionando perfeitamente!"
    echo ""
    echo "📋 Dados de conexão confirmados:"
    echo "   Host: $HOST"
    echo "   Porta: $PORT"
    echo "   Database: $DATABASE"
    echo "   User: $USER"
    echo ""
    exit 0
else
    print_error "❌ Conexão PostgreSQL: FALHOU"
    echo ""
    print_info "Execute no servidor remoto:"
    echo "   sudo bash verificar_configuracao_postgresql.sh"
    echo ""
    exit 1
fi

