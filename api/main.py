"""
API RESTful para Books to Scrape
FastAPI application com endpoints para consumo dos dados de livros
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

from api.models import Book, BookList, GenreList, StatsResponse, HealthResponse
from api.utils import load_books_data, filter_books, sort_books, search_books

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa FastAPI
app = FastAPI(
    title="Books to Scrape API",
    description="API RESTful para consulta de dados de livros extraídos via web scraping",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuração CORS - permite acesso público
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega dados ao iniciar
try:
    BOOKS_DF = load_books_data()
    logger.info(f"Dados carregados: {len(BOOKS_DF)} livros")
except Exception as e:
    logger.error(f"Erro ao carregar dados: {e}")
    BOOKS_DF = pd.DataFrame()


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "mensagem": "Books to Scrape API",
        "versao": "1.0.0",
        "documentacao": "/docs",
        "saude": "/health",
        "endpoints": {
            "livros": "/books",
            "livro_por_id": "/books/{id}",
            "busca": "/books/search",
            "generos": "/books/genres",
            "livros_por_genero": "/books/genre/{genre}",
            "estatisticas": "/stats",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Endpoint de verificação de saúde da API"""
    return {
        "status": "saudavel",
        "timestamp": datetime.utcnow().isoformat(),
        "total_livros": len(BOOKS_DF),
        "dados_carregados": not BOOKS_DF.empty,
    }


@app.get("/books", response_model=BookList, tags=["Books"])
async def get_books(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Livros por página"),
    sort: Optional[str] = Query(None, description="Campo para ordenação (ex: price, rating, title)"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Ordem: asc ou desc"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Rating mínimo"),
):
    """
    Lista paginada de livros com filtros e ordenação

    - **page**: número da página (inicia em 1)
    - **per_page**: quantidade de itens por página (máximo 100)
    - **sort**: campo para ordenação (price, rating, title, category)
    - **order**: ordem (asc para crescente/desc para decrescente)
    - **category**: filtrar por categoria específica
    - **min_price/max_price**: filtro de faixa de preço
    - **min_rating**: filtro de avaliação mínima
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    df = BOOKS_DF.copy()

    # Aplicar filtros
    df = filter_books(df, category=category, min_price=min_price, max_price=max_price, min_rating=min_rating)

    # Aplicar ordenação
    if sort:
        df = sort_books(df, sort, order)

    # Paginação
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page

    if start >= total and total > 0:
        raise HTTPException(status_code=404, detail="Página não encontrada")

    books_page = df.iloc[start:end].to_dict("records")

    return {
        "total": total,
        "pagina": page,
        "por_pagina": per_page,
        "total_paginas": (total + per_page - 1) // per_page,
        "livros": books_page,
    }


@app.get("/books/search", response_model=BookList, tags=["Books"])
async def search_books_endpoint(
    q: str = Query(..., min_length=1, description="Termo de busca"),
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Livros por página"),
):
    """
    Busca livros por título ou descrição

    - **q**: termo de busca (pesquisa em título e descrição)
    - **page**: número da página
    - **per_page**: quantidade de livros por página
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    df = search_books(BOOKS_DF, q)

    # Paginação
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page

    books_page = df.iloc[start:end].to_dict("records")

    return {
        "total": total,
        "pagina": page,
        "por_pagina": per_page,
        "total_paginas": (total + per_page - 1) // per_page,
        "livros": books_page,
    }


@app.get("/books/genres", response_model=GenreList, tags=["Genres"])
async def get_genres():
    """
    Lista todas as categorias/gêneros disponíveis com contagem de livros
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    genre_counts = BOOKS_DF["category"].value_counts().to_dict()
    genres = [{"nome": genre, "contagem": count} for genre, count in genre_counts.items()]

    return {"total": len(genres), "generos": genres}


@app.get("/books/genre/{genre}", response_model=BookList, tags=["Genres"])
async def get_books_by_genre(
    genre: str,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Livros por página"),
):
    """
    Lista livros de uma categoria/gênero específico (paginado)

    - **genre**: nome da categoria/gênero
    - **page**: número da página
    - **per_page**: livros por página
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    # Busca case-insensitive
    df = BOOKS_DF[BOOKS_DF["category"].str.lower() == genre.lower()]

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Categoria '{genre}' não encontrada")

    # Paginação
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page

    books_page = df.iloc[start:end].to_dict("records")

    return {
        "total": total,
        "pagina": page,
        "por_pagina": per_page,
        "total_paginas": (total + per_page - 1) // per_page,
        "livros": books_page,
    }


