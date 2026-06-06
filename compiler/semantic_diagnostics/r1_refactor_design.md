# R1 Refactor Design — High-Precision Condition-Variable Edge Selection

## 1. Executive Summary

**Rule R1** (`emit_condition_relationships → relation_for_signal`) is the dominant source of low-precision edges in the pipeline: **3,874 edges** (61% of all edges), with **50% falling back to `depends_on`** and **36% defaulting to `controls`** for any non-literal signal that guards an actuator. The root cause is that **every variable extracted from an `IF` condition receives an edge to the assignment target**, regardless of whether the variable is the *primary controller* or merely a *guard*, *feedback check*, or *temporal context*.

This document designs a replacement strategy that:
1. **Decomposes conditions** into dominant, guard, and contextual signals.
2. **Suppresses contextual and redundant guard edges** without losing control logic.
3. **Redirects mode/sensor guards** to the state machine (or suppresses them) instead of directly to every actuator.
4. **Estimates a 63% reduction** in R1 edge count (3,874 → ~1,440) while increasing precision from ~40% to ~85%.

---

## 2. Current R1 Failure Modes

### 2.1 Condition-Variable Explosion

`extract_condition_signals` extracts **all** `VariableNode` instances from a condition. For a nested state-machine branch such as:

```st
IF run AND _step = 0 AND NOT q0 AND in0 AND tx - last <= wait0 THEN
    Q0 := TRUE;
END_IF
```

The current extractor produces edges from **run, _step, q0, in0, tx** to **Q0**. Only `_step` and `run` are semantically meaningful; the rest are guards or arithmetic context.

### 2.2 False `controls` for Generic Signals

Phase 2 heuristic: `if is_actuator_target(target): candidate = "controls"`.  
Consequence: any non-literal signal (e.g., `tx`, `q0`, `in0`) guarding an actuator gets `controls`. This is semantically wrong:
- `tx` (time variable) is **not** a control source.
- `q0` (output mirror) is **feedback**, not a controller.
- `in0` (input sensor) in a state machine should **enable** or **trigger** the state transition, not directly `controls` the actuator.

### 2.3 Mode Star Problem

`run` appears in the outer condition of `SEQUENCE_8`. Currently `run` receives `controls` edges to **every** actuator and internal variable in the entire program. This creates a dense star centered on `run` that obscures the true state-machine topology (`_step → sequences → Q*`).

### 2.4 Missing `enables` / `triggers` / `disables` Coverage

Because Phase 3 only has 10 specific `source_kind → target_kind` overrides, many valid industrial patterns fall through to `depends_on` or `controls`. Examples:
- `mode → state` (run → _step) currently `controls` or `depends_on` → should be `enables`.
- `sensor → state` (in0 → _step) currently `depends_on` → should be `triggers` or `enables`.
- `history → state` (last → _step) currently `depends_on` → should be suppressed or `triggers` (if timer-driven).

---

## 3. Condition-Variable Taxonomy

Every signal in a condition is classified into one of three roles and one of eleven semantic kinds.

### 3.1 Semantic Kinds (source / target)

| Kind | Examples | Industrial Meaning |
|---|---|---|
| `state` | `_step`, `ToolChangeState`, `LightState` | State-machine selector / step register |
| `mode` | `run`, `auto`, `manual` | Global execution / program mode |
| `timer` | `Timer.Q`, `TON_1.Q` | Timer done / elapsed signal |
| `trigger_signal` | `edge`, `start`, `trigger` | One-shot event / latch |
| `reset_signal` | `rst`, `reset`, `stop` | Reset / abort command |
| `sensor` | `Xi0`, `in0`, `Proximity1` | Physical input / sensor |
| `register` | `Ri0`, `DX`, `status` | Internal data / register |
| `history` | `last`, `previous`, `old` | Retained value / timestamp |
| `process_variable` | `Pressure`, `Temp`, `Level` | Analog process measurement |
| `control_signal` | `q0`, `enable_flag`, `Si0` | Boolean control flag |
| `unknown` | `_CRC_GEN`, `REV_IN` | Unclassified / algorithmic variable |

