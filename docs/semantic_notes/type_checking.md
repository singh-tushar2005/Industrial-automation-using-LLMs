# Type Checking

Type checking validates expression and assignment types before transformation.

## Current Types

The project currently uses three semantic type labels:

```text
BOOL
NUMBER
UNKNOWN
```

`UNKNOWN` is used when a variable has no declaration information yet.

## Operator Rules

Arithmetic operators require numeric operands:

```iecst
Counter + 1
```

Comparisons such as `>`, `>=`, `<`, and `<=` require numeric operands and return
`BOOL`:

```iecst
Temp > 100
```

Logical operators require boolean operands and return `BOOL`:

```iecst
StartButton AND SafetyOK
```

Assignments require compatible target and value types:

```iecst
Motor := TRUE;
```

## Declarations

The current grammar does not parse `VAR` declarations yet. For the dataset
examples, the type checker uses a preloaded demo symbol table.

In a larger IEC 61131-3 migration system, symbol data can come from:

- parsed declarations
- PLC tag databases
- engineering exports
- vendor project files
- AI-assisted metadata extraction
