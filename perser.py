class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()
        self.position += 1
        return token

    def check(self, token_type):
        return self.current().token_type == token_type

    def match(self, token_type):
        if self.check(token_type):
            return self.advance()
        return None

    def expect(self, token_type):
        if not self.check(token_type):
            token = self.current()
            raise SyntaxError(
                f"Expected {token_type} at "
                f"line {token.line}, column {token.column}, "
                f"found {token.token_type}"
            )
        return self.advance()

    def parse(self):
        statements = []

        while not self.check("EOF"):
            statements.append(self.statement())

        return {
            "type": "Program",
            "statements": statements
        }

    def statement(self):
        if self.check("FUNCTION"):
            return self.function_declaration()

        if self.check("IF"):
            return self.if_statement()

        if self.check("WHILE"):
            return self.while_statement()

        if self.check("FOR"):
            return self.for_statement()

        if self.check("BREAK"):
            self.advance()
            self.expect("SEMICOLON")
            return {"type": "Break"}

        if self.check("CONTINUE"):
            self.advance()
            self.expect("SEMICOLON")
            return {"type": "Continue"}

        if self.check("RETURN"):
            return self.return_statement()

        return self.expression_statement()

    def function_declaration(self):
        self.expect("FUNCTION")

        name = self.expect("IDENTIFIER").value

        self.expect("LPAREN")

        parameters = []

        if not self.check("RPAREN"):
            while True:
                param_type = self.type_name()
                param_name = self.expect("IDENTIFIER").value

                parameters.append({
                    "name": param_name,
                    "type": param_type
                })

                if not self.match("COMMA"):
                    break

        self.expect("RPAREN")
        body = self.block()

        return {
            "type": "Function",
            "name": name,
            "parameters": parameters,
            "body": body
        }

    def type_name(self):
        if self.match("INT"):
            return "int"

        if self.match("BOOL"):
            return "bool"

        token = self.current()

        raise SyntaxError(
            f"Expected type at line {token.line}, "
            f"column {token.column}"
        )

    def block(self):
        self.expect("LBRACE")

        statements = []

        while not self.check("RBRACE"):
            if self.check("EOF"):
                token = self.current()
                raise SyntaxError(
                    f"Missing '}}' at line {token.line}, "
                    f"column {token.column}"
                )

            statements.append(self.statement())

        self.expect("RBRACE")

        return {
            "type": "Block",
            "statements": statements
        }

    def if_statement(self):
        self.expect("IF")
        self.expect("LPAREN")

        condition = self.expression()

        self.expect("RPAREN")

        then_branch = self.block()
        else_branch = None

        if self.match("ELSE"):
            else_branch = self.block()

        return {
            "type": "If",
            "condition": condition,
            "then": then_branch,
            "else": else_branch
        }

    def while_statement(self):
        self.expect("WHILE")
        self.expect("LPAREN")

        condition = self.expression()

        self.expect("RPAREN")

        body = self.block()

        return {
            "type": "While",
            "condition": condition,
            "body": body
        }

    def for_statement(self):
        self.expect("FOR")
        self.expect("LPAREN")

        initialization = None
        condition = None
        update = None

        if not self.check("SEMICOLON"):
            initialization = self.expression()

        self.expect("SEMICOLON")

        if not self.check("SEMICOLON"):
            condition = self.expression()

        self.expect("SEMICOLON")

        if not self.check("RPAREN"):
            update = self.expression()

        self.expect("RPAREN")

        body = self.block()

        return {
            "type": "For",
            "initialization": initialization,
            "condition": condition,
            "update": update,
            "body": body
        }

    def return_statement(self):
        self.expect("RETURN")

        value = self.expression()

        self.expect("SEMICOLON")

        return {
            "type": "Return",
            "value": value
        }

    def expression_statement(self):
        expression = self.expression()
        self.expect("SEMICOLON")

        return {
            "type": "ExpressionStatement",
            "expression": expression
        }

    def expression(self):
        return self.assignment()

    def assignment(self):
        left = self.equality()

        if self.match("OPERATOR"):
            operator = self.tokens[self.position - 1].value

            if operator == "=":
                right = self.assignment()

                return {
                    "type": "Assignment",
                    "left": left,
                    "right": right
                }

            self.position -= 1

        return left

    def equality(self):
        node = self.comparison()

        while self.check("OPERATOR"):
            operator = self.current().value

            if operator not in ["==", "!="]:
                break

            self.advance()

            right = self.comparison()

            node = {
                "type": "Binary",
                "operator": operator,
                "left": node,
                "right": right
            }

        return node

    def comparison(self):
        node = self.term()

        while self.check("OPERATOR"):
            operator = self.current().value

            if operator not in ["<", ">", "<=", ">="]:
                break

            self.advance()

            right = self.term()

            node = {
                "type": "Binary",
                "operator": operator,
                "left": node,
                "right": right
            }

        return node

    def term(self):
        node = self.factor()

        while self.check("OPERATOR"):
            operator = self.current().value

            if operator not in ["+", "-"]:
                break

            self.advance()

            right = self.factor()

            node = {
                "type": "Binary",
                "operator": operator,
                "left": node,
                "right": right
            }

        return node

    def factor(self):
        node = self.unary()

        while self.check("OPERATOR"):
            operator = self.current().value

            if operator not in ["*", "/", "%"]:
                break

            self.advance()

            right = self.unary()

            node = {
                "type": "Binary",
                "operator": operator,
                "left": node,
                "right": right
            }

        return node

    def unary(self):
        if self.check("OPERATOR"):
            operator = self.current().value

            if operator in ["+", "-"]:
                self.advance()

                operand = self.unary()

                return {
                    "type": "Unary",
                    "operator": operator,
                    "operand": operand
                }

        return self.primary()

    def primary(self):
        token = self.current()

        if self.match("NUMBER"):
            return {
                "type": "Number",
                "value": int(token.value)
            }

        if self.match("TRUE"):
            return {
                "type": "Boolean",
                "value": True
            }

        if self.match("FALSE"):
            return {
                "type": "Boolean",
                "value": False
            }

        if self.match("IDENTIFIER"):
            name = token.value

            if self.match("LPAREN"):
                arguments = []

                if not self.check("RPAREN"):
                    while True:
                        arguments.append(self.expression())

                        if not self.match("COMMA"):
                            break

                self.expect("RPAREN")

                return {
                    "type": "Call",
                    "name": name,
                    "arguments": arguments
                }

            return {
                "type": "Identifier",
                "name": name
            }

        if self.match("LPAREN"):
            expression = self.expression()
            self.expect("RPAREN")
            return expression

        raise SyntaxError(
            f"Unexpected token {token.token_type} "
            f"at line {token.line}, column {token.column}"
        )
