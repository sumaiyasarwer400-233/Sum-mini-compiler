class ASTNode:
    """Base class for all AST nodes."""

    def __init__(self, line=0, column=0):
        self.line = line
        self.column = column


class Program(ASTNode):
    def __init__(self, declarations, line=0, column=0):
        super().__init__(line, column)
        self.declarations = declarations


class Block(ASTNode):
    def __init__(self, statements, line=0, column=0):
        super().__init__(line, column)
        self.statements = statements


class VariableDeclaration(ASTNode):
    def __init__(self, var_type, name, line=0, column=0):
        super().__init__(line, column)
        self.var_type = var_type
        self.name = name


class ArrayDeclaration(ASTNode):
    def __init__(self, element_type, name, size, line=0, column=0):
        super().__init__(line, column)
        self.element_type = element_type
        self.name = name
        self.size = size


class FunctionDeclaration(ASTNode):
    def __init__(
        self,
        name,
        parameters,
        body,
        return_type="int",
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_type = return_type


class Parameter(ASTNode):
    def __init__(self, param_type, name, line=0, column=0):
        super().__init__(line, column)
        self.param_type = param_type
        self.name = name


class IfStatement(ASTNode):
    def __init__(
        self,
        condition,
        then_branch,
        else_branch=None,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class WhileStatement(ASTNode):
    def __init__(
        self,
        condition,
        body,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.condition = condition
        self.body = body


class SwitchStatement(ASTNode):
    def __init__(
        self,
        expression,
        cases,
        default_case=None,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.expression = expression
        self.cases = cases
        self.default_case = default_case


class CaseStatement(ASTNode):
    def __init__(
        self,
        value,
        statements,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.value = value
        self.statements = statements


class BreakStatement(ASTNode):
    def __init__(self, line=0, column=0):
        super().__init__(line, column)


class ReturnStatement(ASTNode):
    def __init__(self, expression=None, line=0, column=0):
        super().__init__(line, column)
        self.expression = expression


class Assignment(ASTNode):
    def __init__(
        self,
        target,
        expression,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.target = target
        self.expression = expression


class ArrayAccess(ASTNode):
    def __init__(
        self,
        name,
        index,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.name = name
        self.index = index


class ExpressionStatement(ASTNode):
    def __init__(self, expression, line=0, column=0):
        super().__init__(line, column)
        self.expression = expression


class BinaryExpression(ASTNode):
    def __init__(
        self,
        left,
        operator,
        right,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpression(ASTNode):
    def __init__(
        self,
        operator,
        operand,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand


class NumberLiteral(ASTNode):
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class StringLiteral(ASTNode):
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class BooleanLiteral(ASTNode):
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class Identifier(ASTNode):
    def __init__(self, name, line=0, column=0):
        super().__init__(line, column)
        self.name = name


class FunctionCall(ASTNode):
    def __init__(
        self,
        name,
        arguments,
        line=0,
        column=0
    ):
        super().__init__(line, column)
        self.name = name
        self.arguments = arguments
