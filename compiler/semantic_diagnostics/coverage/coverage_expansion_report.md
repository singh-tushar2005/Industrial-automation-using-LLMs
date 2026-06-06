# Coverage Expansion Report

## 1. Global Coverage

| Metric | Before | After | Δ |
|---|---|---|---|
| Coverage % | 60.0% | 99.2% | +39.2pp |
| Executable statements | 5786 | 5786 | 0 |
| Covered statements | 3471 | 5740 | +2269 |
| Uncovered statements | 2314 | 46 | -2268 |

## 2. Operation Frequencies (After Expansion)

| Operation Type | Count |
|---|---|
| comparison_operation | 2265 |
| data_movement | 1324 |
| function_invocation | 581 |
| bitwise_operation | 469 |
| timer_invocation | 433 |
| fb_invocation | 424 |
| process_calculation | 345 |
| state_update | 290 |
| measurement_calculation | 242 |
| history_update | 227 |
| accumulator_update | 212 |
| lookup_operation | 194 |
| array_write | 191 |
| matrix_access | 127 |
| iterative_computation | 79 |
| bitwise_update | 68 |
| counter_update | 33 |
| mathematical_solver | 30 |
| array_read | 12 |
| return | 6 |

## 3. Relationship Frequencies (After Expansion)

| Relationship Type | Count |
|---|---|
| depends_on | 525 |
| sequences | 368 |
| activates | 158 |
| controls | 109 |
| triggers | 64 |
| transitions_to | 57 |
| contains | 40 |
| uses | 20 |
| disables | 3 |

## 4. Per-Dataset Coverage

