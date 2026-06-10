"""Intent-aware semantic impact analysis.

This module consumes existing semantic outputs: graph topology, semantic
evidence, operations, behaviors, and intents. It does not extract new
semantics or modify dependency reasoning. It maps node failures to affected
behaviors, intents, and capability loss.
"""

try:
    from semantic.dependency_reasoner import DependencyReasoner
except ModuleNotFoundError:
    from dependency_reasoner import DependencyReasoner


class ImpactResult:
    """Semantic impact result for one source node."""

    def __init__(
        self,
        source_node,
        affected_nodes=None,
        affected_behaviors=None,
        affected_intents=None,
        severity="LOW",
        explanation="",
        capability_loss=None,
    ):
        self.source_node = source_node
        self.affected_nodes = affected_nodes or []
        self.affected_behaviors = affected_behaviors or []
        self.affected_intents = affected_intents or []
        self.severity = severity
        self.explanation = explanation
        self.capability_loss = capability_loss or []

    def to_dict(self):
        return {
            "source_node": self.source_node,
            "affected_nodes": self.affected_nodes,
            "affected_behaviors": self.affected_behaviors,
            "affected_intents": self.affected_intents,
            "severity": self.severity,
            "capability_loss": self.capability_loss,
            "explanation": self.explanation,
        }


BEHAVIOR_TO_INTENTS = {
    "CHECKSUM_GENERATION": ["DATA_INTEGRITY_VERIFICATION", "BITWISE_DATA_PROCESSING"],
    "FLOW_MEASUREMENT": ["RATE_BASED_MEASUREMENT", "PROCESS_MONITORING"],
    "STATE_MACHINE_CONTROL": [
        "STATE_BASED_CONTROL",
        "MULTI_ACTUATOR_COORDINATION",
        "RESOURCE_TRANSFER",
        "RESOURCE_COORDINATION",
        "PROCESS_AUTOMATION",
    ],
    "SEQUENTIAL_MACHINE_CONTROL": [
        "SEQUENTIAL_CONTROL",
        "MULTI_ACTUATOR_COORDINATION",
        "RESOURCE_TRANSFER",
        "RESOURCE_COORDINATION",
        "PROCESS_AUTOMATION",
    ],
    "MATRIX_COMPUTATION": ["MATRIX_PROCESSING", "DATA_TRANSFORMATION"],
    "MATHEMATICAL_SOLVER": ["NUMERICAL_SOLVING", "MATHEMATICAL_COMPUTATION"],
    "COUNTER_PROCESSING": ["EVENT_COUNTING", "RATE_BASED_MEASUREMENT", "PROCESS_MONITORING"],
    "DATA_TRANSFORMATION": ["DATA_TRANSFORMATION", "MATRIX_PROCESSING"],
}

BEHAVIOR_CAPABILITIES = {
    "CHECKSUM_GENERATION": "integrity verification unavailable",
    "FLOW_MEASUREMENT": "rate measurement unavailable",
    "STATE_MACHINE_CONTROL": "state-based control strategy impacted",
    "SEQUENTIAL_MACHINE_CONTROL": "sequence progression unavailable",
    "MATRIX_COMPUTATION": "matrix or indexed data processing unavailable",
    "MATHEMATICAL_SOLVER": "numerical solving capability unavailable",
    "COUNTER_PROCESSING": "event counting unavailable",
    "DATA_TRANSFORMATION": "data transformation capability unavailable",
}

INTENT_CAPABILITIES = {
    "DATA_INTEGRITY_VERIFICATION": "data integrity verification objective affected",
    "RATE_BASED_MEASUREMENT": "rate-based measurement objective affected",
    "SEQUENTIAL_CONTROL": "ordered control objective affected",
    "STATE_BASED_CONTROL": "state-based control objective affected",
    "MULTI_ACTUATOR_COORDINATION": "multi-target coordination objective affected",
    "RESOURCE_TRANSFER": "resource transfer objective affected",
    "RESOURCE_COORDINATION": "resource coordination objective affected",
    "PROCESS_AUTOMATION": "process automation objective affected",
    "MATRIX_PROCESSING": "matrix processing objective affected",
    "NUMERICAL_SOLVING": "numerical solving objective affected",
    "MATHEMATICAL_COMPUTATION": "mathematical computation objective affected",
    "EVENT_COUNTING": "event counting objective affected",
    "PROCESS_MONITORING": "process monitoring objective affected",
    "DATA_TRANSFORMATION": "data transformation objective affected",
    "BITWISE_DATA_PROCESSING": "bitwise data processing objective affected",
}


