class Interpreter:
    def __init__(self):
        self.stack = []
        self.memory = {}
        self.labels = {}
        self.pc = 0

    def prepare_labels(self, code):
        self.labels = {}

        for index, instruction in enumerate(code):
            parts = instruction.split()

            if parts and parts[0] == "LABEL":
                self.labels[parts[1]] = index

    def get_value(self, value):
        if value in self.memory:
            return self.memory[value]

        try:
            return int(value)
        except ValueError:
            return 0

    def run(self, code):
        self.stack = []
        self.memory = {}
        self.pc = 0

        self.prepare_labels(code)

        while self.pc < len(code):
            instruction = code[self.pc]
            parts = instruction.split()

            if not parts:
                self.pc += 1
                continue

            operation = parts[0]

            if operation == "PUSH":
                value = self.get_value(parts[1])
                self.stack.append(value)

            elif operation == "STORE":
                if self.stack:
                    self.memory[parts[1]] = self.stack.pop()

            elif operation == "ADD":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left + right)

            elif operation == "SUB":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left - right)

            elif operation == "MUL":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left * right)

            elif operation == "DIV":
                right = self.stack.pop()
                left = self.stack.pop()

                if right == 0:
                    raise RuntimeError(
                        "Division by zero"
                    )

                self.stack.append(left // right)

            elif operation == "MOD":
                right = self.stack.pop()
                left = self.stack.pop()

                if right == 0:
                    raise RuntimeError(
                        "Modulo by zero"
                    )

                self.stack.append(left % right)

            elif operation == "CMP_EQ":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(
                    1 if left == right else 0
                )

            elif operation == "CMP_NE":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(
                    1 if left != right else 0
                )

            elif operation == "CMP_LT":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(
                    1 if left < right else 0
                )

            elif operation == "CMP_GT":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(
                    1 if left > right else 0
                )

            elif operation == "CMP_LE":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(
                    1 if left <= right else 0
                )

            elif operation == "CMP_GE":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(
                    1 if left >= right else 0
                )

            elif operation == "JUMP":
                self.pc = self.labels[parts[1]]
                continue

            elif operation == "JUMP_IF_FALSE":
                value = self.stack.pop()

                if value == 0:
                    self.pc = self.labels[parts[1]]
                    continue

            elif operation == "RETURN":
                return self.get_value(parts[1])

            elif operation == "LABEL":
                pass

            elif operation == "FUNCTION":
                pass

            elif operation == "END_FUNCTION":
                pass

            elif operation == "PARAM":
                pass

            elif operation == "CALL":
                pass

            elif operation == "BREAK":
                pass

            elif operation == "CONTINUE":
                pass

            self.pc += 1

        if self.stack:
            return self.stack[-1]

        return None
