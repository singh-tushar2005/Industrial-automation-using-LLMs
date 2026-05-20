# IEC 61499 Migration Pipeline

The long-term goal is to migrate IEC 61131-3 Structured Text into IEC 61499
function-block-oriented models.

## Why Semantic Analysis Comes First

IEC 61499 transformation needs more than syntax. It needs to know:

- which variables are read
- which variables are written
- which expressions are boolean conditions
- which expressions are numeric calculations
- how nested control logic is structured
- where data and event dependencies exist

The current parser and semantic analyzer provide the early foundation for those
facts.

## Future Pipeline

```text
Structured Text source
    ↓
AST
    ↓
semantic analysis
    ↓
dependency graph
    ↓
function block mapping
    ↓
event and data connections
    ↓
verification
```

## Transformation Passes To Add Later

Future passes may include:

- variable read/write extraction
- condition normalization
- control-flow analysis
- data dependency graph construction
- function block candidate generation
- event connection generation
- semantic equivalence checks
- export to IEC 61499 tool formats