class SemanticImpactAnalyzer:
    """Analyze behavior, intent, and capability impact for graph nodes."""

    def __init__(self, graph, semantic_model=None, behaviors=None, intents=None, operations=None, relationships=None, evidence=None):
        self.graph = graph
        self.semantic_model = semantic_model or {}
        self.behaviors = self._items(behaviors or self.semantic_model.get("behaviors", []), "behaviors")
        self.intents = self._items(intents or self.semantic_model.get("intents", []), "intents")
        self.operations = operations or self.semantic_model.get("operations", {})
        self.relationships = relationships or self.semantic_model.get("relationships", {})
        self.evidence = evidence or self.semantic_model.get("evidence", {})
        self.reasoner = DependencyReasoner(graph)

        self.behavior_types = [self._behavior_type(item) for item in self.behaviors]
        self.intent_types = [self._intent_type(item) for item in self.intents]
        self.operation_items = self._items(self.operations, "operations")
        self.relationship_items = self._items(self.relationships, "relationships")
        self.evidence_items = self._items(self.evidence, "items")

    def analyze_behavior_impact(self):
        """Return ImpactResult objects with affected behaviors populated."""
        return [self._impact_for_node(node_id) for node_id in self._all_node_ids()]

    def analyze_intent_impact(self):
        """Return ImpactResult objects with affected intents populated."""
        return [self._impact_for_node(node_id) for node_id in self._all_node_ids()]

    def analyze_capability_loss(self):
        """Return ImpactResult objects with semantic capability loss populated."""
        return [self._impact_for_node(node_id) for node_id in self._all_node_ids()]

    def analyze_all(self):
        """Return complete impact results for all graph nodes."""
        return [self._impact_for_node(node_id) for node_id in self._all_node_ids()]

    def _impact_for_node(self, node_id):
        affected_nodes = sorted(set(self.reasoner.find_transitive_dependencies(node_id)) | self._semantic_neighbors(node_id))
        affected_behaviors = self._affected_behaviors(node_id, affected_nodes)
        affected_intents = self._affected_intents(node_id, affected_behaviors, affected_nodes)
        capability_loss = self._capability_loss(affected_behaviors, affected_intents)
        severity = self._severity(affected_behaviors, affected_intents, affected_nodes)
        explanation = self._explanation(node_id, affected_behaviors, affected_intents, capability_loss)
        return ImpactResult(
            source_node=node_id,
            affected_nodes=affected_nodes,
            affected_behaviors=affected_behaviors,
            affected_intents=affected_intents,
            severity=severity,
            capability_loss=capability_loss,
            explanation=explanation,
        )

    def _affected_behaviors(self, node_id, affected_nodes):
        candidates = {node_id} | set(affected_nodes)
        behavior_scores = {}
        for candidate in candidates:
            kind = self._node_kind(candidate)
            evidence_types = self._evidence_types_for_node(candidate)
            operation_types = self._operation_types_for_node(candidate)
            relation_types = self._relation_types_for_node(candidate)
            for behavior in self.behavior_types:
                if self._supports_behavior(behavior, kind, evidence_types, operation_types, relation_types):
                    behavior_scores[behavior] = behavior_scores.get(behavior, 0) + 1
        return sorted(behavior_scores)

    def _affected_intents(self, node_id, affected_behaviors, affected_nodes):
        intents = set()
        for behavior in affected_behaviors:
            intents.update(BEHAVIOR_TO_INTENTS.get(behavior, []))

        candidates = {node_id} | set(affected_nodes)
        for candidate in candidates:
            kind = self._node_kind(candidate)
            evidence_types = self._evidence_types_for_node(candidate)
            operation_types = self._operation_types_for_node(candidate)
            relation_types = self._relation_types_for_node(candidate)
            intents.update(self._direct_intents(kind, evidence_types, operation_types, relation_types))

        if self.intent_types:
            intents = intents & set(self.intent_types)
        return sorted(intents)

    def _capability_loss(self, affected_behaviors, affected_intents):
        capabilities = []
        for behavior in affected_behaviors:
            capability = BEHAVIOR_CAPABILITIES.get(behavior)
            if capability:
                capabilities.append(capability)
        for intent in affected_intents:
            capability = INTENT_CAPABILITIES.get(intent)
            if capability:
                capabilities.append(capability)
        return sorted(set(capabilities))

    def _severity(self, affected_behaviors, affected_intents, affected_nodes):
        score = 0
        score += len(affected_behaviors) * 2
        score += len(affected_intents) * 3
        score += min(len(affected_nodes), 10)
        relationship_support = 0
        for node_id in affected_nodes:
            relationship_support += len(self._relation_types_for_node(node_id))
        score += min(relationship_support, 8)

        if score >= 22:
            return "CRITICAL"
        if score >= 14:
            return "HIGH"
        if score >= 7:
            return "MEDIUM"
        return "LOW"

    def _explanation(self, node_id, behaviors, intents, capabilities):
        if not behaviors and not intents:
            return f"{node_id} has graph impact but no supported behavior or intent mapping from current semantic outputs."
        parts = [f"{node_id} contributes to {', '.join(behaviors) or 'no recognized behavior'}."]
        if intents:
            parts.append(f"Those behavior signals support {', '.join(intents)}.")
        if capabilities:
            parts.append(f"Capability loss: {', '.join(capabilities)}.")
        return " ".join(parts)

    # ------------------------------------------------------------------
    # Semantic signal matching
    # ------------------------------------------------------------------

    def _supports_behavior(self, behavior, node_kind, evidence_types, operation_types, relation_types):
        if behavior == "FLOW_MEASUREMENT":
            return (
                node_kind in {"sensor", "process_variable", "counter", "history"}
                or bool(evidence_types & {"measurement_calculation", "history_variable", "counter"})
                or bool(operation_types & {"measurement_calculation", "history_update", "counter_update"})
            )
        if behavior == "COUNTER_PROCESSING":
            return node_kind == "counter" or "counter" in evidence_types or bool(operation_types & {"counter_update", "counter_invocation"})
        if behavior == "STATE_MACHINE_CONTROL":
            return node_kind == "state" or "state_transition" in evidence_types or "state_transition" in operation_types or "transitions_to" in relation_types
        if behavior == "SEQUENTIAL_MACHINE_CONTROL":
            return node_kind == "state" or bool(relation_types & {"sequences", "transitions_to"}) or "state_transition" in operation_types
        if behavior == "CHECKSUM_GENERATION":
            return bool(evidence_types & {"accumulator", "bitwise_operation"}) or bool(operation_types & {"accumulator_update", "bitwise_update", "bitwise_operation"})
        if behavior == "MATRIX_COMPUTATION":
            return bool(evidence_types & {"matrix_access", "array_access"}) or bool(operation_types & {"matrix_access", "array_read", "array_write"})
        if behavior == "MATHEMATICAL_SOLVER":
            return bool(evidence_types & {"process_calculation"}) or bool(operation_types & {"mathematical_solver", "iterative_computation", "process_calculation"})
        if behavior == "DATA_TRANSFORMATION":
            return bool(evidence_types & {"array_access", "fb_invocation", "process_calculation", "bitwise_operation"}) or bool(operation_types & {"data_movement", "array_read", "array_write", "process_calculation", "function_invocation", "fb_invocation"})
        return False

    def _direct_intents(self, node_kind, evidence_types, operation_types, relation_types):
        intents = set()
        if node_kind == "counter" or "counter" in evidence_types or bool(operation_types & {"counter_update", "counter_invocation"}):
            intents.update({"EVENT_COUNTING", "RATE_BASED_MEASUREMENT"})
        if "measurement_calculation" in evidence_types or "measurement_calculation" in operation_types:
            intents.add("RATE_BASED_MEASUREMENT")
        if node_kind == "state" or "state_transition" in evidence_types or bool(relation_types & {"transitions_to", "sequences"}):
            intents.update({"STATE_BASED_CONTROL", "SEQUENTIAL_CONTROL"})
        if bool(relation_types & {"controls", "activates"}):
            intents.add("MULTI_ACTUATOR_COORDINATION")
        if bool(evidence_types & {"accumulator", "bitwise_operation"}) or bool(operation_types & {"accumulator_update", "bitwise_update"}):
            intents.update({"DATA_INTEGRITY_VERIFICATION", "BITWISE_DATA_PROCESSING"})
        if bool(evidence_types & {"matrix_access", "array_access"}) or bool(operation_types & {"matrix_access", "array_read", "array_write"}):
            intents.add("MATRIX_PROCESSING")
        if bool(operation_types & {"mathematical_solver", "iterative_computation"}):
            intents.update({"NUMERICAL_SOLVING", "MATHEMATICAL_COMPUTATION"})
        if bool(operation_types & {"data_movement", "process_calculation", "function_invocation", "fb_invocation"}):
            intents.add("DATA_TRANSFORMATION")
        return intents

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------

    def _items(self, value, key):
        if value is None:
            return []
        if isinstance(value, dict):
            return list(value.get(key, []))
        if isinstance(value, list):
            return value
        return list(value) if hasattr(value, "__iter__") else []

    def _all_node_ids(self):
        node_ids = {node.node_id for node in self.graph.nodes()}
        for relationship in self.relationship_items:
            if relationship.get("source"):
                node_ids.add(str(relationship["source"]))
            if relationship.get("target"):
                node_ids.add(str(relationship["target"]))
        for operation in self.operation_items:
            target = operation.get("target")
            if self._is_semantic_identifier(target):
                node_ids.add(str(target))
            for source in operation.get("sources", []):
                if self._is_semantic_identifier(source):
                    node_ids.add(str(source))
        for item in self.evidence_items:
            entities = item.get("extracted_entities", {}) if isinstance(item, dict) else {}
            for value in self._flatten_entities(entities):
                if self._is_semantic_identifier(value):
                    node_ids.add(str(value))
        return sorted(node_ids)

    def _is_semantic_identifier(self, value):
        if value is None:
            return False
        text = str(value)
        if not text or text == "<none>":
            return False
        if text in {"+", "-", "*", "/", "=", "<>", "<", ">", "<=", ">=", "AND", "OR", "XOR", "NOT", "MOD"}:
            return False
        if text.upper() in {"TRUE", "FALSE"}:
            return False
        if text.replace(".", "", 1).isdigit():
            return False
        return True

    def _semantic_neighbors(self, node_id):
        neighbors = set()
        for relationship in self.relationship_items:
            source = relationship.get("source")
            target = relationship.get("target")
            if source == node_id and target:
                neighbors.add(str(target))
            if target == node_id and source:
                neighbors.add(str(source))
        for operation in self.operation_items:
            target = operation.get("target")
            sources = operation.get("sources", [])
            if target == node_id:
                neighbors.update(str(source) for source in sources if source and source != "<none>")
            if node_id in sources and target and target != "<none>":
                neighbors.add(str(target))
        neighbors.discard(node_id)
        return neighbors

    def _node_kind(self, node_id):
        node = self.graph.get_node(node_id)
        if node:
            return node.node_kind
        evidence_types = self._evidence_types_for_node(node_id)
        operation_types = self._operation_types_for_node(node_id)
        if "counter" in evidence_types or bool(operation_types & {"counter_update", "counter_invocation"}):
            return "counter"
        if "history_variable" in evidence_types or "history_update" in operation_types:
            return "history"
        if "state_transition" in evidence_types or "state_transition" in operation_types:
            return "state"
        if "fb_invocation" in evidence_types or "fb_invocation" in operation_types:
            return "function_block"
        if bool(evidence_types & {"measurement_calculation", "process_calculation"}):
            return "process_variable"
        return "unknown"

    def _behavior_type(self, behavior):
        value = behavior.get("behavior_type") if isinstance(behavior, dict) else getattr(behavior, "behavior_type", None)
        return value.value if hasattr(value, "value") else value

    def _intent_type(self, intent):
        value = intent.get("intent_type") if isinstance(intent, dict) else getattr(intent, "intent_type", None)
        return value.value if hasattr(value, "value") else value

    def _operation_types_for_node(self, node_id):
        result = set()
        for operation in self.operation_items:
            target = operation.get("target")
            sources = operation.get("sources", [])
            if target == node_id or node_id in sources:
                result.add(operation.get("operation_type"))
        return {item for item in result if item}

    def _relation_types_for_node(self, node_id):
        result = set()
        for relationship in self.relationship_items:
            if relationship.get("source") == node_id or relationship.get("target") == node_id:
                result.add(relationship.get("relation"))
        return {item for item in result if item}

    def _evidence_types_for_node(self, node_id):
        result = set()
        for item in self.evidence_items:
            entities = item.get("extracted_entities", {}) if isinstance(item, dict) else {}
            values = self._flatten_entities(entities)
            if node_id in values:
                result.add(item.get("evidence_type"))
        return {item for item in result if item}

    def _flatten_entities(self, value):
        if isinstance(value, dict):
            results = []
            for nested in value.values():
                results.extend(self._flatten_entities(nested))
            return results
        if isinstance(value, list):
            results = []
            for nested in value:
                results.extend(self._flatten_entities(nested))
            return results
        if value is None:
            return []
        return [str(value)]


def analyze_behavior_impact(graph, semantic_model=None, behaviors=None, operations=None, relationships=None, evidence=None):
    analyzer = SemanticImpactAnalyzer(
        graph,
        semantic_model=semantic_model,
        behaviors=behaviors,
        operations=operations,
        relationships=relationships,
        evidence=evidence,
    )
    return analyzer.analyze_behavior_impact()


def analyze_intent_impact(graph, semantic_model=None, intents=None, behaviors=None, operations=None, relationships=None, evidence=None):
    analyzer = SemanticImpactAnalyzer(
        graph,
        semantic_model=semantic_model,
        intents=intents,
        behaviors=behaviors,
        operations=operations,
        relationships=relationships,
        evidence=evidence,
    )
    return analyzer.analyze_intent_impact()


def analyze_capability_loss(graph, semantic_model=None, intents=None, behaviors=None, operations=None, relationships=None, evidence=None):
    analyzer = SemanticImpactAnalyzer(
        graph,
        semantic_model=semantic_model,
        intents=intents,
        behaviors=behaviors,
        operations=operations,
        relationships=relationships,
        evidence=evidence,
    )
    return analyzer.analyze_capability_loss()
