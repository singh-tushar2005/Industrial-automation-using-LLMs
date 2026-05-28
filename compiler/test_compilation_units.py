"""Isolated grammar-boundary test suite for root-level compilation unit sequencing.

Tests whether the parser supports:
- single compilation unit parsing
- multiple compilation units in sequence
- mixed FUNCTION / FUNCTION_BLOCK / PROGRAM parsing
- EOF handling
- empty-body compilation units

Run: python -m compiler.test_compilation_units
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parser.st_parser import parse_st_program


def _test(name, code, should_pass):
    """Run one test case and report result."""
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
    print("SINGLE UNIT PARSING")
    print("=" * 60)

    all_passed &= _test(
        "single FUNCTION_BLOCK",
        "FUNCTION_BLOCK FB1\nEND_FUNCTION_BLOCK",
        True,
    )
    all_passed &= _test(
        "single FUNCTION",
        "FUNCTION F1 : BOOL\nEND_FUNCTION",
        True,
    )
    all_passed &= _test(
        "single PROGRAM",
        "PROGRAM P1\nEND_PROGRAM",
        True,
    )
    all_passed &= _test(
        "single FUNCTION_BLOCK with body",
        "FUNCTION_BLOCK FB1\n  x := 1;\nEND_FUNCTION_BLOCK",
        True,
    )
    all_passed &= _test(
        "single FUNCTION with body",
        "FUNCTION F1 : BOOL\n  F1 := TRUE;\nEND_FUNCTION",
        True,
    )

    print()
    print("=" * 60)
    print("MULTIPLE UNIT PARSING")
    print("=" * 60)

    all_passed &= _test(
        "two FUNCTION_BLOCKs",
        "FUNCTION_BLOCK FB1\nEND_FUNCTION_BLOCK\n\nFUNCTION_BLOCK FB2\nEND_FUNCTION_BLOCK",
        True,
    )
    all_passed &= _test(
        "two FUNCTIONs",
        "FUNCTION F1 : BOOL\nEND_FUNCTION\n\nFUNCTION F2 : BOOL\nEND_FUNCTION",
        True,
    )
    all_passed &= _test(
        "mixed FUNCTION_BLOCK + FUNCTION",
        "FUNCTION_BLOCK FB1\nEND_FUNCTION_BLOCK\n\nFUNCTION F1 : BOOL\nEND_FUNCTION",
        True,
    )
    all_passed &= _test(
        "mixed FUNCTION + FUNCTION_BLOCK",
        "FUNCTION F1 : BOOL\nEND_FUNCTION\n\nFUNCTION_BLOCK FB1\nEND_FUNCTION_BLOCK",
        True,
    )
    all_passed &= _test(
        "FUNCTION + FUNCTION_BLOCK + PROGRAM",
        "FUNCTION F1 : BOOL\nEND_FUNCTION\n\nFUNCTION_BLOCK FB1\nEND_FUNCTION_BLOCK\n\nPROGRAM P1\nEND_PROGRAM",
        True,
    )

    print()
    print("=" * 60)
    print("EMPTY-BODY COMPILATION UNITS")
    print("=" * 60)

    all_passed &= _test(
        "empty FUNCTION_BLOCK with VAR",
        "FUNCTION_BLOCK FB1\n  VAR\n    x : INT;\n  END_VAR\nEND_FUNCTION_BLOCK",
        True,
    )
    all_passed &= _test(
        "empty FUNCTION with VAR_INPUT",
        "FUNCTION F1 : BOOL\n  VAR_INPUT\n    x : INT;\n  END_VAR\nEND_FUNCTION",
        True,
    )

    print()
    print("=" * 60)
    print("BACKWARD COMPATIBILITY")
    print("=" * 60)

    all_passed &= _test(
        "raw statement block (no compilation unit)",
        "x := 1;\ny := 2;",
        True,
    )
    all_passed &= _test(
        "raw IF statement",
        "IF x THEN y := 1; END_IF;",
        True,
    )

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
