#!/usr/bin/env python3
"""
Script para atualizar DATABASE_URL no arquivo .env
MaraBet AI - Atualização de credenciais
"""

import os
import re
from pathlib import Path

def atualizar_env():
    """Atualiza DATABASE_URL no arquivo .env"""
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        print("💡 Criando arquivo .env a partir de config_production.env...")
        
        config_file = Path("config_production.env")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Arquivo .env criado!")
        else:
            print("❌ Arquivo config_production.env também não encontrado")
            return False
    
    # Ler arquivo .env
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Senha antiga e nova
    senha_antiga = "ctcaddTcMaRVioDY4ksol"
    senha_nova = "ctcaddTcMaRVioDY4kso"
    
    # Verificar se precisa atualizar
    if senha_nova in content:
        print("✅ Arquivo .env já está atualizado com a senha correta")
        return True
    
    # Atualizar senha
    content_updated = content.replace(senha_antiga, senha_nova)
    
    # Verificar se houve mudança
    if content == content_updated:
        print("ℹ️  Nenhuma alteração necessária")
        return True
    
    # Fazer backup
    backup_file = Path(".env.backup")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_file}")
    
    # Escrever arquivo atualizado
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content_updated)
    
    print("✅ Arquivo .env atualizado!")
    print(f"   Senha antiga: {senha_antiga[:10]}...")
    print(f"   Senha nova: {senha_nova[:10]}...")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ATUALIZAÇÃO DO ARQUIVO .env")
    print("=" * 60)
    print()
    
    if atualizar_env():
        print("\n✅ Atualização concluída!")
        print("\n💡 Teste a conexão:")
        print("   python database_connection.py")
    else:
        print("\n❌ Erro na atualização")
        exit(1)

