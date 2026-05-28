"""Semantic AST visitors that return traversal data."""

class ASTVisitor:
    """Base visitor with generic class-name dispatch."""

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


class SemanticTraversalVisitor(ASTVisitor):
    """Visitor that recursively records the structure and meaning of an AST."""

    def __init__(self):
        self.depth = 0
        self.traversal = []

    def record_line(self, message):
        """Record one traversal event without printing it."""

        self.traversal.append(
            {
                "depth": self.depth,
                "message": message,
            }
        )

    def traverse(self, ast):
        """Visit an AST and return collected traversal data."""

        self.visit(ast)
        return self.get_results()

    def get_results(self):
        """Return a copy of the traversal data collected so far."""

        return list(self.traversal)

    def visit_child(self, label, child_node):
        """Record a label, then recursively visit one child node."""

        self.record_line(label)
        self.depth += 1
        self.visit(child_node)
        self.depth -= 1

    def visit_children(self, label, child_nodes):
        """Record a label, then recursively visit a list of child nodes."""

        self.record_line(label)
        self.depth += 1

        for index, child_node in enumerate(child_nodes, start=1):
            self.record_line(f"Statement {index}")
            self.depth += 1
            self.visit(child_node)
            self.depth -= 1

        self.depth -= 1

    def visit_ProgramNode(self, node):
        """Visit a complete Structured Text program."""

        self.record_line("ProgramNode: start of Structured Text program")
        self.depth += 1
        self.visit(node.body)
        self.depth -= 1
        self.record_line("ProgramNode: end of program")

    def visit_BlockNode(self, node):
        """Visit an ordered block of statements."""

        statement_count = len(node.statements)
        self.record_line(f"BlockNode: {statement_count} statement(s)")
        self.visit_children("Block contents:", node.statements)

    def visit_IfStatementNode(self, node):
        """Visit an IF statement and recursively traverse its condition/body."""

        self.record_line("IfStatementNode: conditional execution")
        self.depth += 1
        self.visit_child("Condition:", node.condition)
        self.visit_child("THEN body:", node.then_body)
        self.depth -= 1

    def visit_AssignmentNode(self, node):
        """Visit an assignment target and assigned value."""

        self.record_line("AssignmentNode: write value into variable")
        self.depth += 1
        self.visit_child("Target variable:", node.target)
        self.visit_child("Assigned expression:", node.value)
        self.depth -= 1

    def visit_BinaryExpressionNode(self, node):
        """Visit arithmetic and comparison expressions with left/right sides."""

        self.record_line(f"BinaryExpressionNode: operator {node.operator!r}")
        self.depth += 1
        self.visit_child("Left expression:", node.left)
        self.visit_child("Right expression:", node.right)
        self.depth -= 1

    def visit_LogicalExpressionNode(self, node):
        """Visit logical expressions such as AND, OR, and NOT."""

        operand_count = len(node.operands)
        self.record_line(
            f"LogicalExpressionNode: operator {node.operator!r} "
            f"with {operand_count} operand(s)"
        )
        self.depth += 1

        for index, operand in enumerate(node.operands, start=1):
            self.visit_child(f"Operand {index}:", operand)

        self.depth -= 1

    def visit_VariableNode(self, node):
        """Visit a variable reference."""

        self.record_line(f"VariableNode: variable name {node.name!r}")

    def visit_BooleanNode(self, node):
        """Visit a TRUE/FALSE literal."""

        self.record_line(f"BooleanNode: boolean value {node.value!r}")

    def visit_NumberNode(self, node):
        """Visit a numeric literal."""

        self.record_line(f"NumberNode: numeric value {node.value!r}")

    def visit_TimeLiteralNode(self, node):
        """Visit an IEC time literal."""

        self.record_line(f"TimeLiteralNode: time value {node.value!r}")

    def visit_FunctionBlockCallNode(self, node):
        """Visit a function block invocation and its named arguments."""

        self.record_line(f"FunctionBlockCallNode: call {node.name!r}")
        self.depth += 1

        for argument_name, argument_value in node.arguments:
            self.visit_child(f"Argument {argument_name}:", argument_value)

        self.depth -= 1

    def visit_CaseStatementNode(self, node):
        """Visit a CASE statement and all of its branches."""

        self.record_line("CaseStatementNode: state or mode selection")
        self.depth += 1
        self.visit_child("Selector:", node.selector)
        self.record_line("Branches:")
        self.depth += 1

        for index, branch in enumerate(node.branches, start=1):
            self.record_line(f"Branch {index}")
            self.depth += 1
            self.visit(branch)
            self.depth -= 1

        self.depth -= 1

        if node.else_body is not None:
            self.visit_child("ELSE body:", node.else_body)

        self.depth -= 1

    def visit_CaseBranchNode(self, node):
        """Visit one CASE branch."""

        self.visit_child("Match value:", node.match_value)
        self.visit_child("Branch body:", node.body)

    def visit_CompilationUnitNode(self, node):
        """Visit a PROGRAM, FUNCTION, or FUNCTION_BLOCK compilation unit."""

        self.record_line(
            f"CompilationUnitNode: {node.kind} {node.name!r}"
        )
        self.depth += 1

        if node.return_type:
            self.record_line(f"Return type: {node.return_type!r}")

        for var_block in node.var_blocks:
            self.visit(var_block)

        self.visit_child("Body:", node.body)
        self.depth -= 1

    def visit_VarBlockNode(self, node):
        """Visit a VAR / VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT block."""

        self.record_line(f"VarBlockNode: {node.kind} ({len(node.declarations)} declaration(s))")
        self.depth += 1

        for declaration in node.declarations:
            self.visit(declaration)

        self.depth -= 1

    def visit_VariableDeclarationNode(self, node):
        """Visit one variable declaration."""

        default_info = f" := {node.default_value!r}" if node.default_value is not None else ""
        self.record_line(
            f"VariableDeclarationNode: {', '.join(node.names)} : {node.var_type}{default_info}"
        )


# Backward-compatible name for older code that imported PrintingSemanticVisitor.
# The class no longer prints; it records traversal events for main.py to present.
PrintingSemanticVisitor = SemanticTraversalVisitor
