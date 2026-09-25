from ast import (
    Program,
    StructDecl,
    FunctionDecl,
    VarDecl,
    Block,
    Assign,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    PrintStmt,
    BreakStmt,
    ContinueStmt,
    ExprStmt,
    Literal,
    Variable,
    Binary,
    Unary,
    Call,
    Member,
)


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # =========================
    # Basic helpers
    # =========================

    def current(self):
        return self.tokens[self.pos]

    def check(self, kind):
        return self.current().kind == kind

    def advance(self):
        token = self.current()

        if self.pos < len(self.tokens) - 1:
            self.pos += 1

        return token

    def match(self, kind):
        if self.check(kind):
            return self.advance()

        return None

    def expect(self, kind):
        if not self.check(kind):
            token = self.current()

            raise SyntaxError(
                f"Expected {kind}, got {token.kind} "
                f"at line {token.line}, "
                f"column {token.column}"
            )

        return self.advance()

    # =========================
    # Program
    # =========================

    def parse(self):
        declarations = []

        while not self.check("EOF"):

            if self.check("STRUCT"):
                declarations.append(
                    self.struct_declaration()
                )

            elif self.check("FUNCTION"):
                declarations.append(
                    self.function_declaration()
                )

            else:
                token = self.current()

                raise SyntaxError(
                    f"Expected struct or function "
                    f"at line {token.line}, "
                    f"column {token.column}"
                )

        return Program(declarations)

    # =========================
    # Struct
    # =========================

    def struct_declaration(self):

        self.expect("STRUCT")

        name = self.expect("IDENTIFIER").value

        self.expect("LBRACE")

        fields = []

        while not self.check("RBRACE"):

            field_name = self.expect(
                "IDENTIFIER"
            ).value

            self.expect("COLON")

            field_type = self.type_name()

            self.expect("SEMICOLON")

            fields.append(
                VarDecl(
                    field_name,
                    field_type
                )
            )

        self.expect("RBRACE")
        self.expect("SEMICOLON")

        return StructDecl(
            name,
            fields
        )

    # =========================
    # Function
    # =========================

    def function_declaration(self):

        self.expect("FUNCTION")

        name = self.expect(
            "IDENTIFIER"
        ).value

        self.expect("LPAREN")

        params = []

        if not self.check("RPAREN"):

            while True:

                param_name = self.expect(
                    "IDENTIFIER"
                ).value

                self.expect("COLON")

                param_type = self.type_name()

                params.append(
                    VarDecl(
                        param_name,
                        param_type
                    )
                )

                if not self.match("COMMA"):
                    break

        self.expect("RPAREN")

        return_type = None

        if self.match("COLON"):
            return_type = self.type_name()

        body = self.block()

        return FunctionDecl(
            name,
            params,
            return_type,
            body
        )

    # =========================
    # Type
    # =========================

    def type_name(self):

        token = self.current()

        if token.kind in [
            "INT",
            "FLOAT",
            "STRING",
            "BOOL",
        ]:
            self.advance()
            return token.value

        if token.kind == "IDENTIFIER":
            self.advance()
            return token.value

        raise SyntaxError(
            f"Expected type at line "
            f"{token.line}, column {token.column}"
        )

    # =========================
    # Block
    # =========================

    def block(self):

        self.expect("LBRACE")

        statements = []

        while not self.check("RBRACE"):

            if self.check("EOF"):
                token = self.current()

                raise SyntaxError(
                    f"Unclosed block at line "
                    f"{token.line}"
                )

            statements.append(
                self.statement()
            )

        self.expect("RBRACE")

        return Block(statements)

    # =========================
    # Statement
    # =========================

    def statement(self):

        if self.check("LBRACE"):
            return self.block()

        if self.check("FUNCTION"):
            return self.function_declaration()

        if self.check("IF"):
            return self.if_statement()

        if self.check("WHILE"):
            return self.while_statement()

        if self.check("RETURN"):
            return self.return_statement()

        if self.check("PRINT"):
            return self.print_statement()

        if self.check("BREAK"):
            self.advance()
            self.expect("SEMICOLON")
            return BreakStmt()

        if self.check("CONTINUE"):
            self.advance()
            self.expect("SEMICOLON")
            return ContinueStmt()

        if self.check("INT") or \
           self.check("FLOAT") or \
           self.check("STRING") or \
           self.check("BOOL"):

            return self.variable_declaration()

        expression = self.expression()

        if self.match("ASSIGN"):

            value = self.expression()

            self.expect("SEMICOLON")

            return Assign(
                expression,
                value
            )

        self.expect("SEMICOLON")

        return ExprStmt(expression)

    # =========================
    # Variable declaration
    # =========================

    def variable_declaration(self):

        type_name = self.type_name()

        name = self.expect(
            "IDENTIFIER"
        ).value

        initializer = None

        if self.match("ASSIGN"):
            initializer = self.expression()

        self.expect("SEMICOLON")

        return VarDecl(
            name,
            type_name,
            initializer
        )

    # =========================
    # If
    # =========================

    def if_statement(self):

        self.expect("IF")

        self.expect("LPAREN")

        condition = self.expression()

        self.expect("RPAREN")

        then_branch = self.block()

        else_branch = None

        if self.match("ELSE"):
            else_branch = self.block()

        return IfStmt(
            condition,
            then_branch,
            else_branch
        )

    # =========================
    # While
    # =========================

    def while_statement(self):

        self.expect("WHILE")

        self.expect("LPAREN")

        condition = self.expression()

        self.expect("RPAREN")

        body = self.block()

        return WhileStmt(
            condition,
            body
        )

    # =========================
    # Return
    # =========================

    def return_statement(self):

        self.expect("RETURN")

        value = None

        if not self.check("SEMICOLON"):
            value = self.expression()

        self.expect("SEMICOLON")

        return ReturnStmt(value)

    # =========================
    # Print
    # =========================

    def print_statement(self):

        self.expect("PRINT")

        self.expect("LPAREN")

        value = self.expression()

        self.expect("RPAREN")

        self.expect("SEMICOLON")

        return PrintStmt(value)

    # =========================
    # Expression
    # =========================

    def expression(self):
        return self.logical_or()

    # =========================
    # OR
    # =========================

    def logical_or(self):

        expr = self.logical_and()

        while self.match("OR"):

            right = self.logical_and()

            expr = Binary(
                expr,
                "||",
                right
            )

        return expr

    # =========================
    # AND
    # =========================

    def logical_and(self):

        expr = self.equality()

        while self.match("AND"):

            right = self.equality()

            expr = Binary(
                expr,
                "&&",
                right
            )

        return expr

    # =========================
    # Equality
    # =========================

    def equality(self):

        expr = self.comparison()

        while True:

            if self.match("EQ"):

                right = self.comparison()

                expr = Binary(
                    expr,
                    "==",
                    right
                )

            elif self.match("NE"):

                right = self.comparison()

                expr = Binary(
                    expr,
                    "!=",
                    right
                )

            else:
                break

        return expr

    # =========================
    # Comparison
    # =========================

    def comparison(self):

        expr = self.term()

        while True:

            if self.match("LT"):

                right = self.term()

                expr = Binary(
                    expr,
                    "<",
                    right
                )

            elif self.match("GT"):

                right = self.term()

                expr = Binary(
                    expr,
                    ">",
                    right
                )

            elif self.match("LE"):

                right = self.term()

                expr = Binary(
                    expr,
                    "<=",
                    right
                )

            elif self.match("GE"):

                right = self.term()

                expr = Binary(
                    expr,
                    ">=",
                    right
                )

            else:
                break

        return expr

    # =========================
    # Term
    # =========================

    def term(self):

        expr = self.factor()

        while True:

            if self.match("PLUS"):

                right = self.factor()

                expr = Binary(
                    expr,
                    "+",
                    right
                )

            elif self.match("MINUS"):

                right = self.factor()

                expr = Binary(
                    expr,
                    "-",
                    right
                )

            else:
                break

        return expr

    # =========================
    # Factor
    # =========================

    def factor(self):

        expr = self.unary()

        while True:

            if self.match("STAR"):

                right = self.unary()

                expr = Binary(
                    expr,
                    "*",
                    right
                )

            elif self.match("SLASH"):

                right = self.unary()

                expr = Binary(
                    expr,
                    "/",
                    right
                )

            elif self.match("MOD"):

                right = self.unary()

                expr = Binary(
                    expr,
                    "%",
                    right
                )

            else:
                break

        return expr

    # =========================
    # Unary
    # =========================

    def unary(self):

        if self.match("NOT"):

            return Unary(
                "!",
                self.unary()
            )

        if self.match("MINUS"):

            return Unary(
                "-",
                self.unary()
            )

        return self.postfix()

    # =========================
    # Postfix
    # =========================

    def postfix(self):

        expr = self.primary()

        while True:

            if self.match("LPAREN"):

                arguments = []

                if not self.check("RPAREN"):

                    while True:

                        arguments.append(
                            self.expression()
                        )

                        if not self.match("COMMA"):
                            break

                self.expect("RPAREN")

                expr = Call(
                    expr,
                    arguments
                )

            elif self.match("DOT"):

                name = self.expect(
                    "IDENTIFIER"
                ).value

                expr = Member(
                    expr,
                    name
                )

            else:
                break

        return expr

    # =========================
    # Primary
    # =========================

    def primary(self):

        token = self.current()

        if self.match("INT_LITERAL"):
            return Literal(token.value)

        if self.match("FLOAT_LITERAL"):
            return Literal(token.value)

        if self.match("STRING_LITERAL"):
            return Literal(token.value)

        if self.match("TRUE"):
            return Literal(True)

        if self.match("FALSE"):
            return Literal(False)

        if self.match("IDENTIFIER"):
            return Variable(token.value)

        if self.match("LPAREN"):

            expr = self.expression()

            self.expect("RPAREN")

            return expr

        raise SyntaxError(
            f"Unexpected token {token.kind} "
            f"at line {token.line}, "
            f"column {token.column}"
        )
