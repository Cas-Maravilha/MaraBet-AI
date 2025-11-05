#!/usr/bin/env python3
"""
Predições Avançadas com Machine Learning
MaraBet AI - Predições usando algoritmos de ML com dados reais
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_prepare_data():
    """Carrega e prepara dados para ML"""
    logger.info("📊 CARREGANDO E PREPARANDO DADOS PARA ML")
    print("=" * 60)
    
    try:
        with open('real_football_data_valid.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fixtures = data.get('fixtures', [])
        logger.info(f"   {len(fixtures)} partidas carregadas")
        
        # Preparar dados para ML
        matches_data = []
        for fixture in fixtures:
            try:
                match = {
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'home_score': fixture['goals']['home'] if fixture['goals']['home'] is not None else 0,
                    'away_score': fixture['goals']['away'] if fixture['goals']['away'] is not None else 0,
                    'league_id': fixture['league']['id'],
                    'season': fixture['league']['season']
                }
                matches_data.append(match)
            except Exception as e:
                continue
        
        logger.info(f"   {len(matches_data)} partidas processadas para ML")
        return matches_data
        
    except Exception as e:
        logger.error(f"   Erro ao carregar dados: {e}")
        return None

def create_features(matches_data):
    """Cria features para o modelo de ML"""
    logger.info("🔧 CRIANDO FEATURES PARA ML")
    print("=" * 60)
    
    df = pd.DataFrame(matches_data)
    
    # Calcular estatísticas dos times
    team_stats = {}
    for _, match in df.iterrows():
        home_team = match['home_team']
        away_team = match['away_team']
        
        if home_team not in team_stats:
            team_stats[home_team] = {'games': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0}
        if away_team not in team_stats:
            team_stats[away_team] = {'games': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0}
        
        team_stats[home_team]['games'] += 1
        team_stats[home_team]['goals_for'] += match['home_score']
        team_stats[home_team]['goals_against'] += match['away_score']
        
        team_stats[away_team]['games'] += 1
        team_stats[away_team]['goals_for'] += match['away_score']
        team_stats[away_team]['goals_against'] += match['home_score']
        
        if match['home_score'] > match['away_score']:
            team_stats[home_team]['wins'] += 1
        elif match['away_score'] > match['home_score']:
            team_stats[away_team]['wins'] += 1
    
    # Criar features para cada partida
    features = []
    targets = []
    
    for _, match in df.iterrows():
        home_team = match['home_team']
        away_team = match['away_team']
        
        if home_team in team_stats and away_team in team_stats:
            home_stats = team_stats[home_team]
            away_stats = team_stats[away_team]
            
            # Features do time da casa
            home_win_rate = home_stats['wins'] / max(home_stats['games'], 1)
            home_avg_goals_for = home_stats['goals_for'] / max(home_stats['games'], 1)
            home_avg_goals_against = home_stats['goals_against'] / max(home_stats['games'], 1)
            
            # Features do time visitante
            away_win_rate = away_stats['wins'] / max(away_stats['games'], 1)
            away_avg_goals_for = away_stats['goals_for'] / max(away_stats['games'], 1)
            away_avg_goals_against = away_stats['goals_against'] / max(away_stats['games'], 1)
            
            # Features combinadas
            feature_vector = [
                home_win_rate,
                home_avg_goals_for,
                home_avg_goals_against,
                away_win_rate,
                away_avg_goals_for,
                away_avg_goals_against,
                home_win_rate - away_win_rate,  # Diferença de força
                home_avg_goals_for - away_avg_goals_against,  # Ataque casa vs defesa fora
                away_avg_goals_for - home_avg_goals_against,  # Ataque fora vs defesa casa
            ]
            
            features.append(feature_vector)
            
            # Target (resultado da partida)
            if match['home_score'] > match['away_score']:
                targets.append(0)  # Vitória da casa
            elif match['away_score'] > match['home_score']:
                targets.append(2)  # Vitória do visitante
            else:
                targets.append(1)  # Empate
    
    logger.info(f"   {len(features)} features criadas")
    return np.array(features), np.array(targets), team_stats

def train_models(X, y):
    """Treina múltiplos modelos de ML"""
    logger.info("🤖 TREINANDO MODELOS DE ML")
    print("=" * 60)
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalizar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Modelos
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
    }
    
    trained_models = {}
    
    for name, model in models.items():
        logger.info(f"   Treinando {name}...")
        
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        trained_models[name] = {
            'model': model,
            'scaler': scaler if name == 'Logistic Regression' else None,
            'accuracy': accuracy
        }
        
        logger.info(f"   {name} - Acurácia: {accuracy:.2%}")
    
    return trained_models

def predict_future_matches(trained_models, team_stats):
    """Prediz partidas futuras"""
    logger.info("🔮 PREDIZENDO PARTIDAS FUTURAS")
    print("=" * 60)
    
    # Selecionar times para simular partidas
    teams = list(team_stats.keys())
    if len(teams) < 2:
        logger.error("   Dados insuficientes para predições")
        return []
    
    predictions = []
    
    # Simular 5 partidas
    for i in range(5):
        home_team = teams[i % len(teams)]
        away_team = teams[(i + 1) % len(teams)]
        
        if home_team != away_team:
            # Criar features para a partida
            home_stats = team_stats[home_team]
            away_stats = team_stats[away_team]
            
            home_win_rate = home_stats['wins'] / max(home_stats['games'], 1)
            home_avg_goals_for = home_stats['goals_for'] / max(home_stats['games'], 1)
            home_avg_goals_against = home_stats['goals_against'] / max(home_stats['games'], 1)
            
            away_win_rate = away_stats['wins'] / max(away_stats['games'], 1)
            away_avg_goals_for = away_stats['goals_for'] / max(away_stats['games'], 1)
            away_avg_goals_against = away_stats['goals_against'] / max(away_stats['games'], 1)
            
            feature_vector = np.array([[
                home_win_rate,
                home_avg_goals_for,
                home_avg_goals_against,
                away_win_rate,
                away_avg_goals_for,
                away_avg_goals_against,
                home_win_rate - away_win_rate,
                home_avg_goals_for - away_avg_goals_against,
                away_avg_goals_for - home_avg_goals_against,
            ]])
            
            # Predições de todos os modelos
            model_predictions = {}
            for name, model_info in trained_models.items():
                model = model_info['model']
                scaler = model_info['scaler']
                
                if scaler:
                    features_scaled = scaler.transform(feature_vector)
                    pred_proba = model.predict_proba(features_scaled)[0]
                else:
                    pred_proba = model.predict_proba(feature_vector)[0]
                
                model_predictions[name] = pred_proba
            
            # Média das predições (ensemble)
            avg_proba = np.mean(list(model_predictions.values()), axis=0)
            
            # Determinar resultado mais provável
            result_labels = ['Casa', 'Empate', 'Fora']
            predicted_result = result_labels[np.argmax(avg_proba)]
            confidence = np.max(avg_proba)
            
            # Calcular odds
            odds = 1 / avg_proba
            
            prediction = {
                'home_team': home_team,
                'away_team': away_team,
                'prediction': predicted_result,
                'confidence': confidence,
                'probabilities': {
                    'home_win': avg_proba[0],
                    'draw': avg_proba[1],
                    'away_win': avg_proba[2]
                },
                'odds': {
                    'home_win': odds[0],
                    'draw': odds[1],
                    'away_win': odds[2]
                },
                'model_predictions': model_predictions
            }
            
            predictions.append(prediction)
    
    return predictions

def run_advanced_predictions():
    """Executa predições avançadas com ML"""
    print("🤖 PREDIÇÕES AVANÇADAS COM MACHINE LEARNING - MARABET AI")
    print("=" * 80)
    
    # 1. Carregar e preparar dados
    matches_data = load_and_prepare_data()
    if not matches_data:
        return False
    
    # 2. Criar features
    X, y, team_stats = create_features(matches_data)
    if len(X) == 0:
        logger.error("   Nenhuma feature criada")
        return False
    
    # 3. Treinar modelos
    trained_models = train_models(X, y)
    
    # 4. Mostrar estatísticas dos times
    print("\n📊 ESTATÍSTICAS DOS TIMES:")
    print("=" * 60)
    for team, stats in sorted(team_stats.items(), key=lambda x: x[1]['wins'], reverse=True)[:10]:
        win_rate = stats['wins'] / max(stats['games'], 1)
        avg_goals_for = stats['goals_for'] / max(stats['games'], 1)
        avg_goals_against = stats['goals_against'] / max(stats['games'], 1)
        
        print(f"   {team}:")
        print(f"     Jogos: {stats['games']} | Vitórias: {stats['wins']} | Taxa: {win_rate:.2%}")
        print(f"     Gols Pró: {avg_goals_for:.2f} | Gols Contra: {avg_goals_against:.2f}")
        print()
    
    # 5. Predições futuras
    predictions = predict_future_matches(trained_models, team_stats)
    
    if not predictions:
        logger.error("   Nenhuma predição gerada")
        return False
    
    # 6. Mostrar predições
    print("\n🔮 PREDIÇÕES AVANÇADAS:")
    print("=" * 60)
    
    for i, prediction in enumerate(predictions, 1):
        print(f"   🏆 Partida {i}: {prediction['home_team']} vs {prediction['away_team']}")
        print(f"      Predição: {prediction['prediction']} (Confiança: {prediction['confidence']:.2%})")
        print(f"      Probabilidades: Casa {prediction['probabilities']['home_win']:.2%} | Empate {prediction['probabilities']['draw']:.2%} | Fora {prediction['probabilities']['away_win']:.2%}")
        print(f"      Odds: Casa {prediction['odds']['home_win']:.2f} | Empate {prediction['odds']['draw']:.2f} | Fora {prediction['odds']['away_win']:.2f}")
        
        # Mostrar predições individuais dos modelos
        print(f"      Predições dos Modelos:")
        for model_name, model_proba in prediction['model_predictions'].items():
            result_labels = ['Casa', 'Empate', 'Fora']
            model_pred = result_labels[np.argmax(model_proba)]
            model_conf = np.max(model_proba)
            print(f"        {model_name}: {model_pred} ({model_conf:.2%})")
        print()
    
    # 7. Análise de valor das apostas
    print("\n💰 ANÁLISE DE VALOR DAS APOSTAS:")
    print("=" * 60)
    
    for prediction in predictions:
        # Calcular valor esperado
        home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
        draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
        away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
        
        print(f"   {prediction['home_team']} vs {prediction['away_team']}:")
        print(f"      Valor Casa: {home_value:.2%} {'✅' if home_value > 0.05 else '❌'}")
        print(f"      Valor Empate: {draw_value:.2%} {'✅' if draw_value > 0.05 else '❌'}")
        print(f"      Valor Fora: {away_value:.2%} {'✅' if away_value > 0.05 else '❌'}")
        print()
    
    # 8. Resumo
    print("\n📊 RESUMO DAS PREDIÇÕES AVANÇADAS:")
    print("=" * 60)
    print(f"   Total de partidas analisadas: {len(matches_data)}")
    print(f"   Times analisados: {len(team_stats)}")
    print(f"   Features criadas: {X.shape[1]}")
    print(f"   Predições geradas: {len(predictions)}")
    
    if predictions:
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        print(f"   Confiança média: {avg_confidence:.2%}")
    
    # Contar apostas com valor positivo
    positive_value_bets = 0
    for prediction in predictions:
        home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
        draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
        away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
        
        if home_value > 0.05 or draw_value > 0.05 or away_value > 0.05:
            positive_value_bets += 1
    
    print(f"   Apostas com valor positivo (>5%): {positive_value_bets}/{len(predictions)}")
    
    # Mostrar acurácia dos modelos
    print(f"\n🤖 PERFORMANCE DOS MODELOS:")
    print("=" * 60)
    for name, model_info in trained_models.items():
        print(f"   {name}: {model_info['accuracy']:.2%}")
    
    print("\n🎉 PREDIÇÕES AVANÇADAS CONCLUÍDAS COM SUCESSO!")
    return True

if __name__ == "__main__":
    run_advanced_predictions()
