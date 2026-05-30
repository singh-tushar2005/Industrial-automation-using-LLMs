"""Semantic type checker for Structured Text ASTs."""

try:
    # Works when imported as a package from the project root.
    from semantic.symbol_table import SymbolTable
    from semantic.visitor import ASTVisitor
except ModuleNotFoundError:
    # Works when this file is run directly from inside semantic/.
    from symbol_table import SymbolTable
    from visitor import ASTVisitor


TYPE_BOOL = "BOOL"
TYPE_NUMBER = "NUMBER"
TYPE_TIME = "TIME"
TYPE_UNKNOWN = "UNKNOWN"


class TypeChecker(ASTVisitor):
    """Semantic visitor that validates expression and assignment types."""

    def __init__(self, symbol_table=None):
        self.symbol_table = symbol_table or SymbolTable()
        self.errors = []
        self.warnings = []
        self.analysis_results = {}

    def error(self, message):
        """Record a semantic error."""

        self.errors.append(message)

    def warning(self, message):
        """Record a semantic warning."""

        self.warnings.append(message)

    def check(self, ast):
        """Run type checking on an AST and return True when no errors exist."""

        self.visit(ast)
        self.analysis_results["program_is_valid"] = not self.errors
        self.analysis_results["symbol_count"] = len(self.symbol_table.symbols)
        return not self.errors

    def get_report(self):
        """Return all type-checking results without printing anything."""

        return {
            "program_is_valid": not self.errors,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "symbols": self.symbol_table.to_dict(),
            "analysis_results": dict(self.analysis_results),
        }

    # ------------------------------------------------------------------
    # Program and statement nodes
    # ------------------------------------------------------------------

    def visit_ProgramNode(self, node):
        """A program's type is not a value; check its body statements."""

        self.visit(node.body)
        return None

    def visit_CompilationUnitNode(self, node):
        """A compilation unit's type is not a value; check its body."""

        self.visit(node.body)
        return None

    def visit_VarBlockNode(self, node):
        """Variable declaration blocks have no executable type."""

        return None

    def visit_VariableDeclarationNode(self, node):
        """Variable declarations have no executable type."""

        return None

    def visit_BlockNode(self, node):
        """Check every statement in order."""

        for statement in node.statements:
            self.visit(statement)

        return None

    def visit_CaseStatementNode(self, node):
        """Check selector, branches, and optional ELSE body."""

        self.visit(node.selector)

        for branch in node.branches:
            self.visit(branch)

        if node.else_body is not None:
            self.visit(node.else_body)

        return None

    def visit_CaseBranchNode(self, node):
        """Check one CASE branch."""

        self.visit(node.match_value)
        self.visit(node.body)
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

        for elsif_condition, elsif_body in node.elsif_branches:
            elsif_condition_type = self.visit(elsif_condition)
            if elsif_condition_type not in (TYPE_BOOL, TYPE_UNKNOWN):
                self.error(
                    "ELSIF condition must be BOOL, "
                    f"but found {elsif_condition_type} in {elsif_condition!r}"
                )
            self.visit(elsif_body)

        if node.else_body is not None:
            self.visit(node.else_body)

        return None

    def visit_AssignmentNode(self, node):
        """Check that the assigned value matches the target variable type."""

        if node.target.__class__.__name__ == "ArrayIndexNode":
            target_name = node.target.array
        else:
            target_name = node.target.name
        value_type = self.visit(node.value)
        existing_target_type = self.symbol_table.lookup(target_name)

        if existing_target_type is None:
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

    def visit_FunctionBlockCallNode(self, node):
        """Check function block call argument expressions."""

        for argument in node.arguments:
            argument_name = argument.name
            argument_value = argument.value
            argument_type = self.visit(argument_value)

            if argument_name in ("IN", "CU", "CD", "R", "RESET", "LOAD"):
                if argument_type not in (TYPE_BOOL, TYPE_UNKNOWN):
                    self.error(
                        f"Function block argument {argument_name!r} should be BOOL, "
                        f"but found {argument_type}"
                    )

            if argument_name in ("PT", "PV"):
                if argument_type not in (TYPE_TIME, TYPE_NUMBER, TYPE_UNKNOWN):
                    self.error(
                        f"Function block argument {argument_name!r} should be TIME "
                        f"or NUMBER, but found {argument_type}"
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

    def visit_TimeLiteralNode(self, node):
        """IEC time literals have TIME type."""

        return TYPE_TIME

    def visit_TypedLiteralNode(self, node):
        """Typed literals map to their corresponding type."""

        type_map = {
            "BOOL": TYPE_BOOL,
            "BYTE": TYPE_NUMBER,
            "WORD": TYPE_NUMBER,
            "DWORD": TYPE_NUMBER,
            "INT": TYPE_NUMBER,
            "DINT": TYPE_NUMBER,
            "UINT": TYPE_NUMBER,
            "UDINT": TYPE_NUMBER,
            "REAL": TYPE_NUMBER,
            "TIME": TYPE_TIME,
            "STRING": "STRING",
        }
        return type_map.get(node.type_name.upper(), TYPE_UNKNOWN)

    def visit_ArrayIndexNode(self, node):
        """Array indexing returns the element type, which is unknown here."""

        self.visit(node.array)
        self.visit(node.index)
        return TYPE_UNKNOWN

    def visit_FunctionInvocationNode(self, node):
        """Function invocations return an unknown type without a signature table."""

        for argument in node.arguments:
            self.visit(argument.value)
        return TYPE_UNKNOWN

    def visit_InvocationArgumentNode(self, node):
        """Invocation arguments have no standalone type."""

        self.visit(node.value)
        return None

    def visit_ForLoopNode(self, node):
        """Check FOR loop body."""

        self.visit(node.start_expr)
        self.visit(node.end_expr)
        if node.step_expr is not None:
            self.visit(node.step_expr)
        self.visit(node.body)
        return None

    def visit_WhileLoopNode(self, node):
        """Check WHILE loop condition and body."""

        condition_type = self.visit(node.condition)
        if condition_type not in (TYPE_BOOL, TYPE_UNKNOWN):
            self.error(
                "WHILE condition must be BOOL, "
                f"but found {condition_type} in {node.condition!r}"
            )
        self.visit(node.body)
        return None

    def visit_RepeatLoopNode(self, node):
        """Check REPEAT loop condition and body."""

        condition_type = self.visit(node.condition)
        if condition_type not in (TYPE_BOOL, TYPE_UNKNOWN):
            self.error(
                "REPEAT UNTIL condition must be BOOL, "
                f"but found {condition_type} in {node.condition!r}"
            )
        self.visit(node.body)
        return None

    def visit_ExitNode(self, node):
        """EXIT has no type."""

        return None

    def visit_ReturnNode(self, node):
        """RETURN has no type; check value if present."""

        if node.value is not None:
            self.visit(node.value)
        return None

    def visit_ArrayTypeNode(self, node):
        """Array type declarations have no executable type."""

        return None

    def visit_ConfigurationNode(self, node):
        """Configuration declarations have no executable type; check body."""

        self.visit(node.body)
        return None

    def visit_ResourceNode(self, node):
        """Resource declarations have no executable type; check body."""

        self.visit(node.body)
        return None

    def visit_TaskNode(self, node):
        """Task declarations have no executable type; check arguments."""

        for argument in node.arguments:
            if hasattr(argument, "value"):
                self.visit(argument)
            elif isinstance(argument, (tuple, list)) and len(argument) == 2:
                self.visit(argument[1])
        return None

    def visit_ProgramBindingNode(self, node):
        """Program bindings have no executable type."""

        return None

    def visit_MemoryMappingNode(self, node):
        """Memory mappings have no executable type."""

        return None

    def visit_StringLiteralNode(self, node):
        """String literals have no known type in the current type system."""

        return TYPE_UNKNOWN

    def has_unknown_operand(self, left_type, right_type):
        """Return True when an expression cannot be fully checked yet."""

        return TYPE_UNKNOWN in (left_type, right_type)


def build_demo_symbol_table():
    """Create known variable types for the current dataset examples."""

    symbols = SymbolTable()
    symbols.insert("Alarm", TYPE_BOOL)
    symbols.insert("Counter", TYPE_NUMBER)
    symbols.insert("Limit", TYPE_NUMBER)
    symbols.insert("Motor", TYPE_BOOL)
    symbols.insert("SafetyOK", TYPE_BOOL)
    symbols.insert("StartButton", TYPE_BOOL)
    symbols.insert("Temp", TYPE_NUMBER)
    symbols.insert("Warning", TYPE_BOOL)
    symbols.insert("AutoMode", TYPE_BOOL)
    symbols.insert("ManualMode", TYPE_BOOL)
    symbols.insert("EmergencyStop", TYPE_BOOL)
    symbols.insert("FaultActive", TYPE_BOOL)
    symbols.insert("FaultReset", TYPE_BOOL)
    symbols.insert("DoorClosed", TYPE_BOOL)
    symbols.insert("GuardClosed", TYPE_BOOL)
    symbols.insert("TankLevel", TYPE_NUMBER)
    symbols.insert("HighLevel", TYPE_NUMBER)
    symbols.insert("LowLevel", TYPE_NUMBER)
    symbols.insert("Pressure", TYPE_NUMBER)
    symbols.insert("PressureHighLimit", TYPE_NUMBER)
    symbols.insert("Temperature", TYPE_NUMBER)
    symbols.insert("TempHighLimit", TYPE_NUMBER)
    symbols.insert("Pump", TYPE_BOOL)
    symbols.insert("InletValve", TYPE_BOOL)
    symbols.insert("OutletValve", TYPE_BOOL)
    symbols.insert("Mixer", TYPE_BOOL)
    symbols.insert("Heater", TYPE_BOOL)
    symbols.insert("CoolingValve", TYPE_BOOL)
    symbols.insert("Conveyor", TYPE_BOOL)
    symbols.insert("Clamp", TYPE_BOOL)
    symbols.insert("Cutter", TYPE_BOOL)
    symbols.insert("StartupStep", TYPE_NUMBER)
    symbols.insert("SequenceStep", TYPE_NUMBER)
    symbols.insert("BatchStep", TYPE_NUMBER)
    symbols.insert("FaultCode", TYPE_NUMBER)
    symbols.insert("SystemReady", TYPE_BOOL)
    symbols.insert("SensorPresent", TYPE_BOOL)
    symbols.insert("GuardOpen", TYPE_BOOL)
    symbols.insert("Mode", TYPE_NUMBER)
    symbols.insert("ProcessEnable", TYPE_BOOL)
    symbols.insert("StartCommand", TYPE_BOOL)
    symbols.insert("StopCommand", TYPE_BOOL)
    symbols.insert("MotorRun", TYPE_BOOL)
    symbols.insert("MotorContactor", TYPE_BOOL)
    symbols.insert("OverloadTrip", TYPE_BOOL)
    symbols.insert("StartTimer.Q", TYPE_BOOL)
    symbols.insert("StopTimer.Q", TYPE_BOOL)
    symbols.insert("PurgeTimer.Q", TYPE_BOOL)
    symbols.insert("FillTimer.Q", TYPE_BOOL)
    symbols.insert("MixTimer.Q", TYPE_BOOL)
    symbols.insert("FaultTimer.Q", TYPE_BOOL)
    symbols.insert("PulseTimer.Q", TYPE_BOOL)
    symbols.insert("CounterDone", TYPE_BOOL)
    return symbols
