"""Tests for the Verifier agent."""

import pytest
from agents.verifier import Verifier


def test_verifier_validates_successful_results():
    """Test that verifier correctly validates successful results."""
    verifier = Verifier()
    
    plan = {
        "task_summary": "Test task",
        "steps": [
            {
                "id": 1,
                "title": "Test step",
                "description": "Test",
                "tool": "GitHubTool",
                "inputs": {},
                "expected_output_schema": {
                    "type": "object",
                    "required": ["repos"]
                },
                "retry": 0
            }
        ],
        "final_output_schema": {
            "type": "object",
            "required": ["summary", "evidence", "confidence"]
        }
    }
    
    executor_results = [
        {
            "id": 1,
            "tool_call": {"name": "GitHubTool", "args": {}},
            "tool_result": {
                "ok": True,
                "status_code": 200,
                "data": {
                    "repos": [
                        {"name": "test-repo", "stars": 1000}
                    ]
                }
            },
            "success": True,
            "attempts": 1,
            "error": None
        }
    ]
    
    verification = verifier.verify_results(plan, executor_results)
    
    # Verify structure
    assert "final_output" in verification
    assert "issues" in verification
    assert "confidence" in verification
    assert "verifier_metadata" in verification
    
    # Verify final output
    final_output = verification["final_output"]
    assert "summary" in final_output
    assert "evidence" in final_output
    assert "confidence" in final_output
    
    # Should have no issues for successful result
    assert len(verification["issues"]) == 0
    
    # Confidence should be high
    assert verification["confidence"] >= 0.8
    
    print("✓ Verifier validated successful results correctly")
    print(f"  Confidence: {verification['confidence']}")
    print(f"  Summary: {final_output['summary']}")


def test_verifier_detects_failures():
    """Test that verifier detects failed steps."""
    verifier = Verifier()
    
    plan = {
        "task_summary": "Test task",
        "steps": [
            {
                "id": 1,
                "title": "Failed step",
                "description": "Test",
                "tool": "GitHubTool",
                "inputs": {},
                "expected_output_schema": {
                    "type": "object",
                    "required": ["repos"]
                },
                "retry": 0
            }
        ],
        "final_output_schema": {
            "type": "object",
            "required": ["summary", "evidence", "confidence"]
        }
    }
    
    executor_results = [
        {
            "id": 1,
            "tool_call": {"name": "GitHubTool", "args": {}},
            "tool_result": {},
            "success": False,
            "attempts": 1,
            "error": "API rate limit exceeded"
        }
    ]
    
    verification = verifier.verify_results(plan, executor_results)
    
    # Should have issues for failed result
    assert len(verification["issues"]) > 0
    
    # Confidence should be low
    assert verification["confidence"] < 0.8
    
    print("✓ Verifier detected failures correctly")
    print(f"  Issues found: {len(verification['issues'])}")
    print(f"  Confidence: {verification['confidence']}")


def test_verifier_detects_missing_fields():
    """Test that verifier detects missing required fields."""
    verifier = Verifier()
    
    plan = {
        "task_summary": "Test task",
        "steps": [
            {
                "id": 1,
                "title": "Test step",
                "description": "Test",
                "tool": "GitHubTool",
                "inputs": {},
                "expected_output_schema": {
                    "type": "object",
                    "required": ["repos", "total_count"]
                },
                "retry": 0
            }
        ],
        "final_output_schema": {
            "type": "object",
            "required": ["summary", "evidence", "confidence"]
        }
    }
    
    executor_results = [
        {
            "id": 1,
            "tool_call": {"name": "GitHubTool", "args": {}},
            "tool_result": {
                "ok": True,
                "status_code": 200,
                "data": {
                    "repos": []  # Missing total_count
                }
            },
            "success": True,
            "attempts": 1,
            "error": None
        }
    ]
    
    verification = verifier.verify_results(plan, executor_results)
    
    # Should have issues for missing field
    issues = verification["issues"]
    assert len(issues) > 0
    assert any("total_count" in issue["issue"] for issue in issues)
    
    print("✓ Verifier detected missing fields correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
