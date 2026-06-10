"""Domain-independent intent reasoner.

Rules consume only SemanticEvidence, operations, relationships, and behaviors.
They do not inspect filenames, dataset names, benchmark identifiers, or
application-specific labels.
"""

from collections import Counter

try:
    from semantic.intent import Intent, IntentReasoningResult, IntentType
except ModuleNotFoundError:
    from intent import Intent, IntentReasoningResult, IntentType


CONFIDENCE_VALUES = {
    "low": 0.35,
    "medium": 0.65,
    "high": 0.95,
}


class IntentReasoner:
    """Infer high-level software intent from semantic pipeline outputs."""

    def __init__(
        self,
        semantic_model=None,
        evidence=None,
        context=None,
        behaviors=None,
        relationships=None,
        operations=None,
    ):
        self.semantic_model = semantic_model
        self.context = context

        if semantic_model is not None:
            evidence = evidence if evidence is not None else getattr(semantic_model, "evidence", None)
            behaviors = behaviors if behaviors is not None else getattr(semantic_model, "behaviors", None)
            relationships = relationships if relationships is not None else getattr(semantic_model, "relationships", None)
            operations = operations if operations is not None else getattr(semantic_model, "operations", None)

        self.evidence = evidence or {}
        self.behaviors = behaviors or []
        self.relationships = relationships or {}
        self.operations = operations or {}

        self.behavior_map = self._behavior_map()
        self.evidence_counts = self._evidence_counts()
        self.operation_counts = self._operation_counts()
        self.relationship_counts = self._relationship_counts()
        self.relationship_items = self._relationship_items()
        self.evidence_average = self._evidence_average_confidence()

    def reason(self):
        """Return all supported intents and a dominant intent."""
        candidates = [
            self._state_based_control(),
            self._sequential_control(),
            self._multi_actuator_coordination(),
            self._event_driven_control(),
            self._rate_based_measurement(),
            self._event_counting(),
            self._process_monitoring(),
            self._data_integrity_verification(),
            self._data_transformation(),
            self._bitwise_data_processing(),
            self._mathematical_computation(),
            self._matrix_processing(),
            self._numerical_solving(),
            self._resource_coordination(),
            self._resource_transfer(),
            self._process_automation(),
        ]
        intents = [intent for intent in candidates if intent is not None and intent.confidence >= 0.38]

        if not intents:
            intents = [self._fallback_intent()]

        return IntentReasoningResult(intents)

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------

    def _behavior_map(self):
        result = {}
        for behavior in self._as_list(self.behaviors, "behaviors"):
            behavior_type = self._value(behavior.get("behavior_type") if isinstance(behavior, dict) else getattr(behavior, "behavior_type", None))
            if not behavior_type:
                continue
            confidence = behavior.get("confidence") if isinstance(behavior, dict) else getattr(behavior, "confidence", "medium")
            result[behavior_type] = max(result.get(behavior_type, 0.0), self._confidence_value(confidence))
        return result

    def _evidence_counts(self):
        if hasattr(self.evidence, "get_scope_counts"):
            return dict(self.evidence.get_scope_counts().get("industrial", {}))
        if isinstance(self.evidence, dict):
            scope_counts = self.evidence.get("scope_counts", {})
            if "industrial" in scope_counts:
                return dict(scope_counts.get("industrial", {}))
            return dict(self.evidence.get("counts", {}))
        return {}

    def _operation_counts(self):
        if isinstance(self.operations, dict):
            if self.operations.get("industrial_operation_counts"):
                return dict(self.operations.get("industrial_operation_counts", {}))
            return dict(self.operations.get("operation_counts", {}))
        return {}

    def _relationship_counts(self):
        if isinstance(self.relationships, dict):
            if self.relationships.get("industrial_relation_counts"):
                return dict(self.relationships.get("industrial_relation_counts", {}))
            return dict(self.relationships.get("relation_counts", {}))
        return {}

    def _relationship_items(self):
        if isinstance(self.relationships, dict):
            return list(self.relationships.get("industrial_relationships") or self.relationships.get("relationships") or [])
        return self._as_list(self.relationships, "relationships")

    def _evidence_average_confidence(self):
        if hasattr(self.evidence, "to_dict"):
            return float(self.evidence.to_dict().get("average_confidence", 0.0))
        if isinstance(self.evidence, dict):
            return float(self.evidence.get("average_confidence", 0.0))
        return 0.0

    def _as_list(self, value, key):
        if value is None:
            return []
        if isinstance(value, dict):
            return value.get(key, [])
        if isinstance(value, list):
            return value
        return list(value) if hasattr(value, "__iter__") else []

    def _value(self, value):
        return value.value if hasattr(value, "value") else value

    def _confidence_value(self, confidence):
        if isinstance(confidence, (int, float)):
            return max(0.0, min(float(confidence), 1.0))
        return CONFIDENCE_VALUES.get(str(confidence).lower(), 0.5)

    def _has_behavior(self, behavior_type):
        return self.behavior_map.get(behavior_type, 0.0) > 0.0

    def _behavior_strength(self, *behavior_types):
        return max((self.behavior_map.get(bt, 0.0) for bt in behavior_types), default=0.0)

    def _count_score(self, counts, names, strong_at=3):
        total = sum(counts.get(name, 0) for name in names)
        if total <= 0:
            return 0.0
        return min(1.0, total / float(strong_at))

    def _relationship_score(self, names, strong_at=3):
        return self._count_score(self.relationship_counts, names, strong_at)

    def _operation_score(self, names, strong_at=3):
        return self._count_score(self.operation_counts, names, strong_at)

    def _evidence_score(self, names, strong_at=3):
        count_strength = self._count_score(self.evidence_counts, names, strong_at)
        if count_strength == 0.0:
            return 0.0
        return min(1.0, (count_strength + self.evidence_average) / 2.0)

    def _distinct_control_targets(self):
        targets = set()
        for rel in self.relationship_items:
            if isinstance(rel, dict):
                relation = rel.get("relation")
                target = rel.get("target")
            else:
                relation = getattr(rel, "relation", None)
                target = getattr(rel, "target", None)
            if relation in ("controls", "activates") and target is not None:
                targets.add(str(target))
        return len(targets)

    def _support_items(self, counts, names):
        return [f"{name}={counts.get(name, 0)}" for name in names if counts.get(name, 0)]

    def _behavior_support(self, names):
        return [f"{name}={round(self.behavior_map[name], 3)}" for name in names if self.behavior_map.get(name)]

    def _combine(self, behavior, relationship, operation, evidence, consistency):
        return round(
            (0.42 * behavior)
            + (0.22 * relationship)
            + (0.20 * operation)
            + (0.11 * evidence)
            + (0.05 * consistency),
            3,
        )

    def _consistent(self, *scores):
        positive = [score for score in scores if score > 0.0]
        if len(positive) >= 3:
            return 1.0
        if len(positive) == 2:
            return 0.65
        if len(positive) == 1:
            return 0.25
        return 0.0

    def _intent(self, intent_type, confidence, behaviors, relationships, operations, evidence, explanation):
        return Intent(
            intent_type=intent_type,
            confidence=confidence,
            supporting_behaviors=self._behavior_support(behaviors),
            supporting_relationships=self._support_items(self.relationship_counts, relationships),
            supporting_operations=self._support_items(self.operation_counts, operations),
            supporting_evidence=self._support_items(self.evidence_counts, evidence),
            explanation=explanation,
        )

    # ------------------------------------------------------------------
    # Intent rules
    # ------------------------------------------------------------------

    def _state_based_control(self):
        behaviors = ["STATE_MACHINE_CONTROL"]
        relationships = ["transitions_to", "controls", "enables", "disables"]
        operations = ["state_transition", "state_update", "lookup_operation", "comparison_operation"]
        evidence = ["state_transition", "state_variable", "timer"]
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=4)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.38:
            return None
        return self._intent(IntentType.STATE_BASED_CONTROL, score, behaviors, relationships, operations, evidence, "Explicit state behavior and transition/control semantics indicate state-based control.")

    def _sequential_control(self):
        behaviors = ["SEQUENTIAL_MACHINE_CONTROL"]
        relationships = ["transitions_to", "sequences", "controls"]
        operations = ["state_transition", "state_update", "counter_update", "history_update"]
        evidence = ["state_transition", "counter", "history_variable"]
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(["transitions_to", "sequences"], strong_at=4)
        o = self._operation_score(operations, strong_at=5)
        e = self._evidence_score(evidence, strong_at=5)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.38:
            return None
        return self._intent(IntentType.SEQUENTIAL_CONTROL, score, behaviors, relationships, operations, evidence, "Ordered state transitions and sequence relationships indicate sequential control.")

    def _multi_actuator_coordination(self):
        behaviors = ["STATE_MACHINE_CONTROL", "SEQUENTIAL_MACHINE_CONTROL"]
        relationships = ["controls", "activates", "enables", "disables", "sequences"]
        operations = ["state_transition", "comparison_operation", "data_movement"]
        evidence = ["state_transition", "state_variable"]
        target_score = min(1.0, self._distinct_control_targets() / 2.0)
        b = self._behavior_strength(*behaviors)
        r = max(target_score, self._relationship_score(["controls", "activates"], strong_at=3))
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.40:
            return None
        intent = self._intent(IntentType.MULTI_ACTUATOR_COORDINATION, score, behaviors, relationships, operations, evidence, "Shared control behavior drives multiple control targets through coordinated relationships.")
        if self._distinct_control_targets():
            intent.supporting_relationships.append(f"distinct_control_targets={self._distinct_control_targets()}")
        return intent

    def _event_driven_control(self):
        behaviors = ["STATE_MACHINE_CONTROL", "SEQUENTIAL_MACHINE_CONTROL", "COUNTER_PROCESSING"]
        relationships = ["triggers", "activates", "enables", "disables"]
        operations = ["comparison_operation", "timer_invocation", "counter_invocation", "history_update"]
        evidence = ["timer", "counter", "history_variable"]
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=3)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=4)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.42:
            return None
        return self._intent(IntentType.EVENT_DRIVEN_CONTROL, score, behaviors, relationships, operations, evidence, "Trigger, activation, timer, counter, or history signals indicate event-driven control.")

    def _rate_based_measurement(self):
        behaviors = ["FLOW_MEASUREMENT", "COUNTER_PROCESSING"]
        relationships = ["feeds", "activates", "depends_on"]
        operations = ["measurement_calculation", "process_calculation", "counter_update", "history_update"]
        evidence = ["measurement_calculation", "counter", "history_variable"]
        b = self._behavior_strength("FLOW_MEASUREMENT")
        r = self._relationship_score(relationships, strong_at=3)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.40:
            return None
        return self._intent(IntentType.RATE_BASED_MEASUREMENT, score, behaviors, relationships, operations, evidence, "Measurement calculations, counters, and history updates indicate rate-based measurement.")

    def _event_counting(self):
        behaviors = ["COUNTER_PROCESSING"]
        relationships = ["triggers", "feeds", "depends_on"]
        operations = ["counter_update", "counter_invocation", "comparison_operation"]
        evidence = ["counter"]
        has_counter_signal = (
            self._has_behavior("COUNTER_PROCESSING")
            or self.evidence_counts.get("counter", 0) > 0
            or self.operation_counts.get("counter_update", 0) > 0
            or self.operation_counts.get("counter_invocation", 0) > 0
        )
        if not has_counter_signal:
            return None
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=3)
        o = self._operation_score(operations, strong_at=3)
        e = self._evidence_score(evidence, strong_at=2)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.40:
            return None
        return self._intent(IntentType.EVENT_COUNTING, score, behaviors, relationships, operations, evidence, "Counter behavior and counter operations indicate event counting.")

    def _process_monitoring(self):
        behaviors = ["FLOW_MEASUREMENT", "COUNTER_PROCESSING", "STATE_MACHINE_CONTROL"]
        relationships = ["depends_on", "feeds", "enables", "disables"]
        operations = ["comparison_operation", "history_update", "measurement_calculation", "process_calculation"]
        evidence = ["measurement_calculation", "history_variable", "counter", "assertion_logic"]
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(operations, strong_at=5)
        e = self._evidence_score(evidence, strong_at=4)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.45:
            return None
        return self._intent(IntentType.PROCESS_MONITORING, score, behaviors, relationships, operations, evidence, "Comparison, history, measurement, or dependency signals indicate monitored process conditions.")

    def _data_integrity_verification(self):
        behaviors = ["CHECKSUM_GENERATION"]
        relationships = ["feeds", "depends_on"]
        operations = ["bitwise_update", "accumulator_update", "bitwise_operation", "iterative_computation"]
        evidence = ["bitwise_operation", "accumulator"]
        has_integrity_signal = (
            self._has_behavior("CHECKSUM_GENERATION")
            or (
                self.operation_counts.get("bitwise_update", 0) > 0
                and self.operation_counts.get("accumulator_update", 0) >= 3
                and self.evidence_counts.get("bitwise_operation", 0) >= 3
            )
        )
        if not has_integrity_signal:
            return None
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=3)
        o = self._operation_score(["bitwise_update", "accumulator_update"], strong_at=6)
        e = self._evidence_score(evidence, strong_at=5)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.40:
            return None
        return self._intent(IntentType.DATA_INTEGRITY_VERIFICATION, score, behaviors, relationships, operations, evidence, "Repeated accumulator and bitwise update patterns indicate data integrity verification.")

    def _data_transformation(self):
        behaviors = ["DATA_TRANSFORMATION", "MATRIX_COMPUTATION", "CHECKSUM_GENERATION"]
        relationships = ["feeds", "depends_on"]
        operations = ["data_movement", "array_read", "array_write", "process_calculation", "function_invocation"]
        evidence = ["array_access", "process_calculation", "fb_invocation", "bitwise_operation"]
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(operations, strong_at=5)
        e = self._evidence_score(evidence, strong_at=4)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.42:
            return None
        return self._intent(IntentType.DATA_TRANSFORMATION, score, behaviors, relationships, operations, evidence, "Data movement, array access, and process calculation indicate representation transformation.")

    def _bitwise_data_processing(self):
        behaviors = ["CHECKSUM_GENERATION", "DATA_TRANSFORMATION"]
        relationships = ["feeds", "depends_on"]
        operations = ["bitwise_update", "bitwise_operation", "accumulator_update"]
        evidence = ["bitwise_operation", "accumulator"]
        b = self._behavior_strength(*behaviors) * 0.85
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(["bitwise_operation"], strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.42:
            return None
        return self._intent(IntentType.BITWISE_DATA_PROCESSING, score, behaviors, relationships, operations, evidence, "Bitwise evidence and bitwise operations indicate bit-level data processing.")

    def _mathematical_computation(self):
        behaviors = ["MATHEMATICAL_SOLVER", "DATA_TRANSFORMATION"]
        relationships = ["feeds", "depends_on"]
        operations = ["mathematical_solver", "iterative_computation", "process_calculation", "return"]
        evidence = ["process_calculation"]
        has_math_signal = (
            self._has_behavior("MATHEMATICAL_SOLVER")
            or self.operation_counts.get("mathematical_solver", 0) >= 2
            or (
                self.operation_counts.get("process_calculation", 0) >= 4
                and self.operation_counts.get("measurement_calculation", 0) == 0
            )
        )
        if not has_math_signal:
            return None
        b = max(self._behavior_strength("MATHEMATICAL_SOLVER"), self._behavior_strength("DATA_TRANSFORMATION") * 0.45)
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.40:
            return None
        return self._intent(IntentType.MATHEMATICAL_COMPUTATION, score, behaviors, relationships, operations, evidence, "Numeric calculation, math functions, or iterative computation indicate mathematical computation.")

    def _matrix_processing(self):
        behaviors = ["MATRIX_COMPUTATION"]
        relationships = ["feeds", "depends_on"]
        operations = ["matrix_access", "array_read", "array_write", "iterative_computation", "bitwise_update"]
        evidence = ["matrix_access", "array_access", "bitwise_operation"]
        has_matrix_signal = (
            self._has_behavior("MATRIX_COMPUTATION")
            or self.evidence_counts.get("matrix_access", 0) > 0
            or self.operation_counts.get("matrix_access", 0) > 0
            or self.evidence_counts.get("array_access", 0) >= 3
        )
        if not has_matrix_signal:
            return None
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.40:
            return None
        return self._intent(IntentType.MATRIX_PROCESSING, score, behaviors, relationships, operations, evidence, "Matrix or array access patterns with processing operations indicate matrix processing.")

    def _numerical_solving(self):
        behaviors = ["MATHEMATICAL_SOLVER"]
        relationships = ["feeds", "depends_on"]
        operations = ["mathematical_solver", "iterative_computation", "comparison_operation", "return"]
        evidence = ["process_calculation"]
        has_solver_signal = (
            self._has_behavior("MATHEMATICAL_SOLVER")
            or (
                self.operation_counts.get("mathematical_solver", 0) >= 2
                and self.operation_counts.get("iterative_computation", 0) >= 1
            )
        )
        if not has_solver_signal:
            return None
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=4)
        o = self._operation_score(["mathematical_solver", "iterative_computation"], strong_at=3)
        e = self._evidence_score(evidence, strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.42:
            return None
        return self._intent(IntentType.NUMERICAL_SOLVING, score, behaviors, relationships, operations, evidence, "Mathematical solver behavior and iterative computation indicate numerical solving.")

    def _resource_coordination(self):
        behaviors = ["STATE_MACHINE_CONTROL", "SEQUENTIAL_MACHINE_CONTROL", "COUNTER_PROCESSING"]
        relationships = ["controls", "enables", "disables", "sequences"]
        operations = ["state_transition", "comparison_operation", "data_movement"]
        evidence = ["state_transition", "state_variable"]
        if sum(self.relationship_counts.get(name, 0) for name in relationships) == 0:
            return None
        b = self._behavior_strength(*behaviors)
        r = self._relationship_score(relationships, strong_at=5)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=3)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.45:
            return None
        return self._intent(IntentType.RESOURCE_COORDINATION, score, behaviors, relationships, operations, evidence, "Control relationships coordinate shared controlled targets or resource availability.")

    def _resource_transfer(self):
        behaviors = ["SEQUENTIAL_MACHINE_CONTROL", "STATE_MACHINE_CONTROL"]
        relationships = ["sequences", "controls", "transitions_to"]
        operations = ["state_transition", "state_update", "data_movement"]
        evidence = ["state_transition", "state_variable"]
        has_both = self._has_behavior("SEQUENTIAL_MACHINE_CONTROL") and self._has_behavior("STATE_MACHINE_CONTROL")
        b = self._behavior_strength(*behaviors)
        if has_both:
            b = min(1.0, b + 0.15)
        actuator_coordination = min(1.0, (self.relationship_counts.get("controls", 0) + self.relationship_counts.get("sequences", 0)) / 5.0)
        r = max(self._relationship_score(relationships, strong_at=5), actuator_coordination)
        o = self._operation_score(operations, strong_at=4)
        e = self._evidence_score(evidence, strong_at=4)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.48:
            return None
        return self._intent(IntentType.RESOURCE_TRANSFER, score, behaviors, relationships, operations, evidence, "Sequential/state control combined with coordinated control relationships indicates resource transfer.")

    def _process_automation(self):
        control_relationships = ["controls", "enables", "disables", "triggers", "activates", "sequences"]
        behavior_count = len([bt for bt, score in self.behavior_map.items() if score > 0.0])
        control_rel_count = sum(self.relationship_counts.get(name, 0) for name in control_relationships)
        if behavior_count < 2 and control_rel_count < 2:
            return None
        behaviors = list(self.behavior_map.keys())
        operations = ["state_transition", "comparison_operation", "process_calculation", "measurement_calculation", "data_movement"]
        evidence = ["state_transition", "measurement_calculation", "process_calculation", "counter", "timer"]
        b = min(1.0, behavior_count / 2.0)
        r = min(1.0, control_rel_count / 4.0)
        o = self._operation_score(operations, strong_at=6)
        e = self._evidence_score(evidence, strong_at=5)
        score = self._combine(b, r, o, e, self._consistent(b, r, o, e))
        if score < 0.50:
            return None
        intent = self._intent(IntentType.PROCESS_AUTOMATION, score, behaviors, control_relationships, operations, evidence, "Multiple behaviors and multiple control relationships indicate broader process automation.")
        intent.supporting_behaviors.append(f"recognized_behavior_count={behavior_count}")
        intent.supporting_relationships.append(f"control_relationship_count={control_rel_count}")
        return intent

    def _fallback_intent(self):
        relationships = list(self.relationship_counts.keys())[:5]
        operations = list(self.operation_counts.keys())[:5]
        evidence = list(self.evidence_counts.keys())[:5]
        signal_groups = sum(1 for group in (relationships, operations, evidence, self.behavior_map) if group)
        confidence = 0.25 + (0.08 * signal_groups)
        return Intent(
            intent_type=IntentType.GENERAL_PROCESS_CONTROL,
            confidence=min(0.49, confidence),
            supporting_behaviors=self._behavior_support(list(self.behavior_map.keys())),
            supporting_relationships=self._support_items(self.relationship_counts, relationships),
            supporting_operations=self._support_items(self.operation_counts, operations),
            supporting_evidence=self._support_items(self.evidence_counts, evidence),
            explanation="No stronger domain-independent intent passed the support threshold.",
        )
