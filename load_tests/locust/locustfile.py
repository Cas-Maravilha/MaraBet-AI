"""
Testes de Carga com Locust - MaraBet AI
Simula usuários acessando o sistema de previsões
"""

from locust import HttpUser, task, between
import random
import json

class MaraBetUser(HttpUser):
    """Simula usuário do MaraBet AI"""
    
    # Tempo de espera entre requisições (1-5 segundos)
    wait_time = between(1, 5)
    
    def on_start(self):
        """Executado quando usuário inicia"""
        # Fazer login
        self.login()
    
    def login(self):
        """Autentica usuário"""
        response = self.client.post("/api/auth/login", json={
            "username": "teste",
            "password": "marabet123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(5)
    def view_home(self):
        """Acessa página inicial"""
        self.client.get("/")
    
    @task(10)
    def view_predictions(self):
        """Visualiza previsões"""
        self.client.get("/api/predictions/today")
    
    @task(8)
    def view_live_predictions(self):
        """Visualiza previsões ao vivo"""
        self.client.get("/api/predictions/live")
    
    @task(3)
    def view_prediction_detail(self):
        """Visualiza detalhes de previsão"""
        prediction_id = random.randint(1, 100)
        self.client.get(f"/api/predictions/{prediction_id}")
    
    @task(2)
    def view_statistics(self):
        """Visualiza estatísticas"""
        self.client.get("/api/statistics")
    
    @task(2)
    def view_teams(self):
        """Visualiza times"""
        self.client.get("/api/teams")
    
    @task(1)
    def create_bet(self):
        """Cria uma aposta"""
        self.client.post("/api/bets", json={
            "prediction_id": random.randint(1, 50),
            "stake": random.choice([100, 200, 500, 1000]),
            "bookmaker": random.choice(["SportingBet", "Bet365", "1xBet"])
        })
    
    @task(2)
    def view_bankroll(self):
        """Visualiza bankroll"""
        self.client.get("/api/bankroll")
    
    @task(1)
    def view_history(self):
        """Visualiza histórico"""
        self.client.get("/api/history")

class AdminUser(HttpUser):
    """Simula usuário administrador"""
    
    wait_time = between(2, 8)
    
    def on_start(self):
        """Login como admin"""
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "marabet123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def view_dashboard(self):
        """Visualiza dashboard admin"""
        self.client.get("/api/admin/dashboard")
    
    @task(2)
    def view_users(self):
        """Lista usuários"""
        self.client.get("/api/admin/users")
    
    @task(1)
    def view_system_stats(self):
        """Visualiza estatísticas do sistema"""
        self.client.get("/api/admin/stats")

# Configuração de testes
# Executar: locust -f locustfile.py --host=http://localhost:8000
