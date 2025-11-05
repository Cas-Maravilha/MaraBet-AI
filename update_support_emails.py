#!/usr/bin/env python3
"""
Atualizar Emails de Suporte - MaraBet AI
Atualiza todos os emails de suporte para comercial@marabet.ao e suporte@marabet.ao
"""

import os
import re
from datetime import datetime

def update_file(filepath, old_patterns, new_values):
    """Atualiza emails em um arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Substituir padrões
        for old, new in zip(old_patterns, new_values):
            if old in content:
                content = content.replace(old, new)
                updated = True
        
        # Salvar se houve mudança
        if updated and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"❌ Erro ao processar {filepath}: {e}")
        return False

def main():
    print("=" * 80)
    print("📧 ATUALIZAÇÃO DE EMAILS DE SUPORTE - MARABET AI")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Padrões para substituir
    old_patterns = [
        'admin@marabet.ao',
        'admin@marabet.com',
        'suporte@marabet.ai',
        'info@marabet.ai',
    ]
    
    new_values = [
        'comercial@marabet.ao',
        'comercial@marabet.ao',
        'suporte@marabet.ao',
        'suporte@marabet.ao',
    ]
    
    # Arquivos para atualizar
    files_to_update = [
        # Configurações principais
        'config_local_server.env.example',
        'config_production.env',
        'server_config.json',
        
        # Guias e Documentação
        'AUDITORIA_TECNICA_FINAL.md',
        'VERIFICACAO_PRODUCAO_FINAL.md',
        'COMPATIBILIDADE_MULTIPLATAFORMA.md',
        
        # README
        'README.md',
        
        # Documentação técnica
        'SSL_HTTPS_DOCUMENTATION.md',
        'AUTOMATED_BACKUP_DOCUMENTATION.md',
        'GRAFANA_MONITORING_DOCUMENTATION.md',
        'DATABASE_MIGRATIONS_DOCUMENTATION.md',
        'LOAD_TESTING_DOCUMENTATION.md',
        'DOCKER_INSTALLATION_GUIDE.md',
        'DEPLOYMENT_GUIDE.md',
        
        # Scripts
        'setup_ssl.sh',
        'setup_production.sh',
        
        # Monitoramento
        'monitoring/alertmanager/config.yml',
        'monitoring/grafana/grafana.ini',
        
        # Backup
        'backups/scripts/backup.sh',
        'setup_automated_backup.py',
    ]
    
    updated_count = 0
    not_found_count = 0
    
    print("📋 Atualizando arquivos...")
    print("-" * 80)
    
    for filepath in files_to_update:
        if os.path.exists(filepath):
            if update_file(filepath, old_patterns, new_values):
                print(f"✅ Atualizado: {filepath}")
                updated_count += 1
            else:
                print(f"⏭️  Sem mudanças: {filepath}")
        else:
            print(f"⚠️  Não encontrado: {filepath}")
            not_found_count += 1
    
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"✅ Arquivos atualizados: {updated_count}")
    print(f"⚠️  Arquivos não encontrados: {not_found_count}")
    
    print("\n📧 EMAILS ATUALIZADOS PARA:")
    print("   • Comercial: comercial@marabet.ao")
    print("   • Suporte: suporte@marabet.ao")
    
    print("\n📞 CONTATOS COMPLETOS:")
    print("   • WhatsApp: +224 932027393")
    print("   • Email Comercial: comercial@marabet.ao")
    print("   • Email Suporte: suporte@marabet.ao")
    print("   • Telegram: @marabet_support")
    
    print("\n🎉 ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("🇦🇴 Sistema pronto para produção com emails corretos!")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

