"""Standalone industrial compiler diagnostics subsystem.

Analyzes IEC 61131-3 Structured Text datasets for parser, AST, and visitor
compatibility without modifying the main pipeline or semantic architecture.

Operates incrementally: only re-analyzes datasets whose contents have changed.
Scopes to industrial datasets only: ``datasets/industrial_data/`` and nested
subdirectories.

Usage:
    python -m compiler.grammar_diagnostics

Produces per-dataset JSON + markdown reports in
``compiler/parser_diagnostics/datasets/``,
a ``compatibility_index.json`` with historical scores,
and a global ``grammar_summary.json``.
"""

import hashlib
import json
import re
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Existing project infrastructure (read-only usage)
from parser.st_parser import DATASETS_DIR, find_dataset_files, load_st_file, parse_st_program
from semantic.visitor import SemanticTraversalVisitor

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DIAGNOSTICS_DIR = Path(__file__).resolve().parent / "parser_diagnostics"
DATASETS_REPORTS_DIR = DIAGNOSTICS_DIR / "datasets"

INDEX_PATH = DIAGNOSTICS_DIR / "compatibility_index.json"
SUMMARY_PATH = DIAGNOSTICS_DIR / "grammar_summary.json"

# Industrial dataset scope (recursive, never scans educational/toy/test sets).
INDUSTRIAL_DATASETS_DIR = DATASETS_DIR / "Industrial_data"

# ---------------------------------------------------------------------------
# IEC 61131-3 construct catalog
# ---------------------------------------------------------------------------
CONSTRUCT_PATTERNS = {
    "IF": [r"\bIF\b"],
    "CASE_OF": [r"\bCASE\b.*\bOF\b"],
    "assignment": [r":="],
    "boolean_logic": [r"\b(AND|OR|NOT|XOR)\b"],
    "arithmetic_expression": [r"[\+\-\*/](?!=)"],
    "comparison_expression": [r"(>=|<=|<>|>|<|=)(?!=)"],
    "FUNCTION": [r"\bFUNCTION\b(?!_BLOCK)"],
    "FUNCTION_BLOCK": [r"\bFUNCTION_BLOCK\b"],
    "VAR": [r"\bVAR\b\s*\n", r"\bVAR\b\s+\w+"],
    "VAR_INPUT": [r"\bVAR_INPUT\b"],
    "VAR_OUTPUT": [r"\bVAR_OUTPUT\b"],
    "VAR_IN_OUT": [r"\bVAR_IN_OUT\b"],
    "FOR_LOOP": [r"\bFOR\b.*\bTO\b"],
    "WHILE_LOOP": [r"\bWHILE\b.*\bDO\b"],
    "REPEAT_LOOP": [r"\bREPEAT\b.*\bUNTIL\b"],
    "timer_TON": [r"\bTON\b"],
    "timer_TOF": [r"\bTOF\b"],
    "timer_TP": [r"\bTP\b"],
    "counter_CTU": [r"\bCTU\b"],
    "counter_CTD": [r"\bCTD\b"],
    "counter_CTUD": [r"\bCTUD\b"],
    "FB_invocation": [r"\w+\s*\("],
    "time_literal": [r"T#\d+(?:ms|s|m|h|d)"],
    "numeric_literal": [r"\b\d+(?:\.\d+)?\b"],
    "boolean_literal": [r"\b(TRUE|FALSE)\b"],
    "state_machine": [r"\bSTATE\b|\bTRANSITION\b|\bSTEP\b"],
    "multiline_boolean": [r"\b(AND|OR)\b.*\n.*\b(AND|OR)\b"],
}

SUPPORTED_GRAMMAR_CONSTRUCTS = {
    "IF",
    "CASE_OF",
    "assignment",
    "boolean_logic",
    "arithmetic_expression",
    "comparison_expression",
    "time_literal",
    "numeric_literal",
    "boolean_literal",
    "FB_invocation",
}

SUPPORTED_AST_NODES = {
    "ProgramNode",
    "BlockNode",
    "IfStatementNode",
    "CaseStatementNode",
    "CaseBranchNode",
    "AssignmentNode",
    "BinaryExpressionNode",
    "LogicalExpressionNode",
    "VariableNode",
    "BooleanNode",
    "NumberNode",
    "TimeLiteralNode",
    "FunctionBlockCallNode",
}

