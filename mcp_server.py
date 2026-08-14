"""MCP Server for AI Operations Assistant tools using FastMCP and stdio transport."""

import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool
from tools.news_tool import NewsTool

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("AIOpsAssistantTools")

# Instantiate underlying tools
github_tool_instance = GitHubTool()
weather_tool_instance = WeatherTool()
news_tool_instance = NewsTool()


@mcp.tool()
def github_search_repos(query: str, per_page: int = 10, sort: str = "stars", order: str = "desc") -> Dict[str, Any]:
    """Search GitHub repositories matching a query string."""
    response = github_tool_instance.call({
        "operation": "search_repos",
        "query": query,
        "per_page": per_page,
        "sort": sort,
        "order": order
    })
    return response.to_dict()


@mcp.tool()
def github_get_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Get detailed information for a specific GitHub repository."""
    response = github_tool_instance.call({
        "operation": "get_repo",
        "owner": owner,
        "repo": repo
    })
    return response.to_dict()


@mcp.tool()
def github_get_repos_batch(repo_list: List[str]) -> Dict[str, Any]:
    """Get details for multiple GitHub repositories at once."""
    response = github_tool_instance.call({
        "operation": "get_repos_batch",
        "repo_list": repo_list
    })
    return response.to_dict()


@mcp.tool()
def weather_current(city: str, units: str = "metric") -> Dict[str, Any]:
    """Get current weather conditions for a specified city."""
    response = weather_tool_instance.call({
        "operation": "current_weather",
        "city": city,
        "units": units
    })
    return response.to_dict()


@mcp.tool()
def weather_forecast(city: str, units: str = "metric", cnt: int = 5) -> Dict[str, Any]:
    """Get weather forecast for a specified city."""
    response = weather_tool_instance.call({
        "operation": "forecast",
        "city": city,
        "units": units,
        "cnt": cnt
    })
    return response.to_dict()


@mcp.tool()
def news_search(query: str, language: str = "en", page_size: int = 10) -> Dict[str, Any]:
    """Search news articles matching a keyword query."""
    response = news_tool_instance.call({
        "operation": "search_news",
        "query": query,
        "language": language,
        "page_size": page_size
    })
    return response.to_dict()


@mcp.tool()
def news_top_headlines(category: Optional[str] = None, country: str = "us", page_size: int = 10) -> Dict[str, Any]:
    """Get top headlines by category or country."""
    args = {
        "operation": "top_headlines",
        "country": country,
        "page_size": page_size
    }
    if category:
        args["category"] = category
    response = news_tool_instance.call(args)
    return response.to_dict()


if __name__ == "__main__":
    mcp.run(transport="stdio")
