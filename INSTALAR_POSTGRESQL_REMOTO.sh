#!/bin/bash

# =============================================
# Script: Instalação e Configuração PostgreSQL
# Instala PostgreSQL 14 e configura acesso remoto
# Para servidor remoto Ubuntu/Debian
# =============================================

set -e

echo "🚀 Iniciando instalação e configuração do PostgreSQL..."
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script precisa ser executado com sudo"
    echo "   Execute: sudo bash INSTALAR_POSTGRESQL_REMOTO.sh"
    exit 1
fi

# Variáveis
POSTGRESQL_VERSION="14"
DB_USER="meu_root\$marabet"
DB_NAME="marabet"
DB_PASSWORD="dudbeeGdNBSxjpEWlop"

# === 1. Atualizar sistema ===
echo "🔄 Atualizando sistema..."
apt update
echo "✅ Sistema atualizado"
echo ""

# === 2. Instalar PostgreSQL ===
echo "📦 Instalando PostgreSQL $POSTGRESQL_VERSION..."

# Verificar se já está instalado
if command -v psql &> /dev/null; then
    INSTALLED_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)
    echo "   ⚠️  PostgreSQL já está instalado (versão $INSTALLED_VERSION)"
else
    # Adicionar repositório do PostgreSQL (se necessário)
    if [ ! -f "/etc/apt/sources.list.d/pgdg.list" ]; then
        echo "   📝 Adicionando repositório oficial do PostgreSQL..."
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
        wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
        apt update
    fi
    
    # Instalar PostgreSQL
    apt install -y postgresql-$POSTGRESQL_VERSION postgresql-client-$POSTGRESQL_VERSION
    echo "✅ PostgreSQL $POSTGRESQL_VERSION instalado"
fi
echo ""

# === 3. Iniciar e habilitar serviço ===
echo "⚡ Iniciando e habilitando PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql
echo "✅ PostgreSQL iniciado e habilitado"
echo ""

# === 4. Criar usuário e banco ===
echo "🗄 Criando usuário e banco de dados..."

# Criar usuário
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "   ✅ Usuário $DB_USER já existe"
    sudo -u postgres psql -c "ALTER USER \"$DB_USER\" WITH PASSWORD '$DB_PASSWORD';" > /dev/null 2>&1
    echo "   ✅ Senha atualizada"
else
    sudo -u postgres psql -c "CREATE USER \"$DB_USER\" WITH PASSWORD '$DB_PASSWORD' CREATEDB;" > /dev/null 2>&1
    echo "   ✅ Usuário criado"
fi

# Criar banco
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "   ✅ Banco $DB_NAME já existe"
else
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER \"$DB_USER\";" > /dev/null 2>&1
    echo "   ✅ Banco criado"
fi

# Conceder privilégios
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO \"$DB_USER\";" > /dev/null 2>&1
echo "✅ Usuário e banco configurados"
echo ""

# === 5. Configurar acesso remoto ===
echo "📝 Configurando acesso remoto..."

# Verificar se script de configuração existe
if [ -f "configurar_postgresql_remoto.sh" ]; then
    echo "   🔄 Executando script de configuração..."
    bash configurar_postgresql_remoto.sh
else
    echo "   ⚠️  Script configurar_postgresql_remoto.sh não encontrado"
    echo "   Execute manualmente: sudo bash configurar_postgresql_remoto.sh"
fi
echo ""

# === 6. Verificar instalação ===
echo "🔍 Verificando instalação..."
psql --version
echo ""

echo "✅ INSTALAÇÃO E CONFIGURAÇÃO CONCLUÍDA!"
echo ""
echo "📋 Dados de conexão:"
echo "   Host: $(hostname -I | awk '{print $1}')"
echo "   Porta: 5432"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Password: $DB_PASSWORD"
echo ""

