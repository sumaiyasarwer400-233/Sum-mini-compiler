class Symbol:
    def __init__(
        self,
        name,
        symbol_type,
        kind="variable",
        size=None,
        parameters=None,
    ):
        self.name = name
        self.symbol_type = symbol_type
        self.kind = kind
        self.size = size
        self.parameters = parameters or []

    def __repr__(self):
        if self.kind == "array":
            return (
                f"Symbol(name={self.name}, "
                f"type={self.symbol_type}, "
                f"kind=array, size={self.size})"
            )

        return (
            f"Symbol(name={self.name}, "
            f"type={self.symbol_type}, "
            f"kind={self.kind})"
        )


class Scope:
    def __init__(self, name="global", parent=None):
        self.name = name
        self.parent = parent
        self.symbols = {}

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
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_level = 0

    def enter_scope(self, name="block"):
        new_scope = Scope(
            name=name,
            parent=self.current_scope
        )

        self.current_scope = new_scope
        self.scope_level += 1

    def exit_scope(self):
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent
            self.scope_level -= 1

    def define(
        self,
        name,
        symbol_type,
        kind="variable",
        size=None,
        parameters=None,
    ):
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            kind=kind,
            size=size,
            parameters=parameters,
        )

        return self.current_scope.define(symbol)

    def define_symbol(self, symbol):
        return self.current_scope.define(symbol)

    def lookup(self, name):
        return self.current_scope.lookup(name)

    def lookup_local(self, name):
        return self.current_scope.lookup_local(name)

    def print_scope(self, scope=None, level=0):
        if scope is None:
            scope = self.global_scope

        indentation = "    " * level

        print(
            f"{indentation}Scope: {scope.name}"
        )

        for name, symbol in scope.symbols.items():
            print(
                f"{indentation}  {name} -> {symbol}"
            )

    def dump(self):
        print("\n========== SYMBOL TABLE ==========")

        scope = self.current_scope

        while scope is not None:
            print(f"\nScope: {scope.name}")

            if not scope.symbols:
                print("  (empty)")

            for name, symbol in scope.symbols.items():
                if symbol.kind == "array":
                    print(
                        f"  {name} : "
                        f"{symbol.symbol_type} "
                        f"[{symbol.size}] "
                        f"({symbol.kind})"
                    )

                elif symbol.kind == "function":
                    print(
                        f"  {name} : "
                        f"{symbol.symbol_type} "
                        f"({symbol.kind})"
                    )

                else:
                    print(
                        f"  {name} : "
                        f"{symbol.symbol_type} "
                        f"({symbol.kind})"
                    )

            scope = scope.parent

        print("==================================")
