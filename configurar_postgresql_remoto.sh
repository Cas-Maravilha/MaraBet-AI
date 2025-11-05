#!/bin/bash

# =============================================
# Script: Configuração Automática PostgreSQL
# Para servidor remoto 37.27.220.67
# Configura acesso remoto completo
# =============================================

set -e  # Aborta em caso de erro

echo "🚀 Iniciando configuração de acesso remoto ao PostgreSQL..."
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script precisa ser executado com sudo"
    echo "   Execute: sudo bash configurar_postgresql_remoto.sh"
    exit 1
fi

# Variáveis de configuração
POSTGRESQL_VERSION="14"
POSTGRESQL_CONF="/etc/postgresql/${POSTGRESQL_VERSION}/main/postgresql.conf"
PG_HBA_CONF="/etc/postgresql/${POSTGRESQL_VERSION}/main/pg_hba.conf"
DB_USER="meu_root\$marabet"
DB_NAME="marabet"
DB_PASSWORD="dudbeeGdNBSxjpEWlop"

echo "📋 Configurações:"
echo "   PostgreSQL Version: $POSTGRESQL_VERSION"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Port: 5432"
echo ""

# === 1. Verificar se PostgreSQL está instalado ===
echo "🔍 Verificando instalação do PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL não está instalado!"
    echo "   Instale com: sudo apt install postgresql-14 postgresql-client-14"
    exit 1
fi

echo "✅ PostgreSQL instalado"
echo ""

# === 2. Fazer backup dos arquivos ===
echo "💾 Fazendo backup dos arquivos de configuração..."
BACKUP_DIR="/etc/postgresql/${POSTGRESQL_VERSION}/main/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp "$POSTGRESQL_CONF" "$BACKUP_DIR/postgresql.conf.backup"
cp "$PG_HBA_CONF" "$BACKUP_DIR/pg_hba.conf.backup"
echo "✅ Backups salvos em: $BACKUP_DIR"
echo ""

# === 3. Configurar postgresql.conf ===
echo "📝 Configurando postgresql.conf..."

# Verificar se listen_addresses já está configurado
if grep -q "^listen_addresses = '*'" "$POSTGRESQL_CONF"; then
    echo "   ✅ listen_addresses já está configurado como '*'"
else
    # Descomentar e alterar listen_addresses
    sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/" "$POSTGRESQL_CONF"
    sed -i "s/^listen_addresses = 'localhost'/listen_addresses = '*'/" "$POSTGRESQL_CONF"
    echo "   ✅ listen_addresses configurado como '*'"
fi

# Verificar configuração
echo "   📊 Configuração atual:"
grep "^listen_addresses" "$POSTGRESQL_CONF" || echo "   ⚠️  listen_addresses não encontrado"
echo ""

# === 4. Configurar pg_hba.conf ===
echo "📝 Configurando pg_hba.conf para acesso remoto..."

# Verificar se regra já existe
if grep -q "host.*marabet.*meu_root" "$PG_HBA_CONF"; then
    echo "   ✅ Regra de acesso remoto já existe"
else
    # Adicionar regras de acesso remoto
    echo "" >> "$PG_HBA_CONF"
    echo "# Configuração para acesso remoto - MaraBet AI" >> "$PG_HBA_CONF"
    echo "# Adicionado em $(date)" >> "$PG_HBA_CONF"
    echo "host    $DB_NAME         $DB_USER    0.0.0.0/0               scram-sha-256" >> "$PG_HBA_CONF"
    echo "host    $DB_NAME         $DB_USER    ::/0                    scram-sha-256" >> "$PG_HBA_CONF"
    echo "   ✅ Regras de acesso remoto adicionadas"
fi

# Verificar regras
echo "   📊 Regras de acesso remoto:"
grep "$DB_USER" "$PG_HBA_CONF" | grep -v "^#" || echo "   ⚠️  Nenhuma regra encontrada"
echo ""

# === 5. Verificar/Criar usuário e banco ===
echo "🗄 Verificando usuário e banco de dados..."

