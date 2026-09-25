class StackMachineInterpreter:
    """
    Small interpreter for MiniLang stack-machine code.
    """

    def __init__(self, instructions):
        self.instructions = instructions
        self.stack = []
        self.variables = {}
        self.labels = {}
        self.ip = 0
        self.return_value = None

        self.build_labels()

    # ---------------------------------------------------------
    # BUILD LABEL TABLE
    # ---------------------------------------------------------
    def build_labels(self):
        self.labels = {}

        for index, instruction in enumerate(self.instructions):
            instruction = instruction.strip()

            if instruction.endswith(":"):
                label = instruction[:-1]
                self.labels[label] = index

    # ---------------------------------------------------------
    # GET VALUE
    # ---------------------------------------------------------
    def get_value(self, value):
        value = value.strip()

        if value.isdigit():
            return int(value)

        if value.startswith("-") and value[1:].isdigit():
            return int(value)

        if value == "true" or value == "True":
            return 1

        if value == "false" or value == "False":
            return 0

        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]

        return self.variables.get(value, 0)

    # ---------------------------------------------------------
    # RUN PROGRAM
    # ---------------------------------------------------------
    def run(self):
        self.ip = 0
        self.stack = []
        self.return_value = None

        while self.ip < len(self.instructions):

            instruction = self.instructions[self.ip].strip()

            # Empty instruction
            if not instruction:
                self.ip += 1
                continue

            # Label
            if instruction.endswith(":"):
                self.ip += 1
                continue

            parts = instruction.split()
            operation = parts[0]

            # -------------------------------------------------
            # PUSH
            # -------------------------------------------------
            if operation == "PUSH":
                value_text = instruction[5:].strip()
                self.stack.append(self.get_value(value_text))

            # -------------------------------------------------
            # LOAD
            # -------------------------------------------------
            elif operation == "LOAD":
                variable = parts[1]
                value = self.variables.get(variable, 0)
                self.stack.append(value)

            # -------------------------------------------------
            # STORE
            # -------------------------------------------------
            elif operation == "STORE":
                variable = parts[1]

                if not self.stack:
                    raise RuntimeError(
                        f"Stack underflow while storing '{variable}'."
                    )

                value = self.stack.pop()
                self.variables[variable] = value

            # -------------------------------------------------
            # ADD
            # -------------------------------------------------
            elif operation == "ADD":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left + right)

            # -------------------------------------------------
            # SUB
            # -------------------------------------------------
            elif operation == "SUB":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left - right)

            # -------------------------------------------------
            # MUL
            # -------------------------------------------------
            elif operation == "MUL":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left * right)

            # -------------------------------------------------
            # DIV
            # -------------------------------------------------
            elif operation == "DIV":
                right = self.stack.pop()
                left = self.stack.pop()

                if right == 0:
                    raise RuntimeError(
                        "Division by zero."
                    )

                self.stack.append(left // right)

            # -------------------------------------------------
            # MOD
            # -------------------------------------------------
            elif operation == "MOD":
                right = self.stack.pop()
                left = self.stack.pop()

                if right == 0:
                    raise RuntimeError(
                        "Modulo by zero."
                    )

                self.stack.append(left % right)

            # -------------------------------------------------
            # COMPARISON
            # -------------------------------------------------
            elif operation == "CMP_EQ":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(left == right))

            elif operation == "CMP_NE":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(left != right))

            elif operation == "CMP_LT":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(left < right))

            elif operation == "CMP_GT":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(left > right))

            elif operation == "CMP_LE":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(left <= right))

            elif operation == "CMP_GE":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(left >= right))

            # -------------------------------------------------
            # LOGICAL OPERATIONS
            # -------------------------------------------------
            elif operation == "AND":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(bool(left) and bool(right)))

            elif operation == "OR":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(int(bool(left) or bool(right)))

            # -------------------------------------------------
            # CONDITIONAL JUMP
            # -------------------------------------------------
            elif operation == "JMP_IF_TRUE":
                label = parts[1]

                if not self.stack:
                    raise RuntimeError(
                        "Stack underflow during conditional jump."
                    )

                condition = self.stack.pop()

                if condition:
                    if label not in self.labels:
                        raise RuntimeError(
                            f"Unknown label '{label}'."
                        )

                    self.ip = self.labels[label]
                    continue

            # -------------------------------------------------
            # UNCONDITIONAL JUMP
            # -------------------------------------------------
            elif operation == "JMP":
                label = parts[1]

                if label not in self.labels:
                    raise RuntimeError(
                        f"Unknown label '{label}'."
                    )

                self.ip = self.labels[label]
                continue

            # -------------------------------------------------
            # RETURN
            # -------------------------------------------------
            elif operation == "RETURN":
                if self.stack:
                    self.return_value = self.stack.pop()
                else:
                    self.return_value = None

                return self.return_value

            # -------------------------------------------------
            # UNKNOWN INSTRUCTION
            # -------------------------------------------------
            else:
                raise RuntimeError(
                    f"Unknown instruction: {instruction}"
                )

            self.ip += 1

        return self.return_value

    # ---------------------------------------------------------
    # PRINT FINAL STATE
    # ---------------------------------------------------------
    def print_state(self):
        print("\n===== INTERPRETER RESULT =====")

        print("Variables:")

        if not self.variables:
            print("  No variables.")
        else:
            for name, value in self.variables.items():
                print(f"  {name} = {value}")

        print(f"Return value: {self.return_value}")

        print("==============================")
