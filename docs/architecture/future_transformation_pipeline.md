# Future Transformation Pipeline

> Roadmap for evolving the current Structured Text semantic analyzer into an
> IEC 61499 transformation and verification platform.

---

## 1. Strategic Direction

The current project parses a subset of IEC 61131-3 Structured Text and performs
basic semantic traversal and type checking. The future system should transform
typed, semantically classified control logic into IEC 61499 architectures.

That requires more than AST conversion. IEC 61499 is event-driven and
component-oriented, while Structured Text is statement-oriented. A serious
migration pipeline must recover control intent, data dependencies, execution
conditions, and safety meaning before generating function blocks.

---

## 2. Why AST Alone Is Insufficient

An AST describes source structure, but transformation requires semantic intent.

```text
AST knows:
├── there is an IF statement
├── the condition is Temp > 100
└── the body assigns Alarm := TRUE

Transformation needs:
├── Temp is a process variable or sensor reading
├── 100 is a threshold
├── Temp > 100 is an alarm condition
├── Alarm := TRUE raises an alarm
├── the condition triggers an event boundary
└── generated IEC 61499 elements must preserve behavior
```

The project must therefore move through semantic abstraction before generation.

---

## 3. Target Future Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                    FUTURE IEC 61499 TRANSFORMATION PLATFORM                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  IEC 61131-3 Source                                                           │
│  ┌───────────────────────┐                                                    │
│  │ Structured Text Files │                                                    │
│  └───────────┬───────────┘                                                    │
│              ▼                                                                │
│  ┌───────────────────────┐        ┌─────────────────────────────────────┐     │
│  │ Parser + AST Builder  │───────▶│ Typed Semantic AST                  │     │
│  └───────────┬───────────┘        └─────────────────┬───────────────────┘     │
│              │                                      │                         │
│              ▼                                      ▼                         │
│  ┌───────────────────────┐        ┌─────────────────────────────────────┐     │
│  │ Symbolic Analysis     │───────▶│ Industrial Semantic Classifier       │     │
│  │ types / vars / deps   │        │ alarms / interlocks / actuators      │     │
│  └───────────┬───────────┘        └─────────────────┬───────────────────┘     │
│              │                                      │                         │
│              ▼                                      ▼                         │
│  ┌───────────────────────────────────────────────────────────────────────┐     │
│  │ Semantic Graph                                                        │     │
│  │ variables, conditions, actions, dependencies, safety constraints       │     │
│  └───────────────────────────────┬───────────────────────────────────────┘     │
│                                  ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐     │
│  │ Intermediate Representation (IR)                                      │     │
│  │ normalized control model independent of ST syntax                     │     │
│  └───────────────────────────────┬───────────────────────────────────────┘     │
│                                  ▼                                             │
│  ┌───────────────────────┐        ┌─────────────────────────────────────┐     │
│  │ LLM Reasoning Layer   │◀──────▶│ Rule-Based Transformation Engine     │     │
│  │ suggestions/review    │        │ deterministic mapping rules          │     │
│  └───────────┬───────────┘        └─────────────────┬───────────────────┘     │
│              │                                      │                         │
│              ▼                                      ▼                         │
│  ┌───────────────────────────────────────────────────────────────────────┐     │
│  │ IEC 61499 Architecture Generator                                      │     │
│  │ function blocks, events, data connections, execution control charts    │     │
│  └───────────────────────────────┬───────────────────────────────────────┘     │
│                                  ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐     │
│  │ Verification + Safety Validation                                      │     │
│  │ semantic equivalence, invariants, traceability, diagnostics           │     │
│  └───────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Intermediate Representation

The IR should represent industrial control meaning independently of source
syntax. It is the contract between semantic analysis and target generation.

### Candidate IR Shape

```text
ControlProgramIR
├── declarations
│   ├── variables
│   ├── types
│   └── roles
├── control_regions
│   ├── conditions
│   ├── actions
│   └── nesting
├── dependencies
│   ├── data dependencies
│   ├── control dependencies
│   └── event candidates
├── industrial_semantics
│   ├── alarms
│   ├── interlocks
│   ├── actuators
│   ├── thresholds
│   └── safety permissives
└── verification_contracts
    ├── invariants
    ├── preconditions
    └── traceability links
```

### Example IR Fragment

For:

```iecst
IF Temp > 100 THEN
    Alarm := TRUE;
END_IF;
```

Possible IR:

```text
ConditionIR
├── id: cond_001
├── kind: THRESHOLD_HIGH
├── signal: Temp
├── operator: >
├── threshold: 100
└── result_type: BOOL

ActionIR
├── id: act_001
├── kind: ALARM_RAISE
├── target: Alarm
├── value: TRUE
└── guarded_by: cond_001
```

---

## 5. Semantic Graph Generation

A semantic graph turns program meaning into an analyzable network.

