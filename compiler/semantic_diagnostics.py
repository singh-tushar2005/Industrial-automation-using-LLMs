"""Semantic diagnostics layer for the industrial automation pipeline.

This module audits semantic quality across the entire corpus without
modifying any pipeline behavior. It inspects classification coverage,
graph topology, relationship distributions, and reasoning output,
then produces structured reports and a human-readable summary.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add project root to path so imports resolve when running from compiler/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import analyze_st_file
from parser.st_parser import find_dataset_files


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

DATASET_DIRS = [
    "datasets/educational",
    "datasets/Industrial_data/Implementation_datasets",
    "datasets/Industrial_data/test_harness",
]

OUTPUT_DIR = Path("compiler/semantic_diagnostics")
DATASETS_DIR = OUTPUT_DIR / "datasets_semantic"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def classify_dataset(file_path):
    """Return the high-level dataset category for a file path."""
    parts = Path(file_path).parts
    if "educational" in parts:
        return "educational"
    if "Implementation_datasets" in parts:
        return "implementation"
    if "test_harness" in parts:
        return "test_harness"
    return "other"


def extract_unknown_patterns(node_names):
    """Extract pattern groups from unknown node identifiers."""
    patterns = {
        "Xi*": re.compile(r"^Xi\d+$"),
        "Yi*": re.compile(r"^Yi\d+$"),
        "Zi*": re.compile(r"^Zi\d+$"),
        "Ri*": re.compile(r"^Ri\d+$"),
        "Si*": re.compile(r"^Si\d+$"),
        "Ho*": re.compile(r"^Ho\d+$"),
        "Ro*": re.compile(r"^Ro\d+$"),
        "Yo*": re.compile(r"^Yo\d+$"),
        "Zo*": re.compile(r"^Zo\d+$"),
        "*_Cnt": re.compile(r".*_Cnt$"),
        "*_Count": re.compile(r".*_Count$"),
        "*_Req": re.compile(r".*_Req$"),
        "*_Cmd": re.compile(r".*_Cmd$"),
        "*_last": re.compile(r".*_last$"),
        "T_PLC_*": re.compile(r"^T_PLC_.*$"),
        "r*": re.compile(r"^r\d+$"),
        "BIT_*": re.compile(r"^BIT_.*$"),
        "run": re.compile(r"^run$"),
        "tmp": re.compile(r"^tmp$"),
        "cnt": re.compile(r"^cnt$"),
        "last": re.compile(r"^last$"),
        "status": re.compile(r"^status$"),
        "out": re.compile(r"^out$"),
        "old": re.compile(r"^old$"),
        "i": re.compile(r"^i$"),
        "w": re.compile(r"^w$"),
        "code": re.compile(r"^code$"),
        "DX": re.compile(r"^DX$"),
        "tl": re.compile(r"^tl$"),
        "Pedestrian*": re.compile(r"^Pedestrian.*$"),
        "int1.*": re.compile(r"^int1\..*$"),
        "piwl.*": re.compile(r"^piwl\..*$"),
        "_*": re.compile(r"^_.*$"),
        "temp": re.compile(r"^temp$"),
        "tx": re.compile(r"^tx$"),
        "MODR": re.compile(r"^MODR$"),
        "OUT": re.compile(r"^OUT$"),
        "T*": re.compile(r"^T\d+.*$"),
    }
    result = Counter()
    for name in node_names:
        matched = False
        for pat_name, regex in patterns.items():
            if regex.match(name):
                result[pat_name] += 1
                matched = True
                break
        if not matched:
            result["other"] += 1
    return result


# ------------------------------------------------------------------
# Core diagnostics
# ------------------------------------------------------------------

def run_diagnostics():
    """Run the full semantic audit across all configured datasets."""

    all_files = []
    for dataset_dir in DATASET_DIRS:
        all_files.extend(find_dataset_files(dataset_dir))

    all_files = sorted(set(all_files))

    per_file_reports = []
    parse_failures = []
    global_unknown_counter = Counter()
    global_relationship_counter = Counter()
    global_node_kind_counter = Counter()

    files_with_control_paths = 0
    files_with_state_machines = 0
    files_with_safety_analysis = 0
    files_with_failure_analysis = 0
    total_classified = 0
    total_nodes = 0
    total_unknown = 0

    for file_path in all_files:
        result = analyze_st_file(file_path, reason=True)

        if not result.get("parse_ok"):
            parse_failures.append({
                "file": str(file_path),
                "error": result.get("parse_error", "unknown"),
            })
            continue

        graph = result["graph"]
        reasoning = result.get("reasoning", {})
        relationships = result.get("relationships", {})
        classification = result.get("classification", {})

        # Classification metrics
        nodes = graph.nodes()
        node_count = len(nodes)
        unknown_nodes = [n for n in nodes if n.node_kind == "unknown"]
        classified_nodes = [n for n in nodes if n.node_kind != "unknown"]
        unknown_count = len(unknown_nodes)
        classified_count = len(classified_nodes)

        total_nodes += node_count
        total_unknown += unknown_count
        total_classified += classified_count

        for n in nodes:
            global_node_kind_counter[n.node_kind] += 1

        unknown_names = [n.node_id for n in unknown_nodes]
        patterns = extract_unknown_patterns(unknown_names)
        global_unknown_counter.update(patterns)

        # Relationship metrics
        rels = relationships.get("relationships", [])
        rel_counts = Counter(r["relation"] for r in rels)
        global_relationship_counter.update(rel_counts)

        # Graph quality
        self_loops = 0
        for edge in graph.edges():
            if edge.source == edge.target:
                self_loops += 1

        isolated = 0
        for n in nodes:
            if not graph.neighbors(n.node_id) and not graph.predecessors(n.node_id):
                isolated += 1

        # Reasoning metrics
        has_cp = bool(reasoning.get("control_paths"))
        has_sm = bool(
            reasoning.get("state_machines", {}).get("states")
        )
        has_si = bool(reasoning.get("safety_impact"))
        has_fp = bool(reasoning.get("failure_propagation"))

        if has_cp:
            files_with_control_paths += 1
        if has_sm:
            files_with_state_machines += 1
        if has_si:
            files_with_safety_analysis += 1
        if has_fp:
            files_with_failure_analysis += 1

        report = {
            "dataset": classify_dataset(file_path),
            "file": str(file_path),
            "classification": {
                "total_nodes": node_count,
                "classified_nodes": classified_count,
                "unknown_nodes": unknown_count,
                "coverage_percent": round(100 * classified_count / node_count, 1) if node_count else 0.0,
            },
            "node_kinds": dict(
                Counter(n.node_kind for n in nodes).most_common()
            ),
            "relationships": {
                "total": len(rels),
                "by_type": dict(rel_counts.most_common()),
            },
            "graph_quality": {
                "self_loops": self_loops,
                "isolated_nodes": isolated,
                "unknown_ratio": round(100 * unknown_count / node_count, 1) if node_count else 0.0,
            },
            "reasoning": {
                "control_paths": reasoning.get("control_path_count", 0),
                "state_machines": len(reasoning.get("state_machines", {}).get("states", [])),
                "safety_impact": reasoning.get("safety_impact_count", 0),
                "failure_propagation": reasoning.get("failure_propagation_count", 0),
            },
            "unknown_patterns": dict(patterns.most_common()),
        }

        per_file_reports.append(report)

    # Overall totals
    files_total = len(all_files)
    files_parsed = len(per_file_reports)
    files_failed = len(parse_failures)

    classification_coverage = (
        round(100 * total_classified / total_nodes, 1) if total_nodes else 0.0
    )
    overall_unknown_ratio = (
        round(100 * total_unknown / total_nodes, 1) if total_nodes else 0.0
    )

    # Top datasets by metric
    by_unknown_ratio = sorted(
        per_file_reports,
        key=lambda x: x["graph_quality"]["unknown_ratio"],
        reverse=True,
    )[:10]

    by_control_paths = sorted(
        per_file_reports,
        key=lambda x: x["reasoning"]["control_paths"],
        reverse=True,
    )[:10]

    by_graph_size = sorted(
        per_file_reports,
        key=lambda x: x["classification"]["total_nodes"],
        reverse=True,
    )[:10]

    zero_relationships = [
        r for r in per_file_reports if r["relationships"]["total"] == 0
    ]

    overall = {
        "files_total": files_total,
        "files_parsed": files_parsed,
        "files_failed": files_failed,
        "parse_failures": parse_failures,
        "classification_coverage": classification_coverage,
        "unknown_ratio": overall_unknown_ratio,
        "total_nodes": total_nodes,
        "total_classified": total_classified,
        "total_unknown": total_unknown,
        "node_kind_distribution": dict(global_node_kind_counter.most_common()),
        "relationship_distribution": dict(global_relationship_counter.most_common()),
        "reasoning_coverage": {
            "files_with_control_paths": files_with_control_paths,
            "files_with_state_machines": files_with_state_machines,
            "files_with_safety_analysis": files_with_safety_analysis,
            "files_with_failure_analysis": files_with_failure_analysis,
        },
        "top_unknown_patterns": dict(global_unknown_counter.most_common(20)),
        "top_datasets_unknown_ratio": [
            {"file": r["file"], "unknown_ratio": r["graph_quality"]["unknown_ratio"]}
            for r in by_unknown_ratio
        ],
        "top_datasets_control_paths": [
            {"file": r["file"], "control_paths": r["reasoning"]["control_paths"]}
            for r in by_control_paths
        ],
        "top_datasets_graph_size": [
            {"file": r["file"], "total_nodes": r["classification"]["total_nodes"]}
            for r in by_graph_size
        ],
        "datasets_with_zero_relationships": [
            {"file": r["file"], "dataset": r["dataset"]}
            for r in zero_relationships
        ],
        "per_file_reports": per_file_reports,
    }

    return overall


# ------------------------------------------------------------------
# Output generation
# ------------------------------------------------------------------

def generate_summary_text(overall):
    """Produce a human-readable summary."""

    lines = [
        "=" * 70,
        "SEMANTIC DIAGNOSTICS SUMMARY",
        "=" * 70,
        "",
        f"Files total:     {overall['files_total']}",
        f"Files parsed:    {overall['files_parsed']}",
        f"Files failed:    {overall['files_failed']}",
        "",
        f"Overall classification coverage: {overall['classification_coverage']}%",
        f"Overall unknown ratio:           {overall['unknown_ratio']}%",
        f"Total nodes:                     {overall['total_nodes']}",
        f"Total classified:                {overall['total_classified']}",
        f"Total unknown:                   {overall['total_unknown']}",
        "",
        "Node Kind Distribution",
        "-" * 40,
    ]
    for kind, count in overall["node_kind_distribution"].items():
        lines.append(f"  {kind:<20} {count:>6}")

    lines.extend([
        "",
        "Top 10 Unknown-Node Patterns",
        "-" * 40,
    ])
    for pat, count in list(overall["top_unknown_patterns"].items())[:10]:
        lines.append(f"  {pat:<20} {count:>6}")

    lines.extend([
        "",
        "Top 10 Relationship Types",
        "-" * 40,
    ])
    for rel, count in list(overall["relationship_distribution"].items())[:10]:
        lines.append(f"  {rel:<20} {count:>6}")

    rc = overall["reasoning_coverage"]
    lines.extend([
        "",
        "Reasoning Coverage",
        "-" * 40,
        f"  Files with control paths:      {rc['files_with_control_paths']}",
        f"  Files with state machines:     {rc['files_with_state_machines']}",
        f"  Files with safety analysis:    {rc['files_with_safety_analysis']}",
        f"  Files with failure analysis:   {rc['files_with_failure_analysis']}",
        "",
        "Top 10 Datasets by Unknown Ratio",
        "-" * 40,
    ])
    for r in overall["top_datasets_unknown_ratio"][:10]:
        fname = Path(r["file"]).name
        lines.append(f"  {fname:<30} {r['unknown_ratio']:>6.1f}%")

    lines.extend([
        "",
        "Top 10 Datasets by Control-Path Count",
        "-" * 40,
    ])
    for r in overall["top_datasets_control_paths"][:10]:
        fname = Path(r["file"]).name
        lines.append(f"  {fname:<30} {r['control_paths']:>6}")

    lines.extend([
        "",
        "Top 10 Datasets by Graph Size",
        "-" * 40,
    ])
    for r in overall["top_datasets_graph_size"][:10]:
        fname = Path(r["file"]).name
        lines.append(f"  {fname:<30} {r['total_nodes']:>6}")

    lines.extend([
        "",
        "Datasets with Zero Semantic Relationships",
        "-" * 40,
    ])
    if overall["datasets_with_zero_relationships"]:
        for r in overall["datasets_with_zero_relationships"]:
            fname = Path(r["file"]).name
            lines.append(f"  {fname:<30} ({r['dataset']})")
    else:
        lines.append("  None")

    lines.extend([
        "",
        "Parse Failures",
        "-" * 40,
    ])
    if overall["parse_failures"]:
        for f in overall["parse_failures"]:
            fname = Path(f["file"]).name
            err = f["error"].split("\n")[0][:50]
            lines.append(f"  {fname:<30} {err}")
    else:
        lines.append("  None")

    lines.extend(["", "=" * 70])
    return "\n".join(lines)


def main():
    """Run diagnostics and write outputs."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    print("Running semantic diagnostics...")
    overall = run_diagnostics()

    # Write JSON
    json_path = OUTPUT_DIR / "semantic_diagnostics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(overall, f, indent=2)
    print(f"Wrote {json_path}")

    # Write summary
    summary_path = OUTPUT_DIR / "semantic_diagnostics_summary.txt"
    summary_text = generate_summary_text(overall)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"Wrote {summary_path}")

    # Write per-file reports into datasets_semantic
    for report in overall["per_file_reports"]:
        fname = Path(report["file"]).stem + "_semantic.json"
        out_path = DATASETS_DIR / fname
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    print(f"Wrote {len(overall['per_file_reports'])} per-file reports to {DATASETS_DIR}")

    # Print quick console summary
    print()
    print(summary_text)

    return overall


if __name__ == "__main__":
    main()
