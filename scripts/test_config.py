#!/usr/bin/env python3
"""
Teste de Configurações - MaraBet AI
Verifica se as configurações estão funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings, validate_settings
from config.api_keys import api_keys_manager

def test_settings():
    """Testa as configurações do sistema"""
    print("🔧 Testando Configurações - MaraBet AI")
    print("=" * 50)
    
    # Testar configurações básicas
    print(f"📱 Aplicação: {settings.app_name} v{settings.app_version}")
    print(f"🌐 Servidor: {settings.host}:{settings.port}")
    print(f"🔧 Debug: {settings.debug}")
    print(f"📊 Workers: {settings.workers}")
    print()
    
    # Testar banco de dados
    print("🗄️ Banco de Dados:")
    print(f"   URL: {settings.database_connection_string}")
    print(f"   Redis: {settings.redis_url}")
    print()
    
    # Testar APIs
    print("🔑 APIs Externas:")
    print(f"   API-Football: {'✅' if settings.api_football_key else '❌'}")
    print(f"   The Odds API: {'✅' if settings.odds_api_key else '❌'}")
    print()
    
    # Testar configurações de coleta
    print("📡 Configurações de Coleta:")
    print(f"   Intervalo: {settings.collection_interval}s")
    print(f"   Requests simultâneos: {settings.max_concurrent_requests}")
    print(f"   Timeout: {settings.request_timeout}s")
    print(f"   Retries: {settings.max_retries}")
    print(f"   Ligas monitoradas: {settings.monitored_leagues_list}")
    print()
    
    # Testar configurações de análise
    print("📊 Configurações de Análise:")
    print(f"   Confiança mínima: {settings.min_confidence}")
    print(f"   Confiança máxima: {settings.max_confidence}")
    print(f"   EV mínimo: {settings.min_value_ev}")
    print(f"   Kelly Fraction: {settings.kelly_fraction}")
    print()
    
    # Testar configurações de segurança
    print("🔒 Configurações de Segurança:")
    print(f"   CORS Origins: {settings.cors_origins_list}")
    print(f"   Hosts permitidos: {settings.allowed_hosts_list}")
    print(f"   JWT Algorithm: {settings.jwt_algorithm}")
    print(f"   JWT Expire: {settings.jwt_expire_minutes}min")
    print()
    
    # Testar configurações de logs
    print("📝 Configurações de Logs:")
    print(f"   Nível: {settings.log_level}")
    print(f"   Arquivo: {settings.log_file}")
    print(f"   Tamanho máximo: {settings.log_max_bytes} bytes")
    print(f"   Backup count: {settings.log_backup_count}")
    print()
    
    # Testar configurações de backup
    print("💾 Configurações de Backup:")
    print(f"   Habilitado: {settings.backup_enabled}")
    print(f"   Intervalo: {settings.backup_interval}s")
    print(f"   Retenção: {settings.backup_retention_days} dias")
    print(f"   Caminho: {settings.backup_path}")
    print()
    
    # Testar configurações angolanas
    print("🇦🇴 Configurações Angolanas:")
    print(f"   Moeda: {settings.currency}")
    print(f"   Fuso horário: {settings.timezone}")
    print(f"   Idioma: {settings.language}")
    print(f"   Casas de apostas: {settings.supported_bookmakers}")
    print()
    
    # Testar validação
    print("✅ Validação das Configurações:")
    if validate_settings():
        print("   Configurações válidas!")
    else:
        print("   ⚠️ Problemas encontrados nas configurações")
    
    print()
    
    # Testar gerenciador de chaves de API
    print("🔑 Status das Chaves de API:")
    api_keys_manager.print_status()
    
    return True

def main():
    """Função principal"""
    try:
        test_settings()
        print("🎉 Teste de configurações concluído com sucesso!")
        return 0
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
