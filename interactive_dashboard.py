#!/usr/bin/env python3
"""
Dashboard Interativo Completo para o sistema de predições expandido MaraBet AI
Com navegação clicável e páginas detalhadas
"""

import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path
import http.server
import socketserver
import urllib.parse
import threading
import time

class InteractiveDashboard:
    def __init__(self):
        self.port = 8081
        self.predictions_data = {}
        self.load_predictions()
    
    def load_predictions(self):
        """Carrega as predições dos arquivos JSON"""
        prediction_files = [f for f in os.listdir('.') if 'predictions' in f and f.endswith('.json')]
        
        for filename in prediction_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                match_data = data.get('match_data', {})
                predictions = data.get('predictions', {})
                
                match_key = f"{match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}"
                
                self.predictions_data[match_key] = {
                    'match_data': match_data,
                    'predictions': predictions,
                    'total_predictions': data.get('total_predictions', 0),
                    'generated_at': data.get('generated_at', 'N/A'),
                    'filename': filename
                }
                
            except Exception as e:
                print(f"Erro ao carregar {filename}: {e}")
    
    def generate_main_page(self):
        """Gera a página principal do dashboard"""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MaraBet AI - Dashboard Interativo</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.9;
        }}
        
        .nav-menu {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .nav-buttons {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .nav-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }}
        
        .nav-btn:hover {{
            background: #5a6fd8;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
            cursor: pointer;
        }}
        
        .stat-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.2em;
            color: #666;
        }}
        
        .matches-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 2em;
            margin-bottom: 25px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        
        .match-card {{
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            background: #f9f9f9;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .match-card:hover {{
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-5px);
            border-color: #667eea;
        }}
        
        .match-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .match-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .match-league {{
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 1em;
        }}
        
        .match-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .match-stat {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .match-stat-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .match-stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .view-details-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 15px;
            width: 100%;
        }}
        
        .view-details-btn:hover {{
            background: #218838;
            transform: translateY(-2px);
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MaraBet AI</h1>
            <p>Dashboard Interativo de Predições Expandidas</p>
        </div>
        
        <div class="nav-menu">
            <div class="nav-buttons">
                <a href="/" class="nav-btn">🏠 Início</a>
                <a href="/matches" class="nav-btn">⚽ Partidas</a>
                <a href="/markets" class="nav-btn">📊 Mercados</a>
                <a href="/stats" class="nav-btn">📈 Estatísticas</a>
                <a href="/about" class="nav-btn">ℹ️ Sobre</a>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card" onclick="location.href='/matches'">
                <div class="stat-number">{len(self.predictions_data)}</div>
                <div class="stat-label">Partidas Analisadas</div>
            </div>
            <div class="stat-card" onclick="location.href='/stats'">
                <div class="stat-number">{sum(data['total_predictions'] for data in self.predictions_data.values())}</div>
                <div class="stat-label">Total de Predições</div>
            </div>
            <div class="stat-card" onclick="location.href='/markets'">
                <div class="stat-number">{len(set(data['match_data'].get('league', 'Unknown') for data in self.predictions_data.values()))}</div>
                <div class="stat-label">Ligas Cobertas</div>
            </div>
            <div class="stat-card" onclick="location.href='/markets'">
                <div class="stat-number">7</div>
                <div class="stat-label">Categorias de Mercados</div>
            </div>
        </div>
        
        <div class="matches-section">
            <h2 class="section-title">🏆 Partidas Analisadas</h2>
"""
        
        for match_key, data in self.predictions_data.items():
            match_data = data['match_data']
            predictions = data['predictions']
            
            # Contar predições por categoria
            categories_count = {cat: len(preds) for cat, preds in predictions.items() if isinstance(preds, dict)}
            
            html += f"""
            <div class="match-card" onclick="location.href='/match/{urllib.parse.quote(match_key)}'">
                <div class="match-header">
                    <div class="match-title">{match_key}</div>
                    <div class="match-league">{match_data.get('league', 'N/A')}</div>
                </div>
                
                <div class="match-stats">
                    <div class="match-stat">
                        <div class="match-stat-number">{data['total_predictions']}</div>
                        <div class="match-stat-label">Predições</div>
                    </div>
                    <div class="match-stat">
                        <div class="match-stat-number">{len(categories_count)}</div>
                        <div class="match-stat-label">Categorias</div>
                    </div>
                    <div class="match-stat">
                        <div class="match-stat-number">{match_data.get('home_team_strength', 0.5):.1f}</div>
                        <div class="match-stat-label">Força Casa</div>
                    </div>
                    <div class="match-stat">
                        <div class="match-stat-number">{match_data.get('away_team_strength', 0.5):.1f}</div>
                        <div class="match-stat-label">Força Visitante</div>
                    </div>
                </div>
                
                <button class="view-details-btn" onclick="event.stopPropagation(); location.href='/match/{urllib.parse.quote(match_key)}'">
                    📊 Ver Detalhes Completos
                </button>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>Dashboard atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p>🎯 Sistema MaraBet AI - Predições Profissionais</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh a cada 60 segundos
        setTimeout(() => {{
            location.reload();
        }}, 60000);
    </script>
</body>
</html>
"""
        return html
    
    def generate_reasoning(self, category, bet_type, prob, match_data):
        """Gera razão detalhada para uma recomendação"""
        home_strength = match_data.get('home_team_strength', 0.5)
        away_strength = match_data.get('away_team_strength', 0.5)
        league = match_data.get('league', 'N/A')
        
        if category == 'goals':
            if 'over' in bet_type.lower():
                return f"Equipes com força média de {home_strength:.2f} e {away_strength:.2f} indicam potencial ofensivo alto na {league}"
            elif 'under' in bet_type.lower():
                return f"Defesas sólidas e baixa média de gols esperada baseada no histórico da {league}"
            elif 'btts' in bet_type.lower():
                return f"Ambas as equipes têm probabilidade alta de marcar: casa {home_strength:.1%}, visitante {away_strength:.1%}"
        
        elif category == 'handicap':
            if 'casa' in bet_type.lower():
                return f"Vantagem de casa ({home_strength:.2f}) supera força visitante ({away_strength:.2f}) na {league}"
            else:
                return f"Equipe visitante compensa desvantagem com força superior ({away_strength:.2f} vs {home_strength:.2f})"
        
        elif category == 'cards':
            intensity = match_data.get('match_intensity', 0.5)
            return f"Intensidade da partida ({intensity:.1%}) e histórico de cartões na {league} indicam alta probabilidade"
        
        elif category == 'corners':
            attack_style = match_data.get('home_attack_style', 0.5)
            return f"Estilo ofensivo ({attack_style:.1%}) e padrões de jogo da {league} favorecem cantos"
        
        elif category == 'double_chance':
            return f"Combinação de probabilidades reduz risco: casa {home_strength:.1%} + empate + visitante {away_strength:.1%}"
        
        elif category == 'exact_score':
            return f"Distribuição de Poisson com λ={home_strength + away_strength:.1f} baseada nas forças das equipes"
        
        else:
            return f"Análise baseada em força das equipes ({home_strength:.2f} vs {away_strength:.2f}) e contexto da {league}"
    
    def get_additional_info(self, category, bet_type, prob, match_data):
        """Gera informação adicional para cada predição"""
        home_strength = match_data.get('home_team_strength', 0.5)
        away_strength = match_data.get('away_team_strength', 0.5)
        
        if category == 'goals':
            if 'over' in bet_type.lower():
                return f"Média esperada: {(home_strength + away_strength) * 2:.1f} gols"
            elif 'under' in bet_type.lower():
                return f"Média esperada: {(home_strength + away_strength) * 1.5:.1f} gols"
            elif 'btts' in bet_type.lower():
                return f"Casa: {home_strength:.1%}, Visitante: {away_strength:.1%}"
        
        elif category == 'handicap':
            diff = abs(home_strength - away_strength)
            return f"Diferença de força: {diff:.2f}"
        
        elif category == 'cards':
            intensity = match_data.get('match_intensity', 0.5)
            return f"Intensidade: {intensity:.1%}"
        
        elif category == 'corners':
            attack_style = match_data.get('home_attack_style', 0.5)
            return f"Estilo ofensivo: {attack_style:.1%}"
        
        elif category == 'double_chance':
            return f"Reduz risco em ~{100-prob*100:.0f}%"
        
        elif category == 'exact_score':
            return f"Distribuição Poisson λ={(home_strength + away_strength):.1f}"
        
        else:
            return f"Força casa: {home_strength:.2f}, visitante: {away_strength:.2f}"
    
    def get_recommended_handicap(self, home_strength, away_strength):
        """Calcula handicap recomendado baseado na diferença de força"""
        diff = home_strength - away_strength
        
        if diff > 0.3:
            return "Casa -1.5"
        elif diff > 0.2:
            return "Casa -1"
        elif diff > 0.1:
            return "Casa -0.5"
        elif diff > -0.1:
            return "Empate (0)"
        elif diff > -0.2:
            return "Visitante +0.5"
        elif diff > -0.3:
            return "Visitante +1"
        else:
            return "Visitante +1.5"
    
    def generate_match_detail_page(self, match_key):
        """Gera página de detalhes de uma partida específica"""
        if match_key not in self.predictions_data:
            return self.generate_404_page()
        
        data = self.predictions_data[match_key]
        match_data = data['match_data']
        predictions = data['predictions']
        
        # Extrair variáveis para análise
        home_strength = match_data.get('home_team_strength', 0.5)
        away_strength = match_data.get('away_team_strength', 0.5)
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{match_key} - MaraBet AI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .back-btn {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }}
        
        .back-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .match-header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .match-title {{
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .match-league {{
            background: #667eea;
            color: white;
            padding: 10px 25px;
            border-radius: 25px;
            font-size: 1.2em;
            display: inline-block;
            margin-bottom: 20px;
        }}
        
        .match-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .info-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .info-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .info-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}
        
        .predictions-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 25px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }}
        
        .category-card {{
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 25px;
            background: #f9f9f9;
            transition: all 0.3s ease;
        }}
        
        .category-card:hover {{
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transform: translateY(-3px);
        }}
        
        .category-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .prediction-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
            transition: all 0.3s ease;
        }}
        
        .prediction-item:hover {{
            background: rgba(102, 126, 234, 0.1);
            padding-left: 10px;
            border-radius: 5px;
        }}
        
        .prediction-item:last-child {{
            border-bottom: none;
        }}
        
        .prediction-name {{
            font-size: 1em;
            color: #555;
            flex: 1;
        }}
        
        .prediction-prob {{
            font-weight: bold;
            font-size: 1.1em;
            padding: 5px 12px;
            border-radius: 15px;
        }}
        
        .confidence-high {{ 
            color: white;
            background: #28a745;
        }}
        .confidence-medium {{ 
            color: white;
            background: #ffc107;
        }}
        .confidence-low {{ 
            color: white;
            background: #dc3545;
        }}
        
        .recommendations {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .recommendation-item {{
            background: #e8f5e8;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 0 10px 10px 0;
        }}
        
        .recommendation-title {{
            font-weight: bold;
            color: #155724;
            margin-bottom: 10px;
        }}
        
        .recommendation-details {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        
        .recommendation-reasoning {{
            color: #555;
            font-size: 0.85em;
            font-style: italic;
            background: rgba(102, 126, 234, 0.1);
            padding: 8px;
            border-radius: 5px;
            margin-top: 8px;
        }}
        
        .match-analysis {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }}
        
        .analysis-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }}
        
        .analysis-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .analysis-content p {{
            margin-bottom: 8px;
            color: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <button class="back-btn" onclick="location.href='/'">← Voltar ao Início</button>
        
        <div class="match-header">
            <h1 class="match-title">{match_key}</h1>
            <div class="match-league">{match_data.get('league', 'N/A')}</div>
            
            <div class="match-info">
                <div class="info-item">
                    <div class="info-label">Total de Predições</div>
                    <div class="info-value">{data['total_predictions']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Força Casa</div>
                    <div class="info-value">{match_data.get('home_team_strength', 0.5):.2f}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Força Visitante</div>
                    <div class="info-value">{match_data.get('away_team_strength', 0.5):.2f}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Gerado em</div>
                    <div class="info-value">{data['generated_at'][:10]}</div>
                </div>
            </div>
        </div>
        
        <div class="predictions-section">
            <h2 class="section-title">📊 Predições Detalhadas por Categoria</h2>
            
            <div class="category-grid">
"""
        
        for category, preds in predictions.items():
            if isinstance(preds, dict):
                html += f"""
                <div class="category-card">
                    <div class="category-title">{category.upper()}</div>
"""
                
                for bet_type, prob in preds.items():
                    confidence_class = "confidence-high" if prob > 0.7 else "confidence-medium" if prob > 0.5 else "confidence-low"
                    
                    # Gerar informação adicional baseada no tipo de aposta
                    additional_info = self.get_additional_info(category, bet_type, prob, match_data)
                    
                    html += f"""
                    <div class="prediction-item">
                        <div style="flex: 1;">
                            <span class="prediction-name">{bet_type}</span>
                            <div style="font-size: 0.8em; color: #888; margin-top: 2px;">{additional_info}</div>
                        </div>
                        <span class="prediction-prob {confidence_class}">{prob:.1%}</span>
                    </div>
"""
                
                html += """
                </div>
"""
        
        html += f"""
            </div>
        </div>
        
        <div class="recommendations">
            <h2 class="section-title">🏆 Top Recomendações</h2>
"""
        
        # Gerar recomendações baseadas nas probabilidades mais altas
        all_predictions = []
        for category, preds in predictions.items():
            if isinstance(preds, dict):
                for bet_type, prob in preds.items():
                    all_predictions.append((category, bet_type, prob))
        
        # Ordenar por probabilidade
        all_predictions.sort(key=lambda x: x[2], reverse=True)
        
        # Gerar recomendações mais detalhadas
        for i, (category, bet_type, prob) in enumerate(all_predictions[:10]):
            # Determinar nível de confiança
            if prob > 0.75:
                confidence_level = "🟢 ALTA"
                confidence_color = "#28a745"
            elif prob > 0.60:
                confidence_level = "🟡 MÉDIA"
                confidence_color = "#ffc107"
            else:
                confidence_level = "🔴 BAIXA"
                confidence_color = "#dc3545"
            
            # Gerar razão baseada no tipo de aposta
            reasoning = self.generate_reasoning(category, bet_type, prob, match_data)
            
            html += f"""
            <div class="recommendation-item">
                <div class="recommendation-title">{i+1}. {category.upper()}: {bet_type}</div>
                <div class="recommendation-details">
                    <strong>Probabilidade:</strong> {prob:.1%} | 
                    <strong>Confiança:</strong> {confidence_level} | 
                    <strong>Categoria:</strong> {category}
                </div>
                <div class="recommendation-reasoning">
                    <strong>Razão:</strong> {reasoning}
                </div>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="match-analysis">
            <h2 class="section-title">📈 Análise Detalhada da Partida</h2>
            
            <div class="analysis-grid">
                <div class="analysis-card">
                    <div class="analysis-title">⚽ Análise de Golos</div>
                    <div class="analysis-content">
                        <p><strong>Média de gols esperada:</strong> {(home_strength + away_strength) * 2:.1f}</p>
                        <p><strong>Probabilidade Over 2.5:</strong> {predictions.get('goals', {}).get('over_2_5', 0):.1% if isinstance(predictions.get('goals'), dict) else 'N/A'}</p>
                        <p><strong>Probabilidade BTTS:</strong> {predictions.get('goals', {}).get('btts_yes', 0):.1% if isinstance(predictions.get('goals'), dict) else 'N/A'}</p>
                        <p><strong>Força ofensiva casa:</strong> {home_strength:.1%}</p>
                        <p><strong>Força ofensiva visitante:</strong> {away_strength:.1%}</p>
                    </div>
                </div>
                
                <div class="analysis-card">
                    <div class="analysis-title">⚖️ Análise de Handicap</div>
                    <div class="analysis-content">
                        <p><strong>Diferença de força:</strong> {abs(home_strength - away_strength):.2f}</p>
                        <p><strong>Vantagem de casa:</strong> {home_strength - away_strength:+.2f}</p>
                        <p><strong>Handicap recomendado:</strong> {self.get_recommended_handicap(home_strength, away_strength)}</p>
                        <p><strong>Probabilidade casa -0.5:</strong> {predictions.get('handicap', {}).get('asian_handicap_home', 0):.1% if isinstance(predictions.get('handicap'), dict) else 'N/A'}</p>
                    </div>
                </div>
                
                <div class="analysis-card">
                    <div class="analysis-title">🟨 Análise de Cartões</div>
                    <div class="analysis-content">
                        <p><strong>Intensidade da partida:</strong> {match_data.get('match_intensity', 0.5):.1%}</p>
                        <p><strong>Probabilidade Over 3.5 cartões:</strong> {predictions.get('cards', {}).get('cards_over_3_5', 0):.1% if isinstance(predictions.get('cards'), dict) else 'N/A'}</p>
                        <p><strong>Probabilidade cartão vermelho:</strong> {predictions.get('cards', {}).get('red_cards_yes', 0):.1% if isinstance(predictions.get('cards'), dict) else 'N/A'}</p>
                        <p><strong>Rigor do árbitro:</strong> {match_data.get('referee_strictness', 0.5):.1%}</p>
                    </div>
                </div>
                
                <div class="analysis-card">
                    <div class="analysis-title">📐 Análise de Cantos</div>
                    <div class="analysis-content">
                        <p><strong>Estilo ofensivo casa:</strong> {match_data.get('home_attack_style', 0.5):.1%}</p>
                        <p><strong>Probabilidade Over 10.5 cantos:</strong> {predictions.get('corners', {}).get('corners_over_10_5', 0):.1% if isinstance(predictions.get('corners'), dict) else 'N/A'}</p>
                        <p><strong>Primeiro canto casa:</strong> {predictions.get('corners', {}).get('corners_first_home', 0):.1% if isinstance(predictions.get('corners'), dict) else 'N/A'}</p>
                        <p><strong>Média esperada:</strong> {(home_strength + away_strength) * 7:.1f} cantos</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_markets_page(self):
        """Gera página de mercados"""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mercados - MaraBet AI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .back-btn {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }}
        
        .back-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .markets-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 2.5em;
            margin-bottom: 30px;
            color: #333;
            text-align: center;
        }}
        
        .markets-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }}
        
        .market-card {{
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 25px;
            background: #f9f9f9;
            transition: all 0.3s ease;
        }}
        
        .market-card:hover {{
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-5px);
        }}
        
        .market-icon {{
            font-size: 3em;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .market-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-bottom: 15px;
        }}
        
        .market-description {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        
        .market-examples {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .example-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .example-list {{
            list-style: none;
            padding: 0;
        }}
        
        .example-list li {{
            padding: 5px 0;
            color: #666;
        }}
        
        .example-list li:before {{
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <button class="back-btn" onclick="location.href='/'">← Voltar ao Início</button>
        
        <div class="markets-section">
            <h1 class="section-title">📊 Mercados de Apostas Disponíveis</h1>
            
            <div class="markets-grid">
                <div class="market-card">
                    <div class="market-icon">⚽</div>
                    <div class="market-title">Mercados de Golos</div>
                    <div class="market-description">
                        Predições específicas para total de gols, ambas marcam, gols exatos e primeiro tempo.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>Over/Under 0.5, 1.5, 2.5, 3.5, 4.5, 5.5 gols</li>
                            <li>Ambas Marcam (BTTS) Sim/Não</li>
                            <li>Gols Exatos: 0, 1, 2, 3, 4, 5+ gols</li>
                            <li>Primeiro Tempo Over/Under</li>
                            <li>Jogo Limpo (Clean Sheet)</li>
                        </ul>
                    </div>
                </div>
                
                <div class="market-card">
                    <div class="market-icon">⚖️</div>
                    <div class="market-title">Mercados de Handicap</div>
                    <div class="market-description">
                        Handicap asiático e europeu para equilibrar as forças das equipes.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>Handicap Asiático: -2.5 a +2.5</li>
                            <li>Handicap Europeu: -3 a +3</li>
                            <li>Handicap de Cantos: -2 a +2</li>
                            <li>Ajuste de força das equipes</li>
                        </ul>
                    </div>
                </div>
                
                <div class="market-card">
                    <div class="market-icon">🟨</div>
                    <div class="market-title">Mercados de Cartões</div>
                    <div class="market-description">
                        Predições para cartões amarelos, vermelhos e totais.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>Total Cartões: Over/Under 1.5-6.5</li>
                            <li>Cartões Amarelos: Over/Under 1.5-4.5</li>
                            <li>Cartões Vermelhos: 0, 1+, 2+</li>
                            <li>Primeiro Cartão: Casa/Visitante</li>
                            <li>Timing: Primeiro/Segundo tempo</li>
                        </ul>
                    </div>
                </div>
                
                <div class="market-card">
                    <div class="market-icon">📐</div>
                    <div class="market-title">Mercados de Cantos</div>
                    <div class="market-description">
                        Predições para cantos de escanteio e corridas.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>Total Cantos: Over/Under 8.5-13.5</li>
                            <li>Handicap de Cantos: -2 a +2</li>
                            <li>Primeiro Canto: Casa/Visitante</li>
                            <li>Corrida de Cantos: Primeiro a 3, 5, 7, 9</li>
                            <li>Timing: Primeiro/Segundo tempo</li>
                        </ul>
                    </div>
                </div>
                
                <div class="market-card">
                    <div class="market-icon">🎯</div>
                    <div class="market-title">Dupla Chance</div>
                    <div class="market-description">
                        Apostas combinadas para reduzir risco.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>Dupla Chance Básica: 1X, X2, 12</li>
                            <li>Tripla Chance: 1X2, 1X, X2, 12</li>
                            <li>Win-Draw-Win: 1, X, 2</li>
                            <li>Dupla Chance Alternativa</li>
                        </ul>
                    </div>
                </div>
                
                <div class="market-card">
                    <div class="market-icon">🎯</div>
                    <div class="market-title">Resultado Exato</div>
                    <div class="market-description">
                        Predições para placar exato e intervalos.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>Resultado Exato: 1-0, 2-1, 3-2, etc.</li>
                            <li>Resultado do Intervalo</li>
                            <li>Grupos de Resultado</li>
                            <li>Vitória sem Sofrer Gols</li>
                            <li>Intervalos de Gols: 0-1, 2-3, 4-5, 6+</li>
                        </ul>
                    </div>
                </div>
                
                <div class="market-card">
                    <div class="market-icon">🏆</div>
                    <div class="market-title">Resultado da Partida</div>
                    <div class="market-description">
                        Predições básicas 1X2 e Win-Draw-Win.
                    </div>
                    <div class="market-examples">
                        <div class="example-title">Exemplos:</div>
                        <ul class="example-list">
                            <li>1X2: Casa, Empate, Visitante</li>
                            <li>Win-Draw-Win: 1, X, 2</li>
                            <li>Probabilidades básicas</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_404_page(self):
        """Gera página 404"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Página não encontrada - MaraBet AI</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .error-container {
            background: rgba(255,255,255,0.1);
            padding: 50px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 4em; margin-bottom: 20px; }
        p { font-size: 1.5em; margin-bottom: 30px; }
        .back-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404</h1>
        <p>Página não encontrada</p>
        <button class="back-btn" onclick="location.href='/'">← Voltar ao Início</button>
    </div>
</body>
</html>
"""
    
    def start_server(self):
        """Inicia o servidor HTTP interativo"""
        class InteractiveHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=os.getcwd(), **kwargs)
            
            def do_GET(self):
                path = self.path.split('?')[0]  # Remove query parameters
                
                if path == '/' or path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_main_page()
                    self.wfile.write(html.encode('utf-8'))
                
                elif path == '/matches':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_main_page()  # Reutiliza a página principal
                    self.wfile.write(html.encode('utf-8'))
                
                elif path == '/markets':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_markets_page()
                    self.wfile.write(html.encode('utf-8'))
                
                elif path.startswith('/match/'):
                    match_key = urllib.parse.unquote(path[7:])  # Remove '/match/'
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_match_detail_page(match_key)
                    self.wfile.write(html.encode('utf-8'))
                
                elif path == '/stats':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_main_page()  # Por enquanto, reutiliza a principal
                    self.wfile.write(html.encode('utf-8'))
                
                elif path == '/about':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_markets_page()  # Por enquanto, reutiliza mercados
                    self.wfile.write(html.encode('utf-8'))
                
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_404_page()
                    self.wfile.write(html.encode('utf-8'))
        
        try:
            with socketserver.TCPServer(("", self.port), InteractiveHandler) as httpd:
                print(f"🚀 Dashboard Interativo iniciado!")
                print(f"🌐 URL Principal: http://localhost:{self.port}")
                print(f"📊 Dashboard: http://localhost:{self.port}/")
                print(f"⚽ Partidas: http://localhost:{self.port}/matches")
                print(f"📊 Mercados: http://localhost:{self.port}/markets")
                print(f"📈 Estatísticas: http://localhost:{self.port}/stats")
                print(f"ℹ️ Sobre: http://localhost:{self.port}/about")
                print("\n🎯 FUNCIONALIDADES INTERATIVAS:")
                print("   • Clique nos cards para navegar")
                print("   • Clique nas partidas para ver detalhes")
                print("   • Menu de navegação no topo")
                print("   • Páginas específicas para cada seção")
                print("\n🛑 Pressione Ctrl+C para parar")
                print("=" * 60)
                
                # Abrir automaticamente no navegador
                webbrowser.open(f'http://localhost:{self.port}')
                
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard interativo parado pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    global dashboard
    dashboard = InteractiveDashboard()
    
    print("🎯 MARABET AI - DASHBOARD INTERATIVO COMPLETO")
    print("=" * 60)
    print(f"📁 Arquivos de predições encontrados: {len(dashboard.predictions_data)}")
    print(f"📊 Total de predições: {sum(data['total_predictions'] for data in dashboard.predictions_data.values())}")
    print()
    
    dashboard.start_server()

if __name__ == "__main__":
    main()
