print("Step 1: starting")

try:
    from dotenv import load_dotenv
    print("Step 2: dotenv imported")
    load_dotenv()
    print("Step 3: dotenv loaded")
except Exception as e:
    print(f"FAILED at dotenv: {e}")

try:
    from scrapers import ArticleAggregator
    print("Step 4: scrapers imported")
except Exception as e:
    print(f"FAILED at scrapers: {e}")

try:
    from summarizer import ArticleSummarizer
    print("Step 5: summarizer imported")
except Exception as e:
    print(f"FAILED at summarizer: {e}")

print("Step 6: done")
