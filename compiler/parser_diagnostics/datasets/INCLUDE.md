# Industrial Compiler Diagnostics: INCLUDE.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/INCLUDE.st`
- **Generated:** 2026-05-28T10:32:40.328294+00:00
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

- **Total lines:** 338
- **FUNCTION_BLOCK blocks:** 3
- **FUNCTION blocks:** 11
- **Multiple compilation units:** yes

## AST Status

- **Status:** full_support
- **Nodes present:** AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CompilationUnitNode, ForLoopNode, FunctionInvocationNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, NumberNode, ProgramNode, TypedLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 1031

## Construct Support

### Supported
- IF
- ELSIF
- ELSE
- assignment
- boolean_logic
- arithmetic_expression
- comparison_expression
- FUNCTION
- FUNCTION_BLOCK
- VAR
- VAR_INPUT
- VAR_OUTPUT
- VAR_IN_OUT
- FOR_LOOP
- FB_invocation
- typed_literal
- numeric_literal
- boolean_literal
- hex_literal
- ON

### Unsupported
- multiline_boolean (lines [64])

## Issues

- **[ERROR]** Unsupported construct: multiline_boolean
