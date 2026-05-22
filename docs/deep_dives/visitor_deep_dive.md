# Visitor Deep Dive

> The visitor system provides reusable recursive traversal over AST nodes.

---

## 1. Purpose

The visitor subsystem solves the problem of walking an AST without putting
analysis logic inside AST node classes.

An AST is recursive:

```text
ProgramNode
└── BlockNode
    └── IfStatementNode
        ├── condition
        └── then_body
            └── AssignmentNode
```

Many analysis passes need to walk this tree. Instead of every pass inventing its
own traversal style, the project uses a shared visitor pattern.

---

## 2. Inputs

Visitor inputs are AST objects produced by the parser:

```text
parse_st_file()
    ↓
ProgramNode
    ↓
visitor.visit(program)
```

---

## 3. Outputs

The base visitor only dispatches. Specific visitors decide what to return.

Current visitor-based outputs include:

| Visitor | Output |
|---|---|
| `SemanticTraversalVisitor` | ordered traversal event data |
| `TypeChecker` | type diagnostics and symbol metadata |
| `IndustrialSemanticClassifier` | industrial behavior findings |

---

## 4. Internal Logic

The base visitor uses class-name dispatch.

```text
node.__class__.__name__ = "IfStatementNode"
    ↓
method name = "visit_IfStatementNode"
    ↓
call self.visit_IfStatementNode(node)
```

This allows a visitor to define methods such as:

```text
visit_ProgramNode()
visit_BlockNode()
visit_AssignmentNode()
visit_FunctionBlockCallNode()
```

If a node has no matching visitor method, `generic_visit()` raises a clear
error.

---

## 5. Recursive Traversal

Recursive traversal means the visitor calls itself on child nodes.

```text
visit_IfStatementNode(node)
├── visit(node.condition)
└── visit(node.then_body)
```

```text
visit_BlockNode(node)
└── for each statement:
    └── visit(statement)
```

This recursion mirrors the AST structure.

---

## 6. Traversal Reuse

The visitor is traversal infrastructure. It is not one fixed analysis.

```text
ASTVisitor
├── SemanticTraversalVisitor
├── TypeChecker
└── IndustrialSemanticClassifier
```

Each pass can reuse the dispatch model while implementing its own node-specific
behavior.

This matters because semantic systems should not duplicate recursion. If every
new pass walks the AST differently, the project becomes fragile:

- some passes may miss new node types
- traversal order may become inconsistent
- nested structures may be handled incorrectly
- future refactors become harder

---

## 7. What This Subsystem Does Not Do

The visitor infrastructure does not:

- parse source text
- create AST nodes
- own symbol table storage
- decide all semantic meanings by itself
- print terminal reports
- generate IEC 61499

It provides the mechanism for walking the tree. Specific subclasses provide
analysis behavior.

---

## 8. Relationships

```text
AST nodes
    ↓
ASTVisitor dispatch
    ↓
specialized semantic pass
    ├── traversal data
    ├── type checking report
    └── industrial classification metadata
```

The visitor is the shared bridge between AST structure and semantic analysis.

---

## 9. Industrial Transformation Relevance

Industrial transformation requires consistent analysis of nested control logic:

- nested IF statements
- CASE-based sequencing
- timer-dependent conditions
- coordinated actuator commands
- safety interlock gates

The visitor pattern ensures each semantic pass can walk these structures
consistently.

---

## 10. Key Principle

> The visitor is the common traversal engine. Higher-level semantic passes
> should build on it instead of duplicating AST recursion.
