# Industrial Compiler Diagnostics: robotic_sequence.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/robotic_sequence.st`
- **Generated:** 2026-05-28T10:32:42.468042+00:00
- **Overall Status:** partial_success

## Compatibility Scores

| Metric | Score |
|--------|-------|
| Parser Compatibility | 95% |
| AST Compatibility | 100% |
| Visitor Compatibility | 100% |
| Control Grammar Support | 100% |
| Computational Grammar Support | 100% |
| Runtime Grammar Support | 100% |

## Progression (vs previous run)

- **Parser:** → 0%  (was 95%)
- **AST:** → 0%  (was 100%)
- **Visitor:** → 0%  (was 100%)

## Parse Status

- **Status:** success
- **Failures:** none

## Corpus Structure

- **Total lines:** 270
- **PROGRAM blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CaseBranchNode, CaseStatementNode, CompilationUnitNode, IfStatementNode, LogicalExpressionNode, NumberNode, ProgramNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 987

## Construct Support

### Supported
- IF
- CASE_OF
- assignment
- boolean_logic
- arithmetic_expression
- comparison_expression
- VAR
- FB_invocation
- numeric_literal
- boolean_literal

### Unsupported
- state_machine (lines [3, 41, 45, 75, 104, 128, 139, 149, 164, 176, 191, 208, 220, 234, 265])
- multiline_boolean (lines [33, 35, 37, 67, 69, 71, 99, 101, 188])

## Issues

- **[ERROR]** Unsupported construct: state_machine
- **[ERROR]** Unsupported construct: multiline_boolean
