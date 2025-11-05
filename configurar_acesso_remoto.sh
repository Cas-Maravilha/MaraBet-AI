#!/bin/bash
# Script para configurar acesso remoto ao PostgreSQL

echo "📝 Configurando acesso remoto ao PostgreSQL..."

# Fazer backup do arquivo original
sudo cp /etc/postgresql/14/main/postgresql.conf /etc/postgresql/14/main/postgresql.conf.backup

# Alterar listen_addresses de localhost para *
# Primeiro tentar descomentar se estiver comentado
sudo sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf

# Se já estiver descomentado com localhost, alterar para *
sudo sed -i "s/^listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf

# Verificar a alteração
echo ""
echo "✅ Alteração aplicada. Configuração atual:"
sudo grep "^listen_addresses" /etc/postgresql/14/main/postgresql.conf || echo "⚠️  listen_addresses não encontrado"

echo ""
echo "📋 Resumo das configurações de conexão:"
sudo grep -E "^listen_addresses|^port" /etc/postgresql/14/main/postgresql.conf | grep -v "^#"

