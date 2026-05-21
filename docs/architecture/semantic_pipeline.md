# Semantic Pipeline

> Architecture specification for semantic traversal, symbol management, type
> checking, and future industrial semantic classification.

---

## 1. Semantic Layer Mission

The semantic layer answers questions that syntax alone cannot answer.

```text
Syntax question:   Is "IF Temp > 100 THEN ..." shaped like valid ST?
Semantic question: Is Temp numeric, is the condition boolean, and what does
                   this logic mean in an industrial control context?
```

The current semantic pipeline is custom-built for this project. The visitor,
symbol table, and type checker are project code, not external semantic analysis
libraries.

---

## 2. Current Semantic Components

| Component | Module | Built With | Role |
|---|---|---|---|
| Base visitor | `semantic/visitor.py` | custom Python dispatch | routes AST nodes to `visit_*` methods |
| Traversal visitor | `semantic/visitor.py` | custom visitor | records recursive AST traversal events |
| Symbol table | `semantic/symbol_table.py` | custom dictionary wrapper | stores variable type facts |
| Type checker | `semantic/type_checker.py` | custom semantic pass | validates expression and assignment types |
| Report formatting | `main.py` | orchestration layer | prints semantic results |

---

## 3. Semantic Traversal Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SEMANTIC TRAVERSAL PASS                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ProgramNode                                                           │
│      │                                                                 │
│      ▼                                                                 │
│  visit_ProgramNode()                                                   │
│      │                                                                 │
│      ▼                                                                 │
│  BlockNode ───────────────▶ visit_BlockNode()                          │
│      │                                                                 │
│      ├── Statement 1 ─────▶ visit_IfStatementNode()                    │
│      │                         │                                       │
│      │                         ├── condition ─▶ visit expression       │
│      │                         └── body      ─▶ visit BlockNode        │
│      │                                                                 │
│      └── Statement N ─────▶ visit_AssignmentNode()                     │
│                                │                                       │
│                                ├── target ─▶ visit_VariableNode()      │
│                                └── value  ─▶ visit expression          │
│                                                                        │
│  Output: ordered traversal events with depth metadata                   │
└────────────────────────────────────────────────────────────────────────┘
```

The traversal pass currently produces explainability data. That same recursive
structure is the foundation for later passes that extract reads, writes,
dependencies, safety conditions, and transformation candidates.

---

## 4. Visitor Pattern

The base visitor dispatches by node class name:

```text
VariableNode           → visit_VariableNode()
BooleanNode            → visit_BooleanNode()
BinaryExpressionNode   → visit_BinaryExpressionNode()
LogicalExpressionNode  → visit_LogicalExpressionNode()
AssignmentNode         → visit_AssignmentNode()
IfStatementNode        → visit_IfStatementNode()
BlockNode              → visit_BlockNode()
ProgramNode            → visit_ProgramNode()
```

This pattern keeps AST classes focused on data. New analysis passes can reuse
the same AST without modifying node definitions.

---

## 5. Symbol Table Architecture

The current symbol table is intentionally simple:

```text
┌──────────────────────┐
│ SymbolTable          │
├──────────────────────┤
│ symbols: dict        │
│                      │
│ Alarm       → BOOL   │
│ Counter     → NUMBER │
│ Limit       → NUMBER │
│ Motor       → BOOL   │
│ SafetyOK    → BOOL   │
│ StartButton → BOOL   │
│ Temp        → NUMBER │
│ Warning     → BOOL   │
└──────────────────────┘
```

The current parser does not support declarations yet, so
`build_demo_symbol_table()` preloads known dataset variables. Future symbol data
should come from parsed `VAR` declarations, PLC tag databases, engineering
exports, or vendor project files.

### Future Symbol Table Shape

```text
ProjectScope
├── ProgramScope
│   ├── input variables
│   ├── output variables
│   ├── local variables
│   └── temporary variables
└── FunctionBlockScope
    ├── ports
    ├── internal state
    └── instance variables
```

---

## 6. Type Checking Workflow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         TYPE CHECKING PASS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  AST node                                                           │
│     │                                                               │
│     ▼                                                               │
│  visit node recursively                                             │
│     │                                                               │
│     ├── VariableNode                                                │
│     │      └── lookup type in SymbolTable                           │
│     │                                                               │
│     ├── BooleanNode                                                 │
│     │      └── return BOOL                                          │
│     │                                                               │
│     ├── NumberNode                                                  │
│     │      └── return NUMBER                                        │
│     │                                                               │
│     ├── BinaryExpressionNode                                        │
│     │      ├── check left type                                      │
│     │      ├── check right type                                     │
│     │      └── validate operator rule                               │
│     │                                                               │
│     ├── LogicalExpressionNode                                       │
│     │      └── require BOOL operands                                │
│     │                                                               │
│     └── AssignmentNode                                              │
│            └── require compatible target/value types                │
│                                                                     │
│  Output: errors, warnings, symbol map, analysis metadata             │
└─────────────────────────────────────────────────────────────────────┘
```

