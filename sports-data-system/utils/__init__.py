"""
Utilitários - Sistema Básico
Módulo com funções auxiliares e utilitários
"""

from .cache import CacheManager
from .logger import setup_logger

__all__ = [
    'CacheManager',
    'setup_logger'
]

__version__ = '1.0.0'
__author__ = 'MaraBet AI Team'
