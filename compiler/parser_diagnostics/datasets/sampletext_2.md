# Industrial Compiler Diagnostics: sampletext_2.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/sampletext_2.st`
- **Generated:** 2026-05-28T10:20:18.524152+00:00
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

- **Total lines:** 308
- **PROGRAM blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CaseBranchNode, CaseStatementNode, CompilationUnitNode, IfStatementNode, LogicalExpressionNode, NumberNode, ProgramNode, VarBlockNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 1409

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
- state_machine (lines [18, 21, 47, 73, 94, 115, 134, 158, 178, 201, 226, 246, 268, 303])
- multiline_boolean (lines [16, 39, 41, 43, 68, 70, 198])

## Issues

- **[ERROR]** Unsupported construct: state_machine
- **[ERROR]** Unsupported construct: multiline_boolean
