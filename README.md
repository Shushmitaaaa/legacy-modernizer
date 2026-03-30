---
title: Legacy Modernizer
emoji: 🔧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# Legacy Codebase Modernization Agent — OpenEnv Environment

An OpenEnv environment where an AI agent modernizes legacy Python codebases step by step. The agent must upgrade syntax, add test coverage, and refactor god functions — with automated graders verifying correctness at each step.

## Motivation

Every software company has legacy code. Modernizing it is a $50B+ problem that requires multi-step reasoning, verification, and domain expertise — making it an ideal environment for training and evaluating AI agents.

## Environment Description

The agent receives a legacy Python codebase and must complete one of three tasks:
- Convert Python 2 syntax to Python 3
- Write comprehensive unit tests for untested code
- Refactor a monolithic god function into clean, focused functions

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| task_id | string | Current task identifier |
| code | string | The legacy Python code to modernize |
| instructions | string | What the agent must do |
| context | object | Additional metadata |
| step_count | int | Steps taken so far |
| max_steps | int | Maximum steps allowed |
| done | bool | Whether episode is complete |
| score | float | Current score (0.0–1.0) |

## Action Space

| Field | Type | Description |
|-------|------|-------------|
| action_type | string | One of: submit_code, run_tests, explain |
| code | string | The modernized code to submit |
| explanation | string | Agent's explanation of changes |

## Tasks

| Task | Difficulty | Max Steps | Description |
|------|-----------|-----------|-------------|
| task_syntax_upgrade | Easy | 5 | Convert Python 2 code to Python 3 |
| task_test_coverage | Medium | 8 | Write pytest unit tests for untested functions |
| task_refactor | Hard | 10 | Break up a god function into focused helpers |

## Grading Logic

Each grader scores 0.0–1.0 with partial credit:

**Syntax Upgrade:** syntax validity (0.30) + patterns fixed (0.50) + runs cleanly (0.20)

**Test Coverage:** file valid (0.10) + test quantity (0.20) + tests pass (0.40) + edge cases (0.15) + error cases (0.15)

**Refactor:** parses valid (0.10) + functions extracted (0.25) + function length (0.25) + single responsibility (0.20) + naming (0.10) + logic preserved (0.10)

## Baseline Scores

Evaluated using `Qwen/Qwen2.5-72B-Instruct` via HuggingFace router:

| Task | Score |
|------|-------|
| task_syntax_upgrade | 1.000 |
| task_test_coverage | 0.550 |
| task_refactor | 0.775 |
| **Average** | **0.775** |

## Setup & Usage

### API Endpoints
```
POST /reset  — Start a new episode
POST /step   — Submit an action
GET  /state  — Get current state
GET  /health — Health check
```

### Run Locally
```bash
git clone https://huggingface.co/spaces/Shushmitaaaaaaaaa/legacy-modernizer
cd legacy-modernizer
pip install -r requirements.txt
python app.py
```

### Run Inference
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export HF_TOKEN="your_hf_token"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export ENV_URL="https://shushmitaaaaaaaaa-legacy-modernizer.hf.space"
python inference.py
```

### Docker
```bash
docker build -t legacy-modernizer .
docker run -p 7860:7860 legacy-modernizer
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| API_BASE_URL | LLM API endpoint |
| MODEL_NAME | Model identifier |
| HF_TOKEN | HuggingFace API key |
| ENV_URL | Environment URL |