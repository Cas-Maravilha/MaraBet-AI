#!/bin/bash
# Script de setup inicial para MaraBet AI

set -e

echo "🔧 MARABET AI - SETUP INICIAL"
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

# Verificar sistema operacional
check_os() {
    log "Verificando sistema operacional..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        success "Sistema Linux detectado"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        success "Sistema macOS detectado"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        success "Sistema Windows detectado"
    else
        warning "Sistema operacional não identificado: $OSTYPE"
        OS="unknown"
    fi
}

# Instalar Docker
install_docker() {
    log "Verificando se Docker está instalado..."
    
    if command -v docker &> /dev/null; then
        success "Docker já está instalado"
        docker --version
        return 0
    fi
    
    log "Docker não encontrado. Instalando..."
    
    case $OS in
        "linux")
            # Instalar Docker no Linux
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            success "Docker instalado no Linux"
            ;;
        "macos")
            # Instalar Docker no macOS
            if command -v brew &> /dev/null; then
                brew install --cask docker
                success "Docker instalado via Homebrew"
            else
                error "Homebrew não encontrado. Instale o Docker Desktop manualmente."
            fi
            ;;
        "windows")
            error "Instale o Docker Desktop para Windows manualmente."
            ;;
        *)
            error "Sistema operacional não suportado para instalação automática do Docker."
            ;;
    esac
}

# Instalar Docker Compose
install_docker_compose() {
    log "Verificando se Docker Compose está instalado..."
    
    if command -v docker-compose &> /dev/null; then
        success "Docker Compose já está instalado"
        docker-compose --version
        return 0
    fi
    
    log "Docker Compose não encontrado. Instalando..."
    
    case $OS in
        "linux")
            # Instalar Docker Compose no Linux
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            success "Docker Compose instalado no Linux"
            ;;
        "macos")
            # Instalar Docker Compose no macOS
            if command -v brew &> /dev/null; then
                brew install docker-compose
                success "Docker Compose instalado via Homebrew"
            else
                error "Homebrew não encontrado. Instale o Docker Compose manualmente."
            fi
            ;;
        "windows")
            error "Docker Compose deve vir com o Docker Desktop para Windows."
            ;;
        *)
            error "Sistema operacional não suportado para instalação automática do Docker Compose."
            ;;
    esac
}

# Configurar arquivo .env
setup_env() {
    log "Configurando arquivo .env..."
    
    if [ -f .env ]; then
        warning "Arquivo .env já existe. Fazendo backup..."
        cp .env .env.backup
    fi
    
    # Criar arquivo .env com suas chaves
    cat > .env << EOF
# Configurações do MaraBet AI
# Gerado automaticamente em $(date)

# API Keys
API_FOOTBALL_KEY=747d6e19a2d3a435fdb7a419007a45fa
THE_ODDS_API_KEY=your_the_odds_api_key_here

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Email
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br

# Banco de dados
DATABASE_URL=sqlite:///data/sports_data.db

# Redis
REDIS_URL=redis://redis:6379

# Aplicação
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
HOST=0.0.0.0
PORT=5000
EOF
    
    success "Arquivo .env criado com suas chaves configuradas"
}

# Criar diretórios necessários
create_directories() {
    log "Criando diretórios necessários..."
    
    mkdir -p data logs reports nginx/ssl scripts backups
    
    # Definir permissões
    chmod 755 data logs reports scripts backups
    chmod 700 nginx/ssl
    
    success "Diretórios criados"
}

# Configurar SSL (opcional)
setup_ssl() {
    log "Configurando certificados SSL..."
    
    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
        log "Gerando certificados SSL auto-assinados..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=BR/ST=SP/L=SaoPaulo/O=MaraBetAI/CN=localhost"
        
        success "Certificados SSL gerados"
    else
        success "Certificados SSL já existem"
    fi
}

# Configurar firewall (Linux)
setup_firewall() {
    if [ "$OS" = "linux" ]; then
        log "Configurando firewall..."
        
        if command -v ufw &> /dev/null; then
            sudo ufw allow 80/tcp
            sudo ufw allow 443/tcp
            sudo ufw allow 5000/tcp
            sudo ufw allow 8000/tcp
            success "Firewall configurado"
        else
            warning "UFW não encontrado. Configure o firewall manualmente."
        fi
    fi
}

# Testar instalação
test_installation() {
    log "Testando instalação..."
    
    # Testar Docker
    if docker --version &> /dev/null; then
        success "Docker funcionando"
    else
        error "Docker não está funcionando"
    fi
    
    # Testar Docker Compose
    if docker-compose --version &> /dev/null; then
        success "Docker Compose funcionando"
    else
        error "Docker Compose não está funcionando"
    fi
    
    # Testar se os arquivos necessários existem
    if [ -f docker-compose.yml ] && [ -f Dockerfile ]; then
        success "Arquivos de configuração encontrados"
    else
        error "Arquivos de configuração não encontrados"
    fi
}

# Mostrar próximos passos
show_next_steps() {
    echo
    success "Setup concluído com sucesso!"
    echo
    log "Próximos passos:"
    echo "1. Configure a senha de app do Yahoo no arquivo .env (opcional)"
    echo "2. Execute: ./scripts/deploy.sh"
    echo "3. Acesse: http://localhost:8000"
    echo
    log "Comandos úteis:"
    echo "- Deploy: ./scripts/deploy.sh"
    echo "- Build: ./scripts/build.sh"
    echo "- Logs: docker-compose logs -f"
    echo "- Parar: docker-compose down"
    echo
    log "Arquivos importantes:"
    echo "- Configuração: .env"
    echo "- Docker: docker-compose.yml"
    echo "- Nginx: nginx/nginx.conf"
    echo "- Scripts: scripts/"
}

# Função principal
main() {
    log "Iniciando setup do MaraBet AI..."
    
    # Verificar sistema operacional
    check_os
    
    # Instalar Docker
    install_docker
    
    # Instalar Docker Compose
    install_docker_compose
    
    # Configurar arquivo .env
    setup_env
    
    # Criar diretórios
    create_directories
    
    # Configurar SSL
    setup_ssl
    
    # Configurar firewall
    setup_firewall
    
    # Testar instalação
    test_installation
    
    # Mostrar próximos passos
    show_next_steps
}

# Executar setup
main "$@"
