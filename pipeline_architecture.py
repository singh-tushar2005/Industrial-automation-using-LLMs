"""Generate a clean, professional pipeline architecture diagram using Graphviz.

This script produces a minimal, presentation-ready visual of the industrial
semantic analysis pipeline from IEC 61131-3 Structured Text input through
to semantic graph generation and future transformation infrastructure.

Output:
    outputs/architecture/pipeline_architecture.png
    outputs/architecture/pipeline_architecture.svg
"""

import os
from pathlib import Path

import graphviz


OUTPUT_DIR = Path("outputs/architecture")
OUTPUT_NAME = "pipeline_architecture"

# Minimal color palette
C_STAGE = "#1a5276"      # deep steel blue — main pipeline stages
C_CORE = "#b9770e"       # warm amber — central traversal engine
C_SUB = "#ffffff"        # white — subsystem interiors
C_FUTURE = "#95a5a6"     # soft gray — future section
C_TEXT = "#2c3e50"      # near-black text
C_ARROW = "#34495e"     # arrow color


def build_architecture_diagram():
    """Build and return the Graphviz Digraph for the pipeline architecture."""

    dot = graphviz.Digraph(
        name="pipeline_architecture",
        format="png",
        engine="dot",
    )

    # Global graph attributes
    dot.attr(
        rankdir="LR",
        bgcolor="white",
        fontname="DejaVu Sans",
        fontsize="16",
        label="Industrial Semantic Analysis Pipeline",
        labelloc="t",
        labeljust="c",
        nodesep="0.6",
        ranksep="1.3",
        splines="ortho",
        overlap="false",
        penwidth="1.5",
    )

    # Node defaults
    dot.attr(
        "node",
        fontname="DejaVu Sans",
        fontsize="12",
        shape="box",
        style="filled,rounded",
        fillcolor=C_STAGE,
        color="none",
        fontcolor="white",
        penwidth="1.5",
        width="2.6",
        height="1.0",
    )

    # Edge defaults
    dot.attr(
        "edge",
        fontname="DejaVu Sans",
        fontsize="10",
        color=C_ARROW,
        penwidth="2.0",
        arrowhead="vee",
        arrowsize="0.9",
    )

    # ------------------------------------------------------------------
    # Main pipeline stages
    # ------------------------------------------------------------------

    dot.node("datasets", "IEC 61131-3\nStructured Text\nDatasets")
    dot.node("parser", "Parser")
    dot.node("ast", "AST\nGeneration")
    dot.node("visitor", "Visitor\nTraversal Engine")

    # ------------------------------------------------------------------
    # Semantic Analysis cluster
    # ------------------------------------------------------------------
    with dot.subgraph(name="cluster_semantic") as sem:
        sem.attr(
            label="Semantic Analysis",
            style="rounded,filled",
            fillcolor="#eaf2f8",
            color=C_STAGE,
            fontcolor=C_TEXT,
            fontsize="13",
            fontname="DejaVu Sans",
            penwidth="1.5",
            margin="20",
        )

        sem.node("typechecker", "Type\nChecking", fillcolor="#7d3c98")
        sem.node("classifier", "Industrial\nClassification", fillcolor="#c0392b")
        sem.node("extractor", "Relationship\nExtraction", fillcolor="#2874a6")

    # ------------------------------------------------------------------
    # Post-analysis stages
    # ------------------------------------------------------------------

    dot.node("relationships", "Semantic\nRelationships")
    dot.node("graph_gen", "Semantic Graph\nGeneration")
    dot.node("graph", "Semantic\nDependency Graph")

    # ------------------------------------------------------------------
    # Future section
    # ------------------------------------------------------------------
    with dot.subgraph(name="cluster_future") as fut:
        fut.attr(
            label="Future Transformation",
            style="rounded,dashed",
            fillcolor="white",
            color=C_FUTURE,
            fontcolor=C_FUTURE,
            fontsize="12",
            fontname="DejaVu Sans",
            penwidth="1.2",
            margin="18",
        )

        fut.node("ir", "Industrial IR", fillcolor=C_FUTURE, fontcolor="white", style="filled,rounded")
        fut.node("iec61499", "IEC 61499\nTransformation", fillcolor=C_FUTURE, fontcolor="white", style="filled,rounded")
        fut.node("reasoning", "Graph\nReasoning", fillcolor=C_FUTURE, fontcolor="white", style="filled,rounded")

    # ------------------------------------------------------------------
    # Core engine styling
    # ------------------------------------------------------------------
    dot.node("visitor", fillcolor=C_CORE)

    # ------------------------------------------------------------------
    # Edges: main flow
    # ------------------------------------------------------------------

    dot.edge("datasets", "parser")
    dot.edge("parser", "ast")
    dot.edge("ast", "visitor")

    # Visitor -> Semantic Analysis subsystems
    dot.edge("visitor", "typechecker", color="#7d3c98", penwidth="1.5")
    dot.edge("visitor", "classifier", color="#c0392b", penwidth="1.5")
    dot.edge("visitor", "extractor", color="#2874a6", penwidth="1.5")

    # Semantic Analysis -> Relationships
    dot.edge("typechecker", "relationships", color=C_ARROW, penwidth="1.5")
    dot.edge("classifier", "relationships", color=C_ARROW, penwidth="1.5")
    dot.edge("extractor", "relationships", color=C_ARROW, penwidth="1.5")

    # Relationships -> Graph Generation -> Dependency Graph
    dot.edge("relationships", "graph_gen")
    dot.edge("graph_gen", "graph")

    # Future dashed edges
    dot.edge("graph", "ir", color=C_FUTURE, penwidth="1.5", style="dashed")
    dot.edge("graph", "iec61499", color=C_FUTURE, penwidth="1.5", style="dashed")
    dot.edge("graph", "reasoning", color=C_FUTURE, penwidth="1.5", style="dashed")

    return dot


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dot = build_architecture_diagram()

    base_path = OUTPUT_DIR / OUTPUT_NAME
    generated = []

    for fmt in ("png", "svg"):
        out_path = base_path.with_suffix(f".{fmt}")
        dot.render(
            filename=str(base_path),
            format=fmt,
            cleanup=True,
        )
        generated.append(out_path)

    print("Pipeline architecture generated:")
    for path in generated:
        print(f"- {path}")


if __name__ == "__main__":
    main()
