# Structured Text Parser Notes

The parser currently handles a small but useful IEC 61131-3 Structured Text
subset:

- boolean literals: `TRUE`, `FALSE`
- variable references: `StartButton`, `Motor`, `Temp`
- numeric literals: `100`, `1`, `12.5`
- assignments: `Motor := TRUE;`
- arithmetic expressions: `Counter + 1`
- comparisons: `Temp > 100`
- logical expressions: `StartButton AND SafetyOK`
- nested `IF ... THEN ... END_IF;` blocks

## Parser Responsibility

The parser should answer one question: is the source text valid for the grammar
we support, and what AST does it produce?

It should not print reports, perform type checking, or transform code into IEC
61499. Those jobs belong to later layers.

## Dataset Files

Examples live in `datasets/*.st`. Keeping examples outside parser source makes
the parser easier to maintain and prepares the project for larger evaluation
sets, vendor snippets, generated edge cases, and AI-assisted benchmark data.

## AST Imports

The repository has an `ast/` folder, which has the same name as Python's
standard library `ast` module. The parser imports the project AST classes by
file path to avoid that name collision.
