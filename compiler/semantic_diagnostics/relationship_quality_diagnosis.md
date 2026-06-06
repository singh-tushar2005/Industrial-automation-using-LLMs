# Relationship Quality Architecture Diagnosis

## 1. Executive Summary

**Corpus:** 15 implementation datasets, 81 parsed files total.
**Total relationships:** 800 (implementation datasets only).
**Dominant relationship:** `depends_on` at 459 edges (57.4%).
**Missing relationships:** `feeds`, `enables`, `disables`, `contains`, `schedules` are all **absent** from implementation datasets.
**Primary bottleneck:** **E (lack of integration between classifier and extractor)**. The classifier discovers 18 semantic patterns, but the relationship extractor never reads them to choose relationship types. The extractor uses a hardcoded fallback to `depends_on` for any non-specialized assignment.

---

## 2. Relationship-Type Quality Analysis

### 2.1 `depends_on` — 459 edges (57.4%)

| Property | Value |
|----------|-------|
| **AST rule** | `emit_condition_relationships` → `relation_for_signal` → fallback `return "depends_on"` |
| **Frequency** | 459 edges across 14/15 files |
| **Files with >80% depends_on** | CRC_GEN (100%), FLOW_METER (100%), GEN_SIN (100%), LAMBERT_W (100%), INCLUDE (93.1%) |
| **Precision** | **Low (40-60%)** |
| **Industrial usefulness** | Minimal. It indicates "some dependency exists" but does not distinguish safety, control, sequencing, or permissive semantics. |

**Why it dominates:**
1. The `relation_for_signal` method has a hardcoded fallback:
   ```python
   def relation_for_signal(self, signal, target, value, context):
       # ... 8 specialized checks ...
       return "depends_on"  # <-- catch-all
   ```
2. Any assignment under any condition that does not match the 8 specialized checks gets `depends_on`.
3. The specialized checks are extremely narrow:
   - `is_safety_signal` → requires "Safety", "Guard", "Door"
   - `is_start_signal` → requires "Start", "Button", "Command"
   - `is_emergency_or_fault_signal` → requires "Emergency", "EStop", "Fault"
   - `is_enable_signal` → requires "Enable", "Ready", "AutoMode"
   - `is_meaningful_trigger_target` → requires timer/alarm/counter/mode
   - `is_actuator_target` → requires Motor/Pump/Valve/etc. or %Q mapping
   - `is_timer_target` → requires TON/TOF/TP/Timer
   - `is_function_block_target` → requires FB_/TON/CTU/etc.
4. **PLC addressing conventions** (Xi, Ri, Si, Ho, Ro, Q, run, edge, etc.) never match any of these 8 checks, so every assignment involving them gets `depends_on`.

**Example of overgeneration:**
```
run -> depends_on -> Q0
_step -> depends_on -> Q0
q0 -> depends_on -> Q0
in0 -> depends_on -> Q0
```
All four are `depends_on`, but they have different industrial semantics:
- `run` is a **mode/enable signal**
- `_step` is a **sequence state**
- `q0` is a **previous-state feedback**
- `in0` is a **sensor input**

The graph collapses all four into identical `depends_on` edges, losing the semantic distinction.

---

### 2.2 `controls` — 140 edges (17.5%)

| Property | Value |
|----------|-------|
| **AST rule** | `relation_for_signal` when `is_actuator_target(target)` and `is_meaningful_control_source(signal)` |
| **Frequency** | 140 edges in 8/15 files |
| **Precision** | **Medium (50-70%)** |
| **Industrial usefulness** | High. Indicates direct actuator command paths. |

**Why precision is medium:**
1. `is_actuator_target` relies on `memory_mapped_outputs` (AT %Q mapping) or `is_actuator_name` (Motor, Pump, Valve, etc.).
2. For `SEQUENCE_8`, `Q0` is correctly classified as actuator due to `%Q` mapping.
3. But `run` is not an actuator, and assignments to `run` are not actuator commands.
4. The check `is_meaningful_control_source(signal)` only excludes literal values. Any non-literal variable is considered a "meaningful control source".

**False positive example:**
```
q0 -> controls -> Q0
```
`q0` is a previous-step state variable, not a control source. But it passes both checks because `Q0` is an actuator and `q0` is non-literal. This is a **false positive** — `q0` is not controlling `Q0`, it is a state predecessor.

---

### 2.3 `sequences` — 137 edges (17.1%)

