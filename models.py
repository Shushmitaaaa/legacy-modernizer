from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from enum import Enum


class ActionType(str, Enum):
    SUBMIT_CODE = "submit_code"
    RUN_TESTS = "run_tests"
    EXPLAIN = "explain"


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ObservationModel(BaseModel):
    task_id: str = Field(..., description="Current task identifier")
    code: str = Field(..., description="The legacy Python code to modernize")
    instructions: str = Field(..., description="What the agent must do")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    step_count: int = Field(default=0, description="Number of steps taken so far")
    max_steps: int = Field(..., description="Maximum steps allowed for this task")
    done: bool = Field(default=False, description="Whether the task is complete")
    score: float = Field(default=0.0, description="Current score (0.0 to 1.0)")


class ActionModel(BaseModel):
    action_type: ActionType = Field(..., description="Type of action")
    code: Optional[str] = Field(None, description="Modernized code submitted")
    explanation: Optional[str] = Field(None, description="Agent's explanation")


class StepResultModel(BaseModel):
    observation: ObservationModel
    reward: float = Field(..., description="Reward for this step (0.0 to 1.0)")
    done: bool = Field(..., description="Whether episode is complete")
    info: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic info")


class ResetRequestModel(BaseModel):
    task_id: Optional[str] = Field(None, description="Specific task to run, or None for random")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class StateModel(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    done: bool
    score: float
    current_code: str
    instructions: str

