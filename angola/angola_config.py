"""
Configuração do Mercado Angolano - MaraBet AI
Configurações específicas para o mercado de apostas de Angola
"""

import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AngolaBookmaker:
    """Casa de apostas angolana"""
    name: str
    code: str
    website: str
    api_endpoint: str
    supported_currencies: List[str]
    min_bet: float
    max_bet: float
    commission_rate: float
    is_active: bool

@dataclass
class AngolaLeague:
    """Liga esportiva relevante para Angola"""
    name: str
    country: str
    priority: int
    season_months: List[str]
    is_active: bool

class AngolaMarketConfig:
    """
    Configuração do mercado angolano
    Gerencia casas de apostas, ligas e configurações locais
    """
    
    def __init__(self, config_file: str = "angola/angola_market_config.json"):
        """
        Inicializa configuração do mercado angolano
        
        Args:
            config_file: Arquivo de configuração
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do mercado angolano"""
        try:
            import os
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_config = self._get_default_config()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão do mercado angolano"""
        return {
            "market_info": {
                "country": "Angola",
                "currency": "AOA",
                "timezone": "Africa/Luanda",
                "language": "pt-AO",
                "date_format": "%d/%m/%Y",
                "number_format": {
                    "decimal_separator": ",",
                    "thousands_separator": ".",
                    "currency_symbol": "AOA"
                }
            },
            "bookmakers": [
                {
                    "name": "Elephantbet",
                    "code": "ELEPHANT",
                    "website": "https://www.elephantbet.com",
                    "api_endpoint": "https://api.elephantbet.com/v1",
                    "supported_currencies": ["AOA", "USD"],
                    "min_bet": 100.0,
                    "max_bet": 1000000.0,
                    "commission_rate": 0.05,
                    "is_active": True
                },
                {
                    "name": "KwanzaBet",
                    "code": "KWANZA",
                    "website": "https://www.kwanzabet.com",
                    "api_endpoint": "https://api.kwanzabet.com/v1",
                    "supported_currencies": ["AOA"],
                    "min_bet": 50.0,
                    "max_bet": 500000.0,
                    "commission_rate": 0.03,
                    "is_active": True
                },
                {
                    "name": "PremierBet",
                    "code": "PREMIER",
                    "website": "https://www.premierbet.com",
                    "api_endpoint": "https://api.premierbet.com/v1",
                    "supported_currencies": ["AOA", "USD", "EUR"],
                    "min_bet": 200.0,
                    "max_bet": 2000000.0,
                    "commission_rate": 0.04,
                    "is_active": True
                },
                {
                    "name": "Bantubet",
                    "code": "BANTU",
                    "website": "https://www.bantubet.com",
                    "api_endpoint": "https://api.bantubet.com/v1",
                    "supported_currencies": ["AOA"],
                    "min_bet": 75.0,
                    "max_bet": 750000.0,
                    "commission_rate": 0.035,
                    "is_active": True
                },
                {
                    "name": "1xBet Angola",
                    "code": "1XBET_AO",
                    "website": "https://www.1xbet.ao",
                    "api_endpoint": "https://api.1xbet.com/v1",
                    "supported_currencies": ["AOA", "USD", "EUR"],
                    "min_bet": 100.0,
                    "max_bet": 1000000.0,
                    "commission_rate": 0.06,
                    "is_active": True
                },
                {
                    "name": "MoBet",
                    "code": "MOBET",
                    "website": "https://www.mobet.com",
                    "api_endpoint": "https://api.mobet.com/v1",
                    "supported_currencies": ["AOA"],
                    "min_bet": 50.0,
                    "max_bet": 500000.0,
                    "commission_rate": 0.04,
                    "is_active": True
                }
            ],
            "leagues": [
                {
                    "name": "Premier League",
                    "country": "Inglaterra",
                    "priority": 1,
                    "season_months": ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "La Liga",
                    "country": "Espanha",
                    "priority": 2,
                    "season_months": ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "Serie A",
                    "country": "Itália",
                    "priority": 3,
                    "season_months": ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "Bundesliga",
                    "country": "Alemanha",
                    "priority": 4,
                    "season_months": ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "Ligue 1",
                    "country": "França",
                    "priority": 5,
                    "season_months": ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "Brasileirão",
                    "country": "Brasil",
                    "priority": 6,
                    "season_months": ["04", "05", "06", "07", "08", "09", "10", "11", "12"],
                    "is_active": True
                },
                {
                    "name": "Primera División",
                    "country": "Argentina",
                    "priority": 7,
                    "season_months": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
                    "is_active": True
                },
                {
                    "name": "MLS",
                    "country": "Estados Unidos",
                    "priority": 8,
                    "season_months": ["03", "04", "05", "06", "07", "08", "09", "10", "11"],
                    "is_active": True
                },
                {
                    "name": "Liga MX",
                    "country": "México",
                    "priority": 9,
                    "season_months": ["07", "08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "J-League",
                    "country": "Japão",
                    "priority": 10,
                    "season_months": ["02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
                    "is_active": True
                },
                {
                    "name": "K-League",
                    "country": "Coreia do Sul",
                    "priority": 11,
                    "season_months": ["03", "04", "05", "06", "07", "08", "09", "10", "11"],
                    "is_active": True
                },
                {
                    "name": "Chinese Super League",
                    "country": "China",
                    "priority": 12,
                    "season_months": ["03", "04", "05", "06", "07", "08", "09", "10", "11"],
                    "is_active": True
                },
                {
                    "name": "Premier League Egípcia",
                    "country": "Egito",
                    "priority": 13,
                    "season_months": ["09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                },
                {
                    "name": "PSL",
                    "country": "África do Sul",
                    "priority": 14,
                    "season_months": ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05"],
                    "is_active": True
                }
            ],
            "bet_types": [
                {
                    "name": "1X2",
                    "description": "Resultado da partida",
                    "is_active": True
                },
                {
                    "name": "Over/Under",
                    "description": "Total de gols",
                    "is_active": True
                },
                {
                    "name": "Both Teams to Score",
                    "description": "Ambas marcam",
                    "is_active": True
                },
                {
                    "name": "Handicap Asiático",
                    "description": "Handicap de gols",
                    "is_active": True
                },
                {
                    "name": "Corner Kicks",
                    "description": "Cantos de escanteio",
                    "is_active": True
                },
                {
                    "name": "Cards",
                    "description": "Cartões amarelos/vermelhos",
                    "is_active": True
                }
            ],
            "pricing": {
                "saas_basic": {
                    "aoa": 82200,
                    "usd": 99,
                    "description": "Plano Básico"
                },
                "saas_professional": {
                    "aoa": 248100,
                    "usd": 299,
                    "description": "Plano Profissional"
                },
                "saas_enterprise": {
                    "aoa": 829500,
                    "usd": 999,
                    "description": "Plano Enterprise"
                },
                "license_perpetual": {
                    "aoa": 12457500,
                    "usd": 15000,
                    "description": "Licença Perpétua"
                },
                "consulting_setup": {
                    "aoa": 4152500,
                    "usd": 5000,
                    "description": "Setup Completo"
                }
            },
            "contact_info": {
                "company_name": "Cas Maravilha",
                "address": "Luanda, Angola",
                "phone": "+244 923066033",
                "email": "casmaravilha@gmail.com",
                "website": "https://www.marabet-ai.ao",
                "whatsapp": "+244 923066033"
            }
        }
    
    def _save_config(self, config: Dict[str, Any]):
        """Salva configuração"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def get_bookmakers(self) -> List[AngolaBookmaker]:
        """Retorna lista de casas de apostas angolanas"""
        bookmakers = []
        for bookmaker_data in self.config.get("bookmakers", []):
            bookmakers.append(AngolaBookmaker(**bookmaker_data))
        return bookmakers
    
    def get_active_bookmakers(self) -> List[AngolaBookmaker]:
        """Retorna casas de apostas ativas"""
        return [b for b in self.get_bookmakers() if b.is_active]
    
    def get_leagues(self) -> List[AngolaLeague]:
        """Retorna lista de ligas"""
        leagues = []
        for league_data in self.config.get("leagues", []):
            leagues.append(AngolaLeague(**league_data))
        return leagues
    
    def get_active_leagues(self) -> List[AngolaLeague]:
        """Retorna ligas ativas"""
        return [l for l in self.get_leagues() if l.is_active]
    
    def get_priority_leagues(self, limit: int = 5) -> List[AngolaLeague]:
        """Retorna ligas prioritárias"""
        active_leagues = self.get_active_leagues()
        return sorted(active_leagues, key=lambda x: x.priority)[:limit]
    
    def get_pricing(self) -> Dict[str, Dict[str, Any]]:
        """Retorna preços em AOA"""
        return self.config.get("pricing", {})
    
    def get_market_info(self) -> Dict[str, Any]:
        """Retorna informações do mercado"""
        return self.config.get("market_info", {})
    
    def get_contact_info(self) -> Dict[str, Any]:
        """Retorna informações de contato"""
        return self.config.get("contact_info", {})
    
    def format_currency(self, amount: float) -> str:
        """Formata valor em AOA"""
        try:
            market_info = self.get_market_info()
            number_format = market_info.get("number_format", {})
            
            decimal_sep = number_format.get("decimal_separator", ",")
            thousands_sep = number_format.get("thousands_separator", ".")
            currency_symbol = number_format.get("currency_symbol", "AOA")
            
            # Formatar número
            formatted_amount = f"{amount:,.2f}".replace(",", "TEMP").replace(".", thousands_sep).replace("TEMP", decimal_sep)
            
            return f"{formatted_amount} {currency_symbol}"
            
        except Exception as e:
            print(f"❌ Erro na formatação: {e}")
            return f"{amount:.2f} AOA"
    
    def get_bookmaker_by_code(self, code: str) -> AngolaBookmaker:
        """Retorna casa de apostas por código"""
        for bookmaker in self.get_bookmakers():
            if bookmaker.code == code:
                return bookmaker
        return None
    
    def get_league_by_name(self, name: str) -> AngolaLeague:
        """Retorna liga por nome"""
        for league in self.get_leagues():
            if league.name == name:
                return league
        return None
    
    def update_bookmaker_status(self, code: str, is_active: bool) -> bool:
        """Atualiza status de casa de apostas"""
        try:
            for bookmaker in self.config.get("bookmakers", []):
                if bookmaker.get("code") == code:
                    bookmaker["is_active"] = is_active
                    self._save_config(self.config)
                    return True
            return False
        except Exception as e:
            print(f"❌ Erro ao atualizar status: {e}")
            return False
    
    def add_bookmaker(self, bookmaker: AngolaBookmaker) -> bool:
        """Adiciona nova casa de apostas"""
        try:
            bookmaker_data = {
                "name": bookmaker.name,
                "code": bookmaker.code,
                "website": bookmaker.website,
                "api_endpoint": bookmaker.api_endpoint,
                "supported_currencies": bookmaker.supported_currencies,
                "min_bet": bookmaker.min_bet,
                "max_bet": bookmaker.max_bet,
                "commission_rate": bookmaker.commission_rate,
                "is_active": bookmaker.is_active
            }
            
            self.config["bookmakers"].append(bookmaker_data)
            self._save_config(self.config)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar casa de apostas: {e}")
            return False

