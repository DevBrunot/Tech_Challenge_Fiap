# Dockerfile para API Books to Scrape
FROM python:3.11-slim

# Metadados
LABEL maintainer="Tech Challenge"
LABEL description="Books to Scrape API"

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p logs data

# Expõe porta da API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando padrão para iniciar a API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

