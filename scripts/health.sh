#!/bin/bash
# Script de verificação de saúde para MaraBet AI

set -e

echo "🏥 MARABET AI - HEALTH CHECK"
echo "============================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Função para erro
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para sucesso
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Função para warning
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se Docker está rodando
check_docker() {
    log "Verificando Docker..."
    
    if ! docker info &> /dev/null; then
        error "Docker não está rodando"
        return 1
    fi
    
    success "Docker está rodando"
    return 0
}

# Verificar containers
check_containers() {
    log "Verificando containers..."
    
    local all_up=true
    
    # Lista de containers esperados
    local expected_containers=("marabet-ai-app" "marabet-ai-redis" "marabet-ai-nginx")
    
    for container in "${expected_containers[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            local status=$(docker ps --format "{{.Status}}" --filter "name=${container}")
            if [[ $status == *"Up"* ]]; then
                success "$container: $status"
            else
                error "$container: $status"
                all_up=false
            fi
        else
            error "$container: Não encontrado"
            all_up=false
        fi
    done
    
    if [ "$all_up" = true ]; then
        success "Todos os containers estão rodando"
        return 0
    else
        error "Alguns containers não estão rodando"
        return 1
    fi
}

# Verificar saúde dos serviços
check_services() {
    log "Verificando saúde dos serviços..."
    
    local all_healthy=true
    
    # API
    if curl -f -s --max-time 10 http://localhost:5000/health &> /dev/null; then
        success "API: OK"
    else
        error "API: FALHOU"
        all_healthy=false
    fi
    
    # Dashboard
    if curl -f -s --max-time 10 http://localhost:8000/health &> /dev/null; then
        success "Dashboard: OK"
    else
        error "Dashboard: FALHOU"
        all_healthy=false
    fi
    
    # Redis
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        success "Redis: OK"
    else
        error "Redis: FALHOU"
        all_healthy=false
    fi
    
    if [ "$all_healthy" = true ]; then
        success "Todos os serviços estão saudáveis"
        return 0
    else
        error "Alguns serviços não estão saudáveis"
        return 1
    fi
}

# Verificar conectividade externa
check_external_connectivity() {
    log "Verificando conectividade externa..."
    
    local all_connected=true
    
    # API-Football
    if curl -f -s --max-time 10 "https://v3.football.api-sports.io/status" &> /dev/null; then
        success "API-Football: Conectado"
    else
        error "API-Football: Sem conexão"
        all_connected=false
    fi
    
    # Telegram
    if curl -f -s --max-time 10 "https://api.telegram.org" &> /dev/null; then
        success "Telegram API: Conectado"
    else
        error "Telegram API: Sem conexão"
        all_connected=false
    fi
    
    # Internet geral
    if ping -c 1 8.8.8.8 &> /dev/null; then
        success "Internet: Conectado"
    else
        error "Internet: Sem conexão"
        all_connected=false
    fi
    
    if [ "$all_connected" = true ]; then
        success "Conectividade externa OK"
        return 0
    else
        error "Problemas de conectividade externa"
        return 1
    fi
}

# Verificar recursos do sistema
check_system_resources() {
    log "Verificando recursos do sistema..."
    
    # CPU
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_usage < 80" | bc -l) )); then
        success "CPU: ${cpu_usage}% (OK)"
    else
        warning "CPU: ${cpu_usage}% (Alto)"
    fi
    
    # Memória
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$mem_usage < 80" | bc -l) )); then
        success "Memória: ${mem_usage}% (OK)"
    else
        warning "Memória: ${mem_usage}% (Alto)"
    fi
    
    # Espaço em disco
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ "$disk_usage" -lt 80 ]; then
        success "Disco: ${disk_usage}% (OK)"
    else
        warning "Disco: ${disk_usage}% (Alto)"
    fi
}

# Verificar logs de erro
check_error_logs() {
    log "Verificando logs de erro..."
    
    local error_count=0
    
    # Verificar logs dos containers
    if docker-compose logs --tail=100 2>&1 | grep -i error | wc -l | grep -q "[1-9]"; then
        error_count=$((error_count + $(docker-compose logs --tail=100 2>&1 | grep -i error | wc -l)))
    fi
    
    # Verificar logs de arquivo
    if [ -d "logs" ]; then
        local file_errors=$(find logs -name "*.log" -exec grep -l -i error {} \; 2>/dev/null | wc -l)
        error_count=$((error_count + file_errors))
    fi
    
    if [ "$error_count" -eq 0 ]; then
        success "Nenhum erro encontrado nos logs"
    else
        warning "Encontrados $error_count erros nos logs"
    fi
}

