class TACGenerator:

    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, *instruction):
        self.code.append(instruction)

    def generate(self, program):
        for declaration in program.declarations:

            if declaration.__class__.__name__ == "FunctionDecl":
                self.function(declaration)

        return self.code

    # ---------------- FUNCTION ----------------

    def function(self, node):

        self.emit("FUNC", node.name)

        self.block(node.body)

        self.emit("END_FUNC", node.name)

    # ---------------- BLOCK ----------------

    def block(self, node):

        for statement in node.statements:
            self.statement(statement)

    # ---------------- STATEMENTS ----------------

    def statement(self, node):

        name = node.__class__.__name__

        if name == "VarDecl":

            if node.initializer is not None:
                value = self.expression(
                    node.initializer
                )

                self.emit(
                    "MOV",
                    node.name,
                    value
                )

        elif name == "Assign":

            value = self.expression(
                node.value
            )

            target = self.target(
                node.target
            )

            self.emit(
                "MOV",
                target,
                value
            )

        elif name == "PrintStmt":

            value = self.expression(
                node.value
            )

            self.emit(
                "PRINT",
                value
            )

        elif name == "ReturnStmt":

            if node.value is None:
                self.emit("RETURN")

            else:
                value = self.expression(
                    node.value
                )

                self.emit(
                    "RETURN",
                    value
                )

        elif name == "ExprStmt":

            self.expression(
                node.expression
            )

        elif name == "IfStmt":

            self.if_statement(node)

        elif name == "WhileStmt":

            self.while_statement(node)

        elif name == "BreakStmt":

            self.emit("BREAK")

        elif name == "ContinueStmt":

            self.emit("CONTINUE")

        elif name == "FunctionDecl":

            self.emit(
                "NESTED_FUNC",
                node.name
            )

    # ---------------- IF ----------------

    def if_statement(self, node):

        else_label = self.new_label()
        end_label = self.new_label()

        condition = self.expression(
            node.condition
        )

        self.emit(
            "JZ",
            condition,
            else_label
        )

        self.block(
            node.then_branch
        )

        self.emit(
            "JMP",
            end_label
        )

        self.emit(
            "LABEL",
            else_label
        )

        if node.else_branch:

            self.block(
                node.else_branch
            )

        self.emit(
            "LABEL",
            end_label
        )

    # ---------------- WHILE ----------------

    def while_statement(self, node):

        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(
            "LABEL",
            start_label
        )

        condition = self.expression(
            node.condition
        )

        self.emit(
            "JZ",
            condition,
            end_label
        )

        self.block(node.body)

        self.emit(
            "JMP",
            start_label
        )

        self.emit(
            "LABEL",
            end_label
        )

    # ---------------- EXPRESSIONS ----------------

    def expression(self, node):

        name = node.__class__.__name__

        if name == "Literal":
            return self.literal(node.value)

        if name == "Variable":
            return node.name

        if name == "Binary":

            left = self.expression(
                node.left
            )

            right = self.expression(
                node.right
            )

            temp = self.new_temp()

            self.emit(
                "BIN",
                temp,
                node.operator,
                left,
                right
            )

            return temp

        if name == "Unary":

            operand = self.expression(
                node.operand
            )

            temp = self.new_temp()

            self.emit(
                "UNARY",
                temp,
                node.operator,
                operand
            )

            return temp

        if name == "Call":

            return self.call(node)

        if name == "Member":

            obj = self.expression(
                node.object
            )

            return f"{obj}.{node.name}"

        return None

    # ---------------- FUNCTION CALL ----------------

    def call(self, node):

        args = []

        for argument in node.arguments:

            args.append(
                self.expression(argument)
            )

        temp = self.new_temp()

        function_name = getattr(
            node.callee,
            "name",
            str(node.callee)
        )

        self.emit(
            "CALL",
            temp,
            function_name,
            len(args),
            *args
        )

        return temp

    # ---------------- ASSIGNMENT TARGET ----------------

    def target(self, node):

        name = node.__class__.__name__

        if name == "Variable":
            return node.name

        if name == "Member":

            obj = self.expression(
                node.object
            )

            return f"{obj}.{node.name}"

        return None

    # ---------------- LITERAL ----------------

    def literal(self, value):

        if isinstance(value, str):
            return repr(value)

        if isinstance(value, bool):

            return (
                "true"
                if value
                else "false"
            )

        return str(value)


def generate_tac(program):

    generator = TACGenerator()

    return generator.generate(program)
