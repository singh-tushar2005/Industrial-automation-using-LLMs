# Industrial Compiler Diagnostics: FT_PIDWL_TestCases.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/test_harness/test_case/FT_PIDWL_TestCases.st`
- **Generated:** 2026-05-28T10:20:56.308107+00:00
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

- **Total lines:** 153
- **PROGRAM blocks:** 1
- **FUNCTION_BLOCK blocks:** 4
- **Multiple compilation units:** yes

## AST Status

- **Status:** full_support
- **Nodes present:** ArrayIndexNode, AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CaseBranchNode, CaseStatementNode, CompilationUnitNode, ForLoopNode, FunctionBlockCallNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, MemoryMappingNode, NumberNode, ProgramNode, TimeLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** partial_support
- **Traversal events:** 695
- **Missing methods:** visit_str

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
- timer_TON (lines [9, 39, 69, 99])

## Issues

- **[ERROR]** Unsupported construct: timer_TON
- **[WARNING]** Missing visitor method: visit_str
