# Visitor Pattern

The visitor pattern is a common compiler technique for walking an AST.

The AST nodes stay simple. They store program structure, but they do not know
how to analyze themselves. A visitor decides what to do based on each node type.

```text
ProgramNode          -> visit_ProgramNode()
IfStatementNode      -> visit_IfStatementNode()
AssignmentNode       -> visit_AssignmentNode()
BinaryExpressionNode -> visit_BinaryExpressionNode()
```

## Why Compilers Use Visitors

Compilers perform many passes over the same AST:

- semantic traversal
- symbol collection
- type checking
- control-flow analysis
- dependency analysis
- code generation
- migration to another runtime model

Visitors keep these operations out of the AST classes. That matters because AST
classes should remain stable data structures while analysis passes evolve.

## Traversal Results

The current semantic traversal records events such as:

```text
ProgramNode: start of Structured Text program
  BlockNode: 1 statement(s)
    IfStatementNode: conditional execution
```

The visitor returns this as structured data. `main.py` decides how to print it.
That keeps semantic analysis reusable outside the terminal.
