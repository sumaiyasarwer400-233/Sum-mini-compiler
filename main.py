import sys
import os

# Make sure Python can find the src modules.
CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from tac import TACGenerator
from optimizer import Optimizer
from backend import StackMachineBackend
from interpreter import StackMachineInterpreter


def print_title(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def read_source_file(filename):
    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    except FileNotFoundError:
        print(
            f"Error: File '{filename}' not found."
        )
        return None

    except OSError as error:
        print(
            f"Error reading file: {error}"
        )
        return None


def run_compiler(filename):
    # ==================================================
    # Read source
    # ==================================================

    source = read_source_file(filename)

    if source is None:
        return False

    print_title(
        "MINILANG COMPILER - VARIANT 2"
    )

    print(
        f"Source file: {filename}"
    )

    print(
        "Variant: 2 "
        "(Structs, Nested Functions, Static Scoping)"
    )

    # ==================================================
    # 1. LEXICAL ANALYSIS
    # ==================================================

    print_title(
        "1. LEXICAL ANALYSIS"
    )

    lexer = Lexer(source)

    tokens = lexer.tokenize()

    if lexer.errors:
        print("Lexical Errors:")

        lexer.print_errors()

        return False

    print(
        f"Tokens generated: {len(tokens)}"
    )

    for token in tokens:
        print(token)

    # ==================================================
    # 2. SYNTAX ANALYSIS
    # ==================================================

    print_title(
        "2. SYNTAX ANALYSIS"
    )

    parser = Parser(tokens)

    ast = parser.parse()

    if parser.has_errors():
        parser.print_errors()

        return False

    print(
        "Parsing completed successfully."
    )

    # ==================================================
    # 3. SEMANTIC ANALYSIS
    # ==================================================

    print_title(
        "3. SEMANTIC ANALYSIS"
    )

    semantic_analyzer = SemanticAnalyzer()

    semantic_analyzer.analyze(ast)

    if semantic_analyzer.has_errors():
        semantic_analyzer.print_errors()

        return False

    print(
        "Semantic analysis completed successfully."
    )

    print(
        "Static scoping and nested scopes "
        "checked successfully."
    )

    # ==================================================
    # 4. TAC GENERATION
    # ==================================================

    print_title(
        "4. THREE-ADDRESS CODE GENERATION"
    )

    tac_generator = TACGenerator()

    tac_code = tac_generator.generate(ast)

    tac_generator.print_code(
        tac_code
    )

    # ==================================================
    # 5. TAC OPTIMIZATION
    # ==================================================

    print_title(
        "5. TAC OPTIMIZATION"
    )

    optimizer = Optimizer()

    optimized_tac = optimizer.optimize(
        tac_code
    )

    optimizer.print_comparison(
        tac_code,
        optimized_tac
    )

    # ==================================================
    # 6. BACKEND
    # ==================================================

    print_title(
        "6. STACK MACHINE BACKEND"
    )

    backend = StackMachineBackend(
        optimized_tac
    )

    machine_code = backend.generate()

    backend.print_code()

    # ==================================================
    # 7. INTERPRETER / RUNNER
    # ==================================================

    print_title(
        "7. STACK MACHINE INTERPRETER"
    )

    interpreter = StackMachineInterpreter(
        machine_code
    )

    try:
        result = interpreter.run()

        interpreter.print_state()

        print(
            "\nProgram executed successfully."
        )

        if result is not None:
            print(
                f"Program return value: {result}"
            )

    except RuntimeError as error:
        print(
            f"\nRuntime Error: {error}"
        )

        return False

    # ==================================================
    # COMPLETE
    # ==================================================

    print_title(
        "COMPILATION COMPLETED"
    )

    print(
        "MiniLang source successfully passed through:"
    )

    print("1. Lexer")
    print("2. Parser")
    print("3. AST")
    print("4. Semantic Analysis")
    print("5. TAC Generation")
    print("6. TAC Optimization")
    print("7. Stack Backend")
    print("8. Interpreter")

    return True


def main():
    # --------------------------------------------------
    # Command line usage:
    #
    # python src/main.py examples/test.mini
    # --------------------------------------------------

    if len(sys.argv) < 2:
        print(
            "Usage:"
        )

        print(
            "python src/main.py "
            "<source_file>"
        )

        print(
            "\nExample:"
        )

        print(
            "python src/main.py "
            "examples/struct_test.mini"
        )

        return

    filename = sys.argv[1]

    success = run_compiler(
        filename
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
