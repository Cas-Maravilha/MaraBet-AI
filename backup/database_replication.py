#!/usr/bin/env python3
"""
Sistema de Replicação de Banco de Dados para o MaraBet AI
Replicação Master-Slave para alta disponibilidade
"""

import os
import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import schedule

logger = logging.getLogger(__name__)

class DatabaseReplication:
    """Sistema de replicação de banco de dados"""
    
    def __init__(self, master_db: str, slave_db: str):
        """Inicializa sistema de replicação"""
        self.master_db = master_db
        self.slave_db = slave_db
        self.replication_log = []
        self.is_replicating = False
        self.last_sync = None
        
        # Configurações
        self.sync_interval = 60  # segundos
        self.batch_size = 1000
        self.max_retries = 3
        
        # Inicializar banco de dados
        self._init_databases()
    
    def _init_databases(self):
        """Inicializa bancos de dados master e slave"""
        # Criar diretórios se não existirem
        Path(self.master_db).parent.mkdir(parents=True, exist_ok=True)
        Path(self.slave_db).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco master
        self._init_master_database()
        
        # Inicializar banco slave
        self._init_slave_database()
    
    def _init_master_database(self):
        """Inicializa banco de dados master"""
        conn = sqlite3.connect(self.master_db)
        
        # Criar tabelas principais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY,
                match_id TEXT NOT NULL,
                bet_type TEXT NOT NULL,
                stake REAL NOT NULL,
                odds REAL NOT NULL,
                profit_loss REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY,
                match_id TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                expected_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS replication_log (
                id INTEGER PRIMARY KEY,
                table_name TEXT NOT NULL,
                operation TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Criar índices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bets_match_id ON bets(match_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bets_timestamp ON bets(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_match_id ON predictions(match_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_replication_synced ON replication_log(synced)")
        
        conn.commit()
        conn.close()
        
        logger.info("Banco de dados master inicializado")
    
    def _init_slave_database(self):
        """Inicializa banco de dados slave"""
        conn = sqlite3.connect(self.slave_db)
        
        # Criar tabelas idênticas ao master
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY,
                match_id TEXT NOT NULL,
                bet_type TEXT NOT NULL,
                stake REAL NOT NULL,
                odds REAL NOT NULL,
                profit_loss REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY,
                match_id TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                expected_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS replication_status (
                id INTEGER PRIMARY KEY,
                last_sync DATETIME,
                last_record_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar índices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bets_match_id ON bets(match_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bets_timestamp ON bets(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_match_id ON predictions(match_id)")
        
        conn.commit()
        conn.close()
        
        logger.info("Banco de dados slave inicializado")
    
    def log_operation(self, table_name: str, operation: str, record_id: int, data: Dict):
        """Registra operação no log de replicação"""
        conn = sqlite3.connect(self.master_db)
        
        conn.execute("""
            INSERT INTO replication_log (table_name, operation, record_id, data)
            VALUES (?, ?, ?, ?)
        """, (table_name, operation, record_id, json.dumps(data)))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Operação registrada: {operation} em {table_name} (ID: {record_id})")
    
    def insert_bet(self, match_id: str, bet_type: str, stake: float, odds: float, 
                   profit_loss: float = None) -> int:
        """Insere aposta no master e registra para replicação"""
        conn = sqlite3.connect(self.master_db)
        
        cursor = conn.execute("""
            INSERT INTO bets (match_id, bet_type, stake, odds, profit_loss)
            VALUES (?, ?, ?, ?, ?)
        """, (match_id, bet_type, stake, odds, profit_loss))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Registrar para replicação
        data = {
            "match_id": match_id,
            "bet_type": bet_type,
            "stake": stake,
            "odds": odds,
            "profit_loss": profit_loss
        }
        self.log_operation("bets", "INSERT", record_id, data)
        
        logger.info(f"Aposta inserida: ID {record_id}")
        return record_id
    
    def insert_prediction(self, match_id: str, prediction: str, confidence: float, 
                         expected_value: float) -> int:
        """Insere predição no master e registra para replicação"""
        conn = sqlite3.connect(self.master_db)
        
        cursor = conn.execute("""
            INSERT INTO predictions (match_id, prediction, confidence, expected_value)
            VALUES (?, ?, ?, ?)
        """, (match_id, prediction, confidence, expected_value))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Registrar para replicação
        data = {
            "match_id": match_id,
            "prediction": prediction,
            "confidence": confidence,
            "expected_value": expected_value
        }
        self.log_operation("predictions", "INSERT", record_id, data)
        
        logger.info(f"Predição inserida: ID {record_id}")
        return record_id
    
    def update_bet(self, bet_id: int, **kwargs) -> bool:
        """Atualiza aposta no master e registra para replicação"""
        conn = sqlite3.connect(self.master_db)
        
        # Construir query de atualização
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['match_id', 'bet_type', 'stake', 'odds', 'profit_loss']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        values.append(bet_id)
        
        query = f"""
            UPDATE bets 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        cursor = conn.execute(query, values)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            # Registrar para replicação
            data = {"bet_id": bet_id, **kwargs}
            self.log_operation("bets", "UPDATE", bet_id, data)
            logger.info(f"Aposta atualizada: ID {bet_id}")
            return True
        
        return False
    
    def sync_to_slave(self) -> Tuple[bool, int]:
        """Sincroniza dados do master para o slave"""
        try:
            logger.debug("Iniciando sincronização para slave")
            
            # Obter registros não sincronizados
            master_conn = sqlite3.connect(self.master_db)
            slave_conn = sqlite3.connect(self.slave_db)
            
            cursor = master_conn.execute("""
                SELECT id, table_name, operation, record_id, data, timestamp
                FROM replication_log
                WHERE synced = FALSE
                ORDER BY timestamp
                LIMIT ?
            """, (self.batch_size,))
            
            records = cursor.fetchall()
            
            if not records:
                master_conn.close()
                slave_conn.close()
                return True, 0
            
            synced_count = 0
            
            for record in records:
                log_id, table_name, operation, record_id, data_json, timestamp = record
                
                try:
                    data = json.loads(data_json)
                    
                    if operation == "INSERT":
                        self._apply_insert(slave_conn, table_name, record_id, data)
                    elif operation == "UPDATE":
                        self._apply_update(slave_conn, table_name, record_id, data)
                    elif operation == "DELETE":
                        self._apply_delete(slave_conn, table_name, record_id)
                    
                    # Marcar como sincronizado
                    master_conn.execute("""
                        UPDATE replication_log 
                        SET synced = TRUE 
                        WHERE id = ?
                    """, (log_id,))
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao sincronizar registro {log_id}: {e}")
                    continue
            
            master_conn.commit()
            slave_conn.commit()
            
            # Atualizar status de sincronização
            slave_conn.execute("""
                INSERT OR REPLACE INTO replication_status (id, last_sync, last_record_id, status)
                VALUES (1, ?, ?, 'active')
            """, (datetime.now(), records[-1][0] if records else 0))
            
            slave_conn.commit()
            
            master_conn.close()
            slave_conn.close()
            
            self.last_sync = datetime.now()
            logger.info(f"Sincronização concluída: {synced_count} registros")
            
            return True, synced_count
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            return False, 0
    
    def _apply_insert(self, conn: sqlite3.Connection, table_name: str, record_id: int, data: Dict):
        """Aplica inserção no slave"""
        if table_name == "bets":
            conn.execute("""
                INSERT OR REPLACE INTO bets (id, match_id, bet_type, stake, odds, profit_loss, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (record_id, data["match_id"], data["bet_type"], data["stake"], 
                  data["odds"], data.get("profit_loss")))
        
        elif table_name == "predictions":
            conn.execute("""
                INSERT OR REPLACE INTO predictions (id, match_id, prediction, confidence, expected_value, timestamp)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (record_id, data["match_id"], data["prediction"], 
                  data["confidence"], data["expected_value"]))
    
    def _apply_update(self, conn: sqlite3.Connection, table_name: str, record_id: int, data: Dict):
        """Aplica atualização no slave"""
        if table_name == "bets":
            set_clauses = []
            values = []
            
            for key, value in data.items():
                if key != "bet_id" and key in ["match_id", "bet_type", "stake", "odds", "profit_loss"]:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if set_clauses:
                values.append(record_id)
                query = f"""
                    UPDATE bets 
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                conn.execute(query, values)
    
    def _apply_delete(self, conn: sqlite3.Connection, table_name: str, record_id: int):
        """Aplica exclusão no slave"""
        if table_name == "bets":
            conn.execute("DELETE FROM bets WHERE id = ?", (record_id,))
        elif table_name == "predictions":
            conn.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
    
    def start_replication(self):
        """Inicia replicação automática"""
        if self.is_replicating:
            logger.warning("Replicação já está ativa")
            return
        
        self.is_replicating = True
        
        # Agendar sincronização
        schedule.every(self.sync_interval).seconds.do(self.sync_to_slave)
        
        # Iniciar thread de replicação
        self.replication_thread = threading.Thread(target=self._replication_worker)
        self.replication_thread.daemon = True
        self.replication_thread.start()
        
        logger.info("Replicação automática iniciada")
    
    def stop_replication(self):
        """Para replicação automática"""
        self.is_replicating = False
        schedule.clear()
        logger.info("Replicação automática parada")
    
    def _replication_worker(self):
        """Worker de replicação"""
        while self.is_replicating:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Erro no worker de replicação: {e}")
                time.sleep(5)
    
    def get_replication_status(self) -> Dict:
        """Obtém status da replicação"""
        try:
            slave_conn = sqlite3.connect(self.slave_db)
            cursor = slave_conn.execute("""
                SELECT last_sync, last_record_id, status
                FROM replication_status
                WHERE id = 1
            """)
            
            result = cursor.fetchone()
            slave_conn.close()
            
            if result:
                last_sync, last_record_id, status = result
                return {
                    "status": status,
                    "last_sync": last_sync,
                    "last_record_id": last_record_id,
                    "is_replicating": self.is_replicating,
                    "sync_interval": self.sync_interval
                }
            else:
                return {
                    "status": "not_initialized",
                    "last_sync": None,
                    "last_record_id": 0,
                    "is_replicating": self.is_replicating,
                    "sync_interval": self.sync_interval
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter status da replicação: {e}")
            return {
                "status": "error",
                "error": str(e),
                "is_replicating": self.is_replicating
            }
    
    def promote_slave_to_master(self) -> bool:
        """Promove slave para master (failover)"""
        try:
            logger.info("Promovendo slave para master")
            
            # Parar replicação
            self.stop_replication()
            
            # Fazer backup do slave atual
            backup_file = f"slave_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            slave_conn = sqlite3.connect(self.slave_db)
            master_conn = sqlite3.connect(self.master_db)
            
            slave_conn.backup(master_conn)
            
            slave_conn.close()
            master_conn.close()
            
            # Atualizar configurações
            old_master = self.master_db
            self.master_db = self.slave_db
            self.slave_db = old_master
            
            logger.info("Slave promovido para master com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao promover slave: {e}")
            return False
    
    def verify_replication_integrity(self) -> Tuple[bool, str]:
        """Verifica integridade da replicação"""
        try:
            master_conn = sqlite3.connect(self.master_db)
            slave_conn = sqlite3.connect(self.slave_db)
            
            # Verificar contagem de registros
            master_bets = master_conn.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
            slave_bets = slave_conn.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
            
            master_predictions = master_conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
            slave_predictions = slave_conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
            
            master_conn.close()
            slave_conn.close()
            
            if master_bets != slave_bets:
                return False, f"Contagem de apostas diferente: Master {master_bets}, Slave {slave_bets}"
            
            if master_predictions != slave_predictions:
                return False, f"Contagem de predições diferente: Master {master_predictions}, Slave {slave_predictions}"
            
            return True, "Integridade da replicação verificada"
            
        except Exception as e:
            logger.error(f"Erro na verificação de integridade: {e}")
            return False, f"Erro: {str(e)}"

# Instância global
db_replication = DatabaseReplication("data/master.db", "data/slave.db")

if __name__ == "__main__":
    # Teste do sistema de replicação
    print("🧪 TESTANDO SISTEMA DE REPLICAÇÃO")
    print("=" * 40)
    
    # Inserir dados de teste
    bet_id = db_replication.insert_bet("39_12345", "home_win", 100.0, 1.85, 85.0)
    pred_id = db_replication.insert_prediction("39_12346", "home_win", 0.75, 0.12)
    
    print(f"Aposta inserida: ID {bet_id}")
    print(f"Predição inserida: ID {pred_id}")
    
    # Sincronizar
    success, count = db_replication.sync_to_slave()
    print(f"Sincronização: {'✅ Sucesso' if success else '❌ Falha'} ({count} registros)")
    
    # Verificar integridade
    is_integrity_ok, message = db_replication.verify_replication_integrity()
    print(f"Integridade: {'✅ OK' if is_integrity_ok else '❌ Falha'} - {message}")
    
    # Status da replicação
    status = db_replication.get_replication_status()
    print(f"Status: {status['status']}")
    print(f"Última sincronização: {status['last_sync']}")
    
    print("\n🎉 TESTES DE REPLICAÇÃO CONCLUÍDOS!")
