# Industrial Semantic Classification

Industrial semantic classification is the layer above ordinary type checking.
It interprets control behavior in terms that matter to automation engineers and
future IEC 61499 transformation passes.

---

## Semantic Abstraction Levels

```text
Source text
    ↓
Parser
    ↓
AST structure
    ↓
Semantic traversal
    ↓
Type checking
    ↓
Industrial semantic classification
    ↓
Transformation-oriented metadata
    ↓
Future semantic IR / IEC 61499 generation
```

Each level answers a different question.

| Layer | Question | Example |
|---|---|---|
| Parser | Is the syntax valid? | `IF Temp > 100 THEN ... END_IF;` |
| AST | What is the structure? | IF node with comparison condition |
| Type checker | Are values compatible? | `Temp` is numeric, condition is BOOL |
| Classifier | What industrial behavior is present? | high-temperature alarm protection |
| IR builder | How should behavior be normalized? | threshold guard + alarm action |

---

## Classifier Role

`semantic/classifier.py` is a symbolic, rule-based semantic pass. It reuses the
existing visitor infrastructure and does not implement a separate traversal
engine.

The classifier identifies patterns such as:

- `SAFETY_INTERLOCK`
- `CONTROLLED_STARTUP_SEQUENCE`
- `FAULT_PROTECTION_SEQUENCE`
- `TIMER_DEPENDENT_CONTROL`
- `ACTUATOR_COORDINATION`
- `ALARM_CONDITION`
- `PROCESS_LIMIT_PROTECTION`
- `MODE_SELECTION_LOGIC`
- `EMERGENCY_SHUTDOWN`
- `PROCESS_ENABLE_CONDITION`
- `PROCESS_SEQUENCING`
- `INDUSTRIAL_FAULT_RECOVERY`

The output is structured metadata. It is intended for future transformation,
semantic IR generation, symbolic checks, and LLM-assisted review.

---

## Example: Process Limit Protection

Structured Text:

```iecst
IF Temperature > TempHighLimit THEN
    Heater := FALSE;
    CoolingValve := TRUE;
    Alarm := TRUE;
END_IF;
```

Type checker view:

```text
Temperature      → NUMBER
TempHighLimit    → NUMBER
Temperature > TempHighLimit → BOOL
Heater := FALSE  → valid BOOL assignment
```

Classifier view:

```text
PROCESS_LIMIT_PROTECTION
├── evidence: Temperature > TempHighLimit
├── meaning: process threshold exceeded
└── transformation hint: create threshold guard in semantic IR

ACTUATOR_COORDINATION
├── evidence: Heater := FALSE, CoolingValve := TRUE
└── meaning: coordinated thermal response

ALARM_CONDITION
├── evidence: Alarm := TRUE
└── meaning: operator or system alarm raised
```

---

## Industrial Behavior Categories

| Category | Typical Evidence | Transformation Meaning |
|---|---|---|
| Safety interlock | `SafetyOK`, `GuardClosed`, `DoorClosed` | safety gate before output command |
| Emergency shutdown | `EmergencyStop`, `EStop` | high-priority safe-state transition |
| Timer-dependent control | `TON`, `TOF`, `TP`, `.Q` | time-based event or guard |
| Actuator coordination | multiple output assignments | grouped output behavior |
| Alarm condition | `Alarm := TRUE` | alarm event/output mapping |
| Fault recovery | `FaultReset`, `FaultActive := FALSE` | recovery transition |
| Mode selection | `CASE Mode OF` | mode/state dispatch |
| Process sequencing | `CASE SequenceStep OF` | execution control state machine |
| Limit protection | `Pressure > PressureHighLimit` | threshold guard |

---

## Why This Matters For IEC 61499

IEC 61499 generation needs semantic intent, not only AST shape.

```text
ST condition/action
    ↓
Semantic classification
    ↓
IR condition/action model
    ↓
IEC 61499 function block and event/data connections
```

For example, a threshold condition and alarm assignment can become a comparator
function block connected to an alarm handling function block. A timer call and
`.Q` condition can become a timer FB whose output event gates downstream logic.

The classifier is therefore a bridge between compiler analysis and industrial
architecture generation.
