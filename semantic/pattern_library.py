"""Industrial semantic pattern detectors for AST nodes.

Diagnostic-only module. Does NOT modify the semantic pipeline.
"""

try:
    from semantic.context.test_detector import TestDetector
except ModuleNotFoundError:
    from context.test_detector import TestDetector


class PatternMatch:
    """Result of a single pattern detection."""

    def __init__(self, pattern_name, confidence, matched_ast_node, extracted_evidence, semantic_scope="INDUSTRIAL"):
        self.pattern_name = pattern_name
        self.confidence = confidence
        self.matched_ast_node = matched_ast_node
        self.extracted_evidence = extracted_evidence
        self.semantic_scope = semantic_scope

    def to_dict(self):
        return {
            "pattern_name": self.pattern_name,
            "confidence": self.confidence,
            "matched_ast_node": self.matched_ast_node,
            "extracted_evidence": self.extracted_evidence,
            "semantic_scope": self.semantic_scope,
        }


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


# ------------------------------------------------------------------
# Pattern detectors
# ------------------------------------------------------------------

class StateTransitionPattern:
    PATTERN_NAME = "StateTransitionPattern"

    def detect(self, node):
        if node.__class__.__name__ != "AssignmentNode":
            return None
        target = describe_node(node.target)
        if not any(t in target for t in ("_step", "Step", "State", "Sequence", "ToolChangeState", "LightState", "StartupStep", "BatchStep")):
            return None
        value = describe_node(node.value)
        return PatternMatch(
            pattern_name=self.PATTERN_NAME,
            confidence="high",
            matched_ast_node="AssignmentNode",
            extracted_evidence={"target": target, "value": value, "kind": "state_transition"},
        )


class CounterUpdatePattern:
    PATTERN_NAME = "CounterUpdatePattern"

    def detect(self, node):
        if node.__class__.__name__ != "AssignmentNode":
            return None
        target = describe_node(node.target)
        if any(t in target for t in ("CTU", "CTD", "CTUD", "Counter", "_Cnt", "_Count", "cnt", "T1_Cnt", "T2_Cnt")):
            value = describe_node(node.value)
            return PatternMatch(
                pattern_name=self.PATTERN_NAME,
                confidence="high",
                matched_ast_node="AssignmentNode",
                extracted_evidence={"target": target, "value": value, "kind": "counter_update"},
            )
        # Also detect self-increment patterns like cnt := cnt + 1
        value = node.value
        if value and value.__class__.__name__ == "BinaryExpressionNode":
            if value.operator in ("+", "-"):
                sources = extract_sources(value)
                if target in sources:
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="medium",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "value": describe_node(value), "kind": "counter_increment"},
                    )
        return None


class HistoryUpdatePattern:
    PATTERN_NAME = "HistoryUpdatePattern"

    def detect(self, node):
        if node.__class__.__name__ != "AssignmentNode":
            return None
        target = describe_node(node.target)
        if any(t in target for t in ("last", "previous", "old", "_last", "history", "x_last", "y_last", "y_last", "tl")):
            value = describe_node(node.value)
            return PatternMatch(
                pattern_name=self.PATTERN_NAME,
                confidence="high",
                matched_ast_node="AssignmentNode",
                extracted_evidence={"target": target, "value": value, "kind": "history_update"},
            )
        return None


class AccumulatorPattern:
    PATTERN_NAME = "AccumulatorPattern"

    def detect(self, node):
        if node.__class__.__name__ != "AssignmentNode":
            return None
        target = describe_node(node.target)
        value = node.value
        if value and value.__class__.__name__ == "BinaryExpressionNode":
            if value.operator in ("XOR", "OR", "AND"):
                sources = extract_sources(value)
                if target in sources:
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="high",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "value": describe_node(value), "kind": "accumulator_bitwise"},
                    )
            if value.operator in ("+", "-", "*", "/"):
                sources = extract_sources(value)
                if target in sources:
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="medium",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "value": describe_node(value), "kind": "accumulator_arithmetic"},
                    )
        return None


class ArrayAccessPattern:
    PATTERN_NAME = "ArrayAccessPattern"

    def detect(self, node):
        if node.__class__.__name__ == "AssignmentNode":
            target = describe_node(node.target)
            value = node.value
            if value and value.__class__.__name__ == "ArrayIndexNode":
                return PatternMatch(
                    pattern_name=self.PATTERN_NAME,
                    confidence="high",
                    matched_ast_node="AssignmentNode",
                    extracted_evidence={"target": target, "value": describe_node(value), "kind": "array_read"},
                )
            if node.target and node.target.__class__.__name__ == "ArrayIndexNode":
                return PatternMatch(
                    pattern_name=self.PATTERN_NAME,
                    confidence="high",
                    matched_ast_node="AssignmentNode",
                    extracted_evidence={"target": target, "value": describe_node(value), "kind": "array_write"},
                )
        return None


class MatrixAccessPattern:
    PATTERN_NAME = "MatrixAccessPattern"

    def detect(self, node):
        if node.__class__.__name__ == "AssignmentNode":
            target = describe_node(node.target)
            value = node.value
            if value and value.__class__.__name__ == "FunctionInvocationNode":
                func_name = value.name.upper()
                if func_name in ("MATRIX_MUL", "MATRIX_ADD", "MATRIX_INV", "MATRIX_TRANSPOSE"):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="high",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "function": func_name, "kind": "matrix_operation"},
                    )
            if any(t in target for t in ("Matrix", "matrix", "mat", "_M", "_A", "_B", "_C", "Result")):
                value_desc = describe_node(value)
                if "[" in value_desc or any(t in value_desc for t in ("mat", "Matrix", "M", "A", "B", "C")):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="medium",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "value": value_desc, "kind": "matrix_access"},
                    )
        return None


