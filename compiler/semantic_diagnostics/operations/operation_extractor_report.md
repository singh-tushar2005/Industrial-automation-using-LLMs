# Operation Extractor Validation Report

## 1. Semantic Coverage

| Metric | Before | After | Δ |
|---|---|---|---|
| Coverage % | 33.5% | 77.1% | +43.6pp |
| Executable statements | 105 | 105 | 0 |
| Covered statements | 35 | 81 | +46 |
| Uncovered statements | 69 | 24 | -45 |

## 2. Operations Detected

**Total operations extracted:** 877

| Operation Type | Count |
|---|---|
| data_movement | 543 |
| comparison_operation | 216 |
| process_calculation | 102 |
| lookup_operation | 9 |
| iterative_computation | 7 |

## 3. Per-Dataset Operations

| Dataset | Executable | Covered | Operations | Coverage % |
|---|---|---|---|---|
| CRC_GEN.st | 9 | 6 | 25 | 66.7% |
| FLOW_METER.st | 8 | 5 | 25 | 62.5% |
| FT_PIDWL.st | 1 | 1 | 8 | 100.0% |
| GEN_BIT.st | 1 | 1 | 39 | 100.0% |
| GEN_SIN.st | 8 | 5 | 15 | 62.5% |
| INCLUDE.st | 27 | 23 | 63 | 85.2% |
| LAMBERT_W.st | 3 | 1 | 11 | 33.3% |
| MATRIX.st | 17 | 15 | 32 | 88.2% |
| SEQUENCE_8.st | 14 | 13 | 85 | 92.9% |
| TOOL_CHANGER.st | 1 | 1 | 13 | 100.0% |
| TRAFFIC_CTRL.st | 3 | 3 | 35 | 100.0% |
| robotic_sequence.st | 4 | 2 | 127 | 50.0% |
| sampletext_2.st | 4 | 2 | 199 | 50.0% |
| sampletext_3.st | 4 | 2 | 199 | 50.0% |
| sampletext_4.st | 1 | 1 | 1 | 100.0% |

## 4. Previously Empty, Now With Operations

Datasets that previously produced **0 nodes / 0 edges** but now produce operations:

- CRC_GEN.st
- LAMBERT_W.st
- MATRIX.st
- sampletext_4.st

## 5. Key Improvements

1. **CRC_GEN**: Previously 0% coverage (pure algorithm). Now extracts process_calculation, comparison_operation, iterative_computation, data_movement, lookup_operation.
2. **LAMBERT_W**: Previously 0% coverage (mathematical solver). Now extracts process_calculation and comparison_operation.
3. **MATRIX**: Previously 0% coverage (matrix operations). Now extracts process_calculation and iterative_computation.
4. **FLOW_METER**: Previously 37.5% coverage. Now extracts additional process_calculation and comparison_operation.
5. **GEN_SIN**: Previously 0% coverage. Now extracts process_calculation and iterative_computation.

## 6. Coverage Gap Analysis

The remaining uncovered executable logic is primarily:
- `FunctionBlockCallNode` (timer/counter calls) — already handled by RelationshipExtractor, but not counted as "covered" by the operation heuristic because they do not generate operations in Phase 1.
- `ReturnNode` — not covered.
- `FunctionInvocationNode` inside complex expressions — not individually extracted.
