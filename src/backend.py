class StackMachineBackend:
    """
    Converts Three-Address Code (TAC)
    into simple stack-machine instructions.
    """

    def __init__(self, tac_code):
        self.tac_code = tac_code
        self.instructions = []
        self.variables = set()

    def generate(self):
        self.instructions = []
        self.variables = set()

        for line in self.tac_code:
            line = line.strip()

            if not line:
                continue

            # Label
            if line.endswith(":"):
                self.instructions.append(line)
                continue

            # goto LABEL
            if line.startswith("goto "):
                label = line[5:].strip()
                self.instructions.append(f"JMP {label}")
                continue

            # if condition goto LABEL
            if line.startswith("if "):
                parts = line.split()

                if len(parts) >= 5 and parts[-2] == "goto":
                    left = parts[1]
                    operator = parts[2]
                    right = parts[3]
                    label = parts[4]

                    self.load_value(left)
                    self.load_value(right)

                    self.instructions.append(
                        f"CMP_{self.operator_name(operator)}"
                    )
                    self.instructions.append(f"JMP_IF_TRUE {label}")

                continue

            # return value
            if line.startswith("return "):
                value = line[7:].strip()
                self.load_value(value)
                self.instructions.append("RETURN")
                continue

            # x = value
            if "=" in line:
                left, right = line.split("=", 1)
                left = left.strip()
                right = right.strip()

                # Binary operation
                parts = right.split()

                if len(parts) == 3:
                    operand1 = parts[0]
                    operator = parts[1]
                    operand2 = parts[2]

                    self.load_value(operand1)
                    self.load_value(operand2)

                    self.instructions.append(
                        self.operation_instruction(operator)
                    )

                    self.instructions.append(
                        f"STORE {left}"
                    )

                    self.variables.add(left)
                    continue

                # Simple assignment
                self.load_value(right)

                self.instructions.append(
                    f"STORE {left}"
                )

                self.variables.add(left)

                continue

        return self.instructions

    # ---------------------------------------------------------
    # LOAD VALUE
    # ---------------------------------------------------------
    def load_value(self, value):
        value = value.strip()

        if value.isdigit() or (
            value.startswith("-") and value[1:].isdigit()
        ):
            self.instructions.append(f"PUSH {value}")

        elif value in {"true", "True"}:
            self.instructions.append("PUSH 1")

        elif value in {"false", "False"}:
            self.instructions.append("PUSH 0")

        elif value.startswith('"') and value.endswith('"'):
            self.instructions.append(f"PUSH {value}")

        else:
            self.instructions.append(f"LOAD {value}")
            self.variables.add(value)

    # ---------------------------------------------------------
    # OPERATOR TO MACHINE INSTRUCTION
    # ---------------------------------------------------------
    def operation_instruction(self, operator):
        operations = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "%": "MOD",
            "==": "CMP_EQ",
            "!=": "CMP_NE",
            "<": "CMP_LT",
            ">": "CMP_GT",
            "<=": "CMP_LE",
            ">=": "CMP_GE",
            "&&": "AND",
            "||": "OR",
        }

        return operations.get(operator, "UNKNOWN_OP")

    # ---------------------------------------------------------
    # OPERATOR NAME
    # ---------------------------------------------------------
    def operator_name(self, operator):
        names = {
            "==": "EQ",
            "!=": "NE",
            "<": "LT",
            ">": "GT",
            "<=": "LE",
            ">=": "GE",
        }

        return names.get(operator, "UNKNOWN")

    # ---------------------------------------------------------
    # PRINT BACKEND CODE
    # ---------------------------------------------------------
    def print_code(self):
        print("\n===== STACK MACHINE CODE =====")

        for instruction in self.instructions:
            print(instruction)

        print("==============================")
