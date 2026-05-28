"""Isolated runtime grammar test suite for TASK declarations.

Run: python -m compiler.runtime_tests.test_tasks
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parser.st_parser import parse_st_program


def _test(name, code, should_pass):
    try:
        ast = parse_st_program(code)
        status = "PASS" if should_pass else "FAIL (unexpectedly passed)"
    except Exception as exc:
        status = "FAIL" if should_pass else "PASS (expected failure)"
        if should_pass:
            status += f"  -> {str(exc)[:120]}"
    print(f"  [{status:40s}] {name}")
    return status.startswith("PASS") or status.startswith("FAIL (expected")


def main():
    all_passed = True

    print("=" * 60)
    print("TASK GRAMMAR")
    print("=" * 60)

    all_passed &= _test("TASK with INTERVAL", "CONFIGURATION C\nTASK t0(INTERVAL := T#100ms);\nEND_CONFIGURATION", True)
    all_passed &= _test("TASK with PRIORITY", "CONFIGURATION C\nTASK t0(PRIORITY := 0);\nEND_CONFIGURATION", True)
    all_passed &= _test("TASK with both args", "CONFIGURATION C\nTASK t0(INTERVAL := T#100ms, PRIORITY := 0);\nEND_CONFIGURATION", True)
    all_passed &= _test("TASK with time literal seconds", "CONFIGURATION C\nTASK t0(INTERVAL := T#2s);\nEND_CONFIGURATION", True)
    all_passed &= _test("TASK with time literal ms", "CONFIGURATION C\nTASK t0(INTERVAL := T#250ms);\nEND_CONFIGURATION", True)
    all_passed &= _test("multiple TASKs", "CONFIGURATION C\nTASK t0(INTERVAL := T#100ms);\nTASK t1(PRIORITY := 1);\nEND_CONFIGURATION", True)
    all_passed &= _test("TASK without args", "CONFIGURATION C\nTASK t0();\nEND_CONFIGURATION", True)

    print()
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
