# Behavior Coverage Gap Report

Scope: `datasets/Industrial_data/Implementation_datasets`.

This report intentionally ignores `datasets/Industrial_data/test_harness` as requested. It uses the existing intent audit outputs and does not modify parser, AST, visitor infrastructure, relationship extraction, intent reasoning, dependency reasoning, or behavior recognition.

## Summary

- Parsed Industrial_data files in current intent audit: 55
- Current `GENERAL_PROCESS_CONTROL` fallback files: 20
- Fallback files in `Implementation_datasets`: 2
- Fallback files in `test_harness`: 18

Because only 2 fallback files are in `Implementation_datasets`, behavior coverage changes scoped to implementation datasets can reduce the fallback count from 20 to at best 18. The requested target of `<10` cannot be reached while ignoring `test_harness`.

## Priority Findings

### FT_PIDWL.st

Why no behavior is emitted:

- Existing behavior recognizers do not have a rule for function-block composition with output limiting.
- `DATA_TRANSFORMATION` currently requires array access plus process calculation or function-block invocation. This file has function-block invocation, data movement, calculation, activation, and coordination relationships, but no array access.
- `MATHEMATICAL_SOLVER` requires at least two `mathematical_solver` operations. This file has arithmetic/process calculation but no advanced solver operations.
- No state, sequence, counter, flow-measurement, matrix, or checksum evidence is present.

Detected evidence:

- `fb_invocation=4`
- `comparison=2`

Detected operations:

- `comparison_operation=3`
- `fb_invocation=4`
- `data_movement=4`
- `process_calculation=1`

Detected relationships:

- `activates=2`
- `coordinates=1`

Current behaviors:

- `<none>`

Missing behavior:

- Existing family fit: `DATA_TRANSFORMATION`, if broadened to include non-array data transformation through function-block composition.
- Candidate semantic pattern: `fb_invocation >= 2` plus `data_movement >= 2` plus `process_calculation >= 1` plus `activates` or `coordinates`.

Recommended action:

- Reuse `DATA_TRANSFORMATION`; do not create a new behavior.
- Add a secondary `DATA_TRANSFORMATION` recognition path for computed function-block composition, independent of array access.
- Expected impact: likely removes fallback for `FT_PIDWL.st` and related full-test variants, but implementation-only impact is 1 file.

### sampletext_4.st

Why no behavior is emitted:

- The file is a boolean condition aggregation expressed as one logical/bitwise assignment.
- `CHECKSUM_GENERATION` correctly does not fire because there is no repeated XOR accumulator pattern.
- `DATA_TRANSFORMATION` correctly does not fire because there is no array access, function-block invocation, process calculation, or data movement distribution.
- Existing behavior families do not include condition aggregation, alarm predicate synthesis, or generic logical monitoring behavior.

Detected evidence:

- `bitwise_operation=1`

Detected operations:

- `bitwise_update=1`

Detected relationships:

- `uses=1`

Current behaviors:

- `<none>`

Missing behavior:

- Existing family fit: none.
- A possible new behavior would be condition aggregation or predicate synthesis, but only one implementation fallback currently requires it.

Recommended action:

- Do not add a new behavior under the stated rule requiring at least two implementation datasets.
- Do not force this into `CHECKSUM_GENERATION` or `DATA_TRANSFORMATION`; that would reduce precision.
- Keep as fallback unless another implementation dataset with the same semantic pattern is identified.

## Implementation Fallback Files

| File | Evidence | Operations | Relationships | Current Behaviors | Missing Behavior | Recommended Action |
|---|---|---|---|---|---|---|
| `FT_PIDWL.st` | `fb_invocation=4`, `comparison=2` | `comparison_operation=3`, `fb_invocation=4`, `data_movement=4`, `process_calculation=1` | `activates=2`, `coordinates=1` | none | Computed FB composition fits broadened `DATA_TRANSFORMATION` | Reuse `DATA_TRANSFORMATION`; add non-array FB composition rule later |
| `sampletext_4.st` | `bitwise_operation=1` | `bitwise_update=1` | `uses=1` | none | Boolean condition aggregation has no existing family fit | No change now; new behavior is not justified by only one implementation dataset |

## No/Weak Behavior Context

The following implementation files have no behavior or medium-confidence behavior, but only two of them currently fall back:

| File | Intent | Current Behaviors | Note |
|---|---|---|---|
| `CRC_GEN.st` | `DATA_INTEGRITY_VERIFICATION` | `CHECKSUM_GENERATION [medium]` | Already non-fallback; checksum behavior exists but confidence is limited by relationship support. |
| `FLOW_METER.st` | `RATE_BASED_MEASUREMENT` | `FLOW_MEASUREMENT [medium]` | Already non-fallback; direct measurement evidence is present. |
| `FT_PIDWL.st` | `GENERAL_PROCESS_CONTROL` | none | Implementation behavior gap. |
| `GEN_SIN.st` | `NUMERICAL_SOLVING` | `MATHEMATICAL_SOLVER [medium]` | Already non-fallback. |
| `INCLUDE.st` | `DATA_INTEGRITY_VERIFICATION` | none | Already non-fallback because intent support is strong; behavior recognizer misses checksum-like support due to strict XOR accumulator requirement. |
| `MATRIX.st` | `MATRIX_PROCESSING` | `MATRIX_COMPUTATION [medium]` | Already non-fallback. |
| `TOOL_CHANGER.st` | `STATE_BASED_CONTROL` | none | Already non-fallback because state/transition support is strong. |
| `sampletext_4.st` | `GENERAL_PROCESS_CONTROL` | none | Implementation behavior gap, but not enough evidence to justify a new behavior family. |

## Minimum Behavior Gaps

Minimum implementation-scoped behavior gaps:

1. Broaden `DATA_TRANSFORMATION` to cover computed function-block composition.
   - Supported by `FT_PIDWL.st`.
   - Uses an existing behavior family.
   - Does not require new behavior taxonomy.

2. Condition aggregation / logical predicate synthesis.
   - Supported by `sampletext_4.st` only.
   - No existing family cleanly represents it.
   - Does not meet the rule for creating a new behavior because fewer than two implementation datasets require it.

## Stop-Condition Assessment

No implementation-only behavior gap set can reduce total `GENERAL_PROCESS_CONTROL` from 20 to `<10`, because 18 of the 20 fallback files are in `test_harness`, which is out of scope for this task.

Under the requested scope, the maximum defensible implementation-only reduction is:

- Current total fallback: 20
- If `FT_PIDWL.st` is addressed by reusing `DATA_TRANSFORMATION`: 19
- If `sampletext_4.st` is also addressed by a future justified behavior: 18

Therefore, the `<10` target requires analyzing `test_harness` fallbacks or changing the task scope. No behavior changes were implemented.
