#!/usr/bin/env python3
"""
Dashboard simplificado para o sistema de predições expandido MaraBet AI
"""

import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path
import http.server
import socketserver
import threading
import time

class PredictionDashboard:
    def __init__(self):
        self.port = 8080
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
    
    def generate_html(self):
        """Gera o HTML do dashboard"""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MaraBet AI - Dashboard de Predições</title>
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
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
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
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            color: #666;
        }}
        
        .matches-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .match-card {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background: #f9f9f9;
            transition: all 0.3s ease;
        }}
        
        .match-card:hover {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .match-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .match-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .match-league {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .predictions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .prediction-category {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #667eea;
        }}
        
        .category-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .prediction-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .prediction-item:last-child {{
            border-bottom: none;
        }}
        
        .prediction-name {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .prediction-prob {{
            font-weight: bold;
            color: #667eea;
        }}
        
        .confidence-high {{ color: #28a745; }}
        .confidence-medium {{ color: #ffc107; }}
        .confidence-low {{ color: #dc3545; }}
        
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 20px auto;
            display: block;
        }}
        
        .refresh-btn:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MaraBet AI</h1>
            <p>Dashboard de Predições Expandidas</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(self.predictions_data)}</div>
                <div class="stat-label">Partidas Analisadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(data['total_predictions'] for data in self.predictions_data.values())}</div>
                <div class="stat-label">Total de Predições</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(data['match_data'].get('league', 'Unknown') for data in self.predictions_data.values()))}</div>
                <div class="stat-label">Ligas Cobertas</div>
            </div>
            <div class="stat-card">
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
            
            html += f"""
            <div class="match-card">
                <div class="match-header">
                    <div class="match-title">{match_key}</div>
                    <div class="match-league">{match_data.get('league', 'N/A')}</div>
                </div>
                
                <div class="predictions-grid">
"""
            
            for category, preds in predictions.items():
                if isinstance(preds, dict):
                    html += f"""
                    <div class="prediction-category">
                        <div class="category-title">{category.upper()}</div>
"""
                    
                    count = 0
                    for bet_type, prob in preds.items():
                        if count < 5:  # Mostrar apenas as primeiras 5 predições
                            confidence_class = "confidence-high" if prob > 0.7 else "confidence-medium" if prob > 0.5 else "confidence-low"
                            html += f"""
                        <div class="prediction-item">
                            <span class="prediction-name">{bet_type}</span>
                            <span class="prediction-prob {confidence_class}">{prob:.1%}</span>
                        </div>
"""
                            count += 1
                    
                    if len(preds) > 5:
                        html += f"""
                        <div class="prediction-item">
                            <span class="prediction-name">... e mais {len(preds) - 5}</span>
                            <span class="prediction-prob">-</span>
                        </div>
"""
                    
                    html += """
                    </div>
"""
            
            html += f"""
                </div>
                <div class="timestamp">
                    Gerado em: {data['generated_at']} | Total: {data['total_predictions']} predições
                </div>
            </div>
"""
        
        html += f"""
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Atualizar Dados</button>
        
        <div class="timestamp">
            Dashboard atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Auto-refresh a cada 30 segundos
        setTimeout(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
        return html
    
    def start_server(self):
        """Inicia o servidor HTTP"""
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=os.getcwd(), **kwargs)
            
            def do_GET(self):
                if self.path == '/' or self.path == '/dashboard':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_html()
                    self.wfile.write(html.encode('utf-8'))
                else:
                    super().do_GET()
        
        try:
            with socketserver.TCPServer(("", self.port), CustomHandler) as httpd:
                print(f"🚀 Dashboard iniciado em http://localhost:{self.port}")
                print(f"📊 Acesse: http://localhost:{self.port}/dashboard")
                print("🛑 Pressione Ctrl+C para parar")
                
                # Abrir automaticamente no navegador
                webbrowser.open(f'http://localhost:{self.port}/dashboard')
                
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard parado pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    global dashboard
    dashboard = PredictionDashboard()
    
    print("🎯 MARABET AI - DASHBOARD DE PREDIÇÕES EXPANDIDAS")
    print("=" * 60)
    print(f"📁 Arquivos de predições encontrados: {len(dashboard.predictions_data)}")
    print(f"📊 Total de predições: {sum(data['total_predictions'] for data in dashboard.predictions_data.values())}")
    print()
    
    dashboard.start_server()

if __name__ == "__main__":
    main()
