import os
from dotenv import load_dotenv

print("1. Testing imports...")

try:
    load_dotenv()
    print("✓ dotenv loaded")
except Exception as e:
    print(f"✗ dotenv error: {e}")

try:
    from mistralai import Mistral
    print("✓ mistralai imported")
except Exception as e:
    print(f"✗ mistralai error: {e}")

try:
    from scrapers import ArticleAggregator
    print("✓ scrapers imported")
except Exception as e:
    print(f"✗ scrapers error: {e}")

print(f"\n2. Checking .env...")
api_key = os.getenv('MISTRAL_API_KEY')
print(f"MISTRAL_API_KEY exists: {api_key is not None}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")

print("\n3. Testing scraper...")
try:
    agg = ArticleAggregator()
    articles = agg.get_articles()
    print(f"✓ Articles scraped: {len(articles)}")
except Exception as e:
    print(f"✗ Scraper error: {e}")
    import traceback
    traceback.print_exc()