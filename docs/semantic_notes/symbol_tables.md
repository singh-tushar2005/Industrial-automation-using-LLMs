# Symbol Tables

A symbol table records facts about names.

For the current Structured Text subset, the main fact is variable type:

```text
Motor       -> BOOL
Temp        -> NUMBER
Counter     -> NUMBER
SafetyOK    -> BOOL
```

## Parser vs Semantic Layer

The parser can recognize that `Motor` is a variable name. It should not decide
what type `Motor` has.

Type information belongs to semantic analysis because it depends on
declarations, engineering metadata, PLC tag databases, or inference rules.

## Current Shape

The first symbol table is intentionally flat:

```text
name -> type
```

That is enough for the current parser subset. Later versions can add nested
scopes for:

- global symbols
- function block symbols
- local variables
- temporary variables
- input and output ports
