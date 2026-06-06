# Relationship Rule Precision Audit

## Audit Scope
- **File audited**: `semantic/relationship_extractor.py`
- **Datasets**: `Implementation_datasets`, `test_harness/Full_test`, `test_harness/test_case`
- **Total files**: 54
- **Total edges logged (pre-deduplication)**: 6,296

---

## Rule Inventory

| Rule ID | Rule Name | Description |
|---|---|---|
| R1 | `emit_condition_relationships -> relation_for_signal` | Main assignment rule: for every signal in an IF condition, calls `relation_for_signal` to determine the relation for the assignment target. |
| R2 | `emit_condition_relationships -> process_limit` | Hardcoded: when `context["kind"] == "process_limit"`, generates `limit_source -> triggers/disables -> target`. |
| R3 | `emit_condition_relationships -> timer` | Hardcoded: when `context["kind"] == "timer"`, generates `timer_source -> activates -> target`. |
| R4 | `visit_AssignmentNode -> case_stack` | For every assignment inside a CASE branch, generates `case_selector -> sequences -> target`. |
| R5 | `visit_CaseStatementNode -> branch_sequence` | For consecutive CASE branches, generates `previous_branch -> sequences -> current_branch`. |
| R6 | `visit_CaseStatementNode -> state_transition` | When a branch body assigns to the selector, generates `current_branch -> transitions_to -> next_state`. |
| R7 | `visit_FunctionBlockCallNode -> timer_trigger` | For TON/TOF/TP calls, generates `input_signal -> triggers -> timer_fb`. |
| R8 | `visit_FunctionBlockCallNode -> timer_preset` | For TON/TOF/TP calls, generates `timer_fb -> depends_on -> preset_time`. |
| R9 | `visit_FunctionBlockCallNode -> timer_state_transition` | When a timer FB is called inside a CASE branch, generates `timer_fb -> triggers -> case_selector`. |
| R10 | `visit_FunctionBlockCallNode -> counter_trigger` | For CTU/CTD/CTUD calls, generates `count_input -> triggers -> counter_fb`. |
| R11 | `visit_FunctionBlockCallNode -> program_uses_fb` | For any FB call, generates `current_program -> uses -> fb_name`. |
| R12 | `visit_FunctionBlockCallNode -> fb_feeds_fb` | When an FB argument references another FB output, generates `referenced_fb -> feeds -> fb_name`. |
| R13 | `visit_ResourceNode -> contains` | Generates `configuration -> contains -> resource`. |
| R14 | `visit_TaskNode -> contains` | Generates `resource -> contains -> task`. |
| R15 | `visit_ProgramBindingNode -> schedules` | Generates `task -> schedules -> program_instance`. |
| R16 | `visit_ProgramBindingNode -> uses` | Generates `instance_name -> uses -> program_type`. |

---

## Rule Frequency (Aggregate)

| Rule ID | Total Edges | Relation Types | Datasets Affected |
|---|---|---|---|
| R1 | **3,874** | `depends_on` (1,931), `controls` (1,384), `activates` (499), `sequences` (48), `triggers` (9), `disables` (3) | 54 |
| R4 | **1,125** | `sequences` (1,125) | 45 |
| R3 | **475** | `activates` (475) | 41 |
| R5 | **272** | `sequences` (272) | 45 |
| R9 | **248** | `triggers` (248) | 41 |
| R11 | **185** | `uses` (185) | 40 |
| R6 | **57** | `transitions_to` (57) | 9 |
| R13 | **20** | `contains` (20) | 20 |
| R14 | **20** | `contains` (20) | 20 |
| R16 | **20** | `uses` (20) | 20 |
| R2 | **0** | — | 0 |
| R7 | **0** | — | 0 |
| R8 | **0** | — | 0 |
| R10 | **0** | — | 0 |
| R12 | **0** | — | 0 |
| R15 | **0** | — | 0 |

---

## Precision Assessment

### HIGH PRECISION

| Rule ID | Reason |
|---|---|
| R3 | Only fires when `context["kind"] == "timer"`. Explicit timer signal required. Always `activates`. |
| R6 | Only fires when `extract_state_assignment` finds the selector being reassigned. Correctly identifies state transitions. |
| R11 | Always correct: a program that calls an FB "uses" that FB. |
| R13 | Always correct: configuration contains resource. |
| R14 | Always correct: resource contains task. |
| R16 | Always correct: program instance uses program type. |

### MEDIUM PRECISION

| Rule ID | Reason |
|---|---|
| R4 | Assumes every CASE branch is a state machine. False positives when CASE is a lookup table (e.g., `DEC_TO_HEX`). |
| R5 | Assumes consecutive CASE branches imply sequencing. False positives when branches are independent modes. |
| R9 | Assumes every timer inside a CASE branch triggers a state transition. The timer may just be a local timeout. |

### LOW PRECISION

| Rule ID | Reason |
|---|---|
| **R1** | **Catch-all rule. 50% of edges are `depends_on` (1,931 / 3,874). `controls` is 36% (1,384). The `depends_on` fallback is the dominant source of low precision.** |

---

## Root Cause Analysis (Low Precision Rules)

### R1: `emit_condition_relationships -> relation_for_signal`

