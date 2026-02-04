"""Base tool interface for all tools in the AI Operations Assistant."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolResponse:
    """Standardized tool response wrapper."""
    
    def __init__(self, ok: bool, status_code: Optional[int] = None, 
                 data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.ok = ok
        self.status_code = status_code
        self.data = data or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "ok": self.ok,
            "status_code": self.status_code
        }
        if self.ok:
            result["data"] = self.data
        else:
            result["error"] = self.error
        return result


class ToolInterface(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    def call(self, args: Dict[str, Any]) -> ToolResponse:
        """
        Execute the tool with given arguments.
        
        Args:
            args: Dictionary of arguments for the tool
            
        Returns:
            ToolResponse object with standardized format
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True
    )
    def _make_http_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make HTTP request with automatic retry and exponential backoff.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments for httpx request
            
        Returns:
            httpx.Response object
        """
        self.logger.info(f"Making {method} request to {url}")
        with httpx.Client(timeout=30.0) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
    
    def _handle_error(self, error: Exception, context: str = "") -> ToolResponse:
        """
        Handle errors and return standardized error response.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            
        Returns:
            ToolResponse with error information
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg)
        
        status_code = None
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
        
        return ToolResponse(ok=False, status_code=status_code, error=error_msg)
