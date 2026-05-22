# Parser Deep Dive

> The parser converts IEC 61131-3 Structured Text source into AST objects.

---

## 1. Purpose

The parser solves the problem of turning text into structure.

Source text is linear:

```iecst
IF TankLevel > HighLevel THEN
    InletValve := FALSE;
    Alarm := TRUE;
END_IF;
```

The rest of the system needs an AST:

```text
IfStatementNode
├── condition: BinaryExpressionNode(">")
└── then_body: BlockNode
```

The parser is the only layer that should understand grammar syntax such as
`IF`, `THEN`, `END_IF`, `CASE`, `:=`, function block calls, and expression
precedence.

---

## 2. Inputs

Parser inputs come from dataset files:

```text
datasets/**/*.st
    ↓
load_st_file()
    ↓
source string
```

The parser currently discovers `.st` files recursively, so examples can live in
industrial categories such as:

```text
datasets/timers/
datasets/safety_systems/
datasets/process_control/
datasets/fault_handling/
```

---

## 3. Outputs

The parser produces AST objects.

```text
parse_st_file(path)
    ↓
ProgramNode
```

The output is consumed by:

- semantic traversal
- type checking
- industrial semantic classification
- future semantic IR generation

---

## 4. Internal Logic

The parser uses `pyparsing` to define grammar rules directly in Python.

### Parsing Layers

```text
Raw text
    ↓
tokens
    ↓
grammar rules
    ↓
parse actions
    ↓
AST nodes
```

### Token Recognition

The parser recognizes:

- keywords: `IF`, `THEN`, `END_IF`, `CASE`, `OF`, `ELSE`, `END_CASE`
- booleans: `TRUE`, `FALSE`
- identifiers: `Motor`, `StartTimer.Q`
- numbers: `100`, `12.5`
- time literals: `T#5s`, `T#250ms`
- operators: `+`, `-`, `*`, `/`, `>`, `>=`, `<`, `<=`, `=`, `<>`
- assignment: `:=`
- function block calls: `Timer(IN := X, PT := T#5s);`

---

## 5. Grammar Flow

```text
program
└── block
    └── statement+
        ├── if_statement
        ├── case_statement
        ├── function_block_call
        └── assignment_statement
```

Expression grammar is recursive:

```text
expression
├── atom
│   ├── identifier
│   ├── number
│   ├── boolean
│   ├── time literal
│   └── parenthesized expression
└── operators
    ├── arithmetic
    ├── comparison
    └── logical
```

---

## 6. Recursive Parsing

Structured Text can nest statements inside statements.

```iecst
IF SafetyOK THEN
    IF Pressure > PressureHighLimit THEN
        Alarm := TRUE;
    END_IF;
END_IF;
```

This requires recursive parsing:

```text
if_statement
└── then_body: block
    └── statement
        └── if_statement
            └── then_body: block
```

The parser uses `Forward()` for rules that need to refer to themselves before
their final definition is available.

---

## 7. Expression Handling

Operator precedence matters. This source:

```iecst
Counter + 1 > Limit
```

should not be interpreted as:

```text
Counter + (1 > Limit)
```

It should become:

```text
(Counter + 1) > Limit
```

AST shape:

```text
BinaryExpressionNode(">")
├── left: BinaryExpressionNode("+")
│   ├── VariableNode("Counter")
│   └── NumberNode(1)
└── right: VariableNode("Limit")
```

The parser uses `infix_notation()` to encode precedence.

---

## 8. AST Instantiation

Parse actions are the bridge from grammar matches to AST construction.

```text
matched syntax                    AST constructor
────────────────────────────────────────────────────────────
Temp                              VariableNode("Temp")
TRUE                              BooleanNode(True)
T#5s                              TimeLiteralNode("T#5s")
Temp > 100                        BinaryExpressionNode(...)
Motor := TRUE;                    AssignmentNode(...)
StartTimer(IN := X, PT := T#5s);  FunctionBlockCallNode(...)
CASE Mode OF ... END_CASE;        CaseStatementNode(...)
```

### Source To AST Example

```iecst
StartTimer(IN := StartCommand AND SafetyOK, PT := T#5s);

IF StartTimer.Q THEN
    Motor := TRUE;
END_IF;
```

```text
ProgramNode
└── BlockNode
    ├── FunctionBlockCallNode("StartTimer")
    │   ├── IN: LogicalExpressionNode("AND")
    │   └── PT: TimeLiteralNode("T#5s")
    └── IfStatementNode
        ├── condition: VariableNode("StartTimer.Q")
        └── then_body: AssignmentNode(Motor, TRUE)
```

---

## 9. What This Subsystem Does Not Do

The parser does not:

- validate industrial meaning
- check type compatibility
- populate final symbol tables from declarations
- classify safety logic
- infer actuator roles
- print analysis reports
- generate IEC 61499

If the parser started doing these jobs, grammar logic would become tangled with
semantic analysis. That would make future transformation work harder.

---

## 10. Relationships

```text
datasets/*.st
    ↓
parser/st_parser.py
    ↓ creates
ast/nodes.py objects
    ↓ consumed by
semantic passes
```

The parser depends on AST definitions. Semantic systems depend on parser output.
The parser should remain upstream and syntax-focused.

---

## 11. Industrial Transformation Relevance

Industrial transformation depends on reliable parsing. IEC 61499 generation
cannot be trusted if the source program is only partially understood.

Parser support for timers, CASE statements, nested IF logic, dotted variables,
and function block calls is especially important because these constructs are
common in realistic PLC systems.

---

## 12. Key Principle

> The parser turns syntax into structure. It should not decide what the
> structure means industrially.
