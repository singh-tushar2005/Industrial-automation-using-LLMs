# Intent Reasoning Report

Intent reasoning is derived from semantic evidence, operations, relationships, and behaviors.
Dataset and file names are used only as report labels.

## Summary

- Files total: 57
- Files parsed: 55
- Files failed: 2
- Average intent confidence: 0.673

## Intent Distribution

- GENERAL_PROCESS_CONTROL: 20
- DATA_INTEGRITY_VERIFICATION: 8
- NUMERICAL_SOLVING: 7
- SEQUENTIAL_CONTROL: 5
- RATE_BASED_MEASUREMENT: 3
- MATRIX_PROCESSING: 3
- MULTI_ACTUATOR_COORDINATION: 3
- PROCESS_AUTOMATION: 3
- EVENT_COUNTING: 2
- STATE_BASED_CONTROL: 1

## Per-Dataset Intent Results

### CRC_GEN.st

- Dataset group: implementation
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.631
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - CHECKSUM_GENERATION=0.65

Supporting relationships:
    - <none>

Supporting operations:
    - bitwise_update=2
    - accumulator_update=10
    - bitwise_operation=10
    - iterative_computation=4

Supporting evidence:
    - bitwise_operation=20
    - accumulator=9

### FLOW_METER.st

- Dataset group: implementation
- Detected intent: RATE_BASED_MEASUREMENT
- Confidence: 0.847
- Explanation: Measurement calculations, counters, and history updates indicate rate-based measurement.

Supporting behaviors:
    - FLOW_MEASUREMENT=0.65

Supporting relationships:
    - feeds=5
    - depends_on=3

Supporting operations:
    - measurement_calculation=1
    - process_calculation=2
    - history_update=7

Supporting evidence:
    - measurement_calculation=1
    - history_variable=7

### FT_PIDWL.st

- Dataset group: implementation
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.49
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - activates=2
    - coordinates=1

Supporting operations:
    - comparison_operation=3
    - fb_invocation=4
    - data_movement=4
    - process_calculation=1

Supporting evidence:
    - fb_invocation=4
    - comparison=2

### GEN_BIT.st

- Dataset group: implementation
- Detected intent: EVENT_COUNTING
- Confidence: 0.975
- Explanation: Counter behavior and counter operations indicate event counting.

Supporting behaviors:
    - COUNTER_PROCESSING=0.95

Supporting relationships:
    - depends_on=17

Supporting operations:
    - counter_update=3
    - comparison_operation=11

Supporting evidence:
    - counter=3

### GEN_SIN.st

- Dataset group: implementation
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.734
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.65

Supporting relationships:
    - feeds=2

Supporting operations:
    - mathematical_solver=3
    - comparison_operation=4

Supporting evidence:
    - process_calculation=5

### INCLUDE.st

- Dataset group: implementation
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.575
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - <none>

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=4
    - accumulator_update=8
    - bitwise_operation=18
    - iterative_computation=1

Supporting evidence:
    - bitwise_operation=24
    - accumulator=9

### LAMBERT_W.st

- Dataset group: implementation
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.809
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.95

Supporting relationships:
    - feeds=1

Supporting operations:
    - mathematical_solver=5
    - iterative_computation=1
    - comparison_operation=2
    - return=1

Supporting evidence:
    - process_calculation=8

### MATRIX.st

- Dataset group: implementation
- Detected intent: MATRIX_PROCESSING
- Confidence: 0.633
- Explanation: Matrix or array access patterns with processing operations indicate matrix processing.

Supporting behaviors:
    - MATRIX_COMPUTATION=0.65

Supporting relationships:
    - <none>

Supporting operations:
    - array_read=3
    - array_write=2
    - iterative_computation=1
    - bitwise_update=14

Supporting evidence:
    - array_access=14
    - bitwise_operation=59

### SEQUENCE_8.st

- Dataset group: implementation
- Detected intent: SEQUENTIAL_CONTROL
- Confidence: 0.979
- Explanation: Ordered state transitions and sequence relationships indicate sequential control.

Supporting behaviors:
    - SEQUENTIAL_MACHINE_CONTROL=0.95

Supporting relationships:
    - transitions_to=9
    - sequences=16
    - controls=31

