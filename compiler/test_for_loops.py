"""Isolated grammar-boundary test suite for FOR loop grammar.

Run: python -m compiler.test_for_loops
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
    print("FOR LOOP GRAMMAR")
    print("=" * 60)

    all_passed &= _test("basic FOR loop", "FOR i := 1 TO 10 DO x := x + 1; END_FOR;", True)
    all_passed &= _test("FOR loop with BY", "FOR i := 1 TO 10 BY 2 DO x := x + 1; END_FOR;", True)
    all_passed &= _test("FOR loop with variable bound", "FOR i := 1 TO N DO x := x + 1; END_FOR;", True)
    all_passed &= _test("FOR loop with expression start", "FOR i := a + 1 TO b DO x := x + 1; END_FOR;", True)
    all_passed &= _test("nested FOR loops", "FOR i := 1 TO 10 DO FOR j := 1 TO 5 DO x := x + 1; END_FOR; END_FOR;", True)
    all_passed &= _test("FOR loop with EXIT", "FOR i := 1 TO 10 DO EXIT; END_FOR;", True)
    all_passed &= _test("FOR loop with multiple body statements", "FOR i := 1 TO 10 DO x := x + 1; y := y + 1; END_FOR;", True)
    all_passed &= _test("FOR loop without body (empty)", "FOR i := 1 TO 10 DO END_FOR;", True)

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
