"""Tests for the Executor agent."""

import pytest
from agents.executor import Executor


def test_executor_runs_github_search():
    """Test that executor can run a GitHub search."""
    executor = Executor()
    
    # Create a simple plan
    plan = {
        "task_summary": "Search GitHub for Python repos",
        "steps": [
            {
                "id": 1,
                "title": "Search repos",
                "description": "Search for Python repositories",
                "tool": "GitHubTool",
                "inputs": {
                    "operation": "search_repos",
                    "query": "python web framework",
                    "per_page": 3
                },
                "expected_output_schema": {
                    "type": "object",
                    "required": ["repos"]
                },
                "retry": 2
            }
        ]
    }
    
    results = executor.execute_plan(plan)
    
    # Verify results
    assert len(results) == 1
    result = results[0]
    
    assert result["id"] == 1
    assert "tool_call" in result
    assert "tool_result" in result
    assert "success" in result
    assert "attempts" in result
    
    if result["success"]:
        print("✓ GitHub search executed successfully")
        tool_result = result["tool_result"]
        if tool_result.get("ok"):
            repos = tool_result.get("data", {}).get("repos", [])
            print(f"  Found {len(repos)} repositories")
    else:
        print(f"✗ Execution failed: {result.get('error')}")


def test_executor_runs_weather_query():
    """Test that executor can run a weather query."""
    executor = Executor()
    
    plan = {
        "task_summary": "Get weather",
        "steps": [
            {
                "id": 1,
                "title": "Get weather",
                "description": "Get current weather in Bangalore",
                "tool": "WeatherTool",
                "inputs": {
                    "operation": "current_weather",
                    "city": "Bangalore"
                },
                "expected_output_schema": {
                    "type": "object",
                    "required": ["temperature", "conditions"]
                },
                "retry": 1
            }
        ]
    }
    
    results = executor.execute_plan(plan)
    
    assert len(results) == 1
    result = results[0]
    
    if result["success"]:
        print("✓ Weather query executed successfully")
        tool_result = result["tool_result"]
        if tool_result.get("ok"):
            data = tool_result.get("data", {})
            print(f"  {data.get('city')}: {data.get('temperature')}°C, {data.get('conditions')}")
    else:
        print(f"✗ Execution failed: {result.get('error')}")


def test_executor_handles_invalid_tool():
    """Test that executor handles invalid tool gracefully."""
    executor = Executor()
    
    plan = {
        "task_summary": "Test invalid tool",
        "steps": [
            {
                "id": 1,
                "title": "Invalid tool",
                "description": "Test with non-existent tool",
                "tool": "NonExistentTool",
                "inputs": {},
                "expected_output_schema": {},
                "retry": 0
            }
        ]
    }
    
    results = executor.execute_plan(plan)
    
    assert len(results) == 1
    result = results[0]
    
    assert result["success"] is False
    assert "not found" in result["error"].lower()
    print("✓ Invalid tool handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
