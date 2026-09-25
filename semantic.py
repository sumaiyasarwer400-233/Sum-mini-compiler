from ast import (
    Program,
    Block,
    VariableDeclaration,
    StructDeclaration,
    FunctionDeclaration,
    IfStatement,
    ReturnStatement,
    Assignment,
    ExpressionStatement,
    BinaryExpression,
    UnaryExpression,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    FunctionCall,
    StructAccess,
)

from symbol_table import SymbolTable


class SemanticAnalyzer:
    """
    Semantic analyzer for MiniLang Variant 2.

    Supports:
    - Symbol table
    - Nested scopes
    - Static scoping
    - Struct/record checking
    - Function checking
    - Type checking
    - Return checking
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

        # Struct definitions are stored globally.
        self.structs = {}

        # Current function being analyzed.
        self.current_function = None

    # ==================================================
    # Error handling
    # ==================================================

    def error(self, node, message):
        line = getattr(node, "line", 0)
        column = getattr(node, "column", 0)

        self.errors.append(
            f"Semantic error at line {line}, "
            f"column {column}: {message}"
        )

    # ==================================================
    # Main analysis
    # ==================================================

    def analyze(self, node):
        if isinstance(node, Program):
            self.analyze_program(node)

        return self.errors

    def analyze_program(self, program):
        # First register all top-level struct definitions.
        for declaration in program.declarations:
            if isinstance(declaration, StructDeclaration):
                self.register_struct(declaration)

        # Register top-level functions before analysis.
        for declaration in program.declarations:
            if isinstance(declaration, FunctionDeclaration):
                self.register_function(declaration)

        # Analyze declarations/statements.
        for declaration in program.declarations:
            self.visit(declaration)

    # ==================================================
    # Visitor
    # ==================================================

    def visit(self, node):
        if node is None:
            return None

        if isinstance(node, StructDeclaration):
            return self.visit_struct_declaration(node)

        if isinstance(node, VariableDeclaration):
            return self.visit_variable_declaration(node)

        if isinstance(node, FunctionDeclaration):
            return self.visit_function_declaration(node)

        if isinstance(node, Block):
            return self.visit_block(node)

        if isinstance(node, IfStatement):
            return self.visit_if(node)

        if isinstance(node, ReturnStatement):
            return self.visit_return(node)

        if isinstance(node, Assignment):
            return self.visit_assignment(node)

        if isinstance(node, ExpressionStatement):
            return self.visit(node.expression)

        if isinstance(node, BinaryExpression):
            return self.visit_binary(node)

        if isinstance(node, UnaryExpression):
            return self.visit_unary(node)

        if isinstance(node, NumberLiteral):
            return "int"

        if isinstance(node, StringLiteral):
            return "string"

        if isinstance(node, BooleanLiteral):
            return "bool"

        if isinstance(node, Identifier):
            return self.visit_identifier(node)

        if isinstance(node, StructAccess):
            return self.visit_struct_access(node)

        if isinstance(node, FunctionCall):
            return self.visit_function_call(node)

        return None

    # ==================================================
    # Structs
    # ==================================================

    def register_struct(self, node):
        if node.name in self.structs:
            self.error(
                node,
                f"Duplicate struct declaration '{node.name}'."
            )
            return

        fields = {}

        for field in node.fields:
            if field.name in fields:
                self.error(
                    field,
                    f"Duplicate field '{field.name}' "
                    f"in struct '{node.name}'."
                )
                continue

            field_type = field.field_type

            if (
                field_type not in
                ("int", "bool", "string")
                and field_type not in self.structs
            ):
                self.error(
                    field,
                    f"Unknown field type '{field_type}'."
                )

            fields[field.name] = field_type

        self.structs[node.name] = fields

    def visit_struct_declaration(self, node):
        # Already processed during registration.
        return None

    # ==================================================
    # Variables
    # ==================================================

    def visit_variable_declaration(self, node):
        var_type = node.var_type

        # Check user-defined struct type.
        if (
            var_type not in
            ("int", "bool", "string")
            and var_type not in self.structs
        ):
            self.error(
                node,
                f"Unknown type '{var_type}'."
            )

        symbol = self.symbol_table.define(
            name=node.name,
            symbol_type=var_type,
            kind="variable"
        )

        if symbol is None:
            self.error(
                node,
                f"Duplicate declaration of '{node.name}'."
            )

    # ==================================================
    # Functions
    # ==================================================

    def register_function(self, node):
        parameters = [
            parameter.param_type
            for parameter in node.parameters
        ]

        symbol = self.symbol_table.define(
            name=node.name,
            symbol_type=node.return_type,
            kind="function",
            parameters=parameters
        )

        if symbol is None:
            self.error(
                node,
                f"Duplicate function declaration '{node.name}'."
            )

    def visit_function_declaration(self, node):
        previous_function = self.current_function

        # Function symbol may already be registered.
        function_symbol = self.symbol_table.lookup_local(node.name)

        # If this is a nested function, define it
        # inside the current lexical scope.
        if function_symbol is None:
            parameters = [
                parameter.param_type
                for parameter in node.parameters
            ]

            function_symbol = self.symbol_table.define(
                name=node.name,
                symbol_type=node.return_type,
                kind="function",
                parameters=parameters
            )

            if function_symbol is None:
                self.error(
                    node,
                    f"Duplicate function '{node.name}'."
                )

        self.current_function = node

        # New lexical scope.
        self.symbol_table.enter_scope(
            f"function:{node.name}"
        )

        # Define parameters.
        for parameter in node.parameters:
            symbol = self.symbol_table.define(
                name=parameter.name,
                symbol_type=parameter.param_type,
                kind="parameter"
            )

            if symbol is None:
                self.error(
                    parameter,
                    f"Duplicate parameter '{parameter.name}'."
                )

        # Analyze function body.
        self.visit(node.body)

        # Exit function scope.
        self.symbol_table.exit_scope()

        self.current_function = previous_function

    # ==================================================
    # Blocks
    # ==================================================

    def visit_block(self, node):
        """
        A block creates a nested lexical scope.

        This is important for static scoping.
        """

        self.symbol_table.enter_scope("block")

        # Register nested functions first.
        for statement in node.statements:
            if isinstance(statement, FunctionDeclaration):
                parameters = [
                    parameter.param_type
                    for parameter in statement.parameters
                ]

                symbol = self.symbol_table.define(
                    name=statement.name,
                    symbol_type=statement.return_type,
                    kind="function",
                    parameters=parameters
                )

                if symbol is None:
                    self.error(
                        statement,
                        f"Duplicate function "
                        f"'{statement.name}'."
                    )

        for statement in node.statements:
            self.visit(statement)

        self.symbol_table.exit_scope()

    # ==================================================
    # If
    # ==================================================

    def visit_if(self, node):
        condition_type = self.visit(node.condition)

        if condition_type != "bool":
            self.error(
                node.condition,
                "If condition must be of type bool."
            )

        self.visit(node.then_branch)

        if node.else_branch is not None:
            self.visit(node.else_branch)

    # ==================================================
    # Return
    # ==================================================

    def visit_return(self, node):
        if self.current_function is None:
            self.error(
                node,
                "Return statement outside a function."
            )
            return

        expected_type = self.current_function.return_type

        if node.expression is None:
            self.error(
                node,
                f"Function '{self.current_function.name}' "
                f"must return {expected_type}."
            )
            return

        actual_type = self.visit(node.expression)

        if actual_type != expected_type:
            self.error(
                node,
                f"Return type mismatch: expected "
                f"{expected_type}, got {actual_type}."
            )

    # ==================================================
    # Assignment
    # ==================================================

    def visit_assignment(self, node):
        target_type = self.visit(node.target)
        value_type = self.visit(node.expression)

        if (
            target_type is not None
            and value_type is not None
            and target_type != value_type
        ):
            self.error(
                node,
                f"Type mismatch in assignment: "
                f"cannot assign {value_type} to {target_type}."
            )

    # ==================================================
    # Identifier
    # ==================================================

    def visit_identifier(self, node):
        symbol = self.symbol_table.lookup(node.name)

        if symbol is None:
            self.error(
                node,
                f"Undeclared identifier '{node.name}'."
            )
            return None

        return symbol.symbol_type

    # ==================================================
    # Struct access
    # ==================================================

    def visit_struct_access(self, node):
        symbol = self.symbol_table.lookup(
            node.object_name
        )

        if symbol is None:
            self.error(
                node,
                f"Undeclared identifier "
                f"'{node.object_name}'."
            )
            return None

        object_type = symbol.symbol_type

        if object_type not in self.structs:
            self.error(
                node,
                f"Invalid member access: "
                f"'{node.object_name}' is not a struct."
            )
            return None

        fields = self.structs[object_type]

        if node.field_name not in fields:
            self.error(
                node,
                f"Struct '{object_type}' has no field "
                f"'{node.field_name}'."
            )
            return None

        return fields[node.field_name]

    # ==================================================
    # Function call
    # ==================================================

    def visit_function_call(self, node):
        symbol = self.symbol_table.lookup(node.name)

        if symbol is None:
            self.error(
                node,
                f"Undeclared function '{node.name}'."
            )
            return None

        if symbol.kind != "function":
            self.error(
                node,
                f"'{node.name}' is not a function."
            )
            return None

        expected = len(symbol.parameters)
        actual = len(node.arguments)

        if expected != actual:
            self.error(
                node,
                f"Invalid function call to '{node.name}': "
                f"expected {expected} arguments, "
                f"got {actual}."
            )

        # Check argument types.
        for index, argument in enumerate(node.arguments):
            actual_type = self.visit(argument)

            if index < len(symbol.parameters):
                expected_type = symbol.parameters[index]

                if actual_type != expected_type:
                    self.error(
                        argument,
                        f"Argument {index + 1} of "
                        f"'{node.name}' must be "
                        f"{expected_type}, got "
                        f"{actual_type}."
                    )

        return symbol.symbol_type

    # ==================================================
    # Binary expression
    # ==================================================

    def visit_binary(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        operator = node.operator

        # Arithmetic operators
        if operator in {"+", "-", "*", "/", "%"}:

            if left_type != "int" or right_type != "int":
                self.error(
                    node,
                    f"Operator '{operator}' requires "
                    f"integer operands."
                )
                return None

            return "int"

        # Comparison operators
        if operator in {"<", ">", "<=", ">="}:

            if left_type != "int" or right_type != "int":
                self.error(
                    node,
                    f"Operator '{operator}' requires "
                    f"integer operands."
                )

            return "bool"

        # Equality
        if operator in {"==", "!="}:

            if (
                left_type is not None
                and right_type is not None
                and left_type != right_type
            ):
                self.error(
                    node,
                    f"Cannot compare {left_type} "
                    f"with {right_type}."
                )

            return "bool"

        # Logical operators
        if operator in {"&&", "||"}:

            if left_type != "bool" or right_type != "bool":
                self.error(
                    node,
                    f"Operator '{operator}' requires "
                    f"boolean operands."
                )

            return "bool"

        self.error(
            node,
            f"Unknown binary operator '{operator}'."
        )

        return None

    # ==================================================
    # Unary expression
    # ==================================================

    def visit_unary(self, node):
        operand_type = self.visit(node.operand)

        if node.operator == "-":

            if operand_type != "int":
                self.error(
                    node,
                    "Unary '-' requires an integer."
                )

            return "int"

        if node.operator == "!":

            if operand_type != "bool":
                self.error(
                    node,
                    "Unary '!' requires a boolean."
                )

            return "bool"

        return None

    # ==================================================
    # Utility
    # ==================================================

    def has_errors(self):
        return len(self.errors) > 0

    def print_errors(self):
        if not self.errors:
            print("No semantic errors.")
            return

        print("\nSemantic Errors:")

        for error in self.errors:
            print("-", error)
