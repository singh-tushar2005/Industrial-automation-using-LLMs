# Orchestration Pipeline Deep Dive

> `main.py` coordinates the compiler-style analysis pipeline and owns
> presentation.

---

## 1. Purpose

The orchestration layer solves the problem of running subsystems in the correct
order.

Each internal module has a focused job:

- parser parses
- AST nodes store structure
- visitors traverse
- symbol table stores facts
- type checker validates
- classifier interprets industrial behavior

`main.py` connects these pieces into one executable workflow.

---

## 2. Inputs

`main.py` starts with dataset files:

```text
datasets/**/*.st
```

The dataset loader finds these files through `find_dataset_files()`.

---

## 3. Outputs

`main.py` produces terminal output:

- parse status
- generated AST view
- semantic traversal report
- type checking report
- industrial classification report
- pipeline summary

It does not produce a transformed IEC 61499 model yet. That is a future stage.

---

## 4. Internal Logic

Current pipeline:

```text
main()
└── load_dataset_files()
    └── run_pipeline(files)
        └── process_st_file(file)
            ├── parse_st_file()
            ├── run_semantic_traversal()
            ├── run_type_checking()
            ├── run_industrial_classification()
            └── print reports
```

Detailed flow:

```text
┌──────────────────────┐
│ dataset file path    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ parser               │
│ source → AST         │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ semantic traversal   │
│ AST → traversal data │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ type checker         │
│ AST → type report    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ classifier           │
│ AST + report → tags  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ main.py presentation │
│ data → CLI report    │
└──────────────────────┘
```

---

## 5. Orchestration vs Logic

Orchestration is coordination. Logic is domain behavior.

`main.py` should know:

- which stages run
- in what order
- how to display results
- how to count passed/failed files

`main.py` should not know:

- grammar rules
- AST construction details
- type compatibility rules
- industrial classification rules
- IEC 61499 mapping rules

This keeps the pipeline modular.

---

## 6. Presentation Separation

Semantic modules return data instead of printing directly.

Good boundary:

```text
TypeChecker.get_report()
    ↓
report dictionary
    ↓
main.py prints report
```

Bad boundary:

```text
TypeChecker prints report internally
```

The bad boundary makes reuse harder. A type checker that prints directly is
awkward to use from tests, notebooks, APIs, batch jobs, or future LLM pipelines.

---

## 7. What This Subsystem Does Not Do

`main.py` does not:

- parse grammar internally
- define AST nodes
- perform recursive semantic traversal itself
- implement type rules
- implement industrial classification rules
- store symbols as a semantic data structure

It calls modules that own those responsibilities.

---

## 8. Relationships

```text
main.py
├── parser/st_parser.py
│   └── parse_st_file()
├── semantic/visitor.py
│   └── SemanticTraversalVisitor
├── semantic/type_checker.py
│   └── TypeChecker
├── semantic/classifier.py
│   └── IndustrialSemanticClassifier
└── prints all presentation output
```

`main.py` is the boundary between internal compiler data and human-readable
command-line presentation.

---

## 9. Industrial Transformation Relevance

Future IEC 61499 generation will add more stages:

```text
industrial classification
    ↓
semantic graph
    ↓
IR builder
    ↓
IEC 61499 generator
    ↓
verification
```

`main.py` can orchestrate those stages without moving transformation logic into
the entrypoint. This is the main reason centralized orchestration matters.

---

## 10. Key Principle

> `main.py` coordinates the pipeline and presents results. It should not become
> a dumping ground for parser, semantic, or transformation logic.
