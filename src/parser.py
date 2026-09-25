from ast import (
    Program,
    Block,
    VariableDeclaration,
    StructDeclaration,
    FieldDeclaration,
    FunctionDeclaration,
    Parameter,
    IfStatement,
    ReturnStatement,
    Assignment,
    ExpressionStatement,
    BinaryExpression,
    UnaryExpression,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    FunctionCall,
    StructAccess,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    # --------------------------------------------------
    # Basic token helpers
    # --------------------------------------------------

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]

    def peek(self, offset=1):
        index = self.position + offset

        if index < len(self.tokens):
            return self.tokens[index]

        return self.tokens[-1]

    def advance(self):
        token = self.current()

        if self.position < len(self.tokens) - 1:
            self.position += 1

        return token

    def check(self, token_type):
        return self.current().type == token_type

    def match(self, token_type):
        if self.check(token_type):
            return self.advance()

        return None

    def error(self, message):
        token = self.current()

        self.errors.append(
            f"Syntax error at line {token.line}, "
            f"column {token.column}: {message}"
        )

    def expect(self, token_type, message):
        if self.check(token_type):
            return self.advance()

        self.error(message)
        return None

    # --------------------------------------------------
    # Program
    # --------------------------------------------------

    def parse(self):
        declarations = []

        while not self.check("EOF"):
            start_position = self.position

            declaration = self.parse_declaration()

            if declaration is not None:
                declarations.append(declaration)

            # Prevent infinite loop after syntax error
            if self.position == start_position:
                self.advance()

        return Program(declarations)

    # --------------------------------------------------
    # Declarations
    # --------------------------------------------------

    def parse_declaration(self):
        # Struct declaration
        if self.check("STRUCT"):
            return self.parse_struct_declaration()

        # Function declaration
        if self.check("FUNCTION"):
            return self.parse_function_declaration()

        # Primitive or user-defined type declaration
        if self.is_type_start():
            # If IDENTIFIER IDENTIFIER appears,
            # it is a struct-type variable declaration.
            if self.check("IDENTIFIER") and self.peek().type == "IDENTIFIER":
                return self.parse_variable_declaration()

            if self.check("INT") or self.check("BOOL") or self.check("STRING_TYPE"):
                return self.parse_variable_declaration()

        # Otherwise parse as a statement
        return self.parse_statement()

    # --------------------------------------------------
    # Type
    # --------------------------------------------------

    def is_type_start(self):
        return self.check("INT") or \
               self.check("BOOL") or \
               self.check("STRING_TYPE") or \
               self.check("IDENTIFIER")

    def parse_type(self):
        token = self.current()

        if token.type == "INT":
            self.advance()
            return "int"

        if token.type == "BOOL":
            self.advance()
            return "bool"

        if token.type == "STRING_TYPE":
            self.advance()
            return "string"

        if token.type == "IDENTIFIER":
            self.advance()
            return token.value

        self.error("Expected a type.")
        return "int"

    # --------------------------------------------------
    # Variable declaration
    #
    # Examples:
    # mint age;
    # mbool active;
    # mstring name;
    # Student s;
    # --------------------------------------------------

    def parse_variable_declaration(self):
        token = self.current()

        var_type = self.parse_type()

        name_token = self.expect(
            "IDENTIFIER",
            "Expected variable name."
        )

        if name_token is None:
            return None

        self.expect(
            "SEMICOLON",
            "Expected ';' after variable declaration."
        )

        return VariableDeclaration(
            var_type,
            name_token.value,
            token.line,
            token.column
        )

    # --------------------------------------------------
    # Struct declaration
    #
    # mstruct Student {
    #     mint id;
    #     mstring name;
    # }
    # --------------------------------------------------

    def parse_struct_declaration(self):
        struct_token = self.advance()

        name_token = self.expect(
            "IDENTIFIER",
            "Expected struct name."
        )

        if name_token is None:
            return None

        self.expect(
            "LBRACE",
            "Expected '{' after struct name."
        )

        fields = []

        while not self.check("RBRACE") and not self.check("EOF"):
            field = self.parse_field_declaration()

            if field is not None:
                fields.append(field)
            else:
                # Recovery
                while (
                    not self.check("SEMICOLON")
                    and not self.check("RBRACE")
                    and not self.check("EOF")
                ):
                    self.advance()

                self.match("SEMICOLON")

        self.expect(
            "RBRACE",
            "Expected '}' after struct fields."
        )

        # Optional semicolon
        self.match("SEMICOLON")

        return StructDeclaration(
            name_token.value,
            fields,
            struct_token.line,
            struct_token.column
        )

    # --------------------------------------------------
    # Struct field
    # --------------------------------------------------

    def parse_field_declaration(self):
        token = self.current()

        if not self.is_type_start():
            self.error("Expected field type.")
            return None

        field_type = self.parse_type()

        name_token = self.expect(
            "IDENTIFIER",
            "Expected field name."
        )

        if name_token is None:
            return None

        self.expect(
            "SEMICOLON",
            "Expected ';' after field declaration."
        )

        return FieldDeclaration(
            field_type,
            name_token.value,
            token.line,
            token.column
        )

    # --------------------------------------------------
    # Function declaration
    #
    # mfunc add(mint a, mint b) {
    #     mreturn a + b;
    # }
    #
    # Nested functions are allowed because
    # parse_statement() also recognizes FUNCTION.
    # --------------------------------------------------

    def parse_function_declaration(self):
        function_token = self.advance()

        name_token = self.expect(
            "IDENTIFIER",
            "Expected function name."
        )

        if name_token is None:
            return None

        self.expect(
            "LPAREN",
            "Expected '(' after function name."
        )

        parameters = []

        if not self.check("RPAREN"):
            parameters = self.parse_parameter_list()

        self.expect(
            "RPAREN",
            "Expected ')' after parameters."
        )

        body = self.parse_block()

        return FunctionDeclaration(
            name_token.value,
            parameters,
            body,
            "int",
            function_token.line,
            function_token.column
        )

    # --------------------------------------------------
    # Parameter list
    # --------------------------------------------------

    def parse_parameter_list(self):
        parameters = []

        while True:
            param_token = self.current()

            param_type = self.parse_type()

            name_token = self.expect(
                "IDENTIFIER",
                "Expected parameter name."
            )

            if name_token is None:
                break

            parameters.append(
                Parameter(
                    param_type,
                    name_token.value,
                    param_token.line,
                    param_token.column
                )
            )

            if not self.match("COMMA"):
                break

        return parameters

    # --------------------------------------------------
    # Block
    #
    # Nested functions are allowed here.
    # --------------------------------------------------

    def parse_block(self):
        block_token = self.expect(
            "LBRACE",
            "Expected '{' to start block."
        )

        statements = []

        while not self.check("RBRACE") and not self.check("EOF"):
            start_position = self.position

            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)

            if self.position == start_position:
                self.advance()

        self.expect(
            "RBRACE",
            "Expected '}' to close block."
        )

        if block_token:
            return Block(
                statements,
                block_token.line,
                block_token.column
            )

        return Block(statements)

    # --------------------------------------------------
    # Statements
    # --------------------------------------------------

    def parse_statement(self):

        # Block
        if self.check("LBRACE"):
            return self.parse_block()

        # Nested function declaration
        if self.check("FUNCTION"):
            return self.parse_function_declaration()

        # Variable declaration
        if self.check("INT") or \
           self.check("BOOL") or \
           self.check("STRING_TYPE"):

            return self.parse_variable_declaration()

        # Struct-type variable declaration
        if (
            self.check("IDENTIFIER")
            and self.peek().type == "IDENTIFIER"
        ):
            return self.parse_variable_declaration()

        # If statement
        if self.check("IF"):
            return self.parse_if_statement()

        # Return statement
        if self.check("RETURN"):
            return self.parse_return_statement()

        # Assignment or expression statement
        return self.parse_expression_or_assignment_statement()

    # --------------------------------------------------
    # If statement
    #
    # mif (condition) {
    # }
    #
    # melse {
    # }
    # --------------------------------------------------

    def parse_if_statement(self):
        if_token = self.advance()

        self.expect(
            "LPAREN",
            "Expected '(' after 'mif'."
        )

        condition = self.parse_expression()

        self.expect(
            "RPAREN",
            "Expected ')' after condition."
        )

        then_branch = self.parse_block()

        else_branch = None

        if self.match("ELSE"):
            else_branch = self.parse_block()

        return IfStatement(
            condition,
            then_branch,
            else_branch,
            if_token.line,
            if_token.column
        )

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    def parse_return_statement(self):
        return_token = self.advance()

        if self.check("SEMICOLON"):
            self.advance()
            return ReturnStatement(
                None,
                return_token.line,
                return_token.column
            )

        expression = self.parse_expression()

        self.expect(
            "SEMICOLON",
            "Expected ';' after return statement."
        )

        return ReturnStatement(
            expression,
            return_token.line,
            return_token.column
        )

    # --------------------------------------------------
    # Assignment / Expression statement
    #
    # Examples:
    # age = 20;
    # student.id = 10;
    # add(5, 6);
    # --------------------------------------------------

    def parse_expression_or_assignment_statement(self):
        expression = self.parse_expression()

        if expression is None:
            return None

        if self.match("ASSIGN"):
            value = self.parse_expression()

            self.expect(
                "SEMICOLON",
                "Expected ';' after assignment."
            )

            return Assignment(
                expression,
                value,
                expression.line,
                expression.column
            )

        self.expect(
            "SEMICOLON",
            "Expected ';' after expression."
        )

        return ExpressionStatement(
            expression,
            expression.line,
            expression.column
        )

    # --------------------------------------------------
    # Expression hierarchy
    # --------------------------------------------------

    def parse_expression(self):
        return self.parse_equality()

    # equality:
    # comparison ( ("==" | "!=") comparison )*

    def parse_equality(self):
        expression = self.parse_comparison()

        while self.check("EQ") or self.check("NE"):
            operator = self.advance()
            right = self.parse_comparison()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                expression.line,
                expression.column
            )

        return expression

    # comparison:
    # term ( ("<" | ">" | "<=" | ">=") term )*

    def parse_comparison(self):
        expression = self.parse_term()

        while (
            self.check("LT")
            or self.check("GT")
            or self.check("LE")
            or self.check("GE")
        ):
            operator = self.advance()
            right = self.parse_term()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                expression.line,
                expression.column
            )

        return expression

    # term:
    # factor ( ("+" | "-") factor )*

    def parse_term(self):
        expression = self.parse_factor()

        while self.check("PLUS") or self.check("MINUS"):
            operator = self.advance()
            right = self.parse_factor()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                expression.line,
                expression.column
            )

        return expression

    # factor:
    # unary ( ("*" | "/" | "%") unary )*

    def parse_factor(self):
        expression = self.parse_unary()

        while (
            self.check("MULTIPLY")
            or self.check("DIVIDE")
            or self.check("MOD")
        ):
            operator = self.advance()
            right = self.parse_unary()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                expression.line,
                expression.column
            )

        return expression

    # --------------------------------------------------
    # Unary
    # --------------------------------------------------

    def parse_unary(self):
        if self.check("NOT") or self.check("MINUS"):
            operator = self.advance()

            operand = self.parse_unary()

            return UnaryExpression(
                operator.value,
                operand,
                operator.line,
                operator.column
            )

        return self.parse_primary()

    # --------------------------------------------------
    # Primary
    # --------------------------------------------------

    def parse_primary(self):

        # Number
        if self.check("NUMBER"):
            token = self.advance()

            return NumberLiteral(
                token.value,
                token.line,
                token.column
            )

        # String
        if self.check("STRING"):
            token = self.advance()

            return StringLiteral(
                token.value,
                token.line,
                token.column
            )

        # Boolean true
        if self.check("TRUE"):
            token = self.advance()

            return BooleanLiteral(
                True,
                token.line,
                token.column
            )

        # Boolean false
        if self.check("FALSE"):
            token = self.advance()

            return BooleanLiteral(
                False,
                token.line,
                token.column
            )

        # Identifier / Function call / Struct access
        if self.check("IDENTIFIER"):
            return self.parse_identifier_expression()

        # Parenthesized expression
        if self.match("LPAREN"):
            expression = self.parse_expression()

            self.expect(
                "RPAREN",
                "Expected ')' after expression."
            )

            return expression

        self.error("Expected expression.")
        return NumberLiteral(0)

    # --------------------------------------------------
    # Identifier expression
    #
    # name
    # name(...)
    # object.field
    # --------------------------------------------------

    def parse_identifier_expression(self):
        name_token = self.advance()

        # Function call
        if self.check("LPAREN"):
            self.advance()

            arguments = []

            if not self.check("RPAREN"):
                arguments = self.parse_argument_list()

            self.expect(
                "RPAREN",
                "Expected ')' after function arguments."
            )

            return FunctionCall(
                name_token.value,
                arguments,
                name_token.line,
                name_token.column
            )

        # Struct member access
        if self.match("DOT"):
            field_token = self.expect(
                "IDENTIFIER",
                "Expected field name after '.'."
            )

            if field_token is None:
                return Identifier(
                    name_token.value,
                    name_token.line,
                    name_token.column
                )

            return StructAccess(
                name_token.value,
                field_token.value,
                name_token.line,
                name_token.column
            )

        # Normal identifier
        return Identifier(
            name_token.value,
            name_token.line,
            name_token.column
        )

    # --------------------------------------------------
    # Function arguments
    # --------------------------------------------------

    def parse_argument_list(self):
        arguments = []

        while True:
            arguments.append(self.parse_expression())

            if not self.match("COMMA"):
                break

        return arguments

    # --------------------------------------------------
    # Error display
    # --------------------------------------------------

    def print_errors(self):
        if not self.errors:
            print("No syntax errors.")
            return

        print("\nSyntax Errors:")

        for error in self.errors:
            print("-", error)

    def has_errors(self):
        return len(self.errors) > 0
