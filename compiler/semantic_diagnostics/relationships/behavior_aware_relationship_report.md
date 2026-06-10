# Behavior-Aware Relationship Refinement Report

## Phase 7: Validation Summary

- **Files analyzed:** 55
- **Total industrial relationships (before):** 1344
- **Total industrial relationships (after):** 992
- **Delta:** -352
- **Percentage change:** -26.19%

## Before vs After Per Relationship Type

| Relation | Before | After | Delta | Suppressed | New Edges |
|----------|--------|-------|-------|------------|----------|
| activates | 158 | 84 | -74 | 40 | 6 |
| contains | 40 | 16 | -24 | 24 | 0 |
| controls | 127 | 93 | -34 | 26 | 0 |
| coordinates | 0 | 3 | +3 | 0 | 3 |
| depends_on | 525 | 60 | -465 | 362 | 0 |
| disables | 3 | 3 | +0 | 0 | 0 |
| feeds | 0 | 135 | +135 | 0 | 135 |
| schedules | 0 | 56 | +56 | 0 | 28 |
| sequences | 368 | 273 | -95 | 95 | 0 |
| transitions_to | 57 | 141 | +84 | 0 | 84 |
| triggers | 46 | 24 | -22 | 40 | 18 |
| uses | 20 | 104 | +84 | 20 | 104 |

## Key Findings

### 1. depends_on Drastically Reduced
- **Before:** 525 edges
- **After:** 60 edges
- **Suppressed:** 362 edges
- **Reason:** Behavior-aware filtering suppresses low-value dependencies (bookkeeping, history, temporary, mode variables) for all behaviors. Files with SEQUENTIAL_MACHINE_CONTROL or STATE_MACHINE_CONTROL no longer emit generic depends_on edges.

### 2. Evidence and Operation Rules Added Semantic Edges
- **transitions_to:** +84 new edges from state_transition evidence/operations
- **feeds:** +135 new edges from history_variable and FB chaining evidence
- **uses:** +104 new edges from bitwise_operation and fb_invocation evidence
- **schedules:** +28 new edges from timer evidence/operations

### 3. controls Reduced Without Explosion
- **Before:** 127 edges
- **After:** 93 edges
- **Suppressed:** 26 edges
- **Max controls in single file:** 31 (in Implementation_datasets/SEQUENCE_8.st)
- **Control path explosion:** NOT DETECTED

### 4. sequences Reduced
- **Before:** 368 edges
- **After:** 273 edges
- **Suppressed:** 95 edges
- **Reason:** Behavior-aware filtering suppresses weak sequencing edges in test harness files and embedded logic.

## Confidence Distribution (After)

| Confidence | Count |
|------------|-------|
| low | 554 |
| medium | 1154 |

## Source Distribution (After)

| Source | Count |
|--------|-------|
| AST_RULE | 1019 |
| EVIDENCE_RULE | 503 |
| OPERATION_RULE | 186 |

## Behavior Support Distribution (After)

| Behavior | Supported Edges |
|----------|------------------|
| CHECKSUM_GENERATION | 53 |
| COUNTER_PROCESSING | 244 |
| FLOW_MEASUREMENT | 69 |
| MATHEMATICAL_SOLVER | 112 |
| MATRIX_COMPUTATION | 59 |
| SEQUENTIAL_MACHINE_CONTROL | 428 |
| STATE_MACHINE_CONTROL | 161 |

## Special Investigation: SEQUENCE_8

### Implementation_datasets/SEQUENCE_8.st
- **Before:** 109 edges
- **After:** 66 edges
- **Delta:** -43

| Relation | Before | After | Delta |
|----------|--------|-------|-------|
| activates | 8 | 8 | +0 |
| controls | 31 | 31 | +0 |
| depends_on | 52 | 0 | -52 |
| disables | 1 | 1 | +0 |
| sequences | 16 | 16 | +0 |
| transitions_to | 0 | 9 | +9 |
| triggers | 1 | 1 | +0 |

**Suppressed Edges:**
- `_step depends_on status`
- `start depends_on run`
- `in2 depends_on last`
- `init depends_on status`
- `in0 depends_on last`
- `_step depends_on q4`
- `in1 depends_on last`
- `edge depends_on run`
- `_step depends_on q6`
- `start depends_on status`
- ... and 20 more

**New Edges:**
- `_step transitions_to -1`
- `_step transitions_to 7`
- `_step transitions_to 4`
- `_step transitions_to 5`
- `_step transitions_to 1`
- `_step transitions_to 2`
- `_step transitions_to 0`
- `_step transitions_to 6`
- `_step transitions_to 3`

