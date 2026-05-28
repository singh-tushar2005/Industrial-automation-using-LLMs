# Industrial Compiler Diagnostics: MATRIX.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/MATRIX.st`
- **Generated:** 2026-05-28T10:20:16.688449+00:00
- **Overall Status:** partial_success

## Compatibility Scores

| Metric | Score |
|--------|-------|
| Parser Compatibility | 100% |
| AST Compatibility | 100% |
| Visitor Compatibility | 100% |
| Control Grammar Support | 100% |
| Computational Grammar Support | 100% |
| Runtime Grammar Support | 100% |

## Progression (vs previous run)

- **Parser:** → 0%  (was 100%)
- **AST:** → 0%  (was 100%)
- **Visitor:** → 0%  (was 100%)

## Parse Status

- **Status:** success
- **Failures:** none

## Corpus Structure

- **Total lines:** 103
- **FUNCTION_BLOCK blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** ArrayIndexNode, AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CompilationUnitNode, ExitNode, ForLoopNode, FunctionInvocationNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, NumberNode, ProgramNode, TypedLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** partial_support
- **Traversal events:** 619
- **Missing methods:** visit_str

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
- FOR_LOOP
- EXIT
- FB_invocation
- typed_literal
- numeric_literal
- boolean_literal
- hex_literal
- array_index
- array_declaration

### Unsupported
_None detected._

## Issues

- **[WARNING]** Missing visitor method: visit_str
