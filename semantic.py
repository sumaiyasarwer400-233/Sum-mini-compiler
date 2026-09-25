from ast import (
    Program,
    Block,
    VariableDeclaration,
    ArrayDeclaration,
    FunctionDeclaration,
    IfStatement,
    WhileStatement,
    SwitchStatement,
    CaseStatement,
    BreakStatement,
    ReturnStatement,
    Assignment,
    ArrayAccess,
    ExpressionStatement,
    BinaryExpression,
    UnaryExpression,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    FunctionCall,
)

from symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

        self.function_names = set()

        self.loop_depth = 0
        self.switch_depth = 0
        self.function_depth = 0

        self.current_function_return_type = None

    def error(self, message, node=None):
        if node is not None:
            message = (
                f"Semantic Error at line {node.line}, "
                f"column {node.column}: {message}"
            )

        else:
            message = f"Semantic Error: {message}"

        self.errors.append(message)

    # -------------------------------------------------
    # Main analysis
    # -------------------------------------------------

    def analyze(self, tree):
        if not isinstance(tree, Program):
            self.error("Invalid AST root.")
            return

        for declaration in tree.declarations:
            self.visit(declaration)

    # -------------------------------------------------
    # Dispatcher
    # -------------------------------------------------

    def visit(self, node):
        if node is None:
            return "void"

        method_name = (
            "visit_" +
            node.__class__.__name__.lower()
        )

        method = getattr(
            self,
            method_name,
            self.visit_unknown
        )

        return method(node)

    def visit_unknown(self, node):
        self.error(
            f"Unsupported AST node: "
            f"{node.__class__.__name__}",
            node
        )

        return "error"

    # -------------------------------------------------
    # Program / Block
    # -------------------------------------------------

    def visit_program(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_block(self, node):
        self.symbol_table.enter_scope("block")

        for statement in node.statements:
            self.visit(statement)

        self.symbol_table.exit_scope()

    # -------------------------------------------------
    # Variable declaration
    # -------------------------------------------------

    def visit_variabledeclaration(self, node):
        existing = self.symbol_table.lookup_local(
            node.name
        )

        if existing is not None:
            self.error(
                f"Duplicate declaration of "
                f"'{node.name}'.",
                node
            )
            return

        self.symbol_table.define(
            node.name,
            node.var_type,
            kind="variable"
        )

    # -------------------------------------------------
    # Array declaration
    # -------------------------------------------------

    def visit_arraydeclaration(self, node):
        existing = self.symbol_table.lookup_local(
            node.name
        )

        if existing is not None:
            self.error(
                f"Duplicate declaration of "
                f"'{node.name}'.",
                node
            )
            return

        if node.size <= 0:
            self.error(
                f"Array '{node.name}' must have "
                f"a positive size.",
                node
            )
            return

        self.symbol_table.define(
            node.name,
            node.element_type,
            kind="array",
            size=node.size
        )

    # -------------------------------------------------
    # Function
    # -------------------------------------------------

    def visit_functiondeclaration(self, node):
        existing = self.symbol_table.lookup_local(
            node.name
        )

        if existing is not None:
            self.error(
                f"Duplicate function "
                f"'{node.name}'.",
                node
            )
            return

        if node.name in self.function_names:
            self.error(
                f"Duplicate function "
                f"'{node.name}'.",
                node
            )
            return

        self.function_names.add(node.name)

        self.symbol_table.define(
            node.name,
            node.return_type,
            kind="function",
            parameters=node.parameters
        )

        self.function_depth += 1

        old_return_type = (
            self.current_function_return_type
        )

        self.current_function_return_type = (
            node.return_type
        )

        self.symbol_table.enter_scope(
            f"function:{node.name}"
        )

        for parameter in node.parameters:
            if self.symbol_table.lookup_local(
                parameter.name
            ):
                self.error(
                    f"Duplicate parameter "
                    f"'{parameter.name}'.",
                    parameter
                )
            else:
                self.symbol_table.define(
                    parameter.name,
                    parameter.param_type,
                    kind="parameter"
                )

        for statement in node.body.statements:
            self.visit(statement)

        self.symbol_table.exit_scope()

        self.current_function_return_type = (
            old_return_type
        )

        self.function_depth -= 1

    # -------------------------------------------------
    # If
    # -------------------------------------------------

    def visit_ifstatement(self, node):
        condition_type = self.visit(
            node.condition
        )

        if condition_type not in (
            "bool",
            "int",
            "error"
        ):
            self.error(
                "If condition must be "
                "boolean or integer.",
                node
            )

        self.visit(node.then_branch)

        if node.else_branch is not None:
            self.visit(node.else_branch)

    # -------------------------------------------------
    # While
    # -------------------------------------------------

    def visit_whilestatement(self, node):
        condition_type = self.visit(
            node.condition
        )

        if condition_type not in (
            "bool",
            "int",
            "error"
        ):
            self.error(
                "While condition must be "
                "boolean or integer.",
                node
            )

        self.loop_depth += 1

        self.visit(node.body)

        self.loop_depth -= 1

    # -------------------------------------------------
    # Switch
    # -------------------------------------------------

    def visit_switchstatement(self, node):
        expression_type = self.visit(
            node.expression
        )

        if expression_type not in (
            "int",
            "bool",
            "error"
        ):
            self.error(
                "Switch expression must be "
                "integer or boolean.",
                node
            )

        case_values = set()

        self.switch_depth += 1

        for case in node.cases:
            if case.value in case_values:
                self.error(
                    f"Duplicate switch case "
                    f"value '{case.value}'.",
                    case
                )
            else:
                case_values.add(case.value)

            self.visit(casesafe(case))

        if node.default_case is not None:
            self.visit(node.default_case)

        self.switch_depth -= 1

    # -------------------------------------------------
    # Case helper
    # -------------------------------------------------

    def visit_casestatement(self, node):
        for statement in node.statements:
            self.visit(statement)

    # -------------------------------------------------
    # Break
    # -------------------------------------------------

    def visit_breakstatement(self, node):
        if (
            self.loop_depth == 0
            and self.switch_depth == 0
        ):
            self.error(
                "'mbreak' can only be used "
                "inside a while loop or switch.",
                node
            )

    # -------------------------------------------------
    # Return
    # -------------------------------------------------

    def visit_returnstatement(self, node):
        if self.function_depth == 0:
            self.error(
                "'mreturn' used outside "
                "a function.",
                node
            )
            return

        expression_type = "void"

        if node.expression is not None:
            expression_type = self.visit(
                node.expression
            )

        if (
            expression_type != "error"
            and self.current_function_return_type
            != expression_type
        ):
            self.error(
                f"Return type mismatch. "
                f"Expected "
                f"'{self.current_function_return_type}', "
                f"got '{expression_type}'.",
                node
            )

    # -------------------------------------------------
    # Assignment
    # -------------------------------------------------

    def visit_assignment(self, node):
        target_type = self.visit(node.target)

        expression_type = self.visit(
            node.expression
        )

        if (
            target_type != "error"
            and expression_type != "error"
            and target_type != expression_type
        ):
            self.error(
                f"Type mismatch in assignment. "
                f"Cannot assign "
                f"'{expression_type}' to "
                f"'{target_type}'.",
                node
            )

    # -------------------------------------------------
    # Array access
    # -------------------------------------------------

    def visit_arrayaccess(self, node):
        symbol = self.symbol_table.lookup(
            node.name
        )

        if symbol is None:
            self.error(
                f"Undeclared identifier "
                f"'{node.name}'.",
                node
            )
            self.visit(node.index)
            return "error"

        if symbol.kind != "array":
            self.error(
                f"'{node.name}' is not an array.",
                node
            )
            self.visit(node.index)
            return "error"

        index_type = self.visit(node.index)

        if index_type not in (
            "int",
            "error"
        ):
            self.error(
                f"Array index of '{node.name}' "
                f"must be an integer.",
                node
            )

        # Compile-time bounds checking
        if isinstance(node.index, NumberLiteral):
            index = node.index.value

            if index < 0 or index >= symbol.size:
                self.error(
                    f"Array index {index} is out of "
                    f"bounds for array "
                    f"'{node.name}' of size "
                    f"{symbol.size}.",
                    node
                )

        return symbol.symbol_type

    # -------------------------------------------------
    # Expression statement
    # -------------------------------------------------

    def visit_expressionstatement(self, node):
        return self.visit(node.expression)

    # -------------------------------------------------
    # Identifier
    # -------------------------------------------------

    def visit_identifier(self, node):
        symbol = self.symbol_table.lookup(
            node.name
        )

        if symbol is None:
            self.error(
                f"Undeclared identifier "
                f"'{node.name}'.",
                node
            )
            return "error"

        if symbol.kind == "array":
            self.error(
                f"Array '{node.name}' must be "
                f"accessed using an index.",
                node
            )
            return "error"

        if symbol.kind == "function":
            self.error(
                f"Function '{node.name}' "
                f"requires a function call.",
                node
            )
            return "error"

        return symbol.symbol_type

    # -------------------------------------------------
    # Number
    # -------------------------------------------------

    def visit_numberliteral(self, node):
        return "int"

    # -------------------------------------------------
    # String
    # -------------------------------------------------

    def visit_stringliteral(self, node):
        return "string"

    # -------------------------------------------------
    # Boolean
    # -------------------------------------------------

    def visit_booleanliteral(self, node):
        return "bool"

    # -------------------------------------------------
    # Binary expression
    # -------------------------------------------------

    def visit_binaryexpression(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if (
            left_type == "error"
            or right_type == "error"
        ):
            return "error"

        arithmetic = {
            "+",
            "-",
            "*",
            "/",
            "%",
        }

        comparison = {
            "<",
            ">",
            "<=",
            ">=",
        }

        equality = {
            "==",
            "!=",
        }

        if node.operator in arithmetic:
            if (
                left_type != "int"
                or right_type != "int"
            ):
                self.error(
                    f"Arithmetic operator "
                    f"'{node.operator}' requires "
                    f"integer operands.",
                    node
                )
                return "error"

            return "int"

        if node.operator in comparison:
            if (
                left_type != "int"
                or right_type != "int"
            ):
                self.error(
                    f"Comparison operator "
                    f"'{node.operator}' requires "
                    f"integer operands.",
                    node
                )
                return "error"

            return "bool"

        if node.operator in equality:
            if left_type != right_type:
                self.error(
                    f"Cannot compare "
                    f"'{left_type}' and "
                    f"'{right_type}'.",
                    node
                )
                return "error"

            return "bool"

        self.error(
            f"Unknown binary operator "
            f"'{node.operator}'.",
            node
        )

        return "error"

    # -------------------------------------------------
    # Unary expression
    # -------------------------------------------------

    def visit_unaryexpression(self, node):
        operand_type = self.visit(
            node.operand
        )

        if operand_type == "error":
            return "error"

        if node.operator == "-":
            if operand_type != "int":
                self.error(
                    "Unary '-' requires "
                    "an integer.",
                    node
                )
                return "error"

            return "int"

        if node.operator == "!":
            if operand_type not in (
                "bool",
                "int"
            ):
                self.error(
                    "Unary '!' requires "
                    "boolean or integer.",
                    node
                )
                return "error"

            return "bool"

        return "error"

    # -------------------------------------------------
    # Function call
    # -------------------------------------------------

    def visit_functioncall(self, node):
        symbol = self.symbol_table.lookup(
            node.name
        )

        if symbol is None:
            self.error(
                f"Undefined function "
                f"'{node.name}'.",
                node
            )

            for argument in node.arguments:
                self.visit(argument)

            return "error"

        if symbol.kind != "function":
            self.error(
                f"'{node.name}' is not a function.",
                node
            )

            return "error"

        if len(node.arguments) != len(
            symbol.parameters
        ):
            self.error(
                f"Function '{node.name}' expects "
                f"{len(symbol.parameters)} "
                f"arguments but got "
                f"{len(node.arguments)}.",
                node
            )

        for index, argument in enumerate(
            node.arguments
        ):
            argument_type = self.visit(
                argument
            )

            if index < len(symbol.parameters):
                expected_type = (
                    symbol.parameters[index].param_type
                )

                if (
                    argument_type != "error"
                    and argument_type != expected_type
                ):
                    self.error(
                        f"Argument {index + 1} "
                        f"of function "
                        f"'{node.name}' should be "
                        f"'{expected_type}', "
                        f"got '{argument_type}'.",
                        node
                    )

        return symbol.symbol_type


def casesafe(case):
    return case
