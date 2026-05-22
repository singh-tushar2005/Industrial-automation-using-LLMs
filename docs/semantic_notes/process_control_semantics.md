# Process Control Semantics

Process control semantics describe how Structured Text logic interacts with
industrial equipment, operating modes, alarms, and plant conditions.

---

## Process-Centric Interpretation

A compiler-style pipeline can identify more than syntax:

```text
IF TankLevel > HighLevel THEN
    InletValve := FALSE;
    Pump := FALSE;
    Alarm := TRUE;
END_IF;
```

Process interpretation:

```text
TankLevel > HighLevel  → overfill protection
InletValve := FALSE    → stop inlet flow
Pump := FALSE          → stop transfer
Alarm := TRUE          → notify fault condition
```

This becomes transformation-oriented metadata:

```text
PROCESS_LIMIT_PROTECTION
ACTUATOR_COORDINATION
ALARM_CONDITION
```

---

## Sequencing And Modes

Industrial workflows are often stateful:

```iecst
CASE BatchStep OF
    0:
        InletValve := TRUE;
    1:
        Mixer := TRUE;
    2:
        OutletValve := TRUE;
END_CASE;
```

Semantic meaning:

```text
BatchStep
├── state 0: fill
├── state 1: mix
└── state 2: discharge
```

This is a candidate for IEC 61499 execution control modeling or event-driven
state transitions.

---

## Transformation-Oriented Metadata

The classifier returns findings that are intentionally shaped for later
pipeline stages.

```text
Finding
├── tag
├── description
├── evidence
├── confidence
├── source node type
└── transformation hints
```

The metadata should later feed:

- semantic IR construction
- dependency graph generation
- IEC 61499 function block candidate selection
- safety validation
- LLM-assisted review and rationale generation

---

## Layered Semantic Analysis

The project should continue to keep semantic layers separate:

```text
Type checker
    validates correctness

Industrial classifier
    identifies behavior

Future semantic graph builder
    connects reads, writes, guards, and actions

Future IR builder
    normalizes behavior for IEC 61499 transformation
```

This prevents industrial interpretation rules from being mixed into low-level
type compatibility checks.
