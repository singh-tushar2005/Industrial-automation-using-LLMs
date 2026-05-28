# Industrial Compiler Diagnostics: DEC_TO_HEX_FullTest.st

- **File:** `/home/res/Research/230957084/Industrial_Automation/Industrial-automation-using-LLMs/datasets/Industrial_data/test_harness/Full_test/DEC_TO_HEX_FullTest.st`
- **Generated:** 2026-05-28T10:20:23.363718+00:00
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
  - [CRITICAL] [multi_program_file] Expected end of text, found 'FUNCTION'  (at char 6740), (line:340, col:1) line 340, col 1
    - Expected: Expected end of text
    - Found: 'FUNCTION'
    - Parsed prefix: 28.1%

## Parse Failure Details

- **Category:** multi_program_file
- **Failing line:** `FUNCTION_BLOCK DEC_TO_HEX`
- **Previous lines:**
  ```  (* T_PLC_MS required *)```
  ```END_FUNCTION_BLOCK```
  ``````
- **Next lines:**
  ```  VAR_INPUT```
  ```    DecimalValue : DINT;```
  ```  END_VAR```
- **Parsed prefix:** 28.1%
- **Parsed lines:** 34.3%

## Corpus Structure

- **Total lines:** 991
- **PROGRAM blocks:** 2
- **FUNCTION_BLOCK blocks:** 22
- **FUNCTION blocks:** 11
- **CONFIGURATION blocks:** 1
- **Multiple compilation units:** yes

## AST Status

- **Status:** no_ast

## Visitor Status

- **Status:** no_ast
- **Traversal events:** 0

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
- RETURN
- FB_invocation
- time_literal
- typed_literal
- numeric_literal
- boolean_literal
- hex_literal
- string_literal
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
- timer_TON (lines [392, 421, 450, 479, 508, 537, 566, 595, 624, 653, 682, 711, 740, 769, 798, 827, 856, 885])
- multiline_boolean (lines [64])

## Issues

- **[CRITICAL]** Expected end of text, found 'FUNCTION'  (at char 6740), (line:340, col:1)