SUPPORTED_VISITOR_METHODS = {
    "visit_ProgramNode",
    "visit_BlockNode",
    "visit_IfStatementNode",
    "visit_CaseStatementNode",
    "visit_CaseBranchNode",
    "visit_AssignmentNode",
    "visit_BinaryExpressionNode",
    "visit_LogicalExpressionNode",
    "visit_VariableNode",
    "visit_BooleanNode",
    "visit_NumberNode",
    "visit_TimeLiteralNode",
    "visit_FunctionBlockCallNode",
}

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------
SEVERITY_INFO = "INFO"
SEVERITY_WARNING = "WARNING"
SEVERITY_ERROR = "ERROR"
SEVERITY_CRITICAL = "CRITICAL"


# =============================================================================
# I/O helpers
# =============================================================================

def _file_hash(path):
    """Return a stable SHA-256 hex digest of a file's contents."""

    hasher = hashlib.sha256()
    hasher.update(Path(path).read_bytes())
    return hasher.hexdigest()


def _load_json(path):
    """Load JSON if it exists, otherwise return None."""

    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return None


def _save_json(path, data):
    """Write *data* to *path* as pretty-printed JSON."""

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# =============================================================================
# Compatibility index
# =============================================================================

def _load_compatibility_index():
    """Load the compatibility index, or return a fresh empty structure."""

    index = _load_json(INDEX_PATH)
    if index is None:
        index = {
            "meta": {
                "version": "1.1.0",
                "created_at": _now_iso(),
            },
            "datasets": {},
        }
    return index


def _save_compatibility_index(index):
    """Persist the compatibility index."""

    index["meta"]["updated_at"] = _now_iso()
    _save_json(INDEX_PATH, index)


def _now_iso():
    """Return current UTC timestamp as ISO-8601 string."""

    return datetime.now(timezone.utc).isoformat()


def _update_index_entry(index, dataset_name, report, file_hash):
    """Merge a new analysis result into the compatibility index with history."""

    scores = report["scores"]
    entry = {
        "hash": file_hash,
        "last_analyzed": _now_iso(),
        "parser_compatibility": scores["parser_compatibility"],
        "ast_compatibility": scores["ast_compatibility"],
        "visitor_compatibility": scores["visitor_compatibility"],
        "status": report["overall_status"],
    }

    history_snapshot = {
        "timestamp": entry["last_analyzed"],
        "parser": scores["parser_compatibility"],
        "ast": scores["ast_compatibility"],
        "visitor": scores["visitor_compatibility"],
        "status": report["overall_status"],
    }

    existing = index["datasets"].get(dataset_name)
    if existing is None:
        entry["history"] = [history_snapshot]
    else:
        history = existing.get("history", [])
        # Append new snapshot; keep up to 20 entries to bound size.
        history.append(history_snapshot)
        entry["history"] = history[-20:]

    index["datasets"][dataset_name] = entry


def _remove_index_entry(index, dataset_name):
    """Remove a dataset from the compatibility index."""

    index["datasets"].pop(dataset_name, None)


# =============================================================================
# Report I/O (incremental)
# =============================================================================

def _dataset_stem(file_path):
    """Return the basename without extension for report naming."""

    return Path(file_path).stem


def _existing_report_path(stem):
    """Return the expected JSON report path for a dataset stem."""

    return DATASETS_REPORTS_DIR / f"{stem}.json"


def _load_existing_report(stem):
    """Load an existing per-dataset JSON report if present."""

    return _load_json(_existing_report_path(stem))


def _remove_dataset_reports(stem):
    """Delete JSON and markdown reports for a removed dataset."""

    for suffix in (".json", ".md"):
        path = DATASETS_REPORTS_DIR / f"{stem}{suffix}"
        if path.exists():
            path.unlink()


def _write_json_report(report, stem):
    """Write the JSON report for one dataset."""

    json_path = DATASETS_REPORTS_DIR / f"{stem}.json"
    _save_json(json_path, report)
    return json_path


