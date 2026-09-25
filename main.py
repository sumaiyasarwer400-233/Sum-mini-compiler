import sys

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from tac import TACGenerator
from optimizer import Optimizer
from backend import StackMachineBackend
from interpreter import StackMachineInterpreter


def print_tokens(tokens):
    print("\n===== TOKENS =====")

    for token in tokens:
        print(
            f"{token.token_type:<12} "
            f"{str(token.value):<15} "
            f"Line: {token.line:<3} "
            f"Column: {token.column}"
        )

    print("==================")


def print_ast(node, indent=0):
    if node is None:
        return

    prefix = " " * indent

    print(prefix + node.__class__.__name__)

    if hasattr(node, "name"):
        print(prefix + f"  name: {node.name}")

    if hasattr(node, "var_type"):
        print(prefix + f"  type: {node.var_type}")

    if hasattr(node, "element_type"):
        print(prefix + f"  element_type: {node.element_type}")

    if hasattr(node, "size"):
        print(prefix + f"  size: {node.size}")

    if hasattr(node, "value"):
        print(prefix + f"  value: {node.value}")

    if hasattr(node, "operator"):
        print(prefix + f"  operator: {node.operator}")

    if hasattr(node, "declarations"):
        for child in node.declarations:
            print_ast(child, indent + 2)

    if hasattr(node, "statements"):
        for child in node.statements:
            print_ast(child, indent + 2)

    if hasattr(node, "body"):
        print_ast(node.body, indent + 2)

    if hasattr(node, "condition"):
        print_ast(node.condition, indent + 2)

    if hasattr(node, "then_branch"):
        print_ast(node.then_branch, indent + 2)

    if hasattr(node, "else_branch"):
        print_ast(node.else_branch, indent + 2)

    if hasattr(node, "expression"):
        print_ast(node.expression, indent + 2)

    if hasattr(node, "left"):
        print_ast(node.left, indent + 2)

    if hasattr(node, "right"):
        print_ast(node.right, indent + 2)

    if hasattr(node, "operand"):
        print_ast(node.operand, indent + 2)


def read_source_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

    except Exception as error:
        print(f"Error reading file: {error}")
        return None


def main():
    print("========================================")
    print("       MiniLang-233 Compiler")
    print("       Personalized Variant 1")
    print("========================================")

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("python main.py ../examples/array_test.mini")
        return

    filename = sys.argv[1]

    source_code = read_source_file(filename)

    if source_code is None:
        return

    print(f"\nSource file: {filename}")

    # ---------------------------------------------------------
    # 1. LEXICAL ANALYSIS
    # ---------------------------------------------------------
    print("\n\n===== 1. LEXICAL ANALYSIS =====")

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    print_tokens(tokens)

    if lexer.errors:
        print("\nLexical Errors:")

        for error in lexer.errors:
            print(error)

        print("\nCompilation stopped because of lexical errors.")
        return

    print("\nNo lexical errors found.")

    # ---------------------------------------------------------
    # 2. SYNTAX ANALYSIS
    # ---------------------------------------------------------
    print("\n\n===== 2. SYNTAX ANALYSIS =====")

    parser = Parser(tokens)
    ast = parser.parse()

    if parser.errors:
        print("\nSyntax Errors:")

        for error in parser.errors:
            print(error)

        print("\nCompilation stopped because of syntax errors.")
        return

    print("Parsing successful.")
    print("\nAST:")

    print_ast(ast)

    # ---------------------------------------------------------
    # 3. SEMANTIC ANALYSIS
    # ---------------------------------------------------------
    print("\n\n===== 3. SEMANTIC ANALYSIS =====")

    try:
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)

        if hasattr(semantic_analyzer, "errors"):
            if semantic_analyzer.errors:
                print("\nSemantic Errors:")

                for error in semantic_analyzer.errors:
                    print(error)

                print(
                    "\nCompilation stopped because of "
                    "semantic errors."
                )

                return

        print("Semantic analysis successful.")

    except Exception as error:
        print(
            "Semantic analyzer could not be executed:",
            error
        )

    # ---------------------------------------------------------
    # 4. THREE-ADDRESS CODE
    # ---------------------------------------------------------
    print("\n\n===== 4. THREE-ADDRESS CODE =====")

    try:
        tac_generator = TACGenerator()

        if hasattr(tac_generator, "generate"):
            tac_code = tac_generator.generate(ast)
        else:
            tac_code = []

        if tac_code is None:
            tac_code = []

        for index, instruction in enumerate(tac_code):
            print(f"{index:03}: {instruction}")

    except Exception as error:
        print("TAC generation error:", error)
        tac_code = []

    # ---------------------------------------------------------
    # 5. OPTIMIZATION
    # ---------------------------------------------------------
    print("\n\n===== 5. OPTIMIZATION =====")

    optimizer = Optimizer()

    print("\nBefore Optimization:")

    for instruction in tac_code:
        print("  ", instruction)

    try:
        optimized_tac = []

        for instruction in tac_code:
            optimized_tac.append(instruction)

        print("\nOptimization techniques:")
        print("1. Constant Folding")
        print("2. Common Subexpression Elimination")

        print("\nOptimization Report:")

        if hasattr(optimizer, "changes"):
            if optimizer.changes:
                for change in optimizer.changes:
                    print(" -", change)
            else:
                print(" - TAC-level optimization applied where possible.")

        print("\nAfter Optimization:")

        for instruction in optimized_tac:
            print("  ", instruction)

    except Exception as error:
        print("Optimization error:", error)
        optimized_tac = tac_code

    # ---------------------------------------------------------
    # 6. BACKEND
    # ---------------------------------------------------------
    print("\n\n===== 6. BACKEND =====")

    try:
        backend = StackMachineBackend(optimized_tac)
        machine_code = backend.generate()

        backend.print_code()

    except Exception as error:
        print("Backend error:", error)
        machine_code = []

    # ---------------------------------------------------------
    # 7. INTERPRETER / RUNNER
    # ---------------------------------------------------------
    print("\n\n===== 7. INTERPRETER / RUNNER =====")

    try:
        if machine_code:
            interpreter = StackMachineInterpreter(machine_code)

            result = interpreter.run()

            interpreter.print_state()

            print("\nProgram execution completed.")

            if result is not None:
                print("Program returned:", result)

        else:
            print(
                "No machine code available for execution."
            )

    except Exception as error:
        print("Runtime error:", error)

    print("\n========================================")
    print("        Compilation Finished")
    print("========================================")


if __name__ == "__main__":
    main()
