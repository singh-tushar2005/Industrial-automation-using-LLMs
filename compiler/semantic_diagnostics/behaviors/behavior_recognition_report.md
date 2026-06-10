# Behavior Recognition Report

## Overview

- **Files total**: 57
- **Files parsed**: 55

## Detected Behaviors

- **MATHEMATICAL_SOLVER**: 7 file(s)
- **SEQUENTIAL_MACHINE_CONTROL**: 6 file(s)
- **STATE_MACHINE_CONTROL**: 6 file(s)
- **COUNTER_PROCESSING**: 5 file(s)
- **CHECKSUM_GENERATION**: 3 file(s)
- **FLOW_MEASUREMENT**: 3 file(s)
- **MATRIX_COMPUTATION**: 3 file(s)

## Per-File Behavior Details

### CRC_GEN.st

**Detected behaviors:**
- `CHECKSUM_GENERATION` — confidence: **medium**
  - Evidence:
    - `bitwise_operation=20`
    - `accumulator=9`
    - `xor_accumulator=yes`
  - Operations:
    - `bitwise_update=2`
    - `accumulator_update=10`

### DEC_TO_HEX.st

- Parse: **FAILED**

### FLOW_METER.st

**Detected behaviors:**
- `FLOW_MEASUREMENT` — confidence: **high**
  - Evidence:
    - `measurement_calculation=1`
    - `history_variable=7`
    - `counter=0`
  - Operations:
    - `process_calculation=2`

### FT_PIDWL.st

**No behaviors detected.**

### GEN_BIT.st

**Detected behaviors:**
- `COUNTER_PROCESSING` — confidence: **high**
  - Evidence:
    - `counter=3`
  - Operations:
    - `counter_update=3`
    - `counter_invocation=0`

### GEN_SIN.st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **medium**
  - Evidence:
    - `process_calculation=5`
  - Operations:
    - `mathematical_solver=3`
    - `iterative_computation=0`
    - `process_calculation=5`

### INCLUDE.st

**No behaviors detected.**

### LAMBERT_W.st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **high**
  - Evidence:
    - `process_calculation=8`
  - Operations:
    - `mathematical_solver=5`
    - `iterative_computation=1`
    - `process_calculation=4`

### MATRIX.st

**Detected behaviors:**
- `MATRIX_COMPUTATION` — confidence: **medium**
  - Evidence:
    - `matrix_access=0`
    - `array_access=14`
    - `bitwise_operation=59`
  - Operations:
    - `array_read=3`
    - `array_write=2`
    - `bitwise_update=14`

### SEQUENCE_8.st

**Detected behaviors:**
- `SEQUENTIAL_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=10`
    - `timer=0`
    - `counter=0`
    - `history_variable=17`
  - Operations:
    - `state_transition=1`
    - `timer_invocation=0`
  - Relationships:
    - `sequences=16`
    - `transitions_to=9`

### TOOL_CHANGER.st

**Detected behaviors:**
- `STATE_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=4`
    - `state_variable=0`
    - `timer=0`
  - Operations:
    - `state_transition=4`
    - `timer_invocation=0`
  - Relationships:
    - `transitions_to=6`
    - `sequences=6`

### TRAFFIC_CTRL.st

**Detected behaviors:**
- `STATE_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=4`
    - `state_variable=0`
    - `timer=8`
  - Operations:
    - `state_transition=4`
    - `timer_invocation=8`
  - Relationships:
    - `transitions_to=8`
    - `sequences=17`

### robotic_sequence.st

**Detected behaviors:**
- `SEQUENTIAL_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=13`
    - `timer=0`
    - `counter=9`
    - `history_variable=0`
  - Operations:
    - `state_transition=13`
    - `timer_invocation=0`
  - Relationships:
    - `sequences=38`
    - `transitions_to=24`
- `COUNTER_PROCESSING` — confidence: **high**
  - Evidence:
    - `counter=9`
  - Operations:
    - `counter_update=9`
    - `counter_invocation=0`

### sampletext_2.st

