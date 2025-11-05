#!/bin/bash
# MaraBet AI - Script de Instalação
# Configuração completa do ambiente

set -e

echo "🚀 MaraBet AI - Instalação do Sistema"
echo "======================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    error "Execute este script no diretório raiz do projeto MaraBet AI"
fi

log "Iniciando instalação do MaraBet AI..."

# 1. Verificar Python
log "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 não encontrado. Instale Python 3.8+ primeiro."
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
log "Python ${PYTHON_VERSION} encontrado"

# 2. Verificar pip
log "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    error "pip3 não encontrado. Instale pip primeiro."
fi

# 3. Criar ambiente virtual
log "Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log "Ambiente virtual criado"
else
    warning "Ambiente virtual já existe"
fi

# 4. Ativar ambiente virtual
log "Ativando ambiente virtual..."
source venv/bin/activate

# 5. Atualizar pip
log "Atualizando pip..."
pip install --upgrade pip

# 6. Instalar dependências
log "Instalando dependências Python..."
pip install -r requirements.txt

# 7. Verificar Docker
log "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    warning "Docker não encontrado. Instale Docker para usar containers."
else
    log "Docker encontrado"
    if ! command -v docker-compose &> /dev/null; then
        warning "Docker Compose não encontrado. Instale Docker Compose."
    else
        log "Docker Compose encontrado"
    fi
fi

# 8. Criar diretórios necessários
log "Criando diretórios..."
mkdir -p data logs backups models
log "Diretórios criados"

# 9. Copiar arquivo de configuração
log "Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log "Arquivo .env criado a partir do template"
        warning "Configure suas chaves de API no arquivo .env"
    elif [ -f "config/development.env" ]; then
        cp config/development.env .env
        log "Arquivo .env criado a partir do template de desenvolvimento"
        warning "Configure suas chaves de API no arquivo .env"
    else
        warning "Arquivo .env.example não encontrado"
    fi
else
    warning "Arquivo .env já existe"
fi

# 10. Inicializar banco de dados
log "Inicializando banco de dados..."
if [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py
    log "Banco de dados inicializado"
else
    warning "Script init_db.py não encontrado"
fi

# 11. Verificar instalação
log "Verificando instalação..."
python -c "import fastapi, sqlalchemy, redis; print('✅ Dependências principais OK')"

log "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas chaves de API no arquivo .env"
echo "2. Execute: source venv/bin/activate"
echo "3. Execute: ./start.sh"
echo ""
echo "📞 Suporte: casmaravilha@gmail.com | +244 923066033"
echo "🌐 Website: https://www.marabet-ai.ao"
