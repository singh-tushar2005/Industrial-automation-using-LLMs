"""Isolated runtime grammar test suite for CONFIGURATION declarations.

Run: python -m compiler.runtime_tests.test_configuration
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parser.st_parser import parse_st_program
from parser.st_parser import ConfigurationNode, BlockNode


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
    print("CONFIGURATION GRAMMAR")
    print("=" * 60)

    all_passed &= _test("empty CONFIGURATION", "CONFIGURATION Config0\nEND_CONFIGURATION", True)
    all_passed &= _test("CONFIGURATION with name", "CONFIGURATION MyConfig\nEND_CONFIGURATION", True)
    all_passed &= _test("CONFIGURATION with TASK", "CONFIGURATION Config0\nTASK t0(INTERVAL := T#100ms, PRIORITY := 0);\nEND_CONFIGURATION", True)
    all_passed &= _test("CONFIGURATION with RESOURCE", "CONFIGURATION Config0\nRESOURCE PLC0 ON PLC\nEND_RESOURCE\nEND_CONFIGURATION", True)
    all_passed &= _test("CONFIGURATION with PROGRAM binding", "CONFIGURATION Config0\nPROGRAM Instance0 WITH task0 : MainProgram;\nEND_CONFIGURATION", True)
    all_passed &= _test("CONFIGURATION with VAR block", "CONFIGURATION Config0\nVAR\n  x : INT;\nEND_VAR\nEND_CONFIGURATION", True)
    all_passed &= _test("nested RESOURCE + TASK + PROGRAM", "CONFIGURATION Config0\nRESOURCE PLC0 ON PLC\nTASK t0(INTERVAL := T#100ms, PRIORITY := 0);\nPROGRAM Instance0 WITH t0 : MainProgram;\nEND_RESOURCE\nEND_CONFIGURATION", True)

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
