.PHONY: help install scrape api test lint format clean docker-build docker-run deploy-render

help:
	@echo "📚 Books to Scrape - Comandos Disponíveis"
	@echo ""
	@echo "  make install       - Instalar dependências"
	@echo "  make scrape        - Executar web scraper"
	@echo "  make api           - Iniciar API"
	@echo "  make test          - Executar testes"
	@echo "  make lint          - Executar linting"
	@echo "  make format        - Formatar código"
	@echo "  make clean         - Limpar arquivos temporários"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Executar com Docker"
	@echo ""

install:
	@echo "📦 Instalando dependências..."
	pip install --upgrade pip
	pip install -r requirements.txt
	mkdir -p logs data tests/data

scrape:
	@echo "🕷️  Executando scraper..."
	python scripts/scraper.py

api:
	@echo "🚀 Iniciando API..."
	@echo "📖 Documentação: http://localhost:8000/docs"
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Executando testes..."
	pytest tests/ -v --cov=api --cov=scripts

lint:
	@echo "🔍 Executando linting..."
	flake8 api/ scripts/ tests/ --max-line-length=127

format:
	@echo "✨ Formatando código..."
	black api/ scripts/ tests/

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	@echo "✅ Limpeza concluída"

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t books-api:latest .

docker-run:
	@echo "🐳 Executando com Docker..."
	docker run -d -p 8000:8000 --name books-api books-api:latest
	@echo "✅ API rodando em http://localhost:8000"

docker-compose-up:
	@echo "🐳 Iniciando com Docker Compose..."
	docker-compose up -d
	@echo "✅ Serviços iniciados"

docker-compose-down:
	@echo "🐳 Parando serviços..."
	docker-compose down

dev:
	@echo "👨‍💻 Modo desenvolvimento..."
	@echo "1. Instalando dependências..."
	make install
	@echo "2. Executando scraper..."
	make scrape
	@echo "3. Iniciando API..."
	make api

