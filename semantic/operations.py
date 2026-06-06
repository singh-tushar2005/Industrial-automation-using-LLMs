"""Industrial operation data structures for semantic coverage."""


class Operation:
    """Represent a single computational or control operation extracted from an AST.

    Operations are distinct from relationships: they describe what the code
    *does* (e.g., a lookup, a comparison, a calculation) rather than what
    it depends on or controls.
    """

    def __init__(
        self,
        operation_type,
        target=None,
        sources=None,
        ast_node_type=None,
        metadata=None,
    ):
        self.operation_type = operation_type
        self.target = target
        self.sources = sources or []
        self.ast_node_type = ast_node_type
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "operation_type": self.operation_type,
            "target": self.target,
            "sources": self.sources,
            "ast_node_type": self.ast_node_type,
            "metadata": self.metadata,
        }

    def __repr__(self):
        return (
            f"Operation({self.operation_type!r}, target={self.target!r}, "
            f"sources={self.sources!r}, ast={self.ast_node_type!r})"
        )
