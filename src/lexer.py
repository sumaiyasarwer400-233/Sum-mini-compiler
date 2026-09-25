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
    # MiniLang-233-006-042
    # Roll = 42
    # 42 mod 4 = 2
    # Variant 2: Structs, Nested Functions, Static Scoping

    KEYWORDS = {
        "mif": "IF",
        "melse": "ELSE",
        "mfunc": "FUNCTION",
        "mreturn": "RETURN",
        "mstruct": "STRUCT",
        "mrecord": "RECORD",
        "mint": "INT",
        "mbool": "BOOL",
        "mstring": "STRING_TYPE",
        "mtrue": "TRUE",
        "mfalse": "FALSE",
    }

    TWO_CHAR_OPERATORS = {
        "==",
        "!=",
        "<=",
        ">=",
        "&&",
        "||",
    }

    ONE_CHAR_OPERATORS = {
        "+",
        "-",
        "*",
        "/",
        "%",
        "=",
        "<",
        ">",
        "!",
    }

    SYMBOLS = {
        "(", ")", "{", "}", "[", "]",
        ";", ",", ":", ".",
    }

    def __init__(self, source_code):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1

        self.tokens = []
        self.errors = []

    # ---------------------------------------------------------
    # CURRENT CHARACTER
    # ---------------------------------------------------------
    def current_char(self):
        if self.position >= len(self.source):
            return None

        return self.source[self.position]

    # ---------------------------------------------------------
    # NEXT CHARACTER
    # ---------------------------------------------------------
    def peek_char(self):
        next_position = self.position + 1

        if next_position >= len(self.source):
            return None

        return self.source[next_position]

    # ---------------------------------------------------------
    # ADVANCE
    # ---------------------------------------------------------
    def advance(self):
        char = self.current_char()

        if char is None:
            return None

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    # ---------------------------------------------------------
    # ADD TOKEN
    # ---------------------------------------------------------
    def add_token(self, token_type, value, line, column):
        self.tokens.append(
            Token(
                token_type,
                value,
                line,
                column
            )
        )

    # ---------------------------------------------------------
    # SKIP WHITESPACE
    # ---------------------------------------------------------
    def skip_whitespace(self):
        while True:
            char = self.current_char()

            if char is None:
                break

            if char in " \t\r":
                self.advance()

            elif char == "\n":
                self.advance()

            else:
                break

    # ---------------------------------------------------------
    # COMMENTS
    # ---------------------------------------------------------
    def skip_comment(self):

        # Single-line comment
        if (
            self.current_char() == "/"
            and self.peek_char() == "/"
        ):
            while self.current_char() is not None:
                char = self.advance()

                if char == "\n":
                    break

            return True

        # Multi-line comment
        if (
            self.current_char() == "/"
            and self.peek_char() == "*"
        ):
            start_line = self.line
            start_column = self.column

            self.advance()
            self.advance()

            while self.current_char() is not None:

                if (
                    self.current_char() == "*"
                    and self.peek_char() == "/"
                ):
                    self.advance()
                    self.advance()
                    return True

                self.advance()

            self.errors.append(
                f"Lexical Error at line {start_line}, "
                f"column {start_column}: "
                f"Unterminated comment."
            )

            return True

        return False

    # ---------------------------------------------------------
    # IDENTIFIER / KEYWORD
    # ---------------------------------------------------------
    def read_identifier(self):
        start_line = self.line
        start_column = self.column

        value = ""

        while True:
            char = self.current_char()

            if char is None:
                break

            if char.isalnum() or char == "_":
                value += self.advance()
            else:
                break

        if value in self.KEYWORDS:
            token_type = self.KEYWORDS[value]
        else:
            token_type = "IDENTIFIER"

        self.add_token(
            token_type,
            value,
            start_line,
            start_column
        )

    # ---------------------------------------------------------
    # NUMBER
    # ---------------------------------------------------------
    def read_number(self):
        start_line = self.line
        start_column = self.column

        value = ""

        while True:
            char = self.current_char()

            if char is None or not char.isdigit():
                break

            value += self.advance()

        self.add_token(
            "NUMBER",
            int(value),
            start_line,
            start_column
        )

    # ---------------------------------------------------------
    # STRING
    # ---------------------------------------------------------
    def read_string(self):
        start_line = self.line
        start_column = self.column

        # Skip opening quote
        self.advance()

        value = ""

        while True:
            char = self.current_char()

            # End of file
            if char is None:
                self.errors.append(
                    f"Lexical Error at line {start_line}, "
                    f"column {start_column}: "
                    f"Unterminated string."
                )
                return

            # Closing quote
            if char == '"':
                self.advance()

                self.add_token(
                    "STRING",
                    value,
                    start_line,
                    start_column
                )

                return

            # Newline inside string
            if char == "\n":
                self.errors.append(
                    f"Lexical Error at line {self.line}, "
                    f"column {self.column}: "
                    f"String cannot contain an unescaped newline."
                )

                return

            # Escape sequence
            if char == "\\":
                self.advance()

                next_char = self.current_char()

                if next_char is None:
                    self.errors.append(
                        f"Lexical Error at line {start_line}, "
                        f"column {start_column}: "
                        f"Invalid string escape."
                    )

                    return

                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\"
                }

                if next_char in escape_map:
                    value += escape_map[next_char]
                    self.advance()

                else:
                    self.errors.append(
                        f"Lexical Error at line {self.line}, "
                        f"column {self.column}: "
                        f"Unknown escape sequence."
                    )

                    self.advance()

            else:
                value += self.advance()

    # ---------------------------------------------------------
    # OPERATORS
    # ---------------------------------------------------------
    def read_operator(self):
        start_line = self.line
        start_column = self.column

        first = self.current_char()
        second = self.peek_char()

        # Two-character operator
        if (
            first is not None
            and second is not None
        ):
            two_char = first + second

            if two_char in self.TWO_CHAR_OPERATORS:
                self.advance()
                self.advance()

                self.add_token(
                    "OPERATOR",
                    two_char,
                    start_line,
                    start_column
                )

                return True

        # One-character operator
        if first in self.ONE_CHAR_OPERATORS:
            self.advance()

            self.add_token(
                "OPERATOR",
                first,
                start_line,
                start_column
            )

            return True

        return False

    # ---------------------------------------------------------
    # SYMBOLS
    # ---------------------------------------------------------
    def read_symbol(self):
        char = self.current_char()

        if char in self.SYMBOLS:
            start_line = self.line
            start_column = self.column

            self.advance()

            self.add_token(
                "SYMBOL",
                char,
                start_line,
                start_column
            )

            return True

        return False

    # ---------------------------------------------------------
    # TOKENIZE
    # ---------------------------------------------------------
    def tokenize(self):

        while self.current_char() is not None:

            self.skip_whitespace()

            if self.current_char() is None:
                break

            if self.skip_comment():
                continue

            char = self.current_char()

            # Identifier or keyword
            if char.isalpha() or char == "_":
                self.read_identifier()
                continue

            # Number
            if char.isdigit():
                self.read_number()
                continue

            # String
            if char == '"':
                self.read_string()
                continue

            # Operator
            if self.read_operator():
                continue

            # Symbol
            if self.read_symbol():
                continue

            # Invalid character
            start_line = self.line
            start_column = self.column

            invalid_char = self.advance()

            self.errors.append(
                f"Lexical Error at line {start_line}, "
                f"column {start_column}: "
                f"Invalid character '{invalid_char}'."
            )

        self.tokens.append(
            Token(
                "EOF",
                "EOF",
                self.line,
                self.column
            )
        )

        return self.tokens

    # ---------------------------------------------------------
    # PRINT ERRORS
    # ---------------------------------------------------------
    def print_errors(self):

        if not self.errors:
            print("No lexical errors found.")

        else:
            for error in self.errors:
                print(error)
