"""Behavior recognition engine.

Consumes SemanticEvidence, SemanticContext, operations, and relationships,
and emits Behavior objects.  All patterns are evidence/operation/relationship
based — no filename rules, no dataset-specific logic.
"""

from collections import Counter

try:
    from semantic.behavior import Behavior, BehaviorType
    from semantic.semantic_evidence import SemanticEvidence
    from semantic.semantic_context import SemanticContext
except ModuleNotFoundError:
    from behavior import Behavior, BehaviorType
    from semantic_evidence import SemanticEvidence
    from semantic_context import SemanticContext


class BehaviorRecognizer:
    """Recognize industrial behaviors from semantic pipeline outputs."""

    def __init__(self, evidence=None, context=None, operations=None, relationships=None):
        self.evidence = evidence
        self.context = context
        self.operations = operations or {}
        self.relationships = relationships or {}
        self.behaviors = []

    def recognize(self):
        """Run all behavior recognizers and return detected Behavior objects."""
        self.behaviors = []
        self._recognize_checksum_generation()
        self._recognize_flow_measurement()
        self._recognize_state_machine_control()
        self._recognize_sequential_machine_control()
        self._recognize_matrix_computation()
        self._recognize_mathematical_solver()
        self._recognize_data_transformation()
        self._recognize_counter_processing()

        # Post-processing: refine state machine vs sequential classification
        self._refine_state_machine_classification()

        # Post-processing: confidence adjustments based on evidence quality
        self._adjust_confidence()

        return list(self.behaviors)

    # ------------------------------------------------------------------
    # Evidence / operation helpers
    # ------------------------------------------------------------------

    def _evidence_counts(self):
        if self.evidence and hasattr(self.evidence, "get_scope_counts"):
            return self.evidence.get_scope_counts().get("industrial", {})
        return {}

    def _evidence_items(self):
        if self.evidence and hasattr(self.evidence, "items"):
            return [item for item in self.evidence.items if item.semantic_scope == "INDUSTRIAL"]
        return []

    def _operation_counts(self):
        ops = self.operations
        if isinstance(ops, dict):
            return ops.get("operation_counts", {})
        return {}

    def _industrial_operation_counts(self):
        ops = self.operations
        if isinstance(ops, dict):
            return ops.get("industrial_operation_counts", {})
        return {}

    def _relationship_counts(self):
        rels = self.relationships
        if isinstance(rels, dict):
            return rels.get("relation_counts", {})
        return {}

    def _industrial_relationship_counts(self):
        rels = self.relationships
        if isinstance(rels, dict):
            return rels.get("industrial_relation_counts", {})
        return {}

    def _has_context_tag(self, tag):
        if self.context and hasattr(self.context, "tags"):
            return tag in self.context.tags
        return False

    def _context_intent(self):
        if self.context and hasattr(self.context, "dominant_intent"):
            return self.context.dominant_intent
        return None

    def _has_xor_accumulator_evidence(self):
        """Check if any accumulator evidence item uses XOR operator with high confidence."""
        for item in self._evidence_items():
            if item.evidence_type == "accumulator":
                op = item.extracted_entities.get("operator", "")
                conf = item.confidence
                if op == "XOR" and conf == "high":
                    return True
        return False

    def _has_measurement_calculation(self):
        """Check if measurement_calculation evidence is present."""
        counts = self._evidence_counts()
        return counts.get("measurement_calculation", 0) >= 1

    def _has_case_statement(self):
        """Check if the program contains a CASE statement (lookup_operation)."""
        opcounts = self._industrial_operation_counts()
        return opcounts.get("lookup_operation", 0) >= 1

    # ------------------------------------------------------------------
    # Behavior recognizers
    # ------------------------------------------------------------------

    def _recognize_checksum_generation(self):
        """CHECKSUM_GENERATION: XOR-based bitwise accumulator updates.

        Refined rule: requires high-confidence XOR accumulator evidence,
        high bitwise update count, and strong accumulator iteration.
        Eliminates utility functions and loop counters that trigger
        generic bitwise + accumulator patterns.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()

        bitwise = ecounts.get("bitwise_operation", 0)
        accumulators = ecounts.get("accumulator", 0)
        bitwise_update = opcounts.get("bitwise_update", 0)
        accumulator_update = opcounts.get("accumulator_update", 0)

        # Core requirement: XOR-based accumulation with sustained bitwise updates
        has_xor_accumulator = self._has_xor_accumulator_evidence()
        if has_xor_accumulator and bitwise >= 5 and bitwise_update >= 2 and accumulator_update >= 5:
            confidence = "high" if accumulator_update >= 8 else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.CHECKSUM_GENERATION,
                    confidence,
                    supporting_evidence=[
                        f"bitwise_operation={bitwise}",
                        f"accumulator={accumulators}",
                        f"xor_accumulator=yes",
                    ],
                    supporting_operations=[
                        f"bitwise_update={bitwise_update}",
                        f"accumulator_update={accumulator_update}",
                    ],
                    supporting_relationships=[],
                )
            )

    def _recognize_flow_measurement(self):
        """FLOW_MEASUREMENT: measurement calculations with direct evidence.

        Refined rule: only triggers on direct measurement_calculation evidence
        (including nested time-based divisions). The secondary signal is removed
        to eliminate false positives from test harness helper functions.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()

        measurements = ecounts.get("measurement_calculation", 0)
        history = ecounts.get("history_variable", 0)
        counters = ecounts.get("counter", 0)
        process_calc = opcounts.get("process_calculation", 0)

        # Direct evidence only: explicit measurement calculation
        if measurements >= 1:
            confidence = "high" if history >= 2 else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.FLOW_MEASUREMENT,
                    confidence,
                    supporting_evidence=[
                        f"measurement_calculation={measurements}",
                        f"history_variable={history}",
                        f"counter={counters}",
                    ],
                    supporting_operations=[
                        f"process_calculation={process_calc}",
                    ],
                    supporting_relationships=[],
                )
            )

    def _recognize_state_machine_control(self):
        """STATE_MACHINE_CONTROL: state transitions with timer or strong CASE structure.

        Refined rule: maintains timer requirement for state machines, but
        CASE-based machines without timers are handled in the refinement step.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()
        relcounts = self._industrial_relationship_counts()

        state_transitions = ecounts.get("state_transition", 0)
        state_vars = ecounts.get("state_variable", 0)
        timers = ecounts.get("timer", 0)
        transitions_to = relcounts.get("transitions_to", 0)
        sequences = relcounts.get("sequences", 0)

        # Core requirement: explicit state transitions with timer FB or strong transition graph
        if (state_transitions >= 1 or transitions_to >= 1) and (timers >= 1 or transitions_to >= 2):
            confidence = "high" if (state_transitions >= 3 or transitions_to >= 2) else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.STATE_MACHINE_CONTROL,
                    confidence,
                    supporting_evidence=[
                        f"state_transition={state_transitions}",
                        f"state_variable={state_vars}",
                        f"timer={timers}",
                    ],
                    supporting_operations=[
                        f"state_transition={opcounts.get('state_transition', 0)}",
                        f"timer_invocation={opcounts.get('timer_invocation', 0)}",
                    ],
                    supporting_relationships=[
                        f"transitions_to={transitions_to}",
                        f"sequences={sequences}",
                    ],
                )
            )

    def _recognize_sequential_machine_control(self):
        """SEQUENTIAL_MACHINE_CONTROL: state transitions without timer FBs + actuator coordination.

        Refined rule: requires timing artifacts (counters or history variables)
        to distinguish from pure CASE-based state machines.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()
        relcounts = self._industrial_relationship_counts()

        state_transitions = ecounts.get("state_transition", 0)
        timers = ecounts.get("timer", 0)
        counters = ecounts.get("counter", 0)
        history = ecounts.get("history_variable", 0)
        fb_invocations = ecounts.get("fb_invocation", 0)
        actuator_sequences = relcounts.get("sequences", 0)
        state_ops = opcounts.get("state_transition", 0)

        has_timing = counters >= 1 or (history >= 5 and state_transitions >= 5)

        # Sequential control: state transitions without timer FBs, but with timing or actuator sequencing
        if state_transitions >= 5 and timers == 0 and (has_timing or actuator_sequences >= 5):
            confidence = "high" if state_transitions >= 5 else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.SEQUENTIAL_MACHINE_CONTROL,
                    confidence,
                    supporting_evidence=[
                        f"state_transition={state_transitions}",
                        f"timer={timers}",
                        f"counter={counters}",
                        f"history_variable={history}",
                    ],
                    supporting_operations=[
                        f"state_transition={state_ops}",
                        f"timer_invocation={opcounts.get('timer_invocation', 0)}",
                    ],
                    supporting_relationships=[
                        f"sequences={actuator_sequences}",
                        f"transitions_to={relcounts.get('transitions_to', 0)}",
                    ],
                )
            )

    def _recognize_matrix_computation(self):
        """MATRIX_COMPUTATION: matrix/array access + bitwise operations.

        MATRIX pattern: array indexing with matrix-like structure, combined
        with bitwise data packing/unpacking.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()

        matrix_access = ecounts.get("matrix_access", 0)
        array_access = ecounts.get("array_access", 0)
        bitwise = ecounts.get("bitwise_operation", 0)
        array_ops = opcounts.get("array_read", 0) + opcounts.get("array_write", 0)

        if matrix_access >= 1 or (array_access >= 3 and bitwise >= 3 and array_ops >= 2):
            confidence = "high" if matrix_access >= 1 else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.MATRIX_COMPUTATION,
                    confidence,
                    supporting_evidence=[
                        f"matrix_access={matrix_access}",
                        f"array_access={array_access}",
                        f"bitwise_operation={bitwise}",
                    ],
                    supporting_operations=[
                        f"array_read={opcounts.get('array_read', 0)}",
                        f"array_write={opcounts.get('array_write', 0)}",
                        f"bitwise_update={opcounts.get('bitwise_update', 0)}",
                    ],
                    supporting_relationships=[],
                )
            )

    def _recognize_mathematical_solver(self):
        """MATHEMATICAL_SOLVER: advanced math functions + iterative refinement.

        LAMBERT_W pattern: LN, EXP, iterative FOR loop with convergence test.
        Also catches SQRT, ABS, MODR, SIN, COS, TAN, etc.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()

        process_calc = ecounts.get("process_calculation", 0)
        math_ops = opcounts.get("mathematical_solver", 0)
        iterative = opcounts.get("iterative_computation", 0)

        # Look for math solver operations or advanced process calculations
        if math_ops >= 2:
            confidence = "high" if math_ops >= 2 and iterative >= 1 else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.MATHEMATICAL_SOLVER,
                    confidence,
                    supporting_evidence=[
                        f"process_calculation={process_calc}",
                    ],
                    supporting_operations=[
                        f"mathematical_solver={math_ops}",
                        f"iterative_computation={iterative}",
                        f"process_calculation={opcounts.get('process_calculation', 0)}",
                    ],
                    supporting_relationships=[],
                )
            )

    def _recognize_data_transformation(self):
        """DATA_TRANSFORMATION: array access + process calculation + FB invocation.

        General pattern: data moves through arrays with computation and
        function block calls.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()

        array_access = ecounts.get("array_access", 0)
        process_calc = ecounts.get("process_calculation", 0)
        fb_invocations = ecounts.get("fb_invocation", 0)

        array_ops = opcounts.get("array_read", 0) + opcounts.get("array_write", 0)
        proc_ops = opcounts.get("process_calculation", 0)

        if array_access >= 2 and (process_calc >= 1 or fb_invocations >= 1):
            confidence = "medium"
            if array_access >= 4 and process_calc >= 2:
                confidence = "high"
            self.behaviors.append(
                Behavior(
                    BehaviorType.DATA_TRANSFORMATION,
                    confidence,
                    supporting_evidence=[
                        f"array_access={array_access}",
                        f"process_calculation={process_calc}",
                        f"fb_invocation={fb_invocations}",
                    ],
                    supporting_operations=[
                        f"array_read={opcounts.get('array_read', 0)}",
                        f"array_write={opcounts.get('array_write', 0)}",
                        f"process_calculation={proc_ops}",
                        f"fb_invocation={opcounts.get('fb_invocation', 0)}",
                    ],
                    supporting_relationships=[],
                )
            )

    def _recognize_counter_processing(self):
        """COUNTER_PROCESSING: counter evidence + counter operations.

        Detects explicit counter updates and counter FB invocations.
        """
        ecounts = self._evidence_counts()
        opcounts = self._industrial_operation_counts()

        counters = ecounts.get("counter", 0)
        counter_ops = opcounts.get("counter_update", 0) + opcounts.get("counter_invocation", 0)

        if counters >= 1 or counter_ops >= 1:
            confidence = "high" if counters >= 2 or counter_ops >= 2 else "medium"
            self.behaviors.append(
                Behavior(
                    BehaviorType.COUNTER_PROCESSING,
                    confidence,
                    supporting_evidence=[
                        f"counter={counters}",
                    ],
                    supporting_operations=[
                        f"counter_update={opcounts.get('counter_update', 0)}",
                        f"counter_invocation={opcounts.get('counter_invocation', 0)}",
                    ],
                    supporting_relationships=[],
                )
            )

    # ------------------------------------------------------------------
    # Post-processing refinements
    # ------------------------------------------------------------------

    def _refine_state_machine_classification(self):
        """Refine state machine vs sequential classification.

        CASE-based state machines without counters or history variables
        should be classified as STATE_MACHINE_CONTROL, not SEQUENTIAL_MACHINE_CONTROL.
        """
        ecounts = self._evidence_counts()
        has_case = self._has_case_statement()
        counters = ecounts.get("counter", 0)
        history = ecounts.get("history_variable", 0)

        has_sequential = any(
            b.behavior_type == BehaviorType.SEQUENTIAL_MACHINE_CONTROL for b in self.behaviors
        )
        has_state_machine = any(
            b.behavior_type == BehaviorType.STATE_MACHINE_CONTROL for b in self.behaviors
        )

        if has_sequential and has_state_machine:
            # CASE-based state machine without timing artifacts → state machine
            if has_case and counters == 0 and history == 0:
                self.behaviors = [
                    b for b in self.behaviors
                    if b.behavior_type != BehaviorType.SEQUENTIAL_MACHINE_CONTROL
                ]
            elif ecounts.get("timer", 0) == 0:
                # IF-based sequential controller without timers → sequential
                self.behaviors = [
                    b for b in self.behaviors
                    if b.behavior_type != BehaviorType.STATE_MACHINE_CONTROL
                ]

    def _adjust_confidence(self):
        """Adjust confidence based on evidence quality and relationship support."""
        relcounts = self._industrial_relationship_counts()
        ecounts = self._evidence_counts()
        has_measurement = self._has_measurement_calculation()
        has_xor = self._has_xor_accumulator_evidence()

        adjusted = []
        for behavior in self.behaviors:
            bt = behavior.behavior_type
            conf = behavior.confidence
            new_conf = conf

            # CHECKSUM_GENERATION: downgrade if no XOR accumulator
            if bt == BehaviorType.CHECKSUM_GENERATION:
                if not has_xor:
                    new_conf = "low"
                elif relcounts.get("sequences", 0) == 0 and relcounts.get("controls", 0) == 0:
                    new_conf = "medium"

            # FLOW_MEASUREMENT: downgrade if no direct measurement evidence
            if bt == BehaviorType.FLOW_MEASUREMENT:
                if not has_measurement:
                    new_conf = "medium"
                elif relcounts.get("feeds", 0) == 0 and relcounts.get("activates", 0) == 0:
                    new_conf = "medium"

            # STATE_MACHINE_CONTROL: upgrade if strong transition graph
            if bt == BehaviorType.STATE_MACHINE_CONTROL:
                transitions = relcounts.get("transitions_to", 0)
                if transitions >= 5:
                    new_conf = "high"

            # SEQUENTIAL_MACHINE_CONTROL: upgrade if strong actuator sequencing
            if bt == BehaviorType.SEQUENTIAL_MACHINE_CONTROL:
                sequences = relcounts.get("sequences", 0)
                if sequences >= 10:
                    new_conf = "high"

            # MATHEMATICAL_SOLVER: downgrade if only from helper functions
            if bt == BehaviorType.MATHEMATICAL_SOLVER:
                math_ops = self._industrial_operation_counts().get("mathematical_solver", 0)
                if math_ops < 2:
                    new_conf = "low"

            # Create new behavior with adjusted confidence
            adjusted.append(
                Behavior(
                    bt,
                    new_conf,
                    supporting_evidence=behavior.supporting_evidence,
                    supporting_operations=behavior.supporting_operations,
                    supporting_relationships=behavior.supporting_relationships,
                )
            )

        self.behaviors = adjusted

    # ------------------------------------------------------------------
    # Result formatting
    # ------------------------------------------------------------------

    def get_results(self):
        """Return a structured report dict for downstream consumers."""
        return {
            "behaviors": [b.to_dict() for b in self.behaviors],
            "behavior_count": len(self.behaviors),
            "behavior_types": [
                b.behavior_type.value if isinstance(b.behavior_type, BehaviorType) else b.behavior_type
                for b in self.behaviors
            ],
        }