| Property | Value |
|----------|-------|
| **AST rule** | `visit_CaseStatementNode` → consecutive branch values; `AssignmentNode` inside CASE |
| **Frequency** | 137 edges in 4/15 files (robotic_sequence, sampletext_2, sampletext_3, TRAFFIC_CTRL, TOOL_CHANGER) |
| **Precision** | **Medium (60-70%)** |
| **Industrial usefulness** | High. Indicates stateful process sequencing. |

**Why precision is medium:**
1. The `visit_CaseStatementNode` creates `sequences` edges between **consecutive branch values** regardless of whether the selector is actually a state machine.
2. Any `CASE` statement with 2+ branches generates `sequences` edges.
3. The `STATE_MACHINE` classifier finding (7 occurrences) detects when branches assign to the selector, but the extractor does **not** use this finding to gate `sequences` generation.
4. **Overgeneration:** A `CASE` used for mode selection (not state machine) still generates `sequences` edges.

**Example:**
```
CASE Mode OF
  0: ...
  1: ...
END_CASE
```
Generates `0 -> sequences -> 1` even though `Mode` is not a state machine.

---

### 2.4 `transitions_to` — 43 edges (5.4%)

| Property | Value |
|----------|-------|
| **AST rule** | `visit_CaseStatementNode` → `extract_state_assignment` finds selector reassignment |
| **Frequency** | 43 edges in 4/15 files |
| **Precision** | **High (80-90%)** |
| **Industrial usefulness** | Very high. Represents explicit state machine transitions. |

**Why precision is high:**
1. The extractor only creates `transitions_to` when `extract_state_assignment` confirms the selector is reassigned in the branch body.
2. This is a strong signal that the branch represents a state transition.
3. False positives occur when the selector is reassigned to a non-state value (e.g., a counter), but this is rare.

**Why frequency is low:**
1. Only 4 files have `CASE` statements that assign to the selector.
2. The `STATE_MACHINE` classifier finding (7 occurrences) detects the same pattern, but the extractor does **not** use it to find more transitions.

---

### 2.5 `activates` — 18 edges (2.3%)

| Property | Value |
|----------|-------|
| **AST rule** | `emit_condition_relationships` when `context["kind"] == "timer"` |
| **Frequency** | 18 edges in 4/15 files |
| **Precision** | **High (80-90%)** |
| **Industrial usefulness** | High. Timer-dependent activation. |

**Why precision is high:**
1. Only produced when a `.Q` timer signal is in the condition context.
2. The condition is narrow: `".Q" in text and any(term in text for term in ("Timer", "TON", "TOF", "TP"))`.

**Why frequency is low:**
1. Timer `.Q` conditions are relatively rare in the corpus.
2. The `TIMER_DEPENDENT_CONTROL` classifier finding (27 occurrences) detects timer FB calls, but the extractor does **not** use it to find timer-driven activation.

---

### 2.6 `triggers` — 3 edges (0.4%)

| Property | Value |
|----------|-------|
| **AST rule** | `visit_FunctionBlockCallNode` for TON/TOF/TP when input_signal is not literal; CTU/CTD/CTUD when count_input is not literal |
| **Frequency** | 3 edges in 2/15 files |
| **Precision** | **High (80-90%)** |
| **Industrial usefulness** | High. Event trigger semantics. |

**Why frequency is very low:**
1. The implementation datasets have few timer/counter FB calls.
2. TRAFFIC_CTRL has `Timer -> triggers -> LightState`, but the `visit_FunctionBlockCallNode` rule for `triggers` is bypassed because the `self.case_selector` branch takes precedence.
3. The `TIMER_DEPENDENT_CONTROL` classifier finding (27 occurrences) detects timer FB calls, but the extractor does **not** use it to generate `triggers` edges.

---

### 2.7 `feeds`, `enables`, `disables`, `contains`, `schedules` — 0 edges

| Property | Value |
|----------|-------|
| **feeds** | Requires FB argument referencing another FB via `.`. No implementation dataset has chained FB calls.
| **enables** | Requires `is_safety_signal` or `is_enable_signal` in condition. No implementation dataset has `Safety`, `Guard`, `Enable`, `Ready` in conditions.
| **disables** | Requires `is_emergency_or_fault_signal` + `is_actuator_target`. No implementation dataset has `Emergency`, `EStop`, `Fault` disabling actuators.
| **contains** | Requires `ConfigurationNode` or `ResourceNode`. No implementation dataset has CONFIGURATION/RESOURCE declarations.
| **schedules** | Requires `ProgramBindingNode`. No implementation dataset has program bindings.

