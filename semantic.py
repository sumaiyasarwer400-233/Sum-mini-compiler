from dataclasses import dataclass


class SemanticError(Exception):
    pass


@dataclass
class Symbol:
    name: str
    type_name: str
    kind: str
    node: object = None


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def define(self, symbol):
        if symbol.name in self.symbols:
            raise SemanticError(
                f"Duplicate declaration: {symbol.name}"
            )
        self.symbols[symbol.name] = symbol

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]

        if self.parent:
            return self.parent.lookup(name)

        return None


class Analyzer:

    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.structs = {}
        self.functions = {}
        self.current_function = None
        self.loop_depth = 0

    def analyze(self, program):

        # First collect all struct declarations
        for declaration in program.declarations:
            if declaration.__class__.__name__ == "StructDecl":
                self.visit_struct(declaration)

        # Collect function headers
        for declaration in program.declarations:
            if declaration.__class__.__name__ == "FunctionDecl":
                self.visit_function_header(declaration)

        # Analyze function bodies
        for declaration in program.declarations:
            if declaration.__class__.__name__ == "FunctionDecl":
                self.visit_function(declaration)

        return True

    # ---------------- STRUCT ----------------

    def visit_struct(self, node):

        if node.name in self.structs:
            raise SemanticError(
                f"Duplicate struct: {node.name}"
            )

        fields = {}

        for field in node.fields:

            if field.name in fields:
                raise SemanticError(
                    f"Duplicate field '{field.name}' "
                    f"in struct '{node.name}'"
                )

            self.check_type(field.type_name)
            fields[field.name] = field.type_name

        self.structs[node.name] = fields

    # ---------------- FUNCTION ----------------

    def visit_function_header(self, node):

        if node.name in self.functions:
            raise SemanticError(
                f"Duplicate function: {node.name}"
            )

        return_type = node.return_type or "void"

        if return_type != "void":
            self.check_type(return_type)

        self.functions[node.name] = node

    def visit_function(self, node):

        old_scope = self.current_scope
        old_function = self.current_function

        self.current_function = node
        self.current_scope = Scope(old_scope)

        # Parameters
        for param in node.params:

            self.check_type(param.type_name)

            symbol = Symbol(
                param.name,
                param.type_name,
                "parameter",
                param
            )

            self.current_scope.define(symbol)

        self.visit_block(node.body)

        self.current_scope = old_scope
        self.current_function = old_function

    # ---------------- BLOCK ----------------

    def visit_block(self, node):

        old_scope = self.current_scope

        self.current_scope = Scope(old_scope)

        for statement in node.statements:
            self.visit(statement)

        self.current_scope = old_scope

    # ---------------- STATEMENTS ----------------

    def visit(self, node):

        name = node.__class__.__name__

        if name == "VarDecl":
            self.visit_var_decl(node)

        elif name == "Assign":
            self.visit_assign(node)

        elif name == "IfStmt":
            self.visit_if(node)

        elif name == "WhileStmt":
            self.visit_while(node)

        elif name == "ReturnStmt":
            self.visit_return(node)

        elif name == "PrintStmt":
            self.type_of(node.value)

        elif name == "BreakStmt":

            if self.loop_depth == 0:
                raise SemanticError(
                    "break used outside loop"
                )

        elif name == "ContinueStmt":

            if self.loop_depth == 0:
                raise SemanticError(
                    "continue used outside loop"
                )

        elif name == "ExprStmt":
            self.type_of(node.expression)

        elif name == "FunctionDecl":
            self.visit_nested_function(node)

    # ---------------- VARIABLE ----------------

    def visit_var_decl(self, node):

        self.check_type(node.type_name)

        symbol = Symbol(
            node.name,
            node.type_name,
            "variable",
            node
        )

        self.current_scope.define(symbol)

        if node.initializer is not None:

            value_type = self.type_of(
                node.initializer
            )

            if not self.is_assignable(
                node.type_name,
                value_type
            ):
                raise SemanticError(
                    f"Type mismatch: cannot assign "
                    f"{value_type} to {node.type_name}"
                )

    # ---------------- ASSIGNMENT ----------------

    def visit_assign(self, node):

        left_type = self.type_of(node.target)
        right_type = self.type_of(node.value)

        if not self.is_assignable(
            left_type,
            right_type
        ):
            raise SemanticError(
                f"Type mismatch: cannot assign "
                f"{right_type} to {left_type}"
            )

    # ---------------- IF ----------------

    def visit_if(self, node):

        condition_type = self.type_of(
            node.condition
        )

        if condition_type != "bool":
            raise SemanticError(
                "If condition must be bool"
            )

        self.visit_block(node.then_branch)

        if node.else_branch:
            self.visit_block(node.else_branch)

    # ---------------- WHILE ----------------

    def visit_while(self, node):

        condition_type = self.type_of(
            node.condition
        )

        if condition_type != "bool":
            raise SemanticError(
                "While condition must be bool"
            )

        self.loop_depth += 1

        self.visit_block(node.body)

        self.loop_depth -= 1

    # ---------------- RETURN ----------------

    def visit_return(self, node):

        if self.current_function is None:
            raise SemanticError(
                "return outside function"
            )

        expected = (
            self.current_function.return_type
            or "void"
        )

        actual = (
            "void"
            if node.value is None
            else self.type_of(node.value)
        )

        if expected != actual:

            if not self.is_assignable(
                expected,
                actual
            ):
                raise SemanticError(
                    f"Return type mismatch: "
                    f"expected {expected}, "
                    f"got {actual}"
                )

    # ---------------- NESTED FUNCTION ----------------

    def visit_nested_function(self, node):

        if node.name in self.current_scope.symbols:
            raise SemanticError(
                f"Duplicate function: {node.name}"
            )

        symbol = Symbol(
            node.name,
            "function",
            "function",
            node
        )

        self.current_scope.define(symbol)

        old_scope = self.current_scope
        old_function = self.current_function

        self.current_function = node
        self.current_scope = Scope(old_scope)

        for param in node.params:

            self.check_type(param.type_name)

            self.current_scope.define(
                Symbol(
                    param.name,
                    param.type_name,
                    "parameter",
                    param
                )
            )

        self.visit_block(node.body)

        self.current_scope = old_scope
        self.current_function = old_function

    # ---------------- TYPE CHECKING ----------------

    def type_of(self, node):

        name = node.__class__.__name__

        # Literal
        if name == "Literal":

            value = node.value

            if isinstance(value, bool):
                return "bool"

            if isinstance(value, int):
                return "int"

            if isinstance(value, float):
                return "float"

            if isinstance(value, str):
                return "string"

        # Variable
        elif name == "Variable":

            symbol = self.current_scope.lookup(
                node.name
            )

            if symbol is None:
                raise SemanticError(
                    f"Undeclared variable: {node.name}"
                )

            return symbol.type_name

        # Binary expression
        elif name == "Binary":

            left = self.type_of(node.left)
            right = self.type_of(node.right)
            op = node.operator

            if op in [
                "+", "-", "*", "/", "%"
            ]:

                if left not in ["int", "float"]:
                    raise SemanticError(
                        "Arithmetic requires numbers"
                    )

                if right not in ["int", "float"]:
                    raise SemanticError(
                        "Arithmetic requires numbers"
                    )

                if (
                    left == "float"
                    or right == "float"
                ):
                    return "float"

                return "int"

            if op in [
                "<", ">", "<=", ">="
            ]:
                return "bool"

            if op in ["==", "!="]:
                return "bool"

            if op in ["&&", "||"]:

                if (
                    left != "bool"
                    or right != "bool"
                ):
                    raise SemanticError(
                        "Logical operators require bool"
                    )

                return "bool"

        # Unary expression
        elif name == "Unary":

            operand_type = self.type_of(
                node.operand
            )

            if node.operator == "!":

                if operand_type != "bool":
                    raise SemanticError(
                        "! requires bool"
                    )

                return "bool"

            if node.operator == "-":

                if operand_type not in [
                    "int",
                    "float"
                ]:
                    raise SemanticError(
                        "Unary - requires number"
                    )

                return operand_type

        # Function call
        elif name == "Call":
            return self.type_of_call(node)

        # Struct member
        elif name == "Member":

            object_type = self.type_of(
                node.object
            )

            if object_type not in self.structs:
                raise SemanticError(
                    f"{object_type} is not a struct"
                )

            fields = self.structs[object_type]

            if node.name not in fields:
                raise SemanticError(
                    f"Unknown field: {node.name}"
                )

            return fields[node.name]

        return "void"

    # ---------------- FUNCTION CALL ----------------

    def type_of_call(self, node):

        if hasattr(node.callee, "name"):

            function_name = node.callee.name

            function = self.functions.get(
                function_name
            )

            if function is None:

                symbol = self.current_scope.lookup(
                    function_name
                )

                if symbol is None:
                    raise SemanticError(
                        f"Undeclared function: "
                        f"{function_name}"
                    )

                function = symbol.node

            if len(node.arguments) != len(
                function.params
            ):
                raise SemanticError(
                    f"Wrong number of arguments "
                    f"for {function_name}"
                )

            for arg, param in zip(
                node.arguments,
                function.params
            ):

                actual = self.type_of(arg)

                if not self.is_assignable(
                    param.type_name,
                    actual
                ):
                    raise SemanticError(
                        f"Argument type mismatch "
                        f"in {function_name}"
                    )

            return (
                function.return_type
                or "void"
            )

        raise SemanticError(
            "Invalid function call"
        )

    # ---------------- TYPE VALIDATION ----------------

    def check_type(self, type_name):

        builtin = {
            "int",
            "float",
            "string",
            "bool",
            "void"
        }

        if type_name in builtin:
            return

        if type_name not in self.structs:
            raise SemanticError(
                f"Unknown type: {type_name}"
            )

    # ---------------- ASSIGNABILITY ----------------

    def is_assignable(
        self,
        target,
        source
    ):

        if target == source:
            return True

        # int can be assigned to float
        if (
            target == "float"
            and source == "int"
        ):
            return True

        return False
