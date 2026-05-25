# Pipeline Overview

> Architecture specification for the IEC 61131-3 Structured Text semantic
> migration pipeline.

---

## 1. System Intent

This repository is evolving into a research-grade industrial automation
migration system. Its long-term purpose is to transform IEC 61131-3 Structured
Text programs into IEC 61499 architectures by combining deterministic compiler
infrastructure with future LLM-assisted semantic reasoning.

The pipeline is intentionally layered:

- source programs enter as `.st` dataset files
- parser logic converts text into AST objects
- semantic passes extract meaning from the AST
- later passes will build an Intermediate Representation
- IEC 61499 generators will use semantic and IR data to produce architectures

The current implementation is small, but the architecture is shaped like a
compiler platform rather than a one-off script.

---

## 2. End-To-End Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                     INDUSTRIAL AUTOMATION MIGRATION PIPELINE                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Source Domain                        Compiler Domain                         │
│  ─────────────                        ───────────────                         │
│                                                                              │
│  ┌──────────────────────┐        ┌──────────────────────────────┐            │
│  │ IEC 61131-3 ST Files │        │ Dataset Discovery / Loading  │            │
│  │ datasets/*.st        │───────▶│ parser.st_parser             │            │
│  │                      │        │ find_dataset_files()         │            │
│  └──────────────────────┘        └──────────────┬───────────────┘            │
│                                                  │                            │
│                                                  ▼                            │
│                                      ┌──────────────────────────┐            │
│                                      │ Parser Layer             │            │
│                                      │ pyparsing grammar        │            │
│                                      │ parse_st_file()          │            │
│                                      └────────────┬─────────────┘            │
│                                                   │ ProgramNode               │
│                                                   ▼                            │
│                                      ┌──────────────────────────┐            │
│                                      │ AST Layer                │            │
│                                      │ ast/nodes.py             │            │
│                                      │ Program / Block / Expr   │            │
│                                      └────────────┬─────────────┘            │
│                                                   │ AST object graph          │
│                                                   ▼                            │
│        Semantic Domain               ┌──────────────────────────┐            │
│        ───────────────               │ Semantic Traversal       │            │
│                                      │ semantic.visitor         │            │
│                                      │ SemanticTraversalVisitor │            │
│                                      └────────────┬─────────────┘            │
│                                                   │ traversal events          │
│                                                   ▼                            │
│                                      ┌──────────────────────────┐            │
│                                      │ Symbol Table             │            │
│                                      │ semantic.symbol_table    │            │
│                                      │ name → semantic type     │            │
│                                      └────────────┬─────────────┘            │
│                                                   │ known symbols             │
│                                                   ▼                            │
│                                      ┌──────────────────────────┐            │
│                                      │ Type Checker             │            │
│                                      │ semantic.type_checker    │            │
│                                      │ BOOL / NUMBER / UNKNOWN  │            │
│                                      └────────────┬─────────────┘            │
│                                                   │ diagnostics + metadata    │
│                                                   ▼                            │
│        Transformation Domain          ┌──────────────────────────┐            │
│        ─────────────────────          │ Semantic Classifier      │            │
│        planned                       │ threshold / alarm /      │            │
│                                      │ interlock / actuator     │            │
│                                      └────────────┬─────────────┘            │
│                                                   │ classified semantics      │
│                                                   ▼                            │
│                                      ┌──────────────────────────┐            │
│                                      │ Intermediate Representation│           │
│                                      │ planned semantic IR       │           │
│                                      └────────────┬─────────────┘            │
│                                                   │ normalized control model  │
│                                                   ▼                            │
│                                      ┌──────────────────────────┐            │
│                                      │ IEC 61499 Generator      │            │
│                                      │ planned FB / event model │            │
│                                      └──────────────────────────┘            │
│                                                                              │
│  Presentation Boundary                                                       │
│  ─────────────────────                                                       │
│  main.py orchestrates stages and prints reports. Internal modules return     │
│  structured data instead of owning terminal output.                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layered Responsibilities

| Layer | Current Module | Technology | Input | Output | Status |
|---|---|---:|---|---|---|
| Dataset layer | `datasets/*.st` | IEC 61131-3 ST text | `.st` files | source strings | Implemented |
| Dataset discovery | `parser/st_parser.py` | `pathlib` | dataset directory | sorted file paths | Implemented |
| Parser layer | `parser/st_parser.py` | `pyparsing` | source string | `ProgramNode` AST | Implemented |
| AST layer | `ast/nodes.py` | Python classes | parse actions | object graph | Implemented |
| Semantic traversal | `semantic/visitor.py` | custom visitor | AST | traversal event data | Implemented |
| Symbol table | `semantic/symbol_table.py` | custom data structure | variable names | type map | Implemented |
| Type checking | `semantic/type_checker.py` | custom semantic pass | AST + symbols | errors, warnings, metadata | Implemented |
| Semantic classifier | planned | custom rules + metadata | checked AST | industrial tags | Planned |
| IR builder | planned | custom IR model | semantic facts | normalized IR | Planned |
| IEC 61499 generator | planned | generator backend | IR | function block architecture | Planned |
| Verification | planned | symbolic checks | ST + generated model | equivalence/safety evidence | Planned |

---

## 4. Data Flow Contracts

The pipeline is designed around explicit data transformations.

```text
┌─────────────┐      ┌──────────────┐      ┌────────────────┐
│ Text Source │─────▶│ Syntax Parse │─────▶│ AST Object     │
│ .st file    │      │ pyparsing    │      │ ProgramNode    │
└─────────────┘      └──────────────┘      └───────┬────────┘
                                                   │
                                                   ▼
┌─────────────────────┐      ┌──────────────────────────────┐
│ Semantic Diagnostics│◀──── │ Semantic Analysis            │
│ errors / warnings   │      │ traversal + symbols + types  │
└──────────┬──────────┘      └──────────────────────────────┘
           │
           ▼
┌─────────────────────┐      ┌──────────────────────────────┐
│ Future IR           │─────▶│ Future IEC 61499 Architecture│
│ normalized semantics│      │ FBs + events + data links    │
└─────────────────────┘      └──────────────────────────────┘
```

### Current Data Objects

| Data Object | Produced By | Consumed By | Purpose |
|---|---|---|---|
| `Path` list | `find_dataset_files()` | `main.py` | repeatable dataset ingestion |
| source string | `load_st_file()` | `parse_st_program()` | raw Structured Text |
| `ProgramNode` | parser parse actions | semantic passes | structured program representation |
| traversal events | `SemanticTraversalVisitor` | `main.py` | explainable AST walk |
| symbol map | `SymbolTable` | `TypeChecker`, `main.py` | known variable types |
| type report | `TypeChecker.get_report()` | `main.py` | semantic diagnostics |

---

## 5. Orchestration Role Of `main.py`

`main.py` is the pipeline entrypoint. It is intentionally not the owner of
parser rules, AST classes, or semantic logic.

```text
main.py
├── discovers datasets
├── invokes parser
├── invokes semantic traversal
├── invokes type checker
├── formats terminal output
└── prints pipeline summary
```

This keeps the system reusable. The parser and semantic passes can later be
called from tests, batch migration jobs, notebooks, web services, or LLM tooling
without depending on terminal output.

---

## 6. Current vs Future Pipeline

### Current Implementation

```text
datasets/*.st
    ↓
parse_st_file()
    ↓
ProgramNode AST
    ↓
SemanticTraversalVisitor
    ↓
TypeChecker
    ↓
main.py report
```

The current system supports:

- assignment statements
- boolean literals
- numeric literals
- arithmetic expressions
- comparison expressions
- logical expressions
- nested `IF` statements
- semantic traversal
- basic symbol table
- basic type checking

### Planned Evolution

```text
datasets/*.st
    ↓
parser
    ↓
AST
    ↓
semantic analysis
    ↓
industrial semantic classification
    ↓
semantic graph
    ↓
IR
    ↓
LLM-assisted transformation reasoning
    ↓
IEC 61499 generation
    ↓
verification and safety validation
```

Future stages should not bypass earlier layers. IEC 61499 generation should
consume semantic facts and IR data, not raw source text alone.

---

## 7. Roadmap

| Milestone | Description | Dependency |
|---|---|---|
| M1 | Keep parser, AST, semantic analysis, and reporting separated | Complete |
| M2 | Add declaration parsing and richer IEC 61131-3 type model | Parser |
| M3 | Add industrial semantic classifier | Type checker + visitor |
| M4 | Build read/write dependency extraction | Semantic traversal |
| M5 | Define transformation IR | Semantic classifier |
| M6 | Generate IEC 61499 function block candidates | IR |
| M7 | Add symbolic verification hooks | IR + generated model |
| M8 | Add LLM-assisted reasoning layer | symbolic facts + IR |

---

## 8. Engineering Principle

> The pipeline should move from syntax to meaning before it attempts
> transformation.

ASTs describe program structure. Semantic analysis describes program meaning.
IEC 61499 generation needs meaning: event causality, data dependencies, actuator
effects, safety conditions, alarm logic, and control intent.
