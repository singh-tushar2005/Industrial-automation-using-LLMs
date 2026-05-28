"""Isolated grammar-boundary test suite for IEC time literal grammar.

Run: python -m compiler.test_time_literals
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
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
    print("TIME LITERAL GRAMMAR")
    print("=" * 60)

    all_passed &= _test("T#2s", "x := T#2s;", True)
    all_passed &= _test("T#100ms", "x := T#100ms;", True)
    all_passed &= _test("T#5m", "x := T#5m;", True)
    all_passed &= _test("T#1h", "x := T#1h;", True)
    all_passed &= _test("t#1s (lowercase)", "x := t#1s;", True)
    all_passed &= _test("TIME#1s (typed literal)", "x := TIME#1s;", True)
    all_passed &= _test("TIME#100ms (typed literal)", "x := TIME#100ms;", True)
    all_passed &= _test("TIME#0s", "x := TIME#0s;", True)
    all_passed &= _test("TIME#1d", "x := TIME#1d;", True)
    all_passed &= _test("time literal in FB call", "Timer(IN := TRUE, PT := T#2s);", True)

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
