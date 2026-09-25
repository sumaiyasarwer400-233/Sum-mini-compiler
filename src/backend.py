class StackMachineBackend:
    """
    MiniLang Stack Machine Backend.

    Converts TAC into simple stack-machine instructions.

    Supported:
    - Constants
    - Variables
    - Arithmetic
    - Comparisons
    - Assignment
    - Labels
    - GOTO
    - Conditional GOTO
    - Parameters
    - Function CALL
    - RETURN
    - Struct member access
    """

    def __init__(self, tac_code):
        self.tac_code = tac_code
        self.instructions = []

    # ==================================================
    # Main generation
    # ==================================================

    def generate(self):
        self.instructions = []

        for tac in self.tac_code:
            tac = tac.strip()

            if not tac:
                continue

            # Comments
            if tac.startswith("#"):
                self.instructions.append(
                    f"; {tac[1:].strip()}"
                )
                continue

            # Label
            if tac.startswith("label "):
                label = tac[6:].strip()

                self.instructions.append(
                    f"LABEL {label}"
                )
                continue

            # GOTO
            if tac.startswith("goto "):
                label = tac[5:].strip()

                self.instructions.append(
                    f"GOTO {label}"
                )
                continue

            # Conditional GOTO
            if tac.startswith("ifFalse "):
                parts = tac.split()

                if len(parts) >= 4:
                    condition = parts[1]
                    label = parts[3]

                    self.instructions.append(
                        f"LOAD {condition}"
                    )
                    self.instructions.append(
                        f"JZ {label}"
                    )

                continue

            # PARAM
            if tac.startswith("param "):
                value = tac[6:].strip()

                self.instructions.append(
                    f"LOAD {value}"
                )
                self.instructions.append(
                    "PARAM"
                )

                continue

            # RETURN
            if tac == "return":
                self.instructions.append(
                    "RETURN"
                )
                continue

            if tac.startswith("return "):
                value = tac[7:].strip()

                self.instructions.append(
                    f"LOAD {value}"
                )
                self.instructions.append(
                    "RETURN"
                )

                continue

            # Function call
            if "= call " in tac:
                self.translate_call(tac)
                continue

            # Assignment
            if "=" in tac:
                self.translate_assignment(tac)
                continue

        return self.instructions

    # ==================================================
    # Function call
    # ==================================================

    def translate_call(self, tac):
        left, right = tac.split("=", 1)

        target = left.strip()
        right = right.strip()

        if not right.startswith("call "):
            return

        call_data = right[5:].strip()

        parts = call_data.split(",")

        function_name = parts[0].strip()

        argument_count = 0

        if len(parts) > 1:
            try:
                argument_count = int(
                    parts[1].strip()
                )
            except ValueError:
                argument_count = 0

        self.instructions.append(
            f"CALL {function_name} {argument_count}"
        )

        self.instructions.append(
            f"STORE {target}"
        )

    # ==================================================
    # Assignment
    # ==================================================

    def translate_assignment(self, tac):
        left, right = tac.split("=", 1)

        target = left.strip()
        expression = right.strip()

        # Unary expression
        if (
            expression.startswith("-")
            and self.is_value(
                expression[1:].strip()
            )
        ):
            operand = expression[1:].strip()

            self.instructions.append(
                f"LOAD {operand}"
            )

            self.instructions.append(
                "NEG"
            )

            self.instructions.append(
                f"STORE {target}"
            )

            return

        if (
            expression.startswith("!")
            and self.is_value(
                expression[1:].strip()
            )
        ):
            operand = expression[1:].strip()

            self.instructions.append(
                f"LOAD {operand}"
            )

            self.instructions.append(
                "NOT"
            )

            self.instructions.append(
                f"STORE {target}"
            )

            return

        # Binary expression
        parts = expression.split()

        if len(parts) == 3:
            left_operand = parts[0]
            operator = parts[1]
            right_operand = parts[2]

            self.instructions.append(
                f"LOAD {left_operand}"
            )

            self.instructions.append(
                f"LOAD {right_operand}"
            )

            operation = self.operator_instruction(
                operator
            )

            self.instructions.append(
                operation
            )

            self.instructions.append(
                f"STORE {target}"
            )

            return

        # Simple assignment
        self.instructions.append(
            f"LOAD {expression}"
        )

        self.instructions.append(
            f"STORE {target}"
        )

    # ==================================================
    # Operators
    # ==================================================

    def operator_instruction(self, operator):

        mapping = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "%": "MOD",
            "==": "EQ",
            "!=": "NE",
            "<": "LT",
            ">": "GT",
            "<=": "LE",
            ">=": "GE",
            "&&": "AND",
            "||": "OR",
        }

        return mapping.get(
            operator,
            f"OP {operator}"
        )

    # ==================================================
    # Value checking
    # ==================================================

    def is_value(self, value):
        value = value.strip()

        if not value:
            return False

        # Integer
        try:
            int(value)
            return True
        except ValueError:
            pass

        # String literal
        if (
            len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        ):
            return True

        # Boolean
        if value in {"0", "1"}:
            return True

        # Variable / temporary / struct member
        if value.replace("_", "").replace(".", "").isalnum():
            return True

        return False

    # ==================================================
    # Print generated backend code
    # ==================================================

    def print_code(self):
        print("\nStack Machine Code:")

        if not self.instructions:
            print("(empty)")
            return

        for index, instruction in enumerate(
            self.instructions,
            start=1
        ):
            print(
                f"{index:03}: {instruction}"
            )