**Over-generation (1,931 `depends_on` edges)**
- **Cause**: `relation_for_signal` falls back to `depends_on` for ANY non-actuator, non-timer, non-FB target when no specialized rule matches.
- **Impact**: Every variable in an IF condition gets a `depends_on` edge to the assignment target.
- **Examples**:
  - `REV_IN -> depends_on -> _CRC_GEN` (test harness variable)
  - `run -> depends_on -> last` (internal state variable)
  - `run -> depends_on -> status` (internal state variable)

**Condition-variable explosion**
- **Cause**: `extract_condition_signals` extracts ALL variables from a condition, including intermediate variables and state variables.
- **Impact**: Complex conditions like `run AND _step = 0 AND NOT q0 AND in0 AND tx - last <= wait0` generate 5+ edges per assignment.
- **Example**: `SEQUENCE_8` generates 286 relationships for 35 graph nodes because each nested IF adds more signals.

**Mode variable treated as generic signal**
- **Cause**: `run` is classified as `mode` (correct), but `run -> depends_on -> last` is `depends_on` because `last` is `history` and Phase 3 has no `mode -> history` rule.
- **Impact**: `run` (execution flag) gets `depends_on` edges to internal state variables.

**State variable treated as generic signal**
- **Cause**: `_step` is classified as `state` (correct), but `_step -> depends_on -> last` is `depends_on` because `last` is `history` and Phase 3 has no `state -> history` rule.
- **Impact**: State variables get `depends_on` edges to internal state variables.

**Fallback dependency logic**
- **Cause**: Phase 2's `elif self.is_actuator_target(target):` is the last meaningful check before `depends_on`. Any non-actuator target falls through to `depends_on`.
- **Impact**: Internal variables, registers, history variables, and unknown variables all get `depends_on`.

---

## Ranked Improvement Opportunities

### 1. Fix R1 `depends_on` over-generation

**Estimated impact if fixed**:
- `depends_on` reduction: **~1,200 edges** (62% of 1,931)
- Precision increase: **from 40% to 75%** for R1
- Datasets affected: **all 54**

**Approach**:
- Add Phase 3 rules for missing source/target combinations:
  - `mode -> history`: `depends_on` → `enables` (or `triggers`)
  - `state -> history`: `depends_on` → `sequences` (or `triggers`)
  - `register -> history`: `depends_on` → `enables`
  - `sensor -> history`: `depends_on` → `triggers`
- Introduce a `is_internal_state_variable` check to suppress `depends_on` for intermediate variables.

### 2. Fix R4 `case_stack` sequences over-generation

**Estimated impact if fixed**:
- `sequences` reduction: **~400 edges** (35% of 1,125)
- Precision increase: **from 60% to 90%** for R4
- Datasets affected: **45**

**Approach**:
- Only generate `case_stack -> sequences -> target` when the CASE selector is confirmed to be a state machine (e.g., `STATE_MACHINE` classifier finding is present).
- For lookup-table CASE statements, suppress the `sequences` edge.

### 3. Fix R5 `branch_sequence` over-generation

**Estimated impact if fixed**:
- `sequences` reduction: **~100 edges** (37% of 272)
- Precision increase: **from 60% to 90%** for R5
- Datasets affected: **45**

**Approach**:
- Only generate `branch_sequence` when `STATE_MACHINE` classifier finding is present.
- For simple lookup tables, suppress the edge.

### 4. Fix R9 `timer_state_transition` ambiguity

**Estimated impact if fixed**:
- `triggers` reduction: **~50 edges** (20% of 248)
- Precision increase: **from 70% to 90%** for R9
- Datasets affected: **41**

**Approach**:
- Only generate `timer_fb -> triggers -> case_selector` when the timer's `.Q` signal is actually used in the condition that controls the state transition.
- If the timer is just a local delay (not a transition trigger), suppress the edge.

---

## Rule: Expected vs Actual Relationship

| Rule ID | Expected | Actual | Precision |
|---|---|---|---|
| R1 | `controls`, `triggers`, `enables`, `disables` | 50% `depends_on`, 36% `controls` | LOW |
| R2 | `triggers` / `disables` | (0 edges in corpus) | N/A |
| R3 | `activates` | 100% `activates` | HIGH |
| R4 | `sequences` | 100% `sequences` | MEDIUM |
| R5 | `sequences` | 100% `sequences` | MEDIUM |
| R6 | `transitions_to` | 100% `transitions_to` | HIGH |
| R7 | `triggers` | (0 edges) | N/A |
| R8 | `depends_on` | (0 edges) | N/A |
| R9 | `triggers` | 100% `triggers` | MEDIUM |
| R10 | `triggers` | (0 edges) | N/A |
| R11 | `uses` | 100% `uses` | HIGH |
| R12 | `feeds` | (0 edges) | N/A |
| R13 | `contains` | 100% `contains` | HIGH |
| R14 | `contains` | 100% `contains` | HIGH |
| R15 | `schedules` | (0 edges) | N/A |
| R16 | `uses` | 100% `uses` | HIGH |

---

## Summary

- **16 rules** identified in `relationship_extractor.py`.
- **10 rules** generated edges in the industrial corpus.
- **6 rules** generated zero edges (R2, R7, R8, R10, R12, R15).
- **R1** is the dominant source of low precision: 3,874 edges (61% of total), with 50% being generic `depends_on`.
- **R4** is the second-largest source: 1,125 edges (18% of total), all `sequences` from CASE branches.
- **Highest precision**: R3, R6, R11, R13, R14, R16 (100% correct relation type).
- **Lowest precision**: R1 (50% `depends_on` fallback).