**Detected behaviors:**
- `SEQUENTIAL_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=13`
    - `timer=0`
    - `counter=9`
    - `history_variable=0`
  - Operations:
    - `state_transition=13`
    - `timer_invocation=0`
  - Relationships:
    - `sequences=38`
    - `transitions_to=24`
- `COUNTER_PROCESSING` — confidence: **high**
  - Evidence:
    - `counter=9`
  - Operations:
    - `counter_update=9`
    - `counter_invocation=0`

### sampletext_3.st

**Detected behaviors:**
- `SEQUENTIAL_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=13`
    - `timer=0`
    - `counter=9`
    - `history_variable=0`
  - Operations:
    - `state_transition=13`
    - `timer_invocation=0`
  - Relationships:
    - `sequences=38`
    - `transitions_to=24`
- `COUNTER_PROCESSING` — confidence: **high**
  - Evidence:
    - `counter=9`
  - Operations:
    - `counter_update=9`
    - `counter_invocation=0`

### sampletext_4.st

**No behaviors detected.**

### CRC_GEN_FullTest (1).st

**Detected behaviors:**
- `CHECKSUM_GENERATION` — confidence: **high**
  - Evidence:
    - `bitwise_operation=44`
    - `accumulator=18`
    - `xor_accumulator=yes`
  - Operations:
    - `bitwise_update=6`
    - `accumulator_update=18`

### CRC_GEN_FullTest.st

**Detected behaviors:**
- `CHECKSUM_GENERATION` — confidence: **high**
  - Evidence:
    - `bitwise_operation=44`
    - `accumulator=18`
    - `xor_accumulator=yes`
  - Operations:
    - `bitwise_update=6`
    - `accumulator_update=18`

### DEC_TO_HEX_FullTest.st

- Parse: **FAILED**

### FLOW_METER_FullTest (1).st

**Detected behaviors:**
- `FLOW_MEASUREMENT` — confidence: **high**
  - Evidence:
    - `measurement_calculation=1`
    - `history_variable=17`
    - `counter=0`
  - Operations:
    - `process_calculation=11`

### FLOW_METER_FullTest.st

**Detected behaviors:**
- `FLOW_MEASUREMENT` — confidence: **high**
  - Evidence:
    - `measurement_calculation=1`
    - `history_variable=17`
    - `counter=0`
  - Operations:
    - `process_calculation=11`

### FT_PIDWL_FullTest (1).st

**No behaviors detected.**

### FT_PIDWL_FullTest.st

**No behaviors detected.**

### GEN_BIT_FullTest.st

**Detected behaviors:**
- `COUNTER_PROCESSING` — confidence: **high**
  - Evidence:
    - `counter=3`
  - Operations:
    - `counter_update=3`
    - `counter_invocation=0`

### GEN_SIN_FullTest (1).st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **high**
  - Evidence:
    - `process_calculation=5`
  - Operations:
    - `mathematical_solver=3`
    - `iterative_computation=1`
    - `process_calculation=12`

### GEN_SIN_FullTest (2).st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **high**
  - Evidence:
    - `process_calculation=5`
  - Operations:
    - `mathematical_solver=3`
    - `iterative_computation=1`
    - `process_calculation=12`

### GEN_SIN_FullTest.st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **high**
  - Evidence:
    - `process_calculation=5`
  - Operations:
    - `mathematical_solver=3`
    - `iterative_computation=1`
    - `process_calculation=12`

### LAMBERT_W_FullTest (1).st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **high**
  - Evidence:
    - `process_calculation=8`
  - Operations:
    - `mathematical_solver=5`
    - `iterative_computation=2`
    - `process_calculation=10`

### LAMBERT_W_FullTest.st

**Detected behaviors:**
- `MATHEMATICAL_SOLVER` — confidence: **high**
  - Evidence:
    - `process_calculation=8`
  - Operations:
    - `mathematical_solver=5`
    - `iterative_computation=2`
    - `process_calculation=10`

### MATRIX_FullTest (1).st

