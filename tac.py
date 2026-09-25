class TACGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, program):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

        for statement in program["statements"]:
            self.generate_statement(statement)

        return self.instructions

    def generate_statement(self, statement):
        node_type = statement["type"]

        if node_type == "Function":
            self.emit(f"FUNCTION {statement['name']}")

            self.generate_statement(
                statement["body"]
            )

            self.emit("END_FUNCTION")
            return

        if node_type == "Block":
            for item in statement["statements"]:
                self.generate_statement(item)
            return

        if node_type == "ExpressionStatement":
            self.generate_expression(
                statement["expression"]
            )
            return

        if node_type == "Return":
            value = self.generate_expression(
                statement["value"]
            )

            self.emit(f"RETURN {value}")
            return

        if node_type == "If":
            condition = self.generate_expression(
                statement["condition"]
            )

            else_label = self.new_label()
            end_label = self.new_label()

            self.emit(
                f"IF_FALSE {condition} GOTO {else_label}"
            )

            self.generate_statement(
                statement["then"]
            )

            self.emit(
                f"GOTO {end_label}"
            )

            self.emit(
                f"LABEL {else_label}"
            )

            if statement["else"] is not None:
                self.generate_statement(
                    statement["else"]
                )

            self.emit(
                f"LABEL {end_label}"
            )
            return

        if node_type == "While":
            start_label = self.new_label()
            end_label = self.new_label()

            self.emit(
                f"LABEL {start_label}"
            )

            condition = self.generate_expression(
                statement["condition"]
            )

            self.emit(
                f"IF_FALSE {condition} GOTO {end_label}"
            )

            self.generate_statement(
                statement["body"]
            )

            self.emit(
                f"GOTO {start_label}"
            )

            self.emit(
                f"LABEL {end_label}"
            )
            return

        if node_type == "For":
            if statement["initialization"]:
                self.generate_expression(
                    statement["initialization"]
                )

            start_label = self.new_label()
            end_label = self.new_label()

            self.emit(
                f"LABEL {start_label}"
            )

            if statement["condition"]:
                condition = self.generate_expression(
                    statement["condition"]
                )

                self.emit(
                    f"IF_FALSE {condition} "
                    f"GOTO {end_label}"
                )

            self.generate_statement(
                statement["body"]
            )

            if statement["update"]:
                self.generate_expression(
                    statement["update"]
                )

            self.emit(
                f"GOTO {start_label}"
            )

            self.emit(
                f"LABEL {end_label}"
            )
            return

        if node_type == "Break":
            self.emit("BREAK")
            return

        if node_type == "Continue":
            self.emit("CONTINUE")
            return

    def generate_expression(self, expression):
        node_type = expression["type"]

        if node_type == "Number":
            return str(expression["value"])

        if node_type == "Boolean":
            return "1" if expression["value"] else "0"

        if node_type == "Identifier":
            return expression["name"]

        if node_type == "Assignment":
            value = self.generate_expression(
                expression["right"]
            )

            name = expression["left"]["name"]

            self.emit(
                f"{name} = {value}"
            )

            return name

        if node_type == "Binary":
            left = self.generate_expression(
                expression["left"]
            )

            right = self.generate_expression(
                expression["right"]
            )

            temp = self.new_temp()

            self.emit(
                f"{temp} = {left} "
                f"{expression['operator']} {right}"
            )

            return temp

        if node_type == "Unary":
            operand = self.generate_expression(
                expression["operand"]
            )

            temp = self.new_temp()

            self.emit(
                f"{temp} = "
                f"{expression['operator']}{operand}"
            )

            return temp

        if node_type == "Call":
            arguments = []

            for argument in expression["arguments"]:
                arguments.append(
                    self.generate_expression(argument)
                )

            for argument in arguments:
                self.emit(f"PARAM {argument}")

            temp = self.new_temp()

            self.emit(
                f"{temp} = CALL "
                f"{expression['name']}, "
                f"{len(arguments)}"
            )

            return temp

        return ""
