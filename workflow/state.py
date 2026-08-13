"""State definition for LangGraph workflow."""

from typing import TypedDict, Dict, Any, List, Optional


class AgentState(TypedDict):
    """TypedDict representing the state passed through the LangGraph workflow."""
    user_task: str
    past_memory: List[Dict[str, Any]]
    plan: Optional[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    verification_status: Optional[Dict[str, Any]]
    retry_count: int
    error: Optional[str]
