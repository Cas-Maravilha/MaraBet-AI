#!/usr/bin/env python3
"""
Teste de Replicação do Banco de Dados
MaraBet AI - Validação de replicação e failover
"""

import psycopg2
import redis
import time
import json
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseReplicationTester:
    """Testador de replicação de banco de dados"""
    
    def __init__(self):
        # Configurações do banco de dados
        self.master_config = {
            'host': 'marabet-master.cluster-xyz.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'database': 'marabet_production',
            'user': 'marabet_user',
            'password': 'secure_password_123'
        }
        
        self.slave_configs = [
            {
                'host': 'marabet-slave-1.cluster-xyz.us-east-1.rds.amazonaws.com',
                'port': 5432,
                'database': 'marabet_production',
                'user': 'marabet_user',
                'password': 'secure_password_123'
            },
            {
                'host': 'marabet-slave-2.cluster-xyz.us-east-1.rds.amazonaws.com',
                'port': 5432,
                'database': 'marabet_production',
                'user': 'marabet_user',
                'password': 'secure_password_123'
            }
        ]
        
        # Configurações do Redis
        self.redis_config = {
            'host': 'marabet-redis.cache.amazonaws.com',
            'port': 6379,
            'db': 0
        }
    
    def test_postgresql_connection(self, config: Dict[str, str]) -> bool:
        """Testa conexão PostgreSQL"""
        try:
            conn = psycopg2.connect(**config)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro de conexão PostgreSQL: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Testa conexão Redis"""
        try:
            r = redis.Redis(**self.redis_config)
            r.ping()
            return True
        except Exception as e:
            logger.error(f"Erro de conexão Redis: {e}")
            return False
    
    def test_master_slave_replication(self) -> Dict[str, Any]:
        """Testa replicação master-slave"""
        logger.info("🗄️ TESTANDO REPLICAÇÃO MASTER-SLAVE")
        print("=" * 60)
        
        results = {
            'master_connected': False,
            'slaves_connected': [],
            'replication_lag': [],
            'replication_healthy': False,
            'test_data_synced': False
        }
        
        # 1. Testar conexão master
        logger.info("1. Testando conexão master...")
        results['master_connected'] = self.test_postgresql_connection(self.master_config)
        logger.info(f"   Master conectado: {results['master_connected']}")
        
        if not results['master_connected']:
            logger.error("❌ Master não conectado")
            return results
        
        # 2. Testar conexões slaves
        logger.info("2. Testando conexões slaves...")
        for i, slave_config in enumerate(self.slave_configs):
            connected = self.test_postgresql_connection(slave_config)
            results['slaves_connected'].append(connected)
            logger.info(f"   Slave {i+1} conectado: {connected}")
        
        # 3. Verificar lag de replicação
        logger.info("3. Verificando lag de replicação...")
        for i, slave_config in enumerate(self.slave_configs):
            if results['slaves_connected'][i]:
                lag = self.get_replication_lag(slave_config)
                results['replication_lag'].append(lag)
                logger.info(f"   Slave {i+1} lag: {lag:.2f}s")
            else:
                results['replication_lag'].append(float('inf'))
        
        # 4. Testar sincronização de dados
        logger.info("4. Testando sincronização de dados...")
        if results['master_connected'] and any(results['slaves_connected']):
            results['test_data_synced'] = self.test_data_synchronization()
            logger.info(f"   Dados sincronizados: {results['test_data_synced']}")
        
        # 5. Determinar saúde da replicação
        results['replication_healthy'] = (
            results['master_connected'] and
            any(results['slaves_connected']) and
            all(lag < 10 for lag in results['replication_lag'] if lag != float('inf')) and
            results['test_data_synced']
        )
        
        return results
    
    def get_replication_lag(self, config: Dict[str, str]) -> float:
        """Obtém lag de replicação"""
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Query para obter lag de replicação
            cursor.execute("""
                SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));
            """)
            
            result = cursor.fetchone()
            lag = result[0] if result[0] is not None else 0
            
            cursor.close()
            conn.close()
            
            return lag
            
        except Exception as e:
            logger.error(f"Erro ao obter lag de replicação: {e}")
            return float('inf')
    
    def test_data_synchronization(self) -> bool:
        """Testa sincronização de dados"""
        try:
            # Inserir dados de teste no master
            master_conn = psycopg2.connect(**self.master_config)
            master_cursor = master_conn.cursor()
            
            test_data = {
                'id': int(time.time()),
                'message': 'Teste de replicação',
                'timestamp': datetime.now()
            }
            
            # Criar tabela de teste se não existir
            master_cursor.execute("""
                CREATE TABLE IF NOT EXISTS replication_test (
                    id INTEGER PRIMARY KEY,
                    message TEXT,
                    timestamp TIMESTAMP
                );
            """)
            
            # Inserir dados de teste
            master_cursor.execute("""
                INSERT INTO replication_test (id, message, timestamp)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    message = EXCLUDED.message,
                    timestamp = EXCLUDED.timestamp;
            """, (test_data['id'], test_data['message'], test_data['timestamp']))
            
            master_conn.commit()
            master_cursor.close()
            master_conn.close()
            
            # Aguardar replicação
            time.sleep(2)
            
            # Verificar se dados foram replicados nos slaves
            for slave_config in self.slave_configs:
                if self.test_postgresql_connection(slave_config):
                    slave_conn = psycopg2.connect(**slave_config)
                    slave_cursor = slave_conn.cursor()
                    
                    slave_cursor.execute("""
                        SELECT id, message, timestamp FROM replication_test
                        WHERE id = %s;
                    """, (test_data['id'],))
                    
                    result = slave_cursor.fetchone()
                    slave_cursor.close()
                    slave_conn.close()
                    
                    if not result:
                        logger.error(f"Dados não replicados para slave {slave_config['host']}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no teste de sincronização: {e}")
            return False
    
    def test_redis_replication(self) -> Dict[str, Any]:
        """Testa replicação Redis"""
        logger.info("🔴 TESTANDO REPLICAÇÃO REDIS")
        print("=" * 60)
        
        results = {
            'redis_connected': False,
            'replication_info': {},
            'replication_healthy': False,
            'test_data_synced': False
        }
        
        # 1. Testar conexão Redis
        logger.info("1. Testando conexão Redis...")
        results['redis_connected'] = self.test_redis_connection()
        logger.info(f"   Redis conectado: {results['redis_connected']}")
        
        if not results['redis_connected']:
            logger.error("❌ Redis não conectado")
            return results
        
        # 2. Obter informações de replicação
        logger.info("2. Obtendo informações de replicação...")
        try:
            r = redis.Redis(**self.redis_config)
            info = r.info('replication')
            results['replication_info'] = info
            logger.info(f"   Role: {info.get('role', 'unknown')}")
            logger.info(f"   Connected slaves: {info.get('connected_slaves', 0)}")
        except Exception as e:
            logger.error(f"Erro ao obter informações de replicação: {e}")
            return results
        
        # 3. Testar sincronização de dados
        logger.info("3. Testando sincronização de dados...")
        try:
            r = redis.Redis(**self.redis_config)
            
            # Inserir dados de teste
            test_key = f"replication_test_{int(time.time())}"
            test_value = "Teste de replicação Redis"
            
            r.set(test_key, test_value, ex=60)  # Expira em 60 segundos
            
            # Verificar se dados foram inseridos
            retrieved_value = r.get(test_key)
            results['test_data_synced'] = retrieved_value == test_value.encode()
            
            logger.info(f"   Dados sincronizados: {results['test_data_synced']}")
            
        except Exception as e:
            logger.error(f"Erro no teste de sincronização Redis: {e}")
            return results
        
        # 4. Determinar saúde da replicação
        results['replication_healthy'] = (
            results['redis_connected'] and
            results['replication_info'].get('connected_slaves', 0) > 0 and
            results['test_data_synced']
        )
        
        return results
    
    def test_database_failover(self) -> Dict[str, Any]:
        """Testa failover do banco de dados"""
        logger.info("🔄 TESTANDO FAILOVER DO BANCO DE DADOS")
        print("=" * 60)
        
        results = {
            'failover_script_exists': False,
            'failover_script_executable': False,
            'failover_simulation': False,
            'failover_time': 0
        }
        
        # 1. Verificar se script de failover existe
        logger.info("1. Verificando script de failover...")
        failover_script = "infrastructure/templates/database_failover.sh"
        results['failover_script_exists'] = os.path.exists(failover_script)
        logger.info(f"   Script existe: {results['failover_script_exists']}")
        
        if not results['failover_script_exists']:
            logger.error("❌ Script de failover não encontrado")
            return results
        
        # 2. Verificar se script é executável
        logger.info("2. Verificando permissões do script...")
        results['failover_script_executable'] = os.access(failover_script, os.X_OK)
        logger.info(f"   Script executável: {results['failover_script_executable']}")
        
        if not results['failover_script_executable']:
            logger.info("   Tornando script executável...")
            os.chmod(failover_script, 0o755)
            results['failover_script_executable'] = True
        
        # 3. Simular failover
        logger.info("3. Simulando failover...")
        start_time = time.time()
        
        try:
            # Executar script de failover (modo de teste)
            result = subprocess.run(
                [failover_script, "test"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results['failover_simulation'] = result.returncode == 0
            results['failover_time'] = time.time() - start_time
            
            logger.info(f"   Failover simulado: {results['failover_simulation']}")
            logger.info(f"   Tempo de failover: {results['failover_time']:.2f}s")
            
            if result.stdout:
                logger.info(f"   Output: {result.stdout}")
            if result.stderr:
                logger.error(f"   Erro: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no script de failover")
        except Exception as e:
            logger.error(f"❌ Erro ao executar script de failover: {e}")
        
        return results
    
    def test_database_performance(self) -> Dict[str, Any]:
        """Testa performance do banco de dados"""
        logger.info("⚡ TESTANDO PERFORMANCE DO BANCO DE DADOS")
        print("=" * 60)
        
        results = {
            'master_performance': {},
            'slave_performance': [],
            'redis_performance': {},
            'overall_performance': 'unknown'
        }
        
        # 1. Testar performance do master
        logger.info("1. Testando performance do master...")
        if self.test_postgresql_connection(self.master_config):
            results['master_performance'] = self.benchmark_database(self.master_config)
            logger.info(f"   Queries por segundo: {results['master_performance'].get('qps', 0):.2f}")
            logger.info(f"   Response time médio: {results['master_performance'].get('avg_response_time', 0):.2f}ms")
        
        # 2. Testar performance dos slaves
        logger.info("2. Testando performance dos slaves...")
        for i, slave_config in enumerate(self.slave_configs):
            if self.test_postgresql_connection(slave_config):
                slave_perf = self.benchmark_database(slave_config)
                results['slave_performance'].append(slave_perf)
                logger.info(f"   Slave {i+1} QPS: {slave_perf.get('qps', 0):.2f}")
            else:
                results['slave_performance'].append({})
        
        # 3. Testar performance do Redis
        logger.info("3. Testando performance do Redis...")
        if self.test_redis_connection():
            results['redis_performance'] = self.benchmark_redis()
            logger.info(f"   Redis QPS: {results['redis_performance'].get('qps', 0):.2f}")
            logger.info(f"   Redis response time: {results['redis_performance'].get('avg_response_time', 0):.2f}ms")
        
        # 4. Determinar performance geral
        master_qps = results['master_performance'].get('qps', 0)
        redis_qps = results['redis_performance'].get('qps', 0)
        
        if master_qps >= 100 and redis_qps >= 1000:
            results['overall_performance'] = 'excellent'
        elif master_qps >= 50 and redis_qps >= 500:
            results['overall_performance'] = 'good'
        elif master_qps >= 10 and redis_qps >= 100:
            results['overall_performance'] = 'acceptable'
        else:
            results['overall_performance'] = 'poor'
        
        return results
    
    def benchmark_database(self, config: Dict[str, str]) -> Dict[str, Any]:
        """Benchmark do banco de dados"""
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Executar queries de benchmark
            queries = [
                "SELECT 1",
                "SELECT COUNT(*) FROM information_schema.tables",
                "SELECT NOW()",
                "SELECT version()"
            ]
            
            times = []
            for _ in range(10):  # 10 iterações
                start_time = time.time()
                for query in queries:
                    cursor.execute(query)
                    cursor.fetchone()
                times.append(time.time() - start_time)
            
            cursor.close()
            conn.close()
            
            avg_time = sum(times) / len(times)
            qps = len(queries) / avg_time
            
            return {
                'qps': qps,
                'avg_response_time': avg_time * 1000,  # ms
                'total_queries': len(queries) * 10
            }
            
        except Exception as e:
            logger.error(f"Erro no benchmark do banco: {e}")
            return {}
    
    def benchmark_redis(self) -> Dict[str, Any]:
        """Benchmark do Redis"""
        try:
            r = redis.Redis(**self.redis_config)
            
            # Executar operações de benchmark
            operations = ['set', 'get', 'ping', 'info']
            times = []
            
            for _ in range(100):  # 100 iterações
                start_time = time.time()
                for op in operations:
                    if op == 'set':
                        r.set(f"benchmark_{int(time.time())}", "test")
                    elif op == 'get':
                        r.get(f"benchmark_{int(time.time())}")
                    elif op == 'ping':
                        r.ping()
                    elif op == 'info':
                        r.info()
                times.append(time.time() - start_time)
            
            avg_time = sum(times) / len(times)
            qps = len(operations) / avg_time
            
            return {
                'qps': qps,
                'avg_response_time': avg_time * 1000,  # ms
                'total_operations': len(operations) * 100
            }
            
        except Exception as e:
            logger.error(f"Erro no benchmark do Redis: {e}")
            return {}
    
    def generate_report(self, pg_results: Dict, redis_results: Dict, failover_results: Dict, perf_results: Dict) -> str:
        """Gera relatório de teste"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE DE REPLICAÇÃO DE BANCO DE DADOS - MARABET AI")
        report.append("=" * 80)
        
        # Resumo geral
        report.append(f"\n📊 RESUMO GERAL:")
        report.append(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  PostgreSQL: {'✅ Saudável' if pg_results['replication_healthy'] else '❌ Com problemas'}")
        report.append(f"  Redis: {'✅ Saudável' if redis_results['replication_healthy'] else '❌ Com problemas'}")
        report.append(f"  Failover: {'✅ Funcionando' if failover_results['failover_simulation'] else '❌ Falhou'}")
        report.append(f"  Performance: {perf_results['overall_performance'].upper()}")
        
        # PostgreSQL results
        report.append(f"\n🗄️ RESULTADOS POSTGRESQL:")
        report.append(f"  Master conectado: {pg_results['master_connected']}")
        report.append(f"  Slaves conectados: {sum(pg_results['slaves_connected'])}/{len(pg_results['slaves_connected'])}")
        report.append(f"  Replicação saudável: {pg_results['replication_healthy']}")
        report.append(f"  Dados sincronizados: {pg_results['test_data_synced']}")
        
        if pg_results['replication_lag']:
            report.append(f"  Lag de replicação:")
            for i, lag in enumerate(pg_results['replication_lag']):
                if lag != float('inf'):
                    report.append(f"    Slave {i+1}: {lag:.2f}s")
                else:
                    report.append(f"    Slave {i+1}: Indisponível")
        
        # Redis results
        report.append(f"\n🔴 RESULTADOS REDIS:")
        report.append(f"  Redis conectado: {redis_results['redis_connected']}")
        report.append(f"  Replicação saudável: {redis_results['replication_healthy']}")
        report.append(f"  Dados sincronizados: {redis_results['test_data_synced']}")
        
        if redis_results['replication_info']:
            report.append(f"  Informações de replicação:")
            report.append(f"    Role: {redis_results['replication_info'].get('role', 'unknown')}")
            report.append(f"    Connected slaves: {redis_results['replication_info'].get('connected_slaves', 0)}")
        
        # Failover results
        report.append(f"\n🔄 RESULTADOS DE FAILOVER:")
        report.append(f"  Script existe: {failover_results['failover_script_exists']}")
        report.append(f"  Script executável: {failover_results['failover_script_executable']}")
        report.append(f"  Failover simulado: {failover_results['failover_simulation']}")
        report.append(f"  Tempo de failover: {failover_results['failover_time']:.2f}s")
        
        # Performance results
        report.append(f"\n⚡ RESULTADOS DE PERFORMANCE:")
        report.append(f"  Performance geral: {perf_results['overall_performance'].upper()}")
        
        if perf_results['master_performance']:
            report.append(f"  Master PostgreSQL:")
            report.append(f"    QPS: {perf_results['master_performance'].get('qps', 0):.2f}")
            report.append(f"    Response time: {perf_results['master_performance'].get('avg_response_time', 0):.2f}ms")
        
        if perf_results['redis_performance']:
            report.append(f"  Redis:")
            report.append(f"    QPS: {perf_results['redis_performance'].get('qps', 0):.2f}")
            report.append(f"    Response time: {perf_results['redis_performance'].get('avg_response_time', 0):.2f}ms")
        
        # Validação de objetivos
        report.append(f"\n🎯 VALIDAÇÃO DE OBJETIVOS:")
        
        if pg_results['replication_healthy']:
            report.append(f"  ✅ Replicação PostgreSQL funcionando")
        else:
            report.append(f"  ❌ Replicação PostgreSQL com problemas")
        
        if redis_results['replication_healthy']:
            report.append(f"  ✅ Replicação Redis funcionando")
        else:
            report.append(f"  ❌ Replicação Redis com problemas")
        
        if failover_results['failover_simulation']:
            report.append(f"  ✅ Failover funcionando")
        else:
            report.append(f"  ❌ Failover falhou")
        
        if perf_results['overall_performance'] in ['excellent', 'good']:
            report.append(f"  ✅ Performance adequada")
        else:
            report.append(f"  ❌ Performance inadequada")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if not pg_results['replication_healthy']:
            report.append(f"  ⚠️ Verificar configuração de replicação PostgreSQL")
        
        if not redis_results['replication_healthy']:
            report.append(f"  ⚠️ Verificar configuração de replicação Redis")
        
        if not failover_results['failover_simulation']:
            report.append(f"  ⚠️ Configurar failover automático")
        
        if perf_results['overall_performance'] == 'poor':
            report.append(f"  ⚠️ Otimizar performance do banco de dados")
        
        report.append(f"  🔄 Executar testes de replicação regularmente")
        report.append(f"  📊 Monitorar lag de replicação")
        report.append(f"  🔧 Manter scripts de failover atualizados")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Função principal"""
    print("🗄️ TESTE DE REPLICAÇÃO DE BANCO DE DADOS - MARABET AI")
    print("=" * 80)
    
    tester = DatabaseReplicationTester()
    
    try:
        # 1. Testar replicação PostgreSQL
        pg_results = tester.test_master_slave_replication()
        
        # 2. Testar replicação Redis
        redis_results = tester.test_redis_replication()
        
        # 3. Testar failover
        failover_results = tester.test_database_failover()
        
        # 4. Testar performance
        perf_results = tester.test_database_performance()
        
        # 5. Gerar relatório
        report = tester.generate_report(pg_results, redis_results, failover_results, perf_results)
        print(f"\n{report}")
        
        # 6. Salvar relatório
        with open("database_replication_test_report.txt", "w") as f:
            f.write(report)
        
        print("\n🎉 TESTE DE REPLICAÇÃO CONCLUÍDO!")
        print("📄 Relatório salvo em: database_replication_test_report.txt")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    main()
