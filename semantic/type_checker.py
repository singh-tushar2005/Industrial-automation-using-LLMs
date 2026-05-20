"""
Beginner-friendly semantic type checker for Structured Text ASTs.

Static semantic analysis means checking program meaning before the program
runs. Syntax answers "is the text shaped like Structured Text?" Semantics asks
"does this program make sense?"

Examples:

    Temp > 100              valid when Temp is numeric
    StartButton AND 1       invalid because AND needs booleans
    Alarm := 42             invalid if Alarm is a boolean variable

Why type checking matters in industrial systems
-----------------------------------------------
Industrial automation code controls real equipment. A type mistake can hide a
logic defect in alarms, safety interlocks, motor commands, counters, and sensor
thresholds. Catching these mistakes early makes migrations safer and gives a
future IEC 61499 transformation pipeline stronger guarantees about the meaning
of the source program.

How this supports IEC 61499 transformation
------------------------------------------
IEC 61499 transformations need more than syntax. They need to know whether a
node is a boolean condition, numeric calculation, variable write, or dependency.
This type-checking visitor is an early semantic pass that can later feed
function block generation, event/data connection mapping, and verification.
"""

try:
    # Works when imported as a package from the project root.
    from semantic.symbol_table import SymbolTable
    from semantic.visitor import ASTVisitor, load_st_parser_module
except ModuleNotFoundError:
    # Works when this file is run directly from inside semantic/.
    from symbol_table import SymbolTable
    from visitor import ASTVisitor, load_st_parser_module


TYPE_BOOL = "BOOL"
TYPE_NUMBER = "NUMBER"
TYPE_UNKNOWN = "UNKNOWN"


