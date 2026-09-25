from ast import (
    Program,
    Block,
    VariableDeclaration,
    ArrayDeclaration,
    FunctionDeclaration,
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


class TACGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
        self.break_labels = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self, prefix="L"):
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, tree):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
        self.break_labels = []

        self.visit(tree)

        return self.instructions

    # -------------------------------------------------
    # Dispatcher
    # -------------------------------------------------

    def visit(self, node):
        if node is None:
            return None

        method_name = (
            "visit_" +
            node.__class__.__name__.lower()
        )

        method = getattr(
            self,
            method_name,
            self.visit_unknown
        )

        return method(node)

    def visit_unknown(self, node):
        self.emit(
            f"# Unsupported node: "
            f"{node.__class__.__name__}"
        )
        return None

    # -------------------------------------------------
    # Program
    # -------------------------------------------------

    def visit_program(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    # -------------------------------------------------
    # Block
    # -------------------------------------------------

    def visit_block(self, node):
        for statement in node.statements:
            self.visit(statement)

    # -------------------------------------------------
    # Variable declaration
    # -------------------------------------------------

    def visit_variabledeclaration(self, node):
        self.emit(
            f"DECLARE {node.name} {node.var_type}"
        )

    # -------------------------------------------------
    # Array declaration
    # -------------------------------------------------

    def visit_arraydeclaration(self, node):
        self.emit(
            f"DECLARE_ARRAY "
            f"{node.name} "
            f"{node.element_type} "
            f"{node.size}"
        )

    # -------------------------------------------------
    # Function declaration
    # -------------------------------------------------

    def visit_functiondeclaration(self, node):
        self.emit(
            f"FUNCTION {node.name}"
        )

        for parameter in node.parameters:
            self.emit(
                f"PARAMETER "
                f"{parameter.name} "
                f"{parameter.param_type}"
            )

        self.visit(node.body)

        self.emit(
            f"END_FUNCTION {node.name}"
        )

    # -------------------------------------------------
    # If
    # -------------------------------------------------

    def visit_ifstatement(self, node):
        false_label = self.new_label("Lfalse")

        condition = self.visit(node.condition)

        self.emit(
            f"IF_FALSE {condition} GOTO {false_label}"
        )

        self.visit(node.then_branch)

        if node.else_branch is not None:
            end_label = self.new_label("Lend")

            self.emit(
                f"GOTO {end_label}"
            )

            self.emit(
                f"LABEL {false_label}"
            )

            self.visit(node.else_branch)

            self.emit(
                f"LABEL {end_label}"
            )

        else:
            self.emit(
                f"LABEL {false_label}"
            )

    # -------------------------------------------------
    # While
    # -------------------------------------------------

    def visit_whilestatement(self, node):
        start_label = self.new_label("Lwhile")
        end_label = self.new_label("LwhileEnd")

        self.emit(
            f"LABEL {start_label}"
        )

        condition = self.visit(node.condition)

        self.emit(
            f"IF_FALSE {condition} GOTO {end_label}"
        )

        self.break_labels.append(end_label)

        self.visit(node.body)

        self.break_labels.pop()

        self.emit(
            f"GOTO {start_label}"
        )

        self.emit(
            f"LABEL {end_label}"
        )

    # -------------------------------------------------
    # Switch
    # -------------------------------------------------

    def visit_switchstatement(self, node):
        switch_value = self.visit(
            node.expression
        )

        end_label = self.new_label(
            "LswitchEnd"
        )

        case_labels = []

        for _ in node.cases:
            case_labels.append(
                self.new_label("Lcase")
            )

        default_label = None

        if node.default_case is not None:
            default_label = self.new_label(
                "Ldefault"
            )

        # Generate comparisons
        for index, case in enumerate(node.cases):
            temp = self.new_temp()

            self.emit(
                f"{temp} = "
                f"{switch_value} == "
                f"{case.value}"
            )

            self.emit(
                f"IF {temp} GOTO "
                f"{case_labels[index]}"
            )

        if default_label is not None:
            self.emit(
                f"GOTO {default_label}"
            )
        else:
            self.emit(
                f"GOTO {end_label}"
            )

        # Generate cases
        self.break_labels.append(end_label)

        for index, case in enumerate(node.cases):
            self.emit(
                f"LABEL {case_labels[index]}"
            )

            self.visit_case_statements(
                case
            )

        # Default
        if node.default_case is not None:
            self.emit(
                f"LABEL {default_label}"
            )

            self.visit(
                node.default_case
            )

        self.break_labels.pop()

        self.emit(
            f"LABEL {end_label}"
        )

    def visit_case_statements(self, case):
        for statement in case.statements:
            self.visit(statement)

    # -------------------------------------------------
    # Break
    # -------------------------------------------------

    def visit_breakstatement(self, node):
        if self.break_labels:
            self.emit(
                f"GOTO {self.break_labels[-1]}"
            )

    # -------------------------------------------------
    # Return
    # -------------------------------------------------

    def visit_returnstatement(self, node):
        if node.expression is None:
            self.emit("RETURN")
            return

        value = self.visit(
            node.expression
        )

        self.emit(
            f"RETURN {value}"
        )

    # -------------------------------------------------
    # Assignment
    # -------------------------------------------------

    def visit_assignment(self, node):
        value = self.visit(
            node.expression
        )

        if isinstance(
            node.target,
            ArrayAccess
        ):
            index = self.visit(
                node.target.index
            )

            self.emit(
                f"STORE_ARRAY "
                f"{node.target.name} "
                f"{index} "
                f"{value}"
            )

        else:
            self.emit(
                f"{node.target.name} = {value}"
            )

    # -------------------------------------------------
    # Expression statement
    # -------------------------------------------------

    def visit_expressionstatement(self, node):
        return self.visit(
            node.expression
        )

    # -------------------------------------------------
    # Identifier
    # -------------------------------------------------

    def visit_identifier(self, node):
        return node.name

    # -------------------------------------------------
    # Array access
    # -------------------------------------------------

    def visit_arrayaccess(self, node):
        index = self.visit(
            node.index
        )

        temp = self.new_temp()

        self.emit(
            f"{temp} = "
            f"LOAD_ARRAY "
            f"{node.name} "
            f"{index}"
        )

        return temp

    # -------------------------------------------------
    # Number
    # -------------------------------------------------

    def visit_numberliteral(self, node):
        return str(node.value)

    # -------------------------------------------------
    # String
    # -------------------------------------------------

    def visit_stringliteral(self, node):
        return f'"{node.value}"'

    # -------------------------------------------------
    # Boolean
    # -------------------------------------------------

    def visit_booleanliteral(self, node):
        if node.value:
            return "1"

        return "0"

    # -------------------------------------------------
    # Binary expression
    # -------------------------------------------------

    def visit_binaryexpression(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        temp = self.new_temp()

        self.emit(
            f"{temp} = "
            f"{left} "
            f"{node.operator} "
            f"{right}"
        )

        return temp

    # -------------------------------------------------
    # Unary expression
    # -------------------------------------------------

    def visit_unaryexpression(self, node):
        operand = self.visit(
            node.operand
        )

        temp = self.new_temp()

        self.emit(
            f"{temp} = "
            f"{node.operator}"
            f"{operand}"
        )

        return temp

    # -------------------------------------------------
    # Function call
    # -------------------------------------------------

    def visit_functioncall(self, node):
        arguments = []

        for argument in node.arguments:
            arguments.append(
                self.visit(argument)
            )

        for argument in arguments:
            self.emit(
                f"PARAM {argument}"
            )

        temp = self.new_temp()

        self.emit(
            f"{temp} = CALL "
            f"{node.name} "
            f"{len(arguments)}"
        )

        return temp
