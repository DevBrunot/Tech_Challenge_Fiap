"""
Configuração de fixtures para testes
"""

import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Diretório para dados de teste"""
    test_dir = Path("tests/data")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


@pytest.fixture(scope="session")
def sample_books_csv(test_data_dir):
    """Cria um CSV de exemplo para testes"""
    csv_path = test_data_dir / "sample_books.csv"

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "title": ["Test Book 1", "Test Book 2", "Test Book 3"],
            "price": [10.99, 20.99, 30.99],
            "availability": ["In stock", "In stock", "Out of stock"],
            "availability_copies": [10, 5, 0],
            "rating": [3, 4, 5],
            "category": ["Fiction", "Science", "Fiction"],
            "product_page_url": [
                "http://example.com/1",
                "http://example.com/2",
                "http://example.com/3",
            ],
            "upc": ["abc123", "def456", "ghi789"],
            "description": ["Great book", "Amazing", "Wonderful"],
            "image_url": [
                "http://example.com/img1.jpg",
                "http://example.com/img2.jpg",
                "http://example.com/img3.jpg",
            ],
            "scraped_at": [
                "2024-01-01T00:00:00",
                "2024-01-01T00:00:00",
                "2024-01-01T00:00:00",
            ],
        }
    )

    df.to_csv(csv_path, index=False)
    return csv_path
