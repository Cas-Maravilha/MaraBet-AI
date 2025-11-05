#!/usr/bin/env python3
"""
Script CLI para Gerenciamento de Secrets - MaraBet AI
Interface de linha de comando para gerenciar chaves de API e credenciais
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secrets import SecretsManager, KeyRotator, SecretsValidator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_secrets_manager(backend: str = "local") -> SecretsManager:
    """Configura o gerenciador de secrets"""
    try:
        # Verificar se master key está definida
        master_key = os.getenv('MARABET_MASTER_KEY')
        if not master_key:
            print("❌ Variável MARABET_MASTER_KEY não definida")
            print("Defina com: export MARABET_MASTER_KEY='sua_chave_mestra_aqui'")
            sys.exit(1)
        
        return SecretsManager(backend=backend, master_key=master_key)
    except Exception as e:
        logger.error(f"❌ Erro ao configurar gerenciador de secrets: {e}")
        sys.exit(1)

def cmd_set_secret(secrets_manager: SecretsManager, key: str, value: str, metadata: str = None):
    """Define um secret"""
    try:
        meta = None
        if metadata:
            import json
            meta = json.loads(metadata)
        
        if secrets_manager.set_secret(key, value, meta):
            print(f"✅ Secret '{key}' definido com sucesso")
        else:
            print(f"❌ Erro ao definir secret '{key}'")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao definir secret: {e}")
        sys.exit(1)

def cmd_get_secret(secrets_manager: SecretsManager, key: str, show_value: bool = True):
    """Obtém um secret"""
    try:
        value = secrets_manager.get_secret(key)
        if value:
            if show_value:
                print(f"🔑 {key}: {value}")
            else:
                print(f"🔑 {key}: {'*' * len(value)}")
        else:
            print(f"❌ Secret '{key}' não encontrado")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao obter secret: {e}")
        sys.exit(1)

def cmd_delete_secret(secrets_manager: SecretsManager, key: str):
    """Remove um secret"""
    try:
        if secrets_manager.delete_secret(key):
            print(f"✅ Secret '{key}' removido com sucesso")
        else:
            print(f"❌ Erro ao remover secret '{key}'")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao remover secret: {e}")
        sys.exit(1)

def cmd_list_secrets(secrets_manager: SecretsManager):
    """Lista todos os secrets"""
    try:
        secrets = secrets_manager.list_secrets()
        if secrets:
            print(f"📋 {len(secrets)} secrets encontrados:")
            for secret in sorted(secrets):
                print(f"  🔑 {secret}")
        else:
            print("📭 Nenhum secret encontrado")
    except Exception as e:
        logger.error(f"❌ Erro ao listar secrets: {e}")
        sys.exit(1)

def cmd_set_api_key(secrets_manager: SecretsManager, service: str, api_key: str):
    """Define chave de API para um serviço"""
    try:
        if secrets_manager.set_api_key(service, api_key):
            print(f"✅ Chave de API para '{service}' definida com sucesso")
        else:
            print(f"❌ Erro ao definir chave de API para '{service}'")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao definir chave de API: {e}")
        sys.exit(1)

def cmd_get_api_key(secrets_manager: SecretsManager, service: str):
    """Obtém chave de API para um serviço"""
    try:
        api_key = secrets_manager.get_api_key(service)
        if api_key:
            print(f"🔑 {service}: {api_key}")
        else:
            print(f"❌ Chave de API para '{service}' não encontrada")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao obter chave de API: {e}")
        sys.exit(1)

def cmd_set_database_credentials(secrets_manager: SecretsManager, credentials: dict):
    """Define credenciais do banco de dados"""
    try:
        if secrets_manager.set_database_credentials(credentials):
            print("✅ Credenciais do banco de dados definidas com sucesso")
        else:
            print("❌ Erro ao definir credenciais do banco de dados")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao definir credenciais do banco: {e}")
        sys.exit(1)

def cmd_validate_secrets(secrets_manager: SecretsManager):
    """Valida todos os secrets"""
    try:
        validator = SecretsValidator()
        results = validator.validate_all_secrets(secrets_manager)
        
        if results:
            print("🔍 Resultados da validação:")
            for key, result in results.items():
                status = "✅" if result['valid'] else "❌"
                print(f"  {status} {key}: {result['message']}")
            
            # Resumo
            summary = validator.get_validation_summary()
            print(f"\n📊 Resumo: {summary['valid_secrets']}/{summary['total_secrets']} secrets válidos ({summary['validation_rate']}%)")
        else:
            print("❌ Nenhum secret encontrado para validação")
    except Exception as e:
        logger.error(f"❌ Erro ao validar secrets: {e}")
        sys.exit(1)

def cmd_export_secrets(secrets_manager: SecretsManager, output_file: str):
    """Exporta todos os secrets"""
    try:
        if secrets_manager.export_secrets(output_file):
            print(f"✅ Secrets exportados para {output_file}")
        else:
            print("❌ Erro ao exportar secrets")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao exportar secrets: {e}")
        sys.exit(1)

def cmd_import_secrets(secrets_manager: SecretsManager, input_file: str):
    """Importa secrets de arquivo"""
    try:
        if secrets_manager.import_secrets(input_file):
            print(f"✅ Secrets importados de {input_file}")
        else:
            print("❌ Erro ao importar secrets")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao importar secrets: {e}")
        sys.exit(1)

def cmd_rotation_status(secrets_manager: SecretsManager):
    """Mostra status do sistema de rotação"""
    try:
        rotator = KeyRotator(secrets_manager)
        status = rotator.get_rotation_status()
        
        print("🔄 Status do Sistema de Rotação:")
        print(f"  Total de chaves: {status['total_keys']}")
        print(f"  Rotação automática: {status['auto_rotate_keys']}")
        print(f"  Chaves para rotacionar: {status['keys_to_rotate']}")
        print(f"  Avisos: {status['warnings']}")
        print(f"  Executando: {'Sim' if status['running'] else 'Não'}")
        print(f"  Última verificação: {status['last_check']}")
    except Exception as e:
        logger.error(f"❌ Erro ao obter status de rotação: {e}")
        sys.exit(1)

def cmd_add_rotation(secrets_manager: SecretsManager, key_name: str, interval_days: int, warning_days: int):
    """Adiciona chave ao sistema de rotação"""
    try:
        rotator = KeyRotator(secrets_manager)
        if rotator.add_key_rotation(key_name, interval_days, warning_days):
            print(f"✅ Chave '{key_name}' adicionada ao sistema de rotação")
        else:
            print(f"❌ Erro ao adicionar chave '{key_name}' à rotação")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar rotação: {e}")
        sys.exit(1)

def cmd_rotate_key(secrets_manager: SecretsManager, key_name: str, new_value: str = None):
    """Rotaciona uma chave específica"""
    try:
        rotator = KeyRotator(secrets_manager)
        if rotator.rotate_key(key_name, new_value):
            print(f"✅ Chave '{key_name}' rotacionada com sucesso")
        else:
            print(f"❌ Erro ao rotacionar chave '{key_name}'")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro ao rotacionar chave: {e}")
        sys.exit(1)

def cmd_start_rotation(secrets_manager: SecretsManager):
    """Inicia rotação automática"""
    try:
        rotator = KeyRotator(secrets_manager)
        rotator.start_auto_rotation()
        print("✅ Rotação automática iniciada")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar rotação automática: {e}")
        sys.exit(1)

def cmd_stop_rotation(secrets_manager: SecretsManager):
    """Para rotação automática"""
    try:
        rotator = KeyRotator(secrets_manager)
        rotator.stop_auto_rotation()
        print("✅ Rotação automática parada")
    except Exception as e:
        logger.error(f"❌ Erro ao parar rotação automática: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Gerenciador de Secrets - MaraBet AI")
    parser.add_argument("--backend", choices=["local", "vault", "aws"], default="local", 
                       help="Backend para armazenamento de secrets")
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando: set
    set_parser = subparsers.add_parser("set", help="Define um secret")
    set_parser.add_argument("key", help="Chave do secret")
    set_parser.add_argument("value", help="Valor do secret")
    set_parser.add_argument("--metadata", help="Metadados em JSON")
    
    # Comando: get
    get_parser = subparsers.add_parser("get", help="Obtém um secret")
    get_parser.add_argument("key", help="Chave do secret")
    get_parser.add_argument("--hide", action="store_true", help="Ocultar valor")
    
    # Comando: delete
    delete_parser = subparsers.add_parser("delete", help="Remove um secret")
    delete_parser.add_argument("key", help="Chave do secret")
    
    # Comando: list
    subparsers.add_parser("list", help="Lista todos os secrets")
    
    # Comando: set-api-key
    api_parser = subparsers.add_parser("set-api-key", help="Define chave de API")
    api_parser.add_argument("service", help="Nome do serviço")
    api_parser.add_argument("api_key", help="Chave de API")
    
    # Comando: get-api-key
    get_api_parser = subparsers.add_parser("get-api-key", help="Obtém chave de API")
    get_api_parser.add_argument("service", help="Nome do serviço")
    
    # Comando: set-db-credentials
    db_parser = subparsers.add_parser("set-db-credentials", help="Define credenciais do banco")
    db_parser.add_argument("--host", required=True, help="Host do banco")
    db_parser.add_argument("--port", required=True, help="Porta do banco")
    db_parser.add_argument("--database", required=True, help="Nome do banco")
    db_parser.add_argument("--username", required=True, help="Usuário do banco")
    db_parser.add_argument("--password", required=True, help="Senha do banco")
    
    # Comando: validate
    subparsers.add_parser("validate", help="Valida todos os secrets")
    
    # Comando: export
    export_parser = subparsers.add_parser("export", help="Exporta secrets")
    export_parser.add_argument("output_file", help="Arquivo de saída")
    
    # Comando: import
    import_parser = subparsers.add_parser("import", help="Importa secrets")
    import_parser.add_argument("input_file", help="Arquivo de entrada")
    
    # Comando: rotation-status
    subparsers.add_parser("rotation-status", help="Status do sistema de rotação")
    
    # Comando: add-rotation
    rotation_parser = subparsers.add_parser("add-rotation", help="Adiciona chave à rotação")
    rotation_parser.add_argument("key_name", help="Nome da chave")
    rotation_parser.add_argument("--interval-days", type=int, default=90, help="Intervalo em dias")
    rotation_parser.add_argument("--warning-days", type=int, default=7, help="Dias de aviso")
    
    # Comando: rotate
    rotate_parser = subparsers.add_parser("rotate", help="Rotaciona uma chave")
    rotate_parser.add_argument("key_name", help="Nome da chave")
    rotate_parser.add_argument("--new-value", help="Novo valor (opcional)")
    
    # Comando: start-rotation
    subparsers.add_parser("start-rotation", help="Inicia rotação automática")
    
    # Comando: stop-rotation
    subparsers.add_parser("stop-rotation", help="Para rotação automática")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Configurar gerenciador de secrets
    secrets_manager = setup_secrets_manager(args.backend)
    
    # Executar comando
    try:
        if args.command == "set":
            cmd_set_secret(secrets_manager, args.key, args.value, args.metadata)
        elif args.command == "get":
            cmd_get_secret(secrets_manager, args.key, not args.hide)
        elif args.command == "delete":
            cmd_delete_secret(secrets_manager, args.key)
        elif args.command == "list":
            cmd_list_secrets(secrets_manager)
        elif args.command == "set-api-key":
            cmd_set_api_key(secrets_manager, args.service, args.api_key)
        elif args.command == "get-api-key":
            cmd_get_api_key(secrets_manager, args.service)
        elif args.command == "set-db-credentials":
            credentials = {
                'host': args.host,
                'port': args.port,
                'database': args.database,
                'username': args.username,
                'password': args.password
            }
            cmd_set_database_credentials(secrets_manager, credentials)
        elif args.command == "validate":
            cmd_validate_secrets(secrets_manager)
        elif args.command == "export":
            cmd_export_secrets(secrets_manager, args.output_file)
        elif args.command == "import":
            cmd_import_secrets(secrets_manager, args.input_file)
        elif args.command == "rotation-status":
            cmd_rotation_status(secrets_manager)
        elif args.command == "add-rotation":
            cmd_add_rotation(secrets_manager, args.key_name, args.interval_days, args.warning_days)
        elif args.command == "rotate":
            cmd_rotate_key(secrets_manager, args.key_name, args.new_value)
        elif args.command == "start-rotation":
            cmd_start_rotation(secrets_manager)
        elif args.command == "stop-rotation":
            cmd_stop_rotation(secrets_manager)
        else:
            print(f"❌ Comando desconhecido: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
