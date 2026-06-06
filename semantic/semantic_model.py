"""Canonical semantic representation for the industrial pipeline.

Aggregates SemanticContext, relationships, and operations into a single
model that downstream reasoners can consume.
"""


try:
    from semantic.semantic_context import SemanticContext
except ModuleNotFoundError:
    from semantic_context import SemanticContext


class SemanticModel:
    """Unified semantic model containing context, classifications, relationships, and operations."""

    def __init__(self, context=None, relationships=None, operations=None):
        self.context = context
        self.relationships = relationships or {}
        self.operations = operations or {}
        self.classifications = context.to_dict() if context else {}

    def to_dict(self):
        return {
            "context": self.classifications,
            "relationships": self.relationships,
            "operations": self.operations,
        }
