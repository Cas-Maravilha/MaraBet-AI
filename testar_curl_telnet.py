#!/usr/bin/env python3
"""
Teste de Conectividade usando curl (equivalente)
MaraBet AI - Teste de conexão TCP usando Python
"""

import socket
import sys

def testar_conexao_curl_style(host, port, timeout=5):
    """
    Testa conectividade TCP no estilo curl -v telnet://
    
    Args:
        host: Endereço IP ou hostname
        port: Porta TCP
        timeout: Timeout em segundos
    
    Returns:
        bool: True se a conexão foi bem-sucedida
    """
    print(f"*   Trying {host}:{port}...")
    sys.stdout.flush()
    
    try:
        # Criar socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Tentar conectar
        result = sock.connect_ex((host, port))
        
        if result == 0:
            # Conexão bem-sucedida
            print(f"* Connected to {host} ({host}) port {port} (#0)")
            print(f"*   Trying {host}:{port}...")
            print(f"* Connected to {host} ({host}) port {port} (#0)")
            print(f"> GET / HTTP/1.1")
            print(f"> Host: {host}:{port}")
            print(f"> User-Agent: curl/7.81.0")
            print(f"> Accept: */*")
            print(f">")
            
            # Fechar conexão
            sock.close()
            print(f"* Closing connection 0")
            print(f"✅ Conexão TCP bem-sucedida!")
            return True
        else:
            print(f"* Failed to connect to {host} port {port}: Connection refused")
            print(f"❌ Conexão TCP falhou!")
            print(f"   Código de erro: {result}")
            sock.close()
            return False
            
    except socket.timeout:
        print(f"* Failed to connect to {host} port {port}: Connection timed out")
        print(f"❌ Timeout ao conectar!")
        return False
    except socket.gaierror as e:
        print(f"* Failed to resolve host: {host}")
        print(f"❌ Erro de resolução DNS!")
        print(f"   Erro: {e}")
        return False
    except Exception as e:
        print(f"* Failed to connect to {host} port {port}: {e}")
        print(f"❌ Erro ao testar conexão!")
        print(f"   Erro: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TESTE DE CONECTIVIDADE (estilo curl -v telnet://)")
    print("=" * 60)
    print()
    
    # Testar PostgreSQL (porta 5432)
    print("=" * 60)
    print("TESTE 1: PostgreSQL (porta 5432)")
    print("=" * 60)
    print()
    print("curl -v telnet://37.27.220.67:5432")
    print()
    postgres_ok = testar_conexao_curl_style("37.27.220.67", 5432)
    
    print()
    print()
    
    # Testar MySQL (porta 3306)
    print("=" * 60)
    print("TESTE 2: MySQL (porta 3306)")
    print("=" * 60)
    print()
    print("curl -v telnet://37.27.220.67:3306")
    print()
    mysql_ok = testar_conexao_curl_style("37.27.220.67", 3306)
    
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

