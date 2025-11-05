#!/bin/bash

# =============================================
# Script: Verificação de Configuração PostgreSQL
# Verifica se tudo está configurado corretamente
# =============================================

echo "🔍 Verificando configuração do PostgreSQL..."
echo ""

POSTGRESQL_VERSION="14"
POSTGRESQL_CONF="/etc/postgresql/${POSTGRESQL_VERSION}/main/postgresql.conf"
PG_HBA_CONF="/etc/postgresql/${POSTGRESQL_VERSION}/main/pg_hba.conf"
DB_USER="meu_root\$marabet"
DB_NAME="marabet"

# === 1. Status do serviço ===
echo "1️⃣ Status do serviço PostgreSQL:"
if systemctl is-active --quiet postgresql; then
    echo "   ✅ PostgreSQL está em execução"
else
    echo "   ❌ PostgreSQL não está em execução"
    echo "      Execute: sudo systemctl start postgresql"
fi
echo ""

# === 2. Porta escutando ===
echo "2️⃣ Porta PostgreSQL (5432):"
if ss -tlnp | grep -q ":5432"; then
    echo "   ✅ PostgreSQL está escutando na porta 5432:"
    ss -tlnp | grep ":5432" | head -2 | sed 's/^/      /'
    
    # Verificar se está escutando em 0.0.0.0
    if ss -tlnp | grep ":5432" | grep -q "0.0.0.0"; then
        echo "   ✅ Está escutando em todas as interfaces (0.0.0.0)"
    else
        echo "   ⚠️  Está escutando apenas em localhost"
    fi
else
    echo "   ❌ PostgreSQL não está escutando na porta 5432"
fi
echo ""

# === 3. postgresql.conf ===
echo "3️⃣ Configuração postgresql.conf:"
if [ -f "$POSTGRESQL_CONF" ]; then
    echo "   📄 Arquivo existe: $POSTGRESQL_CONF"
    
    # Verificar listen_addresses
    if grep -q "^listen_addresses = '*'" "$POSTGRESQL_CONF"; then
        echo "   ✅ listen_addresses = '*' (correto)"
    elif grep -q "^listen_addresses" "$POSTGRESQL_CONF"; then
        echo "   ⚠️  listen_addresses configurado:"
        grep "^listen_addresses" "$POSTGRESQL_CONF" | sed 's/^/      /'
    else
        echo "   ❌ listen_addresses não está configurado"
    fi
else
    echo "   ❌ Arquivo não encontrado: $POSTGRESQL_CONF"
fi
echo ""

# === 4. pg_hba.conf ===
echo "4️⃣ Configuração pg_hba.conf:"
if [ -f "$PG_HBA_CONF" ]; then
    echo "   📄 Arquivo existe: $PG_HBA_CONF"
    
    # Verificar regras de acesso remoto
    REMOTE_RULES=$(grep "host.*$DB_NAME.*$DB_USER" "$PG_HBA_CONF" | grep -v "^#")
    if [ -n "$REMOTE_RULES" ]; then
        echo "   ✅ Regras de acesso remoto encontradas:"
        echo "$REMOTE_RULES" | sed 's/^/      /'
    else
        echo "   ❌ Nenhuma regra de acesso remoto encontrada"
    fi
else
    echo "   ❌ Arquivo não encontrado: $PG_HBA_CONF"
fi
echo ""

# === 5. Usuário e banco ===
echo "5️⃣ Usuário e banco de dados:"
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "   ✅ Usuário $DB_USER existe"
else
    echo "   ❌ Usuário $DB_USER não existe"
fi

if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "   ✅ Banco $DB_NAME existe"
else
    echo "   ❌ Banco $DB_NAME não existe"
fi
echo ""

# === 6. Firewall ===
echo "6️⃣ Firewall (UFW):"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status | grep "Status:" | awk '{print $2}')
    echo "   Status: $UFW_STATUS"
    
    if [ "$UFW_STATUS" = "active" ]; then
        if ufw status | grep -q "5432/tcp"; then
            echo "   ✅ Porta 5432 está permitida"
            ufw status | grep "5432" | sed 's/^/      /'
        else
            echo "   ❌ Porta 5432 não está permitida"
            echo "      Execute: sudo ufw allow 5432/tcp"
        fi
    else
        echo "   ⚠️  Firewall não está ativo (porta pode estar bloqueada por outros meios)"
    fi
else
    echo "   ⚠️  UFW não está instalado (verifique iptables manualmente)"
fi
echo ""

# === 7. Teste de conexão local ===
echo "7️⃣ Teste de conexão local:"
if sudo -u postgres psql -d "$DB_NAME" -U "$DB_USER" -h localhost -c "SELECT current_database(), current_user;" > /dev/null 2>&1; then
    echo "   ✅ Conexão local funcionando"
else
    echo "   ❌ Conexão local falhou (verifique credenciais e pg_hba.conf)"
fi
echo ""

# === Resumo ===
echo "=========================================="
echo "📊 RESUMO DA VERIFICAÇÃO"
echo "=========================================="
echo ""
echo "✅ Verificações concluídas!"
echo ""
echo "💡 Para configurar tudo automaticamente, execute:"
echo "   sudo bash configurar_postgresql_remoto.sh"
echo ""

