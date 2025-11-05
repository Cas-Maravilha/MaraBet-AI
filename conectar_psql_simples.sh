#!/bin/bash
# Script simples para conectar ao PostgreSQL
# Como usuário postgres executando psql

echo "📊 Conectando como usuário postgres ao PostgreSQL..."
echo ""

# Como usuário postgres, conectar ao banco marabet
# (nota: o banco criado foi 'marabet', não 'meu_banco')
sudo -u postgres psql -U "meu_root\$marabet" -d marabet -h localhost "$@"

# Se quiser conectar interativamente, execute:
# sudo -u postgres psql -U "meu_root\$marabet" -d marabet -h localhost