class TypeChecker(ASTVisitor):
    """Semantic visitor that validates expression and assignment types.

    The visitor recursively walks the AST. Statement visits mainly check their
    children. Expression visits return the expression's type so parent nodes can
    validate operators.
    """

    def __init__(self, symbol_table=None):
        # A caller may pass a preloaded symbol table from declarations or test
        # setup. If not, we start empty and infer assignment target types.
        self.symbol_table = symbol_table or SymbolTable()

        # Semantic errors mean the program is invalid.
        self.errors = []

        # Warnings mean the checker lacks declaration information. The current
        # ST subset has no VAR declarations, so unknown input variables are
        # expected until declaration parsing is added.
        self.warnings = []

    def error(self, message):
        """Record a semantic error."""

        self.errors.append(message)

    def warning(self, message):
        """Record a semantic warning."""

        self.warnings.append(message)

    def check(self, ast):
        """Run type checking on an AST and return True when no errors exist."""

        self.visit(ast)
        return not self.errors

    def print_report(self):
        """Print symbols, warnings, and errors clearly for beginners."""

        self.symbol_table.print_symbols()

        print("\nType checking report:")

        if not self.warnings and not self.errors:
            print("  No warnings or errors.")
            return

        if self.warnings:
            print("  Warnings:")
            for warning in self.warnings:
                print(f"    - {warning}")

        if self.errors:
            print("  Errors:")
            for error in self.errors:
                print(f"    - {error}")

    # ------------------------------------------------------------------
    # Program and statement nodes
    # ------------------------------------------------------------------

    def visit_ProgramNode(self, node):
        """A program's type is not a value; check its body statements."""

        self.visit(node.body)
        return None

    def visit_BlockNode(self, node):
        """Check every statement in order."""

        for statement in node.statements:
            self.visit(statement)

        return None

    def visit_IfStatementNode(self, node):
        """An IF condition must be boolean, then its body is checked."""

        condition_type = self.visit(node.condition)

        if condition_type not in (TYPE_BOOL, TYPE_UNKNOWN):
            self.error(
                "IF condition must be BOOL, "
                f"but found {condition_type} in {node.condition!r}"
            )

        self.visit(node.then_body)
        return None

    def visit_AssignmentNode(self, node):
        """Check that the assigned value matches the target variable type."""

        target_name = node.target.name
        value_type = self.visit(node.value)
        existing_target_type = self.symbol_table.lookup(target_name)

        if existing_target_type is None:
            # With no declarations, first assignment is a useful place to infer
            # a variable's type. If the value is unknown, keep the target
            # unknown too, rather than guessing.
            inferred_type = value_type if value_type is not None else TYPE_UNKNOWN
            self.symbol_table.insert(target_name, inferred_type)
            return None

        if TYPE_UNKNOWN in (existing_target_type, value_type):
            return None

        if existing_target_type != value_type:
            self.error(
                f"Cannot assign {value_type} value to {existing_target_type} "
                f"variable {target_name!r}"
            )

        return None

    # ------------------------------------------------------------------
    # Expression nodes
    # ------------------------------------------------------------------

    def visit_BinaryExpressionNode(self, node):
        """Check arithmetic and comparison binary expressions."""

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        operator = node.operator

        if operator in ("+", "-", "*", "/"):
            return self.check_arithmetic_expression(node, left_type, right_type)

        if operator in (">", ">=", "<", "<="):
            return self.check_numeric_comparison(node, left_type, right_type)

        if operator in ("=", "<>"):
            return self.check_equality_comparison(node, left_type, right_type)

        self.error(f"Unknown binary operator {operator!r}")
        return TYPE_UNKNOWN

    def check_arithmetic_expression(self, node, left_type, right_type):
        """Arithmetic operators require numeric operands and return NUMBER."""

        if self.has_unknown_operand(left_type, right_type):
            return TYPE_UNKNOWN

        if left_type != TYPE_NUMBER or right_type != TYPE_NUMBER:
            self.error(
                f"Arithmetic operator {node.operator!r} requires NUMBER operands, "
                f"but found {left_type} and {right_type}"
            )
            return TYPE_UNKNOWN

        return TYPE_NUMBER

    def check_numeric_comparison(self, node, left_type, right_type):
        """Ordering comparisons require numbers and return BOOL."""

        if self.has_unknown_operand(left_type, right_type):
            return TYPE_BOOL

        if left_type != TYPE_NUMBER or right_type != TYPE_NUMBER:
            self.error(
                f"Comparison operator {node.operator!r} requires NUMBER operands, "
                f"but found {left_type} and {right_type}"
            )

        return TYPE_BOOL

    def check_equality_comparison(self, node, left_type, right_type):
        """Equality can compare matching known types and returns BOOL."""

        if self.has_unknown_operand(left_type, right_type):
            return TYPE_BOOL

        if left_type != right_type:
            self.error(
                f"Equality operator {node.operator!r} requires matching types, "
                f"but found {left_type} and {right_type}"
            )

        return TYPE_BOOL

    def visit_LogicalExpressionNode(self, node):
        """Logical operators require boolean operands and return BOOL."""

        operand_types = [self.visit(operand) for operand in node.operands]

        for operand_type in operand_types:
            if operand_type in (TYPE_BOOL, TYPE_UNKNOWN):
                continue

            self.error(
                f"Logical operator {node.operator!r} requires BOOL operands, "
                f"but found {operand_type}"
            )

        return TYPE_BOOL

    def visit_VariableNode(self, node):
        """Look up a variable's type in the symbol table."""

        variable_type = self.symbol_table.lookup(node.name)

        if variable_type is None:
            self.warning(
                f"Variable {node.name!r} has no known type; "
                "add declarations or pre-populate the symbol table"
            )
            self.symbol_table.insert(node.name, TYPE_UNKNOWN)
            return TYPE_UNKNOWN

        return variable_type

    def visit_BooleanNode(self, node):
        """Boolean literals always have BOOL type."""

        return TYPE_BOOL

    def visit_NumberNode(self, node):
        """Numeric literals always have NUMBER type."""

        return TYPE_NUMBER

    def has_unknown_operand(self, left_type, right_type):
        """Return True when an expression cannot be fully checked yet."""

        return TYPE_UNKNOWN in (left_type, right_type)


def build_demo_symbol_table():
    """Create known variable types for the current dataset examples.

    Real IEC 61131-3 projects would usually get these from VAR declarations,
    PLC tag databases, or engineering exports. The current grammar does not
    parse declarations yet, so the demo preloads the variables used by datasets/.
    """

    symbols = SymbolTable()
    symbols.insert("Alarm", TYPE_BOOL)
    symbols.insert("Counter", TYPE_NUMBER)
    symbols.insert("Limit", TYPE_NUMBER)
    symbols.insert("Motor", TYPE_BOOL)
    symbols.insert("SafetyOK", TYPE_BOOL)
    symbols.insert("StartButton", TYPE_BOOL)
    symbols.insert("Temp", TYPE_NUMBER)
    symbols.insert("Warning", TYPE_BOOL)
    return symbols


def type_check_dataset_files():
    """Parse each dataset file and run the semantic type checker."""

    st_parser = load_st_parser_module()
    dataset_files = st_parser.find_dataset_files()

    if not dataset_files:
        print(f"No .st files found in {st_parser.DATASETS_DIR}.")
        return

    for index, file_path in enumerate(dataset_files):
        if index > 0:
            print("\n" + "-" * 72 + "\n")

        print(f"Type checking: {file_path}")
        ast = st_parser.parse_st_file(file_path)
        checker = TypeChecker(build_demo_symbol_table())
        checker.check(ast)
        checker.print_report()


if __name__ == "__main__":
    type_check_dataset_files()
