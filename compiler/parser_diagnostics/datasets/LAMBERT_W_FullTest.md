# Industrial Compiler Diagnostics: LAMBERT_W_FullTest.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/test_harness/Full_test/LAMBERT_W_FullTest.st`
- **Generated:** 2026-05-28T10:33:03.804301+00:00
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

- **Total lines:** 733
- **PROGRAM blocks:** 2
- **FUNCTION_BLOCK blocks:** 14
- **FUNCTION blocks:** 11
- **CONFIGURATION blocks:** 1
- **Multiple compilation units:** yes

## AST Status

- **Status:** full_support
- **Nodes present:** ArrayIndexNode, AssignmentNode, BinaryExpressionNode, BlockNode, BooleanNode, CaseBranchNode, CaseStatementNode, CompilationUnitNode, ConfigurationNode, ExitNode, ForLoopNode, FunctionBlockCallNode, FunctionInvocationNode, IfStatementNode, InvocationArgumentNode, LogicalExpressionNode, MemoryMappingNode, NumberNode, ProgramBindingNode, ProgramNode, ResourceNode, ReturnNode, TaskNode, TimeLiteralNode, TypedLiteralNode, VarBlockNode, VariableDeclarationNode, VariableNode

## Visitor Status

- **Status:** full_support
- **Traversal events:** 2736

## Construct Support

### Supported
- IF
- ELSIF
- ELSE
- CASE_OF
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
- EXIT
- RETURN
- FB_invocation
- time_literal
- typed_literal
- numeric_literal
- boolean_literal
- hex_literal
- array_index
- array_declaration
- CONFIGURATION
- RESOURCE
- TASK
- PROGRAM_binding
- memory_mapping
- WITH
- ON
- AT

### Unsupported
- timer_TON (lines [390, 419, 448, 477, 506, 535, 564, 593, 622, 651])
- multiline_boolean (lines [64])

## Issues

- **[ERROR]** Unsupported construct: timer_TON
- **[ERROR]** Unsupported construct: multiline_boolean
