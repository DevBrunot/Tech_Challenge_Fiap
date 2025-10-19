"""
Funções utilitárias para a API
"""
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def load_books_data(filepath: str = "data/books.csv") -> pd.DataFrame:
    """
    Carrega dados dos livros do arquivo CSV
    
    Args:
        filepath: Caminho para o arquivo CSV
        
    Returns:
        DataFrame com os dados dos livros
    """
    try:
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"Arquivo {filepath} não encontrado")
            return pd.DataFrame()
        
        df = pd.read_csv(filepath)
        logger.info(f"Carregados {len(df)} livros de {filepath}")
        
        # Garantir tipos corretos
        if 'id' in df.columns:
            df['id'] = df['id'].astype(int)
        if 'price' in df.columns:
            df['price'] = df['price'].astype(float)
        if 'rating' in df.columns:
            df['rating'] = df['rating'].astype(int)
        if 'availability_copies' in df.columns:
            df['availability_copies'] = df['availability_copies'].astype(int)
        
        return df
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def filter_books(
    df: pd.DataFrame,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[int] = None
) -> pd.DataFrame:
    """
    Aplica filtros ao DataFrame de livros
    
    Args:
        df: DataFrame original
        category: Filtrar por categoria
        min_price: Preço mínimo
        max_price: Preço máximo
        min_rating: Rating mínimo
        
    Returns:
        DataFrame filtrado
    """
    result = df.copy()
    
    if category:
        result = result[result['category'].str.lower() == category.lower()]
    
    if min_price is not None:
        result = result[result['price'] >= min_price]
    
    if max_price is not None:
        result = result[result['price'] <= max_price]
    
    if min_rating is not None:
        result = result[result['rating'] >= min_rating]
    
    return result


def sort_books(df: pd.DataFrame, sort_by: str, order: str = "asc") -> pd.DataFrame:
    """
    Ordena DataFrame de livros
    
    Args:
        df: DataFrame original
        sort_by: Campo para ordenação
        order: 'asc' ou 'desc'
        
    Returns:
        DataFrame ordenado
    """
    if sort_by not in df.columns:
        logger.warning(f"Campo '{sort_by}' não encontrado. Ignorando ordenação.")
        return df
    
    ascending = order.lower() == "asc"
    return df.sort_values(by=sort_by, ascending=ascending)


def search_books(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Busca livros por termo no título ou descrição
    
    Args:
        df: DataFrame original
        query: Termo de busca
        
    Returns:
        DataFrame com resultados da busca
    """
    query_lower = query.lower()
    
    # Busca em título e descrição
    mask = (
        df['title'].str.lower().str.contains(query_lower, na=False) |
        df['description'].str.lower().str.contains(query_lower, na=False)
    )
    
    return df[mask]

