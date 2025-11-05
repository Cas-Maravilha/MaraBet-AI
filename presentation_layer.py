"""
CAMADA DE APRESENTAÇÃO - MaraBet AI
Sistema modular para dashboard, API REST e notificações
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DashboardData:
    """Dados para dashboard"""
    title: str
    data_type: str
    data: Dict[str, Any]
    charts: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    timestamp: datetime
    refresh_interval: int = 300  # segundos

@dataclass
class APIResponse:
    """Resposta da API"""
    success: bool
    data: Any
    message: str
    timestamp: datetime
    status_code: int = 200

@dataclass
class Notification:
    """Notificação"""
    id: str
    type: str  # email, sms, push, webhook
    recipient: str
    subject: str
    content: str
    priority: str  # low, medium, high, critical
    timestamp: datetime
    status: str = "pending"  # pending, sent, failed

class DashboardInterface(ABC):
    """Interface abstrata para dashboards"""
    
    @abstractmethod
    def create_dashboard(self, data: DashboardData) -> str:
        """Cria dashboard"""
        pass
    
    @abstractmethod
    def update_dashboard(self, dashboard_id: str, data: DashboardData) -> bool:
        """Atualiza dashboard"""
        pass
    
    @abstractmethod
    def get_dashboard_data(self, dashboard_id: str) -> Optional[DashboardData]:
        """Recupera dados do dashboard"""
        pass

class WebDashboard(DashboardInterface):
    """Dashboard web"""
    
    def __init__(self):
        self.dashboards: Dict[str, DashboardData] = {}
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura rotas da API"""
        
        @self.app.route('/api/dashboards', methods=['GET'])
        def get_dashboards():
            return jsonify({
                'dashboards': [
                    {
                        'id': dashboard_id,
                        'title': data.title,
                        'data_type': data.data_type,
                        'timestamp': data.timestamp.isoformat()
                    }
                    for dashboard_id, data in self.dashboards.items()
                ]
            })
        
        @self.app.route('/api/dashboards/<dashboard_id>', methods=['GET'])
        def get_dashboard(dashboard_id):
            if dashboard_id in self.dashboards:
                data = self.dashboards[dashboard_id]
                return jsonify({
                    'id': dashboard_id,
                    'title': data.title,
                    'data_type': data.data_type,
                    'data': data.data,
                    'charts': data.charts,
                    'metrics': data.metrics,
                    'timestamp': data.timestamp.isoformat()
                })
            return jsonify({'error': 'Dashboard não encontrado'}), 404
        
        @self.app.route('/api/dashboards', methods=['POST'])
        def create_dashboard():
            data = request.json
            dashboard_id = f"dashboard_{len(self.dashboards) + 1}"
            
            dashboard_data = DashboardData(
                title=data.get('title', 'Novo Dashboard'),
                data_type=data.get('data_type', 'general'),
                data=data.get('data', {}),
                charts=data.get('charts', []),
                metrics=data.get('metrics', {}),
                timestamp=datetime.now()
            )
            
            self.dashboards[dashboard_id] = dashboard_data
            return jsonify({'id': dashboard_id, 'message': 'Dashboard criado'})
        
        @self.app.route('/')
        def index():
            return self._render_dashboard_template()
    
    def _render_dashboard_template(self) -> str:
        """Renderiza template do dashboard"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MaraBet AI - Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #f9f9f9; }
                .metric { font-size: 24px; font-weight: bold; color: #2c3e50; }
                .chart-container { height: 300px; }
            </style>
        </head>
        <body>
            <h1>MaraBet AI - Dashboard</h1>
            <div class="dashboard">
                <div class="card">
                    <h3>Análises Ativas</h3>
                    <div class="metric" id="active-analyses">0</div>
                </div>
                <div class="card">
                    <h3>Taxa de Acerto</h3>
                    <div class="metric" id="accuracy-rate">0%</div>
                </div>
                <div class="card">
                    <h3>ROI Médio</h3>
                    <div class="metric" id="avg-roi">0%</div>
                </div>
                <div class="card">
                    <h3>Gráfico de Performance</h3>
                    <div class="chart-container">
                        <canvas id="performance-chart"></canvas>
                    </div>
                </div>
            </div>
            
            <script>
                // Simula dados do dashboard
                document.getElementById('active-analyses').textContent = '12';
                document.getElementById('accuracy-rate').textContent = '73.5%';
                document.getElementById('avg-roi').textContent = '+8.4%';
                
                // Gráfico de performance
                const ctx = document.getElementById('performance-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                        datasets: [{
                            label: 'ROI (%)',
                            data: [5.2, 7.8, 6.1, 9.3, 8.7, 8.4],
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            </script>
        </body>
        </html>
        """
        return template
    
    def create_dashboard(self, data: DashboardData) -> str:
        """Cria dashboard"""
        dashboard_id = f"dashboard_{len(self.dashboards) + 1}"
        self.dashboards[dashboard_id] = data
        logger.info(f"Dashboard {dashboard_id} criado")
        return dashboard_id
    
    def update_dashboard(self, dashboard_id: str, data: DashboardData) -> bool:
        """Atualiza dashboard"""
        if dashboard_id in self.dashboards:
            self.dashboards[dashboard_id] = data
            logger.info(f"Dashboard {dashboard_id} atualizado")
            return True
        return False
    
    def get_dashboard_data(self, dashboard_id: str) -> Optional[DashboardData]:
        """Recupera dados do dashboard"""
        return self.dashboards.get(dashboard_id)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Executa o servidor web"""
        logger.info(f"Iniciando servidor web em http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

class APIManager:
    """Gerenciador de API REST"""
    
    def __init__(self):
        self.endpoints: Dict[str, callable] = {}
        self.app = Flask(__name__)
        self._setup_cors()
        self._setup_routes()
    
    def _setup_cors(self):
        """Configura CORS"""
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
            return response
    
    def _setup_routes(self):
        """Configura rotas da API"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        @self.app.route('/api/analyses', methods=['GET'])
        def get_analyses():
            # Simula dados de análises
            analyses = [
                {
                    'id': 'analysis_001',
                    'home_team': 'Manchester City',
                    'away_team': 'Arsenal',
                    'league': 'Premier League',
                    'date': '2024-01-15',
                    'recommendation': 'Over 2.5 Goals',
                    'confidence': 0.75,
                    'expected_value': 0.12,
                    'status': 'active'
                }
            ]
            return jsonify({'analyses': analyses})
        
        @self.app.route('/api/analyses/<analysis_id>', methods=['GET'])
        def get_analysis(analysis_id):
            # Simula dados de análise específica
            analysis = {
                'id': analysis_id,
                'home_team': 'Manchester City',
                'away_team': 'Arsenal',
                'league': 'Premier League',
                'date': '2024-01-15',
                'recommendation': 'Over 2.5 Goals',
                'confidence': 0.75,
                'expected_value': 0.12,
                'odds': 1.65,
                'stake_recommendation': 0.05,
                'risk_level': 'medium',
                'status': 'active'
            }
            return jsonify(analysis)
        
        @self.app.route('/api/predictions', methods=['POST'])
        def create_prediction():
            data = request.json
            
            # Simula criação de predição
            prediction = {
                'id': f"pred_{datetime.now().timestamp()}",
                'home_team': data.get('home_team'),
                'away_team': data.get('away_team'),
                'league': data.get('league'),
                'match_date': data.get('match_date'),
                'prediction': 'Over 2.5 Goals',
                'confidence': 0.78,
                'expected_value': 0.15,
                'created_at': datetime.now().isoformat()
            }
            
            return jsonify(prediction), 201
        
        @self.app.route('/api/notifications', methods=['GET'])
        def get_notifications():
            # Simula notificações
            notifications = [
                {
                    'id': 'notif_001',
                    'type': 'analysis_complete',
                    'title': 'Análise Concluída',
                    'message': 'Análise Manchester City vs Arsenal foi concluída',
                    'timestamp': datetime.now().isoformat(),
                    'read': False
                }
            ]
            return jsonify({'notifications': notifications})
    
    def add_endpoint(self, path: str, handler: callable, methods: List[str] = ['GET']):
        """Adiciona endpoint personalizado"""
        self.app.add_url_rule(path, f"custom_{path.replace('/', '_')}", handler, methods=methods)
        self.endpoints[path] = handler
        logger.info(f"Endpoint {path} adicionado")
    
    def run(self, host='0.0.0.0', port=5001, debug=False):
        """Executa o servidor API"""
        logger.info(f"Iniciando API em http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

class NotificationManager:
    """Gerenciador de notificações"""
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self.email_config = None
        self.sms_config = None
        self.webhook_config = None
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """Configura email"""
        self.email_config = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password
        }
        logger.info("Configuração de email definida")
    
    def configure_sms(self, api_key: str, api_url: str):
        """Configura SMS"""
        self.sms_config = {
            'api_key': api_key,
            'api_url': api_url
        }
        logger.info("Configuração de SMS definida")
    
    def configure_webhook(self, webhook_url: str, headers: Dict[str, str] = None):
        """Configura webhook"""
        self.webhook_config = {
            'url': webhook_url,
            'headers': headers or {}
        }
        logger.info("Configuração de webhook definida")
    
    def send_notification(self, notification: Notification) -> bool:
        """Envia notificação"""
        try:
            if notification.type == 'email':
                return self._send_email(notification)
            elif notification.type == 'sms':
                return self._send_sms(notification)
            elif notification.type == 'webhook':
                return self._send_webhook(notification)
            else:
                logger.error(f"Tipo de notificação não suportado: {notification.type}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            notification.status = 'failed'
            return False
    
    def _send_email(self, notification: Notification) -> bool:
        """Envia email"""
        if not self.email_config:
            logger.error("Configuração de email não definida")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = notification.recipient
            msg['Subject'] = notification.subject
            
            msg.attach(MIMEText(notification.content, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            notification.status = 'sent'
            logger.info(f"Email enviado para {notification.recipient}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def _send_sms(self, notification: Notification) -> bool:
        """Envia SMS"""
        if not self.sms_config:
            logger.error("Configuração de SMS não definida")
            return False
        
        try:
            # Simula envio de SMS (em produção, usaria API real)
            logger.info(f"SMS enviado para {notification.recipient}: {notification.content}")
            notification.status = 'sent'
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return False
    
    def _send_webhook(self, notification: Notification) -> bool:
        """Envia webhook"""
        if not self.webhook_config:
            logger.error("Configuração de webhook não definida")
            return False
        
        try:
            payload = {
                'id': notification.id,
                'type': notification.type,
                'subject': notification.subject,
                'content': notification.content,
                'priority': notification.priority,
                'timestamp': notification.timestamp.isoformat()
            }
            
            response = requests.post(
                self.webhook_config['url'],
                json=payload,
                headers=self.webhook_config['headers']
            )
            
            if response.status_code == 200:
                notification.status = 'sent'
                logger.info(f"Webhook enviado para {self.webhook_config['url']}")
                return True
            else:
                logger.error(f"Erro no webhook: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar webhook: {e}")
            return False
    
    def create_notification(self, type: str, recipient: str, subject: str, 
                          content: str, priority: str = 'medium') -> Notification:
        """Cria notificação"""
        notification = Notification(
            id=f"notif_{datetime.now().timestamp()}",
            type=type,
            recipient=recipient,
            subject=subject,
            content=content,
            priority=priority,
            timestamp=datetime.now()
        )
        
        self.notifications.append(notification)
        return notification
    
    def get_notifications(self, status: str = None) -> List[Notification]:
        """Recupera notificações"""
        if status:
            return [n for n in self.notifications if n.status == status]
        return self.notifications

class PresentationManager:
    """Gerenciador da camada de apresentação"""
    
    def __init__(self):
        self.dashboard = WebDashboard()
        self.api = APIManager()
        self.notifications = NotificationManager()
    
    def start_services(self, dashboard_port=5000, api_port=5001):
        """Inicia todos os serviços"""
        logger.info("Iniciando serviços de apresentação")
        
        # Configura notificações
        self.notifications.configure_email(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="marabet@example.com",
            password="password"
        )
        
        # Inicia dashboard e API em threads separadas
        import threading
        
        dashboard_thread = threading.Thread(
            target=self.dashboard.run,
            kwargs={'host': '0.0.0.0', 'port': dashboard_port, 'debug': False}
        )
        
        api_thread = threading.Thread(
            target=self.api.run,
            kwargs={'host': '0.0.0.0', 'port': api_port, 'debug': False}
        )
        
        dashboard_thread.daemon = True
        api_thread.daemon = True
        
        dashboard_thread.start()
        api_thread.start()
        
        logger.info(f"Dashboard disponível em http://localhost:{dashboard_port}")
        logger.info(f"API disponível em http://localhost:{api_port}")
    
    def create_dashboard_data(self, title: str, data_type: str, 
                            data: Dict[str, Any]) -> DashboardData:
        """Cria dados para dashboard"""
        return DashboardData(
            title=title,
            data_type=data_type,
            data=data,
            charts=self._generate_charts(data_type),
            metrics=self._generate_metrics(data_type),
            timestamp=datetime.now()
        )
    
    def _generate_charts(self, data_type: str) -> List[Dict[str, Any]]:
        """Gera gráficos baseados no tipo de dados"""
        if data_type == 'performance':
            return [
                {
                    'type': 'line',
                    'title': 'ROI ao Longo do Tempo',
                    'data': {
                        'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                        'datasets': [{
                            'label': 'ROI (%)',
                            'data': [5.2, 7.8, 6.1, 9.3, 8.7, 8.4],
                            'borderColor': 'rgb(75, 192, 192)'
                        }]
                    }
                }
            ]
        elif data_type == 'predictions':
            return [
                {
                    'type': 'bar',
                    'title': 'Distribuição de Confiança',
                    'data': {
                        'labels': ['Baixa', 'Média', 'Alta', 'Muito Alta'],
                        'datasets': [{
                            'label': 'Número de Análises',
                            'data': [5, 12, 8, 3],
                            'backgroundColor': ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0']
                        }]
                    }
                }
            ]
        return []
    
    def _generate_metrics(self, data_type: str) -> Dict[str, Any]:
        """Gera métricas baseadas no tipo de dados"""
        if data_type == 'performance':
            return {
                'total_analyses': 28,
                'accuracy_rate': 73.5,
                'avg_roi': 8.4,
                'active_predictions': 12
            }
        elif data_type == 'predictions':
            return {
                'pending_analyses': 3,
                'completed_today': 8,
                'high_confidence': 11,
                'value_bets_found': 5
            }
        return {}

if __name__ == "__main__":
    # Teste da camada de apresentação
    manager = PresentationManager()
    
    # Cria dados de dashboard
    dashboard_data = manager.create_dashboard_data(
        title="MaraBet AI - Performance",
        data_type="performance",
        data={'roi': 8.4, 'accuracy': 73.5}
    )
    
    # Cria dashboard
    dashboard_id = manager.dashboard.create_dashboard(dashboard_data)
    print(f"Dashboard criado: {dashboard_id}")
    
    # Cria notificação
    notification = manager.notifications.create_notification(
        type='email',
        recipient='user@example.com',
        subject='Nova Análise Disponível',
        content='Análise Manchester City vs Arsenal foi concluída',
        priority='high'
    )
    
    print(f"Notificação criada: {notification.id}")
    
    # Inicia serviços
    print("Iniciando serviços...")
    manager.start_services()
    
    print("Teste da camada de apresentação concluído!")
    print("Dashboard: http://localhost:5000")
    print("API: http://localhost:5001")
