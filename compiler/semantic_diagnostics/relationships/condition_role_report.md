# Condition Role Classification Report — Full Industrial Dataset

**Phase A — Diagnostic Only**

Total files scanned: 57

This report shows the output of `classify_condition_roles()` for every `IF` condition across all industrial datasets.
No relationships were modified; this is purely structural inspection.

---

## Implementation_datasets/CRC_GEN.st

### Example 1

**Condition:** `REV_IN`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | REV_IN |
| CONTEXT | — |

### Example 2

**Condition:** `REV_IN`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | REV_IN |
| CONTEXT | — |

### Example 3

**Condition:** `_CRC_GEN AND TypedLiteralNode(type_name='DWORD', value='16#8000_0000') > TypedLiteralNode(type_name='DWORD', value='0')`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | _CRC_GEN |
| CONTEXT | — |

### Example 4

**Condition:** `_CRC_GEN AND TypedLiteralNode(type_name='DWORD', value='16#8000_0000') > TypedLiteralNode(type_name='DWORD', value='0')`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | _CRC_GEN |
| CONTEXT | — |

### Example 5

**Condition:** `REV_OUT`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | REV_OUT |
| CONTEXT | — |

---

## Implementation_datasets/DEC_TO_HEX.st

ERROR: Expected Keyword 'END_FUNCTION_BLOCK', found 'VAR'  (at char 122), (line:8, col:3)
---

## Implementation_datasets/FLOW_METER.st

### Example 1

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 2

**Condition:** `RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | RST |
| CONTEXT | — |

### Example 3

**Condition:** `NOT e_last`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | — |
| CONTEXT | e_last |

### Example 4

**Condition:** `X > 1.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | X |
| CONTEXT | — |

### Example 5

**Condition:** `tx - tl >= UPDATE_TIME AND UPDATE_TIME > t#0s`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | UPDATE_TIME |
| CONTEXT | tx, tl, UPDATE_TIME |

---

## Implementation_datasets/FT_PIDWL.st

### Example 1

**Condition:** `rst`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | rst |
| CONTEXT | — |

### Example 2

**Condition:** `TN = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TN |
| CONTEXT | — |

### Example 3

**Condition:** `Y < LIM_L`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_L |

---

## Implementation_datasets/GEN_BIT.st

### Example 1

**Condition:** `clk AND NOT rst`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | clk, rst |
| CONTEXT | — |

### Example 2

**Condition:** `run`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | run |
| CONTEXT | — |

### Example 3

**Condition:** `cnt = steps`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | cnt |
| CONTEXT | steps |

### Example 4

**Condition:** `cnt = 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | cnt |
| CONTEXT | — |

### Example 5

**Condition:** `cnt < steps`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | cnt |
| CONTEXT | steps |

### Example 6

**Condition:** `cnt = steps AND rep <> 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | cnt, rep |
| CONTEXT | steps |

### Example 7

**Condition:** `rx > rep AND rep <> 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | rx, rep |
| CONTEXT | rep |

### Example 8

**Condition:** `rst`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | rst |
| CONTEXT | — |

---

## Implementation_datasets/GEN_SIN.st

### Example 1

**Condition:** `dl < 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | dl |
| CONTEXT | — |

### Example 2

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 3

**Condition:** `tx >= pt`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | tx |
| CONTEXT | pt |

### Example 4

**Condition:** `pt > t#0s`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | pt |
| CONTEXT | — |

---

## Implementation_datasets/INCLUDE.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 3 more examples*

---

## Implementation_datasets/LAMBERT_W.st

### Example 1

**Condition:** `x < -0.367879441171442`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | x |
| CONTEXT | — |

### Example 2

**Condition:** `FunctionInvocationNode(name='REAL_TO_DWORD', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='w'))]) AND TypedLiteralNode(type_name='DWORD', value='16#FFFF_FFFC') = last`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | w |
| CONTEXT | last |

---

## Implementation_datasets/MATRIX.st

### Example 1

**Condition:** `ArrayIndexNode(array='X', index=VariableNode(name='i')) <> ArrayIndexNode(array='L', index=VariableNode(name='i'))`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `FunctionInvocationNode(name='BIT_OF_DWORD', arguments=[InvocationArgumentNode(name='', value=FunctionInvocationNode(name='BYTE_TO_DWORD', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='temp'))])), InvocationArgumentNode(name='', value=NumberNode(value='0'))])`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | temp |
| CONTEXT | — |