def _write_markdown_report(report, stem):
    """Write a human-readable markdown summary for one dataset."""

    md_path = DATASETS_REPORTS_DIR / f"{stem}.md"
    meta = report["meta"]
    scores = report["scores"]
    issues = report["issues"]

    lines = [
        f"# Industrial Compiler Diagnostics: {meta['dataset']}",
        "",
        f"- **File:** `{meta['file_path']}`",
        f"- **Generated:** {meta['generated_at']}",
        f"- **Overall Status:** {report['overall_status']}",
        "",
        "## Compatibility Scores",
        "",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| Parser Compatibility | {scores['parser_compatibility']}% |",
        f"| AST Compatibility | {scores['ast_compatibility']}% |",
        f"| Visitor Compatibility | {scores['visitor_compatibility']}% |",
    ]

    # Progression tracking vs previous run.
    prog = report.get("progression", {})
    has_prog = any(v is not None for v in prog.values())
    if has_prog:
        lines.extend(["", "## Progression (vs previous run)", ""])
        for metric, label in (("parser", "Parser"), ("ast", "AST"), ("visitor", "Visitor")):
            delta = prog.get(f"{metric}_delta")
            prev = prog.get(f"{metric}_previous")
            if delta is not None:
                if delta > 0:
                    arrow = "↑"
                    sign = "+"
                elif delta < 0:
                    arrow = "↓"
                    sign = ""
                else:
                    arrow = "→"
                    sign = ""
                lines.append(f"- **{label}:** {arrow} {sign}{delta}%  (was {prev}%)")
            else:
                lines.append(f"- **{label}:** first analysis")

    lines.extend([
        "",
        "## Parse Status",
        "",
        f"- **Status:** {report['parse_status']}",
    ])

    if report["parser_failures"]:
        lines.append("- **Failures:**")
        for failure in report["parser_failures"]:
            loc = ""
            if failure.get("line"):
                loc += f" line {failure['line']}"
            if failure.get("column"):
                loc += f", col {failure['column']}"
            lines.append(
                f"  - [{failure.get('severity', 'ERROR')}] "
                f"{failure.get('reason', 'unknown')}{loc}"
            )
    else:
        lines.append("- **Failures:** none")

    lines.extend([
        "",
        "## AST Status",
        "",
        f"- **Status:** {report['ast_status']}",
    ])

    if report["ast_nodes_present"]:
        lines.append("- **Nodes present:** " + ", ".join(report["ast_nodes_present"]))
    if report["missing_ast_nodes"]:
        lines.append("- **Missing nodes:** " + ", ".join(report["missing_ast_nodes"]))

    lines.extend([
        "",
        "## Visitor Status",
        "",
        f"- **Status:** {report['visitor_status']}",
        f"- **Traversal events:** {report['visitor_traversal_event_count']}",
    ])

    if report["missing_visitor_methods"]:
        lines.append("- **Missing methods:** " + ", ".join(report["missing_visitor_methods"]))

    lines.extend([
        "",
        "## Construct Support",
        "",
        "### Supported",
    ])

    if report["supported_constructs"]:
        for sc in report["supported_constructs"]:
            lines.append(f"- {sc}")
    else:
        lines.append("_None detected._")

    lines.extend([
        "",
        "### Unsupported",
    ])

    if report["unsupported_constructs"]:
        for uc in report["unsupported_constructs"]:
            info = report["detected_constructs"].get(uc, {})
            line_info = ""
            if info.get("line_numbers"):
                line_info = f" (lines {info['line_numbers']})"
            lines.append(f"- {uc}{line_info}")
    else:
        lines.append("_None detected._")

    if issues:
        lines.extend(["", "## Issues", ""])
        for issue in issues:
            lines.append(f"- **[{issue['severity']}]** {issue['message']}")

    lines.append("")

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    return md_path


# =============================================================================
# Core analysis functions (unchanged public interface)
# =============================================================================

def detect_constructs(source_code):
    """Scan source text for IEC 61131-3 constructs and return a dict."""

    results = {}

    for construct_name, patterns in CONSTRUCT_PATTERNS.items():
        line_numbers = []
        for pattern in patterns:
            for match in re.finditer(pattern, source_code, re.IGNORECASE | re.MULTILINE):
                line_num = source_code[: match.start()].count("\n") + 1
                line_numbers.append(line_num)

        results[construct_name] = {
            "detected": bool(line_numbers),
            "line_numbers": sorted(set(line_numbers)),
        }

    return results


