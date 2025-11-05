#!/usr/bin/env python3
"""
Script de teste de conexão PostgreSQL remota
Testa conexão ao servidor remoto 37.27.220.67
"""

import sys
import psycopg2
from datetime import datetime

# Configurações de conexão
CONFIG = {
    "host": "37.27.220.67",
    "port": "5432",
    "database": "marabet",
    "user": "meu_root$marabet",
    "password": "dudbeeGdNBSxjpEWlop"
}

# Cores para output (opcional)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    """Imprime informação"""
    print(f"{Colors.YELLOW}💡 {text}{Colors.RESET}")

def test_basic_connection():
    """Testa conexão básica ao PostgreSQL"""
    print_header("TESTE 1: Conexão Básica ao PostgreSQL")
    
    try:
        print(f"🔄 Tentando conectar...")
        print(f"   Host: {CONFIG['host']}")
        print(f"   Porta: {CONFIG['port']}")
        print(f"   Database: {CONFIG['database']}")
        print(f"   User: {CONFIG['user']}")
        print()
        
        conn = psycopg2.connect(**CONFIG)
        print_success("Conexão estabelecida com sucesso!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user, now();")
        result = cursor.fetchone()
        
        print(f"\n📊 Informações da conexão:")
        print(f"   PostgreSQL: {result[0]}")
        print(f"   Database: {result[1]}")
        print(f"   User: {result[2]}")
        print(f"   Data/Hora Servidor: {result[3]}")
        
        cursor.close()
        conn.close()
        print_success("Conexão fechada com sucesso!")
        return True
        
    except psycopg2.OperationalError as e:
        print_error(f"Erro de conexão: {e}")
        print_info("Verificações necessárias:")
        print("   1. Servidor PostgreSQL está em execução?")
        print("   2. Firewall permite conexões na porta 5432?")
        print("   3. postgresql.conf tem listen_addresses = '*'?")
        print("   4. pg_hba.conf permite conexões remotas?")
        return False
        
    except psycopg2.ProgrammingError as e:
        print_error(f"Erro de programação: {e}")
        return False
        
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False

def test_database_operations():
    """Testa operações no banco de dados"""
    print_header("TESTE 2: Operações no Banco de Dados")
    
    try:
        conn = psycopg2.connect(**CONFIG)
        cursor = conn.cursor()
        
        # Teste 1: Listar tabelas
        print("📋 Testando: Listar tabelas do banco...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        if tables:
            print_success(f"Tabelas encontradas: {len(tables)}")
            for table in tables[:5]:  # Mostrar apenas as primeiras 5
                print(f"   - {table[0]}")
            if len(tables) > 5:
                print(f"   ... e mais {len(tables) - 5} tabelas")
        else:
            print_info("Nenhuma tabela encontrada no banco (banco vazio)")
        
        # Teste 2: Criar tabela de teste
        print("\n📝 Testando: Criar tabela de teste...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teste_conexao (
                id SERIAL PRIMARY KEY,
                data_teste TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mensagem TEXT
            );
        """)
        print_success("Tabela de teste criada/verificada")
        
        # Teste 3: Inserir dados
        print("\n📥 Testando: Inserir dados...")
        cursor.execute("""
            INSERT INTO teste_conexao (mensagem) 
            VALUES ('Teste de conexão realizada em %s');
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
        conn.commit()
        print_success("Dados inseridos com sucesso")
        
        # Teste 4: Ler dados
        print("\n📤 Testando: Ler dados...")
        cursor.execute("SELECT COUNT(*) FROM teste_conexao;")
        count = cursor.fetchone()[0]
        print_success(f"Dados lidos: {count} registro(s) na tabela de teste")
        
        # Teste 5: Remover tabela de teste (opcional)
        print("\n🧹 Limpando tabela de teste...")
        cursor.execute("DROP TABLE IF EXISTS teste_conexao;")
        conn.commit()
        print_success("Tabela de teste removida")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Erro nas operações: {e}")
        return False

def test_connection_performance():
    """Testa performance da conexão"""
    print_header("TESTE 3: Performance da Conexão")
    
    try:
        import time
        
        print("⏱️  Medindo tempo de conexão...")
        start_time = time.time()
        conn = psycopg2.connect(**CONFIG)
        connection_time = time.time() - start_time
        
        print_success(f"Tempo de conexão: {connection_time*1000:.2f} ms")
        
        # Teste de query simples
        print("\n⏱️  Medindo tempo de query...")
        cursor = conn.cursor()
        start_time = time.time()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        query_time = time.time() - start_time
        
        print_success(f"Tempo de query: {query_time*1000:.2f} ms")
        
        # Avaliar latência
        if connection_time < 0.1:
            print_success("Latência EXCELENTE (< 100ms)")
        elif connection_time < 0.5:
            print_info("Latência BOA (< 500ms)")
        elif connection_time < 2.0:
            print_info("Latência ACEITÁVEL (< 2s)")
        else:
            print_error("Latência ALTA (> 2s) - verifique a rede")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Erro no teste de performance: {e}")
        return False

def main():
    """Função principal"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     TESTE DE CONEXÃO POSTGRESQL REMOTA                    ║")
    print("║     Servidor: 37.27.220.67:5432                          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    results = []
    
    # Teste 1: Conexão básica
    results.append(("Conexão Básica", test_basic_connection()))
    
    # Teste 2: Operações no banco (só se conexão básica funcionou)
    if results[0][1]:
        results.append(("Operações no Banco", test_database_operations()))
        results.append(("Performance", test_connection_performance()))
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSOU")
        else:
            print_error(f"{test_name}: FALHOU")
    
    print(f"\n📊 Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print_success("\n🎉 TODOS OS TESTES PASSARAM! Conexão funcionando perfeitamente!")
        return 0
    else:
        print_error(f"\n⚠️  {total - passed} teste(s) falharam. Verifique as configurações.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)