### 3.2 Role Classification

| Role | Definition | Examples in `run AND _step=0 AND NOT q0 AND in0 AND tx-last<=wait0` |
|---|---|---|
| **Dominant** | The primary subject of the condition; the variable whose change *causes* the branch to be taken. | `_step` (state comparison), `in0` (sensor in direct guard) |
| **Guard** | Qualifies or enables the dominant; must be true but is not the *reason* for the branch. | `run` (mode guard), `q0` (feedback guard), `NOT` operand |
| **Contextual** | Provides arithmetic / temporal context; not a control source. | `tx`, `last`, `wait0` (timer arithmetic) |

### 3.3 Dominant Signal Detection Rules

```text
1. Binary comparison with state variable (e.g., _step = N, ToolChangeState = 2)
   → Dominant = state variable

2. Variable is a timer done signal (Timer.Q, TON_1.Q)
   → Dominant = timer signal

3. Variable is a trigger signal (edge, start, trigger)
   → Dominant = trigger signal

4. Variable is a process variable in a limit comparison (Pressure > Limit)
   → Dominant = process variable

5. Variable is a standalone sensor (Xi*, in*, Sensor) in a simple condition
   → Dominant = sensor

6. Otherwise (no pattern matches)
   → No dominant signal; all signals treated as co-equal
```

---

## 4. Proposed Refactor Architecture

### 4.1 High-Level Flow

```
visit_AssignmentNode
  ├── For each context in condition_stack:
  │     ├── Step 1: Decompose condition into (dominant, guards, contextual)
  │     ├── Step 2: Classify target kind
  │     ├── Step 3: Determine state-machine presence (state in any context?)
  │     ├── Step 4: For each signal in context:
  │     │     ├── If contextual → SUPPRESS
  │     │     ├── If guard AND state-machine detected → redirect or suppress
  │     │     └── If dominant or direct-control → emit relationship
  │     └── Step 5: Return refined relationships
  └── End
```

### 4.2 New Function: `decompose_condition_signals(context)`

Returns a dict:
```python
{
    "dominant": <signal> or None,
    "guards":   [<signal>, ...],
    "contextual": [<signal>, ...],
    "all":      [<signal>, ...]
}
```

**Contextual suppression rules** (hardcoded, safe):
- Any signal inside a timer arithmetic expression (`tx - last`, `ET - old`, `now - start`) is contextual.
- Any signal whose name matches `is_history()` (`last`, `previous*`) is contextual.
- Any signal that is an output mirror of the target (e.g., `q0` when target is `Q0`) is contextual feedback.

### 4.3 New Function: `should_emit(signal, role, target_kind, state_machine_active)`

| Target Kind | Dominant | Guard | Contextual | State-Machine Active? |
|---|---|---|---|---|
| `actuator` | **Emit** (primary edge) | **Suppress** if state-machine active; else emit `enables` | **Suppress** | If active, only state/mode guards may emit |
| `state` | **Emit** (transition) | **Suppress** mode guards to state; emit `triggers` for sensor/timer guards | **Suppress** | Yes |
| `timer` | **Emit** (`triggers`) | **Suppress** | **Suppress** | N/A |
| `register` | **Emit** (`depends_on` / `feeds`) | Emit if data flow is clear | **Suppress** | N/A |
| `history` | **Emit** (`depends_on`) | **Suppress** | **Suppress** | N/A |
| `unknown` | **Emit** (`depends_on`) | Emit if single-signal condition | **Suppress** | N/A |

### 4.4 Refactored `relation_for_signal` (Role-Aware)

Remove the Phase 2 catch-all (`if is_actuator_target: controls`) and replace with a **pure semantic-role matrix** that is consulted **after** role classification.

