#!/bin/bash
# Script para completar pg_hba.conf com scram-sha-256
# MaraBet AI - Completar linha incompleta no pg_hba.conf

echo "============================================================"
echo "🔧 COMPLETAR PG_HBA.CONF COM SCRAM-SHA-256"
echo "============================================================"
echo ""

# Verificar se está executando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script precisa ser executado como root ou com sudo"
    echo "   Execute: sudo bash completar_pg_hba_scram.sh"
    exit 1
fi

# Localizar arquivo pg_hba.conf
PG_HBA_FILE=$(find /etc -name pg_hba.conf 2>/dev/null | head -1)

if [ -z "$PG_HBA_FILE" ]; then
    echo "❌ Arquivo pg_hba.conf não encontrado"
    echo "   Verifique se PostgreSQL está instalado"
    exit 1
fi

echo "📋 Arquivo encontrado: $PG_HBA_FILE"
echo ""

# Fazer backup
BACKUP_FILE="${PG_HBA_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PG_HBA_FILE" "$BACKUP_FILE"
echo "✅ Backup criado: $BACKUP_FILE"
echo ""

# Verificar se há linha incompleta
if grep -qE "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario[[:space:]]+0\.0\.0\.0/0[[:space:]]*$" "$PG_HBA_FILE"; then
    echo "⚠️  Linha incompleta encontrada (sem método de autenticação)"
    echo ""
    echo "Linha atual:"
    grep -E "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario" "$PG_HBA_FILE"
    echo ""
    
    # Remover linha incompleta
    sed -i '/^host[[:space:]]*meu_banco[[:space:]]*meu_usuario[[:space:]]*0\.0\.0\.0\/0[[:space:]]*$/d' "$PG_HBA_FILE"
    
    # Verificar se linha completa já existe
    if grep -qE "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario[[:space:]]+0\.0\.0\.0/0[[:space:]]+scram-sha-256" "$PG_HBA_FILE"; then
        echo "✅ Linha completa já existe"
    else
        # Adicionar linha completa
        echo "# Conexões remotas para meu_usuario - MaraBet AI" >> "$PG_HBA_FILE"
        echo "host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256" >> "$PG_HBA_FILE"
        echo "✅ Linha completada e adicionada"
    fi
    
elif grep -qE "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario[[:space:]]+0\.0\.0\.0/0[[:space:]]+scram-sha-256" "$PG_HBA_FILE"; then
    echo "✅ Linha já existe e está completa"
    echo ""
    echo "Linha encontrada:"
    grep -E "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario" "$PG_HBA_FILE"
    
elif grep -qE "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario" "$PG_HBA_FILE"; then
    echo "⚠️  Linha encontrada mas com método diferente"
    echo ""
    echo "Linha atual:"
    grep -E "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario" "$PG_HBA_FILE"
    echo ""
    read -p "Deseja substituir por scram-sha-256? (s/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        # Remover linha antiga
        sed -i '/^host[[:space:]]*meu_banco[[:space:]]*meu_usuario/d' "$PG_HBA_FILE"
        # Adicionar linha nova
        echo "# Conexões remotas para meu_usuario - MaraBet AI" >> "$PG_HBA_FILE"
        echo "host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256" >> "$PG_HBA_FILE"
        echo "✅ Linha substituída"
    else
        echo "❌ Operação cancelada"
        exit 0
    fi
else
    echo "ℹ️  Linha não encontrada, adicionando..."
    echo "# Conexões remotas para meu_usuario - MaraBet AI" >> "$PG_HBA_FILE"
    echo "host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256" >> "$PG_HBA_FILE"
    echo "✅ Linha adicionada"
fi

echo ""
echo "📋 Configuração final:"
grep -E "^host[[:space:]]+meu_banco[[:space:]]+meu_usuario" "$PG_HBA_FILE" || echo "⚠️  Linha não encontrada"

echo ""
echo "🔄 Reiniciando PostgreSQL..."
systemctl restart postgresql
sleep 2

# Verificar se está rodando
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL reiniciado com sucesso"
else
    echo "❌ Erro ao reiniciar PostgreSQL"
    echo "   Verifique logs: sudo tail -f /var/log/postgresql/postgresql-*.log"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "============================================================"
echo ""
echo "📋 Linha configurada:"
echo "   host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256"
echo ""
echo "💡 IMPORTANTE: Verifique se a senha do usuário está correta:"
echo "   sudo -u postgres psql"
echo "   ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';"
echo ""
echo "📋 Próximos passos:"
echo "   1. Verificar senha do usuário no PostgreSQL"
echo "   2. Testar conexão localmente:"
echo "      psql -h localhost -U meu_usuario -d meu_banco"
echo ""
echo "   3. Testar conexão remotamente:"
echo "      python testar_conexao.py"
echo ""
echo "============================================================"

