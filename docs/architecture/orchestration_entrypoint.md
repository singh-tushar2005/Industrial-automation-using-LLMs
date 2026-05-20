# Orchestration Entrypoint

`main.py` is the centralized entrypoint for running the current pipeline.

## What Orchestration Means

Orchestration is the software architecture role of coordinating separate
components into one useful workflow. In this project, `main.py`:

1. Finds Structured Text dataset files.
2. Calls the parser to produce AST objects.
3. Calls semantic traversal.
4. Calls type checking.
5. Prints human-readable results.

It does not define AST classes, grammar rules, or semantic checks.

## Why Large Systems Use Centralized Entrypoints

A centralized entrypoint gives users and tools a stable way to run the system.
Instead of remembering several internal scripts, a contributor can run:

```bash
uv run python main.py
```

As the project grows, `main.py` can add command-line flags, output formats, or
batch modes while internal modules remain reusable.

## Future Pipeline Shape

The intended long-term architecture is:

```text
datasets/
    ↓
parser
    ↓
AST
    ↓
semantic analysis
    ↓
IEC 61499 transformation passes
    ↓
verification and reports
```

This keeps transformation work downstream of parsing and semantic analysis.
