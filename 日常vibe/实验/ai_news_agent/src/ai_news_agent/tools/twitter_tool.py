from typing import Type, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS

class TwitterSearchInput(BaseModel):
    """Input for TwitterSearchTool"""
    query: str = Field(description="Search query or username to search for")
    max_results: int = Field(default=5, description="Maximum number of results to return")

class TwitterSearchTool(BaseModel):
    """Tool to search Twitter using DuckDuckGo"""
    name: str = "search_twitter"
    description: str = (
        "Search for recent tweets from specific users or about topics on Twitter/X. "
        "Useful for gathering latest updates from AI thought leaders."
    )
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """Execute the search"""
        try:
            # If query looks like a username (starts with @), convert to site search
            search_query = query
            if query.startswith("@"):
                username = query[1:]
                search_query = f"site:twitter.com from:{username} -inurl:replies"
            elif "twitter.com" not in query and "site:" not in query:
                search_query = f"site:twitter.com {query}"
                
            print(f"🔎 Searching Twitter: {search_query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    search_query, 
                    max_results=max_results,
                    timelimit="d"  # Past day
                ))
            
            if not results:
                return f"No recent tweets found for query: {query}"
            
            formatted_results = []
            for res in results:
                formatted_results.append(
                    f"- Title: {res.get('title')}\n"
                    f"  Link: {res.get('href')}\n"
                    f"  Snippet: {res.get('body')}\n"
                )
                
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"❌ Error searching Twitter: {str(e)}"

# Adapter for CrewAI
class CrewTwitterSearchTool(BaseTool):
    name: str = "search_twitter"
    description: str = (
        "Search for recent tweets from specific users or about topics on Twitter/X. "
        "Useful for gathering latest updates from AI thought leaders."
    )
    args_schema: Type[BaseModel] = TwitterSearchInput
    
    def _run(self, query: str, max_results: int = 5) -> str:
        tool = TwitterSearchTool()
        return tool._run(query, max_results)
