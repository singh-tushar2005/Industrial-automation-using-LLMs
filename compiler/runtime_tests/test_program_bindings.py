"""Isolated runtime grammar test suite for PROGRAM bindings.

Run: python -m compiler.runtime_tests.test_program_bindings
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
    print("PROGRAM BINDING GRAMMAR")
    print("=" * 60)

    all_passed &= _test("PROGRAM binding with TASK", "CONFIGURATION C\nPROGRAM Instance0 WITH task0 : MainProgram;\nEND_CONFIGURATION", True)
    all_passed &= _test("PROGRAM binding without TASK", "CONFIGURATION C\nPROGRAM Instance0 : MainProgram;\nEND_CONFIGURATION", True)
    all_passed &= _test("multiple PROGRAM bindings", "CONFIGURATION C\nPROGRAM Inst0 WITH t0 : Prog0;\nPROGRAM Inst1 WITH t1 : Prog1;\nEND_CONFIGURATION", True)
    all_passed &= _test("PROGRAM binding inside RESOURCE", "CONFIGURATION C\nRESOURCE PLC0 ON PLC\nPROGRAM Instance0 WITH task0 : MainProgram;\nEND_RESOURCE\nEND_CONFIGURATION", True)
    all_passed &= _test("PROGRAM binding with different types", "CONFIGURATION C\nPROGRAM Instance0 WITH task0 : FBType;\nEND_CONFIGURATION", True)

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
