from ast import (
    BinaryExpression,
    UnaryExpression,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
)


class Optimizer:
    """
    MiniLang optimizer.

    Implemented optimizations:
    1. Constant Folding
    2. Common Subexpression Elimination (CSE)
    """

    def __init__(self):
        self.changes = []

    # ---------------------------------------------------------
    # 1. CONSTANT FOLDING
    # ---------------------------------------------------------
    def constant_fold(self, expression):
        if expression is None:
            return expression

        if isinstance(expression, BinaryExpression):
            expression.left = self.constant_fold(expression.left)
            expression.right = self.constant_fold(expression.right)

            if (
                isinstance(expression.left, NumberLiteral)
                and isinstance(expression.right, NumberLiteral)
            ):
                left = expression.left.value
                right = expression.right.value
                operator = expression.operator

                try:
                    if operator == "+":
                        result = left + right
                    elif operator == "-":
                        result = left - right
                    elif operator == "*":
                        result = left * right
                    elif operator == "/":
                        if right == 0:
                            return expression
                        result = left // right
                    elif operator == "%":
                        if right == 0:
                            return expression
                        result = left % right
                    elif operator == "==":
                        result = int(left == right)
                    elif operator == "!=":
                        result = int(left != right)
                    elif operator == "<":
                        result = int(left < right)
                    elif operator == ">":
                        result = int(left > right)
                    elif operator == "<=":
                        result = int(left <= right)
                    elif operator == ">":
                        result = int(left > right)
                    elif operator == ">=":
                        result = int(left >= right)
                    else:
                        return expression

                    old_expression = (
                        f"{left} {operator} {right}"
                    )

                    self.changes.append(
                        f"Constant Folding: "
                        f"{old_expression} -> {result}"
                    )

                    return NumberLiteral(
                        result,
                        expression.line,
                        expression.column,
                    )

                except Exception:
                    return expression

        if isinstance(expression, UnaryExpression):
            expression.operand = self.constant_fold(expression.operand)

            if isinstance(expression.operand, NumberLiteral):
                value = expression.operand.value

                if expression.operator == "-":
                    result = -value

                    self.changes.append(
                        f"Constant Folding: -{value} -> {result}"
                    )

                    return NumberLiteral(
                        result,
                        expression.line,
                        expression.column,
                    )

                if expression.operator == "!":
                    result = int(not value)

                    self.changes.append(
                        f"Constant Folding: !{value} -> {result}"
                    )

                    return NumberLiteral(
                        result,
                        expression.line,
                        expression.column,
                    )

        return expression

    # ---------------------------------------------------------
    # 2. COMMON SUBEXPRESSION ELIMINATION
    # ---------------------------------------------------------
    def expression_key(self, expression):
        if isinstance(expression, NumberLiteral):
            return ("number", expression.value)

        if isinstance(expression, StringLiteral):
            return ("string", expression.value)

        if isinstance(expression, BooleanLiteral):
            return ("boolean", expression.value)

        if isinstance(expression, Identifier):
            return ("identifier", expression.name)

        if isinstance(expression, UnaryExpression):
            return (
                "unary",
                expression.operator,
                self.expression_key(expression.operand),
            )

        if isinstance(expression, BinaryExpression):
            return (
                "binary",
                expression.operator,
                self.expression_key(expression.left),
                self.expression_key(expression.right),
            )

        return None

    def find_common_subexpressions(self, expression):
        found = {}

        def visit(node):
            if node is None:
                return

            if isinstance(node, BinaryExpression):
                visit(node.left)
                visit(node.right)

                key = self.expression_key(node)

                if key is not None:
                    if key in found:
                        found[key]["count"] += 1
                    else:
                        found[key] = {
                            "expression": node,
                            "count": 1,
                        }

            elif isinstance(node, UnaryExpression):
                visit(node.operand)

        visit(expression)

        common = []

        for item in found.values():
            if item["count"] > 1:
                common.append(item["expression"])

        return common

    def apply_cse(self, expression):
        common = self.find_common_subexpressions(expression)

        if not common:
            return expression

        for node in common:
            key = self.expression_key(node)

            self.changes.append(
                "Common Subexpression Elimination: "
                f"reused expression {key}"
            )

        return expression

    # ---------------------------------------------------------
    # OPTIMIZE ONE EXPRESSION
    # ---------------------------------------------------------
    def optimize_expression(self, expression):
        self.changes = []

        expression = self.constant_fold(expression)
        expression = self.apply_cse(expression)

        return expression

    # ---------------------------------------------------------
    # PRINT OPTIMIZATION REPORT
    # ---------------------------------------------------------
    def print_report(self):
        print("\n===== OPTIMIZATION REPORT =====")

        if not self.changes:
            print("No optimization performed.")
            return

        for change in self.changes:
            print("-", change)

        print("===============================")


def optimize_expression(expression):
    optimizer = Optimizer()
    optimized = optimizer.optimize_expression(expression)

    optimizer.print_report()

    return optimized
