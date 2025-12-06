import asyncio
import aiohttp
import feedparser
import hashlib
import json
import os
import logging
from typing import List, Dict, Tuple, Optional

from config import NEWS_SOURCES, IMPORTANT_KEYWORDS, URGENT_KEYWORDS

logger = logging.getLogger(__name__)

SEEN_NEWS_FILE = "seen_news.json"


class NewsTracker:
    def __init__(self):
        self.seen_hashes = set()
        self.load()
    
    def load(self):
        try:
            if os.path.exists(SEEN_NEWS_FILE):
                with open(SEEN_NEWS_FILE, "r") as f:
                    data = json.load(f)
                    self.seen_hashes = set(data.get("hashes", []))
        except:
            pass
    
    def save(self):
        try:
            with open(SEEN_NEWS_FILE, "w") as f:
                hashes_list = list(self.seen_hashes)[-1000:]
                json.dump({"hashes": hashes_list}, f)
        except:
            pass
    
    def get_hash(self, title: str) -> str:
        return hashlib.md5(title.encode()).hexdigest()
    
    def is_seen(self, title: str) -> bool:
        return self.get_hash(title) in self.seen_hashes
    
    def mark_seen(self, title: str):
        self.seen_hashes.add(self.get_hash(title))
        self.save()


tracker = NewsTracker()


async def fetch_rss(source: Dict, session: aiohttp.ClientSession) -> List[Dict]:
    articles = []
    try:
        async with session.get(source["url"], timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                
                for entry in feed.entries[:10]:
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    
                    if title and not tracker.is_seen(title):
                        articles.append({
                            "title": title,
                            "link": link,
                            "source": source["name"],
                            "language": source["language"],
                        })
    except Exception as e:
        logger.warning(f"Error fetching RSS {source['name']}: {e}")
    
    return articles


async def fetch_all_news() -> List[Dict]:
    all_articles = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rss(source, session) for source in NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
    
    logger.info(f"Fetched {len(all_articles)} total articles from all sources")
    return all_articles


def calculate_importance(article: Dict) -> int:
    score = 0
    title_lower = article["title"].lower()
    
    for keyword in URGENT_KEYWORDS:
        if keyword.lower() in title_lower:
            score += 50
    
    for keyword in IMPORTANT_KEYWORDS:
        if keyword.lower() in title_lower:
            score += 10
    
    if article["source"] in ["Times of Israel", "Jerusalem Post"]:
        score += 5
    
    return score


def filter_new_important_news(articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    urgent = []
    important = []
    
    for article in articles:
        score = calculate_importance(article)
        article["score"] = score
        
        if score >= 50:
            urgent.append(article)
        elif score >= 20:
            important.append(article)
    
    urgent.sort(key=lambda x: x["score"], reverse=True)
    important.sort(key=lambda x: x["score"], reverse=True)
    
    return urgent, important


async def check_for_news() -> Tuple[Optional[Dict], List[Dict]]:
    articles = await fetch_all_news()
    urgent, important = filter_new_important_news(articles)
    
    logger.info(f"Found {len(urgent)} urgent, {len(important)} important news")
    
    for article in urgent + important:
        tracker.mark_seen(article["title"])
    
    return urgent[0] if urgent else None, important[:5]


def format_news_for_generation(articles: List[Dict]) -> str:
    if not articles:
        return ""
    
    lines = []
    for i, article in enumerate(articles[:5], 1):
        lines.append(f"{i}. [{article['source']}] {article['title']}")
    
    return "\n".join(lines)
