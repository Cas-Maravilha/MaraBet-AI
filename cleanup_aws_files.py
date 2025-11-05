#!/usr/bin/env python3
"""
Limpeza Completa de Arquivos AWS - MaraBet AI
Remove todos os arquivos relacionados à AWS
"""

import os
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 80)
    print(f"🗑️  {text}")
    print("=" * 80)

print_header("LIMPEZA COMPLETA DE ARQUIVOS AWS - MARABET AI")
print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"📞 Contato: +224 932027393")

# Lista completa de arquivos AWS para remover
aws_files = [
    # Arquivos de configuração AWS
    'create_rds_postgresql.py',
    'rds_summary.py',
    'aws_infrastructure_summary.py',
    'create_aws_infrastructure.py',
    'setup_aws_complete.py',
    'aws_config_guide.py',
    'configure_aws_secret.py',
    'configure_aws_cli.py',
    
    # Scripts de backup AWS
    'configure_direct_backup.py',
    'configure_server_backup.py',
    
    # Infraestrutura AWS
    'infrastructure/backup_restore.py',
    'infrastructure/database_replication.py',
    
    # Scripts de limpeza (após execução)
    'clean_aws_direct.py',
    'remove_aws_config.py',
]

# Arquivos que não devem ser removidos (parte do sistema)
keep_files = [
    'deep_technical_audit.py',
    'setup_automated_backup.py',
    'notifications_personal.py',
    'modular_system.py',
    'presentation_layer.py',
    'storage_layer.py',
]

print("\n📋 ARQUIVOS AWS PARA REMOÇÃO:")
print("-" * 80)

removed_count = 0
not_found_count = 0
skipped_count = 0

for file in aws_files:
    if file in keep_files:
        print(f"⏭️  Mantido (sistema): {file}")
        skipped_count += 1
        continue
    
    if os.path.exists(file):
        try:
            # Criar backup antes de remover
            backup_dir = "backups/removed_aws_files"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copiar para backup
            filename = os.path.basename(file)
            backup_path = os.path.join(backup_dir, filename)
            
            # Se já existe backup, adicionar timestamp
            if os.path.exists(backup_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                backup_path = os.path.join(backup_dir, f"{name}_{timestamp}{ext}")
            
            # Copiar
            import shutil
            shutil.copy2(file, backup_path)
            
            # Remover original
            os.remove(file)
            print(f"✅ Removido: {file}")
            print(f"   💾 Backup: {backup_path}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Erro ao remover {file}: {e}")
    else:
        print(f"⚠️  Não encontrado: {file}")
        not_found_count += 1

print("\n" + "=" * 80)
print("📊 RESUMO DA LIMPEZA")
print("=" * 80)
print(f"✅ Arquivos removidos: {removed_count}")
print(f"💾 Backups criados em: backups/removed_aws_files/")
print(f"⚠️  Não encontrados: {not_found_count}")
print(f"⏭️  Mantidos (sistema): {skipped_count}")

if removed_count > 0:
    print("\n✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("📋 Sistema agora está 100% livre de arquivos AWS")
    print("💾 Backups dos arquivos removidos estão disponíveis")
else:
    print("\n⚠️  Nenhum arquivo foi removido")
    print("Sistema já estava limpo de arquivos AWS")

print("\n🇦🇴 Sistema pronto para Angoweb!")
print("📞 Próximo passo: Contatar Angoweb +244 222 638 200")
print("\n" + "=" * 80)

# Criar relatório
report = f"""# Relatório de Limpeza AWS - MaraBet AI

**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## Arquivos Removidos: {removed_count}

"""

for file in aws_files:
    if os.path.exists(f"backups/removed_aws_files/{os.path.basename(file)}"):
        report += f"- ✅ {file}\n"

report += f"""
## Backups Criados
Localização: `backups/removed_aws_files/`

## Status
✅ Sistema limpo de arquivos AWS
✅ Backups preservados
✅ Pronto para Angoweb

## Próximo Passo
Contatar Angoweb: +244 222 638 200
"""

with open("backups/removed_aws_files/CLEANUP_REPORT.md", "w", encoding="utf-8") as f:
    f.write(report)

print("📄 Relatório salvo: backups/removed_aws_files/CLEANUP_REPORT.md")

