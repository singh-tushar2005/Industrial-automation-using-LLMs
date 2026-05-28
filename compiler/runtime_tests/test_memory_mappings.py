"""Isolated runtime grammar test suite for AT memory mappings.

Run: python -m compiler.runtime_tests.test_memory_mappings
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
    print("MEMORY MAPPING GRAMMAR")
    print("=" * 60)

    all_passed &= _test("AT %QX0.0", "PROGRAM P\nVAR\nOutput AT %QX0.0 : BOOL;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("AT %IW100", "PROGRAM P\nVAR\nInput AT %IW100 : INT;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("AT %MB0", "PROGRAM P\nVAR\nByte AT %MB0 : BYTE;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("AT %MD10", "PROGRAM P\nVAR\nDword AT %MD10 : DWORD;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("AT %MX0.1", "PROGRAM P\nVAR\nBit AT %MX0.1 : BOOL;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("AT %MW50", "PROGRAM P\nVAR\nWord AT %MW50 : WORD;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("multiple AT mappings", "PROGRAM P\nVAR\nOut1 AT %QX0.0 : BOOL;\nOut2 AT %QX0.1 : BOOL;\nEND_VAR\nEND_PROGRAM", True)
    all_passed &= _test("AT in FUNCTION_BLOCK", "FUNCTION_BLOCK FB1\nVAR\nOutput AT %QX0.0 : BOOL;\nEND_VAR\nEND_FUNCTION_BLOCK", True)

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