### test_harness/Full_test/SEQUENCE_8_FullTest (1).st
- **Before:** 129 edges
- **After:** 67 edges
- **Delta:** -62

| Relation | Before | After | Delta |
|----------|--------|-------|-------|
| activates | 10 | 8 | -2 |
| contains | 2 | 0 | -2 |
| controls | 31 | 31 | +0 |
| depends_on | 63 | 0 | -63 |
| disables | 1 | 1 | +0 |
| sequences | 19 | 17 | -2 |
| transitions_to | 0 | 9 | +9 |
| triggers | 2 | 1 | -1 |
| uses | 1 | 0 | -1 |

**Suppressed Edges:**
- `_step depends_on status`
- `init depends_on X_last`
- `instance0 uses TestRunnerProgram`
- `testState sequences TestState`
- `start depends_on run`
- `in2 depends_on last`
- `testState sequences Finished`
- `init depends_on tc`
- `init depends_on status`
- `in0 depends_on last`
- ... and 38 more

**New Edges:**
- `_step transitions_to -1`
- `_step transitions_to 7`
- `_step transitions_to 4`
- `_step transitions_to 5`
- `_step transitions_to 1`
- `_step transitions_to 2`
- `_step transitions_to 0`
- `_step transitions_to 6`
- `_step transitions_to 3`

### test_harness/Full_test/SEQUENCE_8_FullTest.st
- **Before:** 129 edges
- **After:** 67 edges
- **Delta:** -62

| Relation | Before | After | Delta |
|----------|--------|-------|-------|
| activates | 10 | 8 | -2 |
| contains | 2 | 0 | -2 |
| controls | 31 | 31 | +0 |
| depends_on | 63 | 0 | -63 |
| disables | 1 | 1 | +0 |
| sequences | 19 | 17 | -2 |
| transitions_to | 0 | 9 | +9 |
| triggers | 2 | 1 | -1 |
| uses | 1 | 0 | -1 |

**Suppressed Edges:**
- `_step depends_on status`
- `init depends_on X_last`
- `instance0 uses TestRunnerProgram`
- `testState sequences TestState`
- `start depends_on run`
- `in2 depends_on last`
- `testState sequences Finished`
- `init depends_on tc`
- `init depends_on status`
- `in0 depends_on last`
- ... and 38 more

**New Edges:**
- `_step transitions_to -1`
- `_step transitions_to 7`
- `_step transitions_to 4`
- `_step transitions_to 5`
- `_step transitions_to 1`
- `_step transitions_to 2`
- `_step transitions_to 0`
- `_step transitions_to 6`
- `_step transitions_to 3`

### test_harness/test_case/SEQUENCE_8_TestCases (1).st
- **Before:** 6 edges
- **After:** 3 edges
- **Delta:** -3

| Relation | Before | After | Delta |
|----------|--------|-------|-------|
| activates | 2 | 0 | -2 |
| schedules | 0 | 2 | +2 |
| sequences | 3 | 1 | -2 |
| triggers | 1 | 0 | -1 |

**Suppressed Edges:**
- `Timer.Q activates TestState`
- `Timer triggers testState`
- `testState sequences Finished`
- `testState sequences TestState`

**New Edges:**
- `Timer schedules time_event`

### test_harness/test_case/SEQUENCE_8_TestCases.st
- **Before:** 6 edges
- **After:** 3 edges
- **Delta:** -3

| Relation | Before | After | Delta |
|----------|--------|-------|-------|
| activates | 2 | 0 | -2 |
| schedules | 0 | 2 | +2 |
| sequences | 3 | 1 | -2 |
| triggers | 1 | 0 | -1 |

**Suppressed Edges:**
- `Timer.Q activates TestState`
- `Timer triggers testState`
- `testState sequences Finished`
- `testState sequences TestState`

**New Edges:**
- `Timer schedules time_event`

## Conclusion

The behavior-aware relationship refinement successfully reduced total industrial relationships from 1344 to 992 (-352 edges, 26.19%).

Key achievements:
- **Low-value depends_on suppression:** 465 generic dependencies removed.
- **Evidence-driven enrichment:** 275 new edges from semantic evidence and operations (transitions_to, feeds, uses, schedules).
- **Control path explosion prevention:** Max controls per file capped at 31 (well below 100 threshold).
- **Test harness isolation:** Expanded test-harness entity detection prevents test logic from polluting industrial relationships.
- **SEQUENCE_8 stability:** Industrial edges reduced from 109 to 66 in implementation; from 129 to 67 in full test harness.
