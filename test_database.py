#!/usr/bin/env python3
"""
Script para testar o banco de dados do MaraBet AI
"""

from armazenamento.banco_de_dados import *
from datetime import datetime, timedelta
import json

def test_database():
    """Testa as funcionalidades do banco de dados"""
    print("🗄️  MARABET AI - TESTE DO BANCO DE DADOS")
    print("=" * 50)
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        print("\n1. Testando inserção de partida...")
        
        # Criar uma partida de teste
        test_match = Match(
            fixture_id=12345,
            league_id=39,  # Premier League
            league_name="Premier League",
            date=datetime.now() + timedelta(hours=2),
            home_team_id=1,
            home_team_name="Manchester City",
            away_team_id=2,
            away_team_name="Arsenal",
            status="NS",  # Not Started
            statistics=json.dumps({
                "possession": {"home": 60, "away": 40},
                "shots": {"home": 15, "away": 8}
            })
        )
        
        db.add(test_match)
        db.commit()
        print("   ✅ Partida inserida com sucesso!")
        
        print("\n2. Testando inserção de odds...")
        
        # Criar odds de teste
        test_odds = Odds(
            fixture_id=12345,
            bookmaker="Bet365",
            market="Match Winner",
            selection="Home",
            odd=1.85
        )
        
        db.add(test_odds)
        db.commit()
        print("   ✅ Odds inseridas com sucesso!")
        
        print("\n3. Testando inserção de predição...")
        
        # Criar predição de teste
        test_prediction = Prediction(
            fixture_id=12345,
            market="Match Winner",
            selection="Home",
            predicted_probability=0.65,
            implied_probability=0.54,
            recommended_odd=1.54,
            current_odd=1.85,
            expected_value=0.12,
            confidence=0.78,
            stake_percentage=0.05,
            recommended=True,
            factors=json.dumps({
                "form": "excellent",
                "h2h": "favorable",
                "home_advantage": True
            })
        )
        
        db.add(test_prediction)
        db.commit()
        print("   ✅ Predição inserida com sucesso!")
        
        print("\n4. Testando consultas...")
        
        # Consultar partidas
        matches = db.query(Match).filter(Match.league_id == 39).count()
        print(f"   Partidas na Premier League: {matches}")
        
        # Consultar odds
        odds = db.query(Odds).filter(Odds.fixture_id == 12345).count()
        print(f"   Odds para a partida: {odds}")
        
        # Consultar predições recomendadas
        recommendations = db.query(Prediction).filter(Prediction.recommended == True).count()
        print(f"   Predições recomendadas: {recommendations}")
        
        print("\n5. Testando histórico de apostas...")
        
        # Criar histórico de aposta
        test_betting = BettingHistory(
            prediction_id=test_prediction.id,
            fixture_id=12345,
            stake=50.0,
            odd=1.85,
            potential_return=92.5,
            result="pending"
        )
        
        db.add(test_betting)
        db.commit()
        print("   ✅ Histórico de aposta inserido com sucesso!")
        
        print("\n6. Limpeza dos dados de teste...")
        
        # Limpar dados de teste
        db.query(BettingHistory).filter(BettingHistory.fixture_id == 12345).delete()
        db.query(Prediction).filter(Prediction.fixture_id == 12345).delete()
        db.query(Odds).filter(Odds.fixture_id == 12345).delete()
        db.query(Match).filter(Match.fixture_id == 12345).delete()
        db.commit()
        print("   ✅ Dados de teste removidos!")
        
        print("\n🎉 Teste do banco de dados concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        db.rollback()
    finally:
        db.close()

def show_database_info():
    """Mostra informações sobre o banco de dados"""
    print("\n📊 INFORMAÇÕES DO BANCO DE DADOS")
    print("=" * 40)
    print(f"Localização: {engine.url}")
    print(f"Tabelas: {list(Base.metadata.tables.keys())}")
    
    db = SessionLocal()
    try:
        matches_count = db.query(Match).count()
        odds_count = db.query(Odds).count()
        predictions_count = db.query(Prediction).count()
        betting_count = db.query(BettingHistory).count()
        
        print(f"Partidas: {matches_count}")
        print(f"Odds: {odds_count}")
        print(f"Predições: {predictions_count}")
        print(f"Histórico de apostas: {betting_count}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database()
    show_database_info()
