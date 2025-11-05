#!/bin/bash
# Script de inicialização do MaraBet AI

echo "🚀 Iniciando MaraBet AI..."

# Verificar se Redis está rodando
echo "🔴 Verificando Redis..."
while ! redis-cli ping > /dev/null 2>&1; do
    echo "   Aguardando Redis..."
    sleep 2
done
echo "✅ Redis conectado"

# Verificar se banco de dados está acessível
echo "🗄️ Verificando banco de dados..."
python -c "import sqlite3; sqlite3.connect('mara_bet.db')"
echo "✅ Banco de dados acessível"

# Executar migrações se necessário
echo "📊 Executando migrações..."
python -c "from database import init_db; init_db()"
echo "✅ Migrações executadas"

# Iniciar aplicação
echo "🎉 Iniciando aplicação..."
exec python run_automated_collector.py
