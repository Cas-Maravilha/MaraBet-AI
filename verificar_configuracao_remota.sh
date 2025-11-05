#!/bin/bash
# Script para verificar configuração de acesso remoto

echo "📋 Verificando configuração de acesso remoto ao PostgreSQL..."
echo ""

echo "1️⃣ Arquivo postgresql.conf - listen_addresses:"
sudo grep "^listen_addresses" /etc/postgresql/14/main/postgresql.conf

echo ""
echo "2️⃣ Arquivo pg_hba.conf - Regras de autenticação:"
echo "   (Mostrando apenas linhas não comentadas)"
sudo grep -v '^#' /etc/postgresql/14/main/pg_hba.conf | grep -v '^$' | head -10

echo ""
echo "3️⃣ Porta do PostgreSQL (deve estar escutando em todas as interfaces):"
sudo ss -tlnp | grep 5432

echo ""
echo "⚠️  IMPORTANTE: Para permitir conexões remotas, você também precisa:"
echo "   1. Configurar regras no pg_hba.conf para permitir conexões remotas"
echo "   2. Configurar o firewall para permitir conexões na porta 5432"
echo "   3. Usar autenticação segura (md5 ou scram-sha-256)"

