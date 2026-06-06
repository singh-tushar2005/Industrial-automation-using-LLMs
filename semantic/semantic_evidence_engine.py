"""Semantic evidence engine.

Walks the AST once and collects evidence for all semantic layers.
Does NOT classify, emit relationships, or emit operations.
Only collects evidence.
"""

from collections import defaultdict

try:
    from semantic.semantic_evidence import SemanticEvidence, EvidenceItem
    from semantic.context.test_detector import TestDetector
except ModuleNotFoundError:
    from semantic_evidence import SemanticEvidence, EvidenceItem
    from context.test_detector import TestDetector


def describe_node(node):
    """Minimal description of an AST node."""
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
    if node_type == "BinaryExpressionNode":
        return f"{describe_node(node.left)} {node.operator} {describe_node(node.right)}"
    if node_type == "LogicalExpressionNode":
        if node.operator == "NOT":
            return f"NOT {describe_node(node.operands[0])}"
        return f" {node.operator} ".join(describe_node(o) for o in node.operands)
    if node_type == "ArrayIndexNode":
        return f"{describe_node(node.array)}[{describe_node(node.index)}]"
    if node_type == "FunctionInvocationNode":
        return f"{node.name}(...)"
    if node_type == "FunctionBlockCallNode":
        return node.name
    return f"<{node_type}>"


def extract_sources(node):
    """Recursively extract variable names from a node."""
    if node is None:
        return []
    node_type = node.__class__.__name__
    if node_type == "VariableNode":
        return [node.name]
    if node_type in ("NumberNode", "BooleanNode", "TimeLiteralNode", "StringLiteralNode", "TypedLiteralNode"):
        return []
    if node_type == "BinaryExpressionNode":
        return extract_sources(node.left) + extract_sources(node.right)
    if node_type == "LogicalExpressionNode":
        results = []
        for operand in node.operands:
            results.extend(extract_sources(operand))
        return results
    if node_type == "ArrayIndexNode":
        return extract_sources(node.array) + extract_sources(node.index)
    if node_type == "FunctionInvocationNode":
        results = []
        for arg in getattr(node, "arguments", []):
            results.extend(extract_sources(arg.value))
        return results
    if node_type == "FunctionBlockCallNode":
        results = []
        for arg in getattr(node, "arguments", []):
            results.extend(extract_sources(arg.value))
        return results
    return []


