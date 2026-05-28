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


class StringLiteralNode:
    """Represents a string literal such as 'hello' or ''."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringLiteralNode(value={self.value!r})"


class TypedLiteralNode:
    """Represents an IEC typed literal such as BYTE#0 or DWORD#16#8000_0000."""

    def __init__(self, type_name, value):
        self.type_name = type_name
        self.value = value

    def __repr__(self):
        return f"TypedLiteralNode(type_name={self.type_name!r}, value={self.value!r})"


class ArrayIndexNode:
    """Represents array indexing such as PT[pos] or hexDigits[digitValue]."""

    def __init__(self, array, index):
        self.array = array
        self.index = index

    def __repr__(self):
        return f"ArrayIndexNode(array={self.array!r}, index={self.index!r})"


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


class InvocationArgumentNode:
    """Represents one named argument in a function block or function invocation."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"InvocationArgumentNode(name={self.name!r}, value={self.value!r})"


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


class FunctionBlockInvocationNode:
    """Represents a function block invocation used in an expression context."""

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return (
            "FunctionBlockInvocationNode("
            f"name={self.name!r}, "
            f"arguments={self.arguments!r}"
            ")"
        )


class FunctionInvocationNode:
    """Represents a function invocation in an expression context such as SHL(x, 1)."""

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return (
            "FunctionInvocationNode("
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
    """Represents an IF statement with optional ELSIF branches and ELSE body."""

    def __init__(self, condition, then_body, elsif_branches=None, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.elsif_branches = elsif_branches or []
        self.else_body = else_body

    def __repr__(self):
        return (
            "IfStatementNode("
            f"condition={self.condition!r}, "
            f"then_body={self.then_body!r}, "
            f"elsif_branches={self.elsif_branches!r}, "
            f"else_body={self.else_body!r}"
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


class CompilationUnitNode:
    """Top-level IEC 61131-3 compilation unit: PROGRAM, FUNCTION, or FUNCTION_BLOCK."""

    def __init__(self, kind, name, body, var_blocks=None, return_type=None):
        self.kind = kind
        self.name = name
        self.body = body
        self.var_blocks = var_blocks or []
        self.return_type = return_type

    def __repr__(self):
        return (
            f"CompilationUnitNode("
            f"kind={self.kind!r}, "
            f"name={self.name!r}, "
            f"return_type={self.return_type!r}, "
            f"var_blocks={self.var_blocks!r}, "
            f"body={self.body!r}"
            f")"
        )


class VarBlockNode:
    """Variable declaration block: VAR, VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT."""

    def __init__(self, kind, declarations):
        self.kind = kind
        self.declarations = declarations

    def __repr__(self):
        return (
            f"VarBlockNode("
            f"kind={self.kind!r}, "
            f"declarations={self.declarations!r}"
            f")"
        )


class ForLoopNode:
    """Represents a FOR loop: FOR i := 1 TO N BY 2 DO ... END_FOR."""

    def __init__(self, variable, start_expr, end_expr, step_expr, body):
        self.variable = variable
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.step_expr = step_expr
        self.body = body

    def __repr__(self):
        return (
            f"ForLoopNode("
            f"variable={self.variable!r}, "
            f"start_expr={self.start_expr!r}, "
            f"end_expr={self.end_expr!r}, "
            f"step_expr={self.step_expr!r}, "
            f"body={self.body!r}"
            f")"
        )


class WhileLoopNode:
    """Represents a WHILE loop: WHILE condition DO ... END_WHILE."""

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return (
            f"WhileLoopNode("
            f"condition={self.condition!r}, "
            f"body={self.body!r}"
            f")"
        )


class RepeatLoopNode:
    """Represents a REPEAT loop: REPEAT ... UNTIL condition END_REPEAT."""

    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

    def __repr__(self):
        return (
            f"RepeatLoopNode("
            f"body={self.body!r}, "
            f"condition={self.condition!r}"
            f")"
        )


class ExitNode:
    """Represents an EXIT statement."""

    def __repr__(self):
        return "ExitNode()"


class ReturnNode:
    """Represents a RETURN statement with optional value."""

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"ReturnNode(value={self.value!r})"


class ArrayTypeNode:
    """Represents an array type declaration: ARRAY [0..249] OF BYTE."""

    def __init__(self, bounds, element_type):
        self.bounds = bounds
        self.element_type = element_type

    def __repr__(self):
        return (
            f"ArrayTypeNode("
            f"bounds={self.bounds!r}, "
            f"element_type={self.element_type!r}"
            f")"
        )


class VariableDeclarationNode:
    """One variable declaration: names, type, optional default value, optional AT mapping."""

    def __init__(self, names, var_type, default_value=None, at_mapping=None):
        self.names = names
        self.var_type = var_type
        self.default_value = default_value
        self.at_mapping = at_mapping

    def __repr__(self):
        at_info = f", at_mapping={self.at_mapping!r}" if self.at_mapping is not None else ""
        return (
            f"VariableDeclarationNode("
            f"names={self.names!r}, "
            f"var_type={self.var_type!r}, "
            f"default_value={self.default_value!r}"
            f"{at_info}"
            f")"
        )


class MemoryMappingNode:
    """Represents an IEC memory mapping address such as AT %QX0.0 or AT %IW100."""

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return f"MemoryMappingNode(address={self.address!r})"


class TaskNode:
    """Represents an IEC TASK declaration: TASK task0(INTERVAL := T#100ms, PRIORITY := 0);"""

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return (
            f"TaskNode("
            f"name={self.name!r}, "
            f"arguments={self.arguments!r}"
            f")"
        )


class ProgramBindingNode:
    """Represents an IEC PROGRAM binding: PROGRAM Instance0 WITH task0 : MainProgram;"""

    def __init__(self, instance_name, task_name, program_type):
        self.instance_name = instance_name
        self.task_name = task_name
        self.program_type = program_type

    def __repr__(self):
        return (
            f"ProgramBindingNode("
            f"instance_name={self.instance_name!r}, "
            f"task_name={self.task_name!r}, "
            f"program_type={self.program_type!r}"
            f")"
        )


class ResourceNode:
    """Represents an IEC RESOURCE declaration: RESOURCE PLC0 ON PLC ... END_RESOURCE"""

    def __init__(self, name, on, body):
        self.name = name
        self.on = on
        self.body = body

    def __repr__(self):
        return (
            f"ResourceNode("
            f"name={self.name!r}, "
            f"on={self.on!r}, "
            f"body={self.body!r}"
            f")"
        )


class ConfigurationNode:
    """Represents an IEC CONFIGURATION declaration: CONFIGURATION Config0 ... END_CONFIGURATION"""

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self):
        return (
            f"ConfigurationNode("
            f"name={self.name!r}, "
            f"body={self.body!r}"
            f")"
        )
