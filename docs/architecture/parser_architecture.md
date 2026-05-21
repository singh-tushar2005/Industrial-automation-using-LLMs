# Parser Architecture

> Technical architecture for converting IEC 61131-3 Structured Text into
> project AST objects.

---

## 1. Parser Mission

The parser layer is responsible for one core transformation:

```text
IEC 61131-3 Structured Text source  ─────▶  Abstract Syntax Tree
```

It does not perform semantic validation, industrial classification, or IEC 61499
generation. Its job is to recognize supported syntax and construct AST objects
from `ast/nodes.py`.

---

## 2. Why `pyparsing`

`pyparsing` is a pragmatic choice for the current research stage because it lets
the project define grammar rules directly in Python while still producing
structured parse results.

| Requirement | Why `pyparsing` Fits |
|---|---|
| Small evolving grammar | Rules can be extended incrementally |
| Recursive language constructs | `Forward()` supports recursive grammar definitions |
| Operator precedence | `infix_notation()` handles expression precedence cleanly |
| AST construction | parse actions map syntax directly into node classes |
| Research iteration | grammar can change without a generated parser toolchain |

For a later production-grade parser, the project may evaluate generated parsers
or IEC 61131-3 grammar libraries. The current priority is transparent research
iteration and AST-first infrastructure.

---

## 3. Lexical vs Syntactic Structure

Structured Text parsing has two levels of recognition.

```text
Lexical structure
├── keywords: IF, THEN, END_IF, TRUE, FALSE, AND, OR, NOT
├── identifiers: StartButton, SafetyOK, Motor
├── literals: 100, 12.5, TRUE
└── operators: :=, +, -, *, /, >, >=, <, <=, =, <>

Syntactic structure
├── assignment_statement
├── if_statement
├── block
├── expression
└── program
```

The current parser does not expose a separate lexer. Instead, lexical elements
are defined as pyparsing expressions and composed into syntactic rules.

---

## 4. Current Grammar Shape

```text
program
└── block
    └── statement+
        ├── assignment_statement
        │   ├── identifier
        │   ├── :=
        │   ├── expression
        │   └── ;
        └── if_statement
            ├── IF
            ├── expression
            ├── THEN
            ├── block
            ├── END_IF
            └── ;
```

The supported expression grammar includes:

```text
expression
├── number
├── boolean
├── identifier
├── parenthesized expression
├── arithmetic expression
├── comparison expression
└── logical expression
```

---

## 5. Parser Workflow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                           PARSER WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  datasets/logical_if.st                                             │
│          │                                                          │
│          ▼                                                          │
│  load_st_file(file_path)                                            │
│          │  raw source string                                       │
│          ▼                                                          │
│  parse_st_program(source_code)                                      │
│          │                                                          │
│          ▼                                                          │
│  build_st_parser()                                                  │
│          │                                                          │
│          ├── keyword rules                                          │
│          ├── identifier / literal rules                             │
│          ├── recursive expression and statement placeholders         │
│          ├── operator precedence table                              │
│          └── parse actions bound to AST constructors                 │
│          │                                                          │
│          ▼                                                          │
│  parser.parse_string(..., parse_all=True)                           │
│          │                                                          │
│          ▼                                                          │
│  ProgramNode                                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

`parse_all=True` is important because it rejects trailing unsupported text. A
partial parse is not acceptable for a migration pipeline.

---

## 6. AST Construction

The parser uses parse actions as the boundary between syntax and AST structure.

```text
pyparsing match                  parse action                 AST result
────────────────────────────────────────────────────────────────────────────
"StartButton"                   make_variable_node()          VariableNode
"TRUE"                          make_boolean_node()           BooleanNode
"100"                           make_number_node()            NumberNode
"Motor := TRUE;"                make_assignment_node()        AssignmentNode
"IF ... THEN ... END_IF;"       make_if_statement_node()      IfStatementNode
top-level block                 make_program_node()           ProgramNode
```

### AST Construction Diagram

