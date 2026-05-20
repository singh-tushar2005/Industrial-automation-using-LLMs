"""
Beginner-friendly symbol table for semantic analysis.

A symbol table is a compiler data structure that remembers facts about names.
For Structured Text, the most important first fact is usually a variable's type:

    Motor       -> BOOL
    Temp        -> NUMBER
    Counter     -> NUMBER

The parser only knows syntax. It can tell us that "Motor" is a variable name,
but it should not decide what type Motor has. That is semantic analysis work,
so it belongs in the semantic layer.
"""


class SymbolTable:
    """Store variable names and their semantic types.

    This first version uses one flat dictionary. That is enough for the current
    parser because the language subset does not have functions, programs with
    declarations, local scopes, or function blocks yet.

    Later, this can grow into nested scopes:

        global symbols
        function block symbols
        local temporary symbols
        input/output port symbols
    """

    def __init__(self):
        # The keys are variable names, such as "Motor".
        # The values are type names, such as "BOOL" or "NUMBER".
        self.symbols = {}

    def insert(self, name, variable_type):
        """Insert a new variable name and type.

        If the variable already exists, this method updates its type. Keeping
        insertion simple is useful for teaching, and the type checker performs
        compatibility checks before changing established types.
        """

        self.symbols[name] = variable_type

    def lookup(self, name):
        """Return the type for a variable name, or None if it is unknown."""

        return self.symbols.get(name)

    def contains(self, name):
        """Return True when a variable name is already in the table."""

        return name in self.symbols

    def print_symbols(self):
        """Print all known symbols in a stable, readable order."""

        print("Symbol table:")

        if not self.symbols:
            print("  <empty>")
            return

        for name in sorted(self.symbols):
            print(f"  {name}: {self.symbols[name]}")

    def __repr__(self):
        return f"SymbolTable(symbols={self.symbols!r})"
