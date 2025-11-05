#!/bin/bash
# Script de monitoramento para MaraBet AI

set -e

echo "📊 MARABET AI - MONITORAMENTO"
echo "============================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Função para status
status() {
    echo -e "${CYAN}[STATUS]${NC} $1"
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

# Verificar status dos containers
check_containers() {
    log "Verificando status dos containers..."
    
    if ! docker-compose ps | grep -q "Up"; then
        error "Nenhum container está rodando"
        return 1
    fi
    
    # Status de cada container
    while IFS= read -r line; do
        if [[ $line == *"marabet-ai"* ]]; then
            container_name=$(echo $line | awk '{print $1}')
            status=$(echo $line | awk '{print $4}')
            
            if [[ $status == "Up" ]]; then
                success "$container_name: $status"
            else
                error "$container_name: $status"
            fi
        fi
    done < <(docker-compose ps)
}

# Verificar saúde dos serviços
check_health() {
    log "Verificando saúde dos serviços..."
    
    # API
    if curl -f http://localhost:5000/health &> /dev/null; then
        success "API: OK"
    else
        error "API: FALHOU"
    fi
    
    # Dashboard
    if curl -f http://localhost:8000/health &> /dev/null; then
        success "Dashboard: OK"
    else
        error "Dashboard: FALHOU"
    fi
    
    # Redis
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        success "Redis: OK"
    else
        error "Redis: FALHOU"
    fi
}

# Mostrar uso de recursos
show_resources() {
    log "Uso de recursos dos containers..."
    
    echo
    echo "=== CPU e Memória ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    
    echo
    echo "=== Rede e I/O ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Mostrar logs de erro
show_error_logs() {
    log "Verificando logs de erro..."
    
    # Logs dos últimos 10 minutos
    since_time=$(date -d '10 minutes ago' '+%Y-%m-%dT%H:%M:%S' 2>/dev/null || date -v-10M '+%Y-%m-%dT%H:%M:%S' 2>/dev/null || echo "10m")
    
    echo
    echo "=== Logs de Erro (últimos 10 minutos) ==="
    docker-compose logs --since="$since_time" | grep -i error | tail -20 || echo "Nenhum erro encontrado"
    
    echo
    echo "=== Logs de Warning ==="
    docker-compose logs --since="$since_time" | grep -i warning | tail -10 || echo "Nenhum warning encontrado"
}

# Verificar espaço em disco
check_disk_space() {
    log "Verificando espaço em disco..."
    
    echo
    echo "=== Espaço em Disco ==="
    df -h | grep -E "(Filesystem|/dev/)" | head -5
    
    echo
    echo "=== Uso do Docker ==="
    docker system df
}

# Verificar conectividade de rede
check_network() {
    log "Verificando conectividade de rede..."
    
    # Testar APIs externas
    echo
    echo "=== Conectividade Externa ==="
    
    # API-Football
    if curl -f -s --max-time 10 "https://v3.football.api-sports.io/status" &> /dev/null; then
        success "API-Football: Conectado"
    else
        error "API-Football: Sem conexão"
    fi
    
    # Telegram
    if curl -f -s --max-time 10 "https://api.telegram.org" &> /dev/null; then
        success "Telegram API: Conectado"
    else
        error "Telegram API: Sem conexão"
    fi
}

# Mostrar estatísticas do banco de dados
show_database_stats() {
    log "Estatísticas do banco de dados..."
    
    if [ -f "data/sports_data.db" ]; then
        echo
        echo "=== Banco de Dados ==="
        echo "Tamanho: $(du -h data/sports_data.db | cut -f1)"
        echo "Última modificação: $(stat -c %y data/sports_data.db 2>/dev/null || stat -f %Sm data/sports_data.db 2>/dev/null || echo 'N/A')"
        
        # Contar registros (se possível)
        if command -v sqlite3 &> /dev/null; then
            echo
            echo "=== Contagem de Registros ==="
            sqlite3 data/sports_data.db "SELECT 'Partidas:', COUNT(*) FROM matches;" 2>/dev/null || echo "Erro ao acessar banco"
            sqlite3 data/sports_data.db "SELECT 'Odds:', COUNT(*) FROM odds;" 2>/dev/null || echo "Erro ao acessar banco"
            sqlite3 data/sports_data.db "SELECT 'Predições:', COUNT(*) FROM predictions;" 2>/dev/null || echo "Erro ao acessar banco"
        fi
    else
        warning "Banco de dados não encontrado"
    fi
}

# Mostrar estatísticas de logs
show_log_stats() {
    log "Estatísticas de logs..."
    
    if [ -d "logs" ]; then
        echo
        echo "=== Arquivos de Log ==="
        ls -lah logs/ | head -10
        
        echo
        echo "=== Tamanho dos Logs ==="
        du -sh logs/
        
        echo
        echo "=== Logs Mais Recentes ==="
        find logs/ -name "*.log" -type f -exec ls -t {} + | head -5 | xargs ls -lah
    else
        warning "Diretório de logs não encontrado"
    fi
}

# Monitoramento em tempo real
monitor_realtime() {
    log "Iniciando monitoramento em tempo real..."
    log "Pressione Ctrl+C para parar"
    
    while true; do
        clear
        echo "📊 MARABET AI - MONITORAMENTO EM TEMPO REAL"
        echo "============================================="
        echo "Atualizado: $(date)"
        echo
        
        # Status dos containers
        echo "=== Status dos Containers ==="
        docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
        echo
        
        # Uso de recursos
        echo "=== Uso de Recursos ==="
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        echo
        
        # Espaço em disco
        echo "=== Espaço em Disco ==="
        df -h | grep -E "(Filesystem|/dev/)" | head -3
        echo
        
        # Logs recentes
        echo "=== Logs Recentes ==="
        docker-compose logs --tail=5 --timestamps | tail -10
        
        sleep 5
    done
}

# Backup automático
backup_auto() {
    log "Executando backup automático..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup do banco de dados
    if [ -f "data/sports_data.db" ]; then
        cp data/sports_data.db "$BACKUP_DIR/"
        success "Backup do banco criado"
    fi
    
    # Backup dos logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/"
        success "Backup dos logs criado"
    fi
    
    # Backup da configuração
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/"
        success "Backup da configuração criado"
    fi
    
    # Comprimir backup
    tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .
    rm -rf "$BACKUP_DIR"
    
    success "Backup criado: $BACKUP_DIR.tar.gz"
}

# Limpeza automática
cleanup_auto() {
    log "Executando limpeza automática..."
    
    # Limpar logs antigos (mais de 7 dias)
    find logs/ -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Limpar backups antigos (mais de 30 dias)
    find backups/ -name "*.tar.gz" -type f -mtime +30 -delete 2>/dev/null || true
    
    # Limpar containers parados
    docker container prune -f
    
    # Limpar imagens não utilizadas
    docker image prune -f
    
    success "Limpeza concluída"
}

# Função principal
main() {
    case "${1:-status}" in
        "status")
            check_containers
            check_health
            ;;
        "resources")
            show_resources
            ;;
        "logs")
            show_error_logs
            ;;
        "disk")
            check_disk_space
            ;;
        "network")
            check_network
            ;;
        "database")
            show_database_stats
            ;;
        "logstats")
            show_log_stats
            ;;
        "realtime")
            monitor_realtime
            ;;
        "backup")
            backup_auto
            ;;
        "cleanup")
            cleanup_auto
            ;;
        "full")
            check_containers
            check_health
            show_resources
            check_disk_space
            check_network
            show_database_stats
            show_log_stats
            ;;
        *)
            echo "Uso: $0 {status|resources|logs|disk|network|database|logstats|realtime|backup|cleanup|full}"
            echo
            echo "Comandos:"
            echo "  status     - Verificar status dos containers e saúde"
            echo "  resources  - Mostrar uso de recursos"
            echo "  logs       - Mostrar logs de erro"
            echo "  disk       - Verificar espaço em disco"
            echo "  network    - Verificar conectividade de rede"
            echo "  database   - Mostrar estatísticas do banco"
            echo "  logstats   - Mostrar estatísticas de logs"
            echo "  realtime   - Monitoramento em tempo real"
            echo "  backup     - Backup automático"
            echo "  cleanup    - Limpeza automática"
            echo "  full       - Verificação completa"
            exit 1
            ;;
    esac
}

# Executar comando
main "$@"
