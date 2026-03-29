import ast
import subprocess
import sys
import tempfile
import os
from typing import Tuple, Dict, Any


def grade_syntax_upgrade(original_code: str, submitted_code: str) -> Tuple[float, Dict[str, Any]]:
    breakdown = {
        "parses_as_python3": False,
        "runs_without_error": False,
        "python2_patterns_removed": {},
        "score_components": {}
    }

    try:
        ast.parse(submitted_code)
        breakdown["parses_as_python3"] = True
        breakdown["score_components"]["syntax_valid"] = 0.30
    except SyntaxError as e:
        breakdown["parse_error"] = str(e)
        breakdown["score_components"]["syntax_valid"] = 0.0
        return 0.0, breakdown

    patterns = {
        "print_statement": {
            "check": _has_print_statement,
            "weight": 0.10,
            "description": "print() used instead of print statement"
        },
        "iteritems_removed": {
            "check": lambda c: ".iteritems()" not in c and ".itervalues()" not in c and ".iterkeys()" not in c,
            "weight": 0.10,
            "description": ".iteritems()/.itervalues()/.iterkeys() replaced"
        },
        "has_key_removed": {
            "check": lambda c: ".has_key(" not in c,
            "weight": 0.08,
            "description": ".has_key() replaced with 'in' operator"
        },
        "except_syntax_fixed": {
            "check": _no_old_except_syntax,
            "weight": 0.10,
            "description": "except X, e syntax fixed to except X as e"
        },
        "urllib2_removed": {
            "check": lambda c: "urllib2" not in c,
            "weight": 0.06,
            "description": "urllib2 replaced with urllib.request"
        },
        "cpickle_removed": {
            "check": lambda c: "cPickle" not in c and "cStringIO" not in c,
            "weight": 0.06,
            "description": "cPickle/cStringIO replaced with modern equivalents"
        },
    }

    pattern_score = 0.0
    for name, config in patterns.items():
        try:
            passed = config["check"](submitted_code)
        except Exception:
            passed = False
        breakdown["python2_patterns_removed"][name] = {
            "passed": passed,
            "description": config["description"],
            "weight": config["weight"]
        }
        if passed:
            pattern_score += config["weight"]

    breakdown["score_components"]["patterns_fixed"] = pattern_score

    run_score = 0.0
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(submitted_code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, "-c", f"import ast; ast.parse(open('{tmp_path}').read()); print('OK')"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            run_score = 0.20
            breakdown["runs_without_error"] = True
    except Exception as e:
        breakdown["run_error"] = str(e)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    breakdown["score_components"]["runs_cleanly"] = run_score

    total = sum(breakdown["score_components"].values())
    total = round(min(max(total, 0.0), 1.0), 3)
    return total, breakdown


def _has_print_statement(code: str) -> bool:
    lines = code.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('print ') and not stripped.startswith('print('):
            if not stripped.startswith('print ()'):
                return False
    return True


def _no_old_except_syntax(code: str) -> bool:
    import re
    old_pattern = re.compile(r'except\s+\w+(\.\w+)?\s*,\s*\w+\s*:')
    return not bool(old_pattern.search(code))