class ReturnSignal(Exception):
    def __init__(self, value=None):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


# ---------------- ENVIRONMENT ----------------

class Environment:

    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):

        if name in self.values:
            return self.values[name]

        if self.parent:
            return self.parent.get(name)

        raise RuntimeError(
            f"Undefined variable: {name}"
        )

    def set(self, name, value):

        if name in self.values:
            self.values[name] = value
            return

        if self.parent:
            self.parent.set(name, value)
            return

        raise RuntimeError(
            f"Undefined variable: {name}"
        )


# ---------------- FUNCTION ----------------

class FunctionValue:

    def __init__(
        self,
        declaration,
        closure,
        interpreter
    ):
        self.declaration = declaration
        self.closure = closure
        self.interpreter = interpreter

    def call(self, arguments):

        environment = Environment(
            self.closure
        )

        params = self.declaration.params

        for param, value in zip(
            params,
            arguments
        ):
            environment.define(
                param.name,
                value
            )

        try:

            self.interpreter.execute_block(
                self.declaration.body,
                environment
            )

        except ReturnSignal as signal:

            return signal.value

        return None


# ---------------- INTERPRETER ----------------

class Interpreter:

    def __init__(self):

        self.global_environment = (
            Environment()
        )

        self.environment = (
            self.global_environment
        )

        self.functions = {}

    # ---------------- RUN PROGRAM ----------------

    def run(self, program):

        # Register top-level functions
        for declaration in program.declarations:

            if (
                declaration.__class__.__name__
                == "FunctionDecl"
            ):

                function = FunctionValue(
                    declaration,
                    self.global_environment,
                    self
                )

                self.functions[
                    declaration.name
                ] = function

                self.global_environment.define(
                    declaration.name,
                    function
                )

        if "main" not in self.functions:

            raise RuntimeError(
                "main function not found"
            )

        return self.functions["main"].call([])

    # ---------------- BLOCK ----------------

    def execute_block(
        self,
        block,
        environment
    ):

        previous = self.environment

        self.environment = environment

        try:

            for statement in block.statements:
                self.execute(statement)

        finally:

            self.environment = previous

    # ---------------- STATEMENTS ----------------

    def execute(self, node):

        name = node.__class__.__name__

        # Variable declaration
        if name == "VarDecl":

            value = None

            if node.initializer is not None:

                value = self.evaluate(
                    node.initializer
                )

            self.environment.define(
                node.name,
                value
            )

        # Assignment
        elif name == "Assign":

            value = self.evaluate(
                node.value
            )

            self.assign(
                node.target,
                value
            )

        # Print
        elif name == "PrintStmt":

            value = self.evaluate(
                node.value
            )

            print(value)

        # Expression statement
        elif name == "ExprStmt":

            self.evaluate(
                node.expression
            )

        # If statement
        elif name == "IfStmt":

            condition = self.evaluate(
                node.condition
            )

            if condition:

                self.execute_block(
                    node.then_branch,
                    Environment(
                        self.environment
                    )
                )

            elif node.else_branch:

                self.execute_block(
                    node.else_branch,
                    Environment(
                        self.environment
                    )
                )

        # While statement
        elif name == "WhileStmt":

            while self.evaluate(
                node.condition
            ):

                try:

                    self.execute_block(
                        node.body,
                        Environment(
                            self.environment
                        )
                    )

                except BreakSignal:
                    break

                except ContinueSignal:
                    continue

        # Return
        elif name == "ReturnStmt":

            value = None

            if node.value is not None:

                value = self.evaluate(
                    node.value
                )

            raise ReturnSignal(value)

        # Break
        elif name == "BreakStmt":

            raise BreakSignal()

        # Continue
        elif name == "ContinueStmt":

            raise ContinueSignal()

        # Nested function
        elif name == "FunctionDecl":

            function = FunctionValue(
                node,
                self.environment,
                self
            )

            # This closure keeps the surrounding
            # environment for static scoping.
            self.environment.define(
                node.name,
                function
            )

    # ---------------- EXPRESSIONS ----------------

    def evaluate(self, node):

        name = node.__class__.__name__

        # Literal
        if name == "Literal":

            return node.value

        # Variable
        if name == "Variable":

            return self.environment.get(
                node.name
            )

        # Binary
        if name == "Binary":

            left = self.evaluate(
                node.left
            )

            right = self.evaluate(
                node.right
            )

            return self.binary(
                left,
                node.operator,
                right
            )

        # Unary
        if name == "Unary":

            value = self.evaluate(
                node.operand
            )

            if node.operator == "-":
                return -value

            if node.operator == "!":
                return not value

        # Function call
        if name == "Call":

            return self.call_function(
                node
            )

        # Struct member
        if name == "Member":

            obj = self.evaluate(
                node.object
            )

            if not isinstance(obj, dict):

                raise RuntimeError(
                    "Object is not a struct"
                )

            if node.name not in obj:

                raise RuntimeError(
                    f"Unknown field: {node.name}"
                )

            return obj[node.name]

        return None

    # ---------------- OPERATORS ----------------

    def binary(
        self,
        left,
        operator,
        right
    ):

        if operator == "+":
            return left + right

        if operator == "-":
            return left - right

        if operator == "*":
            return left * right

        if operator == "/":
            return left / right

        if operator == "%":
            return left % right

        if operator == "==":
            return left == right

        if operator == "!=":
            return left != right

        if operator == "<":
            return left < right

        if operator == ">":
            return left > right

        if operator == "<=":
            return left <= right

        if operator == ">=":
            return left >= right

        if operator == "&&":
            return left and right

        if operator == "||":
            return left or right

        raise RuntimeError(
            f"Unknown operator: {operator}"
        )

    # ---------------- FUNCTION CALL ----------------

    def call_function(self, node):

        function = self.evaluate(
            node.callee
        )

        arguments = []

        for argument in node.arguments:

            arguments.append(
                self.evaluate(argument)
            )

        if not isinstance(
            function,
            FunctionValue
        ):

            raise RuntimeError(
                "Not a function"
            )

        return function.call(
            arguments
        )

    # ---------------- ASSIGNMENT ----------------

    def assign(
        self,
        target,
        value
    ):

        name = target.__class__.__name__

        if name == "Variable":

            self.environment.set(
                target.name,
                value
            )

        elif name == "Member":

            obj = self.evaluate(
                target.object
            )

            if not isinstance(obj, dict):

                raise RuntimeError(
                    "Object is not a struct"
                )

            obj[target.name] = value

        else:

            raise RuntimeError(
                "Invalid assignment target"
            )
