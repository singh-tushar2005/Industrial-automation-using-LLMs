# Industrial Compiler Diagnostics: MATRIX_TestCases.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/test_harness/test_case/MATRIX_TestCases.st`
- **Generated:** 2026-05-28T10:33:25.139231+00:00
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

- **Total lines:** 169
- **PROGRAM blocks:** 1
- **FUNCTION_BLOCK blocks:** 4
- **Multiple compilation units:** yes

## AST Status

- **Status:** full_support
- **Nodes present:** ArrayIndexNode, AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CaseBranchNode, CaseStatementNode, CompilationUnitNode, ForLoopNode, FunctionBlockCallNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, MemoryMappingNode, NumberNode, ProgramNode, TimeLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 810

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
- VAR_OUTPUT
- FOR_LOOP
- FB_invocation
- time_literal
- numeric_literal
- boolean_literal
- array_index
- array_declaration
- memory_mapping
- AT

### Unsupported
- timer_TON (lines [9, 43, 77, 111])

## Issues

- **[ERROR]** Unsupported construct: timer_TON
