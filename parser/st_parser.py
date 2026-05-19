"""
Beginner-friendly IEC 61131-3 Structured Text IF statement parser.

This example uses pyparsing to parse a very small subset of Structured Text:

    IF StartButton THEN
        Motor := TRUE;
    END_IF;

The goal is educational clarity, not full IEC 61131-3 coverage.
"""

from pprint import pprint

from pyparsing import (
    Group,
    Keyword,
    ParseException,
    ParserElement,
    Suppress,
    Word,
    alphanums,
    alphas,
    oneOf,
)


# Enable packrat parsing, which lets pyparsing remember previous parse results.
# This is optional for this tiny parser, but it is a good habit for larger grammars.
ParserElement.enablePackrat()


def build_st_if_parser():
    """Build and return a parser for one simple Structured Text IF statement."""

    # -------------------------------------------------------------------------
    # 1. Keywords
    # -------------------------------------------------------------------------
    # Keyword() matches a complete language keyword.
    # For example, Keyword("IF") matches "IF" but not the "IF" inside "DIFFERENT".
    IF = Keyword("IF")
    THEN = Keyword("THEN")
    END_IF = Keyword("END_IF")
    TRUE = Keyword("TRUE")
    FALSE = Keyword("FALSE")

    # -------------------------------------------------------------------------
    # 2. Punctuation and operators
    # -------------------------------------------------------------------------
    # Suppress() means "this text is required, but do not include it in output".
    assignment_operator = Suppress(":=")
    semicolon = Suppress(";")

    # -------------------------------------------------------------------------
    # 3. Identifiers
    # -------------------------------------------------------------------------
    # Identifiers are variable names such as StartButton or Motor.
    # This simple rule allows letters and underscores first, then letters,
    # numbers, and underscores after that.
    reserved_words = IF | THEN | END_IF | TRUE | FALSE
    identifier = (~reserved_words + Word(alphas + "_", alphanums + "_")).setName(
        "identifier"
    )

    # -------------------------------------------------------------------------
    # 4. Boolean values
    # -------------------------------------------------------------------------
    # oneOf() creates a parser that accepts one value from a list of choices.
    boolean_value = oneOf("TRUE FALSE").setName("boolean value")

    # -------------------------------------------------------------------------
    # 5. Boolean assignment
    # -------------------------------------------------------------------------
    # Group() keeps related parsed items together.
    #
    # This matches statements like:
    #     Motor := TRUE;
    boolean_assignment = Group(
        identifier("target")
        + assignment_operator
        + boolean_value("value")
        + semicolon
    )("assignment")

    # -------------------------------------------------------------------------
    # 6. IF statement grammar
    # -------------------------------------------------------------------------
    # This matches:
    #     IF <condition> THEN
    #         <boolean assignment>
    #     END_IF;
    #
    # The keywords and punctuation are suppressed so the final output focuses on
    # the meaningful structure: condition, assignment target, and assigned value.
    if_statement = Group(
        Suppress(IF)
        + identifier("condition")
        + Suppress(THEN)
        + boolean_assignment
        + Suppress(END_IF)
        + semicolon
    )("if_statement")

    return if_statement


def parse_st_if_statement(source_code):
    """Parse ST source code and return a plain Python dictionary."""

    parser = build_st_if_parser()

    # parseString() asks pyparsing to apply the grammar to the input text.
    # parseAll=True means the whole input must match, with no extra text left over.
    parsed = parser.parseString(source_code, parseAll=True)

    # Convert pyparsing's ParseResults object into a regular nested dictionary.
    return parsed["if_statement"].asDict()


def main():
    """Run a small example and print the structured parsed output."""

    sample_code = """
    IF StartButton THEN
        Motor := TRUE;
    END_IF;
    """

    print("Source Structured Text:")
    print(sample_code.strip())

    print("\nStructured parsed output:")
    try:
        parsed_output = parse_st_if_statement(sample_code)
        pprint(parsed_output)
    except ParseException as error:
        print("Could not parse the ST code.")
        print(error)


if __name__ == "__main__":
    main()
