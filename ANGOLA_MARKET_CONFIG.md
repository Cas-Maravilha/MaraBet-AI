# 🇦🇴 MaraBet AI - Configuração para o Mercado Angolano

> **Configuração específica para operação no mercado de apostas angolano**

## 🎯 Visão Geral

O MaraBet AI foi adaptado especificamente para o mercado angolano, incluindo suporte à moeda local (Kwanza Angolano - AOA) e ligas angolanas, mantendo as principais ligas internacionais.

## 💰 Configuração de Moeda

### **Moeda Principal: Kwanza Angolano (AOA)**

#### Configuração no Sistema
```bash
# .env
CURRENCY=AOA
CURRENCY_SYMBOL=Kz
EXCHANGE_RATE_API=https://api.exchangerate-api.com/v4/latest/USD
DEFAULT_CURRENCY=AOA
```

#### Conversão Automática
```python
# currency_converter.py
class CurrencyConverter:
    def __init__(self):
        self.base_currency = "USD"
        self.target_currency = "AOA"
        self.exchange_rates = self.load_exchange_rates()
    
    def convert_to_aoa(self, amount, from_currency="USD"):
        """Converte valor para Kwanza Angolano"""
        if from_currency == "AOA":
            return amount
        
        rate = self.exchange_rates.get(from_currency, 1.0)
        return amount * rate * self.exchange_rates.get("AOA", 1.0)
    
    def format_currency(self, amount):
        """Formata valor em Kwanza Angolano"""
        return f"Kz {amount:,.2f}"
```

### **Taxa de Câmbio em Tempo Real**
```python
# exchange_rate_service.py
import requests
from datetime import datetime, timedelta

class ExchangeRateService:
    def __init__(self):
        self.api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.cache_duration = timedelta(hours=1)
        self.last_update = None
        self.rates = {}
    
    def get_aoa_rate(self):
        """Obtém taxa de câmbio USD para AOA"""
        if self.should_update():
            self.update_rates()
        
        return self.rates.get("AOA", 1.0)
    
    def should_update(self):
        """Verifica se precisa atualizar as taxas"""
        if not self.last_update:
            return True
        
        return datetime.now() - self.last_update > self.cache_duration
```

## ⚽ Ligas Mundiais Focadas pelas Casas Angolanas

> **Foco Principal**: As casas de apostas em Angola focam nas principais ligas mundiais (Europa, América do Sul, América do Norte, Ásia e África), não necessariamente nas ligas locais angolanas.

### **Priorização por Região**
- **🇪🇺 Europa**: Prioridade máxima (Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League)
- **🇧🇷 América do Sul**: Prioridade alta (Brasileirão, Primera División, Copa Libertadores)
- **🇺🇸 América do Norte**: Prioridade média (MLS, Liga MX)
- **🇯🇵 Ásia**: Prioridade média (J League, K League, Chinese Super League)
- **🌍 África**: Prioridade média (Premier Soccer League, CAF Champions League)

### **Ligas por Prioridade**

#### **🥇 Prioridade Máxima (Europa)**
- **Premier League** (39) - Inglaterra
- **La Liga** (140) - Espanha
- **Bundesliga** (78) - Alemanha
- **Serie A** (135) - Itália
- **Ligue 1** (61) - França
- **UEFA Champions League** (2) - Europa

#### **🥈 Prioridade Alta (América do Sul)**
- **Brasileirão Série A** (71) - Brasil
- **Primera División** (128) - Argentina
- **Copa Libertadores** (13) - América do Sul
- **Primera A** (239) - Colômbia

#### **🥉 Prioridade Média (América do Norte)**
- **Major League Soccer** (253) - EUA/Canadá
- **Liga MX** (262) - México

#### **🥉 Prioridade Média (Ásia)**
- **J1 League** (98) - Japão
- **K League 1** (292) - Coreia do Sul
- **Chinese Super League** (169) - China

#### **🥉 Prioridade Média (África)**
- **Premier Soccer League** (384) - África do Sul
- **CAF Champions League** (14) - África
- **Egyptian Premier League** (307) - Egito