### Example 3

**Condition:** `NOT release AND code < TypedLiteralNode(type_name='BYTE', value='127')`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | release, code |
| CONTEXT | — |

---

## Implementation_datasets/SEQUENCE_8.st

### Example 1

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 2

**Condition:** `rst`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | rst |
| CONTEXT | — |

### Example 3

**Condition:** `status > TypedLiteralNode(type_name='BYTE', value='0') AND status < TypedLiteralNode(type_name='BYTE', value='100') AND stop_on_error`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | status, stop_on_error |
| CONTEXT | — |

### Example 4

**Condition:** `run AND _step = 0`

| Role | Variables |
|---|---|
| CONTROL | _step |
| PERMISSIVE | run |
| CONTEXT | — |

### Example 5

**Condition:** `NOT q0 AND in0 AND tx - last <= wait0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | q0, in0 |
| CONTEXT | tx, last, wait0 |

### Example 6

**Condition:** `run AND _step = 1`

| Role | Variables |
|---|---|
| CONTROL | _step |
| PERMISSIVE | run |
| CONTEXT | — |

### Example 7

**Condition:** `NOT q1 AND in1 AND tx - last <= wait1`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | q1, in1 |
| CONTEXT | tx, last, wait1 |

### Example 8

**Condition:** `run AND _step = 2`

| Role | Variables |
|---|---|
| CONTROL | _step |
| PERMISSIVE | run |
| CONTEXT | — |

### Example 9

**Condition:** `NOT q2 AND in2 AND tx - last <= wait2`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | q2, in2 |
| CONTEXT | tx, last, wait2 |

### Example 10

**Condition:** `run AND _step = 3`

| Role | Variables |
|---|---|
| CONTROL | _step |
| PERMISSIVE | run |
| CONTEXT | — |

*... and 9 more examples*

---

## Implementation_datasets/TOOL_CHANGER.st

### Example 1

**Condition:** `ToolChangeRequired`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | ToolChangeRequired |
| CONTEXT | — |

### Example 2

**Condition:** `ToolCarouselPosition <> DesiredToolNumber`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | ToolCarouselPosition |
| CONTEXT | DesiredToolNumber |

### Example 3

**Condition:** `ToolCarouselPosition = DesiredToolNumber`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | ToolCarouselPosition |
| CONTEXT | DesiredToolNumber |

---

## Implementation_datasets/TRAFFIC_CTRL.st

### Example 1

**Condition:** `PedestrianButton1`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | PedestrianButton1 |
| CONTEXT | — |

### Example 2

**Condition:** `PedestrianButton2`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | PedestrianButton2 |
| CONTEXT | — |

### Example 3

**Condition:** `PedestrianRequest1 OR PedestrianRequest2`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | PedestrianRequest1, PedestrianRequest2 |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `PedestrianRequest1`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | PedestrianRequest1 |
| CONTEXT | — |

### Example 7

**Condition:** `PedestrianRequest2`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | PedestrianRequest2 |
| CONTEXT | — |

### Example 8

**Condition:** `PedestrianCrossing`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | PedestrianCrossing |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

---

## Implementation_datasets/robotic_sequence.st

### Example 1

**Condition:** `T1_Cnt > 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T1_Cnt |
| CONTEXT | — |

### Example 2

**Condition:** `T2_Cnt > 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T2_Cnt |
| CONTEXT | — |

### Example 3

**Condition:** `Si1 = FALSE OR Xi1 = FALSE OR Xi6 = FALSE OR Xi7 = FALSE OR Xi8 = FALSE OR Xi9 = FALSE OR Ri5 = TRUE OR Zi4 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si1, Xi1, Xi6, Xi7, Xi8, Xi9, Ri5, Zi4 |
| CONTEXT | — |

### Example 4

**Condition:** `Si4 = TRUE AND Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE AND Zi1 = TRUE AND Ri1 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si4, Xi1, Xi6, Xi7, Xi8, Xi9, Zi1, Ri1 |
| CONTEXT | — |

### Example 5

**Condition:** `Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Xi1, Xi6, Xi7, Xi8, Xi9 |
| CONTEXT | — |

### Example 6

**Condition:** `Si2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si2 |
| CONTEXT | — |

### Example 7

**Condition:** `Ri2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Ri2 |
| CONTEXT | — |

### Example 8

**Condition:** `T1_Cnt = 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T1_Cnt |
| CONTEXT | — |

### Example 9

**Condition:** `Xi10 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Xi10 |
| CONTEXT | — |