**Detected behaviors:**
- `MATRIX_COMPUTATION` — confidence: **medium**
  - Evidence:
    - `matrix_access=0`
    - `array_access=14`
    - `bitwise_operation=83`
  - Operations:
    - `array_read=3`
    - `array_write=2`
    - `bitwise_update=18`

### MATRIX_FullTest.st

**Detected behaviors:**
- `MATRIX_COMPUTATION` — confidence: **medium**
  - Evidence:
    - `matrix_access=0`
    - `array_access=14`
    - `bitwise_operation=83`
  - Operations:
    - `array_read=3`
    - `array_write=2`
    - `bitwise_update=18`

### SEQUENCE_8_FullTest (1).st

**Detected behaviors:**
- `SEQUENTIAL_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=10`
    - `timer=0`
    - `counter=0`
    - `history_variable=27`
  - Operations:
    - `state_transition=1`
    - `timer_invocation=0`
  - Relationships:
    - `sequences=19`
    - `transitions_to=10`

### SEQUENCE_8_FullTest.st

**Detected behaviors:**
- `SEQUENTIAL_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=10`
    - `timer=0`
    - `counter=0`
    - `history_variable=27`
  - Operations:
    - `state_transition=1`
    - `timer_invocation=0`
  - Relationships:
    - `sequences=19`
    - `transitions_to=10`

### TOOL_CHANGER_FullTest (1).st

**Detected behaviors:**
- `STATE_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=4`
    - `state_variable=0`
    - `timer=0`
  - Operations:
    - `state_transition=4`
    - `timer_invocation=0`
  - Relationships:
    - `transitions_to=7`
    - `sequences=11`

### TOOL_CHANGER_FullTest.st

**Detected behaviors:**
- `STATE_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=4`
    - `state_variable=0`
    - `timer=0`
  - Operations:
    - `state_transition=4`
    - `timer_invocation=0`
  - Relationships:
    - `transitions_to=7`
    - `sequences=9`

### TRAFFIC_CTRL_FullTest (1).st

**Detected behaviors:**
- `STATE_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=4`
    - `state_variable=0`
    - `timer=8`
  - Operations:
    - `state_transition=4`
    - `timer_invocation=8`
  - Relationships:
    - `transitions_to=9`
    - `sequences=21`

### TRAFFIC_CTRL_FullTest.st

**Detected behaviors:**
- `STATE_MACHINE_CONTROL` — confidence: **high**
  - Evidence:
    - `state_transition=4`
    - `state_variable=0`
    - `timer=8`
  - Operations:
    - `state_transition=4`
    - `timer_invocation=8`
  - Relationships:
    - `transitions_to=9`
    - `sequences=20`

### CRC_GEN_TestCases (1).st

**No behaviors detected.**

### CRC_GEN_TestCases.st

**No behaviors detected.**

### DEC_TO_HEX_TestCases.st

**No behaviors detected.**

### FLOW_METER_TestCases (1).st

**No behaviors detected.**

### FLOW_METER_TestCases.st

**No behaviors detected.**

### FT_PIDWL_TestCases (1).st

**No behaviors detected.**

### FT_PIDWL_TestCases.st

**No behaviors detected.**

### GEN_BIT_TestCases.st

**No behaviors detected.**

### GEN_SIN_TestCases (1).st

**No behaviors detected.**

### GEN_SIN_TestCases.st

**No behaviors detected.**

### LAMBERT_W_TestCases (1).st

**No behaviors detected.**

### LAMBERT_W_TestCases.st

**No behaviors detected.**

### MATRIX_TestCases (1).st

**No behaviors detected.**

### MATRIX_TestCases.st

**No behaviors detected.**

### SEQUENCE_8_TestCases (1).st

**No behaviors detected.**

### SEQUENCE_8_TestCases.st

**No behaviors detected.**

### TOOL_CHANGER_TestCases (1).st

**No behaviors detected.**

### TOOL_CHANGER_TestCases.st

**No behaviors detected.**

### TRAFFIC_CTRL_TestCases (1).st

**No behaviors detected.**

### TRAFFIC_CTRL_TestCases.st

**No behaviors detected.**


---

*Generated by behavior validation pipeline.*
