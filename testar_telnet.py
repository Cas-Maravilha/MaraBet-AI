#!/usr/bin/env python3
"""
Teste de Conectividade TCP (equivalente ao telnet)
MaraBet AI - Teste de conexão TCP direta
"""

import socket
import sys

def testar_conexao_tcp(host, port, timeout=5):
    """
    Testa conectividade TCP (equivalente ao telnet)
    
    Args:
        host: Endereço IP ou hostname
        port: Porta TCP
        timeout: Timeout em segundos
    
    Returns:
        bool: True se a conexão foi bem-sucedida
    """
    try:
        print(f"🔍 Testando conexão TCP: {host}:{port}")
        print(f"   Timeout: {timeout} segundos")
        print()
        
        # Criar socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Tentar conectar
        print(f"🔄 Tentando conectar...")
        result = sock.connect_ex((host, port))
        
        # Fechar socket
        sock.close()
        
        if result == 0:
            print(f"✅ Conexão TCP bem-sucedida!")
            print(f"   Host: {host}")
            print(f"   Porta: {port}")
            print(f"   Status: Porta acessível")
            return True
        else:
            print(f"❌ Conexão TCP falhou!")
            print(f"   Host: {host}")
            print(f"   Porta: {port}")
            print(f"   Status: Porta não acessível ou fechada")
            print(f"   Código de erro: {result}")
            return False
            
    except socket.timeout:
        print(f"❌ Timeout ao conectar!")
        print(f"   Host: {host}")
        print(f"   Porta: {port}")
        print(f"   Timeout: {timeout} segundos")
        return False
    except socket.gaierror as e:
        print(f"❌ Erro de resolução DNS!")
        print(f"   Host: {host}")
        print(f"   Erro: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar conexão!")
        print(f"   Host: {host}")
        print(f"   Porta: {port}")
        print(f"   Erro: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TESTE DE CONECTIVIDADE TCP (equivalente ao telnet)")
    print("=" * 60)
    print()
    
    # Testar PostgreSQL (porta 5432)
    print("=" * 60)
    print("TESTE 1: PostgreSQL (porta 5432)")
    print("=" * 60)
    print()
    postgres_ok = testar_conexao_tcp("37.27.220.67", 5432)
    
    print()
    
    # Testar MySQL (porta 3306)
    print("=" * 60)
    print("TESTE 2: MySQL (porta 3306)")
    print("=" * 60)
    print()
    mysql_ok = testar_conexao_tcp("37.27.220.67", 3306)
    
    print()
    print("=" * 60)
    print("📋 RESUMO")
    print("=" * 60)
    print()
    print(f"PostgreSQL (porta 5432): {'✅ Acessível' if postgres_ok else '❌ Não acessível'}")
    print(f"MySQL (porta 3306): {'✅ Acessível' if mysql_ok else '❌ Não acessível'}")
    print()
    print("=" * 60)
    
    # Exit code baseado nos resultados
    sys.exit(0 if postgres_ok else 1)