Supporting operations:
    - state_transition=1
    - history_update=9

Supporting evidence:
    - state_transition=10
    - history_variable=17

### TOOL_CHANGER.st

- Dataset group: implementation
- Detected intent: STATE_BASED_CONTROL
- Confidence: 0.574
- Explanation: Explicit state behavior and transition/control semantics indicate state-based control.

Supporting behaviors:
    - <none>

Supporting relationships:
    - transitions_to=6

Supporting operations:
    - state_transition=4
    - lookup_operation=1
    - comparison_operation=3

Supporting evidence:
    - state_transition=4

### TRAFFIC_CTRL.st

- Dataset group: implementation
- Detected intent: MULTI_ACTUATOR_COORDINATION
- Confidence: 0.979
- Explanation: Shared control behavior drives multiple control targets through coordinated relationships.

Supporting behaviors:
    - STATE_MACHINE_CONTROL=0.95

Supporting relationships:
    - activates=18
    - sequences=17
    - distinct_control_targets=6

Supporting operations:
    - state_transition=4
    - comparison_operation=11
    - data_movement=19

Supporting evidence:
    - state_transition=4

### robotic_sequence.st

- Dataset group: implementation
- Detected intent: PROCESS_AUTOMATION
- Confidence: 0.993
- Explanation: Multiple behaviors and multiple control relationships indicate broader process automation.

Supporting behaviors:
    - SEQUENTIAL_MACHINE_CONTROL=0.95
    - COUNTER_PROCESSING=0.95
    - recognized_behavior_count=2

Supporting relationships:
    - triggers=6
    - sequences=38
    - control_relationship_count=44

Supporting operations:
    - state_transition=13
    - comparison_operation=37
    - data_movement=67

Supporting evidence:
    - state_transition=13
    - counter=9

### sampletext_2.st

- Dataset group: implementation
- Detected intent: PROCESS_AUTOMATION
- Confidence: 0.993
- Explanation: Multiple behaviors and multiple control relationships indicate broader process automation.

Supporting behaviors:
    - SEQUENTIAL_MACHINE_CONTROL=0.95
    - COUNTER_PROCESSING=0.95
    - recognized_behavior_count=2

Supporting relationships:
    - triggers=6
    - sequences=38
    - control_relationship_count=44

Supporting operations:
    - state_transition=13
    - comparison_operation=37
    - data_movement=139

Supporting evidence:
    - state_transition=13
    - counter=9

### sampletext_3.st

- Dataset group: implementation
- Detected intent: PROCESS_AUTOMATION
- Confidence: 0.993
- Explanation: Multiple behaviors and multiple control relationships indicate broader process automation.

Supporting behaviors:
    - SEQUENTIAL_MACHINE_CONTROL=0.95
    - COUNTER_PROCESSING=0.95
    - recognized_behavior_count=2

Supporting relationships:
    - triggers=6
    - sequences=38
    - control_relationship_count=44

Supporting operations:
    - state_transition=13
    - comparison_operation=37
    - data_movement=139

Supporting evidence:
    - state_transition=13
    - counter=9

### sampletext_4.st

- Dataset group: implementation
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.49
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - uses=1

Supporting operations:
    - bitwise_update=1

Supporting evidence:
    - bitwise_operation=1

### CRC_GEN_FullTest (1).st

- Dataset group: test_harness
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.849
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - CHECKSUM_GENERATION=0.65

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=6
    - accumulator_update=18
    - bitwise_operation=28
    - iterative_computation=5

Supporting evidence:
    - bitwise_operation=44
    - accumulator=18

### CRC_GEN_FullTest.st

- Dataset group: test_harness
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.849
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - CHECKSUM_GENERATION=0.65

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=6
    - accumulator_update=18
    - bitwise_operation=28
    - iterative_computation=5

Supporting evidence:
    - bitwise_operation=44
    - accumulator=18

### FLOW_METER_FullTest (1).st

- Dataset group: test_harness
- Detected intent: RATE_BASED_MEASUREMENT
- Confidence: 0.848
- Explanation: Measurement calculations, counters, and history updates indicate rate-based measurement.

Supporting behaviors:
    - FLOW_MEASUREMENT=0.65

Supporting relationships:
    - feeds=12
    - depends_on=4

