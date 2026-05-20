# AST Concepts

An Abstract Syntax Tree, or AST, represents source code as structured objects
instead of raw text.

For example, this Structured Text:

```iecst
IF StartButton THEN
    Motor := TRUE;
END_IF;
```

can be represented as:

```text
IfStatementNode
├── condition: VariableNode("StartButton")
└── then_body: BlockNode
    └── AssignmentNode
        ├── target: VariableNode("Motor")
        └── value: BooleanNode(True)
```

## Why ASTs Matter

Text is difficult to analyze reliably. An AST makes program structure explicit:

- variables become `VariableNode`
- boolean literals become `BooleanNode`
- numeric values become `NumberNode`
- expressions become `BinaryExpressionNode` or `LogicalExpressionNode`
- statement blocks become `BlockNode`
- complete programs become `ProgramNode`

Once code is in AST form, later compiler passes can operate on structure rather
than searching through strings.

## Recursive Shape

Many AST nodes contain other AST nodes. A comparison such as:

```iecst
Counter + 1 > Limit
```

has a comparison node whose left side is itself an arithmetic expression:

```text
BinaryExpressionNode(">")
├── left: BinaryExpressionNode("+")
│   ├── left: VariableNode("Counter")
│   └── right: NumberNode(1)
└── right: VariableNode("Limit")
```

This recursive shape is what lets small node classes represent large programs.
