import random
from typing import Optional, Dict, Any, Tuple

from models import ObservationModel, ActionModel, StepResultModel, ActionType
from tasks.task_syntax import LEGACY_CODE_SAMPLES as SYNTAX_SAMPLES
from tasks.task_coverage import LEGACY_CODE_SAMPLES as COVERAGE_SAMPLES
from tasks.task_refactor import LEGACY_CODE_SAMPLES as REFACTOR_SAMPLES
from graders.grader_syntax import grade_syntax_upgrade
from graders.grader_coverage import grade_test_coverage
from graders.grader_refactor import grade_refactor


TASK_CONFIG = {
    "task_syntax_upgrade": {
        "samples": SYNTAX_SAMPLES,
        "max_steps": 5,
        "instructions": (
            "You are given legacy Python 2 code. Your job is to modernize it to Python 3.\n"
            "Fix all Python 2 patterns including:\n"
            "- print statements → print() functions\n"
            "- .iteritems() → .items()\n"
            "- .has_key() → 'in' operator\n"
            "- except X, e: → except X as e:\n"
            "- urllib2 → urllib.request\n"
            "- cPickle → pickle\n"
            "- unicode() → str()\n"
            "Submit your modernized code using action_type='submit_code'."
        ),
    },
    "task_test_coverage": {
        "samples": COVERAGE_SAMPLES,
        "max_steps": 8,
        "instructions": (
            "You are given Python source code with zero test coverage.\n"
            "Write comprehensive unit tests using pytest.\n"
            "Requirements:\n"
            "- At least 6 test functions\n"
            "- Cover happy path, edge cases, and error/exception cases\n"
            "- Tests must pass when run against the original source\n"
            "- Use pytest.raises() for exception testing\n"
            "Submit ONLY the test code (not the source) using action_type='submit_code'."
        ),
    },
    "task_refactor": {
        "samples": REFACTOR_SAMPLES,
        "max_steps": 10,
        "instructions": (
            "You are given a monolithic 'god function' that does too many things.\n"
            "Refactor it by extracting smaller, focused functions.\n"
            "Requirements:\n"
            "- Extract at least 4 helper functions\n"
            "- No function should exceed 20 lines\n"
            "- Each function should have a single, clear responsibility\n"
            "- All original behavior must be preserved\n"
            "- Use descriptive function names with verbs (validate_, calculate_, etc.)\n"
            "Submit the fully refactored code using action_type='submit_code'."
        ),
    },
}

ALL_TASK_IDS = list(TASK_CONFIG.keys())


class LegacyModernizerEnv:
    """Core environment managing state for the Legacy Codebase Modernization Agent."""

    def __init__(self):
        self._state: Optional[Dict[str, Any]] = None

    def reset(self, task_id: Optional[str] = None, seed: Optional[int] = None) -> ObservationModel:
        if seed is not None:
            random.seed(seed)

        if task_id is None:
            task_id = random.choice(ALL_TASK_IDS)

        if task_id not in TASK_CONFIG:
            raise ValueError(f"Unknown task_id: {task_id}. Valid: {ALL_TASK_IDS}")

        config = TASK_CONFIG[task_id]
        sample = random.choice(config["samples"])

        self._state = {
            "task_id": task_id,
            "original_code": sample["code"],
            "current_code": sample["code"],
            "sample_id": sample["id"],
            "instructions": config["instructions"],
            "max_steps": config["max_steps"],
            "step_count": 0,
            "done": False,
            "score": 0.0,
            "submitted_test_code": None,
        }

        return self._build_observation()

    def step(self, action: ActionModel) -> StepResultModel:
        if self._state is None:
            raise RuntimeError("Call reset() before step()")
        if self._state["done"]:
            raise RuntimeError("Episode is done. Call reset() to start a new one.")

        self._state["step_count"] += 1
        reward = 0.0
        info = {}

        if action.action_type == ActionType.SUBMIT_CODE:
            if not action.code:
                reward = 0.0
                info["error"] = "No code submitted"
            else:
                score, breakdown = self._grade(action.code)
                reward = score
                self._state["score"] = score
                self._state["current_code"] = action.code
                self._state["done"] = True
                info["grading_breakdown"] = breakdown
                info["final_score"] = score

        elif action.action_type == ActionType.RUN_TESTS:
            # Intermediate feedback: just parse check
            import ast
            try:
                ast.parse(action.code or "")
                reward = 0.05
                info["message"] = "Code parses successfully. Submit when ready."
            except SyntaxError as e:
                reward = 0.0
                info["syntax_error"] = str(e)

        elif action.action_type == ActionType.EXPLAIN:
            reward = 0.0
            info["message"] = "Explanation noted. Submit your code when ready."

        # End episode if max steps reached
        if self._state["step_count"] >= self._state["max_steps"]:
            self._state["done"] = True
            info["reason"] = "Max steps reached"

        obs = self._build_observation()

        return StepResultModel(
            observation=obs,
            reward=reward,
            done=self._state["done"],
            info=info
        )

    def state(self) -> Dict[str, Any]:
        if self._state is None:
            return {"status": "not_initialized", "message": "Call reset() first"}
        return {
            "task_id": self._state["task_id"],
            "step_count": self._state["step_count"],
            "max_steps": self._state["max_steps"],
            "done": self._state["done"],
            "score": self._state["score"],
            "current_code": self._state["current_code"],
            "instructions": self._state["instructions"],
        }

    def _grade(self, submitted_code: str) -> Tuple[float, Dict]:
        task_id = self._state["task_id"]
        original = self._state["original_code"]

        if task_id == "task_syntax_upgrade":
            return grade_syntax_upgrade(original, submitted_code)
        elif task_id == "task_test_coverage":
            return grade_test_coverage(original, submitted_code)
        elif task_id == "task_refactor":
            return grade_refactor(original, submitted_code)
        else:
            return 0.0, {"error": f"No grader for task {task_id}"}

    def _build_observation(self) -> ObservationModel:
        s = self._state
        return ObservationModel(
            task_id=s["task_id"],
            code=s["current_code"],
            instructions=s["instructions"],
            context={"sample_id": s["sample_id"]},
            step_count=s["step_count"],
            max_steps=s["max_steps"],
            done=s["done"],
            score=s["score"],
        )