Supporting operations:
    - measurement_calculation=6
    - process_calculation=11
    - history_update=15

Supporting evidence:
    - measurement_calculation=1
    - history_variable=17

### FLOW_METER_FullTest.st

- Dataset group: test_harness
- Detected intent: RATE_BASED_MEASUREMENT
- Confidence: 0.848
- Explanation: Measurement calculations, counters, and history updates indicate rate-based measurement.

Supporting behaviors:
    - FLOW_MEASUREMENT=0.65

Supporting relationships:
    - feeds=12
    - depends_on=4

Supporting operations:
    - measurement_calculation=6
    - process_calculation=11
    - history_update=15

Supporting evidence:
    - measurement_calculation=1
    - history_variable=17

### FT_PIDWL_FullTest (1).st

- Dataset group: test_harness
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.575
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - <none>

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=4
    - accumulator_update=8
    - bitwise_operation=18
    - iterative_computation=1

Supporting evidence:
    - bitwise_operation=24
    - accumulator=9

### FT_PIDWL_FullTest.st

- Dataset group: test_harness
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.575
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - <none>

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=4
    - accumulator_update=8
    - bitwise_operation=18
    - iterative_computation=1

Supporting evidence:
    - bitwise_operation=24
    - accumulator=9

### GEN_BIT_FullTest.st

- Dataset group: test_harness
- Detected intent: EVENT_COUNTING
- Confidence: 0.974
- Explanation: Counter behavior and counter operations indicate event counting.

Supporting behaviors:
    - COUNTER_PROCESSING=0.95

Supporting relationships:
    - depends_on=18

Supporting operations:
    - counter_update=3
    - comparison_operation=24

Supporting evidence:
    - counter=3

### GEN_SIN_FullTest (1).st

- Dataset group: test_harness
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.974
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.95

Supporting relationships:
    - feeds=8
    - depends_on=1

Supporting operations:
    - mathematical_solver=3
    - iterative_computation=1
    - comparison_operation=17

Supporting evidence:
    - process_calculation=5

### GEN_SIN_FullTest (2).st

- Dataset group: test_harness
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.974
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.95

Supporting relationships:
    - feeds=8
    - depends_on=1

Supporting operations:
    - mathematical_solver=3
    - iterative_computation=1
    - comparison_operation=17

Supporting evidence:
    - process_calculation=5

### GEN_SIN_FullTest.st

- Dataset group: test_harness
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.974
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.95

Supporting relationships:
    - feeds=8
    - depends_on=1

Supporting operations:
    - mathematical_solver=3
    - iterative_computation=1
    - comparison_operation=17

Supporting evidence:
    - process_calculation=5

### LAMBERT_W_FullTest (1).st

- Dataset group: test_harness
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.974
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.95

Supporting relationships:
    - feeds=8
    - depends_on=1

Supporting operations:
    - mathematical_solver=5
    - iterative_computation=2
    - comparison_operation=15
    - return=1

Supporting evidence:
    - process_calculation=8

### LAMBERT_W_FullTest.st

- Dataset group: test_harness
- Detected intent: NUMERICAL_SOLVING
- Confidence: 0.974
- Explanation: Mathematical solver behavior and iterative computation indicate numerical solving.

Supporting behaviors:
    - MATHEMATICAL_SOLVER=0.95

Supporting relationships:
    - feeds=8
    - depends_on=1

Supporting operations:
    - mathematical_solver=5
    - iterative_computation=2
    - comparison_operation=15
    - return=1

Supporting evidence:
    - process_calculation=8

### MATRIX_FullTest (1).st

- Dataset group: test_harness
- Detected intent: MATRIX_PROCESSING
- Confidence: 0.85
- Explanation: Matrix or array access patterns with processing operations indicate matrix processing.

Supporting behaviors:
    - MATRIX_COMPUTATION=0.65

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - matrix_access=2
    - array_read=3
    - array_write=2
    - iterative_computation=2
    - bitwise_update=18

Supporting evidence:
    - array_access=14
    - bitwise_operation=83

### MATRIX_FullTest.st

- Dataset group: test_harness
- Detected intent: MATRIX_PROCESSING
- Confidence: 0.85
- Explanation: Matrix or array access patterns with processing operations indicate matrix processing.

