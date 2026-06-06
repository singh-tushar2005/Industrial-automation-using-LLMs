# Pattern Library Architectural Recommendations

## Audit Basis

These recommendations are derived from a manual precision audit of 2,983 pattern detections across 57 industrial datasets (16 implementation datasets + 41 test harness files). Overall precision: 10.7%. Implementation-only precision: 69.8%. Every pattern is 100% redundant with the existing OperationExtractor.

---

## StateTransitionPattern

**Recommendation: REWRITE**

**Current State:** Naming heuristic on target variable. Matches any AssignmentNode where the target contains `Step`, `State`, `Sequence`, `_step`, `ToolChangeState`, `LightState`, `StartupStep`, or `BatchStep`.

**Problems:**
- Test scaffolding variable `TestState` generates 194 false positives in test harness files.
- `testState` (lowercase) is also matched because the heuristic is case-sensitive on substring but `testState` contains the capitalized substring `State`.
- No context awareness: cannot distinguish between a real industrial state machine (TRAFFIC_CTRL LightState) and a test loop counter (TestState).

**Justification:** The pattern is 33.1% precise overall. In implementation datasets it is 100% precise (48/48 real state machines), but test harness contamination destroys utility. The concept is sound but the detection rule is too permissive.

**Required Rewrite:**
1. Add a blacklist for test variables (`TestState`, `testState`, `test_step`).
2. Require context: the target must be assigned inside a CASE statement or must be guarded by IF conditions that branch to different constant values.
3. Downgrade confidence to `medium` for targets that only contain `State` (not `_step`, `Step`, `Sequence`).
4. Remove `BatchStep` from the heuristic unless the codebase actually contains batch systems.

---

## CounterUpdatePattern

**Recommendation: REWRITE**

**Current State:** Two-branch detection. Branch 1: name substring (`CTU`, `CTD`, `CTUD`, `Counter`, `_Cnt`, `_Count`, `cnt`, `T1_Cnt`, `T2_Cnt`). Branch 2: generic self-increment (`+` or `-`) with target in RHS.

**Problems:**
- Branch 2 matches `floor := floor - 1` (math floor function), `TestState := TestState + 1` (test state), `pos := pos + 1` (loop iterator), `w := w - (we / ...)` (Newton iteration), `dl := 1.0 - dl` (modulo normalization), `X := X + VX` (accumulator), and `T_PLC_US := ...` (timer update).
- Branch 1 matches `T1_Cnt := 500` (counter preset, not a counter update) and `cnt := 0` (counter reset, not an update).
- Severe overlap with AccumulatorPattern on self-increment arithmetic.

**Justification:** 9.8% precision overall. In implementation datasets, 70.5% of detections are real counters (31/44), but the remaining 29.5% are significant false positives (loop iterators, math functions, accumulators). The generic self-increment branch is the primary failure mode.

**Required Rewrite:**
1. Remove Branch 2 entirely. Self-increment is not sufficient evidence for counter semantics.
2. Expand Branch 1 to include `CTU`, `CTD`, `CTUD`, `Counter`, `_Cnt`, `_Count`, `cnt`, `T1_Cnt`, `T2_Cnt` but only when the value is a self-increment/decrement (target in RHS) or the target is assigned a constant preset value.
3. Add a blacklist: `floor`, `FLOOR`, `FLOOR2`, `TestState`, `T_PLC_US`, `T_PLC_MS`, `i`, `j`, `pos`, `bits`, `last`, `dl`, `w`, `x`, `y`.
4. Distinguish between counter preset/reset and counter increment. Add a `kind` for `counter_preset` vs `counter_increment`.

---

## HistoryUpdatePattern

**Recommendation: KEEP**

**Current State:** Naming heuristic on target variable. Matches any AssignmentNode where the target contains `last`, `previous`, `old`, `_last`, `history`, `x_last`, `y_last`, `tl`.

