# Exemplos de Uso da API

## Requisitos

```bash
# Instalar curl ou usar ferramentas como Postman, Insomnia
# Python com requests (opcional)
pip install requests
```

## Exemplos com cURL

### 1. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "total_books": 1000,
  "data_loaded": true
}
```

### 2. Listar Livros (Paginado)

```bash
curl -X GET "http://localhost:8000/books?page=1&per_page=10"
```

**Resposta:**
```json
{
  "total": 1000,
  "page": 1,
  "per_page": 10,
  "total_pages": 100,
  "books": [
    {
      "id": 1,
      "title": "A Light in the Attic",
      "price": 51.77,
      "availability": "In stock",
      "availability_copies": 22,
      "rating": 3,
      "category": "Poetry",
      "product_page_url": "https://books.toscrape.com/catalogue/...",
      "upc": "a897fe39b1053632",
      "description": "It's hard to imagine...",
      "image_url": "https://books.toscrape.com/media/cache/...",
      "scraped_at": "2024-01-15T10:00:00"
    }
  ]
}
```

### 3. Filtrar por Categoria

```bash
curl -X GET "http://localhost:8000/books?category=Fiction&page=1&per_page=5"
```

### 4. Filtrar por Faixa de Preço

```bash
curl -X GET "http://localhost:8000/books?min_price=10&max_price=30&per_page=20"
```

### 5. Filtrar por Rating Mínimo

```bash
curl -X GET "http://localhost:8000/books?min_rating=4&per_page=20"
```

### 6. Ordenar por Preço (Crescente)

```bash
curl -X GET "http://localhost:8000/books?sort=price&order=asc&per_page=10"
```

### 7. Ordenar por Rating (Decrescente)

```bash
curl -X GET "http://localhost:8000/books?sort=rating&order=desc&per_page=10"
```

### 8. Combinar Múltiplos Filtros

```bash
curl -X GET "http://localhost:8000/books?category=Fiction&min_price=20&max_price=50&min_rating=3&sort=price&order=asc&page=1&per_page=10"
```

### 9. Buscar Livro por ID

```bash
curl -X GET "http://localhost:8000/books/1"
```

**Resposta:**
```json
{
  "id": 1,
  "title": "A Light in the Attic",
  "price": 51.77,
  "availability": "In stock",
  "availability_copies": 22,
  "rating": 3,
  "category": "Poetry",
  "product_page_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "upc": "a897fe39b1053632",
  "description": "It's hard to imagine a world without A Light in the Attic...",
  "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
  "scraped_at": "2024-01-15T10:00:00"
}
```

### 10. Buscar Livros por Termo

```bash
curl -X GET "http://localhost:8000/books/search?q=light&page=1&per_page=10"
```

### 11. Listar Todas as Categorias

```bash
curl -X GET "http://localhost:8000/books/genres"
```

**Resposta:**
```json
{
  "total": 50,
  "genres": [
    {
      "name": "Fiction",
      "count": 65
    },
    {
      "name": "Poetry",
      "count": 45
    },
    {
      "name": "Science",
      "count": 32
    }
  ]
}
```

### 12. Livros por Categoria/Gênero

```bash
curl -X GET "http://localhost:8000/books/genre/Fiction?page=1&per_page=20"
```

### 13. Estatísticas Agregadas

```bash
curl -X GET "http://localhost:8000/stats"
```

**Resposta:**
```json
{
  "total_books": 1000,
  "total_categories": 50,
  "price_stats": {
    "mean": 35.85,
    "median": 35.99,
    "min": 10.00,
    "max": 59.99,
    "std": 12.45
  },
  "rating_distribution": {
    "1": 50,
    "2": 150,
    "3": 300,
    "4": 350,
    "5": 150
  },
  "top_categories": {
    "Fiction": 200,
    "Science": 150,
    "History": 120
  },
  "price_bins": {
    "budget": 250,
    "moderate": 400,
    "premium": 250,
    "luxury": 100
  },
  "availability_stats": {
    "In stock": 980,
    "Out of stock": 20
  },
  "avg_normalized_rating": 0.68
}
```

### 14. Amostra para Machine Learning

```bash
curl -X GET "http://localhost:8000/ml/sample?size=100&random_state=42"
```

**Resposta:**
```json
{
  "sample_size": 100,
  "random_state": 42,
  "features": [
    "id", "title", "price", "rating", "category",
    "price_normalized", "rating_normalized", 
    "has_description", "price_category"
  ],
  "data": [...]
}
```

## Exemplos com Python

### Instalação

```bash
pip install requests pandas
```

### Script Básico

```python
import requests
import pandas as pd

