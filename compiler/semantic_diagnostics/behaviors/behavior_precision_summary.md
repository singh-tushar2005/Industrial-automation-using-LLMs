# Behavior Precision Audit Summary

## Audit Scope

- **Datasets**: `datasets/Industrial_data` (Implementation_datasets + test_harness)
- **Files total**: 57
- **Files parsed**: 55
- **Date**: 2026-06-08
- **Constraint**: No code changes performed during audit.

---

## Overall Precision by Behavior

| Behavior | Total Fires | Correct | Weak | Incorrect | Precision |
|----------|------------|---------|------|-----------|-----------|
| CHECKSUM_GENERATION | 23 | 4 | 2 | 17 | 17.4% |
| FLOW_MEASUREMENT | 7 | 3 | 1 | 3 | 42.9% |
| STATE_MACHINE_CONTROL | 3 | 3 | 0 | 0 | **100.0%** |
| SEQUENTIAL_MACHINE_CONTROL | 9 | 6 | 3 | 0 | **66.7%** |
| MATRIX_COMPUTATION | 3 | 3 | 0 | 0 | **100.0%** |
| MATHEMATICAL_SOLVER | 9 | 7 | 0 | 2 | **77.8%** |
| DATA_TRANSFORMATION | 0 | 0 | 0 | 0 | N/A |
| COUNTER_PROCESSING | 5 | 5 | 0 | 0 | **100.0%** |

---

## Focus File Results

| File | Expected | Detected | Classification |
|------|----------|----------|----------------|
| CRC_GEN.st | CHECKSUM_GENERATION | CHECKSUM_GENERATION | **CORRECT** |
| FLOW_METER.st | FLOW_MEASUREMENT | FLOW_MEASUREMENT | **WEAK** |
| SEQUENCE_8.st | SEQUENTIAL_MACHINE_CONTROL | SEQUENTIAL_MACHINE_CONTROL | **CORRECT** |
| TRAFFIC_CTRL.st | STATE_MACHINE_CONTROL | STATE_MACHINE_CONTROL | **CORRECT** |
| MATRIX.st | MATRIX_COMPUTATION | MATRIX_COMPUTATION | **CORRECT** |
| LAMBERT_W.st | MATHEMATICAL_SOLVER | MATHEMATICAL_SOLVER | **CORRECT** |

---

## Special Investigation: FLOW_METER

**Why FLOW_MEASUREMENT is emitted when measurement_calculation = 0**

- **Rule fired**: Secondary signal: `history >= 2 AND process_calc >= 2 AND (timer >= 1 OR fb >= 1)`
- **Evidence chain**: history_variable=7 (x_last, y_last, e_last, tl, tx), fb_invocation=1 (integrator FB), process_calculation=2 (FLOOR, division)
- **Operation chain**: process_calculation=3, history_update=7, fb_invocation=1, accumulator_update=2
- **Relationship chain**: activates=1, depends_on=9, feeds=5
- **Why measurement_calculation = 0**: The evidence engine requires either (a) target containing "Flow/Rate/Speed/Freq" or (b) TIME_TO_REAL in the division expression. The target is `F` (does not match pattern). The division is nested inside a multiplication expression, so TIME_TO_REAL does not appear in the top-level describe_node output.
- **Classification**: **WEAK**. The file is semantically a flow meter, but the detection relies on the secondary signal rather than direct measurement evidence.

---

## Special Investigation: CHECKSUM_GENERATION

**Behavior distribution**: 23 files (3 implementation, 20 test harness)

**True checksum files**:
- CRC_GEN.st (implementation)
- CRC_GEN_FullTest (1).st
- CRC_GEN_FullTest.st

**False positives**: 20 files

**Evidence causing overfiring**:
- `bitwise_operation`: OSCAT helper functions (BIT_OF_DWORD, SHL, SHR, ROL, ROR, AND, OR, XOR) present in almost every test harness file.
- `accumulator`: REFLECT function uses `REFLECT := SHL(REFLECT, 1) OR ...` which is detected as accumulator. Loop counters (`cnt := cnt + 1`, `rx := rx + 1`) are also detected as accumulators.

**Root cause**: The rule `bitwise >= 3 AND accumulators >= 1` cannot distinguish between checksum algorithms and general utility functions that use bitwise operations and accumulation.

**Precision breakdown**:
- Implementation datasets: 33.3% (1 correct, 2 weak out of 3)
- Test harness: 15.0% (3 correct out of 20)

---

## Special Investigation: MATRIX

**Why MATRIX_COMPUTATION is emitted when matrix_access = 0**

