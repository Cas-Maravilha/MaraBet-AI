#!/bin/bash
# Script para conectar como usuário postgres e executar psql

echo "🔄 Trocando para usuário postgres..."
echo ""

# Executar como usuário postgres
sudo su - postgres << 'EOF'

echo "✅ Conectado como usuário postgres"
echo "📊 Executando psql..."
echo ""

# Nota: O banco criado foi 'marabet', não 'meu_banco'
# Vou tentar ambos para ver qual existe

echo "Tentando conectar ao banco 'marabet':"
psql -U "meu_root\$marabet" -d marabet -h localhost -c "SELECT current_database(), current_user;"

echo ""
echo "---"
echo ""

echo "Tentando conectar ao banco 'meu_banco':"
psql -U "meu_root\$marabet" -d meu_banco -h localhost -c "SELECT current_database(), current_user;" 2>&1 || echo "❌ Banco 'meu_banco' não existe"

EOF

