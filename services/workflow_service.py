"""Workflow Service wrapping async LangGraph execution for FastAPI endpoints."""

import logging
from typing import Dict, Any
from workflow.graph import build_workflow_graph
from workflow.state import AgentState

logger = logging.getLogger("services.workflow_service")


class WorkflowService:
    """Service encapsulating LangGraph StateGraph workflow execution."""

    def __init__(self):
        self.graph = build_workflow_graph()

    async def run_task(self, user_task: str) -> Dict[str, Any]:
        """
        Execute a user task asynchronously through the compiled LangGraph workflow.
        
        Args:
            user_task: Task description from user
            
        Returns:
            Dictionary formatted for FastAPI SubmitResponse
        """
        logger.info(f"Initializing LangGraph workflow for task: '{user_task}'")
        
        initial_state: AgentState = {
            "user_task": user_task,
            "past_memory": [],
            "plan": None,
            "tool_results": [],
            "verification_status": None,
            "retry_count": 0,
            "error": None
        }

        # Invoke graph asynchronously
        final_state = await self.graph.ainvoke(initial_state)

        plan = final_state.get("plan") or {}
        executor_results = final_state.get("tool_results") or []
        verification = final_state.get("verification_status") or {}

        logger.info("LangGraph workflow execution completed successfully")
        return {
            "plan": plan,
            "executor_results": executor_results,
            "verification": verification
        }
