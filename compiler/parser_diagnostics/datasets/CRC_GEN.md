# Industrial Compiler Diagnostics: CRC_GEN.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/CRC_GEN.st`
- **Generated:** 2026-05-28T10:32:38.723066+00:00
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

- **Total lines:** 95
- **FUNCTION_BLOCK blocks:** 1

## AST Status

- **Status:** full_support
- **Nodes present:** ArrayIndexNode, AssignmentNode, BinaryExpressionNode, BlockNode, CompilationUnitNode, ForLoopNode, FunctionInvocationNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, NumberNode, ProgramNode, TypedLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode, WhileLoopNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 387

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
- VAR_IN_OUT
- FOR_LOOP
- WHILE_LOOP
- FB_invocation
- typed_literal
- numeric_literal
- hex_literal
- array_index
- array_declaration
- WITH
- AT

### Unsupported
- multiline_boolean (lines [43, 54, 70, 72, 74, 76, 78, 80, 85, 88, 90])

## Issues

- **[ERROR]** Unsupported construct: multiline_boolean
