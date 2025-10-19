"""
Arquivo de entrada para deploy na Vercel
Redireciona para a aplicação principal em api/main.py
"""

from api.main import app

# Exporta a aplicação FastAPI para a Vercel
__all__ = ["app"]
