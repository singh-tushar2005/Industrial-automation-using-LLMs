"""Integration test for grammar primitives across AST and all semantic visitors.

Verifies that FOR loops, function block invocations, and time literals are
fully integrated: parser -> AST -> every visitor pass without missing methods.

Run: python -m compiler.test_ast_visitor_integration
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parser.st_parser import parse_st_program
from semantic.visitor import SemanticTraversalVisitor
from semantic.classifier import IndustrialSemanticClassifier
from semantic.type_checker import TypeChecker, build_demo_symbol_table
from semantic.relationship_extractor import RelationshipExtractor
from semantic.graph_builder import SemanticGraphBuilder

# ---------------------------------------------------------------------------
# Test code that exercises all three grammar primitives
# ---------------------------------------------------------------------------
TEST_CODE = """
PROGRAM IntegrationTest
  VAR
    Counter : INT;
    Motor   : BOOL;
    Timer1  : TON;
  END_VAR

  FOR Counter := 1 TO 5 DO
    Counter := Counter + 1;
    Timer1(IN := TRUE, PT := T#2s);
    IF Timer1.Q THEN
      Motor := TRUE;
    END_IF;
  END_FOR;

  WHILE Motor DO
    Timer1(IN := FALSE, PT := T#100ms);
    Motor := FALSE;
  END_WHILE;

  FOR Counter := 10 TO 1 BY -1 DO
    EXIT;
  END_FOR;
END_PROGRAM
"""


# ---------------------------------------------------------------------------
# AST node inventory helpers
# ---------------------------------------------------------------------------

def gather_ast_node_types(node, types=None):
    """Recursively collect all AST node class names present in a tree."""
    if types is None:
        types = set()
    if node is None or isinstance(node, (bool, int, float, str, tuple)):
        return types
    types.add(node.__class__.__name__)
    for attr in (
        "body", "statements", "condition", "then_body", "else_body",
        "branches", "left", "right", "operands", "value", "target",
        "arguments", "selector", "match_value", "start_expr", "end_expr",
        "step_expr", "variable", "var_blocks", "declarations", "array", "index",
        "elsif_branches", "kind", "names", "var_type", "default_value",
        "element_type", "bounds", "name", "type_name", "return_type",
    ):
        child = getattr(node, attr, None)
        if child is None:
            continue
        if isinstance(child, list):
            for item in child:
                gather_ast_node_types(item, types)
        else:
            gather_ast_node_types(child, types)
    return types


# ---------------------------------------------------------------------------
# Safe visitor that records missing methods instead of crashing
# ---------------------------------------------------------------------------

class SafeVisitor(SemanticTraversalVisitor):
    """Visitor subclass that records missing methods instead of crashing."""

    def __init__(self):
        super().__init__()
        self.missing_methods = []

    def generic_visit(self, node):
        node_type_name = node.__class__.__name__
        method_name = f"visit_{node_type_name}"
        self.missing_methods.append(method_name)
        self.record_line(f"MISSING VISITOR: {method_name} — node skipped")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def _test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    detail_str = f"  -> {detail}" if detail else ""
    print(f"  [{status:40s}] {name}{detail_str}")
    return condition


def main():
    all_passed = True

    print("=" * 60)
    print("AST + VISITOR INTEGRATION TEST")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Parse
    # ------------------------------------------------------------------
    print("\n[Parser]")
    try:
        ast = parse_st_program(TEST_CODE)
        all_passed &= _test("parse succeeds", True)
    except Exception as exc:
        all_passed &= _test("parse succeeds", False, str(exc)[:120])
        print("\nCannot continue without AST.")
        return 1

    # ------------------------------------------------------------------
    # 2. AST node inventory
    # ------------------------------------------------------------------
    print("\n[AST Nodes]")
    present_types = gather_ast_node_types(ast)

    required_nodes = {
        "ProgramNode",
        "CompilationUnitNode",
        "VarBlockNode",
        "VariableDeclarationNode",
        "ForLoopNode",
        "WhileLoopNode",
        "IfStatementNode",
        "AssignmentNode",
        "FunctionBlockCallNode",
        "InvocationArgumentNode",
        "TimeLiteralNode",
        "VariableNode",
        "BooleanNode",
        "NumberNode",
        "BinaryExpressionNode",
        "BlockNode",
        "ExitNode",
    }

    for node_type in required_nodes:
        all_passed &= _test(
            f"AST node: {node_type}",
            node_type in present_types,
            f"present: {present_types}"
        )

    # ------------------------------------------------------------------
    # 3. Semantic traversal visitor
    # ------------------------------------------------------------------
    print("\n[SemanticTraversalVisitor]")
    visitor = SafeVisitor()
    try:
        traversal = visitor.traverse(ast)
        all_passed &= _test("traversal succeeds", True)
        all_passed &= _test(
            "no missing visitor methods",
            not visitor.missing_methods,
            f"missing: {visitor.missing_methods}"
        )
    except Exception as exc:
        all_passed &= _test("traversal succeeds", False, str(exc)[:120])

    # ------------------------------------------------------------------
    # 4. Type checker
    # ------------------------------------------------------------------
    print("\n[TypeChecker]")
    try:
        checker = TypeChecker(build_demo_symbol_table())
        checker.check(ast)
        report = checker.get_report()
        all_passed &= _test("type check completes", True)
        all_passed &= _test(
            "type check has no errors",
            not report["errors"],
            f"errors: {report['errors']}"
        )
    except Exception as exc:
        all_passed &= _test("type check completes", False, str(exc)[:120])

    # ------------------------------------------------------------------
    # 5. Industrial classifier
    # ------------------------------------------------------------------
    print("\n[IndustrialSemanticClassifier]")
    try:
        classifier = IndustrialSemanticClassifier(report)
        classification = classifier.classify(ast)
        all_passed &= _test("classification completes", True)
        all_passed &= _test(
            "classification has findings",
            classification["finding_count"] > 0,
            f"findings: {classification['finding_count']}"
        )
    except Exception as exc:
        all_passed &= _test("classification completes", False, str(exc)[:120])

    # ------------------------------------------------------------------
    # 6. Relationship extractor
    # ------------------------------------------------------------------
    print("\n[RelationshipExtractor]")
    try:
        extractor = RelationshipExtractor(classification, report)
        relationships = extractor.extract(ast)
        all_passed &= _test("relationship extraction completes", True)
        all_passed &= _test(
            "relationships are extracted",
            relationships["relationship_count"] > 0,
            f"count: {relationships['relationship_count']}"
        )
    except Exception as exc:
        all_passed &= _test("relationship extraction completes", False, str(exc)[:120])

    # ------------------------------------------------------------------
    # 7. Semantic graph builder
    # ------------------------------------------------------------------
    print("\n[SemanticGraphBuilder]")
    try:
        builder = SemanticGraphBuilder()
        graph = builder.build(relationships)
        all_passed &= _test("graph build completes", True)
        all_passed &= _test(
            "graph has nodes and edges",
            graph.node_count() > 0 and graph.edge_count() > 0,
            f"nodes={graph.node_count()} edges={graph.edge_count()}"
        )
    except Exception as exc:
        all_passed &= _test("graph build completes", False, str(exc)[:120])

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    if all_passed:
        print("ALL INTEGRATION TESTS PASSED")
    else:
        print("SOME INTEGRATION TESTS FAILED")
    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
