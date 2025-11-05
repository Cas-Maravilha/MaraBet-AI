#!/usr/bin/env python3
"""
Teste de Backup e Restauração
MaraBet AI - Validação de backup automático e restauração
"""

import os
import subprocess
import time
import json
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import sqlite3
import tempfile

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupRestoreTester:
    """Testador de backup e restauração"""
    
    def __init__(self):
        self.backup_dir = "backups"
        self.test_data_dir = "test_data"
        self.restore_dir = "restore_test"
        self.backup_script = "infrastructure/templates/backup.sh"
        self.restore_script = "infrastructure/templates/restore.sh"
        
        # Criar diretórios de teste
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.restore_dir, exist_ok=True)
    
    def create_test_database(self) -> str:
        """Cria banco de dados de teste"""
        logger.info("🗄️ CRIANDO BANCO DE DADOS DE TESTE")
        
        db_path = os.path.join(self.test_data_dir, "test_database.db")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Criar tabelas de teste
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    home_score INTEGER,
                    away_score INTEGER,
                    match_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY,
                    match_id INTEGER,
                    prediction TEXT NOT NULL,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            """)
            
            # Inserir dados de teste
            users_data = [
                (1, 'admin', 'admin@marabet.com'),
                (2, 'user1', 'user1@marabet.com'),
                (3, 'user2', 'user2@marabet.com'),
                (4, 'user3', 'user3@marabet.com'),
                (5, 'user4', 'user4@marabet.com')
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO users (id, username, email)
                VALUES (?, ?, ?)
            """, users_data)
            
            matches_data = [
                (1, 'Barcelona', 'Real Madrid', 2, 1, '2025-10-21 15:00:00'),
                (2, 'Manchester United', 'Liverpool', 1, 3, '2025-10-21 17:30:00'),
                (3, 'Bayern Munich', 'Borussia Dortmund', 4, 0, '2025-10-21 20:00:00'),
                (4, 'PSG', 'Marseille', 2, 2, '2025-10-22 15:00:00'),
                (5, 'Juventus', 'AC Milan', 1, 1, '2025-10-22 17:30:00')
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO matches (id, home_team, away_team, home_score, away_score, match_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, matches_data)
            
            predictions_data = [
                (1, 1, 'home_win', 0.75),
                (2, 2, 'away_win', 0.65),
                (3, 3, 'home_win', 0.85),
                (4, 4, 'draw', 0.45),
                (5, 5, 'draw', 0.55)
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO predictions (id, match_id, prediction, confidence)
                VALUES (?, ?, ?, ?)
            """, predictions_data)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"   Banco de dados criado: {db_path}")
            return db_path
            
        except Exception as e:
            logger.error(f"Erro ao criar banco de teste: {e}")
            return None
    
    def create_test_files(self) -> List[str]:
        """Cria arquivos de teste"""
        logger.info("📁 CRIANDO ARQUIVOS DE TESTE")
        
        test_files = []
        
        # Criar arquivos de configuração
        config_files = [
            "app.conf",
            "database.conf",
            "redis.conf",
            "logging.conf"
        ]
        
        for config_file in config_files:
            file_path = os.path.join(self.test_data_dir, config_file)
            with open(file_path, 'w') as f:
                f.write(f"# Configuração de teste para {config_file}\n")
                f.write(f"# Criado em {datetime.now().isoformat()}\n")
                f.write(f"test_value = {int(time.time())}\n")
            test_files.append(file_path)
        
        # Criar arquivos de log
        log_files = [
            "app.log",
            "error.log",
            "access.log"
        ]
        
        for log_file in log_files:
            file_path = os.path.join(self.test_data_dir, log_file)
            with open(file_path, 'w') as f:
                for i in range(100):
                    f.write(f"{datetime.now().isoformat()} - INFO - Log entry {i}\n")
            test_files.append(file_path)
        
        # Criar arquivos de dados
        data_files = [
            "matches.json",
            "predictions.json",
            "users.json"
        ]
        
        for data_file in data_files:
            file_path = os.path.join(self.test_data_dir, data_file)
            data = {
                "file": data_file,
                "created_at": datetime.now().isoformat(),
                "data": [f"item_{i}" for i in range(50)]
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            test_files.append(file_path)
        
        logger.info(f"   {len(test_files)} arquivos de teste criados")
        return test_files
    
    def test_backup_script(self) -> Dict[str, Any]:
        """Testa script de backup"""
        logger.info("💾 TESTANDO SCRIPT DE BACKUP")
        print("=" * 60)
        
        results = {
            'script_exists': False,
            'script_executable': False,
            'backup_successful': False,
            'backup_files_created': [],
            'backup_size': 0,
            'backup_time': 0,
            'compression_ratio': 0
        }
        
        # 1. Verificar se script existe
        logger.info("1. Verificando script de backup...")
        results['script_exists'] = os.path.exists(self.backup_script)
        logger.info(f"   Script existe: {results['script_exists']}")
        
        if not results['script_exists']:
            logger.error("❌ Script de backup não encontrado")
            return results
        
        # 2. Verificar se script é executável
        logger.info("2. Verificando permissões do script...")
        results['script_executable'] = os.access(self.backup_script, os.X_OK)
        logger.info(f"   Script executável: {results['script_executable']}")
        
        if not results['script_executable']:
            logger.info("   Tornando script executável...")
            os.chmod(self.backup_script, 0o755)
            results['script_executable'] = True
        
        # 3. Executar backup
        logger.info("3. Executando backup...")
        start_time = time.time()
        
        try:
            # Modificar script para usar dados de teste
            env = os.environ.copy()
            env['TEST_MODE'] = 'true'
            env['BACKUP_DIR'] = self.backup_dir
            env['TEST_DATA_DIR'] = self.test_data_dir
            
            result = subprocess.run(
                [self.backup_script, "full"],
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            results['backup_successful'] = result.returncode == 0
            results['backup_time'] = time.time() - start_time
            
            logger.info(f"   Backup executado: {results['backup_successful']}")
            logger.info(f"   Tempo de backup: {results['backup_time']:.2f}s")
            
            if result.stdout:
                logger.info(f"   Output: {result.stdout}")
            if result.stderr:
                logger.error(f"   Erro: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no script de backup")
        except Exception as e:
            logger.error(f"❌ Erro ao executar script de backup: {e}")
        
        # 4. Verificar arquivos de backup criados
        logger.info("4. Verificando arquivos de backup...")
        if os.path.exists(self.backup_dir):
            backup_files = os.listdir(self.backup_dir)
            results['backup_files_created'] = backup_files
            logger.info(f"   Arquivos criados: {len(backup_files)}")
            
            # Calcular tamanho total
            total_size = 0
            for file in backup_files:
                file_path = os.path.join(self.backup_dir, file)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
            
            results['backup_size'] = total_size
            logger.info(f"   Tamanho total: {total_size / 1024:.2f} KB")
        
        return results
    
    def test_restore_script(self) -> Dict[str, Any]:
        """Testa script de restauração"""
        logger.info("🔄 TESTANDO SCRIPT DE RESTAURAÇÃO")
        print("=" * 60)
        
        results = {
            'script_exists': False,
            'script_executable': False,
            'restore_successful': False,
            'restore_time': 0,
            'data_integrity': False,
            'files_restored': []
        }
        
        # 1. Verificar se script existe
        logger.info("1. Verificando script de restauração...")
        results['script_exists'] = os.path.exists(self.restore_script)
        logger.info(f"   Script existe: {results['script_exists']}")
        
        if not results['script_exists']:
            logger.error("❌ Script de restauração não encontrado")
            return results
        
        # 2. Verificar se script é executável
        logger.info("2. Verificando permissões do script...")
        results['script_executable'] = os.access(self.restore_script, os.X_OK)
        logger.info(f"   Script executável: {results['script_executable']}")
        
        if not results['script_executable']:
            logger.info("   Tornando script executável...")
            os.chmod(self.restore_script, 0o755)
            results['script_executable'] = True
        
        # 3. Executar restauração
        logger.info("3. Executando restauração...")
        start_time = time.time()
        
        try:
            # Encontrar arquivo de backup mais recente
            if os.path.exists(self.backup_dir):
                backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.sql')]
                if backup_files:
                    latest_backup = max(backup_files, key=lambda x: os.path.getctime(os.path.join(self.backup_dir, x)))
                    backup_path = os.path.join(self.backup_dir, latest_backup)
                    
                    # Modificar script para usar dados de teste
                    env = os.environ.copy()
                    env['TEST_MODE'] = 'true'
                    env['RESTORE_DIR'] = self.restore_dir
                    env['BACKUP_FILE'] = backup_path
                    
                    result = subprocess.run(
                        [self.restore_script, "database", backup_path],
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    results['restore_successful'] = result.returncode == 0
                    results['restore_time'] = time.time() - start_time
                    
                    logger.info(f"   Restauração executada: {results['restore_successful']}")
                    logger.info(f"   Tempo de restauração: {results['restore_time']:.2f}s")
                    
                    if result.stdout:
                        logger.info(f"   Output: {result.stdout}")
                    if result.stderr:
                        logger.error(f"   Erro: {result.stderr}")
                else:
                    logger.error("❌ Nenhum arquivo de backup encontrado")
            else:
                logger.error("❌ Diretório de backup não encontrado")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no script de restauração")
        except Exception as e:
            logger.error(f"❌ Erro ao executar script de restauração: {e}")
        
        # 4. Verificar integridade dos dados
        logger.info("4. Verificando integridade dos dados...")
        if os.path.exists(self.restore_dir):
            restored_files = os.listdir(self.restore_dir)
            results['files_restored'] = restored_files
            logger.info(f"   Arquivos restaurados: {len(restored_files)}")
            
            # Verificar se banco de dados foi restaurado
            db_files = [f for f in restored_files if f.endswith('.db')]
            if db_files:
                db_path = os.path.join(self.restore_dir, db_files[0])
                results['data_integrity'] = self.verify_database_integrity(db_path)
                logger.info(f"   Integridade dos dados: {results['data_integrity']}")
        
        return results
    
    def verify_database_integrity(self, db_path: str) -> bool:
        """Verifica integridade do banco de dados"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se tabelas existem
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['users', 'matches', 'predictions']
            if not all(table in tables for table in expected_tables):
                logger.error("❌ Tabelas não encontradas")
                return False
            
            # Verificar contagem de registros
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM matches")
            match_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM predictions")
            prediction_count = cursor.fetchone()[0]
            
            logger.info(f"   Usuários: {user_count}")
            logger.info(f"   Partidas: {match_count}")
            logger.info(f"   Predições: {prediction_count}")
            
            # Verificar se dados estão corretos
            cursor.execute("SELECT username FROM users WHERE id = 1")
            admin_user = cursor.fetchone()
            
            if admin_user and admin_user[0] == 'admin':
                logger.info("   ✅ Dados verificados com sucesso")
                return True
            else:
                logger.error("❌ Dados incorretos")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def test_backup_compression(self) -> Dict[str, Any]:
        """Testa compressão de backup"""
        logger.info("🗜️ TESTANDO COMPRESSÃO DE BACKUP")
        print("=" * 60)
        
        results = {
            'compression_enabled': False,
            'compression_ratio': 0,
            'compressed_files': [],
            'space_saved': 0
        }
        
        # Verificar se há arquivos comprimidos
        if os.path.exists(self.backup_dir):
            backup_files = os.listdir(self.backup_dir)
            compressed_files = [f for f in backup_files if f.endswith('.gz')]
            results['compressed_files'] = compressed_files
            results['compression_enabled'] = len(compressed_files) > 0
            
            logger.info(f"   Compressão habilitada: {results['compression_enabled']}")
            logger.info(f"   Arquivos comprimidos: {len(compressed_files)}")
            
            if compressed_files:
                # Calcular taxa de compressão
                total_original_size = 0
                total_compressed_size = 0
                
                for file in compressed_files:
                    file_path = os.path.join(self.backup_dir, file)
                    compressed_size = os.path.getsize(file_path)
                    total_compressed_size += compressed_size
                    
                    # Estimar tamanho original (aproximado)
                    with gzip.open(file_path, 'rb') as f:
                        original_size = len(f.read())
                        total_original_size += original_size
                
                if total_original_size > 0:
                    results['compression_ratio'] = (1 - total_compressed_size / total_original_size) * 100
                    results['space_saved'] = total_original_size - total_compressed_size
                    
                    logger.info(f"   Taxa de compressão: {results['compression_ratio']:.2f}%")
                    logger.info(f"   Espaço economizado: {results['space_saved'] / 1024:.2f} KB")
        
        return results
    
    def test_backup_encryption(self) -> Dict[str, Any]:
        """Testa criptografia de backup"""
        logger.info("🔐 TESTANDO CRIPTOGRAFIA DE BACKUP")
        print("=" * 60)
        
        results = {
            'encryption_enabled': False,
            'encrypted_files': [],
            'encryption_working': False
        }
        
        # Verificar se há arquivos criptografados
        if os.path.exists(self.backup_dir):
            backup_files = os.listdir(self.backup_dir)
            encrypted_files = [f for f in backup_files if f.endswith('.gpg')]
            results['encrypted_files'] = encrypted_files
            results['encryption_enabled'] = len(encrypted_files) > 0
            
            logger.info(f"   Criptografia habilitada: {results['encryption_enabled']}")
            logger.info(f"   Arquivos criptografados: {len(encrypted_files)}")
            
            if encrypted_files:
                # Testar descriptografia
                try:
                    test_file = os.path.join(self.backup_dir, encrypted_files[0])
                    result = subprocess.run(
                        ['gpg', '--decrypt', '--quiet', test_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    results['encryption_working'] = result.returncode == 0
                    logger.info(f"   Criptografia funcionando: {results['encryption_working']}")
                    
                except Exception as e:
                    logger.error(f"Erro ao testar criptografia: {e}")
        
        return results
    
    def test_backup_retention(self) -> Dict[str, Any]:
        """Testa retenção de backup"""
        logger.info("📅 TESTANDO RETENÇÃO DE BACKUP")
        print("=" * 60)
        
        results = {
            'retention_enabled': False,
            'old_files_cleaned': False,
            'retention_policy': 'unknown'
        }
        
        # Verificar se há política de retenção
        if os.path.exists(self.backup_dir):
            backup_files = os.listdir(self.backup_dir)
            
            # Simular arquivos antigos
            old_files = []
            for file in backup_files:
                file_path = os.path.join(self.backup_dir, file)
                if os.path.isfile(file_path):
                    file_age = time.time() - os.path.getctime(file_path)
                    if file_age > 86400:  # Mais de 1 dia
                        old_files.append(file)
            
            results['retention_enabled'] = len(old_files) < len(backup_files)
            results['old_files_cleaned'] = len(old_files) == 0
            
            logger.info(f"   Retenção habilitada: {results['retention_enabled']}")
            logger.info(f"   Arquivos antigos limpos: {results['old_files_cleaned']}")
            logger.info(f"   Total de arquivos: {len(backup_files)}")
            logger.info(f"   Arquivos antigos: {len(old_files)}")
        
        return results
    
    def generate_report(self, backup_results: Dict, restore_results: Dict, 
                       compression_results: Dict, encryption_results: Dict, 
                       retention_results: Dict) -> str:
        """Gera relatório de teste"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE DE BACKUP E RESTAURAÇÃO - MARABET AI")
        report.append("=" * 80)
        
        # Resumo geral
        report.append(f"\n📊 RESUMO GERAL:")
        report.append(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  Backup: {'✅ Funcionando' if backup_results['backup_successful'] else '❌ Falhou'}")
        report.append(f"  Restauração: {'✅ Funcionando' if restore_results['restore_successful'] else '❌ Falhou'}")
        report.append(f"  Compressão: {'✅ Habilitada' if compression_results['compression_enabled'] else '❌ Desabilitada'}")
        report.append(f"  Criptografia: {'✅ Habilitada' if encryption_results['encryption_enabled'] else '❌ Desabilitada'}")
        report.append(f"  Retenção: {'✅ Funcionando' if retention_results['retention_enabled'] else '❌ Desabilitada'}")
        
        # Backup results
        report.append(f"\n💾 RESULTADOS DE BACKUP:")
        report.append(f"  Script existe: {backup_results['script_exists']}")
        report.append(f"  Script executável: {backup_results['script_executable']}")
        report.append(f"  Backup executado: {backup_results['backup_successful']}")
        report.append(f"  Tempo de backup: {backup_results['backup_time']:.2f}s")
        report.append(f"  Arquivos criados: {len(backup_results['backup_files_created'])}")
        report.append(f"  Tamanho total: {backup_results['backup_size'] / 1024:.2f} KB")
        
        # Restore results
        report.append(f"\n🔄 RESULTADOS DE RESTAURAÇÃO:")
        report.append(f"  Script existe: {restore_results['script_exists']}")
        report.append(f"  Script executável: {restore_results['script_executable']}")
        report.append(f"  Restauração executada: {restore_results['restore_successful']}")
        report.append(f"  Tempo de restauração: {restore_results['restore_time']:.2f}s")
        report.append(f"  Arquivos restaurados: {len(restore_results['files_restored'])}")
        report.append(f"  Integridade dos dados: {restore_results['data_integrity']}")
        
        # Compression results
        report.append(f"\n🗜️ RESULTADOS DE COMPRESSÃO:")
        report.append(f"  Compressão habilitada: {compression_results['compression_enabled']}")
        report.append(f"  Arquivos comprimidos: {len(compression_results['compressed_files'])}")
        report.append(f"  Taxa de compressão: {compression_results['compression_ratio']:.2f}%")
        report.append(f"  Espaço economizado: {compression_results['space_saved'] / 1024:.2f} KB")
        
        # Encryption results
        report.append(f"\n🔐 RESULTADOS DE CRIPTOGRAFIA:")
        report.append(f"  Criptografia habilitada: {encryption_results['encryption_enabled']}")
        report.append(f"  Arquivos criptografados: {len(encryption_results['encrypted_files'])}")
        report.append(f"  Criptografia funcionando: {encryption_results['encryption_working']}")
        
        # Retention results
        report.append(f"\n📅 RESULTADOS DE RETENÇÃO:")
        report.append(f"  Retenção habilitada: {retention_results['retention_enabled']}")
        report.append(f"  Arquivos antigos limpos: {retention_results['old_files_cleaned']}")
        
        # Validação de objetivos
        report.append(f"\n🎯 VALIDAÇÃO DE OBJETIVOS:")
        
        if backup_results['backup_successful']:
            report.append(f"  ✅ Backup funcionando")
        else:
            report.append(f"  ❌ Backup falhou")
        
        if restore_results['restore_successful'] and restore_results['data_integrity']:
            report.append(f"  ✅ Restauração funcionando")
        else:
            report.append(f"  ❌ Restauração falhou")
        
        if compression_results['compression_enabled']:
            report.append(f"  ✅ Compressão habilitada")
        else:
            report.append(f"  ❌ Compressão desabilitada")
        
        if encryption_results['encryption_enabled'] and encryption_results['encryption_working']:
            report.append(f"  ✅ Criptografia funcionando")
        else:
            report.append(f"  ❌ Criptografia falhou")
        
        if retention_results['retention_enabled']:
            report.append(f"  ✅ Retenção funcionando")
        else:
            report.append(f"  ❌ Retenção desabilitada")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if not backup_results['backup_successful']:
            report.append(f"  ⚠️ Configurar script de backup")
        
        if not restore_results['restore_successful']:
            report.append(f"  ⚠️ Configurar script de restauração")
        
        if not compression_results['compression_enabled']:
            report.append(f"  ⚠️ Habilitar compressão de backup")
        
        if not encryption_results['encryption_enabled']:
            report.append(f"  ⚠️ Habilitar criptografia de backup")
        
        if not retention_results['retention_enabled']:
            report.append(f"  ⚠️ Configurar política de retenção")
        
        report.append(f"  🔄 Executar testes de backup regularmente")
        report.append(f"  📊 Monitorar tamanho dos backups")
        report.append(f"  🔐 Manter chaves de criptografia seguras")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Função principal"""
    print("💾 TESTE DE BACKUP E RESTAURAÇÃO - MARABET AI")
    print("=" * 80)
    
    tester = BackupRestoreTester()
    
    try:
        # 1. Criar dados de teste
        logger.info("Criando dados de teste...")
        db_path = tester.create_test_database()
        test_files = tester.create_test_files()
        
        if not db_path:
            logger.error("❌ Falha ao criar dados de teste")
            return False
        
        # 2. Testar backup
        backup_results = tester.test_backup_script()
        
        # 3. Testar restauração
        restore_results = tester.test_restore_script()
        
        # 4. Testar compressão
        compression_results = tester.test_backup_compression()
        
        # 5. Testar criptografia
        encryption_results = tester.test_backup_encryption()
        
        # 6. Testar retenção
        retention_results = tester.test_backup_retention()
        
        # 7. Gerar relatório
        report = tester.generate_report(backup_results, restore_results, 
                                      compression_results, encryption_results, 
                                      retention_results)
        print(f"\n{report}")
        
        # 8. Salvar relatório
        with open("backup_restore_test_report.txt", "w") as f:
            f.write(report)
        
        print("\n🎉 TESTE DE BACKUP E RESTAURAÇÃO CONCLUÍDO!")
        print("📄 Relatório salvo em: backup_restore_test_report.txt")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    main()
