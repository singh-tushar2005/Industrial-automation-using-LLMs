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

        if node.elsif_branches:
            for index, (elsif_condition, elsif_body) in enumerate(node.elsif_branches, start=1):
                self.record_line(f"ELSIF {index}:")
                self.depth += 1
                self.visit_child("Condition:", elsif_condition)
                self.visit_child("Body:", elsif_body)
                self.depth -= 1

        if node.else_body is not None:
            self.visit_child("ELSE body:", node.else_body)

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

    def visit_StringLiteralNode(self, node):
        """Visit a string literal."""

        self.record_line(f"StringLiteralNode: string value {node.value!r}")

    def visit_FunctionBlockCallNode(self, node):
        """Visit a function block invocation and its named arguments."""

        self.record_line(f"FunctionBlockCallNode: call {node.name!r}")
        self.depth += 1

        for argument in node.arguments:
            if hasattr(argument, 'name') and hasattr(argument, 'value'):
                label = f"Argument {argument.name}:" if argument.name else "Positional argument:"
                self.visit_child(label, argument.value)
            else:
                # backward compatibility for tuple-based arguments
                argument_name, argument_value = argument
                self.visit_child(f"Argument {argument_name}:", argument_value)

        self.depth -= 1

    def visit_FunctionBlockInvocationNode(self, node):
        """Visit a function block invocation in expression context."""

        self.record_line(f"FunctionBlockInvocationNode: call {node.name!r}")
        self.depth += 1

        for argument in node.arguments:
            if hasattr(argument, 'name') and hasattr(argument, 'value'):
                label = f"Argument {argument.name}:" if argument.name else "Positional argument:"
                self.visit_child(label, argument.value)
            else:
                # backward compatibility for tuple-based arguments
                argument_name, argument_value = argument
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
        at_info = f" AT {node.at_mapping.address}" if node.at_mapping is not None else ""
        var_type_str = node.var_type if isinstance(node.var_type, str) else repr(node.var_type)
        self.record_line(
            f"VariableDeclarationNode: {', '.join(node.names)} : {var_type_str}{default_info}{at_info}"
        )

    def visit_ForLoopNode(self, node):
        """Visit a FOR loop."""

        self.record_line(f"ForLoopNode: loop variable {node.variable!r}")
        self.depth += 1
        self.visit_child("Start:", node.start_expr)
        self.visit_child("End:", node.end_expr)
        if node.step_expr is not None:
            self.visit_child("Step:", node.step_expr)
        self.visit_child("Body:", node.body)
        self.depth -= 1

    def visit_WhileLoopNode(self, node):
        """Visit a WHILE loop."""

        self.record_line("WhileLoopNode: conditional loop")
        self.depth += 1
        self.visit_child("Condition:", node.condition)
        self.visit_child("Body:", node.body)
        self.depth -= 1

    def visit_RepeatLoopNode(self, node):
        """Visit a REPEAT loop."""

        self.record_line("RepeatLoopNode: post-condition loop")
        self.depth += 1
        self.visit_child("Body:", node.body)
        self.visit_child("Condition:", node.condition)
        self.depth -= 1

    def visit_ExitNode(self, node):
        """Visit an EXIT statement."""

        self.record_line("ExitNode: loop exit")

    def visit_ReturnNode(self, node):
        """Visit a RETURN statement."""

        if node.value is not None:
            self.record_line("ReturnNode: return with value")
            self.depth += 1
            self.visit_child("Value:", node.value)
            self.depth -= 1
        else:
            self.record_line("ReturnNode: return")

    def visit_FunctionInvocationNode(self, node):
        """Visit a function invocation in expression context."""

        self.record_line(f"FunctionInvocationNode: call {node.name!r}")
        self.depth += 1

        for argument in node.arguments:
            self.visit_child(f"Argument {argument.name}:", argument.value)

        self.depth -= 1

    def visit_InvocationArgumentNode(self, node):
        """Visit one invocation argument."""

        label = f"Argument {node.name}:" if node.name else "Positional argument:"
        self.visit_child(label, node.value)

    def visit_TypedLiteralNode(self, node):
        """Visit an IEC typed literal."""

        self.record_line(f"TypedLiteralNode: {node.type_name}#{node.value}")

    def visit_ArrayIndexNode(self, node):
        """Visit an array index expression."""

        self.record_line("ArrayIndexNode: array indexing")
        self.depth += 1
        self.visit_child("Array:", node.array)
        self.visit_child("Index:", node.index)
        self.depth -= 1

    def visit_ArrayTypeNode(self, node):
        """Visit an array type declaration."""

        self.record_line(f"ArrayTypeNode: ARRAY [{node.bounds}] OF {node.element_type}")

    def visit_MemoryMappingNode(self, node):
        """Visit an IEC memory mapping address."""

        self.record_line(f"MemoryMappingNode: {node.address}")

    def visit_TaskNode(self, node):
        """Visit a TASK declaration."""

        self.record_line(f"TaskNode: {node.name!r}")
        self.depth += 1

        for argument in node.arguments:
            if hasattr(argument, 'name') and hasattr(argument, 'value'):
                label = f"Argument {argument.name}:" if argument.name else "Positional argument:"
                self.visit_child(label, argument.value)
            else:
                argument_name, argument_value = argument
                self.visit_child(f"Argument {argument_name}:", argument_value)

        self.depth -= 1

    def visit_ProgramBindingNode(self, node):
        """Visit a PROGRAM binding declaration."""

        self.record_line(
            f"ProgramBindingNode: {node.instance_name!r} -> {node.program_type!r}"
        )
        self.depth += 1

        if node.task_name:
            self.record_line(f"Task: {node.task_name!r}")

        self.depth -= 1

    def visit_ResourceNode(self, node):
        """Visit a RESOURCE declaration."""

        self.record_line(f"ResourceNode: {node.name!r} ON {node.on!r}")
        self.depth += 1
        self.visit(node.body)
        self.depth -= 1

    def visit_ConfigurationNode(self, node):
        """Visit a CONFIGURATION declaration."""

        self.record_line(f"ConfigurationNode: {node.name!r}")
        self.depth += 1
        self.visit(node.body)
        self.depth -= 1


# Backward-compatible name for older code that imported PrintingSemanticVisitor.
# The class no longer prints; it records traversal events for main.py to present.
PrintingSemanticVisitor = SemanticTraversalVisitor