class BitwiseUpdatePattern:
    PATTERN_NAME = "BitwiseUpdatePattern"

    def detect(self, node):
        if node.__class__.__name__ == "AssignmentNode":
            value = node.value
            if value and value.__class__.__name__ == "FunctionInvocationNode":
                func_name = value.name.upper()
                if func_name in ("SHL", "SHR", "ROL", "ROR", "AND", "OR", "XOR", "NOT", "BIT_LOAD_B", "BIT_OF_DWORD"):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="high",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": describe_node(node.target), "function": func_name, "kind": "bitwise_function"},
                    )
            if value and value.__class__.__name__ == "BinaryExpressionNode":
                if value.operator in ("AND", "OR", "XOR"):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="high",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": describe_node(node.target), "value": describe_node(value), "kind": "bitwise_expression"},
                    )
        return None


class RateCalculationPattern:
    PATTERN_NAME = "RateCalculationPattern"

    def detect(self, node):
        if node.__class__.__name__ != "AssignmentNode":
            return None
        target = describe_node(node.target)
        value = node.value
        if value and value.__class__.__name__ == "BinaryExpressionNode":
            if value.operator == "/":
                sources = extract_sources(value)
                if any(t in target for t in ("Flow", "flow", "Rate", "rate", "Speed", "speed", "Freq", "freq")):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="high",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "sources": sources, "kind": "rate_calculation"},
                    )
                if any(s in str(sources) for s in ("delta", "time", "dt", "period", "pulse", "count")):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="medium",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": target, "sources": sources, "kind": "rate_calculation"},
                    )
        return None


class ProcessCalculationPattern:
    PATTERN_NAME = "ProcessCalculationPattern"

    def detect(self, node):
        if node.__class__.__name__ == "AssignmentNode":
            value = node.value
            if value and value.__class__.__name__ == "FunctionInvocationNode":
                func_name = value.name.upper()
                if func_name in ("SQRT", "ABS", "EXP", "LN", "SIN", "COS", "TAN", "MODR", "FLOOR", "SIGN_R", "LAMBERT_W"):
                    return PatternMatch(
                        pattern_name=self.PATTERN_NAME,
                        confidence="high",
                        matched_ast_node="AssignmentNode",
                        extracted_evidence={"target": describe_node(node.target), "function": func_name, "kind": "math_calculation"},
                    )
            if value and value.__class__.__name__ == "BinaryExpressionNode":
                if value.operator in ("+", "-", "*", "/", "MOD"):
                    target = describe_node(node.target)
                    if any(t in target for t in ("PID", "FT_", "Control", "Output", "Process")):
                        return PatternMatch(
                            pattern_name=self.PATTERN_NAME,
                            confidence="medium",
                            matched_ast_node="AssignmentNode",
                            extracted_evidence={"target": target, "value": describe_node(value), "kind": "process_calculation"},
                        )
        return None


class FunctionBlockInvocationPattern:
    PATTERN_NAME = "FunctionBlockInvocationPattern"

    def detect(self, node):
        if node.__class__.__name__ == "FunctionBlockCallNode":
            fb_name = node.name
            fb_upper = fb_name.upper()
            kind = "fb_invocation"
            if fb_upper.startswith(("TON", "TOF", "TP")) or "TIMER" in fb_upper:
                kind = "timer_invocation"
            elif fb_upper.startswith(("CTU", "CTD", "CTUD")) or "COUNTER" in fb_upper:
                kind = "counter_invocation"
            elif fb_upper.startswith(("PID", "FT_")):
                kind = "pid_invocation"
            return PatternMatch(
                pattern_name=self.PATTERN_NAME,
                confidence="high",
                matched_ast_node="FunctionBlockCallNode",
                extracted_evidence={"fb_name": fb_name, "kind": kind},
            )
        return None


# ------------------------------------------------------------------
# Pattern Library
# ------------------------------------------------------------------

class PatternLibrary:
    """Collection of all industrial semantic patterns."""

    def __init__(self):
        self.patterns = [
            StateTransitionPattern(),
            CounterUpdatePattern(),
            HistoryUpdatePattern(),
            AccumulatorPattern(),
            ArrayAccessPattern(),
            MatrixAccessPattern(),
            BitwiseUpdatePattern(),
            RateCalculationPattern(),
            ProcessCalculationPattern(),
            FunctionBlockInvocationPattern(),
        ]
        self.test_detector = TestDetector()

    def detect(self, ast):
        """Run all patterns on the AST and return a list of PatternMatch objects."""
        self.test_detector.detect(ast)
        matches = []
        self._walk(ast, matches)
        return matches

    def _walk(self, node, matches):
        if node is None:
            return
        for pattern in self.patterns:
            match = pattern.detect(node)
            if match:
                match.semantic_scope = self.test_detector.get_scope(node)
                matches.append(match)
        for attr in ("body", "then_body", "else_body", "statements", "branches",
                     "elsif_branches", "operands", "left", "right", "arguments",
                     "value", "target", "condition", "start_expr", "end_expr", "step_expr",
                     "var_blocks", "declarations"):
            child = getattr(node, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    self._walk(item, matches)
            else:
                self._walk(child, matches)
