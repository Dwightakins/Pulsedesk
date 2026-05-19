import requests as http
from typing import List, Optional
from dataclasses import dataclass
import logging
import json
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

@dataclass
class Summary:
    title: str
    brief: str
    source: str
    relevance_score: float
    url: str

class ArticleSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment or parameters")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "mistral-large-latest"
    
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
    
    def _call_mistral(self, system_prompt: str, user_message: str) -> str:
        """Direct API call to Mistral, no SDK needed"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3
        }
        
        response = http.post(
            MISTRAL_API_URL,
            headers=self.headers,
            json=payload,
            timeout=90
        )
        
        if response.status_code != 200:
            raise Exception(f"Mistral API error {response.status_code}: {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def summarize_batch(self, articles: List) -> List[Summary]:
        """Summarize batch of articles using Mistral API"""
        if not articles:
            logger.warning("No articles to summarize")
            return []
        
        summaries = []
        
        try:
            system_prompt = self._build_system_prompt()
            formatted_articles = self._format_articles(articles)
            
            logger.info(f"Summarizing {len(articles)} articles with Mistral...")
            
            response_text = self._call_mistral(
                system_prompt,
                formatted_articles + "\n\nReturn the JSON array now."
            )
            
            # Clean response - remove markdown code blocks if present
            clean = response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1]
            if clean.endswith("```"):
                clean = clean.rsplit("```", 1)[0]
            clean = clean.strip()
            
            # Parse JSON array
            try:
                articles_data = json.loads(clean)
                if isinstance(articles_data, list):
                    for data in articles_data:
                        summary = Summary(
                            title=data.get('title', ''),
                            brief=data.get('brief', ''),
                            source=data.get('source', ''),
                            relevance_score=float(data.get('relevance_score', 0)),
                            url=data.get('url', '')
                        )
                        summaries.append(summary)
            except json.JSONDecodeError:
                # Fallback: try line by line
                for line in clean.split('\n'):
                    line = line.strip().rstrip(',')
                    if not line or line in ['[', ']']:
                        continue
                    try:
                        data = json.loads(line)
                        summary = Summary(
                            title=data.get('title', ''),
                            brief=data.get('brief', ''),
                            source=data.get('source', ''),
                            relevance_score=float(data.get('relevance_score', 0)),
                            url=data.get('url', '')
                        )
                        summaries.append(summary)
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"Generated {len(summaries)} summaries from {len(articles)} articles")
            return summaries
        
        except Exception as e:
            logger.error(f"Error summarizing with Mistral: {str(e)}")
            return []
    
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
        