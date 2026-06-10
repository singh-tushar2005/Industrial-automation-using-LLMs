"""Domain-independent intent model.

Intent sits above evidence, operations, relationships, and behaviors. It
describes what the software is trying to accomplish without using filenames,
dataset names, benchmark identity, or application-specific rules.
"""

from enum import Enum


class IntentType(Enum):
    """Canonical high-level software purposes."""

    STATE_BASED_CONTROL = "STATE_BASED_CONTROL"
    SEQUENTIAL_CONTROL = "SEQUENTIAL_CONTROL"
    MULTI_ACTUATOR_COORDINATION = "MULTI_ACTUATOR_COORDINATION"
    EVENT_DRIVEN_CONTROL = "EVENT_DRIVEN_CONTROL"
    RATE_BASED_MEASUREMENT = "RATE_BASED_MEASUREMENT"
    EVENT_COUNTING = "EVENT_COUNTING"
    PROCESS_MONITORING = "PROCESS_MONITORING"
    DATA_INTEGRITY_VERIFICATION = "DATA_INTEGRITY_VERIFICATION"
    DATA_TRANSFORMATION = "DATA_TRANSFORMATION"
    BITWISE_DATA_PROCESSING = "BITWISE_DATA_PROCESSING"
    MATHEMATICAL_COMPUTATION = "MATHEMATICAL_COMPUTATION"
    MATRIX_PROCESSING = "MATRIX_PROCESSING"
    NUMERICAL_SOLVING = "NUMERICAL_SOLVING"
    RESOURCE_COORDINATION = "RESOURCE_COORDINATION"
    RESOURCE_TRANSFER = "RESOURCE_TRANSFER"
    PROCESS_AUTOMATION = "PROCESS_AUTOMATION"
    GENERAL_PROCESS_CONTROL = "GENERAL_PROCESS_CONTROL"


INTENT_SPECIFICITY = {
    IntentType.DATA_INTEGRITY_VERIFICATION.value: 90,
    IntentType.MATRIX_PROCESSING.value: 88,
    IntentType.NUMERICAL_SOLVING.value: 86,
    IntentType.RATE_BASED_MEASUREMENT.value: 84,
    IntentType.SEQUENTIAL_CONTROL.value: 82,
    IntentType.MULTI_ACTUATOR_COORDINATION.value: 81,
    IntentType.STATE_BASED_CONTROL.value: 80,
    IntentType.RESOURCE_TRANSFER.value: 76,
    IntentType.EVENT_COUNTING.value: 74,
    IntentType.BITWISE_DATA_PROCESSING.value: 72,
    IntentType.MATHEMATICAL_COMPUTATION.value: 70,
    IntentType.DATA_TRANSFORMATION.value: 68,
    IntentType.RESOURCE_COORDINATION.value: 66,
    IntentType.EVENT_DRIVEN_CONTROL.value: 64,
    IntentType.PROCESS_MONITORING.value: 62,
    IntentType.PROCESS_AUTOMATION.value: 60,
    IntentType.GENERAL_PROCESS_CONTROL.value: 0,
}


class Intent:
    """A reasoned high-level intent with supporting semantic signals."""

    def __init__(
        self,
        intent_type,
        confidence,
        supporting_behaviors=None,
        supporting_relationships=None,
        supporting_operations=None,
        supporting_evidence=None,
        explanation="",
    ):
        self.intent_type = intent_type
        self.confidence = float(confidence)
        self.supporting_behaviors = supporting_behaviors or []
        self.supporting_relationships = supporting_relationships or []
        self.supporting_operations = supporting_operations or []
        self.supporting_evidence = supporting_evidence or []
        self.explanation = explanation

    def to_dict(self):
        return {
            "intent_type": (
                self.intent_type.value
                if isinstance(self.intent_type, IntentType)
                else self.intent_type
            ),
            "confidence": round(self.confidence, 3),
            "supporting_behaviors": self.supporting_behaviors,
            "supporting_relationships": self.supporting_relationships,
            "supporting_operations": self.supporting_operations,
            "supporting_evidence": self.supporting_evidence,
            "explanation": self.explanation,
        }

    def __repr__(self):
        intent_type = self.intent_type.value if isinstance(self.intent_type, IntentType) else self.intent_type
        return f"Intent({intent_type!r}, confidence={self.confidence!r})"


class IntentReasoningResult:
    """Container returned by the intent reasoner."""

    def __init__(self, intents=None):
        self.intents = sorted(
            intents or [],
            key=lambda item: (
                item.confidence,
                INTENT_SPECIFICITY.get(
                    item.intent_type.value if isinstance(item.intent_type, IntentType) else item.intent_type,
                    0,
                ),
            ),
            reverse=True,
        )
        self.dominant_intent = self.intents[0] if self.intents else None
        self.intent_confidence = self.dominant_intent.confidence if self.dominant_intent else 0.0

    def to_dict(self):
        return {
            "intents": [intent.to_dict() for intent in self.intents],
            "dominant_intent": (
                self.dominant_intent.intent_type.value
                if self.dominant_intent and isinstance(self.dominant_intent.intent_type, IntentType)
                else self.dominant_intent.intent_type
                if self.dominant_intent
                else None
            ),
            "intent_confidence": round(self.intent_confidence, 3),
            "intent_count": len(self.intents),
        }