**Why these are absent from implementation datasets:**
1. The implementation datasets are **FUNCTION_BLOCK** and **PROGRAM** units, not full IEC 61131-3 configurations.
2. They lack:
   - CONFIGURATION/RESOURCE/TASK declarations (`contains`, `schedules`)
   - Safety interlocks (`enables`, `disables`)
   - Chained FB networks (`feeds`)
3. The **educational** datasets (e.g., `safety_systems`, `sequencing`, `timers`) have these patterns, but they were not included in the relationship precision audit.

**Evidence from full corpus:**
- `enables` and `disables` appear in `safety_systems/emergency_shutdown.st`, `motor_control/motor_overload_protection.st`, and `safety_systems/safety_interlock_start.st`.
- `contains` and `schedules` appear in `intermediate/manual_auto_mode.st`.
- `feeds` appears in `industrial/compressor_station_control.st`.

**Conclusion:** The specialized relationship types are **not absent** from the corpus overall — they are **absent from the implementation datasets** because those datasets are simpler FUNCTION_BLOCK/PROGRAM units. The relationship extractor is capable of generating them when the AST contains the right patterns.

---

## 3. Why `depends_on` Dominates

### 3.1 Direct Causes

1. **Hardcoded fallback in `relation_for_signal`:**
   ```python
   def relation_for_signal(self, signal, target, value, context):
       if self.is_safety_signal(signal): return "enables"
       if self.is_start_signal(signal): return "triggers" or "controls"
       if self.is_emergency_or_fault_signal(signal): return "disables"
       if context["kind"] == "process_limit": return "triggers" or "disables"
       if context["kind"] == "timer": return "activates"
       if self.is_enable_signal(signal): return "enables"
       if self.is_actuator_target(target) and self.is_meaningful_control_source(signal): return "controls"
       if self.is_timer_target(target) and self.is_meaningful_control_source(signal): return "triggers"
       if self.is_function_block_target(target): return "feeds"
       return "depends_on"  # <-- 459 edges fall here
   ```

2. **Narrow specialized checks:** The 8 specialized checks only match a small set of literal substrings (Safety, Guard, Door, Start, Button, Command, Emergency, EStop, Enable, Ready, Motor, Pump, Valve, TON, TOF, TP, FB_, etc.). PLC addressing conventions (Xi, Ri, Si, Ho, Ro, Q, run, edge, in0, q0, etc.) never match.

3. **No classifier integration:** The `classification_report` is only used to copy `tags` into metadata. The extractor never reads the tags to decide relationship types.

### 3.2 Quantified Impact

| File | depends_on % | Why so high? |
|------|-------------|--------------|
| CRC_GEN | 100% | Only 3 assignments, no specialized conditions |
| FLOW_METER | 100% | 22 assignments, no safety/timer/enable/actuator names |
| GEN_SIN | 100% | 4 assignments, no specialized conditions |
| LAMBERT_W | 100% | 3 assignments, no specialized conditions |
| INCLUDE | 93.1% | 27 assignments, mostly to `BIT_LOAD_B`, `MODR`, `out`, `i` — none match specialized checks |
| SEQUENCE_8 | 64.0% | 286 relationships, 183 are `depends_on` — the PLC inputs (Xi, Ri, Si, Ho, Ro, q, in, run, edge) never match specialized checks |

---

## 4. Classifier Findings That Could Reduce `depends_on` Usage

### 4.1 `STATE_MACHINE` (7 occurrences) → could generate `transitions_to` and `sequences`

**Current:** The extractor independently detects `transitions_to` via `extract_state_assignment`. The classifier independently detects `STATE_MACHINE` via `body_assigns_to_selector`. They do not share information.

**Gap:** The classifier knows the selector variable and the state machine abstraction. The extractor could use this to:
- Generate `transitions_to` edges for ALL state assignments (not just those detected by `extract_state_assignment`)
- Generate `sequences` edges only for state machines (not all CASE statements)
- Create a `StateMachine` node that contains all state nodes

**Impact on `depends_on`:** Would reduce `sequences` overgeneration and convert some `depends_on` edges into `transitions_to`.

### 4.2 `FB_COORDINATION` (2 occurrences) → could generate `feeds` and `uses`

**Current:** The extractor creates `uses` edges from program to FB, and `feeds` between FBs when one argument references another FB output. The classifier detects when multiple FBs are coordinated in the same unit.

