"""
API - MaraBet AI
Módulo da API FastAPI
"""

from .main import app
from .routes import router

__all__ = [
    "app",
    "router"
]
