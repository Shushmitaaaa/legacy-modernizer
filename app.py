from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from models import (
    ObservationModel,
    ActionModel,
    StepResultModel,
    ResetRequestModel,
    StateModel,
)
from environment import LegacyModernizerEnv, ALL_TASK_IDS

# Global environment instance
env = LegacyModernizerEnv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Legacy Modernizer OpenEnv starting up...")
    yield
    print("Shutting down.")


app = FastAPI(
    title="Legacy Codebase Modernization Agent — OpenEnv",
    description=(
        "An OpenEnv environment where an AI agent modernizes legacy Python codebases. "
        "Tasks include Python 2→3 upgrade, unit test generation, and god-function refactoring."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "Legacy Codebase Modernization Agent",
        "version": "1.0.0",
        "status": "running",
        "tasks": ALL_TASK_IDS,
        "endpoints": {
            "reset": "POST /reset",
            "step": "POST /step",
            "state": "GET /state",
            "health": "GET /health",
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reset", response_model=ObservationModel)
def reset(request: ResetRequestModel = None):
    """
    Reset the environment and return the initial observation.
    Optionally specify a task_id and seed for reproducibility.
    """
    try:
        req = request or ResetRequestModel()
        observation = env.reset(task_id=req.task_id, seed=req.seed)
        return observation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step", response_model=StepResultModel)
def step(action: ActionModel):
    """
    Take a step in the environment with the given action.
    Action types: submit_code, run_tests, explain
    """
    try:
        result = env.step(action)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
def state():
    """
    Get the current environment state without taking a step.
    """
    return env.state()


@app.get("/tasks")
def list_tasks():
    """List all available tasks with descriptions."""
    from environment import TASK_CONFIG
    return {
        task_id: {
            "max_steps": config["max_steps"],
            "instructions": config["instructions"][:200] + "...",
        }
        for task_id, config in TASK_CONFIG.items()
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)