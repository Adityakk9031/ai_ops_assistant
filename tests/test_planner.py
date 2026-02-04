"""Tests for the Planner agent."""

import pytest
import json
from agents.planner import Planner


def test_planner_creates_valid_plan():
    """Test that planner creates a valid plan for a simple task."""
    planner = Planner()
    
    task = "Find the top 3 Python web frameworks on GitHub with more than 5000 stars"
    
    try:
        plan = planner.create_plan(task)
        
        # Verify plan structure
        assert "task_summary" in plan
        assert "steps" in plan
        assert "supported_tools" in plan
        assert "final_output_schema" in plan
        assert "estimated_time_minutes" in plan
        
        # Verify steps
        assert len(plan["steps"]) > 0
        
        for step in plan["steps"]:
            assert "id" in step
            assert "title" in step
            assert "description" in step
            assert "tool" in step
            assert "inputs" in step
            assert "expected_output_schema" in step
            assert "retry" in step
            assert 0 <= step["retry"] <= 5
        
        print(f"✓ Plan created successfully with {len(plan['steps'])} steps")
        print(f"  Task summary: {plan['task_summary']}")
        
    except Exception as e:
        pytest.fail(f"Planner failed: {str(e)}")


def test_planner_handles_weather_task():
    """Test that planner can handle weather-related tasks."""
    planner = Planner()
    
    task = "Get the current weather in Bangalore"
    
    try:
        plan = planner.create_plan(task)
        
        # Verify plan contains weather tool
        tools_used = [step["tool"] for step in plan["steps"]]
        assert "WeatherTool" in tools_used
        
        print(f"✓ Weather task plan created successfully")
        
    except Exception as e:
        pytest.fail(f"Planner failed: {str(e)}")


def test_planner_handles_complex_task():
    """Test that planner can handle complex multi-tool tasks."""
    planner = Planner()
    
    task = "Find top 3 Python web frameworks on GitHub with > 5k stars and current weather in Bangalore, then create a summary"
    
    try:
        plan = planner.create_plan(task)
        
        # Verify plan uses multiple tools
        tools_used = set(step["tool"] for step in plan["steps"])
        assert len(tools_used) >= 2  # Should use at least 2 different tools
        
        print(f"✓ Complex task plan created with {len(tools_used)} different tools")
        
    except Exception as e:
        pytest.fail(f"Planner failed: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
