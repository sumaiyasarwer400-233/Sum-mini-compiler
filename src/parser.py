from ast import (
    Program,
    Block,
    VariableDeclaration,
    ArrayDeclaration,
    FunctionDeclaration,
    Parameter,
    IfStatement,
    WhileStatement,
    SwitchStatement,
    CaseStatement,
    BreakStatement,
    ReturnStatement,
    Assignment,
    ArrayAccess,
    ExpressionStatement,
    BinaryExpression,
    UnaryExpression,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    FunctionCall,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current(self):
        return self.tokens[self.position]

    def peek(self, offset=1):
        index = self.position + offset

        if index >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[index]

    def advance(self):
        token = self.current()

        if self.position < len(self.tokens) - 1:
            self.position += 1

        return token

    def check(self, token_type, value=None):
        token = self.current()

        if token.token_type != token_type:
            return False

        if value is not None and token.value != value:
            return False

        return True

    def match(self, token_type, value=None):
        if self.check(token_type, value):
            return self.advance()

        return None

    def expect(self, token_type, value=None):
        if self.check(token_type, value):
            return self.advance()

        token = self.current()

        expected = value if value is not None else token_type

        self.errors.append(
            f"Syntax Error at line {token.line}, "
            f"column {token.column}: "
            f"Expected '{expected}', "
            f"found '{token.value}'."
        )

        return None

    def parse(self):
        declarations = []

        while not self.check("EOF"):
            declaration = self.parse_declaration()

            if declaration is not None:
                declarations.append(declaration)
            else:
                if not self.check("EOF"):
                    self.advance()

        return Program(declarations)

    # -------------------------------------------------
    # Declarations
    # -------------------------------------------------

    def parse_declaration(self):
        if self.check("FUNCTION"):
            return self.parse_function()

        if self.check("INT") or self.check("BOOL"):
            return self.parse_typed_declaration()

        return self.parse_statement()

    def parse_typed_declaration(self):
        type_token = self.advance()
        var_type = type_token.value

        name_token = self.expect("IDENTIFIER")

        if name_token is None:
            return None

        # Array declaration
        if self.match("SYMBOL", "["):
            size_token = self.expect("NUMBER")

            if size_token is None:
                return None

            self.expect("SYMBOL", "]")
            self.expect("SYMBOL", ";")

            return ArrayDeclaration(
                var_type,
                name_token.value,
                size_token.value,
                type_token.line,
                type_token.column,
            )

        # Normal variable declaration
        self.expect("SYMBOL", ";")

        return VariableDeclaration(
            var_type,
            name_token.value,
            type_token.line,
            type_token.column,
        )

    # -------------------------------------------------
    # Function
    # -------------------------------------------------

    def parse_function(self):
        function_token = self.advance()

        name_token = self.expect("IDENTIFIER")

        if name_token is None:
            return None

        self.expect("SYMBOL", "(")

        parameters = self.parse_parameters()

        self.expect("SYMBOL", ")")

        body = self.parse_block()

        return FunctionDeclaration(
            name_token.value,
            parameters,
            body,
            "int",
            function_token.line,
            function_token.column,
        )

    def parse_parameters(self):
        parameters = []

        if self.check("SYMBOL", ")"):
            return parameters

        while True:
            if not (self.check("INT") or self.check("BOOL")):
                token = self.current()

                self.errors.append(
                    f"Syntax Error at line {token.line}, "
                    f"column {token.column}: "
                    f"Expected parameter type."
                )

                break

            type_token = self.advance()

            name_token = self.expect("IDENTIFIER")

            if name_token is None:
                break

            parameters.append(
                Parameter(
                    type_token.value,
                    name_token.value,
                    type_token.line,
                    type_token.column,
                )
            )

            if not self.match("SYMBOL", ","):
                break

        return parameters

    # -------------------------------------------------
    # Statements
    # -------------------------------------------------

    def parse_statement(self):
        if self.check("SYMBOL", "{"):
            return self.parse_block()

        if self.check("IF"):
            return self.parse_if()

        if self.check("WHILE"):
            return self.parse_while()

        if self.check("SWITCH"):
            return self.parse_switch()

        if self.check("RETURN"):
            return self.parse_return()

        if self.check("BREAK"):
            return self.parse_break()

        if self.check("INT") or self.check("BOOL"):
            return self.parse_typed_declaration()

        return self.parse_expression_or_assignment()

    # -------------------------------------------------
    # Block
    # -------------------------------------------------

    def parse_block(self):
        start = self.expect("SYMBOL", "{")

        statements = []

        while not self.check("EOF") and not self.check("SYMBOL", "}"):
            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)
            else:
                if not self.check("EOF"):
                    self.advance()

        self.expect("SYMBOL", "}")

        if start:
            return Block(
                statements,
                start.line,
                start.column,
            )

        return Block(statements)

    # -------------------------------------------------
    # If
    # -------------------------------------------------

    def parse_if(self):
        token = self.advance()

        self.expect("SYMBOL", "(")

        condition = self.parse_expression()

        self.expect("SYMBOL", ")")

        then_branch = self.parse_statement()

        else_branch = None

        if self.match("ELSE"):
            else_branch = self.parse_statement()

        return IfStatement(
            condition,
            then_branch,
            else_branch,
            token.line,
            token.column,
        )

    # -------------------------------------------------
    # While
    # -------------------------------------------------

    def parse_while(self):
        token = self.advance()

        self.expect("SYMBOL", "(")

        condition = self.parse_expression()

        self.expect("SYMBOL", ")")

        body = self.parse_statement()

        return WhileStatement(
            condition,
            body,
            token.line,
            token.column,
        )

    # -------------------------------------------------
    # Switch
    # -------------------------------------------------

    def parse_switch(self):
        token = self.advance()

        self.expect("SYMBOL", "(")

        expression = self.parse_expression()

        self.expect("SYMBOL", ")")

        self.expect("SYMBOL", "{")

        cases = []
        default_case = None

        while not self.check("EOF") and not self.check("SYMBOL", "}"):
            if self.match("CASE"):
                case_token = self.tokens[self.position - 1]

                value = self.expect("NUMBER")

                self.expect("SYMBOL", ":")

                statements = self.parse_case_statements()

                cases.append(
                    CaseStatement(
                        value.value if value else 0,
                        statements,
                        case_token.line,
                        case_token.column,
                    )
                )

            elif self.match("DEFAULT"):
                self.expect("SYMBOL", ":")

                statements = self.parse_default_statements()

                default_case = Block(statements)

            else:
                current = self.current()

                self.errors.append(
                    f"Syntax Error at line {current.line}, "
                    f"column {current.column}: "
                    f"Expected 'mcase' or 'mdefault'."
                )

                self.advance()

        self.expect("SYMBOL", "}")

        return SwitchStatement(
            expression,
            cases,
            default_case,
            token.line,
            token.column,
        )

    def parse_case_statements(self):
        statements = []

        while (
            not self.check("EOF")
            and not self.check("CASE")
            and not self.check("DEFAULT")
            and not self.check("SYMBOL", "}")
        ):
            if self.check("BREAK"):
                self.advance()
                self.expect("SYMBOL", ";")
                statements.append(BreakStatement())
                break

            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)
            else:
                if not self.check("EOF"):
                    self.advance()

        return statements

    def parse_default_statements(self):
        statements = []

        while (
            not self.check("EOF")
            and not self.check("SYMBOL", "}")
        ):
            if self.check("BREAK"):
                self.advance()
                self.expect("SYMBOL", ";")
                statements.append(BreakStatement())
                break

            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)
            else:
                if not self.check("EOF"):
                    self.advance()

        return statements

    # -------------------------------------------------
    # Return
    # -------------------------------------------------

    def parse_return(self):
        token = self.advance()

        expression = None

        if not self.check("SYMBOL", ";"):
            expression = self.parse_expression()

        self.expect("SYMBOL", ";")

        return ReturnStatement(
            expression,
            token.line,
            token.column,
        )

    # -------------------------------------------------
    # Break
    # -------------------------------------------------

    def parse_break(self):
        token = self.advance()

        self.expect("SYMBOL", ";")

        return BreakStatement(
            token.line,
            token.column,
        )

    # -------------------------------------------------
    # Assignment / Expression
    # -------------------------------------------------

    def parse_expression_or_assignment(self):
        start = self.current()

        # Identifier assignment or array assignment
        if self.check("IDENTIFIER"):
            if self.peek().token_type == "OPERATOR" and self.peek().value == "=":
                name_token = self.advance()

                target = Identifier(
                    name_token.value,
                    name_token.line,
                    name_token.column,
                )

                self.advance()

                expression = self.parse_expression()

                self.expect("SYMBOL", ";")

                return Assignment(
                    target,
                    expression,
                    start.line,
                    start.column,
                )

            if (
                self.peek().token_type == "SYMBOL"
                and self.peek().value == "["
            ):
                name_token = self.advance()

                self.advance()

                index = self.parse_expression()

                self.expect("SYMBOL", "]")

                if (
                    self.check("OPERATOR")
                    and self.current().value == "="
                ):
                    self.advance()

                    expression = self.parse_expression()

                    self.expect("SYMBOL", ";")

                    target = ArrayAccess(
                        name_token.value,
                        index,
                        name_token.line,
                        name_token.column,
                    )

                    return Assignment(
                        target,
                        expression,
                        start.line,
                        start.column,
                    )

                # Array access as expression statement
                array_access = ArrayAccess(
                    name_token.value,
                    index,
                    name_token.line,
                    name_token.column,
                )

                self.expect("SYMBOL", ";")

                return ExpressionStatement(
                    array_access,
                    start.line,
                    start.column,
                )

        expression = self.parse_expression()

        self.expect("SYMBOL", ";")

        return ExpressionStatement(
            expression,
            start.line,
            start.column,
        )

    # -------------------------------------------------
    # Expressions
    # -------------------------------------------------

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        expression = self.parse_comparison()

        while self.check("OPERATOR") and self.current().value in {
            "==",
            "!=",
        }:
            operator = self.advance()

            right = self.parse_comparison()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                operator.line,
                operator.column,
            )

        return expression

    def parse_comparison(self):
        expression = self.parse_term()

        while self.check("OPERATOR") and self.current().value in {
            "<",
            ">",
            "<=",
            ">=",
        }:
            operator = self.advance()

            right = self.parse_term()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                operator.line,
                operator.column,
            )

        return expression

    def parse_term(self):
        expression = self.parse_factor()

        while self.check("OPERATOR") and self.current().value in {
            "+",
            "-",
        }:
            operator = self.advance()

            right = self.parse_factor()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                operator.line,
                operator.column,
            )

        return expression

    def parse_factor(self):
        expression = self.parse_unary()

        while self.check("OPERATOR") and self.current().value in {
            "*",
            "/",
            "%",
        }:
            operator = self.advance()

            right = self.parse_unary()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                operator.line,
                operator.column,
            )

        return expression

    def parse_unary(self):
        if self.check("OPERATOR") and self.current().value in {
            "!",
            "-",
        }:
            operator = self.advance()

            operand = self.parse_unary()

            return UnaryExpression(
                operator.value,
                operand,
                operator.line,
                operator.column,
            )

        return self.parse_primary()

    # -------------------------------------------------
    # Primary
    # -------------------------------------------------

    def parse_primary(self):
        token = self.current()

        if self.check("NUMBER"):
            self.advance()

            return NumberLiteral(
                token.value,
                token.line,
                token.column,
            )

        if self.check("STRING"):
            self.advance()

            return StringLiteral(
                token.value,
                token.line,
                token.column,
            )

        if self.check("TRUE"):
            self.advance()

            return BooleanLiteral(
                True,
                token.line,
                token.column,
            )

        if self.check("FALSE"):
            self.advance()

            return BooleanLiteral(
                False,
                token.line,
                token.column,
            )

        if self.check("IDENTIFIER"):
            name_token = self.advance()

            # Function call
            if self.match("SYMBOL", "("):
                arguments = []

                if not self.check("SYMBOL", ")"):
                    while True:
                        arguments.append(
                            self.parse_expression()
                        )

                        if not self.match("SYMBOL", ","):
                            break

                self.expect("SYMBOL", ")")

                return FunctionCall(
                    name_token.value,
                    arguments,
                    name_token.line,
                    name_token.column,
                )

            # Array access
            if self.match("SYMBOL", "["):
                index = self.parse_expression()

                self.expect("SYMBOL", "]")

                return ArrayAccess(
                    name_token.value,
                    index,
                    name_token.line,
                    name_token.column,
                )

            return Identifier(
                name_token.value,
                name_token.line,
                name_token.column,
            )

        if self.match("SYMBOL", "("):
            expression = self.parse_expression()

            self.expect("SYMBOL", ")")

            return expression

        self.errors.append(
            f"Syntax Error at line {token.line}, "
            f"column {token.column}: "
            f"Unexpected token '{token.value}'."
        )

        self.advance()

        return NumberLiteral(0)
