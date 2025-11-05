#!/usr/bin/env python3
"""
Script para executar o dashboard web do MaraBet AI
"""

import sys
import os
import uvicorn
import logging
from pathlib import Path

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from settings.api_keys import validate_keys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_requirements():
    """Verifica se todos os requisitos estão atendidos"""
    print("🔍 MARABET AI - VERIFICAÇÃO DE REQUISITOS")
    print("=" * 50)
    
    # Verificar se o diretório de templates existe
    templates_dir = Path("dashboard/templates")
    if not templates_dir.exists():
        print("❌ Diretório de templates não encontrado!")
        return False
    
    # Verificar se o arquivo HTML existe
    html_file = templates_dir / "dashboard.html"
    if not html_file.exists():
        print("❌ Arquivo dashboard.html não encontrado!")
        return False
    
    # Verificar se o diretório de arquivos estáticos existe
    static_dir = Path("dashboard/static")
    if not static_dir.exists():
        print("❌ Diretório de arquivos estáticos não encontrado!")
        return False
    
    # Verificar se o banco de dados existe
    db_file = Path("data/sports_data.db")
    if not db_file.exists():
        print("⚠️  Banco de dados não encontrado. Criando...")
        try:
            from armazenamento.banco_de_dados import Base, engine
            Base.metadata.create_all(engine)
            print("✅ Banco de dados criado!")
        except Exception as e:
            print(f"❌ Erro ao criar banco de dados: {e}")
            return False
    
    # Verificar API keys
    print("\n📋 Verificando configuração...")
    if not validate_keys():
        print("⚠️  API Keys não configuradas!")
        print("O dashboard funcionará com dados simulados.")
        print("Para dados reais, configure as API Keys no arquivo .env")
    else:
        print("✅ API Keys configuradas!")
    
    print("\n✅ Todos os requisitos verificados!")
    return True

def start_dashboard():
    """Inicia o dashboard"""
    print("\n🚀 MARABET AI - INICIANDO DASHBOARD")
    print("=" * 50)
    
    try:
        # Configurações do servidor
        host = "0.0.0.0"
        port = 8000
        reload = True
        
        print(f"🌐 Servidor: http://{host}:{port}")
        print(f"📊 Dashboard: http://localhost:{port}")
        print(f"📚 API Docs: http://localhost:{port}/docs")
        print(f"🔄 Reload: {'Ativado' if reload else 'Desativado'}")
        
        print("\n📋 FUNCIONALIDADES DISPONÍVEIS:")
        print("   • Dashboard principal com estatísticas")
        print("   • Visualização de predições em tempo real")
        print("   • Monitoramento de partidas")
        print("   • Métricas de performance")
        print("   • Controle do coletor automatizado")
        print("   • API REST completa")
        
        print("\n🎯 COMO USAR:")
        print("   1. Abra http://localhost:8000 no navegador")
        print("   2. Navegue pelas seções usando o menu lateral")
        print("   3. Use os botões para controlar o sistema")
        print("   4. Os dados são atualizados automaticamente")
        
        print("\n🛑 Para parar o servidor: Ctrl+C")
        print("\n" + "=" * 50)
        
        # Iniciar servidor
        uvicorn.run(
            "dashboard.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard parado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar dashboard: {e}")
        print(f"\n❌ Erro ao iniciar dashboard: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🎯 MARABET AI - DASHBOARD WEB INTERATIVO")
    print("=" * 60)
    
    # Verificar requisitos
    if not check_requirements():
        print("\n❌ Requisitos não atendidos. Verifique os erros acima.")
        sys.exit(1)
    
    # Iniciar dashboard
    start_dashboard()

if __name__ == "__main__":
    main()
