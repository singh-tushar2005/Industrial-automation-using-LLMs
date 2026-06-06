# Industrial Vocabulary Gap Report

## Audit Scope
- **Files audited**: `datasets/Industrial_data/Implementation_datasets/*.st`
- **Pipeline stages inspected**: `semantic/classifier.py`, `semantic/relationship_extractor.py`, `semantic/graph_builder.py`
- **Goal**: Identify vocabulary gaps between actual industrial roles, current semantic classifications, and current relationship behaviors.

---

## Vocabulary Family: Xi* (Sensor Inputs)

### Identifiers Found
`Xi1`, `Xi2`, `Xi3`, `Xi4`, `Xi5`, `Xi6`, `Xi7`, `Xi8`, `Xi9`, `Xi10`

### Actual Industrial Role
**Digital sensor inputs** (proximity switches, limit switches, photoelectric sensors). In IEC 61131-3, `Xi` is a conventional prefix for input variables mapped to physical sensors.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Xi1 | `sensor` | None |
| Xi2 | **Not in graph** | None |
| Xi3 | **Not in graph** | None |
| Xi4 | `sensor` | None |
| Xi5 | `sensor` | None |
| Xi6 | `sensor` | None |
| Xi7 | `sensor` | None |
| Xi8 | `sensor` | None |
| Xi9 | `sensor` | None |
| Xi10 | `sensor` | None |

### Current Relationship Behavior
- **Xi1**: `depends_on -> State` (3×), `sequences -> Yo1`, `sequences -> Ho3`, `sequences -> Ho4`, `sequences -> Ho5`, `sequences -> Zo2`
- **Xi4-Xi9**: `depends_on -> State` (2-3× each)
- **Xi10**: `depends_on -> T1_Cnt`, `depends_on -> State`

### Misclassifications
- **Xi1 as `control_signal` source**: `infer_signal_kind` classifies Xi1 as `control_signal` because `is_control_signal` matches `Xi` prefix. However, Xi1 is a **sensor input**, not a control signal. The source_kind should be `sensor`.
- **Xi* as `depends_on` source**: Sensor inputs that trigger state changes or actuator sequences are given `depends_on` or `sequences` relationships. For state transitions, `depends_on` is semantically weak; `triggers` or `sequences` is more appropriate.

### Missing Classifications
- **Xi2, Xi3**: Declared in `sampletext_3.st` but never referenced in body logic. They do not appear in the graph because no relationships are extracted. The graph builder only sees nodes that are sources or targets of edges.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Xi* | `sensor` node kind, `control_signal` source kind, `depends_on` relation | `sensor` node kind, `sensor` source kind, `triggers` or `sequences` relation |

---

## Vocabulary Family: Ri* (Internal Registers)

### Identifiers Found
`Ri1`, `Ri2`, `Ri3`, `Ri4`, `Ri5`

### Actual Industrial Role
**Internal registers / memory variables** (Boolean flags, status bits, intermediate logic results). `Ri` is a conventional prefix for internal relay/register variables in PLC ladder logic.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Ri1 | `register` | None |
| Ri2 | `register` | None |
| Ri3 | `register` | None |
| Ri4 | `register` | None |
| Ri5 | `register` | None |

### Current Relationship Behavior
- **Ri1-Ri3, Ri5**: `depends_on -> State` (1-3× each)
- **Ri4**: `sequences -> Yo1`, `depends_on -> Parts_Count`, `depends_on -> State`

### Misclassifications
- **Ri* as `control_signal` source**: `infer_signal_kind` classifies Ri* as `control_signal` because `is_control_signal` matches `Ri` prefix. However, Ri* are **internal registers**, not control signals. The source_kind should be `register`.
- **Ri* -> State as `depends_on`**: Register-driven state transitions should use `enables` or `triggers`, not `depends_on`.

### Missing Classifications
- **Ri* in classifier**: The classifier has no tags for register-based logic. `Ri4 -> Yo1` is a register-to-actuator control path, but the classifier only sees `ACTUATOR_COORDINATION` on the actuator side, not the register side.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Ri* | `register` node kind, `control_signal` source kind, `depends_on` relation | `register` node kind, `register` source kind, `enables` or `controls` relation |

---

## Vocabulary Family: Si* (Control Signals)

