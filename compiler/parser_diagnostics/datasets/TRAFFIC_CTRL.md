# Industrial Compiler Diagnostics: TRAFFIC_CTRL.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/TRAFFIC_CTRL.st`
- **Generated:** 2026-05-28T10:32:42.072233+00:00
- **Overall Status:** partial_success

## Compatibility Scores

| Metric | Score |
|--------|-------|
| Parser Compatibility | 96% |
| AST Compatibility | 100% |
| Visitor Compatibility | 100% |
| Control Grammar Support | 100% |
| Computational Grammar Support | 100% |
| Runtime Grammar Support | 100% |

## Progression (vs previous run)

- **Parser:** → 0%  (was 96%)
- **AST:** → 0%  (was 100%)
- **Visitor:** → 0%  (was 100%)

## Parse Status

- **Status:** success
- **Failures:** none

## Corpus Structure

- **Total lines:** 94
- **FUNCTION_BLOCK blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** AssignmentNode, BlockNode, BooleanNode, CaseBranchNode, CaseStatementNode, CompilationUnitNode, FunctionBlockCallNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, NumberNode, ProgramNode, TimeLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 308

## Construct Support

### Supported
- IF
- CASE_OF
- assignment
- boolean_logic
- arithmetic_expression
- comparison_expression
- FUNCTION_BLOCK
- VAR
- VAR_INPUT
- VAR_OUTPUT
- FB_invocation
- time_literal
- numeric_literal
- boolean_literal

### Unsupported
- timer_TON (lines [25])
- state_machine (lines [37])

## Issues

- **[ERROR]** Unsupported construct: timer_TON
- **[ERROR]** Unsupported construct: state_machine