```python
SEMANTIC_ROLE_MATRIX = {
    # Dominant mappings (primary control)
    ("state",       "actuator",     "dominant"):     "sequences",
    ("mode",        "actuator",     "dominant"):     "controls",
    ("mode",        "state",        "dominant"):     "enables",
    ("sensor",      "actuator",     "dominant"):     "controls",
    ("sensor",      "state",        "dominant"):     "triggers",
    ("timer",       "actuator",     "dominant"):     "activates",
    ("timer",       "state",        "dominant"):     "triggers",
    ("trigger_signal", "actuator",  "dominant"):     "activates",
    ("trigger_signal", "state",     "dominant"):     "triggers",
    ("reset_signal", "actuator",    "dominant"):     "disables",
    ("reset_signal", "state",       "dominant"):     "disables",
    ("register",     "actuator",    "dominant"):     "controls",
    ("register",     "state",       "dominant"):     "enables",
    ("process_variable", "actuator", "dominant"):    "disables",

    # Guard mappings (secondary, conditional)
    ("mode",        "actuator",     "guard"):        "enables",
    ("mode",        "state",        "guard"):        "enables",
    ("sensor",      "actuator",     "guard"):        "enables",
    ("sensor",      "state",        "guard"):        "enables",
    ("control_signal", "actuator",  "guard"):        "enables",
    ("control_signal", "state",     "guard"):        "depends_on",

    # Fallback
    ("*",           "*",            "dominant"):     "depends_on",
    ("*",           "*",            "guard"):        "depends_on",
}
```

**Phase 1 (classifier) overrides remain**, but are only applied to **dominant** signals, never to guards or contextual signals.

---

## 5. Edge Selection Rules by Target Category

### 5.1 Actuator Targets (`Q*`, `Ho*`, `Motor*`, `Valve*`)

**State Machine Present ( `_step` or `State` in condition stack )**
- **Keep**: `state → sequences → actuator` (the state machine output)
- **Redirect**: `mode → enables → state` (instead of `mode → controls → actuator`)
- **Suppress**: `sensor`, `timer`, `history`, `control_signal` → actuator (all are transition guards, not direct controllers)
- **Exception**: If a `trigger_signal` (e.g., `edge`) is the *only* condition for a direct actuator set (not inside a state machine), emit `trigger_signal → activates → actuator`.

**No State Machine (Direct Control)**
- **Dominant** → `controls` (mode, sensor, register)
- **Guard** → `enables` (mode, sensor, control_signal)
- **Contextual** → suppress

### 5.2 State Targets (`_step`, `ToolChangeState`, `LightState`)

- **Dominant**:
  - `trigger_signal` → `triggers`
  - `timer` → `triggers`
  - `sensor` → `triggers` (event-driven state machine)
  - `reset_signal` → `disables`
  - `mode` → `enables` (mode enables the state machine globally, but mode should not be inside every step transition condition)
- **Guard**: Suppress `mode` guards to state transitions (they are global, not per-transition).
- **Contextual**: Suppress `history`, `timer arithmetic`.

### 5.3 Timer / Alarm / Counter Targets

- **Dominant**:
  - `sensor` / `trigger_signal` → `triggers`
  - `register` / `process_variable` → `depends_on` (preset / limit)
- **Guard**: `mode` → `enables` (timer only runs when mode is active)
- **Contextual**: suppress arithmetic variables.

### 5.4 Internal / Algorithmic Targets (`_CRC_GEN`, `DX`, `REV_IN`)

- **Dominant**: `signal` / `register` / `unknown` → `depends_on` or `feeds`
- **Guard**: suppress if multi-signal condition (guards are control logic, not data logic)
- **Contextual**: suppress

---

## 6. Before / After Estimates

### 6.1 Aggregate R1 Edge Counts

| Relation | Before | After | Δ | Notes |
|---|---|---|---|---|
| `depends_on` | 1,931 | **~400** | **−1,531** | Contextual/guard suppression |
| `controls` | 1,384 | **~450** | **−934** | Remove false controls from generic guards |
| `activates` | 499 | **~380** | **−119** | Redirect timer-only; suppress mixed conditions |
| `sequences` | 48 | **~120** | **+72** | State→actuator correctly classified |
| `triggers` | 9 | **~85** | **+76** | Trigger/sensor→state now captured |
| `disables` | 3 | **~25** | **+22** | Reset→state/actuator no longer falls to depends_on |
| `enables` | ~0 | **~180** | **+180** | Mode/sensor guards redirected to `enables` |
| **Total R1** | **3,874** | **~1,640** | **−2,234** | **−58% edge count** |

