"""Semantic graph structures for industrial topology modeling.

This module defines the passive graph data layer used to represent connected
industrial semantic topology. It does not perform semantic extraction,
AST traversal, or industrial inference. It is a container layer that
stores nodes, edges, and adjacency mappings for downstream analysis,
graph traversal, and future IEC 61499 transformation.

Graph structure is intentionally lightweight and symbolic. No external graph
databases or visualization frameworks are used at this layer.
"""


NODE_KINDS = {
    "signal",
    "actuator",
    "timer",
    "alarm",
    "process_variable",
    "counter",
    "mode",
    "unknown",
    "configuration",
    "resource",
    "task",
    "program",
    "state",
    "function_block",
    "function",
    "sensor",
}

EDGE_RELATIONS = {
    "enables",
    "disables",
    "triggers",
    "activates",
    "sequences",
    "depends_on",
    "contains",
    "schedules",
    "uses",
    "transitions_to",
    "controls",
    "feeds",
}


class SemanticGraphNode:
    """Represent one industrial entity within a semantic topology.

    A node corresponds to a variable, signal, actuator, timer, or other
    industrial control element that participates in behavioral dependencies.
    """

    def __init__(self, node_id, node_kind="unknown", metadata=None):
        if node_kind not in NODE_KINDS:
            node_kind = "unknown"

        self.node_id = node_id
        self.node_kind = node_kind
        self.metadata = metadata or {}

    def to_dict(self):
        """Return a serializable dictionary representation."""

        return {
            "node_id": self.node_id,
            "node_kind": self.node_kind,
            "metadata": dict(self.metadata),
        }

    def __repr__(self):
        metadata = f", metadata={self.metadata!r}" if self.metadata else ""
        return (
            "SemanticGraphNode("
            f"node_id={self.node_id!r}, "
            f"node_kind={self.node_kind!r}"
            f"{metadata}"
            ")"
        )

    def __eq__(self, other):
        if not isinstance(other, SemanticGraphNode):
            return NotImplemented
        return self.node_id == other.node_id

    def __hash__(self):
        return hash(self.node_id)


class SemanticGraphEdge:
    """Represent one semantic dependency edge between two industrial entities.

    An edge encodes a behavioral interaction such as "enables", "disables",
    "triggers", or "activates". Edges are directed and carry metadata for
    future transformation and reasoning stages.
    """

    def __init__(self, source, relation, target, metadata=None):
        if relation not in EDGE_RELATIONS:
            relation = "depends_on"

        self.source = source
        self.relation = relation
        self.target = target
        self.metadata = metadata or {}

    def to_dict(self):
        """Return a serializable dictionary representation."""

        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "metadata": dict(self.metadata),
        }

    def __repr__(self):
        metadata = f", metadata={self.metadata!r}" if self.metadata else ""
        return (
            "SemanticGraphEdge("
            f"source={self.source!r}, "
            f"relation={self.relation!r}, "
            f"target={self.target!r}"
            f"{metadata}"
            ")"
        )

    def __eq__(self, other):
        if not isinstance(other, SemanticGraphEdge):
            return NotImplemented
        return (
            self.source == other.source
            and self.relation == other.relation
            and self.target == other.target
        )

    def __hash__(self):
        return hash((self.source, self.relation, self.target))


class SemanticGraph:
    """Connected semantic topology container for industrial behavior modeling.

    SemanticGraph stores nodes and edges and maintains adjacency mappings
    for fast traversal queries. It is a passive data structure: it does not
    infer meaning, extract relationships, or perform AST analysis. It
    supports future dependency analysis, graph traversal, IEC 61499 event
    network generation, and industrial IR construction.

    The graph is directed. Multiple edges between the same pair of nodes
    are deduplicated.
    """

    def __init__(self):
        self._nodes = {}
        self._edges = []
        self._outgoing = {}
        self._incoming = {}

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_node(self, node):
        """Add a SemanticGraphNode if it does not already exist."""

        if not isinstance(node, SemanticGraphNode):
            raise TypeError("Expected SemanticGraphNode instance")

        if node.node_id not in self._nodes:
            self._nodes[node.node_id] = node
            self._outgoing[node.node_id] = []
            self._incoming[node.node_id] = []

    def has_node(self, node_id):
        """Return True if a node with the given identifier exists."""

        return node_id in self._nodes

    def get_node(self, node_id):
        """Return the SemanticGraphNode for the given identifier, or None."""

        return self._nodes.get(node_id)

    def nodes(self):
        """Return all nodes in the graph."""

        return list(self._nodes.values())

    def node_count(self):
        """Return the number of nodes in the graph."""

        return len(self._nodes)

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------

    def add_edge(self, edge):
        """Add a SemanticGraphEdge and update adjacency mappings."""

        if not isinstance(edge, SemanticGraphEdge):
            raise TypeError("Expected SemanticGraphEdge instance")

        if edge in self._edges:
            return

        self._edges.append(edge)
        self._outgoing[edge.source].append(edge)
        self._incoming[edge.target].append(edge)

    def edge_count(self):
        """Return the number of edges in the graph."""

        return len(self._edges)

    def edges(self):
        """Return all edges in the graph."""

        return list(self._edges)

    # ------------------------------------------------------------------
    # Adjacency queries
    # ------------------------------------------------------------------

    def neighbors(self, node_id):
        """Return the set of distinct target node identifiers reachable from node_id."""

        if node_id not in self._outgoing:
            return set()

        return {edge.target for edge in self._outgoing[node_id]}

    def outgoing_edges(self, node_id):
        """Return all edges whose source is node_id."""

        return list(self._outgoing.get(node_id, []))

    def incoming_edges(self, node_id):
        """Return all edges whose target is node_id."""

        return list(self._incoming.get(node_id, []))

    def predecessors(self, node_id):
        """Return the set of distinct source node identifiers that reach node_id."""

        if node_id not in self._incoming:
            return set()

        return {edge.source for edge in self._incoming[node_id]}

    # ------------------------------------------------------------------
    # Summary and serialization
    # ------------------------------------------------------------------

    def summary(self):
        """Return a structured summary of the graph topology.

        The summary includes node counts, edge counts, node-kind
        distribution, and a compact dependency listing suitable for
        pipeline reporting and future IR consumption.
        """

        node_kind_counts = {}
        for node in self._nodes.values():
            node_kind_counts[node.node_kind] = node_kind_counts.get(node.node_kind, 0) + 1

        dependencies = []
        for edge in self._edges:
            dependencies.append(f"{edge.source} -> {edge.relation} -> {edge.target}")

        return {
            "node_count": self.node_count(),
            "edge_count": self.edge_count(),
            "node_kinds": dict(sorted(node_kind_counts.items())),
            "dependencies": dependencies,
        }

    def to_dict(self):
        """Return a complete serializable dictionary of the graph."""

        return {
            "nodes": [node.to_dict() for node in self._nodes.values()],
            "edges": [edge.to_dict() for edge in self._edges],
            "summary": self.summary(),
        }

    def __repr__(self):
        return (
            "SemanticGraph("
            f"nodes={self.node_count()}, "
            f"edges={self.edge_count()}"
            ")"
        )