**Problems:**
- `last := tx` in a timer reset context is not a history update (it's a current-time snapshot for a reset operation).
- `tl` (time-last) is matched but is ambiguous.

**Justification:** 80.5% precision overall. In implementation datasets, most matches are true positives (`x_last := X`, `y_last := Y`, `in_last := IN`, `last := tx`). The pattern is the most accurate naming heuristic in the library.

**Required Refinement:**
1. Downgrade confidence to `medium` when the RHS is a current time value (`tx`, `T_PLC_MS`, `T_PLC_US`) rather than a process variable.
2. Remove `tl` from the heuristic unless the variable is clearly a history variable (e.g., `t_last` is better than `tl`).
3. No structural rewrite needed.

---

## AccumulatorPattern

**Recommendation: REWRITE**

**Current State:** Matches self-referential binary expressions with `XOR`, `OR`, `AND` (high confidence) or `+`, `-`, `*`, `/` (medium confidence).

**Problems:**
- Matches `floor := floor - 1` (math floor).
- Matches `TestState := TestState + 1` (test state).
- Matches `T_PLC_US := (SHL(T_PLC_US, N) OR ...) + OFFSET` (timer update).
- Matches `totalTests := totalTests + 1` (test counter).
- Matches `passedTests := passedTests + 1` (test counter).
- Matches `i := IN + in_last * 5.0E-7 * KI * tc + i` (PID integral - this is the only true positive).
- Severe overlap with CounterUpdatePattern.

**Justification:** 10.6% precision overall. In implementation datasets, only 2-3 matches are real accumulators (PID integral `i`, CRC `_CRC_GEN`). The rest are false positives. The pattern conflates any self-referential arithmetic with accumulator semantics.

**Required Rewrite:**
1. Remove the arithmetic branch (`+`, `-`, `*`, `/`) entirely. It is too generic.
2. Keep the bitwise branch (`XOR`, `OR`, `AND`) but restrict it to targets that are declared as `DWORD`, `BYTE`, `WORD`, or `ARRAY` types.
3. Add a new branch for PID/measurement accumulators: target must be in a function block named `PID`, `FT_`, `INTEGRATE`, or `CONTROL`, and the RHS must contain `KI`, `KP`, `KD`, or `integral`.
4. Add a blacklist for test variables and timer variables.

---

## ArrayAccessPattern

**Recommendation: KEEP**

**Current State:** Matches AssignmentNode where the target or value is an ArrayIndexNode.

**Problems:**
- Test harness files use string variables as byte arrays (`<str>[0] := TRUE`). These are syntactically array accesses but semantically test scaffolding.

**Justification:** 86.2% precision overall. The pattern is the most structurally sound detector in the library. It uses actual AST node types (ArrayIndexNode) rather than naming heuristics.

**Required Refinement:**
1. Downgrade confidence to `medium` when the array variable name is `str`, `string`, or `buffer` and the access is in a test harness file.
2. No structural rewrite needed.

---

## MatrixAccessPattern

**Recommendation: REMOVE**

**Current State:** Two-branch detection. Branch 1: value is FunctionInvocationNode with `MATRIX_MUL`, `MATRIX_ADD`, `MATRIX_INV`, `MATRIX_TRANSPOSE`. Branch 2: target contains `Matrix`, `matrix`, `mat`, `_M`, `_A`, `_B`, `_C`, `Result` and value contains `[` or `mat`, `Matrix`, `M`, `A`, `B`, `C`.

**Problems:**
- Branch 1 is never triggered (no `MATRIX_MUL` functions in the corpus).
- Branch 2 has a catastrophic substring bug: `_B` matches `BIT_LOAD_B`, `_C` matches `_CRC_GEN`, single-letter `A` matches `AND`, `B` matches `BYTE`, `C` matches `CRC`, `M` matches `SHR`/`SHL`/`MODR`/`MOD`/`T_PLC_MS`/`T_PLC_US`.
- The pattern detected **0 true positives** across all 57 datasets.
- All 55 detections are false positives (e.g., `BIT_LOAD_B := in AND NOT SHL(...)`).

**Justification:** 0% precision. The pattern is completely broken. The concept of matrix operations is not present in the corpus (the `MATRIX.st` file is a keyboard matrix scanner, not a linear algebra matrix). The OperationExtractor already captures `matrix_access` correctly.

**Action:** Remove the pattern entirely. Do not rewrite.

---

## BitwiseUpdatePattern

**Recommendation: KEEP**

**Current State:** Matches AssignmentNode where value is FunctionInvocationNode with `SHL`, `SHR`, `ROL`, `ROR`, `AND`, `OR`, `XOR`, `NOT`, `BIT_LOAD_B`, `BIT_OF_DWORD` OR value is BinaryExpressionNode with `AND`, `OR`, `XOR`.

**Problems:**
- The boolean branch (`AND`, `OR`, `XOR` in BinaryExpressionNode) can match boolean logic expressions that are not bitwise (e.g., `_CRC_GEN := ... OR ...` is bitwise in CRC context but could be boolean logic in another context).

**Justification:** 95.1% precision overall. The function-name branch is highly accurate. The bitwise operations in the corpus (CRC_GEN, MATRIX, GEN_BIT, INCLUDE) are all real.

**Required Refinement:**
1. For the BinaryExpressionNode branch, require that the target variable is declared as a bitwise type (`DWORD`, `BYTE`, `WORD`, `BOOL` array) or that the expression contains bit-shift functions (`SHL`, `SHR`, `ROL`, `ROR`).
2. No structural rewrite needed.

---

## RateCalculationPattern

**Recommendation: REMOVE**

**Current State:** Matches AssignmentNode where value is `/` operator and target contains `Flow`, `Rate`, `Speed`, `Freq` or sources contain `delta`, `time`, `dt`, `period`, `pulse`, `count`.

**Problems:**
- Detected **0 patterns** across all 57 datasets.
- The FLOW_METER rate calculation (`F := (UDINT_TO_REAL(Y - y_last) + X - x_last) / TIME_TO_REAL(tx - tl) * 3.6E6`) is missed because:
  - Target `F` does not contain `Flow`, `Rate`, `Speed`, or `Freq`.
  - Sources `tx` and `tl` do not contain `delta`, `time`, `dt`, `period`, `pulse`, or `count`.
- The heuristic is based on English naming conventions that do not match the actual German/English mixed naming in the industrial corpus (OSCAT library).

**Justification:** 0% precision. The pattern is dead code. It never fires. The OperationExtractor already captures `measurement_calculation` correctly.

**Action:** Remove the pattern entirely. Do not rewrite.

---

## ProcessCalculationPattern

**Recommendation: REWRITE**

**Current State:** Two-branch detection. Branch 1: value is FunctionInvocationNode with `SQRT`, `ABS`, `EXP`, `LN`, `SIN`, `COS`, `TAN`, `MODR`, `FLOOR`, `SIGN_R`, `LAMBERT_W`. Branch 2: value is BinaryExpressionNode with `+`, `-`, `*`, `/`, `MOD` and target contains `PID`, `FT_`, `Control`, `Output`, `Process`.

**Problems:**
- Branch 1 matches function return variables (`MODR := ...`, `FLOOR := REAL_TO_INT(X)`). These are function bodies, not process calculations.
- Branch 2 is rarely triggered (only 14 total detections) because the target naming heuristic is too narrow.
- Branch 2 misses the FLOW_METER calculation because target `F` does not match.

**Justification:** 71.4% precision. The function-name branch is mostly accurate but conflates function definitions with process calculations. The target-name branch is too narrow and misses real process calculations.

**Required Rewrite:**
1. Distinguish between function return assignments and process calculations. If the assignment target is the same as the enclosing function name, it is a function return, not a process calculation.
2. Expand the target heuristic to include `F_`, `OUT`, `Result`, `Y`, `value`, and any variable in a function block named `PID`, `FLOW`, `METER`, `CONTROL`, `PROCESS`.
3. Keep the mathematical function branch but blacklist function return variables.

---

## FunctionBlockInvocationPattern

**Recommendation: REMOVE**

**Current State:** Matches FunctionBlockCallNode where the name starts with `TON`, `TOF`, `TP` (timer), `CTU`, `CTD`, `CTUD` (counter), `PID`, `FT_` (PID), or contains `TIMER`, `COUNTER`.

**Problems:**
- 100% redundant with OperationExtractor. The OperationExtractor already visits `FunctionBlockCallNode` and classifies `timer_invocation`, `counter_invocation`, `fb_invocation`.
- 805 of 857 detections (93.9%) are test scaffolding blocks (`TestBlock`, `Test_0` through `Test_8`, `Timer` in test harnesses).
- The pattern adds no new semantic information. It simply rediscovers what the OperationExtractor already produces.

**Justification:** 6.1% precision overall. In implementation datasets, 13/13 detections are real FB calls, but the OperationExtractor already captures them. The pattern is completely redundant.

**Action:** Remove the pattern entirely. Do not rewrite. The OperationExtractor is the authoritative source for FB invocations.

---

## Summary of Actions

| Pattern | Action | Rationale |
|---|---|---|
| StateTransitionPattern | REWRITE | 33% precision. TestState contamination. Core concept sound. |
| CounterUpdatePattern | REWRITE | 10% precision. Generic self-increment branch is broken. |
| HistoryUpdatePattern | KEEP | 81% precision. Best naming heuristic. Minor refinements. |
| AccumulatorPattern | REWRITE | 11% precision. Generic arithmetic branch broken. |
| ArrayAccessPattern | KEEP | 86% precision. Structurally sound. Minor refinements. |
| MatrixAccessPattern | REMOVE | 0% precision. Catastrophic substring bug. No true positives. |
| BitwiseUpdatePattern | KEEP | 95% precision. Function branch is highly accurate. |
| RateCalculationPattern | REMOVE | 0% precision. Dead pattern. Never fires. |
| ProcessCalculationPattern | REWRITE | 71% precision. Function return conflation. Target heuristic too narrow. |
| FunctionBlockInvocationPattern | REMOVE | 6% precision. 100% redundant with OperationExtractor. |

**Patterns to Keep:** 3 (HistoryUpdatePattern, ArrayAccessPattern, BitwiseUpdatePattern)
**Patterns to Rewrite:** 3 (StateTransitionPattern, CounterUpdatePattern, ProcessCalculationPattern)
**Patterns to Remove:** 3 (MatrixAccessPattern, RateCalculationPattern, FunctionBlockInvocationPattern)
**Patterns to Remove with possible future rewrite:** 1 (AccumulatorPattern)

If all recommendations are followed, the Pattern Library would shrink from 10 patterns to 6 (3 keep + 3 rewrite). The rewritten patterns would require stricter AST evidence and semantic context integration. The average precision would rise from 10.7% to an estimated 75-85%.
