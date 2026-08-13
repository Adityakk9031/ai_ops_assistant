"""Tests for LangGraph StateGraph workflow and Vector Memory integration."""

import pytest
from workflow.state import AgentState
from workflow.graph import build_workflow_graph
from memory.vector_store import VectorMemoryManager


def test_vector_memory_manager_initialization():
    """Test that VectorMemoryManager initializes cleanly."""
    memory_manager = VectorMemoryManager()
    assert memory_manager.index_name == "ai-ops-memory"


def test_workflow_graph_compilation():
    """Test that LangGraph StateGraph compiles successfully."""
    graph = build_workflow_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test full LangGraph execution for a simple task."""
    graph = build_workflow_graph()
    initial_state: AgentState = {
        "user_task": "Check current weather in London",
        "past_memory": [],
        "plan": None,
        "tool_results": [],
        "verification_status": None,
        "retry_count": 0,
        "error": None
    }

    final_state = await graph.ainvoke(initial_state)

    assert "plan" in final_state
    assert final_state["plan"] is not None
    assert "tool_results" in final_state
    assert "verification_status" in final_state
    assert final_state["verification_status"] is not None
