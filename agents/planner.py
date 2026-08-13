"""Planner agent - creates execution plans from user tasks."""

import os
import json
import logging
from typing import Dict, Any
from pydantic import BaseModel, Field, ValidationError
from llm.gemini_client import GeminiClient, load_prompt_template

logger = logging.getLogger(__name__)


class StepSchema(BaseModel):
    """Schema for a single execution step."""
    id: int
    title: str
    description: str
    tool: str
    inputs: Dict[str, Any]
    expected_output_schema: Dict[str, Any]
    retry: int = Field(ge=0, le=5)


class PlanSchema(BaseModel):
    """Schema for the complete execution plan."""
    task_summary: str = Field(max_length=120)
    steps: list[StepSchema]
    supported_tools: list[Dict[str, str]]
    final_output_schema: Dict[str, Any]
    estimated_time_minutes: int


class Planner:
    """Planner agent that creates execution plans."""
    
    def __init__(self, prompt_file: str = None):
        if prompt_file is None:
            prompt_file = os.path.join(
                os.path.dirname(__file__), 
                "..", "llm", "prompts", "planner_prompt.json"
            )
        
        self.prompt_template = load_prompt_template(prompt_file)
        self.client = GeminiClient()
        self.logger = logging.getLogger("agent.planner")
    
    def create_plan(self, user_task: str, past_memory: list = None) -> Dict[str, Any]:
        """
        Create an execution plan for the given task.
        
        Args:
            user_task: The task description from the user
            past_memory: Optional list of past similar task memories retrieved from Pinecone
            
        Returns:
            Dictionary containing the execution plan
            
        Raises:
            ValueError: If plan generation or validation fails
        """
        self.logger.info(f"Creating plan for task: {user_task}")
        
        # Format the user prompt
        # Use replace() instead of format() because the template contains JSON curly braces
        user_prompt = self.prompt_template["user_template"].replace("{user_task}", user_task)
        
        # Inject past memory context if available
        if past_memory:
            memory_text = "\n\nPAST RELEVANT MEMORY (Retrieved from Pinecone vector store):\n"
            for i, mem in enumerate(past_memory, 1):
                memory_text += f"Past Memory #{i}:\n Task: {mem.get('task')}\n Summary: {mem.get('task_summary')}\n Plan Structure: {json.dumps(mem.get('plan', {}))}\n"
            memory_text += "\nINSTRUCTION: Use the past memory above to guide step creation, follow proven formats, and avoid repeating past errors."
            user_prompt += memory_text
            self.logger.info(f"Injected {len(past_memory)} past memories into Planner prompt")
        
        # Define validator
        def validate_plan(plan_json: Dict[str, Any]) -> bool:
            try:
                # Check for error response
                if "error" in plan_json:
                    self.logger.error(f"Planner returned error: {plan_json['error']}")
                    return False
                
                # Validate against Pydantic schema
                PlanSchema(**plan_json)
                return True
            except ValidationError as e:
                self.logger.error(f"Plan validation failed: {str(e)}")
                return False
        
        # Generate and validate plan
        try:
            plan = self.client.validate_and_retry_json(
                system_instruction=self.prompt_template["system_instruction"],
                user_prompt=user_prompt,
                validator=validate_plan,
                max_retries=2
            )
            
            self.logger.info(f"Successfully created plan with {len(plan.get('steps', []))} steps")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create plan: {str(e)}")
            raise ValueError(f"Plan generation failed: {str(e)}")