### 6.2 Precision Projection

| Metric | Before | After |
|---|---|---|
| R1 edges that are `depends_on` | 50% | 24% |
| R1 edges that are semantically specific (controls/sequences/triggers/activates/disables/enables) | 50% | 76% |
| Estimated overall precision (R1 only) | ~40% | **~85%** |

### 6.3 Rationale for Estimates

- **1,531 `depends_on` removed**: 
  - ~600 from contextual signals (`tx`, `last`, `wait0`, arithmetic temporaries).
  - ~500 from guards in state-machine contexts (`in0`, `q0`, `sensor` → actuator/internal).
  - ~430 from mode-to-internal star (`run` → `last`, `run` → `status`, etc.).
- **934 `controls` removed**:
  - ~600 from generic signals guarding actuators (where `is_actuator_target` was the only heuristic).
  - ~200 from sensor/feedback mirrors (`q0`, `in0` misclassified as `controls`).
  - ~130 from timer/history variables reaching actuators.
- **72 `sequences` added**:
  - State variables (`_step`, `ToolChangeState`) currently misclassified as `controls` to actuators in nested IFs (because Phase 2 `is_actuator_target` overrides Phase 3). Refactor makes `state → actuator` unambiguously `sequences`.
- **76 `triggers` added**:
  - `edge → _step`, `Timer.Q → LightState`, `in0 → _step` currently fall to `depends_on` or are swallowed by `controls`.
- **180 `enables` added**:
  - `run → _step`, `run → ToolChangeState`, `in0 → _step` (guard role).

---

## 7. Worked Examples

### 7.1 SEQUENCE_8 — State-Machine Sequencer

**Source fragment (simplified)**
```st
IF run AND _step = 0 THEN
    IF NOT q0 AND in0 AND tx - last <= wait0 THEN
        Q0 := TRUE;
        last := tx;
        _step := 1;
    END_IF
END_IF
```

**Current R1 output (for the three assignments)**
| Source | Target | Relation | Verdict |
|---|---|---|---|
| `run` | `Q0` | `controls` | Redundant star |
| `_step` | `Q0` | `sequences` | ✅ Correct |
| `q0` | `Q0` | `controls` | ❌ Feedback mirror |
| `in0` | `Q0` | `controls` | ❌ Guard, not controller |
| `tx` | `Q0` | `controls` | ❌ Contextual time var |
| `run` | `last` | `depends_on` | ❌ Mode star to internal |
| `tx` | `last` | `depends_on` | ❌ Self-assignment context |
| `run` | `_step` | `controls` | ❌ Should enable state machine |
| `_step` | `_step` | `depends_on` | ❌ Self-loop |
| `edge` | `_step` | `triggers` | ✅ Correct (from `IF start AND NOT edge`) |

**Current count for this fragment**: ~14 edges (many false).

**Refactored R1 output**
| Source | Target | Relation | Role | Reason |
|---|---|---|---|---|
| `_step` | `Q0` | `sequences` | Dominant | State machine output |
| `run` | `_step` | `enables` | Guard (redirected) | Mode enables the state machine |
| `in0` | `_step` | `enables` | Guard (redirected) | Sensor guard enables transition |
| `tx` | `last` | `depends_on` | Dominant | Direct data assignment (no state machine for `last`) |
| `edge` | `_step` | `triggers` | Dominant | One-shot trigger event |
| `rst` | `_step` | `disables` | Dominant | Reset signal |

**Refactored count for this fragment**: ~6 edges (all semantically precise).

**Reduction**: 57% fewer edges; the state-machine topology (`run → enables → _step → sequences → Q0`) is now explicit and uncluttered.

---

### 7.2 TRAFFIC_CTRL — Timer-Driven State Machine

**Source fragment (simplified)**
```st
CASE LightState OF
    0:
        Timer(IN := TRUE, PT := T#5s);
        IF Timer.Q THEN
            LightState := 1;
            PedestrianLight1 := FALSE;
        END_IF
    1:
        ...
END_CASE
```