### Identifiers Found
`Si1`, `Si2`, `Si3`, `Si4`

### Actual Industrial Role
**Sequence control signals** (start, stop, mode select, interlock). `Si` is a conventional prefix for control signals or sequence bits.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Si1 | `signal` | None |
| Si2 | `signal` | None |
| Si3 | `signal` | None |
| Si4 | `signal` | None |

### Current Relationship Behavior
- **Si1, Si2, Si4**: `depends_on -> State`
- **Si3**: `sequences -> Yo1`, `sequences -> Ho3`, `sequences -> Ho4`, `sequences -> Ho5`, `sequences -> Zo2`, `sequences -> Ro3`

### Misclassifications
- **Si* as `control_signal` source**: Correctly classified as `signal` node kind, but `infer_signal_kind` returns `control_signal` which is acceptable. However, Si1/Si2/Si4 -> State uses `depends_on`, which is too weak for sequence control signals.

### Missing Classifications
- **Si3 as sequence controller**: Si3 drives multiple actuators (`Yo1`, `Ho3`, `Ho4`, `Ho5`, `Zo2`, `Ro3`). The classifier does not tag Si3 as a `MULTI_ACTUATOR_SEQUENCE` source, only the actuators as targets.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Si* | `signal` node kind, `control_signal` source kind, `depends_on` relation | `signal` node kind, `signal` source kind, `triggers` or `sequences` relation |

---

## Vocabulary Family: Ho* (Actuator Outputs)

### Identifiers Found
`Ho1`, `Ho2`, `Ho3`, `Ho4`, `Ho5`

### Actual Industrial Role
**Horizontal actuator outputs** (solenoids, motors, cylinders controlling horizontal motion). `Ho` is a conventional prefix for horizontal outputs.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Ho1-Ho5 | `actuator` | `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE` |

### Current Relationship Behavior
- **Ho1-Ho2**: `sequences <- State` (2× each)
- **Ho3-Ho5**: `sequences <- State` (2× each), `sequences <- Xi1`, `sequences <- Si3`

### Misclassifications
- **Ho* as `sequences` target**: After Phase 1, Ho* targets receive `sequences` from `State`, `Xi1`, and `Si3`. The `sequences` relation is semantically acceptable for multi-actuator sequencing, but `controls` would be more precise for direct actuator commands.

### Missing Classifications
- None significant. Ho* are correctly identified as actuators.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Ho* | `actuator` node kind, `sequences` relation | `actuator` node kind, `controls` or `sequences` relation |

---

## Vocabulary Family: Ro* (Actuator Outputs)

### Identifiers Found
`Ro1`, `Ro2`, `Ro3`

### Actual Industrial Role
**Rotational actuator outputs** (rotary motors, turntables, carousel drives). `Ro` is a conventional prefix for rotational outputs.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Ro1-Ro3 | `actuator` | `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE` |

### Current Relationship Behavior
- **Ro1-Ro2**: `sequences <- State` (2× each)
- **Ro3**: `sequences <- State` (2×), `sequences <- Xi1`, `sequences <- Si3`

### Misclassifications
- Same as Ho*: `sequences` is acceptable but `controls` would be more precise for direct actuator commands.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Ro* | `actuator` node kind, `sequences` relation | `actuator` node kind, `controls` or `sequences` relation |

---

## Vocabulary Family: Yo* (Actuator Outputs)

### Identifiers Found
`Yo1`

### Actual Industrial Role
**Vertical actuator output** (lift, elevator, vertical cylinder). `Yo` is a conventional prefix for vertical outputs.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Yo1 | `actuator` | `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE` |

### Current Relationship Behavior
- `sequences <- State` (2×), `sequences <- Ri4`, `sequences <- Xi1`, `sequences <- Si3`

### Misclassifications
- Same as Ho*: `sequences` from `State` is acceptable, but `sequences` from `Ri4` (a register) is semantically weak. `controls` would be more precise.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Yo1 | `actuator` node kind, `sequences` relation | `actuator` node kind, `controls` or `sequences` relation |

---

## Vocabulary Family: Zo* (Actuator Outputs)

### Identifiers Found
`Zo1`, `Zo2`

