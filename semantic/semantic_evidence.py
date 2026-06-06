"""Semantic evidence container and engine for the shared-evidence pipeline.

Replaces the diagnostic-only pattern library evidence with a structured
evidence system that feeds Classifier, OperationExtractor, and RelationshipExtractor.
"""

from collections import Counter


class EvidenceItem:
    """A single piece of semantic evidence extracted from an AST node."""

    EVIDENCE_TYPES = {
        "state_variable",
        "timer",
        "counter",
        "accumulator",
        "bitwise_operation",
        "array_access",
        "matrix_access",
        "fb_invocation",
        "state_transition",
        "measurement_calculation",
        "history_variable",
        "process_calculation",
        "assertion_logic",
        "test_scaffolding",
    }

    def __init__(self, evidence_type, confidence, ast_node, extracted_entities, metadata=None):
        self.evidence_type = evidence_type
        self.confidence = confidence
        self.ast_node = ast_node
        self.extracted_entities = extracted_entities or {}
        self.metadata = metadata or {}
        self.semantic_scope = metadata.get("semantic_scope", "INDUSTRIAL") if metadata else "INDUSTRIAL"

    def to_dict(self):
        return {
            "evidence_type": self.evidence_type,
            "confidence": self.confidence,
            "ast_node": self.ast_node,
            "extracted_entities": self.extracted_entities,
            "metadata": self.metadata,
            "semantic_scope": self.semantic_scope,
        }


class SemanticEvidence:
    """Container for all semantic evidence collected from an AST.

    Feeds into Classifier, OperationExtractor, and RelationshipExtractor.
    """

    def __init__(self, items=None):
        self.items = items or []

    def add(self, evidence_type, confidence, ast_node, extracted_entities=None, metadata=None):
        self.items.append(EvidenceItem(evidence_type, confidence, ast_node, extracted_entities, metadata))

    def get_by_type(self, evidence_type):
        return [item for item in self.items if item.evidence_type == evidence_type]

    def get_by_scope(self, scope):
        return [item for item in self.items if item.semantic_scope == scope]

    def get_counts(self):
        return dict(Counter(item.evidence_type for item in self.items))

    def get_scope_counts(self):
        industrial = [item for item in self.items if item.semantic_scope == "INDUSTRIAL"]
        test = [item for item in self.items if item.semantic_scope == "TEST"]
        return {
            "industrial": dict(Counter(item.evidence_type for item in industrial)),
            "test": dict(Counter(item.evidence_type for item in test)),
            "combined": dict(Counter(item.evidence_type for item in self.items)),
        }

    def to_dict(self):
        counts = self.get_counts()
        scope_counts = self.get_scope_counts()
        return {
            "items": [item.to_dict() for item in self.items],
            "total_count": len(self.items),
            "counts": counts,
            "scope_counts": scope_counts,
            "average_confidence": self._avg_confidence(),
        }

    def _avg_confidence(self):
        scores = {"low": 0.33, "medium": 0.66, "high": 1.0}
        if not self.items:
            return 0.0
        total = sum(scores.get(item.confidence, 0.5) for item in self.items)
        return round(total / len(self.items), 3)

    def get_evidence_summary(self):
        """Return a summary dict for SemanticContext."""
        counts = self.get_counts()
        return {
            "dominant_evidence": max(counts, key=counts.get) if counts else None,
            "evidence_counts": counts,
            "total_items": len(self.items),
            "average_confidence": self._avg_confidence(),
        }
