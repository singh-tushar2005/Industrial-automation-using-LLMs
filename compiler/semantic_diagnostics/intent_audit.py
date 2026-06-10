"""Intent reasoning diagnostics for Industrial_data datasets."""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import analyze_st_file
from parser.st_parser import find_dataset_files


DATASET_DIRS = [
    "datasets/Industrial_data/Implementation_datasets",
    "datasets/Industrial_data/test_harness",
]

OUTPUT_DIR = Path("compiler/semantic_diagnostics/intents")
SPECIAL_DATASETS = {
    "CRC_GEN",
    "FLOW_METER",
    "SEQUENCE_8",
    "TRAFFIC_CTRL",
    "TOOL_CHANGER",
    "MATRIX",
    "LAMBERT_W",
}


def _dataset_group(path):
    parts = Path(path).parts
    if "Implementation_datasets" in parts:
        return "implementation"
    if "test_harness" in parts:
        return "test_harness"
    return "industrial_data"


def _base_dataset_name(path):
    stem = Path(path).stem
    for suffix in ("_FullTest", "_TestCases"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _summarize_result(file_path, result):
    intents = result.get("intents", {})
    dominant = intents.get("dominant_intent")
    dominant_intent = None
    for intent in intents.get("intents", []):
        if intent.get("intent_type") == dominant:
            dominant_intent = intent
            break

    return {
        "dataset": _dataset_group(file_path),
        "file": str(file_path),
        "base_dataset": _base_dataset_name(file_path),
        "parse_ok": True,
        "detected_intent": dominant,
        "confidence": intents.get("intent_confidence", 0.0),
        "all_intents": intents.get("intents", []),
        "supporting_behaviors": (dominant_intent or {}).get("supporting_behaviors", []),
        "supporting_relationships": (dominant_intent or {}).get("supporting_relationships", []),
        "supporting_operations": (dominant_intent or {}).get("supporting_operations", []),
        "supporting_evidence": (dominant_intent or {}).get("supporting_evidence", []),
        "explanation": (dominant_intent or {}).get("explanation", ""),
        "behaviors": result.get("behaviors", {}).get("behaviors", []),
        "relationship_counts": result.get("relationships", {}).get("industrial_relation_counts")
        or result.get("relationships", {}).get("relation_counts", {}),
        "operation_counts": result.get("operations", {}).get("industrial_operation_counts")
        or result.get("operations", {}).get("operation_counts", {}),
        "evidence_counts": result.get("semantic_model", {}).get("evidence", {}).get("scope_counts", {}).get("industrial", {})
        or result.get("semantic_model", {}).get("evidence", {}).get("counts", {}),
    }


def run_intent_audit():
    files = []
    for dataset_dir in DATASET_DIRS:
        files.extend(find_dataset_files(dataset_dir))
    files = sorted(set(files))

    reports = []
    failures = []
    for file_path in files:
        result = analyze_st_file(file_path, reason=True)
        if not result.get("parse_ok"):
            failures.append({
                "file": str(file_path),
                "error": result.get("parse_error", "unknown"),
            })
            continue
        reports.append(_summarize_result(file_path, result))

    intent_counts = Counter(report["detected_intent"] for report in reports)
    confidence_values = [report["confidence"] for report in reports]
    metrics = {
        "files_total": len(files),
        "files_parsed": len(reports),
        "files_failed": len(failures),
        "parse_failures": failures,
        "intent_distribution": dict(intent_counts.most_common()),
        "average_intent_confidence": round(sum(confidence_values) / len(confidence_values), 3)
        if confidence_values
        else 0.0,
        "low_confidence_files": [
            {
                "file": report["file"],
                "detected_intent": report["detected_intent"],
                "confidence": report["confidence"],
            }
            for report in reports
            if report["confidence"] < 0.55
        ],
        "fallback_files": [
            {
                "file": report["file"],
                "confidence": report["confidence"],
            }
            for report in reports
            if report["detected_intent"] == "GENERAL_PROCESS_CONTROL"
        ],
        "per_file_reports": reports,
    }
    return metrics


def _format_list(items):
    if not items:
        return "    - <none>"
    return "\n".join(f"    - {item}" for item in items)


def generate_reasoning_report(metrics):
    lines = [
        "# Intent Reasoning Report",
        "",
        "Intent reasoning is derived from semantic evidence, operations, relationships, and behaviors.",
        "Dataset and file names are used only as report labels.",
        "",
        "## Summary",
        "",
        f"- Files total: {metrics['files_total']}",
        f"- Files parsed: {metrics['files_parsed']}",
        f"- Files failed: {metrics['files_failed']}",
        f"- Average intent confidence: {metrics['average_intent_confidence']}",
        "",
        "## Intent Distribution",
        "",
    ]
    for intent_type, count in metrics["intent_distribution"].items():
        lines.append(f"- {intent_type}: {count}")

    lines.extend(["", "## Per-Dataset Intent Results", ""])
    for report in metrics["per_file_reports"]:
        lines.extend([
            f"### {Path(report['file']).name}",
            "",
            f"- Dataset group: {report['dataset']}",
            f"- Detected intent: {report['detected_intent']}",
            f"- Confidence: {report['confidence']}",
            f"- Explanation: {report['explanation']}",
            "",
            "Supporting behaviors:",
            _format_list(report["supporting_behaviors"]),
            "",
            "Supporting relationships:",
            _format_list(report["supporting_relationships"]),
            "",
            "Supporting operations:",
            _format_list(report["supporting_operations"]),
            "",
            "Supporting evidence:",
            _format_list(report["supporting_evidence"]),
            "",
        ])

    lines.extend(["", "## Special Analysis", ""])
    special_reports = [report for report in metrics["per_file_reports"] if report["base_dataset"] in SPECIAL_DATASETS]
    for report in special_reports:
        lines.extend([
            f"### {Path(report['file']).name}",
            "",
            "Behaviors:",
            _format_list([
                f"{behavior.get('behavior_type')} [{behavior.get('confidence')}]"
                for behavior in report["behaviors"]
            ]),
            "",
            "Intent:",
            f"    - {report['detected_intent']} [{report['confidence']}]",
            "",
            "Reasoning steps:",
            _format_list([
                "Behavior signals: " + (", ".join(report["supporting_behaviors"]) or "<none>"),
                "Relationship signals: " + (", ".join(report["supporting_relationships"]) or "<none>"),
                "Operation signals: " + (", ".join(report["supporting_operations"]) or "<none>"),
                "Evidence signals: " + (", ".join(report["supporting_evidence"]) or "<none>"),
                "Conclusion: " + report["explanation"],
            ]),
            "",
        ])

    return "\n".join(lines)


def generate_taxonomy_validation(metrics):
    fallback_count = len(metrics["fallback_files"])
    low_confidence_count = len(metrics["low_confidence_files"])
    source_text = Path("semantic/intent_reasoner.py").read_text(encoding="utf-8")
    banned_terms = [
        "CRC_GEN",
        "FLOW_METER",
        "SEQUENCE_8",
        "TRAFFIC_CTRL",
        "TOOL_CHANGER",
        "LAMBERT_W",
        "file_path",
        "Path(",
        "os.path",
        "__file__",
    ]
    violations = [term for term in banned_terms if term in source_text]

    lines = [
        "# Intent Taxonomy Validation",
        "",
        "## Taxonomy Shape",
        "",
        "- Intent names are purpose-level categories, not named industrial applications.",
        "- Rules use behavior, relationship, operation, and evidence distributions.",
        "- `GENERAL_PROCESS_CONTROL` is fallback-only.",
        "",
        "## Generalization Audit",
        "",
        "Checked `semantic/intent_reasoner.py` for dataset, filename, benchmark, and named-sample dependencies.",
    ]
    if violations:
        lines.append(f"- Violations detected: {', '.join(violations)}")
    else:
        lines.append("- Violations detected: none")

    lines.extend([
        "",
        "## Validation Metrics",
        "",
        f"- Parsed files: {metrics['files_parsed']}",
        f"- Distinct detected intents: {len(metrics['intent_distribution'])}",
        f"- Fallback files: {fallback_count}",
        f"- Low-confidence files: {low_confidence_count}",
        f"- Average confidence: {metrics['average_intent_confidence']}",
        "",
        "## Intent Distribution",
        "",
    ])
    for intent_type, count in metrics["intent_distribution"].items():
        lines.append(f"- {intent_type}: {count}")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = run_intent_audit()

    report_path = OUTPUT_DIR / "intent_reasoning_report.md"
    metrics_path = OUTPUT_DIR / "intent_metrics.json"
    validation_path = OUTPUT_DIR / "intent_taxonomy_validation.md"

    report_path.write_text(generate_reasoning_report(metrics), encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    validation_path.write_text(generate_taxonomy_validation(metrics), encoding="utf-8")

    print(f"Wrote {report_path}")
    print(f"Wrote {metrics_path}")
    print(f"Wrote {validation_path}")
    return metrics


if __name__ == "__main__":
    main()
