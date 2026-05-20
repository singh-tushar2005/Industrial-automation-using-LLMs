# Project Documentation System

This folder separates project knowledge from executable source code.

The source tree should stay focused on implementation: parsing, AST nodes,
semantic traversal, type checking, orchestration, and future transformation
passes. The docs tree is the project knowledge base: compiler concepts,
industrial automation background, design reasoning, research notes, and learning
material for future contributors.

## Organization

```text
docs/
├── architecture/          System structure and pipeline design
├── compiler_notes/        General compiler concepts used by the project
├── parser_notes/          IEC 61131-3 parsing and grammar notes
├── semantic_notes/        Visitors, symbol tables, and type checking
├── plc_notes/             PLC and Structured Text background
├── transformation_notes/  IEC 61131-3 to IEC 61499 migration ideas
└── research_notes/        AI-assisted analysis and research direction
```

## Why This Matters

This project is both an implementation and a research platform. Keeping long
explanations in Markdown has three benefits:

1. Source files remain easier to maintain.
2. Learning material can grow without cluttering runtime code.
3. AI-assisted development tools can use the docs as structured context.

## Pipeline Overview

```text
datasets/*.st
    ↓
parser/st_parser.py
    ↓
AST nodes
    ↓
semantic visitors and type checker
    ↓
result data
    ↓
main.py presentation and reporting
```

Future IEC 61499 transformation stages should extend this pipeline by consuming
semantic results rather than re-parsing source text or duplicating analysis.