### Actual Industrial Role
**Z-axis actuator outputs** (depth, clamp, gripper). `Zo` is a conventional prefix for Z-axis outputs.

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Zo1-Zo2 | `actuator` | `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE` |

### Current Relationship Behavior
- **Zo1**: `sequences <- State` (2×)
- **Zo2**: `sequences <- State` (2×), `sequences <- Xi1`, `sequences <- Si3`

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Zo* | `actuator` node kind, `sequences` relation | `actuator` node kind, `controls` or `sequences` relation |

---

## Vocabulary Family: Q* (Generic Outputs)

### Identifiers Found
`Q0`, `Q1`, `Q2`, `Q3`, `Q4`, `Q5`, `Q6`, `Q7`, `QX`, `Q`

### Actual Industrial Role
**Generic Boolean outputs / memory-mapped outputs**. `Q` is the standard IEC 61131-3 prefix for output variables (%QX).

### Current Semantic Classification
| Identifier | Node Kind | Classifier Tags |
|---|---|---|
| Q0-Q3 | `actuator` | `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE` |
| Q4-Q7 | `actuator` | `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE` |
| QX | **Not in graph** | None |
| Q (GEN_SIN) | **Not in graph** | None |

### Current Relationship Behavior
- **GEN_BIT**: Q0-Q3 receive `controls <- clk`, `controls <- rst`, `controls <- run`, `controls <- cnt`
- **SEQUENCE_8**: Q0-Q7 receive `controls <- rst`, `controls <- start`, `controls <- edge`, `controls <- run`, `controls <- _step`, `controls <- q*`, `controls <- in*`, `controls <- tx`
- **QX**: Declared but not used in any relationship.
- **Q (GEN_SIN)**: Declared but not used in any relationship.

### Misclassifications
- **Q0-Q3 in GEN_BIT**: Correctly classified as `actuator` and receive `controls`. No misclassification.
- **Q4-Q7 in SEQUENCE_8**: Correctly classified as `actuator` and receive `controls`. No misclassification.
- **QX**: Not in graph because it is only used in an expression `QX := q0 OR q1 OR ...` but the extractor does not generate relationships for `OR` expressions.
- **Q (GEN_SIN)**: Not in graph because it is declared but never assigned or used in a condition.

### Missing Classifications
- **QX and Q (GEN_SIN)**: These are legitimate output variables but do not appear in the graph because the relationship extractor only generates edges for assignments and conditions, not for variable declarations.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| Q* | `actuator` node kind, `controls` relation | `actuator` node kind, `controls` relation |
| QX, Q (GEN_SIN) | **Not in graph** | `actuator` node kind, no relationships |

---

## Vocabulary Family: `run`

### Identifiers Found
`run` (appears in `FLOW_METER.st`, `FT_PIDWL.st`, `GEN_BIT.st`, `INCLUDE.st`, `SEQUENCE_8.st`)

### Actual Industrial Role
**Execution control flag / run permissive**. In `SEQUENCE_8`, `run` is the master enable for the step sequencer. In `GEN_BIT`, `run` is the cycle enable flag.

### Current Semantic Classification
| File | Node Kind | Classifier Tags |
|---|---|---|
| FLOW_METER | Not in graph | None |
| FT_PIDWL | Not in graph | None |
| GEN_BIT | `unknown` | None |
| INCLUDE | `signal` | None |
| SEQUENCE_8 | `unknown` | None |

### Current Relationship Behavior
- **GEN_BIT**: `run` receives `depends_on <- clk`, `depends_on <- rst`, `depends_on <- rx`, `depends_on <- rep`. `run` emits `controls -> Q0-Q3`, `depends_on -> cnt`, `depends_on -> r0-r3`, `depends_on -> rx`.
- **INCLUDE**: `run` emits `depends_on -> out`, `depends_on -> old`.
- **SEQUENCE_8**: `run` receives `depends_on <- rst`, `depends_on <- start`, `depends_on <- edge`. `run` emits `controls -> Q0-Q7`, `depends_on -> last`, `depends_on -> status`, `depends_on -> q*`, `depends_on -> _step`.

