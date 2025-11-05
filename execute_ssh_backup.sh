#!/bin/bash
# Script para executar comandos SSH - MaraBet AI

echo "🚀 MARABET AI - EXECUTANDO CONFIGURAÇÃO DE BACKUP VIA SSH"
echo "========================================================"

# Configurações
SERVER_IP="3.218.152.100"
KEY_PATH="C:\Users\PC/.ssh/marabet-key.pem"
COMMANDS_FILE="ssh_backup_commands.sh"

echo "📡 Conectando ao servidor: $SERVER_IP"
echo "🔑 Usando chave: $KEY_PATH"

# Executar comandos SSH
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ubuntu@$SERVER_IP 'bash -s' < $COMMANDS_FILE

if [ $? -eq 0 ]; then
    echo "✅ Configuração de backup executada com sucesso"
else
    echo "❌ Falha na execução da configuração de backup"
fi

echo "🎉 CONFIGURAÇÃO VIA SSH CONCLUÍDA!"