**Current R1 output (inside `IF Timer.Q`)**
| Source | Target | Relation | Verdict |
|---|---|---|---|
| `Timer.Q` | `LightState` | `activates` | ✅ (R3 timer rule) |
| `Timer.Q` | `PedestrianLight1` | `activates` | ✅ (R3 timer rule) |

**Note**: R1 does not currently fire here because R3 (`context["kind"] == "timer"`) intercepts the timer condition and emits `activates` for the primary signal only. However, if the condition were `Timer.Q AND PedestrianRequest`, R1 would also emit `PedestrianRequest → depends_on → PedestrianLight1`.

**Refactored R1 output (hypothetical mixed condition)**
```st
IF Timer.Q AND PedestrianRequest THEN
    PedestrianLight1 := FALSE;
END_IF
```

| Source | Target | Relation | Role |
|---|---|---|---|
| `Timer.Q` | `PedestrianLight1` | `activates` | Dominant (timer) |
| `PedestrianRequest` | `PedestrianLight1` | `enables` | Guard (sensor) |

The guard edge is kept but downgraded from `controls` (or `depends_on`) to `enables`, accurately reflecting that the pedestrian request is a permissive input, not the primary driver.

---

### 7.3 TOOL_CHANGER — CASE State Machine

**Source fragment (simplified)**
```st
CASE ToolChangeState OF
    0:
        RotateCarousel := TRUE;
        ToolChangeState := 1;
    1:
        LockTool := TRUE;
        ToolChangeState := 2;
    2:
        RotateCarousel := FALSE;
        ToolChangeState := 0;
END_CASE
```

**Current output (R4 + R5 + R6)**
| Source | Target | Relation | Rule |
|---|---|---|---|
| `ToolChangeState` | `RotateCarousel` | `sequences` | R4 (case_stack) |
| `ToolChangeState` | `LockTool` | `sequences` | R4 |
| `0` | `1` | `sequences` | R5 (branch_sequence) |
| `1` | `2` | `sequences` | R5 |
| `2` | `0` | `sequences` | R5 |
| `0` | `1` | `transitions_to` | R6 (state_transition) |
| `1` | `2` | `transitions_to` | R6 |
| `2` | `0` | `transitions_to` | R6 |

**R1 interaction**: R1 is **not** invoked for the assignments inside the CASE branches because the `case_stack` path (R4) handles them. However, if a branch contains an internal `IF` (e.g., `IF ClampSensor THEN LockTool := TRUE`), R1 would fire.

**Refactored R1 (for nested IF inside CASE)**
```st
CASE ToolChangeState OF
    1:
        IF ClampSensor THEN
            LockTool := TRUE;
        END_IF
END_CASE
```

| Source | Target | Relation | Role |
|---|---|---|---|
| `ToolChangeState` | `LockTool` | `sequences` | R4 (unchanged) |
| `ClampSensor` | `LockTool` | `enables` | Guard (sensor) |
| `ClampSensor` | `ToolChangeState` | `triggers` | Redirected: sensor triggers transition, not actuator directly |

The refactor redirects the sensor from the actuator to the **state machine**, producing a cleaner topology: `ClampSensor → triggers → ToolChangeState → sequences → LockTool`.

---

### 7.4 robotic_sequence — Complex Nested Guards

**Typical pattern**
```st
IF run AND _step = 2 THEN
    IF GripperClosed AND PartPresent AND ElapsedTime - CycleStart >= T#500ms THEN
        RobotArm := TRUE;
        _step := 3;
    END_IF
END_IF
```

**Current R1 output**
- `run` → `RobotArm` (`controls`)
- `_step` → `RobotArm` (`sequences`)
- `GripperClosed` → `RobotArm` (`controls`)
- `PartPresent` → `RobotArm` (`controls`)
- `ElapsedTime` → `RobotArm` (`controls`)
- `CycleStart` → `RobotArm` (`controls`)
- `run` → `_step` (`controls`)
- `GripperClosed` → `_step` (`depends_on`)
- `PartPresent` → `_step` (`depends_on`)
- `ElapsedTime` → `_step` (`depends_on`)
- `CycleStart` → `_step` (`depends_on`)