```text
Source fragment
───────────────
IF Temp > 100 THEN
    Alarm := TRUE;
END_IF;

Parse actions
─────────────
Temp              ──▶ VariableNode("Temp")
100               ──▶ NumberNode(100)
Temp > 100        ──▶ BinaryExpressionNode(left, ">", right)
Alarm             ──▶ VariableNode("Alarm")
TRUE              ──▶ BooleanNode(True)
Alarm := TRUE;    ──▶ AssignmentNode(target, value)
IF ... END_IF;    ──▶ IfStatementNode(condition, then_body)
program           ──▶ ProgramNode(body)
```

---

## 7. Operator Precedence

The parser uses `infix_notation()` to ensure expressions are grouped correctly.

| Precedence | Operators | AST Node |
|---:|---|---|
| 1 | `*`, `/` | `BinaryExpressionNode` |
| 2 | `+`, `-` | `BinaryExpressionNode` |
| 3 | `>`, `>=`, `<`, `<=`, `=`, `<>` | `BinaryExpressionNode` |
| 4 | `NOT` | `LogicalExpressionNode` |
| 5 | `AND` | `LogicalExpressionNode` |
| 6 | `OR` | `LogicalExpressionNode` |

Example:

```iecst
IF Counter + 1 > Limit THEN
    Warning := TRUE;
END_IF;
```

AST structure:

```text
IfStatementNode
├── condition: BinaryExpressionNode(">")
│   ├── left: BinaryExpressionNode("+")
│   │   ├── left: VariableNode("Counter")
│   │   └── right: NumberNode(1)
│   └── right: VariableNode("Limit")
└── then_body: BlockNode
    └── AssignmentNode
        ├── target: VariableNode("Warning")
        └── value: BooleanNode(True)
```

---

## 8. Recursive Parsing And Nested IF

Nested control logic requires recursive grammar rules.

```iecst
IF SafetyOK THEN
    IF Temp > 100 THEN
        Alarm := TRUE;
    END_IF;
END_IF;
```

Recursive structure:

```text
statement
└── if_statement
    └── then_body: block
        └── statement
            └── if_statement
                └── then_body: block
                    └── assignment_statement
```

The parser uses `Forward()` placeholders for `expression` and `statement`
because those rules refer to themselves indirectly.

---

## 9. Why AST Abstraction Is Important

Raw source text is not a stable foundation for transformation. Consider:

```iecst
IF Temp > 100 THEN
    Alarm := TRUE;
END_IF;
```

A text-based migration tool would need to rediscover where the condition,
variable write, threshold value, and statement body are. The AST makes these
facts explicit.

```text
Condition       → BinaryExpressionNode(">")
Measured value  → VariableNode("Temp")
Threshold       → NumberNode(100)
Actuator/alarm  → VariableNode("Alarm")
Command value   → BooleanNode(True)
```

Semantic analysis and IEC 61499 generation should consume this structured form.

---

## 10. Future Grammar Expansion

| Feature | Example | Parser Impact | Transformation Impact |
|---|---|---|---|
| `CASE` | `CASE Mode OF ... END_CASE;` | multi-branch statement node | state/event selection |
| `FOR` | `FOR i := 1 TO 10 DO ... END_FOR;` | loop node + bounds | repeated execution model |
| `WHILE` | `WHILE Ready DO ... END_WHILE;` | loop condition node | cyclic execution mapping |
| `FUNCTION_BLOCK` | `FUNCTION_BLOCK MotorCtrl ...` | declaration and scope grammar | IEC 61499 FB mapping |
| timers | `TON(IN := Start, PT := T#5s)` | call syntax + typed literals | timer FB generation |
| FB calls | `Controller(Start := X);` | invocation node | data/event connection mapping |

Future grammar work should add AST nodes deliberately. Each new syntax category
should have a clear semantic interpretation and transformation role.

---

## 11. Parser Design Rules

1. The parser returns AST objects, not reports.
2. Parse actions construct nodes, not semantic diagnostics.
3. Dataset ingestion remains deterministic and sorted.
4. Unsupported syntax should fail clearly.
5. New grammar features should be accompanied by semantic visitor support.
6. IEC 61499 concerns should remain downstream of the parser.
