from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

class RSSFetchToolInput(BaseModel):
    """Input schema for RSSFetchTool."""
    pass

class RSSFetchTool(BaseTool):
    name: str = "fetch_deep_content_feeds"
    description: str = (
        "Fetches the latest articles from a curated list of high-quality, deep-tech blogs "
        "(e.g., Simon Willison, Andrej Karpathy, Dan Luu). "
        "Returns a list of articles published in the last 48 hours with their full text or summaries."
    )
    args_schema: Type[BaseModel] = RSSFetchToolInput

    def _run(self) -> str:
        # Curated High-Signal Feeds (The "Anti-Slop" List)
        feeds = [
            "https://simonwillison.net/atom/entries/", # Simon Willison
            "https://karpathy.github.io/feed.xml",     # Andrej Karpathy
            "https://openai.com/index.xml",            # OpenAI (Updated URL if needed, often changes) - let's try standard
            "https://openai.com/blog/rss.xml",
            "https://www.anthropic.com/feed",          # Anthropic
            "https://stratechery.com/feed/",           # Stratechery (Ben Thompson)
            "https://gwern.net/feed",                  # Gwern Branwen
            "https://danluu.com/atom.xml",             # Dan Luu
            "https://jvns.ca/atom.xml",                # Julia Evans
            "https://lethain.com/feeds.xml",           # Will Larson
            "https://lilianweng.github.io/index.xml",  # Lilian Weng
            "https://jalammar.github.io/feed.xml",     # Jay Alammar
            "https://applied-llms.org/feed.xml",       # Eugene Yan
        ]

        collected_articles = []
        # Look back 48 hours to ensure we catch "daily" deep dives even if posted yesterday
        cutoff_date = datetime.now() - timedelta(hours=48)

        for feed_url in feeds:
            try:
                # Set a user agent
                feed = feedparser.parse(feed_url, agent="Mozilla/5.0 (compatible; AI_News_Agent/1.0)")
                
                if feed.bozo:
                    continue # Skip broken feeds

                for entry in feed.entries:
                    # Parse date
                    published = None
                    if hasattr(entry, 'published_parsed'):
                        published = entry.published_parsed
                    elif hasattr(entry, 'updated_parsed'):
                        published = entry.updated_parsed
                    
                    if published:
                        dt = datetime.fromtimestamp(time.mktime(published))
                        if dt > cutoff_date:
                            # Extract content (summary or content)
                            content = ""
                            if hasattr(entry, 'content'):
                                content = entry.content[0].value
                            elif hasattr(entry, 'summary'):
                                content = entry.summary
                            
                            # Clean HTML
                            soup = BeautifulSoup(content, 'html.parser')
                            text_content = soup.get_text()[:3000] # Truncate to avoid context limit overflow

                            collected_articles.append({
                                "source": feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else "Unknown Blog",
                                "title": entry.title,
                                "link": entry.link,
                                "date": dt.strftime("%Y-%m-%d"),
                                "content_snippet": text_content
                            })
            except Exception as e:
                print(f"Error fetching {feed_url}: {e}")
                continue

        if not collected_articles:
            return "No deep content articles found in the last 48 hours from the watched feeds."

        # Format output
        output = "Recent Deep Content Articles:\n\n"
        for article in collected_articles:
            output += f"Source: {article['source']}\n"
            output += f"Title: {article['title']}\n"
            output += f"Link: {article['link']}\n"
            output += f"Content Snippet: {article['content_snippet']}...\n"
            output += "-" * 50 + "\n"

        return output
