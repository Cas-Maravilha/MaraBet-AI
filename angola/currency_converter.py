"""
Conversor de Moedas - MaraBet AI Angola
Sistema de conversão e configuração para Kwanza Angolano (AOA)
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CurrencyRate:
    """Taxa de câmbio"""
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime
    source: str

class AngolaCurrencyConverter:
    """
    Conversor de moedas para o mercado angolano
    Gerencia conversões para Kwanza Angolano (AOA)
    """
    
    def __init__(self, config_file: str = "angola/currency_config.json"):
        """
        Inicializa o conversor de moedas
        
        Args:
            config_file: Arquivo de configuração de moedas
        """
        self.config_file = config_file
        self.config = self._load_currency_config()
        self.cache = {}
        self.cache_duration = 3600  # 1 hora
        
        logger.info("AngolaCurrencyConverter inicializado")
    
    def _load_currency_config(self) -> Dict[str, Any]:
        """Carrega configuração de moedas"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_config = {
                    "base_currency": "AOA",
                    "supported_currencies": ["USD", "EUR", "GBP", "BRL", "ZAR"],
                    "exchange_rates": {
                        "USD": 830.50,
                        "EUR": 920.30,
                        "GBP": 1050.80,
                        "BRL": 165.20,
                        "ZAR": 45.60
                    },
                    "api_endpoints": {
                        "primary": "https://api.exchangerate-api.com/v4/latest/AOA",
                        "backup": "https://api.fixer.io/latest?base=AOA"
                    },
                    "update_interval": 3600,
                    "last_update": None
                }
                self._save_currency_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return {}
    
    def _save_currency_config(self, config: Dict[str, Any]):
        """Salva configuração de moedas"""
        try:
            import os
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
    
    def get_exchange_rate(self, from_currency: str, to_currency: str = "AOA") -> Optional[CurrencyRate]:
        """
        Obtém taxa de câmbio
        
        Args:
            from_currency: Moeda de origem
            to_currency: Moeda de destino (padrão: AOA)
            
        Returns:
            Taxa de câmbio
        """
        try:
            # Verificar cache
            cache_key = f"{from_currency}_{to_currency}"
            if cache_key in self.cache:
                cached_rate = self.cache[cache_key]
                if datetime.now() - cached_rate.timestamp < timedelta(seconds=self.cache_duration):
                    return cached_rate
            
            # Tentar API primária
            rate = self._fetch_from_api(from_currency, to_currency, "primary")
            if rate:
                self.cache[cache_key] = rate
                return rate
            
            # Tentar API backup
            rate = self._fetch_from_api(from_currency, to_currency, "backup")
            if rate:
                self.cache[cache_key] = rate
                return rate
            
            # Usar taxa fixa como fallback
            rate = self._get_fixed_rate(from_currency, to_currency)
            if rate:
                self.cache[cache_key] = rate
                return rate
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter taxa de câmbio: {e}")
            return None
    
    def _fetch_from_api(self, from_currency: str, to_currency: str, api_type: str) -> Optional[CurrencyRate]:
        """Busca taxa de API externa"""
        try:
            if api_type == "primary":
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            else:
                url = f"https://api.fixer.io/latest?base={from_currency}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if api_type == "primary":
                rate_value = data["rates"].get(to_currency, 0)
            else:
                rate_value = data["rates"].get(to_currency, 0)
            
            if rate_value > 0:
                return CurrencyRate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate_value,
                    timestamp=datetime.now(),
                    source=f"API_{api_type}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na API {api_type}: {e}")
            return None
    
    def _get_fixed_rate(self, from_currency: str, to_currency: str) -> Optional[CurrencyRate]:
        """Obtém taxa fixa do arquivo de configuração"""
        try:
            if to_currency == "AOA":
                rate_value = self.config.get("exchange_rates", {}).get(from_currency, 0)
            else:
                # Converter via USD como intermediário
                usd_to_aoa = self.config.get("exchange_rates", {}).get("USD", 830.50)
                from_to_usd = self.config.get("exchange_rates", {}).get(from_currency, 0)
                if from_to_usd > 0:
                    rate_value = usd_to_aoa / from_to_usd
                else:
                    return None
            
            if rate_value > 0:
                return CurrencyRate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate_value,
                    timestamp=datetime.now(),
                    source="FIXED_RATE"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter taxa fixa: {e}")
            return None
    
    def convert_to_aoa(self, amount: float, from_currency: str) -> Optional[float]:
        """
        Converte valor para Kwanza Angolano
        
        Args:
            amount: Valor a converter
            from_currency: Moeda de origem
            
        Returns:
            Valor em AOA
        """
        try:
            if from_currency == "AOA":
                return amount
            
            rate = self.get_exchange_rate(from_currency, "AOA")
            if rate:
                return amount * rate.rate
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na conversão: {e}")
            return None
    
    def convert_from_aoa(self, amount: float, to_currency: str) -> Optional[float]:
        """
        Converte valor de Kwanza Angolano para outra moeda
        
        Args:
            amount: Valor em AOA
            to_currency: Moeda de destino
            
        Returns:
            Valor convertido
        """
        try:
            if to_currency == "AOA":
                return amount
            
            rate = self.get_exchange_rate("AOA", to_currency)
            if rate:
                return amount / rate.rate
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na conversão: {e}")
            return None
    
    def format_currency(self, amount: float, currency: str = "AOA") -> str:
        """
        Formata valor monetário
        
        Args:
            amount: Valor a formatar
            currency: Moeda
            
        Returns:
            Valor formatado
        """
        try:
            if currency == "AOA":
                return f"{amount:,.2f} AOA"
            elif currency == "USD":
                return f"${amount:,.2f}"
            elif currency == "EUR":
                return f"€{amount:,.2f}"
            elif currency == "GBP":
                return f"£{amount:,.2f}"
            elif currency == "BRL":
                return f"R$ {amount:,.2f}"
            else:
                return f"{amount:,.2f} {currency}"
                
        except Exception as e:
            logger.error(f"❌ Erro na formatação: {e}")
            return f"{amount:.2f} {currency}"
    
    def get_angola_pricing(self) -> Dict[str, Dict[str, Any]]:
        """Retorna preços em Kwanza Angolano"""
        try:
            # Preços base em USD
            usd_prices = {
                "saas_basic": 99,
                "saas_professional": 299,
                "saas_enterprise": 999,
                "license_perpetual": 15000,
                "consulting_setup": 5000
            }
            
            # Converter para AOA
            aoa_prices = {}
            for key, usd_price in usd_prices.items():
                aoa_price = self.convert_to_aoa(usd_price, "USD")
                if aoa_price:
                    aoa_prices[key] = {
                        "usd": usd_price,
                        "aoa": round(aoa_price, 2),
                        "formatted_aoa": self.format_currency(aoa_price, "AOA"),
                        "formatted_usd": self.format_currency(usd_price, "USD")
                    }
            
            return aoa_prices
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter preços: {e}")
            return {}
    
    def update_exchange_rates(self) -> bool:
        """Atualiza taxas de câmbio"""
        try:
            logger.info("🔄 Atualizando taxas de câmbio...")
            
            updated_rates = {}
            for currency in self.config.get("supported_currencies", []):
                rate = self.get_exchange_rate(currency, "AOA")
                if rate:
                    updated_rates[currency] = rate.rate
            
            if updated_rates:
                self.config["exchange_rates"].update(updated_rates)
                self.config["last_update"] = datetime.now().isoformat()
                self._save_currency_config(self.config)
                
                logger.info("✅ Taxas de câmbio atualizadas")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar taxas: {e}")
            return False
    
    def get_currency_info(self) -> Dict[str, Any]:
        """Retorna informações sobre moedas"""
        return {
            "base_currency": "AOA",
            "supported_currencies": self.config.get("supported_currencies", []),
            "current_rates": self.config.get("exchange_rates", {}),
            "last_update": self.config.get("last_update"),
            "pricing": self.get_angola_pricing()
        }
