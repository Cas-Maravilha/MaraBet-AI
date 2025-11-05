#!/bin/bash
# Script de início rápido para MaraBet AI

set -e

echo "🚀 MARABET AI - INÍCIO RÁPIDO"
echo "============================="

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

# Verificar se Docker está instalado
check_docker() {
    log "Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado. Execute: ./scripts/setup.sh"
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker não está rodando. Inicie o Docker primeiro."
    fi
    
    success "Docker está funcionando"
}

# Verificar se Docker Compose está instalado
check_docker_compose() {
    log "Verificando Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado. Execute: ./scripts/setup.sh"
    fi
    
    success "Docker Compose está funcionando"
}

# Verificar arquivo .env
check_env() {
    log "Verificando configuração..."
    
    if [ ! -f .env ]; then
        warning "Arquivo .env não encontrado. Criando..."
        cat > .env << EOF
# Configurações do MaraBet AI
API_FOOTBALL_KEY=747d6e19a2d3a435fdb7a419007a45fa
THE_ODDS_API_KEY=your_the_odds_api_key_here
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br
DATABASE_URL=sqlite:///data/sports_data.db
REDIS_URL=redis://redis:6379
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
HOST=0.0.0.0
PORT=5000
EOF
        success "Arquivo .env criado com suas chaves"
    else
        success "Arquivo .env encontrado"
    fi
}

# Criar diretórios necessários
create_directories() {
    log "Criando diretórios necessários..."
    
    mkdir -p data logs reports nginx/ssl scripts backups
    
    success "Diretórios criados"
}

# Deploy do sistema
deploy_system() {
    log "Iniciando deploy do sistema..."
    
    # Parar serviços existentes
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Build das imagens
    log "Fazendo build das imagens..."
    docker-compose build --no-cache
    
    # Iniciar serviços
    log "Iniciando serviços..."
    docker-compose up -d
    
    # Aguardar serviços iniciarem
    log "Aguardando serviços iniciarem..."
    sleep 30
    
    success "Sistema iniciado"
}

# Verificar saúde dos serviços
check_health() {
    log "Verificando saúde dos serviços..."
    
    # Aguardar um pouco mais
    sleep 10
    
    # Verificar containers
    local all_up=true
    while IFS= read -r line; do
        if [[ $line == *"marabet-ai"* ]]; then
            container_name=$(echo $line | awk '{print $1}')
            status=$(echo $line | awk '{print $4}')
            
            if [[ $status == *"Up"* ]]; then
                success "$container_name: $status"
            else
                error "$container_name: $status"
                all_up=false
            fi
        fi
    done < <(docker-compose ps)
    
    if [ "$all_up" = true ]; then
        success "Todos os containers estão rodando"
    else
        error "Alguns containers não estão rodando"
    fi
}

# Testar endpoints
test_endpoints() {
    log "Testando endpoints..."
    
    # Aguardar serviços estarem prontos
    sleep 20
    
    # Testar API
    if curl -f -s --max-time 10 http://localhost:5000/health &> /dev/null; then
        success "API: OK"
    else
        warning "API: Não respondeu (pode estar inicializando)"
    fi
    
    # Testar Dashboard
    if curl -f -s --max-time 10 http://localhost:8000/health &> /dev/null; then
        success "Dashboard: OK"
    else
        warning "Dashboard: Não respondeu (pode estar inicializando)"
    fi
    
    # Testar Redis
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        success "Redis: OK"
    else
        warning "Redis: Não respondeu (pode estar inicializando)"
    fi
}

# Mostrar informações do sistema
show_info() {
    echo
    success "Sistema MaraBet AI iniciado com sucesso!"
    echo
    log "Informações do sistema:"
    echo "======================"
    echo "Dashboard: http://localhost:8000"
    echo "API: http://localhost:5000"
    echo "Nginx: http://localhost:80"
    echo
    log "Status dos containers:"
    docker-compose ps
    echo
    log "Comandos úteis:"
    echo "- Ver logs: docker-compose logs -f"
    echo "- Parar: docker-compose down"
    echo "- Restart: docker-compose restart"
    echo "- Status: docker-compose ps"
    echo "- Monitor: ./scripts/monitor.sh"
    echo
    log "Próximos passos:"
    echo "1. Acesse o dashboard: http://localhost:8000"
    echo "2. Configure notificações (opcional)"
    echo "3. Monitore o sistema: ./scripts/monitor.sh"
    echo
    success "Sistema pronto para uso!"
}

# Função principal
main() {
    log "Iniciando configuração rápida do MaraBet AI..."
    
    # Verificações básicas
    check_docker
    check_docker_compose
    check_env
    create_directories
    
    # Deploy
    deploy_system
    
    # Verificações pós-deploy
    check_health
    test_endpoints
    
    # Mostrar informações
    show_info
}

# Executar
main "$@"
