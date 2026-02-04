"""Main FastAPI application for AI Operations Assistant."""

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import Planner, Executor, Verifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent system for automated task execution",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
planner = Planner()
executor = Executor()
verifier = Verifier()


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
    Submit a task for complete execution (plan -> execute -> verify).
    
    This is the main endpoint that orchestrates the entire workflow.
    
    Args:
        request: TaskRequest with task description
        
    Returns:
        SubmitResponse with plan, execution results, and verification
    """
    try:
        logger.info(f"Processing task: {request.task}")
        
        # Step 1: Create plan
        logger.info("Step 1: Creating plan")
        plan = planner.create_plan(request.task)
        
        # Step 2: Execute plan
        logger.info("Step 2: Executing plan")
        executor_results = executor.execute_plan(plan)
        
        # Step 3: Verify results
        logger.info("Step 3: Verifying results")
        verification = verifier.verify_results(plan, executor_results)
        
        # Check if there are issues that need fixing
        issues = verification.get("issues", [])
        if issues:
            logger.warning(f"Found {len(issues)} issues during verification")
            # Optionally re-run failed steps (simple implementation)
            for issue in issues:
                step_id = issue.get("step_id")
                if step_id:
                    logger.info(f"Re-running step {step_id}")
                    retry_result = executor.execute_step_by_id(plan, step_id)
                    # Update the result
                    for i, result in enumerate(executor_results):
                        if result.get("id") == step_id:
                            executor_results[i] = retry_result
                            break
            
            # Re-verify after fixes
            logger.info("Re-verifying after fixes")
            verification = verifier.verify_results(plan, executor_results)
        
        logger.info("Task completed successfully")
        return SubmitResponse(
            plan=plan,
            executor_results=executor_results,
            verification=verification
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
