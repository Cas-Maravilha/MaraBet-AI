#!/usr/bin/env python3
"""
Demonstração do Sistema Básico - MaraBet AI
Mostra todas as funcionalidades do sistema econômico
"""

import sys
import os
import time
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import SportsDataSystem

def show_system_info():
    """Mostra informações do sistema"""
    print("🏈 SISTEMA BÁSICO DE DADOS ESPORTIVOS - MARABET AI")
    print("=" * 70)
    print("""
🎯 CARACTERÍSTICAS:
   • 💰 Econômico: SQLite + APIs gratuitas
   • 🚀 Rápido: Processamento local
   • 📊 Completo: Coleta, processamento, análise
   • 🤖 ML: Modelos de machine learning
   • 📈 Análise: Identificação de value bets
   • 🔧 Simples: Fácil configuração

🏗️ ARQUITETURA:
   • Coletores: API-Football, Odds (simulado)
   • Processadores: Estatísticas, ML
   • Armazenamento: SQLite local
   • Análise: Predições e value bets
   • Utilitários: Cache, logging

📊 FUNCIONALIDADES:
   • Coleta de dados esportivos
   • Processamento e estatísticas
   • Predições com ML
   • Identificação de value bets
   • Armazenamento local
   • Sistema de cache
   • Logging detalhado
""")

def demonstrate_data_collection():
    """Demonstra coleta de dados"""
    print("\n📡 DEMONSTRAÇÃO DE COLETA DE DADOS")
    print("=" * 50)
    
    try:
        system = SportsDataSystem()
        
        print("1. Coletando dados de ligas...")
        leagues_data = system.collect_data(['leagues'])
        print(f"   ✅ Coletadas {len(leagues_data.get('leagues', []))} ligas")
        
        print("2. Coletando dados de times...")
        teams_data = system.collect_data(['teams'], league_id=39, season=2024)
        print(f"   ✅ Coletados {len(teams_data.get('teams', []))} times")
        
        print("3. Coletando partidas...")
        fixtures_data = system.collect_data(['fixtures'], league_id=39, season=2024)
        print(f"   ✅ Coletadas {len(fixtures_data.get('fixtures', []))} partidas")
        
        print("4. Coletando odds...")
        odds_data = system.collect_data(['match_odds'], 
                                      home_team="Manchester City", 
                                      away_team="Arsenal")
        print(f"   ✅ Coletadas {len(odds_data.get('match_odds', []))} odds")
        
        system.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na coleta: {e}")
        return False

def demonstrate_data_processing():
    """Demonstra processamento de dados"""
    print("\n⚙️ DEMONSTRAÇÃO DE PROCESSAMENTO")
    print("=" * 50)
    
    try:
        system = SportsDataSystem()
        
        # Dados simulados para demonstração
        sample_data = {
            'fixtures': [{
                'id': 1,
                'date': '2024-01-15T15:30:00Z',
                'teams': {
                    'home': {'id': 1, 'name': 'Manchester City'},
                    'away': {'id': 2, 'name': 'Arsenal'}
                },
                'goals': {'home': 2, 'away': 1},
                'status': {'short': 'FT', 'long': 'Finished'},
                'league': {'id': 39, 'name': 'Premier League'}
            }],
            'team_stats': [{
                'team_id': 1,
                'wins': 15,
                'draws': 3,
                'losses': 2,
                'goals_scored': 45,
                'goals_conceded': 18
            }]
        }
        
        print("1. Processando estatísticas de partidas...")
        processed_data = system.process_data(sample_data)
        print(f"   ✅ Processadas {len(processed_data.get('match_statistics', []))} partidas")
        
        print("2. Processando estatísticas de times...")
        print(f"   ✅ Processadas {len(processed_data.get('team_statistics', []))} estatísticas")
        
        print("3. Calculando forma recente...")
        # Simula cálculo de forma
        form_stats = system.stats_processor.calculate_team_form(
            sample_data['fixtures'], 1, matches=5
        )
        print(f"   ✅ Forma calculada: {form_stats.get('points', 0)} pontos")
        
        system.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no processamento: {e}")
        return False

def demonstrate_ml_predictions():
    """Demonstra predições de ML"""
    print("\n🤖 DEMONSTRAÇÃO DE MACHINE LEARNING")
    print("=" * 50)
    
    try:
        system = SportsDataSystem()
        
        print("1. Preparando dados de treinamento...")
        training_data = system._prepare_training_data()
        print(f"   ✅ Preparados {len(training_data)} jogos para treinamento")
        
        print("2. Treinando modelos...")
        team_stats = {'1': {}, '2': {}}
        X, y = system.predictions_processor.prepare_training_data(training_data, team_stats)
        
        if X.size > 0:
            results = system.predictions_processor.train_models(X, y)
            print(f"   ✅ Modelos treinados com sucesso")
            
            for model_name, metrics in results.items():
                if 'error' not in metrics:
                    print(f"      • {model_name}: {metrics}")
        else:
            print("   ⚠️ Dados insuficientes para treinamento")
        
        print("3. Fazendo predições...")
        match_data = {'home_team_id': 1, 'away_team_id': 2}
        predictions = system.make_predictions(match_data, team_stats)
        
        if predictions:
            print("   ✅ Predições geradas:")
            for pred_type, pred_data in predictions.items():
                if isinstance(pred_data, dict):
                    print(f"      • {pred_type}: {pred_data.get('prediction', 'N/A')}")
        else:
            print("   ⚠️ Predições não disponíveis (modelos não treinados)")
        
        system.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nas predições: {e}")
        return False