### Example 10

**Condition:** `Ri2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Ri2 |
| CONTEXT | — |

*... and 6 more examples*

---

## Implementation_datasets/sampletext_2.st

### Example 1

**Condition:** `T1_Cnt > 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T1_Cnt |
| CONTEXT | — |

### Example 2

**Condition:** `T2_Cnt > 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T2_Cnt |
| CONTEXT | — |

### Example 3

**Condition:** `Si1 = FALSE OR Xi1 = FALSE OR Xi6 = FALSE OR Xi7 = FALSE OR Xi8 = FALSE OR Xi9 = FALSE OR Ri5 = TRUE OR Zi4 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si1, Xi1, Xi6, Xi7, Xi8, Xi9, Ri5, Zi4 |
| CONTEXT | — |

### Example 4

**Condition:** `Si4 = TRUE AND Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE AND Zi1 = TRUE AND Ri1 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si4, Xi1, Xi6, Xi7, Xi8, Xi9, Zi1, Ri1 |
| CONTEXT | — |

### Example 5

**Condition:** `Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Xi1, Xi6, Xi7, Xi8, Xi9 |
| CONTEXT | — |

### Example 6

**Condition:** `Si2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si2 |
| CONTEXT | — |

### Example 7

**Condition:** `Ri2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Ri2 |
| CONTEXT | — |

### Example 8

**Condition:** `T1_Cnt = 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T1_Cnt |
| CONTEXT | — |

### Example 9

**Condition:** `Xi10 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Xi10 |
| CONTEXT | — |

### Example 10

**Condition:** `Ri2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Ri2 |
| CONTEXT | — |

*... and 6 more examples*

---

## Implementation_datasets/sampletext_3.st

### Example 1

**Condition:** `T1_Cnt > 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T1_Cnt |
| CONTEXT | — |

### Example 2

**Condition:** `T2_Cnt > 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T2_Cnt |
| CONTEXT | — |

### Example 3

**Condition:** `Si1 = FALSE OR Xi1 = FALSE OR Xi6 = FALSE OR Xi7 = FALSE OR Xi8 = FALSE OR Xi9 = FALSE OR Ri5 = TRUE OR Zi4 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si1, Xi1, Xi6, Xi7, Xi8, Xi9, Ri5, Zi4 |
| CONTEXT | — |

### Example 4

**Condition:** `Si4 = TRUE AND Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE AND Zi1 = TRUE AND Ri1 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si4, Xi1, Xi6, Xi7, Xi8, Xi9, Zi1, Ri1 |
| CONTEXT | — |

### Example 5

**Condition:** `Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Xi1, Xi6, Xi7, Xi8, Xi9 |
| CONTEXT | — |

### Example 6

**Condition:** `Si2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Si2 |
| CONTEXT | — |

### Example 7

**Condition:** `Ri2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Ri2 |
| CONTEXT | — |

### Example 8

**Condition:** `T1_Cnt = 0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | T1_Cnt |
| CONTEXT | — |

### Example 9

**Condition:** `Xi10 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Xi10 |
| CONTEXT | — |

### Example 10

