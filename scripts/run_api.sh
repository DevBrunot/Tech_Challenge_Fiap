#!/bin/bash
# Script para executar a API

echo "==========================================";
echo "  Books to Scrape - API";
echo "==========================================";
echo "";

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual...";
    source venv/bin/activate;
fi

# Verificar se os dados existem
if [ ! -f "data/books.csv" ]; then
    echo "⚠️  AVISO: data/books.csv não encontrado!";
    echo "Execute o scraper primeiro: python scripts/scraper.py";
    echo "";
    read -p "Continuar mesmo assim? (y/n) " -n 1 -r
    echo "";
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1;
    fi
fi

echo "Iniciando API...";
echo "Acesse: http://localhost:8000/docs";
echo "";

# Executar API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

