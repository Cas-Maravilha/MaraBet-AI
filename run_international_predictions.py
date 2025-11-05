#!/usr/bin/env python3
"""
Execução Automática do Sistema de Competições Internacionais
MaraBet AI - Executa predições para todas as competições internacionais
"""

import sys
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_international_predictions():
    """Executa predições internacionais automaticamente"""
    print("🌍 SISTEMA DE COMPETIÇÕES INTERNACIONAIS - MARABET AI")
    print("=" * 80)
    
    try:
        # Importar o sistema internacional
        from international_competitions_system import InternationalCompetitionsSystem
        
        # Criar instância do sistema
        predictor = InternationalCompetitionsSystem()
        
        print("🚀 EXECUTANDO PREDIÇÕES INTERNACIONAIS AUTOMATICAMENTE")
        print("=" * 60)
        
        # 1. Executar predições de hoje
        print("\n📅 EXECUTANDO PREDIÇÕES DE HOJE...")
        print("-" * 40)
        success_today = predictor.run_international_predictions("today")
        
        # 2. Executar predições ao vivo
        print("\n🔴 EXECUTANDO PREDIÇÕES AO VIVO...")
        print("-" * 40)
        success_live = predictor.run_international_predictions("live")
        
        # 3. Executar predições futuras
        print("\n🔮 EXECUTANDO PREDIÇÕES FUTURAS...")
        print("-" * 40)
        success_future = predictor.run_international_predictions("future")
        
        # Resumo final
        print("\n🎯 RESUMO DA EXECUÇÃO:")
        print("=" * 50)
        print(f"📅 Predições de hoje: {'✅ Sucesso' if success_today else '❌ Falhou'}")
        print(f"🔴 Predições ao vivo: {'✅ Sucesso' if success_live else '❌ Falhou'}")
        print(f"🔮 Predições futuras: {'✅ Sucesso' if success_future else '❌ Falhou'}")
        
        total_success = sum([success_today, success_live, success_future])
        print(f"\n📊 Total de execuções bem-sucedidas: {total_success}/3")
        
        if total_success > 0:
            print("\n🎉 SISTEMA DE COMPETIÇÕES INTERNACIONAIS EXECUTADO COM SUCESSO!")
            print("🌍 Cobertura global completa implementada e funcionando!")
        else:
            print("\n❌ Nenhuma execução foi bem-sucedida")
            print("🔍 Verifique a configuração da API e conexão com internet")
        
        return total_success > 0
        
    except ImportError as e:
        print(f"❌ Erro ao importar sistema internacional: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False

def main():
    """Função principal"""
    return run_international_predictions()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
