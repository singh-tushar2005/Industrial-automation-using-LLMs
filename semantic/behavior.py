"""Semantic behavior layer: aggregates evidence, operations, and relationships
into recognized industrial behaviors.

Sits above the evidence/operation/relationship layers and below intent.
"""

from enum import Enum, auto


class BehaviorType(Enum):
    """Canonical behavior types recognized by the behavior engine."""

    CHECKSUM_GENERATION = "CHECKSUM_GENERATION"
    FLOW_MEASUREMENT = "FLOW_MEASUREMENT"
    STATE_MACHINE_CONTROL = "STATE_MACHINE_CONTROL"
    SEQUENTIAL_MACHINE_CONTROL = "SEQUENTIAL_MACHINE_CONTROL"
    MATRIX_COMPUTATION = "MATRIX_COMPUTATION"
    MATHEMATICAL_SOLVER = "MATHEMATICAL_SOLVER"
    DATA_TRANSFORMATION = "DATA_TRANSFORMATION"
    COUNTER_PROCESSING = "COUNTER_PROCESSING"


class Behavior:
    """A single recognized behavior with supporting semantic data.

    Behaviors are inferred from evidence counts, operation types, and
    relationship patterns.  They do not depend on filenames or dataset
    identity.
    """

    def __init__(
        self,
        behavior_type,
        confidence,
        supporting_evidence=None,
        supporting_operations=None,
        supporting_relationships=None,
    ):
        self.behavior_type = behavior_type
        self.confidence = confidence
        self.supporting_evidence = supporting_evidence or []
        self.supporting_operations = supporting_operations or []
        self.supporting_relationships = supporting_relationships or []

    def to_dict(self):
        return {
            "behavior_type": (
                self.behavior_type.value
                if isinstance(self.behavior_type, BehaviorType)
                else self.behavior_type
            ),
            "confidence": self.confidence,
            "supporting_evidence": self.supporting_evidence,
            "supporting_operations": self.supporting_operations,
            "supporting_relationships": self.supporting_relationships,
        }

    def __repr__(self):
        return (
            f"Behavior({self.behavior_type.value if isinstance(self.behavior_type, BehaviorType) else self.behavior_type!r}, "
            f"confidence={self.confidence!r})"
        )
