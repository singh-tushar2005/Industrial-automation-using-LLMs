# Recursive Parsing

Structured Text statements can nest inside other statements. For example:

```iecst
IF SafetyOK THEN
    IF Temp > 100 THEN
        Alarm := TRUE;
    END_IF;
END_IF;
```

This requires recursive parsing because an `IF` body contains a block, a block
contains statements, and a statement can itself be another `IF`.

```text
statement
├── assignment_statement
└── if_statement
    └── block
        └── statement
```

## Forward Declarations

Parser libraries such as pyparsing need a placeholder for recursive grammars.
The current parser uses `Forward()` for `expression` and `statement` so grammar
rules can refer to each other before their full definitions are known.

## Expression Precedence

The parser uses pyparsing's `infix_notation()` helper to encode expression
precedence:

1. `*` and `/`
2. `+` and `-`
3. comparisons such as `>`, `<=`, `=`, `<>`
4. `NOT`
5. `AND`
6. `OR`

This lets `Counter + 1 > Limit` become an AST where arithmetic happens before
comparison.

## Left Associativity

For a chain such as:

```iecst
Counter + 1 - Offset
```

the parser folds from the left:

```text
((Counter + 1) - Offset)
```

That produces a tree that later semantic passes can traverse predictably.
