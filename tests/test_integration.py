"""Integration tests for the complete workflow."""

import pytest
from agents import Planner, Executor, Verifier


def test_complete_workflow():
    """Test the complete workflow: plan -> execute -> verify."""
    # Initialize agents
    planner = Planner()
    executor = Executor()
    verifier = Verifier()
    
    # Define task
    task = "Find the top 3 Python web frameworks on GitHub with more than 5000 stars"
    
    try:
        # Step 1: Create plan
        print("\n=== Step 1: Creating Plan ===")
        plan = planner.create_plan(task)
        print(f"✓ Plan created with {len(plan['steps'])} steps")
        print(f"  Task: {plan['task_summary']}")
        
        # Step 2: Execute plan
        print("\n=== Step 2: Executing Plan ===")
        executor_results = executor.execute_plan(plan)
        print(f"✓ Executed {len(executor_results)} steps")
        
        successful_steps = sum(1 for r in executor_results if r["success"])
        print(f"  Successful: {successful_steps}/{len(executor_results)}")
        
        # Step 3: Verify results
        print("\n=== Step 3: Verifying Results ===")
        verification = verifier.verify_results(plan, executor_results)
        print(f"✓ Verification complete")
        print(f"  Confidence: {verification['confidence']}")
        print(f"  Issues: {len(verification['issues'])}")
        
        # Print final output
        print("\n=== Final Output ===")
        final_output = verification["final_output"]
        print(f"Summary: {final_output['summary']}")
        print(f"Evidence items: {len(final_output['evidence'])}")
        
        # Assertions
        assert "final_output" in verification
        assert "summary" in final_output
        assert "evidence" in final_output
        assert "confidence" in final_output
        
        print("\n✓ Complete workflow test passed!")
        
    except Exception as e:
        pytest.fail(f"Workflow failed: {str(e)}")


def test_weather_workflow():
    """Test workflow with weather query."""
    planner = Planner()
    executor = Executor()
    verifier = Verifier()
    
    task = "Get the current weather in Bangalore"
    
    try:
        print("\n=== Testing Weather Workflow ===")
        
        plan = planner.create_plan(task)
        executor_results = executor.execute_plan(plan)
        verification = verifier.verify_results(plan, executor_results)
        
        final_output = verification["final_output"]
        print(f"Summary: {final_output['summary']}")
        
        assert verification["confidence"] > 0.0
        print("✓ Weather workflow test passed!")
        
    except Exception as e:
        pytest.fail(f"Weather workflow failed: {str(e)}")


def test_multi_tool_workflow():
    """Test workflow using multiple tools."""
    planner = Planner()
    executor = Executor()
    verifier = Verifier()
    
    task = "Find top 3 Python web frameworks on GitHub and get weather in Bangalore"
    
    try:
        print("\n=== Testing Multi-Tool Workflow ===")
        
        plan = planner.create_plan(task)
        
        # Verify plan uses multiple tools
        tools_used = set(step["tool"] for step in plan["steps"])
        print(f"Tools used: {', '.join(tools_used)}")
        
        executor_results = executor.execute_plan(plan)
        verification = verifier.verify_results(plan, executor_results)
        
        final_output = verification["final_output"]
        print(f"Summary: {final_output['summary']}")
        print(f"Confidence: {verification['confidence']}")
        
        # Should use at least 2 tools
        assert len(tools_used) >= 2
        print("✓ Multi-tool workflow test passed!")
        
    except Exception as e:
        pytest.fail(f"Multi-tool workflow failed: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