@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book_by_id(book_id: int):
    """
    Retorna detalhes de um livro específico pelo ID

    - **book_id**: ID único do livro
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    book = BOOKS_DF[BOOKS_DF["id"] == book_id]

    if book.empty:
        raise HTTPException(status_code=404, detail=f"Livro com ID {book_id} não encontrado")

    return book.iloc[0].to_dict()


@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_statistics():
    """
    Retorna estatísticas agregadas e features para Data Science/ML

    Inclui:
    - Estatísticas gerais (total de livros, categorias, etc)
    - Estatísticas de preço
    - Distribuição de avaliações
    - Top categorias
    - Features engenheiradas (faixas de preço, avaliação normalizada)
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    df = BOOKS_DF.copy()

    # Estatísticas de preço
    price_stats = {
        "media": float(df["price"].mean()),
        "mediana": float(df["price"].median()),
        "minimo": float(df["price"].min()),
        "maximo": float(df["price"].max()),
        "desvio_padrao": float(df["price"].std()),
    }

    # Distribuição de avaliações
    rating_distribution = df["rating"].value_counts().sort_index().to_dict()
    rating_distribution = {int(k): int(v) for k, v in rating_distribution.items()}

    # Top categorias
    top_categories = df["category"].value_counts().head(10).to_dict()

    # Features engenheiradas
    # Faixas de preço
    df["price_bin"] = pd.cut(df["price"], bins=[0, 20, 40, 60, 100], labels=["economico", "moderado", "premium", "luxo"])
    price_bins = df["price_bin"].value_counts().to_dict()
    price_bins = {str(k): int(v) for k, v in price_bins.items()}

    # Avaliação normalizada (0-1)
    df["normalized_rating"] = df["rating"] / 5.0

    # Estatísticas de disponibilidade
    availability_stats = df["availability"].value_counts().to_dict()

    return {
        "total_livros": len(df),
        "total_categorias": df["category"].nunique(),
        "estatisticas_preco": price_stats,
        "distribuicao_avaliacoes": rating_distribution,
        "top_categorias": top_categories,
        "faixas_preco": price_bins,
        "estatisticas_disponibilidade": availability_stats,
        "media_avaliacao_normalizada": float(df["normalized_rating"].mean()),
    }


# Endpoint extra para exportar amostra de dados para treinamento de ML
@app.get("/ml/sample", tags=["Machine Learning"])
async def get_ml_sample(
    size: int = Query(100, ge=10, le=5000, description="Tamanho da amostra"),
    random_state: int = Query(42, description="Seed para reprodutibilidade"),
):
    """
    Retorna amostra aleatória dos dados para treinamento de modelos ML

    - **size**: tamanho da amostra (10-5000)
    - **random_state**: seed para garantir reprodutibilidade

    Inclui features engenheiradas:
    - preco_normalizado: preço normalizado (0-1)
    - avaliacao_normalizada: avaliação normalizada (0-1)
    - categoria_preco: categoria de preço
    - tem_descricao: flag indicando se tem descrição
    """
    if BOOKS_DF.empty:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")

    df = BOOKS_DF.copy()

    # Features engenheiradas
    df["preco_normalizado"] = (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min())
    df["avaliacao_normalizada"] = df["rating"] / 5.0
    df["tem_descricao"] = df["description"].str.len() > 0
    df["categoria_preco"] = pd.cut(
        df["price"], bins=[0, 20, 40, 60, 100], labels=["economico", "moderado", "premium", "luxo"]
    ).astype(str)

    # Amostragem
    sample_size = min(size, len(df))
    sample = df.sample(n=sample_size, random_state=random_state)

    return {
        "tamanho_amostra": sample_size,
        "seed_aleatorio": random_state,
        "features": list(sample.columns),
        "dados": sample.to_dict("records"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
