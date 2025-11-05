#!/bin/bash
# Script de Build e Inicialização - MaraBet AI

echo "🐳 MARABET AI - BUILD E INICIALIZAÇÃO DOS CONTAINERS"
echo "=================================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Iniciando Docker..."
    sudo systemctl start docker
    sleep 5
fi

# Verificar se Docker Compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Remover imagens antigas
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Build da imagem
echo "🏗️ Fazendo build da imagem..."
docker-compose -f docker-compose.production.yml build --no-cache

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso"
else
    echo "❌ Falha no build da imagem"
    exit 1
fi

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ Serviços iniciados com sucesso"
else
    echo "❌ Falha ao iniciar serviços"
    exit 1
fi

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status
echo "🔍 Verificando status dos containers..."
docker-compose -f docker-compose.production.yml ps

# Verificar logs
echo "📋 Logs da aplicação:"
docker-compose -f docker-compose.production.yml logs --tail=20

# Testar conectividade
echo "🧪 Testando conectividade..."
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Aplicação respondendo corretamente"
else
    echo "⚠️ Aplicação não está respondendo"
fi

echo "🎉 Build e inicialização concluídos!"
echo "🌐 Aplicação disponível em: http://$(curl -s ifconfig.me):8000"