# Criar usuário se não existir
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "   ✅ Usuário $DB_USER já existe"
    # Atualizar senha
    sudo -u postgres psql -c "ALTER USER \"$DB_USER\" WITH PASSWORD '$DB_PASSWORD';" > /dev/null 2>&1
    echo "   ✅ Senha atualizada"
else
    echo "   📝 Criando usuário $DB_USER..."
    sudo -u postgres psql -c "CREATE USER \"$DB_USER\" WITH PASSWORD '$DB_PASSWORD' CREATEDB;" > /dev/null 2>&1
    echo "   ✅ Usuário criado"
fi

# Criar banco se não existir
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "   ✅ Banco $DB_NAME já existe"
else
    echo "   📝 Criando banco $DB_NAME..."
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER \"$DB_USER\";" > /dev/null 2>&1
    echo "   ✅ Banco criado"
fi

# Conceder privilégios
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO \"$DB_USER\";" > /dev/null 2>&1
echo "   ✅ Privilégios concedidos"
echo ""

# === 6. Configurar Firewall (UFW) ===
echo "🧱 Configurando firewall..."

if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "   📝 Firewall UFW está ativo"
        if ufw status | grep -q "5432/tcp"; then
            echo "   ✅ Porta 5432 já está permitida"
        else
            ufw allow 5432/tcp
            echo "   ✅ Porta 5432 adicionada ao firewall"
        fi
    else
        echo "   ⚠️  Firewall UFW não está ativo (opcional)"
    fi
else
    echo "   ⚠️  UFW não está instalado (opcional)"
fi
echo ""

# === 7. Reiniciar PostgreSQL ===
echo "🔄 Reiniciando PostgreSQL..."
systemctl restart postgresql
echo "✅ PostgreSQL reiniciado"
echo ""

# === 8. Verificar status ===
echo "🔍 Verificando status da configuração..."
echo ""

# Verificar se está escutando externamente
echo "📊 Porta PostgreSQL:"
if ss -tlnp | grep -q ":5432"; then
    ss -tlnp | grep ":5432"
    echo "✅ PostgreSQL está escutando na porta 5432"
else
    echo "❌ PostgreSQL não está escutando na porta 5432"
fi
echo ""

# Verificar listen_addresses
echo "📊 Configuração listen_addresses:"
grep "^listen_addresses" "$POSTGRESQL_CONF"
echo ""

# Verificar regras pg_hba.conf
echo "📊 Regras de acesso remoto no pg_hba.conf:"
grep "$DB_USER" "$PG_HBA_CONF" | grep -v "^#" || echo "Nenhuma regra encontrada"
echo ""

# === 9. Teste de conexão local ===
echo "🧪 Testando conexão local..."
if sudo -u postgres psql -d "$DB_NAME" -U "$DB_USER" -h localhost -c "SELECT 'Conexão bem-sucedida!' as status;" > /dev/null 2>&1; then
    echo "✅ Conexão local funcionando!"
else
    echo "⚠️  Conexão local com problemas (verifique credenciais)"
fi
echo ""

# === 10. Resumo final ===
echo "=========================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "📋 Dados de conexão:"
echo "   Host: $(hostname -I | awk '{print $1}') ou 37.27.220.67"
echo "   Porta: 5432"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Password: $DB_PASSWORD"
echo ""
echo "📊 Arquivos modificados:"
echo "   - $POSTGRESQL_CONF"
echo "   - $PG_HBA_CONF"
echo ""
echo "💾 Backups salvos em: $BACKUP_DIR"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Verifique se o firewall do servidor permite conexões na porta 5432"
echo "   2. Para maior segurança, considere restringir acesso por IP no pg_hba.conf"
echo "   3. Use SSL/TLS para conexões seguras quando possível"
echo ""
echo "🧪 Para testar a conexão remota, execute em outro computador:"
echo "   psql -h 37.27.220.67 -p 5432 -U \"$DB_USER\" -d $DB_NAME"
echo ""