def attempt_parse(file_path):
    """Try to parse a .st file. Return (ast_or_none, diagnostics_dict)."""

    diagnostics = {
        "parse_status": "unknown",
        "parse_error": None,
        "parse_error_line": None,
        "parse_error_column": None,
        "parse_traceback": None,
        "partial_ast": False,
    }

    ast = None

    try:
        source_code = load_st_file(file_path)
        ast = parse_st_program(source_code)
        diagnostics["parse_status"] = "success"
    except Exception as exc:
        diagnostics["parse_status"] = "failed"
        diagnostics["parse_error"] = str(exc)
        diagnostics["parse_traceback"] = traceback.format_exc()

        line_no = getattr(exc, "lineno", None)
        col_no = getattr(exc, "col", None)
        if line_no is None:
            line_no = getattr(exc, "line", None)
        if col_no is None:
            col_no = getattr(exc, "column", None)

        diagnostics["parse_error_line"] = line_no
        diagnostics["parse_error_column"] = col_no

        if hasattr(exc, "parser_element") and exc.parser_element is not None:
            diagnostics["partial_ast"] = True

    return ast, diagnostics


def gather_ast_node_types(node, types=None):
    """Recursively collect all AST node class names present in a tree."""

    if types is None:
        types = set()

    if node is None:
        return types

    if isinstance(node, (bool, int, float, str, tuple)):
        return types

    types.add(node.__class__.__name__)

    for attr in ("body", "statements", "condition", "then_body", "else_body",
                 "branches", "left", "right", "operands", "value", "target",
                 "arguments", "selector", "match_value"):
        child = getattr(node, attr, None)
        if child is None:
            continue
        if isinstance(child, list):
            for item in child:
                gather_ast_node_types(item, types)
        else:
            gather_ast_node_types(child, types)

    return types


def analyze_ast(ast):
    """Inspect AST and return diagnostics about coverage."""

    diagnostics = {
        "ast_status": "no_ast",
        "ast_nodes_present": [],
        "ast_nodes_missing": [],
        "ast_coverage_ratio": 0.0,
    }

    if ast is None:
        return diagnostics

    present_types = sorted(gather_ast_node_types(ast))
    diagnostics["ast_nodes_present"] = present_types

    missing = []
    if "ProgramNode" in present_types and len(present_types) <= 2:
        missing.append("StatementNode coverage")

    diagnostics["ast_nodes_missing"] = missing
    diagnostics["ast_status"] = "partial_support" if missing else "full_support"

    total_present = len(present_types)
    supported_present = len([t for t in present_types if t in SUPPORTED_AST_NODES])
    diagnostics["ast_coverage_ratio"] = round(supported_present / total_present, 2) if total_present else 0.0

    return diagnostics


class _SafeVisitor(SemanticTraversalVisitor):
    """Visitor subclass that records missing methods instead of crashing."""

    def __init__(self):
        super().__init__()
        self.missing_methods = []

    def generic_visit(self, node):
        node_type_name = node.__class__.__name__
        method_name = f"visit_{node_type_name}"
        self.missing_methods.append(method_name)
        self.record_line(f"MISSING VISITOR: {method_name} — node skipped")


def analyze_visitor(ast):
    """Try visitor traversal and record gaps."""

    diagnostics = {
        "visitor_status": "no_ast",
        "visitor_methods_present": [],
        "visitor_methods_missing": [],
        "traversal_errors": [],
        "traversal_event_count": 0,
    }

    if ast is None:
        return diagnostics

    visitor = _SafeVisitor()

    try:
        visitor.traverse(ast)
        diagnostics["visitor_status"] = (
            "full_support" if not visitor.missing_methods else "partial_support"
        )
    except Exception as exc:
        diagnostics["visitor_status"] = "failed"
        diagnostics["traversal_errors"].append(str(exc))

    diagnostics["visitor_methods_present"] = sorted(
        {m for m in SUPPORTED_VISITOR_METHODS if hasattr(visitor, m)}
    )
    diagnostics["visitor_methods_missing"] = sorted(set(visitor.missing_methods))
    diagnostics["traversal_event_count"] = len(visitor.traversal)

    return diagnostics