Supporting behaviors:
    - MATRIX_COMPUTATION=0.65

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - matrix_access=2
    - array_read=3
    - array_write=2
    - iterative_computation=2
    - bitwise_update=18

Supporting evidence:
    - array_access=14
    - bitwise_operation=83

### SEQUENCE_8_FullTest (1).st

- Dataset group: test_harness
- Detected intent: SEQUENTIAL_CONTROL
- Confidence: 0.975
- Explanation: Ordered state transitions and sequence relationships indicate sequential control.

Supporting behaviors:
    - SEQUENTIAL_MACHINE_CONTROL=0.95

Supporting relationships:
    - transitions_to=9
    - sequences=17
    - controls=31

Supporting operations:
    - state_transition=1
    - history_update=17

Supporting evidence:
    - state_transition=10
    - history_variable=27

### SEQUENCE_8_FullTest.st

- Dataset group: test_harness
- Detected intent: SEQUENTIAL_CONTROL
- Confidence: 0.975
- Explanation: Ordered state transitions and sequence relationships indicate sequential control.

Supporting behaviors:
    - SEQUENTIAL_MACHINE_CONTROL=0.95

Supporting relationships:
    - transitions_to=9
    - sequences=17
    - controls=31

Supporting operations:
    - state_transition=1
    - history_update=17

Supporting evidence:
    - state_transition=10
    - history_variable=27

### TOOL_CHANGER_FullTest (1).st

- Dataset group: test_harness
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.575
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - <none>

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=4
    - accumulator_update=8
    - bitwise_operation=18
    - iterative_computation=1

Supporting evidence:
    - bitwise_operation=24
    - accumulator=9

### TOOL_CHANGER_FullTest.st

- Dataset group: test_harness
- Detected intent: DATA_INTEGRITY_VERIFICATION
- Confidence: 0.575
- Explanation: Repeated accumulator and bitwise update patterns indicate data integrity verification.

Supporting behaviors:
    - <none>

Supporting relationships:
    - feeds=7
    - depends_on=1

Supporting operations:
    - bitwise_update=4
    - accumulator_update=8
    - bitwise_operation=18
    - iterative_computation=1

Supporting evidence:
    - bitwise_operation=24
    - accumulator=9

### TRAFFIC_CTRL_FullTest (1).st

- Dataset group: test_harness
- Detected intent: MULTI_ACTUATOR_COORDINATION
- Confidence: 0.975
- Explanation: Shared control behavior drives multiple control targets through coordinated relationships.

Supporting behaviors:
    - STATE_MACHINE_CONTROL=0.95

Supporting relationships:
    - activates=18
    - sequences=19
    - distinct_control_targets=6

Supporting operations:
    - state_transition=4
    - comparison_operation=24
    - data_movement=32

Supporting evidence:
    - state_transition=4

### TRAFFIC_CTRL_FullTest.st

- Dataset group: test_harness
- Detected intent: MULTI_ACTUATOR_COORDINATION
- Confidence: 0.975
- Explanation: Shared control behavior drives multiple control targets through coordinated relationships.

Supporting behaviors:
    - STATE_MACHINE_CONTROL=0.95

Supporting relationships:
    - activates=18
    - sequences=18
    - distinct_control_targets=6

Supporting operations:
    - state_transition=4
    - comparison_operation=24
    - data_movement=32

Supporting evidence:
    - state_transition=4

### CRC_GEN_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=2

Supporting operations:
    - timer_invocation=6
    - lookup_operation=2
    - comparison_operation=17
    - fb_invocation=6
    - state_transition=4

Supporting evidence:
    - <none>

### CRC_GEN_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=6
    - lookup_operation=3
    - comparison_operation=19
    - fb_invocation=6
    - function_invocation=12

Supporting evidence:
    - <none>

### DEC_TO_HEX_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=36
    - lookup_operation=18
    - comparison_operation=109
    - fb_invocation=36
    - state_transition=18

Supporting evidence:
    - <none>

### FLOW_METER_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=12
    - lookup_operation=6
    - comparison_operation=37
    - fb_invocation=12
    - state_transition=6

Supporting evidence:
    - <none>

