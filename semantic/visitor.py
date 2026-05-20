"""
Beginner-friendly semantic traversal for Structured Text ASTs.

The parser builds an Abstract Syntax Tree (AST). The semantic layer walks that
tree to understand what the program means.

This file demonstrates the Visitor Pattern:

    * visit(node) looks at the node type.
    * It dispatches to a matching method such as visit_IfStatementNode().
    * Each node-specific method prints what it found.
    * Container nodes recursively visit their child nodes.

Why compilers use visitors
--------------------------
Compilers perform many passes over the same AST:

    * semantic checks
    * type checking
    * variable collection
    * control-flow analysis
    * code generation
    * migration to another language or runtime model

The Visitor Pattern keeps those operations out of the AST node classes. That is
important here because ast/nodes.py should stay focused on data structures,
while semantic/visitor.py focuses on analysis and traversal behavior.

Why this helps IEC 61499 transformation work
--------------------------------------------
Future IEC 61499 migration passes will need to walk IEC 61131-3 Structured Text
programs and recognize meaning: assignments, conditions, dependencies, nested
control logic, and expressions. This visitor is the small first step toward
passes that can map ST logic into function blocks, events, data connections,
and execution control charts.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


class ASTVisitor:
    """Base visitor with generic visit() dispatch.

    The AST nodes in this project are intentionally simple Python classes. They
    do not know how to visit themselves, and they do not need to. The visitor
    decides what to do based on each node's class name.

    Example:

        ProgramNode(...) -> visit_ProgramNode(...)
        IfStatementNode(...) -> visit_IfStatementNode(...)

    Dispatching by class name also keeps this visitor compatible with the
    parser's path-based AST imports. If the same nodes.py file is loaded by two
    modules, Python can create two different class objects with the same names.
    Name-based dispatch avoids fragile isinstance checks in this teaching code.
    """

    def visit(self, node):
        """Visit one AST node by calling its node-specific method."""

        if node is None:
            return None

        node_type_name = node.__class__.__name__
        method_name = f"visit_{node_type_name}"
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        """Raise a clear error when a node type has no visitor method yet."""

        node_type_name = node.__class__.__name__
        raise NotImplementedError(f"No visitor method defined for {node_type_name}")


class PrintingSemanticVisitor(ASTVisitor):
    """Visitor that recursively prints the structure and meaning of an AST.

    This is not a full semantic analyzer yet. It is traversal infrastructure:
    the same recursive shape can later be reused for type checking, symbol
    tables, dependency graphs, IEC 61499 transformations, and diagnostics.
    """

    def __init__(self):
        # depth controls indentation, making nested AST structure easy to see.
        self.depth = 0

    def print_line(self, message):
        """Print one traversal line with indentation for the current depth."""

        indentation = "  " * self.depth
        print(f"{indentation}{message}")

    def visit_child(self, label, child_node):
        """Print a label, then recursively visit one child node."""

        self.print_line(label)
        self.depth += 1
        self.visit(child_node)
        self.depth -= 1

    def visit_children(self, label, child_nodes):
        """Print a label, then recursively visit a list of child nodes."""

        self.print_line(label)
        self.depth += 1

        for index, child_node in enumerate(child_nodes, start=1):
            self.print_line(f"Statement {index}")
            self.depth += 1
            self.visit(child_node)
            self.depth -= 1

        self.depth -= 1

    def visit_ProgramNode(self, node):
        """Visit a complete Structured Text program."""

        self.print_line("ProgramNode: start of Structured Text program")
        self.depth += 1
        self.visit(node.body)
        self.depth -= 1
        self.print_line("ProgramNode: end of program")

    def visit_BlockNode(self, node):
        """Visit an ordered block of statements."""

        statement_count = len(node.statements)
        self.print_line(f"BlockNode: {statement_count} statement(s)")
        self.visit_children("Block contents:", node.statements)

    def visit_IfStatementNode(self, node):
        """Visit an IF statement and recursively traverse its condition/body."""

        self.print_line("IfStatementNode: conditional execution")
        self.depth += 1
        self.visit_child("Condition:", node.condition)
        self.visit_child("THEN body:", node.then_body)
        self.depth -= 1

    def visit_AssignmentNode(self, node):
        """Visit an assignment target and assigned value."""

        self.print_line("AssignmentNode: write value into variable")
        self.depth += 1
        self.visit_child("Target variable:", node.target)
        self.visit_child("Assigned expression:", node.value)
        self.depth -= 1

    def visit_BinaryExpressionNode(self, node):
        """Visit arithmetic and comparison expressions with left/right sides."""

        self.print_line(f"BinaryExpressionNode: operator {node.operator!r}")
        self.depth += 1
        self.visit_child("Left expression:", node.left)
        self.visit_child("Right expression:", node.right)
        self.depth -= 1

    def visit_LogicalExpressionNode(self, node):
        """Visit logical expressions such as AND, OR, and NOT."""

        operand_count = len(node.operands)
        self.print_line(
            f"LogicalExpressionNode: operator {node.operator!r} "
            f"with {operand_count} operand(s)"
        )
        self.depth += 1

        for index, operand in enumerate(node.operands, start=1):
            self.visit_child(f"Operand {index}:", operand)

        self.depth -= 1

    def visit_VariableNode(self, node):
        """Visit a variable reference."""

        self.print_line(f"VariableNode: variable name {node.name!r}")

    def visit_BooleanNode(self, node):
        """Visit a TRUE/FALSE literal."""

        self.print_line(f"BooleanNode: boolean value {node.value!r}")

    def visit_NumberNode(self, node):
        """Visit a numeric literal."""

        self.print_line(f"NumberNode: numeric value {node.value!r}")


def load_st_parser_module():
    """Load parser/st_parser.py for the demo runner.

    The semantic visitor does not own parsing. It simply consumes ASTs. This
    helper is only here so running this file directly can parse the dataset
    examples and immediately demonstrate traversal.
    """

    project_root = Path(__file__).resolve().parents[1]
    parser_path = project_root / "parser" / "st_parser.py"
    parser_spec = spec_from_file_location("industrial_automation_st_parser", parser_path)
    parser_module = module_from_spec(parser_spec)
    parser_spec.loader.exec_module(parser_module)
    return parser_module


def traverse_dataset_files():
    """Parse each dataset .st file, then recursively print its AST traversal."""

    st_parser = load_st_parser_module()
    visitor = PrintingSemanticVisitor()
    dataset_files = st_parser.find_dataset_files()

    if not dataset_files:
        print(f"No .st files found in {st_parser.DATASETS_DIR}.")
        return

    for index, file_path in enumerate(dataset_files):
        if index > 0:
            print("\n" + "-" * 72 + "\n")

        print(f"Semantic traversal for: {file_path}")
        ast = st_parser.parse_st_file(file_path)
        visitor.visit(ast)


if __name__ == "__main__":
    traverse_dataset_files()
