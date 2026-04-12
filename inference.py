import os
import re
import time
import requests


TASKS = [
    "task_syntax_upgrade",
    "task_test_coverage",
    "task_refactor",
]


def get_client():
    from openai import OpenAI

    base_url = os.environ["API_BASE_URL"]
    api_key = os.environ["API_KEY"]

    return OpenAI(base_url=base_url, api_key=api_key)

def call_llm(system_prompt: str, user_prompt: str) -> str:
    client = get_client()
    model = os.environ["MODEL_NAME"]
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def extract_code_block(text: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_task(task_id: str):
    model = os.environ["MODEL_NAME"]
    env_url = os.getenv("ENV_URL", "https://shushmitaaaaaaaaa-legacy-modernizer.hf.space")

    print(f"[START] task={task_id} env=legacy-modernizer model={model}")

    step_num = 0
    rewards = []
    success = False

    try:
        reset_resp = requests.post(
            f"{env_url}/reset",
            json={"task_id": task_id, "seed": 42},
            timeout=30
        )
        reset_resp.raise_for_status()
        obs = reset_resp.json()

        if task_id == "task_syntax_upgrade":
            system = (
                "You are an expert Python developer specializing in modernizing legacy code. "
                "When given Python 2 code, convert it completely to Python 3. "
                "Return ONLY the modernized Python 3 code inside a ```python code block."
            )
        elif task_id == "task_test_coverage":
            system = (
                "You are an expert Python developer specializing in writing comprehensive unit tests. "
                "Write thorough pytest tests covering happy paths, edge cases, and exception scenarios. "
                "Return ONLY the test code inside a ```python code block."
            )
        else:
            system = (
                "You are an expert Python developer specializing in refactoring legacy code. "
                "Extract smaller, focused helper functions from the monolithic god function. "
                "Each function must have a single responsibility and be under 20 lines. "
                "Return ONLY the fully refactored code inside a ```python code block."
            )

        user_prompt = (
            f"INSTRUCTIONS:\n{obs['instructions']}\n\n"
            f"CODE TO WORK ON:\n```python\n{obs['code']}\n```\n\n"
            f"Provide your solution now."
        )

        llm_response = call_llm(system, user_prompt)
        submitted_code = extract_code_block(llm_response)

        step_resp = requests.post(
            f"{env_url}/step",
            json={
                "action_type": "submit_code",
                "code": submitted_code,
                "explanation": "Baseline agent submission"
            },
            timeout=60
        )
        step_resp.raise_for_status()
        result = step_resp.json()

        step_num = 1
        reward = result["reward"]
        done = result["done"]
        rewards.append(reward)
        success = done and reward > 0

        print(f"[STEP] step={step_num} action=submit_code reward={reward:.2f} done={str(done).lower()} error=null")

    except Exception as e:
        step_num = max(step_num, 1)
        rewards.append(0.0)
        print(f"[STEP] step={step_num} action=submit_code reward=0.00 done=false error={str(e)}")
        success = False

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    final_score = rewards[-1] if rewards else 0.0
    print(f"[END] success={str(success).lower()} steps={step_num} score={final_score:.2f} rewards={rewards_str}")


def main():
    for task_id in TASKS:
        run_task(task_id)
        time.sleep(1)


if __name__ == "__main__":
    main()