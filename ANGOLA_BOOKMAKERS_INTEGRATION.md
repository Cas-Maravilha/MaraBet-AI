# 🎰 Integração com Casas de Apostas Angolanas

> **Integração completa com as principais casas de apostas do mercado angolano**

## 🎯 Visão Geral

O MaraBet AI foi desenvolvido com integração nativa para as principais casas de apostas angolanas, permitindo coleta automática de odds, comparação de mercados e identificação de valor em tempo real.

## 🏆 Casas de Apostas Integradas

### **1. ElephantBet Angola** 🐘
- **Prioridade**: Alta (Casa principal)
- **Foco**: Girabola e ligas angolanas
- **Mercados**: 1x2, Over/Under, BTTS, Handicap, Dupla Chance
- **Especialidade**: Odds do Girabola

### **2. KwanzaBet Angola** 💰
- **Prioridade**: Alta (Especializada em AOA)
- **Foco**: Moeda local e ligas angolanas
- **Mercados**: 1x2, Over/Under, BTTS, Handicap, Dupla Chance
- **Especialidade**: Conversão automática para AOA

### **3. PremierBet Angola** 👑
- **Prioridade**: Alta (Casa popular)
- **Foco**: Odds ao vivo e mercados variados
- **Mercados**: 1x2, Over/Under, BTTS, Handicap, Dupla Chance, Live
- **Especialidade**: Apostas ao vivo

### **4. Bantubet Angola** 🏛️
- **Prioridade**: Média (Casa regional)
- **Foco**: Times regionais e ligas locais
- **Mercados**: 1x2, Over/Under, BTTS, Handicap, Dupla Chance
- **Especialidade**: Times de regiões específicas

### **5. 1xBet Angola** 🌍
- **Prioridade**: Alta (Casa internacional)
- **Foco**: Ligas internacionais e locais
- **Mercados**: 1x2, Over/Under, BTTS, Handicap, Dupla Chance, Live
- **Especialidade**: Ligas europeias e mundiais

### **6. MoBet Angola** 📱
- **Prioridade**: Média (Casa móvel)
- **Foco**: Interface móvel otimizada
- **Mercados**: 1x2, Over/Under, BTTS, Handicap, Dupla Chance
- **Especialidade**: Apostas móveis

## 🔧 Implementação Técnica

### **Classe Base para Casas de Apostas**
```python
# angola_bookmaker_base.py
from abc import ABC, abstractmethod
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class AngolaBookmakerBase(ABC):
    """Classe base para casas de apostas angolanas"""
    
    def __init__(self, name: str, base_url: str, currency: str = "AOA"):
        self.name = name
        self.base_url = base_url
        self.currency = currency
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MaraBet-AI/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    @abstractmethod
    def get_odds(self, match_id: str) -> Dict:
        """Obtém odds de uma partida específica"""
        pass
    
    @abstractmethod
    def get_markets(self, match_id: str) -> List[Dict]:
        """Obtém mercados disponíveis para uma partida"""
        pass
    
    def convert_to_aoa(self, amount: float, from_currency: str = "USD") -> float:
        """Converte valor para Kwanza Angolano"""
        if from_currency == "AOA":
            return amount
        
        # Implementar conversão de moeda
        exchange_rate = self.get_exchange_rate(from_currency, "AOA")
        return amount * exchange_rate
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Obtém taxa de câmbio"""
        # Implementar API de câmbio
        pass
```

### **Implementação ElephantBet Angola**
```python
# elephantbet_angola.py
from angola_bookmaker_base import AngolaBookmakerBase
import requests
from typing import Dict, List

class ElephantBetAngola(AngolaBookmakerBase):
    """Integração com ElephantBet Angola"""
    
    def __init__(self):
        super().__init__(
            name="ElephantBet Angola",
            base_url="https://api.elephantbet.ao",
            currency="AOA"
        )
        self.priority = "high"
        self.specialties = ["girabola", "angola_leagues"]
    
    def get_odds(self, match_id: str) -> Dict:
        """Obtém odds da ElephantBet Angola"""
        try:
            response = self.session.get(
                f"{self.base_url}/odds/{match_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_odds_data(data)
            
        except requests.RequestException as e:
            print(f"Erro ao obter odds da ElephantBet: {e}")
            return {}
    
    def get_girabola_odds(self, match_id: str) -> Dict:
        """Obtém odds específicas do Girabola"""
        try:
            response = self.session.get(
                f"{self.base_url}/girabola/odds/{match_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_girabola_odds(data)
            
        except requests.RequestException as e:
            print(f"Erro ao obter odds do Girabola: {e}")
            return {}
    
    def _process_odds_data(self, data: Dict) -> Dict:
        """Processa dados de odds"""
        return {
            "bookmaker": self.name,
            "match_id": data.get("match_id"),
            "markets": self._extract_markets(data),
            "currency": self.currency,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_markets(self, data: Dict) -> List[Dict]:
        """Extrai mercados disponíveis"""
        markets = []
        
        # Mercado 1x2
        if "1x2" in data:
            markets.append({
                "type": "1x2",
                "selections": [
                    {"name": "1", "odds": data["1x2"]["home"]},
                    {"name": "X", "odds": data["1x2"]["draw"]},
                    {"name": "2", "odds": data["1x2"]["away"]}
                ]
            })
        
        # Mercado Over/Under
        if "over_under" in data:
            markets.append({
                "type": "over_under",
                "selections": [
                    {"name": "Over 2.5", "odds": data["over_under"]["over"]},
                    {"name": "Under 2.5", "odds": data["over_under"]["under"]}
                ]
            })
        
        return markets
```

