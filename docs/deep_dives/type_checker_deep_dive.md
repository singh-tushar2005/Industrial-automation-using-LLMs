# Type Checker Deep Dive

> The type checker validates semantic correctness before industrial
> classification and transformation.

---

## 1. Purpose

The type checker answers whether expressions and assignments make sense.

Syntax alone cannot catch this:

```iecst
StartButton AND 1
```

The parser can build an AST, but semantic analysis must reject or warn about
invalid types.

---

## 2. Inputs

The type checker receives:

```text
AST
    from parser

SymbolTable
    known or inferred variable types
```

Current type labels:

```text
BOOL
NUMBER
TIME
UNKNOWN
```

---

## 3. Outputs

The type checker returns a report dictionary:

```text
{
  program_is_valid,
  warnings,
  errors,
  symbols,
  analysis_results
}
```

Consumers:

- `main.py` for reporting
- `IndustrialSemanticClassifier` as context
- future IR and verification passes

---

## 4. Internal Logic

The type checker is a visitor. It walks the AST recursively and returns types
from expression visits.

```text
visit_NumberNode()   → NUMBER
visit_BooleanNode()  → BOOL
visit_TimeLiteralNode() → TIME
visit_VariableNode() → symbol table lookup
```

For composite expressions:

```text
visit_BinaryExpressionNode()
├── type check left expression
├── type check right expression
└── validate operator rule
```

---

## 5. Expression Validation

Arithmetic:

```iecst
Counter + 1
```

Rule:

```text
NUMBER + NUMBER → NUMBER
```

Comparison:

```iecst
TankLevel > HighLevel
```

Rule:

```text
NUMBER > NUMBER → BOOL
```

Logical:

```iecst
StartCommand AND SafetyOK
```

Rule:

```text
BOOL AND BOOL → BOOL
```

---

## 6. Assignment Checking

Assignment:

```iecst
Motor := TRUE;
```

Flow:

```text
target = Motor
value type = BOOL
existing target type = symbol_table.lookup("Motor")
compatible? yes
```

Invalid example:

```iecst
Motor := 42;
```

If `Motor` is known as `BOOL`, assigning a `NUMBER` should produce an error.

---

## 7. Function Block Call Checking

The current type checker performs lightweight argument checks for common
industrial FB arguments.

```iecst
StartTimer(IN := StartCommand, PT := T#5s);
```

Rules:

```text
IN, CU, CD, R, RESET, LOAD → BOOL or UNKNOWN
PT                         → TIME, NUMBER, or UNKNOWN
PV                         → TIME, NUMBER, or UNKNOWN
```

This is not a complete IEC function block type system yet. It is an incremental
semantic foundation.

---

## 8. What This Subsystem Does Not Do

The type checker does not:

- parse source text
- create AST nodes
- classify actuator coordination
- decide safety intent
- generate IEC 61499
- print reports directly

It validates semantic correctness. Industrial interpretation belongs to the
classifier.

---

## 9. Relationships

```text
AST
    ↓
TypeChecker visitor
    ↔ SymbolTable
    ↓
type report
    ↓
main.py and classifier
```

The type checker depends on the AST structure and symbol table facts. It also
provides a cleaner basis for the industrial classifier.

---

## 10. Industrial Transformation Relevance

IEC 61499 transformation must preserve compatible data flow. A generated
function block network should not connect numeric process values into boolean
event guards without an explicit comparison.

Type checking helps identify:

- boolean conditions
- numeric process values
- time literals for timers
- assignment compatibility
- unknown variables that need metadata

---

## 11. Key Principle

> Type checking validates meaning at the language level. It prepares the system
> for industrial semantic interpretation but does not replace it.