def demonstrate_database_operations():
    """Demonstra operações do banco de dados"""
    print("\n💾 DEMONSTRAÇÃO DO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        system = SportsDataSystem()
        
        print("1. Testando conexão com SQLite...")
        if system.db.connect():
            print("   ✅ Conectado ao banco SQLite")
        else:
            print("   ❌ Falha na conexão")
            return False
        
        print("2. Salvando dados de exemplo...")
        sample_data = {
            'leagues': [{
                'id': 39,
                'name': 'Premier League',
                'country': 'England',
                'logo': 'https://example.com/logo.png'
            }],
            'teams': [{
                'id': 1,
                'name': 'Manchester City',
                'code': 'MCI',
                'country': 'England',
                'league_id': 39,
                'season': 2024
            }],
            'fixtures': [{
                'id': 1,
                'date': '2024-01-15T15:30:00Z',
                'timestamp': 1705335000,
                'timezone': 'UTC',
                'status': {'short': 'FT', 'long': 'Finished'},
                'league': {'id': 39, 'name': 'Premier League', 'country': 'England', 'season': 2024},
                'teams': {
                    'home': {'id': 1, 'name': 'Manchester City'},
                    'away': {'id': 2, 'name': 'Arsenal'}
                },
                'goals': {'home': 2, 'away': 1},
                'score': {'halftime': {'home': 1, 'away': 0}, 'fulltime': {'home': 2, 'away': 1}}
            }]
        }
        
        success = system.save_data(sample_data)
        if success:
            print("   ✅ Dados salvos com sucesso")
        else:
            print("   ❌ Erro ao salvar dados")
            return False
        
        print("3. Consultando estatísticas do banco...")
        db_stats = system.db.get_database_stats()
        print(f"   ✅ Estatísticas do banco:")
        for table, count in db_stats.items():
            if table.endswith('_count'):
                table_name = table.replace('_count', '')
                print(f"      • {table_name}: {count} registros")
        
        print("4. Testando consultas...")
        leagues = system.db.get_all_leagues()
        print(f"   ✅ Consultadas {len(leagues)} ligas")
        
        teams = system.db.get_teams_by_league(39)
        print(f"   ✅ Consultados {len(teams)} times da Premier League")
        
        matches = system.db.get_matches_by_league(39, limit=10)
        print(f"   ✅ Consultadas {len(matches)} partidas")
        
        system.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no banco de dados: {e}")
        return False

def demonstrate_cache_system():
    """Demonstra sistema de cache"""
    print("\n🗄️ DEMONSTRAÇÃO DO SISTEMA DE CACHE")
    print("=" * 50)
    
    try:
        system = SportsDataSystem()
        
        print("1. Testando operações de cache...")
        
        # Armazena dados
        test_data = {"test": "value", "number": 42}
        system.cache.set("test_key", test_data)
        print("   ✅ Dados armazenados no cache")
        
        # Recupera dados
        retrieved_data = system.cache.get("test_key")
        if retrieved_data == test_data:
            print("   ✅ Dados recuperados corretamente")
        else:
            print("   ❌ Dados não coincidem")
            return False
        
        # Testa expiração
        system.cache.set("expire_key", "expire_value", ttl=1)
        time.sleep(2)
        expired_data = system.cache.get("expire_key")
        if expired_data is None:
            print("   ✅ Expiração funcionando corretamente")
        else:
            print("   ❌ Expiração não funcionou")
        
        print("2. Estatísticas do cache...")
        cache_stats = system.cache.get_stats()
        print(f"   ✅ Estatísticas:")
        for key, value in cache_stats.items():
            print(f"      • {key}: {value}")
        
        print("3. Testando cache de API...")
        from utils.cache import APICache
        api_cache = APICache(system.cache)
        
        api_cache.set_api_data("test_endpoint", {"data": "test"}, {"param": "value"})
        api_data = api_cache.get_api_data("test_endpoint", {"param": "value"})
        
        if api_data:
            print("   ✅ Cache de API funcionando")
        else:
            print("   ❌ Cache de API falhou")
        
        system.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no cache: {e}")
        return False

def demonstrate_complete_analysis():
    """Demonstra análise completa"""
    print("\n🔍 DEMONSTRAÇÃO DE ANÁLISE COMPLETA")
    print("=" * 50)
    
    try:
        system = SportsDataSystem()
        
        print("Executando análise completa: Manchester City vs Arsenal")
        print("(Isso pode levar alguns segundos...)")
        
        result = system.run_analysis(
            home_team="Manchester City",
            away_team="Arsenal",
            league="Premier League"
        )
        
        if 'error' in result:
            print(f"   ❌ Erro na análise: {result['error']}")
            return False
        
        print("   ✅ Análise concluída com sucesso!")
        
        # Mostra resultados
        print("\n📊 RESULTADOS DA ANÁLISE:")
        print(f"   • Partida: {result['match']}")
        print(f"   • Liga: {result['league']}")
        print(f"   • Data: {result['analysis_date']}")
        
        # Estatísticas do sistema
        stats = result['system_stats']
        print(f"\n📈 ESTATÍSTICAS DO SISTEMA:")
        print(f"   • Uptime: {stats['uptime_seconds']:.1f}s")
        print(f"   • Dados coletados: {stats['data_collected']}")
        print(f"   • Dados processados: {stats['data_processed']}")
        print(f"   • Predições: {stats['predictions_made']}")
        print(f"   • Erros: {stats['errors']}")
        
        # Cache e banco
        print(f"\n💾 ARMAZENAMENTO:")
        print(f"   • Cache: {stats['cache_stats']['active_items']} itens ativos")
        print(f"   • Banco: {stats['database_stats'].get('matches_count', 0)} partidas")
        
        system.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na análise completa: {e}")
        return False

def show_usage_examples():
    """Mostra exemplos de uso"""
    print("\n📚 EXEMPLOS DE USO")
    print("=" * 50)
    print("""
🔧 COMANDOS BÁSICOS:

1. Análise completa:
   python main.py --home-team "Manchester City" --away-team "Arsenal"

2. Apenas coleta:
   python main.py --home-team "Liverpool" --away-team "Chelsea" --collect-only

3. Apenas predições:
   python main.py --home-team "Barcelona" --away-team "Real Madrid" --predict-only

4. Liga específica:
   python main.py --home-team "PSG" --away-team "Marseille" --league "Ligue 1"

🐍 USO PROGRAMÁTICO:

```python
from main import SportsDataSystem

# Inicializa sistema
system = SportsDataSystem()

# Executa análise
result = system.run_analysis("Manchester City", "Arsenal")

# Acessa resultados
predictions = result['predictions']
stats = result['system_stats']

# Limpa recursos
system.cleanup()
```

⚙️ CONFIGURAÇÃO:

1. Edite config/settings.py para personalizar
2. Configure chaves de API em config/.env
3. Ajuste parâmetros de ML e cache
4. Personalize ligas e temporadas
""")

def main():
    """Função principal da demonstração"""
    show_system_info()
    
    print("\n🚀 INICIANDO DEMONSTRAÇÕES")
    print("=" * 70)
    
    # Lista de demonstrações
    demonstrations = [
        ("Coleta de Dados", demonstrate_data_collection),
        ("Processamento", demonstrate_data_processing),
        ("Machine Learning", demonstrate_ml_predictions),
        ("Banco de Dados", demonstrate_database_operations),
        ("Sistema de Cache", demonstrate_cache_system),
        ("Análise Completa", demonstrate_complete_analysis)
    ]
    
    results = []
    
    for name, demo_func in demonstrations:
        print(f"\n▶️ Executando: {name}")
        try:
            success = demo_func()
            results.append((name, success))
            if success:
                print(f"   ✅ {name} - SUCESSO")
            else:
                print(f"   ❌ {name} - FALHOU")
        except Exception as e:
            print(f"   ❌ {name} - ERRO: {e}")
            results.append((name, False))
        
        time.sleep(1)  # Pausa entre demonstrações
    
    # Resumo dos resultados
    print("\n📊 RESUMO DAS DEMONSTRAÇÕES")
    print("=" * 50)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ SUCESSO" if success else "❌ FALHOU"
        print(f"   • {name}: {status}")
    
    print(f"\n🎯 RESULTADO GERAL: {successful}/{total} demonstrações bem-sucedidas")
    
    if successful == total:
        print("🎉 TODAS AS DEMONSTRAÇÕES FORAM BEM-SUCEDIDAS!")
        print("   O sistema está funcionando perfeitamente.")
    elif successful > total // 2:
        print("⚠️ A MAIORIA DAS DEMONSTRAÇÕES FOI BEM-SUCEDIDA")
        print("   O sistema está funcionando com algumas limitações.")
    else:
        print("❌ MUITAS DEMONSTRAÇÕES FALHARAM")
        print("   Verifique a configuração e dependências.")
    
    show_usage_examples()
    
    print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print("Para mais informações, consulte o README.md")
    print("Para suporte, abra uma issue no GitHub")

if __name__ == "__main__":
    main()
