#!/bin/bash

# Script de Deploy com PostgreSQL - MaraBet AI
# Configura e inicia o sistema com PostgreSQL em produção

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Docker está instalado
check_docker() {
    log "Verificando Docker..."
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado. Instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
        exit 1
    fi
    
    success "Docker e Docker Compose estão instalados"
}

# Verificar se arquivo .env existe
check_env_file() {
    log "Verificando arquivo .env..."
    if [ ! -f ".env" ]; then
        error "Arquivo .env não encontrado. Copie .env.example para .env e configure as variáveis."
        exit 1
    fi
    
    # Verificar variáveis obrigatórias
    source .env
    
    if [ -z "$POSTGRES_PASSWORD" ]; then
        error "POSTGRES_PASSWORD não definido no arquivo .env"
        exit 1
    fi
    
    if [ -z "$API_FOOTBALL_KEY" ]; then
        warning "API_FOOTBALL_KEY não definido no arquivo .env"
    fi
    
    if [ -z "$THE_ODDS_API_KEY" ]; then
        warning "THE_ODDS_API_KEY não definido no arquivo .env"
    fi
    
    success "Arquivo .env configurado"
}

# Criar diretórios necessários
create_directories() {
    log "Criando diretórios necessários..."
    
    mkdir -p data
    mkdir -p logs
    mkdir -p reports
    mkdir -p backups
    mkdir -p optimization/results
    mkdir -p optimization/exports
    
    success "Diretórios criados"
}

# Parar containers existentes
stop_containers() {
    log "Parando containers existentes..."
    
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml down --remove-orphans
    fi
    
    success "Containers parados"
}

# Remover volumes antigos (opcional)
cleanup_volumes() {
    if [ "$1" = "--clean" ]; then
        log "Removendo volumes antigos..."
        docker volume prune -f
        success "Volumes limpos"
    fi
}

# Construir imagens
build_images() {
    log "Construindo imagens Docker..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    success "Imagens construídas"
}

# Iniciar PostgreSQL
start_postgres() {
    log "Iniciando PostgreSQL..."
    
    docker-compose -f docker-compose.prod.yml up -d postgres
    
    # Aguardar PostgreSQL estar pronto
    log "Aguardando PostgreSQL estar pronto..."
    timeout=60
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U marabet_user -d marabet_ai &> /dev/null; then
            success "PostgreSQL está pronto"
            return 0
        fi
        
        sleep 2
        counter=$((counter + 2))
    done
    
    error "PostgreSQL não ficou pronto em $timeout segundos"
    exit 1
}

# Configurar banco de dados
setup_database() {
    log "Configurando banco de dados..."
    
    # Executar script de inicialização
    docker-compose -f docker-compose.prod.yml exec postgres psql -U marabet_user -d marabet_ai -f /docker-entrypoint-initdb.d/init_db.sql
    
    success "Banco de dados configurado"
}

# Migrar dados do SQLite (se existir)
migrate_data() {
    if [ -f "data/sports_data.db" ]; then
        log "Migrando dados do SQLite para PostgreSQL..."
        
        # Instalar dependências Python
        pip install psycopg2-binary pandas
        
        # Executar migração
        python scripts/migrate_to_postgres.py \
            --sqlite-path data/sports_data.db \
            --postgres-url "postgresql://marabet_user:${POSTGRES_PASSWORD}@localhost:5432/marabet_ai"
        
        success "Dados migrados do SQLite"
    else
        log "Nenhum arquivo SQLite encontrado, pulando migração"
    fi
}

# Iniciar Redis
start_redis() {
    log "Iniciando Redis..."
    
    docker-compose -f docker-compose.prod.yml up -d redis
    
    # Aguardar Redis estar pronto
    log "Aguardando Redis estar pronto..."
    timeout=30
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker-compose -f docker-compose.prod.yml exec redis redis-cli ping &> /dev/null; then
            success "Redis está pronto"
            return 0
        fi
        
        sleep 1
        counter=$((counter + 1))
    done
    
    error "Redis não ficou pronto em $timeout segundos"
    exit 1
}