### FLOW_METER_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=10
    - lookup_operation=5
    - comparison_operation=31
    - fb_invocation=10
    - state_transition=5

Supporting evidence:
    - <none>

### FT_PIDWL_TestCases (1).st

- Dataset group: test_harness
- Detected intent: SEQUENTIAL_CONTROL
- Confidence: 0.397
- Explanation: Ordered state transitions and sequence relationships indicate sequential control.

Supporting behaviors:
    - <none>

Supporting relationships:
    - sequences=3

Supporting operations:
    - state_transition=5

Supporting evidence:
    - <none>

### FT_PIDWL_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=8
    - lookup_operation=4
    - comparison_operation=29
    - fb_invocation=8
    - state_transition=4

Supporting evidence:
    - <none>

### GEN_BIT_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=6
    - lookup_operation=3
    - comparison_operation=34
    - fb_invocation=6
    - state_transition=3

Supporting evidence:
    - <none>

### GEN_SIN_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=2

Supporting operations:
    - timer_invocation=9
    - lookup_operation=3
    - comparison_operation=31
    - fb_invocation=9
    - state_transition=6

Supporting evidence:
    - <none>

### GEN_SIN_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=10
    - lookup_operation=5
    - comparison_operation=36
    - fb_invocation=10
    - state_transition=5

Supporting evidence:
    - <none>

### LAMBERT_W_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=30
    - lookup_operation=15
    - comparison_operation=91
    - fb_invocation=30
    - state_transition=15

Supporting evidence:
    - <none>

### LAMBERT_W_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=20
    - lookup_operation=10
    - comparison_operation=61
    - fb_invocation=20
    - state_transition=10

Supporting evidence:
    - <none>

### MATRIX_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=2

Supporting operations:
    - timer_invocation=6
    - lookup_operation=2
    - comparison_operation=37
    - fb_invocation=6
    - state_transition=4

Supporting evidence:
    - <none>

### MATRIX_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=8
    - lookup_operation=4
    - comparison_operation=45
    - fb_invocation=8
    - state_transition=4

Supporting evidence:
    - <none>

### SEQUENCE_8_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=4
    - lookup_operation=2
    - comparison_operation=35
    - fb_invocation=4
    - state_transition=2

Supporting evidence:
    - <none>

### SEQUENCE_8_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=4
    - lookup_operation=2
    - comparison_operation=35
    - fb_invocation=4
    - state_transition=2

Supporting evidence:
    - <none>

### TOOL_CHANGER_TestCases (1).st

- Dataset group: test_harness
- Detected intent: SEQUENTIAL_CONTROL
- Confidence: 0.397
- Explanation: Ordered state transitions and sequence relationships indicate sequential control.

Supporting behaviors:
    - <none>

Supporting relationships:
    - sequences=3

Supporting operations:
    - state_transition=9

Supporting evidence:
    - <none>

### TOOL_CHANGER_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=10
    - lookup_operation=5
    - comparison_operation=36
    - fb_invocation=10
    - state_transition=5

Supporting evidence:
    - <none>

### TRAFFIC_CTRL_TestCases (1).st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=2

Supporting operations:
    - timer_invocation=6
    - lookup_operation=2
    - comparison_operation=45
    - fb_invocation=6
    - state_transition=4

Supporting evidence:
    - <none>

### TRAFFIC_CTRL_TestCases.st

- Dataset group: test_harness
- Detected intent: GENERAL_PROCESS_CONTROL
- Confidence: 0.41
- Explanation: No stronger domain-independent intent passed the support threshold.

Supporting behaviors:
    - <none>

Supporting relationships:
    - schedules=2
    - sequences=1

Supporting operations:
    - timer_invocation=8
    - lookup_operation=4
    - comparison_operation=53
    - fb_invocation=8
    - state_transition=4

Supporting evidence:
    - <none>


## Special Analysis

### CRC_GEN.st

Behaviors:
    - CHECKSUM_GENERATION [medium]

Intent:
    - DATA_INTEGRITY_VERIFICATION [0.631]

Reasoning steps:
    - Behavior signals: CHECKSUM_GENERATION=0.65
    - Relationship signals: <none>
    - Operation signals: bitwise_update=2, accumulator_update=10, bitwise_operation=10, iterative_computation=4
    - Evidence signals: bitwise_operation=20, accumulator=9
    - Conclusion: Repeated accumulator and bitwise update patterns indicate data integrity verification.