# Base URL da API
BASE_URL = "http://localhost:8000"

# 1. Health Check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 2. Listar livros
response = requests.get(f"{BASE_URL}/books", params={
    "page": 1,
    "per_page": 20,
    "sort": "price",
    "order": "asc"
})
books = response.json()
print(f"Total de livros: {books['total']}")

# 3. Converter para DataFrame
df = pd.DataFrame(books['books'])
print(df.head())

# 4. Buscar livros
response = requests.get(f"{BASE_URL}/books/search", params={
    "q": "python",
    "per_page": 10
})
results = response.json()
print(f"Encontrados: {results['total']} livros")

# 5. Obter estatísticas
response = requests.get(f"{BASE_URL}/stats")
stats = response.json()
print(f"Preço médio: £{stats['price_stats']['mean']:.2f}")

# 6. Amostra para ML
response = requests.get(f"{BASE_URL}/ml/sample", params={
    "size": 500,
    "random_state": 42
})
ml_data = response.json()
df_ml = pd.DataFrame(ml_data['data'])
print(df_ml.columns)
```

### Análise Exploratória

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Obter todos os livros (paginando)
all_books = []
page = 1
per_page = 100

while True:
    response = requests.get(
        "http://localhost:8000/books",
        params={"page": page, "per_page": per_page}
    )
    data = response.json()
    all_books.extend(data['books'])
    
    if page >= data['total_pages']:
        break
    page += 1

# Criar DataFrame
df = pd.DataFrame(all_books)

# Análises
print(df.describe())
print(df['category'].value_counts().head(10))

# Visualizações
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
df['price'].hist(bins=30)
plt.title('Distribuição de Preços')
plt.xlabel('Preço (£)')

plt.subplot(1, 2, 2)
df['rating'].value_counts().sort_index().plot(kind='bar')
plt.title('Distribuição de Ratings')
plt.xlabel('Rating')

plt.tight_layout()
plt.show()
```

### Integração com Jupyter Notebook

```python
# Notebook: books_analysis.ipynb

import requests
import pandas as pd
import numpy as np
from IPython.display import display

# Configuração
API_URL = "http://localhost:8000"

# Função helper
def get_all_books():
    """Obter todos os livros da API"""
    all_books = []
    page = 1
    
    while True:
        response = requests.get(f"{API_URL}/books", params={
            "page": page,
            "per_page": 100
        })
        data = response.json()
        all_books.extend(data['books'])
        
        if page >= data['total_pages']:
            break
        page += 1
    
    return pd.DataFrame(all_books)

# Carregar dados
df = get_all_books()
display(df.head())

# Feature Engineering
df['price_per_rating'] = df['price'] / df['rating']
df['is_premium'] = df['price'] > df['price'].quantile(0.75)

# Análises
print("Top 10 Livros Mais Caros:")
display(df.nlargest(10, 'price')[['title', 'price', 'rating', 'category']])

print("\nCategorias Mais Populares:")
display(df['category'].value_counts().head(10))
```

### Pipeline de ML

```python
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# 1. Obter dados de treino
response = requests.get("http://localhost:8000/ml/sample", params={
    "size": 800,
    "random_state": 42
})
data = response.json()['data']
df = pd.DataFrame(data)

# 2. Preparar features
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category'])

X = df[['category_encoded', 'rating', 'availability_copies']]
y = df['price']

# 3. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Treinar modelo
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Avaliar
y_pred = model.predict(X_test)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

# 6. Feature Importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance)
```

## Documentação Interativa

Acesse a documentação Swagger interativa:

```
http://localhost:8000/docs
```

Ou ReDoc:

```
http://localhost:8000/redoc
```

## Tratamento de Erros

### Livro não encontrado (404)

```bash
curl -X GET "http://localhost:8000/books/99999"
```

```json
{
  "detail": "Livro com ID 99999 não encontrado"
}
```

### Página inválida (422)

```bash
curl -X GET "http://localhost:8000/books?page=-1"
```

```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error"
    }
  ]
}
```

### Dados não disponíveis (503)

```bash
curl -X GET "http://localhost:8000/books"
```

```json
{
  "detail": "Dados não disponíveis"
}
```

## Rate Limiting

Atualmente não há rate limiting implementado na API, mas recomenda-se:

- Máximo 100 requisições por minuto por IP
- Usar cache local quando possível
- Implementar retry com backoff exponencial

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get("http://localhost:8000/books")
```

## Próximos Passos

1. Implementar autenticação (API Keys)
2. Adicionar rate limiting
3. Implementar cache Redis
4. Adicionar webhooks para atualizações
5. Endpoint de predição ML

