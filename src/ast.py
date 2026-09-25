class ASTNode:
    def __init__(self, node_type, **attributes):
        self.node_type = node_type
        self.attributes = attributes

    def __repr__(self):
        return self._format()

    def _format(self, level=0):
        space = "  " * level
        result = f"{space}{self.node_type}"

        for key, value in self.attributes.items():
            result += f"\n{space}  {key}:"

            if isinstance(value, ASTNode):
                result += "\n" + value._format(level + 2)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ASTNode):
                        result += "\n" + item._format(level + 2)
                    else:
                        result += f"\n{space}    {item}"

            else:
                result += f" {value}"

        return result


class Program(ASTNode):
    def __init__(self, statements):
        super().__init__(
            "Program",
            statements=statements
        )


class Function(ASTNode):
    def __init__(self, name, parameters, body):
        super().__init__(
            "Function",
            name=name,
            parameters=parameters,
            body=body
        )


class Block(ASTNode):
    def __init__(self, statements):
        super().__init__(
            "Block",
            statements=statements
        )


class Number(ASTNode):
    def __init__(self, value):
        super().__init__(
            "Number",
            value=value
        )


class Boolean(ASTNode):
    def __init__(self, value):
        super().__init__(
            "Boolean",
            value=value
        )


class Identifier(ASTNode):
    def __init__(self, name):
        super().__init__(
            "Identifier",
            name=name
        )


class BinaryExpression(ASTNode):
    def __init__(self, operator, left, right):
        super().__init__(
            "BinaryExpression",
            operator=operator,
            left=left,
            right=right
        )


class UnaryExpression(ASTNode):
    def __init__(self, operator, operand):
        super().__init__(
            "UnaryExpression",
            operator=operator,
            operand=operand
        )


class Assignment(ASTNode):
    def __init__(self, left, right):
        super().__init__(
            "Assignment",
            left=left,
            right=right
        )


class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        super().__init__(
            "IfStatement",
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )


class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        super().__init__(
            "WhileStatement",
            condition=condition,
            body=body
        )


class ForStatement(ASTNode):
    def __init__(self, initialization, condition, update, body):
        super().__init__(
            "ForStatement",
            initialization=initialization,
            condition=condition,
            update=update,
            body=body
        )


class ReturnStatement(ASTNode):
    def __init__(self, value):
        super().__init__(
            "ReturnStatement",
            value=value
        )


class BreakStatement(ASTNode):
    def __init__(self):
        super().__init__("BreakStatement")


class ContinueStatement(ASTNode):
    def __init__(self):
        super().__init__("ContinueStatement")


class CallExpression(ASTNode):
    def __init__(self, name, arguments):
        super().__init__(
            "CallExpression",
            name=name,
            arguments=arguments
        )


class ExpressionStatement(ASTNode):
    def __init__(self, expression):
        super().__init__(
            "ExpressionStatement",
            expression=expression
        )