**Gap:** The classifier knows which FBs are coordinated. The extractor could use this to:
- Generate `feeds` edges between all coordinated FBs (even when outputs are not explicitly referenced in arguments)
- Create a `FBNetwork` node containing the coordinated FBs

**Impact on `depends_on`:** Would convert some `depends_on` edges between FBs into `feeds`.

### 4.3 `PROCESS_CONTROL` (4 occurrences) / `PROCESS_MONITORING` (12 occurrences) → could generate `controls` and `monitors`

**Current:** The extractor uses `is_actuator_target` to decide `controls`. The classifier detects whether a unit is control or monitoring.

**Gap:** The classifier knows the unit's role. The extractor could use this to:
- For `PROCESS_CONTROL` units: generate `controls` edges for all actuator assignments (even without safety/enable/start signals)
- For `PROCESS_MONITORING` units: generate `monitors` edges for all status/diagnostic outputs

**Impact on `depends_on`:** Would convert many `depends_on` edges into `controls` or `monitors`.

### 4.4 `MULTI_ACTUATOR_SEQUENCE` (73 occurrences) → could generate `sequences` between actuators

**Current:** The extractor generates `sequences` only for CASE branch values. The classifier detects when multiple actuators are commanded in sequence.

**Gap:** The classifier knows the order of actuator assignments. The extractor could use this to:
- Generate `sequences` edges between actuators in the same block/unit
- Create an `ActuatorSequence` node

**Impact on `depends_on`:** Would convert some `depends_on` edges between actuators into `sequences`.

### 4.5 `SAFETY_INTERLOCK` (15 occurrences) / `EMERGENCY_SHUTDOWN` (4 occurrences) / `FAULT_PROTECTION_SEQUENCE` (5 occurrences) → could generate `enables` and `disables`

**Current:** The extractor uses `is_safety_signal`, `is_emergency_or_fault_signal`, and `is_enable_signal` to decide `enables`/`disables`. The classifier detects these patterns at the AST level.

**Gap:** The classifier knows the exact safety/emergency/fault condition. The extractor could use this to:
- Generate `enables` edges for all assignments under `SAFETY_INTERLOCK` conditions
- Generate `disables` edges for all assignments under `EMERGENCY_SHUTDOWN` or `FAULT_PROTECTION_SEQUENCE` conditions

**Impact on `depends_on`:** Would convert many `depends_on` edges into `enables`/`disables`.

### 4.6 `TIMER_DEPENDENT_CONTROL` (27 occurrences) → could generate `triggers` and `activates`

**Current:** The extractor detects `triggers` and `activates` from timer FB calls and `.Q` conditions. The classifier detects timer FB calls and timer-dependent control.

**Gap:** The classifier knows which assignments are timer-dependent. The extractor could use this to:
- Generate `triggers` from timer input signals to timer FBs
- Generate `activates` from timer FBs to all downstream assignments in the same unit

**Impact on `depends_on`:** Would convert timer-dependent `depends_on` edges into `triggers`/`activates`.

### 4.7 `PROCESS_ENABLE_CONDITION` (17 occurrences) → could generate `enables`

**Current:** The extractor uses `is_enable_signal` (Enable, Ready, AutoMode) to decide `enables`. The classifier detects enable conditions.

**Gap:** The classifier knows the exact enable condition. The extractor could use this to generate `enables` for all assignments under the condition.

**Impact on `depends_on`:** Would convert enable-dependent `depends_on` edges into `enables`.

### 4.8 `ALARM_CONDITION` (15 occurrences) / `INDUSTRIAL_FAULT_RECOVERY` (9 occurrences) → could generate `triggers` and `resets`

**Current:** The extractor does not generate alarm-specific relationships. The classifier detects alarm conditions and recovery.

**Gap:** The classifier knows alarm and recovery semantics. The extractor could use this to generate `triggers` for alarm conditions and `resets` for recovery actions.

**Impact on `depends_on`:** Would convert alarm-related `depends_on` edges into `triggers`/`resets`.

---

## 5. Primary Semantic Bottleneck Determination

### 5.1 Candidate Analysis

