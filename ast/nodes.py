class VariableNode:
    """Represents the name of a variable, such as StartButton or Motor."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VariableNode(name={self.name!r})"


class BooleanNode:
    """Represents a boolean value: TRUE or FALSE in Structured Text."""

    def __init__(self, value):
        self.value = bool(value)

    def __repr__(self):
        return f"BooleanNode(value={self.value!r})"


class NumberNode:
    """Represents a numeric literal, such as 100, 1, or 12.5."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode(value={self.value!r})"


class TimeLiteralNode:
    """Represents an IEC time literal such as T#5s or T#250ms."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"TimeLiteralNode(value={self.value!r})"


class BinaryExpressionNode:
    """Represents two expressions joined by an operator."""

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return (
            "BinaryExpressionNode("
            f"left={self.left!r}, "
            f"operator={self.operator!r}, "
            f"right={self.right!r}"
            ")"
        )


class LogicalExpressionNode:
    """Represents logical expressions such as A AND B, A OR B, or NOT A."""

    def __init__(self, operator, operands):
        self.operator = operator
        self.operands = operands

    def __repr__(self):
        return (
            "LogicalExpressionNode("
            f"operator={self.operator!r}, "
            f"operands={self.operands!r}"
            ")"
        )


class AssignmentNode:
    """Represents assigning a value to a variable, such as Motor := TRUE."""

    def __init__(self, target, value):
        self.target = target
        self.value = value

    def __repr__(self):
        return f"AssignmentNode(target={self.target!r}, value={self.value!r})"


class FunctionBlockCallNode:
    """Represents a function block invocation with named arguments."""

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return (
            "FunctionBlockCallNode("
            f"name={self.name!r}, "
            f"arguments={self.arguments!r}"
            ")"
        )


class BlockNode:
    """Represents an ordered list of statements inside a block."""

    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"BlockNode(statements={self.statements!r})"


class IfStatementNode:
    """Represents an IF statement with a condition and a THEN body."""

    def __init__(self, condition, then_body):
        self.condition = condition
        self.then_body = then_body

    def __repr__(self):
        return (
            "IfStatementNode("
            f"condition={self.condition!r}, "
            f"then_body={self.then_body!r}"
            ")"
        )


class CaseBranchNode:
    """Represents one CASE branch and its statement body."""

    def __init__(self, match_value, body):
        self.match_value = match_value
        self.body = body

    def __repr__(self):
        return (
            "CaseBranchNode("
            f"match_value={self.match_value!r}, "
            f"body={self.body!r}"
            ")"
        )


class CaseStatementNode:
    """Represents a CASE statement with optional ELSE body."""

    def __init__(self, selector, branches, else_body=None):
        self.selector = selector
        self.branches = branches
        self.else_body = else_body

    def __repr__(self):
        return (
            "CaseStatementNode("
            f"selector={self.selector!r}, "
            f"branches={self.branches!r}, "
            f"else_body={self.else_body!r}"
            ")"
        )


class ProgramNode:
    """Represents a complete parsed Structured Text program."""

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return f"ProgramNode(body={self.body!r})"
