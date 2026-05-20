# Layered Architecture

The project follows a compiler-style layered architecture. Each layer has a
clear responsibility and passes structured data to the next layer.

```text
Structured Text datasets
    ↓
Parser
    ↓
Abstract Syntax Tree
    ↓
Semantic analysis
    ↓
Analysis results
    ↓
Orchestration and presentation
```

## Separation of Concerns

Separation of concerns means each module owns one kind of work.

The parser owns grammar recognition and AST construction. It should not print
reports, make semantic decisions, or transform code.

The AST layer owns data structures. It should describe the program shape without
knowing how that shape will be analyzed or printed.

The semantic layer owns meaning. It can traverse the AST, collect symbols,
infer/check types, and return diagnostics.

The orchestration layer owns workflow order. In this project, `main.py` loads
datasets, runs parsing, runs semantic analysis, and prints the report.

## Orchestration vs Business Logic

Orchestration coordinates modules. Business logic performs domain work.

In this project:

- `main.py` is orchestration and presentation.
- `parser/st_parser.py` is parsing logic.
- `semantic/visitor.py` and `semantic/type_checker.py` are analysis logic.
- `semantic/symbol_table.py` is a data structure.

Keeping this boundary clean makes the same parser and semantic passes reusable
from tests, command-line tools, web APIs, notebooks, and future migration jobs.

## Why Compiler Systems Separate Analysis From Presentation

Compiler passes should usually return data, not terminal text. A type checker
that returns structured errors can be reused by:

- a command-line report
- an automated test
- an IDE diagnostic panel
- an AI-assisted migration pipeline
- a verification engine

Printing too early makes later automation harder because downstream tools must
parse human-facing text instead of consuming structured results.
