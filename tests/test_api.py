"""
Testes para API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
import pandas as pd
from pathlib import Path


@pytest.fixture
def client():
    """Cliente de teste para a API"""
    return TestClient(app)


def test_root_endpoint(client):
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data
    assert "versao" in data
    assert data["versao"] == "1.0.0"


def test_health_endpoint(client):
    """Testa health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "total_livros" in data


def test_get_books_pagination(client):
    """Testa paginação da listagem de livros"""
    response = client.get("/books?page=1&per_page=10")
    assert response.status_code in [200, 503]  # 503 se não houver dados

    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "pagina" in data
        assert "por_pagina" in data
        assert "livros" in data
        assert data["pagina"] == 1
        assert data["por_pagina"] == 10


def test_get_books_with_filters(client):
    """Testa filtros de listagem"""
    response = client.get("/books?min_price=10&max_price=50&min_rating=3")
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "livros" in data
        for book in data["livros"]:
            assert book["price"] >= 10
            assert book["price"] <= 50
            assert book["rating"] >= 3


def test_get_books_sorting(client):
    """Testa ordenação de livros"""
    response = client.get("/books?sort=price&order=asc&per_page=5")
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        books = data["livros"]
        if len(books) > 1:
            prices = [book["price"] for book in books]
            assert prices == sorted(prices)


def test_get_book_by_id(client):
    """Testa busca de livro por ID"""
    response = client.get("/books/1")
    assert response.status_code in [200, 404, 503]

    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "price" in data


def test_search_books(client):
    """Testa busca de livros"""
    response = client.get("/books/search?q=test")
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "livros" in data


def test_get_genres(client):
    """Testa listagem de gêneros"""
    response = client.get("/books/genres")
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "generos" in data


def test_get_books_by_genre(client):
    """Testa filtragem por gênero"""
    # Primeiro pega lista de gêneros
    genres_response = client.get("/books/genres")

    if genres_response.status_code == 200:
        genres = genres_response.json()["generos"]
        if genres:
            first_genre = genres[0]["nome"]
            response = client.get(f"/books/genre/{first_genre}")
            assert response.status_code == 200
            data = response.json()
            assert "livros" in data


def test_stats_endpoint(client):
    """Testa endpoint de estatísticas"""
    response = client.get("/stats")
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "total_livros" in data
        assert "estatisticas_preco" in data
        assert "distribuicao_avaliacoes" in data


def test_ml_sample_endpoint(client):
    """Testa endpoint de amostra ML"""
    response = client.get("/ml/sample?size=50&random_state=42")
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "tamanho_amostra" in data
        assert "dados" in data
        assert "features" in data


def test_invalid_page(client):
    """Testa página inválida"""
    response = client.get("/books?page=-1")
    assert response.status_code == 422  # Validation error


def test_invalid_per_page(client):
    """Testa per_page inválido"""
    response = client.get("/books?per_page=200")  # Max é 100
    assert response.status_code == 422
