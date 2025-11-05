#!/usr/bin/env python3
"""
Script para verificar se todas as senhas estão atualizadas
MaraBet AI - Verificação de configuração
"""

import os
from pathlib import Path

senha_correta = "ctcaddTcMaRVioDY4kso"
senha_antiga = "ctcaddTcMaRVioDY4ksol"

print("=" * 60)
print("🔍 VERIFICAÇÃO DE SENHAS - MARABET AI")
print("=" * 60)
print()

# Arquivos para verificar
arquivos_verificar = [
    ".env",
    "config_production.env",
    "config_personal.env",
    "database_connection.py",
    "testar_conexao.py",
    "testar_conexao_detalhado.py",
    "testar_conexao_banco.py",
    "testar_conexao_interativo.py"
]

print("📋 Verificando arquivos de configuração...")
print()

erros = []
sucessos = []

for arquivo in arquivos_verificar:
    path = Path(arquivo)
    if not path.exists():
        continue
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if senha_antiga in content:
            erros.append(f"❌ {arquivo} - Contém senha antiga")
        elif senha_correta in content:
            sucessos.append(f"✅ {arquivo} - Senha correta")
        else:
            # Arquivo pode não ter senha (normal para alguns arquivos)
            pass
    except Exception as e:
        erros.append(f"⚠️  {arquivo} - Erro ao ler: {e}")

# Verificar módulo Python
try:
    from database_connection import db
    if db.config['password'] == senha_correta:
        sucessos.append("✅ database_connection.py (módulo) - Senha correta")
    else:
        erros.append(f"❌ database_connection.py (módulo) - Senha: {db.config['password']}")
except Exception as e:
    erros.append(f"⚠️  database_connection.py (módulo) - Erro: {e}")

# Resultados
print("✅ Arquivos com senha correta:")
for sucesso in sucessos:
    print(f"   {sucesso}")

print()
print("❌ Arquivos com problemas:")
for erro in erros:
    print(f"   {erro}")

print()
print("=" * 60)

if not erros:
    print("✅ TODAS AS SENHAS ESTÃO CORRETAS!")
else:
    print(f"⚠️  {len(erros)} arquivo(s) precisam de atualização")
    print()
    print("💡 Execute: python atualizar_env_forcado.py")

print("=" * 60)

