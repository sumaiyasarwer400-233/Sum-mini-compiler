from symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None
        self.loop_depth = 0

    def error(self, message):
        self.errors.append(message)

    def analyze(self, program):
        for statement in program["statements"]:
            self.check_statement(statement)

    def check_statement(self, statement):
        node_type = statement["type"]

        if node_type == "Function":
            self.check_function(statement)

        elif node_type == "If":
            self.check_expression(statement["condition"])

            self.symbol_table.enter_scope()
            self.check_statement(statement["then"])
            self.symbol_table.exit_scope()

            if statement["else"] is not None:
                self.symbol_table.enter_scope()
                self.check_statement(statement["else"])
                self.symbol_table.exit_scope()

        elif node_type == "While":
            self.check_expression(statement["condition"])

            self.loop_depth += 1

            self.symbol_table.enter_scope()
            self.check_statement(statement["body"])
            self.symbol_table.exit_scope()

            self.loop_depth -= 1

        elif node_type == "For":
            self.symbol_table.enter_scope()

            if statement["initialization"]:
                self.check_expression(
                    statement["initialization"]
                )

            if statement["condition"]:
                condition_type = self.check_expression(
                    statement["condition"]
                )

                if condition_type not in ("bool", "int"):
                    self.error(
                        "For loop condition must be boolean"
                    )

            if statement["update"]:
                self.check_expression(
                    statement["update"]
                )

            self.loop_depth += 1
            self.check_statement(statement["body"])
            self.loop_depth -= 1

            self.symbol_table.exit_scope()

        elif node_type == "Break":
            if self.loop_depth == 0:
                self.error(
                    "break used outside a loop"
                )

        elif node_type == "Continue":
            if self.loop_depth == 0:
                self.error(
                    "continue used outside a loop"
                )

        elif node_type == "Return":
            if self.current_function is None:
                self.error(
                    "return used outside a function"
                )

            else:
                self.check_expression(
                    statement["value"]
                )

        elif node_type == "ExpressionStatement":
            self.check_expression(
                statement["expression"]
            )

    def check_function(self, function):
        name = function["name"]

        if self.symbol_table.lookup_local(name):
            self.error(
                f"Duplicate function declaration: {name}"
            )
            return

        self.symbol_table.define(
            name,
            "function",
            "function"
        )

        previous_function = self.current_function
        self.current_function = function

        self.symbol_table.enter_scope()

        for parameter in function["parameters"]:
            name = parameter["name"]
            data_type = parameter["type"]

            if self.symbol_table.lookup_local(name):
                self.error(
                    f"Duplicate parameter: {name}"
                )
            else:
                self.symbol_table.define(
                    name,
                    data_type,
                    "parameter"
                )

        self.check_statement(function["body"])

        self.symbol_table.exit_scope()

        self.current_function = previous_function

    def check_expression(self, expression):
        if expression is None:
            return "void"

        node_type = expression["type"]

        if node_type == "Number":
            return "int"

        if node_type == "Boolean":
            return "bool"

        if node_type == "Identifier":
            name = expression["name"]

            symbol = self.symbol_table.lookup(name)

            if symbol is None:
                self.error(
                    f"Undeclared identifier: {name}"
                )
                return "error"

            return symbol.symbol_type

        if node_type == "Assignment":
            left_type = self.check_expression(
                expression["left"]
            )

            right_type = self.check_expression(
                expression["right"]
            )

            if expression["left"]["type"] != "Identifier":
                self.error(
                    "Left side of assignment must be a variable"
                )
                return "error"

            if (
                left_type != "error"
                and right_type != "error"
                and left_type != right_type
            ):
                self.error(
                    f"Type mismatch in assignment: "
                    f"{left_type} = {right_type}"
                )

            return left_type

        if node_type == "Binary":
            left_type = self.check_expression(
                expression["left"]
            )

            right_type = self.check_expression(
                expression["right"]
            )

            operator = expression["operator"]

            arithmetic = ["+", "-", "*", "/", "%"]
            comparison = [
                "==", "!=", "<", ">", "<=", ">="
            ]

            if operator in arithmetic:
                if left_type != "int" or right_type != "int":
                    self.error(
                        f"Arithmetic operator '{operator}' "
                        f"requires integer operands"
                    )
                    return "error"

                return "int"

            if operator in comparison:
                if left_type == "error" or right_type == "error":
                    return "error"

                if left_type != right_type:
                    self.error(
                        f"Cannot compare {left_type} "
                        f"with {right_type}"
                    )

                return "bool"

        if node_type == "Unary":
            operand_type = self.check_expression(
                expression["operand"]
            )

            if operand_type != "int":
                self.error(
                    "Unary operator requires integer operand"
                )
                return "error"

            return "int"

        if node_type == "Call":
            function = self.symbol_table.lookup(
                expression["name"]
            )

            if function is None:
                self.error(
                    f"Undefined function: "
                    f"{expression['name']}"
                )

            for argument in expression["arguments"]:
                self.check_expression(argument)

            return "int"

        return "error"
