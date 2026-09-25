class Optimizer:

    # ---------------- CONSTANT FOLDING ----------------

    def constant_folding(self, code):

        optimized = []

        for instruction in code:

            if (
                len(instruction) == 5
                and instruction[0] == "BIN"
            ):

                temp = instruction[1]
                operator = instruction[2]
                left = instruction[3]
                right = instruction[4]

                try:

                    left_value = self.to_value(left)
                    right_value = self.to_value(right)

                    if (
                        left_value is not None
                        and right_value is not None
                    ):

                        result = self.calculate(
                            left_value,
                            operator,
                            right_value
                        )

                        optimized.append(
                            ("MOV", temp, str(result))
                        )

                        continue

                except Exception:
                    pass

            optimized.append(instruction)

        return optimized

    # ---------------- COMMON SUBEXPRESSION ----------------

    def common_subexpression_elimination(
        self,
        code
    ):

        optimized = []
        expressions = {}

        for instruction in code:

            if (
                len(instruction) == 5
                and instruction[0] == "BIN"
            ):

                temp = instruction[1]
                operator = instruction[2]
                left = instruction[3]
                right = instruction[4]

                key = (
                    operator,
                    left,
                    right
                )

                if key in expressions:

                    old_temp = expressions[key]

                    optimized.append(
                        (
                            "MOV",
                            temp,
                            old_temp
                        )
                    )

                    continue

                expressions[key] = temp

            optimized.append(instruction)

        return optimized

    # ---------------- VALUE CONVERSION ----------------

    def to_value(self, value):

        if isinstance(value, str):

            if (
                value.startswith("'")
                and value.endswith("'")
            ):
                return value[1:-1]

            try:

                if "." in value:
                    return float(value)

                return int(value)

            except ValueError:
                return None

        if isinstance(value, (int, float)):
            return value

        return None

    # ---------------- CALCULATION ----------------

    def calculate(
        self,
        left,
        operator,
        right
    ):

        if operator == "+":
            return left + right

        if operator == "-":
            return left - right

        if operator == "*":
            return left * right

        if operator == "/":
            return left / right

        if operator == "%":
            return left % right

        if operator == "==":
            return left == right

        if operator == "!=":
            return left != right

        if operator == "<":
            return left < right

        if operator == ">":
            return left > right

        if operator == "<=":
            return left <= right

        if operator == ">=":
            return left >= right

        return None

    # ---------------- OPTIMIZE ----------------

    def optimize(self, code):

        code = self.constant_folding(code)

        code = self.common_subexpression_elimination(
            code
        )

        return code


def optimize_tac(code):

    optimizer = Optimizer()

    return optimizer.optimize(code)
