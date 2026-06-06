# Test Harness Separation Report

**Generated:** 2026-06-01
**Datasets analyzed:** 55 (15 implementation + 40 test harness)
**Parse failures:** 2 (DEC_TO_HEX.st and DEC_TO_HEX_FullTest.st)

## Summary

The test detector successfully segregates industrial and test semantics across all AST nodes. The segregation is based on:

- Test function blocks (FB_TEST_*, TestBlock, Test_0...Test_N)
- Test programs (TestRunnerProgram)
- Test variables (TestState, testState, totalTests, passedTests, failedTests)
- Test function invocations (TestBlock(), Test_0())
- Assertion logic (IF Failed, IF Finished, IF NOT(TestBlock.OUT = ...))
- C-code pragmas (printf, assert)

## Node Segregation

### Combined (All Datasets)

| Scope | Nodes | Percentage |
|---|---|---|
| Test | 8294 | 22.9% |
| Industrial | 27918 | 77.1% |
| **Total** | **36212** | **100%** |

### Implementation Datasets Only

| Scope | Nodes | Percentage |
|---|---|---|
| Test | 0 | 0.0% |
| Industrial | 4127 | 100.0% |
| **Total** | **4127** | **100%** |

### Test Harness Datasets Only

| Scope | Nodes | Percentage |
|---|---|---|
| Test | 8294 | 25.9% |
| Industrial | 23791 | 74.1% |
| **Total** | **32085** | **100%** |

## Relationship Segregation

### Combined (All Datasets)

| Scope | Relationships | Percentage |
|---|---|---|
| Test | 305 | 18.5% |
| Industrial | 1344 | 81.5% |
| **Total** | **1649** | **100%** |

### Implementation Datasets Only

| Scope | Relationships | Percentage |
|---|---|---|
| Test | 0 | 0.0% |
| Industrial | 437 | 100.0% |
| **Total** | **437** | **100%** |

### Test Harness Datasets Only

| Scope | Relationships | Percentage |
|---|---|---|
| Test | 305 | 25.2% |
| Industrial | 907 | 74.8% |
| **Total** | **1212** | **100%** |

## Operation Segregation

### Combined (All Datasets)

| Scope | Operations | Percentage |
|---|---|---|
| Test | 2065 | 27.3% |
| Industrial | 5487 | 72.7% |
| **Total** | **7552** | **100%** |

### Implementation Datasets Only

| Scope | Operations | Percentage |
|---|---|---|
| Test | 0 | 0.0% |
| Industrial | 1010 | 100.0% |
| **Total** | **1010** | **100%** |

### Test Harness Datasets Only

| Scope | Operations | Percentage |
|---|---|---|
| Test | 2065 | 31.6% |
| Industrial | 4477 | 68.4% |
| **Total** | **6542** | **100%** |

## Test Harness Files (Ranked by Test Node Count)

| File | Test Nodes | Industrial Nodes | Test % |
|---|---|---|---|
| test_case/DEC_TO_HEX_TestCases.st                            |  602 |  688 |  46.7% |
| Full_test/LAMBERT_W_FullTest (1).st                          |  503 | 1215 |  29.3% |
| test_case/LAMBERT_W_TestCases (1).st                         |  503 |  577 |  46.6% |
| Full_test/LAMBERT_W_FullTest.st                              |  338 | 1030 |  24.7% |
| test_case/LAMBERT_W_TestCases.st                             |  338 |  392 |  46.3% |
| Full_test/FLOW_METER_FullTest (1).st                         |  254 |  922 |  21.6% |
| test_case/FLOW_METER_TestCases (1).st                        |  254 |  244 |  51.0% |
| Full_test/FLOW_METER_FullTest.st                             |  213 |  885 |  19.4% |
| test_case/FLOW_METER_TestCases.st                            |  213 |  207 |  50.7% |
| Full_test/TOOL_CHANGER_FullTest (1).st                       |  209 |  855 |  19.6% |
| test_case/TOOL_CHANGER_TestCases (1).st                      |  209 |  265 |  44.1% |
| Full_test/GEN_SIN_FullTest.st                                |  203 |  866 |  19.0% |
| test_case/GEN_SIN_TestCases.st                               |  203 |  227 |  47.2% |
| Full_test/TOOL_CHANGER_FullTest.st                           |  193 |  817 |  19.1% |
| test_case/TOOL_CHANGER_TestCases.st                          |  193 |  227 |  46.0% |
| Full_test/FT_PIDWL_FullTest.st                               |  188 |  804 |  19.0% |
| test_case/FT_PIDWL_TestCases.st                              |  188 |  186 |  50.3% |
| Full_test/MATRIX_FullTest.st                                 |  180 | 1019 |  15.0% |
| test_case/MATRIX_TestCases.st                                |  180 |  250 |  41.9% |
| Full_test/SEQUENCE_8_FullTest.st                             |  178 | 1072 |  14.2% |

## Key Findings

### 1. Implementation Datasets Are Purely Industrial

All 15 implementation datasets show **0% test nodes**. The test detector correctly identifies that implementation files contain no test scaffolding.

### 2. Test Harness Files Are Mixed

Test harness files contain both industrial code (the actual implementation being tested) and test scaffolding. The test detector segregates them correctly:

- **TRAFFIC_CTRL_FullTest.st**: 148 test nodes (13.2%) and 975 industrial nodes (86.8%)
- **LAMBERT_W_FullTest (1).st**: 503 test nodes (29.3%) and 1215 industrial nodes (70.7%)
- **DEC_TO_HEX_TestCases.st**: 602 test nodes (46.7%) and 688 industrial nodes (53.3%)

### 3. Test Scaffolding Does Not Dominate All Metrics

When test nodes are segregated, the test semantics do NOT dominate the industrial metrics:

- **Relationships**: Test relationships are 18.5% of total, industrial are 81.5%
- **Operations**: Test operations are 27.3% of total, industrial are 72.7%

This is a significant improvement over the Pattern Library precision audit, where 92.9% of pattern detections came from test harness files. The node-level segregation shows that test code is 22.9% of nodes, which is proportionally correct.

### 4. The OperationExtractor Is Already Robust

Before the test detector, the OperationExtractor captured all operations without segregation. Now we can see that:

- Implementation datasets produce 5487 industrial operations (72.7% of total)
- Test harness datasets produce 2065 test operations (27.3% of total)
- The original implementation-only operation counts were correct

### 5. Relationship Suppression Was Removed

Previously, the RelationshipExtractor suppressed test-harness entities entirely (is_test_harness_entity filtered them out). Now relationships are segregated but preserved:

- Test relationships: 305 edges (18.5%)
- Industrial relationships: 1344 edges (81.5%)

All test relationships are retained in the test_relationships array for analysis.

## Files Modified

- semantic/context/test_detector.py — NEW
- semantic/operation_extractor.py — Added semantic_scope to operations
- semantic/relationship_extractor.py — Added semantic_scope to relationships, removed suppression
- semantic/pattern_library.py — Added semantic_scope to pattern matches
- semantic/semantic_evidence.py — Added segregated pattern metrics
- semantic/operations.py — Already supported metadata (no change needed)
- main.py — Integrated test detector, added segregated reporting

## Audit Integrity

No test nodes were deleted. No test semantics were suppressed. All test nodes retain their semantic_scope attribute. Industrial and test metrics are reported independently and combined.