### Misclassifications
- **Node kind `unknown`**: In `GEN_BIT` and `SEQUENCE_8`, `run` is classified as `unknown` because `infer_target_kind` does not match any pattern. `run` should be `signal` or `mode`.
- **Source kind `signal`**: Correct in `INCLUDE`, but in `GEN_BIT` and `SEQUENCE_8`, `run` is the source of `controls` edges. The source_kind should be `control_signal` or `mode`, not `signal`.
- **Relationship `depends_on`**: `run` driving `Q*` should be `controls`, not `depends_on`. In `GEN_BIT`, `run -> depends_on -> cnt` is semantically weak; `triggers` or `enables` would be better.

### Missing Classifications
- **FLOW_METER, FT_PIDWL**: `run` appears only in comments (`(* run integrator *)`, `(* run PIWL controller first *)`). The extractor does not process comments.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| run | `unknown` or `signal` node kind, `depends_on` relation | `signal` or `mode` node kind, `controls` or `enables` relation |

---

## Vocabulary Family: `rst`

### Identifiers Found
`rst` (appears in `FT_PIDWL.st`, `GEN_BIT.st`, `SEQUENCE_8.st`)

### Actual Industrial Role
**Reset signal / master reset flag**. Used to clear state, reset counters, and restart sequences.

### Current Semantic Classification
| File | Node Kind | Classifier Tags |
|---|---|---|
| FT_PIDWL | `signal` | None |
| GEN_BIT | `signal` | None |
| SEQUENCE_8 | `signal` | None |

### Current Relationship Behavior
- **FT_PIDWL**: `rst -> depends_on -> piwl.RST`
- **GEN_BIT**: `rst` emits `depends_on -> run`, `depends_on -> cnt`, `depends_on -> r0-r3`, `controls -> Q0-Q3`, `depends_on -> rx`.
- **SEQUENCE_8**: `rst` emits `depends_on -> _step`, `depends_on -> run`, `controls -> Q0-Q7`.

### Misclassifications
- **Node kind `signal`**: Correct.
- **Relationship `depends_on`**: `rst -> depends_on -> run` and `rst -> depends_on -> _step` are semantically weak. A reset signal should use `disables` or `triggers` for state clearing, and `controls` for actuator reset.
- **Source kind**: `source_kind=signal` is correct for a reset signal.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| rst | `signal` node kind, `depends_on` relation | `signal` node kind, `disables` or `triggers` for state/counter reset, `controls` for actuator reset |

---

## Vocabulary Family: `edge`

### Identifiers Found
`edge` (appears in `SEQUENCE_8.st`)

### Actual Industrial Role
**Edge detection flag / one-shot trigger**. Used to detect rising edges on the `start` input and trigger a single sequence restart.

### Current Semantic Classification
| File | Node Kind | Classifier Tags |
|---|---|---|
| SEQUENCE_8 | `signal` | None |

### Current Relationship Behavior
- `edge` emits `depends_on -> _step`, `depends_on -> last`, `depends_on -> status`, `controls -> Q0-Q7`, `depends_on -> run`.

### Misclassifications
- **Node kind `signal`**: Acceptable, but `edge` is more precisely a **history** or **timer** element because it stores the previous state of `start`.
- **Relationship `depends_on`**: `edge -> depends_on -> _step` and `edge -> depends_on -> run` are semantically weak. An edge trigger should use `triggers` or `activates`.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| edge | `signal` node kind, `depends_on` relation | `history` or `signal` node kind, `triggers` or `activates` relation |

---

## Vocabulary Family: `_step`

### Identifiers Found
`_step` (appears in `SEQUENCE_8.st`)

### Actual Industrial Role
**Step counter / sequencer state variable**. `_step` stores the current step index (0-7) and drives the CASE statement that selects which Q* output to activate.

### Current Semantic Classification
| File | Node Kind | Classifier Tags |
|---|---|---|
| SEQUENCE_8 | `unknown` | None |

### Current Relationship Behavior
- `_step` receives `depends_on <- rst`, `depends_on <- start`, `depends_on <- edge`.
- `_step` emits `controls -> Q0-Q7`, `depends_on -> last`, `depends_on -> status`, `depends_on -> run`, `depends_on -> q*`.

