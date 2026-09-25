class Symbol:
    def __init__(self, name, symbol_type, kind="variable"):
        self.name = name
        self.symbol_type = symbol_type
        self.kind = kind

    def __repr__(self):
        return (
            f"Symbol(name={self.name}, "
            f"type={self.symbol_type}, "
            f"kind={self.kind})"
        )


class Scope:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, symbol):
        if symbol.name in self.symbols:
            return False

        self.symbols[symbol.name] = symbol
        return True

    def lookup_local(self, name):
        return self.symbols.get(name)

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.lookup(name)

        return None


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope

    def enter_scope(self):
        self.current_scope = Scope(self.current_scope)

    def exit_scope(self):
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def define(self, name, symbol_type, kind="variable"):
        symbol = Symbol(
            name,
            symbol_type,
            kind
        )

        return self.current_scope.define(symbol)

    def lookup(self, name):
        return self.current_scope.lookup(name)

    def lookup_local(self, name):
        return self.current_scope.lookup_local(name)

    def print_scope(self, scope=None, level=0):
        if scope is None:
            scope = self.current_scope

        spaces = "  " * level

        print(spaces + "Scope:")

        for symbol in scope.symbols.values():
            print(
                spaces +
                f"  {symbol.name} : "
                f"{symbol.symbol_type} "
                f"({symbol.kind})"
            )
