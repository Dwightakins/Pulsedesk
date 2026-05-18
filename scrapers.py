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
    category: str
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now()

class ScraperConfig:
    TIMEOUT = 20
    RETRIES = 3
    RETRY_DELAY = 2
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    SOURCES = {
        # ── Tech (3) ──────────────────────────────────
        'techcabal': {
            'url': 'https://techcabal.com',
            'selectors': {'article': 'article, div[class*="post"], div[class*="card"], div[class*="story"]', 'title': 'h1, h2, h3'},
            'category': 'Tech'
        },
        'techpoint': {
            'url': 'https://techpoint.africa',
            'selectors': {'article': 'article, div[class*="post"], div[class*="card"], div[class*="story"]', 'title': 'h1, h2, h3'},
            'category': 'Tech'
        },
        'technext': {
            'url': 'https://technext24.com',
            'selectors': {'article': 'article, div[class*="post"], div[class*="card"], div[class*="item"]', 'title': 'h1, h2, h3, h4'},
            'category': 'Tech'
        },
        
        # ── Business (3) ─────────────────────────────
        'businessday': {
            'url': 'https://businessday.ng',
            'selectors': {'article': 'article, div[class*="post"]', 'title': 'h2, h3'},
            'category': 'Business'
        },
        'guardian': {
            'url': 'https://guardian.ng/category/business-services/business/',
            'selectors': {'article': 'article, div[class*="post"], div[class*="entry"], div[class*="item"]', 'title': 'h2, h3, h4'},
            'category': 'Business'
        },
        'punch': {
            'url': 'https://punchng.com/topics/business/',
            'selectors': {'article': 'article, div[class*="post"], div[class*="entry"]', 'title': 'h2, h3'},
            'category': 'Business'
        },
        
        # ── Finance (3) ──────────────────────────────
        'nairametrics': {
            'url': 'https://nairametrics.com',
            'selectors': {'article': 'article', 'title': 'h2, h3'},
            'category': 'Finance'
        },
        'thecable_business': {
            'url': 'https://www.thecable.ng/business/',
            'selectors': {'article': 'article, div[class*="post"], div[class*="card"], div[class*="item"]', 'title': 'h2, h3, h4'},
            'category': 'Finance'
        },
        'premiumtimes_business': {
            'url': 'https://www.premiumtimesng.com/business',
            'selectors': {'article': 'article, div[class*="post"], div[class*="item"], div[class*="entry"]', 'title': 'h2, h3, h4'},
            'category': 'Finance'
        },
        
        # ── Entertainment (2) ────────────────────────
        'bellanaija': {
            'url': 'https://www.bellanaija.com',
            'selectors': {'article': 'article, div[class*="post"], div[class*="entry"], div[class*="item"], div[class*="card"]', 'title': 'h2, h3, h4'},
            'category': 'Entertainment'
        },
        'pulse': {
            'url': 'https://www.pulse.ng/entertainment',
            'selectors': {'article': 'article, div[class*="post"], div[class*="card"], div[class*="item"], div[class*="story"]', 'title': 'h2, h3, h4'},
            'category': 'Entertainment'
        },
    }


class BaseScraper:
    def __init__(self, source_key: str, config: Dict):
        self.source_key = source_key
        self.source_name = source_key.replace('_', ' ').title()
        self.url = config['url']
        self.selectors = config['selectors']
        self.category = config['category']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ScraperConfig.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
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
    
    def _get_base_domain(self) -> str:
        """Extract base domain from URL for normalizing links"""
        from urllib.parse import urlparse
        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _normalize_url(self, href: str) -> str:
        if not href or href.startswith('javascript') or href == '#' or href.startswith('mailto'):
            return None
        if href.startswith('http'):
            return href
        base = self._get_base_domain()
        return f"{base}/{href.lstrip('/')}"
    
    def _extract_articles(self, soup: BeautifulSoup) -> List[Article]:
        articles = []
        seen_titles = set()
        
        try:
            # Try article-level extraction first
            article_elements = soup.select(self.selectors['article'])[:12]
            
            for element in article_elements:
                title_elem = element.select_one(self.selectors['title'])
                link_elem = element.find('a', href=True)
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    href = link_elem.get('href')
                    
                    if title and len(title) > 10 and title not in seen_titles:
                        url = self._normalize_url(href)
                        if url:
                            seen_titles.add(title)
                            articles.append(Article(
                                title=title,
                                url=url,
                                source=self.source_name,
                                category=self.category
                            ))
            
            # Fallback: if article-level gave nothing, try title-level directly
            if not articles:
                title_elements = soup.select(self.selectors['title'])[:12]
                for elem in title_elements:
                    link = elem.find('a', href=True) or elem.find_parent('a', href=True)
                    if link:
                        title = elem.get_text(strip=True)
                        href = link.get('href')
                        if title and len(title) > 10 and title not in seen_titles:
                            url = self._normalize_url(href)
                            if url:
                                seen_titles.add(title)
                                articles.append(Article(
                                    title=title,
                                    url=url,
                                    source=self.source_name,
                                    category=self.category
                                ))
            
            logger.info(f"{self.source_name} [{self.category}]: Extracted {len(articles)} articles")
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
    
    def scrape_all(self, max_workers: int = 4) -> List[Article]:
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
        
        logger.info(f"Scrape complete: {len(all_articles)} total articles across {len(self.scrapers)} sources")
        return all_articles
    
    def get_articles(self) -> List[Article]:
        return self.scrape_all()


if __name__ == "__main__":
    aggregator = ArticleAggregator()
    articles = aggregator.get_articles()
    
    print(f"\n{'='*70}")
    print(f"PULSDESK SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    articles_by_category = {}
    for article in articles:
        if article.category not in articles_by_category:
            articles_by_category[article.category] = []
        articles_by_category[article.category].append(article)
    
    for category in ['Tech', 'Business', 'Finance', 'Entertainment']:
        items = articles_by_category.get(category, [])
        print(f"\n{category.upper()} ({len(items)} articles)")
        print("-" * 70)
        for item in items[:5]:
            print(f"  [{item.source}] {item.title[:55]}...")
            print(f"  {item.url}\n")
