"""Symbol table data structure for semantic analysis."""


class SymbolTable:
    """Store variable names and their semantic types."""

    def __init__(self):
        self.symbols = {}

    def insert(self, name, variable_type):
        """Insert or update a variable name and type."""

        self.symbols[name] = variable_type

    def lookup(self, name):
        """Return the type for a variable name, or None if it is unknown."""

        return self.symbols.get(name)

    def contains(self, name):
        """Return True when a variable name is already in the table."""

        return name in self.symbols

    def to_dict(self):
        """Return known symbols in stable order."""

        return {name: self.symbols[name] for name in sorted(self.symbols)}

    def __repr__(self):
        return f"SymbolTable(symbols={self.symbols!r})"
