"""Isolated grammar-boundary test suite for FB/Function invocation grammar.

Run: python -m compiler.test_invocations
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
    print("FB INVOCATION GRAMMAR")
    print("=" * 60)

    all_passed &= _test("FB call as statement", "Timer(IN := TRUE, PT := T#2s);", True)
    all_passed &= _test("FB call single argument", "Timer(IN := TRUE);", True)
    all_passed &= _test("FB call no arguments", "Timer();", True)
    all_passed &= _test("FB call multiline", "Timer(\n    IN := TRUE,\n    PT := T#2s\n);", True)
    all_passed &= _test("nested function in expression", "x := SHL(y, 1);", True)
    all_passed &= _test("function in assignment RHS", "x := BYTE_TO_DWORD(PT[pos]);", True)
    all_passed &= _test("nested function call", "x := BOOL_TO_DWORD((DX AND BYTE#16#80) > BYTE#0);", True)
    all_passed &= _test("function call in IF condition", "IF SHL(x, 1) > 10 THEN y := 1; END_IF;", True)
    all_passed &= _test("function call with expression argument", "x := SHL(a + b, 1);", True)
    all_passed &= _test("FB call in expression context", "x := Timer.Q;", True)

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