### **Ligas Europeias (Prioridade Máxima)**

> **Foco Principal**: As casas de apostas em Angola focam nas principais ligas mundiais (Europa, América do Sul, América do Norte, Ásia e África), não necessariamente nas ligas locais angolanas.
```python
# european_leagues.py
EUROPEAN_LEAGUES = {
    "premier_league": {
        "id": 39,
        "name": "Premier League",
        "country": "Inglaterra",
        "priority": "high",
        "popularity": "very_high"
    },
    "la_liga": {
        "id": 140,
        "name": "La Liga",
        "country": "Espanha",
        "priority": "high",
        "popularity": "very_high"
    },
    "bundesliga": {
        "id": 78,
        "name": "Bundesliga",
        "country": "Alemanha",
        "priority": "high",
        "popularity": "high"
    },
    "serie_a": {
        "id": 135,
        "name": "Serie A",
        "country": "Itália",
        "priority": "high",
        "popularity": "high"
    },
    "ligue_1": {
        "id": 61,
        "name": "Ligue 1",
        "country": "França",
        "priority": "high",
        "popularity": "high"
    },
    "champions_league": {
        "id": 2,
        "name": "UEFA Champions League",
        "country": "Europa",
        "priority": "very_high",
        "popularity": "very_high"
    }
}
```

### **Ligas da América do Sul (Prioridade Alta)**
```python
# south_american_leagues.py
SOUTH_AMERICAN_LEAGUES = {
    "brasileirao": {
        "id": 71,
        "name": "Brasileirão Série A",
        "country": "Brasil",
        "priority": "high",
        "popularity": "very_high"
    },
    "argentina_primera": {
        "id": 128,
        "name": "Primera División",
        "country": "Argentina",
        "priority": "high",
        "popularity": "high"
    },
    "copa_libertadores": {
        "id": 13,
        "name": "Copa Libertadores",
        "country": "América do Sul",
        "priority": "high",
        "popularity": "very_high"
    },
    "colombia_primera": {
        "id": 239,
        "name": "Primera A",
        "country": "Colômbia",
        "priority": "medium",
        "popularity": "medium"
    }
}
```

### **Ligas da América do Norte (Prioridade Média)**
```python
# north_american_leagues.py
NORTH_AMERICAN_LEAGUES = {
    "mls": {
        "id": 253,
        "name": "Major League Soccer",
        "country": "EUA/Canadá",
        "priority": "medium",
        "popularity": "medium"
    },
    "liga_mx": {
        "id": 262,
        "name": "Liga MX",
        "country": "México",
        "priority": "medium",
        "popularity": "medium"
    }
}
```

### **Ligas Asiáticas (Prioridade Média)**
```python
# asian_leagues.py
ASIAN_LEAGUES = {
    "j_league": {
        "id": 98,
        "name": "J1 League",
        "country": "Japão",
        "priority": "medium",
        "popularity": "medium"
    },
    "k_league": {
        "id": 292,
        "name": "K League 1",
        "country": "Coreia do Sul",
        "priority": "medium",
        "popularity": "medium"
    },
    "chinese_super_league": {
        "id": 169,
        "name": "Chinese Super League",
        "country": "China",
        "priority": "low",
        "popularity": "low"
    }
}
```

### **Ligas Africanas (Prioridade Média)**
```python
# african_leagues.py
AFRICAN_LEAGUES = {
    "premier_soccer_league": {
        "id": 384,
        "name": "Premier Soccer League",
        "country": "África do Sul",
        "priority": "medium",
        "popularity": "medium"
    },
    "caf_champions_league": {
        "id": 14,
        "name": "CAF Champions League",
        "country": "África",
        "priority": "medium",
        "popularity": "medium"
    },
    "egyptian_premier": {
        "id": 307,
        "name": "Egyptian Premier League",
        "country": "Egito",
        "priority": "low",
        "popularity": "low"
    }
}
```

## 🏆 Ligas Internacionais Mantidas

