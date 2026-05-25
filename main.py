"""Central orchestration entrypoint for the Structured Text pipeline."""

import argparse
from pathlib import Path
from pprint import pprint

from pyparsing import ParseException

from parser.st_parser import DATASETS_DIR, find_dataset_files, parse_st_file
from semantic.classifier import IndustrialSemanticClassifier
from semantic.graph_builder import SemanticGraphBuilder
from semantic.relationship_extractor import RelationshipExtractor
from semantic.type_checker import TypeChecker, build_demo_symbol_table
from semantic.visitor import SemanticTraversalVisitor


SECTION_WIDTH = 78


def print_section(title):
    """Print a readable section header for command-line output."""

    print("\n" + "=" * SECTION_WIDTH)
    print(title)
    print("=" * SECTION_WIDTH)


def print_subsection(title):
    """Print a smaller header inside one dataset file's report."""

    print("\n" + title)
    print("-" * len(title))


def load_dataset_files():
    """Return all Structured Text dataset files."""

    return find_dataset_files(DATASETS_DIR)


def run_semantic_traversal(ast):
    """Run semantic traversal and return data for the presentation layer."""

    visitor = SemanticTraversalVisitor()
    return visitor.traverse(ast)


def run_type_checking(ast):
    """Run semantic type checking and return a report dictionary."""

    checker = TypeChecker(build_demo_symbol_table())
    checker.check(ast)
    return checker.get_report()


def run_industrial_classification(ast, type_report):
    """Run industrial semantic classification and return metadata."""

    classifier = IndustrialSemanticClassifier(type_report)
    return classifier.classify(ast)


def run_relationship_extraction(ast, classification_report, type_report):
    """Run semantic relationship extraction and return graph-ready edges."""

    extractor = RelationshipExtractor(classification_report, type_report)
    return extractor.extract(ast)


def run_graph_generation(relationship_report):
    """Run semantic graph generation and return a connected topology."""

    builder = SemanticGraphBuilder()
    return builder.build(relationship_report)


def print_traversal_results(traversal_results):
    """Print traversal data returned by semantic/visitor.py."""

    for event in traversal_results:
        indentation = "  " * event["depth"]
        print(f"{indentation}{event['message']}")


def print_symbol_table(symbols):
    """Print symbol-table data returned by the semantic layer."""

    print("Symbol table:")

    if not symbols:
        print("  <empty>")
        return

    for name, variable_type in symbols.items():
        print(f"  {name}: {variable_type}")


def print_type_check_report(report):
    """Print type-checking data returned by semantic/type_checker.py."""

    print_symbol_table(report["symbols"])
    print("\nType checking report:")

    warnings = report["warnings"]
    errors = report["errors"]

    if not warnings and not errors:
        print("  No warnings or errors.")
        return

    if warnings:
        print("  Warnings:")
        for warning in warnings:
            print(f"    - {warning}")

    if errors:
        print("  Errors:")
        for error in errors:
            print(f"    - {error}")


def print_industrial_classification_report(report):
    """Print industrial semantic metadata returned by semantic/classifier.py."""

    findings = report["findings"]

    print(f"Industrial semantic findings: {report['finding_count']}")

    if not findings:
        print("  No industrial semantic patterns detected.")
        return

    print("Detected tags:")
    for tag in report["tags"]:
        print(f"  - {tag}")

    print("\nFindings:")
    for index, finding in enumerate(findings, start=1):
        print(f"  {index}. {finding['tag']} [{finding['confidence']}]")
        print(f"     Evidence: {finding['evidence']}")
        print(f"     Meaning:  {finding['description']}")

        if finding["transformation_hints"]:
            print("     Transformation hints:")
            for hint in finding["transformation_hints"]:
                print(f"       - {hint}")


def print_classification_summary(report):
    """Print compact industrial classification tags."""

    if not report["tags"]:
        print("  <no industrial semantic classifications>")
        return

    for tag in report["tags"]:
        print(f"  - {tag}")


def print_relationship_report(report):
    """Print extracted semantic relationship edges."""

    relationships = report["relationships"]

    if not relationships:
        print("  <no semantic relationships extracted>")
        return

    for relationship in relationships:
        print(
            f"  - {relationship['source']} "
            f"{relationship['relation']} "
            f"{relationship['target']}"
        )


def print_relationship_summary(report):
    """Print relationship counts by relation type."""

    if not report["relation_counts"]:
        print("  <no relationship summary available>")
        return

    for relation, count in report["relation_counts"].items():
        print(f"  - {relation}: {count}")


def print_interpretation_summary(report):
    """Print high-level industrial behavior interpretation."""

    summaries = report["interpretation_summary"]

    if not summaries:
        print("  - no high-level industrial behavior interpretation available yet")
        return

    print("  The control logic represents:")
    for summary in summaries:
        print(f"  - {summary}")