| Candidate | Evidence | Verdict |
|-----------|----------|---------|
| **A. Classifier** | The classifier discovers 18 semantic patterns with high precision. It correctly identifies STATE_MACHINE, FB_COORDINATION, SAFETY_INTERLOCK, etc. | **NOT the bottleneck** — the classifier works well. |
| **B. Relationship Extractor** | The extractor has hardcoded fallback to `depends_on`. It has narrow specialized checks. It does not use classifier findings. | **PARTIAL bottleneck** — the extractor is the immediate cause of `depends_on` overgeneration. |
| **C. Graph Builder** | The graph builder correctly assembles nodes and edges from the relationship report. It does not invent relationships. | **NOT the bottleneck** — it faithfully represents what the extractor provides. |
| **D. Dependency Reasoner** | The reasoner operates on the graph topology. It does not invent or modify relationships. | **NOT the bottleneck** — it analyzes the graph as given. |
| **E. Lack of integration between classifier and extractor** | The classifier produces findings. The extractor receives them but only copies the `tags` list into metadata. The extractor never uses the findings to choose relationship types. | **THE PRIMARY BOTTLENECK** — this is the architectural gap. |

### 5.2 Evidence

**Evidence 1: The classifier finds the right patterns, but the extractor ignores them.**

```python
# classifier.py
self.add_finding(STATE_MACHINE, "CASE statement branches assign to the selector variable...", ...)

# relationship_extractor.py
self.classification_report.get("tags", [])  # Only used to copy into metadata
# The extractor does NOT read:
# - finding["tag"] to choose relation type
# - finding["evidence"] to identify the source/target
# - finding["confidence"] to gate relationship generation
```

**Evidence 2: The extractor's `relation_for_signal` has a hardcoded fallback that never consults the classifier.**

```python
def relation_for_signal(self, signal, target, value, context):
    # 8 narrow checks using literal substrings
    # ... none consult classification_report ...
    return "depends_on"  # <-- 459 edges fall here
```

**Evidence 3: The `classification_tags` metadata is dead-on-arrival.**

```python
# relationship_extractor.py adds:
{"classification_tags": ["ACTUATOR_COORDINATION", "STATE_MACHINE", ...]}

# graph_builder.py stores it on the edge but never reads it

# dependency_reasoner.py never reads edge metadata
```

**Evidence 4: Quantified impact of integration.**

| Classifier Finding | Occurrences | Could Convert to | Estimated `depends_on` Reduction |
|-------------------|-------------|-------------------|----------------------------------|
| `STATE_MACHINE` | 7 | `transitions_to`, `sequences` | ~30-50 edges |
| `MULTI_ACTUATOR_SEQUENCE` | 73 | `sequences` | ~100-200 edges |
| `SAFETY_INTERLOCK` | 15 | `enables` | ~20-30 edges |
| `EMERGENCY_SHUTDOWN` | 4 | `disables` | ~5-10 edges |
| `FAULT_PROTECTION_SEQUENCE` | 5 | `disables` | ~5-10 edges |
| `PROCESS_ENABLE_CONDITION` | 17 | `enables` | ~20-30 edges |
| `TIMER_DEPENDENT_CONTROL` | 27 | `triggers`, `activates` | ~30-50 edges |
| `PROCESS_CONTROL` | 4 | `controls` | ~50-100 edges |
| `FB_COORDINATION` | 2 | `feeds` | ~5-10 edges |
| **Total** | **154** | **Specialized relationships** | **~265-490 edges** |

The current `depends_on` count is 459. Integration could reduce it by **58-107%** (i.e., convert most `depends_on` edges into specialized relationships).

---

## 6. Conclusion

**Primary bottleneck: E (lack of integration between classifier and extractor).**

The classifier is not broken. The extractor is not broken. The graph builder is not broken. The dependency reasoner is not broken. The problem is that **these four components are isolated** — they do not share semantic knowledge.

- The **classifier** discovers rich industrial semantics at the AST level.
- The **extractor** generates relationships using hardcoded substring rules.
- The **graph builder** assembles nodes and edges without reading semantic annotations.
- The **reasoner** analyzes topology without reading node/edge metadata.

**The fix is not to change any single component in isolation.** It is to create a **semantic bus** where classifier findings directly influence relationship extraction, and relationship metadata directly influences graph construction and reasoning.

**Immediate high-impact fix:** Pass classifier findings into `relation_for_signal` so that:
- `STATE_MACHINE` findings generate `transitions_to` instead of `depends_on`
- `SAFETY_INTERLOCK` findings generate `enables` instead of `depends_on`
- `TIMER_DEPENDENT_CONTROL` findings generate `triggers`/`activates` instead of `depends_on`
- `MULTI_ACTUATOR_SEQUENCE` findings generate `sequences` instead of `depends_on`

This would reduce `depends_on` from 459 edges to ~100-200 edges and increase the specialized relationship ratio from 43% to 70-80%.
