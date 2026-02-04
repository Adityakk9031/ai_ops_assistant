"""News API tool for fetching news articles."""

import os
from typing import Dict, Any
from tools.base_tool import ToolInterface, ToolResponse


class NewsTool(ToolInterface):
    """Tool for fetching news from NewsAPI."""
    
    def __init__(self):
        super().__init__("NewsTool")
        self.api_key = os.getenv("NEWSAPI_KEY")
        if not self.api_key:
            self.logger.warning("NEWSAPI_KEY not set")
        self.base_url = "https://newsapi.org/v2"
    
    def call(self, args: Dict[str, Any]) -> ToolResponse:
        """
        Execute news API operations.
        
        Supported operations:
        - search_news: Search for news articles
        - top_headlines: Get top headlines
        
        Args:
            args: Dictionary with 'operation' and operation-specific parameters
            
        Returns:
            ToolResponse with news data
        """
        operation = args.get("operation", "search_news")
        
        try:
            if operation == "search_news":
                return self._search_news(
                    query=args.get("query", ""),
                    language=args.get("language", "en"),
                    page_size=args.get("page_size", 10)
                )
            elif operation == "top_headlines":
                return self._get_top_headlines(
                    category=args.get("category"),
                    country=args.get("country", "us"),
                    page_size=args.get("page_size", 10)
                )
            else:
                return ToolResponse(ok=False, error=f"Unknown operation: {operation}")
        except Exception as e:
            return self._handle_error(e, f"News API error ({operation})")
    
    def _search_news(self, query: str, language: str = "en", page_size: int = 10) -> ToolResponse:
        """Search for news articles."""
        if not query:
            return ToolResponse(ok=False, error="Query parameter is required")
        
        if not self.api_key:
            return ToolResponse(ok=False, error="NEWSAPI_KEY not configured")
        
        url = f"{self.base_url}/everything"
        params = {
            "q": query,
            "apiKey": self.api_key,
            "language": language,
            "pageSize": min(page_size, 100),  # API max is 100
            "sortBy": "relevancy"
        }
        
        try:
            response = self._make_http_request("GET", url, params=params)
            data = response.json()
            
            articles = []
            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "source": item.get("source", {}).get("name"),
                    "author": item.get("author"),
                    "url": item.get("url"),
                    "published_at": item.get("publishedAt"),
                    "content": item.get("content")
                })
            
            return ToolResponse(
                ok=True,
                status_code=response.status_code,
                data={
                    "articles": articles,
                    "total_results": data.get("totalResults", 0)
                }
            )
        except Exception as e:
            if "401" in str(e):
                return ToolResponse(
                    ok=False,
                    status_code=401,
                    error="Invalid NewsAPI key"
                )
            raise
    
    def _get_top_headlines(self, category: str = None, country: str = "us", 
                          page_size: int = 10) -> ToolResponse:
        """Get top headlines."""
        if not self.api_key:
            return ToolResponse(ok=False, error="NEWSAPI_KEY not configured")
        
        url = f"{self.base_url}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": country,
            "pageSize": min(page_size, 100)
        }
        
        if category:
            params["category"] = category
        
        try:
            response = self._make_http_request("GET", url, params=params)
            data = response.json()
            
            articles = []
            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "source": item.get("source", {}).get("name"),
                    "author": item.get("author"),
                    "url": item.get("url"),
                    "published_at": item.get("publishedAt"),
                    "content": item.get("content")
                })
            
            return ToolResponse(
                ok=True,
                status_code=response.status_code,
                data={
                    "articles": articles,
                    "total_results": data.get("totalResults", 0)
                }
            )
        except Exception as e:
            if "401" in str(e):
                return ToolResponse(
                    ok=False,
                    status_code=401,
                    error="Invalid NewsAPI key"
                )
            raise
