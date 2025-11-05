#!/usr/bin/env python3
"""
Script de Migração de Banco de Dados - MaraBet AI
Executa migrações SQL no banco de dados PostgreSQL
"""

import os
import sys
import psycopg2
from datetime import datetime

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'marabet'),
    'user': os.getenv('DB_USER', 'marabetuser'),
    'password': os.getenv('DB_PASSWORD', 'changeme')
}

def print_header(text):
    print("\n" + "=" * 80)
    print(f"📊 {text}")
    print("=" * 80)

def connect_db():
    """Conecta ao banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Conectado ao banco: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        sys.exit(1)

def get_executed_migrations(conn):
    """Retorna lista de migrações já executadas"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(20) PRIMARY KEY,
                description TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"⚠️  Erro ao verificar migrações: {e}")
        return []

def execute_migration(conn, filepath, version):
    """Executa um arquivo de migração"""
    try:
        print(f"\n🔄 Executando migração: {version}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Registrar migração executada
        cursor.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
            (version, f"Migração {version}")
        )
        
        conn.commit()
        print(f"✅ Migração {version} executada com sucesso!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao executar migração {version}: {e}")
        return False

def execute_seeds(conn, filepath):
    """Executa arquivo de seeds"""
    try:
        print(f"\n🌱 Executando seeds...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        
        print(f"✅ Seeds executados com sucesso!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"⚠️  Aviso ao executar seeds: {e}")
        return False

def backup_database(conn):
    """Cria backup do banco antes das migrações"""
    try:
        backup_file = f"migrations/backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        print(f"\n💾 Criando backup: {backup_file}")
        
        os.system(f"pg_dump -h {DB_CONFIG['host']} -U {DB_CONFIG['user']} -d {DB_CONFIG['database']} > {backup_file}")
        
        print(f"✅ Backup criado com sucesso!")
        return True
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível criar backup: {e}")
        return False

def rollback_migration(conn, version):
    """Reverte uma migração (se houver arquivo de rollback)"""
    rollback_file = f"migrations/rollback_{version}.sql"
    
    if not os.path.exists(rollback_file):
        print(f"❌ Arquivo de rollback não encontrado: {rollback_file}")
        return False
    
    try:
        print(f"\n↩️  Revertendo migração: {version}")
        
        with open(rollback_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Remover da tabela de migrações
        cursor.execute("DELETE FROM schema_migrations WHERE version = %s", (version,))
        
        conn.commit()
        print(f"✅ Migração {version} revertida com sucesso!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao reverter migração {version}: {e}")
        return False

def verify_database(conn):
    """Verifica estrutura do banco"""
    try:
        print(f"\n🔍 Verificando estrutura do banco...")
        
        cursor = conn.cursor()
        
        # Contar tabelas
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"📊 Tabelas: {table_count}")
        
        # Contar índices
        cursor.execute("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE schemaname = 'public'
        """)
        index_count = cursor.fetchone()[0]
        print(f"📑 Índices: {index_count}")
        
        # Listar migrações executadas
        cursor.execute("SELECT version, executed_at FROM schema_migrations ORDER BY version")
        migrations = cursor.fetchall()
        
        if migrations:
            print(f"\n✅ Migrações executadas ({len(migrations)}):")
            for version, executed_at in migrations:
                print(f"   • {version} - {executed_at}")
        
        return True
    except Exception as e:
        print(f"⚠️  Erro ao verificar banco: {e}")
        return False

def main():
    """Função principal"""
    print_header("MARABET AI - SISTEMA DE MIGRAÇÕES")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📞 Contato: +224 932027393")
    
    # Argumentos
    import argparse
    parser = argparse.ArgumentParser(description='Sistema de Migrações MaraBet AI')
    parser.add_argument('--migrate', action='store_true', help='Executar migrações pendentes')
    parser.add_argument('--seed', action='store_true', help='Executar seeds')
    parser.add_argument('--rollback', metavar='VERSION', help='Reverter migração específica')
    parser.add_argument('--verify', action='store_true', help='Verificar estrutura do banco')
    parser.add_argument('--backup', action='store_true', help='Criar backup do banco')
    
    args = parser.parse_args()
    
    # Conectar ao banco
    conn = connect_db()
    
    try:
        # Backup (se solicitado ou antes de migrar)
        if args.backup or args.migrate:
            backup_database(conn)
        
        # Executar migrações
        if args.migrate:
            print_header("EXECUTANDO MIGRAÇÕES")
            
            # Obter migrações já executadas
            executed = get_executed_migrations(conn)
            print(f"📋 Migrações já executadas: {len(executed)}")
            
            # Buscar arquivos de migração
            migration_files = sorted([
                f for f in os.listdir('migrations') 
                if f.endswith('.sql') and f[0].isdigit()
            ])
            
            if not migration_files:
                print("⚠️  Nenhuma migração encontrada!")
            else:
                # Executar migrações pendentes
                for migration_file in migration_files:
                    version = migration_file.split('_')[0]
                    
                    if version not in executed:
                        filepath = os.path.join('migrations', migration_file)
                        success = execute_migration(conn, filepath, version)
                        
                        if not success:
                            print(f"❌ Falha na migração {version}. Abortando...")
                            sys.exit(1)
                    else:
                        print(f"⏭️  Migração {version} já executada")
        
        # Executar seeds
        if args.seed:
            print_header("EXECUTANDO SEEDS")
            seed_file = 'migrations/seeds/dev_seeds.sql'
            
            if os.path.exists(seed_file):
                execute_seeds(conn, seed_file)
            else:
                print(f"⚠️  Arquivo de seeds não encontrado: {seed_file}")
        
        # Rollback
        if args.rollback:
            print_header(f"REVERTENDO MIGRAÇÃO {args.rollback}")
            rollback_migration(conn, args.rollback)
        
        # Verificar estrutura
        if args.verify or args.migrate:
            verify_database(conn)
        
        # Se nenhum argumento, mostrar ajuda
        if not any([args.migrate, args.seed, args.rollback, args.verify, args.backup]):
            parser.print_help()
            print("\n📋 Exemplos de uso:")
            print("   python migrate.py --migrate          # Executar migrações")
            print("   python migrate.py --migrate --seed   # Migrar e adicionar seeds")
            print("   python migrate.py --verify           # Verificar estrutura")
            print("   python migrate.py --rollback 001     # Reverter migração 001")
            print("   python migrate.py --backup           # Criar backup")
        
        print(f"\n🎉 OPERAÇÃO CONCLUÍDA COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
    finally:
        conn.close()
        print(f"\n📊 Conexão fechada")

if __name__ == "__main__":
    main()