### **Ligas Principais**
```python
INTERNATIONAL_LEAGUES = {
    "premier_league": {
        "id": 39,
        "name": "Premier League",
        "country": "Inglaterra",
        "priority": "high"
    },
    "la_liga": {
        "id": 140,
        "name": "La Liga",
        "country": "Espanha",
        "priority": "high"
    },
    "bundesliga": {
        "id": 78,
        "name": "Bundesliga",
        "country": "Alemanha",
        "priority": "high"
    },
    "serie_a": {
        "id": 135,
        "name": "Serie A",
        "country": "Itália",
        "priority": "high"
    },
    "ligue_1": {
        "id": 61,
        "name": "Ligue 1",
        "country": "França",
        "priority": "high"
    },
    "brasileirao": {
        "id": 71,
        "name": "Brasileirão Série A",
        "country": "Brasil",
        "priority": "medium"
    }
}
```

## 🎰 Casas de Apostas Angolanas

### **Integração com Casas Locais**

#### **ElephantBet Angola**
```python
# elephantbet_angola.py
class ElephantBetAngola:
    def __init__(self):
        self.base_url = "https://elephantbet.ao"
        self.currency = "AOA"
        self.markets = ["1x2", "over_under", "btts", "handicap", "dupla_chance"]
        self.priority = "high"  # Casa principal em Angola
        self.specialties = ["european_leagues", "champions_league", "brasileirao"]
    
    def get_odds(self, match_id):
        """Obtém odds da ElephantBet Angola"""
        # Implementação específica para ElephantBet Angola
        pass
    
    def get_european_odds(self, match_id):
        """Obtém odds de ligas europeias"""
        # Foco em Premier League, La Liga, Bundesliga, Serie A, Ligue 1
        pass
    
    def get_champions_league_odds(self, match_id):
        """Obtém odds da Champions League"""
        # Especialidade em competições europeias
        pass
```

#### **KwanzaBet Angola**
```python
# kwanzabet_angola.py
class KwanzaBetAngola:
    def __init__(self):
        self.base_url = "https://kwanzabet.ao"
        self.currency = "AOA"
        self.markets = ["1x2", "over_under", "btts", "handicap", "dupla_chance"]
        self.priority = "high"  # Casa especializada em AOA
        self.specialties = ["south_american_leagues", "copa_libertadores", "brasileirao"]
    
    def get_odds(self, match_id):
        """Obtém odds da KwanzaBet Angola"""
        # Implementação específica para KwanzaBet Angola
        pass
    
    def get_south_american_odds(self, match_id):
        """Obtém odds de ligas sul-americanas"""
        # Foco em Brasileirão, Primera División, Copa Libertadores
        pass
    
    def get_brasileirao_odds(self, match_id):
        """Obtém odds do Brasileirão"""
        # Especialidade em futebol brasileiro
        pass
```

#### **PremierBet Angola**
```python
# premierbet_angola.py
class PremierBetAngola:
    def __init__(self):
        self.base_url = "https://premierbet.ao"
        self.currency = "AOA"
        self.markets = ["1x2", "over_under", "btts", "handicap", "dupla_chance"]
        self.priority = "high"  # Casa popular em Angola
        self.specialties = ["live_odds", "european_leagues", "world_cup"]
    
    def get_odds(self, match_id):
        """Obtém odds da PremierBet Angola"""
        # Implementação específica para PremierBet Angola
        pass
    
    def get_live_odds(self, match_id):
        """Obtém odds ao vivo"""
        # Odds em tempo real para ligas mundiais
        pass
    
    def get_world_cup_odds(self, match_id):
        """Obtém odds da Copa do Mundo"""
        # Especialidade em competições mundiais
        pass
```

