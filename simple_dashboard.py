#!/usr/bin/env python3
"""
Dashboard Simplificado e Funcional para o sistema de predições expandido MaraBet AI
"""

import json
import os
import webbrowser
from datetime import datetime
import http.server
import socketserver
import urllib.parse

class SimpleDashboard:
    def __init__(self):
        self.port = 8082
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
        """Gera a página principal"""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MaraBet AI - Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; color: white; margin-bottom: 30px; }}
        .header h1 {{ font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ 
            background: white; border-radius: 15px; padding: 20px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); text-align: center;
            transition: transform 0.3s ease; cursor: pointer;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .stat-label {{ font-size: 1.1em; color: #666; }}
        .matches-section {{ background: white; border-radius: 15px; padding: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 2em; margin-bottom: 25px; color: #333; border-bottom: 3px solid #667eea; padding-bottom: 15px; }}
        .match-card {{ 
            border: 1px solid #e0e0e0; border-radius: 15px; padding: 25px; 
            margin-bottom: 25px; background: #f9f9f9; transition: all 0.3s ease;
            cursor: pointer;
        }}
        .match-card:hover {{ box-shadow: 0 8px 25px rgba(0,0,0,0.15); transform: translateY(-3px); }}
        .match-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .match-title {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .match-league {{ background: #667eea; color: white; padding: 8px 20px; border-radius: 25px; font-size: 1em; }}
        .match-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px; }}
        .match-stat {{ text-align: center; padding: 15px; background: white; border-radius: 10px; border-left: 4px solid #667eea; }}
        .match-stat-number {{ font-size: 1.5em; font-weight: bold; color: #667eea; }}
        .match-stat-label {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
        .view-btn {{ 
            background: #28a745; color: white; border: none; padding: 12px 25px; 
            border-radius: 25px; font-size: 1em; cursor: pointer; 
            transition: all 0.3s ease; margin-top: 15px; width: 100%;
        }}
        .view-btn:hover {{ background: #218838; transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MaraBet AI</h1>
            <p>Dashboard Interativo de Predições Expandidas</p>
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
                
                <button class="view-btn" onclick="event.stopPropagation(); location.href='/match/{urllib.parse.quote(match_key)}'">
                    📊 Ver Detalhes Completos
                </button>
            </div>
"""
        
        html += f"""
        </div>
        
        <div style="text-align: center; color: white; margin-top: 40px; padding: 20px; opacity: 0.8;">
            <p>Dashboard atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p>🎯 Sistema MaraBet AI - Predições Profissionais</p>
        </div>
    </div>
    
    <script>
        setTimeout(() => {{ location.reload(); }}, 60000);
    </script>
</body>
</html>
"""
        return html
    
    def generate_match_detail_page(self, match_key):
        """Gera página de detalhes de uma partida"""
        if match_key not in self.predictions_data:
            return self.generate_404_page()
        
        data = self.predictions_data[match_key]
        match_data = data['match_data']
        predictions = data['predictions']
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{match_key} - MaraBet AI</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .back-btn {{ 
            background: rgba(255,255,255,0.2); color: white; border: none; 
            padding: 10px 20px; border-radius: 25px; font-size: 1em; 
            cursor: pointer; transition: all 0.3s ease; margin-bottom: 20px;
        }}
        .back-btn:hover {{ background: rgba(255,255,255,0.3); }}
        .match-header {{ 
            background: white; border-radius: 15px; padding: 30px; 
            margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .match-title {{ font-size: 2.5em; color: #333; margin-bottom: 10px; }}
        .match-league {{ 
            background: #667eea; color: white; padding: 10px 25px; 
            border-radius: 25px; font-size: 1.2em; display: inline-block; margin-bottom: 20px;
        }}
        .match-info {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; margin-top: 20px;
        }}
        .info-item {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px; }}
        .info-label {{ font-size: 0.9em; color: #666; margin-bottom: 5px; }}
        .info-value {{ font-size: 1.2em; font-weight: bold; color: #333; }}
        .predictions-section {{ 
            background: white; border-radius: 15px; padding: 30px; 
            margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .section-title {{ 
            font-size: 1.8em; margin-bottom: 25px; color: #333; 
            border-bottom: 3px solid #667eea; padding-bottom: 15px;
        }}
        .category-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 25px;
        }}
        .category-card {{ 
            border: 1px solid #e0e0e0; border-radius: 15px; padding: 25px; 
            background: #f9f9f9; transition: all 0.3s ease;
        }}
        .category-card:hover {{ box-shadow: 0 8px 25px rgba(0,0,0,0.1); transform: translateY(-3px); }}
        .category-title {{ 
            font-size: 1.3em; font-weight: bold; color: #333; 
            margin-bottom: 20px; text-align: center; padding-bottom: 10px; 
            border-bottom: 2px solid #667eea;
        }}
        .prediction-item {{ 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 12px 0; border-bottom: 1px solid #f0f0f0; 
            transition: all 0.3s ease;
        }}
        .prediction-item:hover {{ 
            background: rgba(102, 126, 234, 0.1); padding-left: 10px; border-radius: 5px;
        }}
        .prediction-item:last-child {{ border-bottom: none; }}
        .prediction-name {{ font-size: 1em; color: #555; flex: 1; }}
        .prediction-prob {{ 
            font-weight: bold; font-size: 1.1em; padding: 5px 12px; border-radius: 15px;
        }}
        .confidence-high {{ color: white; background: #28a745; }}
        .confidence-medium {{ color: white; background: #ffc107; }}
        .confidence-low {{ color: white; background: #dc3545; }}
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
                    html += f"""
                    <div class="prediction-item">
                        <span class="prediction-name">{bet_type}</span>
                        <span class="prediction-prob {confidence_class}">{prob:.1%}</span>
                    </div>
"""
                
                html += """
                </div>
"""
        
        html += f"""
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
        """Inicia o servidor HTTP"""
        class SimpleHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=os.getcwd(), **kwargs)
            
            def do_GET(self):
                path = self.path.split('?')[0]
                
                if path == '/' or path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_main_page()
                    self.wfile.write(html.encode('utf-8'))
                
                elif path.startswith('/match/'):
                    match_key = urllib.parse.unquote(path[7:])
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_match_detail_page(match_key)
                    self.wfile.write(html.encode('utf-8'))
                
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html = dashboard.generate_404_page()
                    self.wfile.write(html.encode('utf-8'))
        
        try:
            with socketserver.TCPServer(("", self.port), SimpleHandler) as httpd:
                print(f"🚀 Dashboard Simplificado iniciado!")
                print(f"🌐 URL: http://localhost:{self.port}")
                print(f"📊 Dashboard: http://localhost:{self.port}/")
                print("\n🎯 FUNCIONALIDADES:")
                print("   • Página principal com estatísticas")
                print("   • Partidas clicáveis para detalhes")
                print("   • Predições detalhadas por categoria")
                print("   • Níveis de confiança coloridos")
                print("\n🛑 Pressione Ctrl+C para parar")
                print("=" * 50)
                
                webbrowser.open(f'http://localhost:{self.port}')
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard parado pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    global dashboard
    dashboard = SimpleDashboard()
    
    print("🎯 MARABET AI - DASHBOARD SIMPLIFICADO")
    print("=" * 50)
    print(f"📁 Arquivos de predições encontrados: {len(dashboard.predictions_data)}")
    print(f"📊 Total de predições: {sum(data['total_predictions'] for data in dashboard.predictions_data.values())}")
    print()
    
    dashboard.start_server()

if __name__ == "__main__":
    main()
