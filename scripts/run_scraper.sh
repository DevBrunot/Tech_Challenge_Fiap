#!/bin/bash
# Script para executar o scraper com logging

echo "==========================================";
echo "  Books to Scrape - Web Scraper";
echo "==========================================";
echo "";

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual...";
    source venv/bin/activate;
fi

# Criar diretórios necessários
mkdir -p logs data

# Executar scraper
echo "Iniciando scraper...";
echo "";

python scripts/scraper.py

echo "";
echo "==========================================";
echo "  Scraping concluído!";
echo "  Verifique: data/books.csv";
echo "  Logs: logs/scraper.log";
echo "==========================================";

