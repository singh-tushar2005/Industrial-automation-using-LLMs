# Domain-Independent Intent Taxonomy

Intent answers: "What is this software trying to accomplish?"

An intent is a high-level software purpose inferred from semantic evidence,
operations, relationships, and recognized behaviors. Intent inference must not
use filenames, dataset names, benchmark identifiers, variable names alone, or
application-specific rules. Variable names may appear only as payload inside
already-extracted evidence, operations, relationships, or behavior explanations.

## Confidence Rules

Intent confidence combines four signal groups:

- Behavior confidence: strength of recognized behaviors.
- Relationship confidence: presence and density of semantic relationships that
  support the purpose.
- Operation confidence: presence and density of operations that implement the
  purpose.
- Evidence confidence: direct semantic evidence and its average confidence.

High confidence requires a strong behavior plus at least two consistent support
groups. Medium confidence requires a matching behavior plus one support group,
or several consistent support groups without a strong behavior. Low confidence
means partial support only. `GENERAL_PROCESS_CONTROL` is emitted only when no
stronger intent is supported.

## Control Intents

### STATE_BASED_CONTROL

Definition: Maintains an explicit logical state and changes behavior according
to that state.

Required behaviors: `STATE_MACHINE_CONTROL`.

Optional behaviors: `SEQUENTIAL_MACHINE_CONTROL`, `COUNTER_PROCESSING`.

Supporting relationships: `transitions_to`, `controls`, `enables`, `disables`.

Supporting operations: `state_transition`, `state_update`, `lookup_operation`,
`comparison_operation`.

Examples: mode selection, staged control, guarded state changes.

Non-examples: pure calculation, pure data copy, isolated counter increments.

### SEQUENTIAL_CONTROL

Definition: Advances through ordered steps where later actions depend on prior
step completion.

Required behaviors: `SEQUENTIAL_MACHINE_CONTROL`.

Optional behaviors: `STATE_MACHINE_CONTROL`, `COUNTER_PROCESSING`.

Supporting relationships: `transitions_to`, `sequences`, `controls`.

Supporting operations: `state_transition`, `state_update`, `counter_update`,
`history_update`.

Examples: ordered startup, multi-step execution, phase progression.

Non-examples: independent boolean interlocks, one-shot calculations.

### MULTI_ACTUATOR_COORDINATION

Definition: Coordinates multiple controlled targets from shared state,
conditions, or transitions.

Required behaviors: `STATE_MACHINE_CONTROL` or `SEQUENTIAL_MACHINE_CONTROL`.

Optional behaviors: `COUNTER_PROCESSING`.

Supporting relationships: multiple `controls` edges, plus `enables`,
`disables`, or `sequences`.

Supporting operations: `state_transition`, `comparison_operation`,
`data_movement`.

Examples: shared state driving several outputs, mutually coordinated actions.

Non-examples: one output controlled by one condition, pure measurement.

### EVENT_DRIVEN_CONTROL

Definition: Performs control actions in response to events, edges, timers, or
threshold changes.

Required behaviors: any control behavior with event-like support.

Optional behaviors: `COUNTER_PROCESSING`, `FLOW_MEASUREMENT`.

Supporting relationships: `triggers`, `activates`, `enables`, `disables`.

Supporting operations: `comparison_operation`, `timer_invocation`,
`counter_invocation`, `history_update`.

Examples: edge-triggered action, timer-driven transition, threshold response.

Non-examples: continuous calculation with no discrete trigger.

## Measurement Intents

### RATE_BASED_MEASUREMENT

Definition: Computes a rate or flow-like measurement from counts, elapsed
change, or process calculation.

Required behaviors: `FLOW_MEASUREMENT`.

Optional behaviors: `COUNTER_PROCESSING`.

Supporting relationships: `feeds`, `activates`, `depends_on`.

Supporting operations: `measurement_calculation`, `process_calculation`,
`counter_update`, `history_update`.

Examples: rate from count delta over time, scaled measurement calculation.

Non-examples: arbitrary arithmetic without measurement evidence.

### EVENT_COUNTING

Definition: Counts occurrences or transitions as a primary purpose.

Required behaviors: `COUNTER_PROCESSING`.

Optional behaviors: `FLOW_MEASUREMENT`.

Supporting relationships: `triggers`, `feeds`, `depends_on`.

Supporting operations: `counter_update`, `counter_invocation`,
`comparison_operation`.

Examples: count accumulation, thresholded count tracking.

Non-examples: loop indices used only for array traversal.

### PROCESS_MONITORING

Definition: Observes process conditions and derives status, alarms, or
readiness from measurements, comparisons, or history.

Required behaviors: measurement, counter, or control behavior with monitoring
relationships.

Optional behaviors: `FLOW_MEASUREMENT`, `COUNTER_PROCESSING`.

Supporting relationships: `depends_on`, `feeds`, `enables`, `disables`.

Supporting operations: `comparison_operation`, `history_update`,
`measurement_calculation`, `process_calculation`.

Examples: threshold monitoring, status derivation, trend/history comparison.

Non-examples: transformation with no monitored condition.

## Data Processing Intents

### DATA_INTEGRITY_VERIFICATION

Definition: Computes verification data by repeated accumulation and bitwise
transformation.

Required behaviors: `CHECKSUM_GENERATION`.

