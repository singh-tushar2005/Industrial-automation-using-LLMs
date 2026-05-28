# Industrial Compiler Diagnostics: GEN_BIT.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/GEN_BIT.st`
- **Generated:** 2026-05-28T10:20:14.879866+00:00
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

- **Total lines:** 80
- **FUNCTION_BLOCK blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CompilationUnitNode, FunctionInvocationNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, NumberNode, ProgramNode, TypedLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 352

## Construct Support

### Supported
- IF
- ELSE
- assignment
- boolean_logic
- arithmetic_expression
- comparison_expression
- FUNCTION_BLOCK
- VAR
- VAR_INPUT
- VAR_OUTPUT
- FOR_LOOP
- FB_invocation
- typed_literal
- numeric_literal
- boolean_literal

### Unsupported
- state_machine (lines [33, 58])
- multiline_boolean (lines [30])

## Issues

- **[ERROR]** Unsupported construct: state_machine
- **[ERROR]** Unsupported construct: multiline_boolean
