"""Operation extractor for computational and control semantics.

Extracts high-level industrial operations from AST executable nodes.
Operates in parallel with the relationship extractor; it does not
produce relationships or graph edges.
"""

from collections import Counter

try:
    from semantic.operations import Operation
    from semantic.context.test_detector import TestDetector
except ModuleNotFoundError:
    from operations import Operation
    from context.test_detector import TestDetector


class OperationExtractor:
    """Extract industrial operations from an AST.

    Supports:
    - AssignmentNode
    - IfStatementNode
    - CaseStatementNode
    - ForLoopNode
    - WhileLoopNode
    - RepeatLoopNode
    """

    def __init__(self, context=None, test_detector=None):
        self.context = context
        self.operations = []
        self.test_detector = test_detector
        if self.test_detector is None:
            self.test_detector = TestDetector()

    def extract(self, ast):
        """Run extraction and return structured results."""
        self.test_detector.detect(ast)
        self.visit(ast)
        return self.get_results()

    def get_results(self):
        industrial_ops = [op for op in self.operations if op.metadata.get("semantic_scope") == "INDUSTRIAL"]
        test_ops = [op for op in self.operations if op.metadata.get("semantic_scope") == "TEST"]
        return {
            "operations": [op.to_dict() for op in self.operations],
            "operation_counts": dict(Counter(op.operation_type for op in self.operations)),
            "total_operations": len(self.operations),
            "industrial_operations": [op.to_dict() for op in industrial_ops],
            "industrial_operation_counts": dict(Counter(op.operation_type for op in industrial_ops)),
            "industrial_total_operations": len(industrial_ops),
            "test_operations": [op.to_dict() for op in test_ops],
            "test_operation_counts": dict(Counter(op.operation_type for op in test_ops)),
            "test_total_operations": len(test_ops),
        }

    # ------------------------------------------------------------------
    # Visitor dispatch
    # ------------------------------------------------------------------

    def visit(self, node):
        if node is None:
            return
        node_type = node.__class__.__name__
        method = getattr(self, f"visit_{node_type}", self.generic_visit)
        method(node)

    def generic_visit(self, node):
        for attr in (
            "body", "then_body", "else_body", "statements", "branches",
            "elsif_branches", "operands", "left", "right", "arguments",
            "value", "target", "condition", "start_expr", "end_expr", "step_expr",
            "var_blocks", "declarations",
        ):
            child = getattr(node, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    self.visit(item)
            else:
                self.visit(child)

    # ------------------------------------------------------------------
    # Specific visitors
    # ------------------------------------------------------------------

    def visit_AssignmentNode(self, node):
        op_type = self._classify_assignment(node)
        target = self._describe(node.target)
        sources = self._extract_sources(node.value)
        self._add_operation(op_type, target, sources, "AssignmentNode", node)
        self.generic_visit(node)

    def visit_IfStatementNode(self, node):
        comparisons = self._extract_comparisons(node.condition)
        for sources in comparisons:
            self._add_operation("comparison_operation", None, sources, "IfStatementNode", node)
        self.generic_visit(node)

    def visit_CaseStatementNode(self, node):
        selector = self._describe(node.selector)
        self._add_operation("lookup_operation", selector, [], "CaseStatementNode", node)
        self.generic_visit(node)

    def visit_ForLoopNode(self, node):
        self._add_operation("iterative_computation", None, [], "ForLoopNode", node)
        self.generic_visit(node)

    def visit_WhileLoopNode(self, node):
        self._add_operation("iterative_computation", None, [], "WhileLoopNode", node)
        self.generic_visit(node)

    def visit_RepeatLoopNode(self, node):
        self._add_operation("iterative_computation", None, [], "RepeatLoopNode", node)
        self.generic_visit(node)

    def visit_FunctionBlockCallNode(self, node):
        fb_name = node.name.upper()
        if fb_name.startswith(("TON", "TOF", "TP")) or "TIMER" in fb_name:
            op_type = "timer_invocation"
        elif fb_name.startswith(("CTU", "CTD", "CTUD")) or "COUNTER" in fb_name:
            op_type = "counter_invocation"
        else:
            op_type = "fb_invocation"
        self._add_operation(op_type, node.name, [], "FunctionBlockCallNode", node)
        self.generic_visit(node)

    def visit_FunctionInvocationNode(self, node):
        func_name = node.name.upper()
        if func_name in ("SHL", "SHR", "ROL", "ROR", "AND", "OR", "XOR", "NOT", "BIT_LOAD_B", "BIT_OF_DWORD"):
            op_type = "bitwise_operation"
        elif func_name in ("LAMBERT_W", "SIN", "COS", "TAN", "EXP", "LN", "SQRT", "MODR", "ABS", "FLOOR", "SIGN_R"):
            op_type = "mathematical_solver"
        else:
            op_type = "function_invocation"
        sources = []
        for arg in getattr(node, "arguments", []):
            sources.extend(self._extract_sources(arg.value))
        self._add_operation(op_type, node.name, sources, "FunctionInvocationNode", node)
        self.generic_visit(node)

    def visit_ReturnNode(self, node):
        sources = []
        if node.value is not None:
            sources = self._extract_sources(node.value)
        self._add_operation("return", None, sources, "ReturnNode", node)
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add_operation(self, op_type, target, sources, ast_node_type, node=None):
        semantic_scope = "INDUSTRIAL"
        if node is not None:
            semantic_scope = self.test_detector.get_scope(node)
        self.operations.append(
            Operation(
                operation_type=op_type,
                target=target,
                sources=sources,
                ast_node_type=ast_node_type,
                metadata={"semantic_scope": semantic_scope},
            )
        )

    def _describe(self, node):
        if node is None:
            return "<none>"
        node_type = node.__class__.__name__
        if node_type == "VariableNode":
            return node.name
        if node_type == "NumberNode":
            return str(node.value)
        if node_type == "BooleanNode":
            return "TRUE" if node.value else "FALSE"
        if node_type == "TimeLiteralNode":
            return node.value
        if node_type == "TypedLiteralNode":
            return f"{node.type_name}#{node.value}"
        if node_type == "StringLiteralNode":
            return node.value
        if node_type == "BinaryExpressionNode":
            return f"{self._describe(node.left)} {node.operator} {self._describe(node.right)}"
        if node_type == "LogicalExpressionNode":
            if node.operator == "NOT":
                return f"NOT {self._describe(node.operands[0])}"
            return f" {node.operator} ".join(self._describe(o) for o in node.operands)
        if node_type == "ArrayIndexNode":
            return f"{self._describe(node.array)}[{self._describe(node.index)}]"
        if node_type == "FunctionInvocationNode":
            return f"{node.name}(...)"
        if node_type == "FunctionBlockCallNode":
            return node.name
        return f"<{node_type}>"

    def _extract_sources(self, node):
        """Recursively extract all variable names from a value node."""
        if node is None:
            return []
        node_type = node.__class__.__name__
        if node_type == "VariableNode":
            return [node.name]
        if node_type in ("NumberNode", "BooleanNode", "TimeLiteralNode", "StringLiteralNode", "TypedLiteralNode"):
            return []
        if node_type == "BinaryExpressionNode":
            left = self._extract_sources(node.left)
            right = self._extract_sources(node.right)
            return left + right
        if node_type == "LogicalExpressionNode":
            results = []
            for operand in node.operands:
                results.extend(self._extract_sources(operand))
            return results
        if node_type == "ArrayIndexNode":
            return self._extract_sources(node.array) + self._extract_sources(node.index)
        if node_type == "FunctionInvocationNode":
            results = []
            for arg in getattr(node, "arguments", []):
                results.extend(self._extract_sources(arg.value))
            return results
        if node_type == "FunctionBlockCallNode":
            results = []
            for arg in getattr(node, "arguments", []):
                results.extend(self._extract_sources(arg.value))
            return results
        return []

    def _classify_assignment(self, node):
        target = self._describe(node.target)
        value = node.value
        value_type = value.__class__.__name__ if value else None
        target_type = node.target.__class__.__name__ if node.target else None

        # Array write (target is array index)
        if target_type == "ArrayIndexNode":
            return "array_write"

        # Array read (value is array index)
        if value_type == "ArrayIndexNode":
            return "array_read"

        # Counter update
        if any(t in target for t in ("CTU", "CTD", "CTUD", "Counter", "_Cnt", "_Count", "cnt", "T1_Cnt", "T2_Cnt")):
            return "counter_update"

        # History update
        if any(t in target for t in ("last", "previous", "old", "_last", "history", "x_last", "y_last")):
            return "history_update"

        # Accumulator update
        if any(t in target for t in ("acc", "accumulator", "sum", "total", "_CRC_GEN", "crc")):
            return "accumulator_update"

        # Matrix access
        if any(t in target for t in ("Matrix", "matrix", "mat", "_M", "_A", "_B", "_C")):
            return "matrix_access"

        # State update
        if any(t in target for t in ("Step", "State", "Sequence", "_step", "ToolChangeState", "LightState", "StartupStep")):
            return "state_update"

        # Function invocation
        if value_type == "FunctionInvocationNode":
            func_name = value.name.upper() if value else ""
            # Context-aware: data_processing → bitwise_update
            if self.context and self.context.data_processing_detected:
                if func_name in ("SHL", "SHR", "ROL", "ROR", "AND", "OR", "XOR", "NOT", "BIT_LOAD_B", "BIT_OF_DWORD"):
                    return "bitwise_update"
            return "process_calculation"

        # Function block call
        if value_type == "FunctionBlockCallNode":
            return "process_calculation"

        # Binary expression
        if value_type == "BinaryExpressionNode":
            if value.operator in ("+", "-", "*", "/", "MOD"):
                # Context-aware: measurement system → measurement_calculation
                if self.context and self.context.measurement_system_detected:
                    return "measurement_calculation"
                # Context-aware: state machine → state_transition for state variables
                if self.context and self.context.state_machine_detected:
                    if any(t in target for t in ("Step", "State", "Sequence", "_step")):
                        return "state_transition"
                return "process_calculation"
            if value.operator in ("AND", "OR", "XOR", "SHL", "SHR", "ROL", "ROR"):
                # Context-aware: data_processing → bitwise_update
                if self.context and self.context.data_processing_detected:
                    return "bitwise_update"
                return "process_calculation"
            return "process_calculation"

        # Simple copy / literal
        if value_type in ("VariableNode", "NumberNode", "BooleanNode", "TimeLiteralNode", "TypedLiteralNode"):
            # Context-aware: state machine → state_transition for state variables
            if self.context and self.context.state_machine_detected:
                if any(t in target for t in ("Step", "State", "Sequence", "_step")):
                    return "state_transition"
            return "data_movement"

        return "process_calculation"

    def _extract_comparisons(self, node):
        """Extract all comparison sub-expressions from a condition node.
        Returns a list of [source_variable, ...] for each comparison."""
        if node is None:
            return []
        node_type = node.__class__.__name__

        if node_type == "BinaryExpressionNode":
            if node.operator in ("=", "<>", "<", ">", "<=", ">="):
                return [self._extract_sources(node)]
            return []

        if node_type == "LogicalExpressionNode":
            results = []
            for operand in node.operands:
                results.extend(self._extract_comparisons(operand))
            return results

        if node_type == "VariableNode":
            # Boolean guard like "IF run THEN"
            return [[node.name]]

        return []
