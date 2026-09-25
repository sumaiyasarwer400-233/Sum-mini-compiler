class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return (
            f"Token({self.token_type}, {self.value!r}, "
            f"line={self.line}, column={self.column})"
        )


class Lexer:
    KEYWORDS = {
        "mif": "IF",
        "melse": "ELSE",
        "mwhile": "WHILE",
        "mfor": "FOR",
        "mbreak": "BREAK",
        "mcontinue": "CONTINUE",
        "mfunc": "FUNCTION",
        "mreturn": "RETURN",
        "mint": "INT",
        "mbool": "BOOL",
        "mtrue": "TRUE",
        "mfalse": "FALSE",
    }

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def advance(self):
        if self.position < len(self.source):
            if self.source[self.position] == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

            self.position += 1

    def peek(self):
        if self.position + 1 < len(self.source):
            return self.source[self.position + 1]
        return ""

    def add_token(self, token_type, value, line, column):
        self.tokens.append(
            Token(token_type, value, line, column)
        )

    def read_identifier(self):
        start_line = self.line
        start_column = self.column
        value = ""

        while self.position < len(self.source):
            ch = self.source[self.position]

            if ch.isalnum() or ch == "_":
                value += ch
                self.advance()
            else:
                break

        token_type = self.KEYWORDS.get(value, "IDENTIFIER")

        self.add_token(
            token_type,
            value,
            start_line,
            start_column
        )

    def read_number(self):
        start_line = self.line
        start_column = self.column
        value = ""

        while (
            self.position < len(self.source)
            and self.source[self.position].isdigit()
        ):
            value += self.source[self.position]
            self.advance()

        self.add_token(
            "NUMBER",
            value,
            start_line,
            start_column
        )

    def read_string(self):
        start_line = self.line
        start_column = self.column

        self.advance()
        value = ""

        while (
            self.position < len(self.source)
            and self.source[self.position] != '"'
        ):
            if self.source[self.position] == "\n":
                raise SyntaxError(
                    f"Unterminated string at "
                    f"line {start_line}, column {start_column}"
                )

            value += self.source[self.position]
            self.advance()

        if self.position >= len(self.source):
            raise SyntaxError(
                f"Unterminated string at "
                f"line {start_line}, column {start_column}"
            )

        self.advance()

        self.add_token(
            "STRING",
            value,
            start_line,
            start_column
        )

    def tokenize(self):
        while self.position < len(self.source):
            ch = self.source[self.position]

            # Whitespace
            if ch in " \t\r":
                self.advance()
                continue

            # New line
            if ch == "\n":
                self.advance()
                continue

            # Identifier or keyword
            if ch.isalpha() or ch == "_":
                self.read_identifier()
                continue

            # Number
            if ch.isdigit():
                self.read_number()
                continue

            # String
            if ch == '"':
                self.read_string()
                continue

            line = self.line
            column = self.column

            # Two-character operators
            two_char = ch + self.peek()

            if two_char in ["==", "!=", "<=", ">="]:
                self.add_token(
                    "OPERATOR",
                    two_char,
                    line,
                    column
                )
                self.advance()
                self.advance()
                continue

            # Single-character operators
            if ch in "+-*/%=<>":
                self.add_token(
                    "OPERATOR",
                    ch,
                    line,
                    column
                )
                self.advance()
                continue

            # Symbols
            symbols = {
                "(": "LPAREN",
                ")": "RPAREN",
                "{": "LBRACE",
                "}": "RBRACE",
                "[": "LBRACKET",
                "]": "RBRACKET",
                ";": "SEMICOLON",
                ",": "COMMA",
            }

            if ch in symbols:
                self.add_token(
                    symbols[ch],
                    ch,
                    line,
                    column
                )
                self.advance()
                continue

            # Invalid character
            raise SyntaxError(
                f"Invalid character '{ch}' "
                f"at line {line}, column {column}"
            )

        self.tokens.append(
            Token("EOF", "", self.line, self.column)
        )

        return self.tokens
