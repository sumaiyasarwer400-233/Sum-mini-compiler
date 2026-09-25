class Symbol:
    def __init__(
        self,
        name,
        symbol_type,
        kind="variable",
        parameters=None,
        fields=None
    ):
        self.name = name
        self.symbol_type = symbol_type
        self.kind = kind
        self.parameters = parameters or []
        self.fields = fields or {}

    def __repr__(self):
        return (
            f"Symbol("
            f"name={self.name}, "
            f"type={self.symbol_type}, "
            f"kind={self.kind}"
            f")"
        )


class Scope:
    def __init__(self, name="global", parent=None):
        self.name = name
        self.parent = parent
        self.symbols = {}

    def define(self, symbol):
        """
        Add a symbol to the current scope.

        Returns:
            True  -> symbol added
            False -> duplicate symbol in current scope
        """
        if symbol.name in self.symbols:
            return False

        self.symbols[symbol.name] = symbol
        return True

    def lookup_local(self, name):
        """
        Search only the current scope.
        """
        return self.symbols.get(name)

    def lookup(self, name):
        """
        Static/lexical scope lookup.

        Search order:
        current scope
        -> parent scope
        -> grandparent scope
        -> global scope
        """
        scope = self

        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]

            scope = scope.parent

        return None


class SymbolTable:
    """
    Symbol table supporting nested scopes and static scoping.

    Example:

        global scope
             |
        function scope
             |
        nested function scope

    A nested function can access symbols from
    its enclosing lexical scope.
    """

    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope

    # --------------------------------------------------
    # Scope management
    # --------------------------------------------------

    def enter_scope(self, name="scope"):
        new_scope = Scope(
            name=name,
            parent=self.current_scope
        )

        self.current_scope = new_scope

        return new_scope

    def exit_scope(self):
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    # --------------------------------------------------
    # Symbol management
    # --------------------------------------------------

    def define(
        self,
        name,
        symbol_type,
        kind="variable",
        parameters=None,
        fields=None
    ):
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            kind=kind,
            parameters=parameters,
            fields=fields
        )

        success = self.current_scope.define(symbol)

        if success:
            return symbol

        return None

    def define_symbol(self, symbol):
        return self.current_scope.define(symbol)

    # --------------------------------------------------
    # Lookup
    # --------------------------------------------------

    def lookup(self, name):
        """
        Static scope lookup.

        The nearest lexical declaration is returned.
        """
        return self.current_scope.lookup(name)

    def lookup_local(self, name):
        return self.current_scope.lookup_local(name)

    # --------------------------------------------------
    # Utility functions
    # --------------------------------------------------

    def current_scope_name(self):
        return self.current_scope.name

    def print_scope(self, scope=None, level=0):
        if scope is None:
            scope = self.current_scope

        indentation = "  " * level

        print(
            f"{indentation}Scope: {scope.name}"
        )

        for name, symbol in scope.symbols.items():
            print(
                f"{indentation}  "
                f"{name} -> "
                f"{symbol.kind}, "
                f"type={symbol.symbol_type}"
            )

    def print_current_scope(self):
        self.print_scope(self.current_scope)

    def reset(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
