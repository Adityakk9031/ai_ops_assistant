"""GitHub API tool for repository search and details."""

import os
from typing import Dict, Any, List, Optional
import httpx
from tools.base_tool import ToolInterface, ToolResponse


class GitHubTool(ToolInterface):
    """Tool for interacting with GitHub API."""
    
    def __init__(self):
        super().__init__("GitHubTool")
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            self.logger.warning("GITHUB_TOKEN not set - API rate limits will be restricted")
        self.base_url = "https://api.github.com"
    
    def call(self, args: Dict[str, Any]) -> ToolResponse:
        """
        Execute GitHub API operations.
        
        Supported operations:
        - search_repos: Search for repositories
        - get_repo: Get details for a specific repository
        
        Args:
            args: Dictionary with 'operation' and operation-specific parameters
            
        Returns:
            ToolResponse with GitHub data
        """
        operation = args.get("operation", "search_repos")
        
        try:
            if operation == "search_repos":
                return self._search_repos(
                    query=args.get("query", ""),
                    per_page=args.get("per_page", 10),
                    sort=args.get("sort", "stars"),
                    order=args.get("order", "desc")
                )
            elif operation == "get_repo":
                return self._get_repo(
                    owner=args.get("owner", ""),
                    repo=args.get("repo", "")
                )
            elif operation == "get_repos_batch":
                return self._get_repos_batch(args.get("repo_list", []))
            else:
                return ToolResponse(ok=False, error=f"Unknown operation: {operation}")
        except Exception as e:
            return self._handle_error(e, f"GitHub API error ({operation})")
    
    def _search_repos(self, query: str, per_page: int = 10, 
                     sort: str = "stars", order: str = "desc") -> ToolResponse:
        """Search GitHub repositories."""
        if not query:
            return ToolResponse(ok=False, error="Query parameter is required")
        
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "per_page": min(per_page, 100),  # GitHub max is 100
            "sort": sort,
            "order": order
        }
        headers = self._get_headers()
        
        try:
            response = self._make_http_request("GET", url, params=params, headers=headers)
            data = response.json()
            
            # Extract relevant repo information
            repos = []
            for item in data.get("items", []):
                repos.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "owner": item.get("owner", {}).get("login"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language"),
                    "url": item.get("html_url"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at")
                })
            
            return ToolResponse(
                ok=True,
                status_code=response.status_code,
                data={
                    "repos": repos,
                    "total_count": data.get("total_count", 0)
                }
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                return ToolResponse(
                    ok=False,
                    status_code=403,
                    error="GitHub API rate limit exceeded. Please wait or add GITHUB_TOKEN."
                )
            raise
    
    def _get_repo(self, owner: str, repo: str) -> ToolResponse:
        """Get details for a specific repository."""
        if not owner or not repo:
            return ToolResponse(ok=False, error="Both owner and repo parameters are required")
        
        url = f"{self.base_url}/repos/{owner}/{repo}"
        headers = self._get_headers()
        
        try:
            response = self._make_http_request("GET", url, headers=headers)
            data = response.json()
            
            repo_data = {
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "owner": data.get("owner", {}).get("login"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "watchers": data.get("watchers_count"),
                "language": data.get("language"),
                "url": data.get("html_url"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "open_issues": data.get("open_issues_count"),
                "license": data.get("license", {}).get("name") if data.get("license") else None
            }
            
            return ToolResponse(
                ok=True,
                status_code=response.status_code,
                data={"repo": repo_data}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return ToolResponse(
                    ok=False,
                    status_code=404,
                    error=f"Repository {owner}/{repo} not found"
                )
            raise
    
    def _get_repos_batch(self, repo_list: List[str]) -> ToolResponse:
        """Get details for multiple repositories."""
        if not repo_list:
            return ToolResponse(ok=False, error="repo_list parameter is required")
        
        repos = []
        errors = []
        
        for repo_full_name in repo_list:
            parts = repo_full_name.split("/")
            if len(parts) != 2:
                errors.append(f"Invalid repo format: {repo_full_name}")
                continue
            
            owner, repo = parts
            result = self._get_repo(owner, repo)
            
            if result.ok:
                repos.append(result.data["repo"])
            else:
                errors.append(f"{repo_full_name}: {result.error}")
        
        return ToolResponse(
            ok=len(repos) > 0,
            status_code=200 if len(repos) > 0 else 400,
            data={
                "repos": repos,
                "errors": errors if errors else None
            }
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Ops-Assistant"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
