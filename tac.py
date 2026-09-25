from ast import (
    Program,
    Block,
    VariableDeclaration,
    StructDeclaration,
    FunctionDeclaration,
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


class TACGenerator:
    """
    Three-Address Code generator for MiniLang Variant 2.

    Supports:
    - Variables
    - Arithmetic expressions
    - Boolean expressions
    - Assignments
    - If/else
    - Functions
    - Nested functions
    - Function calls
    - Return
    - Struct member access
    """

    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    # ==================================================
    # Utility
    # ==================================================

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self, prefix="L"):
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def emit(self, instruction):
        self.code.append(instruction)

    # ==================================================
    # Main
    # ==================================================

    def generate(self, node):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

        self.visit(node)

        return self.code

    # ==================================================
    # Visitor
    # ==================================================

    def visit(self, node):
        if node is None:
            return None

        if isinstance(node, Program):
            return self.visit_program(node)

        if isinstance(node, Block):
            return self.visit_block(node)

        if isinstance(node, StructDeclaration):
            return self.visit_struct_declaration(node)

        if isinstance(node, VariableDeclaration):
            return self.visit_variable_declaration(node)

        if isinstance(node, FunctionDeclaration):
            return self.visit_function_declaration(node)

        if isinstance(node, IfStatement):
            return self.visit_if(node)

        if isinstance(node, ReturnStatement):
            return self.visit_return(node)

        if isinstance(node, Assignment):
            return self.visit_assignment(node)

        if isinstance(node, ExpressionStatement):
            return self.visit(node.expression)

        if isinstance(node, BinaryExpression):
            return self.visit_binary(node)

        if isinstance(node, UnaryExpression):
            return self.visit_unary(node)

        if isinstance(node, NumberLiteral):
            return str(node.value)

        if isinstance(node, StringLiteral):
            return f'"{node.value}"'

        if isinstance(node, BooleanLiteral):
            return "1" if node.value else "0"

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, StructAccess):
            return f"{node.object_name}.{node.field_name}"

        if isinstance(node, FunctionCall):
            return self.visit_function_call(node)

        return None

    # ==================================================
    # Program
    # ==================================================

    def visit_program(self, node):
        for declaration in node.declarations:
            self.visit(declaration)

    # ==================================================
    # Struct
    # ==================================================

    def visit_struct_declaration(self, node):
        # Struct declarations do not need executable TAC.
        self.emit(f"# struct {node.name}")

        for field in node.fields:
            self.emit(
                f"# field {field.field_type} {field.name}"
            )

        self.emit(f"# end struct {node.name}")

    # ==================================================
    # Variable declaration
    # ==================================================

    def visit_variable_declaration(self, node):
        # Declaration itself does not need executable TAC.
        self.emit(
            f"# declare {node.var_type} {node.name}"
        )

    # ==================================================
    # Block
    # ==================================================

    def visit_block(self, node):
        for statement in node.statements:
            self.visit(statement)

    # ==================================================
    # Function declaration
    # ==================================================

    def visit_function_declaration(self, node):
        self.emit(f"label FUNC_{node.name}")

        # Parameters
        for index, parameter in enumerate(node.parameters):
            self.emit(
                f"# param {index + 1} "
                f"{parameter.param_type} "
                f"{parameter.name}"
            )

        self.visit(node.body)

        self.emit(f"return 0")
        self.emit(f"label END_{node.name}")

    # ==================================================
    # If / Else
    # ==================================================

    def visit_if(self, node):
        condition = self.visit(node.condition)

        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")

        self.emit(
            f"ifFalse {condition} goto {else_label}"
        )

        self.visit(node.then_branch)

        if node.else_branch is not None:
            self.emit(f"goto {end_label}")

            self.emit(f"label {else_label}")

            self.visit(node.else_branch)

            self.emit(f"label {end_label}")

        else:
            self.emit(f"label {else_label}")

    # ==================================================
    # Return
    # ==================================================

    def visit_return(self, node):
        if node.expression is None:
            self.emit("return")
            return

        value = self.visit(node.expression)

        self.emit(f"return {value}")

    # ==================================================
    # Assignment
    # ==================================================

    def visit_assignment(self, node):
        value = self.visit(node.expression)

        target = self.visit(node.target)

        self.emit(f"{target} = {value}")

        return target

    # ==================================================
    # Binary expression
    # ==================================================

    def visit_binary(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        temp = self.new_temp()

        self.emit(
            f"{temp} = {left} {node.operator} {right}"
        )

        return temp

    # ==================================================
    # Unary expression
    # ==================================================

    def visit_unary(self, node):
        operand = self.visit(node.operand)

        temp = self.new_temp()

        self.emit(
            f"{temp} = {node.operator}{operand}"
        )

        return temp

    # ==================================================
    # Function call
    # ==================================================

    def visit_function_call(self, node):
        arguments = []

        for argument in node.arguments:
            value = self.visit(argument)
            arguments.append(value)

            self.emit(f"param {value}")

        temp = self.new_temp()

        self.emit(
            f"{temp} = call {node.name}, "
            f"{len(arguments)}"
        )

        return temp

    # ==================================================
    # Formatting
    # ==================================================

    def print_code(self, code=None):
        if code is None:
            code = self.code

        print("\nThree-Address Code (TAC):")

        if not code:
            print("(empty)")
            return

        for index, instruction in enumerate(code, start=1):
            print(
                f"{index:03}: {instruction}"
            )
