"""
Testes para funções utilitárias
"""

import pytest
import pandas as pd
from api.utils import filter_books, sort_books, search_books


@pytest.fixture
def sample_dataframe():
    """DataFrame de exemplo para testes"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "title": ["Book A", "Book B", "Book C", "Book D", "Book E"],
            "price": [10.0, 20.0, 30.0, 40.0, 50.0],
            "rating": [1, 2, 3, 4, 5],
            "category": ["Fiction", "Fiction", "Science", "Science", "History"],
            "description": [
                "A great book",
                "Another book",
                "Science book",
                "Tech book",
                "History book",
            ],
        }
    )


def test_filter_by_category(sample_dataframe):
    """Testa filtragem por categoria"""
    result = filter_books(sample_dataframe, category="Fiction")
    assert len(result) == 2
    assert all(result["category"] == "Fiction")


def test_filter_by_price_range(sample_dataframe):
    """Testa filtragem por faixa de preço"""
    result = filter_books(sample_dataframe, min_price=20.0, max_price=40.0)
    assert len(result) == 3
    assert all((result["price"] >= 20.0) & (result["price"] <= 40.0))


def test_filter_by_rating(sample_dataframe):
    """Testa filtragem por rating"""
    result = filter_books(sample_dataframe, min_rating=3)
    assert len(result) == 3
    assert all(result["rating"] >= 3)


def test_filter_combined(sample_dataframe):
    """Testa múltiplos filtros combinados"""
    result = filter_books(
        sample_dataframe, category="Science", min_price=25.0, min_rating=3
    )
    assert len(result) == 2


def test_sort_ascending(sample_dataframe):
    """Testa ordenação crescente"""
    result = sort_books(sample_dataframe, "price", "asc")
    prices = result["price"].tolist()
    assert prices == sorted(prices)


def test_sort_descending(sample_dataframe):
    """Testa ordenação decrescente"""
    result = sort_books(sample_dataframe, "price", "desc")
    prices = result["price"].tolist()
    assert prices == sorted(prices, reverse=True)


def test_sort_invalid_column(sample_dataframe):
    """Testa ordenação com coluna inválida"""
    result = sort_books(sample_dataframe, "invalid_column", "asc")
    # Deve retornar o DataFrame original sem modificações
    assert len(result) == len(sample_dataframe)


def test_search_in_title(sample_dataframe):
    """Testa busca no título"""
    result = search_books(sample_dataframe, "Book A")
    assert len(result) == 1
    assert result.iloc[0]["title"] == "Book A"


def test_search_in_description(sample_dataframe):
    """Testa busca na descrição"""
    result = search_books(sample_dataframe, "Science")
    assert len(result) >= 1


def test_search_case_insensitive(sample_dataframe):
    """Testa busca case-insensitive"""
    result1 = search_books(sample_dataframe, "book")
    result2 = search_books(sample_dataframe, "BOOK")
    assert len(result1) == len(result2)


def test_search_no_results(sample_dataframe):
    """Testa busca sem resultados"""
    result = search_books(sample_dataframe, "xyz123notfound")
    assert len(result) == 0