def calculate_scores(detected_constructs, parse_diagnostics, ast_diagnostics, visitor_diagnostics):
    """Calculate compatibility percentages."""

    scores = {
        "parser_compatibility": 0,
        "ast_compatibility": 0,
        "visitor_compatibility": 0,
    }

    total_constructs = len([c for c in detected_constructs.values() if c["detected"]])
    supported_count = sum(
        1
        for name, info in detected_constructs.items()
        if info["detected"] and name in SUPPORTED_GRAMMAR_CONSTRUCTS
    )

    if parse_diagnostics["parse_status"] == "success":
        base = 100.0
    elif parse_diagnostics["parse_status"] == "failed":
        base = 0.0
    else:
        base = 50.0

    if total_constructs > 0:
        construct_ratio = supported_count / total_constructs
        if base == 0.0:
            scores["parser_compatibility"] = int(construct_ratio * 100)
        else:
            scores["parser_compatibility"] = int(base * (0.7 + 0.3 * construct_ratio))
    else:
        scores["parser_compatibility"] = int(base)

    present = ast_diagnostics.get("ast_nodes_present", [])
    if present:
        supported_present = len([t for t in present if t in SUPPORTED_AST_NODES])
        scores["ast_compatibility"] = int((supported_present / len(present)) * 100)
    else:
        scores["ast_compatibility"] = 0 if ast_diagnostics["ast_status"] == "no_ast" else 50

    missing = visitor_diagnostics.get("visitor_methods_missing", [])
    event_count = visitor_diagnostics.get("traversal_event_count", 0)
    if visitor_diagnostics["visitor_status"] == "no_ast":
        scores["visitor_compatibility"] = 0
    elif visitor_diagnostics["visitor_status"] == "failed":
        scores["visitor_compatibility"] = 0
    elif not missing:
        scores["visitor_compatibility"] = 100
    else:
        scores["visitor_compatibility"] = max(10, min(100, int(event_count * 2)))

    return scores


def build_dataset_report(file_path, source_code, detected_constructs, parse_diagnostics,
                         ast_diagnostics, visitor_diagnostics, scores):
    """Assemble the full diagnostic report dict for one dataset."""

    dataset_name = Path(file_path).name

    supported_constructs = [
        name for name, info in detected_constructs.items()
        if info["detected"] and name in SUPPORTED_GRAMMAR_CONSTRUCTS
    ]
    unsupported_constructs = [
        name for name, info in detected_constructs.items()
        if info["detected"] and name not in SUPPORTED_GRAMMAR_CONSTRUCTS
    ]

    parser_failures = []
    if parse_diagnostics["parse_status"] == "failed":
        parser_failures.append({
            "line": parse_diagnostics["parse_error_line"],
            "column": parse_diagnostics["parse_error_column"],
            "reason": parse_diagnostics["parse_error"],
            "severity": SEVERITY_CRITICAL,
        })

    failure_text = parse_diagnostics.get("parse_error", "") or ""
    for construct_name in unsupported_constructs:
        if any(keyword.lower() in failure_text.lower() for keyword in construct_name.split("_")):
            parser_failures.append({
                "line": parse_diagnostics["parse_error_line"],
                "column": parse_diagnostics["parse_error_column"],
                "construct": construct_name,
                "reason": "unsupported grammar inferred from parser failure",
                "severity": SEVERITY_ERROR,
            })

    missing_ast_nodes = ast_diagnostics.get("ast_nodes_missing", [])
    missing_visitor_methods = visitor_diagnostics.get("visitor_methods_missing", [])

    issues = []
    if parse_diagnostics["parse_status"] == "failed":
        issues.append({
            "category": "parser",
            "severity": SEVERITY_CRITICAL,
            "message": parse_diagnostics["parse_error"],
        })
    elif unsupported_constructs:
        for uc in unsupported_constructs:
            issues.append({
                "category": "grammar",
                "severity": SEVERITY_ERROR,
                "message": f"Unsupported construct: {uc}",
            })

    if missing_ast_nodes:
        for ma in missing_ast_nodes:
            issues.append({
                "category": "ast",
                "severity": SEVERITY_WARNING,
                "message": f"Missing AST node support: {ma}",
            })

    if missing_visitor_methods:
        for mv in missing_visitor_methods:
            issues.append({
                "category": "visitor",
                "severity": SEVERITY_WARNING,
                "message": f"Missing visitor method: {mv}",
            })

    if parse_diagnostics["parse_status"] == "failed":
        overall_status = "failed"
    elif unsupported_constructs or missing_ast_nodes or missing_visitor_methods:
        overall_status = "partial_success"
    else:
        overall_status = "success"

    report = {
        "meta": {
            "dataset": dataset_name,
            "file_path": str(file_path),
            "generated_at": _now_iso(),
            "diagnostics_version": "1.1.0",
        },
        "overall_status": overall_status,
        "parse_status": parse_diagnostics["parse_status"],
        "ast_status": ast_diagnostics["ast_status"],
        "visitor_status": visitor_diagnostics["visitor_status"],
        "scores": scores,
        "supported_constructs": supported_constructs,
        "unsupported_constructs": unsupported_constructs,
        "detected_constructs": detected_constructs,
        "missing_ast_nodes": missing_ast_nodes,
        "missing_visitor_methods": missing_visitor_methods,
        "parser_failures": parser_failures,
        "ast_nodes_present": ast_diagnostics.get("ast_nodes_present", []),
        "visitor_methods_present": visitor_diagnostics.get("visitor_methods_present", []),
        "visitor_traversal_event_count": visitor_diagnostics.get("traversal_event_count", 0),
        "issues": issues,
    }

    return report


