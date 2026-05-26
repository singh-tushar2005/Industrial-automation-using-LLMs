"""Semantic graph visualization layer for industrial dependency topology rendering.

This module renders SemanticGraph objects into visual graph diagrams using
Graphviz. It is a pure rendering layer: it does not perform semantic
inference, modify graph topology, extract relationships, or rebuild graph
logic. It only consumes existing graph state and produces visual output.

Output formats:
- PNG (raster, presentation-ready)
- SVG (scalable, web-ready)

Output directory:
- outputs/graphs/
"""

import os
from pathlib import Path

try:
    import graphviz
except ImportError as exc:
    raise ImportError(
        "graphviz Python package is required. Install with: uv pip install graphviz"
    ) from exc

try:
    from semantic.semantic_graph import SemanticGraph
except ModuleNotFoundError:
    from semantic_graph import SemanticGraph


# ------------------------------------------------------------------
# Visual styling maps
# ------------------------------------------------------------------

NODE_SHAPE_MAP = {
    "signal": "ellipse",
    "actuator": "box",
    "timer": "hexagon",
    "alarm": "diamond",
    "process_variable": "cylinder",
    "counter": "doubleoctagon",
    "mode": "box",
    "unknown": "ellipse",
}

NODE_COLOR_MAP = {
    "signal": "#3498db",
    "actuator": "#27ae60",
    "timer": "#f39c12",
    "alarm": "#e74c3c",
    "process_variable": "#9b59b6",
    "counter": "#1abc9c",
    "mode": "#e67e22",
    "unknown": "#7f8c8d",
}

NODE_FILL_MAP = {
    "signal": "#ebf5fb",
    "actuator": "#e9f7ef",
    "timer": "#fef5e7",
    "alarm": "#fdedec",
    "process_variable": "#f4ecf7",
    "counter": "#e8f8f5",
    "mode": "#fef5e7",
    "unknown": "#f2f3f4",
}

EDGE_COLOR_MAP = {
    "enables": "#27ae60",
    "disables": "#c0392b",
    "triggers": "#2980b9",
    "activates": "#8e44ad",
    "sequences": "#d68910",
    "depends_on": "#7f8c8d",
}

EDGE_PENWIDTH_MAP = {
    "enables": "2.0",
    "disables": "2.2",
    "triggers": "1.8",
    "activates": "1.8",
    "sequences": "1.6",
    "depends_on": "1.4",
}

SUBSYSTEM_KEYWORDS = {
    "safety": ["Safety", "Guard", "Door", "EStop", "Emergency", "Interlock"],
    "process": ["Pressure", "Temp", "Temperature", "Level", "Flow", "Speed", "Limit"],
    "actuator": ["Motor", "Pump", "Valve", "Heater", "Mixer", "Conveyor", "Clamp", "Cutter"],
    "timer": ["TON", "TOF", "TP", "Timer"],
}

SUBSYSTEM_LABELS = {
    "safety": "Safety Subsystem",
    "process": "Process Subsystem",
    "actuator": "Actuator Subsystem",
    "timer": "Timer Subsystem",
}

SUBSYSTEM_COLORS = {
    "safety": "#fadbd8",
    "process": "#d6eaf8",
    "actuator": "#d5f5e3",
    "timer": "#fcf3cf",
}


# ------------------------------------------------------------------
# Visualizer
# ------------------------------------------------------------------