### **Implementação KwanzaBet Angola**
```python
# kwanzabet_angola.py
from angola_bookmaker_base import AngolaBookmakerBase
import requests
from typing import Dict, List

class KwanzaBetAngola(AngolaBookmakerBase):
    """Integração com KwanzaBet Angola"""
    
    def __init__(self):
        super().__init__(
            name="KwanzaBet Angola",
            base_url="https://api.kwanzabet.ao",
            currency="AOA"
        )
        self.priority = "high"
        self.specialties = ["aoa_currency", "angola_leagues"]
    
    def get_odds(self, match_id: str) -> Dict:
        """Obtém odds da KwanzaBet Angola"""
        try:
            response = self.session.get(
                f"{self.base_url}/odds/{match_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_odds_data(data)
            
        except requests.RequestException as e:
            print(f"Erro ao obter odds da KwanzaBet: {e}")
            return {}
    
    def get_angola_odds(self, match_id: str) -> Dict:
        """Obtém odds de ligas angolanas"""
        try:
            response = self.session.get(
                f"{self.base_url}/angola/odds/{match_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_angola_odds(data)
            
        except requests.RequestException as e:
            print(f"Erro ao obter odds angolanas: {e}")
            return {}
```

### **Implementação PremierBet Angola**
```python
# premierbet_angola.py
from angola_bookmaker_base import AngolaBookmakerBase
import requests
from typing import Dict, List

class PremierBetAngola(AngolaBookmakerBase):
    """Integração com PremierBet Angola"""
    
    def __init__(self):
        super().__init__(
            name="PremierBet Angola",
            base_url="https://api.premierbet.ao",
            currency="AOA"
        )
        self.priority = "high"
        self.specialties = ["live_odds", "popular_markets"]
    
    def get_odds(self, match_id: str) -> Dict:
        """Obtém odds da PremierBet Angola"""
        try:
            response = self.session.get(
                f"{self.base_url}/odds/{match_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_odds_data(data)
            
        except requests.RequestException as e:
            print(f"Erro ao obter odds da PremierBet: {e}")
            return {}
    
    def get_live_odds(self, match_id: str) -> Dict:
        """Obtém odds ao vivo"""
        try:
            response = self.session.get(
                f"{self.base_url}/live/odds/{match_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_live_odds(data)
            
        except requests.RequestException as e:
            print(f"Erro ao obter odds ao vivo: {e}")
            return {}
```

## 🔄 Gerenciador de Casas de Apostas

