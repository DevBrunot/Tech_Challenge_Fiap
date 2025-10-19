"""
Web Scraper para Books to Scrape
Extrai dados de livros de https://books.toscrape.com/
"""
import csv
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BooksToScrapeScraper:
    """Scraper para extrair dados de livros do Books to Scrape"""
    
    BASE_URL = "https://books.toscrape.com"
    RATING_MAP = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    
    def __init__(self, delay: float = 0.5, max_retries: int = 3):
        """
        Inicializa o scraper
        
        Args:
            delay: Tempo de espera entre requisições (segundos)
            max_retries: Número máximo de tentativas em caso de falha
        """
        self.delay = delay
        self.max_retries = max_retries
        self.session = self._create_session()
        
        # Criar diretório de logs se não existir
        Path('logs').mkdir(exist_ok=True)
        
    def _create_session(self) -> requests.Session:
        """Cria sessão com retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Faz requisição HTTP com tratamento de erros
        
        Args:
            url: URL da página
            
        Returns:
            BeautifulSoup object ou None em caso de erro
        """
        try:
            logger.info(f"Acessando: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)  # Rate limiting
            return BeautifulSoup(response.content, 'lxml')
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return None
    
    def _extract_rating(self, book_element) -> int:
        """Extrai rating do livro"""
        try:
            rating_class = book_element.find('p', class_='star-rating')
            if rating_class:
                rating_text = rating_class.get('class')[1]
                return self.RATING_MAP.get(rating_text, 0)
        except Exception as e:
            logger.warning(f"Erro ao extrair rating: {e}")
        return 0
    
    def _extract_price(self, price_text: str) -> float:
        """Extrai valor numérico do preço"""
        try:
            # Remove símbolos de moeda e converte para float
            return float(price_text.replace('£', '').replace('€', '').strip())
        except ValueError:
            return 0.0
    
    def _parse_availability(self, availability_text: str) -> Dict:
        """
        Parse da string de disponibilidade
        
        Returns:
            Dict com 'status' e 'copies'
        """
        try:
            # Ex: "In stock (22 available)"
            if 'In stock' in availability_text:
                import re
                match = re.search(r'\((\d+) available\)', availability_text)
                copies = int(match.group(1)) if match else 0
                return {'status': 'In stock', 'copies': copies}
            return {'status': 'Out of stock', 'copies': 0}
        except Exception as e:
            logger.warning(f"Erro ao parsear disponibilidade: {e}")
            return {'status': 'Unknown', 'copies': 0}
    
    def _scrape_book_details(self, book_url: str) -> Dict:
        """
        Extrai detalhes completos de um livro
        
        Args:
            book_url: URL da página do livro
            
        Returns:
            Dict com detalhes do livro
        """
        soup = self._get_page(book_url)
        if not soup:
            return {}
        
        try:
            details = {}
            
            # UPC e tabela de informações
            table = soup.find('table', class_='table table-striped')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    header = row.find('th').text.strip()
                    value = row.find('td').text.strip()
                    if header == 'UPC':
                        details['upc'] = value
                    elif header == 'Availability':
                        availability = self._parse_availability(value)
                        details['availability'] = availability['status']
                        details['availability_copies'] = availability['copies']
            
            # Descrição do produto
            product_desc = soup.find('div', id='product_description')
            if product_desc:
                desc_p = product_desc.find_next('p')
                details['description'] = desc_p.text.strip() if desc_p else ''
            else:
                details['description'] = ''
            
            return details
            
        except Exception as e:
            logger.error(f"Erro ao extrair detalhes de {book_url}: {e}")
            return {}
    
    def _scrape_category_page(self, url: str, category: str) -> List[Dict]:
        """
        Extrai livros de uma página de categoria
        
        Args:
            url: URL da página
            category: Nome da categoria
            
        Returns:
            Lista de dicts com dados dos livros
        """
        books = []
        soup = self._get_page(url)
        
        if not soup:
            return books
        
        # Encontra todos os livros na página
        book_elements = soup.find_all('article', class_='product_pod')
        
        for idx, book in enumerate(book_elements, 1):
            try:
                # Dados básicos
                title_element = book.find('h3').find('a')
                title = title_element.get('title', '')
                book_path = title_element.get('href', '')
                
                # Constrói URL completa do livro
                if book_path.startswith('../../..'):
                    book_path = book_path.replace('../../..', '')
                book_url = f"{self.BASE_URL}/catalogue{book_path}"
                
                # Preço
                price_element = book.find('p', class_='price_color')
                price = self._extract_price(price_element.text) if price_element else 0.0
                
                # Rating
                rating = self._extract_rating(book)
                
                # Imagem
                img_element = book.find('img')
                img_url = img_element.get('src', '') if img_element else ''
                if img_url and not img_url.startswith('http'):
                    img_url = f"{self.BASE_URL}/{img_url.lstrip('../')}"
                
                # Detalhes adicionais da página do livro
                book_details = self._scrape_book_details(book_url)
                
                # Monta o registro completo
                book_data = {
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'category': category,
                    'product_page_url': book_url,
                    'image_url': img_url,
                    'upc': book_details.get('upc', ''),
                    'availability': book_details.get('availability', 'Unknown'),
                    'availability_copies': book_details.get('availability_copies', 0),
                    'description': book_details.get('description', ''),
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                books.append(book_data)
                logger.info(f"Extraído: {title} ({category})")
                
            except Exception as e:
                logger.error(f"Erro ao processar livro {idx}: {e}")
                continue
        
        return books
    
    def _get_all_categories(self) -> List[Dict]:
        """
        Obtém lista de todas as categorias
        
        Returns:
            Lista de dicts com 'name' e 'url' de cada categoria
        """
        soup = self._get_page(self.BASE_URL)
        if not soup:
            return []
        
        categories = []
        category_list = soup.find('ul', class_='nav nav-list')
        
        if category_list:
            # Pula o primeiro item (Books)
            category_items = category_list.find('ul').find_all('li')
            
            for item in category_items:
                link = item.find('a')
                if link:
                    name = link.text.strip()
                    url = f"{self.BASE_URL}/{link.get('href')}"
                    categories.append({'name': name, 'url': url})
        
        logger.info(f"Encontradas {len(categories)} categorias")
        return categories
    
    def _scrape_all_pages_in_category(self, category_url: str, category_name: str) -> List[Dict]:
        """
        Extrai todos os livros de todas as páginas de uma categoria
        
        Args:
            category_url: URL da primeira página da categoria
            category_name: Nome da categoria
            
        Returns:
            Lista de todos os livros da categoria
        """
        all_books = []
        current_url = category_url
        page = 1
        
        while current_url:
            logger.info(f"Processando {category_name} - página {page}")
            books = self._scrape_category_page(current_url, category_name)
            all_books.extend(books)
            
            # Verifica se há próxima página
            soup = self._get_page(current_url)
            if soup:
                next_button = soup.find('li', class_='next')
                if next_button:
                    next_link = next_button.find('a')
                    if next_link:
                        # Constrói URL da próxima página
                        next_page = next_link.get('href')
                        base = '/'.join(current_url.split('/')[:-1])
                        current_url = f"{base}/{next_page}"
                        page += 1
                        continue
            
            # Não há próxima página
            break
        
        return all_books
    
    def scrape_all_books(self) -> List[Dict]:
        """
        Extrai todos os livros de todas as categorias
        
        Returns:
            Lista com todos os livros
        """
        logger.info("Iniciando scraping completo do site")
        start_time = time.time()
        
        all_books = []
        categories = self._get_all_categories()
        
        for idx, category in enumerate(categories, 1):
            logger.info(f"Processando categoria {idx}/{len(categories)}: {category['name']}")
            books = self._scrape_all_pages_in_category(
                category['url'],
                category['name']
            )
            all_books.extend(books)
            logger.info(f"Total de livros extraídos de {category['name']}: {len(books)}")
        
        # Adiciona ID único para cada livro
        for idx, book in enumerate(all_books, 1):
            book['id'] = idx
        
        elapsed_time = time.time() - start_time
        logger.info(f"Scraping concluído! Total: {len(all_books)} livros em {elapsed_time:.2f}s")
        
        return all_books
    
    def save_to_csv(self, books: List[Dict], filepath: str = 'data/books.csv'):
        """
        Salva lista de livros em arquivo CSV
        
        Args:
            books: Lista de dicts com dados dos livros
            filepath: Caminho do arquivo de saída
        """
        if not books:
            logger.warning("Nenhum livro para salvar")
            return
        
        # Garante que o diretório existe
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Define ordem das colunas
        fieldnames = [
            'id', 'title', 'price', 'availability', 'availability_copies',
            'rating', 'category', 'product_page_url', 'upc', 'description',
            'image_url', 'scraped_at'
        ]
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(books)
            
            logger.info(f"Dados salvos em {filepath} ({len(books)} registros)")
        except Exception as e:
            logger.error(f"Erro ao salvar CSV: {e}")


def main():
    """Função principal para executar o scraper"""
    logger.info("=" * 80)
    logger.info("Iniciando Books to Scrape Scraper")
    logger.info("=" * 80)
    
    scraper = BooksToScrapeScraper(delay=0.5, max_retries=3)
    books = scraper.scrape_all_books()
    scraper.save_to_csv(books)
    
    logger.info("=" * 80)
    logger.info("Processo concluído!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()


