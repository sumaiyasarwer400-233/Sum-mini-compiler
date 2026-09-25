class StackMachine:
    def __init__(self):
        self.code = []

    def generate(self, instructions):
        self.code = []

        for instruction in instructions:
            parts = instruction.split()

            if not parts:
                continue

            # x = value
            if len(parts) == 3 and parts[1] == "=":
                target = parts[0]
                value = parts[2]

                self.code.append(f"PUSH {value}")
                self.code.append(f"STORE {target}")

            # t1 = a + b
            elif len(parts) == 5 and parts[1] == "=":
                target = parts[0]
                left = parts[2]
                operator = parts[3]
                right = parts[4]

                self.code.append(f"PUSH {left}")
                self.code.append(f"PUSH {right}")

                operation = {
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
                    ">=": "CMP_GE"
                }

                if operator in operation:
                    self.code.append(
                        operation[operator]
                    )

                self.code.append(
                    f"STORE {target}"
                )

            elif parts[0] == "LABEL":
                self.code.append(
                    f"LABEL {parts[1]}"
                )

            elif parts[0] == "GOTO":
                self.code.append(
                    f"JUMP {parts[1]}"
                )

            elif parts[0] == "IF_FALSE":
                condition = parts[1]
                label = parts[3]

                self.code.append(
                    f"PUSH {condition}"
                )
                self.code.append(
                    f"JUMP_IF_FALSE {label}"
                )

            elif parts[0] == "RETURN":
                self.code.append(
                    f"RETURN {parts[1]}"
                )

            elif parts[0] == "PARAM":
                self.code.append(
                    f"PUSH {parts[1]}"
                )

            elif parts[0] == "CALL":
                self.code.append(instruction)

            elif "CALL" in instruction:
                self.code.append(instruction)

            elif parts[0] == "FUNCTION":
                self.code.append(instruction)

            elif parts[0] == "END_FUNCTION":
                self.code.append(instruction)

            elif parts[0] == "BREAK":
                self.code.append("BREAK")

            elif parts[0] == "CONTINUE":
                self.code.append("CONTINUE")

        return self.code
