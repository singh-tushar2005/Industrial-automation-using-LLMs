"""
Beginner-friendly IEC 61131-3 Structured Text parser.

This parser is still intentionally small, but it now handles the important
building blocks that make real industrial automation code interesting:

    * arithmetic expressions, such as Counter + 1
    * numeric comparisons, such as Temp > 100
    * logical expressions, such as StartButton AND SafetyOK
    * multiple statements inside an IF block
    * nested IF statements

The parser does not define AST classes. It imports them from ../ast/nodes.py so
the project keeps a compiler-like separation:

    parser/st_parser.py  -> grammar and parse actions
    ast/nodes.py         -> AST data structures
    datasets/*.st        -> real Structured Text examples

Keeping examples in external dataset files matters because parser code and
training/evaluation data are different concerns. The parser should describe the
language. The dataset should describe the examples we want to test, compare,
label, or eventually feed into AI migration pipelines.
"""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from pprint import pprint

from pyparsing import (
    Forward,
    Keyword,
    OneOrMore,
    OpAssoc,
    ParseException,
    ParserElement,
    Suppress,
    Word,
    alphanums,
    alphas,
    infix_notation,
    one_of,
    pyparsing_common,
)


# Packrat parsing lets pyparsing remember earlier parse results.
# Recursive grammars and expression grammars often revisit the same text, so
# this keeps the parser fast as examples grow.
ParserElement.enable_packrat()


# -------------------------------------------------------------------------
# AST imports
# -------------------------------------------------------------------------
# This folder is named "ast", which is also the name of Python's standard
# library ast module. Importing by file path avoids that name collision while
# still keeping all AST definitions in one shared architecture file.
AST_NODES_PATH = Path(__file__).resolve().parents[1] / "ast" / "nodes.py"
AST_NODES_SPEC = spec_from_file_location("industrial_automation_ast_nodes", AST_NODES_PATH)
AST_NODES_MODULE = module_from_spec(AST_NODES_SPEC)
AST_NODES_SPEC.loader.exec_module(AST_NODES_MODULE)

VariableNode = AST_NODES_MODULE.VariableNode
BooleanNode = AST_NODES_MODULE.BooleanNode
NumberNode = AST_NODES_MODULE.NumberNode
BinaryExpressionNode = AST_NODES_MODULE.BinaryExpressionNode
LogicalExpressionNode = AST_NODES_MODULE.LogicalExpressionNode
AssignmentNode = AST_NODES_MODULE.AssignmentNode
BlockNode = AST_NODES_MODULE.BlockNode
IfStatementNode = AST_NODES_MODULE.IfStatementNode
ProgramNode = AST_NODES_MODULE.ProgramNode


# -------------------------------------------------------------------------
# Dataset paths
# -------------------------------------------------------------------------
# PROJECT_ROOT points at the repository folder:
#
#     D:/Industrial Automation
#
# DATASETS_DIR is where .st Structured Text examples live. Adding new parser
# examples should usually mean adding another .st file here, not editing parser
# source code.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"


# -------------------------------------------------------------------------
# Parse action helpers
# -------------------------------------------------------------------------
# A parse action is called when a grammar rule matches. These functions are the
# bridge between raw syntax and AST objects.


def make_variable_node(tokens):
    """Convert parsed identifier text into a VariableNode."""

    return VariableNode(tokens[0])


def make_boolean_node(tokens):
    """Convert TRUE or FALSE into a BooleanNode."""

    return BooleanNode(tokens[0] == "TRUE")


def make_number_node(tokens):
    """Convert an integer or decimal literal into a NumberNode."""

    return NumberNode(tokens[0])


def _make_left_associative_binary_node(tokens, node_factory):
    """Build a left-to-right expression tree from pyparsing operator tokens.

    pyparsing gives infix parse actions a flat list for a chain like:

        Counter + 1 - Offset

    as:

        [Counter, "+", 1, "-", Offset]

    A compiler wants a tree, so we fold that list from the left:

        ((Counter + 1) - Offset)
    """

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


def make_block_node(tokens):
    """Wrap a sequence of parsed statements in a BlockNode."""

    return BlockNode(list(tokens))


def make_if_statement_node(tokens):
    """Convert IF syntax into an IfStatementNode."""

    return IfStatementNode(tokens["condition"], tokens["then_body"])


def make_program_node(tokens):
    """Wrap the top-level statement block in a ProgramNode."""

    return ProgramNode(tokens[0])


