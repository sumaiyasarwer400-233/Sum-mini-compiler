import re


class Optimizer:
    def __init__(self):
        self.changes = []

    def optimize(self, tac_code):
        self.changes = []

        folded_code = self.constant_folding(
            tac_code
        )

        optimized_code = (
            self.common_subexpression_elimination(
                folded_code
            )
        )

        return optimized_code

    # -------------------------------------------------
    # CONSTANT FOLDING
    # -------------------------------------------------

    def constant_folding(self, tac_code):

        optimized = []

        pattern = re.compile(
            r"^(\w+)\s*=\s*"
            r"(-?\d+)\s*"
            r"([+\-*/%])\s*"
            r"(-?\d+)$"
        )

        for instruction in tac_code:

            match = pattern.match(
                instruction.strip()
            )

            if not match:

                optimized.append(
                    instruction
                )

                continue

            target = match.group(1)

            left = int(
                match.group(2)
            )

            operator = match.group(3)

            right = int(
                match.group(4)
            )

            try:

                result = self.calculate(
                    left,
                    operator,
                    right
                )

                new_instruction = (
                    f"{target} = {result}"
                )

                optimized.append(
                    new_instruction
                )

                self.changes.append(
                    f"Constant Folding: "
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

            except ZeroDivisionError:

                optimized.append(
                    instruction
                )

        return optimized

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

            if right == 0:
                raise ZeroDivisionError

            return left // right

        if operator == "%":

            if right == 0:
                raise ZeroDivisionError

            return left % right

        raise ValueError(
            f"Unknown operator: {operator}"
        )

    # -------------------------------------------------
    # COMMON SUBEXPRESSION ELIMINATION
    # -------------------------------------------------

    def common_subexpression_elimination(
        self,
        tac_code
    ):

        optimized = []

        expression_table = {}

        binary_pattern = re.compile(
            r"^(\w+)\s*=\s*"
            r"(\w+|-?\d+)\s*"
            r"([+\-*/%])\s*"
            r"(\w+|-?\d+)$"
        )

        for instruction in tac_code:

            match = binary_pattern.match(
                instruction.strip()
            )

            if not match:

                optimized.append(
                    instruction
                )

                continue

            target = match.group(1)

            left = match.group(2)

            operator = match.group(3)

            right = match.group(4)

            expression_key = (
                left,
                operator,
                right
            )

            if expression_key in expression_table:

                old_temp = (
                    expression_table[
                        expression_key
                    ]
                )

                new_instruction = (
                    f"{target} = {old_temp}"
                )

                optimized.append(
                    new_instruction
                )

                self.changes.append(
                    f"CSE: {instruction} "
                    f"-> {new_instruction}"
                )

            else:

                expression_table[
                    expression_key
                ] = target

                optimized.append(
                    instruction
                )

        return optimized

    # -------------------------------------------------
    # DISPLAY BEFORE / AFTER
    # -------------------------------------------------

    def print_comparison(
        self,
        before,
        after
    ):

        print(
            "\n" + "=" * 55
        )

        print(
            "TAC OPTIMIZATION"
        )

        print(
            "=" * 55
        )

        print(
            "\nBEFORE OPTIMIZATION:"
        )

        if before:

            for index, instruction in enumerate(
                before,
                start=1
            ):

                print(
                    f"{index:03}: "
                    f"{instruction}"
                )

        else:

            print("(empty)")

        print(
            "\nAFTER OPTIMIZATION:"
        )

        if after:

            for index, instruction in enumerate(
                after,
                start=1
            ):

                print(
                    f"{index:03}: "
                    f"{instruction}"
                )

        else:

            print("(empty)")

        print(
            "\nOPTIMIZATION CHANGES:"
        )

        if not self.changes:

            print(
                "No optimization applied."
            )

        else:

            for change in self.changes:

                print(
                    "-",
                    change
                )

        print(
            "=" * 55
        )

    # -------------------------------------------------
    # SIMPLE EXPRESSION FOLDING
    # -------------------------------------------------

    def constant_fold(self, expression):

        if not isinstance(
            expression,
            str
        ):

            return expression

        match = re.match(
            r"^\s*(-?\d+)\s*"
            r"([+\-*/%])\s*"
            r"(-?\d+)\s*$",
            expression
        )

        if not match:

            return expression

        left = int(
            match.group(1)
        )

        operator = match.group(2)

        right = int(
            match.group(3)
        )

        try:

            return self.calculate(
                left,
                operator,
                right
            )

        except ZeroDivisionError:

            return expression