def print_graph_summary(graph):
    """Print semantic graph topology summary."""

    summary = graph.summary()

    print(f"  Nodes: {summary['node_count']}")
    print(f"  Edges: {summary['edge_count']}")

    print("\n  Node Types:")
    if summary["node_kinds"]:
        for kind, count in summary["node_kinds"].items():
            print(f"    - {kind}: {count}")
    else:
        print("    <no nodes>")

    print("\n  Dependencies:")
    if summary["dependencies"]:
        for dependency in summary["dependencies"]:
            print(f"    - {dependency}")
    else:
        print("    <no dependencies>")


def analyze_st_file(file_path):
    """Run all analysis stages and return structured results."""

    try:
        ast = parse_st_file(file_path)
    except ParseException as error:
        return {
            "file_path": file_path,
            "parse_ok": False,
            "parse_error": str(error),
        }

    traversal_results = run_semantic_traversal(ast)
    type_check_report = run_type_checking(ast)
    classification_report = run_industrial_classification(ast, type_check_report)
    relationship_report = run_relationship_extraction(
        ast,
        classification_report,
        type_check_report,
    )
    semantic_graph = run_graph_generation(relationship_report)

    return {
        "file_path": file_path,
        "parse_ok": True,
        "ast": ast,
        "traversal": traversal_results,
        "type_check": type_check_report,
        "classification": classification_report,
        "relationships": relationship_report,
        "graph": semantic_graph,
    }


def print_high_level_report(result):
    """Print the default transformation-oriented semantic report."""

    print_section(f"Industrial Semantic Analysis: {result['file_path']}")

    if not result["parse_ok"]:
        print("Parse result: FAILED")
        print(result["parse_error"])
        return False

    print_subsection("Industrial Semantic Classification")
    print_classification_summary(result["classification"])

    print_subsection("Semantic Relationships")
    print_relationship_report(result["relationships"])

    print_subsection("Relationship Summary")
    print_relationship_summary(result["relationships"])

    print_subsection("Industrial Interpretation")
    print_interpretation_summary(result["relationships"])

    print_subsection("Semantic Graph Summary")
    print_graph_summary(result["graph"])

    if result["type_check"]["program_is_valid"]:
        print("\nAnalysis result: OK")
    else:
        print("\nAnalysis result: SEMANTIC ERRORS FOUND")

    return result["type_check"]["program_is_valid"]


def print_debug_report(result):
    """Print lower-level compiler infrastructure details for debugging."""

    print_section(f"Debug Pipeline Details: {result['file_path']}")

    if not result["parse_ok"]:
        print("Parse result: FAILED")
        print(result["parse_error"])
        return False

    print("Parse result: OK")

    print_subsection("Generated AST")
    pprint(result["ast"])

    print_subsection("Semantic Visitor Traversal")
    print_traversal_results(result["traversal"])

    print_subsection("Semantic Type Checking")
    print_type_check_report(result["type_check"])

    print_subsection("Industrial Semantic Classification")
    print_industrial_classification_report(result["classification"])

    print_subsection("Semantic Relationships")
    print_relationship_report(result["relationships"])

    print_subsection("Semantic Graph")
    print_graph_summary(result["graph"])

    if result["type_check"]["program_is_valid"]:
        print("\nPipeline result: OK")
    else:
        print("\nPipeline result: SEMANTIC ERRORS FOUND")

    return result["type_check"]["program_is_valid"]


def process_st_file(file_path, debug=False):
    """Run the complete analysis pipeline for one file."""

    result = analyze_st_file(file_path)

    if debug:
        return print_debug_report(result)

    return print_high_level_report(result)


def run_pipeline(dataset_files, debug=False):
    """Run every Structured Text file through the centralized pipeline."""

    passed_count = 0

    for file_path in dataset_files:
        if process_st_file(file_path, debug=debug):
            passed_count += 1

    total_count = len(dataset_files)

    print_section("Pipeline Summary")
    print(f"Files processed: {total_count}")
    print(f"Files passed:    {passed_count}")
    print(f"Files failed:    {total_count - passed_count}")


def build_argument_parser():
    """Build CLI options for normal and debug reporting."""

    argument_parser = argparse.ArgumentParser(
        description="Run industrial semantic analysis for Structured Text datasets."
    )
    argument_parser.add_argument(
        "--debug",
        action="store_true",
        help="Show internal AST, traversal, symbol, and type-checking details.",
    )
    return argument_parser


def main():
    """Project entrypoint used by `uv run python main.py`."""

    arguments = build_argument_parser().parse_args()
    dataset_files = load_dataset_files()

    if not dataset_files:
        print(f"No .st files found in {Path(DATASETS_DIR)}.")
        return

    run_pipeline(dataset_files, debug=arguments.debug)


if __name__ == "__main__":
    main()
