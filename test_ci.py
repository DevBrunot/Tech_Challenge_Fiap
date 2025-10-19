#!/usr/bin/env python3
"""
Script de teste para verificar se o ambiente CI está funcionando
"""

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    try:
        import fastapi
        import uvicorn
        import pandas as pd
        import numpy as np
        import requests
        from bs4 import BeautifulSoup
        import pytest
        import pytest_cov
        import httpx
        print("OK - Todos os imports funcionaram!")
        return True
    except ImportError as e:
        print(f"ERRO - Erro de import: {e}")
        return False

def test_api_creation():
    """Testa se a API pode ser criada"""
    try:
        from api.main import app
        print("OK - API criada com sucesso!")
        return True
    except Exception as e:
        print(f"ERRO - Erro ao criar API: {e}")
        return False

def test_data_loading():
    """Testa se os dados podem ser carregados"""
    try:
        from api.utils import load_books_data
        df = load_books_data("data/books.csv")
        if df.empty:
            print("ERRO - DataFrame vazio!")
            return False
        print(f"OK - Dados carregados: {len(df)} livros")
        return True
    except Exception as e:
        print(f"ERRO - Erro ao carregar dados: {e}")
        return False

if __name__ == "__main__":
    print("Testando ambiente CI...")
    
    tests = [
        test_imports,
        test_api_creation,
        test_data_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("AMBIENTE CI FUNCIONANDO!")
        exit(0)
    else:
        print("PROBLEMAS NO AMBIENTE CI")
        exit(1)