### **Classe Principal de Integração**
```python
# angola_bookmaker_manager.py
from typing import Dict, List, Optional
from elephantbet_angola import ElephantBetAngola
from kwanzabet_angola import KwanzaBetAngola
from premierbet_angola import PremierBetAngola
from bantubet_angola import BantubetAngola
from onexbet_angola import OneXBetAngola
from mobet_angola import MoBetAngola

class AngolaBookmakerManager:
    """Gerenciador de casas de apostas angolanas"""
    
    def __init__(self):
        self.bookmakers = {
            "elephantbet": ElephantBetAngola(),
            "kwanzabet": KwanzaBetAngola(),
            "premierbet": PremierBetAngola(),
            "bantubet": BantubetAngola(),
            "onexbet": OneXBetAngola(),
            "mobet": MoBetAngola()
        }
        self.priority_order = ["elephantbet", "kwanzabet", "premierbet", "onexbet", "bantubet", "mobet"]
    
    def get_all_odds(self, match_id: str) -> Dict[str, Dict]:
        """Obtém odds de todas as casas de apostas"""
        all_odds = {}
        
        for bookmaker_name, bookmaker in self.bookmakers.items():
            try:
                odds = bookmaker.get_odds(match_id)
                if odds:
                    all_odds[bookmaker_name] = odds
            except Exception as e:
                print(f"Erro ao obter odds da {bookmaker_name}: {e}")
        
        return all_odds
    
    def get_best_odds(self, match_id: str, market_type: str) -> Dict:
        """Obtém as melhores odds para um mercado específico"""
        all_odds = self.get_all_odds(match_id)
        best_odds = {}
        
        for bookmaker_name, odds_data in all_odds.items():
            for market in odds_data.get("markets", []):
                if market["type"] == market_type:
                    for selection in market["selections"]:
                        selection_name = selection["name"]
                        odds_value = selection["odds"]
                        
                        if selection_name not in best_odds or odds_value > best_odds[selection_name]["odds"]:
                            best_odds[selection_name] = {
                                "odds": odds_value,
                                "bookmaker": bookmaker_name,
                                "currency": "AOA"
                            }
        
        return best_odds
    
    def compare_odds(self, match_id: str) -> Dict:
        """Compara odds entre todas as casas"""
        all_odds = self.get_all_odds(match_id)
        comparison = {}
        
        for bookmaker_name, odds_data in all_odds.items():
            comparison[bookmaker_name] = {
                "markets_available": len(odds_data.get("markets", [])),
                "currency": odds_data.get("currency", "AOA"),
                "timestamp": odds_data.get("timestamp"),
                "markets": odds_data.get("markets", [])
            }
        
        return comparison
```

## 📊 Configuração de Prioridades

### **Configuração de Casas de Apostas**
```python
# angola_bookmaker_config.py
ANGOLA_BOOKMAKER_CONFIG = {
    "elephantbet": {
        "priority": 1,
        "enabled": True,
        "specialties": ["girabola", "angola_leagues"],
        "markets": ["1x2", "over_under", "btts", "handicap", "dupla_chance"],
        "update_interval": 30  # segundos
    },
    "kwanzabet": {
        "priority": 2,
        "enabled": True,
        "specialties": ["aoa_currency", "angola_leagues"],
        "markets": ["1x2", "over_under", "btts", "handicap", "dupla_chance"],
        "update_interval": 30
    },
    "premierbet": {
        "priority": 3,
        "enabled": True,
        "specialties": ["live_odds", "popular_markets"],
        "markets": ["1x2", "over_under", "btts", "handicap", "dupla_chance", "live"],
        "update_interval": 15  # mais frequente para odds ao vivo
    },
    "onexbet": {
        "priority": 4,
        "enabled": True,
        "specialties": ["international_leagues", "variety"],
        "markets": ["1x2", "over_under", "btts", "handicap", "dupla_chance", "live"],
        "update_interval": 30
    },
    "bantubet": {
        "priority": 5,
        "enabled": True,
        "specialties": ["regional_teams", "local_focus"],
        "markets": ["1x2", "over_under", "btts", "handicap", "dupla_chance"],
        "update_interval": 60
    },
    "mobet": {
        "priority": 6,
        "enabled": True,
        "specialties": ["mobile_optimized", "convenience"],
        "markets": ["1x2", "over_under", "btts", "handicap", "dupla_chance"],
        "update_interval": 45
    }
}
```

## 🚀 Uso Prático

### **Exemplo de Integração**
```python
# exemplo_uso.py
from angola_bookmaker_manager import AngolaBookmakerManager

# Inicializar gerenciador
manager = AngolaBookmakerManager()

# Obter odds de uma partida
match_id = "girabola_2024_001"
all_odds = manager.get_all_odds(match_id)

# Comparar odds
comparison = manager.compare_odds(match_id)

# Obter melhores odds para mercado 1x2
best_1x2 = manager.get_best_odds(match_id, "1x2")

print("Melhores odds 1x2:")
for selection, data in best_1x2.items():
    print(f"{selection}: {data['odds']} ({data['bookmaker']})")
```

## 📈 Monitoramento e Métricas

### **Métricas de Performance**
```python
# angola_bookmaker_metrics.py
class AngolaBookmakerMetrics:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0,
            "odds_updates": 0,
            "best_odds_found": 0
        }
    
    def record_request(self, bookmaker: str, success: bool, response_time: float):
        """Registra métrica de requisição"""
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        # Atualizar tempo médio de resposta
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["total_requests"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_success_rate(self) -> float:
        """Calcula taxa de sucesso"""
        if self.metrics["total_requests"] == 0:
            return 0.0
        
        return self.metrics["successful_requests"] / self.metrics["total_requests"]
```

---

**Integração completa com casas de apostas angolanas!** 🇦🇴🎰

*Maximize suas oportunidades de apostas com acesso a todas as principais casas do mercado angolano.*
