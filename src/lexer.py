class Token:
    def __init__(self, kind, value, line, column):
        self.kind = kind
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return (
            f"Token({self.kind}, {self.value!r}, "
            f"{self.line}:{self.column})"
        )


class Lexer:
    KEYWORDS = {
        "struct": "STRUCT",
        "function": "FUNCTION",
        "int": "INT",
        "float": "FLOAT",
        "string": "STRING",
        "bool": "BOOL",
        "true": "TRUE",
        "false": "FALSE",
        "return": "RETURN",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "break": "BREAK",
        "continue": "CONTINUE",
        "print": "PRINT",
    }

    TWO_CHAR_OPS = {
        "==": "EQ",
        "!=": "NE",
        "<=": "LE",
        ">=": "GE",
        "&&": "AND",
        "||": "OR",
    }

    ONE_CHAR_OPS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "%": "MOD",
        "=": "ASSIGN",
        ":": "COLON",
        "<": "LT",
        ">": "GT",
        "!": "NOT",
        ";": "SEMICOLON",
        ",": "COMMA",
        ".": "DOT",
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LBRACE",
        "}": "RBRACE",
    }

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def current(self):
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def advance(self):
        ch = self.current()

        if ch is None:
            return None

        self.pos += 1

        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return ch

    def tokenize(self):
        tokens = []

        while self.current() is not None:

            ch = self.current()

            # Whitespace
            if ch.isspace():
                self.advance()
                continue

            # Single-line comments
            if ch == "/" and self.pos + 1 < len(self.source):
                if self.source[self.pos + 1] == "/":
                    while (
                        self.current() is not None
                        and self.current() != "\n"
                    ):
                        self.advance()
                    continue

            # Identifier / keyword
            if ch.isalpha() or ch == "_":
                tokens.append(self.identifier())
                continue

            # Number
            if ch.isdigit():
                tokens.append(self.number())
                continue

            # String
            if ch == '"':
                tokens.append(self.string())
                continue

            # Two-character operators
            two = self.source[self.pos:self.pos + 2]

            if two in self.TWO_CHAR_OPS:
                line = self.line
                column = self.column

                self.advance()
                self.advance()

                tokens.append(
                    Token(
                        self.TWO_CHAR_OPS[two],
                        two,
                        line,
                        column
                    )
                )
                continue

            # One-character operators
            if ch in self.ONE_CHAR_OPS:
                line = self.line
                column = self.column

                self.advance()

                tokens.append(
                    Token(
                        self.ONE_CHAR_OPS[ch],
                        ch,
                        line,
                        column
                    )
                )
                continue

            # Invalid character
            raise SyntaxError(
                f"Unexpected character '{ch}' "
                f"at line {self.line}, column {self.column}"
            )

        # End of file
        tokens.append(
            Token(
                "EOF",
                "",
                self.line,
                self.column
            )
        )

        return tokens

    def identifier(self):
        line = self.line
        column = self.column
        result = ""

        while (
            self.current() is not None
            and (
                self.current().isalnum()
                or self.current() == "_"
            )
        ):
            result += self.advance()

        kind = self.KEYWORDS.get(
            result,
            "IDENTIFIER"
        )

        return Token(
            kind,
            result,
            line,
            column
        )

    def number(self):
        line = self.line
        column = self.column
        result = ""

        while (
            self.current() is not None
            and self.current().isdigit()
        ):
            result += self.advance()

        # Float number
        if self.current() == ".":
            result += self.advance()

            while (
                self.current() is not None
                and self.current().isdigit()
            ):
                result += self.advance()

            return Token(
                "FLOAT_LITERAL",
                float(result),
                line,
                column
            )

        # Integer
        return Token(
            "INT_LITERAL",
            int(result),
            line,
            column
        )

    def string(self):
        line = self.line
        column = self.column

        self.advance()

        result = ""

        while (
            self.current() is not None
            and self.current() != '"'
        ):
            ch = self.advance()

            if ch == "\\":
                next_ch = self.current()

                if next_ch is None:
                    break

                self.advance()

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\",
                }

                result += escapes.get(
                    next_ch,
                    next_ch
                )

            else:
                result += ch

        if self.current() != '"':
            raise SyntaxError(
                f"Unterminated string "
                f"at line {line}, column {column}"
            )

        self.advance()

        return Token(
            "STRING_LITERAL",
            result,
            line,
            column
        )