# Iniciar aplicação
start_application() {
    log "Iniciando aplicação MaraBet AI..."
    
    docker-compose -f docker-compose.prod.yml up -d marabet-ai
    
    success "Aplicação iniciada"
}

# Iniciar dashboard
start_dashboard() {
    log "Iniciando dashboard..."
    
    docker-compose -f docker-compose.prod.yml up -d dashboard
    
    success "Dashboard iniciado"
}

# Iniciar coletor
start_collector() {
    log "Iniciando coletor automatizado..."
    
    docker-compose -f docker-compose.prod.yml up -d collector
    
    success "Coletor iniciado"
}

# Iniciar Nginx
start_nginx() {
    log "Iniciando Nginx..."
    
    docker-compose -f docker-compose.prod.yml up -d nginx
    
    success "Nginx iniciado"
}

# Iniciar monitoramento
start_monitoring() {
    log "Iniciando monitoramento..."
    
    docker-compose -f docker-compose.prod.yml up -d monitoring
    
    success "Monitoramento iniciado"
}

# Verificar saúde dos serviços
health_check() {
    log "Verificando saúde dos serviços..."
    
    # Verificar PostgreSQL
    if docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U marabet_user -d marabet_ai &> /dev/null; then
        success "PostgreSQL: OK"
    else
        error "PostgreSQL: FALHOU"
    fi
    
    # Verificar Redis
    if docker-compose -f docker-compose.prod.yml exec redis redis-cli ping &> /dev/null; then
        success "Redis: OK"
    else
        error "Redis: FALHOU"
    fi
    
    # Verificar aplicação
    if curl -f http://localhost:8000/health &> /dev/null; then
        success "Aplicação: OK"
    else
        error "Aplicação: FALHOU"
    fi
    
    # Verificar dashboard
    if curl -f http://localhost:8001/health &> /dev/null; then
        success "Dashboard: OK"
    else
        error "Dashboard: FALHOU"
    fi
}

# Mostrar status dos containers
show_status() {
    log "Status dos containers:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    log "URLs de acesso:"
    echo "  🌐 Aplicação: http://localhost:8000"
    echo "  📊 Dashboard: http://localhost:8001"
    echo "  🔧 Otimização: http://localhost:8000/optimization"
    echo "  📈 Monitoramento: http://localhost:9090"
    echo "  🗄️ PostgreSQL: localhost:5432"
    echo "  🔴 Redis: localhost:6379"
}

# Função principal
main() {
    log "🚀 Iniciando deploy do MaraBet AI com PostgreSQL"
    
    # Verificações iniciais
    check_docker
    check_env_file
    create_directories
    
    # Parar containers existentes
    stop_containers
    cleanup_volumes "$1"
    
    # Construir imagens
    build_images
    
    # Iniciar serviços em ordem
    start_postgres
    setup_database
    migrate_data
    start_redis
    start_application
    start_dashboard
    start_collector
    start_nginx
    start_monitoring
    
    # Verificar saúde
    health_check
    
    # Mostrar status
    show_status
    
    success "🎉 Deploy concluído com sucesso!"
    log "Para ver os logs: docker-compose -f docker-compose.prod.yml logs -f"
    log "Para parar: docker-compose -f docker-compose.prod.yml down"
}

# Verificar argumentos
case "${1:-}" in
    --help|-h)
        echo "Uso: $0 [--clean]"
        echo ""
        echo "Opções:"
        echo "  --clean    Remove volumes antigos antes do deploy"
        echo "  --help     Mostra esta ajuda"
        exit 0
        ;;
    --clean)
        main --clean
        ;;
    "")
        main
        ;;
    *)
        error "Argumento inválido: $1"
        echo "Use --help para ver as opções disponíveis"
        exit 1
        ;;
esac
