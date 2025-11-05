#!/usr/bin/env python3
"""
Sistema de Backup para o MaraBet AI
Backup automático e validado de dados críticos
"""

import os
import shutil
import sqlite3
import json
import gzip
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import schedule
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BackupInfo:
    """Informações do backup"""
    backup_id: str
    timestamp: datetime
    backup_type: str
    size_bytes: int
    checksum: str
    status: str
    files: List[str]
    database_backup: bool
    models_backup: bool
    config_backup: bool

class BackupManager:
    """Gerenciador de backups"""
    
    def __init__(self, backup_dir: str = "backups"):
        """Inicializa gerenciador de backups"""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.max_backups = 30  # Manter últimos 30 backups
        self.compression = True
        self.encryption = False  # Implementar se necessário
        
        # Diretórios para backup (verificar se existem)
        self.backup_paths = {}
        if os.path.exists('mara_bet.db'):
            self.backup_paths['database'] = 'mara_bet.db'
        if os.path.exists('models/'):
            self.backup_paths['models'] = 'models/'
        if os.path.exists('settings/'):
            self.backup_paths['config'] = 'settings/'
        if os.path.exists('logs/'):
            self.backup_paths['logs'] = 'logs/'
        if os.path.exists('data/'):
            self.backup_paths['data'] = 'data/'
        if os.path.exists('monitoring/'):
            self.backup_paths['monitoring'] = 'monitoring/'
        
        # Metadados de backups
        self.metadata_file = self.backup_dir / 'backup_metadata.json'
        self.load_metadata()
    
    def load_metadata(self):
        """Carrega metadados de backups"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {'backups': []}
    
    def save_metadata(self):
        """Salva metadados de backups"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def create_backup(self, backup_type: str = "full") -> BackupInfo:
        """Cria backup completo"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id
        
        logger.info(f"Iniciando backup: {backup_id}")
        
        try:
            # Criar diretório do backup
            backup_path.mkdir(exist_ok=True)
            
            files_backed_up = []
            total_size = 0
            
            # Backup do banco de dados
            if self.backup_paths['database'] and os.path.exists(self.backup_paths['database']):
                db_backup = self._backup_database(backup_path)
                if db_backup:
                    files_backed_up.append(db_backup)
                    total_size += os.path.getsize(backup_path / db_backup)
            
            # Backup de modelos
            if self.backup_paths['models'] and os.path.exists(self.backup_paths['models']):
                models_backup = self._backup_directory(
                    self.backup_paths['models'], 
                    backup_path / 'models'
                )
                files_backed_up.extend(models_backup)
                total_size += sum(os.path.getsize(backup_path / f) for f in models_backup)
            
            # Backup de configurações
            if self.backup_paths['config'] and os.path.exists(self.backup_paths['config']):
                config_backup = self._backup_directory(
                    self.backup_paths['config'], 
                    backup_path / 'config'
                )
                files_backed_up.extend(config_backup)
                total_size += sum(os.path.getsize(backup_path / f) for f in config_backup)
            
            # Backup de logs
            if self.backup_paths['logs'] and os.path.exists(self.backup_paths['logs']):
                logs_backup = self._backup_directory(
                    self.backup_paths['logs'], 
                    backup_path / 'logs'
                )
                files_backed_up.extend(logs_backup)
                total_size += sum(os.path.getsize(backup_path / f) for f in logs_backup)
            
            # Backup de dados
            if self.backup_paths['data'] and os.path.exists(self.backup_paths['data']):
                data_backup = self._backup_directory(
                    self.backup_paths['data'], 
                    backup_path / 'data'
                )
                files_backed_up.extend(data_backup)
                total_size += sum(os.path.getsize(backup_path / f) for f in data_backup)
            
            # Backup de monitoramento
            if self.backup_paths['monitoring'] and os.path.exists(self.backup_paths['monitoring']):
                monitoring_backup = self._backup_directory(
                    self.backup_paths['monitoring'], 
                    backup_path / 'monitoring'
                )
                files_backed_up.extend(monitoring_backup)
                total_size += sum(os.path.getsize(backup_path / f) for f in monitoring_backup)
            
            # Comprimir backup se habilitado
            if self.compression:
                compressed_file = f"{backup_id}.tar.gz"
                self._compress_backup(backup_path, self.backup_dir / compressed_file)
                shutil.rmtree(backup_path)  # Remover diretório não comprimido
                backup_path = self.backup_dir / compressed_file
                total_size = os.path.getsize(backup_path)
            
            # Calcular checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Criar informações do backup
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type=backup_type,
                size_bytes=total_size,
                checksum=checksum,
                status="completed",
                files=files_backed_up,
                database_backup=self.backup_paths['database'] and os.path.exists(self.backup_paths['database']),
                models_backup=self.backup_paths['models'] and os.path.exists(self.backup_paths['models']),
                config_backup=self.backup_paths['config'] and os.path.exists(self.backup_paths['config'])
            )
            
            # Salvar metadados
            self.metadata['backups'].append(backup_info.__dict__)
            self.save_metadata()
            
            logger.info(f"Backup concluído: {backup_id} ({total_size} bytes)")
            return backup_info
            
        except Exception as e:
            logger.error(f"Erro ao criar backup {backup_id}: {e}")
            
            # Criar backup info com erro
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=datetime.now(),
                backup_type=backup_type,
                size_bytes=0,
                checksum="",
                status="failed",
                files=[],
                database_backup=False,
                models_backup=False,
                config_backup=False
            )
            
            self.metadata['backups'].append(backup_info.__dict__)
            self.save_metadata()
            
            return backup_info
    
    def _backup_database(self, backup_path: Path) -> Optional[str]:
        """Backup do banco de dados SQLite"""
        try:
            db_file = self.backup_paths['database']
            backup_file = "database_backup.db"
            backup_file_path = backup_path / backup_file
            
            # Conectar ao banco e fazer backup
            conn = sqlite3.connect(db_file)
            backup_conn = sqlite3.connect(backup_file_path)
            conn.backup(backup_conn)
            conn.close()
            backup_conn.close()
            
            logger.info(f"Backup do banco de dados: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Erro no backup do banco: {e}")
            return None
    
    def _backup_directory(self, source_dir: str, dest_dir: Path) -> List[str]:
        """Backup de diretório"""
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                logger.warning(f"Diretório não existe: {source_dir}")
                return []
                
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            backed_files = []
            
            for item in source_path.rglob('*'):
                if item.is_file():
                    try:
                        # Manter estrutura de diretórios
                        rel_path = item.relative_to(source_path)
                        dest_file = dest_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copiar arquivo
                        shutil.copy2(item, dest_file)
                        backed_files.append(str(rel_path))
                    except Exception as e:
                        logger.warning(f"Erro ao copiar arquivo {item}: {e}")
                        continue
            
            logger.info(f"Backup de diretório {source_dir}: {len(backed_files)} arquivos")
            return backed_files
            
        except Exception as e:
            logger.error(f"Erro no backup do diretório {source_dir}: {e}")
            return []
    
    def _compress_backup(self, source_path: Path, dest_path: Path):
        """Comprime backup"""
        try:
            import tarfile
            
            with tarfile.open(dest_path, 'w:gz') as tar:
                tar.add(source_path, arcname=source_path.name)
            
            logger.info(f"Backup comprimido: {dest_path}")
            
        except Exception as e:
            logger.error(f"Erro ao comprimir backup: {e}")
            raise
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum do arquivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular checksum: {e}")
            return ""
    
    def restore_backup(self, backup_id: str, restore_path: str = ".") -> bool:
        """Restaura backup"""
        try:
            logger.info(f"Iniciando restauração: {backup_id}")
            
            # Encontrar backup
            backup_info = self._find_backup(backup_id)
            if not backup_info:
                logger.error(f"Backup não encontrado: {backup_id}")
                return False
            
            # Verificar se backup existe
            backup_file = self.backup_dir / f"{backup_id}.tar.gz"
            if not backup_file.exists():
                backup_file = self.backup_dir / backup_id
                if not backup_file.exists():
                    logger.error(f"Arquivo de backup não encontrado: {backup_id}")
                    return False
            
            # Descomprimir se necessário
            if backup_file.suffix == '.gz':
                temp_dir = self.backup_dir / f"temp_{backup_id}"
                self._decompress_backup(backup_file, temp_dir)
                source_path = temp_dir
            else:
                source_path = backup_file
            
            # Restaurar arquivos
            restore_path = Path(restore_path)
            restore_path.mkdir(parents=True, exist_ok=True)
            
            # Restaurar banco de dados
            if backup_info.get('database_backup'):
                db_backup = source_path / "database_backup.db"
                if db_backup.exists():
                    shutil.copy2(db_backup, restore_path / "mara_bet.db")
                    logger.info("Banco de dados restaurado")
            
            # Restaurar diretórios
            for subdir in ['models', 'config', 'logs', 'data', 'monitoring']:
                subdir_path = source_path / subdir
                if subdir_path.exists():
                    dest_subdir = restore_path / subdir
                    if dest_subdir.exists():
                        shutil.rmtree(dest_subdir)
                    shutil.copytree(subdir_path, dest_subdir)
                    logger.info(f"Diretório {subdir} restaurado")
            
            # Limpar diretório temporário
            if source_path != backup_file:
                shutil.rmtree(source_path)
            
            logger.info(f"Restauração concluída: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na restauração {backup_id}: {e}")
            return False
    
    def _decompress_backup(self, compressed_file: Path, dest_dir: Path):
        """Descomprime backup"""
        try:
            import tarfile
            
            with tarfile.open(compressed_file, 'r:gz') as tar:
                tar.extractall(dest_dir)
            
            logger.info(f"Backup descomprimido: {dest_dir}")
            
        except Exception as e:
            logger.error(f"Erro ao descomprimir backup: {e}")
            raise
    
    def _find_backup(self, backup_id: str) -> Optional[Dict]:
        """Encontra backup por ID"""
        for backup in self.metadata['backups']:
            if backup['backup_id'] == backup_id:
                return backup
        return None
    
    def list_backups(self) -> List[BackupInfo]:
        """Lista todos os backups"""
        backups = []
        for backup_data in self.metadata['backups']:
            # Converter timestamp se necessário
            timestamp = backup_data['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, dict):
                timestamp = datetime.fromisoformat(timestamp['iso'])
            
            backup_info = BackupInfo(
                backup_id=backup_data['backup_id'],
                timestamp=timestamp,
                backup_type=backup_data['backup_type'],
                size_bytes=backup_data['size_bytes'],
                checksum=backup_data['checksum'],
                status=backup_data['status'],
                files=backup_data['files'],
                database_backup=backup_data['database_backup'],
                models_backup=backup_data['models_backup'],
                config_backup=backup_data['config_backup']
            )
            backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x.timestamp, reverse=True)
    
    def cleanup_old_backups(self):
        """Remove backups antigos"""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            backups_to_remove = backups[self.max_backups:]
            
            for backup in backups_to_remove:
                # Remover arquivo de backup
                backup_file = self.backup_dir / f"{backup.backup_id}.tar.gz"
                if not backup_file.exists():
                    backup_file = self.backup_dir / backup.backup_id
                
                if backup_file.exists():
                    if backup_file.is_dir():
                        shutil.rmtree(backup_file)
                    else:
                        backup_file.unlink()
                
                # Remover dos metadados
                self.metadata['backups'] = [
                    b for b in self.metadata['backups'] 
                    if b['backup_id'] != backup.backup_id
                ]
                
                logger.info(f"Backup removido: {backup.backup_id}")
            
            self.save_metadata()
    
    def validate_backup(self, backup_id: str) -> bool:
        """Valida integridade do backup"""
        try:
            backup_info = self._find_backup(backup_id)
            if not backup_info:
                return False
            
            # Verificar arquivo de backup
            backup_file = self.backup_dir / f"{backup_id}.tar.gz"
            if not backup_file.exists():
                backup_file = self.backup_dir / backup_id
            
            if not backup_file.exists():
                return False
            
            # Verificar checksum
            current_checksum = self._calculate_checksum(backup_file)
            if current_checksum != backup_info['checksum']:
                logger.error(f"Checksum inválido para backup {backup_id}")
                return False
            
            logger.info(f"Backup validado: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação do backup {backup_id}: {e}")
            return False
    
    def schedule_backups(self):
        """Agenda backups automáticos"""
        # Backup diário às 2h
        schedule.every().day.at("02:00").do(self.create_backup, "daily")
        
        # Backup semanal aos domingos às 3h
        schedule.every().sunday.at("03:00").do(self.create_backup, "weekly")
        
        # Limpeza de backups antigos diariamente às 4h
        schedule.every().day.at("04:00").do(self.cleanup_old_backups)
        
        logger.info("Backups agendados")
    
    def run_scheduler(self):
        """Executa agendador de backups"""
        logger.info("Iniciando agendador de backups")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto

# Instância global
backup_manager = BackupManager()

if __name__ == "__main__":
    # Teste do sistema de backup
    print("🧪 TESTANDO SISTEMA DE BACKUP")
    print("=" * 40)
    
    # Criar backup de teste
    backup_info = backup_manager.create_backup("test")
    print(f"Backup criado: {backup_info.backup_id}")
    print(f"Status: {backup_info.status}")
    print(f"Tamanho: {backup_info.size_bytes} bytes")
    print(f"Checksum: {backup_info.checksum}")
    
    # Listar backups
    backups = backup_manager.list_backups()
    print(f"\nTotal de backups: {len(backups)}")
    
    for backup in backups[:3]:  # Mostrar últimos 3
        print(f"  - {backup.backup_id}: {backup.timestamp} ({backup.size_bytes} bytes)")
    
    # Validar backup
    if backups:
        latest_backup = backups[0]
        is_valid = backup_manager.validate_backup(latest_backup.backup_id)
        print(f"\nValidação do backup mais recente: {'✅ Válido' if is_valid else '❌ Inválido'}")
    
    print("\n🎉 TESTES DE BACKUP CONCLUÍDOS!")
