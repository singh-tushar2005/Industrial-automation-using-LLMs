# Industrial Compiler Diagnostics: DEC_TO_HEX.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/Implementation_datasets/DEC_TO_HEX.st`
- **Generated:** 2026-05-28T10:32:38.743422+00:00
- **Overall Status:** failed

## Compatibility Scores

| Metric | Score |
|--------|-------|
| Parser Compatibility | 25% |
| AST Compatibility | 0% |
| Visitor Compatibility | 0% |
| Control Grammar Support | 0% |
| Computational Grammar Support | 0% |
| Runtime Grammar Support | 0% |

## Progression (vs previous run)

- **Parser:** → 0%  (was 25%)
- **AST:** → 0%  (was 0%)
- **Visitor:** → 0%  (was 0%)

## Parse Status

- **Status:** failed
- **Failures:**
  - [CRITICAL] [invalid_statement_sequence] Expected Keyword 'END_FUNCTION_BLOCK', found 'VAR'  (at char 122), (line:8, col:3) line 8, col 3
    - Expected: Expected Keyword 'END_FUNCTION_BLOCK'
    - Found: 'VAR'
    - Parsed prefix: 11.6%

## Parse Failure Details

- **Category:** invalid_statement_sequence
- **Failing line:** `  VAR`
- **Previous lines:**
  ```  VAR_OUTPUT```
  ```    HexString : STRING;```
  ```  END_VAR```
- **Next lines:**
  ```    i : INT;```
  ```    hexDigits : ARRAY [0..15] OF STRING := ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'];```
  ```    digitIndex : INT;```
- **Parsed prefix:** 11.6%
- **Parsed lines:** 18.6%

## Corpus Structure

- **Total lines:** 43
- **FUNCTION_BLOCK blocks:** 1

## AST Status

- **Status:** no_ast

## Visitor Status

- **Status:** no_ast
- **Traversal events:** 0

## Construct Support

### Supported
- IF
- assignment
- boolean_logic
- arithmetic_expression
- comparison_expression
- FUNCTION_BLOCK
- VAR
- VAR_INPUT
- VAR_OUTPUT
- FOR_LOOP
- RETURN
- FB_invocation
- numeric_literal
- boolean_literal
- string_literal
- array_index
- array_declaration

### Unsupported
_None detected._

## Issues

- **[CRITICAL]** Expected Keyword 'END_FUNCTION_BLOCK', found 'VAR'  (at char 122), (line:8, col:3)
