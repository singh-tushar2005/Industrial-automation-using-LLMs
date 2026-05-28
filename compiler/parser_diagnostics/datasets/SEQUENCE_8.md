# Industrial Compiler Diagnostics: SEQUENCE_8.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/SEQUENCE_8.st`
- **Generated:** 2026-05-28T10:32:41.883195+00:00
- **Overall Status:** partial_success

## Compatibility Scores

| Metric | Score |
|--------|-------|
| Parser Compatibility | 98% |
| AST Compatibility | 100% |
| Visitor Compatibility | 100% |
| Control Grammar Support | 100% |
| Computational Grammar Support | 100% |
| Runtime Grammar Support | 100% |

## Progression (vs previous run)

- **Parser:** → 0%  (was 98%)
- **AST:** → 0%  (was 100%)
- **Visitor:** → 0%  (was 100%)

## Parse Status

- **Status:** success
- **Failures:** none

## Corpus Structure

- **Total lines:** 211
- **FUNCTION_BLOCK blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CompilationUnitNode, FunctionInvocationNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, NumberNode, ProgramNode, ReturnNode, TypedLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 1322

## Construct Support

### Supported
- IF
- ELSIF
- assignment
- boolean_logic
- arithmetic_expression
- comparison_expression
- FUNCTION_BLOCK
- VAR
- VAR_INPUT
- VAR_OUTPUT
- RETURN
- FB_invocation
- typed_literal
- numeric_literal
- boolean_literal
- ON

### Unsupported
- multiline_boolean (lines [96, 108, 122, 136, 150, 164, 178, 192])

## Issues

- **[ERROR]** Unsupported construct: multiline_boolean
