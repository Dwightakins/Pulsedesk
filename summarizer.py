import requests as http
from typing import List, Optional
from dataclasses import dataclass
import logging
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-120b"
BATCH_SIZE = 10          # articles per request, keeps each call small
PAUSE_BETWEEN_BATCHES = 20  # seconds, stays under the free tokens-per-minute limit

@dataclass
class Summary:
    title: str
    brief: str
    source: str
    relevance_score: float
    url: str

class ArticleSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment or parameters")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = os.getenv('GROQ_MODEL') or DEFAULT_MODEL
    
    def _build_system_prompt(self) -> str:
        return """You are a business intelligence summarizer for Nigerian and African tech/art markets.

Your job:
1. Read articles about business, tech, and art in Nigeria/Africa
2. Extract the MOST IMPORTANT takeaway (1-2 sentences, clear and actionable)
3. Rate relevance (0-1) for a founder/executive
4. Be selective - not everything matters

Return ONLY a valid JSON array of objects like this:
[
    {
        "title": "original article title",
        "brief": "1-2 sentence summary of what matters",
        "source": "source name",
        "relevance_score": 0.85,
        "url": "article url"
    }
]

High relevance: actionable insights, market moves, competitive threats, opportunities
Low relevance: generic news, announcements without context

Return ONLY the JSON array. No markdown, no explanation, no code blocks."""
    
    def _format_articles(self, articles: List) -> str:
        formatted = "Process and summarize these articles:\n\n"
        for i, article in enumerate(articles, 1):
            formatted += f"{i}. Title: {article.title}\n"
            formatted += f"   Source: {article.source}\n"
            formatted += f"   URL: {article.url}\n\n"
        return formatted
    
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Direct API call to Groq (OpenAI-compatible), retries on 429"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3
        }

        for attempt in range(4):
            response = http.post(
                GROQ_API_URL,
                headers=self.headers,
                json=payload,
                timeout=90
            )
            if response.status_code == 429 and attempt < 3:
                try:
                    wait = int(float(response.headers.get("Retry-After", 15 * (attempt + 1))))
                except ValueError:
                    wait = 15 * (attempt + 1)
                wait = max(1, min(wait, 60))
                logger.warning(f"Groq 429, retrying in {wait}s (attempt {attempt + 1}/3)")
                time.sleep(wait)
                continue
            break

        if response.status_code != 200:
            raise Exception(f"Groq API error {response.status_code}: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _parse_summaries(self, response_text: str) -> List[Summary]:
        """Pull the JSON array out of the model reply and build Summary objects"""
        clean = (response_text or "").strip()
        start, end = clean.find("["), clean.rfind("]")
        if start == -1 or end <= start:
            logger.warning("Model reply had no JSON array")
            return []

        try:
            items = json.loads(clean[start:end + 1])
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse model reply as JSON: {e}")
            return []

        summaries = []
        for data in items if isinstance(items, list) else []:
            if not isinstance(data, dict):
                continue
            try:
                score = float(data.get('relevance_score', 0))
            except (TypeError, ValueError):
                score = 0.0
            summaries.append(Summary(
                title=str(data.get('title', '')),
                brief=str(data.get('brief', '')),
                source=str(data.get('source', '')),
                relevance_score=score,
                url=str(data.get('url', ''))
            ))
        return summaries

    def summarize_batch(self, articles: List) -> List[Summary]:
        """Summarize articles with Groq, in small groups so one bad reply cannot sink the run"""
        if not articles:
            logger.warning("No articles to summarize")
            return []

        system_prompt = self._build_system_prompt()
        chunks = [articles[i:i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]
        logger.info(f"Summarizing {len(articles)} articles with Groq ({self.model}) in {len(chunks)} batch(es)...")

        summaries = []
        for n, chunk in enumerate(chunks, 1):
            if n > 1:
                time.sleep(PAUSE_BETWEEN_BATCHES)
            try:
                response_text = self._call_llm(
                    system_prompt,
                    self._format_articles(chunk) + "\n\nReturn the JSON array now."
                )
                batch = self._parse_summaries(response_text)
                logger.info(f"Batch {n}/{len(chunks)}: {len(batch)} summaries from {len(chunk)} articles")
                summaries.extend(batch)
            except Exception as e:
                logger.error(f"Batch {n}/{len(chunks)} failed: {str(e)}")

        logger.info(f"Generated {len(summaries)} summaries from {len(articles)} articles")
        return summaries

    def filter_by_relevance(self, summaries: List[Summary], threshold: float = 0.6) -> List[Summary]:
        filtered = [s for s in summaries if s.relevance_score >= threshold]
        logger.info(f"Filtered to {len(filtered)} high-relevance articles (threshold: {threshold})")
        return filtered
    
    def sort_by_relevance(self, summaries: List[Summary]) -> List[Summary]:
        return sorted(summaries, key=lambda x: x.relevance_score, reverse=True)


if __name__ == "__main__":
    from scrapers import ArticleAggregator
    
    print("Starting PulseDesk summarizer...")
    
    aggregator = ArticleAggregator()
    articles = aggregator.get_articles()
    print(f"Articles scraped: {len(articles)}")
    
    if articles:
        try:
            summarizer = ArticleSummarizer()
            summaries = summarizer.summarize_batch(articles)
            
            filtered = summarizer.filter_by_relevance(summaries, threshold=0.6)
            sorted_summaries = summarizer.sort_by_relevance(filtered)
            
            print(f"\n{'='*75}")
            print(f"PULSDESK - DAILY DIGEST PREVIEW")
            print(f"{'='*75}\n")
            
            for i, summary in enumerate(sorted_summaries[:5], 1):
                print(f"{i}. [{summary.source}]")
                print(f"   {summary.title}")
                print(f"   > {summary.brief}")
                print(f"   Relevance: {summary.relevance_score:.0%}")
                print(f"   {summary.url}\n")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("No articles found to summarize")
