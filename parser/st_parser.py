"""IEC 61131-3 Structured Text parser that returns project AST objects."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pyparsing import (
    Combine,
    Forward,
    Keyword,
    OneOrMore,
    OpAssoc,
    Optional,
    ParseException,
    ParserElement,
    Regex,
    Suppress,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
    delimited_list,
    infix_notation,
    one_of,
    pyparsing_common,
)


# Cache repeated parse work for recursive grammar rules.
ParserElement.enable_packrat()


# -------------------------------------------------------------------------
# AST imports
# -------------------------------------------------------------------------
# Import by path to avoid colliding with Python's standard-library ast module.
AST_NODES_PATH = Path(__file__).resolve().parents[1] / "ast" / "nodes.py"
AST_NODES_SPEC = spec_from_file_location("industrial_automation_ast_nodes", AST_NODES_PATH)
AST_NODES_MODULE = module_from_spec(AST_NODES_SPEC)
AST_NODES_SPEC.loader.exec_module(AST_NODES_MODULE)

VariableNode = AST_NODES_MODULE.VariableNode
BooleanNode = AST_NODES_MODULE.BooleanNode
NumberNode = AST_NODES_MODULE.NumberNode
TimeLiteralNode = AST_NODES_MODULE.TimeLiteralNode
StringLiteralNode = AST_NODES_MODULE.StringLiteralNode
TypedLiteralNode = AST_NODES_MODULE.TypedLiteralNode
ArrayIndexNode = AST_NODES_MODULE.ArrayIndexNode
BinaryExpressionNode = AST_NODES_MODULE.BinaryExpressionNode
LogicalExpressionNode = AST_NODES_MODULE.LogicalExpressionNode
AssignmentNode = AST_NODES_MODULE.AssignmentNode
InvocationArgumentNode = AST_NODES_MODULE.InvocationArgumentNode
FunctionBlockCallNode = AST_NODES_MODULE.FunctionBlockCallNode
FunctionInvocationNode = AST_NODES_MODULE.FunctionInvocationNode
BlockNode = AST_NODES_MODULE.BlockNode
IfStatementNode = AST_NODES_MODULE.IfStatementNode
CaseBranchNode = AST_NODES_MODULE.CaseBranchNode
CaseStatementNode = AST_NODES_MODULE.CaseStatementNode
ProgramNode = AST_NODES_MODULE.ProgramNode
CompilationUnitNode = AST_NODES_MODULE.CompilationUnitNode
VarBlockNode = AST_NODES_MODULE.VarBlockNode
VariableDeclarationNode = AST_NODES_MODULE.VariableDeclarationNode
ForLoopNode = AST_NODES_MODULE.ForLoopNode
WhileLoopNode = AST_NODES_MODULE.WhileLoopNode
RepeatLoopNode = AST_NODES_MODULE.RepeatLoopNode
ExitNode = AST_NODES_MODULE.ExitNode
ReturnNode = AST_NODES_MODULE.ReturnNode
ArrayTypeNode = AST_NODES_MODULE.ArrayTypeNode
MemoryMappingNode = AST_NODES_MODULE.MemoryMappingNode
TaskNode = AST_NODES_MODULE.TaskNode
ProgramBindingNode = AST_NODES_MODULE.ProgramBindingNode
ResourceNode = AST_NODES_MODULE.ResourceNode
ConfigurationNode = AST_NODES_MODULE.ConfigurationNode


# -------------------------------------------------------------------------
# Dataset paths
# -------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"


# -------------------------------------------------------------------------
# Parse action helpers
# -------------------------------------------------------------------------
# Parse actions convert matched syntax into AST objects.


def make_variable_node(tokens):
    """Convert parsed identifier text into a VariableNode."""

    return VariableNode(tokens[0])


def make_boolean_node(tokens):
    """Convert TRUE or FALSE into a BooleanNode."""

    return BooleanNode(tokens[0] == "TRUE")


def make_number_node(tokens):
    """Convert an integer or decimal literal into a NumberNode."""

    return NumberNode(tokens[0])


def token_text(token):
    """Return a plain string from a pyparsing token or ParseResults object."""

    if isinstance(token, str):
        return token

    return str(token[0])


def make_time_literal_node(tokens):
    """Convert an IEC time literal into a TimeLiteralNode."""

    return TimeLiteralNode(tokens[0])


def make_string_literal_node(tokens):
    """Convert a string literal into a StringLiteralNode."""

    return StringLiteralNode(tokens[0])


def make_typed_literal_node(tokens):
    """Convert an IEC typed literal into a TypedLiteralNode."""

    parts = tokens[0].split("#", 1)
    return TypedLiteralNode(parts[0], parts[1])


def make_array_index_node(tokens):
    """Convert array indexing syntax into an ArrayIndexNode."""

    return ArrayIndexNode(token_text(tokens["array"]), tokens["index"])


def _make_left_associative_binary_node(tokens, node_factory):
    """Build a left-to-right expression tree from operator tokens."""

    parts = tokens[0]
    expression = parts[0]

    for index in range(1, len(parts), 2):
        operator = parts[index]
        right = parts[index + 1]
        expression = node_factory(expression, operator, right)

    return expression


def make_binary_expression_node(tokens):
    """Build arithmetic and comparison BinaryExpressionNode objects."""

    return _make_left_associative_binary_node(
        tokens,
        lambda left, operator, right: BinaryExpressionNode(left, operator, right),
    )


def make_logical_expression_node(tokens):
    """Build AND/OR LogicalExpressionNode objects."""

    return _make_left_associative_binary_node(
        tokens,
        lambda left, operator, right: LogicalExpressionNode(operator, [left, right]),
    )


def make_not_expression_node(tokens):
    """Build a unary NOT LogicalExpressionNode."""

    operator, operand = tokens[0]
    return LogicalExpressionNode(operator, [operand])


def make_assignment_node(tokens):
    """Convert assignment syntax into an AssignmentNode."""

    return AssignmentNode(tokens["target"], tokens["value"])


def make_invocation_argument_node(tokens):
    """Convert one named argument into an InvocationArgumentNode."""

    return InvocationArgumentNode(token_text(tokens["name"]), tokens["value"])


def make_function_block_call_node(tokens):
    """Convert invocation syntax into a FunctionBlockCallNode."""

    return FunctionBlockCallNode(token_text(tokens["name"]), list(tokens.get("arguments", [])))


def make_function_invocation_node(tokens):
    """Convert function invocation syntax into a FunctionInvocationNode."""

    return FunctionInvocationNode(token_text(tokens["name"]), list(tokens.get("arguments", [])))


def make_block_node(tokens):
    """Wrap a sequence of parsed statements in a BlockNode."""

    return BlockNode(list(tokens))


def make_if_statement_node(tokens):
    """Convert IF syntax into an IfStatementNode."""

    return IfStatementNode(
        tokens["condition"],
        tokens["then_body"],
        list(tokens.get("elsif_branches", [])),
        tokens.get("else_body"),
    )


def make_case_branch_node(tokens):
    """Convert one CASE branch into a CaseBranchNode."""

    return CaseBranchNode(tokens["match_value"], tokens["body"])


def make_case_statement_node(tokens):
    """Convert CASE syntax into a CaseStatementNode."""

    return CaseStatementNode(
        tokens["selector"],
        list(tokens.get("branches", [])),
        tokens.get("else_body"),
    )


def make_for_loop_node(tokens):
    """Convert FOR syntax into a ForLoopNode."""

    return ForLoopNode(
        token_text(tokens["variable"]),
        tokens["start"],
        tokens["end"],
        tokens.get("step", NumberNode("1")),
        tokens["body"],
    )


def make_while_loop_node(tokens):
    """Convert WHILE syntax into a WhileLoopNode."""

    return WhileLoopNode(tokens["condition"], tokens["body"])


def make_repeat_loop_node(tokens):
    """Convert REPEAT syntax into a RepeatLoopNode."""

    return RepeatLoopNode(tokens["body"], tokens["condition"])


def make_exit_node(tokens):
    """Convert EXIT syntax into an ExitNode."""

    return ExitNode()


def make_return_node(tokens):
    """Convert RETURN syntax into a ReturnNode."""

    return ReturnNode(tokens.get("value", None))


def make_program_node(tokens):
    """Wrap the top-level statement block in a ProgramNode."""

    return ProgramNode(tokens[0])


def make_variable_declaration_node(tokens):
    """Convert parsed variable declaration into a VariableDeclarationNode."""

    names = list(tokens.get("names", []))
    if not names and "name" in tokens:
        names = [token_text(tokens["name"])]
    var_type = tokens.get("var_type", "")
    if isinstance(var_type, str):
        var_type = token_text(var_type)
    elif hasattr(var_type, "__iter__") and not isinstance(var_type, (dict, str)):
        # ParseResults or list from identifier_text
        var_type = token_text(var_type)
    default_value = tokens.get("default", None)
    at_mapping = tokens.get("at", None)
    return VariableDeclarationNode(names, var_type, default_value, at_mapping)


def make_var_block_node(tokens):
    """Convert parsed VAR section into a VarBlockNode."""

    kind = token_text(tokens.get("var_kind", "VAR"))
    declarations = list(tokens.get("declarations", []))
    return VarBlockNode(kind, declarations)


def make_memory_mapping_node(tokens):
    """Convert an AT address into a MemoryMappingNode."""

    return MemoryMappingNode(token_text(tokens[0]))


def make_task_node(tokens):
    """Convert TASK declaration into a TaskNode."""

    return TaskNode(token_text(tokens["task_name"]), list(tokens.get("arguments", [])))


def make_program_binding_node(tokens):
    """Convert PROGRAM binding syntax into a ProgramBindingNode."""

    return ProgramBindingNode(
        token_text(tokens["instance_name"]),
        token_text(tokens.get("task_name", "")),
        token_text(tokens["program_type"]),
    )


def make_resource_node(tokens):
    """Convert RESOURCE syntax into a ResourceNode."""

    return ResourceNode(
        token_text(tokens["resource_name"]),
        token_text(tokens["on"]),
        BlockNode(list(tokens.get("body", []))),
    )


def make_configuration_node(tokens):
    """Convert CONFIGURATION syntax into a ConfigurationNode."""

    return ConfigurationNode(
        token_text(tokens["config_name"]),
        BlockNode(list(tokens.get("body", []))),
    )


def build_st_parser():
    """Build and return a parser for IEC 61131-3 Structured Text programs."""

    IF = Keyword("IF")
    THEN = Keyword("THEN")
    END_IF = Keyword("END_IF")
    ELSIF = Keyword("ELSIF")
    ELSE = Keyword("ELSE")
    TRUE = Keyword("TRUE")
    FALSE = Keyword("FALSE")
    AND = Keyword("AND")
    OR = Keyword("OR")
    XOR = Keyword("XOR")
    NOT = Keyword("NOT")
    CASE = Keyword("CASE")
    OF = Keyword("OF")
    END_CASE = Keyword("END_CASE")

    # Loop keywords
    FOR = Keyword("FOR")
    TO = Keyword("TO")
    BY = Keyword("BY")
    DO = Keyword("DO")
    END_FOR = Keyword("END_FOR")
    WHILE = Keyword("WHILE")
    END_WHILE = Keyword("END_WHILE")
    REPEAT = Keyword("REPEAT")
    UNTIL = Keyword("UNTIL")
    END_REPEAT = Keyword("END_REPEAT")
    EXIT = Keyword("EXIT")
    RETURN = Keyword("RETURN")

    # IEC compilation-unit keywords
    PROGRAM_KW = Keyword("PROGRAM")
    END_PROGRAM = Keyword("END_PROGRAM")
    FUNCTION_KW = Keyword("FUNCTION")
    END_FUNCTION = Keyword("END_FUNCTION")
    FUNCTION_BLOCK_KW = Keyword("FUNCTION_BLOCK")
    END_FUNCTION_BLOCK = Keyword("END_FUNCTION_BLOCK")

    # Variable-section keywords
    VAR_KW = Keyword("VAR")
    VAR_INPUT = Keyword("VAR_INPUT")
    VAR_OUTPUT = Keyword("VAR_OUTPUT")
    VAR_IN_OUT = Keyword("VAR_IN_OUT")
    END_VAR = Keyword("END_VAR")
    ARRAY = Keyword("ARRAY")

    # Runtime / deployment keywords
    CONFIGURATION_KW = Keyword("CONFIGURATION")
    END_CONFIGURATION = Keyword("END_CONFIGURATION")
    RESOURCE_KW = Keyword("RESOURCE")
    END_RESOURCE = Keyword("END_RESOURCE")
    TASK_KW = Keyword("TASK")
    WITH_KW = Keyword("WITH")
    ON_KW = Keyword("ON")
    AT_KW = Keyword("AT")

    assignment_operator = Suppress(":=")
    semicolon = Suppress(";")
    colon = Suppress(":")
    comma = Suppress(",")

    comparison_operator = one_of("> >= < <= = <>")

    # Recursive placeholders are filled after dependent rules are defined.
    expression = Forward()
    statement = Forward()
    runtime_item = Forward()

    reserved_words = (
        IF | THEN | END_IF | ELSIF | ELSE | TRUE | FALSE | AND | OR | XOR | NOT | CASE | OF | END_CASE
        | FOR | TO | BY | DO | END_FOR | WHILE | END_WHILE | REPEAT | UNTIL | END_REPEAT | EXIT | RETURN
        | PROGRAM_KW | END_PROGRAM | FUNCTION_KW | END_FUNCTION
        | FUNCTION_BLOCK_KW | END_FUNCTION_BLOCK
        | VAR_KW | VAR_INPUT | VAR_OUTPUT | VAR_IN_OUT | END_VAR | ARRAY
        | CONFIGURATION_KW | END_CONFIGURATION | RESOURCE_KW | END_RESOURCE
        | TASK_KW | WITH_KW | ON_KW | AT_KW
    )
    identifier_part = Word(alphas + "_", alphanums + "_")
    identifier_text = (~reserved_words + Combine(identifier_part + ZeroOrMore("." + identifier_part))).set_name(
        "identifier"
    )
    identifier = identifier_text.copy().set_parse_action(make_variable_node)

    boolean_value = (TRUE | FALSE).set_name("boolean value")
    boolean_value = boolean_value.copy().set_parse_action(make_boolean_node)

    number = Regex(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?!\.\d)").set_name("number")
    number = number.set_parse_action(make_number_node)

    # Case-insensitive time literal: T#2s, t#1s, T#0s
    time_literal = Regex(r"[tT]#\d+(?:ms|s|m|h|d)").set_name("time literal")
    time_literal = time_literal.set_parse_action(make_time_literal_node)

    # Plain hex literal: 16#00000001, 8#377, 2#1010
    hex_literal = Regex(r"\b(16|8|2)#[0-9A-Fa-f_]+\b").set_name("hex literal")
    hex_literal = hex_literal.set_parse_action(make_number_node)

    # String literal: 'hello', '', '0'
    string_literal = Regex(r"'[^']*'").set_name("string literal")
    string_literal = string_literal.set_parse_action(make_string_literal_node)

    # Typed literals: BYTE#0, DWORD#16#8000_0000, BYTE#2#0000_0001, REAL#1.0, STRING#'0', TIME#1s
    # Reordered so specific forms (16#, 2#, time values) are tried before generic hex/digit matches.
    typed_literal = Regex(
        r"\b(BOOL|BYTE|WORD|DWORD|INT|DINT|UINT|UDINT|REAL|TIME|STRING)"
        r"#(16#[0-9A-Fa-f_]+|2#[01_]+|\d+(?:ms|s|m|h|d)|[0-9._]+|'[^']*')"
    ).set_name("typed literal")
    typed_literal = typed_literal.set_parse_action(make_typed_literal_node)

    # IEC memory mapping address: AT %QX0.0, AT %IW100, AT %MB0
    at_address = Regex(r"%[IQMX][XBWD]?\d+(?:\.\d+)?").set_name("AT address")
    at_address = at_address.copy().set_parse_action(make_memory_mapping_node)

    parenthesized_expression = Suppress("(") + expression + Suppress(")")

    # Array indexing: PT[pos], hexDigits[digitValue]
    array_index = (
        identifier_text("array")
        + Suppress("[")
        + expression("index")
        + Suppress("]")
    )
    array_index.set_parse_action(make_array_index_node)

    # Function invocation in expression context: SHL(x, 1), SIN(x), BYTE_TO_DWORD(PT[pos])
    # Supports both named and positional arguments
    invocation_argument = (
        Optional(identifier_text("name") + assignment_operator)
        + expression("value")
    )
    invocation_argument.set_parse_action(
        lambda t: InvocationArgumentNode(
            token_text(t.get("name", "")), t["value"]
        )
        if "name" in t
        else InvocationArgumentNode("", t["value"])
    )

    function_invocation = (
        identifier_text("name")
        + Suppress("(")
        + Optional(delimited_list(invocation_argument, delim=",")("arguments"))
        + Suppress(")")
    )
    function_invocation.set_parse_action(make_function_invocation_node)

    # Atoms: the basic building blocks of expressions
    atom = function_invocation | typed_literal | time_literal | hex_literal | string_literal | number | boolean_value | array_index | identifier | parenthesized_expression

    # Operator order defines expression precedence from highest to lowest.
    expression <<= infix_notation(
        atom,
        [
            (one_of("* /"), 2, OpAssoc.LEFT, make_binary_expression_node),
            (one_of("+ -"), 2, OpAssoc.LEFT, make_binary_expression_node),
            (comparison_operator, 2, OpAssoc.LEFT, make_binary_expression_node),
            (NOT, 1, OpAssoc.RIGHT, make_not_expression_node),
            (AND, 2, OpAssoc.LEFT, make_logical_expression_node),
            (XOR, 2, OpAssoc.LEFT, make_logical_expression_node),
            (OR, 2, OpAssoc.LEFT, make_logical_expression_node),
        ],
    )

    assignment_target = (array_index | identifier).set_parse_action(lambda t: t[0])
    assignment_statement = (
        assignment_target("target")
        + assignment_operator
        + expression("value")
        + semicolon
    )
    assignment_statement.set_parse_action(make_assignment_node)

    # Function block call (statement level): Timer(IN := TRUE, PT := T#2s);
    fb_call_argument = (
        identifier_text("name") + assignment_operator + expression("value")
    )
    fb_call_argument.set_parse_action(make_invocation_argument_node)

    function_block_call = (
        identifier_text("name")
        + Suppress("(")
        + Optional(delimited_list(fb_call_argument, delim=",")("arguments"))
        + Suppress(")")
        + semicolon
    )
    function_block_call.set_parse_action(make_function_block_call_node)

    block = OneOrMore(statement).set_parse_action(make_block_node)
    optional_block = ZeroOrMore(statement).set_parse_action(make_block_node)

    # Control flow statements
    exit_statement = Suppress(EXIT) + semicolon
    exit_statement.set_parse_action(make_exit_node)

    return_statement = Suppress(RETURN) + Optional(expression("value")) + semicolon
    return_statement.set_parse_action(make_return_node)

    # Loop statements
    for_loop = (
        Suppress(FOR)
        + identifier_text("variable")
        + assignment_operator
        + expression("start")
        + Suppress(TO)
        + expression("end")
        + Optional(Suppress(BY) + expression("step"))
        + Suppress(DO)
        + optional_block("body")
        + Suppress(END_FOR)
        + Optional(semicolon)
    )
    for_loop.set_parse_action(make_for_loop_node)

    while_loop = (
        Suppress(WHILE)
        + expression("condition")
        + Suppress(DO)
        + optional_block("body")
        + Suppress(END_WHILE)
        + Optional(semicolon)
    )
    while_loop.set_parse_action(make_while_loop_node)

    repeat_loop = (
        Suppress(REPEAT)
        + optional_block("body")
        + Suppress(UNTIL)
        + expression("condition")
        + Suppress(END_REPEAT)
        + Optional(semicolon)
    )
    repeat_loop.set_parse_action(make_repeat_loop_node)

    # IF statement with ELSIF and ELSE
    elsif_branch = (
        Suppress(ELSIF)
        + expression("condition")
        + Suppress(THEN)
        + block("body")
    )
    elsif_branch.set_parse_action(lambda t: (t["condition"], t["body"]))

    if_statement = (
        Suppress(IF)
        + expression("condition")
        + Suppress(THEN)
        + block("then_body")
        + ZeroOrMore(elsif_branch)("elsif_branches")
        + Optional(Suppress(ELSE) + block("else_body"))
        + Suppress(END_IF)
        + Optional(semicolon)
    )
    if_statement.set_parse_action(make_if_statement_node)

    case_branch = (
        expression("match_value")
        + colon
        + block("body")
    )
    case_branch.set_parse_action(make_case_branch_node)

    case_statement = (
        Suppress(CASE)
        + expression("selector")
        + Suppress(OF)
        + OneOrMore(case_branch)("branches")
        + Optional(Suppress(ELSE) + block("else_body"))
        + Suppress(END_CASE)
        + Optional(semicolon)
    )
    case_statement.set_parse_action(make_case_statement_node)

    statement <<= (
        case_statement
        | if_statement
        | for_loop
        | while_loop
        | repeat_loop
        | exit_statement
        | return_statement
        | function_block_call
        | assignment_statement
    )

    # -----------------------------------------------------------------
    # Variable declaration support
    # -----------------------------------------------------------------
    identifier_list = (
        identifier_text
        + ZeroOrMore(Suppress(",") + identifier_text)
    )
    identifier_list.set_parse_action(lambda t: list(t))

    # Array type declaration: ARRAY [0..249] OF BYTE
    # Array bounds are typically simple integer literals or constants,
    # not full expressions, so we use a simpler rule to avoid infix_notation issues.
    array_bound_atom = number | identifier_text
    array_bounds = (
        array_bound_atom("lower")
        + Suppress("..")
        + array_bound_atom("upper")
    )
    array_type = (
        Suppress(ARRAY)
        + Suppress("[")
        + array_bounds("bounds")
        + Suppress("]")
        + Suppress("OF")
        + identifier_text("element_type")
    )
    array_type.set_parse_action(
        lambda t: ArrayTypeNode(
            (t["lower"], t["upper"]),
            token_text(t["element_type"]),
        )
    )

    var_type = array_type | identifier_text

    var_declaration = (
        identifier_list("names")
        + Optional(Suppress(AT_KW) + at_address("at"))
        + Suppress(":")
        + var_type("var_type")
        + Optional(Suppress(":=") + expression("default"))
        + semicolon
    )
    var_declaration.set_parse_action(make_variable_declaration_node)

    var_block = (
        (VAR_KW | VAR_INPUT | VAR_OUTPUT | VAR_IN_OUT)("var_kind")
        + ZeroOrMore(var_declaration)("declarations")
        + Suppress(END_VAR)
    )
    var_block.set_parse_action(make_var_block_node)

    var_blocks = ZeroOrMore(var_block)("var_blocks")

    # -----------------------------------------------------------------
    # Compilation-unit support
    # -----------------------------------------------------------------
    program_unit = (
        Suppress(PROGRAM_KW)
        + identifier_text("unit_name")
        + var_blocks
        + optional_block("body")
        + Suppress(END_PROGRAM)
    )
    program_unit.set_parse_action(
        lambda t: CompilationUnitNode(
            "PROGRAM",
            token_text(t.get("unit_name")),
            t.get("body"),
            list(t.get("var_blocks", [])),
            None,
        )
    )

    function_unit = (
        Suppress(FUNCTION_KW)
        + identifier_text("unit_name")
        + Suppress(":")
        + identifier_text("return_type")
        + var_blocks
        + optional_block("body")
        + Suppress(END_FUNCTION)
    )
    function_unit.set_parse_action(
        lambda t: CompilationUnitNode(
            "FUNCTION",
            token_text(t.get("unit_name")),
            t.get("body"),
            list(t.get("var_blocks", [])),
            token_text(t.get("return_type")),
        )
    )

    function_block_unit = (
        Suppress(FUNCTION_BLOCK_KW)
        + identifier_text("unit_name")
        + var_blocks
        + optional_block("body")
        + Suppress(END_FUNCTION_BLOCK)
    )
    function_block_unit.set_parse_action(
        lambda t: CompilationUnitNode(
            "FUNCTION_BLOCK",
            token_text(t.get("unit_name")),
            t.get("body"),
            list(t.get("var_blocks", [])),
            None,
        )
    )

    # -----------------------------------------------------------------
    # Runtime / deployment grammar support
    # -----------------------------------------------------------------

    # TASK declaration: TASK task0(INTERVAL := T#100ms, PRIORITY := 0);
    task_declaration = (
        Suppress(TASK_KW)
        + identifier_text("task_name")
        + Suppress("(")
        + Optional(delimited_list(fb_call_argument, delim=",")("arguments"))
        + Suppress(")")
        + semicolon
    )
    task_declaration.set_parse_action(make_task_node)

    # PROGRAM binding: PROGRAM Instance0 WITH task0 : MainProgram;
    program_binding = (
        Suppress(PROGRAM_KW)
        + identifier_text("instance_name")
        + Optional(Suppress(WITH_KW) + identifier_text("task_name"))
        + Suppress(":")
        + identifier_text("program_type")
        + semicolon
    )
    program_binding.set_parse_action(make_program_binding_node)

    # Items that can appear inside CONFIGURATION or RESOURCE
    runtime_item <<= (
        task_declaration
        | program_binding
        | var_block
    )

    # RESOURCE declaration: RESOURCE PLC0 ON PLC ... END_RESOURCE
    resource_unit = (
        Suppress(RESOURCE_KW)
        + identifier_text("resource_name")
        + Suppress(ON_KW)
        + identifier_text("on")
        + ZeroOrMore(runtime_item)("body")
        + Suppress(END_RESOURCE)
    )
    resource_unit.set_parse_action(make_resource_node)

    # CONFIGURATION declaration: CONFIGURATION Config0 ... END_CONFIGURATION
    configuration_unit = (
        Suppress(CONFIGURATION_KW)
        + identifier_text("config_name")
        + ZeroOrMore(runtime_item | resource_unit)("body")
        + Suppress(END_CONFIGURATION)
    )
    configuration_unit.set_parse_action(make_configuration_node)

    # Backward-compatible top level: try compilation units, fall back to raw block.
    program = block.copy()
    program.add_parse_action(make_program_node)
    compilation_unit = (program_unit | function_unit | function_block_unit | configuration_unit | resource_unit) | program

    # Industrial IEC 61131-3 files frequently contain multiple compilation units
    # in sequence (e.g., INCLUDE.st). Wrap them in a ProgramNode so the rest
    # of the pipeline sees a single root node.
    root_parser = OneOrMore(compilation_unit)
    root_parser.set_parse_action(lambda t: ProgramNode(BlockNode(list(t))))

    return root_parser


def parse_st_program(source_code):
    """Parse Structured Text source code and return the AST root node."""

    parser = build_st_parser()

    # Strip IEC 61131-3 comments and C-style pragma blocks before parsing.
    block_comment = Regex(r"\(\*[^*]*\*+(?:[^)*][^*]*\*+)*\)")
    line_comment = Regex(r"//[^\n]*")
    pragma_block = Regex(r"\{[^{}]*\}")
    parser.ignore(block_comment | line_comment | pragma_block)

    parsed = parser.parse_string(source_code, parse_all=True)
    return parsed[0]


def parse_st_if_statement(source_code):
    """Parse source code and return the first top-level IF statement.

    Kept for compatibility with earlier examples that parsed one IF statement.
    """

    program = parse_st_program(source_code)
    first_statement = program.body.statements[0]

    if not isinstance(first_statement, IfStatementNode):
        raise ParseException(source_code, 0, "Expected a top-level IF statement")

    return first_statement


def load_st_file(file_path):
    """Load one Structured Text file and return its text."""

    return Path(file_path).read_text(encoding="utf-8")


def parse_st_file(file_path):
    """Load one .st file, parse it, and return the generated ProgramNode."""

    source_code = load_st_file(file_path)
    return parse_st_program(source_code)


def find_dataset_files(dataset_dir=DATASETS_DIR):
    """Return all .st files under dataset_dir, recursively, in stable sorted order.

    Excludes any files inside directories named ``docs`` to keep documentation
    and executable datasets architecturally separated.
    """

    dataset_path = Path(dataset_dir)

    if not dataset_path.exists():
        return []

    files = [
        path
        for path in dataset_path.rglob("*.st")
        if "docs" not in path.parts
    ]

    return sorted(files)


def parse_dataset_files(file_paths):
    """Parse multiple Structured Text files and return their ASTs."""

    return [parse_st_file(file_path) for file_path in file_paths]


def parse_dataset_file_map(file_paths):
    """Parse files and return a file_path -> AST mapping."""

    return {Path(file_path): parse_st_file(file_path) for file_path in file_paths}