### Current Type Rules

| Construct | Rule | Result |
|---|---|---|
| Boolean literal | `TRUE` or `FALSE` | `BOOL` |
| Numeric literal | integer or decimal | `NUMBER` |
| Variable reference | lookup in symbol table | known type or `UNKNOWN` |
| Arithmetic | operands must be `NUMBER` | `NUMBER` |
| Ordering comparison | operands must be `NUMBER` | `BOOL` |
| Equality comparison | known operands should match | `BOOL` |
| Logical expression | operands must be `BOOL` | `BOOL` |
| IF condition | condition must be `BOOL` or `UNKNOWN` | statement check |
| Assignment | target and value must be compatible | statement check |

---

## 7. Industrial Semantic Classification

The current type checker validates basic meaning. The next semantic layer should
classify industrial intent.

| Industrial Meaning | Example ST Pattern | Candidate Tag |
|---|---|---|
| Threshold condition | `Temp > 100` | `THRESHOLD_HIGH` |
| Safety logic | `StartButton AND SafetyOK` | `SAFETY_INTERLOCK_CONDITION` |
| Actuator control | `Motor := TRUE` | `ACTUATOR_ENABLE` |
| Alarm condition | `Alarm := TRUE` inside threshold IF | `ALARM_RAISE` |
| Interlock logic | `SafetyOK AND DoorClosed` | `INTERLOCK_CHAIN` |
| Reset command | `Alarm := FALSE` | `ALARM_CLEAR` |

These tags should be computed from AST structure plus symbol/type facts. They
should not be guessed from raw text alone.

---

## 8. Worked Example: Alarm Threshold

Source:

```iecst
IF Temp > 100 THEN
    Alarm := TRUE;
END_IF;
```

AST-level facts:

```text
IfStatementNode
├── condition: BinaryExpressionNode(">")
│   ├── left: VariableNode("Temp")
│   └── right: NumberNode(100)
└── then_body
    └── AssignmentNode
        ├── target: VariableNode("Alarm")
        └── value: BooleanNode(True)
```

Type facts:

```text
Temp  → NUMBER
Alarm → BOOL
Temp > 100 → BOOL
Alarm := TRUE → valid assignment
```

Industrial semantic facts:

```text
condition.kind       = threshold_condition
condition.signal     = Temp
condition.operator   = >
condition.threshold  = 100
action.kind          = alarm_raise
action.target        = Alarm
```

Future IEC 61499 transformation hint:

```text
Threshold detector FB ──event──▶ Alarm command FB
Temp data input        ──data──▶ Threshold detector FB
```

---

## 9. Worked Example: Safety Interlock

Source:

```iecst
IF StartButton AND SafetyOK THEN
    Motor := TRUE;
    Alarm := FALSE;
END_IF;
```

Semantic interpretation:

```text
StartButton       → operator request
SafetyOK          → safety permissive
AND               → interlock gate
Motor := TRUE     → actuator enable
Alarm := FALSE    → alarm clear / normal state
```

Potential tags:

```text
IF condition       → INTERLOCK_CHAIN
StartButton        → OPERATOR_COMMAND
SafetyOK           → SAFETY_PERMISSIVE
Motor assignment   → ACTUATOR_ENABLE
Alarm assignment   → ALARM_CLEAR
```

---

## 10. Semantic Metadata Model: Planned

A future semantic pass should produce structured metadata similar to:

```text
SemanticProgram
├── variables
│   ├── Temp: NUMBER, role=SENSOR
│   ├── Alarm: BOOL, role=ALARM
│   └── Motor: BOOL, role=ACTUATOR
├── conditions
│   └── threshold Temp > 100
├── actions
│   ├── Alarm := TRUE
│   └── Motor := TRUE
└── dependencies
    ├── Temp -> Alarm
    └── StartButton, SafetyOK -> Motor
```

This metadata becomes the bridge between AST analysis and IEC 61499 generation.

---

## 11. Design Rules

1. Semantic passes are custom project systems.
2. Semantic modules return data, not presentation text.
3. Industrial tags should be based on AST + symbol + type facts.
4. Type checking must run before transformation.
5. Unknown types should produce warnings, not silent assumptions.
6. Safety-related classifications should remain auditable and explainable.
