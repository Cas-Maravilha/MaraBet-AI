#!/usr/bin/env python3
"""
Script de backup do PostgreSQL para MaraBet AI
Cria backups automáticos e programados do banco de dados
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import schedule
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLBackup:
    """Gerenciador de backup do PostgreSQL"""
    
    def __init__(self, postgres_url: str, backup_dir: str = "./backups"):
        """
        Inicializa o gerenciador de backup
        
        Args:
            postgres_url: URL de conexão do PostgreSQL
            backup_dir: Diretório para armazenar backups
        """
        self.postgres_url = postgres_url
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def test_connection(self) -> bool:
        """Testa a conexão com o PostgreSQL"""
        try:
            conn = psycopg2.connect(self.postgres_url)
            conn.close()
            logger.info("✅ Conexão com PostgreSQL estabelecida")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com PostgreSQL: {e}")
            return False
    
    def create_backup(self, backup_name: str = None) -> str:
        """
        Cria backup do banco de dados
        
        Args:
            backup_name: Nome do arquivo de backup (opcional)
            
        Returns:
            Caminho do arquivo de backup criado
        """
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"marabet_ai_backup_{timestamp}.sql"
            
            backup_path = self.backup_dir / backup_name
            
            # Extrair informações de conexão da URL
            # postgresql://user:password@host:port/database
            url_parts = self.postgres_url.replace("postgresql://", "").split("/")
            db_name = url_parts[1]
            auth_parts = url_parts[0].split("@")
            user_pass = auth_parts[0].split(":")
            host_port = auth_parts[1].split(":")
            
            username = user_pass[0]
            password = user_pass[1]
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
            
            # Comando pg_dump
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={username}",
                f"--dbname={db_name}",
                "--verbose",
                "--clean",
                "--no-owner",
                "--no-privileges",
                "--format=custom",
                f"--file={backup_path}"
            ]
            
            # Definir senha como variável de ambiente
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            logger.info(f"🔄 Criando backup: {backup_name}")
            
            # Executar pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verificar se o arquivo foi criado
                if backup_path.exists():
                    file_size = backup_path.stat().st_size
                    logger.info(f"✅ Backup criado com sucesso: {backup_path} ({file_size:,} bytes)")
                    return str(backup_path)
                else:
                    logger.error("❌ Arquivo de backup não foi criado")
                    return None
            else:
                logger.error(f"❌ Erro ao criar backup: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restaura backup do banco de dados
        
        Args:
            backup_path: Caminho para o arquivo de backup
            
        Returns:
            True se a restauração foi bem-sucedida
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"❌ Arquivo de backup não encontrado: {backup_path}")
                return False
            
            # Extrair informações de conexão da URL
            url_parts = self.postgres_url.replace("postgresql://", "").split("/")
            db_name = url_parts[1]
            auth_parts = url_parts[0].split("@")
            user_pass = auth_parts[0].split(":")
            host_port = auth_parts[1].split(":")
            
            username = user_pass[0]
            password = user_pass[1]
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
            
            # Comando pg_restore
            cmd = [
                "pg_restore",
                f"--host={host}",
                f"--port={port}",
                f"--username={username}",
                f"--dbname={db_name}",
                "--verbose",
                "--clean",
                "--no-owner",
                "--no-privileges",
                backup_path
            ]
            
            # Definir senha como variável de ambiente
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            logger.info(f"🔄 Restaurando backup: {backup_path}")
            
            # Executar pg_restore
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Backup restaurado com sucesso")
                return True
            else:
                logger.error(f"❌ Erro ao restaurar backup: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def list_backups(self) -> list:
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            for file_path in self.backup_dir.glob("marabet_ai_backup_*.sql"):
                stat = file_path.stat()
                backups.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
            
            # Ordenar por data de criação (mais recente primeiro)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar backups: {e}")
            return []
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """
        Remove backups antigos
        
        Args:
            days_to_keep: Número de dias para manter backups
            
        Returns:
            Número de backups removidos
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            for file_path in self.backup_dir.glob("marabet_ai_backup_*.sql"):
                file_date = datetime.fromtimestamp(file_path.stat().st_ctime)
                
                if file_date < cutoff_date:
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"🗑️ Backup antigo removido: {file_path.name}")
            
            logger.info(f"✅ {removed_count} backups antigos removidos")
            return removed_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar backups antigos: {e}")
            return 0
    
    def get_backup_info(self, backup_path: str) -> dict:
        """
        Obtém informações sobre um backup
        
        Args:
            backup_path: Caminho para o arquivo de backup
            
        Returns:
            Dicionário com informações do backup
        """
        try:
            if not os.path.exists(backup_path):
                return None
            
            stat = os.stat(backup_path)
            
            # Comando pg_restore --list para obter informações do backup
            cmd = ["pg_restore", "--list", backup_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            info = {
                'path': backup_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'tables': [],
                'functions': [],
                'triggers': []
            }
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'TABLE' in line:
                        info['tables'].append(line.strip())
                    elif 'FUNCTION' in line:
                        info['functions'].append(line.strip())
                    elif 'TRIGGER' in line:
                        info['triggers'].append(line.strip())
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações do backup: {e}")
            return None
    
    def schedule_backup(self, time_str: str = "02:00", days_to_keep: int = 30):
        """
        Agenda backup automático
        
        Args:
            time_str: Horário para executar backup (formato HH:MM)
            days_to_keep: Número de dias para manter backups
        """
        def backup_job():
            logger.info("🕐 Executando backup agendado")
            backup_path = self.create_backup()
            if backup_path:
                self.cleanup_old_backups(days_to_keep)
        
        schedule.every().day.at(time_str).do(backup_job)
        
        logger.info(f"📅 Backup agendado para {time_str} todos os dias")
        logger.info(f"🗑️ Backups antigos serão removidos após {days_to_keep} dias")
        
        # Executar em loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Backup do PostgreSQL para MaraBet AI")
    parser.add_argument("--postgres-url", required=True, help="URL de conexão do PostgreSQL")
    parser.add_argument("--backup-dir", default="./backups", help="Diretório para backups")
    parser.add_argument("--create", action="store_true", help="Criar backup")
    parser.add_argument("--restore", help="Restaurar backup (caminho do arquivo)")
    parser.add_argument("--list", action="store_true", help="Listar backups")
    parser.add_argument("--cleanup", type=int, help="Limpar backups antigos (dias)")
    parser.add_argument("--info", help="Informações sobre backup (caminho do arquivo)")
    parser.add_argument("--schedule", help="Agendar backup (horário HH:MM)")
    parser.add_argument("--days-to-keep", type=int, default=30, help="Dias para manter backups")
    
    args = parser.parse_args()
    
    backup_manager = PostgreSQLBackup(args.postgres_url, args.backup_dir)
    
    # Testar conexão
    if not backup_manager.test_connection():
        sys.exit(1)
    
    if args.create:
        backup_path = backup_manager.create_backup()
        if backup_path:
            logger.info(f"✅ Backup criado: {backup_path}")
        else:
            logger.error("❌ Falha ao criar backup")
            sys.exit(1)
    
    elif args.restore:
        if backup_manager.restore_backup(args.restore):
            logger.info("✅ Backup restaurado com sucesso")
        else:
            logger.error("❌ Falha ao restaurar backup")
            sys.exit(1)
    
    elif args.list:
        backups = backup_manager.list_backups()
        if backups:
            print("\n📋 Backups disponíveis:")
            print("-" * 80)
            for backup in backups:
                print(f"📁 {backup['name']}")
                print(f"   Tamanho: {backup['size']:,} bytes")
                print(f"   Criado: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Modificado: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("📭 Nenhum backup encontrado")
    
    elif args.cleanup:
        removed = backup_manager.cleanup_old_backups(args.cleanup)
        logger.info(f"🗑️ {removed} backups antigos removidos")
    
    elif args.info:
        info = backup_manager.get_backup_info(args.info)
        if info:
            print(f"\n📊 Informações do backup: {args.info}")
            print("-" * 50)
            print(f"Tamanho: {info['size']:,} bytes")
            print(f"Criado: {info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Modificado: {info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Tabelas: {len(info['tables'])}")
            print(f"Funções: {len(info['functions'])}")
            print(f"Triggers: {len(info['triggers'])}")
        else:
            logger.error("❌ Não foi possível obter informações do backup")
            sys.exit(1)
    
    elif args.schedule:
        backup_manager.schedule_backup(args.schedule, args.days_to_keep)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