```text
┌────────────┐      reads       ┌──────────────┐      guards      ┌────────────┐
│ Temp       │ ───────────────▶ │ Temp > 100   │ ───────────────▶ │ Alarm TRUE │
│ variable   │                  │ condition    │                  │ action     │
└────────────┘                  └──────────────┘                  └────────────┘
       │                                │                                │
       │ type=NUMBER                    │ kind=THRESHOLD_HIGH            │ kind=ALARM_RAISE
       │                                │                                │
       ▼                                ▼                                ▼
   sensor role                    event candidate                 IEC 61499 output
```

Graph edges should encode:

- variable reads
- variable writes
- guard relationships
- condition/action dependencies
- safety constraints
- event candidates
- data connection candidates

---

## 6. IEC 61499 Generation Concepts

IEC 61499 uses function blocks, events, data inputs/outputs, and execution
control. Structured Text migration needs mapping rules from semantic IR to
event-driven components.

| ST Semantic Concept | IEC 61499 Candidate |
|---|---|
| threshold condition | comparator / monitor function block |
| assignment to actuator | output control function block |
| alarm assignment | alarm handler function block |
| interlock chain | safety gate function block |
| nested IF | event/control dependency chain |
| variable dependency | data connection |
| condition transition | event connection |

### Example Mapping

```text
ST condition/action:

    IF Temp > 100 THEN
        Alarm := TRUE;
    END_IF;

IEC 61499 candidate:

    ┌───────────────┐   EVT_HIGH   ┌───────────────┐
    │ ThresholdHigh │─────────────▶│ AlarmCommand  │
    │ FB            │              │ FB            │
    ├───────────────┤              ├───────────────┤
    │ Temp: REAL    │─────────────▶│ Alarm: BOOL   │
    │ Limit: REAL   │              │ Value: TRUE   │
    └───────────────┘              └───────────────┘
```

---

## 7. Symbolic + LLM Hybrid Architecture

LLMs can assist migration, but they should not be the only source of truth.
Industrial systems require traceability, repeatability, and safety evidence.

```text
┌───────────────────────────────┐
│ Deterministic Compiler Layer  │
├───────────────────────────────┤
│ parser                        │
│ AST                           │
│ symbols                       │
│ type checking                 │
│ dependency graph              │
│ IR                            │
└───────────────┬───────────────┘
                │ structured facts
                ▼
┌───────────────────────────────┐
│ LLM-Assisted Reasoning Layer  │
├───────────────────────────────┤
│ transformation suggestions    │
│ naming recommendations        │
│ ambiguity review              │
│ documentation generation      │
│ migration rationale drafting  │
└───────────────┬───────────────┘
                │ proposed decisions
                ▼
┌───────────────────────────────┐
│ Verification Layer            │
├───────────────────────────────┤
│ rule checks                   │
│ type checks                   │
│ dependency validation         │
│ safety constraints            │
│ human review evidence         │
└───────────────────────────────┘
```

### Why Symbolic Systems Come First

Symbolic analysis is necessary before LLM integration because it provides:

- deterministic parsing
- repeatable type facts
- explicit variable dependencies
- auditable diagnostics
- traceable transformation inputs
- safety-critical constraints

LLMs should operate over structured semantic facts. They should not infer
critical control behavior from raw text without compiler support.

---

## 8. Formal Verification And Safety Validation

Future verification should check both semantic correctness and industrial
safety constraints.

| Verification Area | Example Question |
|---|---|
| Type preservation | Does generated IEC 61499 use compatible data types? |
| Dependency preservation | Does every ST read/write appear in generated connections? |
| Guard preservation | Is `Alarm := TRUE` still guarded by `Temp > 100`? |
| Interlock preservation | Is `Motor := TRUE` still guarded by `SafetyOK`? |
| Event causality | Are event chains consistent with control dependencies? |
| Traceability | Can every generated FB be traced to source AST/IR facts? |

### Verification Flow

```text
ST AST + semantic facts
        │
        ▼
Transformation IR ─────▶ IEC 61499 model
        │                       │
        └──────────┬────────────┘
                   ▼
          Verification engine
                   │
                   ▼
     pass / fail / warnings / trace report
```

---

## 9. Planned Milestones

| Phase | Milestone | Output |
|---:|---|---|
| 1 | Expand parser coverage | declarations, loops, CASE, FB calls |
| 2 | Add semantic metadata extraction | reads, writes, condition/action facts |
| 3 | Add industrial semantic classifier | alarms, interlocks, actuators, thresholds |
| 4 | Define IR schema | normalized transformation model |
| 5 | Build semantic graph | dependency and event candidate graph |
| 6 | Add IEC 61499 generator prototype | FB candidates and connections |
| 7 | Add verification checks | traceability and preservation reports |
| 8 | Integrate LLM assistant | review, rationale, ambiguity resolution |

---

## 10. Research Principle

> A reliable migration system should not jump directly from source text to
> generated IEC 61499. It should pass through syntax, semantics, IR,
> transformation, and verification.

This layered path is what makes the system suitable for industrial automation,
compiler research, and AI-assisted engineering.
