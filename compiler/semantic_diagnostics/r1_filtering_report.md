# R1 Filtering Report

**Scope:** `datasets/Industrial_data/Implementation_datasets`

**Change:** Added `is_edge_worthy()` filter inside `emit_condition_relationships` (Rule R1). Only the following signals now generate relationships:
- state variables
- sensors
- trigger signals
- reset signals
- timer done signals
- counters

All other signals (mode variables, generic booleans, history, timing, bookkeeping) are filtered as CONTEXT_ONLY.

## 1. Before / After Metrics

| Metric | Before | After | Δ |
|---|---|---|---|
| Total edges | 800 | 437 | -363 |
| R1 edges | 610 | 247 | -363 |
| `depends_on` edges | 418 | 155 | -263 |

**R1 reduction:** 363 edges (59.5%)
**Total graph reduction:** 363 edges (45.4%)

## 2. Top 50 Filtered Variables

These are the most frequently filtered signals (CONTEXT_ONLY) that no longer generate R1 edges.

| Rank | Variable | Filtered Occurrences |
|---|---|---|
| 1 | run | 82 |
| 2 | tx | 49 |
| 3 | Tx | 21 |
| 4 | Si3 | 21 |
| 5 | clk | 17 |
| 6 | cnt | 14 |
| 7 | Y | 12 |
| 8 | q7 | 10 |
| 9 | ToolChangeRequired | 9 |
| 10 | Ri2 | 9 |
| 11 | Ri4 | 9 |
| 12 | q1 | 8 |
| 13 | q2 | 8 |
| 14 | q3 | 8 |
| 15 | q4 | 8 |
| 16 | q5 | 8 |
| 17 | q6 | 8 |
| 18 | q0 | 6 |
| 19 | PedestrianCrossing | 6 |
| 20 | T1_Cnt | 6 |
| 21 | T2_Cnt | 6 |
| 22 | Zi2 | 6 |
| 23 | ToolCarouselPosition | 5 |
| 24 | UPDATE_TIME | 4 |
| 25 | _E | 3 |
| 26 | X | 3 |
| 27 | debug | 3 |
| 28 | x | 3 |
| 29 | PedestrianRequest1 | 3 |
| 30 | PedestrianRequest2 | 3 |
| 31 | Si1 | 3 |
| 32 | Ri5 | 3 |
| 33 | Zi4 | 3 |
| 34 | Si4 | 3 |
| 35 | Zi1 | 3 |
| 36 | Ri1 | 3 |
| 37 | Si2 | 3 |
| 38 | Ri3 | 3 |
| 39 | REV_IN | 2 |
| 40 | _CRC_GEN | 2 |
| 41 | rep | 2 |
| 42 | tc | 2 |
| 43 | ki | 2 |
| 44 | release | 2 |
| 45 | code | 2 |
| 46 | REV_OUT | 1 |
| 47 | PULSE_MODE | 1 |
| 48 | e_last | 1 |
| 49 | rx | 1 |
| 50 | dl | 1 |

## 3. Notable Filtered Patterns

### Mode variable star eliminated
- `run` was previously generating edges to every actuator and internal variable in `SEQUENCE_8` (e.g., `run → Q0`, `run → last`, `run → status`). All of these are now filtered.

### Timing / bookkeeping variables eliminated
- `tx` (time variable) — filtered from all timer arithmetic expressions.
- `last` (history) — filtered from all update conditions.
- `wait0`, `wait1`, etc. — filtered from all comparison thresholds.

### Generic control signals eliminated
- `q0`, `q1`, etc. (feedback mirrors) — filtered from `NOT q0` guard conditions.
- `clk`, `cnt`, `tmp`, `status` — filtered as local bookkeeping.

### Sensor / process variables preserved
- `in0`, `in1`, etc. — remain edge-worthy (sensors).
- `Xi1`, `Xi6`, etc. — remain edge-worthy (sensors).
- `_step` — remains edge-worthy (state variable).
- `Timer.Q` — remains edge-worthy (timer done).
- `edge`, `rst` — remain edge-worthy (trigger / reset).

---

## Validation Summary

| Check | Result |
|---|---|
| Parser modified | No |
| AST modified | No |
| Classifier modified | No |
| Graph builder modified | No |
| Dependency reasoner modified | No |
| Relationship types changed | No |
| R1 edge count reduced | Yes |
