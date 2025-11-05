#!/bin/bash
# Script para build do Docker - MaraBet AI

set -e

echo "🐳 MARABET AI - BUILD DOCKER"
echo "=============================="

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
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Instale o Docker primeiro."
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    warning "Arquivo .env não encontrado. Criando arquivo de exemplo..."
    cat > .env << EOF
# Configurações do MaraBet AI
API_FOOTBALL_KEY=your_api_football_key_here
THE_ODDS_API_KEY=your_the_odds_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_password_here
NOTIFICATION_EMAIL=your_email@example.com
ADMIN_EMAIL=admin@example.com
EOF
    warning "Configure suas chaves no arquivo .env antes de continuar."
fi

# Criar diretórios necessários
log "Criando diretórios necessários..."
mkdir -p data logs reports nginx/ssl

# Definir versão da imagem
VERSION=${1:-latest}
IMAGE_NAME="marabet-ai"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

log "Building imagem Docker: ${FULL_IMAGE_NAME}"

# Build da imagem
log "Iniciando build da imagem..."
if docker build -t "${FULL_IMAGE_NAME}" .; then
    success "Imagem ${FULL_IMAGE_NAME} criada com sucesso!"
else
    error "Falha ao criar a imagem Docker"
fi

# Verificar se a imagem foi criada
if docker images | grep -q "${IMAGE_NAME}"; then
    success "Imagem verificada e pronta para uso"
    
    # Mostrar informações da imagem
    log "Informações da imagem:"
    docker images | grep "${IMAGE_NAME}"
    
    # Mostrar tamanho da imagem
    IMAGE_SIZE=$(docker images --format "table {{.Size}}" "${FULL_IMAGE_NAME}" | tail -n 1)
    log "Tamanho da imagem: ${IMAGE_SIZE}"
    
else
    error "Imagem não foi criada corretamente"
fi

# Opção para testar a imagem
read -p "Deseja testar a imagem agora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Testando a imagem..."
    
    # Testar se a imagem roda
    if docker run --rm "${FULL_IMAGE_NAME}" python -c "print('MaraBet AI - Teste OK')"; then
        success "Imagem testada com sucesso!"
    else
        error "Falha no teste da imagem"
    fi
fi

# Opção para fazer push (se configurado)
if [ ! -z "$DOCKER_REGISTRY" ]; then
    read -p "Deseja fazer push para o registry? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Fazendo push para ${DOCKER_REGISTRY}/${FULL_IMAGE_NAME}..."
        docker tag "${FULL_IMAGE_NAME}" "${DOCKER_REGISTRY}/${FULL_IMAGE_NAME}"
        docker push "${DOCKER_REGISTRY}/${FULL_IMAGE_NAME}"
        success "Push concluído!"
    fi
fi

echo
success "Build concluído com sucesso!"
echo
log "Próximos passos:"
echo "1. Configure suas chaves no arquivo .env"
echo "2. Execute: docker-compose up -d"
echo "3. Acesse: http://localhost:8000"
echo
log "Comandos úteis:"
echo "- Ver logs: docker-compose logs -f"
echo "- Parar serviços: docker-compose down"
echo "- Rebuild: docker-compose up --build -d"
echo "- Limpar: docker system prune -a"
