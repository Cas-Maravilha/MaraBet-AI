#!/bin/bash
# Script para deploy do MaraBet AI

set -e

echo "🚀 MARABET AI - DEPLOY"
echo "======================"

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
    exit 1
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
if ! docker info &> /dev/null; then
    error "Docker não está rodando. Inicie o Docker primeiro."
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    error "Arquivo .env não encontrado. Configure suas chaves primeiro."
fi

# Verificar se as chaves estão configuradas
if grep -q "your_api_football_key_here" .env; then
    warning "Chaves não configuradas no .env. Configure suas chaves primeiro."
    exit 1
fi

# Função para parar serviços existentes
stop_services() {
    log "Parando serviços existentes..."
    docker-compose down --remove-orphans || true
    success "Serviços parados"
}

# Função para limpar containers antigos
cleanup() {
    log "Limpando containers antigos..."
    docker-compose down --remove-orphans || true
    docker system prune -f || true
    success "Limpeza concluída"
}

# Função para verificar saúde dos serviços
health_check() {
    log "Verificando saúde dos serviços..."
    
    # Aguardar serviços iniciarem
    sleep 30
    
    # Verificar API
    if curl -f http://localhost:5000/health &> /dev/null; then
        success "API está funcionando"
    else
        warning "API não está respondendo"
    fi
    
    # Verificar Dashboard
    if curl -f http://localhost:8000/health &> /dev/null; then
        success "Dashboard está funcionando"
    else
        warning "Dashboard não está respondendo"
    fi
    
    # Verificar Redis
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        success "Redis está funcionando"
    else
        warning "Redis não está respondendo"
    fi
}

# Função para mostrar logs
show_logs() {
    log "Mostrando logs dos serviços..."
    docker-compose logs --tail=50 -f
}

# Função para backup
backup() {
    log "Criando backup dos dados..."
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup do banco de dados
    if [ -f "data/sports_data.db" ]; then
        cp data/sports_data.db "$BACKUP_DIR/"
        success "Backup do banco de dados criado"
    fi
    
    # Backup dos logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/"
        success "Backup dos logs criado"
    fi
    
    success "Backup criado em: $BACKUP_DIR"
}

# Função para restore
restore() {
    if [ -z "$1" ]; then
        error "Especifique o diretório de backup para restore"
    fi
    
    BACKUP_DIR="$1"
    if [ ! -d "$BACKUP_DIR" ]; then
        error "Diretório de backup não encontrado: $BACKUP_DIR"
    fi
    
    log "Restaurando backup de: $BACKUP_DIR"
    
    # Restore do banco de dados
    if [ -f "$BACKUP_DIR/sports_data.db" ]; then
        cp "$BACKUP_DIR/sports_data.db" data/
        success "Banco de dados restaurado"
    fi
    
    # Restore dos logs
    if [ -d "$BACKUP_DIR/logs" ]; then
        cp -r "$BACKUP_DIR/logs" .
        success "Logs restaurados"
    fi
}

# Função para monitoramento
monitor() {
    log "Iniciando monitoramento dos serviços..."
    
    while true; do
        echo "=== Status dos Serviços - $(date) ==="
        
        # Status dos containers
        docker-compose ps
        
        # Uso de recursos
        echo
        echo "=== Uso de Recursos ==="
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
        
        # Espaço em disco
        echo
        echo "=== Espaço em Disco ==="
        df -h | grep -E "(Filesystem|/dev/)"
        
        sleep 60
    done
}

# Função principal de deploy
deploy() {
    log "Iniciando deploy do MaraBet AI..."
    
    # Parar serviços existentes
    stop_services
    
    # Limpar containers antigos
    cleanup
    
    # Criar diretórios necessários
    log "Criando diretórios necessários..."
    mkdir -p data logs reports nginx/ssl
    
    # Build das imagens
    log "Fazendo build das imagens..."
    docker-compose build --no-cache
    
    # Iniciar serviços
    log "Iniciando serviços..."
    docker-compose up -d
    
    # Aguardar serviços iniciarem
    log "Aguardando serviços iniciarem..."
    sleep 30
    
    # Verificar saúde dos serviços
    health_check
    
    # Mostrar status
    log "Status dos serviços:"
    docker-compose ps
    
    success "Deploy concluído com sucesso!"
    
    echo
    log "Serviços disponíveis:"
    echo "- Dashboard: http://localhost:8000"
    echo "- API: http://localhost:5000"
    echo "- Nginx: http://localhost:80"
    echo
    log "Comandos úteis:"
    echo "- Ver logs: docker-compose logs -f"
    echo "- Parar: docker-compose down"
    echo "- Restart: docker-compose restart"
    echo "- Monitor: $0 monitor"
}

# Menu principal
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        deploy
        ;;
    "logs")
        show_logs
        ;;
    "health")
        health_check
        ;;
    "backup")
        backup
        ;;
    "restore")
        restore "$2"
        ;;
    "monitor")
        monitor
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Uso: $0 {deploy|stop|restart|logs|health|backup|restore|monitor|cleanup}"
        echo
        echo "Comandos:"
        echo "  deploy   - Deploy completo do sistema"
        echo "  stop     - Parar todos os serviços"
        echo "  restart  - Reiniciar todos os serviços"
        echo "  logs     - Mostrar logs dos serviços"
        echo "  health   - Verificar saúde dos serviços"
        echo "  backup   - Criar backup dos dados"
        echo "  restore  - Restaurar backup (especifique o diretório)"
        echo "  monitor  - Monitorar serviços em tempo real"
        echo "  cleanup  - Limpar containers e imagens antigas"
        exit 1
        ;;
esac
