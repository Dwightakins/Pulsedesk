import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Article:
    title: str
    url: str
    source: str
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now()

class ScraperConfig:
    TIMEOUT = 8
    RETRIES = 3
    RETRY_DELAY = 1
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    SOURCES = {
        'nairametrics': {
            'url': 'https://nairametrics.com',
            'selectors': {'article': 'article', 'title': 'h2, h3'},
            'link_attr': 'href'
        },
        'businessday': {
            'url': 'https://businessday.ng',
            'selectors': {'article': 'article, div[class*="post"]', 'title': 'h2, h3'},
            'link_attr': 'href'
        },
        'techpoint': {
            'url': 'https://techpoint.africa',
            'selectors': {'article': 'article', 'title': 'h2, h3'},
            'link_attr': 'href'
        },
        'artnews': {
            'url': 'https://www.artnews.com',
            'selectors': {'article': 'article', 'title': 'h2, h3'},
            'link_attr': 'href'
        },
        'art_africa': {
            'url': 'https://www.artafricamagazine.org',
            'selectors': {'article': 'article, div[class*="post"]', 'title': 'h2, h3'},
            'link_attr': 'href'
        }
    }

class BaseScraper:
    def __init__(self, source_key: str, config: Dict):
        self.source_key = source_key
        self.source_name = source_key.replace('_', ' ').title()
        self.url = config['url']
        self.selectors = config['selectors']
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': ScraperConfig.USER_AGENT})
    
    def _fetch(self) -> Optional[BeautifulSoup]:
        for attempt in range(ScraperConfig.RETRIES):
            try:
                response = self.session.get(
                    self.url,
                    timeout=ScraperConfig.TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt < ScraperConfig.RETRIES - 1:
                    logger.warning(f"{self.source_name}: Attempt {attempt + 1} failed, retrying...")
                    time.sleep(ScraperConfig.RETRY_DELAY)
                else:
                    logger.error(f"{self.source_name}: Failed after {ScraperConfig.RETRIES} attempts - {str(e)}")
                    return None
    
    def _normalize_url(self, href: str) -> str:
        if not href or href.startswith('javascript'):
            return None
        if href.startswith('http'):
            return href
        base = self.url.rstrip('/')
        return f"{base}/{href.lstrip('/')}"
    
    def _extract_articles(self, soup: BeautifulSoup) -> List[Article]:
        articles = []
        try:
            article_elements = soup.select(self.selectors['article'])[:8]
            for element in article_elements:
                title_elem = element.select_one(self.selectors['title'])
                link_elem = element.find('a', href=True)
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    href = link_elem.get('href')
                    if title and len(title) > 5:
                        url = self._normalize_url(href)
                        if url:
                            articles.append(Article(
                                title=title,
                                url=url,
                                source=self.source_name
                            ))
            logger.info(f"{self.source_name}: Extracted {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"{self.source_name}: Error extracting - {str(e)}")
            return []
    
    def scrape(self) -> List[Article]:
        soup = self._fetch()
        if soup:
            return self._extract_articles(soup)
        return []

class ArticleAggregator:
    def __init__(self):
        self.config = ScraperConfig()
        self.scrapers = {
            key: BaseScraper(key, config)
            for key, config in self.config.SOURCES.items()
        }
    
    def scrape_all(self, max_workers: int = 3) -> List[Article]:
        all_articles = []
        logger.info(f"Starting concurrent scrape of {len(self.scrapers)} sources...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(scraper.scrape): name
                for name, scraper in self.scrapers.items()
            }
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"Error scraping {source_name}: {str(e)}")
        logger.info(f"Scrape complete: {len(all_articles)} total articles")
        return all_articles
    
    def get_articles(self) -> List[Article]:
        return self.scrape_all()

if __name__ == "__main__":
    aggregator = ArticleAggregator()
    articles = aggregator.get_articles()
    
    print(f"\n{'='*70}")
    print(f"PULSDESK SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    articles_by_source = {}
    for article in articles:
        if article.source not in articles_by_source:
            articles_by_source[article.source] = []
        articles_by_source[article.source].append(article)
    
    for source, items in articles_by_source.items():
        print(f"\n{source.upper()} ({len(items)} articles)")
        print("-" * 70)
        for item in items[:3]:
            print(f"  {item.title[:60]}...")
            print(f"  {item.url}\n")