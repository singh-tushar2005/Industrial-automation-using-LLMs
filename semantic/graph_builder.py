"""Semantic graph assembly layer for industrial topology construction.

The SemanticGraphBuilder consumes relationship extraction output and
constructs a connected SemanticGraph topology. It is a transformation
layer: it converts flat relationship edges into structured graph nodes,
edges, and adjacency mappings.

This module does NOT perform AST traversal or semantic inference. It
relies on the RelationshipExtractor to produce relationship edges and
only handles graph assembly, node normalization, and node-kind inference.
"""

import re

try:
    from semantic.semantic_graph import (
        NODE_KINDS,
        SemanticGraph,
        SemanticGraphEdge,
        SemanticGraphNode,
    )
except ModuleNotFoundError:
    from semantic_graph import (
        NODE_KINDS,
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

            source_kind = self._resolve_node_kind(
                metadata.get("source_kind"), source_id
            )
            target_kind = self._resolve_node_kind(
                metadata.get("target_kind"), target_id
            )

            source_node = SemanticGraphNode(
                node_id=source_id,
                node_kind=source_kind,
                metadata={"inferred_kind": metadata.get("source_kind") is None},
            )
            target_node = SemanticGraphNode(
                node_id=target_id,
                node_kind=target_kind,
                metadata={"inferred_kind": metadata.get("target_kind") is None},
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

    def _resolve_node_kind(self, metadata_kind, node_id):
        """Return a valid node kind, falling back to naming inference when needed.

        Naming rules apply only when semantic metadata is absent or invalid.
        """
        if metadata_kind and metadata_kind in NODE_KINDS and metadata_kind != "unknown":
            return metadata_kind
        return self.infer_node_kind(node_id)

    # ------------------------------------------------------------------
    # Node kind inference
    # ------------------------------------------------------------------

    def infer_node_kind(self, name):
        """Infer the industrial semantic kind of a node from its name.

        The inference uses symbolic naming heuristics commonly found in
        IEC 61131-3 Structured Text programs. This is a best-effort
        classification and defaults to "unknown" when no pattern matches.
        """

        if self.is_configuration(name):
            return "configuration"

        if self.is_resource(name):
            return "resource"

        if self.is_task(name):
            return "task"

        if self.is_program(name):
            return "program"

        if self.is_state(name):
            return "state"

        if self.is_function_block(name):
            return "function_block"

        if self.is_function(name):
            return "function"

        if self.is_timer(name):
            return "timer"

        if self.is_counter(name):
            return "counter"

        if self.is_alarm(name):
            return "alarm"

        if self.is_history(name):
            return "history"

        if self.is_register(name):
            return "register"

        if self.is_sensor(name):
            return "sensor"

        if self.is_actuator(name):
            return "actuator"

        if self.is_process_variable(name):
            return "process_variable"

        if self.is_mode(name):
            return "mode"

        if self.is_signal(name):
            return "signal"

        return "unknown"

    def is_register(self, name):
        """Return True if the name matches PLC register/relay patterns."""

        return bool(
            re.match(r"^(Ri\d+|r\d+|R\d+|Zi\d+|Z\d+)$", name)
        )

    def is_history(self, name):
        """Return True if the name matches history/memory retention patterns."""

        return (
            name == "last"
            or name.endswith("_last")
            or name.startswith("previous")
            or name.startswith("old")
        )

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
        ) or bool(re.match(r"^(Ho\d+|Ro\d+|Zo\d+|Yo\d+|Q\d+)$", name))

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
        ) or bool(re.match(r".*(_Cnt|_Count)$", name)) or name.startswith("Counter")

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
        ) or bool(re.match(r"^Si\d+$", name))

    def is_sensor(self, name):
        """Return True if the name matches known sensor patterns."""

        return any(
            term in name
            for term in (
                "Sensor",
                "Switch",
                "Proximity",
                "Encoder",
                "Transducer",
                "Detector",
                "Probe",
                "Photo",
                "Inductive",
                "Capacitive",
            )
        ) or bool(re.match(r"^(Xi\d+|X\d+)$", name))

    def is_configuration(self, name):
        return name.startswith("Config")

    def is_resource(self, name):
        return name.startswith("Res") or name.startswith("PLC")

    def is_task(self, name):
        return name.startswith("task") or "Task" in name

    def is_program(self, name):
        return name.startswith("Prog") or name.endswith("Program") or name.startswith("Main")

    def is_state(self, name):
        return name in ("State", "LightState", "Step", "StartupStep", "BatchStep", "Mode")

    def is_function_block(self, name):
        fb_upper = name.upper()
        return fb_upper.startswith(("FB_", "TON", "TOF", "TP", "CTU", "CTD", "CTUD", "FT_", "PID")) or name.endswith("Block")

    def is_function(self, name):
        return name.upper().startswith(("F_", "FC_", "SHR", "SHL", "ROL", "ROR", "NOT", "AND", "OR", "XOR")) or name in ("FLOOR", "MODR", "SIGN_R", "BIT_OF_DWORD", "REVERSE", "REFLECT", "BIT_LOAD_B", "_BYTE_TO_INT", "T_PLC_MS", "T_PLC_US")