class SemanticEvidenceEngine:
    """Single-pass AST walker that collects all semantic evidence."""

    def __init__(self):
        self.evidence = SemanticEvidence()
        self.test_detector = TestDetector()

    def collect(self, ast):
        """Run evidence collection and return SemanticEvidence."""
        self.test_detector.detect(ast)
        self._walk(ast)
        return self.evidence

    def _scope(self, node):
        """Return semantic scope for a node."""
        if node is None:
            return "INDUSTRIAL"
        return getattr(node, "semantic_scope", "INDUSTRIAL")

    def _walk(self, node):
        if node is None or isinstance(node, (bool, int, float, str, bytes, tuple, list, dict, set)):
            return
        if not hasattr(node, '__class__') or not hasattr(node, '__dict__'):
            return

        node_type = node.__class__.__name__
        scope = self._scope(node)

        # AssignmentNode evidence
        if node_type == "AssignmentNode":
            self._collect_assignment(node, scope)

        # FunctionBlockCallNode evidence
        if node_type == "FunctionBlockCallNode":
            self._collect_fb_call(node, scope)

        # FunctionInvocationNode evidence
        if node_type == "FunctionInvocationNode":
            self._collect_function_invocation(node, scope)

        # IfStatementNode evidence
        if node_type == "IfStatementNode":
            self._collect_if_statement(node, scope)

        # ArrayIndexNode evidence
        if node_type == "ArrayIndexNode":
            self._collect_array_index(node, scope)

        # VariableDeclNode evidence
        if node_type == "VariableDeclNode":
            self._collect_variable_decl(node, scope)

        # Continue walking children
        for attr in (
            "body", "then_body", "else_body", "statements", "branches",
            "elsif_branches", "operands", "left", "right", "arguments",
            "value", "target", "condition", "start_expr", "end_expr", "step_expr",
            "var_blocks", "declarations", "variables",
        ):
            child = getattr(node, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    self._walk(item)
            else:
                self._walk(child)

    def _collect_assignment(self, node, scope):
        target = describe_node(node.target)
        target_type = node.target.__class__.__name__ if node.target else None
        value = node.value
        value_type = value.__class__.__name__ if value else None

        # State transition
        if any(t in target for t in ("_step", "Step", "State", "Sequence", "ToolChangeState", "LightState", "StartupStep")):
            self.evidence.add("state_transition", "high", node,
                {"target": target, "value": describe_node(value)}, {"semantic_scope": scope})

        # Counter update
        if any(t in target for t in ("CTU", "CTD", "CTUD", "Counter", "_Cnt", "_Count", "cnt", "T1_Cnt", "T2_Cnt")):
            self.evidence.add("counter", "high", node,
                {"target": target, "value": describe_node(value)}, {"semantic_scope": scope})

        # History update
        if any(t in target for t in ("last", "previous", "old", "_last", "history", "x_last", "y_last")):
            self.evidence.add("history_variable", "high", node,
                {"target": target, "value": describe_node(value)}, {"semantic_scope": scope})

        # Accumulator update
        if value_type == "BinaryExpressionNode":
            if value.operator in ("XOR", "OR", "AND"):
                sources = extract_sources(value)
                if target in sources:
                    self.evidence.add("accumulator", "high", node,
                        {"target": target, "operator": value.operator}, {"semantic_scope": scope})
            elif value.operator in ("+", "-", "*", "/"):
                sources = extract_sources(value)
                if target in sources:
                    self.evidence.add("accumulator", "medium", node,
                        {"target": target, "operator": value.operator}, {"semantic_scope": scope})

        # Array access
        if value_type == "ArrayIndexNode" or target_type == "ArrayIndexNode":
            kind = "array_read" if value_type == "ArrayIndexNode" else "array_write"
            self.evidence.add("array_access", "high", node,
                {"target": target, "value": describe_node(value), "kind": kind}, {"semantic_scope": scope})

        # Bitwise update
        if value_type == "FunctionInvocationNode":
            func_name = value.name.upper()
            if func_name in ("SHL", "SHR", "ROL", "ROR", "AND", "OR", "XOR", "NOT", "BIT_LOAD_B", "BIT_OF_DWORD"):
                self.evidence.add("bitwise_operation", "high", node,
                    {"target": target, "function": func_name}, {"semantic_scope": scope})
        if value_type == "BinaryExpressionNode" and value.operator in ("AND", "OR", "XOR"):
            self.evidence.add("bitwise_operation", "high", node,
                {"target": target, "operator": value.operator}, {"semantic_scope": scope})

        # Process calculation
        if value_type == "FunctionInvocationNode":
            func_name = value.name.upper()
            if func_name in ("SQRT", "ABS", "EXP", "LN", "SIN", "COS", "TAN", "MODR", "FLOOR", "SIGN_R", "LAMBERT_W"):
                self.evidence.add("process_calculation", "high", node,
                    {"target": target, "function": func_name}, {"semantic_scope": scope})

        # Measurement calculation
        if value_type == "BinaryExpressionNode" and value.operator == "/":
            if any(t in target for t in ("Flow", "flow", "Rate", "rate", "Speed", "speed", "Freq", "freq")):
                self.evidence.add("measurement_calculation", "high", node,
                    {"target": target}, {"semantic_scope": scope})

        # Matrix access
        if value_type == "FunctionInvocationNode":
            func_name = value.name.upper()
            if func_name in ("MATRIX_MUL", "MATRIX_ADD", "MATRIX_INV", "MATRIX_TRANSPOSE"):
                self.evidence.add("matrix_access", "high", node,
                    {"target": target, "function": func_name}, {"semantic_scope": scope})
        if any(t in target for t in ("Matrix", "matrix", "mat", "_M", "_A", "_B", "_C", "Result")):
            if value_type == "ArrayIndexNode" or "[" in describe_node(value):
                self.evidence.add("matrix_access", "medium", node,
                    {"target": target, "value": describe_node(value)}, {"semantic_scope": scope})

    def _collect_fb_call(self, node, scope):
        fb_name = node.name.upper()
        if fb_name.startswith(("TON", "TOF", "TP")) or "TIMER" in fb_name:
            self.evidence.add("timer", "high", node,
                {"fb_name": node.name, "kind": "timer_invocation"}, {"semantic_scope": scope})
        elif fb_name.startswith(("CTU", "CTD", "CTUD")) or "COUNTER" in fb_name:
            self.evidence.add("counter", "high", node,
                {"fb_name": node.name, "kind": "counter_invocation"}, {"semantic_scope": scope})
        else:
            self.evidence.add("fb_invocation", "high", node,
                {"fb_name": node.name, "kind": "fb_invocation"}, {"semantic_scope": scope})

    def _collect_function_invocation(self, node, scope):
        func_name = node.name.upper()
        if func_name in ("SHL", "SHR", "ROL", "ROR", "AND", "OR", "XOR", "NOT", "BIT_LOAD_B", "BIT_OF_DWORD"):
            self.evidence.add("bitwise_operation", "high", node,
                {"function": func_name}, {"semantic_scope": scope})
        elif func_name in ("SQRT", "ABS", "EXP", "LN", "SIN", "COS", "TAN", "MODR", "FLOOR", "SIGN_R", "LAMBERT_W"):
            self.evidence.add("process_calculation", "high", node,
                {"function": func_name}, {"semantic_scope": scope})

    def _collect_if_statement(self, node, scope):
        # Detect comparison operations
        cond = node.condition
        if cond and cond.__class__.__name__ == "BinaryExpressionNode":
            if cond.operator in ("=", "<>", "<", ">", "<=", ">="):
                sources = extract_sources(cond)
                self.evidence.add("comparison", "medium", node,
                    {"sources": sources, "operator": cond.operator}, {"semantic_scope": scope})

    def _collect_array_index(self, node, scope):
        # ArrayIndexNode as standalone expression
        self.evidence.add("array_access", "high", node,
            {"array": describe_node(node.array), "index": describe_node(node.index)}, {"semantic_scope": scope})

    def _collect_variable_decl(self, node, scope):
        name = getattr(node, "name", "")
        # Detect state variables by declaration
        if any(t in name for t in ("_step", "Step", "State", "Sequence", "ToolChangeState", "LightState", "StartupStep")):
            self.evidence.add("state_variable", "medium", node, {"variable": name}, {"semantic_scope": scope})
        if any(t in name for t in ("CTU", "CTD", "CTUD", "Counter", "_Cnt", "_Count", "cnt", "T1_Cnt", "T2_Cnt")):
            self.evidence.add("counter", "medium", node, {"variable": name}, {"semantic_scope": scope})
        if any(t in name for t in ("last", "previous", "old", "_last", "history", "x_last", "y_last")):
            self.evidence.add("history_variable", "medium", node, {"variable": name}, {"semantic_scope": scope})
        if any(t in name for t in ("Timer", "timer", "TON", "TOF", "TP")):
            self.evidence.add("timer", "medium", node, {"variable": name}, {"semantic_scope": scope})