# =============================================================================
# Global summary
# =============================================================================

def build_global_summary(reports):
    """Aggregate per-dataset reports into a global grammar summary."""

    construct_counter = Counter()
    unsupported_counter = Counter()
    ast_node_counter = Counter()
    visitor_missing_counter = Counter()
    dataset_summaries = []
    severity_counts = Counter()

    for report in reports:
        meta = report["meta"]
        dataset_summaries.append({
            "dataset": meta["dataset"],
            "overall_status": report["overall_status"],
            "scores": report["scores"],
            "issue_count": len(report.get("issues", [])),
        })

        for name, info in report.get("detected_constructs", {}).items():
            if info["detected"]:
                construct_counter[name] += 1
                if name not in SUPPORTED_GRAMMAR_CONSTRUCTS:
                    unsupported_counter[name] += 1

        for node in report.get("ast_nodes_present", []):
            ast_node_counter[node] += 1

        for method in report.get("missing_visitor_methods", []):
            visitor_missing_counter[method] += 1

        for issue in report.get("issues", []):
            severity_counts[issue["severity"]] += 1

    total = len(reports)
    success = sum(1 for r in reports if r["overall_status"] == "success")
    partial = sum(1 for r in reports if r["overall_status"] == "partial_success")
    failed = sum(1 for r in reports if r["overall_status"] == "failed")

    return {
        "meta": {
            "generated_at": _now_iso(),
            "total_datasets": total,
            "diagnostics_version": "1.1.0",
        },
        "dataset_summaries": dataset_summaries,
        "maturity": {"success": success, "partial_success": partial, "failed": failed},
        "construct_frequencies": dict(construct_counter),
        "unsupported_construct_frequencies": dict(unsupported_counter),
        "ast_node_frequencies": dict(ast_node_counter),
        "missing_visitor_method_frequencies": dict(visitor_missing_counter),
        "severity_counts": dict(severity_counts),
        "parser_average_score": round(
            sum(r["scores"]["parser_compatibility"] for r in reports) / total, 1
        ) if total else 0,
        "ast_average_score": round(
            sum(r["scores"]["ast_compatibility"] for r in reports) / total, 1
        ) if total else 0,
        "visitor_average_score": round(
            sum(r["scores"]["visitor_compatibility"] for r in reports) / total, 1
        ) if total else 0,
    }


# =============================================================================
# Dataset analysis (single file)
# =============================================================================

def analyze_dataset(file_path):
    """Run the full diagnostic pipeline for one .st file."""

    source_code = ""
    try:
        source_code = load_st_file(file_path)
    except Exception as exc:
        return {
            "meta": {
                "dataset": Path(file_path).name,
                "file_path": str(file_path),
                "generated_at": _now_iso(),
                "diagnostics_version": "1.1.0",
            },
            "overall_status": "failed",
            "parse_status": "failed",
            "ast_status": "no_ast",
            "visitor_status": "no_ast",
            "scores": {"parser_compatibility": 0, "ast_compatibility": 0, "visitor_compatibility": 0},
            "supported_constructs": [],
            "unsupported_constructs": [],
            "detected_constructs": {},
            "missing_ast_nodes": [],
            "missing_visitor_methods": [],
            "parser_failures": [{"reason": f"File load error: {exc}", "severity": SEVERITY_CRITICAL}],
            "ast_nodes_present": [],
            "visitor_methods_present": [],
            "visitor_traversal_event_count": 0,
            "issues": [{"category": "io", "severity": SEVERITY_CRITICAL, "message": str(exc)}],
        }

    detected_constructs = detect_constructs(source_code)
    ast, parse_diagnostics = attempt_parse(file_path)
    ast_diagnostics = analyze_ast(ast)
    visitor_diagnostics = analyze_visitor(ast)
    scores = calculate_scores(detected_constructs, parse_diagnostics, ast_diagnostics, visitor_diagnostics)

    return build_dataset_report(
        file_path, source_code, detected_constructs,
        parse_diagnostics, ast_diagnostics, visitor_diagnostics, scores,
    )