### FLOW_METER.st

Behaviors:
    - FLOW_MEASUREMENT [medium]

Intent:
    - RATE_BASED_MEASUREMENT [0.847]

Reasoning steps:
    - Behavior signals: FLOW_MEASUREMENT=0.65
    - Relationship signals: feeds=5, depends_on=3
    - Operation signals: measurement_calculation=1, process_calculation=2, history_update=7
    - Evidence signals: measurement_calculation=1, history_variable=7
    - Conclusion: Measurement calculations, counters, and history updates indicate rate-based measurement.

### LAMBERT_W.st

Behaviors:
    - MATHEMATICAL_SOLVER [high]

Intent:
    - NUMERICAL_SOLVING [0.809]

Reasoning steps:
    - Behavior signals: MATHEMATICAL_SOLVER=0.95
    - Relationship signals: feeds=1
    - Operation signals: mathematical_solver=5, iterative_computation=1, comparison_operation=2, return=1
    - Evidence signals: process_calculation=8
    - Conclusion: Mathematical solver behavior and iterative computation indicate numerical solving.

### MATRIX.st

Behaviors:
    - MATRIX_COMPUTATION [medium]

Intent:
    - MATRIX_PROCESSING [0.633]

Reasoning steps:
    - Behavior signals: MATRIX_COMPUTATION=0.65
    - Relationship signals: <none>
    - Operation signals: array_read=3, array_write=2, iterative_computation=1, bitwise_update=14
    - Evidence signals: array_access=14, bitwise_operation=59
    - Conclusion: Matrix or array access patterns with processing operations indicate matrix processing.

### SEQUENCE_8.st

Behaviors:
    - SEQUENTIAL_MACHINE_CONTROL [high]

Intent:
    - SEQUENTIAL_CONTROL [0.979]

Reasoning steps:
    - Behavior signals: SEQUENTIAL_MACHINE_CONTROL=0.95
    - Relationship signals: transitions_to=9, sequences=16, controls=31
    - Operation signals: state_transition=1, history_update=9
    - Evidence signals: state_transition=10, history_variable=17
    - Conclusion: Ordered state transitions and sequence relationships indicate sequential control.

### TOOL_CHANGER.st

Behaviors:
    - <none>

Intent:
    - STATE_BASED_CONTROL [0.574]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: transitions_to=6
    - Operation signals: state_transition=4, lookup_operation=1, comparison_operation=3
    - Evidence signals: state_transition=4
    - Conclusion: Explicit state behavior and transition/control semantics indicate state-based control.

### TRAFFIC_CTRL.st

Behaviors:
    - STATE_MACHINE_CONTROL [high]

Intent:
    - MULTI_ACTUATOR_COORDINATION [0.979]

Reasoning steps:
    - Behavior signals: STATE_MACHINE_CONTROL=0.95
    - Relationship signals: activates=18, sequences=17, distinct_control_targets=6
    - Operation signals: state_transition=4, comparison_operation=11, data_movement=19
    - Evidence signals: state_transition=4
    - Conclusion: Shared control behavior drives multiple control targets through coordinated relationships.

### CRC_GEN_FullTest.st

Behaviors:
    - CHECKSUM_GENERATION [medium]

Intent:
    - DATA_INTEGRITY_VERIFICATION [0.849]

Reasoning steps:
    - Behavior signals: CHECKSUM_GENERATION=0.65
    - Relationship signals: feeds=7, depends_on=1
    - Operation signals: bitwise_update=6, accumulator_update=18, bitwise_operation=28, iterative_computation=5
    - Evidence signals: bitwise_operation=44, accumulator=18
    - Conclusion: Repeated accumulator and bitwise update patterns indicate data integrity verification.

### FLOW_METER_FullTest.st

Behaviors:
    - FLOW_MEASUREMENT [medium]

Intent:
    - RATE_BASED_MEASUREMENT [0.848]

