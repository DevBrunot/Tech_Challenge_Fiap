# Arquitetura do Sistema - Books to Scrape API

## Visão Geral

O sistema implementa um pipeline completo de ETL (Extract, Transform, Load) para coleta, processamento e disponibilização de dados de livros através de uma API RESTful.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPELINE DE DADOS                            │
└─────────────────────────────────────────────────────────────────────┘

1. EXTRAÇÃO (Web Scraping)
   ┌──────────────────────┐
   │  books.toscrape.com  │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │   Scraper Python     │
   │   - BeautifulSoup    │
   │   - Requests         │
   │   - Retry Logic      │
   │   - Rate Limiting    │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │   data/books.csv     │
   │   (1000+ registros)  │
   └──────────┬───────────┘

2. TRANSFORMAÇÃO & SERVIR
              │
              ▼
   ┌──────────────────────┐
   │   API FastAPI        │
   │   - Endpoints REST   │
   │   - Paginação        │
   │   - Filtros          │
   │   - Busca            │
   │   - Features ML      │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │   Redis Cache        │
   │   (opcional)         │
   └──────────────────────┘

3. CONSUMO
              │
              ▼
   ┌─────────────────────────────────────────┐
   │  Clientes (Apps, Data Science, ML)      │
   │  - Web Applications                      │
   │  - Jupyter Notebooks                     │
   │  - ML Training Pipelines                 │
   │  - Analytics Dashboards                  │
   └─────────────────────────────────────────┘
```

## Componentes

### 1. Web Scraper (`scripts/scraper.py`)

**Responsabilidades:**
- Extrair dados estruturados de https://books.toscrape.com/
- Tratamento robusto de erros e retry logic
- Rate limiting para não sobrecarregar o servidor
- Logging detalhado de todas as operações

**Características:**
- **Resiliência**: Retry automático com backoff exponencial
- **Rate Limiting**: Delay configurável entre requisições
- **Logging**: Logs detalhados em `logs/scraper.log`
- **Incremental**: Pode ser executado múltiplas vezes
- **Validação**: Valida dados antes de salvar

**Esquema de Dados Extraídos:**
```python
{
    'id': int,                      # ID único
    'title': str,                   # Título do livro
    'price': float,                 # Preço em £
    'availability': str,            # Status de disponibilidade
    'availability_copies': int,     # Número de cópias
    'rating': int,                  # Rating 1-5
    'category': str,                # Categoria/gênero
    'product_page_url': str,        # URL da página
    'upc': str,                     # Código UPC
    'description': str,             # Descrição
    'image_url': str,               # URL da imagem
    'scraped_at': str              # Timestamp ISO
}
```

### 2. API RESTful (`api/`)

**Stack Técnica:**
- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn (ASGI)
- **Validação**: Pydantic models
- **Documentação**: OpenAPI/Swagger automática

**Endpoints Principais:**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Health check |
| GET | `/books` | Lista paginada com filtros |
| GET | `/books/{id}` | Detalhes de um livro |
| GET | `/books/search` | Busca por termo |
| GET | `/books/genres` | Lista de categorias |
| GET | `/books/genre/{genre}` | Livros por categoria |
| GET | `/stats` | Estatísticas agregadas |
| GET | `/ml/sample` | Amostra para ML |

**Features:**
- ✅ Paginação completa
- ✅ Filtros (preço, rating, categoria)
- ✅ Ordenação (ASC/DESC)
- ✅ Busca full-text
- ✅ CORS habilitado
- ✅ Documentação Swagger
- ✅ Features para ML
- ✅ Estatísticas agregadas

### 3. Camada de Cache (Opcional)

**Redis**:
- Cache de listagens frequentes
- TTL configurável
- Invalidação automática

## Estratégia de Escalabilidade

### Horizontal Scaling

1. **Load Balancer**: Nginx/HAProxy na frente da API
2. **Múltiplas Instâncias**: Deploy em Kubernetes/Docker Swarm
3. **Auto-scaling**: Baseado em métricas de CPU/memória

### Data Layer

1. **Database Migration**:
   - Migrar de CSV para PostgreSQL/MongoDB
   - Índices em campos de busca (title, category)
   - Full-text search com PostgreSQL

2. **Cache Layer**:
   - Redis para queries frequentes
   - TTL de 5-15 minutos
   - Cache warming em horários de baixo tráfego

3. **CDN**:
   - CloudFlare/AWS CloudFront para API responses
   - Cache de imagens dos livros

### Processamento Assíncrono

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Scraper   │────────▶│  Message     │────────▶│  Workers    │
│   Trigger   │         │  Queue       │         │  (Celery)   │
└─────────────┘         │  (RabbitMQ)  │         └─────────────┘
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Database    │
                        │  (Postgres)  │
                        └──────────────┘
```

