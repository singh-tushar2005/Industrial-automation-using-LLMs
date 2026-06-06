# Pattern Precision Summary

## Executive Summary

The Pattern Library detects 2,983 patterns across 57 industrial datasets. Manual audit reveals an estimated **overall precision of 10.7%** (320 true positives vs 2,663 false positives). Test harness files dominate detections (92.9% of all patterns) and account for the majority of false positives.

| Pattern | Total | TP | FP | Precision | Depth |
|---|---|---|---|---|---|
| StateTransitionPattern | 290 | 96 | 194 | 33.1% | 1 |
| CounterUpdatePattern | 634 | 62 | 572 | 9.8% | 2 |
| HistoryUpdatePattern | 236 | 190 | 46 | 80.5% | 1 |
| AccumulatorPattern | 612 | 65 | 547 | 10.6% | 2 |
| ArrayAccessPattern | 203 | 175 | 28 | 86.2% | 2 |
| MatrixAccessPattern | 55 | 0 | 55 | 0.0% | 1 |
| BitwiseUpdatePattern | 82 | 78 | 4 | 95.1% | 2 |
| RateCalculationPattern | 0 | 0 | 0 | 0.0% | 1 |
| ProcessCalculationPattern | 14 | 10 | 4 | 71.4% | 2 |
| FunctionBlockInvocationPattern | 857 | 52 | 805 | 6.1% | 2 |

## Key Findings

### 1. Test Harness Contamination

92.9% of all pattern detections occur in test harness files (Full_test and TestCases). Test scaffolding variables (TestState, totalTests, passedTests, TestBlock, Timer) produce thousands of false positives that drown out real industrial semantics.

### 2. Catastrophic Substring Bug: MatrixAccessPattern

MatrixAccessPattern uses the target heuristic `("Matrix", "matrix", "mat", "_M", "_A", "_B", "_C", "Result")`. The substring `_B` matches `BIT_LOAD_B`, `_C` matches `_CRC_GEN`, and the single-letter matches `A`, `B`, `C`, `M` match almost any expression containing `AND`, `BYTE`, `CRC`, or `SHR`. The pattern detected **0 true positives** across all 57 datasets.

### 3. Dead Pattern: RateCalculationPattern

RateCalculationPattern detected **0 patterns** across all datasets because the heuristics (target must contain `Flow/Rate/Speed/Freq`, sources must contain `delta/time/dt/period/pulse/count`) do not match real industrial code. The FLOW_METER rate calculation (`F := (UDINT_TO_REAL(Y - y_last) + X - x_last) / TIME_TO_REAL(tx - tl) * 3.6E6`) is missed because target `F` and sources `tx`, `tl` do not match the heuristic.

### 4. Severe Overlap: CounterUpdatePattern vs AccumulatorPattern

Both patterns match generic self-increment arithmetic (`target := target + value`). In implementation datasets, `X := X + VX` (FLOW_METER accumulator) is matched by both CounterUpdatePattern and AccumulatorPattern. In test harness files, `TestState := TestState + 1` is matched by CounterUpdatePattern, AccumulatorPattern, and StateTransitionPattern simultaneously.

### 5. 100% Redundancy with OperationExtractor

Every pattern detection has a corresponding operation in the OperationExtractor. The Pattern Library adds **zero new semantic information**. The OperationExtractor already captures state_update, counter_update, history_update, accumulator_update, array_read, array_write, matrix_access, bitwise_update, measurement_calculation, process_calculation, mathematical_solver, timer_invocation, counter_invocation, and fb_invocation.

## Implementation Dataset Precision

When restricted to the 16 implementation datasets (real industrial code, no test scaffolding), precision rises to **69.8%** (148 TP / 212 total). The remaining 30% false positives are mostly loop iterators (`pos := pos + 1`), mathematical floor functions (`floor := floor - 1`), and time accumulators (`last := last + pt`).

## Conclusion

The Pattern Library is a diagnostic tool that rediscovers syntax-level operations already captured by the OperationExtractor. Its naming heuristics are too broad, producing massive false positives in test harness files. The MatrixAccessPattern and RateCalculationPattern are broken. The FunctionBlockInvocationPattern is entirely redundant. With targeted rewrites, 3 patterns could be salvaged; the rest should be removed or rewritten.
