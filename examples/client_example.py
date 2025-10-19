"""
Exemplo de cliente para consumir a Books API
Demonstra os principais casos de uso
"""

import requests
import pandas as pd
from typing import List, Dict
import json


class BooksAPIClient:
    """Cliente para interagir com a Books API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa o cliente

        Args:
            base_url: URL base da API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> Dict:
        """Verifica saúde da API"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_books(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: str = None,
        order: str = "asc",
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        min_rating: int = None,
    ) -> Dict:
        """
        Lista livros com filtros

        Args:
            page: Número da página
            per_page: Livros por página
            sort: Campo para ordenação
            order: Ordem (asc/desc)
            category: Filtrar por categoria
            min_price: Preço mínimo
            max_price: Preço máximo
            min_rating: Rating mínimo

        Returns:
            Dict com resultados paginados
        """
        params = {"page": page, "per_page": per_page, "order": order}

        if sort:
            params["sort"] = sort
        if category:
            params["category"] = category
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if min_rating is not None:
            params["min_rating"] = min_rating

        response = self.session.get(f"{self.base_url}/books", params=params)
        response.raise_for_status()
        return response.json()

    def get_book_by_id(self, book_id: int) -> Dict:
        """Obtém detalhes de um livro por ID"""
        response = self.session.get(f"{self.base_url}/books/{book_id}")
        response.raise_for_status()
        return response.json()

    def search_books(self, query: str, page: int = 1, per_page: int = 20) -> Dict:
        """
        Busca livros por termo

        Args:
            query: Termo de busca
            page: Número da página
            per_page: Livros por página

        Returns:
            Dict com resultados da busca
        """
        params = {"q": query, "page": page, "per_page": per_page}
        response = self.session.get(f"{self.base_url}/books/search", params=params)
        response.raise_for_status()
        return response.json()

    def get_genres(self) -> Dict:
        """Lista todas as categorias/gêneros"""
        response = self.session.get(f"{self.base_url}/books/genres")
        response.raise_for_status()
        return response.json()

    def get_books_by_genre(self, genre: str, page: int = 1, per_page: int = 20) -> Dict:
        """Lista livros de uma categoria específica"""
        params = {"page": page, "per_page": per_page}
        response = self.session.get(
            f"{self.base_url}/books/genre/{genre}", params=params
        )
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict:
        """Obtém estatísticas agregadas"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def get_ml_sample(self, size: int = 100, random_state: int = 42) -> Dict:
        """Obtém amostra para Machine Learning"""
        params = {"size": size, "random_state": random_state}
        response = self.session.get(f"{self.base_url}/ml/sample", params=params)
        response.raise_for_status()
        return response.json()

    def get_all_books(self) -> List[Dict]:
        """
        Obtém todos os livros (paginando automaticamente)

        Returns:
            Lista com todos os livros
        """
        all_books = []
        page = 1

        while True:
            data = self.get_books(page=page, per_page=100)
            all_books.extend(data["books"])

            if page >= data["total_pages"]:
                break
            page += 1

        return all_books


def example_basic_usage():
    """Exemplo básico de uso"""
    print("=" * 80)
    print("EXEMPLO 1: Uso Básico")
    print("=" * 80)

    client = BooksAPIClient()

    # Health check
    health = client.health_check()
    print(f"\n✅ API Status: {health['status']}")
    print(f"📚 Total de livros: {health['total_books']}")

    # Listar livros
    books = client.get_books(page=1, per_page=5)
    print(f"\n📖 Primeiros 5 livros:")
    for book in books["books"]:
        print(f"  - {book['title']} (£{book['price']})")


def example_filtering():
    """Exemplo de filtros"""
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Filtros e Ordenação")
    print("=" * 80)

    client = BooksAPIClient()

    # Filtrar por preço e rating
    books = client.get_books(
        min_price=20, max_price=40, min_rating=4, sort="price", order="asc", per_page=5
    )

    print(f"\n💎 Livros bem avaliados (rating ≥ 4) entre £20-40:")
    for book in books["books"]:
        stars = "⭐" * book["rating"]
        print(f"  {stars} {book['title']} - £{book['price']}")


def example_search():
    """Exemplo de busca"""
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Busca")
    print("=" * 80)

    client = BooksAPIClient()

    # Buscar livros
    results = client.search_books("light", per_page=3)

    print(f"\n🔍 Resultados para 'light' ({results['total']} encontrados):")
    for book in results["books"]:
        print(f"  - {book['title']}")


def example_categories():
    """Exemplo de categorias"""
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Categorias")
    print("=" * 80)

    client = BooksAPIClient()

    # Listar categorias
    genres = client.get_genres()

    print(f"\n📚 Top 10 Categorias:")
    for genre in genres["genres"][:10]:
        print(f"  - {genre['name']}: {genre['count']} livros")

    # Livros de uma categoria
    if genres["genres"]:
        first_genre = genres["genres"][0]["name"]
        books = client.get_books_by_genre(first_genre, per_page=3)

        print(f"\n📖 Livros de '{first_genre}':")
        for book in books["books"]:
            print(f"  - {book['title']}")


def example_statistics():
    """Exemplo de estatísticas"""
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Estatísticas")
    print("=" * 80)

    client = BooksAPIClient()

    stats = client.get_stats()

    print(f"\n📊 Estatísticas Gerais:")
    print(f"  Total de livros: {stats['total_books']}")
    print(f"  Categorias: {stats['total_categories']}")

    print(f"\n💰 Estatísticas de Preço:")
    print(f"  Média: £{stats['price_stats']['mean']:.2f}")
    print(f"  Mediana: £{stats['price_stats']['median']:.2f}")
    print(f"  Mín: £{stats['price_stats']['min']:.2f}")
    print(f"  Máx: £{stats['price_stats']['max']:.2f}")

    print(f"\n⭐ Distribuição de Ratings:")
    for rating, count in sorted(stats["rating_distribution"].items()):
        stars = "⭐" * int(rating)
        bar = "█" * (count // 10)
        print(f"  {stars} {bar} {count}")


def example_dataframe():
    """Exemplo com Pandas DataFrame"""
    print("\n" + "=" * 80)
    print("EXEMPLO 6: Análise com Pandas")
    print("=" * 80)

    client = BooksAPIClient()

    # Obter dados
    books = client.get_books(per_page=100)
    df = pd.DataFrame(books["books"])

    print(f"\n📊 Análise Exploratória:")
    print(f"\nPrimeiras linhas:")
    print(df[["title", "price", "rating", "category"]].head())

    print(f"\n\nEstatísticas:")
    print(df[["price", "rating"]].describe())

    print(f"\n\nTop 5 Categorias:")
    print(df["category"].value_counts().head())


def example_ml_integration():
    """Exemplo de integração com ML"""
    print("\n" + "=" * 80)
    print("EXEMPLO 7: Integração com Machine Learning")
    print("=" * 80)

    client = BooksAPIClient()

    # Obter amostra para ML
    ml_data = client.get_ml_sample(size=100, random_state=42)

    print(f"\n🤖 Dados para ML:")
    print(f"  Tamanho da amostra: {ml_data['sample_size']}")
    print(f"  Random state: {ml_data['random_state']}")
    print(f"  Features: {', '.join(ml_data['features'][:5])}...")

    # Converter para DataFrame
    df = pd.DataFrame(ml_data["data"])

    print(f"\n\n📊 Features Engenheiradas:")
    print(
        f"  - price_normalized: {df['price_normalized'].min():.2f} - {df['price_normalized'].max():.2f}"
    )
    print(
        f"  - rating_normalized: {df['rating_normalized'].min():.2f} - {df['rating_normalized'].max():.2f}"
    )
    print(f"  - price_category: {df['price_category'].unique().tolist()}")

    print(f"\n\n💡 Use estes dados para:")
    print(f"  - Regressão: Prever preços com base em features")
    print(f"  - Classificação: Prever ratings")
    print(f"  - Clustering: Agrupar livros similares")
    print(f"  - Análise de sentimento: Baseado em descrições")


def main():
    """Função principal"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "📚 BOOKS API - EXEMPLOS DE USO" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Executar exemplos
        example_basic_usage()
        example_filtering()
        example_search()
        example_categories()
        example_statistics()
        example_dataframe()
        example_ml_integration()

        print("\n" + "=" * 80)
        print("✅ Todos os exemplos executados com sucesso!")
        print("=" * 80)
        print("\n💡 Dicas:")
        print("  - Use a documentação interativa: http://localhost:8000/docs")
        print("  - Veja mais exemplos em: docs/API_EXAMPLES.md")
        print("  - Leia a arquitetura em: docs/ARCHITECTURE.md")
        print("=" * 80 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API")
        print("   Certifique-se de que a API está rodando:")
        print("   uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")


if __name__ == "__main__":
    main()
