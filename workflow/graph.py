"""LangGraph StateGraph orchestration for AI Operations Assistant."""

import logging
from typing import Dict, Any
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from workflow.state import AgentState
from memory.vector_store import VectorMemoryManager
from agents import Planner, Executor, Verifier

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("workflow.graph")

# Singletons for memory and agents within graph scope
vector_memory = VectorMemoryManager()
planner = Planner()
executor = Executor()
verifier = Verifier()


def memory_node(state: AgentState) -> Dict[str, Any]:
    """Memory Node: Query Pinecone vector database for similar past tasks."""
    user_task = state["user_task"]
    logger.info(f"[LangGraph: Memory Node] Querying Pinecone for past memory matching: '{user_task}'")
    
    memories = vector_memory.search_similar_tasks(user_task, k=2)
    logger.info(f"[LangGraph: Memory Node] Injected {len(memories)} past memories into graph state")
    return {"past_memory": memories}


def planner_node(state: AgentState) -> Dict[str, Any]:
    """Planner Node: Generate structured plan incorporating vector memories."""
    user_task = state["user_task"]
    past_memory = state.get("past_memory", [])
    logger.info(f"[LangGraph: Planner Node] Creating plan for task: '{user_task}'")
    
    plan = planner.create_plan(user_task, past_memory=past_memory)
    logger.info(f"[LangGraph: Planner Node] Plan created with {len(plan.get('steps', []))} steps")
    return {"plan": plan}


def executor_node(state: AgentState) -> Dict[str, Any]:
    """Executor Node: Run plan steps using tool adapters."""
    plan = state["plan"]
    logger.info(f"[LangGraph: Executor Node] Running plan steps for '{plan.get('task_summary', '')}'")
    
    tool_results = executor.execute_plan(plan)
    logger.info(f"[LangGraph: Executor Node] Executed {len(tool_results)} step(s)")
    return {"tool_results": tool_results}


def verifier_node(state: AgentState) -> Dict[str, Any]:
    """Verifier Node: Inspect results and compute confidence score."""
    plan = state["plan"]
    tool_results = state.get("tool_results", [])
    logger.info("[LangGraph: Verifier Node] Validating step execution results")
    
    verification = verifier.verify_results(plan, tool_results)
    current_retry = state.get("retry_count", 0) + 1
    
    logger.info(f"[LangGraph: Verifier Node] Confidence: {verification.get('confidence')}, Issues: {len(verification.get('issues', []))}")
    return {
        "verification_status": verification,
        "retry_count": current_retry
    }


def save_memory_node(state: AgentState) -> Dict[str, Any]:
    """SaveMemory Node: Upsert successful task & plan into Pinecone."""
    user_task = state["user_task"]
    plan = state.get("plan", {})
    verification = state.get("verification_status", {})
    
    logger.info("[LangGraph: SaveMemory Node] Task completed successfully. Upserting to Pinecone memory")
    vector_memory.save_successful_task(user_task, plan, verification)
    return {}


def route_verifier(state: AgentState) -> str:
    """Conditional Edge: Route from Verifier to SaveMemory, Executor retry, or END."""
    verification = state.get("verification_status", {})
    issues = verification.get("issues", [])
    retry_count = state.get("retry_count", 0)
    
    if not issues:
        logger.info("[LangGraph Conditional Edge] Verification succeeded with 0 issues -> Routing to SaveMemory")
        return "save_memory"
    
    if retry_count < 2:
        logger.warning(f"[LangGraph Conditional Edge] Found {len(issues)} issue(s), retry_count={retry_count} -> Routing back to Executor")
        return "executor"
    
    logger.warning(f"[LangGraph Conditional Edge] Max retries ({retry_count}) reached -> Routing to SaveMemory")
    return "save_memory"


def build_workflow_graph():
    """Build and compile the LangGraph StateGraph."""
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("memory", memory_node)
    builder.add_node("planner", planner_node)
    builder.add_node("executor", executor_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("save_memory", save_memory_node)
    
    # Add static edges
    builder.add_edge(START, "memory")
    builder.add_edge("memory", "planner")
    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "verifier")
    
    # Add conditional edge from verifier
    builder.add_conditional_edges(
        "verifier",
        route_verifier,
        {
            "save_memory": "save_memory",
            "executor": "executor",
            "end": END
        }
    )
    
    builder.add_edge("save_memory", END)
    
    graph = builder.compile()
    logger.info("Successfully compiled LangGraph StateGraph workflow")
    return graph
