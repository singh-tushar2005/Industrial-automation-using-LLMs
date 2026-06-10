"""Generate intent-aware dependency reasoning diagnostics."""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import analyze_st_file
from parser.st_parser import find_dataset_files
from semantic.semantic_impact import SemanticImpactAnalyzer


DATASET_DIRS = [
    "datasets/Industrial_data/Implementation_datasets",
    "datasets/Industrial_data/test_harness",
]

OUTPUT_DIR = Path("compiler/semantic_diagnostics/dependency_reasoning")
SPECIAL_DATASETS = {
    "CRC_GEN",
    "FLOW_METER",
    "SEQUENCE_8",
    "TRAFFIC_CTRL",
    "TOOL_CHANGER",
    "MATRIX",
    "LAMBERT_W",
}


def base_dataset_name(path):
    stem = Path(path).stem
    for suffix in ("_FullTest", "_TestCases"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def dataset_group(path):
    parts = Path(path).parts
    if "Implementation_datasets" in parts:
        return "implementation"
    if "test_harness" in parts:
        return "test_harness"
    return "industrial_data"


def run_audit():
    files = []
    for dataset_dir in DATASET_DIRS:
        files.extend(find_dataset_files(dataset_dir))
    files = sorted(set(files))

    behavior_reports = []
    intent_reports = []
    markdown_reports = []
    failures = []

    for file_path in files:
        result = analyze_st_file(file_path, reason=True)
        if not result.get("parse_ok"):
            failures.append({
                "file": str(file_path),
                "error": result.get("parse_error", "unknown"),
            })
            continue

        analyzer = SemanticImpactAnalyzer(
            result["graph"],
            semantic_model=result.get("semantic_model", {}),
            behaviors=result.get("behaviors", {}).get("behaviors", []),
            intents=result.get("intents", {}).get("intents", []),
            operations=result.get("operations", {}),
            relationships=result.get("relationships", {}),
            evidence=result.get("semantic_model", {}).get("evidence", {}),
        )
        impacts = [impact.to_dict() for impact in analyzer.analyze_all()]
        behavior_impacts = [
            {
                "source_node": impact["source_node"],
                "affected_nodes": impact["affected_nodes"],
                "affected_behaviors": impact["affected_behaviors"],
                "severity": impact["severity"],
                "explanation": impact["explanation"],
            }
            for impact in impacts
        ]
        intent_impacts = [
            {
                "source_node": impact["source_node"],
                "affected_nodes": impact["affected_nodes"],
                "affected_intents": impact["affected_intents"],
                "capability_loss": impact["capability_loss"],
                "severity": impact["severity"],
                "explanation": impact["explanation"],
            }
            for impact in impacts
        ]

        common = {
            "file": str(file_path),
            "dataset": dataset_group(file_path),
            "base_dataset": base_dataset_name(file_path),
            "dominant_intent": result.get("intents", {}).get("dominant_intent"),
            "behaviors": result.get("behaviors", {}).get("behaviors", []),
        }
        behavior_reports.append({**common, "node_impacts": behavior_impacts})
        intent_reports.append({**common, "node_impacts": intent_impacts})
        markdown_reports.append({**common, "node_impacts": impacts})

    return {
        "files_total": len(files),
        "files_parsed": len(behavior_reports),
        "files_failed": len(failures),
        "parse_failures": failures,
        "behavior_reports": behavior_reports,
        "intent_reports": intent_reports,
        "markdown_reports": markdown_reports,
    }


def summarize_counts(reports, key):
    counter = Counter()
    for report in reports:
        for impact in report["node_impacts"]:
            counter.update(impact.get(key, []))
    return dict(counter.most_common())


def format_list(items, indent="    "):
    if not items:
        return f"{indent}- <none>"
    return "\n".join(f"{indent}- {item}" for item in items)


def generate_markdown(data):
    behavior_distribution = summarize_counts(data["behavior_reports"], "affected_behaviors")
    intent_distribution = summarize_counts(data["intent_reports"], "affected_intents")
    severity_distribution = Counter()
    for report in data["intent_reports"]:
        for impact in report["node_impacts"]:
            severity_distribution[impact["severity"]] += 1

    lines = [
        "# Intent-Aware Dependency Reasoning Report",
        "",
        "This report extends graph-level dependency reasoning with semantic impact analysis.",
        "It uses existing SemanticEvidence, Operations, Relationships, Behaviors, Intents, and graph reachability.",
        "No parser, extractor, recognizer, intent reasoner, relationship extractor, or dependency reasoner changes are required.",
        "",
        "## Summary",
        "",
        f"- Files total: {data['files_total']}",
        f"- Files parsed: {data['files_parsed']}",
        f"- Files failed: {data['files_failed']}",
        "",
        "## Affected Behavior Distribution",
        "",
    ]
    for behavior, count in behavior_distribution.items():
        lines.append(f"- {behavior}: {count}")

    lines.extend(["", "## Affected Intent Distribution", ""])
    for intent, count in intent_distribution.items():
        lines.append(f"- {intent}: {count}")

    lines.extend(["", "## Criticality Distribution", ""])
    for severity, count in severity_distribution.most_common():
        lines.append(f"- {severity}: {count}")

    lines.extend(["", "## Special Analysis", ""])
    special_reports = [
        report
        for report in data["markdown_reports"]
        if report["base_dataset"] in SPECIAL_DATASETS
    ]
    for report in special_reports:
        lines.extend([
            f"### {Path(report['file']).name}",
            "",
            f"- Dataset group: {report['dataset']}",
            f"- Dominant intent: {report['dominant_intent']}",
            "",
            "Recognized behaviors:",
            format_list([
                f"{behavior.get('behavior_type')} [{behavior.get('confidence')}]"
                for behavior in report["behaviors"]
            ]),
            "",
            "Node -> Behavior -> Intent -> Capability chains:",
            "",
        ])
        semantic_impacts = [
            impact for impact in report["node_impacts"]
            if impact["affected_behaviors"] or impact["affected_intents"] or impact["capability_loss"]
        ]
        if not semantic_impacts:
            lines.append("- `<none>` -> `<none>` -> `<none>` -> graph-only impact")
            lines.append("")
            continue

        for impact in semantic_impacts:
            lines.extend([
                f"- `{impact['source_node']}`",
                f"  - Behavior: {', '.join(impact['affected_behaviors']) or '<none>'}",
                f"  - Intent: {', '.join(impact['affected_intents']) or '<none>'}",
                f"  - Capability: {', '.join(impact['capability_loss']) or '<none>'}",
                f"  - Severity: {impact['severity']}",
                f"  - Reason: {impact['explanation']}",
            ])
        lines.append("")

    lines.extend(["", "## Parse Failures", ""])
    if data["parse_failures"]:
        for failure in data["parse_failures"]:
            lines.append(f"- {Path(failure['file']).name}: {failure['error'].splitlines()[0]}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = run_audit()

    behavior_path = OUTPUT_DIR / "behavior_impact_analysis.json"
    intent_path = OUTPUT_DIR / "intent_impact_analysis.json"
    report_path = OUTPUT_DIR / "intent_aware_reasoning_report.md"

    behavior_payload = {
        "files_total": data["files_total"],
        "files_parsed": data["files_parsed"],
        "files_failed": data["files_failed"],
        "parse_failures": data["parse_failures"],
        "behavior_impact_distribution": summarize_counts(data["behavior_reports"], "affected_behaviors"),
        "reports": data["behavior_reports"],
    }
    intent_payload = {
        "files_total": data["files_total"],
        "files_parsed": data["files_parsed"],
        "files_failed": data["files_failed"],
        "parse_failures": data["parse_failures"],
        "intent_impact_distribution": summarize_counts(data["intent_reports"], "affected_intents"),
        "reports": data["intent_reports"],
    }

    behavior_path.write_text(json.dumps(behavior_payload, indent=2), encoding="utf-8")
    intent_path.write_text(json.dumps(intent_payload, indent=2), encoding="utf-8")
    report_path.write_text(generate_markdown(data), encoding="utf-8")

    print(f"Wrote {report_path}")
    print(f"Wrote {behavior_path}")
    print(f"Wrote {intent_path}")


if __name__ == "__main__":
    main()
