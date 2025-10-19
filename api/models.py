"""
Modelos Pydantic para validação e documentação da API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Book(BaseModel):
    """Modelo de um livro"""

    id: int = Field(..., description="ID único do livro")
    title: str = Field(..., description="Título do livro")
    price: float = Field(..., description="Preço do livro em libras")
    availability: str = Field(..., description="Status de disponibilidade")
    availability_copies: int = Field(..., description="Número de cópias disponíveis")
    rating: int = Field(..., ge=1, le=5, description="Rating de 1 a 5 estrelas")
    category: str = Field(..., description="Categoria/gênero do livro")
    product_page_url: str = Field(..., description="URL da página do produto")
    upc: str = Field(..., description="Código UPC do produto")
    description: Optional[str] = Field(None, description="Descrição do livro")
    image_url: str = Field(..., description="URL da imagem da capa")
    scraped_at: str = Field(..., description="Data/hora da coleta (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "A Light in the Attic",
                "price": 51.77,
                "availability": "In stock",
                "availability_copies": 22,
                "rating": 3,
                "category": "Poetry",
                "product_page_url": "https://books.toscrape.com/catalogue/...",
                "upc": "a897fe39b1053632",
                "description": "It's hard to imagine a world without A Light in the Attic...",
                "image_url": "https://books.toscrape.com/media/cache/...",
                "scraped_at": "2024-01-15T10:30:00",
            }
        }


class BookList(BaseModel):
    """Lista paginada de livros"""

    total: int = Field(..., description="Total de livros encontrados", alias="total")
    pagina: int = Field(..., description="Página atual", alias="pagina")
    por_pagina: int = Field(..., description="Itens por página", alias="por_pagina")
    total_paginas: int = Field(
        ..., description="Total de páginas", alias="total_paginas"
    )
    livros: List[Book] = Field(
        ..., description="Lista de livros da página", alias="livros"
    )

    class Config:
        populate_by_name = True


class Genre(BaseModel):
    """Modelo de gênero/categoria"""

    nome: str = Field(..., description="Nome da categoria", alias="nome")
    contagem: int = Field(
        ..., description="Número de livros na categoria", alias="contagem"
    )

    class Config:
        populate_by_name = True


class GenreList(BaseModel):
    """Lista de gêneros/categorias"""

    total: int = Field(..., description="Total de categorias", alias="total")
    generos: List[Genre] = Field(
        ..., description="Lista de categorias", alias="generos"
    )

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    """Resposta do health check"""

    status: str = Field(..., description="Status da aplicação", alias="status")
    timestamp: str = Field(
        ..., description="Timestamp da verificação", alias="timestamp"
    )
    total_livros: int = Field(
        ..., description="Total de livros carregados", alias="total_livros"
    )
    dados_carregados: bool = Field(
        ..., description="Indica se os dados foram carregados", alias="dados_carregados"
    )

    class Config:
        populate_by_name = True


class StatsResponse(BaseModel):
    """Estatísticas agregadas dos dados"""

    total_livros: int = Field(..., description="Total de livros", alias="total_livros")
    total_categorias: int = Field(
        ..., description="Total de categorias", alias="total_categorias"
    )
    estatisticas_preco: Dict[str, float] = Field(
        ..., description="Estatísticas de preço", alias="estatisticas_preco"
    )
    distribuicao_avaliacoes: Dict[int, int] = Field(
        ..., description="Distribuição de avaliações", alias="distribuicao_avaliacoes"
    )
    top_categorias: Dict[str, int] = Field(
        ..., description="Top 10 categorias", alias="top_categorias"
    )
    faixas_preco: Dict[str, int] = Field(
        ..., description="Distribuição por faixa de preço", alias="faixas_preco"
    )
    estatisticas_disponibilidade: Dict[str, int] = Field(
        ...,
        description="Estatísticas de disponibilidade",
        alias="estatisticas_disponibilidade",
    )
    media_avaliacao_normalizada: float = Field(
        ...,
        description="Média da avaliação normalizada",
        alias="media_avaliacao_normalizada",
    )

    class Config:
        populate_by_name = True
