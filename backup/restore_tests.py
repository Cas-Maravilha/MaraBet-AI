#!/usr/bin/env python3
"""
Testes de Restauração para o MaraBet AI
Validação de procedimentos de disaster recovery
"""

import os
import shutil
import tempfile
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import pytest

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup.backup_manager import BackupManager, BackupInfo

logger = logging.getLogger(__name__)

class RestoreTester:
    """Testador de procedimentos de restauração"""
    
    def __init__(self):
        """Inicializa testador"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="marabet_test_"))
        self.backup_manager = BackupManager(str(self.test_dir / "backups"))
        self.test_data = self._create_test_data()
    
    def _create_test_data(self) -> Dict:
        """Cria dados de teste"""
        # Criar banco de dados de teste
        db_path = self.test_dir / "mara_bet.db"
        conn = sqlite3.connect(db_path)
        
        # Criar tabelas de teste
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY,
                match_id TEXT,
                bet_type TEXT,
                stake REAL,
                odds REAL,
                profit_loss REAL,
                timestamp DATETIME
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY,
                match_id TEXT,
                prediction TEXT,
                confidence REAL,
                expected_value REAL,
                timestamp DATETIME
            )
        """)
        
        # Inserir dados de teste
        test_bets = [
            (1, "39_12345", "home_win", 100.0, 1.85, 85.0, "2024-01-01 10:00:00"),
            (2, "140_67890", "draw", 50.0, 3.40, -50.0, "2024-01-01 11:00:00"),
            (3, "78_11111", "over_2_5", 75.0, 2.10, 82.5, "2024-01-01 12:00:00")
        ]
        
        conn.executemany("INSERT INTO bets VALUES (?, ?, ?, ?, ?, ?, ?)", test_bets)
        
        test_predictions = [
            (1, "39_12346", "home_win", 0.75, 0.12, "2024-01-01 10:30:00"),
            (2, "140_67891", "away_win", 0.65, 0.08, "2024-01-01 11:30:00")
        ]
        
        conn.executemany("INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?)", test_predictions)
        conn.commit()
        conn.close()
        
        # Criar diretórios de teste
        (self.test_dir / "models").mkdir(exist_ok=True)
        (self.test_dir / "settings").mkdir(exist_ok=True)
        (self.test_dir / "logs").mkdir(exist_ok=True)
        (self.test_dir / "data").mkdir(exist_ok=True)
        
        # Criar arquivos de teste
        (self.test_dir / "models" / "model.pkl").write_text("fake_model_data")
        (self.test_dir / "settings" / "config.py").write_text("fake_config_data")
        (self.test_dir / "logs" / "app.log").write_text("fake_log_data")
        (self.test_dir / "data" / "data.json").write_text('{"test": "data"}')
        
        return {
            "database": str(db_path),
            "models": str(self.test_dir / "models"),
            "settings": str(self.test_dir / "settings"),
            "logs": str(self.test_dir / "logs"),
            "data": str(self.test_dir / "data")
        }
    
    def test_full_backup_restore(self) -> Tuple[bool, str]:
        """Testa backup e restauração completa"""
        try:
            logger.info("🧪 Testando backup e restauração completa")
            
            # Configurar paths de backup
            self.backup_manager.backup_paths = self.test_data
            
            # Criar backup
            backup_info = self.backup_manager.create_backup("test_full")
            
            if backup_info.status != "completed":
                return False, f"Backup falhou: {backup_info.status}"
            
            # Criar diretório de restauração
            restore_dir = self.test_dir / "restore_test"
            restore_dir.mkdir(exist_ok=True)
            
            # Restaurar backup
            success = self.backup_manager.restore_backup(backup_info.backup_id, str(restore_dir))
            
            if not success:
                return False, "Restauração falhou"
            
            # Verificar arquivos restaurados
            restored_files = [
                restore_dir / "mara_bet.db",
                restore_dir / "models" / "model.pkl",
                restore_dir / "settings" / "config.py",
                restore_dir / "logs" / "app.log",
                restore_dir / "data" / "data.json"
            ]
            
            for file_path in restored_files:
                if not file_path.exists():
                    return False, f"Arquivo não restaurado: {file_path}"
            
            # Verificar banco de dados
            db_path = restore_dir / "mara_bet.db"
            conn = sqlite3.connect(db_path)
            
            # Verificar tabelas
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if "bets" not in tables or "predictions" not in tables:
                return False, "Tabelas do banco não restauradas"
            
            # Verificar dados
            cursor = conn.execute("SELECT COUNT(*) FROM bets")
            bet_count = cursor.fetchone()[0]
            
            if bet_count != 3:
                return False, f"Dados de apostas não restaurados: {bet_count} esperado 3"
            
            cursor = conn.execute("SELECT COUNT(*) FROM predictions")
            pred_count = cursor.fetchone()[0]
            
            if pred_count != 2:
                return False, f"Dados de predições não restaurados: {pred_count} esperado 2"
            
            conn.close()
            
            logger.info("✅ Teste de backup e restauração completa passou")
            return True, "Backup e restauração completa funcionando"
            
        except Exception as e:
            logger.error(f"Erro no teste de backup completo: {e}")
            return False, f"Erro: {str(e)}"
    
    def test_database_integrity(self) -> Tuple[bool, str]:
        """Testa integridade do banco de dados"""
        try:
            logger.info("🧪 Testando integridade do banco de dados")
            
            # Configurar paths de backup
            self.backup_manager.backup_paths = self.test_data
            
            # Criar backup
            backup_info = self.backup_manager.create_backup("test_integrity")
            
            if backup_info.status != "completed":
                return False, f"Backup falhou: {backup_info.status}"
            
            # Validar backup
            is_valid = self.backup_manager.validate_backup(backup_info.backup_id)
            
            if not is_valid:
                return False, "Validação do backup falhou"
            
            # Restaurar e verificar integridade
            restore_dir = self.test_dir / "integrity_test"
            restore_dir.mkdir(exist_ok=True)
            
            success = self.backup_manager.restore_backup(backup_info.backup_id, str(restore_dir))
            
            if not success:
                return False, "Restauração falhou"
            
            # Verificar integridade do banco restaurado
            db_path = restore_dir / "mara_bet.db"
            conn = sqlite3.connect(db_path)
            
            # Executar verificação de integridade
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result != "ok":
                return False, f"Integridade do banco falhou: {result}"
            
            # Verificar foreign keys
            cursor = conn.execute("PRAGMA foreign_key_check")
            fk_errors = cursor.fetchall()
            
            if fk_errors:
                return False, f"Erros de foreign key: {fk_errors}"
            
            conn.close()
            
            logger.info("✅ Teste de integridade do banco passou")
            return True, "Integridade do banco de dados verificada"
            
        except Exception as e:
            logger.error(f"Erro no teste de integridade: {e}")
            return False, f"Erro: {str(e)}"
    
    def test_backup_compression(self) -> Tuple[bool, str]:
        """Testa compressão de backups"""
        try:
            logger.info("🧪 Testando compressão de backups")
            
            # Configurar paths de backup
            self.backup_manager.backup_paths = self.test_data
            self.backup_manager.compression = True
            
            # Criar backup comprimido
            backup_info = self.backup_manager.create_backup("test_compression")
            
            if backup_info.status != "completed":
                return False, f"Backup falhou: {backup_info.status}"
            
            # Verificar se arquivo comprimido existe
            compressed_file = self.backup_manager.backup_dir / f"{backup_info.backup_id}.tar.gz"
            
            if not compressed_file.exists():
                return False, "Arquivo comprimido não criado"
            
            # Verificar se diretório não comprimido foi removido
            uncompressed_dir = self.backup_manager.backup_dir / backup_info.backup_id
            
            if uncompressed_dir.exists():
                return False, "Diretório não comprimido não foi removido"
            
            # Verificar tamanho do arquivo comprimido
            compressed_size = compressed_file.stat().st_size
            
            if compressed_size == 0:
                return False, "Arquivo comprimido está vazio"
            
            # Restaurar backup comprimido
            restore_dir = self.test_dir / "compression_test"
            restore_dir.mkdir(exist_ok=True)
            
            success = self.backup_manager.restore_backup(backup_info.backup_id, str(restore_dir))
            
            if not success:
                return False, "Restauração do backup comprimido falhou"
            
            # Verificar se arquivos foram restaurados
            db_path = restore_dir / "mara_bet.db"
            
            if not db_path.exists():
                return False, "Banco de dados não restaurado do backup comprimido"
            
            logger.info("✅ Teste de compressão passou")
            return True, f"Compressão funcionando (tamanho: {compressed_size} bytes)"
            
        except Exception as e:
            logger.error(f"Erro no teste de compressão: {e}")
            return False, f"Erro: {str(e)}"
    
    def test_backup_cleanup(self) -> Tuple[bool, str]:
        """Testa limpeza de backups antigos"""
        try:
            logger.info("🧪 Testando limpeza de backups antigos")
            
            # Configurar paths de backup
            self.backup_manager.backup_paths = self.test_data
            self.backup_manager.max_backups = 3
            
            # Criar múltiplos backups
            backup_ids = []
            for i in range(5):
                backup_info = self.backup_manager.create_backup(f"test_cleanup_{i}")
                backup_ids.append(backup_info.backup_id)
                # Simular tempo entre backups
                import time
                time.sleep(1)
            
            # Verificar quantos backups existem
            backups = self.backup_manager.list_backups()
            
            if len(backups) != 5:
                return False, f"Esperado 5 backups, encontrado {len(backups)}"
            
            # Executar limpeza
            self.backup_manager.cleanup_old_backups()
            
            # Verificar se apenas 3 backups restaram
            backups_after_cleanup = self.backup_manager.list_backups()
            
            if len(backups_after_cleanup) != 3:
                return False, f"Esperado 3 backups após limpeza, encontrado {len(backups_after_cleanup)}"
            
            # Verificar se os backups mais antigos foram removidos
            remaining_ids = [b.backup_id for b in backups_after_cleanup]
            
            if backup_ids[0] in remaining_ids or backup_ids[1] in remaining_ids:
                return False, "Backups antigos não foram removidos"
            
            logger.info("✅ Teste de limpeza passou")
            return True, f"Limpeza funcionando (mantidos {len(backups_after_cleanup)} backups)"
            
        except Exception as e:
            logger.error(f"Erro no teste de limpeza: {e}")
            return False, f"Erro: {str(e)}"
    
    def test_restore_validation(self) -> Tuple[bool, str]:
        """Testa validação de restauração"""
        try:
            logger.info("🧪 Testando validação de restauração")
            
            # Configurar paths de backup
            self.backup_manager.backup_paths = self.test_data
            
            # Criar backup
            backup_info = self.backup_manager.create_backup("test_validation")
            
            if backup_info.status != "completed":
                return False, f"Backup falhou: {backup_info.status}"
            
            # Validar backup
            is_valid = self.backup_manager.validate_backup(backup_info.backup_id)
            
            if not is_valid:
                return False, "Validação do backup falhou"
            
            # Corromper backup para testar detecção
            backup_file = self.backup_manager.backup_dir / f"{backup_info.backup_id}.tar.gz"
            
            if not backup_file.exists():
                backup_file = self.backup_manager.backup_dir / backup_info.backup_id
            
            # Adicionar dados corrompidos
            with open(backup_file, "ab") as f:
                f.write(b"corrupted_data")
            
            # Tentar validar backup corrompido
            is_valid_corrupted = self.backup_manager.validate_backup(backup_info.backup_id)
            
            if is_valid_corrupted:
                return False, "Validação não detectou backup corrompido"
            
            logger.info("✅ Teste de validação passou")
            return True, "Validação de backup funcionando corretamente"
            
        except Exception as e:
            logger.error(f"Erro no teste de validação: {e}")
            return False, f"Erro: {str(e)}"
    
    def run_all_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Executa todos os testes"""
        logger.info("🚀 Iniciando testes de restauração")
        
        tests = {
            "full_backup_restore": self.test_full_backup_restore,
            "database_integrity": self.test_database_integrity,
            "backup_compression": self.test_backup_compression,
            "backup_cleanup": self.test_backup_cleanup,
            "restore_validation": self.test_restore_validation
        }
        
        results = {}
        
        for test_name, test_func in tests.items():
            try:
                success, message = test_func()
                results[test_name] = (success, message)
                
                if success:
                    logger.info(f"✅ {test_name}: {message}")
                else:
                    logger.error(f"❌ {test_name}: {message}")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: Erro inesperado - {e}")
                results[test_name] = (False, f"Erro inesperado: {str(e)}")
        
        return results
    
    def cleanup(self):
        """Limpa arquivos de teste"""
        try:
            shutil.rmtree(self.test_dir)
            logger.info("Arquivos de teste removidos")
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos de teste: {e}")

def run_restore_tests():
    """Executa testes de restauração"""
    tester = RestoreTester()
    
    try:
        results = tester.run_all_tests()
        
        # Resumo dos resultados
        total_tests = len(results)
        passed_tests = sum(1 for success, _ in results.values() if success)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 RESUMO DOS TESTES DE RESTAURAÇÃO")
        print("=" * 50)
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {failed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ TESTES QUE FALHARAM:")
            for test_name, (success, message) in results.items():
                if not success:
                    print(f"  - {test_name}: {message}")
        
        return passed_tests == total_tests
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    # Executar testes
    success = run_restore_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES DE RESTAURAÇÃO PASSARAM!")
        exit(0)
    else:
        print("\n❌ ALGUNS TESTES DE RESTAURAÇÃO FALHARAM!")
        exit(1)