**Count**: ~11 edges, many false.

**Refactored R1 output**
| Source | Target | Relation | Role |
|---|---|---|---|
| `_step` | `RobotArm` | `sequences` | Dominant (state output) |
| `run` | `_step` | `enables` | Guard (mode) |
| `GripperClosed` | `_step` | `enables` | Guard (sensor) |
| `PartPresent` | `_step` | `enables` | Guard (sensor) |
| `ElapsedTime` | `_step` | `triggers` | Guard (timer context → triggers transition) |
| `CycleStart` | `_step` | `depends_on` | Contextual (timer baseline) |

**Count**: 6 edges, all semantically meaningful.

- The **actuator** (`RobotArm`) receives only **one** edge (`_step → sequences`), which is the true industrial topology.
- The **sensors** and **mode** are redirected to the **state machine** (`_step`), where they belong.
- The **timer variables** (`ElapsedTime`, `CycleStart`) are either redirected as `triggers` or suppressed as contextual.

---

## 8. Implementation Plan

### 8.1 Files to Modify

| File | Change | Function(s) |
|---|---|---|
| `semantic/relationship_extractor.py` | Refactor | `emit_condition_relationships`, `relation_for_signal`, new `decompose_condition_signals`, `should_emit`, `is_contextual_signal` |
| `semantic/relationship_extractor.py` | Add heuristic | `is_output_mirror`, `is_timer_arithmetic` |
| `semantic/graph_builder.py` | Validate | Ensure `NODE_KINDS` includes all new kinds (already done) |

### 8.2 Risk Mitigation

| Risk | Mitigation |
|---|---|
| Over-suppression (losing real control paths) | Make suppression **opt-in per dataset** via a feature flag `USE_R1_REFACTOR`. Run A/B against the audit script. |
| State-machine detection false negatives | Use both structural detection (`_step` or `State` in condition stack) AND classifier tag `STATE_MACHINE` / `MULTI_ACTUATOR_SEQUENCE`. If either is true, apply state-machine rules. |
| Legacy algorithmic programs (e.g., CRC_GEN) need `depends_on` | The `unknown` → `unknown` path remains `depends_on`. Only suppress when target is `actuator`, `state`, or `timer`. |
| `enables` relation is new to R1 | Add `enables` to the `interpretation_summary` builder (already supported in `semantic_graph.py`). |

### 8.3 Validation Steps

1. Run the full `semantic_diagnostics.py` audit before and after.
2. Compare `SEQUENCE_8` output: should show exactly `run → enables → _step`, `_step → sequences → Q0`, `edge → triggers → _step`, `rst → disables → _step`.
3. Ensure `TOOL_CHANGER` CASE edges (R4–R6) are **unchanged**.
4. Check total edge count drops by ~55–60% while `sequences`/`triggers`/`enables` rise.
5. Manual review of 10 random `depends_on` edges to confirm they are genuine data dependencies (e.g., `REV_IN → _CRC_GEN`).

### 8.4 Rollback Criteria

Rollback to current R1 if:
- Any dataset loses >20% of its **actuator-target edges** (indicates over-suppression).
- `SEQUENCE_8` or `TRAFFIC_CTRL` graphs become disconnected (no path from `run` to `Q0`).
- Overall `controls` count drops below 300 (indicates legitimate direct-control paths were removed).

---

## 9. Summary

The R1 refactor replaces the **"one edge per signal"** explosion model with a **"dominant + guards + suppress"** model. By structurally analyzing the condition expression, the extractor can:

1. **Identify** that `_step` is the dominant controller in a state-machine branch.
2. **Suppress** the feedback mirror `q0`, the timer variable `tx`, and the internal history `last` from polluting the actuator node.
3. **Redirect** mode guards (`run`) and sensor guards (`in0`) to the state machine, producing `enables` and `triggers` edges instead of a dense `controls` star.

**Expected outcome**: A **58% reduction** in R1 edge count, a **doubling of precision** (40% → 85%), and a graph topology that clearly reveals the industrial control structure: **mode → enables → state → sequences → actuator**.