def build_st_parser():
    """Build and return a parser for a small Structured Text program."""

    # ---------------------------------------------------------------------
    # 1. Keywords
    # ---------------------------------------------------------------------
    # Keyword() matches complete words only. Keyword("IF") will match IF, but
    # it will not accidentally match the IF inside a longer identifier.
    IF = Keyword("IF")
    THEN = Keyword("THEN")
    END_IF = Keyword("END_IF")
    TRUE = Keyword("TRUE")
    FALSE = Keyword("FALSE")
    AND = Keyword("AND")
    OR = Keyword("OR")
    NOT = Keyword("NOT")

    # ---------------------------------------------------------------------
    # 2. Punctuation and operators
    # ---------------------------------------------------------------------
    # Suppress() means the text must exist in the source, but it should not
    # appear in the parse results. AST nodes keep meaning, not punctuation.
    assignment_operator = Suppress(":=")
    semicolon = Suppress(";")

    comparison_operator = one_of("> >= < <= = <>")

    # ---------------------------------------------------------------------
    # 3. Recursive grammar placeholders
    # ---------------------------------------------------------------------
    # An IF block can contain statements, and a statement can itself be an IF.
    # That circular relationship is a recursive grammar, so pyparsing needs a
    # Forward() placeholder before the full rule is known.
    expression = Forward()
    statement = Forward()

    # ---------------------------------------------------------------------
    # 4. Atomic values
    # ---------------------------------------------------------------------
    # These are the smallest pieces of an expression: names, numbers, booleans,
    # and parenthesized subexpressions.
    reserved_words = IF | THEN | END_IF | TRUE | FALSE | AND | OR | NOT
    identifier_text = (~reserved_words + Word(alphas + "_", alphanums + "_")).set_name(
        "identifier"
    )
    identifier = identifier_text.copy().set_parse_action(make_variable_node)

    boolean_value = (TRUE | FALSE).set_name("boolean value")
    boolean_value = boolean_value.copy().set_parse_action(make_boolean_node)

    number = pyparsing_common.number.copy().set_name("number")
    number = number.set_parse_action(make_number_node)

    parenthesized_expression = Suppress("(") + expression + Suppress(")")
    atom = number | boolean_value | identifier | parenthesized_expression

    # ---------------------------------------------------------------------
    # 5. Expression parsing
    # ---------------------------------------------------------------------
    # Expressions are central to compiler design because they describe how
    # values are computed. Conditions, assignments, loop bounds, and function
    # arguments all eventually depend on expression trees.
    #
    # infix_notation() handles precedence for us:
    #   * and / happen before + and -
    #   comparisons happen after arithmetic
    #   NOT happens before AND
    #   AND happens before OR
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

    # ---------------------------------------------------------------------
    # 6. Statements
    # ---------------------------------------------------------------------
    # Assignment statements can now assign any expression, not only TRUE/FALSE:
    #
    #     Motor := TRUE;
    #     NextCount := Counter + 1;
    assignment_statement = (
        identifier("target")
        + assignment_operator
        + expression("value")
        + semicolon
    )
    assignment_statement.set_parse_action(make_assignment_node)

    # A block is one or more statements. Because statement is recursive, this
    # block can contain assignments, IF statements, or IF statements containing
    # more IF statements.
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

    # Now that both concrete statement forms exist, fill in the Forward().
    statement <<= if_statement | assignment_statement

    # A program is just a top-level block wrapped in ProgramNode.
    program = block.copy()
    program.add_parse_action(make_program_node)

    return program


def parse_st_program(source_code):
    """Parse Structured Text source code and return a ProgramNode."""

    parser = build_st_parser()
    parsed = parser.parse_string(source_code, parse_all=True)
    return parsed[0]


def parse_st_if_statement(source_code):
    """Parse source code and return the first top-level IF statement.

    Older examples in this project used this function when the parser only
    understood one IF statement. Keeping it makes the expanded parser easier to
    try without breaking beginner scripts that already call it.
    """

    program = parse_st_program(source_code)
    first_statement = program.body.statements[0]

    if not isinstance(first_statement, IfStatementNode):
        raise ParseException(source_code, 0, "Expected a top-level IF statement")

    return first_statement


def load_st_file(file_path):
    """Load one Structured Text file and return its text.

    The parser works with strings, but migration systems usually work with
    files. This small loader is the bridge between dataset files and the parser.
    """

    return Path(file_path).read_text(encoding="utf-8")


def parse_st_file(file_path):
    """Load one .st file, parse it, and return the generated ProgramNode."""

    source_code = load_st_file(file_path)
    return parse_st_program(source_code)


def find_dataset_files(dataset_dir=DATASETS_DIR):
    """Return all .st files in a dataset directory in stable sorted order.

    Sorting gives repeatable output. Repeatability is important for testing,
    debugging, and AI evaluation pipelines where the same input set should
    produce results in the same order every run.
    """

    dataset_path = Path(dataset_dir)

    if not dataset_path.exists():
        return []

    return sorted(dataset_path.glob("*.st"))


def print_ast_for_file(file_path):
    """Load, parse, and print the AST for one Structured Text file."""

    source_code = load_st_file(file_path)

    print(f"Dataset file: {file_path}")
    print("Source Structured Text:")
    print(source_code.strip())
    print("\nGenerated AST:")

    try:
        ast = parse_st_program(source_code)
        pprint(ast)
    except ParseException as error:
        print("Could not parse the ST code.")
        print(error)


def parse_dataset_files(file_paths):
    """Parse multiple Structured Text files sequentially and print each AST."""

    for index, file_path in enumerate(file_paths):
        if index > 0:
            print("\n" + "-" * 72 + "\n")

        print_ast_for_file(file_path)


def build_argument_parser():
    """Build a tiny command-line interface for the dataset parser.

    With no arguments, the parser reads every .st file from datasets/.
    You can also pass one or more explicit .st files:

        python parser/st_parser.py datasets/nested_if.st
    """

    argument_parser = argparse.ArgumentParser(
        description="Parse IEC 61131-3 Structured Text dataset files."
    )
    argument_parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Optional .st files to parse. Defaults to every .st file in datasets/.",
    )
    return argument_parser


def main():
    """Load Structured Text dataset files, parse them, and print their ASTs."""

    argument_parser = build_argument_parser()
    arguments = argument_parser.parse_args()

    # Hardcoded examples are useful for a first tutorial, but they quickly
    # become a bottleneck. Real migration work needs many external examples:
    # vendor snippets, legacy PLC programs, edge cases, and labeled evaluation
    # cases. Keeping those in datasets/ means the parser can grow without
    # mixing language logic with test data.
    dataset_files = arguments.files or find_dataset_files()

    if not dataset_files:
        print(f"No .st files found in {DATASETS_DIR}.")
        return

    parse_dataset_files(dataset_files)


if __name__ == "__main__":
    main()