def main():
    """Função principal para demonstração"""
    try:
        # Criar configuração
        config = AngolaMarketConfig()
        
        # Mostrar informações
        print("🇦🇴 Configuração do Mercado Angolano - MaraBet AI")
        print("=" * 50)
        
        # Informações do mercado
        market_info = config.get_market_info()
        print(f"País: {market_info.get('country')}")
        print(f"Moeda: {market_info.get('currency')}")
        print(f"Fuso Horário: {market_info.get('timezone')}")
        print(f"Idioma: {market_info.get('language')}")
        print()
        
        # Casas de apostas ativas
        print("🏢 Casas de Apostas Ativas:")
        for bookmaker in config.get_active_bookmakers():
            print(f"  • {bookmaker.name} ({bookmaker.code})")
            print(f"    Website: {bookmaker.website}")
            print(f"    Moedas: {', '.join(bookmaker.supported_currencies)}")
            print(f"    Aposta mínima: {config.format_currency(bookmaker.min_bet)}")
            print(f"    Aposta máxima: {config.format_currency(bookmaker.max_bet)}")
            print()
        
        # Ligas prioritárias
        print("⚽ Ligas Prioritárias:")
        for league in config.get_priority_leagues(5):
            print(f"  • {league.name} ({league.country}) - Prioridade {league.priority}")
        print()
        
        # Preços
        print("💰 Preços em Kwanza Angolano:")
        pricing = config.get_pricing()
        for key, price_info in pricing.items():
            print(f"  • {price_info['description']}: {config.format_currency(price_info['aoa'])}")
        print()
        
        # Informações de contato
        contact_info = config.get_contact_info()
        print("📞 Informações de Contato:")
        print(f"  • Empresa: {contact_info.get('company_name')}")
        print(f"  • Endereço: {contact_info.get('address')}")
        print(f"  • Telefone: {contact_info.get('phone')}")
        print(f"  • Email: {contact_info.get('email')}")
        print(f"  • Website: {contact_info.get('website')}")
        print(f"  • WhatsApp: {contact_info.get('whatsapp')}")
        
        print("\n✅ Configuração do mercado angolano carregada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
