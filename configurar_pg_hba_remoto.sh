#!/bin/bash
# Script para configurar pg_hba.conf para permitir conexões remotas

echo "📝 Configurando pg_hba.conf para acesso remoto..."

# Fazer backup
sudo cp /etc/postgresql/14/main/pg_hba.conf /etc/postgresql/14/main/pg_hba.conf.backup

# Adicionar regra para permitir conexões remotas do usuário marabet
# Usando scram-sha-256 para autenticação segura
echo ""
echo "🔐 Adicionando regra de acesso remoto para o usuário meu_root\$marabet..."

# Adicionar regras após as configurações existentes
sudo bash -c "cat >> /etc/postgresql/14/main/pg_hba.conf << 'EOF'

# Configuração para acesso remoto - MaraBet AI
# Permitir conexões remotas do usuário meu_root$marabet ao banco marabet
host    marabet         meu_root\$marabet    0.0.0.0/0               scram-sha-256
host    marabet         meu_root\$marabet    ::/0                    scram-sha-256
EOF"

echo ""
echo "✅ Regras adicionadas ao pg_hba.conf"
echo ""
echo "📋 Regras de acesso remoto configuradas:"
sudo grep "meu_root" /etc/postgresql/14/main/pg_hba.conf

echo ""
echo "⚠️  ATENÇÃO: As conexões remotas foram configuradas para aceitar de QUALQUER IP (0.0.0.0/0)"
echo "    Para maior segurança, considere restringir a IPs específicos."
echo ""
echo "🔄 Para aplicar as mudanças, reinicie o PostgreSQL:"
echo "   sudo systemctl reload postgresql"