# =============================================================================
# Main orchestrator (incremental, industrial-scoped)
# =============================================================================

def run_diagnostics(force=False):
    """Run incremental diagnostics over industrial datasets.

    Args:
        force: If True, re-analyze all datasets regardless of change detection.
    """

    # Scope: only industrial_data directory.
    dataset_files = find_dataset_files(INDUSTRIAL_DATASETS_DIR)

    if not dataset_files:
        print("No .st files found in datasets/industrial_data/.")
        return

    # Ensure output directories exist.
    DATASETS_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    index = _load_compatibility_index()
    reports = []
    analyzed_count = 0
    skipped_count = 0

    print(f"Analyzing industrial datasets: {len(dataset_files)} file(s)\n")

    current_names = set()

    for file_path in dataset_files:
        dataset_name = file_path.name
        current_names.add(dataset_name)
        stem = _dataset_stem(file_path)

        current_hash = _file_hash(file_path)
        existing_entry = index["datasets"].get(dataset_name)

        # ALWAYS run full diagnostics — even unchanged datasets are re-evaluated
        # so that compiler infrastructure improvements are captured.
        report = analyze_dataset(file_path)
        reports.append(report)
        analyzed_count += 1

        # Compute progression against the previous run.
        progression = {}
        for metric in ("parser", "ast", "visitor"):
            prev_val = existing_entry.get(f"{metric}_compatibility") if existing_entry else None
            curr_val = report["scores"][f"{metric}_compatibility"]
            progression[f"{metric}_previous"] = prev_val
            progression[f"{metric}_delta"] = (curr_val - prev_val) if prev_val is not None else None

        report["progression"] = progression

        _write_json_report(report, stem)
        _write_markdown_report(report, stem)
        _update_index_entry(index, dataset_name, report, current_hash)

        scores = report["scores"]
        prog = report["progression"]

        def _fmt_delta(metric):
            delta = prog.get(f"{metric}_delta")
            if delta is None:
                return ""
            if delta > 0:
                return f" ↑+{delta}"
            if delta < 0:
                return f" ↓{delta}"
            return " →0"

        print(
            f"  {dataset_name:40s}  "
            f"parser={scores['parser_compatibility']:3d}%{_fmt_delta('parser'):6s}  "
            f"ast={scores['ast_compatibility']:3d}%{_fmt_delta('ast'):6s}  "
            f"visitor={scores['visitor_compatibility']:3d}%{_fmt_delta('visitor'):6s}"
        )

    # Clean stale diagnostics for removed datasets.
    stale_names = [name for name in index["datasets"] if name not in current_names]
    for stale_name in stale_names:
        stale_stem = Path(stale_name).stem
        _remove_dataset_reports(stale_stem)
        _remove_index_entry(index, stale_name)
        print(f"  {stale_name:40s}  status={'removed':14s}  (stale diagnostics cleaned)")

    # Persist index and global summary.
    _save_compatibility_index(index)

    summary = build_global_summary(reports)
    _save_json(SUMMARY_PATH, summary)

    print(f"\nDiagnostics complete.")
    print(f"  Analyzed:  {analyzed_count}")
    if stale_names:
        print(f"  Removed:   {len(stale_names)} (stale)")
    print(f"\nMaturity: {summary['maturity']['success']} success, "
          f"{summary['maturity']['partial_success']} partial, "
          f"{summary['maturity']['failed']} failed")
    print(f"Average scores: parser={summary['parser_average_score']}%  "
          f"ast={summary['ast_average_score']}%  "
          f"visitor={summary['visitor_average_score']}%")
    print(f"\nArtifacts:")
    print(f"  - {INDEX_PATH}")
    print(f"  - {SUMMARY_PATH}")
    print(f"  - {DATASETS_REPORTS_DIR}/")

    return summary, reports


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_diagnostics()