### Misclassifications
- **Node kind `unknown`**: `_step` is a **state** variable, not `unknown`. It is the selector for a CASE statement that implements a state machine.
- **Source kind**: In relationships, `_step` is labeled as `source_kind=signal` (inherited from `infer_signal_kind`). It should be `state`.
- **Relationship `depends_on`**: `_step -> depends_on -> run` and `_step -> depends_on -> q*` are semantically weak. `_step` should use `sequences` or `controls` for Q* outputs, and `triggers` or `activates` for run/status.

### Desired Behavior
| Role | Current Behavior | Desired Behavior |
|---|---|---|
| _step | `unknown` node kind, `depends_on` relation | `state` node kind, `controls` or `sequences` relation for Q*, `triggers` for run/status |

---

## Summary Table

| Identifier | Actual Role | Current Node Kind | Current Source Kind | Current Relation | Desired Node Kind | Desired Source Kind | Desired Relation |
|---|---|---|---|---|---|---|---|
| Xi* | Sensor input | `sensor` | `control_signal` | `depends_on` | `sensor` | `sensor` | `triggers` |
| Ri* | Internal register | `register` | `control_signal` | `depends_on` | `register` | `register` | `enables` / `controls` |
| Si* | Control signal | `signal` | `control_signal` | `depends_on` | `signal` | `signal` | `triggers` / `sequences` |
| Ho* | Horizontal actuator | `actuator` | — | `sequences` | `actuator` | — | `controls` / `sequences` |
| Ro* | Rotational actuator | `actuator` | — | `sequences` | `actuator` | — | `controls` / `sequences` |
| Yo1 | Vertical actuator | `actuator` | — | `sequences` | `actuator` | — | `controls` / `sequences` |
| Zo* | Z-axis actuator | `actuator` | — | `sequences` | `actuator` | — | `controls` / `sequences` |
| Q* | Generic output | `actuator` | — | `controls` | `actuator` | — | `controls` |
| QX | Aggregate output | **Not in graph** | — | — | `actuator` | — | — |
| Q (GEN_SIN) | Boolean output | **Not in graph** | — | — | `actuator` | — | — |
| run | Execution flag | `unknown` / `signal` | `signal` | `depends_on` | `signal` / `mode` | `control_signal` | `controls` / `enables` |
| rst | Reset signal | `signal` | `signal` | `depends_on` | `signal` | `signal` | `disables` / `triggers` |
| edge | Edge trigger | `signal` | `signal` | `depends_on` | `history` / `signal` | `signal` | `triggers` / `activates` |
| _step | Sequencer state | `unknown` | `signal` | `depends_on` | `state` | `state` | `controls` / `sequences` |

---

## Root Cause Analysis

### 1. `infer_signal_kind` is overly broad
`is_control_signal` in `relationship_extractor.py` matches `Xi`, `Ri`, `Si`, `Zi` prefixes as control signals. This causes sensor inputs and internal registers to be labeled as `control_signal` source kind, which is semantically incorrect.

### 2. `infer_target_kind` lacks `state` and `history` patterns
- `run` is not matched by any pattern, so it becomes `unknown`.
- `_step` is not matched by any pattern, so it becomes `unknown`.
- `edge` matches `is_signal` (because it contains no special terms) and gets `signal`, but it should be `history`.

### 3. `is_actuator_name` is now consistent but `is_actuator_target` still relies on output variable detection
- `Q*` in `GEN_SIN` and `QX` in `SEQUENCE_8` are not in `memory_mapped_outputs` or `bool_output_variables` because they lack `%Q` AT mappings or VAR_OUTPUT declarations.
- The graph builder's `is_actuator_name` recognizes `Q\d+`, but the relationship extractor only adds nodes that are sources or targets of edges. `QX` and `Q` (GEN_SIN) are never sources or targets because they are only declared, not used in assignments or conditions.

### 4. Relationship extractor does not generate edges for variable declarations
- Variables that are declared but never used in assignments or conditions do not appear in the graph. This is a structural limitation, not a vocabulary gap.

### 5. `relation_for_signal` falls back to `depends_on` for non-actuator, non-timer, non-FB targets
- `run`, `rst`, `edge`, `_step` driving non-actuator targets (like `last`, `status`, `run`, `_step`, `cnt`) get `depends_on` because they are not recognized as meaningful control sources for those targets.
- `run` driving `Q*` gets `controls` because `Q*` is an actuator, but `run` driving `cnt` or `last` gets `depends_on`.