| Dataset | Executable | Covered | Operations | Coverage % |
|---|---|---|---|---|
| Implementation_datasets/CRC_GEN.st | 26 | 26 | 47 | 100.0% |
| Implementation_datasets/FLOW_METER.st | 25 | 25 | 33 | 100.0% |
| Implementation_datasets/FT_PIDWL.st | 12 | 12 | 12 | 100.0% |
| Implementation_datasets/GEN_BIT.st | 36 | 36 | 47 | 100.0% |
| Implementation_datasets/GEN_SIN.st | 15 | 15 | 23 | 100.0% |
| Implementation_datasets/INCLUDE.st | 64 | 64 | 102 | 100.0% |
| Implementation_datasets/LAMBERT_W.st | 13 | 13 | 19 | 100.0% |
| Implementation_datasets/MATRIX.st | 33 | 31 | 57 | 93.9% |
| Implementation_datasets/SEQUENCE_8.st | 60 | 60 | 88 | 100.0% |
| Implementation_datasets/TOOL_CHANGER.st | 13 | 13 | 13 | 100.0% |
| Implementation_datasets/TRAFFIC_CTRL.st | 42 | 42 | 43 | 100.0% |
| Implementation_datasets/robotic_sequence.st | 106 | 106 | 127 | 100.0% |
| Implementation_datasets/sampletext_2.st | 178 | 178 | 199 | 100.0% |
| Implementation_datasets/sampletext_3.st | 178 | 178 | 199 | 100.0% |
| Implementation_datasets/sampletext_4.st | 1 | 1 | 1 | 100.0% |
| test_harness/Full_test/CRC_GEN_FullTest (1).st | 136 | 135 | 197 | 99.3% |
| test_harness/Full_test/CRC_GEN_FullTest.st | 142 | 141 | 213 | 99.3% |
| test_harness/Full_test/FLOW_METER_FullTest (1).st | 183 | 182 | 235 | 99.5% |
| test_harness/Full_test/FLOW_METER_FullTest.st | 168 | 167 | 219 | 99.4% |
| test_harness/Full_test/FT_PIDWL_FullTest (1).st | 128 | 127 | 173 | 99.2% |
| test_harness/Full_test/FT_PIDWL_FullTest.st | 140 | 139 | 186 | 99.3% |
| test_harness/Full_test/GEN_BIT_FullTest.st | 149 | 148 | 216 | 99.3% |
| test_harness/Full_test/GEN_SIN_FullTest (1).st | 146 | 145 | 201 | 99.3% |
| test_harness/Full_test/GEN_SIN_FullTest (2).st | 146 | 145 | 201 | 99.3% |
| test_harness/Full_test/GEN_SIN_FullTest.st | 158 | 157 | 214 | 99.4% |
| test_harness/Full_test/LAMBERT_W_FullTest (1).st | 306 | 305 | 365 | 99.7% |
| test_harness/Full_test/LAMBERT_W_FullTest.st | 231 | 230 | 285 | 99.6% |
| test_harness/Full_test/MATRIX_FullTest (1).st | 143 | 140 | 227 | 97.9% |
| test_harness/Full_test/MATRIX_FullTest.st | 161 | 158 | 247 | 98.1% |
| test_harness/Full_test/SEQUENCE_8_FullTest (1).st | 158 | 157 | 248 | 99.4% |
| test_harness/Full_test/SEQUENCE_8_FullTest.st | 158 | 157 | 248 | 99.4% |
| test_harness/Full_test/TOOL_CHANGER_FullTest (1).st | 162 | 161 | 212 | 99.4% |
| test_harness/Full_test/TOOL_CHANGER_FullTest.st | 156 | 155 | 204 | 99.4% |
| test_harness/Full_test/TRAFFIC_CTRL_FullTest (1).st | 152 | 151 | 221 | 99.3% |
| test_harness/Full_test/TRAFFIC_CTRL_FullTest.st | 170 | 169 | 241 | 99.4% |
| test_harness/test_case/CRC_GEN_TestCases (1).st | 46 | 45 | 48 | 97.8% |
| test_harness/test_case/CRC_GEN_TestCases.st | 52 | 51 | 64 | 98.1% |
| test_harness/test_case/DEC_TO_HEX_TestCases.st | 274 | 273 | 292 | 99.6% |
| test_harness/test_case/FLOW_METER_TestCases (1).st | 94 | 93 | 100 | 98.9% |
| test_harness/test_case/FLOW_METER_TestCases.st | 79 | 78 | 84 | 98.7% |
| test_harness/test_case/FT_PIDWL_TestCases (1).st | 52 | 51 | 59 | 98.1% |
| test_harness/test_case/FT_PIDWL_TestCases.st | 64 | 63 | 72 | 98.4% |
| test_harness/test_case/GEN_BIT_TestCases.st | 49 | 48 | 67 | 98.0% |
| test_harness/test_case/GEN_SIN_TestCases (1).st | 67 | 66 | 76 | 98.5% |
| test_harness/test_case/GEN_SIN_TestCases.st | 79 | 78 | 89 | 98.7% |
| test_harness/test_case/LAMBERT_W_TestCases (1).st | 229 | 228 | 244 | 99.6% |
| test_harness/test_case/LAMBERT_W_TestCases.st | 154 | 153 | 164 | 99.4% |
| test_harness/test_case/MATRIX_TestCases (1).st | 46 | 45 | 68 | 97.8% |
| test_harness/test_case/MATRIX_TestCases.st | 64 | 63 | 88 | 98.4% |
| test_harness/test_case/SEQUENCE_8_TestCases (1).st | 34 | 33 | 58 | 97.1% |
| test_harness/test_case/SEQUENCE_8_TestCases.st | 34 | 33 | 58 | 97.1% |
| test_harness/test_case/TOOL_CHANGER_TestCases (1).st | 85 | 84 | 97 | 98.8% |
| test_harness/test_case/TOOL_CHANGER_TestCases.st | 79 | 78 | 89 | 98.7% |
| test_harness/test_case/TRAFFIC_CTRL_TestCases (1).st | 46 | 45 | 76 | 97.8% |
| test_harness/test_case/TRAFFIC_CTRL_TestCases.st | 64 | 63 | 96 | 98.4% |

## 5. Newly Covered Statement Categories

The following categories are now explicitly represented by the semantic layer:

- **array_read**: Reading from an array index (e.g., `val := arr[i]`).
- **array_write**: Writing to an array index (e.g., `arr[i] := val`).
- **counter_update**: Incrementing or resetting a counter (e.g., `cnt := cnt + 1`).
- **history_update**: Updating a history variable (e.g., `last := tx`).
- **accumulator_update**: Accumulating values (e.g., `crc := crc XOR byte`).
- **matrix_access**: Matrix operations (e.g., `Result := Matrix_Mul(A, B)`).
- **state_update**: Updating a state variable (e.g., `_step := 3`).
- **fb_invocation**: Standalone function block calls (e.g., `TON_1(IN := TRUE, PT := T#5s)`).
- **timer_invocation**: Timer block calls (e.g., `TON_1(...)`).
- **counter_invocation**: Counter block calls (e.g., `CTU_1(...)`).
- **function_invocation**: Standalone function calls (e.g., `SHL(x, 1)`).
- **return**: Return statements (e.g., `RETURN result`).

## 6. Coverage Gap Analysis

Remaining uncovered statements: 46 (0.8%).

The remaining uncovered logic is primarily:
- Deeply nested control structures where the operation extractor does not create a separate operation for every nested branch.
- `IfStatementNode` guards that are purely boolean checks without semantic targets (e.g., `IF run THEN`).
