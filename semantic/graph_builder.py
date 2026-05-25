"""Semantic graph assembly layer for industrial topology construction.

The SemanticGraphBuilder consumes relationship extraction output and
constructs a connected SemanticGraph topology. It is a transformation
layer: it converts flat relationship edges into structured graph nodes,
edges, and adjacency mappings.

This module does NOT perform AST traversal or semantic inference. It
relies on the RelationshipExtractor to produce relationship edges and
only handles graph assembly, node normalization, and node-kind inference.
"""

try:
    from semantic.semantic_graph import (
        SemanticGraph,
        SemanticGraphEdge,
        SemanticGraphNode,
    )
except ModuleNotFoundError:
    from semantic_graph import (
        SemanticGraph,
        SemanticGraphEdge,
        SemanticGraphNode,
    )


class SemanticGraphBuilder:
    """Transform flat relationship edges into a connected semantic graph.

    The builder iterates over relationship extraction results, creates
    graph nodes for every source and target entity, infers industrial
    node kinds from naming conventions, and assembles directed edges
    into a SemanticGraph object.
    """

    def __init__(self):
        self.graph = SemanticGraph()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, relationship_report):
        """Consume a relationship report and return a populated SemanticGraph.

        Args:
            relationship_report: dict with key "relationships" containing
                a list of relationship dictionaries. Each dictionary must
                have keys "source", "relation", and "target".

        Returns:
            SemanticGraph with nodes, edges, and adjacency mappings populated.
        """

        relationships = relationship_report.get("relationships", [])

        for relationship in relationships:
            source_id = relationship.get("source", "")
            target_id = relationship.get("target", "")
            relation = relationship.get("relation", "depends_on")
            metadata = relationship.get("metadata", {})

            if not source_id or not target_id:
                continue

            source_kind = self.infer_node_kind(source_id)
            target_kind = self.infer_node_kind(target_id)

            source_node = SemanticGraphNode(
                node_id=source_id,
                node_kind=source_kind,
                metadata={"inferred_kind": True},
            )
            target_node = SemanticGraphNode(
                node_id=target_id,
                node_kind=target_kind,
                metadata={"inferred_kind": True},
            )

            self.graph.add_node(source_node)
            self.graph.add_node(target_node)

            edge = SemanticGraphEdge(
                source=source_id,
                relation=relation,
                target=target_id,
                metadata=metadata,
            )
            self.graph.add_edge(edge)

        return self.graph

    # ------------------------------------------------------------------
    # Node kind inference
    # ------------------------------------------------------------------

    def infer_node_kind(self, name):
        """Infer the industrial semantic kind of a node from its name.

        The inference uses symbolic naming heuristics commonly found in
        IEC 61131-3 Structured Text programs. This is a best-effort
        classification and defaults to "unknown" when no pattern matches.
        """

        if self.is_timer(name):
            return "timer"

        if self.is_counter(name):
            return "counter"

        if self.is_alarm(name):
            return "alarm"

        if self.is_actuator(name):
            return "actuator"

        if self.is_process_variable(name):
            return "process_variable"

        if self.is_mode(name):
            return "mode"

        if self.is_signal(name):
            return "signal"

        return "unknown"

    def is_actuator(self, name):
        """Return True if the name matches known actuator patterns."""

        return any(
            term in name
            for term in (
                "Motor",
                "Pump",
                "Valve",
                "Heater",
                "Mixer",
                "Conveyor",
                "Clamp",
                "Cutter",
                "Contactor",
                "Cylinder",
                "Fan",
                "Blower",
                "Compressor",
                "Solenoid",
            )
        )

    def is_timer(self, name):
        """Return True if the name matches known timer patterns."""

        return any(
            term in name
            for term in (
                "TON",
                "TOF",
                "TP",
                "Timer",
            )
        )

    def is_alarm(self, name):
        """Return True if the name matches known alarm patterns."""

        return any(
            term in name
            for term in (
                "Alarm",
                "Warning",
                "Fault",
                "Trip",
            )
        )

    def is_process_variable(self, name):
        """Return True if the name matches known process variable patterns."""

        return any(
            term in name
            for term in (
                "Pressure",
                "Temp",
                "Temperature",
                "Level",
                "Limit",
                "Flow",
                "Speed",
                "Position",
                "Current",
                "Voltage",
                "Torque",
            )
        )

    def is_counter(self, name):
        """Return True if the name matches known counter patterns."""

        return any(
            term in name
            for term in (
                "CTU",
                "CTD",
                "CTUD",
                "Counter",
            )
        )

    def is_mode(self, name):
        """Return True if the name matches known mode or state patterns."""

        return any(
            term in name
            for term in (
                "Mode",
                "Auto",
                "Manual",
                "State",
                "Step",
                "Sequence",
            )
        )

    def is_signal(self, name):
        """Return True if the name matches known control signal patterns."""

        return any(
            term in name
            for term in (
                "Safety",
                "Guard",
                "Door",
                "Start",
                "Stop",
                "Button",
                "Command",
                "Enable",
                "Ready",
                "AutoMode",
                "ManualMode",
                "EStop",
                "Emergency",
                "Interlock",
                "Permissive",
                "Run",
                "Done",
                "Q",
            )
        )
