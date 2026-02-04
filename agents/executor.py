"""Executor agent - executes plans by calling tools."""

import logging
from typing import Dict, Any, List
from tools import GitHubTool, WeatherTool, NewsTool
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class Executor:
    """Executor agent that runs plan steps using tools."""
    
    def __init__(self):
        # Initialize all available tools
        self.tools = {
            "GitHubTool": GitHubTool(),
            "WeatherTool": WeatherTool(),
            "NewsTool": NewsTool()
        }
        self.logger = logging.getLogger("agent.executor")
    
    def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a plan by running each step.
        
        Args:
            plan: The execution plan from Planner
            
        Returns:
            List of step results
        """
        self.logger.info(f"Executing plan: {plan.get('task_summary', 'Unknown task')}")
        
        steps = plan.get("steps", [])
        results = []
        
        for step in steps:
            result = self._execute_step(step)
            results.append(result)
            
            # Log step completion
            if result["success"]:
                self.logger.info(f"Step {step['id']} completed successfully")
            else:
                self.logger.warning(f"Step {step['id']} failed: {result.get('error')}")
        
        return results
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step.
        
        Args:
            step: Step definition from plan
            
        Returns:
            Step result dictionary
        """
        step_id = step.get("id")
        tool_name = step.get("tool")
        inputs = step.get("inputs", {})
        max_retries = step.get("retry", 0)
        
        self.logger.info(f"Executing step {step_id}: {step.get('title')}")
        
        # Get the tool
        tool = self.tools.get(tool_name)
        if not tool:
            return {
                "id": step_id,
                "tool_call": {"name": tool_name, "args": inputs},
                "tool_result": {},
                "success": False,
                "attempts": 0,
                "error": f"Tool '{tool_name}' not found"
            }
        
        # Execute with retry logic
        attempts = 0
        last_error = None
        
        for attempt in range(max_retries + 1):
            attempts += 1
            try:
                # Call the tool
                response = tool.call(inputs)
                
                if response.ok:
                    return {
                        "id": step_id,
                        "tool_call": {"name": tool_name, "args": inputs},
                        "tool_result": response.to_dict(),
                        "success": True,
                        "attempts": attempts,
                        "error": None
                    }
                else:
                    last_error = response.error
                    if attempt < max_retries:
                        self.logger.warning(
                            f"Step {step_id} attempt {attempt + 1} failed: {last_error}. Retrying..."
                        )
                        # Exponential backoff
                        import time
                        time.sleep(2 ** attempt)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    self.logger.warning(
                        f"Step {step_id} attempt {attempt + 1} raised exception: {last_error}. Retrying..."
                    )
                    import time
                    time.sleep(2 ** attempt)
        
        # All retries exhausted
        return {
            "id": step_id,
            "tool_call": {"name": tool_name, "args": inputs},
            "tool_result": {},
            "success": False,
            "attempts": attempts,
            "error": last_error or "Unknown error"
        }
    
    def execute_step_by_id(self, plan: Dict[str, Any], step_id: int) -> Dict[str, Any]:
        """
        Execute a specific step by ID (for re-execution).
        
        Args:
            plan: The execution plan
            step_id: ID of the step to execute
            
        Returns:
            Step result dictionary
        """
        steps = plan.get("steps", [])
        for step in steps:
            if step.get("id") == step_id:
                return self._execute_step(step)
        
        return {
            "id": step_id,
            "tool_call": {},
            "tool_result": {},
            "success": False,
            "attempts": 0,
            "error": f"Step {step_id} not found in plan"
        }