#### **Bantubet Angola**
```python
# bantubet_angola.py
class BantubetAngola:
    def __init__(self):
        self.base_url = "https://bantubet.ao"
        self.currency = "AOA"
        self.markets = ["1x2", "over_under", "btts", "handicap", "dupla_chance"]
        self.priority = "medium"  # Casa regional
        self.specialties = ["african_leagues", "caf_champions_league", "european_leagues"]
    
    def get_odds(self, match_id):
        """Obtém odds da Bantubet Angola"""
        # Implementação específica para Bantubet Angola
        pass
    
    def get_african_odds(self, match_id):
        """Obtém odds de ligas africanas"""
        # Foco em Premier Soccer League, CAF Champions League
        pass
    
    def get_caf_odds(self, match_id):
        """Obtém odds da CAF Champions League"""
        # Especialidade em competições africanas
        pass
```

#### **1xBet Angola**
```python
# 1xbet_angola.py
class OneXBetAngola:
    def __init__(self):
        self.base_url = "https://1xbet.ao"
        self.currency = "AOA"
        self.markets = ["1x2", "over_under", "btts", "handicap", "dupla_chance", "live"]
        self.priority = "high"  # Casa internacional com presença local
        self.specialties = ["all_leagues", "variety", "asian_leagues", "north_american_leagues"]
    
    def get_odds(self, match_id):
        """Obtém odds da 1xBet Angola"""
        # Implementação específica para 1xBet Angola
        pass
    
    def get_international_odds(self, match_id):
        """Obtém odds de ligas internacionais"""
        # Foco em todas as ligas mundiais
        pass
    
    def get_asian_odds(self, match_id):
        """Obtém odds de ligas asiáticas"""
        # J League, K League, Chinese Super League
        pass
```

#### **MoBet Angola**
```python
# mobet_angola.py
class MoBetAngola:
    def __init__(self):
        self.base_url = "https://mobet.ao"
        self.currency = "AOA"
        self.markets = ["1x2", "over_under", "btts", "handicap", "dupla_chance"]
        self.priority = "medium"  # Casa móvel especializada
        self.specialties = ["mobile_optimized", "popular_leagues", "european_leagues"]
    
    def get_odds(self, match_id):
        """Obtém odds da MoBet Angola"""
        # Implementação específica para MoBet Angola
        pass
    
    def get_mobile_odds(self, match_id):
        """Obtém odds otimizadas para mobile"""
        # Interface móvel otimizada para ligas populares
        pass
    
    def get_popular_leagues_odds(self, match_id):
        """Obtém odds das ligas mais populares"""
        # Premier League, La Liga, Champions League, Brasileirão
        pass
```

## 📊 Configuração de Mercados

### **Mercados Disponíveis**
```python
# angola_markets.py
ANGOLA_MARKETS = {
    "1x2": {
        "name": "Resultado da Partida",
        "selections": ["1", "X", "2"],
        "popular": True
    },
    "over_under": {
        "name": "Mais/Menos Gols",
        "selections": ["Over 2.5", "Under 2.5"],
        "popular": True
    },
    "btts": {
        "name": "Ambas Marcam",
        "selections": ["Sim", "Não"],
        "popular": True
    },
    "handicap": {
        "name": "Handicap Asiático",
        "selections": ["Casa -1", "Fora +1"],
        "popular": False
    },
    "dupla_chance": {
        "name": "Dupla Chance",
        "selections": ["1X", "12", "X2"],
        "popular": False
    }
}
```

### **Horários de Funcionamento**
```python
# angola_schedule.py
ANGOLA_SCHEDULE = {
    "girabola": {
        "match_days": ["Sábado", "Domingo"],
        "match_times": ["15:00", "17:00", "19:00"],
        "timezone": "Africa/Luanda"
    },
    "taca_angola": {
        "match_days": ["Quarta-feira", "Sábado", "Domingo"],
        "match_times": ["15:00", "17:00", "19:00"],
        "timezone": "Africa/Luanda"
    }
}
```

## 🔧 Configuração do Sistema

