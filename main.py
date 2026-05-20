"""Central orchestration entrypoint for the Structured Text pipeline."""

from pathlib import Path
from pprint import pprint

from pyparsing import ParseException

from parser.st_parser import DATASETS_DIR, find_dataset_files, parse_st_file
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


def process_st_file(file_path):
    """Run the complete parse -> semantic traversal -> type check pipeline."""

    print_section(f"Dataset file: {file_path}")

    try:
        ast = parse_st_file(file_path)
    except ParseException as error:
        print("Parse result: FAILED")
        print(error)
        return False

    print("Parse result: OK")

    print_subsection("Generated AST")
    pprint(ast)

    print_subsection("Semantic Visitor Traversal")
    traversal_results = run_semantic_traversal(ast)
    print_traversal_results(traversal_results)

    print_subsection("Semantic Type Checking")
    type_check_report = run_type_checking(ast)
    print_type_check_report(type_check_report)

    if type_check_report["program_is_valid"]:
        print("\nPipeline result: OK")
    else:
        print("\nPipeline result: SEMANTIC ERRORS FOUND")

    return type_check_report["program_is_valid"]


def run_pipeline(dataset_files):
    """Run every Structured Text file through the centralized pipeline."""

    passed_count = 0

    for file_path in dataset_files:
        if process_st_file(file_path):
            passed_count += 1

    total_count = len(dataset_files)

    print_section("Pipeline Summary")
    print(f"Files processed: {total_count}")
    print(f"Files passed:    {passed_count}")
    print(f"Files failed:    {total_count - passed_count}")


def main():
    """Project entrypoint used by `uv run python main.py`."""

    dataset_files = load_dataset_files()

    if not dataset_files:
        print(f"No .st files found in {Path(DATASETS_DIR)}.")
        return

    run_pipeline(dataset_files)


if __name__ == "__main__":
    main()
