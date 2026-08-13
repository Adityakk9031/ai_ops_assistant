"""Main FastAPI application for AI Operations Assistant."""

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables first before importing agents/services
load_dotenv()

from agents import Planner, Executor, Verifier
from services.workflow_service import WorkflowService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent system for automated task execution powered by LangGraph and Pinecone",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents & services
planner = Planner()
executor = Executor()
verifier = Verifier()
workflow_service = WorkflowService()



# Request/Response models
class TaskRequest(BaseModel):
    task: str


class PlanResponse(BaseModel):
    plan: Dict[str, Any]


class ExecuteRequest(BaseModel):
    plan: Dict[str, Any]


class ExecuteResponse(BaseModel):
    results: list[Dict[str, Any]]


class VerifyRequest(BaseModel):
    plan: Dict[str, Any]
    executor_results: list[Dict[str, Any]]


class VerifyResponse(BaseModel):
    verification: Dict[str, Any]


class SubmitResponse(BaseModel):
    plan: Dict[str, Any]
    executor_results: list[Dict[str, Any]]
    verification: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Operations Assistant",
        "version": "1.0.0",
        "endpoints": {
            "/api/submit": "Submit a task for complete execution (plan -> execute -> verify)",
            "/api/plan": "Create an execution plan for a task",
            "/api/execute": "Execute a plan",
            "/api/verify": "Verify execution results"
        }
    }


@app.post("/api/plan", response_model=PlanResponse)
async def create_plan(request: TaskRequest):
    """
    Create an execution plan for a given task.
    
    Args:
        request: TaskRequest with task description
        
    Returns:
        PlanResponse with execution plan
    """
    try:
        logger.info(f"Creating plan for task: {request.task}")
        plan = planner.create_plan(request.task)
        return PlanResponse(plan=plan)
    except Exception as e:
        logger.error(f"Plan creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Plan creation failed: {str(e)}")


@app.post("/api/execute", response_model=ExecuteResponse)
async def execute_plan(request: ExecuteRequest):
    """
    Execute a plan by running all steps.
    
    Args:
        request: ExecuteRequest with plan
        
    Returns:
        ExecuteResponse with execution results
    """
    try:
        logger.info("Executing plan")
        results = executor.execute_plan(request.plan)
        return ExecuteResponse(results=results)
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.post("/api/verify", response_model=VerifyResponse)
async def verify_results(request: VerifyRequest):
    """
    Verify execution results and assemble final output.
    
    Args:
        request: VerifyRequest with plan and executor results
        
    Returns:
        VerifyResponse with verification results
    """
    try:
        logger.info("Verifying results")
        verification = verifier.verify_results(request.plan, request.executor_results)
        return VerifyResponse(verification=verification)
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.post("/api/submit", response_model=SubmitResponse)
async def submit_task(request: TaskRequest):
    """
    Submit a task for complete execution (Memory -> Plan -> Execute -> Verify -> SaveMemory).
    
    Orchestrated via LangGraph StateGraph workflow backed by Pinecone vector DB memory.
    
    Args:
        request: TaskRequest with task description
        
    Returns:
        SubmitResponse with plan, execution results, and verification
    """
    try:
        logger.info(f"Processing task via LangGraph StateGraph: '{request.task}'")
        result = await workflow_service.run_task(request.task)
        
        return SubmitResponse(
            plan=result["plan"],
            executor_results=result["executor_results"],
            verification=result["verification"]
        )
        
    except Exception as e:
        logger.error(f"Task submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")



@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
