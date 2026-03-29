import ast
import re
from typing import Tuple, Dict, Any, List


def grade_refactor(original_code: str, refactored_code: str) -> Tuple[float, Dict[str, Any]]:
    breakdown = {
        "parses_valid": False,
        "functions_extracted": 0,
        "max_function_length": 0,
        "single_responsibility": False,
        "descriptive_names": False,
        "original_logic_preserved": False,
        "score_components": {}
    }

    try:
        tree = ast.parse(refactored_code)
        breakdown["parses_valid"] = True
        breakdown["score_components"]["parses_valid"] = 0.10
    except SyntaxError as e:
        breakdown["parse_error"] = str(e)
        return 0.0, breakdown

    functions = _extract_functions(tree)
    num_functions = len(functions)
    breakdown["functions_extracted"] = num_functions

    if num_functions >= 6:
        extract_score = 0.25
    elif num_functions >= 4:
        extract_score = 0.20
    elif num_functions >= 2:
        extract_score = 0.10
    else:
        extract_score = 0.0
    breakdown["score_components"]["functions_extracted"] = extract_score

    max_len, avg_len = _analyze_function_lengths(functions)
    breakdown["max_function_length"] = max_len

    if max_len <= 15:
        length_score = 0.25
    elif max_len <= 20:
        length_score = 0.20
    elif max_len <= 30:
        length_score = 0.12
    elif max_len <= 50:
        length_score = 0.05
    else:
        length_score = 0.0
    breakdown["score_components"]["function_length"] = length_score
    breakdown["avg_function_length"] = round(avg_len, 1)

    srp_score = _check_single_responsibility(functions)
    breakdown["single_responsibility"] = srp_score > 0.5
    breakdown["score_components"]["single_responsibility"] = srp_score * 0.20

    naming_score = _check_descriptive_names(functions)
    breakdown["descriptive_names"] = naming_score > 0.5
    breakdown["score_components"]["naming"] = naming_score * 0.10

    logic_score = _check_logic_preserved(original_code, refactored_code)
    breakdown["original_logic_preserved"] = logic_score > 0.5
    breakdown["score_components"]["logic_preserved"] = logic_score * 0.10

    total = sum(breakdown["score_components"].values())
    total = round(min(max(total, 0.0), 1.0), 3)
    return total, breakdown


def _extract_functions(tree):
    return [node for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _analyze_function_lengths(functions):
    if not functions:
        return 0, 0.0
    lengths = [getattr(fn, 'end_lineno', fn.lineno) - fn.lineno + 1 for fn in functions]
    return max(lengths), sum(lengths) / len(lengths)


def _check_single_responsibility(functions):
    focused_verbs = ['validate', 'check', 'calculate', 'compute', 'process',
                     'parse', 'format', 'send', 'save', 'load', 'get', 'set',
                     'build', 'create', 'update', 'fetch', 'apply', 'verify']
    if not functions:
        return 0.0
    focused = sum(1 for fn in functions
                  if any(v in fn.name.lower() for v in focused_verbs))
    return focused / len(functions)


def _check_descriptive_names(functions):
    if not functions:
        return 0.0
    good = sum(1 for fn in functions
               if not fn.name.startswith('__') and
               (len(fn.name) >= 5 and ('_' in fn.name or len(fn.name) >= 8)))
    return min(good / max(len(functions), 1), 1.0)


def _check_logic_preserved(original, refactored):
    key_patterns = [r'\b0\.08\b', r'\b10\b', r'\bORD-\b',
                    r'shipping_cost', r'subtotal', r'order_id', r'confirmed', r'payment']
    matches = sum(1 for p in key_patterns
                  if re.search(p, original) and re.search(p, refactored))
    return matches / len(key_patterns)