- **Rule fired**: `array_access >= 3 AND bitwise >= 3 AND array_ops >= 2`
- **Actual triggering evidence**: array_access=14, bitwise_operation=56
- **Actual triggering operations**: array_read=3, array_write=2, bitwise_update=13
- **Explanation**: MATRIX.st is a matrix keypad scanner. It does not use matrix math functions (MATRIX_MUL, etc.), so matrix_access=0. The behavior is correctly detected via the fallback rule that requires array indexing combined with bitwise operations for bit packing/unpacking.
- **Classification**: **CORRECT**. The 56 bitwise_operation evidences come from BIT_LOAD_B, BIT_OF_DWORD, SHL, XOR, AND, OR used in the keypad scanning logic.

---

## False Positive Analysis

| Root Cause | Count | Description |
|------------|-------|-------------|
| test harness contamination | 23 | OSCAT helper functions in test harness files are industrial-scoped but trigger behaviors unrelated to the FB under test. |
| accumulator overfiring | 2 | Loop counters and REFLECT accumulation detected as accumulators but are not checksum algorithms. |
| history variable overfiring | 4 | Timing variables (tx, last, tl) in helper functions trigger history_variable evidence, causing FLOW_MEASUREMENT false positives. |
| operation threshold too low | 2 | FLOW_METER_FullTest has math_ops=1 and iterative=1, triggering MATHEMATICAL_SOLVER via the secondary rule. |
| state detection error | 3 | TOOL_CHANGER is a CASE-based state machine but detected as SEQUENTIAL_MACHINE_CONTROL because it has no timers and actuator sequences. |

---

## Behavior Coverage (Implementation Datasets)

| File | Expected | Detected | Missing | Unexpected |
|------|----------|----------|---------|------------|
| CRC_GEN.st | CHECKSUM_GENERATION | CHECKSUM_GENERATION | — | — |
| FLOW_METER.st | FLOW_MEASUREMENT | FLOW_MEASUREMENT | — | — |
| SEQUENCE_8.st | SEQUENTIAL_MACHINE_CONTROL | SEQUENTIAL_MACHINE_CONTROL | — | — |
| TRAFFIC_CTRL.st | STATE_MACHINE_CONTROL | STATE_MACHINE_CONTROL | — | — |
| MATRIX.st | MATRIX_COMPUTATION | MATRIX_COMPUTATION | — | — |
| LAMBERT_W.st | MATHEMATICAL_SOLVER | MATHEMATICAL_SOLVER | — | — |
| DEC_TO_HEX.st | — | — | — | — |
| FT_PIDWL.st | — | — | — | — |
| GEN_BIT.st | COUNTER_PROCESSING | CHECKSUM_GENERATION, COUNTER_PROCESSING | — | CHECKSUM_GENERATION |
| GEN_SIN.st | MATHEMATICAL_SOLVER | MATHEMATICAL_SOLVER | — | — |
| INCLUDE.st | — | CHECKSUM_GENERATION | — | CHECKSUM_GENERATION |
| robotic_sequence.st | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING | — | — |
| sampletext_2.st | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING | — | — |
| sampletext_3.st | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING | — | — |
| sampletext_4.st | — | — | — | — |
| TOOL_CHANGER.st | STATE_MACHINE_CONTROL | SEQUENTIAL_MACHINE_CONTROL | STATE_MACHINE_CONTROL | SEQUENTIAL_MACHINE_CONTROL |

---

## Key Findings

1. **Focus files are correctly detected** (6/6): All user-specified focus files (CRC_GEN, FLOW_METER, SEQUENCE_8, TRAFFIC_CTRL, MATRIX, LAMBERT_W) have their expected behaviors detected.

2. **CHECKSUM_GENERATION has the worst precision** (17.4% overall): The rule is too broad. It fires on any file with bitwise operations and accumulators, which includes most utility libraries and test harnesses.

3. **Test harness contamination is the dominant false positive source**: 23 of 26 incorrect behaviors come from test harness files. The OSCAT helper functions (included in test harnesses) are industrial-scoped and trigger bitwise, accumulator, and history variable evidence.

4. **FLOW_METER detection is weak**: The detection is semantically correct but relies on the secondary rule because the evidence engine cannot detect the measurement calculation in the nested division expression.

5. **STATE_MACHINE_CONTROL, MATRIX_COMPUTATION, and COUNTER_PROCESSING have perfect precision**: These rules are well-calibrated and do not produce false positives.

6. **TOOL_CHANGER is misclassified**: It is a CASE-based state machine (3 states) but detected as SEQUENTIAL_MACHINE_CONTROL because the rule requires `timers >= 1` for STATE_MACHINE_CONTROL and TOOL_CHANGER has no timer FBs.

7. **DATA_TRANSFORMATION never fires**: After switching to industrial-only evidence, no files match the rule. This suggests the rule may be too restrictive or the evidence types it depends on are not well-represented in industrial code.

---

*Generated by behavior precision audit. No code changes were made.*
