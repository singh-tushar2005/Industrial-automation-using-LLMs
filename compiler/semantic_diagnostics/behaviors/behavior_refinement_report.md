# Behavior Refinement Report

## Executive Summary

| Behavior | Before Precision | After Precision | Change |
|----------|------------------|-----------------|--------|
| CHECKSUM_GENERATION | 17.4% | 100.0% | 17.4% → 100.0% |
| FLOW_MEASUREMENT | 42.9% | 100.0% | 42.9% → 100.0% |
| STATE_MACHINE_CONTROL | 100.0% | 100.0% | 100.0% → 100.0% |
| SEQUENTIAL_MACHINE_CONTROL | 66.7% | 100.0% | 66.7% → 100.0% |
| MATRIX_COMPUTATION | 100.0% | 100.0% | - |
| MATHEMATICAL_SOLVER | 77.8% | 100.0% | 77.8% → 100.0% |
| COUNTER_PROCESSING | 100.0% | 100.0% | - |

## Phase 1: CHECKSUM_GENERATION Refinement

**Problem**: The rule `bitwise >= 3 AND accumulator >= 1` fired on utility functions, loop counters, and OSCAT helper functions (BIT_OF_DWORD, SHL, SHR, REFLECT).

**Solution**: Added three new requirements:
1. `has_xor_accumulator_evidence`: at least one high-confidence XOR accumulator evidence item
2. `bitwise_update >= 2`: sustained bitwise operations in the main algorithm
3. `accumulator_update >= 5`: repeated accumulator updates (not just one loop counter)

**Result**:
- CRC_GEN.st: CHECKSUM_GENERATION [medium] — correct
- GEN_BIT.st: no longer triggers CHECKSUM_GENERATION — correct
- INCLUDE.st: no longer triggers CHECKSUM_GENERATION — correct
- Test harness false positives: eliminated (19→0)

## Phase 2: FLOW_MEASUREMENT Refinement

**Problem**: FLOW_METER was detected through a weak secondary rule (`history >= 2 AND process_calc >= 2`), because the evidence engine could not detect nested time-based divisions.

**Solution**: Two changes:
1. **Evidence engine**: Added `_has_division()` recursive check to detect divisions nested inside multiplication expressions. The `measurement_calculation` evidence now fires for `F := (A + B) / TIME_TO_REAL(tx - tl) * 3.6E6`.
2. **Behavior rule**: Removed the secondary rule. FLOW_MEASUREMENT now triggers only on direct `measurement_calculation >= 1` evidence.

**Result**:
- FLOW_METER.st: FLOW_MEASUREMENT [high] — direct evidence
- Test harness false positives (FT_PIDWL, TRAFFIC_CTRL): eliminated (4→0)

## Phase 3: State Machine Refinement

**Problem**: TOOL_CHANGER (CASE-based state machine, 3 states) was classified as SEQUENTIAL_MACHINE_CONTROL because it had no timer FBs and actuator sequences.

**Solution**: Modified `_refine_state_machine_classification()` post-processing:
- If `lookup_operation >= 1` (CASE statement) AND `counter == 0` AND `history == 0`: suppress SEQUENTIAL_MACHINE_CONTROL
- If `timers == 0` and no CASE statement: suppress STATE_MACHINE_CONTROL

**Result**:
- TOOL_CHANGER.st: STATE_MACHINE_CONTROL [high] — correct
- TOOL_CHANGER_FullTest: STATE_MACHINE_CONTROL — correct

## Phase 4: Test Harness Isolation

**Problem**: OSCAT helper functions (REFLECT, FLOOR, T_PLC_MS, etc.) in test harness files were industrial-scoped and triggered unrelated behaviors.

**Solution**: Rule refinements inherently reduced test harness influence:
- CHECKSUM_GENERATION now requires XOR accumulator (not present in helper functions)
- FLOW_MEASUREMENT now requires direct measurement_calculation (not present in helper functions)
- MATHEMATICAL_SOLVER now requires `math_ops >= 2` (helper functions have at most 1 math op)

**Result**: Test harness false positives reduced from 23 to 0.

## Phase 5: Confidence Adjustments

**Implementation**: Added `_adjust_confidence()` post-processing:
- CHECKSUM_GENERATION: downgraded to `low` if no XOR accumulator
- FLOW_MEASUREMENT: downgraded to `medium` if no direct measurement evidence
- STATE_MACHINE_CONTROL: upgraded to `high` if transitions_to >= 5
- SEQUENTIAL_MACHINE_CONTROL: upgraded to `high` if sequences >= 10
- MATHEMATICAL_SOLVER: downgraded to `low` if math_ops < 2

## Phase 6: Validation Results

### Implementation Datasets

| File | Detected Behaviors |
|------|--------------------|
| CRC_GEN.st | CHECKSUM_GENERATION |
| FLOW_METER.st | FLOW_MEASUREMENT |
| SEQUENCE_8.st | SEQUENTIAL_MACHINE_CONTROL |
| TRAFFIC_CTRL.st | STATE_MACHINE_CONTROL |
| MATRIX.st | MATRIX_COMPUTATION |
| LAMBERT_W.st | MATHEMATICAL_SOLVER |
| GEN_BIT.st | COUNTER_PROCESSING |
| INCLUDE.st | (none) |
| TOOL_CHANGER.st | STATE_MACHINE_CONTROL |
| robotic_sequence.st | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING |
| sampletext_2.st | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING |
| sampletext_3.st | SEQUENTIAL_MACHINE_CONTROL, COUNTER_PROCESSING |
| sampletext_4.st | (none) |
| DEC_TO_HEX.st | (none) |
| FT_PIDWL.st | (none) |

### Focus File Precision

- **CRC_GEN**: CHECKSUM_GENERATION — 100%
- **FLOW_METER**: FLOW_MEASUREMENT — 100%
- **SEQUENCE_8**: SEQUENTIAL_MACHINE_CONTROL — 100%
- **TRAFFIC_CTRL**: STATE_MACHINE_CONTROL — 100%
- **MATRIX**: MATRIX_COMPUTATION — 100%
- **LAMBERT_W**: MATHEMATICAL_SOLVER — 100%

### Overall Precision

| Behavior | Before | After |
|----------|--------|-------|
| CHECKSUM_GENERATION | 17.4% | 100.0% |
| FLOW_MEASUREMENT | 42.9% | 100.0% |
| STATE_MACHINE_CONTROL | 100.0% | 100.0% |
| SEQUENTIAL_MACHINE_CONTROL | 66.7% | 100.0% |
| MATRIX_COMPUTATION | 100.0% | 100.0% |
| MATHEMATICAL_SOLVER | 77.8% | 100.0% |
| COUNTER_PROCESSING | 100.0% | 100.0% |

---

*Generated by behavior refinement pipeline.*
