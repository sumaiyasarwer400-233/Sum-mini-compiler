import re


class Optimizer:
    """
    MiniLang TAC Optimizer.

    Implemented optimizations:
    1. Constant Folding
    2. Common Subexpression Elimination (CSE)

    The optimizer works directly on TAC.
    """

    def __init__(self):
        self.changes = []

    # ==================================================
    # Main optimization pipeline
    # ==================================================

    def optimize(self, tac_code):
        """
        Apply both optimizations.

        Order:
            TAC
             ↓
        Constant Folding
             ↓
        CSE
             ↓
        Optimized TAC
        """

        self.changes = []

        folded_code = self.constant_folding(tac_code)

        optimized_code = self.common_subexpression_elimination(
            folded_code
        )

        return optimized_code

    # ==================================================
    # 1. Constant Folding
    # ==================================================

    def constant_folding(self, tac_code):
        optimized = []

        pattern = re.compile(
            r"^(\w+)\s*=\s*(-?\d+)\s*"
            r"([+\-*/%])\s*(-?\d+)$"
        )

        for instruction in tac_code:

            match = pattern.match(
                instruction.strip()
            )

            if not match:
                optimized.append(instruction)
                continue

            target = match.group(1)
            left = int(match.group(2))
            operator = match.group(3)
            right = int(match.group(4))

            try:
                result = self.calculate(
                    left,
                    operator,
                    right
                )

                new_instruction = (
                    f"{target} = {result}"
                )

                optimized.append(new_instruction)

                self.changes.append(
                    "Constant Folding: "
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

            except ZeroDivisionError:
                # Do not optimize division by zero.
                optimized.append(instruction)

        return optimized

    # ==================================================
    # Constant calculation
    # ==================================================

    def calculate(self, left, operator, right):

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

    # ==================================================
    # 2. Common Subexpression Elimination
    # ==================================================

    def common_subexpression_elimination(
        self,
        tac_code
    ):
        optimized = []

        expression_table = {}

        binary_pattern = re.compile(
            r"^(\w+)\s*=\s*"
            r"(\w+|-?\d+)\s+"
            r"([+\-*/%])\s+"
            r"(\w+|-?\d+)$"
        )

        for instruction in tac_code:

            match = binary_pattern.match(
                instruction.strip()
            )

            if not match:
                optimized.append(instruction)
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

            # Check exact expression.
            if expression_key in expression_table:

                old_temp = expression_table[
                    expression_key
                ]

                new_instruction = (
                    f"{target} = {old_temp}"
                )

                optimized.append(
                    new_instruction
                )

                self.changes.append(
                    "CSE: "
                    f"{instruction} -> "
                    f"{new_instruction}"
                )

            else:

                expression_table[
                    expression_key
                ] = target

                optimized.append(
                    instruction
                )

        return optimized

    # ==================================================
    # Show optimization report
    # ==================================================

    def print_comparison(
        self,
        before,
        after
    ):
        print("\n" + "=" * 55)
        print("TAC OPTIMIZATION")
        print("=" * 55)

        print("\nBEFORE OPTIMIZATION:")

        if before:
            for index, instruction in enumerate(
                before,
                start=1
            ):
                print(
                    f"{index:03}: {instruction}"
                )
        else:
            print("(empty)")

        print("\nAFTER OPTIMIZATION:")

        if after:
            for index, instruction in enumerate(
                after,
                start=1
            ):
                print(
                    f"{index:03}: {instruction}"
                )
        else:
            print("(empty)")

        print("\nOPTIMIZATION CHANGES:")

        if not self.changes:
            print("No optimization applied.")

        else:
            for change in self.changes:
                print("-", change)

        print("=" * 55)

    # ==================================================
    # Convenience method
    # ==================================================

    def constant_fold(self, expression):
        """
        Compatibility helper.

        If an expression contains only integer constants,
        evaluate it.
        """

        if not isinstance(expression, str):
            return expression

        match = re.match(
            r"^\s*(-?\d+)\s*"
            r"([+\-*/%])\s*"
            r"(-?\d+)\s*$",
            expression
        )

        if not match:
            return expression

        left = int(match.group(1))
        operator = match.group(2)
        right = int(match.group(3))

        try:
            return self.calculate(
                left,
                operator,
                right
            )
        except ZeroDivisionError:
            return expression
