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
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
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
DEBUG_DIR = DIAGNOSTICS_DIR / "debug"

INDEX_PATH = DIAGNOSTICS_DIR / "compatibility_index.json"
SUMMARY_PATH = DIAGNOSTICS_DIR / "grammar_summary.json"

# Industrial dataset scope (recursive, never scans educational/toy/test sets).
INDUSTRIAL_DATASETS_DIR = DATASETS_DIR / "Industrial_data"

# ---------------------------------------------------------------------------
# IEC 61131-3 construct catalog
# ---------------------------------------------------------------------------
CONSTRUCT_PATTERNS = {
    "IF": [r"\bIF\b"],
    "ELSIF": [r"\bELSIF\b"],
    "ELSE": [r"\bELSE\b"],
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
    "EXIT": [r"\bEXIT\b"],
    "RETURN": [r"\bRETURN\b"],
    "timer_TON": [r"\bTON\b"],
    "timer_TOF": [r"\bTOF\b"],
    "timer_TP": [r"\bTP\b"],
    "counter_CTU": [r"\bCTU\b"],
    "counter_CTD": [r"\bCTD\b"],
    "counter_CTUD": [r"\bCTUD\b"],
    "FB_invocation": [r"\w+\s*\("],
    "time_literal": [r"[tT]#\d+(?:ms|s|m|h|d)"],
    "typed_literal": [r"\b(BOOL|BYTE|WORD|DWORD|INT|DINT|UINT|UDINT|REAL|TIME|STRING)#[^;\s,]+"],
    "numeric_literal": [r"\b\d+(?:\.\d+)?\b"],
    "boolean_literal": [r"\b(TRUE|FALSE)\b"],
    "hex_literal": [r"\b(16|8|2)#[0-9A-Fa-f_]+\b"],
    "string_literal": [r"'[^']*'"],
    "state_machine": [r"\bSTATE\b|\bTRANSITION\b|\bSTEP\b"],
    "multiline_boolean": [r"\b(AND|OR)\b[^;\n]*\n[^;\n]*\b(AND|OR)\b"],
    "array_index": [r"\w+\s*\["],
    "array_declaration": [r"\bARRAY\b.*\bOF\b"],
    "CONFIGURATION": [r"\bCONFIGURATION\b"],
    "RESOURCE": [r"\bRESOURCE\b"],
    "TASK": [r"\bTASK\b"],
    "PROGRAM_binding": [r"\bPROGRAM\b[^;\n]*\bWITH\b[^;\n]*:"],
    "memory_mapping": [r"\bAT\b\s*%[IQMX][XBWD]?\d+(?:\.\d+)?"],
    "WITH": [r"\bWITH\b"],
    "ON": [r"\bON\b"],
    "AT": [r"\bAT\b"],
}

SUPPORTED_GRAMMAR_CONSTRUCTS = {
    "IF",
    "ELSIF",
    "ELSE",
    "CASE_OF",
    "assignment",
    "boolean_logic",
    "arithmetic_expression",
    "comparison_expression",
    "time_literal",
    "typed_literal",
    "numeric_literal",
    "boolean_literal",
    "hex_literal",
    "string_literal",
    "FB_invocation",
    "FOR_LOOP",
    "WHILE_LOOP",
    "REPEAT_LOOP",
    "EXIT",
    "RETURN",
    "array_index",
    "array_declaration",
    "FUNCTION",
    "FUNCTION_BLOCK",
    "VAR",
    "VAR_INPUT",
    "VAR_OUTPUT",
    "VAR_IN_OUT",
    "CONFIGURATION",
    "RESOURCE",
    "TASK",
    "PROGRAM_binding",
    "memory_mapping",
    "WITH",
    "ON",
    "AT",
}

