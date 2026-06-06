# Semantic Integration Phase 1 Report

## Objective
Reduce `depends_on` overgeneration by wiring existing classifier findings into `relationship_extractor.py` during relationship extraction.

## Scope
- **Target datasets**: `datasets/Industrial_data/Implementation_datasets`
- **Modified files**: `semantic/relationship_extractor.py`
- **Modified functions**: 3 (`is_actuator_name`, `relation_for_signal`, `import re`)
- **Constraint**: No architecture redesign, no new node types, no new graph abstractions.

## Mapping Table

| Classifier Tag | Target Relation | Trigger Condition | Rationale |
|---|---|---|---|
| `MULTI_ACTUATOR_SEQUENCE` | `sequences` | `target` appears in the classifier's evidence list | Multiple actuators commanded in sequence; edges to sequence members are upgraded from `depends_on` to `sequences` |
| `PROCESS_CONTROL` | `controls` | `target` is an actuator and current unit name matches evidence | Control unit commanding an actuator; overrides generic `depends_on` |
| `SAFETY_INTERLOCK` | `enables` | Condition text matches evidence | Safety permissive signal |
| `EMERGENCY_SHUTDOWN` | `disables` | Condition text matches evidence | Emergency stop signal |
| `FAULT_PROTECTION_SEQUENCE` | `disables` | Condition text matches evidence | Fault protection signal |
| `PROCESS_ENABLE_CONDITION` | `enables` | Condition text matches evidence | Process enable signal |
| `TIMER_DEPENDENT_CONTROL` | `activates` | Condition text matches evidence | Timer-driven activation |
| `STATE_MACHINE` | `transitions_to` | `context["kind"] == "state_change"` | State machine transition |

## Vocabulary Update

`is_actuator_name` was also extended to recognise PLC naming patterns (`Ho\d+`, `Ro\d+`, `Zo\d+`, `Yo\d+`, `Q\d+`) that were already present in `semantic/classifier.py` and `semantic/graph_builder.py` but missing from the extractor. This ensures consistency across the pipeline.

## Implementation Datasets: Before vs After Metrics

### Per-File Comparison

| File | depends_on (before) | depends_on (after) | controls (before) | controls (after) | sequences (before) | sequences (after) | transitions_to (before) | transitions_to (after) | activates (before) | activates (after) | triggers (before) | triggers (after) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `robotic_sequence.st` | 49 | 36 | 0 | 0 | 38 | 51 | 12 | 12 | 0 | 0 | 0 | 0 |
| `sampletext_2.st` | 49 | 36 | 0 | 0 | 38 | 51 | 12 | 12 | 0 | 0 | 0 | 0 |
| `sampletext_3.st` | 49 | 36 | 0 | 0 | 38 | 51 | 12 | 12 | 0 | 0 | 0 | 0 |
| `FT_PIDWL.st` | 1 | 1 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `MATRIX.st` | 1 | 1 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `INCLUDE.st` | 27 | 27 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `TRAFFIC_CTRL.st` | 7 | 7 | 4 | 6 | 17 | 17 | 4 | 4 | 18 | 16 | 3 | 3 |
| `GEN_BIT.st` | 56 | 56 | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `SEQUENCE_8.st` | 183 | 183 | 103 | 103 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `TOOL_CHANGER.st` | 5 | 5 | 7 | 7 | 6 | 6 | 3 | 3 | 0 | 0 | 0 | 0 |
| `CRC_GEN.st` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `FLOW_METER.st` | 22 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `GEN_SIN.st` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `LAMBERT_W.st` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `DEC_TO_HEX.st` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `sampletext_4.st` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Aggregate Totals

| Relation | Before | After | Change |
|---|---|---|---|
| `depends_on` | 459 | 420 | **−39 (−8.5%)** |
| `controls` | 140 | 136 | **−4 (−2.9%)** |
| `sequences` | 137 | 182 | **+45 (+32.8%)** |
| `transitions_to` | 43 | 43 | 0 |
| `activates` | 18 | 16 | **−2 (−11.1%)** |
| `triggers` | 3 | 3 | 0 |
| **Total** | **800** | **800** | **0** |

## Analysis

### What Changed
1. ** robotic_sequence / sampletext_2 / sampletext_3**: `MULTI_ACTUATOR_SEQUENCE` classifier finding identified PLC actuators (`Yo1`, `Ro1`, `Ro2`, `Ro3`, `Ho1`–`Ho5`, `Zo1`, `Zo2`). The extractor now converts 13 `depends_on` edges per file to `sequences` (39 total).
2. **TRAFFIC_CTRL**: `PROCESS_CONTROL` finding (`TrafficLightControl`) converts 2 `activates` edges to `controls` for actuator targets (`NorthSouthGreen`, `NorthSouthYellow`, etc.) inside the control unit.
3. **FT_PIDWL / MATRIX / INCLUDE**: `MULTI_ACTUATOR_SEQUENCE` evidence is `Run_Count`. The extractor converts the 2 `controls` edges per file to `sequences`. This is a false positive because `Run_Count` is a counter, not an actuator, but the classifier lists it as sequence evidence.

### Impact on `depends_on`
- **39 fewer `depends_on` edges** (8.5% reduction) across the 3 robotic sequence files.
- The 6 `controls` → `sequences` conversions in `FT_PIDWL`/`MATRIX`/`INCLUDE` are neutral for `depends_on` but reduce `controls`.
- `PROCESS_CONTROL` converts `activates` → `controls` (2 edges), which is a precision improvement but does not affect `depends_on`.

### Precision Notes
- **True positives**: The 39 `depends_on` → `sequences` conversions in robotic sequence files are correct. The PLC actuators are genuinely part of a multi-actuator sequence.
- **False positives**: `Run_Count` in `FT_PIDWL`/`MATRIX`/`INCLUDE` is treated as an actuator sequence member. Future Phase 2 should filter classifier evidence through `is_actuator_target()` before accepting it.
- **Vocabulary consistency**: The PLC pattern update (`Ho\d+`, `Ro\d+`, etc.) ensures the extractor now recognises the same actuators as the classifier and graph builder, closing a vocabulary gap.

## Conclusion

Phase 1 achieved an **8.5% reduction in `depends_on`** (39 edges) by wiring two classifier tags (`MULTI_ACTUATOR_SEQUENCE`, `PROCESS_CONTROL`) into the extractor. The `sequences` relation now absorbs the converted edges, improving semantic precision. The remaining `depends_on` overgeneration (420 edges) is dominated by `SEQUENCE_8` (183 edges) and `GEN_BIT` (56 edges), which lack matching classifier findings. Phase 2 should focus on those files.
