"""Semantic relationship structures for industrial behavior modeling."""


class Relationship:
    """Represent one semantic edge between industrial control entities.

    A semantic relationship is different from an AST parent/child connection.
    The AST says that an IF statement contains a condition and a body. A
    relationship says that the condition has industrial meaning, such as
    "SafetyOK enables Motor" or "PressureHigh disables Pump".

    These relationships are early transformation-oriented edges. Later, they
    can become graph edges for dependency analysis, IEC 61499 event/data
    connection generation, symbolic verification, or LLM-assisted reasoning.
    """

    def __init__(self, source, relation, target, metadata=None):
        self.source = source
        self.relation = relation
        self.target = target
        self.metadata = metadata or {}

    def to_dict(self):
        """Return a graph-friendly dictionary representation."""

        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "metadata": dict(self.metadata),
        }

    def __repr__(self):
        metadata = f", metadata={self.metadata!r}" if self.metadata else ""
        return (
            "Relationship("
            f"source={self.source!r}, "
            f"relation={self.relation!r}, "
            f"target={self.target!r}"
            f"{metadata}"
            ")"
        )