# Verificar banco de dados
check_database() {
    log "Verificando banco de dados..."
    
    if [ -f "data/sports_data.db" ]; then
        local db_size=$(du -h data/sports_data.db | cut -f1)
        success "Banco de dados: $db_size"
        
        # Verificar se o banco está acessível
        if command -v sqlite3 &> /dev/null; then
            if sqlite3 data/sports_data.db "SELECT 1;" &> /dev/null; then
                success "Banco de dados: Acessível"
            else
                error "Banco de dados: Inacessível"
            fi
        fi
    else
        error "Banco de dados não encontrado"
    fi
}

# Verificar configuração
check_configuration() {
    log "Verificando configuração..."
    
    # Verificar arquivo .env
    if [ -f ".env" ]; then
        success "Arquivo .env: Encontrado"
        
        # Verificar se as chaves estão configuradas
        if grep -q "your_api_football_key_here" .env; then
            warning "Chaves de API não configuradas"
        else
            success "Chaves de API: Configuradas"
        fi
    else
        error "Arquivo .env não encontrado"
    fi
    
    # Verificar docker-compose.yml
    if [ -f "docker-compose.yml" ]; then
        success "Docker Compose: Encontrado"
    else
        error "Docker Compose não encontrado"
    fi
}

# Verificar performance
check_performance() {
    log "Verificando performance..."
    
    # Tempo de resposta da API
    local api_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/health 2>/dev/null || echo "0")
    if (( $(echo "$api_time < 1.0" | bc -l) )); then
        success "API Response Time: ${api_time}s (OK)"
    else
        warning "API Response Time: ${api_time}s (Lento)"
    fi
    
    # Tempo de resposta do Dashboard
    local dashboard_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health 2>/dev/null || echo "0")
    if (( $(echo "$dashboard_time < 1.0" | bc -l) )); then
        success "Dashboard Response Time: ${dashboard_time}s (OK)"
    else
        warning "Dashboard Response Time: ${dashboard_time}s (Lento)"
    fi
}

# Gerar relatório de saúde
generate_health_report() {
    log "Gerando relatório de saúde..."
    
    local report_file="health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "MaraBet AI - Relatório de Saúde"
        echo "==============================="
        echo "Data/Hora: $(date)"
        echo "Sistema: $(uname -s) $(uname -m)"
        echo
        
        echo "=== Status dos Containers ==="
        docker-compose ps
        echo
        
        echo "=== Uso de Recursos ==="
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        echo
        
        echo "=== Espaço em Disco ==="
        df -h | grep -E "(Filesystem|/dev/)"
        echo
        
        echo "=== Logs de Erro (últimos 50) ==="
        docker-compose logs --tail=50 | grep -i error || echo "Nenhum erro encontrado"
        echo
        
        echo "=== Conectividade Externa ==="
        echo "API-Football: $(curl -f -s --max-time 5 "https://v3.football.api-sports.io/status" &> /dev/null && echo "OK" || echo "FALHOU")"
        echo "Telegram: $(curl -f -s --max-time 5 "https://api.telegram.org" &> /dev/null && echo "OK" || echo "FALHOU")"
        echo "Internet: $(ping -c 1 8.8.8.8 &> /dev/null && echo "OK" || echo "FALHOU")"
        
    } > "$report_file"
    
    success "Relatório salvo em: $report_file"
}

# Função principal
main() {
    local overall_status=0
    
    log "Iniciando verificação de saúde completa..."
    echo
    
    # Executar todas as verificações
    check_docker || overall_status=1
    check_containers || overall_status=1
    check_services || overall_status=1
    check_external_connectivity || overall_status=1
    check_system_resources
    check_error_logs
    check_database
    check_configuration
    check_performance
    
    echo
    echo "==============================="
    
    if [ $overall_status -eq 0 ]; then
        success "SISTEMA SAUDÁVEL - Todas as verificações críticas passaram"
    else
        error "SISTEMA COM PROBLEMAS - Algumas verificações críticas falharam"
    fi
    
    # Gerar relatório
    generate_health_report
    
    exit $overall_status
}

# Executar verificação
main "$@"
