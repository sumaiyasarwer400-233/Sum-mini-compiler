class Optimizer:
    def optimize(self, instructions):
        result = self.constant_folding(instructions)
        result = self.common_subexpression_elimination(result)
        return result

    def constant_folding(self, instructions):
        optimized = []

        for instruction in instructions:
            parts = instruction.split()

            if len(parts) == 5 and parts[1] == "=":
                left = parts[0]
                value1 = parts[2]
                operator = parts[3]
                value2 = parts[4]

                if self.is_number(value1) and self.is_number(value2):
                    a = int(value1)
                    b = int(value2)

                    try:
                        if operator == "+":
                            value = a + b
                        elif operator == "-":
                            value = a - b
                        elif operator == "*":
                            value = a * b
                        elif operator == "/":
                            if b == 0:
                                optimized.append(instruction)
                                continue
                            value = a // b
                        elif operator == "%":
                            if b == 0:
                                optimized.append(instruction)
                                continue
                            value = a % b
                        else:
                            optimized.append(instruction)
                            continue

                        optimized.append(
                            f"{left} = {value}"
                        )
                        continue

                    except Exception:
                        pass

            optimized.append(instruction)

        return optimized

    def common_subexpression_elimination(
        self,
        instructions
    ):
        optimized = []
        expressions = {}

        for instruction in instructions:
            parts = instruction.split()

            if len(parts) == 5 and parts[1] == "=":
                result_name = parts[0]
                left = parts[2]
                operator = parts[3]
                right = parts[4]

                expression = (
                    left,
                    operator,
                    right
                )

                if expression in expressions:
                    previous_result = expressions[expression]

                    optimized.append(
                        f"{result_name} = "
                        f"{previous_result}"
                    )
                    continue

                expressions[expression] = result_name

            optimized.append(instruction)

        return optimized

    @staticmethod
    def is_number(value):
        try:
            int(value)
            return True
        except ValueError:
            return False
