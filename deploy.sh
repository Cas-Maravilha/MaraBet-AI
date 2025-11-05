#!/bin/bash
# Script de Deploy - MaraBet AI

echo "🚀 MARABET AI - DEPLOY DA APLICAÇÃO"
echo "=================================="

# Atualizar sistema
echo "🔄 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
fi

# Instalar Docker Compose se não estiver instalado
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Instalar ferramentas úteis
echo "🛠️ Instalando ferramentas..."
sudo apt install -y htop curl wget vim nano git python3 python3-pip python3-venv

# Configurar variáveis de ambiente
echo "🌐 Configurando variáveis de ambiente..."
echo 'export DATABASE_URL="postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres"' >> ~/.bashrc
echo 'export REDIS_URL="redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379"' >> ~/.bashrc
echo 'export API_FOOTBALL_KEY="71b2b62386f2d1275cd3201a73e1e045"' >> ~/.bashrc
echo 'export SECRET_KEY="MaraBet2024!SuperSecretKey"' >> ~/.bashrc
echo 'export ENVIRONMENT="production"' >> ~/.bashrc
echo 'export DEBUG="false"' >> ~/.bashrc

# Recarregar configurações
source ~/.bashrc

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Remover imagens antigas
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Construir e iniciar aplicação
echo "🏗️ Construindo e iniciando aplicação..."
docker-compose -f docker-compose.production.yml up --build -d

# Verificar status
echo "🔍 Verificando status dos containers..."
docker ps

# Verificar logs
echo "📋 Logs da aplicação:"
docker-compose logs --tail=20

echo "✅ Deploy concluído!"
echo "🌐 Aplicação disponível em: http://$(curl -s ifconfig.me):8000"
