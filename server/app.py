from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ObservationModel,
    ActionModel,
    StepResultModel,
    ResetRequestModel,
    StateModel,
)
from environment import LegacyModernizerEnv, ALL_TASK_IDS

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
    try:
        result = env.step(action)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def list_tasks():
    from environment import TASK_CONFIG
    return {
        task_id: {
            "max_steps": config["max_steps"],
            "instructions": config["instructions"][:200] + "...",
        }
        for task_id, config in TASK_CONFIG.items()
    }


@app.get("/grader")
def grader_info():
    return {
        "graders": {
            "task_syntax_upgrade": {
                "type": "programmatic",
                "description": "Grades Python 2 to 3 syntax conversion",
                "score_range": [0.0, 1.0],
                "components": ["syntax_valid", "patterns_fixed", "runs_cleanly"]
            },
            "task_test_coverage": {
                "type": "programmatic",
                "description": "Grades unit test quality and coverage",
                "score_range": [0.0, 1.0],
                "components": ["test_file_valid", "test_quantity", "tests_pass", "edge_cases", "error_cases"]
            },
            "task_refactor": {
                "type": "programmatic",
                "description": "Grades god function refactoring quality",
                "score_range": [0.0, 1.0],
                "components": ["parses_valid", "functions_extracted", "function_length", "single_responsibility", "naming", "logic_preserved"]
            }
        }
    }


@app.get("/baseline")
def baseline_info():
    return {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "api_base": "https://router.huggingface.co/v1",
        "scores": {
            "task_syntax_upgrade": 1.000,
            "task_test_coverage": 0.600,
            "task_refactor": 0.720,
            "average": 0.773
        },
        "inference_script": "inference.py",
        "runtime_seconds": 107
    }


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()