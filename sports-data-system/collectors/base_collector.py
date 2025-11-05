"""
Coletor Base - Sistema Básico
Classe base para todos os coletores de dados
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Classe base para coletores de dados"""
    
    def __init__(self, name: str, base_url: str, api_key: str = None, 
                 rate_limit: int = 10, timeout: int = 30):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limit = rate_limit  # requests per minute
        self.timeout = timeout
        
        # Controle de rate limiting
        self.last_request_time = None
        self.request_count = 0
        self.rate_limit_window = 60  # 1 minuto
        
        # Configuração de sessão HTTP
        self.session = requests.Session()
        self._setup_session()
        
        # Estatísticas
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'total_data_points': 0,
            'last_request': None,
            'errors': []
        }
    
    def _setup_session(self):
        """Configura a sessão HTTP com retry e timeouts"""
        # Configuração de retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers padrão
        self.session.headers.update({
            'User-Agent': 'MaraBet-AI-Basic/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        if self.api_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.api_key
            })
    
    def _rate_limit_check(self):
        """Verifica e aplica rate limiting"""
        now = datetime.now()
        
        # Reset contador se passou da janela de tempo
        if (self.last_request_time is None or 
            (now - self.last_request_time).total_seconds() >= self.rate_limit_window):
            self.request_count = 0
            self.last_request_time = now
        
        # Verifica se atingiu o limite
        if self.request_count >= self.rate_limit:
            sleep_time = self.rate_limit_window - (now - self.last_request_time).total_seconds()
            if sleep_time > 0:
                logger.info(f"Rate limit atingido. Aguardando {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = datetime.now()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Faz requisição HTTP com controle de rate limiting"""
        self._rate_limit_check()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Fazendo requisição: {url}")
            
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            
            self.stats['total_requests'] += 1
            self.stats['last_request'] = datetime.now()
            self.request_count += 1
            
            # Verifica rate limiting
            if response.status_code == 429:
                self.stats['rate_limited_requests'] += 1
                logger.warning(f"Rate limited pela API {self.name}")
                return None
            
            # Verifica sucesso
            if response.status_code == 200:
                self.stats['successful_requests'] += 1
                data = response.json()
                logger.debug(f"Requisição bem-sucedida: {len(str(data))} bytes")
                return data
            else:
                self.stats['failed_requests'] += 1
                logger.error(f"Erro na requisição: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.stats['failed_requests'] += 1
            logger.error(f"Timeout na requisição para {url}")
            return None
        except requests.exceptions.RequestException as e:
            self.stats['failed_requests'] += 1
            error_msg = f"Erro na requisição: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
        except Exception as e:
            self.stats['failed_requests'] += 1
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    @abstractmethod
    def collect_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta dados específicos do serviço"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do coletor"""
        success_rate = 0
        if self.stats['total_requests'] > 0:
            success_rate = self.stats['successful_requests'] / self.stats['total_requests']
        
        return {
            'name': self.name,
            'base_url': self.base_url,
            'has_api_key': self.api_key is not None,
            'rate_limit': self.rate_limit,
            'stats': self.stats.copy(),
            'success_rate': success_rate,
            'is_healthy': success_rate > 0.8 and len(self.stats['errors']) < 10
        }
    
    def reset_stats(self):
        """Reseta estatísticas do coletor"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'total_data_points': 0,
            'last_request': None,
            'errors': []
        }
    
    def is_healthy(self) -> bool:
        """Verifica se o coletor está saudável"""
        stats = self.get_stats()
        return stats['is_healthy']
    
    def __str__(self):
        return f"{self.name}Collector(url={self.base_url})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', base_url='{self.base_url}')"