### Monitoramento

- **APM**: DataDog, New Relic
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus + Grafana
- **Alertas**: PagerDuty

## Casos de Uso para Data Science

### 1. Análise Exploratória

```python
import requests
import pandas as pd

# Obter dados
response = requests.get('http://api.example.com/books?per_page=1000')
df = pd.DataFrame(response.json()['books'])

# Análises
print(df['price'].describe())
print(df['category'].value_counts())
```

### 2. Feature Engineering

A API já fornece features prontas:
- `price_normalized`: Preço normalizado (0-1)
- `rating_normalized`: Rating normalizado (0-1)
- `price_category`: Budget, Moderate, Premium, Luxury
- `has_description`: Boolean

### 3. Datasets para Treinamento

```python
# Amostra reproduzível para ML
response = requests.get('http://api.example.com/ml/sample?size=500&random_state=42')
train_data = response.json()['data']
```

## Integração com ML Pipelines

### Fluxo de Trabalho

```
1. COLETA DE DADOS
   └─▶ GET /ml/sample?size=1000

2. PRÉ-PROCESSAMENTO
   └─▶ Features já normalizadas
   └─▶ Encoding de categorias
   └─▶ Split train/test

3. TREINAMENTO
   └─▶ Modelos: Regressão de preço, Classificação de rating

4. PREDIÇÃO
   └─▶ Novo endpoint: POST /ml/predict

5. FEEDBACK LOOP
   └─▶ Armazenar predições
   └─▶ Re-treinar periodicamente
```

### Endpoints Futuros para ML

```python
# Proposta de endpoints adicionais
POST /ml/predict          # Predição de preço/rating
GET  /ml/models           # Listar modelos disponíveis
GET  /ml/model/{id}       # Detalhes de um modelo
POST /ml/train            # Trigger treinamento
GET  /ml/metrics          # Métricas dos modelos
```

### Versionamento de Datasets

```bash
# Estrutura proposta
data/
├── v1.0/
│   ├── books_20240101.csv
│   └── metadata.json
├── v1.1/
│   ├── books_20240201.csv
│   └── metadata.json
└── latest -> v1.1/
```

## Segurança

### Implementado
- ✅ CORS configurado
- ✅ Rate limiting (via scraper)
- ✅ Validação de inputs (Pydantic)
- ✅ Health checks

### Recomendações Futuras
- 🔄 Autenticação (API Keys, OAuth2)
- 🔄 Rate limiting na API (limitações por IP)
- 🔄 HTTPS obrigatório
- 🔄 Input sanitization avançado
- 🔄 Audit logging

## Performance

### Otimizações Atuais
- Carregamento de dados em memória (DataFrame)
- Filtros e buscas otimizados com Pandas
- Paginação para evitar payloads grandes

### Benchmarks Esperados
- Latência: < 100ms (p95)
- Throughput: ~1000 req/s (single instance)
- Memory: ~200MB (com 1000 livros)

### Otimizações Futuras
```python
# Índices de banco de dados
CREATE INDEX idx_category ON books(category);
CREATE INDEX idx_price ON books(price);
CREATE INDEX idx_rating ON books(rating);
CREATE INDEX idx_title_fulltext ON books USING GIN(to_tsvector('english', title));

# Caching
@cache(expire=300)
def get_books_list(...):
    ...
```

## Manutenção

### Backups
- Backup diário do CSV
- Versionamento no Git
- Arquivos de log rotacionados

### Monitoramento
- Health check endpoint
- Logs estruturados
- Métricas de uso

### Atualizações
```bash
# Re-executar scraper periodicamente
0 2 * * * cd /app && python scripts/scraper.py
```

## Tecnologias

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Linguagem | Python | 3.11+ |
| Web Framework | FastAPI | 0.104+ |
| Web Server | Uvicorn | 0.24+ |
| Scraping | BeautifulSoup4 | 4.12+ |
| HTTP Client | Requests | 2.31+ |
| Data Processing | Pandas | 2.1+ |
| Validation | Pydantic | 2.5+ |
| Testing | Pytest | 7.4+ |
| Cache | Redis | 7+ |
| Container | Docker | 24+ |
| CI/CD | GitHub Actions | - |
| Deploy | Render/Heroku | - |

## Conclusão

Esta arquitetura fornece:
- ✅ Pipeline completo de dados
- ✅ API escalável e documentada
- ✅ Pronto para integração com ML
- ✅ Monitoramento e observabilidade
- ✅ Deploy automatizado
- ✅ Testes automatizados