Reasoning steps:
    - Behavior signals: FLOW_MEASUREMENT=0.65
    - Relationship signals: feeds=12, depends_on=4
    - Operation signals: measurement_calculation=6, process_calculation=11, history_update=15
    - Evidence signals: measurement_calculation=1, history_variable=17
    - Conclusion: Measurement calculations, counters, and history updates indicate rate-based measurement.

### LAMBERT_W_FullTest.st

Behaviors:
    - MATHEMATICAL_SOLVER [high]

Intent:
    - NUMERICAL_SOLVING [0.974]

Reasoning steps:
    - Behavior signals: MATHEMATICAL_SOLVER=0.95
    - Relationship signals: feeds=8, depends_on=1
    - Operation signals: mathematical_solver=5, iterative_computation=2, comparison_operation=15, return=1
    - Evidence signals: process_calculation=8
    - Conclusion: Mathematical solver behavior and iterative computation indicate numerical solving.

### MATRIX_FullTest.st

Behaviors:
    - MATRIX_COMPUTATION [medium]

Intent:
    - MATRIX_PROCESSING [0.85]

Reasoning steps:
    - Behavior signals: MATRIX_COMPUTATION=0.65
    - Relationship signals: feeds=7, depends_on=1
    - Operation signals: matrix_access=2, array_read=3, array_write=2, iterative_computation=2, bitwise_update=18
    - Evidence signals: array_access=14, bitwise_operation=83
    - Conclusion: Matrix or array access patterns with processing operations indicate matrix processing.

### SEQUENCE_8_FullTest.st

Behaviors:
    - SEQUENTIAL_MACHINE_CONTROL [high]

Intent:
    - SEQUENTIAL_CONTROL [0.975]

Reasoning steps:
    - Behavior signals: SEQUENTIAL_MACHINE_CONTROL=0.95
    - Relationship signals: transitions_to=9, sequences=17, controls=31
    - Operation signals: state_transition=1, history_update=17
    - Evidence signals: state_transition=10, history_variable=27
    - Conclusion: Ordered state transitions and sequence relationships indicate sequential control.

### TOOL_CHANGER_FullTest.st

Behaviors:
    - <none>

Intent:
    - DATA_INTEGRITY_VERIFICATION [0.575]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: feeds=7, depends_on=1
    - Operation signals: bitwise_update=4, accumulator_update=8, bitwise_operation=18, iterative_computation=1
    - Evidence signals: bitwise_operation=24, accumulator=9
    - Conclusion: Repeated accumulator and bitwise update patterns indicate data integrity verification.

### TRAFFIC_CTRL_FullTest.st

Behaviors:
    - STATE_MACHINE_CONTROL [high]

Intent:
    - MULTI_ACTUATOR_COORDINATION [0.975]

Reasoning steps:
    - Behavior signals: STATE_MACHINE_CONTROL=0.95
    - Relationship signals: activates=18, sequences=18, distinct_control_targets=6
    - Operation signals: state_transition=4, comparison_operation=24, data_movement=32
    - Evidence signals: state_transition=4
    - Conclusion: Shared control behavior drives multiple control targets through coordinated relationships.

### CRC_GEN_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=6, lookup_operation=3, comparison_operation=19, fb_invocation=6, function_invocation=12
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.

### FLOW_METER_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=10, lookup_operation=5, comparison_operation=31, fb_invocation=10, state_transition=5
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.

### LAMBERT_W_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=20, lookup_operation=10, comparison_operation=61, fb_invocation=20, state_transition=10
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.

### MATRIX_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=8, lookup_operation=4, comparison_operation=45, fb_invocation=8, state_transition=4
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.

### SEQUENCE_8_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=4, lookup_operation=2, comparison_operation=35, fb_invocation=4, state_transition=2
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.

### TOOL_CHANGER_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=10, lookup_operation=5, comparison_operation=36, fb_invocation=10, state_transition=5
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.

### TRAFFIC_CTRL_TestCases.st

Behaviors:
    - <none>

Intent:
    - GENERAL_PROCESS_CONTROL [0.41]

Reasoning steps:
    - Behavior signals: <none>
    - Relationship signals: schedules=2, sequences=1
    - Operation signals: timer_invocation=8, lookup_operation=4, comparison_operation=53, fb_invocation=8, state_transition=4
    - Evidence signals: <none>
    - Conclusion: No stronger domain-independent intent passed the support threshold.