**Condition:** `Ri2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Ri2 |
| CONTEXT | — |

*... and 6 more examples*

---

## Implementation_datasets/sampletext_4.st

No IF conditions found.
---

## test_harness/Full_test/CRC_GEN_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 23 more examples*

---

## test_harness/Full_test/CRC_GEN_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 24 more examples*

---

## test_harness/Full_test/DEC_TO_HEX_FullTest.st

ERROR: Expected end of text, found 'FUNCTION'  (at char 6740), (line:340, col:1)
---

## test_harness/Full_test/FLOW_METER_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 39 more examples*

---

## test_harness/Full_test/FLOW_METER_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 34 more examples*

---

## test_harness/Full_test/FT_PIDWL_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 23 more examples*

---

## test_harness/Full_test/FT_PIDWL_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 27 more examples*

---

## test_harness/Full_test/GEN_BIT_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 27 more examples*

---

## test_harness/Full_test/GEN_SIN_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 29 more examples*

---

## test_harness/Full_test/GEN_SIN_FullTest (2).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 29 more examples*

---

## test_harness/Full_test/GEN_SIN_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 33 more examples*

---

## test_harness/Full_test/LAMBERT_W_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 81 more examples*

---

## test_harness/Full_test/LAMBERT_W_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 56 more examples*

---

## test_harness/Full_test/MATRIX_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 21 more examples*

---

## test_harness/Full_test/MATRIX_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 27 more examples*

---

## test_harness/Full_test/SEQUENCE_8_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 33 more examples*

---

## test_harness/Full_test/SEQUENCE_8_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 33 more examples*

---

## test_harness/Full_test/TOOL_CHANGER_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 34 more examples*

---

## test_harness/Full_test/TOOL_CHANGER_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 32 more examples*

---

## test_harness/Full_test/TRAFFIC_CTRL_FullTest (1).st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 28 more examples*

---

## test_harness/Full_test/TRAFFIC_CTRL_FullTest.st

### Example 1

**Condition:** `FunctionInvocationNode(name='INT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR |
| CONTEXT | X |

### Example 2

**Condition:** `FunctionInvocationNode(name='DINT_TO_REAL', arguments=[InvocationArgumentNode(name='', value=VariableNode(name='FLOOR2'))]) > X`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | FLOOR2 |
| CONTEXT | X |

### Example 3

**Condition:** `divi = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | divi |
| CONTEXT | — |

### Example 4

**Condition:** `VAL`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | VAL |
| CONTEXT | — |

### Example 5

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 6

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 7

**Condition:** `debug`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | debug |
| CONTEXT | — |

### Example 8

**Condition:** `NOT init`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init |
| CONTEXT | — |

### Example 9

**Condition:** `NOT init OR RST`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | init, RST |
| CONTEXT | — |

### Example 10

**Condition:** `Y >= LIM_H`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Y |
| CONTEXT | LIM_H |

*... and 34 more examples*

---

## test_harness/test_case/CRC_GEN_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock._CRC_GEN = 7`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `NOT TestBlock._CRC_GEN = 8`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

### Example 6

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `NOT TestBlock._CRC_GEN = 9`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `NOT TestBlock._CRC_GEN = 10`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

*... and 5 more examples*

---

## test_harness/test_case/CRC_GEN_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock._CRC_GEN = FunctionInvocationNode(name='STRING_TO_DWORD', arguments=[InvocationArgumentNode(name='', value=StringLiteralNode(value="'0x6FC1025C'"))])`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock._CRC_GEN = FunctionInvocationNode(name='STRING_TO_DWORD', arguments=[InvocationArgumentNode(name='', value=StringLiteralNode(value="'0x0'"))])`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock._CRC_GEN = FunctionInvocationNode(name='STRING_TO_DWORD', arguments=[InvocationArgumentNode(name='', value=StringLiteralNode(value="'0x6FC1025C'"))])`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock._CRC_GEN |
| CONTEXT | — |

### Example 10

**Condition:** `NOT Test_0.Finished AND NOT Test_0.FAILED`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_0.Finished, Test_0.FAILED |
| CONTEXT | — |

*... and 6 more examples*

---

## test_harness/test_case/DEC_TO_HEX_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.HexString = StringLiteralNode(value="'0'")`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.HexString |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.HexString = StringLiteralNode(value="'1'")`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.HexString |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.HexString = StringLiteralNode(value="'A'")`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.HexString |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 81 more examples*

---

## test_harness/test_case/FLOW_METER_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.F = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.F |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.F = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.F |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.F = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.F |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 21 more examples*

---

## test_harness/test_case/FLOW_METER_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.F = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.F |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.F = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.F |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.F = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.F |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 16 more examples*

---

## test_harness/test_case/FT_PIDWL_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Y = 0.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `NOT TestBlock.Y = 1.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

### Example 6

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 7

**Condition:** `NOT TestBlock.Y = 2.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `NOT TestBlock.Y = 0.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

*... and 7 more examples*

---

## test_harness/test_case/FT_PIDWL_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Y = 0.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.Y = 2.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.Y = 2.0 AND TestBlock.LIM = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Y, TestBlock.LIM |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 11 more examples*

---

## test_harness/test_case/GEN_BIT_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Q0 = FALSE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.CNT = 0 AND TestBlock.RUN = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.CNT, TestBlock.RUN |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.Q0 = FALSE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.CNT = 0 AND TestBlock.RUN = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.CNT, TestBlock.RUN |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.Q0 = FALSE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.CNT = 0 AND TestBlock.RUN = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.CNT, TestBlock.RUN |
| CONTEXT | — |

### Example 10

**Condition:** `NOT Test_0.Finished AND NOT Test_0.FAILED`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_0.Finished, Test_0.FAILED |
| CONTEXT | — |

*... and 6 more examples*

---

## test_harness/test_case/GEN_SIN_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Q = TRUE AND TestBlock.OUT = 1.5`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `NOT TestBlock.Q = FALSE AND TestBlock.OUT = 0.9`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

### Example 6

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `NOT TestBlock.Q = TRUE AND TestBlock.OUT = 1.5`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `NOT TestBlock.Q = FALSE AND TestBlock.OUT = 0.7`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

*... and 12 more examples*

---

## test_harness/test_case/GEN_SIN_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Q = FALSE AND TestBlock.OUT = 1.7071067811865475`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.Q = TRUE AND TestBlock.OUT = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.Q = FALSE AND TestBlock.OUT = 2.0606601717798214`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q, TestBlock.OUT |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 16 more examples*

---

## test_harness/test_case/LAMBERT_W_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.OUT = -1000.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.OUT |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.OUT = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.OUT |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.OUT = 0.35173371124919584`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.OUT |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 66 more examples*

---

## test_harness/test_case/LAMBERT_W_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.OUT = -1000.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.OUT |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.OUT = 0.0`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.OUT |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.OUT = 4.31748811353631`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.OUT |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 41 more examples*

---

## test_harness/test_case/MATRIX_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.CODE = 0 AND TestBlock._TP = FALSE AND TestBlock.Y1 = TRUE AND TestBlock.Y2 = FALSE AND TestBlock.Y3 = FALSE AND TestBlock.Y4 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `NOT TestBlock.CODE = 0 AND TestBlock._TP = FALSE AND TestBlock.Y1 = TRUE AND TestBlock.Y2 = TRUE AND TestBlock.Y3 = TRUE AND TestBlock.Y4 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

### Example 6

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `NOT TestBlock.CODE = 0 AND TestBlock._TP = FALSE AND TestBlock.Y1 = TRUE AND TestBlock.Y2 = FALSE AND TestBlock.Y3 = FALSE AND TestBlock.Y4 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `NOT TestBlock.CODE = 0 AND TestBlock._TP = FALSE AND TestBlock.Y1 = TRUE AND TestBlock.Y2 = FALSE AND TestBlock.Y3 = TRUE AND TestBlock.Y4 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

*... and 5 more examples*

---

## test_harness/test_case/MATRIX_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.CODE = 1 AND TestBlock._TP = FALSE AND TestBlock.Y1 = TRUE AND TestBlock.Y2 = FALSE AND TestBlock.Y3 = TRUE AND TestBlock.Y4 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.CODE = 2 AND TestBlock._TP = TRUE AND TestBlock.Y1 = FALSE AND TestBlock.Y2 = TRUE AND TestBlock.Y3 = FALSE AND TestBlock.Y4 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.CODE = 3 AND TestBlock._TP = FALSE AND TestBlock.Y1 = TRUE AND TestBlock.Y2 = TRUE AND TestBlock.Y3 = TRUE AND TestBlock.Y4 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.CODE, TestBlock._TP, TestBlock.Y1, TestBlock.Y2, TestBlock.Y3, TestBlock.Y4 |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 11 more examples*

---

## test_harness/test_case/SEQUENCE_8_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Q0 = FALSE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.Q4 = FALSE AND TestBlock.Q5 = FALSE AND TestBlock.Q6 = FALSE AND TestBlock.Q7 = FALSE AND TestBlock.QX = FALSE AND TestBlock.RUN = FALSE AND TestBlock._STEP = -1 AND TestBlock.STATUS = 110`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.Q4, TestBlock.Q5, TestBlock.Q6, TestBlock.Q7, TestBlock.QX, TestBlock.RUN, TestBlock._STEP, TestBlock.STATUS |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.Q0 = TRUE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.Q4 = FALSE AND TestBlock.Q5 = FALSE AND TestBlock.Q6 = FALSE AND TestBlock.Q7 = FALSE AND TestBlock.QX = TRUE AND TestBlock.RUN = TRUE AND TestBlock._STEP = 0 AND TestBlock.STATUS = 111`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.Q4, TestBlock.Q5, TestBlock.Q6, TestBlock.Q7, TestBlock.QX, TestBlock.RUN, TestBlock._STEP, TestBlock.STATUS |
| CONTEXT | — |

### Example 7

**Condition:** `NOT Test_0.Finished AND NOT Test_0.FAILED`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_0.Finished, Test_0.FAILED |
| CONTEXT | — |

### Example 8

**Condition:** `Test_0.Finished`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_0.Finished |
| CONTEXT | — |

### Example 9

**Condition:** `NOT Test_1.Finished AND NOT Test_1.FAILED`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_1.Finished, Test_1.FAILED |
| CONTEXT | — |

### Example 10

**Condition:** `Test_1.Finished`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_1.Finished |
| CONTEXT | — |

*... and 1 more examples*

---

## test_harness/test_case/SEQUENCE_8_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.Q0 = FALSE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.Q4 = FALSE AND TestBlock.Q5 = FALSE AND TestBlock.Q6 = FALSE AND TestBlock.Q7 = FALSE AND TestBlock.QX = FALSE AND TestBlock.RUN = FALSE AND TestBlock._STEP = -1 AND TestBlock.STATUS = 110`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.Q4, TestBlock.Q5, TestBlock.Q6, TestBlock.Q7, TestBlock.QX, TestBlock.RUN, TestBlock._STEP, TestBlock.STATUS |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.Q0 = FALSE AND TestBlock.Q1 = FALSE AND TestBlock.Q2 = FALSE AND TestBlock.Q3 = FALSE AND TestBlock.Q4 = FALSE AND TestBlock.Q5 = FALSE AND TestBlock.Q6 = FALSE AND TestBlock.Q7 = FALSE AND TestBlock.QX = FALSE AND TestBlock.RUN = FALSE AND TestBlock._STEP = -1 AND TestBlock.STATUS = 110`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.Q0, TestBlock.Q1, TestBlock.Q2, TestBlock.Q3, TestBlock.Q4, TestBlock.Q5, TestBlock.Q6, TestBlock.Q7, TestBlock.QX, TestBlock.RUN, TestBlock._STEP, TestBlock.STATUS |
| CONTEXT | — |

### Example 7

**Condition:** `NOT Test_0.Finished AND NOT Test_0.FAILED`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_0.Finished, Test_0.FAILED |
| CONTEXT | — |

### Example 8

**Condition:** `Test_0.Finished`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_0.Finished |
| CONTEXT | — |

### Example 9

**Condition:** `NOT Test_1.Finished AND NOT Test_1.FAILED`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_1.Finished, Test_1.FAILED |
| CONTEXT | — |

### Example 10

**Condition:** `Test_1.Finished`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | Test_1.Finished |
| CONTEXT | — |

*... and 1 more examples*

---

## test_harness/test_case/TOOL_CHANGER_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.RotateCarousel = TRUE AND TestBlock.LockTool = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `NOT TestBlock.RotateCarousel = FALSE AND TestBlock.LockTool = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

### Example 6

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 7

**Condition:** `NOT TestBlock.RotateCarousel = FALSE AND TestBlock.LockTool = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `NOT TestBlock.RotateCarousel = FALSE AND TestBlock.LockTool = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

*... and 18 more examples*

---

## test_harness/test_case/TOOL_CHANGER_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.RotateCarousel = TRUE AND TestBlock.LockTool = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.RotateCarousel = FALSE AND TestBlock.LockTool = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.RotateCarousel = TRUE AND TestBlock.LockTool = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.RotateCarousel, TestBlock.LockTool |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 16 more examples*

---

## test_harness/test_case/TRAFFIC_CTRL_TestCases (1).st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.NorthSouthRed = FALSE AND TestBlock.NorthSouthYellow = FALSE AND TestBlock.NorthSouthGreen = TRUE AND TestBlock.EastWestRed = TRUE AND TestBlock.EastWestYellow = FALSE AND TestBlock.EastWestGreen = FALSE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `NOT TestBlock.NorthSouthRed = FALSE AND TestBlock.NorthSouthYellow = TRUE AND TestBlock.NorthSouthGreen = FALSE AND TestBlock.EastWestRed = TRUE AND TestBlock.EastWestYellow = FALSE AND TestBlock.EastWestGreen = FALSE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

### Example 6

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `NOT TestBlock.NorthSouthRed = TRUE AND TestBlock.NorthSouthYellow = FALSE AND TestBlock.NorthSouthGreen = FALSE AND TestBlock.EastWestRed = FALSE AND TestBlock.EastWestYellow = FALSE AND TestBlock.EastWestGreen = TRUE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

### Example 9

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 10

**Condition:** `NOT TestBlock.NorthSouthRed = TRUE AND TestBlock.NorthSouthYellow = FALSE AND TestBlock.NorthSouthGreen = FALSE AND TestBlock.EastWestRed = FALSE AND TestBlock.EastWestYellow = TRUE AND TestBlock.EastWestGreen = FALSE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

*... and 5 more examples*

---

## test_harness/test_case/TRAFFIC_CTRL_TestCases.st

### Example 1

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 2

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 3

**Condition:** `NOT TestBlock.NorthSouthRed = FALSE AND TestBlock.NorthSouthYellow = FALSE AND TestBlock.NorthSouthGreen = TRUE AND TestBlock.EastWestRed = TRUE AND TestBlock.EastWestYellow = FALSE AND TestBlock.EastWestGreen = FALSE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

### Example 4

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 5

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 6

**Condition:** `NOT TestBlock.NorthSouthRed = FALSE AND TestBlock.NorthSouthYellow = TRUE AND TestBlock.NorthSouthGreen = FALSE AND TestBlock.EastWestRed = TRUE AND TestBlock.EastWestYellow = FALSE AND TestBlock.EastWestGreen = FALSE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = FALSE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

### Example 7

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 8

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

### Example 9

**Condition:** `NOT TestBlock.NorthSouthRed = TRUE AND TestBlock.NorthSouthYellow = FALSE AND TestBlock.NorthSouthGreen = FALSE AND TestBlock.EastWestRed = TRUE AND TestBlock.EastWestYellow = FALSE AND TestBlock.EastWestGreen = TRUE AND TestBlock.PedestrianLight1 = FALSE AND TestBlock.PedestrianLight2 = TRUE`

| Role | Variables |
|---|---|
| CONTROL | — |
| PERMISSIVE | TestBlock.NorthSouthRed, TestBlock.NorthSouthYellow, TestBlock.NorthSouthGreen, TestBlock.EastWestRed, TestBlock.EastWestYellow, TestBlock.EastWestGreen, TestBlock.PedestrianLight1, TestBlock.PedestrianLight2 |
| CONTEXT | — |

### Example 10

**Condition:** `Timer.Q`

| Role | Variables |
|---|---|
| CONTROL | Timer.Q |
| PERMISSIVE | — |
| CONTEXT | — |

*... and 11 more examples*

---

## Summary

| Dataset | IF Conditions | CONTROL Vars | PERMISSIVE Vars | CONTEXT Vars |
|---|---|---|---|---|
| Implementation_datasets/CRC_GEN.st | 5 | 0 | 5 | 0 |
| Implementation_datasets/DEC_TO_HEX.st | ERROR | 0 | 0 | 0 |
| Implementation_datasets/FLOW_METER.st | 5 | 0 | 4 | 4 |
| Implementation_datasets/FT_PIDWL.st | 3 | 0 | 3 | 1 |
| Implementation_datasets/GEN_BIT.st | 8 | 0 | 11 | 4 |
| Implementation_datasets/GEN_SIN.st | 4 | 0 | 4 | 1 |
| Implementation_datasets/INCLUDE.st | 13 | 0 | 14 | 3 |
| Implementation_datasets/LAMBERT_W.st | 2 | 0 | 2 | 1 |
| Implementation_datasets/MATRIX.st | 3 | 0 | 3 | 0 |
| Implementation_datasets/SEQUENCE_8.st | 19 | 8 | 28 | 24 |
| Implementation_datasets/TOOL_CHANGER.st | 3 | 0 | 3 | 2 |
| Implementation_datasets/TRAFFIC_CTRL.st | 10 | 4 | 7 | 0 |
| Implementation_datasets/robotic_sequence.st | 16 | 0 | 37 | 0 |
| Implementation_datasets/sampletext_2.st | 16 | 0 | 37 | 0 |
| Implementation_datasets/sampletext_3.st | 16 | 0 | 37 | 0 |
| Implementation_datasets/sampletext_4.st | 0 | 0 | 0 | 0 |
| test_harness/Full_test/CRC_GEN_FullTest (1).st | 33 | 6 | 29 | 3 |
| test_harness/Full_test/CRC_GEN_FullTest.st | 34 | 6 | 31 | 3 |
| test_harness/Full_test/DEC_TO_HEX_FullTest.st | ERROR | 0 | 0 | 0 |
| test_harness/Full_test/FLOW_METER_FullTest (1).st | 49 | 12 | 42 | 7 |
| test_harness/Full_test/FLOW_METER_FullTest.st | 44 | 10 | 38 | 7 |
| test_harness/Full_test/FT_PIDWL_FullTest (1).st | 33 | 7 | 33 | 4 |
| test_harness/Full_test/FT_PIDWL_FullTest.st | 37 | 8 | 37 | 4 |
| test_harness/Full_test/GEN_BIT_FullTest.st | 37 | 6 | 52 | 7 |
| test_harness/Full_test/GEN_SIN_FullTest (1).st | 39 | 9 | 39 | 4 |
| test_harness/Full_test/GEN_SIN_FullTest (2).st | 39 | 9 | 39 | 4 |
| test_harness/Full_test/GEN_SIN_FullTest.st | 43 | 10 | 43 | 4 |
| test_harness/Full_test/LAMBERT_W_FullTest (1).st | 91 | 30 | 76 | 4 |
| test_harness/Full_test/LAMBERT_W_FullTest.st | 66 | 20 | 56 | 4 |
| test_harness/Full_test/MATRIX_FullTest (1).st | 31 | 6 | 47 | 3 |
| test_harness/Full_test/MATRIX_FullTest.st | 37 | 8 | 53 | 3 |
| test_harness/Full_test/SEQUENCE_8_FullTest (1).st | 43 | 12 | 72 | 27 |
| test_harness/Full_test/SEQUENCE_8_FullTest.st | 43 | 12 | 72 | 27 |
| test_harness/Full_test/TOOL_CHANGER_FullTest (1).st | 44 | 12 | 44 | 5 |
| test_harness/Full_test/TOOL_CHANGER_FullTest.st | 42 | 10 | 42 | 5 |
| test_harness/Full_test/TRAFFIC_CTRL_FullTest (1).st | 38 | 10 | 59 | 3 |
| test_harness/Full_test/TRAFFIC_CTRL_FullTest.st | 44 | 12 | 65 | 3 |
| test_harness/test_case/CRC_GEN_TestCases (1).st | 15 | 6 | 10 | 0 |
| test_harness/test_case/CRC_GEN_TestCases.st | 16 | 6 | 12 | 0 |
| test_harness/test_case/DEC_TO_HEX_TestCases.st | 91 | 36 | 72 | 0 |
| test_harness/test_case/FLOW_METER_TestCases (1).st | 31 | 12 | 24 | 0 |
| test_harness/test_case/FLOW_METER_TestCases.st | 26 | 10 | 20 | 0 |
| test_harness/test_case/FT_PIDWL_TestCases (1).st | 17 | 7 | 16 | 0 |
| test_harness/test_case/FT_PIDWL_TestCases.st | 21 | 8 | 20 | 0 |
| test_harness/test_case/GEN_BIT_TestCases.st | 16 | 6 | 27 | 0 |
| test_harness/test_case/GEN_SIN_TestCases (1).st | 22 | 9 | 21 | 0 |
| test_harness/test_case/GEN_SIN_TestCases.st | 26 | 10 | 25 | 0 |
| test_harness/test_case/LAMBERT_W_TestCases (1).st | 76 | 30 | 60 | 0 |
| test_harness/test_case/LAMBERT_W_TestCases.st | 51 | 20 | 40 | 0 |
| test_harness/test_case/MATRIX_TestCases (1).st | 15 | 6 | 30 | 0 |
| test_harness/test_case/MATRIX_TestCases.st | 21 | 8 | 36 | 0 |
| test_harness/test_case/SEQUENCE_8_TestCases (1).st | 11 | 4 | 30 | 0 |
| test_harness/test_case/SEQUENCE_8_TestCases.st | 11 | 4 | 30 | 0 |
| test_harness/test_case/TOOL_CHANGER_TestCases (1).st | 28 | 12 | 27 | 0 |
| test_harness/test_case/TOOL_CHANGER_TestCases.st | 26 | 10 | 25 | 0 |
| test_harness/test_case/TRAFFIC_CTRL_TestCases (1).st | 15 | 6 | 38 | 0 |
| test_harness/test_case/TRAFFIC_CTRL_TestCases.st | 21 | 8 | 44 | 0 |


### Grand Totals

| Metric | Count |
|---|---|
| Total IF Conditions | 1546 |
| Total CONTROL Variables | 445 |
| Total PERMISSIVE Variables | 1771 |
| Total CONTEXT Variables | 171 |
