#!/usr/bin/env python3
"""
Script para atualizar FORÇADAMENTE DATABASE_URL no arquivo .env
MaraBet AI - Atualização de credenciais
"""

from pathlib import Path
import re

def atualizar_env_forcado():
    """Atualiza DATABASE_URL no arquivo .env forçadamente"""
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    # Ler arquivo .env
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Senha antiga e nova
    senha_antiga = "ctcaddTcMaRVioDY4ksol"
    senha_nova = "ctcaddTcMaRVioDY4kso"
    
    # Fazer backup
    backup_file = Path(".env.backup")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Backup criado: {backup_file}")
    
    # Atualizar linhas
    updated_lines = []
    for line in lines:
        if "DATABASE_URL" in line:
            # Substituir senha antiga pela nova
            if senha_antiga in line:
                line = line.replace(senha_antiga, senha_nova)
                print(f"📝 Linha atualizada: {line.strip()}")
            elif senha_nova in line:
                print(f"✅ Linha já está correta: {line.strip()}")
        updated_lines.append(line)
    
    # Escrever arquivo atualizado
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("✅ Arquivo .env atualizado!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ATUALIZAÇÃO FORÇADA DO ARQUIVO .env")
    print("=" * 60)
    print()
    
    if atualizar_env_forcado():
        print("\n✅ Atualização concluída!")
        print("\n💡 Verificando atualização...")
        
        # Verificar
        with open(".env", 'r', encoding='utf-8') as f:
            content = f.read()
            if "ctcaddTcMaRVioDY4kso" in content:
                print("✅ Senha correta encontrada no .env")
            if "ctcaddTcMaRVioDY4ksol" in content:
                print("⚠️  Senha antiga ainda encontrada no .env")
        
        print("\n💡 Teste a conexão:")
        print("   python testar_conexao.py")
    else:
        print("\n❌ Erro na atualização")
        exit(1)