### **Variáveis de Ambiente para Angola**
```bash
# .env
# Configuração de Moeda
CURRENCY=AOA
CURRENCY_SYMBOL=Kz
DEFAULT_CURRENCY=AOA

# Configuração de Fuso Horário
TIMEZONE=Africa/Luanda

# Configuração de Ligas
ANGOLA_LEAGUES_ENABLED=true
INTERNATIONAL_LEAGUES_ENABLED=true

# Configuração de Casas de Apostas Angolanas
ELEPHANTBET_ANGOLA_ENABLED=true
KWANZABET_ANGOLA_ENABLED=true
PREMIERBET_ANGOLA_ENABLED=true
BANTUBET_ANGOLA_ENABLED=true
ONEXBET_ANGOLA_ENABLED=true
MOBET_ANGOLA_ENABLED=true

# Configuração de Mercados
ANGOLA_MARKETS_ENABLED=true
INTERNATIONAL_MARKETS_ENABLED=true
```

### **Configuração de Banco de Dados**
```python
# angola_database_config.py
ANGOLA_DB_CONFIG = {
    "currency": "AOA",
    "timezone": "Africa/Luanda",
    "leagues": [
        "angola_girabola",
        "angola_taca",
        "angola_supercup",
        "premier_league",
        "la_liga",
        "bundesliga",
        "serie_a",
        "ligue_1",
        "brasileirao"
    ],
    "markets": [
        "1x2",
        "over_under",
        "btts",
        "handicap",
        "dupla_chance"
    ]
}
```

## 📱 Interface Adaptada

### **Dashboard em Português (Angola)**
```python
# angola_dashboard.py
ANGOLA_TRANSLATIONS = {
    "dashboard_title": "MaraBet AI - Angola",
    "total_matches": "Total de Partidas",
    "recommended_bets": "Apostas Recomendadas",
    "profit_today": "Lucro Hoje",
    "profit_month": "Lucro do Mês",
    "win_rate": "Taxa de Acerto",
    "roi": "Retorno sobre Investimento",
    "currency": "Kwanza Angolano (AOA)"
}
```

### **Relatórios em AOA**
```python
# angola_reports.py
class AngolaReportGenerator:
    def __init__(self):
        self.currency = "AOA"
        self.symbol = "Kz"
    
    def generate_profit_report(self, data):
        """Gera relatório de lucros em AOA"""
        report = {
            "total_profit": f"Kz {data['profit']:,.2f}",
            "monthly_profit": f"Kz {data['monthly_profit']:,.2f}",
            "roi": f"{data['roi']:.2f}%",
            "win_rate": f"{data['win_rate']:.2f}%"
        }
        return report
```

## 🚀 Deploy para Angola

### **Docker Compose para Angola**
```yaml
# docker-compose.angola.yml
version: '3.8'

services:
  marabet-ai:
    build: .
    environment:
      - CURRENCY=AOA
      - TIMEZONE=Africa/Luanda
      - ANGOLA_LEAGUES_ENABLED=true
      - INTERNATIONAL_LEAGUES_ENABLED=true
    ports:
      - "8000:8000"
    volumes:
      - ./angola_config:/app/config
      - ./angola_data:/app/data
```

### **Scripts de Configuração**
```bash
# setup_angola.sh
#!/bin/bash

echo "🇦🇴 Configurando MaraBet AI para Angola..."

# Configurar moeda
export CURRENCY=AOA
export CURRENCY_SYMBOL=Kz

# Configurar fuso horário
export TIMEZONE=Africa/Luanda

# Configurar ligas angolanas
export ANGOLA_LEAGUES_ENABLED=true

# Iniciar sistema
docker-compose -f docker-compose.angola.yml up -d

echo "✅ Sistema configurado para Angola!"
echo "🌐 Acesse: http://localhost:8000"
```

## 📞 Suporte Local

### **Contato em Angola**
- **Email**: angola@marabet.ai
- **Telefone**: +244 923 456 789
- **WhatsApp**: +244 923 456 789
- **Endereço**: Luanda, Angola

### **Horários de Atendimento**
- **Segunda a Sexta**: 8:00 - 18:00 (Horário de Luanda)
- **Sábado**: 9:00 - 13:00 (Horário de Luanda)
- **Domingo**: Fechado

---

**Sistema MaraBet AI adaptado para o mercado angolano!** 🇦🇴💰

*Maximize seus lucros no mercado de apostas angolano com a mais avançada tecnologia de IA.*
