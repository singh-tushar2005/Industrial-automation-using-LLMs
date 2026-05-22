# Classifier Deep Dive

> The industrial classifier interprets typed AST structures as automation
> behavior.

---

## 1. Purpose

The classifier solves a higher-level semantic problem:

```text
What industrial behavior does this control logic represent?
```

The type checker can validate:

```text
TankLevel > HighLevel → BOOL
```

The classifier interprets:

```text
TankLevel > HighLevel → PROCESS_LIMIT_PROTECTION
```

This is the transition from syntax-centric analysis toward industrial process
semantic understanding.

---

## 2. Inputs

The classifier receives:

```text
AST
    from parser

type report
    from TypeChecker
```

The type report is context. The classifier still walks the AST itself using the
existing visitor infrastructure.

---

## 3. Outputs

The classifier returns structured semantic metadata:

```text
{
  findings: [...],
  finding_count,
  tags,
  semantic_model
}
```

Each finding includes:

```text
tag
description
evidence
node_type
confidence
transformation_hints
```

This output is designed for:

- future semantic IR generation
- IEC 61499 transformation
- industrial behavior modeling
- symbolic verification
- future LLM-assisted reasoning

---

## 4. Internal Logic

The classifier subclasses the existing visitor system.

```text
IndustrialSemanticClassifier(ASTVisitor)
```

It does not duplicate traversal infrastructure. It defines node-specific
classification behavior:

```text
visit_IfStatementNode()
visit_CaseStatementNode()
visit_AssignmentNode()
visit_FunctionBlockCallNode()
```

The visitor dispatch system handles recursive movement through the AST.

---

## 5. Semantic Abstraction Layers

```text
AST structure
    IF TankLevel > HighLevel THEN Alarm := TRUE

Type checker
    TankLevel: NUMBER
    HighLevel: NUMBER
    condition: BOOL
    Alarm: BOOL

Classifier
    PROCESS_LIMIT_PROTECTION
    ALARM_CONDITION

Future IR
    threshold guard + alarm action
```

The classifier is higher-level than the type checker but lower-level than a
full transformation generator.

---

## 6. Industrial Semantic Examples

### Process Limit Protection

```iecst
IF Pressure > PressureHighLimit THEN
    Pump := FALSE;
    Alarm := TRUE;
END_IF;
```

Findings:

```text
PROCESS_LIMIT_PROTECTION
ACTUATOR_COORDINATION
ALARM_CONDITION
```

### Safety Logic

```iecst
IF StartCommand AND SafetyOK AND GuardClosed THEN
    MotorRun := TRUE;
END_IF;
```

Findings:

```text
SAFETY_INTERLOCK
PROCESS_ENABLE_CONDITION
ACTUATOR_COORDINATION
```

### Timer-Dependent Control

```iecst
StartTimer(IN := StartCommand, PT := T#5s);

IF StartTimer.Q THEN
    Motor := TRUE;
END_IF;
```

Findings:

```text
TIMER_DEPENDENT_CONTROL
ACTUATOR_COORDINATION
```

### Actuator Coordination

```iecst
IF EmergencyStop THEN
    Motor := FALSE;
    Pump := FALSE;
    InletValve := FALSE;
END_IF;
```

Findings:

```text
EMERGENCY_SHUTDOWN
ACTUATOR_COORDINATION
SAFETY_INTERLOCK
```

---

## 7. What This Subsystem Does Not Do

The classifier does not:

- replace the parser
- replace AST generation
- replace type checking
- perform machine learning
- generate IEC 61499 directly
- print reports directly
- implement a separate traversal engine

It is symbolic and rule-based. It interprets already parsed and checked program
structure.

---

## 8. Relationships

```text
parser
    ↓
AST
    ↓
type checker ─────▶ type report
    ↓                 │
classifier ◀─────────┘
    ↓
industrial semantic metadata
```

`main.py` orchestrates this relationship. The classifier remains a semantic
module and returns data.

---

## 9. Industrial Transformation Relevance

IEC 61499 transformation needs behavior categories:

- safety gates
- timers
- alarms
- actuator outputs
- process thresholds
- modes
- sequences
- fault recovery

The classifier creates these categories from AST evidence. This is the bridge
between compiler analysis and industrial architecture generation.

---

## 10. Key Principle

> The classifier interprets industrial meaning. It should be downstream of
> parsing and type checking, and upstream of IR/generation.
