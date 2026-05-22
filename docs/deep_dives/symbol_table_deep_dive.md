# Symbol Table Deep Dive

> The symbol table is semantic memory for names discovered or known during
> analysis.

---

## 1. Purpose

The symbol table solves the problem of remembering facts about identifiers.

When the parser sees:

```iecst
IF Temp > 100 THEN
    Alarm := TRUE;
END_IF;
```

it knows `Temp` and `Alarm` are names. It does not know their types or roles.
The symbol table stores semantic facts:

```text
Temp  → NUMBER
Alarm → BOOL
```

---

## 2. Inputs

The symbol table does not read dataset files directly.

Inputs come from semantic systems:

```text
AST traversal
    ↓
semantic pass sees a variable
    ↓
symbol table lookup or insert
```

In the current project, `build_demo_symbol_table()` preloads known variables for
the dataset examples. Future versions should populate symbols from parsed
declarations, PLC tag exports, or engineering metadata.

---

## 3. Outputs

The symbol table returns type facts.

```text
lookup("Motor") → BOOL
lookup("Pressure") → NUMBER
lookup("UnknownName") → None
```

Consumers:

- type checker
- industrial classifier through type reports
- future semantic graph builder
- future IR builder

---

## 4. Internal Logic

The current symbol table is a small dictionary-backed data structure:

```text
SymbolTable
└── symbols
    ├── Motor: BOOL
    ├── Pump: BOOL
    ├── TankLevel: NUMBER
    ├── StartTimer.Q: BOOL
    └── FaultCode: NUMBER
```

Operations:

| Operation | Meaning |
|---|---|
| `insert(name, type)` | store or update a semantic fact |
| `lookup(name)` | retrieve a type or return `None` |
| `contains(name)` | check whether a name is known |
| `to_dict()` | return stable ordered symbol data |

---

## 5. Semantic Lookup Example

Expression:

```iecst
Pressure > PressureHighLimit
```

Type checker flow:

```text
visit BinaryExpressionNode(">")
├── visit VariableNode("Pressure")
│   └── symbol_table.lookup("Pressure") → NUMBER
├── visit VariableNode("PressureHighLimit")
│   └── symbol_table.lookup("PressureHighLimit") → NUMBER
└── comparison NUMBER > NUMBER → BOOL
```

---

## 6. Type Inference Example

If a variable is assigned before being known:

```iecst
NewOutput := TRUE;
```

The type checker can infer:

```text
NewOutput → BOOL
```

This is useful while declaration parsing is still incomplete. In a mature IEC
61131-3 parser, declarations should become the primary source of symbol facts.

---

## 7. What This Subsystem Does Not Do

The symbol table does not:

- parse code
- recursively walk ASTs
- read dataset files
- validate expressions by itself
- classify industrial behavior
- print reports

It stores semantic context. Semantic passes decide when to read or write that
context.

---

## 8. Relationships

```text
TypeChecker
    ├── reads VariableNode
    ├── asks SymbolTable for type
    ├── records warnings/errors
    └── may insert inferred assignment target types
```

```text
SymbolTable
    ↑ populated by semantic systems
    ↓ consumed by semantic systems
```

This shared memory makes semantic passes consistent.

---

## 9. Industrial Transformation Relevance

IEC 61499 generation must know what kind of data flows between function blocks.

Examples:

- `Motor` as `BOOL` likely maps to an output command.
- `TankLevel` as `NUMBER` likely maps to an analog process value.
- `StartTimer.Q` as `BOOL` likely maps to an event/guard condition.

The symbol table is the first layer of semantic context needed for these later
decisions.

---

## 10. Key Principle

> A symbol table is memory for semantic facts. It does not discover all facts by
> itself; semantic passes populate and consume it.
