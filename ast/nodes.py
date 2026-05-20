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
        # IEC 61131-3 has many numeric types. For this teaching parser, we keep
        # it simple: whole numbers become int, decimal numbers become float.
        self.value = value

    def __repr__(self):
        return f"NumberNode(value={self.value!r})"


class BinaryExpressionNode:
    """Represents two expressions joined by an operator.

    Examples:
        Counter + 1
        Temp > 100
        Counter + 1 > Limit

    The left and right sides can be simple values or more expression nodes.
    That recursive shape is what lets the AST represent large expressions.
    """

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


class ProgramNode:
    """Represents a complete parsed Structured Text program."""

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return f"ProgramNode(body={self.body!r})"


# Example Structured Text:
#
# IF StartButton THEN
#     Motor := TRUE;
# END_IF;
#
# The same logic represented as beginner-friendly AST nodes:
example_ast = IfStatementNode(
    condition=VariableNode("StartButton"),
    then_body=BlockNode(
        [
            AssignmentNode(
                target=VariableNode("Motor"),
                value=BooleanNode(True),
            )
        ]
    ),
)


if __name__ == "__main__":
    print(example_ast)
