"""Canonical semantic representation for the industrial pipeline.

Aggregates SemanticContext, relationships, and operations into a single
model that downstream reasoners can consume.
"""


try:
    from semantic.semantic_context import SemanticContext
except ModuleNotFoundError:
    from semantic_context import SemanticContext


class SemanticModel:
    """Unified semantic model containing evidence, context, relationships, operations, behaviors, and intents."""

    def __init__(
        self,
        context=None,
        relationships=None,
        operations=None,
        evidence=None,
        behaviors=None,
        intents=None,
        dominant_intent=None,
        intent_confidence=0.0,
    ):
        self.context = context
        self.relationships = relationships or {}
        self.operations = operations or {}
        self.evidence = evidence or {}
        self.classifications = context.to_dict() if context else {}
        self.behaviors = behaviors or []
        self.intents = intents or []
        self.dominant_intent = dominant_intent
        self.intent_confidence = intent_confidence

    def to_dict(self):
        return {
            "context": self.classifications,
            "relationships": self.relationships,
            "operations": self.operations,
            "evidence": self.evidence,
            "behaviors": [b.to_dict() if hasattr(b, "to_dict") else b for b in self.behaviors],
            "intents": [i.to_dict() if hasattr(i, "to_dict") else i for i in self.intents],
            "dominant_intent": self.dominant_intent,
            "intent_confidence": self.intent_confidence,
        }
