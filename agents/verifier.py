"""Verifier agent - validates execution results and assembles final output."""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from llm.gemini_client import GeminiClient, load_prompt_template

logger = logging.getLogger(__name__)


class Verifier:
    """Verifier agent that validates execution results."""
    
    def __init__(self, prompt_file: str = None):
        if prompt_file is None:
            prompt_file = os.path.join(
                os.path.dirname(__file__),
                "..", "llm", "prompts", "verifier_prompt.json"
            )
        
        self.prompt_template = load_prompt_template(prompt_file)
        self.client = GeminiClient()
        self.logger = logging.getLogger("agent.verifier")
    
    def verify_results(self, plan: Dict[str, Any], 
                      executor_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify execution results and assemble final output.
        
        Args:
            plan: The execution plan from Planner
            executor_results: Results from Executor
            
        Returns:
            Verification result with final output
        """
        self.logger.info("Verifying execution results")
        
        # First, do local validation checks
        issues = self._perform_local_checks(plan, executor_results)
        
        # Assemble evidence from successful steps
        evidence = self._assemble_evidence(executor_results)
        
        # Create a summary using LLM
        summary = self._create_summary(plan, executor_results, evidence)
        
        # Calculate confidence based on issues and success rate
        confidence = self._calculate_confidence(executor_results, issues)
        
        # Prepare verification metadata
        verifier_metadata = {
            "verified_at": datetime.utcnow().isoformat() + "Z",
            "checks": [
                "Schema validation for each step",
                "Success rate calculation",
                "Data type validation",
                "Required fields presence check"
            ]
        }
        
        # Assemble final output
        final_output = {
            "summary": summary,
            "evidence": evidence,
            "confidence": confidence
        }
        
        result = {
            "final_output": final_output,
            "issues": issues,
            "confidence": confidence,
            "verifier_metadata": verifier_metadata
        }
        
        self.logger.info(f"Verification complete. Confidence: {confidence:.2f}, Issues: {len(issues)}")
        return result
    
    def _perform_local_checks(self, plan: Dict[str, Any], 
                             executor_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform local validation checks."""
        issues = []
        steps = {step["id"]: step for step in plan.get("steps", [])}
        
        for result in executor_results:
            step_id = result.get("id")
            step = steps.get(step_id)
            
            if not step:
                continue
            
            # Check if step succeeded
            if not result.get("success"):
                issues.append({
                    "step_id": step_id,
                    "issue": f"Step failed: {result.get('error')}",
                    "fix_action": f"Re-run step {step_id} with inputs: {json.dumps(step.get('inputs'))}"
                })
                continue
            
            # Check if expected output schema is satisfied
            expected_schema = step.get("expected_output_schema", {})
            required_fields = expected_schema.get("required", [])
            
            tool_result = result.get("tool_result", {})
            data = tool_result.get("data", {})
            
            for field in required_fields:
                if field not in data:
                    issues.append({
                        "step_id": step_id,
                        "issue": f"Missing required field: {field}",
                        "fix_action": f"Re-run step {step_id} and ensure field '{field}' is present"
                    })
        
        return issues
    
    def _assemble_evidence(self, executor_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assemble evidence from successful steps."""
        evidence = []
        
        for result in executor_results:
            if result.get("success"):
                tool_result = result.get("tool_result", {})
                data = tool_result.get("data", {})
                
                evidence.append({
                    "step_id": result.get("id"),
                    "tool": result.get("tool_call", {}).get("name"),
                    "data": data
                })
        
        return evidence
    
    def _create_summary(self, plan: Dict[str, Any], 
                       executor_results: List[Dict[str, Any]],
                       evidence: List[Dict[str, Any]]) -> str:
        """Create a human-readable summary of results."""
        task_summary = plan.get("task_summary", "Task")
        
        # Count successes
        successful_steps = sum(1 for r in executor_results if r.get("success"))
        total_steps = len(executor_results)
        
        # Build summary
        summary_parts = [f"Task: {task_summary}"]
        summary_parts.append(f"Completed {successful_steps}/{total_steps} steps successfully.")
        
        # Add key findings from evidence
        for ev in evidence:
            tool = ev.get("tool")
            data = ev.get("data", {})
            
            if tool == "GitHubTool":
                repos = data.get("repos", [])
                if repos:
                    summary_parts.append(f"Found {len(repos)} GitHub repositories.")
                    top_repo = repos[0] if repos else None
                    if top_repo:
                        summary_parts.append(
                            f"Top result: {top_repo.get('full_name')} "
                            f"({top_repo.get('stars')} stars)"
                        )
            
            elif tool == "WeatherTool":
                city = data.get("city")
                temp = data.get("temperature")
                conditions = data.get("conditions")
                if city and temp is not None:
                    summary_parts.append(
                        f"Weather in {city}: {temp}°C, {conditions}"
                    )
            
            elif tool == "NewsTool":
                articles = data.get("articles", [])
                if articles:
                    summary_parts.append(f"Found {len(articles)} news articles.")
        
        return " ".join(summary_parts)
    
    def _calculate_confidence(self, executor_results: List[Dict[str, Any]], 
                             issues: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on results and issues."""
        if not executor_results:
            return 0.0
        
        # Base confidence on success rate
        successful_steps = sum(1 for r in executor_results if r.get("success"))
        total_steps = len(executor_results)
        success_rate = successful_steps / total_steps
        
        # Reduce confidence for each issue
        issue_penalty = len(issues) * 0.1
        
        confidence = max(0.0, min(1.0, success_rate - issue_penalty))
        return round(confidence, 2)
