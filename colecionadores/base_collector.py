import requests
import time
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import logging
from settings.settings import MAX_RETRIES, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Classe base para todos os colecionadores"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.request_count = 0
        self.last_request_time = 0
        
    def _rate_limit(self, min_interval: float = 1.0):
        """Implementa rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     headers: Optional[Dict] = None) -> Dict:
        """Faz requisição com retry automático"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
                
                self.request_count += 1
                
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                else:
                    logger.error(f"Request failed: {response.status_code}")
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception (attempt {attempt+1}): {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(2 ** attempt)
        
        return {}
    
    @abstractmethod
    def collect(self, **kwargs) -> List[Dict]:
        """Método abstrato para coleta de dados"""
        pass
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do colecionador"""
        return {
            'total_requests': self.request_count,
            'collector_type': self.__class__.__name__
        }