Optional behaviors: `DATA_TRANSFORMATION`.

Supporting relationships: `feeds`, `depends_on`.

Supporting operations: `bitwise_update`, `accumulator_update`,
`bitwise_operation`, `iterative_computation`.

Examples: repeated checksum accumulation, parity-like verification update.

Non-examples: single bit extraction used as a control condition.

### DATA_TRANSFORMATION

Definition: Converts, packs, maps, or reshapes data from one representation to
another.

Required behaviors: `DATA_TRANSFORMATION` or strong operation/evidence support.

Optional behaviors: `MATRIX_COMPUTATION`, `CHECKSUM_GENERATION`.

Supporting relationships: `feeds`, `depends_on`.

Supporting operations: `data_movement`, `array_read`, `array_write`,
`process_calculation`, `function_invocation`.

Examples: encoding, table mapping, representation conversion.

Non-examples: state changes where output control is the primary purpose.

### BITWISE_DATA_PROCESSING

Definition: Uses bitwise logic to pack, unpack, mask, rotate, or combine data.

Required behaviors: bitwise evidence and bitwise operations.

Optional behaviors: `CHECKSUM_GENERATION`, `DATA_TRANSFORMATION`.

Supporting relationships: `feeds`, `depends_on`.

Supporting operations: `bitwise_update`, `bitwise_operation`,
`accumulator_update`.

Examples: masking, shifting, rotating, packed-bit extraction.

Non-examples: boolean control expressions with no data transformation purpose.

## Computational Intents

### MATHEMATICAL_COMPUTATION

Definition: Computes numeric results using arithmetic, functions, or iterative
calculation.

Required behaviors: `MATHEMATICAL_SOLVER` or strong process-calculation support.

Optional behaviors: `DATA_TRANSFORMATION`.

Supporting relationships: `feeds`, `depends_on`.

Supporting operations: `mathematical_solver`, `iterative_computation`,
`process_calculation`, `return`.

Examples: function approximation, numeric transformation, iterative refinement.

Non-examples: arithmetic used only to increment a state or counter.

### MATRIX_PROCESSING

Definition: Processes indexed or matrix-shaped data structures.

Required behaviors: `MATRIX_COMPUTATION`.

Optional behaviors: `DATA_TRANSFORMATION`, `MATHEMATICAL_SOLVER`.

Supporting relationships: `feeds`, `depends_on`.

Supporting operations: `matrix_access`, `array_read`, `array_write`,
`iterative_computation`, `bitwise_update`.

Examples: indexed table update, matrix element processing, array-based packing.

Non-examples: scalar arithmetic without array or matrix access evidence.

### NUMERICAL_SOLVING

Definition: Solves a numeric problem through repeated approximation,
convergence, or advanced math functions.

Required behaviors: `MATHEMATICAL_SOLVER`.

Optional behaviors: `DATA_TRANSFORMATION`.

Supporting relationships: `feeds`, `depends_on`.

Supporting operations: `mathematical_solver`, `iterative_computation`,
`comparison_operation`, `return`.

Examples: iterative root/function solving, convergence-tested calculations.

Non-examples: direct one-pass arithmetic with no solver behavior.

## System Intents

### RESOURCE_COORDINATION

Definition: Coordinates access, availability, or sequencing across shared
resources or controlled targets.

Required behaviors: control behaviors with multiple coordinated relationships.

Optional behaviors: `COUNTER_PROCESSING`.

Supporting relationships: `controls`, `enables`, `disables`, `sequences`.

Supporting operations: `state_transition`, `comparison_operation`,
`data_movement`.

Examples: arbitration, shared resource gating, coordinated readiness.

Non-examples: independent calculations or isolated data transformation.

### RESOURCE_TRANSFER

Definition: Transfers a resource or work item through ordered states using
coordinated control.

Required behaviors: `SEQUENTIAL_MACHINE_CONTROL` and `STATE_MACHINE_CONTROL`,
or one of them with strong actuator coordination.

Optional behaviors: `COUNTER_PROCESSING`.

Supporting relationships: `sequences`, `controls`, `transitions_to`.

Supporting operations: `state_transition`, `state_update`, `data_movement`.

Examples: ordered handoff, staged transfer, coordinated movement through steps.

Non-examples: pure sequencing without a transfer/coordination structure.

### PROCESS_AUTOMATION

Definition: Automates an overall process by combining multiple behaviors and
multiple control relationships.

Required behaviors: at least two recognized behaviors, or one strong control
behavior with broad relationship support.

Optional behaviors: any recognized behavior.

Supporting relationships: multiple control-oriented relationships such as
`controls`, `enables`, `disables`, `triggers`, `activates`, `sequences`.

Supporting operations: mixed control, measurement, data, or calculation
operations.

Examples: combined control, measurement, and data processing workflow.

Non-examples: a single narrow calculation or a single isolated relationship.

## Fallback

### GENERAL_PROCESS_CONTROL

Definition: Generic process-control purpose when no stronger domain-independent
intent has sufficient support.

Required behaviors: none.

Optional behaviors: any weak or partial behavior.

Supporting relationships: any semantic relationship.

Supporting operations: any extracted operation.

Examples: sparse logic with insufficient evidence for a specific intent.

Non-examples: any program with a supported stronger intent above fallback
threshold.
