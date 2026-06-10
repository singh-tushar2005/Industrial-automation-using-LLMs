"""Test detector for segregating industrial and test semantics.

Detects test function blocks, test programs, test variables,
assertion logic, and verification counters. Sets semantic_scope
attribute on AST nodes: INDUSTRIAL or TEST.

Does NOT delete or suppress test nodes. Only segregates them.
"""


TEST_VARIABLE_NAMES = {
    "TestState", "testState", "totalTests", "passedTests", "failedTests",
    "TestBlock", "testBlock", "testResult", "testOutcomeArray",
    "Finished", "Failed", "Failed",
}

TEST_NAME_PREFIXES = {
    "Test", "TEST", "test", "FB_TEST", "FB_TEST",
}

TEST_FB_PREFIXES = {
    "Test", "TEST", "test", "FB_TEST",
}

TEST_PROGRAM_NAMES = {
    "TestRunnerProgram", "test_runner", "main_test", "TEST_MAIN",
}

TEST_FUNCTION_NAMES = {
    "printf", "assert", "TEST", "test",
}

TEST_ASSERTION_KEYWORDS = {
    "Failed", "Finished", "assert", "ASSERT",
}


class TestDetector:
    """Detects test-related nodes in an AST and marks their semantic_scope."""

    def __init__(self):
        self.test_nodes = set()
        self.industrial_nodes = set()
        self._node_id_counter = 0

    def detect(self, ast):
        """Run detection and set semantic_scope on all nodes.

        Returns a dict with test_nodes and industrial_nodes counts.
        """
        # First pass: identify test nodes
        self._walk(ast, in_test_context=False)
        # Second pass: mark all nodes
        self._mark_all(ast)
        return {
            "test_nodes": len(self.test_nodes),
            "industrial_nodes": len(self.industrial_nodes),
        }

    def _node_id(self, node):
        """Return a unique ID for a node object."""
        if not hasattr(node, "_test_detector_id"):
            node._test_detector_id = self._node_id_counter
            self._node_id_counter += 1
        return node._test_detector_id

    def _walk(self, node, in_test_context=False):
        if node is None or isinstance(node, (bool, int, float, str, bytes, tuple, list, dict, set)):
            return
        # Ensure node is an object with attributes
        if not hasattr(node, '__class__') or not hasattr(node, '__dict__'):
            return
        node_id = self._node_id(node)
        if node_id in self.test_nodes or node_id in self.industrial_nodes:
            return

        is_test = in_test_context or self._is_test_node(node)
        if is_test:
            self.test_nodes.add(node_id)
        else:
            self.industrial_nodes.add(node_id)

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
                    self._walk(item, in_test_context=is_test)
            else:
                self._walk(child, in_test_context=is_test)

    def _is_test_node(self, node):
        """Determine if a node is test-related."""
        node_type = node.__class__.__name__

        # Test function blocks and programs
        if node_type in ("FunctionBlockNode", "ProgramNode", "CompilationUnitNode"):
            name = getattr(node, "name", "")
            if name and any(name.startswith(p) or p in name for p in TEST_FB_PREFIXES):
                return True
            if name in TEST_PROGRAM_NAMES:
                return True

        # Test function definitions
        if node_type == "FunctionNode":
            name = getattr(node, "name", "")
            if name and any(name.startswith(p) or p in name for p in TEST_FUNCTION_NAMES):
                return True

        # Test variable declarations
        if node_type in ("VariableDeclNode", "VariableDeclarationNode"):
            name = getattr(node, "name", "")
            if name and self._is_test_name(name):
                return True

        # Assignment to test variables
        if node_type == "AssignmentNode":
            target = getattr(node, "target", None)
            if target:
                target_name = getattr(target, "name", "")
                if target_name and self._is_test_name(target_name):
                    return True

        # Function block calls to test blocks
        if node_type == "FunctionBlockCallNode":
            name = getattr(node, "name", "")
            if name and self._is_test_name(name):
                return True

        # Assertion logic: IF statements checking Failed/Finished
        if node_type == "IfStatementNode":
            condition = getattr(node, "condition", None)
            if condition:
                cond_str = self._node_str(condition)
                if cond_str and any(k in cond_str for k in TEST_ASSERTION_KEYWORDS):
                    return True

        # Printf/assert calls (C-style pragmas in test harness)
        if node_type == "CCodeNode" or node_type == "PragmaNode":
            return True

        return False

    def _is_test_name(self, name):
        """Check if a name is test-related."""
        if name in TEST_VARIABLE_NAMES:
            return True
        for prefix in TEST_NAME_PREFIXES:
            if name.startswith(prefix) or prefix in name:
                return True
        return False

    def _node_str(self, node):
        """Minimal string representation for condition checking."""
        if node is None:
            return ""
        node_type = node.__class__.__name__
        if node_type == "VariableNode":
            return getattr(node, "name", "")
        if node_type == "BinaryExpressionNode":
            return f"{self._node_str(node.left)} {node.operator} {self._node_str(node.right)}"
        if node_type == "LogicalExpressionNode":
            return f" {node.operator} ".join(self._node_str(o) for o in node.operands)
        if node_type == "FunctionInvocationNode":
            return node.name
        return ""

    def _mark_all(self, node):
        """Set semantic_scope attribute on all nodes."""
        if node is None or isinstance(node, (bool, int, float, str, bytes, tuple, list, dict, set)):
            return
        if not hasattr(node, '__class__') or not hasattr(node, '__dict__'):
            return
        node_id = self._node_id(node)
        if node_id in self.test_nodes:
            node.semantic_scope = "TEST"
        else:
            node.semantic_scope = "INDUSTRIAL"
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
                    self._mark_all(item)
            else:
                self._mark_all(child)

    def get_scope(self, node):
        """Return the semantic_scope of a node."""
        if node is None:
            return "INDUSTRIAL"
        return getattr(node, "semantic_scope", "INDUSTRIAL")


class TestSegregationReport:
    """Aggregates test and industrial metrics for semantic analysis."""

    def __init__(self):
        self.industrial = []
        self.test = []
        self.combined = []

    def add(self, item, scope):
        self.combined.append(item)
        if scope == "TEST":
            self.test.append(item)
        else:
            self.industrial.append(item)

    def get_counts(self):
        return {
            "industrial": len(self.industrial),
            "test": len(self.test),
            "combined": len(self.combined),
        }

    def get_industrial_items(self):
        return self.industrial

    def get_test_items(self):
        return self.test

    def get_combined_items(self):
        return self.combined
