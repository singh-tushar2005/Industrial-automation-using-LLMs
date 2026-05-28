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
BinaryExpressionNode = AST_NODES_MODULE.BinaryExpressionNode
LogicalExpressionNode = AST_NODES_MODULE.LogicalExpressionNode
AssignmentNode = AST_NODES_MODULE.AssignmentNode
FunctionBlockCallNode = AST_NODES_MODULE.FunctionBlockCallNode
BlockNode = AST_NODES_MODULE.BlockNode
IfStatementNode = AST_NODES_MODULE.IfStatementNode
CaseBranchNode = AST_NODES_MODULE.CaseBranchNode
CaseStatementNode = AST_NODES_MODULE.CaseStatementNode
ProgramNode = AST_NODES_MODULE.ProgramNode
CompilationUnitNode = AST_NODES_MODULE.CompilationUnitNode
VarBlockNode = AST_NODES_MODULE.VarBlockNode
VariableDeclarationNode = AST_NODES_MODULE.VariableDeclarationNode


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


def make_function_block_argument(tokens):
    """Convert one named function block argument into a tuple."""

    return (token_text(tokens["name"]), tokens["value"])


def make_function_block_call_node(tokens):
    """Convert invocation syntax into a FunctionBlockCallNode."""

    return FunctionBlockCallNode(token_text(tokens["name"]), list(tokens.get("arguments", [])))


def make_block_node(tokens):
    """Wrap a sequence of parsed statements in a BlockNode."""

    return BlockNode(list(tokens))


def make_if_statement_node(tokens):
    """Convert IF syntax into an IfStatementNode."""

    return IfStatementNode(tokens["condition"], tokens["then_body"])


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


def make_program_node(tokens):
    """Wrap the top-level statement block in a ProgramNode."""

    return ProgramNode(tokens[0])


def make_variable_declaration_node(tokens):
    """Convert parsed variable declaration into a VariableDeclarationNode."""

    names = list(tokens.get("names", []))
    if not names and "name" in tokens:
        names = [token_text(tokens["name"])]
    var_type = token_text(tokens.get("var_type", ""))
    default_value = tokens.get("default", None)
    return VariableDeclarationNode(names, var_type, default_value)


def make_var_block_node(tokens):
    """Convert parsed VAR section into a VarBlockNode."""

    kind = token_text(tokens.get("var_kind", "VAR"))
    declarations = list(tokens.get("declarations", []))
    return VarBlockNode(kind, declarations)


def build_st_parser():
    """Build and return a parser for IEC 61131-3 Structured Text programs."""

    IF = Keyword("IF")
    THEN = Keyword("THEN")
    END_IF = Keyword("END_IF")
    TRUE = Keyword("TRUE")
    FALSE = Keyword("FALSE")
    AND = Keyword("AND")
    OR = Keyword("OR")
    NOT = Keyword("NOT")
    CASE = Keyword("CASE")
    OF = Keyword("OF")
    ELSE = Keyword("ELSE")
    END_CASE = Keyword("END_CASE")

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

    assignment_operator = Suppress(":=")
    semicolon = Suppress(";")
    colon = Suppress(":")
    comma = Suppress(",")

    comparison_operator = one_of("> >= < <= = <>")

    # Recursive placeholders are filled after dependent rules are defined.
    expression = Forward()
    statement = Forward()

    reserved_words = (
        IF | THEN | END_IF | TRUE | FALSE | AND | OR | NOT | CASE | OF | ELSE | END_CASE
        | PROGRAM_KW | END_PROGRAM | FUNCTION_KW | END_FUNCTION
        | FUNCTION_BLOCK_KW | END_FUNCTION_BLOCK
        | VAR_KW | VAR_INPUT | VAR_OUTPUT | VAR_IN_OUT | END_VAR
    )
    identifier_part = Word(alphas + "_", alphanums + "_")
    identifier_text = (~reserved_words + Combine(identifier_part + ZeroOrMore("." + identifier_part))).set_name(
        "identifier"
    )
    identifier = identifier_text.copy().set_parse_action(make_variable_node)

    boolean_value = (TRUE | FALSE).set_name("boolean value")
    boolean_value = boolean_value.copy().set_parse_action(make_boolean_node)

    number = pyparsing_common.number.copy().set_name("number")
    number = number.set_parse_action(make_number_node)

    time_literal = Regex(r"T#\d+(?:ms|s|m|h|d)").set_name("time literal")
    time_literal = time_literal.set_parse_action(make_time_literal_node)

    parenthesized_expression = Suppress("(") + expression + Suppress(")")
    atom = time_literal | number | boolean_value | identifier | parenthesized_expression

    # Operator order defines expression precedence from highest to lowest.
    expression <<= infix_notation(
        atom,
        [
            (one_of("* /"), 2, OpAssoc.LEFT, make_binary_expression_node),
            (one_of("+ -"), 2, OpAssoc.LEFT, make_binary_expression_node),
            (comparison_operator, 2, OpAssoc.LEFT, make_binary_expression_node),
            (NOT, 1, OpAssoc.RIGHT, make_not_expression_node),
            (AND, 2, OpAssoc.LEFT, make_logical_expression_node),
            (OR, 2, OpAssoc.LEFT, make_logical_expression_node),
        ],
    )

    assignment_statement = (
        identifier("target")
        + assignment_operator
        + expression("value")
        + semicolon
    )
    assignment_statement.set_parse_action(make_assignment_node)

    function_block_argument = (
        identifier_text("name") + assignment_operator + expression("value")
    )
    function_block_argument.set_parse_action(make_function_block_argument)

    function_block_call = (
        identifier_text("name")
        + Suppress("(")
        + Optional(delimited_list(function_block_argument, delim=",")("arguments"))
        + Suppress(")")
        + semicolon
    )
    function_block_call.set_parse_action(make_function_block_call_node)

    block = OneOrMore(statement).set_parse_action(make_block_node)

    if_statement = (
        Suppress(IF)
        + expression("condition")
        + Suppress(THEN)
        + block("then_body")
        + Suppress(END_IF)
        + semicolon
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

    statement <<= case_statement | if_statement | function_block_call | assignment_statement

    # -----------------------------------------------------------------
    # Variable declaration support
    # -----------------------------------------------------------------
    identifier_list = (
        identifier_text
        + ZeroOrMore(Suppress(",") + identifier_text)
    )
    identifier_list.set_parse_action(lambda t: list(t))

    var_declaration = (
        identifier_list("names")
        + Suppress(":")
        + identifier_text("var_type")
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
        + block("body")
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
        + block("body")
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
        + block("body")
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

    # Backward-compatible top level: try compilation units, fall back to raw block.
    program = block.copy()
    program.add_parse_action(make_program_node)
    compilation_unit = (program_unit | function_unit | function_block_unit) | program

    return compilation_unit


def parse_st_program(source_code):
    """Parse Structured Text source code and return the AST root node."""

    parser = build_st_parser()

    # Strip IEC 61131-3 comments before parsing.
    block_comment = Regex(r"\(\*[^*]*\*+(?:[^)*][^*]*\*+)*\)")
    line_comment = Regex(r"//[^\n]*")
    parser.ignore(block_comment | line_comment)

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
