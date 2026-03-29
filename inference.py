"""
inference.py — Baseline inference script for Legacy Codebase Modernization Agent
Uses OpenAI client against the configured API_BASE_URL and MODEL_NAME.
Must complete in < 20 minutes on vcpu=2, memory=8gb.
"""

import os
import json
import time
import requests
from openai import OpenAI


API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
ENV_URL      = os.environ.get("ENV_URL", "https://shushmitaaaaaaaaa-legacy-modernizer.hf.space")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "sk-placeholder")

TASKS = [
    "task_syntax_upgrade",
    "task_test_coverage",
    "task_refactor",
]


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the LLM and return its text response."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def extract_code_block(text: str) -> str:
    """Extract code from a markdown code block if present."""
    import re
    
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_task(task_id: str) -> dict:
    """Run a single task end-to-end and return the result."""
    print(f"\n{'='*60}")
    print(f"  TASK: {task_id}")
    print(f"{'='*60}")

    
    reset_resp = requests.post(
        f"{ENV_URL}/reset",
        json={"task_id": task_id, "seed": 42},
        timeout=30
    )
    reset_resp.raise_for_status()
    obs = reset_resp.json()

    print(f"  Instructions preview: {obs['instructions'][:120]}...")
    print(f"  Code length: {len(obs['code'])} chars")

    
    if task_id == "task_syntax_upgrade":
        system = (
            "You are an expert Python developer specializing in modernizing legacy code. "
            "When given Python 2 code, you convert it completely to Python 3. "
            "Return ONLY the modernized Python 3 code, inside a ```python code block. "
            "Do not include any explanation outside the code block."
        )
    elif task_id == "task_test_coverage":
        system = (
            "You are an expert Python developer specializing in writing comprehensive unit tests. "
            "When given Python source code, you write thorough pytest tests covering happy paths, "
            "edge cases, and exception scenarios. "
            "Return ONLY the test code inside a ```python code block. "
            "Do not include imports of the source module — that will be handled automatically."
        )
    else:  
        system = (
            "You are an expert Python developer specializing in refactoring legacy code. "
            "When given a monolithic god function, you extract smaller, focused helper functions. "
            "Each function must have a single responsibility and be under 20 lines. "
            "Preserve all original behavior exactly. "
            "Return ONLY the fully refactored code inside a ```python code block."
        )

    user_prompt = (
        f"INSTRUCTIONS:\n{obs['instructions']}\n\n"
        f"CODE TO WORK ON:\n```python\n{obs['code']}\n```\n\n"
        f"Provide your solution now."
    )

   
    print("  Calling LLM...")
    t0 = time.time()
    llm_response = call_llm(system, user_prompt)
    elapsed = time.time() - t0
    print(f"  LLM responded in {elapsed:.1f}s")

    submitted_code = extract_code_block(llm_response)
    print(f"  Extracted code: {len(submitted_code)} chars")

    
    step_resp = requests.post(
        f"{ENV_URL}/step",
        json={
            "action_type": "submit_code",
            "code": submitted_code,
            "explanation": "Baseline agent submission"
        },
        timeout=60
    )
    step_resp.raise_for_status()
    result = step_resp.json()

    score = result["reward"]
    breakdown = result["info"].get("grading_breakdown", {})

    print(f"\n  ✅ SCORE: {score:.3f}")
    if "score_components" in breakdown:
        print("  Score breakdown:")
        for component, value in breakdown["score_components"].items():
            print(f"    {component}: {value:.3f}")

    return {
        "task_id": task_id,
        "score": score,
        "done": result["done"],
        "breakdown": breakdown,
        "llm_time_seconds": round(elapsed, 2),
    }


def main():
    print("\n" + "="*60)
    print("  LEGACY CODEBASE MODERNIZATION AGENT — BASELINE INFERENCE")
    print("="*60)
    print(f"  ENV_URL:    {ENV_URL}")
    print(f"  MODEL_NAME: {MODEL_NAME}")
    print(f"  API_BASE:   {API_BASE_URL}")

   
    try:
        health = requests.get(f"{ENV_URL}/health", timeout=10)
        health.raise_for_status()
        print(f"  Environment: HEALTHY ✅")
    except Exception as e:
        print(f"  Environment health check FAILED: {e}")
        raise

    results = []
    total_start = time.time()

    for task_id in TASKS:
        try:
            result = run_task(task_id)
            results.append(result)
        except Exception as e:
            print(f"  ERROR on {task_id}: {e}")
            results.append({"task_id": task_id, "score": 0.0, "error": str(e)})

    
    total_elapsed = time.time() - total_start
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores)

    print("\n" + "="*60)
    print("  FINAL RESULTS SUMMARY")
    print("="*60)
    for r in results:
        status = "✅" if r["score"] >= 0.7 else "⚠️" if r["score"] >= 0.4 else "❌"
        print(f"  {status} {r['task_id']}: {r['score']:.3f}")
    print(f"\n  Average Score: {avg_score:.3f}")
    print(f"  Total Time:    {total_elapsed:.1f}s")
    print("="*60)

   
    with open("results.json", "w") as f:
        json.dump({
            "results": results,
            "average_score": avg_score,
            "total_time_seconds": round(total_elapsed, 2),
            "model": MODEL_NAME,
        }, f, indent=2)

    print("\n  Results saved to results.json")
    return results


if __name__ == "__main__":
    main()