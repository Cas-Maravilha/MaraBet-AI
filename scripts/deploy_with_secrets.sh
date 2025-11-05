#!/bin/bash

# Script de Deploy com Sistema de Secrets - MaraBet AI
# Deploy completo com gerenciamento seguro de secrets

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

# Verificar se Python está instalado
check_python() {
    log "Verificando Python..."
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não está instalado. Instale o Python 3 primeiro."
        exit 1
    fi
    
    # Verificar versão mínima
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
        error "Python 3.8+ é necessário. Versão atual: $python_version"
        exit 1
    fi
    
    success "Python $python_version encontrado"
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

# Instalar dependências Python
install_dependencies() {
    log "Instalando dependências Python..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        success "Dependências Python instaladas"
    else
        warning "Arquivo requirements.txt não encontrado"
    fi
}

# Configurar sistema de secrets
setup_secrets() {
    log "Configurando sistema de secrets..."
    
    # Verificar se master key está definida
    if [ -z "$MARABET_MASTER_KEY" ]; then
        warning "MARABET_MASTER_KEY não definida, gerando automaticamente..."
        export MARABET_MASTER_KEY=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?') for _ in range(64)))")
        echo "export MARABET_MASTER_KEY='$MARABET_MASTER_KEY'" >> ~/.bashrc
        success "Master key gerada e salva em ~/.bashrc"
    fi
    
    # Inicializar sistema de secrets
    python3 scripts/init_secrets.py --backend local
    
    if [ $? -eq 0 ]; then
        success "Sistema de secrets configurado"
    else
        error "Erro ao configurar sistema de secrets"
        exit 1
    fi
}

# Configurar chaves de API
setup_api_keys() {
    log "Configurando chaves de API..."
    
    # Verificar se arquivo .env existe
    if [ ! -f ".env" ]; then
        error "Arquivo .env não encontrado. Execute setup_secrets primeiro."
        exit 1
    fi
    
    # Carregar variáveis do .env
    source .env
    
    # Configurar API-Football se fornecida
    if [ ! -z "$API_FOOTBALL_KEY" ] && [ "$API_FOOTBALL_KEY" != "your_api_football_key_here" ]; then
        python3 scripts/secrets_manager.py set-api-key api_football "$API_FOOTBALL_KEY"
        success "Chave API-Football configurada"
    else
        warning "Chave API-Football não configurada. Configure manualmente depois."
    fi
    
    # Configurar The Odds API se fornecida
    if [ ! -z "$THE_ODDS_API_KEY" ] && [ "$THE_ODDS_API_KEY" != "your_odds_api_key_here" ]; then
        python3 scripts/secrets_manager.py set-api-key odds_api "$THE_ODDS_API_KEY"
        success "Chave The Odds API configurada"
    else
        warning "Chave The Odds API não configurada. Configure manualmente depois."
    fi
    
    # Configurar Telegram se fornecido
    if [ ! -z "$TELEGRAM_BOT_TOKEN" ] && [ "$TELEGRAM_BOT_TOKEN" != "your_telegram_bot_token_here" ]; then
        python3 scripts/secrets_manager.py set telegram_bot_token "$TELEGRAM_BOT_TOKEN"
        success "Token do Telegram configurado"
    else
        warning "Token do Telegram não configurado. Configure manualmente depois."
    fi
    
    if [ ! -z "$TELEGRAM_CHAT_ID" ] && [ "$TELEGRAM_CHAT_ID" != "your_telegram_chat_id_here" ]; then
        python3 scripts/secrets_manager.py set telegram_chat_id "$TELEGRAM_CHAT_ID"
        success "Chat ID do Telegram configurado"
    fi
}

# Validar secrets
validate_secrets() {
    log "Validando secrets..."
    
    python3 scripts/secrets_manager.py validate
    
    if [ $? -eq 0 ]; then
        success "Secrets validados com sucesso"
    else
        warning "Alguns secrets falharam na validação. Verifique as configurações."
    fi
}

# Configurar rotação automática
setup_rotation() {
    log "Configurando rotação automática de chaves..."
    
    # Adicionar chaves importantes à rotação
    python3 scripts/secrets_manager.py add-rotation jwt_secret_key --interval-days 365 --warning-days 30
    python3 scripts/secrets_manager.py add-rotation master_key --interval-days 365 --warning-days 30
    python3 scripts/secrets_manager.py add-rotation api_key_api_football --interval-days 180 --warning-days 14
    python3 scripts/secrets_manager.py add-rotation api_key_odds_api --interval-days 180 --warning-days 14
    python3 scripts/secrets_manager.py add-rotation telegram_bot_token --interval-days 180 --warning-days 14
    
    success "Sistema de rotação configurado"
}

# Criar diretórios necessários
create_directories() {
    log "Criando diretórios necessários..."
    
    mkdir -p data
    mkdir -p logs
    mkdir -p reports
    mkdir -p backups
    mkdir -p secrets/data
    mkdir -p secrets/backups
    mkdir -p optimization/results
    mkdir -p optimization/exports
    
    # Definir permissões restritivas para diretórios de secrets
    chmod 700 secrets/data
    chmod 700 secrets/backups
    
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

# Construir imagens
build_images() {
    log "Construindo imagens Docker..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    success "Imagens construídas"
}

# Iniciar serviços
start_services() {
    log "Iniciando serviços..."
    
    # Iniciar PostgreSQL
    docker-compose -f docker-compose.prod.yml up -d postgres
    
    # Aguardar PostgreSQL estar pronto
    log "Aguardando PostgreSQL estar pronto..."
    timeout=60
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U marabet_user -d marabet_ai &> /dev/null; then
            success "PostgreSQL está pronto"
            break
        fi
        
        sleep 2
        counter=$((counter + 2))
    done
    
    if [ $counter -ge $timeout ]; then
        error "PostgreSQL não ficou pronto em $timeout segundos"
        exit 1
    fi
    
    # Iniciar Redis
    docker-compose -f docker-compose.prod.yml up -d redis
    
    # Aguardar Redis estar pronto
    log "Aguardando Redis estar pronto..."
    timeout=30
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker-compose -f docker-compose.prod.yml exec redis redis-cli ping &> /dev/null; then
            success "Redis está pronto"
            break
        fi
        
        sleep 1
        counter=$((counter + 1))
    done
    
    if [ $counter -ge $timeout ]; then
        error "Redis não ficou pronto em $timeout segundos"
        exit 1
    fi
    
    # Iniciar aplicação
    docker-compose -f docker-compose.prod.yml up -d marabet-ai
    success "Aplicação iniciada"
    
    # Iniciar dashboard
    docker-compose -f docker-compose.prod.yml up -d dashboard
    success "Dashboard iniciado"
    
    # Iniciar coletor
    docker-compose -f docker-compose.prod.yml up -d collector
    success "Coletor iniciado"
    
    # Iniciar Nginx
    docker-compose -f docker-compose.prod.yml up -d nginx
    success "Nginx iniciado"
    
    # Iniciar monitoramento
    docker-compose -f docker-compose.prod.yml up -d monitoring
    success "Monitoramento iniciado"
}

# Iniciar rotação automática
start_rotation() {
    log "Iniciando rotação automática de chaves..."
    
    python3 scripts/secrets_manager.py start-rotation
    
    success "Rotação automática iniciada"
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
    
    echo ""
    log "Comandos úteis:"
    echo "  📋 Listar secrets: python3 scripts/secrets_manager.py list"
    echo "  🔍 Validar secrets: python3 scripts/secrets_manager.py validate"
    echo "  🔄 Status rotação: python3 scripts/secrets_manager.py rotation-status"
    echo "  📊 Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  🛑 Parar: docker-compose -f docker-compose.prod.yml down"
}

# Função principal
main() {
    log "🚀 Iniciando deploy do MaraBet AI com Sistema de Secrets"
    
    # Verificações iniciais
    check_python
    check_docker
    
    # Instalar dependências
    install_dependencies
    
    # Criar diretórios
    create_directories
    
    # Configurar sistema de secrets
    setup_secrets
    
    # Configurar chaves de API
    setup_api_keys
    
    # Validar secrets
    validate_secrets
    
    # Configurar rotação
    setup_rotation
    
    # Parar containers existentes
    stop_containers
    
    # Construir imagens
    build_images
    
    # Iniciar serviços
    start_services
    
    # Iniciar rotação automática
    start_rotation
    
    # Verificar saúde
    health_check
    
    # Mostrar status
    show_status
    
    success "🎉 Deploy com Sistema de Secrets concluído com sucesso!"
}

# Verificar argumentos
case "${1:-}" in
    --help|-h)
        echo "Uso: $0 [--help]"
        echo ""
        echo "Deploy completo do MaraBet AI com sistema de gerenciamento de secrets"
        echo ""
        echo "O script irá:"
        echo "  1. Verificar dependências (Python, Docker)"
        echo "  2. Instalar dependências Python"
        echo "  3. Configurar sistema de secrets"
        echo "  4. Configurar chaves de API (se fornecidas)"
        echo "  5. Validar secrets"
        echo "  6. Configurar rotação automática"
        echo "  7. Fazer deploy dos serviços"
        echo "  8. Iniciar rotação automática"
        echo "  9. Verificar saúde dos serviços"
        echo ""
        echo "Variáveis de ambiente necessárias:"
        echo "  MARABET_MASTER_KEY - Chave mestra para criptografia (gerada automaticamente se não definida)"
        echo ""
        echo "Variáveis opcionais (configure no .env):"
        echo "  API_FOOTBALL_KEY - Chave da API-Football"
        echo "  THE_ODDS_API_KEY - Chave da The Odds API"
        echo "  TELEGRAM_BOT_TOKEN - Token do bot do Telegram"
        echo "  TELEGRAM_CHAT_ID - ID do chat do Telegram"
        exit 0
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
