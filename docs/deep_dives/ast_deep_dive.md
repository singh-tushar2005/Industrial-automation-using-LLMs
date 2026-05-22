# AST Deep Dive

> The Abstract Syntax Tree is the project’s structured representation of a
> Structured Text program.

---

## 1. Purpose

The AST solves a fundamental compiler problem: source code text is difficult to
analyze directly.

Structured Text is written as characters:

```iecst
IF Temp > 100 THEN
    Alarm := TRUE;
END_IF;
```

A compiler-oriented system needs structure:

```text
IfStatementNode
├── condition: BinaryExpressionNode(">")
│   ├── left: VariableNode("Temp")
│   └── right: NumberNode(100)
└── then_body: BlockNode
    └── AssignmentNode
        ├── target: VariableNode("Alarm")
        └── value: BooleanNode(True)
```

The AST turns code into objects that later systems can traverse, validate,
classify, and transform.

---

## 2. Inputs

AST classes do not receive raw `.st` files directly.

Inputs to AST object creation come from the parser:

```text
Structured Text source
    ↓
parser/st_parser.py
    ↓
AST constructor calls
```

For example, when the parser recognizes `Alarm := TRUE;`, it constructs:

```text
AssignmentNode(
    target=VariableNode("Alarm"),
    value=BooleanNode(True)
)
```

---

## 3. Outputs

The AST layer produces object graphs.

Current important node types include:

| Node | Meaning |
|---|---|
| `ProgramNode` | complete parsed ST program |
| `BlockNode` | ordered statement list |
| `IfStatementNode` | conditional execution |
| `CaseStatementNode` | mode/state/sequence selection |
| `CaseBranchNode` | one CASE branch |
| `AssignmentNode` | variable write |
| `FunctionBlockCallNode` | stateful FB invocation |
| `BinaryExpressionNode` | arithmetic or comparison expression |
| `LogicalExpressionNode` | `AND`, `OR`, `NOT` logic |
| `VariableNode` | variable reference |
| `BooleanNode` | boolean literal |
| `NumberNode` | numeric literal |
| `TimeLiteralNode` | IEC time literal such as `T#5s` |

Consumers:

- semantic traversal visitor
- type checker
- industrial semantic classifier
- future IR builder
- future IEC 61499 generator

---

## 4. Internal Logic

The AST layer is intentionally simple. Each class stores fields and provides a
readable `repr`.

```text
VariableNode
└── name

AssignmentNode
├── target
└── value

IfStatementNode
├── condition
└── then_body
```

The key idea is nesting. Nodes contain other nodes. This lets a small set of
classes represent complex industrial logic.

### Nested Tree Example

```iecst
IF StartCommand AND SafetyOK THEN
    StartTimer(IN := StartCommand, PT := T#5s);
    IF StartTimer.Q THEN
        Motor := TRUE;
    END_IF;
END_IF;
```

Tree shape:

```text
ProgramNode
└── BlockNode
    └── IfStatementNode
        ├── condition: LogicalExpressionNode("AND")
        │   ├── VariableNode("StartCommand")
        │   └── VariableNode("SafetyOK")
        └── then_body: BlockNode
            ├── FunctionBlockCallNode("StartTimer")
            │   ├── IN: VariableNode("StartCommand")
            │   └── PT: TimeLiteralNode("T#5s")
            └── IfStatementNode
                ├── condition: VariableNode("StartTimer.Q")
                └── then_body: AssignmentNode("Motor", TRUE)
```

---

## 5. What This Subsystem Does Not Do

The AST layer does not:

- read files
- tokenize source code
- parse grammar
- check types
- decide whether a variable is an actuator
- classify industrial behavior
- print reports
- generate IEC 61499

This boundary is important. AST classes should remain stable data containers.
The parser creates ASTs. Semantic passes interpret ASTs.

---

## 6. Relationships

```text
parser/st_parser.py
    │ creates
    ▼
ast/nodes.py objects
    │ consumed by
    ├── semantic/visitor.py
    ├── semantic/type_checker.py
    ├── semantic/classifier.py
    └── future transformation passes
```

The parser depends on AST definitions because it needs classes to instantiate.
The AST layer should not depend on the parser. That direction keeps the model
usable by other future frontends, tests, or generated AST builders.

---

## 7. Industrial Transformation Relevance

IEC 61499 transformation needs structured meaning. The AST is the first step
toward that meaning.

The AST tells later systems:

- where conditions are
- where assignments are
- which expressions are nested
- where timers and function block calls occur
- how CASE-based state logic is organized

Without an AST, semantic systems would need to search raw text repeatedly. With
an AST, they can reason over explicit structure.

---

## 8. Key Principle

> The AST represents program shape. It should not own program meaning.

Meaning is added by semantic passes layered on top.