# Domain classification for semantic-node-based scoring.
CONTROL_AST_NODES = {
    "IfStatementNode", "CaseStatementNode", "ForLoopNode", "WhileLoopNode",
    "RepeatLoopNode", "AssignmentNode", "FunctionBlockCallNode",
    "FunctionBlockInvocationNode", "ExitNode", "ReturnNode",
}
COMPUTATIONAL_AST_NODES = {
    "TypedLiteralNode", "ArrayTypeNode", "BinaryExpressionNode",
    "LogicalExpressionNode", "FunctionInvocationNode", "ArrayIndexNode",
    "NumberNode", "BooleanNode", "StringLiteralNode", "TimeLiteralNode",
}
RUNTIME_AST_NODES = {
    "ConfigurationNode", "ResourceNode", "TaskNode", "ProgramBindingNode",
    "MemoryMappingNode", "CompilationUnitNode", "VarBlockNode",
    "VariableDeclarationNode",
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
    "StringLiteralNode",
    "TypedLiteralNode",
    "ArrayIndexNode",
    "FunctionBlockCallNode",
    "FunctionBlockInvocationNode",
    "FunctionInvocationNode",
    "InvocationArgumentNode",
    "ForLoopNode",
    "WhileLoopNode",
    "RepeatLoopNode",
    "ExitNode",
    "ReturnNode",
    "ArrayTypeNode",
    "CompilationUnitNode",
    "VarBlockNode",
    "VariableDeclarationNode",
    "MemoryMappingNode",
    "TaskNode",
    "ProgramBindingNode",
    "ResourceNode",
    "ConfigurationNode",
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
    "visit_StringLiteralNode",
    "visit_TypedLiteralNode",
    "visit_ArrayIndexNode",
    "visit_FunctionBlockCallNode",
    "visit_FunctionBlockInvocationNode",
    "visit_FunctionInvocationNode",
    "visit_InvocationArgumentNode",
    "visit_ForLoopNode",
    "visit_WhileLoopNode",
    "visit_RepeatLoopNode",
    "visit_ExitNode",
    "visit_ReturnNode",
    "visit_ArrayTypeNode",
    "visit_CompilationUnitNode",
    "visit_VarBlockNode",
    "visit_VariableDeclarationNode",
    "visit_MemoryMappingNode",
    "visit_TaskNode",
    "visit_ProgramBindingNode",
    "visit_ResourceNode",
    "visit_ConfigurationNode",
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


def _write_debug_log(report, stem, ast, parse_diagnostics, ast_diagnostics, visitor_diagnostics, corpus_structure=None):
    """Write semantic debug diagnostics to help trace scoring decisions."""

    debug_path = DEBUG_DIR / f"{stem}.json"
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    # Determine unsupported node types present in the AST
    present = ast_diagnostics.get("ast_nodes_present", [])
    unsupported_nodes = [n for n in present if n not in SUPPORTED_AST_NODES]

    # Determine root type and container hierarchy
    root_type = type(ast).__name__ if ast is not None else "None"
    top_level_types = []
    if ast is not None and hasattr(ast, "body"):
        body = ast.body
        if hasattr(body, "statements"):
            top_level_types = [type(s).__name__ for s in body.statements[:5]]
        elif hasattr(body, "__iter__"):
            try:
                top_level_types = [type(s).__name__ for s in body[:5]]
            except Exception:
                pass

    # Semantic node counts
    present_set = set(present)
    control_nodes = sorted(present_set & CONTROL_AST_NODES)
    computational_nodes = sorted(present_set & COMPUTATIONAL_AST_NODES)
    runtime_nodes = sorted(present_set & RUNTIME_AST_NODES)

    debug_data = {
        "meta": {
            "dataset": report["meta"]["dataset"],
            "generated_at": report["meta"]["generated_at"],
        },
        "ast_root_type": root_type,
        "top_level_types": top_level_types,
        "semantic_node_count": len(present),
        "control_nodes": control_nodes,
        "computational_nodes": computational_nodes,
        "runtime_nodes": runtime_nodes,
        "unsupported_ast_nodes": unsupported_nodes,
        "visitor_traversal_status": visitor_diagnostics.get("visitor_status", "unknown"),
        "visitor_traversal_errors": visitor_diagnostics.get("traversal_errors", []),
        "visitor_missing_methods": visitor_diagnostics.get("visitor_methods_missing", []),
        "visitor_event_count": visitor_diagnostics.get("traversal_event_count", 0),
        "parse_failure_details": {
            "category": parse_diagnostics.get("parse_failure_category", ""),
            "error_context": parse_diagnostics.get("parse_error_context", {}),
            "error_line_text": parse_diagnostics.get("parse_error_line_text", ""),
            "nearby_lines": parse_diagnostics.get("parse_error_nearby_lines", {}),
            "expected_tokens": parse_diagnostics.get("parse_expected_tokens", ""),
            "found_token": parse_diagnostics.get("parse_found_token", ""),
            "file_offset": parse_diagnostics.get("parse_file_offset"),
            "parsed_prefix_percentage": parse_diagnostics.get("parsed_prefix_percentage", 0.0),
            "parsed_line_percentage": parse_diagnostics.get("parsed_line_percentage", 0.0),
        },
        "corpus_structure": corpus_structure or {},
        "scoring_decisions": {
            "parser_status": parse_diagnostics.get("parse_status"),
            "ast_nodes_total": len(present),
            "ast_nodes_supported": len([n for n in present if n in SUPPORTED_AST_NODES]),
            "ast_coverage_ratio": ast_diagnostics.get("ast_coverage_ratio", 0.0),
            "domain_scores": {
                "control": report["scores"].get("control_grammar_support"),
                "computational": report["scores"].get("computational_grammar_support"),
                "runtime": report["scores"].get("runtime_grammar_support"),
            },
        },
    }
    _save_json(debug_path, debug_data)
    return debug_path


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
        f"| Control Grammar Support | {scores.get('control_grammar_support', 'N/A')}% |",
        f"| Computational Grammar Support | {scores.get('computational_grammar_support', 'N/A')}% |",
        f"| Runtime Grammar Support | {scores.get('runtime_grammar_support', 'N/A')}% |",
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
            category = failure.get("category", "")
            cat_str = f" [{category}]" if category else ""
            lines.append(
                f"  - [{failure.get('severity', 'ERROR')}]"
                f"{cat_str} "
                f"{failure.get('reason', 'unknown')}{loc}"
            )
            if failure.get("expected"):
                lines.append(f"    - Expected: {failure['expected']}")
            if failure.get("found"):
                lines.append(f"    - Found: {failure['found']}")
            if failure.get("parsed_prefix_pct") is not None:
                lines.append(f"    - Parsed prefix: {failure['parsed_prefix_pct']}%")
    else:
        lines.append("- **Failures:** none")

    # Parse failure details
    pfd = report.get("parse_failure_details", {})
    if pfd and pfd.get("category"):
        lines.extend([
            "",
            "## Parse Failure Details",
            "",
            f"- **Category:** {pfd.get('category', 'unknown')}",
        ])
        if pfd.get("error_line_text"):
            lines.append(f"- **Failing line:** `{pfd['error_line_text']}`")
        nearby = pfd.get("nearby_lines", {})
        if nearby.get("previous_lines"):
            lines.append("- **Previous lines:**")
            for pl in nearby["previous_lines"]:
                lines.append(f"  ```{pl}```")
        if nearby.get("next_lines"):
            lines.append("- **Next lines:**")
            for nl in nearby["next_lines"]:
                lines.append(f"  ```{nl}```")
        if pfd.get("parsed_prefix_percentage"):
            lines.append(f"- **Parsed prefix:** {pfd['parsed_prefix_percentage']}%")
        if pfd.get("parsed_line_percentage"):
            lines.append(f"- **Parsed lines:** {pfd['parsed_line_percentage']}%")

    # Corpus structure
    cs = report.get("corpus_structure", {})
    if cs:
        lines.extend([
            "",
            "## Corpus Structure",
            "",
        ])
        if cs.get("total_lines"):
            lines.append(f"- **Total lines:** {cs['total_lines']}")
        if cs.get("program_count"):
            lines.append(f"- **PROGRAM blocks:** {cs['program_count']}")
        if cs.get("function_block_count"):
            lines.append(f"- **FUNCTION_BLOCK blocks:** {cs['function_block_count']}")
        if cs.get("function_count"):
            lines.append(f"- **FUNCTION blocks:** {cs['function_count']}")
        if cs.get("configuration_count"):
            lines.append(f"- **CONFIGURATION blocks:** {cs['configuration_count']}")
        if cs.get("assert_expect_count"):
            lines.append(f"- **ASSERT/EXPECT patterns:** {cs['assert_expect_count']}")
        if cs.get("multiple_compilation_units"):
            lines.append("- **Multiple compilation units:** yes")
        if cs.get("has_dialect_keywords"):
            lines.append("- **Non-IEC dialect keywords:** detected")
        if cs.get("has_c_style_comments"):
            lines.append("- **C-style comments:** detected")
        if cs.get("is_near_empty"):
            lines.append("- **Near-empty file:** yes")

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


def analyze_corpus_structure(source_code):
    """Detect structural anomalies in source code that may explain parse failures.

    Returns a dict with counts and flags for corpus-level patterns.
    """
    lines = source_code.splitlines()
    total_lines = len(lines)

    # Count top-level compilation-unit keywords
    program_count = len(re.findall(r"\bPROGRAM\b", source_code, re.IGNORECASE))
    fb_count = len(re.findall(r"\bFUNCTION_BLOCK\b", source_code, re.IGNORECASE))
    func_count = len(re.findall(r"\bFUNCTION\b(?!_BLOCK)", source_code, re.IGNORECASE))
    config_count = len(re.findall(r"\bCONFIGURATION\b", source_code, re.IGNORECASE))

    # Test harness keywords
    assert_count = len(re.findall(r"\bASSERT\b|\bEXPECT\b|\bTEST\b|\bVERIFY\b", source_code, re.IGNORECASE))

    # Non-IEC wrappers / metadata
    has_metadata_header = bool(re.search(r"^\s*(//|\(\*|#)", source_code, re.MULTILINE))
    has_dialect_keywords = bool(re.search(r"\binclude\b|\bimport\b|\bdef\b|\bclass\b", source_code, re.IGNORECASE))

    # Malformed separators
    has_c_style_comments = "/*" in source_code or "*/" in source_code
    has_pythonic_indent = bool(re.search(r"^\s{4,}\w+", source_code, re.MULTILINE))

    # Empty or near-empty
    is_near_empty = total_lines < 3 and len(source_code.strip()) < 50

    return {
        "total_lines": total_lines,
        "program_count": program_count,
        "function_block_count": fb_count,
        "function_count": func_count,
        "configuration_count": config_count,
        "assert_expect_count": assert_count,
        "has_metadata_header": has_metadata_header,
        "has_dialect_keywords": has_dialect_keywords,
        "has_c_style_comments": has_c_style_comments,
        "has_pythonic_indent": has_pythonic_indent,
        "is_near_empty": is_near_empty,
        "multiple_compilation_units": (program_count + fb_count + func_count + config_count) > 1,
    }


def _extract_nearby_lines(source_code, line_no, context=3):
    """Return prev N, target, and next N lines from source code."""
    lines = source_code.splitlines()
    if line_no is None or line_no < 1:
        return {"target_line": "", "previous_lines": [], "next_lines": []}

    idx = line_no - 1
    prev_start = max(0, idx - context)
    next_end = min(len(lines), idx + context + 1)

    return {
        "target_line": lines[idx] if idx < len(lines) else "",
        "previous_lines": lines[prev_start:idx],
        "next_lines": lines[idx + 1:next_end],
    }


def _classify_parse_failure(exc, source_code, error_line, error_line_text):
    """Classify the parse failure into a high-level category."""

    msg = str(exc).lower()
    found = getattr(exc, "found", "")
    pelem = getattr(exc, "parser_element", None)
    pelem_name = str(pelem) if pelem else ""

    # Check for test harness / assertion keywords
    if re.search(r"\bASSERT\b|\bEXPECT\b|\bTEST\b|\bVERIFY\b", source_code, re.IGNORECASE):
        return "unsupported_test_harness"

    # Check for metadata / wrapper headers
    if source_code.strip().startswith("//") or source_code.strip().startswith("(*"):
        if re.search(r"\btest\b|\bfixture\b|\bsuite\b", source_code[:200], re.IGNORECASE):
            return "unsupported_test_harness"

    # Dialect mismatch: keywords that look like C/Java but not IEC
    if re.search(r"\binclude\b|\bimport\b|\bdef\b|\bclass\b", source_code, re.IGNORECASE):
        return "dialect_mismatch"

    # Multiple top-level blocks
    prog_count = len(re.findall(r"\bPROGRAM\b", source_code, re.IGNORECASE))
    fb_count = len(re.findall(r"\bFUNCTION_BLOCK\b", source_code, re.IGNORECASE))
    if prog_count > 1 or fb_count > 1:
        return "multi_program_file"

    # Malformed corpus: very short or non-printable
    if len(source_code.strip()) < 20:
        return "malformed_corpus"

    # Unexpected token at end of file = partial parse
    if "expected end of text" in msg or "expected end-of-text" in msg:
        return "partial_parse"

    # Unsupported runtime constructs
    if re.search(r"\bCONFIGURATION\b|\bRESOURCE\b|\bTASK\b", source_code, re.IGNORECASE):
        if "configuration" not in pelem_name.lower() and "resource" not in pelem_name.lower():
            return "unsupported_runtime_construct"

    # Unsupported keyword in error context
    if error_line_text:
        known_unsupported = ["WITH", "PRIORITY", "INTERVAL", "EXTENDS", "IMPLEMENTS", "INTERFACE"]
        for kw in known_unsupported:
            if kw in error_line_text.upper():
                return "unsupported_keyword"

    # Invalid statement sequence
    if "expected" in msg and (";" in msg or "end_" in msg):
        return "invalid_statement_sequence"

    # Unexpected token
    if "expected" in msg and "found" in msg:
        return "unexpected_token"

    return "unknown_parse_failure"


def attempt_parse(file_path):
    """Try to parse a .st file. Return (ast_or_none, diagnostics_dict)."""

    diagnostics = {
        "parse_status": "unknown",
        "parse_error": None,
        "parse_error_line": None,
        "parse_error_column": None,
        "parse_traceback": None,
        "partial_ast": False,
        "parse_error_context": {},
        "parse_error_line_text": "",
        "parse_error_nearby_lines": {"previous_lines": [], "next_lines": []},
        "parse_expected_tokens": "",
        "parse_found_token": "",
        "parse_file_offset": None,
        "parse_failure_category": "",
        "parsed_prefix_percentage": 0.0,
        "parsed_line_percentage": 0.0,
    }

    ast = None
    source_code = ""

    try:
        source_code = load_st_file(file_path)
        ast = parse_st_program(source_code)
        diagnostics["parse_status"] = "success"
    except Exception as exc:
        diagnostics["parse_status"] = "failed"
        diagnostics["parse_error"] = str(exc)
        diagnostics["parse_traceback"] = traceback.format_exc()

        # Extract pyparsing-specific attributes
        line_no = getattr(exc, "lineno", None)
        col_no = getattr(exc, "col", None)
        loc = getattr(exc, "loc", None)
        found = getattr(exc, "found", "")
        msg = getattr(exc, "msg", "")
        pelem = getattr(exc, "parser_element", None)

        if line_no is None:
            line_no = getattr(exc, "line", None)
        if col_no is None:
            col_no = getattr(exc, "column", None)

        diagnostics["parse_error_line"] = line_no
        diagnostics["parse_error_column"] = col_no
        diagnostics["parse_file_offset"] = loc
        diagnostics["parse_found_token"] = found
        diagnostics["parse_expected_tokens"] = msg

        if hasattr(exc, "parser_element") and exc.parser_element is not None:
            diagnostics["partial_ast"] = True

        # Context extraction
        nearby = _extract_nearby_lines(source_code, line_no, context=3)
        diagnostics["parse_error_line_text"] = nearby["target_line"]
        diagnostics["parse_error_nearby_lines"] = {
            "previous_lines": nearby["previous_lines"],
            "next_lines": nearby["next_lines"],
        }
        diagnostics["parse_error_context"] = {
            "line_number": line_no,
            "column": col_no,
            "file_offset": loc,
            "failing_element": str(pelem) if pelem else "",
        }

        # Partial parse detection
        total_chars = len(source_code)
        total_lines = source_code.count("\n") + 1
        if loc is not None and total_chars > 0:
            diagnostics["parsed_prefix_percentage"] = round(min(100.0, (loc / total_chars) * 100), 1)
        if line_no is not None and total_lines > 0:
            diagnostics["parsed_line_percentage"] = round(min(100.0, (line_no / total_lines) * 100), 1)

        # Failure classification
        diagnostics["parse_failure_category"] = _classify_parse_failure(
            exc, source_code, line_no, nearby["target_line"]
        )

    return ast, diagnostics


def gather_ast_node_types(node, types=None, visited=None):
    """Recursively collect all AST node class names present in a tree.

    Generalized walker that traverses:
    - AST nodes via __dict__ inspection
    - list, tuple, set, dict values, ParseResults
    - arbitrary nested containers

    Uses visited-ids to avoid infinite recursion on cyclic structures.
    """
    if types is None:
        types = set()
    if visited is None:
        visited = set()

    if node is None:
        return types

    # Skip primitive scalars
    if isinstance(node, (bool, int, float, str)):
        return types

    # Skip already-visited objects to avoid cycles
    node_id = id(node)
    if node_id in visited:
        return types
    visited.add(node_id)

    # If it's a dict-like container, traverse its values
    if isinstance(node, dict):
        for value in node.values():
            gather_ast_node_types(value, types, visited)
        return types

    # If it's a sequence-like container (but not string/bytes)
    if isinstance(node, (list, tuple, set)):
        for item in node:
            gather_ast_node_types(item, types, visited)
        return types

    # If it's a ParseResults or similar iterable container
    try:
        iterable = iter(node)
    except TypeError:
        pass
    else:
        # Avoid infinite recursion on strings/bytes (already handled above)
        if not isinstance(node, (str, bytes)):
            for item in iterable:
                gather_ast_node_types(item, types, visited)
            return types

    # If it's an object with a __dict__, inspect ALL attributes
    if hasattr(node, "__dict__") and hasattr(node, "__class__"):
        types.add(node.__class__.__name__)
        for attr_value in node.__dict__.values():
            gather_ast_node_types(attr_value, types, visited)

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
    # Only flag "StatementNode coverage" when the file is truly empty of
    # semantic content (no compilation units, configurations, or executable nodes).
    has_semantic_content = any(
        t in present_types for t in (
            "CompilationUnitNode", "ConfigurationNode", "ResourceNode",
            "TaskNode", "ProgramBindingNode", "IfStatementNode", "CaseStatementNode",
            "AssignmentNode", "ForLoopNode", "WhileLoopNode", "RepeatLoopNode",
            "FunctionBlockCallNode", "FunctionInvocationNode",
        )
    )
    if "ProgramNode" in present_types and len(present_types) <= 2 and not has_semantic_content:
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


def _domain_score_from_nodes(present_nodes, domain_nodes, parse_failed=False):
    """Return a 0-100 score for how many *present_nodes* in *domain_nodes* are supported.

    A domain scores 100 when no relevant nodes are present (nothing required).
    When relevant nodes ARE present, the score is the percentage of those
    node types that are in SUPPORTED_AST_NODES.
    When parse_failed is True, semantic nodes were NOT materialized, so score 0.
    """
    if parse_failed:
        return 0
    relevant = present_nodes & domain_nodes
    if not relevant:
        return 100
    supported = sum(1 for n in relevant if n in SUPPORTED_AST_NODES)
    return int((supported / len(relevant)) * 100)


def calculate_scores(detected_constructs, parse_diagnostics, ast_diagnostics, visitor_diagnostics):
    """Calculate compatibility percentages with semantic-node-based domain scores."""

    scores = {
        "parser_compatibility": 0,
        "ast_compatibility": 0,
        "visitor_compatibility": 0,
        "control_grammar_support": 0,
        "computational_grammar_support": 0,
        "runtime_grammar_support": 0,
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

    # CRITICAL: when parser fails and no AST is produced, cap score at 25%
    ast = ast_diagnostics.get("ast_nodes_present", [])
    if parse_diagnostics["parse_status"] == "failed" and not ast:
        scores["parser_compatibility"] = min(scores["parser_compatibility"], 25)

    present = ast_diagnostics.get("ast_nodes_present", [])
    if present:
        supported_present = len([t for t in present if t in SUPPORTED_AST_NODES])
        scores["ast_compatibility"] = int((supported_present / len(present)) * 100)
    else:
        scores["ast_compatibility"] = 0 if ast_diagnostics["ast_status"] == "no_ast" else 50

    # Semantic-node-based domain scoring
    present_set = set(present)
    parse_failed = parse_diagnostics["parse_status"] == "failed"
    scores["control_grammar_support"] = _domain_score_from_nodes(present_set, CONTROL_AST_NODES, parse_failed)
    scores["computational_grammar_support"] = _domain_score_from_nodes(present_set, COMPUTATIONAL_AST_NODES, parse_failed)
    scores["runtime_grammar_support"] = _domain_score_from_nodes(present_set, RUNTIME_AST_NODES, parse_failed)

    # Visitor coverage scoring based on actual AST node coverage
    missing = visitor_diagnostics.get("visitor_methods_missing", [])
    if visitor_diagnostics["visitor_status"] == "no_ast":
        scores["visitor_compatibility"] = 0
    elif visitor_diagnostics["visitor_status"] == "failed":
        scores["visitor_compatibility"] = 0
    elif not missing:
        scores["visitor_compatibility"] = 100
    else:
        # Compute coverage: how many unique AST node types present have
        # corresponding visitor methods vs. how many are missing.
        present_node_set = set(present)
        # Map missing visitor methods back to node names
        missing_node_set = {m.replace("visit_", "") for m in missing}
        # Nodes present in AST that have visitor support
        covered_nodes = present_node_set - missing_node_set
        # Total nodes present that require visitor support (ignore structural nodes)
        structural_nodes = {"ProgramNode", "BlockNode"}
        relevant_nodes = present_node_set - structural_nodes
        if relevant_nodes:
            covered = len(relevant_nodes & covered_nodes)
            scores["visitor_compatibility"] = int((covered / len(relevant_nodes)) * 100)
        else:
            scores["visitor_compatibility"] = 100

    return scores


def build_dataset_report(file_path, source_code, detected_constructs, parse_diagnostics,
                         ast_diagnostics, visitor_diagnostics, scores, corpus_structure=None):
    """Assemble the full diagnostic report dict for one dataset."""

    dataset_name = Path(file_path).name
    corpus_structure = corpus_structure or {}

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
        failure = {
            "line": parse_diagnostics["parse_error_line"],
            "column": parse_diagnostics["parse_error_column"],
            "reason": parse_diagnostics["parse_error"],
            "severity": SEVERITY_CRITICAL,
            "category": parse_diagnostics.get("parse_failure_category", "unknown"),
            "expected": parse_diagnostics.get("parse_expected_tokens", ""),
            "found": parse_diagnostics.get("parse_found_token", ""),
            "file_offset": parse_diagnostics.get("parse_file_offset"),
            "parsed_prefix_pct": parse_diagnostics.get("parsed_prefix_percentage"),
            "parsed_line_pct": parse_diagnostics.get("parsed_line_percentage"),
            "error_line_text": parse_diagnostics.get("parse_error_line_text", ""),
            "nearby_lines": parse_diagnostics.get("parse_error_nearby_lines", {}),
        }
        parser_failures.append(failure)

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

    # Domain-aware semantic node classification
    present_nodes = set(ast_diagnostics.get("ast_nodes_present", []))
    control_nodes = sorted(present_nodes & CONTROL_AST_NODES)
    computational_nodes = sorted(present_nodes & COMPUTATIONAL_AST_NODES)
    runtime_nodes = sorted(present_nodes & RUNTIME_AST_NODES)

    report = {
        "meta": {
            "dataset": dataset_name,
            "file_path": str(file_path),
            "generated_at": _now_iso(),
            "diagnostics_version": "2.2.0",
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
        "domain_support": {
            "control_nodes": control_nodes,
            "computational_nodes": computational_nodes,
            "runtime_nodes": runtime_nodes,
        },
        "corpus_structure": corpus_structure,
        "parse_failure_details": {
            "category": parse_diagnostics.get("parse_failure_category", ""),
            "error_context": parse_diagnostics.get("parse_error_context", {}),
            "error_line_text": parse_diagnostics.get("parse_error_line_text", ""),
            "nearby_lines": parse_diagnostics.get("parse_error_nearby_lines", {}),
            "expected_tokens": parse_diagnostics.get("parse_expected_tokens", ""),
            "found_token": parse_diagnostics.get("parse_found_token", ""),
            "file_offset": parse_diagnostics.get("parse_file_offset"),
            "parsed_prefix_percentage": parse_diagnostics.get("parsed_prefix_percentage", 0.0),
            "parsed_line_percentage": parse_diagnostics.get("parsed_line_percentage", 0.0),
        },
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

    # Domain-aware averages
    def _avg(key):
        vals = [r["scores"][key] for r in reports if key in r["scores"]]
        return round(sum(vals) / len(vals), 1) if vals else 0

    return {
        "meta": {
            "generated_at": _now_iso(),
            "total_datasets": total,
            "diagnostics_version": "2.0.0",
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
        "control_grammar_average": _avg("control_grammar_support"),
        "computational_grammar_average": _avg("computational_grammar_support"),
        "runtime_grammar_average": _avg("runtime_grammar_support"),
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
    corpus_structure = analyze_corpus_structure(source_code)
    ast, parse_diagnostics = attempt_parse(file_path)
    ast_diagnostics = analyze_ast(ast)
    visitor_diagnostics = analyze_visitor(ast)
    scores = calculate_scores(detected_constructs, parse_diagnostics, ast_diagnostics, visitor_diagnostics)
    report = build_dataset_report(
        file_path, source_code, detected_constructs,
        parse_diagnostics, ast_diagnostics, visitor_diagnostics, scores,
        corpus_structure=corpus_structure,
    )

    stem = _dataset_stem(file_path)
    _write_debug_log(report, stem, ast, parse_diagnostics, ast_diagnostics, visitor_diagnostics, corpus_structure=corpus_structure)

    return report


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
            f"visitor={scores['visitor_compatibility']:3d}%{_fmt_delta('visitor'):6s}  "
            f"ctl={scores.get('control_grammar_support', 0):3d}%  "
            f"cmp={scores.get('computational_grammar_support', 0):3d}%  "
            f"rt={scores.get('runtime_grammar_support', 0):3d}%"
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
    print(f"Domain averages: control={summary.get('control_grammar_average', 0)}%  "
          f"computational={summary.get('computational_grammar_average', 0)}%  "
          f"runtime={summary.get('runtime_grammar_average', 0)}%")
    print(f"\nArtifacts:")
    print(f"  - {INDEX_PATH}")
    print(f"  - {SUMMARY_PATH}")
    print(f"  - {DATASETS_REPORTS_DIR}/")
    print(f"  - {DEBUG_DIR}/")

    return summary, reports


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_diagnostics()
