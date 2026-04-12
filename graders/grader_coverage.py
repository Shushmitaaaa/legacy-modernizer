import ast
import subprocess
import sys
import tempfile
import os
import re
from typing import Tuple, Dict, Any


def grade_test_coverage(source_code: str, test_code: str) -> Tuple[float, Dict[str, Any]]:
    breakdown = {
        "test_file_valid": False,
        "tests_found": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "has_edge_cases": False,
        "has_error_cases": False,
        "score_components": {}
    }

    try:
        ast.parse(test_code)
        breakdown["test_file_valid"] = True
        breakdown["score_components"]["test_file_valid"] = 0.10
    except SyntaxError as e:
        breakdown["parse_error"] = str(e)
        breakdown["score_components"]["test_file_valid"] = 0.0
        return 0.0, breakdown

    test_functions = _count_test_functions(test_code)
    breakdown["tests_found"] = test_functions

    if test_functions >= 6:
        test_count_score = 0.20
    elif test_functions >= 4:
        test_count_score = 0.15
    elif test_functions >= 2:
        test_count_score = 0.10
    else:
        test_count_score = 0.05
    breakdown["score_components"]["test_quantity"] = test_count_score

    pass_score, passed, failed, errors = _run_tests(source_code, test_code)
    breakdown["tests_passed"] = passed
    breakdown["tests_failed"] = failed + errors
    breakdown["score_components"]["tests_pass"] = pass_score * 0.40

    edge_case_score = _check_edge_cases(test_code)
    breakdown["has_edge_cases"] = edge_case_score > 0
    breakdown["score_components"]["edge_cases"] = edge_case_score * 0.15

    error_case_score = _check_error_cases(test_code)
    breakdown["has_error_cases"] = error_case_score > 0
    breakdown["score_components"]["error_cases"] = error_case_score * 0.15

    total = sum(breakdown["score_components"].values())
    total = round(min(max(total, 0.0), 1.0), 3)
    return total, breakdown


def _count_test_functions(test_code: str) -> int:
    tree = ast.parse(test_code)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                count += 1
    return count


def _run_tests(source_code: str, test_code: str) -> Tuple[float, int, int, int]:
    with tempfile.TemporaryDirectory() as tmpdir:
        # write source
        src_path = os.path.join(tmpdir, "source_module.py")
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write(source_code)

        # clean test code — remove any existing imports of source_module to avoid duplicates
        clean_test = re.sub(r'^\s*(import source_module|from source_module.*)\n', 
                           '', test_code, flags=re.MULTILINE)
        
        # prepend the import
        injected = f"import sys\nsys.path.insert(0, '{tmpdir}')\nfrom source_module import *\n\n" + clean_test

        test_path = os.path.join(tmpdir, "test_solution.py")
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(injected)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path,
                 "--tb=no", "-q", "--no-header",
                 "-p", "no:cacheprovider",
                 "--timeout=30"],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=tmpdir,
                env={**os.environ, "PYTHONPATH": tmpdir, "PYTHONDONTWRITEBYTECODE": "1"}
            )
            output = result.stdout + result.stderr

            # parse pytest summary line e.g. "3 passed, 1 failed"
            passed = len(re.findall(r'\bPASSED\b', output))
            failed = len(re.findall(r'\bFAILED\b', output))
            errors = len(re.findall(r'\bERROR\b', output))

            # fallback: parse summary line "X passed"
            if passed == 0 and failed == 0 and errors == 0:
                m = re.search(r'(\d+) passed', output)
                if m:
                    passed = int(m.group(1))
                m2 = re.search(r'(\d+) failed', output)
                if m2:
                    failed = int(m2.group(1))
                m3 = re.search(r'(\d+) error', output)
                if m3:
                    errors = int(m3.group(1))

            total_tests = passed + failed + errors
            if total_tests == 0:
                return 0.0, 0, 0, 0
            return passed / total_tests, passed, failed, errors

        except subprocess.TimeoutExpired:
            return 0.0, 0, 0, 1
        except Exception:
            return 0.0, 0, 0, 1


def _check_edge_cases(test_code: str) -> float:
    edge_indicators = [
        r'\b0\b', r'\[\]', r'""', r"''", r'\bNone\b',
        r'\bempty\b', r'\bzero\b', r'\bboundary\b', r'-\d+', r'\b100\b',
        r'\bmax\b', r'\bmin\b', r'\bnegative\b'
    ]
    matches = sum(1 for pattern in edge_indicators if re.search(pattern, test_code))
    return min(matches / 4, 1.0)


def _check_error_cases(test_code: str) -> float:
    error_indicators = [
        r'pytest\.raises', r'assertRaises', r'ValueError',
        r'TypeError', r'KeyError', r'ZeroDivisionError',
        r'Exception', r'with pytest'
    ]
    matches = sum(1 for pattern in error_indicators if re.search(pattern, test_code))
    return min(matches / 3, 1.0)