class SemanticGraphVisualizer:
    """Render a SemanticGraph into Graphviz visual output.

    The visualizer is the final rendering layer in the pipeline. It
    consumes a populated SemanticGraph and generates industrial dependency
    diagrams. No semantic inference or graph modification occurs here.
    """

    DEFAULT_OUTPUT_DIR = Path("outputs/graphs")
    DEFAULT_FORMATS = ("png",)
    DEFAULT_ENGINE = "dot"

    def __init__(self, output_dir=None, formats=None, engine=None):
        self.output_dir = Path(output_dir or self.DEFAULT_OUTPUT_DIR)
        self.formats = formats or list(self.DEFAULT_FORMATS)
        self.engine = engine or self.DEFAULT_ENGINE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, graph, output_name, title=None):
        """Render one SemanticGraph to all configured output formats.

        Args:
            graph: SemanticGraph object with nodes and edges.
            output_name: base filename (no extension) for output files.
            title: optional graph title override.

        Returns:
            list of Path objects for generated output files.
        """

        self.output_dir.mkdir(parents=True, exist_ok=True)

        dot = self.build_dot(graph, title=title)

        generated = []
        for fmt in self.formats:
            out_path = self.output_dir / f"{output_name}.{fmt}"
            dot.render(
                filename=str(out_path.with_suffix("")),
                format=fmt,
                cleanup=True,
            )
            generated.append(out_path)

        return generated

    def build_dot(self, graph, title=None):
        """Build a graphviz.Digraph from a SemanticGraph.

        This method constructs the complete Graphviz representation:
        graph attributes, node definitions, edge definitions, and optional
        subsystem clusters. It does not write to disk.
        """

        if title is None:
            title = (
                f"Industrial Semantic Dependency Graph\n"
                f"Nodes: {graph.node_count()}   Edges: {graph.edge_count()}"
            )

        dot = graphviz.Digraph(
            name="industrial_semantic_graph",
            format="png",
            engine=self.engine,
        )

        # Global graph attributes
        dot.attr(
            rankdir="LR",
            bgcolor="white",
            fontname="DejaVu Sans",
            fontsize="14",
            label=title,
            labelloc="t",
            labeljust="c",
            nodesep="0.55",
            ranksep="1.1",
            splines="true",
            overlap="false",
        )

        # Global node defaults
        dot.attr(
            "node",
            fontname="DejaVu Sans",
            fontsize="11",
            shape="ellipse",
            style="filled,rounded",
            fillcolor="#f8f9f9",
            color="#2c3e50",
            fontcolor="#2c3e50",
            penwidth="1.5",
        )

        # Global edge defaults
        dot.attr(
            "edge",
            fontname="DejaVu Sans",
            fontsize="10",
            color="#34495e",
            fontcolor="#34495e",
            penwidth="1.5",
            arrowhead="vee",
            arrowsize="0.9",
        )

        # Determine subsystem cluster memberships
        cluster_map = self._assign_clusters(graph)

        # Render nodes (grouped by cluster where applicable)
        self._render_nodes(dot, graph, cluster_map)

        # Render edges
        self._render_edges(dot, graph)

        return dot

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------

    def _assign_clusters(self, graph):
        """Map each node_id to a subsystem cluster label, if any."""

        mapping = {}
        for node in graph.nodes():
            for subsystem, keywords in SUBSYSTEM_KEYWORDS.items():
                if any(kw in node.node_id for kw in keywords):
                    mapping[node.node_id] = subsystem
                    break
        return mapping

    def _render_nodes(self, dot, graph, cluster_map):
        """Render all graph nodes into the Graphviz Digraph.

        Nodes belonging to a recognized subsystem are placed inside a
        cluster subgraph for visual grouping.
        """

        # Group nodes by cluster
        clusters = {}
        unclustered = []

        for node in graph.nodes():
            subsystem = cluster_map.get(node.node_id)
            if subsystem:
                clusters.setdefault(subsystem, []).append(node)
            else:
                unclustered.append(node)

        # Render clustered nodes
        for subsystem, nodes in clusters.items():
            with dot.subgraph(name=f"cluster_{subsystem}") as c:
                c.attr(
                    label=SUBSYSTEM_LABELS[subsystem],
                    style="rounded,filled",
                    fillcolor=SUBSYSTEM_COLORS[subsystem],
                    color="gray60",
                    fontcolor="#2c3e50",
                    fontsize="12",
                    fontname="DejaVu Sans",
                    penwidth="1.2",
                    margin="15",
                )
                for node in nodes:
                    self._add_node(c, node)

        # Render unclustered nodes
        for node in unclustered:
            self._add_node(dot, node)

    def _add_node(self, target, node):
        """Add a single node to a graphviz target (graph or subgraph)."""

        kind = node.node_kind
        shape = NODE_SHAPE_MAP.get(kind, "ellipse")
        color = NODE_COLOR_MAP.get(kind, "#7f8c8d")
        fillcolor = NODE_FILL_MAP.get(kind, "#f2f3f4")

        style = "filled"
        if kind == "mode":
            style = "filled,rounded"
        elif kind in ("timer", "alarm", "counter"):
            style = "filled"

        target.node(
            node.node_id,
            label=node.node_id,
            shape=shape,
            color=color,
            fillcolor=fillcolor,
            style=style,
            fontcolor=color,
            penwidth="2.0" if kind != "unknown" else "1.2",
        )

    def _render_edges(self, dot, graph):
        """Render all graph edges into the Graphviz Digraph."""

        for edge in graph.edges():
            relation = edge.relation
            edge_color = EDGE_COLOR_MAP.get(relation, "#34495e")
            penwidth = EDGE_PENWIDTH_MAP.get(relation, "1.5")

            dot.edge(
                edge.source,
                edge.target,
                label=relation,
                color=edge_color,
                fontcolor=edge_color,
                penwidth=penwidth,
            )
